# -*- coding:utf-8 -*-
'''
Created on 2016年7月4日

@author: zhaojiangang
'''


from sre_compile import isstring

from dizhu.activitynew.activity import ActivityNew
from dizhu.entity.dizhuconf import DIZHU_GAMEID
from dizhu.entity.utils import TimeCycleRegister
import freetime.util.log as ftlog
from hall.entity import hallstore, hallitem, datachangenotify
from hall.game import TGHall
from poker.entity.biz.content import TYContentRegister
from poker.entity.biz.exceptions import TYBizConfException
from poker.entity.biz.item.item import TYAssetUtils
import poker.entity.biz.message.message as pkmessage
from poker.entity.biz.store.store import TYOrderDeliveryEvent, TYProductBuyType
from poker.entity.dao import daobase
from poker.entity.events.tyevent import ChargeNotifyEvent
from poker.util import strutil
from hall.entity.hallconf import HALL_GAMEID


class SendPrizeCountLimitRecord(object):
    '''
    商品购买限制记录，用于记录购买周期内的购买次数
    '''
    def __init__(self, lastSendTimestamp, count):
        # 最后一次送奖时间
        self.lastSendTimestamp = lastSendTimestamp
        # 周期内送奖此时
        self.count = count

class SendPrizeStatus(object):
    def __init__(self, userId, limitRecord=None):
        self.userId = userId
        self.limitRecord = limitRecord
        
    def fromDict(self, d):
        rcd = d.get('rcd')
        self.limitRecord = SendPrizeCountLimitRecord(rcd['lst'], rcd['cnt'])
        return self
    
    def toDict(self):
        return {'rcd':{'lst':self.limitRecord.lastSendTimestamp, 'cnt':self.limitRecord.count}}
    
def loadStatus(userId, actId):
    jstr = daobase.executeUserCmd(userId, 'hget', 'act:%s:%s' % (DIZHU_GAMEID, userId), actId)
    if jstr:
        d = strutil.loads(jstr)
        return SendPrizeStatus(userId).fromDict(d)
    return None

def saveStatus(actId, status):
    d = status.toDict()
    jstr = strutil.dumps(d)
    daobase.executeUserCmd(status.userId, 'hset', 'act:%s:%s' % (DIZHU_GAMEID, status.userId), actId, jstr)

