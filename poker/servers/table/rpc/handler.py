# -*- coding: utf-8 -*-
"""
Created on 2016年11月29日

@author: liaoxx
"""
from poker.protocol.rpccore import markRpcCall
from freetime.util import log as ftlog
from poker.entity.configure import gdata
from freetime.entity.msg import MsgPack

@markRpcCall(groupName='gtRoomId', lockName='userId', syncCall=1)
def doPlayerLeave(gameId, userId, gtRoomId, tableId, seatId, clientId):
    pass