# -*- coding: utf-8 -*-
"""
Created on 2013-3-18

@author: Administrator
"""
from datetime import datetime
import json
import freetime.util.log as ftlog
from poker.entity.dao import daobase, daoconst
from poker.entity.dao.daoconst import GameOrderSchema
from poker.protocol.rpccore import markRpcCall

@markRpcCall(groupName='userId', lockName='', syncCall=1)
def _getExchangeRecords(gameId, userId):
    pass

@markRpcCall(groupName='', lockName='', syncCall=1)
def _makeExchangeId():
    pass

@markRpcCall(groupName='userId', lockName='', syncCall=1)
def _makeGameOrderId(gameId, userId, productId):
    pass

@markRpcCall(groupName='userId', lockName='', syncCall=1)
def _setGameOrderInfo(userId, orderId, datas):
    pass

@markRpcCall(groupName='', lockName='', syncCall=1)
def _getGameOrderInfo(orderId):
    pass