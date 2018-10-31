# -*- coding:utf-8 -*-
'''
Created on 2016年7月4日

@author: zhaojiangang
'''

from poker.entity.biz.confobj import TYConfable, TYConfableRegister
import poker.util.timestamp as pktimestamp


class TimeCycle(TYConfable):
    def __init__(self):
        super(TimeCycle, self).__init__()
        
    def isSameCycle(self, timestamp1, timestamp2):
        '''
        判断timestamp1和timestamp2是否在同一个周期
        '''
        raise NotImplemented()
    
    def decodeFromDict(self, d):
        return self

class TimeCycleLife(TimeCycle):
    '''
    本周期
    '''
    TYPE_ID = 'life'
    
    def isSameCycle(self, timestamp1, timestamp2):
        return True
        
class TimeCyclePerDay(TimeCycle):
    '''
    每日
    '''
    TYPE_ID = 'perDay'
    
    def isSameCycle(self, timestamp1, timestamp2):
        return pktimestamp.getDayStartTimestamp(timestamp1) \
                == pktimestamp.getDayStartTimestamp(timestamp2)
    
class TimeCyclePerMonth(TimeCycle):
    '''
    每月限购
    '''
    TYPE_ID = 'perMonth'
    def isSameCycle(self, timestamp1, timestamp2):
        return pktimestamp.getMonthStartTimestamp(timestamp1) \
                == pktimestamp.getMonthStartTimestamp(timestamp2)
                
class TimeCycleRegister(TYConfableRegister):
    _typeid_clz_map = {
        TimeCycleLife.TYPE_ID:TimeCycleLife,
        TimeCyclePerDay.TYPE_ID:TimeCyclePerDay,
        TimeCyclePerMonth.TYPE_ID:TimeCyclePerMonth,
    }
    

