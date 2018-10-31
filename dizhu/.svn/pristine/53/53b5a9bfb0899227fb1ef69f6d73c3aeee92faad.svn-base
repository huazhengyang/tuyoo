# -*- coding=utf-8 -*-
'''
Created on 2018年6月1日

@author: wangyonghui
'''
from sre_compile import isstring
from dizhu.entity.dizhu_invite import InviteHelper
from freetime.entity.msg import MsgPack
from hall.servers.common.base_checker import BaseMsgPackChecker
from poker.protocol import router
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod
from hall.entity.hallconf import HALL_GAMEID


@markCmdActionHandler
class InviteTcpHandler(BaseMsgPackChecker):
    def __init__(self):
        super(InviteTcpHandler, self).__init__()

    def _check_param_inviteUserId(self, msg, key, params):
        value = msg.getParam('inviteUserId')
        if value and isinstance(value, int):
            return None, value
        return 'ERROR of inviteUserId !' + str(value), None

    def _check_param_inviteeId(self, msg, key, params):
        value = msg.getParam('inviteeId')
        if value and isinstance(value, int):
            return None, value
        return 'ERROR of inviteeId !' + str(value), None

    def _check_param_pointId(self, msg, key, params):
        value = msg.getParam('pointId')
        if value and isstring(value):
            try:
                value = int(value)
            except:
                return 'ERROR of pointId !' + str(value), None
            return None, value
        return 'ERROR of pointId !' + str(value), None

    @classmethod
    def makeErrorResponse(cls, cmd, action, errorCode, info):
        mo = MsgPack()
        mo.setCmd(cmd)
        mo.setResult('action', action)
        mo.setResult('code', errorCode)
        mo.setResult('info', info)
        mo.setResult('gameId', HALL_GAMEID)
        return mo

    @markCmdActionMethod(cmd='dizhu', action='query_invite_info', clientIdVer=0)
    def doQueryInviteInfo(self, gameId, userId, clientId):
        """
        查询邀请信息
        """
        mo = MsgPack()
        mo.setCmd('dizhu')
        mo.setResult('action', 'query_invite_info')
        mo.setResult('gameId', gameId)
        mo.setResult('clientId', clientId)
        inviteeList, bigReward = InviteHelper.getInviteeList(userId)
        mo.setResult('inviteeList', inviteeList)
        mo.setResult('bigReward', bigReward)
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd='dizhu', action='bind_invite_user', clientIdVer=0)
    def doBindInviteUser(self, gameId, userId, clientId, inviteUserId, pointId):
        """绑定上线推荐人ID"""
        mo = MsgPack()
        mo.setCmd('dizhu')
        mo.setResult('action', 'bind_invite_user')
        mo.setResult('clientId', clientId)
        errcode, errmsg = InviteHelper.doBindInviteUser(userId, inviteUserId, pointId)
        mo.setResult('code', errcode)
        mo.setResult('errmsg', errmsg)
        mo.setResult('gameId', gameId)
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd='dizhu', action='get_invite_reward_all', clientIdVer=0)
    def doGetInviteRewardAll(self, gameId, userId, clientId):
        """
        获取推荐人奖励
        一键领取
        """
        mo = MsgPack()
        mo.setCmd('dizhu')
        mo.setResult('action', 'get_invite_reward_all')
        mo.setResult('gameId', gameId)
        rewardList, bigReward = InviteHelper.doGetInviteRewardAll(userId)
        mo.setResult('rewardList', rewardList)
        mo.setResult('bigReward', bigReward)
        mo.setResult('clientId', clientId)
        router.sendToUser(mo, userId)
