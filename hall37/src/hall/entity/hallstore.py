# -*- coding=utf-8
'''
Created on 2015年7月1日

@author: zhaojiangang
'''

import freetime.util.log as ftlog
from hall.entity import hallitem, hallconf, hallvip, datachangenotify, \
    hallstocklimit, hallshare
from hall.entity.hallconf import HALL_GAMEID
from hall.game import TGHall
from poker.entity.biz.item.item import TYAssetUtils
from poker.entity.biz.store.dao import TYOrderDao, TYClientStoreConf
from poker.entity.biz.store.exceptions import TYStoreConfException, \
    TYBuyProductUnknownException, TYProductNotSupportExchangeException, \
    TYProductExchangeNotEnoughException
from poker.entity.biz.store.store import TYStoreSystem, TYStoreSystemImpl, \
    TYBuyCondition, TYBuyConditionRegister, TYOrderDeliveryEvent, TYChargeInfo
from poker.entity.configure import pokerconf
from poker.entity.dao import paydata, daobase
from poker.entity.dao.daoconst import GameOrderSchema
import poker.entity.dao.gamedata as pkgamedata
import poker.entity.dao.userdata as pkuserdata
from poker.entity.events.tyevent import EventConfigure, ChargeNotifyEvent, \
    UserEvent
import poker.entity.events.tyeventbus as pkeventbus
from poker.util import strutil
import poker.util.timestamp as pktimestamp
from hall.entity.todotask import TodoTaskHelper


class TYOrderDaoImpl(TYOrderDao):
    UPDATE_STATE_LUA_SCRIPT = '''
    local key = tostring(KEYS[1])
    local state = tonumber(KEYS[2])
    local expectState = tonumber(KEYS[3])
    local oldState = tonumber(redis.call('hget', key, 'state'))
    if oldState ~= expectState then
        return {1, oldState}
    end
    redis.call('hset', key, 'state', state)
    return {0, oldState}
    '''
    UPDATE_LUA_ALIAS = 'TYOrderDaoImpl.update_state_lua_script'

    def __init__(self):
        daobase.loadLuaScripts(self.UPDATE_LUA_ALIAS, self.UPDATE_STATE_LUA_SCRIPT)

    def addOrder(self, order):
        '''
        增加order
        '''
        datas = {GameOrderSchema.ORDERID: order.orderId,
                 GameOrderSchema.PLATFORMORDERID: order.platformOrderId,
                 GameOrderSchema.USERID: order.userId,
                 GameOrderSchema.GAMEID: order.gameId,
                 GameOrderSchema.REALGAMEID: order.realGameId,
                 GameOrderSchema.PRODID: order.productId,
                 GameOrderSchema.COUNT: order.count,
                 GameOrderSchema.CREATETIME: order.createTime,
                 GameOrderSchema.UPDATETIME: order.updateTime,
                 GameOrderSchema.CLIENTID: order.clientId,
                 GameOrderSchema.STATE: order.state,
                 GameOrderSchema.ERRORCODE: order.errorCode,
                 GameOrderSchema.CHARGEINFO: self.__encodeChargeInfo(order.chargeInfo)
                 }
        paydata.setGameOrderInfo(order.userId, order.orderId, datas)
        ftlog.debug('TYOrderDaoImpl.addOrder orderId=', order.orderId,
                    'datas=', datas)

    def loadOrder(self, orderId):
        '''
        加载order
        '''
        datas = paydata.getGameOrderInfo(orderId)
        chargeInfo = self._decodeChargeInfo(datas[GameOrderSchema.CHARGEINFO])

        from poker.entity.biz.store.store import TYOrder
        return TYOrder(datas[GameOrderSchema.ORDERID], datas[GameOrderSchema.PLATFORMORDERID],
                       datas[GameOrderSchema.USERID], datas[GameOrderSchema.GAMEID], datas[GameOrderSchema.REALGAMEID],
                       datas[GameOrderSchema.PRODID], datas[GameOrderSchema.COUNT],
                       datas[GameOrderSchema.CLIENTID], datas[GameOrderSchema.CREATETIME],
                       datas[GameOrderSchema.UPDATETIME], datas[GameOrderSchema.STATE],
                       datas[GameOrderSchema.ERRORCODE], chargeInfo)

    def updateOrder(self, order, expectState):
        '''
        更新order
        '''
        key = 'gameOrder:%s' % (order.orderId)
        error, oldState = daobase._executePayDataLua(self.UPDATE_LUA_ALIAS, 3,
                                                     key,
                                                     order.state,
                                                     expectState)
        if error != 0:
            return error, oldState

        datas = {
            GameOrderSchema.UPDATETIME: order.updateTime,
            GameOrderSchema.ERRORCODE: order.errorCode,
            GameOrderSchema.PRODID: order.productId,
            GameOrderSchema.REALGAMEID: order.realGameId,
            GameOrderSchema.CHARGEINFO: self.__encodeChargeInfo(order.chargeInfo)
        }
        paydata.setGameOrderInfo(order.userId, order.orderId, datas)
        ftlog.debug('TYOrderDaoImpl.updateOrder orderId=', order.orderId,
                    'datas=', datas)
        return error, oldState

    def __toInt(self, value):
        return int(value) if value is not None else value

    def __encodeChargeInfo(self, chargeInfo):
        if not chargeInfo:
            return {}
        d = {
            'chargeType': chargeInfo.chargeType,
            'charges': chargeInfo.chargeMap,
            'consumes': chargeInfo.consumeMap
        }
        return d

    def _decodeChargeInfo(self, chargeInfoDict):
        chargeType = chargeInfoDict.get('chargeType', '')
        charges = chargeInfoDict.get('charges', {})
        consumes = chargeInfoDict.get('consumes', {})
        return TYChargeInfo(chargeType, charges, consumes)


