# -*- coding=utf-8 -*-

from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from hall.entity import hallfree
from hall.entity import halltask
from hall.entity.halltask import hall_new_user_task_sys, hall_charge_task_sys, HallNewUserSubTaskSystem, \
    HallChargeSubTaskSystem
from hall.servers.common.base_checker import BaseMsgPackChecker
from poker.entity.biz.item.item import TYAssetUtils
from poker.entity.biz.task.exceptions import TYTaskException
from poker.protocol import router
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod
import poker.util.timestamp as pktimestamp
from hall.entity.todotask import TodoTaskHelper
from poker.entity.dao import gamedata
from hall.entity.hallconf import HALL_GAMEID
import json

FREEITEMID_NEWCHECKIN = 101


class FreeHelper(object):
    @classmethod
    def getFreeById(cls, freeList, freeItemId):
        for free in freeList:
            if free.freeItemId == freeItemId:
                return free
        return None

    @classmethod
    def getCurStateOfFreeItem(cls, gameId, userId, clientId, free, timestamp):
        for state in free.states:
            checkConditionsOk = True
            for condition in state.conditionList:
                if not condition.check(gameId, userId, clientId, timestamp):
                    checkConditionsOk = False
            if checkConditionsOk:
                return state
        return None

    @classmethod
    def encodeFree(cls, gameId, userId, clientId, free, timestamp):
        ret = None
        curState = cls.getCurStateOfFreeItem(gameId, userId, clientId, free, timestamp)

        if curState and curState.visible:
            ret = {
                'id': free.freeItemId,
                'iconRes': free.iconRes,
                "itemName": free.itemName,
                'desc': curState.desc,
                'btnText': curState.btnText,
                'markVisible': False if free.freeItemId == FREEITEMID_NEWCHECKIN else curState.hasMark,
                'btnAvailable': cls.getNewCheckinStatus(userId) if free.freeItemId == FREEITEMID_NEWCHECKIN else curState.enable
            }
        else:
            ftlog.debug('FreeHelper.encodeFree no state finded gameId=', gameId,
                       'userId=', userId,
                       'clientId=', clientId,
                       "freeItemId=", free.freeItemId)
        return ret

    @classmethod
    def getNewCheckinStatus(cls, userId):
        info = gamedata.getGameAttr(userId, HALL_GAMEID, 'checkin_new')
        if not info:
            return True

        info = json.loads(info)
        return info.get('isCheckIn')

    @classmethod
    def encodeFreeList(cls, gameId, userId, clientId, freeList, timestamp):
        ret = []
        for free in freeList:
            f = cls.encodeFree(gameId, userId, clientId, free, timestamp)
            if f:
                ret.append(f)
        return ret

    @classmethod
    def makeFreeResponse(cls, gameId, userId, clientId, freeList, timestamp):
        """
        {
            "cmd": "game",
            "result": {
                "action": "free_list",
                "gameId": 9999,
                "userId": 10856,
                "freeList": [
                    {
                        "btnAvailable": true,
                        "iconRes": "checkin",
                        "btnText": "签到",
                        "markVisible": true,
                        "id": 1,
                        "desc": "每日签到就赠送500金币和1次免费抽奖机会!\n(今天您还没有签到)"
                    },
                    {
                        "btnAvailable": true,
                        "iconRes": "lottery",
                        "btnText": "抽奖",
                        "markVisible": false,
                        "id": 2,
                        "desc": "您还可以使用钻石进行抽奖!"
                    },
                    {
                        "btnAvailable": false,
                        "iconRes": "share",
                        "btnText": "局对分享",
                        "markVisible": true,
                        "id": 18,
                        "desc": ""
                    },
                    {
                        "btnAvailable": false,
                        "iconRes": "share",
                        "btnText": "召唤好友",
                        "markVisible": true,
                        "id": 19,
                        "desc": ""
                    }
                ]
            }
        }
        """
        mo = MsgPack()
        mo.setCmd('game')
        mo.setResult('action', 'free_list')
        mo.setResult('gameId', gameId)
        mo.setResult('userId', userId)
        mo.setResult('freeList', cls.encodeFreeList(gameId, userId, clientId, freeList, timestamp))
        return mo


