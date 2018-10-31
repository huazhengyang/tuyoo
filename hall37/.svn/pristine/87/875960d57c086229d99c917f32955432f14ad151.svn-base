# -*- coding: utf-8 -*-
'''
Created on 2015年5月20日

@author: zqh
'''
from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from hall.entity import hallitem
from hall.entity.hallconf import HALL_GAMEID
from hall.entity.hallitem import TYDecroationItem
from hall.servers.util.item_handler import ItemHelper
from poker.entity.biz.exceptions import TYBizException
from poker.entity.biz.item.exceptions import TYItemException, \
    TYItemNotFoundException
from poker.entity.configure import configure
from poker.entity.dao import sessiondata
import poker.entity.dao.gamedata as pkgamedata
from poker.protocol.rpccore import markRpcCall
import poker.util.timestamp as pktimestamp


def ensureItemExistsOld(userBag, itemId):
    # 老版本不支持非互斥型道具
    item = userBag.getItemByKindId(itemId)
    if not item:
        raise TYItemNotFoundException(itemId)
    return item
    
    
def _encodeItem(kindId, item, timestamp):
    count = startTime = 0
    if item:
        count = item.balance(timestamp)
        if item.itemKind.units.isTiming():
            startTime = max(0, timestamp - 86400 * count)
    return {
        'itemId':kindId,
        'count':count,
        'startTime':startTime
    }
    
    
def getUserItem(userId, gameId, kindId, userBag):
    item = userBag.getItemByKindId(kindId)
    if not item:
        raise TYItemNotFoundException(kindId)
    timestamp = pktimestamp.getCurrentTimestamp()
    return _encodeItem(kindId, item, timestamp)


def getUserItemList(userId, gameId, userBag):
    result = []
    items = userBag.getAllItem()
    timestamp = pktimestamp.getCurrentTimestamp()
    for item in items:
        if item.itemKind.singleMode:
            result.append(_encodeItem(item.kindId, item, timestamp))
    return result


def addUserItem(userId, gameId, kindId, count, eventId, userBag):
    timestamp = pktimestamp.getCurrentTimestamp()
    itemKind = hallitem.itemSystem.findItemKind(kindId)
    if not itemKind:
        ftlog.warn('TYOldItemTransfer.addUserItem gameId=', gameId, 'userId=', userId, 'itemKindId=', kindId, 'err=', 'UnknownItemKindId')
        raise TYItemException(-1, '未知的道具类型')
    item = userBag.addItemUnitsByKind(gameId, itemKind, count, timestamp, 0, eventId, 0)
    return _encodeItem(kindId, item[0], timestamp)


def consumeUserItem(userId, gameId, kindId, count, eventId, userBag):
    timestamp = pktimestamp.getCurrentTimestamp()
    itemKind = hallitem.itemSystem.findItemKind(kindId)
    if not itemKind:
        ftlog.warn('TYOldItemTransfer.consumeUserItem gameId=', gameId, 'userId=', userId, 'itemKindId=', kindId, 'err=', 'UnknownItemKindId')
        raise TYItemException(-1, '未知的道具类型')
    count = userBag.consumeUnitsCountByKind(gameId, itemKind, count, timestamp, eventId, 0)
    item = userBag.getItemByKindId(kindId)
    balance = userBag.calcTotalUnitsCount(itemKind)
    val = {
           "cCount": count,
           "itemId": kindId,
           "count": balance,
           "startTime": item.createTime if item else 0
    }
    
    return val


def useUserItem(userId, gameId, kindId, userBag):
    item = None
    try :
        item = ensureItemExistsOld(userBag, kindId)
    except (TYBizException, TYItemException) as e:
        ftlog.warn('useUserItem.handleException gameId=', gameId, 'userId=', userId, 'itemId=', kindId, 'errorCode=', e.errorCode, 'message=', e.message)
        val = {
            "error": e.message
        }
        return val
    if not item :
        ftlog.warn('useUserItem the item is none, gameId=', gameId, 'userId=', userId, 'itemId=', kindId)
        val = {
            "error": 'the item is none'
        }
        return val

    actionName = ItemHelper.translateUseActionName(item)
    if actionName:
        try:
            item = userBag.getItemByKindId(kindId)
            actionResult = userBag.doAction(gameId, item, actionName)
            message = actionResult.message
            itemKind = hallitem.itemSystem.findItemKind(kindId)
            balance = userBag.calcTotalUnitsCount(itemKind)
            val = {
                   "itemId": kindId,
                   "startTime": item.createTime if item else 0,
                   "count": balance,
                   "info": message
            }
            return val
        except (TYBizException, TYItemException) as e:
            ftlog.warn('useUserItem.handleException gameId=', gameId, 'userId=', userId, 'itemId=', kindId, 'errorCode=', e.errorCode, 'message=', e.message)
            val = {
                "error": e.message
            }
            
            return val
    raise TYItemException(-1, 'item action not found')


