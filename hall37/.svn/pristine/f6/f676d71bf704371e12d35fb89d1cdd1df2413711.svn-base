# -*- coding:utf-8 -*-
'''
Created on 2016年5月25日

@author: zhaojiangang
'''
from hall.entity import hallitem
from hall.entity.hallitem import TYExchangeItem
import freetime.util.log as ftlog

userId = 170385860
userAssets = hallitem.itemSystem.loadUserAssets(userId)
userBag = userAssets.getUserBag()

items = userBag.getAllKindItemByKindId(4141)
items = []
for item in items:
    if item.state == TYExchangeItem.STATE_NORMAL:
        items.append(item)
        
def removeItem(self, gameId, item, timestamp, eventId, intEventParam):

ftlog.info('hotfix_item_4141_toomuch userId=', userId,
           'itemsIds=', [item.itemId for item in items],
           'count=', len(items))