@markCmdActionHandler
class FreeTcpHandler(BaseMsgPackChecker):
    def __init__(self):
        super(FreeTcpHandler, self).__init__()

    def _check_param_freeItemId(self, msg, key, params):
        freeItemId = msg.getParam('freeItemId')
        if not isinstance(freeItemId, int):
            return 'ERROR of index !' + str(freeItemId), None
        return None, freeItemId

    # 获取列表请求
    @markCmdActionMethod(cmd='game', action="free_list", clientIdVer=0)
    def doFreeList(self, gameId, userId, clientId):
        timestamp = pktimestamp.getCurrentTimestamp()
        freeList = hallfree.getFree(gameId, userId, clientId, timestamp)
        mo = FreeHelper.makeFreeResponse(gameId, userId, clientId, freeList, timestamp)
        router.sendToUser(mo, userId)

    # 点击按钮回调
    @markCmdActionMethod(cmd='game', action="free_checkout", clientIdVer=0)
    def doCheckout(self, gameId, userId, clientId, freeItemId):
        """
        {
            "cmd": "game",
            "params": {
                "action": "free_checkout",
                "userId": 10856,
                "gameId": 9999,
                "freeItemId": 1
            }
        }
        """
        if freeItemId == FREEITEMID_NEWCHECKIN:
            from hall.entity.newcheckin import clientReqCheckin
            clientReqCheckin(userId,clientId,gameId)
            return
        timestamp = pktimestamp.getCurrentTimestamp()
        freeList = hallfree.getFree(gameId, userId, clientId, timestamp)
        free = FreeHelper.getFreeById(freeList, freeItemId)
        if free:
            curState = FreeHelper.getCurStateOfFreeItem(gameId, userId, clientId, free, timestamp)
            if curState:
                todotasks = TodoTaskHelper.makeTodoTasksByFactory(gameId, userId, clientId, curState.todotaskList)
                if todotasks:
                    TodoTaskHelper.sendTodoTask(gameId, userId, todotasks)

    @staticmethod
    def _encode_task(task, gameid, userid, clientid):
        state = 0
        if task.isFinished:
            state = 2 if task.gotReward else 1
        ret = {
            'id': task.kindId,
            'name': task.taskKind.name,
            'desc': task.taskKind.desc,
            'reward': task.taskKind.rewardContent.desc if task.taskKind.rewardContent else '',
            'iconUrl': task.taskKind.pic,
            'state': state,  # -1未解锁,0进行中,1已完成,2已领奖
            'progress': task.progress,
            'progressMax': task.taskKind.count,
            'freshTip': task.taskKind.freshTip
        }
        if not state and task.taskKind.todotask_factory:
            todotask = task.taskKind.todotask_factory.newTodoTask(gameid, userid, clientid)
            if todotask:  # 有些clientid是不配置大额商品的,导致类似todotask.payOrder,会取空
                ret['todotask'] = todotask.toDict()
            if task.taskKind.lblEnter:
                ret['lblEnter'] = task.taskKind.lblEnter
        return ret

    @staticmethod
    def _encode_task_kind(task_kind):
        return {
            'id': task_kind.kindId,
            'name': task_kind.name,
            # 'desc': task_kind.desc,
            # 'reward': task_kind.rewardContent.desc if task_kind.rewardContent else '',
            'iconUrl': task_kind.pic,
            'state': -1,  # -1未解锁,0进行中,1已完成,2已领奖
            # 'progress': 0,
            # 'progressMax': task_kind.count,
            'freshTip': task_kind.freshTip
        }

    @staticmethod
    def _build_single_type_task(tasks, subsys, gameid, userid, clientid, curtime):
        taskmodel = subsys.loadTaskModel(userid, curtime, clientid)
        if not taskmodel:
            return

        # 先填充已存储的任务
        user_task_unit = taskmodel.userTaskUnit
        task_list = user_task_unit.taskList
        if task_list:
            task_list.sort(key=lambda t: t.updateTime)
            for task in task_list:
                tasks.append(FreeTcpHandler._encode_task(task, gameid, userid, clientid))
            # 再填充未接的任务
            task_pool = task_list[0].taskKind.taskKindPool  # 当前pool
            task_order = task_pool.task_order
            for i in xrange(len(task_list), len(task_order)):
                task_kind = task_pool.findTaskKind(task_order[i])
                tasks.append(FreeTcpHandler._encode_task_kind(task_kind))

    @classmethod
    def _build_task_info(cls, gameid, userid, clientid):
        """
        {
            "cmd": "game",
            "result": {
                "action": "task_info",
                "tasks": [
                    {
                        "progressMax": 6,
                        "freshTip": false,
                        "name": "100奖券",
                        "todotask": {
                            "action": "pop_active_wnd",
                            "params": {
                                "actId": "activity_viprenwu_1123"
                            }
                        },
                        "iconUrl": "task_coupon",
                        "state": 0,
                        "progress": 0,
                        "reward": "100奖券",
                        "lblEnter": "充值",
                        "id": 40001,
                        "desc": "单笔充值满6元，可得100奖券"
                    },
                    {
                        "iconUrl": "task_iphoneCard",
                        "state": -1,
                        "freshTip": false,
                        "id": 40002,
                        "name": "10元话费卡"
                    },
                    {
                        "iconUrl": "task_iphoneCard",
                        "state": -1,
                        "freshTip": false,
                        "id": 40003,
                        "name": "50元话费卡"
                    }
                ]
            }
        }
        """
        tasks = []
        curtime = pktimestamp.getCurrentTimestamp()
        # 分派任务
        cls._build_single_type_task(tasks, hall_new_user_task_sys, gameid, userid, clientid, curtime)
        cls._build_single_type_task(tasks, hall_charge_task_sys, gameid, userid, clientid, curtime)
        mo = MsgPack()
        mo.setCmd('game')
        mo.setResult('action', 'task_info')
        mo.setResult('tasks', tasks if tasks else [])
        return mo

    @markCmdActionMethod(cmd='game', action='query_task', clientIdVer=0)
    def do_query_task(self, gameId, userId, clientId):
        """
        上行消息：
        {
            "cmd": "game",
            "params": {
                "action": "query_task",
                "userId": 10856,
                "gameId": 9999
            }
        }
        """
        msg_ret = self._build_task_info(gameId, userId, clientId)
        router.sendToUser(msg_ret, userId)

    def _check_param_taskid(self, msg, key, params):
        value = msg.getParam(key)
        if value and isinstance(value, int):
            return None, value
        return 'ERROR of taskid:' + str(value), None

    @markCmdActionMethod(cmd='game', action='get_task_reward', clientIdVer=0)
    def do_get_task_reward(self, gameId, userId, clientId, taskid):
        curtime = pktimestamp.getCurrentTimestamp()
        task_kind = halltask._taskSystem.findTaskKind(taskid)
        if not task_kind:
            return 
        subsys = task_kind.taskUnit.subTaskSystem
        if not isinstance(subsys, (HallNewUserSubTaskSystem, HallChargeSubTaskSystem)):  # 目前只有这俩走这里
            return

        try:
            taskmodel = subsys.loadTaskModel(userId, curtime, clientId)
            if not taskmodel:
                raise TYTaskException(-1, "未知的任务:%s" % taskid)
            task = taskmodel.userTaskUnit.findTask(taskid)
            if not task:
                raise TYTaskException(-2, "未知的任务:%s" % taskid)
            asset_list = subsys.getTaskReward(task, curtime, 'FREE_TASK', taskid)
            router.sendToUser(self._build_task_info(gameId, userId, clientId), userId)

            rewardstr = TYAssetUtils.buildContentsString(asset_list)
            mo = MsgPack()
            mo.setCmd('game')
            mo.setResult('action', 'get_task_reward')
            mo.setResult('code', 0)
            mo.setResult('info', '恭喜您获得了%s' % rewardstr)
            router.sendToUser(mo, userId)
        except TYTaskException, e:
            mo = MsgPack()
            mo.setCmd('game')
            mo.setResult('action', 'get_task_reward')
            mo.setResult('code', e.errorCode)
            mo.setResult('info', e.message)
            router.sendToUser(mo, userId)
