# -*- coding: utf-8 -*-
import functools
import json

import datetime

import freetime.util.log as ftlog
import poker.util.timestamp as pktimestamp
from freetime.core.tasklet import FTTasklet
from freetime.core.timer import FTTimer
from poker.entity.biz import bireport
from poker.entity.configure import configure
from dizhu.entity.official_counts.dao import official_dao
from dizhu.entity.dizhuconf import DIZHU_GAMEID, PROMOTE, WITHDRAW, RED_ENVELOPE
from dizhu.entity.official_counts.events import OfficialMessageEvent
from poker.entity.dao import onlinedata, userdata
from poker.entity.events.tyevent import EventHeartBeat
from poker.util import webpage, strutil
from poker.entity.dao import daobase


ACTIVE_USER_LIST_KEY = 'wxActiveUserList2'

def getActiveUserList():
    ret = daobase.executeRePlayCmd('GET', ACTIVE_USER_LIST_KEY)
    if not ret:
        return []
    if ftlog.is_debug():
        ftlog.debug('wx_official.getActiveUserList',
                    'activeUserList=', ret)
    return ret


def doRankInfo(userId, rankDict):
    official_dao.setRank(userId, DIZHU_GAMEID, json.dumps(rankDict))

def getRankInfo(userId):
    try:
        rankInfo = official_dao.getRank(userId, DIZHU_GAMEID)
        rankInfo = json.loads(rankInfo) if rankInfo else {}
    except Exception, e:
        ftlog.warn('wx_official.getRankInfo userId=', userId,
                   'err=', e.message)
        return {}
    if ftlog.is_debug():
        ftlog.debug('wx_official.getRankInfo',
                    'userId=', userId,
                    'rankInfo=', rankInfo,
                    'type(rankInfo)=', type(rankInfo))
    return rankInfo


def filterNotActiveUserToSend(evt, userIdList):
    ret = getActiveUserList() or ''
    friendsToSend = [userId for userId in userIdList if str(userId) in ret.split(',')]
    if ftlog.is_debug():
        ftlog.debug('wx_official.filterNotActiveUserToSend',
                    'userId=', evt.userId,
                    'eventId= ', evt.eventId,
                    'friendsToSend=', friendsToSend)
    return friendsToSend


def filterOfflineToSend(evt):
    rankInfo = getRankInfo(evt.userId)
    if not rankInfo:
        return []
    if evt.eventId == PROMOTE:
        rankInfo = evt.kwargs.get('rankInfo', {})
        userIds = [userId for userId in rankInfo if
                (userId != str(evt.userId) and rankInfo[str(userId)] == rankInfo[str(evt.userId)])]
    else:
        userIds = [userId for userId in rankInfo if userId != str(evt.userId)]
    friendsToSend = [int(userId) for userId in userIds if not onlinedata.getOnlineState(int(userId))]
    if ftlog.is_debug():
        ftlog.debug('wx_official.filterOfflineToSend',
                    'userId=', evt.userId,
                    'eventId= ', evt.eventId,
                    'rankInfo=', rankInfo,
                    'userIds=', userIds,
                    'friendsToSend=', friendsToSend)
    return friendsToSend


def subscribeOfficialMessageEvent():
    from hall.game import TGHall
    TGHall.getEventBus().subscribe(OfficialMessageEvent, _processOfficialMessage)


def _processOfficialMessage(evt):
    switch = configure.getGameJson(DIZHU_GAMEID, 'official.message', {}).get('switch')
    if not switch:
        return
    FTTimer(0, functools.partial(processMessage, evt))

