# -*- coding: utf-8 -*-
"""
Created on 2017年11月28日

@author: lyj
"""
import json
import time
from datetime import datetime
import freetime.util.log as ftlog
import poker.util.timestamp as pktimestamp
from hall.entity import datachangenotify, hallitem
from poker.entity.biz.exceptions import TYBizException
from poker.entity.dao import gamedata
from poker.entity.events.tyevent import UserEvent
from hall.entity import hallconf

def __ftlog_dummy__(*argl, **argd):
    pass

debug = ftlog.debug if ftlog.is_debug() else __ftlog_dummy__

class SevenDaysCheckinException(TYBizException):
    def __init__(self, ec, message):
        super(SevenDaysCheckinException, self).__init__(ec, message)

class InvalidCheckinException(SevenDaysCheckinException):
    def __init__(self, message='非法签到'):
        super(InvalidCheckinException, self).__init__(-1, message)

class AlreadyCheckinException(SevenDaysCheckinException):
    def __init__(self, message='已经签过到'):
        super(AlreadyCheckinException, self).__init__(-1, message)


class AlreadyGetRewardException(SevenDaysCheckinException):
    def __init__(self, message='奖励已经领取'):
        super(AlreadyGetRewardException, self).__init__(-1, message)


class SevenDaysCheckinStatus(object):
    def __init__(self, userId, gameId, firstCheckInTime, lastCheckInTime, checkInDays):
        self._userId = userId
        self._gameId = gameId
        self._firstCheckInTime = firstCheckInTime  # 本周期第一次签到当天0点0分
        self._lastCheckInTime = lastCheckInTime  #timestamp
        self._checkInDays = checkInDays #int

    @property
    def userId(self):
        return self._userId

    @property
    def gameId(self):
        return self._gameId

    @property
    def getFirstCheckInTime(self):
        return self._firstCheckInTime

    @property
    def getLastCheckInTime(self):
        return self._lastCheckInTime

    @property
    def getCheckInDays(self):
        return self._checkInDays

    def isTodayCheckined(self):
        '''
        判断今天是否已经签过到了
        '''
        return pktimestamp.is_same_day(pktimestamp.getCurrentTimestamp(), self._lastCheckInTime)

    def doCheckIn(self):
        '''
        签到
        '''
        if self.isTodayCheckined():
            debug('today has checkined!')
            return False
        else:
            if self._checkInDays == 0:
                self._firstCheckInTime = pktimestamp.getDayStartTimestamp()

            self._lastCheckInTime = pktimestamp.getCurrentTimestamp()
            self._checkInDays += 1
            debug('checkined! checkInDays =', self._checkInDays)
            return True

    def adjust(self):
        '''
        从每周1开始，周日结束，算一周
        '''
        if self._firstCheckInTime + 604800 < pktimestamp.getCurrentTimestamp():
            self._checkInDays = 0

        return self

    def modify(self, firstCheckInTime, lastCheckInTime, checkInDays):
        self._firstCheckInTime = firstCheckInTime
        self._lastCheckInTime = lastCheckInTime
        self._checkInDays = checkInDays
        return self.adjust()


class SevenDaysCheckinEvent(UserEvent):
    def __init__(self, userId, gameId, status):
        super(SevenDaysCheckinEvent, self).__init__(userId, gameId)
        self.status = status


class SevenDaysCheckinOkEvent(SevenDaysCheckinEvent):
    def __init__(self, userId, gameId, status, checkinDate):
        super(SevenDaysCheckinOkEvent, self).__init__(userId, gameId, status)
        self.checkinDate = checkinDate


class DaysRewardGotEvent(SevenDaysCheckinEvent):
    def __init__(self, userId, gameId, status, days):
        super(DaysRewardGotEvent, self).__init__(userId, gameId, status)
        self.days = days


