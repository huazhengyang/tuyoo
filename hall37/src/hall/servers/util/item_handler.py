# -*- coding: utf-8 -*-
'''
Created on 2015年5月20日

@author: zqh
'''

from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from hall.entity import hallitem, hallstore, hallpopwnd
from hall.entity.hallitem import TYDecroationItem, TYBoxItem, TYSwitchItem, \
    TYItemBindingsException, TYExchangeItem
from hall.entity.todotask import TodoTaskShowInfo, TodoTaskGotoShop, \
    TodoTaskHelper, TodoTaskPopTip, TodoTaskRegister
from hall.servers.common.base_checker import BaseMsgPackChecker
from poker.entity.biz.exceptions import TYBizException
from poker.entity.biz.item.exceptions import TYItemNotFoundException, \
    TYItemActionConditionNotEnoughException
from poker.protocol import router, runcmd
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod
import poker.util.timestamp as pktimestamp
from poker.util import strutil


class ItemHelper(object):
    TRANSLATE_MAP = {
        "9999_6": {
            "2003": 30,
            "2002": 40,
            "1001": 70,
            "1009": 79,
            "1002": 80,
            "3002": 90,
            "3001": 91,
            "1008": 100,
            "1007": 110,
            "1004": 120,
            "1005": 121,
            "1006": 122,
            "130": 130,
            "131": 131,
        },
        "6_9999": {
            "30": 2003,
            "40": 2002,
            "70": 1001,
            "79": 1009,
            "80": 1002,
            "90": 3002,
            "91": 3001,
            "100": 1008,
            "110": 1007,
            "120": 1004,
            "121": 1005,
            "122": 1006,
            "130": 130,
            "131": 131,
        }
    }
    
    @classmethod
    def makeItemListResponse(cls, gameId, userId):
        mo = MsgPack()
        mo.setCmd('bag')
        mo.setResult('action', 'update')
        mo.setResult('gameId', gameId)
        mo.setResult('userId', userId)
        mo.setResult('normal_list', cls.queryUserItemList(gameId, userId))
        mo.setResult('special_list', [])
        return mo

    @classmethod
    def translateItemId(cls, fromGameId, toGameId, itemId):
        assert (9999 in (fromGameId, toGameId))
        if fromGameId == toGameId:
            return itemId

        translateKey = '%s_%s' % (fromGameId, toGameId)
        translateMap = cls.TRANSLATE_MAP.get(translateKey)
        if not translateMap:
            return itemId
        return translateMap.get(str(itemId), -1)

    @classmethod
    def translateUseActionName(cls, item):
        if isinstance(item, TYBoxItem):
            return 'open'
        elif isinstance(item, TYDecroationItem):
            if item.isWore:
                return 'unwear'
            return 'wear'
        elif isinstance(item, TYSwitchItem):
            if item.isOn:
                return 'turnOff'
            return 'turnOn'
        return None

    @classmethod
    def queryUserItemList(cls, gameId, userId):
        ret = []
        userBag = hallitem.itemSystem.loadUserAssets(userId).getUserBag()
        itemList = userBag.getAllItem()
        timestamp = pktimestamp.getCurrentTimestamp()
        for item in itemList:
            if (not item.itemKind.singleMode
                or not item.itemKind.visibleInBag
                or not item.visibleInBag(timestamp)):
                continue
            itemId = cls.translateItemId(9999, gameId, item.itemKind.kindId)
            actionNameForUse = cls.translateUseActionName(item)
            if itemId != -1:
                balance = item.balance(timestamp)
                # 记牌器特殊处理，老版本客户端只认30这个itemId
                useGameId = 9999
                if item.kindId == 2003:
                    itemId = 30
                    useGameId = 6
                data = {
                    'id': itemId,
                    'name': item.itemKind.displayName,
                    'count': '%s%s' % (balance, item.itemKind.units.displayName),
                    'desc': item.itemKind.desc,
                    'pic': item.itemKind.pic,
                    'canUse': True if actionNameForUse else False,
                    'num': balance,
                    'gameId': useGameId
                }
                ret.append(data)
        return ret

    @classmethod
    def makeItemListResponseV3_7(cls, gameId, userId):
        mo = MsgPack()
        mo.setCmd('item')
        mo.setResult('action', 'list')
        mo.setResult('gameId', gameId)
        mo.setResult('userId', userId)
        mo.setResult('tabs', cls.queryUserItemTabsV3_7(gameId, userId))
        return mo
    
    @classmethod
    def makeItemListResponseByGame(cls, gameId, userId):
        mo = MsgPack()
        mo.setCmd('item')
        mo.setResult('action', 'list_by_game')
        mo.setResult('gameId', gameId)
        mo.setResult('userId', userId)
        mo.setResult('tabs', cls.queryUserItemTabsByGame(gameId, userId))
        return mo

    @classmethod
    def encodeItemAction(cls, gameId, userBag, item, action, timestamp):
        from poker.entity.dao import sessiondata
        from hall.entity.hallitem import TYItemActionExchange
        if isinstance(action, TYItemActionExchange) and action.isJdActualProduct():
            clientIdVer = sessiondata.getClientIdVer(userBag.userId)
            if clientIdVer < 3.90:
                return {
                   'action':action.name,
                   'type': action.TYPE_ID,
                   'name':action.displayName
                }
        ret = {
            'action': action.name,
            'type': action.TYPE_ID,
            'name': action.displayName,
        }
        inputParams = action.getInputParams(gameId, userBag, item, timestamp)
        if inputParams:
            ret['params'] = inputParams
        return ret


    @classmethod
    def encodeItemActionList(cls, gameId, userBag, item, timestamp):
        ret = []
        actions = userBag.getExecutableActions(item, timestamp)
        for action in actions:
            ret.append(cls.encodeItemAction(gameId, userBag, item, action, timestamp))
        return ret

    @classmethod
    def encodeUserItem(cls, gameId, userBag, item, timestamp):
        ret = {
            'id': item.itemId,
            'kindId': item.kindId,
            'gameId': item.itemKind.gameId,
            'catagoryId': item.itemKind.catagoryId,
            'sortId': item.itemKind.sortId,
            'catagoryDesc': item.itemKind.catagoryDesc,
            'name': item.itemKind.displayName,
            'units': item.itemKind.units.displayName,
            'desc': item.itemKind.desc,
            'pic': item.itemKind.pic,
            'count': max(1, item.remaining),
            'maskinbag': item.itemKind.maskinbag,
            'actions': cls.encodeItemActionList(gameId, userBag, item, timestamp)
        }
        if item.expiresTime >= 0:
            ret['expires'] = item.expiresTime
        # 3.9 物品描述中的过去时间要向客户端传递
        if item.itemKind.expiresTime:
            ret['expiresTime'] = item.itemKind.expiresTime
        if item.itemKind.actionPackage:
            ret['actionPackage'] = item.itemKind.actionPackage
        return ret

    @classmethod
    def encodeUserItemList(cls, gameId, userBag, timestamp):
        ret = []
        itemList = userBag.getAllItem()
        for item in itemList:
            # 捕鱼插件中宝石和勋章特殊处理
            #if item.kindId in (1223, 1224):
            #    ret.append(cls.encodeUserItem(gameId, userBag, item, timestamp))
            #    continue
            if item.itemKind.visibleInBag and item.visibleInBag(timestamp):
                ret.append(cls.encodeUserItem(gameId, userBag, item, timestamp))
        return ret
    
    @classmethod
    def encodeUserItemListByGame(cls, gameId, userBag, timestamp):
        ret = []
        itemList = userBag.getAllItem()
        for item in itemList:
            ftlog.debug('encodeUserItemListByGame item gameId:', item.itemKind.gameId, ' request gameId:', gameId)
            if item.isExpires(timestamp):
                continue
            if item.itemKind.gameId == gameId:
                ret.append(cls.encodeUserItem(gameId, userBag, item, timestamp))
            ## bycj PhoneCard
            if item.kindId in [4179, 4178, 4141] and item.state == TYExchangeItem.STATE_NORMAL:
                ret.append(cls.encodeUserItem(gameId, userBag, item, timestamp))
        return ret

    @classmethod
    def queryUserItemTabsV3_7(cls, gameId, userId, userBag=None):
        ret = []
        if userBag is None:
            userBag = hallitem.itemSystem.loadUserAssets(userId).getUserBag()
        timestamp = pktimestamp.getCurrentTimestamp()
        ret.append({'name': '', 'items': cls.encodeUserItemList(gameId, userBag, timestamp)})
        return ret
    
    @classmethod
    def queryUserItemTabsByGame(cls, gameId, userId, userBag = None):
        ret = []
        if userBag is None:
            userBag = hallitem.itemSystem.loadUserAssets(userId).getUserBag()
        timestamp = pktimestamp.getCurrentTimestamp()
        ret.append({'name': '', 'items':cls.encodeUserItemListByGame(gameId, userBag, timestamp)})
        return ret

    @classmethod
    def makeDoActionResponse(cls, gameId, userId, actionResult):
        mo = MsgPack()
        mo.setCmd('bag')
        mo.setResult('gameId', gameId)
        mo.setResult('userId', userId)
        mo.setResult('action', 'open')
        mo.setResult('info', actionResult.message)
        return mo


