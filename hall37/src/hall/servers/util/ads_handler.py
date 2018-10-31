# -*- coding=utf-8
'''
Created on 2015年8月13日

@author: zhaojiangang
'''

from freetime.entity.msg import MsgPack
from hall.entity import hallads
from hall.servers.common.base_checker import BaseMsgPackChecker
from poker.protocol import router
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod
from hall.entity.todotask import TodoTaskHelper
import freetime.util.log as ftlog
import poker.util.timestamp as pktimestamp

class AdsHelper(object):
    @classmethod
    def encodeAds(cls, gameId, userId, clientId, ads):
        ret = {
            'id':ads.adsId,
            'clickable':ads.clickable,
            'pic':ads.pic
        }
        if ads.clickable and ads.todotasks:
            todotasks = []
            for todotaskFac in ads.todotasks:
                todotask = todotaskFac.newTodoTask(gameId, userId, clientId)
                if todotask:
                    todotasks.append(todotask)
            if todotasks:
                ret['tasks'] = TodoTaskHelper.encodeTodoTasks(todotasks)
        return ret
    
    @classmethod
    def encodeAdsList(cls, gameId, userId, clientId, adsList):
        ret = []
        for ads in adsList:
            if ftlog.is_debug():
                ftlog.debug('adsId=', ads.adsId,
                        'adsclickable=', ads.clickable,
                        'adspic=', ads.pic,
                        'adsstartDT=', ads.startDT,
                        'adsendDT', ads.endDT,
                        'adstodotask=', ads.todotasks,
                        'adscondition=', ads.condition)
            if not hallads.checkAds(gameId, userId, clientId, ads, pktimestamp.getCurrentTimestamp()):
                continue
            ret.append(cls.encodeAds(gameId, userId, clientId, ads))
        return ret
    
    @classmethod
    def encodeAdsTemplate(cls, gameId, userId, clientId, adsTemplate):
        return {
            'interval':adsTemplate.interval,
            'items':cls.encodeAdsList(gameId, userId, clientId, adsTemplate.adsList)
        }
    
    @classmethod
    def makeAdsQueryResponse(cls, gameId, userId, clientId, adsTemplate):
        mo = MsgPack()
        mo.setCmd('ads')
        mo.setResult('action', 'query')
        mo.setResult('gameId', gameId)
        mo.setResult('userId', userId)
        mo.setResult('ads', cls.encodeAdsTemplate(gameId, userId, clientId, adsTemplate))
        return mo

@markCmdActionHandler
class AdsHandler(BaseMsgPackChecker):
    def __init__(self):
        super(AdsHandler, self).__init__()
        
    @markCmdActionMethod(cmd='ads', action="query", clientIdVer=0)
    def doAdsQuery(self, gameId, userId, clientId):
        adsTemplate = hallads.queryAds(gameId, userId, clientId)
        mo = AdsHelper.makeAdsQueryResponse(gameId, userId, clientId, adsTemplate)
        router.sendToUser(mo, userId)
        
            
