# -*- coding=utf-8

from poker.protocol.rpccore import markRpcCall
import hall.entity.hallexchange as hallEx
from poker.entity.biz.exceptions import TYBizException

@markRpcCall(groupName="userId", lockName="userId", syncCall=1)
def handleAuditResult(gameId, userId, exchangeId, result):
    try:
        hallEx.handleExchangeAuditResult( userId, exchangeId, result )
        return 0, None
    except TYBizException, e:
        return e.errorCode, e.message


@markRpcCall(groupName="userId", lockName="userId", syncCall=1)
def handleShippingResult(gameId, userId, exchangeId, result):
    try:
        hallEx.handleShippingResult( userId, exchangeId, result )
        return 0, None
    except TYBizException, e:
        return e.errorCode, e.message