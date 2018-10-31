# -*- coding: utf-8 -*-
"""
Created on 2015年6月3日

@author: zhaojiangang
"""
from datetime import datetime
from sre_compile import isstring
import struct
import freetime.util.log as ftlog
import poker.entity.biz.bireport as pkbireport
from poker.entity.biz.confobj import TYConfableRegister, TYConfable
from poker.entity.biz.content import TYContentUtils
from poker.entity.biz.exceptions import TYBizBadDataException
from poker.entity.biz.item.exceptions import TYItemConfException, TYUnExecuteableException, TYUnknownAssetKindException, TYDuplicateItemIdException, TYItemActionConditionNotEnoughException, TYAssetNotEnoughException, TYItemActionParamException
from poker.entity.events.tyevent import ModuleTipEvent, ItemCountChangeEvent
import poker.entity.events.tyeventbus as pkeventbus
from poker.util import strutil
import poker.util.timestamp as pktimestamp
MAX_4_BYTEI = 2147483647
MAX_UINT = 4294967295

class TYComponentItem(object, ):
    """
    可以合成的道具零件配置
    """

    def __init__(self, itemKindId, count):
        pass

    @classmethod
    def decodeFromDict(cls, d):
        pass

    @classmethod
    def decodeList(cls, l):
        pass

class TYItemData(object, ):
    """
    道具的存储对象，用于序列化数据成二进制
    """
    BASE_STRUCT_FMT = 'H5IB'
    BASE_STRUCT_LEN = struct.calcsize(BASE_STRUCT_FMT)

    def __init__(self):
        pass

    def toDict(self):
        pass

    def fromDict(self, d):
        pass

    @classmethod
    def decodeKindId(cls, itemData):
        pass

    @classmethod
    def encodeToBytes(cls, itemData):
        pass

    @classmethod
    def adjustUint(cls, value):
        pass

    @classmethod
    def decodeFromBytes(cls, itemData, dataBytes):
        pass

    def _getStructFormat(self):
        pass

    def _getFieldNames(self):
        pass

class TYItemActionCondition(TYConfable, ):
    """
    道具动作条件类，用于定义一个条件，在执行某个动作时检查
    """

    def __init__(self):
        pass

    def getParam(self, paramName, defVal=None):
        pass

    @property
    def failure(self):
        pass

    def check(self, gameId, userAssets, item, timestamp, params):
        pass

    def _conform(self, gameId, userAssets, item, timestamp, params):
        pass

    def _onFailure(self, gameId, userAssets, item, timestamp, params):
        pass

    def decodeFromDict(self, d):
        pass

class TYItemActionConditionRegister(TYConfableRegister, ):
    """
    道具动作条件类注册，主要是用于根据不同的typeId生成响应的条件类
    """
    _typeid_clz_map = {}

class TYItemActionResult(object, ):
    """
    执行某个动作的返回值
    """

    def __init__(self, action, item, message='', todotask=None):
        pass

class TYItemAction(TYConfable, ):
    """
    动作类，用于对某个道具执行一个动作
    """

    def __init__(self):
        pass

    @property
    def name(self):
        pass

    @property
    def displayName(self):
        pass

    @property
    def message(self):
        pass

    @property
    def mail(self):
        pass

    @property
    def itemKind(self):
        pass

    def getInputParams(self, gameId, userBag, item, timestamp):
        pass

    @property
    def conditionList(self):
        pass

    def checkParams(self, gameId, userAssets, item, timestamp, params):
        pass

    def getParamNameTypeList(self):
        pass

    def canDo(self, userBag, item, timestamp):
        """
        判断是否可以对item执行本动作
        """
        pass

    def initWhenLoaded(self, itemKind, itemKindMap, assetKindMap):
        """
        当配置解析工作完成后调用，用于初始化配置中一些itemKind相关的数据
        """
        pass

    def doAction(self, gameId, userAssets, item, timestamp, params):
        """
        对item执行本动作
        """
        pass

    def decodeFromDict(self, d):
        """
        从一个dict配置中解析该动作类
        """
        pass

    def _checkConditions(self, gameId, userAssets, item, timestamp, params):
        pass

    def _decodeFromDictImpl(self, d):
        """
        用于子类解析自己特有的数据
        """
        pass

    def _initWhenLoaded(self, itemKind, itemKindMap, assetKindMap):
        pass

    def _doActionImpl(self, gameId, userAssets, item, timestamp, params):
        pass

