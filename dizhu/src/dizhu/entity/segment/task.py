# -*- coding:utf-8 -*-
import time
import copy
from collections import OrderedDict
from sre_compile import isstring

import freetime.util.log as ftlog
from freetime.entity.msg import MsgPack
import poker.entity.biz.message.message as pkmessage
from poker.entity.biz.item.item import TYAssetUtils
from poker.util import timestamp as pktimestamp
from poker.entity.biz.confobj import TYConfable, TYConfableRegister
from poker.entity.biz.exceptions import TYBizConfException
from poker.entity.biz.content import TYContentRegister
from poker.entity.biz.task.task import TYTaskInspectorRegister
from poker.entity.configure import configure, gdata
from poker.entity.dao import daobase
from poker.protocol import router
from poker.util import strutil
from hall.entity.hallconf import HALL_GAMEID
from hall.entity import hallitem, datachangenotify
from hall.entity.usercoupon.events import UserCouponReceiveEvent
from hall.entity.usercoupon import user_coupon_details
from dizhu.entity.dizhuconf import DIZHU_GAMEID
from dizhu.entity.segment.dizhu_segment_match import SegmentMatchHelper


NEWBIE_KEY = 'task:%d:segment:newbie:%d'
DAILY_KEY = 'task:%d:segment:daily:%d'


def newbie_key(uid):
    return NEWBIE_KEY % (DIZHU_GAMEID, uid)


def daily_key(uid):
    return DAILY_KEY % (DIZHU_GAMEID, uid)


def user_db(*args):
    return daobase.executeUserCmd(*args)


def _is_init_newbie_attr(uid):
    """是否初始化了新手任务"""
    return user_db(uid, "EXISTS", newbie_key(uid))


def set_newbie_attrs(uid, data_list):
    return user_db(uid, "HMSET", newbie_key(uid), *data_list)


def set_newbie_attr(uid, field, value):
    user_db(uid, "HSET", newbie_key(uid), field, value)


def _init_newbie_data(uid, data_list):
    set_newbie_attrs(uid, data_list)


def get_newbie_attr(uid, field):
    return user_db(uid, "HGET", newbie_key(uid), field)


def get_newbie_attrs(uid, fields):
    return user_db(uid, "HMGET", newbie_key(uid), *fields)


def _is_init_daily_attr(uid):
    """是否初始化了新手任务"""
    return user_db(uid, "EXISTS", daily_key(uid))


def set_daily_attr(uid, field, value):
    user_db(uid, "HSET", daily_key(uid), field, value)


def set_daily_attrs(uid, data_list, set_expire=False):
    """
    @param uid:
    @param data_list:
    @param set_expire: 是否设置过期,领奖最后一个任务后为True
    @return:
    """
    if set_expire:
        expire_time = TaskTimeManager.get_daily_task_remain_time()
        user_db(uid, "HMSET", daily_key(uid), *data_list)
        user_db(uid, "EXPIRE", daily_key(uid), expire_time)
        return True
    else:
        return user_db(uid, "HMSET", daily_key(uid), *data_list)


def get_daily_attr(uid, field):
    return user_db(uid, "HGET", daily_key(uid), field)


def get_daily_attrs(uid, fields):
    return user_db(uid, "HMGET", daily_key(uid), *fields)


def _reset_daily_task_expire(uid, delta_ts):
    """动态更改"""
    if gdata.mode() not in (2, 3, 4):
        return
    expire_time = int(time.time()) + delta_ts
    user_db(uid, "EXPIRE", daily_key(uid), expire_time)


def is_today_daily_task(create_time):
    return pktimestamp.is_same_day(create_time, int(time.time()))


def get_user_segment(uid):
    issue = SegmentMatchHelper.getCurrentIssue()
    userSegmentIssue = SegmentMatchHelper.getUserSegmentDataIssue(uid, issue)
    if not userSegmentIssue:
        return 0
    return userSegmentIssue.segment


class TaskErrorCode(object):
    NO_ERR = 0       # 没有错误
    UNKNOWN_ERR = 1  # 服务器内部错误
    TASK_ID_ERR = 2  # taskId错误
    TASK_RESET = 3   # 任务已重置,需要刷新


