# -*- coding:utf-8 -*-
'''
Created on 2016年7月25日

@author: zhaojiangang
'''
import freetime.util.log as ftlog
from hall.servers.util.rpc import match_remote
from hall.servers.util.rpc.match_remote import UserMatchInfo
from poker.entity.biz.content import TYContentItem
from poker.entity.dao import daobase
from poker.util import strutil


def decodeUserMatchInfo(gameId, userId, bigRoomId, jstr):
    d = strutil.loads(jstr)
    if d:
        ret = UserMatchInfo(gameId, userId, bigRoomId)
        ret.state = d['st']
        ret.instId = d['instId']
        ret.ctrlRoomId = d['crid']
        fee = d.get('fee')
        if fee:
            ret.feeItem = TYContentItem.decodeFromDict(fee)
        return ret
    return None

def loadUserMatchInfo(gameId, userId, bigRoomId):
    try:
        key = buildKey(gameId, userId)
        jstr = daobase.executeUserCmd(userId, 'hget', key, bigRoomId)
        if jstr:
            return decodeUserMatchInfo(gameId, userId, bigRoomId, jstr)
        return None
    except:
        ftlog.error('match_remote.loadUserMatchInfo gameId=', gameId,
                    'userId=', userId,
                    'bigRoomId=', bigRoomId)
        return None
    
def saveUserMatchInfo(info):
    d = {
        'st':info.state,
        'instId':info.instId,
        'crid':info.ctrlRoomId
    }
    if info.feeItem:
        d['fee'] = info.feeItem.toDict()
    jstr = strutil.dumps(d)
    key = buildKey(info.gameId, info.userId)
    daobase.executeUserCmd(info.userId, 'hset', key, info.bigRoomId, jstr)
    
def removeUserMatchInfo(info):
    key = buildKey(info.gameId, info.userId)
    daobase.executeUserCmd(info.userId, 'hdel', key, info.bigRoomId)
    

def buildKey(gameId, userId):
    return 'minfo:%s:%s' % (gameId, userId)

match_remote.loadUserMatchInfoOld = match_remote.loadUserMatchInfo
match_remote.loadUserMatchInfo = loadUserMatchInfo

match_remote.removeUserMatchInfoOld = match_remote.removeUserMatchInfo
match_remote.removeUserMatchInfo = removeUserMatchInfo

match_remote.saveUserMatchInfoOld = match_remote.saveUserMatchInfo
match_remote.saveUserMatchInfo = saveUserMatchInfo