class TYItemActionRegister(TYConfableRegister, ):
    """
    用户道具动作类注册
    """
    _typeid_clz_map = {}

class TYItemUnits(TYConfable, ):
    """
    道具单位类，用于道具的增加和消耗
    """

    def __init__(self):
        pass

    def isTiming(self):
        pass

    def add(self, item, count, timestamp):
        """
        给item增加count个单位
        """
        pass

    def balance(self, item, timestamp):
        """
        剩余多少个单位
        """
        pass

    def consume(self, item, count, timestamp):
        """
        给item消耗count个单位
        @return: consumeCount
        """
        pass

    def forceConsume(self, item, count, timestamp):
        """
        强制消耗count个单位，如果不足则消耗所有
        @return: consumeCount
        """
        pass

    def decodeFromDict(self, d):
        pass

    def _decodeFromDictImpl(self, d):
        pass

class TYItemUnitsRegister(TYConfableRegister, ):
    """
    道具单位注册类
    """
    _typeid_clz_map = {}

class TYItemKind(TYConfable, ):
    """
    定义一种具体的道具，比如月光钥匙，记牌器
    """

    def __init__(self):
        pass

    def isExpires(self, timestamp):
        pass

    def newItem(self, itemId, timestamp):
        """
        产生一个新的本种类的道具，id=itemId
        @param itemId: 道具ID
        @param timestamp: 当前时间戳
        @return: Item的子类
        """
        pass

    def newItemForDecode(self, itemId):
        """
        产生一个本种类的道具，用于反序列化
        """
        pass

    def newItemData(self):
        """
        产生一个ItemData
        """
        pass

    def getSupportedActions(self):
        """
        获取支持的动作列表
        @return: list<TYItemAction>
        """
        pass

    def findActionByName(self, actionName):
        """
        根据action名称查找action
        """
        pass

    def findActionsByNames(self, actionNames):
        """
        查找name在actionNames列表中的action
        """
        pass

    def initWhenLoaded(self, itemKindMap, assetKindMap):
        """

        """
        pass

    def processWhenUserLogin(self, item, userAssets, gameId, isDayFirst, timestamp):
        pass

    def processWhenAdded(self, item, userAssets, gameId, timestamp):
        pass

    def _initWhenLoaded(self, itemKindMap, assetKindMap):
        pass

    def _initComponentList(self, itemKindMap):
        pass

    def decodeFromDict(self, d):
        """
        从d中解析数据
        """
        pass

    def _decodeFromDictImpl(self, d):
        pass

    def visibleTrade(self):
        """
        是否可以交易
        @return: True: 可以, False: 不可以'
        """
        pass

class TYItem(object, ):
    """
    道具基类
    """

    def __init__(self, itemKind, itemId):
        pass

    @property
    def itemKind(self):
        pass

    @property
    def kindId(self):
        pass

    @property
    def itemId(self):
        pass

    def checkMaxOwnCount(self):
        pass

    def isDied(self, timestamp):
        pass

    def isExpires(self, timestamp):
        """
        检查道具是否到期
        @param timestamp: 当前时间戳
        @return: 到期返回True, 否则返回False
        """
        pass

    def visibleInBag(self, timestamp):
        pass

    def onDied(self, timestamp):
        pass

    def needRemoveFromBag(self, timestamp):
        """
        检查是否需要从背包删除该道具
        @param timestamp: 当前时间戳
        @return: 需要返回True, 否则返回False
        """
        pass

    def addUnits(self, count, timestamp):
        """
        添加count个单位
        """
        pass

    def balance(self, timestamp):
        """
        剩余多少个单位
        """
        pass

    def consume(self, count, timestamp):
        """
        消耗count个单位
        @return: consumeCount
        """
        pass

    def forceConsume(self, item, count, timestamp):
        """
        强制消耗count个单位，如果不足则消耗所有
        @return: consumeCount
        """
        pass

    def decodeFromItemData(self, itemData):
        pass

    def encodeToItemData(self):
        pass

    def _decodeFromItemData(self, itemData):
        pass

    def _encodeToItemData(self, itemData):
        pass

