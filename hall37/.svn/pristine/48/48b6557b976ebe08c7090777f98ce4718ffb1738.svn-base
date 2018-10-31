# -*- coding=utf-8
'''
Created on 2015年7月21日

@author: zhaojiangang
'''
from sre_compile import isstring

import freetime.util.log as ftlog
from hall.entity import sdkclient, datachangenotify, hallitem
from hall.entity.hallconf import HALL_GAMEID
from poker.entity.biz.exceptions import TYBizException, TYBizConfException
from poker.entity.biz.message import message as pkmessage
from poker.entity.configure import configure as pkconfigure
from poker.entity.dao import paydata
import poker.entity.dao.daoconst as pkdaoconst
import poker.entity.dao.userchip as pkuserchip
from poker.entity.events.tyevent import EventUserLogin
from poker.util import strutil
from poker.entity.events.tyevent import EventConfigure
import poker.entity.events.tyeventbus as pkeventbus


class CouponItem(object):
    TYPE_PHONE_CARD = 1
    TYPE_ID_CHIP = 4
    VALID_TYPES = set([TYPE_PHONE_CARD, TYPE_ID_CHIP])
    def __init__(self):
        self.couponId = None
        self.couponCount = None
        self.itemCount = None
        self.itemUnits = None
        self.itemName = None
        self.itemType = None
        self.pic = None
        self.tag = None
        self.mailOk = None
        self.mailFail = None
        
    def decodeFromDict(self, d):
        self.couponId = d.get('id')
        if not self.couponId:
            raise TYBizConfException(d, 'couponItem.id must be set')
        self.couponCount = d.get('couponCount')
        if not isinstance(self.couponCount, int) or self.couponCount <= 0:
            raise TYBizConfException(d, 'couponItem.couponCount must be int > 0')
        self.itemCount = d.get('itemCount')
        if not isinstance(self.itemCount, int) or self.itemCount <= 0:
            raise TYBizConfException(d, 'couponItem.itemCount must be int > 0')
        self.itemUnits = d.get('itemUnits', '')
        if not isstring(self.itemUnits):
            raise TYBizConfException(d, 'couponItem.itemUnits must be string')
        self.itemName = d.get('itemName')
        if not isstring(self.itemName) or not self.itemName:
            raise TYBizConfException(d, 'couponItem.itemCount must be not empty string')
        self.itemType = d.get('itemType')
        if self.itemType not in self.VALID_TYPES:
            raise TYBizConfException(d, 'couponItem.itemType must in %s' % (self.VALID_TYPES))
        self.pic = d.get('pic', '')
        if not isstring(self.pic):
            raise TYBizConfException(d, 'couponItem.pic must be string')
        self.tag = d.get('tag', '')
        if not isstring(self.tag):
            raise TYBizConfException(d, 'couponItem.tag must be string')
        self.mailOk = d.get('mailOk', '')
        if not isstring(self.mailOk):
            raise TYBizConfException(d, 'couponItem.mailOk must be string')
        self.mailFail = d.get('mailFail', '')
        if not isstring(self.mailFail):
            raise TYBizConfException(d, 'couponItem.mailFail must be string')
        return self
    
