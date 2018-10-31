# -*- coding:utf-8 -*-
'''
Created on 2017年12月18日

@author: zhaojiangang
'''
from freetime.entity.msg import MsgPack
from hall.entity import hall_invite, hallitem
from hall.entity.hallconf import HALL_GAMEID
from hall.entity.todotask import TodoTaskHelper, TodoTaskShowRewards
from hall.servers.common.base_checker import BaseMsgPackChecker
from poker.entity.biz.exceptions import TYBizException
from poker.protocol import router
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod


@markCmdActionHandler
class InviteTcpHandler(BaseMsgPackChecker):
    def _check_param_inviter(self, msg, key, params):
        value = msg.getParam(key)
        if value and isinstance(value, int) :
            return None, value
        return 'ERROR of inviter !' + str(value), None
    
    @classmethod
    def buildRewards(cls, assetList):
        ret = []
        for atup in assetList:
            ret.append({
                'itemId':atup[0].kindId,
                'name':atup[0].displayName,
                'pic':atup[0].pic,
                'count':atup[1]
            })
        return ret
    
    @classmethod
    def _doBindInviter(cls, userId, gameId, clientId, inviter):
        mo = MsgPack()
        mo.setCmd('hall_invite')
        mo.setResult('action', 'bind_inviter')
        mo.setResult('gameId', gameId)
        mo.setResult('userId', userId)
        
        try:
            status = hall_invite.loadUserInviteStatus(userId)
            assetList = hall_invite.setInviter(status, inviter)
            mo.setResult('inviter', inviter)
            if assetList:
                TodoTaskHelper.sendTodoTask(HALL_GAMEID, userId, TodoTaskShowRewards(cls.buildRewards(assetList)))
        except TYBizException, e:
            mo.setResult('ec', e.errorCode)
            mo.setResult('info', e.message)
        
        return mo
    
    @markCmdActionMethod(cmd='hall_invite', action='bind_inviter')
    def doBindInviter(self, userId, gameId, clientId, inviter):
        mo = self._doBindInviter(userId, gameId, clientId, inviter)
        if mo:
            router.sendToUser(mo, userId)
    
    @classmethod
    def buildInviterInfo(cls):
        info = {}
        content = hall_invite.getBindInviterReward()
        if content:
            info['rewards'] = hallitem.buildItemInfoList(content.getItems())
        return info
    
    @classmethod
    def _doInviterInfo(cls, userId, gameId, clientId):
        mo = MsgPack()
        mo.setCmd('hall_invite')
        mo.setResult('action', 'inviter_info')
        mo.setResult('info', cls.buildInviterInfo())
        return mo
            
    @markCmdActionMethod(cmd='hall_invite', action='inviter_info')
    def doInviterInfo(self, userId, gameId, clientId):
        mo = self._doInviterInfo(userId, gameId, clientId)
        if mo:
            router.sendToUser(mo, userId)
    
    @classmethod
    def _encodeInvitees(cls, status, clientId):
        ret = []
        for invitee in status.inviteeMap.values():
            d = {
                'userId':invitee.userId,
                'name':invitee.userAttrs.get('name', ''),
                'purl':invitee.userAttrs.get('purl', ''),
                'gotten':invitee.gotten,
                'received':invitee.received
            }
            if not invitee.gotten:
                remindTodotaskFac = hall_invite.getRemindTodotask(clientId)
                if remindTodotaskFac:
                    todotask = remindTodotaskFac.newTodoTask(HALL_GAMEID, invitee.userId, clientId)
                    if todotask:
                        d['todotask'] = todotask.toDict()
            ret.append(d)
        return ret

    @classmethod
    def _doInviteeInfo(cls, userId, gameId, clientId):
        mo = MsgPack()
        mo.setCmd('hall_invite')
        mo.setResult('action', 'invitee_info')
        status = hall_invite.loadUserInviteStatus(userId)
        mo.setResult('invitees', cls._encodeInvitees(status, clientId))
        return mo
    
    @markCmdActionMethod(cmd='hall_invite', action='invitee_info')
    def doInviteeInfo(self, userId, gameId, clientId):
        mo = self._doInviteeInfo(userId, gameId, clientId)
        if mo:
            router.sendToUser(mo, userId)
    
    @classmethod
    def _doGainInviteeReward(cls, userId, gameId, clientId, invitee):
        mo = MsgPack()
        mo.setCmd('hall_invite')
        mo.setResult('action', 'gain_invitee_reward')
        status = hall_invite.loadUserInviteStatus(userId)
        received = hall_invite.receiveInviteeReward(status, invitee)
        mo.setResult('reward', {'itemId':'user:coupon', 'count':received})
        return mo
    
    def _check_param_invitee(self, msg, key, params):
        value = msg.getParam(key)
        if value and isinstance(value, int) :
            return None, value
        return 'ERROR of invitee !' + str(value), None
    
    @markCmdActionMethod(cmd='hall_invite', action='gain_invitee_reward')
    def doGainInviteeReward(self, userId, gameId, clientId, invitee):
        mo = self._doGainInviteeReward(userId, gameId, clientId, invitee)
        if mo:
            router.sendToUser(mo, userId)
            mo = self._doInviteeInfo(userId, gameId, clientId)
            if mo:
                router.sendToUser(mo, userId)
            
    


