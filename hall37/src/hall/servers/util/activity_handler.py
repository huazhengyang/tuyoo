# -*- coding: utf-8 -*-
"""
Created on 2015年5月20日

@author: zqh
"""

from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
import hall.entity.hallactivity.activity as activity
from hall.servers.common.base_checker import BaseMsgPackChecker
from poker.protocol import router, runcmd
from poker.protocol.decorator import markCmdActionMethod, markCmdActionHandler
from hall.entity.hallactivity.activity_send_reward import ActivitySendReward


class ActivityTcpHelper(object):
    @classmethod
    def getOldResponseMsg(cls, result, gameId, userId, activityId, action):
        mo = MsgPack()
        mo.setCmd('activity_request')
        mo.setResult("gameId", gameId)
        mo.setResult("userId", userId)
        mo.setResult("activityId", activityId)
        mo.setResult("action", action)
        if not result:
            result = {"errorInfo": "unknown action", "errorCode": 1}
        for key in result:
            mo.setResult(key, result[key])
        return mo

    @classmethod
    def getResponseMsg(cls, result, gameId, userId, activityId, action):
        mo = MsgPack()
        mo.setCmd('act')
        mo.setResult("gameId", gameId)
        mo.setResult("userId", userId)
        mo.setResult("activityId", activityId)
        mo.setResult("action", action)
        if not result:
            result = {"errorInfo": "unknown action", "errorCode": 1}
        for key in result:
            mo.setResult(key, result[key])
        return mo


