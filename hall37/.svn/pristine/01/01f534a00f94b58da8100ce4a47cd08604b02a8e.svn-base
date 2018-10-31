# -*- coding:utf-8 -*-
'''
Created on 2017年10月27日

@author: zhaojiangang
'''
import freetime.util.log as ftlog
from poker.entity.biz.item.item import TYUserBagImpl, TYItemDao, TYItemData
import poker.util.timestamp as pktimestamp


def saveItem(self, userId, item):
    '''
    保存用户道具
    '''
    if item.kindId == 1086:
        ftlog.info('TYItemDao.saveItem',
                   'userId=', userId,
                   'kindId=', item.kindId,
                   'itemId=', item.itemId)
    itemDataBytes = TYItemData.encodeToBytes(item.encodeToItemData())
    self._itemDataDao.saveItem(userId, item.itemId, itemDataBytes)


def removeItem(self, userId, item):
    '''
    删除用户道具
    '''
    if item.kindId == 1086:
        ftlog.info('TYItemDao.removeItem',
                   'userId=', userId,
                   'kindId=', item.kindId,
                   'itemId=', item.itemId)
    self._itemDataDao.removeItem(userId, item.itemId)


TYItemDao.saveItem = saveItem
TYItemDao.removeItem = removeItem


def processWhenUserLogin(self, gameId, isDayFirst, timestamp=None):
    '''
    当用户登录时调用该方法，处理对用户登录感兴趣的道具
    @param gameId: 哪个游戏驱动
    @param isDayFirst: 是否是
    '''
    items = list(self._itemIdMap.values())
    timestamp = timestamp if timestamp is not None else pktimestamp.getCurrentTimestamp()
    for item in items:
        needRemove = False
        if item.needRemoveFromBag(timestamp):
            self._removeItem(item)
            needRemove = True
        else:
            item.itemKind.processWhenUserLogin(item, self._assets,
                                               gameId, isDayFirst, timestamp)
        
        try:
            if item.kindId == 1086:
                ftlog.info('TYUserBagImpl.processWhenUserLogin',
                           'userId=', self.userId,
                           'itemId=', item.itemId,
                           'itemData=', item.encodeToItemData().toDict(),
                           'needRemove=', needRemove,
                           'timestamp=', timestamp)
        except:
            ftlog.warn('TYUserBagImpl.processWhenUserLogin',
                       'userId=', self.userId,
                       'itemId=', item.itemId,
                       'itemData=', item.encodeToItemData().toDict(),
                       'needRemove=', needRemove,
                       'timestamp=', timestamp)


TYUserBagImpl.processWhenUserLogin = processWhenUserLogin


