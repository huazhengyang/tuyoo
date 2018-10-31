# -*- coding: utf-8 -*-
"""
Created on 2015年5月20日

@author: zqh
"""
import freetime.util.log as ftlog
from poker.protocol import router, rpccore
from poker.protocol.rpccore import markRpcCall
from poker.entity.configure import gdata

def forceLogOut(userId, logoutmsg):
    pass

@markRpcCall(groupName='userId', lockName='userId', syncCall=0)
def _forceLogOut(userId, logoutmsg):
    """
    强制某一个用户推出TCP登录
    """
    pass

def notifyUsers(message, userIds=[]):
    """
    通知所有在线用户, 
    strMessage 字符串，为需要发送的消息
    """
    pass

@markRpcCall(groupName='intServerId', lockName='intServerId', syncCall=0)
def _notifyUsers(intServerId, message, userIds):
    pass

def forceLogOut2(userId, connId, logoutmsg):
    pass

def forceLogOut3(userId, logoutmsg):
    pass

@markRpcCall(groupName=rpccore.RPC_FIRST_SERVERID, lockName='userId', syncCall=0)
def _forceLogOut2(connId, userId, logoutmsg):
    """
    强制某一个用户推出TCP登录
    """
    pass

def _forceLogOut2_(connId, userId, logoutmsg):
    """
    强制某一个用户推出TCP登录
    """
    pass