@markCmdActionHandler
class ActivityTcpHandler(BaseMsgPackChecker):
    def __init__(self):
        pass

    def _check_param_action(self, msg, key, params):
        action = msg.getParam(key)
        if action and isinstance(action, (str, unicode)):
            return None, action
        return 'ERROR of action !' + str(action), None

    def _check_param_activityId(self, msg, key, params):
        activityId = msg.getParam(key)
        if activityId and isinstance(activityId, (str, unicode)):
            return None, activityId
        return 'ERROR of activityId !' + str(activityId), None

    @markCmdActionMethod(cmd='act', action="list", clientIdVer=0)
    def doActivityListOld(self, gameId, userId, clientId):
        msg = runcmd.getMsgPack()
        ftlog.debug('doActivityListOld msg=', msg)
        activityList = activity.activitySystem.getActivityList(gameId, userId, clientId)
        mo = MsgPack()
        mo.setCmd('activity_list')
        mo.setResult("gameId", gameId)
        mo.setResult("userId", userId)
        mo.setResult("list", activityList)
        ftlog.debug("doActivityList, mo=", mo)
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd='act', action="list", clientIdVer=3.7)
    def doActivityList(self, gameId, userId, clientId):
        msg = runcmd.getMsgPack()
        ftlog.debug('doActivityList msg=', msg)
        activityList = activity.activitySystem.getActivityList(gameId, userId, clientId)
        mo = MsgPack()
        mo.setCmd('act')
        mo.setResult("gameId", gameId)
        mo.setResult("userId", userId)
        mo.setResult("action", "list")
        mo.setResult("list", activityList)
        ftlog.debug("doActivityList, mo=", mo)
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd='act', action="actState", clientIdVer=3.7)
    def doActivityState(self, gameId, userId, clientId):
        msg = runcmd.getMsgPack()
        actList = msg.getParam('actList')
        ftlog.debug('doActivityList msg=', msg)
        activity.changeActStateForUser(userId, gameId, clientId, actList)

    @markCmdActionMethod(cmd='act', action="exchange", clientIdVer=0)
    def doActivityExchangeOld(self, gameId, userId, clientId, activityId, action):
        msg = runcmd.getMsgPack()
        ftlog.debug('doActivityExchangeOld msg=', msg)
        result = activity.activitySystem.handleActivityRequest(userId, gameId, clientId, msg)
        mo = ActivityTcpHelper.getOldResponseMsg(result, gameId, userId, activityId, action)
        ftlog.debug('doActivityExchangeOld res=', mo)
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd='act', action="exchange", clientIdVer=3.7)
    def doActivityExchange(self, gameId, userId, clientId, activityId, action):
        msg = runcmd.getMsgPack()
        ftlog.debug('doActivityExchange msg=', msg)
        result = activity.activitySystem.handleActivityRequest(userId, gameId, clientId, msg)
        mo = ActivityTcpHelper.getOldResponseMsg(result, gameId, userId, activityId, action)
        ftlog.debug('doActivityExchange res=', mo)
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd='act', action="getGifts", clientIdVer=0)
    def doActivityGetGiftOld(self, gameId, userId, clientId, activityId, action):
        msg = runcmd.getMsgPack()
        ftlog.debug('doActivityGetGiftOld msg=', msg)
        result = activity.activitySystem.handleActivityRequest(userId, gameId, clientId, msg)
        mo = ActivityTcpHelper.getOldResponseMsg(result, gameId, userId, activityId, action)
        ftlog.debug('doActivityGetGiftOld res=', mo)
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd='act', action="getGifts", clientIdVer=3.7)
    def doActivityGetGift(self, gameId, userId, clientId, activityId, action):
        msg = runcmd.getMsgPack()
        ftlog.debug('doActivityGetGift msg=', msg)
        result = activity.activitySystem.handleActivityRequest(userId, gameId, clientId, msg)
        mo = ActivityTcpHelper.getOldResponseMsg(result, gameId, userId, activityId, action)
        ftlog.debug('doActivityGetGift res=', mo)
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd='act', action="buy", clientIdVer=0)
    def doActivityBuyOld(self, gameId, userId, clientId, activityId, action):
        msg = runcmd.getMsgPack()
        ftlog.debug('doActivityBuy msg=', msg)
        result = activity.activitySystem.handleActivityRequest(userId, gameId, clientId, msg)
        mo = ActivityTcpHelper.getOldResponseMsg(result, gameId, userId, activityId, action)
        ftlog.debug('doActivityBuy res=', mo)
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd='act', action="buy", clientIdVer=3.7)
    def doActivityBuy(self, gameId, userId, clientId, activityId, action):
        msg = runcmd.getMsgPack()
        ftlog.debug('doActivityBuy msg=', msg)
        result = activity.activitySystem.handleActivityRequest(userId, gameId, clientId, msg)
        mo = ActivityTcpHelper.getResponseMsg(result, gameId, userId, activityId, action)
        ftlog.debug('doActivityBuy res=', mo)
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd='act', action="activityflipcard", clientIdVer=0)
    def doActivityFanfanleOld(self, gameId, userId, clientId, activityId, action):
        msg = runcmd.getMsgPack()
        ftlog.debug('doActivityFanfanle msg=', msg)
        result = activity.activitySystem.handleActivityRequest(userId, gameId, clientId, msg)
        mo = ActivityTcpHelper.getOldResponseMsg(result, gameId, userId, activityId, action)
        ftlog.debug('doActivityFanfanle res=', mo)
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd='act', action="activityflipcard", clientIdVer=3.7)
    def doActivityFanfanle(self, gameId, userId, clientId, activityId, action):
        msg = runcmd.getMsgPack()
        ftlog.debug('doActivityFanfanle msg=', msg)
        result = activity.activitySystem.handleActivityRequest(userId, gameId, clientId, msg)
        mo = ActivityTcpHelper.getOldResponseMsg(result, gameId, userId, activityId, action)
        ftlog.debug('doActivityFanfanle res=', mo)
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd='act', action="activityflipcardMoney", clientIdVer=0)
    def doActivityFanfanleMoneyOld(self, gameId, userId, clientId, activityId, action):
        msg = runcmd.getMsgPack()
        ftlog.debug('doActivityFanfanleMoney msg=', msg)
        result = activity.activitySystem.handleActivityRequest(userId, gameId, clientId, msg)
        mo = ActivityTcpHelper.getOldResponseMsg(result, gameId, userId, activityId, action)
        ftlog.debug('doActivityFanfanleMoney res=', mo)
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd='act', action="activityflipcardMoney", clientIdVer=3.7)
    def doActivityFanfanleMoney(self, gameId, userId, clientId, activityId, action):
        msg = runcmd.getMsgPack()
        ftlog.debug('doActivityFanfanleMoney msg=', msg)
        result = activity.activitySystem.handleActivityRequest(userId, gameId, clientId, msg)
        mo = ActivityTcpHelper.getOldResponseMsg(result, gameId, userId, activityId, action)
        ftlog.debug('doActivityFanfanleMoney res=', mo)
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd='act', action="activityflipcardIsMoney", clientIdVer=0)
    def doActivityFanfanleIsMoneyOld(self, gameId, userId, clientId, activityId, action):
        msg = runcmd.getMsgPack()
        ftlog.debug('doActivityFanfanleMoney msg=', msg)
        result = activity.activitySystem.handleActivityRequest(userId, gameId, clientId, msg)
        mo = ActivityTcpHelper.getOldResponseMsg(result, gameId, userId, activityId, action)
        ftlog.debug('doActivityFanfanleMoney res=', mo)
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd='act', action="activityflipcardIsMoney", clientIdVer=3.7)
    def doActivityFanfanleIsMoney(self, gameId, userId, clientId, activityId, action):
        msg = runcmd.getMsgPack()
        ftlog.debug('doActivityFanfanleMoney msg=', msg)
        result = activity.activitySystem.handleActivityRequest(userId, gameId, clientId, msg)
        mo = ActivityTcpHelper.getOldResponseMsg(result, gameId, userId, activityId, action)
        ftlog.debug('doActivityFanfanleMoney res=', mo)
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd='act', action="activityDdzFundGet", clientIdVer=0)
    def doActivityDdzFundGet(self, gameId, userId, clientId, activityId, action):
        '''
        地主基金活动协议
        '''
        msg = runcmd.getMsgPack()
        ftlog.debug('doActivityDdzFundGet msg=', msg)
        result = activity.activitySystem.handleActivityRequest(userId, gameId, clientId, msg)
        mo = ActivityTcpHelper.getOldResponseMsg(result, gameId, userId, activityId, action)
        ftlog.debug('doActivityDdzFundGet res=', mo)
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd='act', action="activityDdzFundCheck", clientIdVer=0)
    def doActivityDdzFundCheck(self, gameId, userId, clientId, activityId, action):
        '''
        地主基金活动协议
        '''
        msg = runcmd.getMsgPack()
        ftlog.debug('doActivityDdzFundCheck msg=', msg)
        result = activity.activitySystem.handleActivityRequest(userId, gameId, clientId, msg)
        mo = ActivityTcpHelper.getOldResponseMsg(result, gameId, userId, activityId, action)
        ftlog.debug('doActivityDdzFundCheck res=', mo)
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd='act', action="activityHSZZ", clientIdVer=0)
    def doActivityHSZZ(self, gameId, userId, clientId, activityId):
        '''
        皇室战争推广
        '''
        ActivitySendReward.doSendReward(gameId, userId, clientId, activityId)

    @markCmdActionMethod(cmd='act', action="*", clientIdVer=0)
    def doActivityAllAction(self, gameId, userId, clientId, activityId, action):
        '''
        地主基金活动协议
        '''
        msg = runcmd.getMsgPack()
        ftlog.debug('doActivityAllAction msg=', msg)
        result = activity.activitySystem.handleActivityRequest(userId, gameId, clientId, msg)
        mo = ActivityTcpHelper.getOldResponseMsg(result, gameId, userId, activityId, action)
        ftlog.debug('doActivityAllAction res=', mo)
        router.sendToUser(mo, userId)


        