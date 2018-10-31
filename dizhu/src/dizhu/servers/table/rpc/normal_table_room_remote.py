# -*- coding:utf-8 -*-
'''
Created on 2017年2月13日

@author: zhaojiangang
'''
from dizhucomm.core.exceptions import ChipNotEnoughException
import freetime.util.log as ftlog
from poker.entity.configure import gdata
from poker.protocol.rpccore import markRpcCall

@markRpcCall(groupName='roomId', lockName='', syncCall=1)
def quickStart(gameId, userId, roomId, tableId, continueBuyin):
    room = gdata.rooms()[roomId]
    # 开始游戏
    try:
        seat = room.quickStart(userId, tableId, continueBuyin)
        # 返回(talbeId，seatId)
        return (seat.tableId, seat.seatId) if seat else (0, 0)
    except ChipNotEnoughException, e:
        ftlog.error('quickStart',
                    'userId=', userId,
                    'tableId=', tableId,
                    'continueBuyin=', continueBuyin,
                    'error=', e.message)
        return 0, 0

@markRpcCall(groupName='roomId', lockName='', syncCall=1)
def mixQuickStart(gameId, userId, roomId, tableId, continueBuyin, mixId):
    room = gdata.rooms()[roomId]
    # 开始游戏
    try:
        seat = room.quickStart(userId, tableId, continueBuyin, mixId)
        # 返回(talbeId，seatId)
        return (seat.tableId, seat.seatId) if seat else (0, 0)
    except ChipNotEnoughException, e:
        ftlog.error('mixQuickStart',
                    'userId=', userId,
                    'tableId=', tableId,
                    'mixId=', mixId,
                    'continueBuyin=', continueBuyin,
                    'error=', e.message)
        return 0, 0

@markRpcCall(groupName='roomId', lockName='', syncCall=1)
def leaveRoom(gameId, userId, roomId, reason):
    room = gdata.rooms()[roomId]
    return room.leaveRoom(userId, reason)


