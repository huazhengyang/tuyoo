# -*- coding: utf-8 -*-
"""
Created on 2015年6月8日

@author: zhaojiangang
"""
from datetime import datetime
import json
from sre_compile import isstring
import time
import freetime.util.log as ftlog
from poker.entity.biz.confobj import TYConfable, TYConfableRegister
from poker.entity.biz.content import TYContentUtils, TYContentRegister, TYContentItem
from poker.entity.biz.item.item import TYAssetUtils
import poker.entity.biz.message.message as pkmessage
from poker.entity.biz.store.exceptions import TYStoreConfException, TYBuyProductUnknownException, TYBuyProductOverCountException, TYBuyConditionNotEnoughException, TYOrderNotFoundException, TYDeliveryOrderDiffUserException, TYDeliveryProductNotFoundException, TYBadOrderStateException, TYStoreException, TYDeliveryOrderDiffProductException
from poker.entity.configure import pokerconf
import poker.entity.dao.gamedata as pkgamedata
from poker.entity.events.tyevent import UserEvent
from poker.util import strutil
import poker.util.timestamp as pktimestamp

class TYProductBuyType(object, ):
    BUY_TYPE_CHARGE = 'charge'
    BUY_TYPE_CONSUME = 'consume'
    BUY_TYPE_DIRECT = 'direct'
    BUY_TYPE_EXCHANGE = 'exchange'
    ALL_BUY_TYPES = set([BUY_TYPE_CHARGE, BUY_TYPE_CONSUME, BUY_TYPE_DIRECT, BUY_TYPE_EXCHANGE])

    @classmethod
    def isValidBuyType(cls, buyType):
        pass

class TYBuyCondition(TYConfable, ):
    """
    购买条件
    @param userId: 哪个用户购买
    @param product: 购买哪个商品
    @return: 如果符合购买条件则返回True，否则返回False
    """

    def __init__(self):
        pass

    def check(self, userId, product):
        pass

    def decodeFromDict(self, d):
        pass

    def _decodeFromDictImpl(self, d):
        pass

class TYBuyConditionRegister(TYConfableRegister, ):
    _typeid_clz_map = {}

class TYProduct(TYConfable, ):

    def __init__(self):
        pass

    def clone(self):
        pass

    def getMinFixedAssetCount(self, assetKindId):
        pass

    def decodeFromDict(self, d):
        pass

class TYChargeInfo(object, ):

    def __init__(self, chargeType, chargeMap, consumeMap):
        pass

    def __repr__(self):
        pass

    def __str__(self):
        pass

    def __unicode__(self):
        pass

    def getCharge(self, name, defValue):
        pass

    def getConsume(self, name, defValue):
        pass

    def toDict(self):
        pass

class TYOrder(object, ):
    STATE_CREATE = 0
    STATE_DELIVERYING = 1
    STATE_DELIVERY = 2

    def __init__(self, orderId=None, platformOrderId=None, userId=None, gameId=None, realGameId=0, productId=None, count=None, clientId=None, createTime=None, updateTime=None, state=STATE_CREATE, errorCode=None, chargeInfo=None):
        pass

class TYOrderDeliveryResult(object, ):

    def __init__(self, order, assetItems):
        pass

class TYOrderDeliveryEvent(UserEvent, ):
    """
    发货事件，发货后由商品系统发出
    """

    def __init__(self, gameId, userId, orderDeliveryResult):
        pass

class TYShelves(object, ):
    """
    货架类，用于定义该货架能卖什么商品，是否在商城显示等
    """

    def __init__(self, name, displayName, productList, visibleInStore, iconType, sortValue=0, visibleCondition=None):
        pass

    def cloneForProducts(self, productList):
        pass

    @property
    def name(self):
        pass

    @property
    def displayName(self):
        pass

    @property
    def visibleInStore(self):
        pass

    @property
    def iconType(self):
        pass

    @property
    def sortValue(self):
        pass

    @property
    def productMap(self):
        pass

    @property
    def productList(self):
        pass

    @property
    def visibleCondition(self):
        pass

    def findProduct(self, productId):
        pass

    def findProductByAssetMinCount(self, assetKindId, minCount):
        """
        从本货架中查找最少包含minCount个assetKindId的商品
        @return: Product or None
        """
        pass

class TYBuyCountLimitRecord(object, ):
    """
    商品购买限制记录，用于记录购买周期内的购买次数
    """

    def __init__(self, lastBuyTimestamp, count):
        pass

class TYBuyCountLimitTimeCycle(TYConfable, ):

    def __init__(self):
        pass

    def isSameCycle(self, timestamp1, timestamp2):
        """
        判断timestamp1和timestamp2是否在同一个周期
        """
        pass

    def decodeFromDict(self, d):
        pass

class TYBuyCountLimitTimeCycleLife(TYBuyCountLimitTimeCycle, ):
    """
    本周期内限购
    """
    TYPE_ID = 'life'

    def isSameCycle(self, timestamp1, timestamp2):
        pass

class TYBuyCountLimitTimeCyclePerDay(TYBuyCountLimitTimeCycle, ):
    """
    每日限购
    """
    TYPE_ID = 'perDay'

    def isSameCycle(self, timestamp1, timestamp2):
        pass

class TYBuyCountLimitTimeCyclePerMonth(TYBuyCountLimitTimeCycle, ):
    """
    每月限购
    """
    TYPE_ID = 'perMonth'

    def isSameCycle(self, timestamp1, timestamp2):
        pass

