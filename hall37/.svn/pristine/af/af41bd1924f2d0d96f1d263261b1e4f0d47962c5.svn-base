# -*- coding:utf-8 -*-
'''
Created on 2017年12月25日

@author: zhaojiangang
'''
from sre_compile import isstring

import freetime.util.log as ftlog
from hall.entity import hallvip, datachangenotify, hallitem
from hall.entity.hallconf import HALL_GAMEID
from hall.entity.hallevent import UserReceivedCouponEvent
from poker.entity.biz.content import TYContentRegister
from poker.entity.biz.exceptions import TYBizConfException, TYBizException
from poker.entity.biz.item.item import TYAssetUtils
from poker.entity.configure import configure
from poker.entity.dao import daobase, userchip, sessiondata
from poker.entity.events.tyevent import EventConfigure
import poker.entity.events.tyeventbus as pkeventbus
from poker.util import strutil
import poker.util.timestamp as pktimestamp


# 初始化标志
_inited = False
# map<exchangeId, exchageItem>
_exchangeMap = {}
# list<(vipRange, exchangeItemList)>
_vipExchangeList = []


class ReceivedItem(object):
    def __init__(self, count=0, source=None, timestamp=0):
        # 数量
        self.count = count
        # 来源
        self.source = source
        # 领取时间
        self.timestamp = timestamp
    
    def toDict(self):
        return {
            'count':self.count,
            'source':self.source,
            'time':self.timestamp
        }
    
    def fromDict(self, d):
        self.count = d['count']
        self.source = d['source']
        self.timestamp = d['time']
        return self


MAX_RECEIVED_ITEMS = 10


class ExchangeItem(object):
    def __init__(self):
        # 兑换id
        self.exchangeId = None
        self.name = None
        self.desc = None
        # 图片
        self.pic = None
        # 话费多少奖券
        self.cost = None
        # 发货内容
        self.content = None
    
    def fromDict(self, d):
        self.exchangeId = d.get('exchangeId')
        if not isinstance(self.exchangeId, int) and self.exchangeId <= 0:
            raise TYBizConfException(d, 'ExchangeItem.exchangeId must be int > 0')
        
        self.name = d.get('name')
        if not isstring(self.name):
            raise TYBizConfException(d, 'ExchangeItem.name must be string')
        
        self.desc = d.get('desc', '')
        if not isstring(self.desc):
            raise TYBizConfException(d, 'ExchangeItem.desc must be string')
        
        self.pic = d.get('pic')
        if not isstring(self.pic):
            raise TYBizConfException(d, 'ExchangeItem.pic must be string')
        
        self.cost = d.get('cost')
        if not isinstance(self.cost, int) and self.cost <= 0:
            raise TYBizConfException(d, 'ExchangeItem.cost must be int > 0')
        
        self.content = TYContentRegister.decodeFromDict(d.get('content'))
        return self
    

EXCHANGE_STATE_NORMAL = 0
EXCHANGE_STATE_EXCHANGED = 1

EXCHANGE_STATES = (EXCHANGE_STATE_NORMAL, EXCHANGE_STATE_EXCHANGED)

 
class UserStatus(object):
    def __init__(self, userId, couponCount):
        self.userId = userId
        # 用户奖券数量
        self.couponCount = couponCount
        # 收到的红包券
        self.receivedItems = []
        # 该用户能兑换的商品list<exchangeItem, state>
        self.exchangeItems = []

    def addReceivedItem(self, count, source, timestamp):
        item = ReceivedItem(count, source, timestamp)
        self.receivedItems.append(item)
        self.trimReceivedItems()
        return item
    
    def trimReceivedItems(self):
        trimCount = len(self.receivedItems) - MAX_RECEIVED_ITEMS
        trimCount = max(0, trimCount)
        if trimCount > 0:
            self.receivedItems = self.receivedItems[trimCount:]
    
    def addExchangeItem(self, exchangeItem, state):
        self.exchangeItems.append((exchangeItem, state))
        
    def getOpenItem(self):
        for exchange, state in self.exchangeItems:
            if self.couponCount >= exchange.cost and state == EXCHANGE_STATE_NORMAL:
                return exchange
        return None
    

def findExchange(exchangeId):
    return _exchangeMap.get(exchangeId)


def findInitExchangeList(vipLevel):
    for vipRange, exchangeList in _vipExchangeList:
        if ((vipRange[0] == -1 or vipLevel >= vipRange[0])
            and (vipRange[1] == -1 or vipLevel <= vipRange[1])):
            return exchangeList
    return None


