# -*- coding: utf-8 -*-
'''
Created on 2017年8月22日
@author: ljh
'''
import time
import json
import uuid
import freetime.util.log as ftlog
from freetime.core.timer import FTTimer
from freetime.entity.msg import MsgPack
from datetime import datetime
from poker.entity.dao import daobase, gamedata, onlinedata
from poker.util import strutil
from poker.util.constants import CLIENT_SYS_ANDROID, CLIENT_SYS_IOS
from poker.protocol import router
from poker.entity.configure import gdata
from hall.entity.hallconf import HALL_GAMEID

NOTIFY_TIME_ATONCE_ID = '-2'  # 立即
NOTIFY_TIME_TIMER_ID = '-1'  # 定时
NOTIFY_TIME_EVERYDAY_ID = '0'  # 每天
NOTIFY_TIME_WEEK_1_ID = '1'  # 周一
NOTIFY_TIME_WEEK_2_ID = '2'  # 周二
NOTIFY_TIME_WEEK_3_ID = '3'  # 周三
NOTIFY_TIME_WEEK_4_ID = '4'  # 周四
NOTIFY_TIME_WEEK_5_ID = '5'  # 周五
NOTIFY_TIME_WEEK_6_ID = '6'  # 周六
NOTIFY_TIME_WEEK_7_ID = '7'  # 周日
NOTIFY_TIME_LIST = [NOTIFY_TIME_ATONCE_ID, NOTIFY_TIME_TIMER_ID, NOTIFY_TIME_EVERYDAY_ID, NOTIFY_TIME_WEEK_1_ID,
                    NOTIFY_TIME_WEEK_2_ID, NOTIFY_TIME_WEEK_3_ID, NOTIFY_TIME_WEEK_4_ID,
                    NOTIFY_TIME_WEEK_5_ID, NOTIFY_TIME_WEEK_6_ID, NOTIFY_TIME_WEEK_7_ID]

NOTIFY_TIME_REDIS_KEY_LIST = [NOTIFY_TIME_EVERYDAY_ID, NOTIFY_TIME_WEEK_1_ID,
                              NOTIFY_TIME_WEEK_2_ID, NOTIFY_TIME_WEEK_3_ID, NOTIFY_TIME_WEEK_4_ID,
                              NOTIFY_TIME_WEEK_5_ID, NOTIFY_TIME_WEEK_6_ID, NOTIFY_TIME_WEEK_7_ID]

NOTIFY_TYPEID_ANNOUNCE = '1'  # 公告通知
NOTIFY_TYPEID_MESSAGE = '2'  # 消息通知
NOTIFY_TYPEID_LIST = [NOTIFY_TYPEID_ANNOUNCE, NOTIFY_TYPEID_MESSAGE]

hallidList = ('hall6', 'hall8', 'hall3', 'hall7', 'hall10', 'hall17', 'hall20', 'hall21', 'hall25', 'hall30', 'hall42')
hallnameList = ('斗地主大厅', '德州大厅', '象棋大厅', '麻将大厅', '拼十大厅', '保皇大厅', '五子棋大厅', '跑胡子大厅', '军旗大厅', '新三张牌大厅', '双升大厅')

# 进程启动标志位
_inited = False
# 更新通知列表时间,禁止推送
_pushed = True
# 通知持续时长
NOTIFY_TIMER_LIFE = 5 * 60
# 更新日期标志
_update = None
# 更新今日通知列表标志
_upnotify = int(time.time())
# 更新今日列表时长
_upduration = 5

# 今日的通知列表
notify_today_list = {}
# notify redis key 每天 还有周一到周日:n:hallid
notify_key = 'notify:everyday:%s:%s'
# notify redis key 定时:hallid
notify_timer_key = 'notify:timer:%s'
# 今日通知Redis 新增加 这个key中保存 每日、周一到周日中属于今日的、定时中属于今日的、立即消息
notify_todayadd_key = 'notify:todayadd'
# 今日通知Redis 删除 这个key中保存 每日、周一到周日中属于今日的、定时中属于今日的、立即消息
notify_todaydel_key = 'notify:todaydel'
notify_match_user_date_key = 'notify:match:user:date:%s:%s'
notify_match_user_zset_key = 'notify:match:user:zset:%s'
NOTIFY_MATCH_NORMAL = 1
NOTIFY_MATCH_RECOMMEND = 2


