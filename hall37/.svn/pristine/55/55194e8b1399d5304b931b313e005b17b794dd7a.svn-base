# -*- coding:utf-8 -*-
'''
Created on 2016年4月26日

@author: zhaojiangang
'''
from datetime import datetime
from sre_compile import isstring

import freetime.util.log as ftlog
from hall.entity import datachangenotify
from hall.entity.hallconf import HALL_GAMEID
from poker.entity.biz.content import TYContentRegister
from poker.entity.biz.exceptions import TYBizConfException
from poker.entity.biz.item.item import TYAssetUtils
from poker.entity.biz.message import message
from poker.entity.biz.store.store import TYOrderDeliveryEvent
from poker.entity.configure import configure
from poker.entity.dao import gamedata
from poker.entity.events.tyevent import EventConfigure
import poker.entity.events.tyeventbus as pkeventbus
from poker.util import strutil
import poker.util.timestamp as pktimestamp


class GiftConf(object):
    def __init__(self):
        self.gameIds = None
        # 翻奖内容
        self.giftContent = None
        # 给用户发的消息
        self.mail = None
        # 最大数量
        self.maxCount = None
        self.conf = None
        
    def decodeFromDict(self, d):
        self.gameIds = d.get('gameIds', [])
        self.mail = d.get('mail', '')
        if not isstring(self.mail):
            raise TYBizConfException(d, 'GiftConf.mail must be str')
        self.giftContent = TYContentRegister.decodeFromDict(d.get('content'))
        self.maxCount = d.get('maxCount', -1)
        if not isinstance(self.maxCount, int) or self.maxCount < -1:
            raise TYBizConfException(d, 'GiftConf.maxCount must int >= -1')
        self.conf = d
        return self
    
class Conf(object):
    def __init__(self):
        # 活动开始结束时间
        self.startDT = None
        self.endDT = None
        # key=productId, value=GiftConf
        self.giftMap = {}
        
    def findGiftConf(self, productId):
        return self.giftMap.get(productId)
    
    def decodeFromDict(self, d):
        startTime = d.get('startTime')
        if startTime:
            try:
                self.startDT = datetime.strptime(startTime, '%Y-%m-%d %H:%M:%S')
            except:
                raise TYBizConfException(d, 'GiftConf.startTime must be datetime string with format %Y-%m-%d %H:%M:%S')
        endTime = d.get('endTime')
        if endTime:
            try:
                self.endDT = datetime.strptime(endTime, '%Y-%m-%d %H:%M:%S')
            except:
                raise TYBizConfException(d, 'GiftConf.endTime must be datetime string with format %Y-%m-%d %H:%M:%S')

        if self.startDT and self.endDT and self.endDT < self.startDT:
            raise TYBizConfException(d, 'GiftConf.endTime must ge than startTime')
        
        for giftD in d.get('gifts', []):
            productIds = giftD.get('productIds')
            if not productIds or not isinstance(productIds, list):
                raise TYBizConfException(d, 'GiftConf.productIds must be list')
            gift = GiftConf().decodeFromDict(giftD)
            for productId in productIds:
                self.giftMap[productId] = gift
        return self
    
_inited = False
_conf = None