class TaskTimeManager(object):
    """任务时间相关管理,方便修改时间进行测试"""
    expire_ts = pktimestamp.getCurrentDayLeftSeconds() + int(time.time())
    is_testing = False
    change_delta_ts = 0

    @classmethod
    def is_old_task(cls, create_time):
        if (cls.is_testing and cls.change_delta_ts > 0
                and gdata.mode() in (2, 3, 4)):
            delta = cls.expire_ts - int(time.time())
            is_old = create_time < cls.expire_ts - cls.change_delta_ts
            if delta <= 0:
                cls.expire_ts += cls.change_delta_ts

            return is_old
        else:
            cls.is_testing = False
            return not pktimestamp.is_same_day(create_time, int(time.time()))

    @classmethod
    def _reset_daily_task_expire(cls, delta_ts):
        """动态更改,供测试接口使用"""
        if gdata.mode() not in (2, 3, 4):
            return
        cls.is_testing = True
        cls.change_delta_ts = delta_ts
        cls.expire_ts = int(time.time()) + delta_ts

    @classmethod
    def get_daily_task_remain_time(cls):
        """获取每日任务离重置剩余的时间, 单位:秒"""
        if (cls.is_testing and gdata.mode() in (2, 3, 4)
                and cls.change_delta_ts > 0):
            if cls.expire_ts <= int(time.time()):
                cls.expire_ts += cls.change_delta_ts

            return cls.expire_ts - int(time.time())
        else:
            timestamp = pktimestamp.getCurrentDayLeftSeconds()
            timestamp = max(0, timestamp)
            return timestamp


class SegmentNewbieTaskKind(TYConfable):
    """
    新手任务种类
    """
    TYPE_ID = 'ddz.segment.newbie.task'

    def __init__(self):
        # 监控者
        self.inspector = None
        self.reward_content = None
        self.reward_mail = ''
        self.totalLimit = None
        self.multi_reward_content = None

    def decodeFromDict(self, d):
        self.inspector = TYTaskInspectorRegister.decodeFromDict(d['inspector'])
        reward_content = d.get('rewardContent')
        reward_multi_rate = d.get("multiReward", {}).get("rewardMultiRate", 0)
        if not isinstance(reward_multi_rate, (int, float)):
            raise TYBizConfException(d, 'task.rewardMultiRate must be number')
        self.totalLimit = d.get('total', 0)
        if not isinstance(self.totalLimit, int):
            raise TYBizConfException(d, 'task.totalLimit must be int')
        if reward_content:
            multi_reward_content = copy.deepcopy(reward_content)
            if reward_multi_rate > 0:
                for item in multi_reward_content.get("items", []):
                    if "count" not in item:
                        continue
                    item["count"] += int(item["count"] * reward_multi_rate)
            self.reward_content = TYContentRegister.decodeFromDict(reward_content)
            self.multi_reward_content = TYContentRegister.decodeFromDict(multi_reward_content)
            self.reward_mail = d.get('rewardMail', '')
            if not isstring(self.reward_mail):
                raise TYBizConfException(d, 'task.rewardMail must be string')
        return self

    def processEvent(self, task, event):
        if not self.inspector:
            return
        return self.inspector.processEvent(task, event)


class SegmentDailyTaskKind(TYConfable):
    """
    每日段位任务
    """
    TYPE_ID = 'ddz.segment.daily.task'

    def __init__(self):
        # 监控者
        self.segment_id = 0
        self.inspector = None
        self.reward_content = None
        self.reward_mail = ''
        self.totalLimit = None
        self.multi_reward_content = None

    def decodeFromDict(self, d):
        self.inspector = TYTaskInspectorRegister.decodeFromDict(d['inspector'])
        self.segment_id = d["segmentId"]
        reward_content = d.get('rewardContent')
        reward_multi_rate = d.get("multiReward", {}).get("rewardMultiRate", 0)
        if not isinstance(reward_multi_rate, (int, float)):
            raise TYBizConfException(d, 'task.rewardMultiRate must be number')
        self.totalLimit = d.get('total', 0)
        if not isinstance(self.totalLimit, int):
            raise TYBizConfException(d, 'task.totalLimit must be int')
        if reward_content:
            multi_reward_content = copy.deepcopy(reward_content)
            if reward_multi_rate > 0:
                for item in multi_reward_content.get("items", []):
                    if "count" not in item:
                        continue
                    item["count"] += int(item["count"]*reward_multi_rate)
            self.reward_content = TYContentRegister.decodeFromDict(reward_content)
            self.multi_reward_content = TYContentRegister.decodeFromDict(multi_reward_content)
            self.reward_mail = d.get('rewardMail', '')

            if not isstring(self.reward_mail):
                raise TYBizConfException(d, 'task.rewardMail must be string')
        return self

    def processEvent(self, task, event):
        if not self.inspector:
            return
        return self.inspector.processEvent(task, event)