# 公告通知
def sendNotify_announce(gameId, userId, argd):
    results = {}
    results['context'] = argd['context']
    results['action'] = 'notify_announce'

    mp = MsgPack()
    mp.setCmd('game_notice')
    mp.setResult('gameId', gameId)
    mp.setResult('userId', userId)
    mp.updateResult(results)
    router.sendToUser(mp, userId)
    ftlog.hinfo('notify sendNotify_announce', gameId, userId, results)


# 消息通知
def sendNotify_message(gameId, userId, argd):
    results = {}
    results['pic'] = argd['iconAddr']
    results['des'] = argd['context']
    results['buttonType'] = argd['buttonType'] if argd['buttonType'] in ('1', '2') else '1'
    results['todo'] = argd['passthrough']
    results['closeTime'] = argd['timelimit']
    results['alarmime'] = '0'
    results['action'] = 'notify_message'
    results['hideIcon'] = argd.get('hideIcon', '0')

    if len(argd['passthrough']) > 5:
        todoTask = eval(argd['passthrough'])
        results['todo'] = todoTask
        ftlog.hinfo('notify sendNotify_message passthrough todoTask', gameId, userId, todoTask,
                    type(todoTask), argd['passthrough'])

    mp = MsgPack()
    mp.setCmd('game_notice')
    mp.setResult('gameId', gameId)
    mp.setResult('userId', userId)
    mp.updateResult(results)
    router.sendToUser(mp, userId)
    ftlog.hinfo('notify sendNotify_message', gameId, userId, results)