class TYBuyConditionCharm(TYBuyCondition):
    TYPE_ID = 'charmValue'

    def __init__(self):
        super(TYBuyConditionCharm, self).__init__()
        self.startCharm = None
        self.endCharm = None

    def check(self, userId, product):
        userCharm = pkuserdata.getCharm(userId)
        ret = ((self.startCharm is None or userCharm >= self.startCharm)
               and (self.endCharm is None or userCharm <= self.endCharm))
        if ftlog.is_debug():
            ftlog.debug('TYBuyConditionCharm.check userId=', userId,
                        'productId=', product.productId,
                        'userCharm=', userCharm,
                        'startCharm=', self.startCharm,
                        'endCharm=', self.endCharm,
                        'ret=', ret)
        return ret

    def _decodeFromDictImpl(self, d):
        startCharm = d.get('startCharm', None)
        endCharm = d.get('endCharm', None)
        if startCharm is not None and not isinstance(startCharm, int):
            raise TYStoreConfException(d, 'TYBuyConditionCharm.startCharm must be None or int')
        if endCharm is not None and not isinstance(endCharm, int):
            raise TYStoreConfException(d, 'TYBuyConditionCharm.endCharm must be None or int')
        if endCharm is not None and startCharm is not None and endCharm < startCharm:
            raise TYStoreConfException(d, 'TYBuyConditionCharm.endCharm must et startCharm')
        self.startCharm = startCharm
        self.endCharm = endCharm
        return self


class TYBuyConditionVipLevel(TYBuyCondition):
    '''
    购买条件
    @param userId: 哪个用户购买
    @param product: 购买哪个商品
    @return: 如果符合购买条件则返回True，否则返回False
    '''
    TYPE_ID = 'vipLevel'

    def __init__(self):
        super(TYBuyConditionVipLevel, self).__init__()
        self.startLevel = None
        self.endLevel = None

    def check(self, userId, product):
        userVip = hallvip.userVipSystem.getUserVip(userId)
        ftlog.debug('TYBuyConditionVipLevel.check userId=', userId,
                    'productId=', product.productId,
                    'startLevel=', self.startLevel,
                    'endLevel=', self.endLevel,
                    'userVipLevel=', userVip.vipLevel.level)
        if self.startLevel > 0 and userVip.vipLevel.level < self.startLevel:
            ftlog.debug('TYBuyConditionVIP.check userId=', userId,
                        'productId=', product.productId,
                        'startLevel=', self.startLevel,
                        'userVipLevel=', userVip.vipLevel.level)
            return False
        if self.endLevel > 0 and userVip.vipLevel.level > self.endLevel:
            ftlog.debug('TYBuyConditionVIP.check userId=', userId,
                        'productId=', product.productId,
                        'endLevel=', self.endLevel,
                        'userVipLevel=', userVip.vipLevel.level)
            return False
        return True

    def _decodeFromDictImpl(self, d):
        startLevel = d.get('startLevel', -1)
        endLevel = d.get('endLevel', -1)
        if not isinstance(startLevel, int):
            raise TYStoreConfException(d, 'TYBuyConditionVipLevel.startLevel must be int')
        if not isinstance(endLevel, int):
            raise TYStoreConfException(d, 'TYBuyConditionVipLevel.endLevel must be int')
        if endLevel != -1 and endLevel < startLevel:
            raise TYStoreConfException(d, 'TYBuyConditionVipLevel.endLevel must greater startLevel')
        self.startLevel = startLevel
        self.endLevel = endLevel
        return self


