# -*- coding:utf-8 -*-
'''
Created on 2017年11月9日

@author: zhaojiangang
'''
from poker.entity.biz.confobj import TYConfableRegister, TYConfable
import poker.util.timestamp as pktimestamp


class HallTimeCycle(TYConfable):
    '''
    时间周期
    '''
    def isSameCycle(self, ts1, ts2):
        '''
        判断ts1和ts2是否属于同一个周期
        '''
        raise NotImplementedError
    
    def decodeFromDict(self, d):
        return self


class HallTimeCycleLife(HallTimeCycle):
    '''
    life周期
    '''
    TYPE_ID = 'life'
    
    def isSameCycle(self, ts1, ts2):
        '''
        判断ts1和ts2是否属于同一个周期
        '''
        return True


class HallTimeCycleDay(HallTimeCycle):
    '''
    每天为一周期
    '''
    TYPE_ID = 'day'
    
    def isSameCycle(self, ts1, ts2):
        '''
        判断ts1和ts2是否属于同一个周期
        '''
        return pktimestamp.is_same_day(ts1, ts2)


class HallTimeCycleRegister(TYConfableRegister):
    _typeid_clz_map = {
        HallTimeCycleDay.TYPE_ID:HallTimeCycleDay,
        HallTimeCycleLife.TYPE_ID:HallTimeCycleLife,
    }