class Notify(object):
    '''
    一条通知
    '''

    def __init__(self, argd):
        self.argd = argd
        self._alive = False

        if self.argd['ntimeId'] == NOTIFY_TIME_ATONCE_ID:
            self.startTimer = FTTimer(0, self.start)
            ftlog.hinfo('Notify.__init__ atonce', self.argd)
        else:
            ntime = [0, 1]
            if self.argd['ntimeId'] == NOTIFY_TIME_TIMER_ID:
                try:
                    dtList = self.argd['ntime'].split('|')
                    ntime = map(int, dtList[1].split(':'))
                except:
                    ftlog.warn('Notify.__init__.NOTIFY_TIME_TIMER_ID error')
                    ntime = map(int, '00:01'.split(':'))
            else:
                ntime = map(int, self.argd['ntime'].split(':'))
            hm = map(int, getNowTimeStr().split(':'))

            interval = (ntime[0] * 60 * 60 + ntime[1] * 60) - (hm[0] * 60 * 60 + hm[1] * 60)
            ftlog.hinfo('Notify.__init__ begin:', ntime, hm, interval, (ntime[0] * 60 * 60 + ntime[1] * 60),
                        (hm[0] * 60 * 60 + hm[1] * 60))
            if interval > 0:
                self.startTimer = FTTimer(interval, self.start)

            ftlog.hinfo('Notify.__init__ end:', interval, self.argd)

    def start(self):
        self.startTimer.cancel()

        if self.argd['rmTag'] == 1:
            ftlog.hinfo('Notify.start error because be removed', self.argd['uuid'])
            return

        self._alive = True
        self.endTimer = FTTimer(NOTIFY_TIMER_LIFE, self.end)

        ftlog.hinfo('Notify.start', NOTIFY_TIMER_LIFE, self.argd['uuid'])

    def end(self):
        self.endTimer.cancel()
        self._alive = False

        if self.argd['ntimeId'] == NOTIFY_TIME_TIMER_ID:
            daobase.executeRankCmd('HDEL', notify_timer_key % self.argd['hall'], self.uuid)
            ftlog.hinfo('HDEL.notify timer', self.argd)

        ftlog.hinfo('Notify.end', self.argd['uuid'])

    def pushNotify(self, userId, gameId, clientId, clientSys):
        try:
        
            if ftlog.is_debug():
                ftlog.hinfo('Notify.pushNotify enter argd=', userId, gameId, clientId, clientSys, self.typeId,
                            self.typeId == NOTIFY_TYPEID_ANNOUNCE, self.argd)
            if self.argd['rmTag'] == 1:
                ftlog.hinfo('Notify.pushNotify notify be removed', userId, gameId, clientId, clientSys)
                return
            if len(self.argd['userId']) >= len('10000') and str(userId) not in self.argd['userId'].split('|'):
                ftlog.hinfo('Notify.pushNotify userId not match', userId, gameId, clientId, clientSys)
                return
            package = self.argd['package']
            if len(package) > 0:
                if clientId not in package.split('|'):
                    ftlog.hinfo('Notify.pushNotify clientId not in package', userId, gameId, clientId, clientSys)
                    return
    
            platform = self.argd['platform']
            if platform == '1':
                if clientSys != CLIENT_SYS_IOS:
                    ftlog.hinfo('Notify.pushNotify clientSys not is ios', userId, gameId, clientId, clientSys)
                    return
            elif platform == '2':
                if clientSys != CLIENT_SYS_ANDROID:
                    ftlog.hinfo('Notify.pushNotify clientSys not is android', userId, gameId, clientId, clientSys)
                    return
            elif platform == '3':
                pass #任意平台都可以
            else:
                ftlog.warn('Notify.pushNotify clientSys error platform')
                return
    
            if clientId.count(self.argd['hall']) == 0:
                ftlog.hinfo('Notify.pushNotify hall not match', userId, gameId, self.argd['hall'], clientId, clientSys)
                return
            else:
                plugin_gameid = self.argd['gameId']
                if len(plugin_gameid) > 0:
                    if plugin_gameid != str(gameId):
                        ftlog.hinfo('Notify.pushNotify plugin_gameid not match', userId, gameId, self.argd['gameId'],
                                    clientId,
                                    clientSys)
                        return
    
            if self.typeId == NOTIFY_TYPEID_ANNOUNCE:
                sendNotify_announce(gameId, userId, self.argd)
            elif self.typeId == NOTIFY_TYPEID_MESSAGE:
                sendNotify_message(gameId, userId, self.argd)
        except:            
            ftlog.error('Notify.pushNotify before11', userId, gameId, clientId, clientSys, self.argd)
    def rmTag(self):
        self.argd['rmTag'] = 1
        ftlog.hinfo('Notify.rmTag is 1', self.uuid)

    @property
    def alive(self):
        return self._alive

    @property
    def typeId(self):
        return self.argd['typeId']

    @property
    def uuid(self):
        return self.argd['uuid']

    def __str__(self):
        return dict(self.argd).__repr__()

    def __repr__(self):
        return self.__str__()


def update_notify_today_list():
    global notify_today_list
    notify_add = daobase.executeRankCmd('HGETALL', notify_todayadd_key)
    if notify_add and len(notify_add) > 0:
        for i in xrange(len(notify_add) / 2):
            uuid, notify = notify_add[i * 2], notify_add[i * 2 + 1]
            argd = json.loads(notify)
            ntimeId = argd['ntimeId']
            ntime = argd['ntime']
            if ntimeId == NOTIFY_TIME_ATONCE_ID:
                if uuid not in notify_today_list:
                    notify_today_list[uuid] = Notify(argd)
            elif ntimeId == NOTIFY_TIME_TIMER_ID:
                dtList = argd['ntime'].split('|')
                date = dtList[0]
                ntime = dtList[1]
                if date == getNowDateStr():
                    if ntime > getNowTimeStr():
                        if uuid not in notify_today_list:
                            notify_today_list[uuid] = Notify(argd)
            elif ntimeId == NOTIFY_TIME_EVERYDAY_ID:
                if ntime > getNowTimeStr():
                    if uuid not in notify_today_list:
                        notify_today_list[uuid] = Notify(argd)
            else:
                if ntimeId == getNowWeekdayStr():
                    if ntime > getNowTimeStr():
                        if uuid not in notify_today_list:
                            notify_today_list[uuid] = Notify(argd)

    notify_del = daobase.executeRankCmd('HGETALL', notify_todaydel_key)
    if notify_del and len(notify_del) > 0:
        for i in xrange(len(notify_del) / 2):
            uuid = notify_del[i * 2]
            if uuid in notify_today_list:
                if notify_today_list[uuid].argd['rmTag'] != 1:
                    notify_today_list[uuid].rmTag()