class TYBuyConditionWithCondition(TYBuyCondition):
    TYPE_ID = 'withCondition'
    
    def __init__(self):
        super(TYBuyConditionWithCondition, self).__init__()
        self.condition = None
        
    def check(self, userId, product):
        from poker.entity.dao import sessiondata
        clientId = sessiondata.getClientId(userId)
        return self.condition.check(HALL_GAMEID, userId, clientId, pktimestamp.getCurrentTimestamp())
    
    def _decodeFromDictImpl(self, d):
        from hall.entity.hallusercond import UserConditionRegister
        cond = d.get('condition')
        self.condition = UserConditionRegister.decodeFromDict(cond)
        return self


class TYClientStoreConfImpl(TYClientStoreConf):
    def findTemplateNameByClientId(self, clientId):
        '''
        根据clientId查找商城模版名称
        '''
        tname = hallconf.getClientStoreConf(clientId)
        return tname

    #         clientStoreConf = hallconf.getClientStoreConf(clientId) or {}
    #         clientOs, _ver, _ = strutil.parseClientId(clientId)
    #         clientOs = clientOs.lower()
    #         if clientOs == 'ios':
    #             return clientStoreConf.get('template', 'goods_conf_ios')
    #         else:
    #             return clientStoreConf.get('template', 'goods_conf_android')

    def isClosedLastBuy(self, clientId):
        '''
        判断clientId是否关闭了最后购买记录
        '''
        #         clientStoreConf = hallconf.getClientStoreConf(clientId) or {}
        #         return clientStoreConf.get('closeLastBuy', 0)
        conf = None
        templates = hallconf.getStoreCloseLastTemplates()
        if templates:
            tname = hallconf.getClientStoreCloseLastConf(clientId)
            conf = templates.get(tname)
        return conf.get('closeLastBuy', 0) if conf else 0


storeSystem = TYStoreSystem()
_inited = False


def _registerClasses():
    TYBuyConditionRegister.registerClass(TYBuyConditionVipLevel.TYPE_ID, TYBuyConditionVipLevel)
    TYBuyConditionRegister.registerClass(TYBuyConditionCharm.TYPE_ID, TYBuyConditionCharm)
    TYBuyConditionRegister.registerClass(TYBuyConditionWithCondition.TYPE_ID, TYBuyConditionWithCondition)

def _reloadConf():
    global storeSystem
    productsConf = hallconf.getProductsConf()
    storeConf = hallconf.getStoreTemplates()
    storeSystem.reloadConf(productsConf, storeConf)


def _onConfChanged(event):
    if _inited and event.isModuleChanged(['store', 'products']):
        ftlog.debug('hallstore._onConfChanged')
        _reloadConf()


class UserFirstRecharedEvent(UserEvent):
    def __init__(self, gameId, userId):
        super(UserFirstRecharedEvent, self).__init__(userId, gameId)


def _onChargeNotify(event):
    ftlog.info('hallstore._onChargeNotify gameId=', event.gameId,
               'userId=', event.userId,
               'diamonds=', event.diamonds,
               'rmbs=', event.rmbs,
               'firstRechargeThreshold=', storeSystem.firstRechargeThreshold)
    changeNames = set()
    if event.diamonds > 0:
        changeNames.add('promotion_loc')
    if event.diamonds >= storeSystem.firstRechargeThreshold:
        count = pkgamedata.incrGameAttr(event.userId, HALL_GAMEID, 'first_recharge', 1)
        if count == 1:
            TGHall.getEventBus().publishEvent(UserFirstRecharedEvent(HALL_GAMEID, event.userId))
            changeNames.add('promotion_loc')
    datachangenotify.sendDataChangeNotify(HALL_GAMEID, event.userId, changeNames)


