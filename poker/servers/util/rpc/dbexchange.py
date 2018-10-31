# -*- coding: utf-8 -*-
from poker.entity.dao import daobase
from poker.entity.dao.daoconst import GameExchangeSchema
from poker.protocol.rpccore import markRpcCall

@markRpcCall(groupName='userId', lockName='', syncCall=1)
def _getExchangeDataAll(userId, gameId):
    """
    取得用户所有的兑换数据
    """
    pass

@markRpcCall(groupName='userId', lockName='', syncCall=1)
def _setExchangeData(userId, gameId, exchangeId, exchangeData):
    """
    设置用户的一个兑换的数据
    """
    pass

@markRpcCall(groupName='userId', lockName='', syncCall=1)
def _getExchangeData(userId, gameId, exchangeId):
    """
    设置用户的一个兑换的数据
    """
    pass