class TYItemKindRegister(TYConfableRegister, ):
    _typeid_clz_map = {}

class TYUserBag(object, ):

    @property
    def userId(self):
        pass

    @property
    def userAssets(self):
        pass

    def findItem(self, itemId):
        """
        在背包中根据itemId查找道具
        @param itemId: 要查找的道具ID
        @return: item or None
        """
        pass

    def getAllItem(self):
        """
        获取所有item
        @return: list<Item>
        """
        pass

    def getItemByKind(self, itemKind):
        """
        获取某个类型的一个道具
        """
        pass

    def getItemByKindId(self, itemKindId):
        """
        获取某个类型的一个道具
        """
        pass

    def getAllKindItem(self, itemKind):
        """
        获取所有item
        @return: list<Item>
        """
        pass

    def getAllKindItemByKindId(self, kindId):
        """
        获取所有item
        @return: list<Item>
        """
        pass

    def getAllTypeItem(self, itemType):
        """
        获取所有item类类型为itemType的道具
        @return: list<Item>
        """
        pass

    def addItem(self, gameId, item, timestamp, eventId, intEventParam):
        """
        添加一个道具到背包
        """
        pass

    def addItemUnits(self, gameId, item, count, timestamp, eventId, intEventParam):
        """
        给某个道具添加count个单位
        """
        pass

    def addItemUnitsByKind(self, gameId, itemKind, count, timestamp, fromUserId, eventId, intEventParam, roomId=0, tableId=0, roundId=0, param01=0, param02=0):
        """
        添加count个单位的道具
        """
        pass

    def removeItem(self, gameId, item, timestamp, eventId, intEventParam):
        """
        在背包中根据itemId删除道具，返回删除的道具
        @param itemId: 要删除的道具ID
        @return: item or None
        """
        pass

    def calcTotalUnitsCount(self, itemKind, timestamp=None):
        """
        计算所有itemKind种类的道具的数量
        @param itemKind: 那种类型
        @param timestamp: 当前时间
        @return: 剩余多少个单位
        """
        pass

    def consumeItemUnits(self, gameId, item, unitsCount, timestamp, eventId, intEventParam):
        """
        消耗item unitsCount个单位
        @param item: 那个道具
        @param unitsCount: 多少个单位
        @return: consumeCount
        """
        pass

    def consumeUnitsCountByKind(self, gameId, itemKind, unitsCount, timestamp, eventId, intEventParam, roomId=0, tableId=0, roundId=0, param01=0, param02=0):
        """
        消耗道具种类为itemKind的unitsCount个单位的道具
        @param itemKind: 那种类型
        @param unitsCount: 多少个单位
        @return: consumeCount
        """
        pass

    def forceConsumeUnitsCountByKind(self, gameId, itemKind, unitsCount, timestamp, eventId, intEventParam):
        """
        强制消耗道具种类为itemKind的unitsCount个单位的道具，如果不够则消耗所有的
        @param itemKind: 那种类型
        @param unitsCount: 多少个单位
        @return: consumeCount
        """
        pass

    def updateItem(self, gameId, item, timestamp=None):
        """
        保存道具
        @param item: 要保存的道具
        """
        pass

    def processWhenUserLogin(self, gameId, isDayFirst, timestamp=None):
        """
        当用户登录时调用该方法，处理对用户登录感兴趣的道具
        @param gameId: 哪个游戏驱动
        @param isDayFirst: 是否是
        """
        pass

    def getExecutableActions(self, item, timestamp):
        """
        获取item支持的动作列表
        @return: list<TYItemAction>
        """
        pass

    def doAction(self, gameId, item, actionName, timestamp=None, params={}):
        """
        执行动作
        @param gameId: 哪个游戏驱动的
        @param item: 哪个道具执行
        @param actionName: 执行哪个动作
        @param params: 参数
        """
        pass

class TYItemDao(object, ):

    def __init__(self, itemSystem, itemDataDao):
        pass

    def loadAll(self, userId):
        """
        加载用户所有的道具
        """
        pass

    def saveItem(self, userId, item):
        """
        保存用户道具
        """
        pass

    def removeItem(self, userId, item):
        """
        删除用户道具
        """
        pass

    def nextItemId(self):
        """
        获取一个全局唯一的道具Id
        """
        pass

    def _decodeItem(self, userId, itemId, itemDataBytes):
        pass