def _onOrderDelivery(event):
    if event.orderDeliveryResult.assetItems:
        changedNames = TYAssetUtils.getChangeDataNames(event.orderDeliveryResult.assetItems)
        datachangenotify.sendDataChangeNotify(event.gameId, event.userId, changedNames)
        ftlog.info('hallstore._onOrderDelivery gameId=', event.gameId,
                   'userId=', event.userId,
                   'orderDeliveryResult=', event.orderDeliveryResult)


CHECK_DIAMOND_CHIP_RATE = 2000


def _checkDelivery(self, orderDeliveryResult):
    try:
        order = orderDeliveryResult.order
        if order.orderId.startswith('GO'):
            return
        consumeDiamond = int(order.chargeInfo.getConsume('coin', 0))
        totalPriceDiamond = int(order.product.priceDiamond) * order.count
        if consumeDiamond < totalPriceDiamond:
            ftlog.warn('WARNING checkDelivery err=', 'NotEnoughDiamond',
                       'orderId=', order.orderId,
                       'userId=', order.userId,
                       'gameId=', order.gameId,
                       'productId=', order.productId,
                       'count=', order.count,
                       'price=', order.product.price,
                       'priceDiamond=', order.product.priceDiamond,
                       'totalPriceDiamond=', totalPriceDiamond,
                       'consumeDiamond=', consumeDiamond)
            return
        elif consumeDiamond > totalPriceDiamond:
            ftlog.warn('WARNING checkDelivery err=', 'OverLoadDiamond',
                       'orderId=', order.orderId,
                       'userId=', order.userId,
                       'gameId=', order.gameId,
                       'productId=', order.productId,
                       'count=', order.count,
                       'price=', order.product.price,
                       'priceDiamond=', order.product.priceDiamond,
                       'totalPriceDiamond=', totalPriceDiamond,
                       'consumeDiamond=', consumeDiamond)
            return

        if orderDeliveryResult.itemList:
            # 统计获得了多少金币
            deliveryChip = TYAssetUtils.getAssetCount(orderDeliveryResult.assetItems, hallitem.ASSET_CHIP_KIND_ID)
            maxChip = consumeDiamond * CHECK_DIAMOND_CHIP_RATE
            if deliveryChip > maxChip:
                ftlog.warn('WARNING checkDelivery err=', 'OverMaxChip',
                           'orderId=', order.orderId,
                           'userId=', order.userId,
                           'gameId=', order.gameId,
                           'productId=', order.productId,
                           'count=', order.count,
                           'price=', order.product.price,
                           'priceDiamond=', order.product.priceDiamond,
                           'totalPriceDiamond=', totalPriceDiamond,
                           'consumeDiamond=', consumeDiamond,
                           'deliveryChip=', deliveryChip,
                           'maxChip=', maxChip,
                           'checkRate=', CHECK_DIAMOND_CHIP_RATE)
    except:
        ftlog.exception()


def _initialize():
    ftlog.debug('store initialize begin')
    from hall.entity.hallusercond import UserConditionRegister
    global storeSystem
    global _inited
    if not _inited:
        _inited = True
        storeSystem = TYStoreSystemImpl(hallitem.itemSystem, TYOrderDaoImpl(),
                                        TYClientStoreConfImpl(), TGHall.getEventBus(),
                                        UserConditionRegister)
        _registerClasses()
        _reloadConf()
        pkeventbus.globalEventBus.subscribe(EventConfigure, _onConfChanged)
        TGHall.getEventBus().subscribe(ChargeNotifyEvent, _onChargeNotify)
        TGHall.getEventBus().subscribe(TYOrderDeliveryEvent, _onOrderDelivery)
    ftlog.debug('store initialize end')


def isFirstRecharged(userId):
    return pkgamedata.getGameAttrInt(userId, HALL_GAMEID, 'first_recharge') > 0


def isGetFirstRechargeReward(userId):
    return pkgamedata.getGameAttrInt(userId, HALL_GAMEID, 'first_recharge_reward') > 0


def setFirstRechargeReward(userId):
    return pkgamedata.setnxGameAttr(userId, HALL_GAMEID, 'first_recharge_reward', 1) == 1


