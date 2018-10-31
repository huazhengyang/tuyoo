# -*- coding:utf-8 -*-
'''
Created on 2018年10月29日

@author: wangyonghui
'''
from poker.entity.dao import daobase
import poker.util.timestamp as pktimestamp


class RewardIdGenRedis(object):
    ''' 奖励ID生成器 '''
    @classmethod
    def genRewardId(cls, nowTimestamp):
        cls.updateRewardIdInfo(nowTimestamp)
        return daobase.executeRePlayCmd('HINCRBY', 'reward.system.id.number', 'number', 1)

    @classmethod
    def updateRewardIdInfo(cls, nowTimestamp):
        ''' ID 从 1000001 开始 '''
        timstamp = int(daobase.executeRePlayCmd('HGET', 'reward.system.id.number', 'timestamp') or 0)
        if not pktimestamp.is_same_day(nowTimestamp, timstamp):
            daobase.executeRePlayCmd('HSET', 'reward.system.id.number', 'number', 1000000)
            daobase.executeRePlayCmd('HSET', 'reward.system.id.number', 'timestamp', nowTimestamp)