def processMessage(evt):
    if ftlog.is_debug():
        ftlog.debug('wx_official._processOfficialMessage',
                    'eventId= ', evt.eventId,
                    'userId= ', evt.userId,
                    'gameId= ', evt.gameId)
    eventId = evt.eventId
    now = pktimestamp.getCurrentTimestamp()
    try:
        friendsToSend = filterOfflineToSend(evt)
        friendsToSend = filterNotActiveUserToSend(evt, friendsToSend)
        if configure.getGameJson(DIZHU_GAMEID, 'official.message', {}).get('testUserIds'):
            friendsToSend = configure.getGameJson(DIZHU_GAMEID, 'official.message', {}).get('testUserIds')
        if not friendsToSend:
            return
    except Exception, e:
        ftlog.warn('wx_official._processOfficialMessage userId=', evt.userId, 'filterOfflineToSend error', 'err=', e.message)
        return

    conf = configure.getGameJson(DIZHU_GAMEID, 'official.message', {}).get('templates', {}).get(evt.eventId)
    if not conf:
        return
    if ftlog.is_debug():
        ftlog.debug('wx_official._processOfficialMessage',
                    'userId=', evt.userId,
                    'eventId= ', evt.eventId,
                    'friendsToSend=', friendsToSend,
                    'conf=', conf)
    for targetUserId in friendsToSend:
        try:
            ret, needReloadRecord = _checkSendCondition(targetUserId, evt.gameId, eventId, now, configure.getGameJson(DIZHU_GAMEID, 'official.message', {}))
            if ftlog.is_debug():
                ftlog.debug('wx_official._processOfficialMessage',
                            'userId=', evt.userId,
                            'eventId= ', evt.eventId,
                            'ret=', ret,
                            'needReloadRecord=', needReloadRecord)
            if not ret:
                continue

            gdssUrl = 'http://gdss.touch4.me/?act=wxCommonApi.sendCsMsgFromGameComm'
            parasDict = {}
            parasDict['appid'] = 'wx992c1fb532d3bff3'
            parasDict['userId'] = targetUserId
            parasDict['wxgameappid'] = 'wx785e80cff6120de5'
            userName, _ = userdata.getAttrs(evt.userId, ['name', 'purl'])
            evt.msgParams.update({'userName': userName})
            parasDict['msg'] = strutil.replaceParams(conf.get('msg'), evt.msgParams)
            parasDict['needmsg'] = conf.get('needmsg')
            parasDict['needcard'] = conf.get('needcard')
            if eventId == RED_ENVELOPE:
                mixId = evt.kwargs.get('mixId', 0)
                parasDict['mediaid'] = conf.get('mediaid').get(str(mixId)) if parasDict['needcard'] else ''
            else:
                parasDict['mediaid'] = conf.get('mediaid') if parasDict['needcard'] else ''
            parasDict['cardtitle'] = conf.get('cardtitle') if parasDict['needcard'] else ''
            hbody, _ = webpage.webgetGdss(gdssUrl, parasDict)
            resJson = json.loads(hbody)
            retcode = resJson.get('retcode', -1)
            retmsg = resJson.get('retmsg', '消息推送出错')
            if retcode == -1:
                if ftlog.is_debug():
                    ftlog.debug('wx_official._processOfficialMessage sent fail',
                                'userId=', evt.userId,
                                'eventId= ', evt.eventId,
                                'targetUserId=', targetUserId,
                                'retcode=', retcode,
                                'retmsg=', retmsg,
                                'ret=', ret,
                                'needReloadRecord=', needReloadRecord)
                continue
            bireport.reportGameEvent('WX_OFFICIAL',
                                     evt.userId,
                                     evt.gameId,
                                     0,
                                     0,
                                     0,
                                     0, 0, 0, [evt.eventId, targetUserId],
                                     0,
                                     0,
                                     0)
            if not needReloadRecord:
                official_dao.delOfficialPushRecord(targetUserId, evt.gameId)
            official_dao.setOfficialPushRecord(targetUserId, evt.gameId, json.dumps({eventId: now}))
            if ftlog.is_debug():
                ftlog.debug('wx_official._processOfficialMessage sent success',
                            'userId=', evt.userId,
                            'eventId= ', evt.eventId,
                            'targetUserId=', targetUserId,
                            'retcode=', retcode,
                            'retmsg=', retmsg,
                            'ret=', ret,
                            'needReloadRecord=', needReloadRecord)
            FTTasklet.getCurrentFTTasklet().sleepNb(0.5)
        except Exception, e:
            if ftlog.is_debug():
                ftlog.error('wx_official._processOfficialMessage sent error',
                            'userId=', evt.userId,
                            'eventId= ', evt.eventId,
                            'targetUserId=', targetUserId,
                            'error=', e.message)
            continue