def upNotifyTodayList():
    global _pushed, _upnotify, _upduration
    ntime = int(time.time())
    if ntime - _upnotify > _upduration:
        _upnotify = ntime
        _pushed = False
        update_notify_today_list()
        _pushed = True


def pushNotify(userId, gameId, clientId):
    '''玩家自己push消息'''
    # cmd='user', action='heart_beat' 6s client req once but real 30s
    gameId = onlinedata.getLastGameId(userId)
    if ftlog.is_debug():
        ftlog.debug('hallnewnotify pushNotify', userId, gameId, clientId)

    global notify_today_list, _pushed
    if ftlog.is_debug():
        ftlog.debug('hallnewnotify.pushNotify', userId, gameId, clientId, notify_today_list, _pushed)
    if _pushed is False:
        ftlog.hinfo('hallnewnotify.pushNotify is in cannot push time', userId, gameId, clientId)
        return

    upNotifyTodayList()

    length = len(notify_today_list)
    if length == 0:
        ftlog.hinfo('hallnewnotify.notifytodaylist is empty', userId, gameId, clientId)
        return

    todaynotifylist = gamedata.getGameAttr(userId, HALL_GAMEID, 'todaynotifylist')
    if not todaynotifylist:
        todaynotifylist = []
    else:
        todaynotifylist = json.loads(todaynotifylist)
    clientSys, _, _ = strutil.parseClientId(clientId)
    if ftlog.is_debug():
        ftlog.hinfo('hallnewnotify.pushNotify todaynotifylist:', userId, gameId, clientId, todaynotifylist)

    todaykeyList = notify_today_list.keys()
    for uuid in todaykeyList:
        notifyIns = notify_today_list[uuid]
        if ftlog.is_debug():
            ftlog.hinfo('hallnewnotify.pushNotify.loop notifyIns', uuid, userId, notifyIns.alive, notifyIns.uuid,
                        todaynotifylist, notifyIns.uuid not in todaynotifylist)
        if notifyIns.alive:
            if notifyIns.uuid not in todaynotifylist:
                notifyIns.pushNotify(userId, gameId, clientId, clientSys)
                todaynotifylist.append(notifyIns.uuid)
    gamedata.setGameAttr(userId, HALL_GAMEID, 'todaynotifylist', json.dumps(todaynotifylist))


def getNowDateStr():
    return datetime.now().strftime('%Y%m%d')


def getNowTimeStr():
    return datetime.now().strftime('%H:%M')


def getNowWeekdayStr():
    # 0-6是星期一到星期日
    weekday = datetime.now().weekday()
    return str(weekday + 1)


