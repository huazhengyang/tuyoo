# -*- coding: utf-8 -*-
"""
Created on 2015年6月8日

@author: zhaojiangang
"""
from poker.entity.biz.exceptions import TYBizException

class TYStoreException(TYBizException, ):

    def __init__(self, errorCode, message):
        pass

class TYStoreConfException(TYStoreException, ):

    def __init__(self, conf, message):
        pass

    def __str__(self):
        pass

    def __unicode__(self):
        pass

class TYBuyProductUnknownException(TYStoreException, ):

    def __init__(self, productId):
        pass

    def __str__(self):
        pass

    def __unicode__(self):
        pass

class TYProductNotSupportExchangeException(TYStoreException, ):

    def __init__(self, productId):
        pass

    def __str__(self):
        pass

    def __unicode__(self):
        pass

class TYProductExchangeNotEnoughException(TYStoreException, ):

    def __init__(self, productId, message):
        pass

    def __str__(self):
        pass

    def __unicode__(self):
        pass

class TYProductStoreNotEnoughException(TYStoreException, ):

    def __init__(self, errorCode, message='TYProductStoreNotEnoughException'):
        pass

    def __str__(self):
        pass

    def __unicode__(self):
        pass

class TYBuyProductOverCountException(TYStoreException, ):

    def __init__(self, productId, buyCountLimit, record, limit):
        pass

    def __str__(self):
        pass

    def __unicode__(self):
        pass

class TYBuyConditionNotEnoughException(TYStoreException, ):

    def __init__(self, productId, buyCondition):
        pass

class TYOrderNotFoundException(TYStoreException, ):

    def __init__(self, orderId):
        pass

    def __str__(self):
        pass

    def __unicode__(self):
        pass

class TYDeliveryOrderDiffUserException(TYStoreException, ):

    def __init__(self, orderId, orderUserId, userId):
        pass

    def __str__(self):
        pass

    def __unicode__(self):
        pass

class TYDeliveryOrderDiffProductException(TYStoreException, ):

    def __init__(self, orderId, orderProductId, productId):
        pass

    def __str__(self):
        pass

    def __unicode__(self):
        pass

class TYDeliveryProductNotFoundException(TYStoreException, ):

    def __init__(self, orderId, productId):
        pass

    def __str__(self):
        pass

    def __unicode__(self):
        pass

class TYBadOrderStateException(TYStoreException, ):

    def __init__(self, orderId, orderState, expectState):
        pass

    def __str__(self):
        pass

    def __unicode__(self):
        pass