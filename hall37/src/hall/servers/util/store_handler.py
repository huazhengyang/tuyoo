# -*- coding=utf-8
'''
Created on 2015年7月8日

@author: zhaojiangang
'''
from datetime import datetime
from sre_compile import isstring

from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from hall.entity import hallstore, hallitem, datachangenotify, hall_first_recharge
from hall.entity import hallvip
from hall.entity.todotask import TodoTaskPayOrder, TodoTaskShowInfo, \
    TodoTaskHelper, TodoTaskGotoShop
from hall.game import TGHall
from hall.servers.common.base_checker import BaseMsgPackChecker
from poker.entity.biz import orderid
from poker.entity.biz.exceptions import TYBizException
import poker.entity.biz.message.message as pkmessage
from poker.entity.biz.store.exceptions import TYBuyProductUnknownException
from poker.entity.biz.store.store import TYChargeInfo
from poker.entity.configure import pokerconf
from poker.entity.events.tyevent import ChargeNotifyEvent
from poker.protocol import router, runcmd
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod
from poker.util import strutil
import poker.util.timestamp as pktimestamp
from poker.entity.dao import sessiondata, paydata
from hall.entity.hallusercond import UserConditionRegister
from hall.entity.hallconf import HALL_GAMEID

class StoreHelper(object):
    @classmethod
    def buildProductInfo(cls, product):
        discount = None
        if product.desc.startswith(u'赠'):
            discount = product.desc.split('+')
        info = {
            'id':product.productId,
            'name':product.displayName,
            'nameurl':product.displayNamePic,
            'price':product.price,
            'priceurl':product.pricePic,
            'desc':product.desc,
            'discount':discount if discount else [],
            'pic':product.pic,
            'tag':product.tag,
        }
        if product.buyType:
            info['buy_type'] = product.buyType
        if product.priceDiamond:
            info['price_diamond'] = product.priceDiamond
        if product.diamondExchangeRate:
            info['exchange_rate'] = product.diamondExchangeRate
        if product.extDesc:
            info['addition'] = product.extDesc
        if product.buyLimitDesc:
            info['limit'] = product.buyLimitDesc
        if product.clientParams:
            info['clientParams'] = product.clientParams
        if 'exchange' == product.buyType and product.exchangeFeeContentItem:
            info['cost'] = {
                'itemId':product.exchangeFeeContentItem.assetKindId,
                'count':product.exchangeFeeContentItem.count
            }
        return info
    
    @classmethod
    def buildProductInfos(cls, productList, userId):
        productInfos = []
        if productList:
            for product in productList:
                # 按显示条件过滤
                if cls.isProductShow(product, userId):
                    ftlog.debug('StoreHelper.buildProductInfos product=', product,
                                'userId=', userId,
                                'isProductShow=true')
                    productInfos.append(cls.buildProductInfo(product))
                else:
                    ftlog.debug('StoreHelper.buildProductInfos product=', product,
                                'userId=', userId,
                                'isProductShow=false')
        return productInfos
    
    @classmethod
    def isProductShow(cls, product, userId):
        ftlog.debug('StoreHelper.isProductShow product=', product,
                    'userId=', userId)
        
        if product.showConditions:
            ftlog.debug('StoreHelper.isProductShow product conditions:', product.showConditions)
            pConditions = product.showConditions
            if not isinstance(pConditions, list):
                pConditions = [pConditions]
            conditions = UserConditionRegister.decodeList(pConditions)
            
            for cond in conditions:
                clientId = sessiondata.getClientId(userId)
                if not cond.check(HALL_GAMEID, userId, clientId, pktimestamp.getCurrentTimestamp()):
                    ftlog.debug('StoreHelper.isProductShow not suitable for condition:', cond)
                    return False
        return True
    
    @classmethod
    def shelvesToProductIdList(cls, gameId, userId, clientId, shelves):
        productInfos = cls.buildProductInfos(shelves.productList, userId) if shelves else []
        # 拼十老包需要特殊处理一下，price替换为price_diamond
        if gameId == 10:
            _, clientVer, _ = strutil.parseClientId(clientId)
            if clientVer <= 3.31:
                for productInfo in productInfos:
                    if 'price_diamond' in productInfo:
                        productInfo['price'] = productInfo['price_diamond']
                    productInfo['name'] = ''
        return productInfos

    @classmethod
    def makeStoreConfigResponse(cls, gameId, userId, clientId):
        mo = MsgPack()
        mo.setCmd('store_config')
        mo.setResult('action', 'update')
        chipShelves = hallstore.storeSystem.getShelvesByClientId(gameId, userId, clientId, 'coin')
        itemShelves = hallstore.storeSystem.getShelvesByClientId(gameId, userId, clientId, 'item')
        quickShelves = hallstore.storeSystem.getShelvesByClientId(gameId, userId, clientId, 'quick')
        diamondShelves = hallstore.storeSystem.getShelvesByClientId(gameId, userId, clientId, 'diamond')
        mo.setResult('coin_list', cls.shelvesToProductIdList(gameId, userId, clientId, chipShelves))
        mo.setResult('item_list', cls.shelvesToProductIdList(gameId, userId, clientId, itemShelves))
        mo.setResult('quick_list', cls.shelvesToProductIdList(gameId, userId, clientId, quickShelves))
        mo.setResult('diamond_list', cls.shelvesToProductIdList(gameId, userId, clientId, diamondShelves))
        return mo
    
    @classmethod
    def getStoreTabs(cls, gameId, userId, clientId):
        shelvesList = hallstore.storeSystem.getShelvesListByClientId(gameId, userId, clientId)
        shelvesList.sort(key=lambda shelves:shelves.sortValue)
        tabs = []
        for shelves in shelvesList:
            if shelves.visibleInStore and shelves.productList:
                tabs.append({
                    'name':shelves.displayName,
                    'subStore':shelves.name,
                    'iconType':shelves.iconType,
                    'items':cls.buildProductInfos(shelves.productList, userId)
                })
        ftlog.debug('StoreHandleImpl.getStoreTabs gameId=', gameId,
                    'userId=', userId,
                    'clientId=', clientId,
                    'tabs=', tabs)
        return tabs

    @classmethod
    def getStoreTabByName(cls, gameId, userId, tabName, clientId):
        shelvesList = hallstore.storeSystem.getShelvesListByClientId(gameId, userId, clientId)
        datas = {}
        for shelves in shelvesList:
            if shelves.productList and tabName == shelves.name :
                datas = {
                    'name':shelves.displayName,
                    'subStore':shelves.name,
                    'iconType':shelves.iconType,
                    'items':cls.buildProductInfos(shelves.productList, userId)
                }
                break
        ftlog.debug('StoreHandleImpl.getStoreTabByName gameId=', gameId,
                    'userId=', userId,
                    'clientId=', clientId,
                    'datas=', datas)
        return datas
    
    @classmethod
    def makeStoreConfigResponseV3_5(cls, gameId, userId, clientId):
        mo = MsgPack()
        mo.setCmd('store_config')
        mo.setResult('action', 'update')
        mo.setResult('tabs', cls.getStoreTabs(gameId, userId, clientId))
        return mo

    @classmethod
    def makeProductDeliveryFailResponse(cls):
        mo = MsgPack()
        mo.setCmd('prod_delivery')
        fail = hallstore.storeSystem.deliveryConf.get('fail', {})
        mo.setResult('info', fail.get('title', u'很抱歉，添加物品失败啦！'))
        mo.setResult('content', fail.get('content', u'请尽快联系我们的客服，我们一定会第一时间处理'))
        mo.setResult('tips', fail.get('tips', u'如有问题请拨打客服电话'))
        mo.setError(1, u'很抱歉，添加物品失败啦！')
        return mo
    
    @classmethod
    def makeProductDeliveryErrorResponse(cls, ec, info):
        mo = MsgPack()
        mo.setCmd('prod_delivery')
        mo.setError(ec, info)
        return mo
    
    @classmethod
    def buildProductDeliveryContent(cls, nt, succConf, orderDeliveryResult):
        try:
            sdkItem = None
            consume = ''
            chargeInfo = orderDeliveryResult.order.chargeInfo
            if chargeInfo and chargeInfo.chargeType:
                consume = str(chargeInfo.getCharge('rmb', 0)) + '元'
                dcount = chargeInfo.getCharge('diamond', 0) - chargeInfo.getConsume('coin', 0)
                if dcount > 0:
                    sdkItem = {'name':'钻石', 'count':dcount, 'units':'个'}
            elif chargeInfo:
                consumes = [] 
                for assetKindId, count in chargeInfo.consumeMap.iteritems():
                    if assetKindId == 'coin':
                        consumes.append(str(chargeInfo.getConsume('coin', 0)) + '钻石')
                    else:
                        assetKind = hallitem.itemSystem.findAssetKind(assetKindId)
                        if assetKind:
                            consumes.append(assetKind.buildContent(count))
                consume = '，'.join(consumes)
            contentBase = succConf.get('content', u'您于${datetime}成功购买\n ${productName}\n本次消费：${consume}')
            contentList = []
            if sdkItem:
                contentList.append(u'%s：%s%s' % (sdkItem['name'], sdkItem['count'], sdkItem['units']))
            
            if orderDeliveryResult.assetItems:
                for assetKind, count, _final in orderDeliveryResult.assetItems:
                    contentList.append(assetKind.buildContentForDelivery(count))
            timestr = None
            try:
                timestr = nt.strftime(succConf.get('timefmt', '%Y-%m-%d %H:%M:%S'))
            except:
                ftlog.error()
                timestr = nt.strftime('%Y-%m-%d %H:%M:%S')
            return strutil.replaceParams(contentBase, {
                'datetime':timestr,
                'content':'\n'.join(contentList),
                'productName': orderDeliveryResult.order.product.displayName,
                'consume':consume,
            })
        except:
            ftlog.error()
            return ''
        
    @classmethod
    def makeProductDeliveryResponse(cls, userId, orderDeliveryResult, prodId=None):
        mo = MsgPack()
        mo.setCmd('prod_delivery')
        mo.setResult('userId', userId)
        mo.setResult('gameId', orderDeliveryResult.order.gameId)
        if orderDeliveryResult.order.realGameId:
            mo.setResult('realGameId', orderDeliveryResult.order.realGameId)
        mo.setResult('prodId', prodId or orderDeliveryResult.order.productId)
        mo.setResult('orderId', orderDeliveryResult.order.orderId)
        mo.setResult('prodName', orderDeliveryResult.order.product.displayName)
        mo.setResult('pic', orderDeliveryResult.order.product.pic)
        mo.setResult('raffle', 0)
        clientVer = sessiondata.getClientIdVer(userId)
        if clientVer >= 3.37:
            conf = hallstore.storeSystem.deliveryConf
            succ = conf.get('succ', {})
            mo.setResult('info', succ.get('title'))
            mo.setResult('tips', succ.get('tips', u'如有问题请拨打客服电话'))
            mo.setResult('content', cls.buildProductDeliveryContent(datetime.now(), succ, orderDeliveryResult))
        return mo