def exchangeProduct(gameId, userId, clientId, orderId, productId, count):
    product = storeSystem.findProduct(productId)
    if not product:
        raise TYBuyProductUnknownException(productId)

    if product.buyType != 'exchange':
        raise TYProductNotSupportExchangeException(productId)

    timestamp = pktimestamp.getCurrentTimestamp()

    # 限购系统锁定
    periodId = hallstocklimit.productBuyLimitSystem.lockProduct(gameId, userId, productId, count, timestamp)

    # 创建订单
    try:
        storeSystem.buyProduct(gameId, gameId, userId, clientId, orderId, productId, count)
    except:
        if periodId:
            hallstocklimit.productBuyLimitSystem.unlockProduct(gameId, userId, periodId, productId,
                                                               count, 1, timestamp)
        raise

    # 
    ftlog.info('hallstore.exchangeProduct gameId=', gameId,
               'userId=', userId,
               'clientId=', clientId,
               'orderId=', orderId,
               'productId=', productId,
               'count=', count)

    try:
        # 消耗兑换的东西
        userAssets = hallitem.itemSystem.loadUserAssets(userId)
        assetTuple = userAssets.consumeAsset(gameId, product.exchangeFeeContentItem.assetKindId,
                                             product.exchangeFeeContentItem.count * count,
                                             timestamp,
                                             'BUY_PRODUCT', pokerconf.productIdToNumber(productId))
        if assetTuple[1] < product.exchangeFeeContentItem.count * count:
            ftlog.warn('hallstore.exchangeProduct gameId=', gameId,
                       'userId=', userId,
                       'clientId=', clientId,
                       'orderId=', orderId,
                       'productId=', productId,
                       'count=', count,
                       'consumedCount=', assetTuple[1],
                       'needConsumeCount=', product.exchangeFeeContentItem.count * count,
                       'err=', 'ConsumeNotEnough')
            msg = strutil.replaceParams(product.exchangeFeeNotEnoughText, {'feeName': assetTuple[0].displayName})
            raise TYProductExchangeNotEnoughException(productId, msg)

        datachangenotify.sendDataChangeNotify(gameId, userId, TYAssetUtils.getChangeDataNames([assetTuple]))
        consumeMap = {assetTuple[0].kindId: assetTuple[1]}
        ret = storeSystem.deliveryOrder(userId, orderId, productId, TYChargeInfo('', {}, consumeMap))

        # 分享提示
        shareId = hallshare.getShareId('exchangeShare', userId, gameId)
        if ftlog.is_debug():
            ftlog.debug('handleExchangeAuditResult shareId: ', shareId)

        share = hallshare.findShare(shareId)
        if share:
            desc = share.getDesc(gameId, userId, True)
            newDesc = strutil.replaceParams(desc, {'exchangeDesc': product.displayName})
            share.setDesc(newDesc)
            task = share.buildTodotask(HALL_GAMEID, userId, 'exchange')
            TodoTaskHelper.sendTodoTask(HALL_GAMEID, userId, task)

        if periodId:
            hallstocklimit.productBuyLimitSystem.deliveryProduct(gameId, userId, periodId, productId, count, timestamp)
        return ret
    except:
        if periodId:
            hallstocklimit.productBuyLimitSystem.unlockProduct(gameId, userId, periodId, productId, count, 2, timestamp)
        raise


def findProduct(gameId, userId, productId):
    product = storeSystem.findProduct(productId)
    return product


def findProductFromShelves(gameId, userId, clientId, shelvesName):
    shelves = storeSystem.getShelvesByClientId(gameId, userId, clientId, shelvesName)
    if shelves and shelves.productList:
        return shelves.productList[0]
    return None


def findShelvesListByNames(gameId, userId, clientId, shelvesNames):
    if not shelvesNames:
        return storeSystem.getShelvesListByClientId(gameId, userId, clientId)
    ret = []
    for shelvesName in shelvesNames:
        shelves = storeSystem.getShelvesByClientId(gameId, userId, clientId, shelvesName)
        if shelves:
            ret.append(shelves)
    return ret


def calcScore(v, count):
    flag = cmp(v, count)
    if flag == 0:
        return 0
    elif flag < 0:
        return 2
    return 1


def cmpEQ_GT_LT(v1, v2, count):
    '''
    排序，等于count的 < 大于count的 < 小于count的
    小于count的要倒排序
    '''
    score1 = calcScore(v1, count)
    score2 = calcScore(v2, count)
    ret = cmp(score1, score2)
    if ret == 0:
        if score1 == 2:
            return cmp(v2, v1)
        return cmp(v1, v2)
    return ret


def productCmpPriceDiamond(count):
    def cmpImpl(p1, p2):
        return cmpEQ_GT_LT(int(p1.priceDiamond), int(p2.priceDiamond), count)

    return cmpImpl