def on_conf_changed(event):
    if event.isChanged(['game:6:task.segment:0']):
        ftlog.debug('SegmentTaskData._on_conf_changed')
        SegmentTaskData.reload_conf()


def reload_conf():
    SegmentTaskData.reload_conf()


class SegmentTaskData(object):
    """所有任务数据类"""
    newbie_task_map = OrderedDict()  # 新手任务 {task_id: task_info, ...}
    daily_task_map = {}   # 返现/段位任务 { 段位id: [task1, task2, ... ], ...}
    daily_tasks_total = 0
    conf = {}  # 任务总配置
    task_kind_map = {}  # {task_id: taskKind, ...}

    @classmethod
    def initialize(cls):
        cls.reload_conf()

    @classmethod
    def reload_conf(cls):
        """加载配置"""
        cls.conf = configure.getGameJson(DIZHU_GAMEID, "task.segment", {})
        cls._build_data()
        cls.init_task_inspectors()

    @classmethod
    def init_task_inspectors(cls):
        try:
            cls._register_events(cls.task_kind_map.values())
        except:
            cls._unregister_events(cls.task_kind_map.values())
            ftlog.error('SegmentTaskData init_task_inspectors err|',
                        cls.task_kind_map)

    @classmethod
    def _collect_event_map(cls, task_kinds):
        event_map = {}
        for task_kind in task_kinds:
            for event_type, gids in task_kind.inspector.interestEventMap.iteritems():
                gids = gids or gdata.gameIds()
                exists_gids = event_map.get(event_type)
                if not exists_gids:
                    exists_gids = set()
                    event_map[event_type] = exists_gids

                exists_gids.update(gids)
        return event_map

    @classmethod
    def _register_events(cls, task_kinds):
        event_map = cls._collect_event_map(task_kinds)
        for event_type, gameIds in event_map.iteritems():
            for gameId in gameIds:
                game = gdata.games().get(gameId)
                if not game:
                    ftlog.warn('SegmentTaskData._register_events gameId=',
                               gameId, 'eventType=', event_type,
                               'err=', 'Not find game')

                if ftlog.is_debug():
                    ftlog.debug('SegmentTaskData._register_events gameId=',
                                gameId, 'eventType=', event_type)
                game.getEventBus().subscribe(event_type, cls.handle_event)

    @classmethod
    def _unregister_events(cls, task_kinds):
        event_map = cls._collect_event_map(task_kinds)
        for event_type, gameIds in event_map.iteritems():
            for gameId in gameIds:
                game = gdata.games().get(gameId)
                if game:
                    if ftlog.is_debug():
                        ftlog.debug('SegmentTaskData._register_events gameId=',
                                    gameId, 'eventType=', event_type)
                    game.getEventBus().unsubscribe(event_type, cls.handle_event)
                else:
                    ftlog.warn('SegmentTaskData._register_events gameId=',
                               gameId, 'eventType=', event_type,
                               'err=', 'Not find game')

    @classmethod
    def _build_data(cls):
        cls._build_newbie_data()
        cls._build_daily_data()

    @classmethod
    def _build_newbie_data(cls):
        """新手任务数据"""
        newbie_conf = cls.conf.get("newbie", {})
        newbie_task_info = newbie_conf.get("tasks", {})
        newbie_orders = newbie_conf.get("tasks_order", [])
        for task_id in newbie_orders:
            task_id = str(task_id)
            if task_id not in newbie_task_info:
                continue
            task_conf = newbie_task_info[task_id]
            cls.newbie_task_map[task_id] = task_conf
            task_kind = SegmentTaskKindRegister.decodeFromDict(task_conf)
            cls.task_kind_map[str(task_id)] = task_kind

    @classmethod
    def _build_daily_data(cls):
        """每日任务(段位/返现任务)数据"""
        task_info = cls.conf["daily"].get("segment_task_list", {})
        is_valid = True
        task_total = 0
        if task_info:
            tasks = task_info.values()
            is_valid = all(len(i) == len(tasks[0]) for i in tasks)
            task_total = len(tasks[0])
        if not is_valid:
            ftlog.error('segment_task_list conf err| task_info', task_info)
            return

        cls.daily_task_map = task_info
        cls.daily_tasks_total = task_total

        for segment_id, task_list in task_info.items():
            for task_conf in task_list:
                task_conf["segmentId"] = segment_id
                task_kind = SegmentTaskKindRegister.decodeFromDict(task_conf)
                cls.task_kind_map[str(task_conf["id"])] = task_kind

    @classmethod
    def get_newbie_task(cls):
        return cls.newbie_task_map

    @classmethod
    def get_newbie_task_by_id(cls, task_id):
        return cls.newbie_task_map.get(task_id, {})

    @classmethod
    def get_daily_tasks(cls, segment):
        return cls.daily_task_map.get(segment, [])

    @classmethod
    def get_daily_task_by_id(cls, segment, index_):
        tasks = cls.get_daily_tasks(segment)
        if index_ < len(tasks):
            return tasks[index_]
        return {}

    @classmethod
    def handle_event(cls, event):
        event_tasks = UserTaskData.on_event_get_tasks(event.userId)
        if not event_tasks:
            return
        for user_task in event_tasks:
            user_task_kind = cls.task_kind_map[str(user_task["taskId"])]
            task = UserTask(event.userId, user_task_kind)
            task.set_attrs_from_dict(user_task)
            user_task_kind.processEvent(task, event)
            if ftlog.is_debug():
                ftlog.debug('SegmentTaskData.handle_event',
                            'userId', event.userId,
                            'event', event,
                            'user_task', user_task
                            )

    @classmethod
    def get_task_kind(cls, task_id):
        return cls.task_kind_map.get(task_id)