class TYItemSystem(object, ):

    def getInitItems(self):
        """
        获取用户初始化配置
        """
        pass

    def getInitItemsNew(self):
        """
        获取用户初始化配置
        """
        pass

    def getInitItemsByTemplateName(self, templateName):
        """
        获取用户初始化模版
        """
        pass

    def findAssetKind(self, kindId):
        """
        根据kindId查找asset定义
        @return: AssetKind or None
        """
        pass

    def getAllAssetKind(self):
        """
        获取所有asset定义
        @return: list<AssetKind>
        """
        pass

    def getAllRateAssetKind(self):
        """
        获取所有显示比例不是1的asset定义
        @return: list<AssetKind>
        """
        pass

    def findItemKind(self, kindId):
        """
        根据kindId查找道具定义
        @param kindId: 道具类型ID 
        @return: ItemKind 
        """
        pass

    def getAllItemKind(self):
        """
        获取所有道具定义
        @return: list<ItemKind>
        """
        pass

    def getAllItemKindByType(self, itemKindClassType):
        """
        获取所有itemKindClassType类型的道具定义
        @return: list<ItemKind>
        """
        pass

    def loadUserAssets(self, userId):
        """
        加载用户资产
        @return: UserAssets
        """
        pass

    def newItemFromItemData(self, itemData):
        """

        """
        pass

class TYUserAssets(object, ):

    @property
    def userId(self):
        """
        获取用户ID
        @return: userId 
        """
        pass

    def getUserBag(self):
        """
        获取用户背包
        @return: TYUserBag
        """
        pass

    def balance(self, gameId, assetKindId, timestamp):
        """
        获取assetKindId的余额
        @return: (TYAssetKind, balance)
        """
        pass

    def addAsset(self, gameId, assetKindId, count, timestamp, eventId, intEventParam, roomId=0, tableId=0, roundId=0, param01=0, param02=0):
        """
        增加Asset
        @param gameId: 哪个游戏驱动的
        @param assetKindId: asset种类ID
        @param count: 个数
        @param timestamp: 时间戳
        @param eventId: 哪个事件触发的
        @param intEventParam: eventId相关的参数
        @return: (TYAssetKind, addCount, final)
        """
        pass

    def consumeAsset(self, gameId, assetKindId, count, timestamp, eventId, intEventParam, roomId=0, tableId=0, roundId=0, param01=0, param02=0):
        """
        消耗Asset
        @param gameId: 哪个游戏驱动的
        @param assetKindId: asset种类ID
        @param count: 个数
        @param timestamp: 时间戳
        @param eventId: 哪个事件触发的
        @param intEventParam: eventId相关的参数
        @return: (TYAssetKind, consumeCount, final)
        """
        pass

    def forceConsumeAsset(self, gameId, assetKindId, count, timestamp, eventId, intEventParam):
        """
        消耗Asset
        @param gameId: 哪个游戏驱动的
        @param assetKindId: asset种类
        @param count: 个数
        @param timestamp: 时间戳
        @param eventId: 哪个事件触发的
        @param intEventParam: eventId相关的参数
        @return: (TYAssetKind, consumeCount, final)
        """
        pass

    def consumeContentItemList(self, gameId, contentItemList, ignoreUnknown, eventId, intEventParam, roomId=0, tableId=0, roundId=0, param01=0, param02=0):
        """
        消耗contentItemList
        @param gameId: 哪个游戏驱动的
        @param contentItemList: 要消耗的内容
        @param ignoreUnknown: 是否忽略不认识的item, 如果不忽略则会抛出异常
        @param eventId: 哪个事件触发的
        @param intEventParam: eventId相关的参数
        @return: list<(TYAssetKind, consumeCount, final)>
        """
        pass

    def sendContentItemList(self, gameId, contentItemList, count, ignoreUnknown, timestamp, eventId, intEventParam, roomId=0, tableId=0, roundId=0, param01=0, param02=0):
        """
        给用户发货
        @param gameId: 哪个游戏驱动的
        @param contentItemList: 要发货的内容
        @param count: 数量
        @param ignoreUnknown: 是否忽略不认识的item, 如果不忽略则会抛出异常
        @param eventId: 哪个事件触发的
        @param intEventParam: eventId相关的参数
        @return: list<(TYAssetKind, consumeCount, final)>
        """
        pass

    def sendContent(self, gameId, content, count, ignoreUnknown, timestamp, eventId, intEventParam, param01=0, param02=0):
        """
        给用户发货
        @param gameId: 哪个游戏驱动的
        @param content: 要发货的内容
        @param count: 发多少个
        @param ignoreUnknown: 是否忽略不认识的item, 如果不忽略则会抛出异常
        @param eventId: 哪个事件触发的
        @param intEventParam: eventId相关的参数
        @return: list<(TYAssetKind, consumeCount, final)>
        """
        pass

