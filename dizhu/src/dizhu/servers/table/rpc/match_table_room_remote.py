# -*- coding:utf-8 -*-
'''
Created on 2017年5月24日

@author: wangyonghui
'''
from poker.entity.configure import gdata
from poker.protocol.rpccore import markRpcCall

@markRpcCall(groupName='roomId', lockName='', syncCall=1)
def leaveRoom(gameId, userId, roomId, tableId, reason):
    room = gdata.rooms()[roomId]
    return room.leaveRoom(userId, tableId, reason)


