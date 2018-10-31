# -*- coding: utf-8 -*-
'''
Created on 2017/11/30 10:39
@author: lyj
@file: daily_free_give.py
@desc: 
'''
import json
from freetime.util import log as ftlog
from poker.entity.dao import gamedata
from poker.entity.dao import userchip
from hall.entity.hallconf import HALL_GAMEID
import poker.util.timestamp as pktimestamp
from hall.entity import hallconf, datachangenotify, hallitem
from poker.entity.biz.exceptions import TYBizException

'''
房间配置: dailyFreeGiveEnable -- 该房间是否开启每日赠送
大厅配置: daily_free_give/0.json
    dailyFreeGiveCount: 每日赠送次数
    dailyFreeGiveAmount: 每次赠送多少金币
    dailyFreeGiveLimit: 赠送时检查玩家金币限制
'''
DAILY_FREE_GIVE_CONF_KEY = 'daily_free_give'
DAILY_FREE_GIVE_COUNT = 'dailyFreeGiveCount'
DAILY_FREE_GIVE_AMOUNT = 'dailyFreeGiveAmount'
DAILY_FREE_GIVE_LIMIT = 'dailyFreeGiveLimit'

GAME_DATA_DAILY_FREE_GIVE = 'dailyFreeGive'


_DEBUG = 1 if ftlog.is_debug() else 0

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


class DailyFreeGiveException(TYBizException):
    def __init__(self, ec, message):
        super(DailyFreeGiveException, self).__init__(ec, message)


class NotConfigException(DailyFreeGiveException):
    def __init__(self, message='低保赠送没有配置'):
        super(NotConfigException, self).__init__(-1, message)


class NotValidException(DailyFreeGiveException):
    def __init__(self, message='不满足领取低保赠送的资格'):
        super(NotValidException, self).__init__(-1, message)


class AlreadyRecieveAllException(DailyFreeGiveException):
    def __init__(self, message='每日低保赠送已经全部领取'):
        super(AlreadyRecieveAllException, self).__init__(-1, message)


def getDailyFreeGiveConfig():
    dailyFreeGiveCountConf = hallconf.getDailyFreeGiveConf().get(DAILY_FREE_GIVE_COUNT, 0)
    dailyFreeGiveAmountConf = hallconf.getDailyFreeGiveConf().get(DAILY_FREE_GIVE_AMOUNT, 0)
    dailyFreeGiveLimitConf = hallconf.getDailyFreeGiveConf().get(DAILY_FREE_GIVE_LIMIT, 0)
    debug('dailyFreeGiveCountConf:', dailyFreeGiveCountConf
          , 'dailyFreeGiveAmountConf:', dailyFreeGiveAmountConf
          , 'dailyFreeGiveLimitConf:', dailyFreeGiveLimitConf)
    return dailyFreeGiveCountConf, dailyFreeGiveAmountConf, dailyFreeGiveLimitConf

def loadDailyFreeGiveStatus(userId):
    lastFreeGiveTime, freeGiveCountLeft = 0, 0
    try:
        d = gamedata.getGameAttrJson(userId, HALL_GAMEID, GAME_DATA_DAILY_FREE_GIVE)
        if d:
            lastFreeGiveTime  = d.get('t', 0)
            freeGiveCountLeft = d.get('c', 0)
            debug('userId:', userId, 'lastFreeGiveTime:', lastFreeGiveTime, 'freeGiveCountLeft:', freeGiveCountLeft)
    except:
        ftlog.error()

    return lastFreeGiveTime, freeGiveCountLeft


def saveDailyFreeGiveStatus(userId, lastFreeGiveTime, freeGiveCountLeft):
    d = {'t': lastFreeGiveTime, 'c': freeGiveCountLeft}
    jstr = json.dumps(d)
    debug('saveDailyFreeGiveStatus: userId =', userId
          , 'lastFreeGiveTime =', d['t']
          , 'freeGiveCountLeft =', d['c'])
    gamedata.setGameAttr(userId, HALL_GAMEID, GAME_DATA_DAILY_FREE_GIVE, jstr)

