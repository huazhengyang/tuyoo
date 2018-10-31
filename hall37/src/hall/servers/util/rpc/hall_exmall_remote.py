# -*- coding=utf-8

from poker.protocol.rpccore import markRpcCall
import hall.entity.hall_exmall as hallEx
from poker.entity.biz.exceptions import TYBizException


@markRpcCall(groupName='userId', lockName='userId', syncCall=1)
def handleAuditResult(gameId, userId, orderId, result):
    try:
        hallEx.handleExchangeAuditResult(userId, orderId, result)
        return 0, None
    except TYBizException, e:
        return e.errorCode, e.message


@markRpcCall(groupName='userId', lockName='userId', syncCall=1)
def handleShippingResult(gameId, userId, orderId, result, jdOrderId):
    try:
        hallEx.handleShippingResult(userId, orderId, result, {'jdOrderId':jdOrderId} if jdOrderId else None)
        return 0, None
    except TYBizException, e:
        return e.errorCode, e.message


