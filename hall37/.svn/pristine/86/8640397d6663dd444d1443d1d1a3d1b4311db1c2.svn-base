# -*- coding=utf-8
'''
Created on 2017年7月3日

@author: wangzhen

用户每日游戏数据，弱存储数据，每日凌晨即被清空
weakdata.getWeakData(userId, hallconf.HALL_GAMEID, weakdata.CYCLE_TYPE_DAY, key)
用例：用于支持用户每日重复的活动，如每日转盘抽奖次数等。
'''

import time
from poker.entity.dao import weakdata, daobase
from poker.util import strutil


DAILY_DATA_KEY = 'user_dailydata'               # 用户每日数据
SERVER_DAILY_DATA_KEY = 'server_dailydata'      # 服务器每日数据，与单个用户无关,服务器上所有用户共享该数据


def setDailyData(userId, gameId, key, value):
    '''
    设置每日数据
    :param userId:
    :param gameId:
    :param key:
    :param value:
    '''
    dailyData = weakdata.getWeakData(userId, gameId, weakdata.CYCLE_TYPE_DAY, DAILY_DATA_KEY)
    dailyData[key] = value
    weakdata.setWeakData(userId, gameId, weakdata.CYCLE_TYPE_DAY, DAILY_DATA_KEY, dailyData)

def getDailyData(userId, gameId, key, default=None):
    '''
    获取每日数据
    :param userId:
    :param gameId:
    :param key:
    '''
    dailyData = weakdata.getWeakData(userId, gameId, weakdata.CYCLE_TYPE_DAY, DAILY_DATA_KEY)
    return dailyData.get(key, default)

def hasDailyData(userId, gameId, key):
    '''
    每日数据是否存在
    :param userId:
    :param gameId:
    :param key:
    '''
    dailyData = weakdata.getWeakData(userId, gameId, weakdata.CYCLE_TYPE_DAY, DAILY_DATA_KEY)
    return dailyData.has_key(key)



def setServerDailyData(key, value):
    '''
    设置服务器每日数据
    :param key:
    :param value:
    '''
    redisKey = SERVER_DAILY_DATA_KEY + time.strftime("%m%d")
    jsonstr = daobase.executeMixCmd('GET', redisKey)
    data = strutil.loads(jsonstr, ignoreException=True, execptionValue={})
    if not isinstance(data, dict) :
        data = {}
    data[key] = value
    expire = 86400      # 每日数据，最大生命周期为一天
    ret = daobase.executeMixCmd('SETEX', redisKey, expire, strutil.dumps(data))
    return ret

def getServerDailyData(key, default = None):
    '''
    获取服务器每日数据
    :param key:
    :param default:
    '''
    redisKey = SERVER_DAILY_DATA_KEY + time.strftime("%m%d")
    jsonstr = daobase.executeMixCmd('GET', redisKey)
    data = strutil.loads(jsonstr, ignoreException=True, execptionValue={})
    if not isinstance(data, dict) :
        data = {}
    value = data.get(key, default)
    return value

