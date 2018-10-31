# -*- coding: utf-8 -*-
"""
Created on 2015年5月20日

@author: zqh
"""
import freetime.util.log as ftlog
from poker.entity.configure import gdata, synccenter
from poker.protocol.rpccore import markRpcCall, RPC_FIRST_SERVERID
from poker.util import strutil
from poker.protocol import _runenv

def hotFix(hotfixpy, serverIds, isWait, hotparams):
    pass

@markRpcCall(groupName=RPC_FIRST_SERVERID, lockName='', syncCall=1)
def _syncHotFix(serverId, hotfixpy, hotparams):
    pass

@markRpcCall(groupName=RPC_FIRST_SERVERID, lockName='', syncCall=0)
def _asyncHotFix(serverId, hotfixpy, hotparams):
    pass

def _doHotFix(hotfixpy, hotparams):
    pass

def reloadConfig(serverIds, keylist, reloadlist, sleepTime=0.01):
    pass

@markRpcCall(groupName=RPC_FIRST_SERVERID, lockName='serverId', syncCall=1)
def _reloadConfig(serverId, keylist, reloadlist, sleepTime):
    pass