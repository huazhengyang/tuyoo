# -*- coding=utf-8
'''
Created on 2018年8月20日

@author: wangyonghui
'''
from dizhu.activities_wx.activity_wx import ActivityWxHelper, ActivityWxException
from freetime.entity.msg import MsgPack
from hall.servers.common.base_checker import BaseMsgPackChecker
from poker.protocol import router, runcmd
from poker.protocol.decorator import markCmdActionMethod, markCmdActionHandler


@markCmdActionHandler
class ActivityWxTcpHandler(BaseMsgPackChecker):
    def __init__(self):
        pass

    def _check_param_action(self, msg, key, params):
        action = msg.getParam(key)
        if action and isinstance(action, (str, unicode)):
            return None, action
        return 'ERROR of action !' + str(action), None

    def _check_param_actId(self, msg, key, params):
        actId = msg.getParam(key)
        if actId and isinstance(actId, (str, unicode)):
            return None, actId
        return 'ERROR of actId !' + str(actId), None

    @markCmdActionMethod(cmd='act_wx', action="list", clientIdVer=0)
    def doActivityWxList(self, gameId, userId, clientId):
        activityWxList = ActivityWxHelper.getActivityList(userId, clientId)
        mo = MsgPack()
        mo.setCmd('act_wx')
        mo.setResult('action', 'list')
        mo.setResult('gameId', gameId)
        mo.setResult('userId', userId)
        mo.setResult('list', activityWxList)
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd='act_wx', action="*", clientIdVer=0)
    def doActivityWxAllAction(self, gameId, userId, clientId, actId, action):
        '''
        地主基金活动协议
        '''
        msg = runcmd.getMsgPack()
        errCode = 0
        errMsg = None
        result = None
        try:
            result = ActivityWxHelper.handleActivityRequest(userId, clientId, actId, action, msg)
        except ActivityWxException as e:
            errCode, errMsg = e.errCode, e.errMsg
        mo = MsgPack()
        mo.setCmd('act_wx')
        mo.setResult('action', action)
        mo.setResult('userId', userId)
        mo.setResult('actId', actId)
        mo.setResult('gameId', gameId)
        mo.setResult('errcode', errCode)
        mo.setResult('errmsg', errMsg)
        mo.setResult('result', result)
        router.sendToUser(mo, userId)


