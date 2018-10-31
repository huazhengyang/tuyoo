# -*- coding:utf-8 -*-
'''
Created on 2017年6月8日

@author: zhaojiangang
'''

import freetime.util.log as ftlog
from hall.entity.hall_item_exchange import HallItemAutoExchange


def decodeFromDict(self, d):
    from hall.entity.hallusercond import UserConditionRegister
    self.conditions = UserConditionRegister.decodeList(d.get('conditions', []))
    self.itemSrc = d.get('itemIdSrc', None)
    self.itemDst = d.get('itemIdDst', None)
    self.ratio = d.get('ratio', 0)
    self.message = d.get('message', None)
    if (not self.itemSrc) or (not self.message) or (not self.itemDst) or (not self.ratio) or (self.ratio < 1) or (not isinstance(self.ratio, int)):
        ftlog.error('HallItemAutoExchange.exchange config error. src:', self.itemSrc, ' dst:', self.itemDst, ' ratio:', self.ratio)
        return None
    if self.itemDst == self.itemSrc:
        ftlog.error('HallItemAutoExchange.exchange config error. src:', self.itemSrc, ' dst:', self.itemDst, ' ratio:', self.ratio)
        return None
    return self

HallItemAutoExchange.decodeFromDict = decodeFromDict