class UserTaskData(object):
    """用户任务数据类
        newbie:
        key: task:gameId:segment:newbie:userId
        field:
            status:task_id 0: 未完成 1: 已完成,未领奖 2 已完成,已领奖
    """
    STATUS_UNFINISHED = 0
    STATUS_UNREWARDED = 1
    STATUS_REWARDED = 2

    @classmethod
    def get_cur_task(cls, uid):
        """获取用户当前奖励"""
        newbie_finished, status_info = cls._is_newbie_finished(uid)
        if not newbie_finished:
            for task_id, status in status_info.items():
                if status != cls.STATUS_REWARDED:
                    return cls.build_newbie_task_info(uid, task_id)

            ftlog.error('get_cur_task err| userId', uid,
                        'status_info', status_info,
                        'newbie_task', SegmentTaskData.get_newbie_task())
        else:
            return cls.get_cur_daily_task(uid)

        return {}

    @classmethod
    def get_cur_daily_task(cls, uid):
        """
        获取当前每日任务
        @param uid:
        @return:
        """
        fields = ("index", "segment", "progress",
                  "allFinished", "createTime", "allFinishTime")
        res = get_daily_attrs(uid, fields)
        index_, segment, _progress, all_finished, create_time = res[:5]
        need_init = False
        if all_finished:
            if res[5] and TaskTimeManager.is_old_task(res[5]):
                need_init = True
            else:
                return {}

        if (not _is_init_daily_attr(uid) or need_init
                or str(segment) not in SegmentTaskData.daily_task_map):
            # 当前没有段位任务/是之前的任务
            segment = get_user_segment(uid)
            if str(segment) not in SegmentTaskData.daily_task_map:
                return {}
            index_ = 0
            data_list = [
                "allFinished", 0,
                "index", index_,
                "segment", segment,
                "progress", 0,
                "createTime", int(time.time())
            ]
            set_daily_attrs(uid, data_list)

        return cls.build_daily_task_info(uid, segment, index_)

    @classmethod
    def on_event_get_tasks(cls, uid):
        """任务事件触发时获取任务列表"""
        tasks = []
        newbie_finished, status_info = cls._is_newbie_finished(uid)
        if newbie_finished:
            ret = cls.get_cur_daily_task(uid)
            if ret:
                tasks.append(ret)
            return tasks
        for task_id, status in status_info.items():
            if status == cls.STATUS_REWARDED:
                continue
            tasks.append(cls.build_newbie_task_info(uid, task_id))
        return tasks

    @classmethod
    def build_newbie_task_info(cls, uid, task_id):
        task_data = SegmentTaskData.get_newbie_task()
        ret = {}
        if task_id in task_data:
            task = task_data[task_id]
            progress = cls.get_newbie_task_progress(uid, task_id)
            if not isinstance(progress, int):
                progress = 0
            ret = {
                "taskId": task_id,
                "desc": task["desc"],
                "extRewardDesc": task.get("extRewardDesc", ""),
                "title": task["title"],
                "total": task["total"],
                "pic": task["pic"],
                "progress": min(progress, task["total"]),
            }

            reward_desc_list = [task["rewardDesc"]]
            if task.get("multiReward", {}).get("rewardMultiRate", 0) > 0:
                reward_desc_list.append(
                    task["multiReward"]["multiRewardDesc"])

            ret["rewardDesc"] = reward_desc_list
        return ret

    @classmethod
    def build_daily_task_info(cls, uid, segment_id, index_):
        segment_id = str(segment_id)
        task_list = SegmentTaskData.get_daily_tasks(segment_id)
        ret = {}
        if index_ < len(task_list):
            task_info = task_list[index_]
            progress = cls.get_daily_task_progress(uid)
            if not isinstance(progress, int):
                progress = 0
            ret = {
                "taskId": str(task_info["id"]),
                "desc": task_info["desc"],
                "extRewardDesc": task_info.get("extRewardDesc", ""),
                "title": task_info["title"],
                "total": task_info["total"],
                "pic": task_info["pic"],
                "progress": min(progress, task_info["total"]),
            }
            reward_desc_list = [task_info["rewardDesc"]]
            if task_info.get("multiReward", {}).get("rewardMultiRate", 0) > 0:
                reward_desc_list.append(task_info["multiReward"]["multiRewardDesc"])

            ret["rewardDesc"] = reward_desc_list
        return ret

    @classmethod
    def _send_rewards(cls, uid, task_id, task_kind, multi_award):
        reward_content = task_kind.reward_content
        if multi_award:
            reward_content = task_kind.multi_reward_content
        userAssets = hallitem.itemSystem.loadUserAssets(uid)
        assetList = userAssets.sendContent(DIZHU_GAMEID,
                                           reward_content,
                                           1,
                                           True,
                                           int(time.time()),
                                           'TASK_REWARD',
                                           int(task_id))
        ftlog.debug('UserTaskData._send_rewards',
                    'task_id=', task_id,
                    'userId=', uid,
                    'assets=',
                    [(atup[0].kindId, atup[1]) for atup in assetList])
        changed = TYAssetUtils.getChangeDataNames(assetList)
        datachangenotify.sendDataChangeNotify(DIZHU_GAMEID, uid, changed)

        if task_kind.reward_mail:
            contents = TYAssetUtils.buildContentsString(assetList)
            mail = strutil.replaceParams(task_kind.reward_mail,
                                         {'rewardContent': contents})
            pkmessage.sendPrivate(HALL_GAMEID, uid, 0, mail)

        return reward_content

    @classmethod
    def reward(cls, uid, task_id, multi_award):
        """领奖"""
        task_id = str(task_id)
        task_kind = SegmentTaskData.get_task_kind(task_id)
        if not task_kind:
            ftlog.warn('UserTaskData.reward err| uid', uid, 'task_id', task_id)
            return {}, {}, TaskErrorCode.TASK_ID_ERR
        if task_kind.TYPE_ID == SegmentNewbieTaskKind.TYPE_ID:
            task_info = SegmentTaskData.get_newbie_task_by_id(task_id)
            fields = ("progress.%s" % task_id, "status.%s" % task_id)
            progress, status = get_newbie_attrs(uid, fields)
            if progress >= task_info["total"] and status != cls.STATUS_REWARDED:
                update_data = [fields[0], progress,
                               fields[1], cls.STATUS_REWARDED,
                               ]
                if not set_newbie_attrs(uid, update_data):
                    ftlog.warn('UserTaskData.reward set_newbie_attrs err |',
                               'uid', uid, 'task_id', task_id)
                    return {}, {}, TaskErrorCode.UNKNOWN_ERR
                rewards = cls._send_rewards(uid, task_id, task_kind, multi_award)
                reward_info = {
                    "reward_content": rewards,
                    "reward_pic": task_info.get("rewardPic", ""),
                }
                return cls.get_cur_task(uid), reward_info, TaskErrorCode.NO_ERR
        elif task_kind.TYPE_ID == SegmentDailyTaskKind.TYPE_ID:
            segment_id = str(task_kind.segment_id)
            fields = ("index", "segment", "progress", "createTime")
            ret = get_daily_attrs(uid, fields)
            if any(i is None for i in ret):
                return {}, {}, TaskErrorCode.TASK_RESET
            task_info = SegmentTaskData.get_daily_task_by_id(segment_id, ret[0])
            if (str(ret[1]) == segment_id
                    and "total" in task_info and ret[2] >= task_info["total"]):
                segment = str(get_user_segment(uid))
                set_expire = False
                if ret[3] and TaskTimeManager.is_old_task(ret[3]):
                    # 是之前的任务,重新发布
                    data_list = [
                        "allFinished", 0,
                        "index", 0,
                        "segment", segment,
                        "progress", 0,
                        "createTime", int(time.time()),
                    ]
                elif ret[0] >= SegmentTaskData.daily_tasks_total - 1:
                    data_list = [
                        "allFinished", 1,
                        "allFinishTime", int(time.time()),
                    ]
                    set_expire = True
                else:
                    data_list = [
                        "allFinished", 0,
                        "index", ret[0]+1,
                        "segment", segment,
                        "progress", 0,
                        "createTime", int(time.time()),
                    ]
                if not set_daily_attrs(uid, data_list, set_expire):
                    ftlog.warn('UserTaskData.reward set_daily_attrs err |',
                               'uid', uid, 'task_id', task_id)
                    return {}, {}, TaskErrorCode.UNKNOWN_ERR
                rewards = cls._send_rewards(uid, task_id, task_kind, multi_award)
                reward_info = {
                    "reward_content": rewards,
                    "reward_pic": task_info.get("rewardPic", ""),
                }
                return cls.get_cur_task(uid), reward_info, TaskErrorCode.NO_ERR

        ftlog.warn('UserTaskData.reward task_id err| uid', uid,
                   'task_id', task_id)

        return {}, {}, TaskErrorCode.TASK_RESET

    @classmethod
    def update_newbie_task(cls, uid, task_id, progress):
        field = "progress.%s" % task_id
        set_newbie_attr(uid, field, progress)

    @classmethod
    def update_daily_task(cls, uid, progress):
        field = "progress"
        set_daily_attr(uid, field, progress)

    @classmethod
    def _is_newbie_finished(cls, uid):
        """判断当前新手任务是否已经完成
        @return all_finished[True/False],
                task_status_info[OrderDict{taskId: status}]
        """
        ret = OrderedDict()
        if not _is_init_newbie_attr(uid):
            _init_newbie_data(uid, cls.gen_newbie_init_data())

        if get_newbie_attr(uid, "allFinished") == 1:
            return True, ret

        fields_map = cls.get_all_newbie_status_fields()
        vals = get_newbie_attrs(uid, fields_map.values())
        all_finished = all(v == cls.STATUS_REWARDED for v in vals)
        if all_finished:
            set_newbie_attr(uid, "allFinished", 1)

        for i, task_id in enumerate(fields_map.keys()):
            ret[task_id] = vals[i]

        return all_finished, ret

    @classmethod
    def _is_daily_finished(cls, uid):
        return get_daily_attr(uid, "allFinished") == 1

    @classmethod
    def get_all_newbie_status_fields(cls):
        """返回所有新手任务id与任务hash中fields字典"""
        tasks_map = SegmentTaskData.get_newbie_task()
        ret = OrderedDict()
        for i in tasks_map.keys():
            ret[i] = "status.%s" % i
        return ret

    @classmethod
    def get_newbie_task_progress(cls, uid, task_id):
        """获取新手任务进度"""
        return get_newbie_attr(uid, 'progress.%s' % task_id)

    @classmethod
    def get_daily_task_progress(cls, uid):
        """获取每日段位任务进度"""
        return get_daily_attr(uid, 'progress')

    @classmethod
    def gen_newbie_init_data(cls):
        tasks_map = SegmentTaskData.get_newbie_task()
        ret = []
        status_default_val = 0
        progress_default_val = 0
        for i in tasks_map.keys():
            status_field = "status.%s" % i
            ret.append(status_field)
            ret.append(status_default_val)

            progress_filed = "progress.%s" % i
            ret.append(progress_filed)
            ret.append(progress_default_val)

        ret.extend(["allFinished", 0])
        return ret


