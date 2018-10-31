# -*- coding=utf-8
'''
Created on 2015年12月16日

@author: wuyongsheng
'''
from freetime.entity.msg import MsgPack
from hall.entity import lottery
from hall.servers.common.base_checker import BaseMsgPackChecker 
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod
from poker.protocol import  router,runcmd
import freetime.util.log as ftlog


class LotteryHelper(object):
    @classmethod
    def encodeLottery(cls, gameId, userId, clientId, itemLottery):
        ret = {
            'lotteryId':itemLottery.lotteryId,
            'picUrl':itemLottery.picUrl
        }
        return ret
    
    @classmethod
    def encodeLotteryList(cls, gameId, userId, clientId, itemList):
        ret = []
        for d in itemList:
            ret.append(cls.encodeLottery(gameId, userId, clientId, d))
        return ret
    
    @classmethod
    def encodeLotteryTemplate(cls, gameId, userId, clientId, lotteryTemplate):
        return cls.encodeLotteryList(gameId, userId, clientId, lotteryTemplate.items)
    
    @classmethod
    def makeLotteryQueryResponse(cls, gameId, userId, clientId, lotteryTemplate):
        mo = MsgPack()
        mo.setCmd('lottery')
        mo.setResult('action', 'lottery_update')
        mo.setResult('gameId', gameId)
        mo.setResult('userId', userId)
        mo.setResult('result', lotteryTemplate)
        return mo
    @classmethod
    def getResponseMsg(cls,result,gameId,userId,action):
        mo = MsgPack()
        mo.setCmd('lottery')     
        mo.setResult("gameId", gameId)
        mo.setResult("userId", userId)
        mo.setResult("action", action)
        if not result:
            result = {"errorInfo":"unknown action", "errorCode":1}
        for key in result:
            mo.setResult(key, result[key])
        return mo

@markCmdActionHandler
class LotteryHandler(BaseMsgPackChecker):
    def __init__(self):
        super(LotteryHandler, self).__init__()
    
    @markCmdActionMethod(cmd='lottery', action="lottery_card", clientIdVer=0)
    def doLotteryCardQuery(self, gameId, userId, clientId):
        msg = runcmd.getMsgPack()
        result = lottery.handleLotteryRequest(userId, gameId, clientId, msg)  
        mo = LotteryHelper.getResponseMsg(result, gameId, userId,'lottery_card')
        router.sendToUser(mo, userId)
        
    @markCmdActionMethod(cmd='lottery', action="lottery_chip", clientIdVer=0)
    def doLotteryChipQuery(self, gameId, userId, clientId):
        msg = runcmd.getMsgPack()
        result = lottery.handleLotteryRequest(userId, gameId, clientId, msg)  
        mo = LotteryHelper.getResponseMsg(result, gameId, userId,'lottery_chip')
        router.sendToUser(mo, userId)
        
    @markCmdActionMethod(cmd='lottery', action="lottery_update", clientIdVer=0)
    def doLotteryUpdateQuery(self, gameId, userId, clientId):
        lotteryTemplate = lottery.queryLottery(gameId, userId, clientId)
        mo = LotteryHelper.makeLotteryQueryResponse(gameId, userId, clientId, lotteryTemplate)
        router.sendToUser(mo, userId)
    
    
        
            
