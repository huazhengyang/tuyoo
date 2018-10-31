# -*- coding: utf-8 -*-
'''
'''
from hall.entity import hallitem, datachangenotify
from poker.protocol.rpccore import markRpcCall
import poker.util.timestamp as pktimestamp
from hall.entity.hallitem import TYDecroationItemKind
from hall.servers.util.item_handler import ItemHelper
from datetime import datetime
from hall.entity.hallconf import HALL_GAMEID


def makeErrorResponse(ec, message):
    return {'ec':ec, 'message':message}


def makeResponse(result):
    assert(isinstance(result, dict))
    return result


def notifyChangedForItem(gameId, userId, itemKind):
    changed = ['item']
    if isinstance(itemKind, TYDecroationItemKind):
        changed.append('decoration')
    datachangenotify.sendDataChangeNotify(HALL_GAMEID, userId, changed)
    

def encodeItem(userBag, item, timestamp):
    ret = {
        'itemId':item.itemId,
        'kindId':item.kindId,
        'displayName':item.itemKind.displayName,
        'pic':item.itemKind.pic,
        'count':max(1, item.balance(timestamp)),
        'units':item.itemKind.units.displayName,
        'actions':ItemHelper.encodeItemActionList(HALL_GAMEID, userBag, item, timestamp)
    }
    if item.itemKind.units.isTiming and item.expiresTime > 0:
        ret['expires'] = datetime.fromtimestamp(item.expiresTime).strftime('%Y-%m-%d %H:%M:%S')
    return ret


@markRpcCall(groupName="", lockName="", syncCall=1)
def listItem():
    itemKindList = hallitem.itemSystem.getAllItemKind()
    items = []
    for itemKind in itemKindList:
        items.append({
            'kindId':itemKind.kindId,
            'displayName':itemKind.displayName,
            'masks':itemKind.masks if isinstance(itemKind, TYDecroationItemKind) else 0
        })
    return 0, items


@markRpcCall(groupName="userId", lockName="userId", syncCall=1)
def getUserItemsCount(userId):
    userBag = hallitem.itemSystem.loadUserAssets(userId).getUserBag()
    timestamp = pktimestamp.getCurrentTimestamp()
    items = {}
    for item in userBag.getAllItem():
        items[item.kindId] = {'count':max(1, item.balance(timestamp))}
    return items


@markRpcCall(groupName="userId", lockName="userId", syncCall=1)
def listUserItem(userId):
    userBag = hallitem.itemSystem.loadUserAssets(userId).getUserBag()
    items = []
    timestamp = pktimestamp.getCurrentTimestamp()
    for item in userBag.getAllItem():
        items.append(encodeItem(userBag, item, timestamp))
    return 0, items

    
@markRpcCall(groupName="userId", lockName="userId", syncCall=1)
def removeUserItem(gameId, userId, itemId, eventId, intEventParam=0):
    userBag = hallitem.itemSystem.loadUserAssets(userId).getUserBag()
    item = userBag.findItem(itemId)
    if not item:
        return -1, '道具不存在: %s' % (itemId)
    timestamp = pktimestamp.getCurrentTimestamp()
    userBag.removeItem(gameId, item, timestamp, eventId, intEventParam)
    notifyChangedForItem(gameId, userId, item.itemKind)
    return 0, None


@markRpcCall(groupName="userId", lockName="userId", syncCall=1)
def addUserItem(gameId, userId, kindId, count, eventId, intEventParam=0):
    timestamp = pktimestamp.getCurrentTimestamp()
    itemKind = hallitem.itemSystem.findItemKind(kindId)
    if not itemKind:
        return -1, '不能识别的道具类型: %s' % (kindId)
    userBag = hallitem.itemSystem.loadUserAssets(userId).getUserBag()
    userBag.addItemUnitsByKind(gameId, itemKind, count, timestamp, 0,
                               eventId, intEventParam)
    notifyChangedForItem(gameId, userId, itemKind)
    return 0, None


@markRpcCall(groupName="userId", lockName="userId", syncCall=1)
def consumeUserItemByKind(gameId, userId, kindId, count, eventId, intEventParam=0):
    if count <= 0:
        return -1, 'count参数必须大于0: %s' % (count)
    itemKind = hallitem.itemSystem.findItemKind(kindId)
    if not itemKind:
        return -1, '不能识别的道具类型: %s' % (kindId)

    timestamp = pktimestamp.getCurrentTimestamp()
    userBag = hallitem.itemSystem.loadUserAssets(userId).getUserBag()
    consumeCount = userBag.consumeUnitsCountByKind(gameId, itemKind, count, timestamp,
                                                   eventId, intEventParam)
    if consumeCount < count:
        return -1, '道具数量不足'
    notifyChangedForItem(gameId, userId, itemKind)
    return 0, None