def queryDailyFreeGive(userId, gameId):
    '''
    :desc: 查询每日低保赠送
    :param
    :return: {
        "dailyFreeGiveCountConf": dailyFreeGiveCountConf
        , "dailyFreeGiveAmountConf": dailyFreeGiveAmountConf
        , "dailyFreeGiveLimitConf": dailyFreeGiveLimitConf
        , "freeGiveCountLeft": freeGiveCountLeft
        }
    '''
    retParam = {
        "dailyFreeGiveCountConf": 0,
        "dailyFreeGiveAmountConf": 0,
        "dailyFreeGiveLimitConf": 0,
        "freeGiveCountLeft": 0,
        "canRecieveFreeGive": 0
        }
    debug('queryDailyFreeGive, userId =', userId, 'gameId =', gameId)
    try:
        dailyFreeGiveCountConf, dailyFreeGiveAmountConf, dailyFreeGiveLimitConf = getDailyFreeGiveConfig()
        if dailyFreeGiveCountConf <= 0 or dailyFreeGiveAmountConf <= 0 or dailyFreeGiveLimitConf <= 0:
            debug('daily free give not configured')
            return retParam

        retParam["dailyFreeGiveCountConf"] = dailyFreeGiveCountConf
        retParam["dailyFreeGiveAmountConf"] = dailyFreeGiveAmountConf
        retParam["dailyFreeGiveLimitConf"] = dailyFreeGiveLimitConf

        # 检查今天低保送豆的资格是否已经用完
        lastFreeGiveTime, freeGiveCountLeft = loadDailyFreeGiveStatus(userId)
        if lastFreeGiveTime < pktimestamp.getDayStartTimestamp():
            freeGiveCountLeft = dailyFreeGiveCountConf

        if freeGiveCountLeft <= 0:
            debug('free give count <= 0, userId =', userId, 'freeGiveCountLeft =', freeGiveCountLeft)
            return retParam

        retParam["freeGiveCountLeft"] = freeGiveCountLeft

        # 检查玩家的chip是否低于赠送下限
        chip = userchip.getUserChipAll(userId)
        if chip >= dailyFreeGiveLimitConf:
            debug('user chip bigger then min, userChip =', chip, 'minChip =', dailyFreeGiveLimitConf)
            return retParam

        retParam["canRecieveFreeGive"] = 1

        debug('can give user free chip, userId =', userId
              , 'gameId =', gameId
              , 'lastFreeGiveTime =', lastFreeGiveTime
              , 'freeGiveCountLeft =', freeGiveCountLeft)

        return retParam

    except Exception as e:
        ftlog.error(e)


def receiveDailyFreeGive(userId, gameId):
    '''
    :desc: 领取每日低保赠送
    :param
    :return:
    '''
    debug('receiveDailyFreeGive, userId =', userId, 'gameId =', gameId)
    try:
        dailyFreeGiveCountConf, dailyFreeGiveAmountConf, dailyFreeGiveLimitConf = getDailyFreeGiveConfig()

        if dailyFreeGiveCountConf <= 0 or dailyFreeGiveAmountConf <= 0 or dailyFreeGiveLimitConf <= 0:
            debug('daily free give not configured')
            return None

        # 检查玩家的chip是否低于下限
        chip = userchip.getUserChipAll(userId)
        if chip >= dailyFreeGiveLimitConf:
            debug('user chip bigger then min, userChip =', chip, 'minChip =', dailyFreeGiveLimitConf)
            return None

        # 检查今天低保送豆的资格是否已经用完
        lastFreeGiveTime, freeGiveCountLeft = loadDailyFreeGiveStatus(userId)
        if lastFreeGiveTime < pktimestamp.getDayStartTimestamp():
            freeGiveCountLeft = dailyFreeGiveCountConf

        if freeGiveCountLeft <= 0:
            debug('free give count <= 0, userId =', userId, 'freeGiveCountLeft =', freeGiveCountLeft)
            return None

        debug('can give user free chip, userId =', userId
              , 'gameId =', gameId
              , 'userChip =', userchip
              , 'lastFreeGiveTime =', lastFreeGiveTime
              , 'freeGiveCountLeft =', freeGiveCountLeft)

        # 更新资格
        lastFreeGiveTime, freeGiveCountLeft = pktimestamp.getCurrentTimestamp(), freeGiveCountLeft - 1
        saveDailyFreeGiveStatus(userId, lastFreeGiveTime, freeGiveCountLeft)

        # 低保赠送
        userAssets = hallitem.itemSystem.loadUserAssets(userId)
        assetKind, _addCount, _final = userAssets.addAsset(gameId, 'user:chip', dailyFreeGiveAmountConf, lastFreeGiveTime, 'SZMJ_DAILY_FREE_GIVE_REWARD', 0)

        debug('user receive daily free chip, userId =', userId
              , 'gameId =', gameId
              , 'addCount =', _addCount
              , 'final =', _final
              , 'lastFreeGiveTime =', lastFreeGiveTime
              , 'freeGiveCountLeft =', freeGiveCountLeft)

        changed = []
        if assetKind.keyForChangeNotify:
            changed.append(assetKind.keyForChangeNotify)

        datachangenotify.sendDataChangeNotify(gameId, userId, changed)

        return assetKind, _addCount, _final, freeGiveCountLeft

    except Exception as e:
        ftlog.error(e)


if __name__ == "__main__":
    pass

