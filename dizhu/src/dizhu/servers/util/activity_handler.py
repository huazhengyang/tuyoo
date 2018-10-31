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
            result = {"errorInfo":"unknown action", "errorCode":1}
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
            result = {"errorInfo":"unknown action", "errorCode":1}
        for key in result:
            mo.setResult(key, result[key])
        return mo
            
@markCmdActionHandler  
class ActivityTcpHandler(BaseMsgPackChecker):
    def __init__(self):
        pass

    @classmethod
    def _check_param_action(cls, msg, key, params):
        action = msg.getParam(key)
        if action and isinstance(action, (str, unicode)) :
            return None, action
        return 'ERROR of action !' + str(action), None

    @classmethod
    def _check_param_activityId(cls, msg, key, params):
        activityId = msg.getParam(key)
        if activityId and isinstance(activityId, (str, unicode)) :
            return None, activityId
        return 'ERROR of activityId !' + str(activityId), None

    @markCmdActionMethod(cmd='act', action="ddz.redenvelope.update", clientIdVer=0, scope="game")
    def doActivityRedEnvelopeUpdate(self, gameId, userId, clientId, activityId, action):
        msg = runcmd.getMsgPack()
        ftlog.debug('doActivityRedEnvelopeUpdate msg=', msg)
        result = activity.activitySystem.handleActivityRequest(userId, gameId, clientId, msg)
        mo = ActivityTcpHelper.getOldResponseMsg(result, gameId, userId, activityId, action)
        ftlog.debug('doActivityRedEnvelopeUpdate res=', mo)
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd='act', action="ddz.redenvelope.get", clientIdVer=0, scope="game")
    def doActivityRedEnvelopeGet(self, gameId, userId, clientId, activityId, action):
        msg = runcmd.getMsgPack()
        ftlog.debug('doActivityRedEnvelopeGet msg=', msg)
        result = activity.activitySystem.handleActivityRequest(userId, gameId, clientId, msg)
        mo = ActivityTcpHelper.getOldResponseMsg(result, gameId, userId, activityId, action)
        ftlog.debug('doActivityRedEnvelopeGet res=', mo)
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd='act', action="ddz.dumplings.update", clientIdVer=0, scope="game")
    def doActivityDumplingsUpdate(self, gameId, userId, clientId, activityId, action):
        msg = runcmd.getMsgPack()
        ftlog.debug('doActivityDumplingsUpdate msg=', msg)
        result = activity.activitySystem.handleActivityRequest(userId, gameId, clientId, msg)
        config = activity.activitySystem._dao.getClientActivityConfig(clientId, activityId)
        mo = ActivityTcpHelper.getOldResponseMsg(result, gameId, userId, activityId, action)
        ftlog.debug('doActivityDumplingsUpdate res=', mo)
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd='act', action="ddz.wishing.btn", clientIdVer=0, scope="game")
    def doActivityWishingWellBtn(self, gameId, userId, clientId, activityId, action):
        msg = runcmd.getMsgPack()
        ftlog.debug('doActivityWishingWellBtn msg=', msg)
        result = activity.activitySystem.handleActivityRequest(userId, gameId, clientId, msg)
        config = activity.activitySystem._dao.getClientActivityConfig(clientId, activityId)
        mo = ActivityTcpHelper.getOldResponseMsg(result, gameId, userId, activityId, action)
        ftlog.debug('doActivityWishingWellBtn res=', mo)
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd='act', action="ddz.wishing.update", clientIdVer=0, scope="game")
    def doActivityWishingWellUpdate(self, gameId, userId, clientId, activityId, action):
        msg = runcmd.getMsgPack()
        ftlog.debug('doActivityWishingWellUpdate msg=', msg)
        result = activity.activitySystem.handleActivityRequest(userId, gameId, clientId, msg)
        config = activity.activitySystem._dao.getClientActivityConfig(clientId, activityId)
        mo = ActivityTcpHelper.getOldResponseMsg(result, gameId, userId, activityId, action)
        ftlog.debug('doActivityWishingWellUpdate res=', mo)
        router.sendToUser(mo, userId)
