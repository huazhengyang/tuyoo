# -*- coding: utf-8 -*-
"""
Created on 2015年6月2日

@author: zhaojiangang
"""
from poker.entity.biz.exceptions import TYBizException

class TYItemException(TYBizException, ):

    def __init__(self, errorCode, message):
        pass

    def __str__(self):
        pass

    def __unicode__(self):
        pass

class TYItemConfException(TYItemException, ):

    def __init__(self, conf, message):
        pass

    def __str__(self):
        pass

    def __unicode__(self):
        pass

class TYItemActionException(TYItemException, ):

    def __init__(self, action, message):
        pass

    def __str__(self):
        pass

    def __unicode__(self):
        pass

class TYItemActionParamException(TYItemException, ):

    def __init__(self, action, message):
        pass

    def __str__(self):
        pass

    def __unicode__(self):
        pass

class TYItemActionConditionException(TYItemException, ):

    def __init__(self, item, message):
        pass

class TYItemActionConditionNotEnoughException(TYItemActionConditionException, ):

    def __init__(self, item, condition):
        pass

    def __str__(self):
        pass

    def __unicode__(self):
        pass

class TYUnExecuteableException(TYItemException, ):

    def __init__(self, item, actionName):
        pass

    def __str__(self):
        pass

    def __unicode__(self):
        pass

class TYDuplicateItemIdException(TYItemException, ):

    def __init__(self, itemId):
        pass

    def __str__(self):
        pass

    def __unicode__(self):
        pass

class TYAssetException(TYBizException, ):

    def __init__(self, errorCode, message):
        pass

class TYUnknownAssetKindException(TYAssetException, ):

    def __init__(self, kindId):
        pass

    def __str__(self):
        pass

    def __unicode__(self):
        pass

class TYAssetNotEnoughException(TYAssetException, ):

    def __init__(self, assetKind, required, actually):
        pass

    def __str__(self):
        pass

    def __unicode__(self):
        pass

class TYUnknownItemKindException(TYItemException, ):

    def __init__(self, kindId):
        pass

    def __str__(self):
        pass

    def __unicode__(self):
        pass

class TYItemNotFoundException(TYItemException, ):

    def __init__(self, itemId):
        pass

    def __str__(self):
        pass

    def __unicode__(self):
        pass