class UserTask(object):
    """任务任务类"""
    def __init__(self, uid, task_kind):
        self.taskKind = task_kind
        self.uid = uid
        self.task_id = 0
        self.progress = 0
        self.status = 0
        self.total = 0
        self.updateTime = 0
        self.finishCount = 0

    @property
    def userId(self):
        return self.uid

    @property
    def kindId(self):
        return self.task_id

    def set_attrs_from_dict(self, d):
        self.task_id = d["taskId"]
        self.progress = d["progress"]
        self.total = d["total"]

    def setProgress(self, progress, timestamp):
        if ftlog.is_debug():
            ftlog.debug("UserTask.setProgress | self.progress", self.progress,
                        "progress", progress, "self.total", self.total)
        self.updateTime = timestamp
        if not progress <= self.total:
            SegmentTaskHelper.send_get_task_response(DIZHU_GAMEID, self.uid)
            return False, 0

        if self.taskKind.TYPE_ID == SegmentNewbieTaskKind.TYPE_ID:
            UserTaskData.update_newbie_task(self.uid, self.task_id, progress)
        elif self.taskKind.TYPE_ID == SegmentDailyTaskKind.TYPE_ID:
            UserTaskData.update_daily_task(self.uid, progress)

        SegmentTaskHelper.send_get_task_response(DIZHU_GAMEID, self.uid)
        self.finishCount += 1
        return True, 1