def productCmpContains(assetKindId, count):
    def cmpImpl(p1, p2):
        v1 = p1.getMinFixedAssetCount(assetKindId)
        v2 = p2.getMinFixedAssetCount(assetKindId)
        return cmpEQ_GT_LT(v1, v2, count)

    return cmpImpl


def doFilter(product, filters):
    if isinstance(filters, (list, set)):
        for f in filters:
            if not f(product):
                return False
        return True
    else:
        return filters(product)


def filterProductsByShelvesList(shelvesList, filters, comparator):
    # key=productId, value=(product, shelves)
    ret = []
    productSet = set()
    for shelves in shelvesList:
        for product in shelves.productList:
            if product not in productSet and doFilter(product, filters):
                ret.append((product, shelves))
                productSet.add(product)
    if ftlog.is_debug():
        ftlog.debug('hallstore.filterProductsByShelvesList before sort'
                    'shelves=', [shelves.name for shelves in shelvesList],
                    'ret=', [(p.productId, s.name) for p, s in ret])
    if comparator:
        ret.sort(cmp=lambda x, y: comparator(x[0], y[0]))
    return ret


def findProductByProductId(shelvesList, productId):
    for shelves in shelvesList:
        product = shelves.findProduct(productId)
        if product:
            return product, shelves
    return None, None


def makePriceDiamondFilter(baseValue, minValue, maxValue):
    def doFilter(product):
        priceDiamond = int(product.priceDiamond)
        return (priceDiamond >= minValue
                and (maxValue < 0 or priceDiamond <= maxValue))

    return doFilter


def makeContainsFilter(assetKindId, baseValue, minValue, maxValue):
    def doFilter(product):
        containCount = product.getMinFixedAssetCount(assetKindId)
        return (containCount >= minValue
                and (maxValue < 0 or containCount <= maxValue))

    return doFilter


def makeBuyTypeFilter(buyTypes):
    def doFilter(product):
        return not buyTypes or product.buyType in buyTypes

    return doFilter


def findProductByContains(gameId, userId, clientId, shelvesNames, buyTypes,
                          assetKindId, count, minCount=None, maxCount=None):
    retList = findProductListByContains(gameId, userId, clientId, shelvesNames, buyTypes,
                                        assetKindId, count, minCount, maxCount)
    return retList[0] if retList else (None, None)


def findProductListByContains(gameId, userId, clientId, shelvesNames, buyTypes,
                              assetKindId, count, minCount=None, maxCount=None):
    minCount = count if minCount is None or minCount < 0 else minCount
    maxCount = -1 if maxCount is None or maxCount < -1 else maxCount
    shelvesList = findShelvesListByNames(gameId, userId, clientId, shelvesNames)
    comparator = productCmpContains(assetKindId, count)
    containsFilter = makeContainsFilter(assetKindId, count, minCount, maxCount)
    buyTypeFilter = makeBuyTypeFilter(buyTypes)
    filters = [containsFilter, buyTypeFilter]
    ret = filterProductsByShelvesList(shelvesList, filters, comparator)
    if ftlog.is_debug():
        ftlog.debug('hallstore.findProductListByContains gameId=', gameId,
                    'userId=', userId,
                    'clientId=', clientId,
                    'shelvesNames=', shelvesNames,
                    'buyTypes=', buyTypes,
                    'assetKindId=', assetKindId,
                    'count=', count,
                    'minCount=', minCount,
                    'maxCount=', maxCount,
                    'ret=', [(p.productId, s.name) for p, s in ret])
    return ret


def findProductByPriceDiamond(gameId, userId, clientId, shelvesNames, buyTypes,
                              count, minCount=None, maxCount=None):
    retList = findProductListByPriceDiamond(gameId, userId, clientId, shelvesNames, buyTypes,
                                            count, minCount, maxCount)
    return retList[0] if retList else (None, None)