@markCmdActionHandler
class ItemTcpHandler(BaseMsgPackChecker):
    UNSUPPORTED_TODOTASK_PC = {
        'typeId':'todotask.showInfo',
        'info':'抱歉,您的游戏版本暂不支持该兑换,请前往手机应用市场下载最新版本《途游斗地主》手机应用进行兑换,或联系客服4008-098-000兑换.',
    }
    
    UNSUPPORTED_TODOTASK = {
        'typeId':'todotask.showInfo',
        'info':'抱歉,您的游戏版本太老了，请前往应用市场下载最新版本游戏进行兑换.',
    }
    
    def __init__(self):
        pass

    def _check_param_itemId(self, msg, key, params):
        itemId = msg.getParam('id')
        if not itemId:
            itemId = msg.getParam('itemId')
        if itemId and isinstance(itemId, int):
            return None, itemId
        return 'ERROR of itemId !' + str(itemId), None

    def _check_param_params(self, msg, key, params):
        ret = msg.getParam('params')
        if ret and not isinstance(ret, dict):
            return 'ERROR of params !' + str(ret), None
        return None, ret

    @markCmdActionMethod(cmd='item', action="list", clientIdVer=3.7)
    def doItemListV3_7(self, gameId, userId):
        mo = ItemHelper.makeItemListResponseV3_7(gameId, userId)
        router.sendToUser(mo, userId)
        
    @markCmdActionMethod(cmd='item', action="list_by_game", clientIdVer=3.7)
    def doItemListByGame(self, gameId, userId):
        mo = ItemHelper.makeItemListResponseByGame(gameId, userId)
        router.sendToUser(mo, userId)

    def _isNotPCorMAC(self, clientId):
        return strutil.isTheOsClient(clientId, 'winpc') or strutil.isTheOsClient(clientId, 'mac')
    
    def _doItemActionUnsupportedExchange(self, gameId, userId, clientId, itemId, params):
        todotaskD = self.UNSUPPORTED_TODOTASK_PC if self._isNotPCorMAC(clientId) else self.UNSUPPORTED_TODOTASK
        todotaskFac = TodoTaskRegister.decodeFromDict(todotaskD)
        if todotaskFac:
            todotask = todotaskFac.newTodoTask(gameId, userId, clientId)
            TodoTaskHelper.sendTodoTask(gameId, userId, todotask)
    
    def _doItemAction(self, gameId, userId, clientId, itemId, params):
        from hall.entity.hallitem import TYItemActionExchange
        from poker.entity.dao import sessiondata
        try:
            timestamp = pktimestamp.getCurrentTimestamp()
            userBag = hallitem.itemSystem.loadUserAssets(userId).getUserBag()
            item = userBag.findItem(itemId)
            if not item:
                raise TYItemNotFoundException(itemId)
            actionName = runcmd.getMsgPack().getParam('action')
            
            if ftlog.is_debug():
                ftlog.debug('ItemTcpHandler._doItemAction',
                            'gameId=', gameId,
                            'userId=', userId,
                            'clientId=', clientId,
                            'itemId=', itemId,
                            'params=', params)
                
            action = item.itemKind.findActionByName(actionName)
            # 3.9以下不支持京东实物
            if action and isinstance(action, TYItemActionExchange) and action.isJdActualProduct():
                clientIdVer = sessiondata.getClientIdVer(userBag.userId)
                if clientIdVer < 3.90:
                    self._doItemActionUnsupportedExchange(gameId, userId, clientId, itemId, params)
                    return
                
            actionResult = userBag.doAction(gameId, item, actionName, timestamp, params)

            mo = ItemHelper.makeItemListResponseV3_7(gameId, userId)
            router.sendToUser(mo, userId)

            _, cVer, _ = strutil.parseClientId(clientId)
            if actionResult:
                if actionResult.todotask and cVer >= 3.90:
                    TodoTaskHelper.sendTodoTask(gameId, userId, actionResult.todotask)
                elif actionResult.message:
                    if isinstance(actionResult.action, TYItemActionExchange) and actionResult.action.isWechatRedPack():
                        mytodo = TodoTaskShowInfo(actionResult.message)
                    else:
                        mytodo = TodoTaskPopTip(actionResult.message)
                    TodoTaskHelper.sendTodoTask(gameId, userId, mytodo)

        except TYBizException, e:
            self.handleException(itemId, gameId, userId, clientId, e)
            
    @markCmdActionMethod(cmd='item', action="*", clientIdVer=3.7)
    def doItemAction(self, gameId, userId, clientId, itemId, params):
        self._doItemAction(gameId, userId, clientId, itemId, params)

    @markCmdActionMethod(cmd='bag', action="update", clientIdVer=0)
    def doBagUpdate(self, gameId, userId):
        mo = ItemHelper.makeItemListResponse(gameId, userId)
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd='bag', action="open", clientIdVer=0)
    def doItemUseOld(self, gameId, userId, itemId, clientId):
        try:
            # 老版本只认30这个itemId
            if itemId == 30:
                itemId = 2003
            itemId = ItemHelper.translateItemId(gameId, 9999, itemId)
            userBag = hallitem.itemSystem.loadUserAssets(userId).getUserBag()
            item = self._ensureItemExistsOld(userBag, itemId)
            actionName = ItemHelper.translateUseActionName(item)
            if actionName:
                actionResult = userBag.doAction(gameId, item, actionName)
                router.sendToUser(ItemHelper.makeDoActionResponse(gameId, userId, actionResult), userId)
                router.sendToUser(ItemHelper.makeItemListResponse(gameId, userId), userId)
            else:
                mo = MsgPack()
                mo.setCmd('bag')
                mo.setResult('gameId', gameId)
                mo.setResult('userId', userId)
                mo.setResult('itemId', itemId)
                mo.setError(-1, '该道具不能使用')
                router.sendToUser(mo, userId)
        except TYBizException, e:
            self.handleException(itemId, gameId, userId, clientId, e)

    def _check_param_users(self, msg, key, params):
        users = msg.getParam(key)
        if users is not None and not isinstance(users, list):
            return 'ERROR of users !' + str(users), None
        return None, users

    def _ensureItemExistsOld(self, userBag, itemId):
        # 老版本不支持非互斥型道具
        item = userBag.getItemByKindId(itemId)
        if not item:
            raise TYItemNotFoundException(itemId)
        return item

    def handleItemActionConditionException(self, itemId, gameId, userId, clientId, e):
        showInfo = TodoTaskShowInfo(e.message)
        payOrder = e.condition.getParam('payOrder')
        if payOrder:
            product, shelves = hallstore.findProductByPayOrder(gameId, userId, clientId, payOrder)
            if product:
                showInfo.setSubCmd(TodoTaskGotoShop(shelves.name))
        else:
            todotask = e.condition.getParam('todotask')
            if todotask:
                factory = hallpopwnd.decodeTodotaskFactoryByDict(todotask)
                if factory:
                    todotask = factory.newTodoTask(gameId, userId, clientId)
                    TodoTaskHelper.sendTodoTask(gameId, userId, todotask)
                    return
        TodoTaskHelper.sendTodoTask(gameId, userId, showInfo)

    def handleItemBindingsException(self, itemId, gameId, userId, clientId, e):
        showInfo = TodoTaskShowInfo(e.message)
        payOrder = e.itemBindings.getParam('payOrder')
        if payOrder:
            product, shelves = hallstore.findProductByPayOrder(gameId, userId, clientId, payOrder)
            if product:
                showInfo.setSubCmd(TodoTaskGotoShop(shelves.name))
        else:
            todotask = e.itemBindings.getParam('todotask')
            if todotask:
                todotask = TodoTaskRegister.decodeFromDict(todotask).newTodoTask(gameId, userId, clientId)
                TodoTaskHelper.sendTodoTask(gameId, userId, todotask)
                return
        TodoTaskHelper.sendTodoTask(gameId, userId, showInfo)

    def handleException(self, itemId, gameId, userId, clientId, e):
        if ftlog.is_debug():
            ftlog.debug('ItemTcpHandler.handleException itemId=', itemId,
                        'gameId=', gameId,
                        'userId=', userId,
                        'clientId=', clientId,
                        'e=', e)
        if isinstance(e, TYItemActionConditionNotEnoughException):
            self.handleItemActionConditionException(itemId, gameId, userId, clientId, e)
        elif isinstance(e, TYItemBindingsException):
            self.handleItemBindingsException(itemId, gameId, userId, clientId, e)
        else:
            TodoTaskHelper.sendTodoTask(gameId, userId, TodoTaskShowInfo(e.message))
