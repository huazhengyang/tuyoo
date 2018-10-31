# -*- coding:utf-8 -*-
'''
Created on 2017年12月15日

@author: zhaojiangang
'''
from poker.entity.dao import userdata
from poker.protocol.rpccore import markRpcCall
from poker.entity.biz.exceptions import TYBizConfException, TYBizException
from hall.entity import hall_invite
from hall.entity.hallconf import HALL_GAMEID
import poker.util.timestamp as pktimestamp
import freetime.util.log as ftlog


@markRpcCall(groupName='userId', lockName='userId', syncCall=1)
def addInvitee(userId, invitee):
    try:
        if not userdata.checkUserData(userId):
            raise TYBizConfException(-1, 'ID不存在')
        
        status = hall_invite.loadUserInviteStatus(userId)
        if not status.findInvitee(invitee):
            hall_invite.addInvitee(status, invitee)
        return 0, None
    except TYBizException, e:
        return e.errorCode, e.message
    

@markRpcCall(groupName='userId', lockName='userId', syncCall=1)
def sendInviteeReward(userId, invitee, rewardCount):
    if ftlog.is_debug():
        ftlog.debug('hall_invite_remote.sendInviteeReward',
                    'userId=', userId,
                    'invitee=', invitee,
                    'rewardCount=', rewardCount)
    try:
        if not userdata.checkUserData(userId):
            raise TYBizConfException(-1, 'ID不存在')
        
        status = hall_invite.loadUserInviteStatus(userId)
        if status.findInvitee(invitee):
            hall_invite.sendInviteeReward(status, invitee, rewardCount, pktimestamp.getCurrentTimestamp())
        return 0, None
    except TYBizException, e:
        return e.errorCode, e.message


@markRpcCall(groupName='userId', lockName='userId', syncCall=1)
def _testOnUserLogin(userId, clipboardContent, dayFirst, isCreate, clientId):
    from poker.entity.events.tyevent import EventUserLogin
    hall_invite._onUserLogin(EventUserLogin(userId, HALL_GAMEID, dayFirst, isCreate, clientId))
    return 0, None


