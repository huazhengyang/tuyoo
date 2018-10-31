# -*- coding:utf-8 -*-

import json

import freetime.util.log as ftlog
from dizhu.entity.dizhuconf import DIZHU_GAMEID
from hall.entity.hallevent import HallShare3Event
from hall.game import TGHall
from poker.entity.dao import gamedata
import poker.util.timestamp as pktimestamp


class UserShareCountData(object):
    ''' 用户分享数据 '''
    def __init__(self, userId):
        self.userId = userId
        self.dailyCount = None
        self.totalCount = None
        self.timestamp = None

    def loadData(self):
        shareDataStr = gamedata.getGameAttr(self.userId, DIZHU_GAMEID, 'userShareData')
        if not shareDataStr:
            self.dailyCount = 0
            self.totalCount = 0
            self.timestamp = pktimestamp.getCurrentTimestamp()
        else:
            shareDataDict = json.loads(shareDataStr)
            self.dailyCount = shareDataDict.get('dailyCount', 0)
            self.totalCount = shareDataDict.get('totalCount', 0)
            self.timestamp = shareDataDict.get('timestamp', 0)

        if not pktimestamp.is_same_day(self.timestamp, pktimestamp.getCurrentTimestamp()):
            self.dailyCount = 0
            self.timestamp = pktimestamp.getCurrentTimestamp()
            self.saveData()
        return self

    def saveData(self):
        savedDict = {
            'dailyCount': self.dailyCount,
            'totalCount': self.totalCount,
            'timestamp': self.timestamp
        }
        gamedata.setGameAttr(self.userId, DIZHU_GAMEID, 'userShareData', json.dumps(savedDict))


def getTotalShareTimes(userId):
    return UserShareCountData(userId).loadData().totalCount


def getDayShareTimes(userId):
    return UserShareCountData(userId).loadData().dailyCount


def increaseShareTimes(userId):
    userShareCount = UserShareCountData(userId).loadData()
    userShareCount.dailyCount += 1
    userShareCount.totalCount += 1
    userShareCount.saveData()


def _initialize():
    ftlog.debug('dizhu_share_count._initialize begin')
    TGHall.getEventBus().subscribe(HallShare3Event, _processHallShare3Event)
    ftlog.debug('dizhu_share_count._initialize end')


def _processHallShare3Event(evt):
    if ftlog.is_debug():
        ftlog.debug('dizhu_share_count._processHallShare3Event userId=', evt.userId)
    increaseShareTimes(evt.userId)