def check(typeId, ntimeId, ntime, iconAddr, context, passthrough, platform, buttonType, hall, gameId,
          package, userId, timelimit):
    def log():
        return (
            'typeId', typeId, 'ntimeId', ntimeId, 'ntime', ntime, 'iconAddr', iconAddr, 'context', context,
            'passthrough',
            passthrough, 'platform', platform, 'buttonType', buttonType, 'hall', hall, 'gameId', gameId, 'package',
            package, 'userId', userId, 'timelimit', timelimit)

    if typeId not in NOTIFY_TYPEID_LIST:
        ftlog.hinfo('notify check typeid error', log())
        return False
    if ntimeId not in NOTIFY_TIME_LIST:
        ftlog.hinfo('notify check ntimeId error', log())
        return False
    if ntime > '23:59':
        ftlog.hinfo('notify check ntime > 23:59 error', log())
        return False

    if ntimeId == NOTIFY_TIME_TIMER_ID:
        dtList = ntime.split('|')
        if len(dtList) != 2:
            ftlog.hinfo('notify check timer ntime format error', log())
            return False

        date = dtList[0]
        if date == getNowDateStr():
            if ntime <= getNowTimeStr():
                ftlog.hinfo('notify check timer ntime < now error', log())
                return False
        elif date < getNowDateStr():
            ftlog.hinfo('notify check timer date expire error', log())
            return False
    if not str(timelimit).isdigit():
        ftlog.hinfo('notify check timelimit not digit error', log())
        return False

    if hall not in hallidList:
        ftlog.hinfo('notify check hall not in hallidList error', log())
        return False

    if len(passthrough) > 5:
        try:
            todoTask = json.loads(passthrough)
            ftlog.debug('notify check json.loads(passthrough) ', passthrough, type(passthrough), todoTask,
                        type(todoTask))
        except:
            ftlog.hinfo('notify check passthrough format error', log())
            return False

    return True


# http调用
def addNotifyInfo(typeId, ntimeId, ntime, iconAddr, context, passthrough, platform, buttonType, hall,
                  gameId, package, userId, timelimit, mapArgs=None):
    '''
    typeId 发送类型 1公告通知 2消息通知 3系统推送 必须选一个,没有默认
    ntimeId 发送时间 -2立即、-1定时、0每天、1周一、2周二、3周三、4周四、5周五、6周六、7周日 必须选一个,没有默认
    ntime 时间12:35 如果是ntimeId-2立即 可以不填 ,ntimeId-1定时 20170822|12:35,其他的 ntimeId,必须填一个时间,没有默认
    iconAddr 路径 必须填,没有默认
    context 文本内容 存文本 不超过50字 必须填,没有默认
    passthrough 透传消息,json{todotask} 可以不填,默认为空字符串
    platform 1 ios、2 android 必须选一个,没有默认
    buttonType 按钮类型 1确定 2忽略+前往  不选 默认确定
    hall 不需要手动填写的,根据用户权限给分配, 例如:'hall6', 'hall30'
    gameId 插件gameId  比如斗地主大厅的'30'插件,  不选发送所有插件,不填就是空字符串
    package 多个clientId,以 | 分割 'clientId1|clientId2|' 例如'Android_4.56_tyGuest,weixinPay,tyAccount.yisdkpay,alipay.0-hall6.baidusearch.tu|
    Ios_4.56_tyGuest,weixinPay,tyAccount.yisdkpay,alipay.0-hall6.baidusearch.tu' 不填就是空字符串
    userId 不填发送给所有的用户 'userId1|userId2|' 例如 '123456|78923' 不填就是空字符串
    '''
    if not check(typeId, ntimeId, ntime, iconAddr, context, passthrough, platform, buttonType, hall, gameId,
                 package, userId, timelimit):
        ftlog.hinfo('addNotifyInfo check error')
        return False

    argd = {'typeId': typeId, 'ntimeId': ntimeId, 'ntime': ntime, 'iconAddr': iconAddr, 'context': context,
            'passthrough': passthrough, 'platform': platform, 'buttonType': buttonType,
            'hall': hall, 'gameId': gameId, 'package': package, 'userId': userId,
            'uuid': uuid.uuid1().get_hex(), 'createTime': int(time.time()), 'rmTag': 0, 'timelimit': timelimit}
    
    if mapArgs:
        argd.update(mapArgs)
    
    ftlog.hinfo('addNotifyInfo mapargs, argd', mapArgs, argd)

    if ntimeId == NOTIFY_TIME_ATONCE_ID:
        daobase.executeRankCmd('HSET', notify_todayadd_key, argd['uuid'], json.dumps(argd))
        ftlog.hinfo('addNotifyInfo atonce ntimeId -2', ntimeId, argd)
    elif ntimeId == NOTIFY_TIME_TIMER_ID:
        daobase.executeRankCmd('HSET', notify_timer_key % hall, argd['uuid'], json.dumps(argd))
        ftlog.hinfo('addNotifyInfo timer ntimeId -1', ntimeId, argd)
        dtList = ntime.split('|')
        date = dtList[0]
        if date == getNowDateStr():
            daobase.executeRankCmd('HSET', notify_todayadd_key, argd['uuid'], json.dumps(argd))
            ftlog.hinfo('addNotifyInfo timeradd ntimeId -1', ntimeId, argd)

    elif ntimeId == NOTIFY_TIME_EVERYDAY_ID:
        daobase.executeRankCmd('HSET', notify_key % (ntimeId, hall), argd['uuid'], json.dumps(argd))
        ftlog.hinfo('addNotifyInfo everyday ntimeId 0', ntimeId, argd)
        if ntime <= getNowTimeStr():
            ftlog.hinfo('notify everyday ntime over', typeId, ntimeId, ntime, iconAddr, context, passthrough, platform,
                        buttonType,
                        hall, gameId,
                        package, userId)
        else:
            daobase.executeRankCmd('HSET', notify_todayadd_key, argd['uuid'], json.dumps(argd))
            ftlog.hinfo('addNotifyInfo everydayadd ntimeId 0', ntimeId, argd)
    else:
        daobase.executeRankCmd('HSET', notify_key % (ntimeId, hall), argd['uuid'], json.dumps(argd))
        ftlog.hinfo('addNotifyInfo weekday ntimeId 1-7', ntimeId, argd)
        if ntimeId == getNowWeekdayStr():
            if ntime <= getNowTimeStr():
                ftlog.hinfo('notify weekday ntime over', typeId, ntimeId, ntime, iconAddr, context, passthrough,
                            platform,
                            buttonType,
                            hall, gameId,
                            package, userId)
            else:
                daobase.executeRankCmd('HSET', notify_todayadd_key, argd['uuid'], json.dumps(argd))
                ftlog.hinfo('addNotifyInfo weekdayadd ntimeId 1-7', ntimeId, argd)

    return True