def _onOrderDelivery(event):
    from hall.entity import hallitem
    nowDT = datetime.now()
    order = event.orderDeliveryResult.order

    if ((_conf.startDT and nowDT < _conf.startDT)
        or (_conf.endDT and nowDT >= _conf.endDT)):
        if ftlog.is_debug():
            ftlog.debug('buy_send_gift._onOrderDelivery outofTime userId=', event.userId,
                        'orderId=', order.orderId,
                        'productId=', order.productId,
                        'nowDT=', nowDT.strftime('%Y-%m-%d %H:%M:%S'),
                        'startDT=', _conf.startDT.strftime('%Y-%m-%d %H:%M:%S'),
                        'endDT=', _conf.endDT.strftime('%Y-%m-%d %H:%M:%S'))
        return
    
    giftConf = _conf.findGiftConf(order.productId)
    if not giftConf:
        if ftlog.is_debug():
            ftlog.debug('buy_send_gift._onOrderDelivery noGiftConf userId=', event.userId,
                        'orderId=', order.orderId,
                        'productId=', order.productId,
                        'orderClientId=', order.clientId)
        return
    
    hallGameId = strutil.getGameIdFromHallClientId(order.clientId)
    if hallGameId not in giftConf.gameIds:
        if ftlog.is_debug():
            ftlog.debug('buy_send_gift._onOrderDelivery notInGameIds userId=', event.userId,
                        'orderId=', order.orderId,
                        'productId=', order.productId,
                        'giftConf=', giftConf.conf,
                        'orderClientId=', order.clientId,
                        'hallGameId=', hallGameId,
                        'gameIds=', giftConf.gameIds)
        return
    
    count = 0
    if giftConf.maxCount >= 0:
        limitD = gamedata.getGameAttrJson(order.userId, hallGameId, 'act.buy_send_gift', {})
        count = limitD.get(order.productId, 0)
        if count + 1 > giftConf.maxCount:
            ftlog.info('buy_send_gift._onOrderDelivery overLimit userId=', event.userId,
                       'orderId=', order.orderId,
                       'productId=', order.productId,
                       'giftConf=', giftConf.conf if giftConf else None,
                       'orderClientId=', order.clientId,
                       'count=', count,
                       'maxCount=', giftConf.maxCount)
            return
        count += 1
        limitD[order.productId] = count
        gamedata.setGameAttr(order.userId, hallGameId, 'act.buy_send_gift', strutil.dumps(limitD))
    
    assetList = None
    if giftConf.giftContent:
        userAssets = hallitem.itemSystem.loadUserAssets(order.userId)
        #def sendContent(self, gameId, content, count, ignoreUnknown, timestamp, eventId, intEventParam):
        assetList = userAssets.sendContent(hallGameId, giftConf.giftContent, 1,
                                           True, pktimestamp.getCurrentTimestamp(),
                                           'ACTIVITY_REWARD',
                                           10043)
    changedDataNames = TYAssetUtils.getChangeDataNames(assetList) if assetList else set()
    
    contentStr = TYAssetUtils.buildContentsString(assetList) if assetList else ''
    if giftConf.mail:
        mail = strutil.replaceParams(giftConf.mail, {'gotContent':contentStr, 'price':order.product.price})
        message.send(hallGameId, message.MESSAGE_TYPE_SYSTEM, order.userId, mail)
        changedDataNames.add('message')
    if changedDataNames:
        datachangenotify.sendDataChangeNotify(HALL_GAMEID, order.userId, changedDataNames)
    ftlog.info('buy_send_gift._onOrderDelivery sendGift userId=', event.userId,
               'orderId=', order.orderId,
               'productId=', order.productId,
               'giftConf=', giftConf.conf if giftConf else None,
               'orderClientId=', order.clientId,
               'count=', count,
               'maxCount=', giftConf.maxCount,
               'assetList=', [(a[0].kindId, a[1]) for a in assetList] if assetList else None)

def _reloadConf():
    global _conf
    d = configure.getGameJson(HALL_GAMEID, 'tmpacts:buy_send_gift', {}, None)
    conf = Conf().decodeFromDict(d)
    _conf = conf
    ftlog.debug('buy_send_gift._reloadConf successed',
               'startTime=', conf.startDT.strftime('%Y-%m-%d %H:%M:%S'),
               'endTime=', conf.endDT.strftime('%Y-%m-%d %H:%M:%S'),
               'productIds=', [(productId, giftConf.gameIds) for productId, giftConf in _conf.giftMap.iteritems()])
    
def _onConfChanged(event):
    if _inited and event.isChanged('game:9999:tmpacts:buy_send_gift'):
        ftlog.debug('buy_send_gift._onConfChanged')
        _reloadConf()
        
def _initialize():
    from hall.game import TGHall
    ftlog.debug('buy_send_gift initialize begin')
    global _inited
    if not _inited:
        _inited = True
        _reloadConf()
        TGHall.getEventBus().subscribe(TYOrderDeliveryEvent, _onOrderDelivery)
        pkeventbus.globalEventBus.subscribe(EventConfigure, _onConfChanged)
    ftlog.debug('buy_send_gift initialize end')
    
    
    