class TYRecycleResult(object, ):

    def __init__(self, item, gotItems):
        pass

class TYUserBagImpl(TYUserBag, ):

    def __init__(self, userId, dao, assets):
        pass

    def load(self):
        pass

    @property
    def userId(self):
        pass

    @property
    def userAssets(self):
        pass

    def _onCountChanged(self):
        pass

    def findItem(self, itemId):
        """
        在背包中根据itemId查找道具
        @param itemId: 要查找的道具ID
        @return: item or None
        """
        pass

    def getAllItem(self):
        """
        获取所有item
        @return: list<Item>
        """
        pass

    def getItemByKind(self, itemKind):
        """
        获取某个类型的一个道具
        """
        pass

    def getItemByKindId(self, itemKindId):
        """
        获取某个类型的一个道具
        """
        pass

    def getAllKindItem(self, itemKind):
        """
        获取所有item
        @return: list<Item>
        """
        pass

    def getAllKindItemByKindId(self, kindId):
        """
        获取所有item
        @return: list<Item>
        """
        pass

    def getAllTypeItem(self, itemType):
        """
        获取所有item类类型为itemType的道具
        @return: list<Item>
        """
        pass

    def addItem(self, gameId, item, timestamp, eventId, intEventParam):
        """
        添加一个道具到背包
        """
        pass

    def addItemUnits(self, gameId, item, count, timestamp, eventId, intEventParam):
        """
        给某个道具添加count个单位
        """
        pass

    def addItemUnitsByKind(self, gameId, itemKind, count, timestamp, fromUserId, eventId, intEventParam, roomId=0, tableId=0, roundId=0, param01=0, param02=0):
        """
        添加count个单位的道具
        """
        pass

    def removeItem(self, gameId, item, timestamp, eventId, intEventParam):
        """
        在背包中根据itemId删除道具，返回删除的道具
        @param itemId: 要删除的道具ID
        @return: item or None
        """
        pass

    def calcTotalUnitsCount(self, itemKind, timestamp=None):
        """
        计算所有itemKind种类的道具的数量
        @param itemKind: 那种类型
        @return: 剩余多少个单位
        """
        pass

    def _calcTotalUnitsCount(self, sameKindItemList, timestamp):
        pass

    def consumeItemUnits(self, gameId, item, unitsCount, timestamp, eventId, intEventParam):
        """
        消耗item unitsCount个单位
        @param item: 那个道具
        @param unitsCount: 多少个单位
        @return: consumeCount
        """
        pass

    def consumeUnitsCountByKind(self, gameId, itemKind, unitsCount, timestamp, eventId, intEventParam, roomId=0, tableId=0, roundId=0, param01=0, param02=0):
        """
        消耗道具种类为itemKind的unitsCount个单位的道具
        @param itemKind: 那种类型
        @param unitsCount: 多少个单位
        @return: consumeCount
        """
        pass

    def forceConsumeUnitsCountByKind(self, gameId, itemKind, unitsCount, timestamp, eventId, intEventParam):
        """
        强制消耗道具种类为itemKind的unitsCount个单位的道具，如果不够则消耗所有的
        @param itemKind: 那种类型
        @param unitsCount: 多少个单位
        @return: consumeCount
        """
        pass

    def updateItem(self, gameId, item, timestamp=None):
        """
        保存道具
        @param item: 要保存的道具
        """
        pass

    def processWhenUserLogin(self, gameId, isDayFirst, timestamp=None):
        """
        当用户登录时调用该方法，处理对用户登录感兴趣的道具
        @param gameId: 哪个游戏驱动
        @param isDayFirst: 是否是
        """
        pass

    def getExecutableActions(self, item, timestamp):
        """
        获取item支持的动作列表
        @return: list<TYItemAction>
        """
        pass

    def doAction(self, gameId, item, actionName, timestamp=None, params={}):
        """
        执行动作
        @param gameId: 哪个游戏驱动的
        @param item: 哪个道具执行
        @param actionName: 执行哪个动作
        """
        pass

    def _findActionByName(self, actions, actionName):
        pass

    def _addItem(self, item):
        pass

    def _removeItem(self, item):
        pass

    def _updateItem(self, item, timestamp):
        pass

    def _addItemToMap(self, item):
        pass

    def _removeItemFromMap(self, item):
        pass