class SegmentTaskHelper(object):
    """下发相关消息类"""

    @classmethod
    def send_get_task_response(cls, gid, uid):
        task = UserTaskData.get_cur_task(uid)
        ret = {
            "task": task,
            "resetRemainTime": TaskTimeManager.get_daily_task_remain_time(),
        }
        mo = MsgPack()
        mo.setCmd('dizhu')
        mo.setResult('gameId', gid)
        mo.setResult('userId', uid)
        mo.setResult('action', 'get_segment_task')
        for k, v in ret.items():
            mo.setResult(k, v)
        router.sendToUser(mo, uid)

    @classmethod
    def _build_reward_info(cls, rewards):
        """构建奖励信息"""
        ret = {
            "pic": rewards.get("reward_pic", "")
        }
        reward_items = rewards["reward_content"].getItems()
        for reward_item in reward_items:
            if reward_item.assetKindId == "user:coupon":
                ret["count"] = float('%.2f' % (reward_item.count/100.00))
                ret["raw_count"] = reward_item.count
                break

        return ret

    @classmethod
    def send_get_award_response(cls, gid, uid, task_id, multi_award):
        task, rewards, err_code = UserTaskData.reward(uid, task_id, multi_award)
        ret = {
            "nextTask": task,
            "resetRemainTime": TaskTimeManager.get_daily_task_remain_time(),
            "code": err_code,
        }
        if rewards:
            ret["rewardInfo"] = cls._build_reward_info(rewards)
            if "raw_count" in ret["rewardInfo"]:
                cls._publish_reward_event(uid, ret["rewardInfo"]["raw_count"])

        mo = MsgPack()
        mo.setCmd('dizhu')
        mo.setResult('gameId', gid)
        mo.setResult('userId', uid)
        mo.setResult('action', 'get_segment_task_award')
        for k, v in ret.items():
            mo.setResult(k, v)
        router.sendToUser(mo, uid)

    @classmethod
    def _publish_reward_event(cls, uid, count):
        from hall.game import TGHall
        TGHall.getEventBus().publishEvent(
            UserCouponReceiveEvent(HALL_GAMEID, uid, count,
                                   user_coupon_details.USER_COUPON_SOURCE_SEGMENT_TASK))


class SegmentTaskKindRegister(TYConfableRegister):
    _typeid_clz_map = {
        SegmentNewbieTaskKind.TYPE_ID: SegmentNewbieTaskKind,
        SegmentDailyTaskKind.TYPE_ID: SegmentDailyTaskKind,
    }