def _checkSendCondition(userId, gameId, eventId, timeStamp, conf):
    startTime = configure.getGameJson(DIZHU_GAMEID, 'official.message', {}).get('startTime')
    stopTime = configure.getGameJson(DIZHU_GAMEID, 'official.message', {}).get('stopTime')
    start = datetime.datetime.strptime(startTime, "%H:%M").time()
    stop = datetime.datetime.strptime(stopTime, "%H:%M").time()
    now = datetime.datetime.now().time()
    if start >= stop or now < start or now > stop:
        if ftlog.is_debug():
            ftlog.debug('wx_official._checkSendCondition',
                        'userId=', userId,
                        'gameId=', gameId,
                        'start=', start,
                        'stop=', stop,
                        'now=', now,
                        'eventId=', eventId)
        return None, None
    hasSend = official_dao.getOfficialPushRecord(userId, gameId)
    if not hasSend:
        return 1, 'ok'
    hasSendAttrNames = [json.loads(i).keys()[0] for i in hasSend]
    hasSendTimes = [json.loads(i).values()[0] for i in hasSend]
    if not pktimestamp.is_same_day(timeStamp, hasSendTimes[-1]):
        return 1, None
    if timeStamp - hasSendTimes[-1] < conf.get('timeInterval'):
        return None, None
    if len(hasSend) < conf.get('dayTimes'):
        if hasSendAttrNames.count(eventId) < conf['templates'][eventId]['count']:
            return 1, 'ok'
    return None, None


def _initialize(isCenter):
    ftlog.info('wx_official._initialize begin')
    subscribeOfficialMessageEvent()
    if isCenter:
        from poker.entity.events.tyeventbus import globalEventBus
        globalEventBus.subscribe(EventHeartBeat, _onTimer)
    ftlog.info('wx_official._initialize end')


_processGetActiveUserListInterval = 3600 * 2   # 每 2 小时处理一次
_prevGetActiveUserListTimestamp = 0


def _onTimer(evt):
    global _prevGetActiveUserListTimestamp
    timestamp = pktimestamp.getCurrentTimestamp()
    if not _prevGetActiveUserListTimestamp or timestamp - _prevGetActiveUserListTimestamp > _processGetActiveUserListInterval:
        _prevGetActiveUserListTimestamp = timestamp
        _getActiveUserList()

def _getActiveUserList():
    ''' 获取公众号用户列表 '''
    FTTimer(0, _getActiveUserListByTimer)

def _getActiveUserListByTimer():
    try:
        gdssUrl = 'http://gdss.touch4.me/?act=wxCommonApi.getActiveUserList&appid=wx992c1fb532d3bff3'
        userListInfo, _ = webpage.webgetGdss(gdssUrl, {})
        userListInfo = json.loads(userListInfo)
        retcode = userListInfo.get('code')
        data = userListInfo.get('data')
        if retcode == 1 and data:
            daobase.executeRePlayCmd('SET', ACTIVE_USER_LIST_KEY, data)
            if ftlog.is_debug():
                ftlog.debug('wx_official._getActiveUserList',
                            'activeUserList=', data[:50],
                            '......')
    except Exception, e:
        ftlog.error('wx_official._getActiveUserListByTimer err=', e.message)

def _isActive(userId):
    try:
        gdssUrl = 'http://gdss.touch4.me/?act=wxCommonApi.getActiveUserList&appid=wx992c1fb532d3bff3'
        userListInfo, _ = webpage.webgetGdss(gdssUrl, {})
        userListInfo = json.loads(userListInfo)
        retcode = userListInfo.get('code')
        data = userListInfo.get('data')
        if retcode == 1 and data:
            if str(userId) in data:
                return 1
        return 0
    except Exception, e:
        ftlog.error('wx_official._isActive err=', e.message)
        return 0