def initUserStatus(status, clientId):
    vipLevel = hallvip.userVipSystem.getUserVip(status.userId).vipLevel.level
    exchangeList = findInitExchangeList(vipLevel)
    if exchangeList:
        for ei in exchangeList:
            status.addExchangeItem(ei, EXCHANGE_STATE_NORMAL)
    
    ftlog.info('hall_red_packet_exchange.initUserStatus',
               'userId=', status.userId,
               'vipLevel=', vipLevel,
               'exchangeList=', [e.exchangeId for e in exchangeList] if exchangeList else [])
    return status


def saveUserStatus(status):
    ritems = []
    eitems = []
    for ritem in status.receivedItems:
        ritems.append({'count':ritem.count, 'source':ritem.source, 'time':ritem.timestamp})
    for eitem, state in status.exchangeItems:
        eitems.append((eitem.exchangeId, state))

    jstr = strutil.dumps({'ritems':ritems, 'eitems':eitems})
    daobase.executeUserCmd(status.userId, 'hset', 'rpexchange:%s:%s' % (HALL_GAMEID, status.userId), 'status', jstr)
    if ftlog.is_debug():
        ftlog.debug('hall_red_packet_exchange.saveUserStatus',
                    'userId=', status.userId,
                    'jstr=', jstr)


def loadUserStatus(userId, clientId, timestamp=None):
    coupon = userchip.getCoupon(userId)
    jstr = daobase.executeUserCmd(userId, 'hget', 'rpexchange:%s:%s' % (HALL_GAMEID, userId), 'status')
    if ftlog.is_debug():
        ftlog.debug('hall_red_packet_exchange.loadUserStatus',
                    'userId=', userId,
                    'clientId=', clientId,
                    'jstr=', jstr)
    if jstr:
        try:
            d = strutil.loads(jstr)
            status = UserStatus(userId, coupon)
            for ritem in d.get('ritems', []):
                status.addReceivedItem(ritem['count'], ritem['source'], ritem['time'])
            for eitem in d.get('eitems', []):
                eid, state = eitem[0], eitem[1]
                exchange = findExchange(eid)
                if not exchange:
                    ftlog.warn('hall_red_packet_exchange.loadUserStatus UnknownExchange',
                               'userId=', userId,
                               'clientId=', clientId,
                               'exchangId=', eid)
                    continue
                if state not in EXCHANGE_STATES:
                    ftlog.warn('hall_red_packet_exchange.loadUserStatus BadState',
                               'userId=', userId,
                               'clientId=', clientId,
                               'exchangId=', eid,
                               'state=', state)
                    continue
                
                status.addExchangeItem(exchange, state)
            return status
        except:
            ftlog.warn('hall_red_packet_exchange.loadUserStatus BadData',
                       'userId=', userId,
                       'clientId=', clientId,
                       'jstr=', jstr)
    
    return initUserStatus(UserStatus(userId, coupon), clientId)


def payForExchange(userAssets, exchangeItem, timestamp=None):
    timestamp = timestamp or pktimestamp.getCurrentTimestamp()
    assetTuple = userAssets.consumeAsset(HALL_GAMEID,
                                         'user:coupon',
                                         exchangeItem.cost,
                                         timestamp,
                                         'HALL_RP_EXCHANGE_COST',
                                         exchangeItem.exchangeId)

    if assetTuple[1] < exchangeItem.cost:
        ftlog.warn ('hall_red_packet_exchange.payForExchange'
                    'gameId=', HALL_GAMEID,
                    'userId=', userAssets.userId,
                    'cost=', ('user:coupon', exchangeItem.cost),
                    'consumedCount=', assetTuple[1],
                    'err=', 'CostNotEnough')

        raise TYBizException(-1, '您的%s不足' % (assetTuple[0].displayName))

    if assetTuple[0].keyForChangeNotify:
        datachangenotify.sendDataChangeNotify(HALL_GAMEID, userAssets.userId, assetTuple[0].keyForChangeNotify)


def backCostForExchange(userAssets, exchangeItem, timestamp=None):
    timestamp = timestamp or pktimestamp.getCurrentTimestamp()
    assetKind, _addCount, _final = userAssets.addAsset(HALL_GAMEID,
                                                       'user:coupon',
                                                       exchangeItem.cost,
                                                       timestamp,
                                                       'HALL_RP_EXCHANGE_COST_BACK',
                                                       exchangeItem.exchangeId)
    if assetKind.keyForChangeNotify:
        datachangenotify.sendDataChangeNotify(HALL_GAMEID, userAssets.userId, assetKind.keyForChangeNotify)


def deliveryContentForExchange(userAssets, exchangeItem, timestamp=None):
    timestamp = timestamp or pktimestamp.getCurrentTimestamp()
    assetList = userAssets.sendContent(HALL_GAMEID, exchangeItem.content,
                                       1, True, timestamp,
                                       'HALL_RP_EXCHANGE_DELIVERY',
                                       exchangeItem.exchangeId)
    changed = TYAssetUtils.getChangeDataNames(assetList)
    if changed:
        datachangenotify.sendDataChangeNotify(HALL_GAMEID, userAssets.userId, changed)

    return assetList