def _loadStatus(userId, gameId):
    try:
        d = gamedata.getGameAttrJson(userId, gameId, 'sevenDaysCheckin')
        if d:
            fct = d.get('fct', 0)
            lct = d.get('lct', 0)
            cd  = d.get('cd' , 0)
            debug('firstCheckInTime', fct, 'lastCheckInTime:', lct, 'checkInDays:', cd)
            status = SevenDaysCheckinStatus(userId, gameId, fct, lct, cd)
            return status
    except:
        ftlog.error()
    return None


def _saveStatus(status):
    d = {'fct':status.getFirstCheckInTime, 'lct': status.getLastCheckInTime, 'cd': status.getCheckInDays}
    jstr = json.dumps(d)
    debug('_saveStatus: userId =', status.userId
          , 'gameId =', status.gameId
          , 'fct =', d['fct']
          , 'lct =', d['lct']
          , 'cd =',  d['cd'])
    gamedata.setGameAttr(status.userId, status.gameId, 'sevenDaysCheckin', jstr)


_sevenDaysCheckinConf = None

def getConf(gameId):
    global _sevenDaysCheckinConf
    _sevenDaysCheckinConf = hallconf.get_game_config(gameId, 'sevendayscheckin')
    if not _sevenDaysCheckinConf:
        raise InvalidCheckinException
    return _sevenDaysCheckinConf


def loadStatus(userId, gameId):
    '''
    返回用户的签到状态
    @param userId: 用户ID
    @param timestamp: 当前时间戳
    @return: SevenDaysCheckinStatus
    '''
    status = _loadStatus(userId, gameId)
    if status:
        return status.adjust()
    else:
        return SevenDaysCheckinStatus(userId, gameId, 0, 0, 0)


def checkin(userId, gameId, clientId, nowDate=None):
    '''
    用户签到
    @param userId: 用户ID
    @param nowDate: 当前日期
    @return: SevenDaysCheckinStatus
    '''
    from hall.game import TGHall

    nowDate = nowDate or datetime.now().date()
    status = loadStatus(userId, gameId)

    if not status.doCheckIn():
        debug('doCheckIn failed, userId =', status.userId
              , 'gameId =', status.gameId
              , 'lastCheckInTime =', status.getLastCheckInTime)
        raise AlreadyCheckinException('亲，你已经领取过签到奖励了！')

    _saveStatus(status)

    # 自动领奖
    days = status.getCheckInDays
    getDaysReward(userId, days, gameId)

    TGHall.getEventBus().publishEvent(SevenDaysCheckinOkEvent(userId, gameId, status, nowDate))

    debug('checkin userId =', userId
               , 'gameId =', gameId
               , 'clientId =', clientId)

    return status

def getDaysReward(userId, days, gameId, nowDate=None):
    '''
    领取累计签到奖励
    @param userId: 用户ID
    @param days: 领取累计几天的奖励
    @param nowDate: 当前日期
    @return:
    '''
    dayRewards =  getConf(gameId).get('daysRewards', {})

    dayToGift(days, dayRewards, userId, gameId)

    debug('getDaysReward userId =', userId
               , 'days =', days
               , 'gameId =', gameId
               , 'nowDate =', nowDate)


def dayToGift(days, rewards, userId, gameId):
    for _k, v in enumerate(rewards):
        if v.get('days', 0) == days:
            reward = v.get('reward', {})
            items = reward.get("items", [])
            sendGiftToUser(days, items, userId, gameId)
            break


def sendGiftToUser(days, item, userId, gameId):
    debug('dayToGift userId =', userId
               , 'item =', item
               , 'gameId =', gameId
               , 'userId =', userId)
    userAssets = hallitem.itemSystem.loadUserAssets(userId)

    changed = []
    for _k, v in enumerate(item):
        assetKind, _addCount, _final = userAssets.addAsset(gameId, v.get("itemId"), v.get("count"), int(time.time()),
                                                           'SZMJ_SEVEN_DAYS_CHECKIN_REWARD', days)
        if assetKind.keyForChangeNotify:
            changed.append(assetKind.keyForChangeNotify)

    datachangenotify.sendDataChangeNotify(gameId, userId, changed)
