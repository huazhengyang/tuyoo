# -*- coding: utf-8 -*-
"""
Created on 2015年5月20日

@author: zqh
"""
from poker.entity.configure import gdata
from poker.protocol import rpccore

def doCheckUserLoc(userId, gameId, roomId, tableId, clientId):
    pass

@rpccore.markRpcCall(groupName=rpccore.RPC_FIRST_SERVERID, lockName='', syncCall=1)
def _doCheckUserLoc(serverId, userId, gameId, roomId, tableId, clientId):
    pass