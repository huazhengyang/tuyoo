# -*- coding:utf-8 -*-
'''
Created on 2016年9月29日

@author: zhaojiangang
'''
from dizhu.room.ftroom import FTConf
import freetime.util.log as ftlog
from poker.entity.biz.content import TYContentItem
from poker.entity.biz.exceptions import TYBizException
from poker.entity.configure import gdata
from poker.protocol.rpccore import markRpcCall


@markRpcCall(groupName='roomId', lockName='', syncCall=1)
def createFT(roomId, userId, nRound, playMode, canDouble, fee, goodCard):
    if fee is not None:
        fee = TYContentItem.decodeFromDict(fee)
    ftConf = FTConf(nRound, fee, canDouble, playMode, goodCard)
    ftTable = gdata.rooms()[roomId].createFT(userId, ftConf)
    return ftTable.ftId

@markRpcCall(groupName='roomId', lockName='', syncCall=1)
def enterFT(roomId, userId, ftId):
    try:
        ftTable = gdata.rooms()[roomId].enterFT(userId, ftId)
        return 0, ftTable.table.tableId
    except TYBizException, e:
        return e.errorCode, e.message

@markRpcCall(groupName='roomId', lockName='', syncCall=1)
def continueFT(roomId, userId, ftId):
    try:
        ftTable = gdata.rooms()[roomId].continueFT(userId, ftId)
        return 0, ftTable.expires
    except TYBizException, e:
        return e.errorCode, e.message

@markRpcCall(groupName='roomId', lockName='', syncCall=1)
def disbindFT(roomId, ftId, returnFee):
    gdata.rooms()[roomId].disbindFT(ftId, returnFee)

@markRpcCall(groupName='roomId', lockName='', syncCall=1)
def ftExists(roomId, ftId):
    ftTable = gdata.rooms()[roomId].findFT(ftId)
    if ftlog.is_debug():
        ftlog.debug('ft_room_remote.ftExists roomId=', roomId,
                    'ftId=', ftId,
                    'ftTable=', ftTable)
    return True if ftTable else False


