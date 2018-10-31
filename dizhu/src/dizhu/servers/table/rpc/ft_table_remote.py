# -*- coding:utf-8 -*-
'''
Created on 2016年11月3日

@author: zhaojiangang
'''
from dizhu.games.friend.tableproto import FTTableDetails
from poker.entity.configure import gdata
from poker.protocol.rpccore import markRpcCall
from dizhucomm.room.tableroom import DizhuTableRoom


@markRpcCall(groupName='roomId', lockName='', syncCall=1)
def ftBind(gameId, roomId, tableId, ftTable):
    room = gdata.rooms()[roomId]
    table = room.maptable[tableId]
    ftDetails = FTTableDetails().fromDict(ftTable)
    return table.bindFT(ftDetails)

@markRpcCall(groupName='roomId', lockName='', syncCall=1)
def ftEnter(gameId, userId, roomId, tableId, ftId):
    room = gdata.rooms()[roomId]
    if isinstance(room, DizhuTableRoom):
        return room.enterFT(tableId, ftId, userId)
    else:
        table = room.maptable[tableId]
        return table.doFTEnter(ftId, userId)

@markRpcCall(groupName='roomId', lockName='', syncCall=1)
def leaveRoom(gameId, userId, roomId, reason):
    room = gdata.rooms()[roomId]
    return room.leaveRoom(userId, reason)


