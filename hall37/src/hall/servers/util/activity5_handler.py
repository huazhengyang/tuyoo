# -*- coding: utf-8 -*-
'''
Created on 2015年5月20日

@author: zqh
'''


from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
import hall.entity.hallactivity.activity as activity
from hall.servers.common.base_checker import BaseMsgPackChecker
from poker.protocol import router, runcmd
from poker.protocol.decorator import markCmdActionMethod, markCmdActionHandler
from poker.entity.configure import configure
from hall.servers.util.store_handler import StoreHelper


def _doActivity5ActMsgList(gameId, userId, clientId):
    activityList = activity.activitySystem.getActivityList(gameId, userId, clientId)
    return activityList


def _doActivity5CityMsgList(gameId, userId, clientId):
    datas = configure.getTcContent('activity.city', None, clientId)
    if datas:
        return datas['datas']
    return []


def _doActivity5PrizeMsgList(gameId, userId, clientId):
    datas = configure.getTcContent('activity.prize', None, clientId)
    if datas:
        return datas['datas']
    return []


def _doActivity5ExchangeItemList(gameId, userId, clientId):
    datas = StoreHelper.getStoreTabByName(gameId, userId, 'coupon', clientId)
    return datas

@markCmdActionHandler  
class Activity5TcpHandler(BaseMsgPackChecker):

    
    def __init__(self):
        pass
    
    def _check_param_action(self, msg, key, params):
        action = msg.getParam(key)
        if action and isinstance(action, (str, unicode)) :
            return None, action
        return 'ERROR of action !' + str(action), None


    def _check_param_activityId(self, msg, key, params):
        activityId = msg.getParam(key)
        if activityId and isinstance(activityId, (str, unicode)) :
            return None, activityId
        return 'ERROR of activityId !' + str(activityId), None
    

    @markCmdActionMethod(cmd='act', action="act_msg_list", clientIdVer=0)
    def doActivity5ActMsgList(self, gameId, userId, clientId):
        msg = runcmd.getMsgPack()
        ftlog.debug('doActivity5List msg=', msg)
        actList = _doActivity5ActMsgList(gameId, userId, clientId)
        mo = MsgPack()
        mo.setCmd('act')     
        mo.setResult("gameId", gameId)
        mo.setResult("userId", userId)
        mo.setResult("action", "act_msg_list")
        mo.setResult("list", actList)   
        ftlog.debug("doActivity5List, mo=", mo)     
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd='act', action="city_msg_list", clientIdVer=0)
    def doActivity5CityMsgList(self, gameId, userId, clientId):
        msg = runcmd.getMsgPack()
        ftlog.debug('doActivity5CityMsgList msg=', msg)
        msgList = _doActivity5CityMsgList(gameId, userId, clientId)
        mo = MsgPack()
        mo.setCmd('act')     
        mo.setResult("gameId", gameId)
        mo.setResult("userId", userId)
        mo.setResult("action", "city_msg_list")
        mo.setResult("list", msgList)   
        ftlog.debug("doActivity5CityMsgList, mo=", mo)     
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd='act', action="prize_msg_list", clientIdVer=3.7)
    def doActivity5PrizeMsgList(self, gameId, userId, clientId):
        msg = runcmd.getMsgPack()
        ftlog.debug('doActivity5PrizeMsgList msg=', msg)
        prizeList = _doActivity5PrizeMsgList(gameId, userId, clientId)
        mo = MsgPack()
        mo.setCmd('act')     
        mo.setResult("gameId", gameId)
        mo.setResult("userId", userId)
        mo.setResult("action", "prize_msg_list")
        mo.setResult("list", prizeList)   
        ftlog.debug("doActivity5PrizeMsgList, mo=", mo)     
        router.sendToUser(mo, userId)
            
    @markCmdActionMethod(cmd='act', action="exchange_item_list", clientIdVer=0)
    def doActivity5ExchangeItemList(self, gameId, userId, clientId):
        msg = runcmd.getMsgPack()
        ftlog.debug('doActivity5ExchangeItemList msg=', msg)
        exchangeList = _doActivity5ExchangeItemList(gameId, userId, clientId)
        mo = MsgPack()
        mo.setCmd('act')     
        mo.setResult("gameId", gameId)
        mo.setResult("userId", userId)
        mo.setResult("action", "exchange_item_list")
        mo.updateResult(exchangeList)
        ftlog.debug("doActivity5ExchangeItemList, mo=", mo)     
        router.sendToUser(mo, userId)