def updateTimingUserItems(userId, gameId, isDayFirst, userBag):
    '''
    @return: []
    '''
    userBag.processWhenUserLogin(gameId, isDayFirst)
    val = {
           "items":[]
    }
    
    return val


def loadUserDecroation(userId, gameId, userBag):
    decroationItemList = userBag.getAllTypeItem(TYDecroationItem)
    items = []
    for decroationItem in decroationItemList:
        if decroationItem.isWore:
            items.append(decroationItem.itemKind.kindId)
    
    val = {
        'itemIds': items
    }
    return val


def eventIdToString(eventId):
    eventIds = configure.getJson('poker:map.bieventid', {})
    for key, value in eventIds.iteritems():
        if eventId == value:
            return key
    return "UNKNOWN"


@markRpcCall(groupName="userId", lockName="userId", syncCall=1)
def doOldRemoteCallNew(userId, msgline):
    '''
    必须要返回dict的实例
    '''
    try:
        ftlog.debug('doOldRemoteCallNew->msgline=', msgline)
        
        msg = MsgPack()
        msg.unpack(msgline)
        action = msg.getAction()
        gameId = msg.getParam('gameId', -1)
        userId = msg.getParam('userId', -1)
        userBag = hallitem.itemSystem.loadUserAssets(userId).getUserBag()
        clientId = sessiondata.getClientId(userId)
        if pkgamedata.setnxGameAttr(userId, HALL_GAMEID, 'flag.item.trans', 1) == 1:
            hallitem._tranformItems(gameId, userId, clientId, userBag)
            
        mo = MsgPack()
        mo.setResult('action', action)
        if action == 'getUserItem':
            kindId = msg.getParam('itemId', -1)
            val = getUserItem(userId, gameId, kindId, userBag)
            mo.setResult('item', val)
        
        elif action == 'getUserItemList':
            result = getUserItemList(userId, gameId, userBag)
            mo.setResult('item', result)

        elif action == 'addUserItem':
            kindId = msg.getParam('itemId', -1)
            count = msg.getParam('count', -1)
            eventId = msg.getParam('eventId', -1)
            eventId = eventIdToString(eventId)
            ftlog.debug('addUserItem itemId=', kindId, 'count=', count, 'eventId=', eventId)
            val = addUserItem(userId, gameId, kindId, count, eventId, userBag)
            mo.setResult('item', val)
        
        elif action == 'addUserItems':
            pass
        elif action == 'consumeUserItem':
            kindId = msg.getParam('itemId', -1)
            count = msg.getParam('count', -1)
            eventId = msg.getParam('eventId', -1)
            eventId = eventIdToString(eventId)
            ftlog.debug('consumeUserItem itemId=', kindId, 'count=', count, 'eventId=', eventId)
            val = consumeUserItem(userId, gameId, kindId, count, eventId, userBag)
            mo.setResult('item', val)
        elif action == 'useUserItem':
            kindId = msg.getParam('itemId', -1)
            val = useUserItem(userId, gameId, kindId, userBag)
            mo.setResult('item', val)
        elif action == 'updateTimingUserItems':
            isDayFirst = msg.getParam('isDayFirst', False)
            val = updateTimingUserItems(userId, gameId, isDayFirst, userBag)
            mo.setResult('item', val)
        elif action == 'loadUserDecroation':
            val = loadUserDecroation(userId, gameId, userBag)
            mo.setResult('item', val)
        else:
            ftlog.error('doOldRemoteCallNew unknown rpc action action=', action, 'gameId=', gameId, 'userId=', userId)
        
        ftlog.debug('doOldRemoteCallNew->mo=', mo._ht)
        mo.setResult('code', 0)
        return mo._ht
    except TYItemException:
        mo = MsgPack()
        mo.setResult('code', -1)
        return mo._ht
    except:
        ftlog.error()
        mo = MsgPack()
        mo.setResult('code', -1)
        return mo._ht