def indexOfExchangeItem(status, exchangeItemId):
    for i, (eitem, _) in enumerate(status.exchangeItems):
        if eitem.exchangeId == exchangeItemId:
            return i, eitem
    return -1, None


def updateExchangeItemState(status, exchangeItemId, state):
    i, eitem = indexOfExchangeItem(status, exchangeItemId)
    if i != -1:
        status.exchangeItems[i] = (eitem, state)
        return True
    return False
        

def doExchange(status, exchangeId):
    exchangeItem = status.getOpenItem()
    if not exchangeItem:
        raise TYBizException(-1, '没有可以兑换的项目')
    
    if exchangeItem.exchangeId != exchangeId:
        raise TYBizException(-1, '兑换项目不匹配')
    
    state = 0
    userAssets = hallitem.itemSystem.loadUserAssets(status.userId)
    try:
        payForExchange(userAssets, exchangeItem)
        updateExchangeItemState(status, exchangeItem.exchangeId, EXCHANGE_STATE_EXCHANGED)
        saveUserStatus(status)
        state = 1
        ret = deliveryContentForExchange(userAssets, exchangeItem)
        state = 2
        status.couponCount = userchip.getCoupon(status.userId)
        return exchangeItem.cost, ret
    except:
        if state == 1:
            backCostForExchange(userAssets, exchangeItem)
        ftlog.error('hall_red_packet_exchange.doExchange',
                    'userId=', status.userId,
                    'exchangeId=', exchangeId,
                    'state=', state)
        raise
    

def _reloadConf():
    global _exchangeMap
    global _vipExchangeList

    exchangeMap = {}
    vipExchangeList = []
    
    conf = configure.getGameJson(HALL_GAMEID, 'red_packet_exchange', {})
    
    for exchangeD in conf.get('exchanges', []):
        exchange = ExchangeItem().fromDict(exchangeD)
        if exchangeMap.get(exchange.exchangeId):
            raise TYBizConfException(exchangeD, 'Duplicate exchangeId %s' % (exchange.exchangeId))
        exchangeMap[exchange.exchangeId] = exchange

    for vipExchangeListD in conf.get('vipExchangeList', []):
        vipRange = vipExchangeListD.get('vipRange')
        if (not isinstance(vipRange, list)
            or len(vipRange) != 2
            or not isinstance(vipRange[0], int)
            or not isinstance(vipRange[1], int)):
            raise TYBizConfException(vipExchangeListD, 'vipExchangeList.vipRange must be int list and len=2')
        
        if vipRange[1] != -1 and vipRange[1] < vipRange[0]:
            raise TYBizConfException(vipExchangeListD, 'vipExchangeList.vipRange[1] must be >= vipRange[0]')
        
        exchangeIds = vipExchangeListD.get('exchangeIds')
        if not isinstance(exchangeIds, list):
            raise TYBizConfException(vipExchangeListD, 'vipExchangeList.exchangeIds must be list')

        exchangeList = []
        for exchangeId in exchangeIds:
            exchange = exchangeMap.get(exchangeId)
            if not exchange:
                raise TYBizConfException(vipExchangeListD, 'Unknown exchange %s' % (exchangeId))
            exchangeList.append(exchange)
        
        vipExchangeList.append((vipRange, exchangeList))

    _exchangeMap = exchangeMap
    _vipExchangeList = vipExchangeList
    
    ftlog.info('hall_red_packet_exchange._reloadConf ok',
               'exchangeIds=', _exchangeMap.keys())
    

def _onUserReceivedCouponEvent(event):
    if ftlog.is_debug():
        ftlog.debug('hall_red_packet_exchange._onUserReceivedCouponEvent',
                    'userId=', event.userId,
                    'count=', event.count,
                    'source=', event.source)
    
    if event.count > 0:
        clientId = sessiondata.getClientId(event.userId)
        timestamp = pktimestamp.getCurrentTimestamp()
        status = loadUserStatus(event.userId, clientId, timestamp) 
        status.addReceivedItem(event.count, event.source, timestamp)
        saveUserStatus(status)
        datachangenotify.sendDataChangeNotify(HALL_GAMEID, event.userId, 'rpexchange')


def _onConfChanged(event):
    if _inited and event.isChanged('game:9999:red_packet_exchange:0'):
        _reloadConf()


def _initialize():
    from hall.game import TGHall
    global _inited
    if not _inited:
        _inited = True
        _reloadConf()
        pkeventbus.globalEventBus.subscribe(EventConfigure, _onConfChanged)
        TGHall.getEventBus().subscribe(UserReceivedCouponEvent, _onUserReceivedCouponEvent)
        
        if ftlog.is_debug():
            ftlog.debug('hall_red_packet_exchange._initialized ok')