# http调用
def getHallNotifyInfo(hall):
    retList = []
    # 定时
    notify_timerList = daobase.executeRankCmd('HGETALL', notify_timer_key % hall)
    if notify_timerList and len(notify_timerList) > 0:
        for i in xrange(len(notify_timerList) / 2):
            argd = json.loads(notify_timerList[i * 2 + 1])
            retList.append(argd)
    # 每日、周一到周日
    for n in NOTIFY_TIME_REDIS_KEY_LIST:
        notify_everydayList = daobase.executeRankCmd('HGETALL', notify_key % (n, hall))
        if notify_everydayList and len(notify_everydayList) > 0:
            for i in xrange(len(notify_everydayList) / 2):
                argd = json.loads(notify_everydayList[i * 2 + 1])
                retList.append(argd)

    # 立即消息由于持续时间很短,所以暂时不提供查询功能
    # 可以通过daobase.executeRankCmd("HGETALL", notify_todayadd_key)筛选立即消息,当然还得判断时间有效性
    if ftlog.is_debug():
        ftlog.debug('getHallNotifyInfo hallx', hall, retList)
    return retList


# http调用
def delHallNotifyInfo(ntimeId, uuid, hall, ntime):
    if ntimeId == NOTIFY_TIME_TIMER_ID:
        dtList = ntime.split('|')
        date = dtList[0]
        mtime = dtList[1]
        if date == getNowDateStr():
            if mtime > getNowTimeStr():
                argd = daobase.executeRankCmd('HGET', notify_timer_key % hall, uuid)
                if argd:
                    daobase.executeRankCmd('HSET', notify_todaydel_key, uuid, json.dumps(argd))

        return daobase.executeRankCmd('HDEL', notify_timer_key % hall, uuid)

    elif ntimeId in NOTIFY_TIME_REDIS_KEY_LIST:
        if ntimeId == getNowWeekdayStr() or ntimeId == NOTIFY_TIME_EVERYDAY_ID:
            if ntime > getNowTimeStr():
                argd = daobase.executeRankCmd('HGET', notify_key % (ntimeId, hall), uuid)
                if argd:
                    daobase.executeRankCmd('HSET', notify_todaydel_key, uuid, json.dumps(argd))

        return daobase.executeRankCmd('HDEL', notify_key % (ntimeId, hall), uuid)

    elif ntimeId == NOTIFY_TIME_ATONCE_ID:
        # 这个分支属于防御性的,因为查询接口没有提供查询立即消息的功能
        ftlog.hinfo('delHallNotifyInfo atonce', ntimeId, uuid, hall, ntime)
        return True

    ftlog.hinfo('delHallNotifyInfo error', ntimeId, uuid, hall, ntime)
    return False