def findProductListByPriceDiamond(gameId, userId, clientId, shelvesNames, buyTypes,
                                  count, minCount=None, maxCount=None):
    minCount = count if minCount is None or minCount < 0 else minCount
    maxCount = -1 if maxCount is None or maxCount < -1 else maxCount
    shelvesList = findShelvesListByNames(gameId, userId, clientId, shelvesNames)
    comparator = productCmpPriceDiamond(count)
    priceDiamondFilter = makePriceDiamondFilter(count, minCount, maxCount)
    buyTypeFilter = makeBuyTypeFilter(buyTypes)
    filters = [priceDiamondFilter, buyTypeFilter]
    ret = filterProductsByShelvesList(shelvesList, filters, comparator)
    if ftlog.is_debug():
        ftlog.debug('hallstore.findProductListByPriceDiamond gameId=', gameId,
                    'userId=', userId,
                    'clientId=', clientId,
                    'shelvesNames=', shelvesNames,
                    'buyTypes=', buyTypes,
                    'count=', count,
                    'minCount=', minCount,
                    'maxCount=', maxCount,
                    'ret=', [(p.productId, s.name) for p, s in ret])
    return ret


def findProductListByPayOrder(gameId, userId, clientId, payOrder):
    if ftlog.is_debug():
        ftlog.debug('hallstore.findProductListByPayOrder gameId=', gameId,
                    'userId=', userId,
                    'clientId=', clientId,
                    'payOrder=', payOrder)

    productId = payOrder.get('productId')
    if productId:
        product, shelves = storeSystem.findProductInShelves(gameId, userId, clientId, productId)
        if product:
            return [(product, shelves)]
        return []

    productIds = payOrder.get('productIds')
    if productIds:
        ret = []
        for productId in productIds:
            product, shelves = storeSystem.findProductInShelves(gameId, userId, clientId, productId)
            if product:
                ret.append((product, shelves))
        return ret

    contains = payOrder.get('contains')
    priceDiamond = payOrder.get('priceDiamond')
    if not contains and not priceDiamond:
        if ftlog.is_debug():
            ftlog.debug('hallstore.findProductListByPayOrder gameId=', gameId,
                        'userId=', userId,
                        'clientId=', clientId,
                        'payOrder=', payOrder,
                        'err=', 'EmptyPayOrder')
        return []
    shelvesNames = payOrder.get('shelves')
    buyTypes = payOrder.get('buyTypes')
    if contains:
        count = contains['count']
        minCount = contains.get('minCount', count)
        maxCount = contains.get('maxCount')
        return findProductListByContains(gameId, userId, clientId, shelvesNames, buyTypes,
                                         contains['itemId'], count, minCount, maxCount)
    else:
        count = priceDiamond['count']
        minCount = priceDiamond.get('minCount', count)
        maxCount = priceDiamond.get('maxCount')
        return findProductListByPriceDiamond(gameId, userId, clientId, shelvesNames, buyTypes,
                                             count, minCount, maxCount)


def findProductByPayOrder(gameId, userId, clientId, payOrder):
    product = shelves = None
    retList = findProductListByPayOrder(gameId, userId, clientId, payOrder)
    if retList:
        product, shelves = retList[0][0], retList[0][1]
    if ftlog.is_debug():
        ftlog.debug('hallstore.findProductByPayOrder gameId=', gameId,
                    'userId=', userId,
                    'clientId=', clientId,
                    'payOrder=', payOrder,
                    'product=', product.productId if product else None,
                    'shelves=', shelves.name if shelves else None)
    return product, shelves


if __name__ == '__main__':
    #     print cmpEQ_GT_LT(100, 101, 102)
    #
    #     testCases = [
    #         (100, 101, 102, 1),
    #         (100, 102, 102, 1),
    #         (100, 103, 102, 1),
    #         (102, 103, 102, -1),
    #         (103, 102, 102, 1),
    #         # 值相等肯定相等
    #         (103, 103, 102, 0),
    #         (101, 101, 102, 0),
    #
    #         (20, 80, 60, 1),
    #         (50000, 60000, 60000, 1)
    #     ]
    #     for i, testCase in enumerate(testCases):
    #         ret = cmpEQ_GT_LT(testCase[0], testCase[1], testCase[2])
    #         print 'testCase', i, testCase[0], testCase[1], testCase[2]
    #         assert(ret == testCase[3])

    #     print cmpEQ_GT_LT(80, 20, 60)
    class Pdt(object):
        def __init__(self, pdtName, priceDiamond, containsCount):
            self.name = pdtName
            self.priceDiamond = priceDiamond
            self.containsCount = containsCount

        def getMinFixedAssetCount(self, assetKindId):
            return self.containsCount


    ps = [Pdt('T50K', 50, 50000), Pdt('T60K', 60, 60000)]
    comparator = productCmpPriceDiamond(60)
    ps.sort(cmp=lambda x, y: comparator(x, y))
    print [p.name for p in ps]
