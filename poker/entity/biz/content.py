# -*- coding: utf-8 -*-
"""
Created on 2015年6月1日

@author: zhaojiangang
"""
import random
from sre_compile import isstring
from poker.entity.biz.confobj import TYConfable, TYConfableRegister
from poker.entity.biz.exceptions import TYBizConfException

class TYContentItem(object, ):

    def __init__(self, assetKindId, count):
        pass

    @classmethod
    def decodeFromDict(cls, d):
        pass

    @classmethod
    def decodeList(cls, l):
        pass

    @classmethod
    def encodeList(cls, l):
        pass

    def toDict(self):
        pass

class TYContent(TYConfable, ):

    def __init__(self):
        pass

    def getItems(self):
        """
        @return: list<TYContentItem>
        """
        pass

    def decodeFromDict(self, d):
        pass

    def _decodeFromDictImpl(self, d):
        pass

class TYEmptyContent(TYContent, ):
    TYPE_ID = 'EmptyContent'

    def __init__(self):
        pass

    def getItems(self):
        pass

class TYContentItemGenerator(object, ):

    @classmethod
    def make(cls, assetKindId, start, stop, step):
        pass

    def __init__(self, assetKindId):
        pass

    def generate(self):
        pass

    @classmethod
    def decodeFromDict(cls, d):
        pass

    @classmethod
    def decodeList(cls, l):
        pass

class TYContentItemGeneratorFixed(TYContentItemGenerator, ):

    def __init__(self, assetKindId, count):
        pass

    def generateMin(self):
        pass

    def generate(self):
        pass

class TYContentItemGeneratorRange(TYContentItemGenerator, ):

    def __init__(self, assetKindId, start, stop, step=1):
        pass

    def generateMin(self):
        pass

    def generate(self):
        pass

class TYFixedContent(TYContent, ):
    TYPE_ID = 'FixedContent'

    def __init__(self):
        pass

    def addItem(self, assetKindId, start, stop=None, step=None):
        pass

    def getMinItems(self):
        pass

    def getItems(self):
        pass

    def _decodeFromDictImpl(self, d):
        pass

class TYRandomContent(TYContent, ):
    TYPE_ID = 'RandomContent'

    def __init__(self):
        pass

    def addContent(self, weight, content):
        pass

    def getItems(self):
        pass

    def _selectContent(self):
        pass

    def _decodeFromDictImpl(self, d):
        pass

class TYCompositeContent(TYContent, ):
    TYPE_ID = 'CompositeContent'

    def __init__(self):
        pass

    @property
    def contents(self):
        pass

    def addContent(self, contents):
        pass

    def getItems(self):
        pass

    def _decodeFromDictImpl(self, d):
        pass

class TYContentUtils(object, ):

    @classmethod
    def getFixedContents(cls, content):
        pass

    @classmethod
    def getMinFixedAssetCount(cls, content, assetKindId):
        pass

    @classmethod
    def mergeContentItemList(cls, contentItemList):
        pass

class TYContentRegister(TYConfableRegister, ):
    _typeid_clz_map = {TYFixedContent.TYPE_ID: TYFixedContent, TYEmptyContent.TYPE_ID: TYEmptyContent, TYRandomContent.TYPE_ID: TYRandomContent, TYCompositeContent.TYPE_ID: TYCompositeContent}
if (__name__ == '__main__'):
    contentItemList = []
    contentItemList.append(TYContentItem('user:chip', 1))
    contentItemList.append(TYContentItem('user:coupon', 1))
    contentItemList.append(TYContentItem('user:chip', 2))
    contentItemList.append(TYContentItem('user:coupon', 2))
    contentItemList.append(TYContentItem('user:charm', 2))
    contentItemList.append(TYContentItem('user:coupon', 2))
    mergedContentItemList = TYContentUtils.mergeContentItemList(contentItemList)
    for ci in mergedContentItemList:
        print ci.__dict__