def initNotifyFromRedis():
    global notify_today_list
    notify_today_list = {}
    serverType = gdata.serverType()

    if serverType == gdata.SRV_TYPE_CENTER:
        # 清空今日通知Redis
        # 新通知
        daobase.executeRankCmd('DEL', notify_todayadd_key)
        # 新删除
        daobase.executeRankCmd('DEL', notify_todaydel_key)

        for hall in hallidList:
            # 定时
            notify_timerList = daobase.executeRankCmd('HGETALL', notify_timer_key % hall)
            if notify_timerList and len(notify_timerList) > 0:
                hremList = []
                for i in xrange(len(notify_timerList) / 2):
                    uuid, notify_timer = notify_timerList[i * 2], notify_timerList[i * 2 + 1]
                    argd = json.loads(notify_timer)
                    dtList = argd['ntime'].split('|')
                    date = dtList[0]
                    ntime = dtList[1]
                    if date == getNowDateStr():
                        if ntime <= getNowTimeStr():
                            hremList.append(uuid)
                    elif date < getNowDateStr():
                        hremList.append(uuid)

                if len(hremList) > 0: daobase.executeRankCmd('HDEL', notify_timer_key % hall, hremList)

    elif serverType == gdata.SRV_TYPE_UTIL:
        for hall in hallidList:
            # 定时
            notify_timerList = daobase.executeRankCmd('HGETALL', notify_timer_key % hall)
            if notify_timerList and len(notify_timerList) > 0:
                for i in xrange(len(notify_timerList) / 2):
                    uuid, notify_timer = notify_timerList[i * 2], notify_timerList[i * 2 + 1]
                    argd = json.loads(notify_timer)
                    dtList = argd['ntime'].split('|')
                    date = dtList[0]
                    ntime = dtList[1]
                    if date == getNowDateStr():
                        if ntime > getNowTimeStr():
                            notify_today_list[argd['uuid']] = Notify(argd)

            # 每天
            notify_everydayList = daobase.executeRankCmd('HGETALL', notify_key % ('0', hall))
            if notify_everydayList and len(notify_everydayList) > 0:
                for i in xrange(len(notify_everydayList) / 2):
                    argd = json.loads(notify_everydayList[i * 2 + 1])
                    if argd['ntime'] <= getNowTimeStr():
                        continue

                    notify_today_list[argd['uuid']] = Notify(argd)

            # 周几
            notify_weekdayList = daobase.executeRankCmd('HGETALL', notify_key % (getNowWeekdayStr(), hall))
            if notify_weekdayList and len(notify_weekdayList) > 0:
                for i in xrange(len(notify_weekdayList) / 2):
                    argd = json.loads(notify_weekdayList[i * 2 + 1])
                    if argd['ntime'] <= getNowTimeStr():
                        continue

                    notify_today_list[argd['uuid']] = Notify(argd)

    for key in notify_today_list:
        ftlog.hinfo('_initialize.Notify:', key, notify_today_list[key])