class CouponService(object):    
# key=couponId, value=DizhuCouponItem
    def __init__(self, gameId):
        self._gameId = gameId
        self._couponItemMap = {}
        self._couponItemList = []
        self._qqGroup = ''
        self._instruction = ''
        self._mailWhenCanExchange = ''
        
    def reloadConf(self, conf):
        qqGroup = conf.get('qqGroup', '')
        if not isstring(qqGroup):
            raise TYBizConfException(conf, 'qqGroup must be string')
        instruction = conf.get('instruction', '')
        if not isstring(instruction):
            raise TYBizConfException(conf, 'instruction must be string')
        mailWhenCanExchange = conf.get('mailWhenCanExchange', '')
        if not isstring(mailWhenCanExchange):
            raise TYBizConfException(conf, 'mailWhenCanExchange must be string')
        items = conf.get('items', [])
        if not isinstance(items, list):
            raise TYBizConfException(conf, 'items must be list')
        couponItemList = []
        couponItemMap = {}
        for item in items:
            couponItem = CouponItem().decodeFromDict(item)
            if couponItem.couponId in couponItemMap:
                raise TYBizConfException(item, 'Duplicate couponId %s' % (couponItem.couponId))
            couponItemList.append(couponItem)
            couponItemMap[couponItem.couponId] = couponItem
        
        self._couponItemList = couponItemList
        self._couponItemMap = couponItemMap
        self._qqGroup = qqGroup
        self._instruction = instruction
        self._mailWhenCanExchange = mailWhenCanExchange
        ftlog.debug('CouponService.reloadConf successed gameId=', self.gameId,
                   'couponItems=', self._couponItemMap.keys(),
                   'qqGroup=', self._qqGroup,
                   'instruction=', self._instruction,
                   'mailWhenCanExchange=', self._mailWhenCanExchange)
    
    @property
    def gameId(self):
        return self._gameId
    
    def findCouponItem(self, itemId):
        return self._couponItemMap.get(itemId)
    
    @property
    def qqGroup(self):
        return self._qqGroup
    @property
    def instruction(self):
        return self._instruction
    @property
    def couponItems(self):
        return self._couponItemList
    
    def exchangeCouponItem(self, userId, couponId, **kwargs):
        couponItem = self.findCouponItem(couponId)
        if not couponItem:
            if ftlog.is_debug():
                ftlog.debug('CouponService.exchangeCouponItem userId=', userId,
                            'couponId=', couponId,
                            'kwargs=', kwargs,
                            'gameId=', self.gameId,
                            'coupons=', self._couponItemMap.keys())
            raise TYBizException(-1, 'Not found couponId %s' % (couponId))
        
        if (couponItem.itemType == CouponItem.TYPE_PHONE_CARD
            and not kwargs.get('phone')):
            # 检查chargePhone参数
            raise TYBizException(-1, 'Please input phone number')
        
        # 减奖券
        trueDelta, final = pkuserchip.incrCoupon(userId, self.gameId, -couponItem.couponCount,
                                                 pkdaoconst.CHIP_NOT_ENOUGH_OP_MODE_NONE,
                                                 0, 0, 0)
        if -trueDelta < couponItem.couponCount:
            raise TYBizException(-1, 'Coupon not enough')
        
        costContent = hallitem.buildContent('user:coupon', couponItem.couponCount)
        
        if couponItem.itemType == CouponItem.TYPE_PHONE_CARD:
            phone = kwargs.get('phone')
            isCtyOk = sdkclient.couponCharge(self.gameId, userId, phone, '', '',
                                             couponItem.couponCount, couponItem.itemCount)
            if isCtyOk:
                mail = couponItem.mailOk
            else:
                mail = couponItem.mailFail
            if mail:
                mail = strutil.replaceParams(mail, {
                            'costContent':costContent,
                            'couponCount':str(couponItem.couponCount),
                            'itemCount':str(couponItem.itemCount),
                            'itemName':couponItem.itemName,
                            'phone':phone,
                            'qqGroup':self._qqGroup
                        })
                pkmessage.send(HALL_GAMEID, pkmessage.MESSAGE_TYPE_SYSTEM, userId, mail)
                datachangenotify.sendDataChangeNotify(HALL_GAMEID, userId, 'message')
        elif couponItem.itemType == CouponItem.TYPE_ID_CHIP:
            pkuserchip.incrChip(userId, self.gameId, couponItem.itemCount,
                                pkdaoconst.CHIP_NOT_ENOUGH_OP_MODE_NONE,
                                0, 0, 0)
            mail = couponItem.mailOk
            if mail:
                mail = strutil.replaceParams(mail, {
                            'costContent':costContent,
                            'couponCount':str(couponItem.couponCount),
                            'itemCount':str(couponItem.itemCount),
                            'itemName':couponItem.itemName,
                            'qqGroup':self._qqGroup
                        })
                pkmessage.send(HALL_GAMEID, pkmessage.MESSAGE_TYPE_SYSTEM, userId, mail)
                datachangenotify.sendDataChangeNotify(HALL_GAMEID, userId, 'message')
        return trueDelta, final
    
    def getExchangeRecords(self, userId):
        return paydata.getExchangeRecords(HALL_GAMEID, userId)
        
    def findMinCouponItem(self, itemTypes):
        found = None
        for item in self._couponItemList:
            if (item.itemType in itemTypes
                and (found is None
                     or item.couponCount < found.couponCount)):
                found = item
        return found
    
    def onUserLogin(self, event):
        if not self._mailWhenCanExchange:
            return
        _, clientVer, _ = strutil.parseClientId(event.clientId)
        if clientVer < 3.0:
            return
        if not event.dayFirst or event.gameId != HALL_GAMEID:
            return
        couponItem = self.findMinCouponItem([CouponItem.TYPE_PHONE_CARD])
        if not couponItem:
            return
        userCouponCount = pkuserchip.getCoupon(event.userId)
        if userCouponCount >= couponItem.couponCount:
            pkmessage.send(HALL_GAMEID, pkmessage.MESSAGE_TYPE_SYSTEM, event.userId, self._mailWhenCanExchange)
            datachangenotify.sendDataChangeNotify(self.gameId, event.userId, 'message')
    
_inited = False
couponService = CouponService(HALL_GAMEID)

def _reloadConf():
    global couponService
    conf = pkconfigure.getGameJson(HALL_GAMEID, 'coupon', {})
    couponService.reloadConf(conf)

def _onConfChanged(event):
    if _inited and event.isChanged('game:9999:coupon:0'):
        ftlog.debug('hallcoupon._onConfChanged')
        _reloadConf()

def _initialize():
    ftlog.debug('hallcoupon initialize begin')
    from hall.game import TGHall
    global _inited
    global flipCard
    if not _inited:
        _inited = True
        pkeventbus.globalEventBus.subscribe(EventConfigure, _onConfChanged)
        TGHall.getEventBus().subscribe(EventUserLogin, couponService.onUserLogin)
        _reloadConf()
    ftlog.debug('hallcoupon initialize end')
    

