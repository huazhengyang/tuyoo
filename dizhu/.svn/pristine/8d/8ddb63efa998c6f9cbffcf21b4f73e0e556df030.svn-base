# -*- coding:utf-8 -*-
'''
Created on 2017年12月31日

@author: wangyonghui
'''
from poker.entity.configure import gdata
from poker.protocol.rpccore import markRpcCall


@markRpcCall(groupName='roomId', lockName='', syncCall=1)
def reportRoomUserOccupy(roomId, shadowRoomId, roomOccupy):
    return gdata.rooms()[roomId].roomUserOccupy(shadowRoomId, roomOccupy)
