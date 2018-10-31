# -*- coding:utf-8 -*-
'''
Created on 2016年7月4日

@author: zhaojiangang
'''
from datetime import datetime

from poker.entity.biz.confobj import TYConfable, TYConfableRegister
from sre_compile import isstring
from poker.entity.biz.exceptions import TYBizConfException


class ActivityNew(TYConfable):
    def __init__(self):
        self._actId = None
        self._intActId = None
        self._startTime = None
        self._endTime = None
    
    @property
    def actId(self):
        return self._actId
    
    @property
    def intActId(self):
        return self._intActId
    
    @property
    def startTime(self):
        return self._startTime
    
    @property
    def endTime(self):
        return self._endTime
    
    def init(self):
        pass
    
    def cleanup(self):
        pass
    
    def checkTime(self, timestamp):
        nowDT = datetime.fromtimestamp(timestamp)
        if self._startTime and nowDT < self._startTime:
            return -1
        
        if self._endTime and nowDT >= self._endTime:
            return 1
        
        return 0
    
    def decodeFromDict(self, d):
        self._actId = d.get('actId')
        if not self._actId or not isstring(self._actId):
            raise TYBizConfException(d, 'actId must not empty string')
        
        self._intActId = d.get('intActId', 0)
        if not isinstance(self._intActId, int) or self._intActId < 0:
            raise TYBizConfException(d, 'intActId must int >= 0')
        
        startTime = d.get('startTime')
        if startTime is not None:
            startTime = datetime.strptime(startTime, '%Y-%m-%d %H:%M:%S')
        
        endTime = d.get('endTime')
        if endTime is not None:
            endTime = datetime.strptime(endTime, '%Y-%m-%d %H:%M:%S')
            
        self._startTime = startTime
        self._endTime = endTime
        
        self._decodeFromDictImpl(d)
        return self
        
    def _decodeFromDictImpl(self, d):
        return self

class ActivityNewRegister(TYConfableRegister):
    '''
    活动注册
    '''
    _typeid_clz_map = {}


