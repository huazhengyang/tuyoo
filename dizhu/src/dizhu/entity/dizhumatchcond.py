# -*- coding:utf-8 -*-
'''
Created on 2016年3月25日

@author: zhaojiangang
'''
from sre_compile import isstring

from dizhu.entity.dizhuconf import DIZHU_GAMEID
import freetime.util.log as ftlog
from hall.entity.hallusercond import UserConditionRegister
from poker.entity.biz.exceptions import TYBizConfException
from poker.entity.configure import configure, gdata
from poker.entity.dao import sessiondata
import poker.util.timestamp as pktimestamp


class MatchCondition(object):
    def __init__(self):
        self.failure = None
        self.condition = None
        
    def check(self, gameId, userId, clientId, timestamp):
        if not self.condition.check(gameId, userId, clientId, timestamp):
            return False
        return True
    
    def decodeFromDict(self, d):
        self.failure = d.get('failure', '')
        if not isstring(self.failure):
            raise TYBizConfException(d, 'MatchCondition.failure must be string')
        self.condition = UserConditionRegister.decodeFromDict(d.get('condition'))
        return self
    
    @classmethod
    def decodeList(cls, l):
        ret = []
        for d in l:
            ret.append(MatchCondition().decodeFromDict(d))
        return ret

def checkMatchSigninCond(userId, roomId):
    if userId <= 10000:
        # 机器人不检查
        return True, None
    
    matchCondConf = configure.getGameJson(DIZHU_GAMEID, 'bigmatch.filter', {})
    if not matchCondConf:
        if ftlog.is_debug():
            ftlog.debug('dizhumatchcond.checkMatchSigninCond EmptyMatchCondConf roomId=', roomId,
                        'gameId=', DIZHU_GAMEID,
                        'userId=', userId,
                        'matchCondConf=', matchCondConf)
        return True, None

    bigRoomId = gdata.getBigRoomId(roomId)
    condConf = matchCondConf.get(str(bigRoomId))
    
    if ftlog.is_debug():
        ftlog.debug('dizhumatchcond.checkMatchSigninCond roomId=', roomId,
                    'gameId=', DIZHU_GAMEID,
                    'userId=', userId,
                    'bigRoomId=', bigRoomId,
                    'condConf=', condConf,
                    'matchCondConf=', matchCondConf)
        
    if condConf:
        clientId = sessiondata.getClientId(userId)
        timestamp = pktimestamp.getCurrentTimestamp()
        cond = MatchCondition().decodeFromDict(condConf)
        if not cond.check(DIZHU_GAMEID, userId, clientId, timestamp):
            return False, cond
    return True, None


