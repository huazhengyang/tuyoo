# -*- coding:utf-8 -*-
'''
Created on 2017年9月28日

@author: wangyonghui
'''
from dizhu.entity.dizhufishing import buildRecordUniqueKey, FishHelper
from poker.entity.dao import daobase


@classmethod
def getFishingHistory(cls):
    historyList = daobase.executeRePlayCmd('lrange', buildRecordUniqueKey(), 0, - 1) or []
    ret = []
    for history in historyList:
        try:
            ret.append(eval(history))
        except:
            pass
    return ret

FishHelper.getFishingHistory = getFishingHistory