class TYBuyCountLimitTimeCycleRegister(TYConfableRegister, ):
    _typeid_clz_map = {TYBuyCountLimitTimeCycleLife.TYPE_ID: TYBuyCountLimitTimeCycleLife, TYBuyCountLimitTimeCyclePerDay.TYPE_ID: TYBuyCountLimitTimeCyclePerDay, TYBuyCountLimitTimeCyclePerMonth.TYPE_ID: TYBuyCountLimitTimeCyclePerMonth}

class TYBuyCountLimit(TYConfable, ):
    """
    商品购买数量限制类，用于定义该商品的购买周期，以及每个周期内可购买多少数量，以及一些提示信息等
    """
    LIMIT_NON = 0
    LIMIT_START = 1
    LIMIT_END = 2
    LIMIT_COUNT = 3

    def __init__(self):
        pass

    def incrRecordCount(self, userId, record, count=1, timestamp=None):
        """
        增加count次购买次数
        @param record: 购买限制记录TYBuyLimitRecord
        @param count: 增加多少次
        @param timestamp: 当前时间戳
        @return: record
        """
        pass

    def checkLimit(self, userId, record, count=1, timestamp=None):
        """
        检查再购买count次是否超出购买限制
        @param record: 购买限制记录TYBuyLimitRecord
        @param count: 增加多少次
        @param timestamp: 当前时间戳
        @return: LIMIT_XXX
        """
        pass

    def getFailureByLimit(self, limit):
        """
        根据limit的值获取failue信息
        """
        pass

    def decodeFromDict(self, d):
        pass

    def _isOverCount(self, userId, record, count, timestamp):
        pass

class TYStoreSystem(object, ):

    def getShelvesListByClientId(self, gameId, userId, clientId):
        """
        根据clientId查找货架列表
        @return list<TYShelves>
        """
        pass

    def getShelvesByClientId(self, gameId, userId, clientId, shelvesName):
        """
        根据clientId查找货架列表
        @return TYShelves or None
        """
        pass

    def buyProduct(self, gameId, realGameId, userId, clientId, orderId, productId, count):
        """
        购买id=productId的商品
        @return: order
        """
        pass

    def findOrder(self, orderId):
        """
        查找订单
        """
        pass

    def deliveryOrder(self, userId, orderId, productId, chargeInfo, switchProductId=None, realGameId=0, orderPlatformId=''):
        """
        给订单发货
        """
        pass

    def getLastBuyProduct(self, gameId, userId):
        """
        获取最后购买的商品及购买商品的clientId
        @return: (product, clientId), or (None, None)
        """
        pass

    def findProduct(self, productId):
        """
        根据productId查找product
        @return: TYProduct or None
        """
        pass

    def isCloseLastBuy(self, clientId):
        """
        判断clientId是否关闭了最后购买记录
        """
        pass

    @property
    def firstRechargeThreshold(self):
        pass

class TYLastBuyConf(object, ):

    def __init__(self):
        pass

    def decodeFromDict(self, d):
        pass

class TYStoreSystemImpl(TYStoreSystem, ):

    def __init__(self, itemSystem, orderDao, clientStoreConf, eventBus, userCondRegister):
        pass

    def reloadConf(self, productsConf, storeConf):
        pass

    def getPricePic(self, price):
        pass

    @property
    def lastBuyConf(self):
        pass

    @property
    def firstRechargeThreshold(self):
        pass

    @property
    def deliveryConf(self):
        pass

    def getShelvesListByClientId(self, gameId, userId, clientId):
        pass

    def getShelvesByClientId(self, gameId, userId, clientId, shelvesName):
        pass

    def buyProduct(self, gameId, realGameId, userId, clientId, orderId, productId, count):
        pass

    def findProductInShelves(self, gameId, userId, clientId, productId):
        pass

    def canBuyProduct(self, gameId, userId, clientId, product, count):
        pass

    def _buyProductImpl(self, gameId, userId, clientId, orderId, product, count):
        pass

    def findOrder(self, orderId):
        """
        查找订单
        """
        pass

    def deliveryOrder(self, userId, orderId, productId, chargeInfo, switchProductId=None, realGameId=0, platformOrderId=''):
        """
        给订单发货
        """
        pass

    def getLastBuyProduct(self, gameId, userId):
        """
        获取最后购买的商品及购买商品的clientId
        """
        pass

    def findProduct(self, productId):
        """
        根据userId和clientId获取所有会员商品
        @return: list<Product>
        """
        pass

    def isCloseLastBuy(self, clientId):
        """
        判断clientId是否关闭了最后购买记录
        """
        pass

    def _productIdListToProductList(self, productIdList, allProductMap=None):
        pass

    def _filterBuyLimitProducts(self, userId, productList):
        pass

    def _checkProductLimit(self, userId, product, count, timestamp):
        pass

    def _checkBuyCountLimit(self, userId, product, count, timestamp):
        pass

    def _checkBuyConditions(self, userId, product, count, buyConditions):
        pass

    def _checkNotInVisibleBuyConditions(self, userId, product, count, buyConditions):
        pass

    def _recordBuy(self, orderDeliveryResult):
        pass

    def _loadOrder(self, orderId):
        pass

    def _deliveryOrder(self, order):
        pass

    def _finishDelivery(self, order, errorCode):
        pass

    def _recordForBuyCountLimit(self, order):
        pass

    def _buildBuyCountLimitRecordField(self, userId, productId):
        pass

    def _loadBuyCountLimitRecord(self, userId, productId, timestamp):
        pass

    def _saveBuyCountLimitRecord(self, userId, productId, record):
        pass

    def _recordLastBuyProduct(self, order):
        pass