class TYAssetKind(TYConfable, ):
    TYPE_ID = 'unknown'

    def __init__(self):
        pass

    def decodeFromDict(self, d):
        pass

    def buildContentForDelivery(self, count):
        pass

    def buildContent(self, count, needUnits=True):
        pass

    def add(self, gameId, userAssets, kindId, count, timestamp, eventId, intEventParam, roomId=0, tableId=0, roundId=0, param01=0, param02=0):
        """
        @return: finalCount
        """
        pass

    def consume(self, gameId, userAssets, kindId, count, timestamp, eventId, intEventParam, roomId=0, tableId=0, roundId=0, param01=0, param02=0):
        """
        @return: consumeCount, finalCount
        """
        pass

    def forceConsume(self, gameId, userAssets, kindId, count, timestamp, eventId, intEventParam):
        """
        @return: consumeCount, finalCount
        """
        pass

    def balance(self, userAssets, timestamp):
        """
        @return: balance
        """
        pass

class TYAssetKindItem(TYAssetKind, ):

    def __init__(self, itemKind):
        pass

    @classmethod
    def buildKindIdByItemKind(cls, itemKind):
        pass

    @classmethod
    def buildKindIdByItemKindId(cls, itemKindId):
        pass

    def add(self, gameId, userAssets, kindId, count, timestamp, eventId, intEventParam, roomId=0, tableId=0, roundId=0, param01=0, param02=0):
        """
        @return: finalCount
        """
        pass

    def consume(self, gameId, userAssets, kindId, count, timestamp, eventId, intEventParam, roomId=0, tableId=0, roundId=0, param01=0, param02=0):
        """
        @return: consumeCount, finalCount
        """
        pass

    def forceConsume(self, gameId, userAssets, kindId, count, timestamp, eventId, intEventParam):
        """
        @return: consumeCount
        """
        pass

    def balance(self, userAssets, timestamp):
        """
        @return: balance
        """
        pass

class TYAssetKindRegister(TYConfableRegister, ):
    _typeid_clz_map = {}

class TYItemSystemImpl(TYItemSystem, ):

    def __init__(self, itemDataDao):
        pass

    def _decodeInitItems(self, initItemDictList, itemKindMap):
        pass

    def reloadConf(self, conf):
        pass

    def getInitItems(self):
        """
        获取用户初始化配置
        """
        pass

    def getInitItemsNew(self):
        """
        获取用户初始化配置
        """
        pass

    def getInitItemsByTemplateName(self, templateName):
        pass

    def findAssetKind(self, kindId):
        """
        根据kindId查找asset定义
        @return: AssetKind or None
        """
        pass

    def getAllAssetKind(self):
        """
        获取所有asset定义
        @return: list<AssetKind>
        """
        pass

    def getAllRateAssetKind(self):
        """
        获取所有显示比例不是1的asset定义
        @return: list<AssetKind>
        """
        pass

    def findItemKind(self, kindId):
        """
        根据kindId查找道具定义
        @param kindId: 道具类型ID 
        @return: ItemDefine 
        """
        pass

    def getAllItemKind(self):
        """
        获取所有道具定义
        @return: list<ItemKind>
        """
        pass

    def getAllItemKindByType(self, itemKindClassType):
        """
        获取所有itemKindClassType类型的道具定义
        @return: list<ItemKind>
        """
        pass

    def loadUserAssets(self, userId):
        """
        加载用户背包
        @return: UserAssets
        """
        pass

    def newItemFromItemData(self, itemData):
        pass