def _initialize():
    ftlog.hinfo('notifytodaylist initialize begin', datetime.now())
    global _inited
    if not _inited:
        _inited = True
        resetNotifyTodayList()
        ftlog.hinfo('notifytodaylist initialize end', datetime.now())


def resetNotifyTodayList():
    global _update
    date = datetime.now().strftime('%Y-%m-%d')
    if _update != date:
        _update = date
        global _pushed
        _pushed = False
        initNotifyFromRedis()
        _pushed = True
        ftlog.hinfo('resetNotifyTodayList')


def onEventHeartBeat(event):
    resetNotifyTodayList()
def addMatchNotify(gameId, userId, matchName, matchDesc, matchIcon, signinFee, timestamp, matchId, notifyType, gameType,
                   matchIndex):
    '''notifyType[1正常2推荐]'''
    matchNotify = {'gameId': gameId, 'gameType': gameType, 'matchIndex': matchIndex, 'userId': userId,
                   'matchName': matchName,
                   'matchDesc': matchDesc, 'matchIcon': matchIcon, 'signinFee': signinFee, 'timestamp': int(timestamp),
                   'notifyType': notifyType, 'uuid': uuid.uuid1().get_hex(), 'matchId': matchId}
    if ftlog.is_debug():
        ftlog.debug('addMatchNotify',
                    'userId=', userId,
                    'matchNotify=', matchNotify)
    date = datetime.fromtimestamp(timestamp).strftime('%Y%m%d')
    daobase.executeRankCmd('HSET', notify_match_user_date_key % (userId, date), matchId, strutil.dumps(matchNotify))
    daobase.executeRankCmd('SADD', notify_match_user_zset_key % userId, date)
    msg = MsgPack()
    msg.setCmd('hall')
    msg.setResult('action', 'addMatchNotify')
    msg.setResult('gameId', gameId)
    msg.setResult('userId', userId)
    msg.setResult('matchNotify', matchNotify)
    router.sendToUser(msg, userId)
def clearExpireMatchNotify(userId):
    dateList = daobase.executeRankCmd('SMEMBERS', notify_match_user_zset_key % userId)
    if dateList and len(dateList) > 0:
        dateList.sort()
        nowDate = getNowDateStr()
        rmList = []
        for date in dateList:
            if date < nowDate:
                rmList.append(date)
                daobase.executeRankCmd('DEL', notify_match_user_date_key % (userId, date))
        if len(rmList) > 0:
            daobase.executeRankCmd('SREM', notify_match_user_zset_key % userId, *rmList)
def getMatchNotifyList(userId):
    clearExpireMatchNotify(userId)
    matchNotifyList = []
    dateList = daobase.executeRankCmd('SMEMBERS', notify_match_user_zset_key % userId)
    if dateList and len(dateList) > 0:
        dateList.sort()
        for date in dateList:
            retMatchList = daobase.executeRankCmd('HVALS', notify_match_user_date_key % (userId, date))
            if retMatchList and len(retMatchList) > 0:
                for retMatch in retMatchList:
                    try:
                        match = strutil.loads(retMatch)
                        matchNotifyList.append(match)
                    except:
                        ftlog.warn('getMatchNotifyList json loads error',
                                   'userId=', userId,
                                   'match=', retMatch)
    if ftlog.is_debug():
        ftlog.debug('getMatchNotifyList matchNotifyList=', userId, matchNotifyList)
    return matchNotifyList
def clearAllMatchNotify(userId):
    dateList = daobase.executeRankCmd('SMEMBERS', notify_match_user_zset_key % userId)
    if dateList and len(dateList) > 0:
        for date in dateList:
            daobase.executeRankCmd('DEL', notify_match_user_date_key % (userId, date))
    return daobase.executeRankCmd('DEL', notify_match_user_zset_key % userId)
