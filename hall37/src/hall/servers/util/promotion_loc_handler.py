# -*- coding=utf-8
'''
Created on 2015年8月3日

@author: zhaojiangang
'''
from datetime import datetime
import freetime.util.log as ftlog
from freetime.entity.msg import MsgPack
from hall.entity import hallpromote
from hall.servers.common.base_checker import BaseMsgPackChecker
from poker.protocol import router
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod
import poker.util.timestamp as pktimestamp
from hall.entity.todotask import TodoTaskHelper
from hall.entity.hallconf import HALL_GAMEID


class PromotionHelper(object):
    @classmethod
    def encodePromote(cls, gameId, userId, clientId, promote):
        try:
            todotasks = TodoTaskHelper.makeTodoTasksByFactory(gameId, userId, clientId, promote.promotion.todotasks)
            tempRedPoint = False
            timestamp = pktimestamp.getCurrentTimestamp()
            ftlog.debug('promote.promotion.redPoint =', promote.promotion.redPoint)
            for d in promote.promotion.redPoint:
                if d:
                    tempRedPoint = d.check(HALL_GAMEID, userId, clientId, timestamp)
            ret = {
                'id':promote.promotion.promotionId,
                'loc':promote.position.pos,
                'name':promote.promotion.displayName,
                'url':promote.promotion.url,
                'defaultRes':promote.promotion.defaultRes,
                'animate':promote.promotion.animate,
                'redPoint':tempRedPoint,
                'tasks':TodoTaskHelper.encodeTodoTasks(todotasks)
            }
            if promote.stopTime != -1:
                ret['endtime'] = datetime.fromtimestamp(promote.stopTime).strftime('%Y-%m-%d %H:%M:%S')
            return ret
        except:
            ftlog.error('PromotionHelper.encodePromote gameId=', gameId,
                        'userId=', userId,
                        'clientId=', clientId,
                        'promotionId=', promote.promotion.promotionId)
            return None
        
    @classmethod
    def encodePromoteList(cls, gameId, userId, clientId, promoteList):
        ret = []
        for promote in promoteList:
            p = cls.encodePromote(gameId, userId, clientId, promote)
            if p:
                ret.append(p)
        return ret
    
    @classmethod
    def makePromotionUpdateResponse(cls, gameId, userId, clientId, promoteList):
        mo = MsgPack()
        mo.setCmd('promotion_loc')
        mo.setResult('action', 'update')
        mo.setResult('promotions', cls.encodePromoteList(gameId, userId, clientId, promoteList))
        return mo
    
@markCmdActionHandler
class PromotionTcpHandler(BaseMsgPackChecker):
    def __init__(self):
        super(PromotionTcpHandler, self).__init__()
    
    @markCmdActionMethod(cmd='promotion_loc', action="update", clientIdVer=0)
    def doUpdate(self, gameId, userId, clientId):
        timestamp = pktimestamp.getCurrentTimestamp()
        promoteList = hallpromote.getPromotes(gameId, userId, clientId, timestamp)
        mo = PromotionHelper.makePromotionUpdateResponse(gameId, userId, clientId, promoteList)
        router.sendToUser(mo, userId)


