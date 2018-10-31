# -*- coding:utf-8 -*-
'''
Created on 2015年12月23日

@author: zhaojiangang
'''
from hall.entity import neituiguang
from hall.entity.neituiguang import NeituiguangException, BadInviterException
from poker.entity.dao import userdata
from poker.protocol.rpccore import markRpcCall
import poker.util.timestamp as pktimestamp


@markRpcCall(groupName="userId", lockName="userId", syncCall=1)
def canBeInviter(userId, invitee):
    try:
        if not userdata.checkUserData(userId):
            raise BadInviterException('口令错误')
        timestamp = pktimestamp.getCurrentTimestamp()
        status = neituiguang.loadStatus(userId, timestamp)
        neituiguang.ensureCanBeInviter(status, invitee)
        return 0, None
    except NeituiguangException, e:
        return e.errorCode, e.message


@markRpcCall(groupName="userId", lockName="userId", syncCall=1)
def addInvitee(userId, invitee, accepted):
    try:
        if not userdata.checkUserData(userId):
            raise BadInviterException('用户不存在')
        timestamp = pktimestamp.getCurrentTimestamp()
        status = neituiguang.loadStatus(userId, timestamp)
        if not status.findInvitee(invitee):
            if status.inviteeCount:
                pass
            neituiguang.addInvitee(status, invitee, accepted)
        return 0, None
    except NeituiguangException, e:
        return e.errorCode, e.message


@markRpcCall(groupName="userId", lockName="userId", syncCall=0)
def onInvitationAccepted(userId, invitee):
    try:
        if not userdata.checkUserData(userId):
            raise BadInviterException('用户不存在')
        timestamp = pktimestamp.getCurrentTimestamp()
        status = neituiguang.loadStatus(userId, timestamp)
        invitation = status.findInvitee(invitee)
        if invitation:
            neituiguang.onInvitationAccepted(status, invitation)
        return 0, None
    except NeituiguangException, e:
        return e.errorCode, e.message


@markRpcCall(groupName="userId", lockName="userId", syncCall=1)
def set_inviter(userId, inviter):
    """
    @param userId:
    @param inviter:
    @return: 设置userId的上线为inviter
    """
    try:
        timestamp = pktimestamp.getCurrentTimestamp()
        status = neituiguang.loadStatus(userId, timestamp)

        # 检查是否能成为推荐人
        # 转到promoteCode所在的UT进程中去处理
        ec, info = canBeInviter(inviter, userId)
        if ec != 0:
            raise NeituiguangException(ec, info)

        # 设置推荐人
        neituiguang.setInviter(status, inviter)
        # 添加invitee，此处不需要处理失败的情况，前面已经检查了
        return addInvitee(inviter, userId, status.isBindMobile)
    except NeituiguangException, e:
        return e.errorCode, e.message


@markRpcCall(groupName="userId", lockName="userId", syncCall=1)
def get_invitee(userId):
    """
    @param userId:
    @return: 获取userId的下线,列表,[{'uid': uid}, ...]
    """
    timestamp = pktimestamp.getCurrentTimestamp()
    status = neituiguang.loadStatus(userId, timestamp)
    return status.encodeInvitee()


@markRpcCall(groupName="userId", lockName="userId", syncCall=1)
def get_inviter(userId):
    """
    @param userId:
    @return: 获取userId的上线,uid,0就是没有
    """
    timestamp = pktimestamp.getCurrentTimestamp()
    status = neituiguang.loadStatus(userId, timestamp)
    inviter = status.inviter
    return inviter.userId if inviter else 0


if __name__ == '__main__':
    pass
