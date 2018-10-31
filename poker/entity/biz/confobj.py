# -*- coding: utf-8 -*-
"""
Created on 2015年6月3日

@author: zhaojiangang
"""
from poker.entity.biz.exceptions import TYBizConfException
from poker.util.reflection import TYClassRegister
import freetime.util.log as ftlog

class TYConfable(object, ):
    TYPE_ID = 'unknown'

    def __init__(self):
        pass

    def decodeFromDict(self, d):
        pass

class TYConfableRegister(TYClassRegister, ):

    @classmethod
    def decodeFromDict(cls, d):
        pass

    @classmethod
    def decodeList(cls, dictList):
        pass