@markCmdActionHandler    
class StoreTcpHandler(BaseMsgPackChecker):
    SUB_PRODUCT_MAP = {
        'TY9999D0012002': 'TY9999D0012002_SUB',
        'TY9999D0010004': 'TY9999D0010004_SUB',
        'TY9999D0012004': 'TY9999D0012004_SUB',
        'TY9999D0015001': 'TY9999D0015001_SUB',
        'TY9999D0015002': 'TY9999D0015002_SUB'
    }
    
    def __init__(self):
        self.orderSeq = 0
    
    def _check_param_chargeType(self, msg, key, params):
        chargeType = msg.getParam(key)
        if chargeType and not isstring(chargeType):
            return 'ERROR of chargeType !' + str(chargeType), None
        return None, chargeType or ''
    
    def _check_param_consumeMap(self, msg, key, params):
        consumeMap = msg.getParam(key)
        if consumeMap and not isinstance(consumeMap, dict):
            return 'ERROR of consumeMap !' + str(consumeMap), None
        if consumeMap:
            for k, v in consumeMap.iteritems():
                if not isstring(k):
                    return 'consumeMap.key must be string !' + str(consumeMap), None
                if not isinstance(v, (int, float)):
                    return 'consumeMap.value must be int or float !' + str(consumeMap), None
        return None, consumeMap or {}
    
    def _check_param_chargeMap(self, msg, key, params):
        chargeMap = msg.getParam(key)
        if chargeMap and not isinstance(chargeMap, dict):
            return 'ERROR of chargeMap !' + str(chargeMap), None
        if chargeMap:
            for k, v in chargeMap.iteritems():
                if not isstring(k):
                    return 'chargeMap.key must be string !' + str(chargeMap), None
                if not isinstance(v, (int, float)):
                    return 'chargeMap.value must be int or float !' + str(chargeMap), None
        return None, chargeMap or {}

    def _check_param_orderId(self, msg, key, params):
        orderId = msg.getParam(key)
        if (isstring(orderId)
            and (orderid.is_valid_orderid_str(orderId)
                 or orderId in ('ios_compensate', 'momo_compensate'))):
            return None, orderId
        return 'ERROR of orderId !' + str(orderId), None

    def _check_param_productId(self, msg, key, params):
        productId = msg.getParam(key)
        if isstring(productId) and productId:
            return None, productId
        return 'ERROR of productId !' + str(productId), None
    
    def _check_param_prodId(self, msg, key, params):
        productId = msg.getParam(key)
        if isstring(productId) and productId:
            return None, productId
        return 'ERROR of prodId !' + str(productId), None

    def _check_param_diamonds(self, msg, key, params):
        diamonds = msg.getParam(key)
        try:
            diamonds = int(diamonds)
            return None, diamonds
        except:
            return 'ERROR of diamonds !' + str(diamonds), None


    def _check_param_rmbs(self, msg, key, params):
        rmbs = msg.getParam(key)
        try:
            rmbs = float(rmbs)
            return None, rmbs
        except:
            return 'ERROR of rmbs !' + str(rmbs), None
        
    def _check_param_realGameId(self, msg, key, params):
        value = msg.getParam(key, 0)
        try:
            value = int(value)
        except:
            value = 0
        return None, value
    
    @markCmdActionMethod(cmd='store_config', action="update", clientIdVer=0)
    def doStoreConfigUpdate(self, gameId, userId):
        clientId = sessiondata.getClientId(userId)
        router.sendToUser(StoreHelper.makeStoreConfigResponse(gameId, userId, clientId), userId)
       
    @markCmdActionMethod(cmd='store_config', action="update", clientIdVer=3.5)
    def doStoreConfigUpdateV3_5(self, gameId, userId):
        clientId = sessiondata.getClientId(userId)
        router.sendToUser(StoreHelper.makeStoreConfigResponseV3_5(gameId, userId, clientId), userId)
         
    @markCmdActionMethod(cmd='buy_prod', clientIdVer=0)
    def doBuyProductOld(self, gameId, userId, prodId):
        mo = MsgPack()
        mo.setCmd('buy_prod')
        mo.setResult('gameId', gameId)
        mo.setResult('userId', userId)
        mo.setResult('prodId', prodId)
        
        try:
            clientId = sessiondata.getClientId(userId)
            orderId = self._makeOrderId(gameId, userId, prodId)
            hallstore.storeSystem.buyProduct(gameId, gameId, userId, clientId, orderId, prodId, 1)
            mo.setResult('orderId', orderId)
            router.sendToUser(mo, userId)
        except TYBizException, e:
            mo.setError(e.errorCode, e.message)
        except:
            ftlog.error()
            mo.setError(1, 'create order error')
        return mo
            
    @markCmdActionMethod(cmd='store', action="buy", clientIdVer=0)
    def doBuyProduct(self, gameId, userId, prodId):
        try:
            clientId = sessiondata.getClientId(userId)
            orderId = self._makeOrderId(gameId, userId, prodId)
            orderDeliveryResult = hallstore.exchangeProduct(gameId, userId, clientId, orderId, prodId, 1)
            mo = StoreHelper.makeProductDeliveryResponse(userId, orderDeliveryResult)
            router.sendToUser(mo, userId)
        except TYBizException, e:
            TodoTaskHelper.sendTodoTask(gameId, userId, TodoTaskShowInfo(e.message))
            
    @classmethod
    def deliveryProduct(cls, gameId, realGameId, userId, orderId, prodId,
                        chargeType, chargeMap, consumeMap, isSub=False, orderPlatformId=''):
        orderId = cls.checkCompensateOrderId(gameId, realGameId, userId, orderId, prodId)
        try:
            switchProductId = None
            if isSub:
                switchProductId = cls.SUB_PRODUCT_MAP.get(prodId)
            orderDeliveryResult = hallstore.storeSystem.deliveryOrder(userId, orderId, prodId,
                                                                      TYChargeInfo(chargeType, chargeMap,
                                                                                   consumeMap), switchProductId, realGameId=realGameId, platformOrderId=orderPlatformId)
            try:
                # 发送全系统内的充值事件
                from tuyoo5.core import tygame
                from tuyoo5.core import typlugin
                clientId = sessiondata.getClientId(userId)
                evt = tygame.GlobalChargeEvent(userId, gameId, realGameId, 
                                               chargeMap['rmb'], chargeMap['diamond'], 
                                               prodId, clientId, orderId, orderPlatformId)
                typlugin.asyncTrigerGlobalEvent(evt)
            except Exception, e:
                ftlog.info('freetime5 not patched GlobalChargeEvent !', str(e))

            mo = StoreHelper.makeProductDeliveryResponse(userId, orderDeliveryResult, prodId)
            router.sendToUser(mo, userId)
        except TYBizException, e:
            ftlog.warn('StoreTcpHandler.deliveryProduct gameId=', gameId,
                        'userId=', userId,
                        'orderId=', orderId,
                        'productId=', prodId,
                        'ec=', e.errorCode,
                        'info=', e.message)
            if isinstance(e, TYBuyProductUnknownException):
                mo = StoreHelper.makeProductDeliveryFailResponse()
            else:
                mo = StoreHelper.makeProductDeliveryErrorResponse(e.errorCode, e.message)
            router.sendToUser(mo, userId)
        return mo
    
    @markCmdActionMethod(cmd='prod_delivery', clientIdVer=0)
    def doDeliveryProduct(self, gameId, realGameId, userId, orderId, prodId,
                          chargeType, chargeMap, consumeMap):
        msg = runcmd.getMsgPack()
        isSub = msg.getParam('isSub', 0)
        orderPlatformId = msg.getParam('orderPlatformId', '')
        return self.deliveryProduct(gameId, realGameId, userId, orderId, prodId, chargeType, chargeMap, consumeMap, isSub, orderPlatformId)

    @markCmdActionMethod(cmd='quickbuy', action="get_info", clientIdVer=0)
    def doQuickBuyGetInfo(self, gameId, userId):
        clientId = sessiondata.getClientId(userId)
        toStoreTodotask = TodoTaskGotoShop('coin')
        if hallstore.storeSystem.isCloseLastBuy(clientId):
            TodoTaskHelper.sendTodoTask(gameId, userId, toStoreTodotask)
            return
        
        lastBuyProduct, _lastBuyClientId = hallstore.storeSystem.getLastBuyProduct(gameId, userId)
        if (not lastBuyProduct
            or not lastBuyProduct.recordLastBuy
            or not hallstore.storeSystem.canBuyProduct(gameId, userId, clientId, lastBuyProduct, 1)):
            if hallstore.storeSystem.lastBuyConf.payOrder:
                product, _ = hallstore.findProductByPayOrder(gameId, userId, clientId, hallstore.storeSystem.lastBuyConf.payOrder)
                if product:
                    payOrderTodoTask = TodoTaskPayOrder(product)
                    desc = strutil.replaceParams(hallstore.storeSystem.lastBuyConf.desc2, {'product.displayName':product.displayName,
                                                                                           'product.price':product.price})
                    popInfoTodoTask = TodoTaskShowInfo(desc, True)
                    popInfoTodoTask.setSubCmd(payOrderTodoTask)
                    TodoTaskHelper.sendTodoTask(gameId, userId, popInfoTodoTask)
                    return
            TodoTaskHelper.sendTodoTask(gameId, userId, toStoreTodotask)
            return

        payOrderTodoTask = TodoTaskPayOrder(lastBuyProduct)
        desc = strutil.replaceParams(hallstore.storeSystem.lastBuyConf.desc, {'product.displayName':lastBuyProduct.displayName,
                                                                              'product.price':lastBuyProduct.price})
        popInfoTodoTask = TodoTaskShowInfo(desc, True)
        popInfoTodoTask.setSubCmd(payOrderTodoTask)
        popInfoTodoTask.setSubText(hallstore.storeSystem.lastBuyConf.subText)
        
        popInfoTodoTask.setSubCmdExt(toStoreTodotask)
        popInfoTodoTask.setSubTextExt(hallstore.storeSystem.lastBuyConf.subTextExt)
        TodoTaskHelper.sendTodoTask(gameId, userId, popInfoTodoTask)
        
    @classmethod
    def _makeOrderId(cls, gameId, userId, productId):
        return paydata.makeGameOrderId(gameId, userId, productId)
    
    @markCmdActionMethod(cmd='get_first_recharge', action="recieve", clientIdVer=0)
    def doGetFirstRechargeReward(self, gameId, userId, clientId):
        if not hallstore.isFirstRecharged(userId):
            mo = MsgPack()
            mo.setCmd('get_first_recharge')
            mo.setError(-1, '你还没有首充！')
            router.sendToUser(mo, userId)
            return
        
        if not hallstore.setFirstRechargeReward(userId):
            mo = MsgPack()
            mo.setCmd('get_first_recharge')
            mo.setError(-1, '您已经领取了！')
            router.sendToUser(mo, userId)
            return

        timestamp = pktimestamp.getCurrentTimestamp()
        userAssets = hallitem.itemSystem.loadUserAssets(userId)
        itemKindId = hall_first_recharge.queryFirstRecharge(gameId, userId, clientId)
        assetKindId = hallitem.itemIdToAssetId(itemKindId)
        balance = userAssets.balance(gameId, assetKindId, timestamp)
        if balance <= 0:
            userAssets.addAsset(gameId, assetKindId, 1, timestamp, 'FIRST_RECHARGE', 0)
            
            ftlog.info('SotreTcpHandler.doGetFirstRechargeReward gameId=', gameId,
                       'userId=', userId,
                       'itemId=', itemKindId)

            userBag = userAssets.getUserBag()
            item = userBag.getItemByKindId(itemKindId)
            if item:
                try:
                    userBag.doAction(gameId, item, 'open', timestamp)
                except:
                    ftlog.error('SotreTcpHandler.doGetFirstRechargeReward gameId=', gameId,
                                'userId=', userId,
                                'itemId=', itemKindId)
            pkmessage.send(gameId, pkmessage.MESSAGE_TYPE_PRIVATE, userId, '恭喜您获得首充豪华大礼包奖励！')
        datachangenotify.sendDataChangeNotify(gameId, userId, ['item', 'promotion_loc'])
    
    @markCmdActionMethod(cmd='charge_notify', action="", clientIdVer=0)
    def doChargeNotify(self, gameId, userId, prodId, rmbs, diamonds, clientId):
        if diamonds > 0:
            hallvip.userVipSystem.addUserVipExp(gameId, userId, diamonds, 'BUY_PRODUCT', pokerconf.productIdToNumber(prodId))
        TGHall.getEventBus().publishEvent(ChargeNotifyEvent(userId, gameId, rmbs, diamonds, prodId, clientId))
        
        try:
            # 发送全系统内的充值事件
            from tuyoo5.core import tygame
            from tuyoo5.core import typlugin
            clientId = sessiondata.getClientId(userId)
            evt = tygame.GlobalChargeEvent(userId, gameId, gameId, 
                                           rmbs, diamonds, 
                                           prodId, clientId, '', '')
            typlugin.asyncTrigerGlobalEvent(evt)
        except Exception, e:
            ftlog.info('freetime5 not patched GlobalChargeEvent !', str(e))
        
        mo = MsgPack()
        mo.setCmd('charge_notify')
        mo.setResult('userId', userId)
        mo.setResult('gameId', gameId)
        return mo

    @classmethod
    def checkCompensateOrderId(cls, gameId, realGameId, userId, orderId, productId):
        '''
        自动补单处理
        '''
        if orderId in ('ios_compensate', 'momo_compensate'):
            ftlog.info('checkCompensateOrderId compensate fix->', gameId, realGameId, userId, orderId, productId)
            try:
                clientId = sessiondata.getClientId(userId)
                orderId = cls._makeOrderId(gameId, userId, productId)
                order = hallstore.storeSystem.buyProduct(gameId, realGameId, userId, clientId, orderId, productId, 1)
                orderId = order.orderId
                ftlog.info('checkCompensateOrderId compensate fix->orderId=', orderId)
            except:
                ftlog.error('ERROR checkCompensateOrderId compensate fix !!', gameId, realGameId, userId, orderId, productId)
        return orderId