class BuySendPrize(ActivityNew):
    TYPE_ID = 'ddz.act.buy_send_prize'
    def __init__(self):
        super(BuySendPrize, self).__init__()
        self._prizes = None
        self._limitCount = 0
        self._timeCycle = None
        self._mail = None
        self._hallGameIds = None
        
    def init(self):
        TGHall.getEventBus().subscribe(ChargeNotifyEvent, self._onChargeNotify)
        TGHall.getEventBus().subscribe(TYOrderDeliveryEvent, self._onOrderDelivery)
    
    def cleanup(self):
        TGHall.getEventBus().unsubscribe(ChargeNotifyEvent, self._onChargeNotify)
        TGHall.getEventBus().unsubscribe(TYOrderDeliveryEvent, self._onOrderDelivery)
    
    def findPrize(self, gameId, userId, clientId, productId):
        for payOrder, content in self._prizes:
            products = hallstore.findProductListByPayOrder(gameId, userId, clientId, payOrder)
            for product, _ in products:
                if product.productId == productId:
                    return product, content
        return None, None
    
    def _decodeFromDictImpl(self, d):
        self._prizes = []
        self._limitCount = d.get('limitCount', -1)
        if not isinstance(self._limitCount, int) or self._limitCount < -1:
            raise TYBizConfException(d, 'limitCount must be int >= -1')
        self._mail = d.get('mail', '')
        if not isstring(self._mail):
            raise TYBizConfException(d, 'mail must be string')
        self._timeCycle = TimeCycleRegister.decodeFromDict(d.get('limitTimeCycle'))
        for prize in d.get('prizes', []):
            payOrder = prize.get('payOrder')
            if not payOrder or not isinstance(payOrder, dict):
                raise TYBizConfException(prize, 'prize.payOrder must dict')
            content = TYContentRegister.decodeFromDict(prize.get('content'))
            self._prizes.append((payOrder, content))
        self._hallGameIds = d.get('hallGameIds', [])
        if not isinstance(self._hallGameIds, list):
            raise TYBizConfException(d, 'BuySendPrize.hallGameIds must be list')
        for hallGameId in self._hallGameIds:
            if not isinstance(hallGameId, int):
                raise TYBizConfException(d, 'BuySendPrize.hallGameIds must be int list')
        return self
        
    def loadStatus(self, userId, timestamp):
        try:
            status = loadStatus(userId, self.actId)
            if status:
                return self.adjustStatus(status, timestamp)
        except:
            ftlog.warn('BuySendPrize.loadStatus userId=', userId)
        return self.adjustStatus(SendPrizeStatus(userId), timestamp)
        
    def saveStatus(self, status):
        saveStatus(self.actId, status)
        
    def adjustStatus(self, status, timestamp):
        if not status.limitRecord:
            if ftlog.is_debug():
                ftlog.debug('BuySendPrize.adjustStatus limitRecord is None')
            status.limitRecord = SendPrizeCountLimitRecord(timestamp, 0)
        else:
            isSameCycle = self._timeCycle.isSameCycle(status.limitRecord.lastSendTimestamp, timestamp)
            if ftlog.is_debug():
                ftlog.debug('BuySendPrize.adjustStatus isSameCycle=', isSameCycle,
                            'lastSendTimestamp=', status.limitRecord.lastSendTimestamp,
                            'timestamp=', timestamp)
            if not isSameCycle:
                status.limitRecord.lastSendTimestamp = timestamp
                status.limitRecord.count = 0
        return status
    
    def canSendPrize(self, userId, timestamp):
        if self.checkTime(timestamp) != 0:
            return False
        status = self.loadStatus(userId, timestamp)
        return not self._isOverLimit(status, timestamp, 1)
    
    def _isOverLimit(self, status, timestamp, count):
        return self._limitCount >= 0 and status.limitRecord.count + count > self._limitCount
    
    def _onChargeNotify(self, event):
        if ftlog.is_debug():
            ftlog.debug('BuySendPrize._onChargeNotify gameId=', event.gameId,
                        'userId=', event.userId,
                        'clientId=', event.clientId,
                        'productId=', event.productId,
                        'hallGameIds=', self._hallGameIds)
        hallGameId = strutil.getGameIdFromHallClientId(event.clientId)
        if (not self._hallGameIds or hallGameId in self._hallGameIds) and self.checkTime(event.timestamp) == 0:
            product, content = self.findPrize(event.gameId, event.userId, event.clientId, event.productId)
            
            if ftlog.is_debug():
                ftlog.debug('BuySendPrize._onChargeNotify gameId=', event.gameId,
                            'userId=', event.userId,
                            'productId=', event.productId,
                            'hallGameIds=', self._hallGameIds,
                            'prize=', (product, content))
                
            if product and product.buyType == TYProductBuyType.BUY_TYPE_CHARGE:
                self._sendPrizeIfNeed(DIZHU_GAMEID, event.userId, event.clientId, product, content, event.timestamp)
            
    def _onOrderDelivery(self, event):
        if ftlog.is_debug():
            ftlog.debug('BuySendPrize._onOrderDelivery gameId=', event.gameId,
                        'userId=', event.userId,
                        'clientId=', event.orderDeliveryResult.order.clientId,
                        'productId=', event.orderDeliveryResult.order.productId,
                        'hallGameIds=', self._hallGameIds)
        hallGameId = strutil.getGameIdFromHallClientId(event.orderDeliveryResult.order.clientId)
        if (not self._hallGameIds or hallGameId in self._hallGameIds) and self.checkTime(event.timestamp) == 0:
            product, content = self.findPrize(event.gameId, event.userId, event.orderDeliveryResult.order.clientId, event.orderDeliveryResult.order.productId)
            if ftlog.is_debug():
                ftlog.debug('BuySendPrize._onOrderDelivery gameId=', event.gameId,
                            'userId=', event.userId,
                            'productId=', event.orderDeliveryResult.order.productId,
                            'hallGameIds=', self._hallGameIds,
                            'prize=', (product, content))
            if product and product.buyType != TYProductBuyType.BUY_TYPE_CHARGE:
                self._sendPrizeIfNeed(DIZHU_GAMEID, event.userId, event.orderDeliveryResult.order.clientId, product, content, event.timestamp)
        
    def _sendPrizeIfNeed(self, gameId, userId, clientId, product, prizeContent, timestamp):
        # 加载活动数据
        status = self.loadStatus(userId, timestamp)
        if self._isOverLimit(status, timestamp, 1):
            if ftlog.is_debug():
                ftlog.debug('BuySendPrize._sendPrizeIfNeed OverLimit gameId=', gameId,
                            'userId=', userId,
                            'clientId=', clientId,
                            'productId=', product.productId,
                            'count=', status.limitRecord.count,
                            'limitCount=', self._limitCount)
            return
    
        status.limitRecord.count += 1
        status.limitRecord.lastSendTimestamp = timestamp
        self.saveStatus(status)
            
        # 检查是否已经发过奖励
        userAssets = hallitem.itemSystem.loadUserAssets(userId)
        assetList = userAssets.sendContent(gameId, prizeContent, 1, True, timestamp, 'ACTIVITY_REWARD', self.intActId)
        
        changed = TYAssetUtils.getChangeDataNames(assetList)
        changed.add('promotion_loc')
        datachangenotify.sendDataChangeNotify(gameId, userId, changed)
        
        if self._mail:
            contents = TYAssetUtils.buildContentsString(assetList)
            mail = strutil.replaceParams(self._mail, {'rewardContent':contents})
            pkmessage.sendPrivate(HALL_GAMEID, userId, 0, mail)
            
        ftlog.info('BuySendPrize._sendPrizeIfNeed gameId=', gameId,
                   'userId=', userId,
                   'clientId=', clientId,
                   'productId=', product.productId,
                   'buyType=', product.buyType,
                   'actId=', self.actId,
                   'intActId=', self.intActId,
                   'sendAssets=', [(at[0].kindId, at[1]) for at in assetList],
                   'timestamp=', timestamp,
                   'count=', status.limitRecord.count)