class TYUserAssetsImpl(TYUserAssets, ):

    def __init__(self, userId, itemSystem, itemDao):
        pass

    @property
    def userId(self):
        pass

    def getUserBag(self):
        pass

    def balance(self, gameId, assetKindId, timestamp):
        """
        获取assetKindId的余额
        """
        pass

    def addAsset(self, gameId, assetKindId, count, timestamp, eventId, intEventParam, roomId=0, tableId=0, roundId=0, param01=0, param02=0):
        """
        增加Asset
        @param gameId: 哪个游戏驱动的
        @param assetKindId: asset种类ID
        @param count: 个数
        @param timestamp: 时间戳
        @param eventId: 哪个事件触发的
        @param intEventParam: eventId相关的参数
        @return: (AssetKind, count, final)
        """
        pass

    def consumeAsset(self, gameId, assetKindId, count, timestamp, eventId, intEventParam, roomId=0, tableId=0, roundId=0, param01=0, param02=0):
        """
        消耗Asset
        @param gameId: 哪个游戏驱动的
        @param assetKindId: asset种类ID
        @param count: 个数
        @param eventId: 哪个事件触发的
        @param intEventParam: eventId相关的参数
        @return: (TYAssetKind, consumeCount, final)
        """
        pass

    def forceConsumeAsset(self, gameId, assetKindId, count, timestamp, eventId, intEventParam):
        """
        消耗Asset
        @param gameId: 哪个游戏驱动的
        @param assetKindId: asset种类
        @param count: 个数
        @param timestamp: 时间戳
        @param eventId: 哪个事件触发的
        @param intEventParam: eventId相关的参数
        @return: (TYAssetKind, consumeCount, final)
        """
        pass

    def __backConsumed(self, gameId, assetList, eventId, intEventParam, roomId=0, tableId=0, roundId=0, param01=0, param02=0):
        pass

    def consumeContentItemList(self, gameId, contentItemList, ignoreUnknown, timestamp, eventId, intEventParam, roomId=0, tableId=0, roundId=0, param01=0, param02=0):
        """
        消耗contentItemList
        @param gameId: 哪个游戏驱动的
        @param contentItemList: 要消耗的内容
        @param ignoreUnknown: 是否忽略不认识的item, 如果不忽略则会抛出异常
        @param eventId: 哪个事件触发的
        @param intEventParam: eventId相关的参数
        @return: list<(TYAssetKind, consumeCount, final)>
        """
        pass

    def sendContentItemList(self, gameId, contentItemList, count, ignoreUnknown, timestamp, eventId, intEventParam, roomId=0, tableId=0, roundId=0, param01=0, param02=0):
        """
        给用户发货
        @param gameId: 哪个游戏驱动的
        @param contentItemList: 要发货的内容
        @param ignoreUnknown: 是否忽略不认识的item, 如果不忽略则会抛出异常
        @param eventId: 哪个事件触发的
        @param intEventParam: eventId相关的参数
        @return: list<(TYAssetKind, consumeCount, final)>
        """
        pass

    def sendContent(self, gameId, content, count, ignoreUnknown, timestamp, eventId, intEventParam, param01=0, param02=0):
        """
        给用户发货
        @param gameId: 哪个游戏驱动的
        @param content: 要发货的内容
        @param count: 发多少个
        @param ignoreUnknown: 是否忽略不认识的item, 如果不忽略则会抛出异常
        @param eventId: 哪个事件触发的
        @param intEventParam: eventId相关的参数
        @return: list<(TYAssetKind, consumeCount, final)>
        """
        pass

class TYAssetUtils(object, ):

    @classmethod
    def buildContent(cls, assetKindTuple, needUnits=True):
        pass

    @classmethod
    def buildContents(cls, assetKindTupleList, needUnits=True):
        pass

    @classmethod
    def buildContentsString(cls, assetKindTupleList, needUnits=True):
        pass

    @classmethod
    def buildItemContent(cls, itemKindTuple):
        pass

    @classmethod
    def buildItemContents(cls, itemKindTupleList):
        pass

    @classmethod
    def buildItemContentsString(cls, itemKindTupleList):
        pass

    @classmethod
    def getChangeDataNames(cls, assetKindTupleList):
        pass

    @classmethod
    def getAssetCount(cls, assetKindTupleList, assetKindId):
        pass