# -*- coding=utf-8
'''
Created on 2015年7月1日

@author: zhaojiangang
'''

from datetime import datetime
from sre_compile import isstring
import struct

import freetime.util.log as ftlog
from hall.entity import hallconf, datachangenotify, hallled
from hall.entity.hallconf import HALL_GAMEID
from hall.entity.todotask import TodoTaskHelper, TodoTaskPayOrder, \
    TodoTaskShowRewards
from hall.game import TGHall
from poker.entity.biz.content import TYContentRegister, TYEmptyContent, \
    TYContentItem, TYContentUtils
from poker.entity.biz.exceptions import TYBizConfException, TYBizException
from poker.entity.biz.item.dao import TYItemDataDao
from poker.entity.biz.item.exceptions import TYItemException, \
    TYItemConfException, TYItemActionParamException
from poker.entity.biz.item.item import TYItemSystem, TYItemSystemImpl, \
    TYItemActionCondition, TYItemAction, TYItemUnits, TYItemData, TYItem, TYItemKind, \
    TYAssetKind, TYItemActionConditionRegister, TYItemActionRegister, \
    TYItemUnitsRegister, TYItemKindRegister, TYAssetKindRegister, TYAssetKindItem, \
    TYItemActionResult, TYAssetUtils
import poker.entity.biz.message.message as pkmessage
from poker.entity.dao import sessiondata, itemdata, userdata, daobase, gamedata
import poker.entity.dao.daobase as pkdao
import poker.entity.dao.daoconst as pkdaoconst
import poker.entity.dao.gamedata as pkgamedata
import poker.entity.dao.userchip as pkuserchip
import poker.entity.dao.userdata as pkuserdata
from poker.entity.events.tyevent import EventConfigure, UserEvent
import poker.entity.events.tyeventbus as pkeventbus
from poker.util import strutil, keywords
import poker.util.timestamp as pktimestamp
from poker.protocol import runcmd
from hall.entity.inviter_shop import TYAssetKindDifangFangka

class TYItemCannotSaleException(TYItemException):
    def __init__(self, item):
        super(TYItemCannotSaleException, self).__init__(-1, '不能出售给系统')
        self.item = item

    def __str__(self):
        return '%s:%s %s:%s' % (self.errorCode, self.message, self.item.itemId, self.item.kindId)
    
    def __unicode__(self):
        return u'%s:%s %s:%s' % (self.errorCode, self.message, self.item.itemId, self.item.kindId)

class TYItemCannotPresentException(TYItemException):
    def __init__(self, item, message='不能赠送'):
        super(TYItemCannotPresentException, self).__init__(-1, message)
        self.item = item

    def __str__(self):
        return '%s:%s %s:%s' % (self.errorCode, self.message, self.item.itemId, self.item.kindId)
    
    def __unicode__(self):
        return u'%s:%s %s:%s' % (self.errorCode, self.message, self.item.itemId, self.item.kindId)

class TYItemAlreadyDiedException(TYItemException):
    def __init__(self, item):
        super(TYItemAlreadyDiedException, self).__init__(-1, '该道具已经过期或者损坏')
        self.item = item

    def __str__(self):
        return '%s:%s %s:%s' % (self.errorCode, self.message, self.item.itemId, self.item.kindId)
    
    def __unicode__(self):
        return u'%s:%s %s:%s' % (self.errorCode, self.message, self.item.itemId, self.item.kindId)

class TYItemCannotRepairException(TYItemException):
    def __init__(self, item):
        super(TYItemCannotRepairException, self).__init__(-1, '该道具不能被修复')
        self.item = item

    def __str__(self):
        return '%s:%s %s:%s' % (self.errorCode, self.message, self.item.itemId, self.item.kindId)
    
    def __unicode__(self):
        return u'%s:%s %s:%s' % (self.errorCode, self.message, self.item.itemId, self.item.kindId)

class TYItemCannotDropException(TYItemException):
    def __init__(self, item):
        super(TYItemCannotDropException, self).__init__(-1, '该道具不能被丢弃')
        self.item = item

    def __str__(self):
        return '%s:%s %s:%s' % (self.errorCode, self.message, self.item.itemId, self.item.kindId)
    
    def __unicode__(self):
        return u'%s:%s %s:%s' % (self.errorCode, self.message, self.item.itemId, self.item.kindId)


class TYItemCannotAssembleException(TYItemException):
    def __init__(self, item):
        super(TYItemCannotAssembleException, self).__init__(-1, '该道具不能组装')
        self.item = item

    def __str__(self):
        return '%s:%s %s:%s' % (self.errorCode, self.message, self.item.itemId, self.item.kindId)
    
    def __unicode__(self):
        return u'%s:%s %s:%s' % (self.errorCode, self.message, self.item.itemId, self.item.kindId)

class TYItemKindAssembleNotEnoughException(TYItemException):
    def __init__(self, itemKind, notEnoughItemKind, required, actually):
        super(TYItemKindAssembleNotEnoughException, self).__init__(-1, '%s数量不足' % (notEnoughItemKind.displayName))
        self.itemKind = itemKind
        self.notEnoughItemKind = notEnoughItemKind
        self.required = required
        self.actually = actually

    def __str__(self):
        return '%s:%s %s %s' % (self.errorCode, self.message, self.itemKind.kindId, self.notEnoughItemKind.kindId)
    
    def __unicode__(self):
        return u'%s:%s %s %s' % (self.errorCode, self.message, self.itemKind.kindId, self.notEnoughItemKind.kindId)

class TYItemNotEnoughException(TYItemException):
    def __init__(self, item):
        super(TYItemNotEnoughException, self).__init__(-1, '道具数量不足')
        self.item = item
        
    def __str__(self):
        return '%s:%s %s:%s' % (self.errorCode, self.message, self.item.itemId, self.item.kindId)
    
    def __unicode__(self):
        return u'%s:%s %s:%s' % (self.errorCode, self.message, self.item.itemId, self.item.kindId)
    
class TYItemAlreadyExpiresException(TYItemException):
    def __init__(self, item):
        super(TYItemAlreadyExpiresException, self).__init__(-1, '道具已经过期')
        self.item = item
        
    def __str__(self):
        return '%s:%s %s:%s' % (self.errorCode, self.message, self.item.itemId, self.item.kindId)
    
    def __unicode__(self):
        return u'%s:%s %s:%s' % (self.errorCode, self.message, self.item.itemId, self.item.kindId)

class TYItemAlreadyWoreException(TYItemException):
    def __init__(self, item):
        super(TYItemAlreadyWoreException, self).__init__(-1, '道具已经佩戴')
        self.item = item
        
    def __str__(self):
        return '%s:%s %s:%s' % (self.errorCode, self.message, self.item.itemId, self.item.kindId)
    
    def __unicode__(self):
        return u'%s:%s %s:%s' % (self.errorCode, self.message, self.item.itemId, self.item.kindId)

class TYItemAlreadyOnException(TYItemException):
    def __init__(self, item):
        super(TYItemAlreadyOnException, self).__init__(-1, '道具已经开启')
        self.item = item
        
    def __str__(self):
        return '%s:%s %s:%s' % (self.errorCode, self.message, self.item.itemId, self.item.kindId)
    
    def __unicode__(self):
        return u'%s:%s %s:%s' % (self.errorCode, self.message, self.item.itemId, self.item.kindId)

class TYItemAlreadyOffException(TYItemException):
    def __init__(self, item):
        super(TYItemAlreadyOffException, self).__init__(-1, '道具已经关闭')
        self.item = item
        
    def __str__(self):
        return '%s:%s %s:%s' % (self.errorCode, self.message, self.item.itemId, self.item.kindId)
    
    def __unicode__(self):
        return u'%s:%s %s:%s' % (self.errorCode, self.message, self.item.itemId, self.item.kindId)


class TYItemNotWoreException(TYItemException):
    def __init__(self, item):
        super(TYItemNotWoreException, self).__init__(-1, '道具没有佩戴')
        self.item = item
        
    def __str__(self):
        return '%s:%s %s:%s' % (self.errorCode, self.message, self.item.itemId, self.item.kindId)
    
    def __unicode__(self):
        return u'%s:%s %s:%s' % (self.errorCode, self.message, self.item.itemId, self.item.kindId)


class TYItemAlreadyCheckinException(TYItemException):
    def __init__(self, item):
        super(TYItemAlreadyCheckinException, self).__init__(-1, '道具已经过签到')
        self.item = item
        
    def __str__(self):
        return '%s:%s %s:%s' % (self.errorCode, self.message, self.item.itemId, self.item.kindId)
    
    def __unicode__(self):
        return u'%s:%s %s:%s' % (self.errorCode, self.message, self.item.itemId, self.item.kindId)

class TYItemAlreadyAuditException(TYItemException):
    def __init__(self, item):
        super(TYItemAlreadyAuditException, self).__init__(-1, '审核中')
        self.item = item
        
    def __str__(self):
        return '%s:%s %s:%s' % (self.errorCode, self.message, self.item.itemId, self.item.kindId)
    
    def __unicode__(self):
        return u'%s:%s %s:%s' % (self.errorCode, self.message, self.item.itemId, self.item.kindId)

class TYItemBindings(object):
    def __init__(self, items, params):
        self.items = items
        self.params = params
        
    def getParam(self, paramName, defVal=None):
        return self.params.get(paramName, defVal)
     
    @property
    def failure(self):
        return self.getParam('failure', '')
    
    @classmethod
    def decodeFromDict(cls, d):
        params = d.get('params', {})
        if not isinstance(params, dict):
            raise TYItemConfException(d, 'TYItemBindings.params must be dict')
        items = TYContentItem.decodeList(d.get('items', []))
        return TYItemBindings(items, params)
        
    # 处理items
    def consume(self, gameId, item, userAssets, timestamp, eventId, intEventParam,
                roomId=0, tableId=0, roundId=0, param01=0, param02=0):
        for contentItem in self.items:
            assetKind, consumeCount, final = userAssets.consumeAsset(gameId,
                                                                     contentItem.assetKindId,
                                                                     contentItem.count,
                                                                     timestamp,
                                                                     eventId,
                                                                     intEventParam,
                                                                     roomId=roomId,
                                                                     tableId=tableId,
                                                                     roundId=roundId,
                                                                     param01=param01,
                                                                     param02=param02)
            if consumeCount == contentItem.count:
                return True, (assetKind, consumeCount, final)
        return False, None
        
class TYItemBindingsException(TYItemException):
    def __init__(self, item, itemBindings):
        super(TYItemBindingsException, self).__init__(-1, itemBindings.failure)
        self.item = item
        self.itemBindings = itemBindings

    def __str__(self):
        return '%s:%s %s:%s %s' % (self.errorCode, self.message, self.item.itemId, self.item.kindId, [(ci.assetKindId, ci.count) for ci in self.itemBindings.items])
    
    def __unicode__(self):
        return u'%s:%s %s:%s %s' % (self.errorCode, self.message, self.item.itemId, self.item.kindId, [(ci.assetKindId, ci.count) for ci in self.itemBindings.items])

class TYItemActionConditionLeastOncePay(TYItemActionCondition):
    '''
    至少支付一次的条件
    '''
    TYPE_ID = 'PAY.LEAST_ONCE'
    def __init__(self):
        super(TYItemActionConditionLeastOncePay, self).__init__()
        
    def _conform(self, gameId, userAssets, item, timestamp, params):
        return pkuserdata.getAttr(userAssets.userId, 'payCount') > 0

class ItemActionConditionGameDashifenLevel(TYItemActionCondition):
    '''
    大师分等级
    '''
    TYPE_ID = 'item.action.cond.game.dashifen.level'
    def __init__(self):
        super(ItemActionConditionGameDashifenLevel, self).__init__()
        self.minLevel = None
        self.maxLevel = None
        self.gameId = None

    def _conform(self, gameId, userAssets, item, timestamp, params):
        from poker.entity.game.game import TYGame
        userId = userAssets.userId
        clientId = sessiondata.getClientId(userId)
        dashifen = TYGame(self.gameId).getDaShiFen(userId, clientId)
        level = dashifen.get('level', 0) if dashifen else 0
        
        if ftlog.is_debug():
            ftlog.debug('ItemActionConditionGameDashifenLevel._conform gameId=', gameId,
                        'userId=', userId,
                        'clientId=', clientId,
                        'selfGameId=', self.gameId,
                        'dashifen=', dashifen,
                        'level=', level,
                        'minLevel=', self.minLevel,
                        'maxLevel=', self.maxLevel)
            
        return (self.minLevel == -1 or level >= self.minLevel) \
            and (self.maxLevel == -1 or level < self.maxLevel)
          
    def decodeFromDict(self, d):
        super(ItemActionConditionGameDashifenLevel, self).decodeFromDict(d)
        # minLevel
        self.minLevel = self.params.get('minLevel', -1)
        if not isinstance(self.minLevel, int) or self.minLevel < -1:
            raise TYBizConfException(self.params, 'UserConditionGameDashifen.params.minLevel must be int >= -1')
        
        # maxLevel
        self.maxLevel = self.params.get('maxLevel', -1)
        if not isinstance(self.maxLevel, int) or self.maxLevel < -1:
            raise TYBizConfException(self.params, 'UserConditionGameDashifen..maxLevel must be int >= -1')
        if self.maxLevel != -1 and self.maxLevel < self.minLevel:
            raise TYBizConfException(self.params, 'UserConditionGameDashifen.params.maxLevel must >= minLevel')
        
        # gameId
        self.gameId = self.params.get('gameId', 6)
        if not isinstance(self.gameId, int) or self.gameId < 0:
            raise TYBizConfException(self.params, 'UserConditionGameDashifen.params.gameId must >= 0')
        return self
        
class TYItemActionConditionLeastOnceAlipay(TYItemActionCondition):
    '''
    至少使用过支付宝支付一次的条件
    '''
    TYPE_ID = 'ALIPAY.LEAST_ONCE'
    def __init__(self):
        super(TYItemActionConditionLeastOnceAlipay, self).__init__()
        
    def _conform(self, gameId, userAssets, item, timestamp, params):
        return pkuserdata.getAttr(userAssets.userId, 'used_alipay') > 0
    
class TYItemActionConditionGotDaysRange(TYItemActionCondition):
    '''
    获取该道具达到多少天
    '''
    def __init__(self, start, end=None):
        super(TYItemActionConditionGotDaysRange, self).__init__()
        assert(start is not None and start >= 0)
        assert(end is None or end >= start)
        self._start = start
        self._end = end

    def _conform(self, gameId, userAssets, item, timestamp, params):
        nowTimestamp = pktimestamp.getDayStartTimestamp(timestamp)
        gotTimestamp = pktimestamp.getDayStartTimestamp(item.createTime)
        gotDays = (nowTimestamp - gotTimestamp) / 86400
        return gotDays >= self._start if not self._end else \
            gotDays >= self._start and gotDays <= self._end
    
class TYItemActionConditionGotSecondDaysLater(TYItemActionConditionGotDaysRange):
    TYPE_ID = 'ITEM.GOT.SECOND_DAYS_LATER'
    def __init__(self):
        super(TYItemActionConditionGotSecondDaysLater, self).__init__(1)

class TYItemActionConditionBindPhoneCheck(TYItemActionCondition):
    '''
    检查是否留过手机号
    '''
    TYPE_ID = 'BINDPHONE.CHECK.IF_NEED_BIND_PHONE'
    def __init__(self):
        super(TYItemActionConditionBindPhoneCheck, self).__init__()
        
    def _conform(self, gameId, userAssets, item, timestamp, params):
        bindPhone = params.get('bindPhone', 0)
        if bindPhone:
            bindMobile = pkuserdata.getAttr(userAssets.userId, 'bindMobile')
            if not bindMobile:
                return False
            bindMobile = str(bindMobile)
            params['phoneNumber'] = bindMobile
        return True

class TYItemActionConditionBindWeixin(TYItemActionCondition):
    '''
    检查是否留过手机号
    '''
    TYPE_ID = 'item.action.cond.bind.weixin'
    def __init__(self):
        super(TYItemActionConditionBindWeixin, self).__init__()
        
    def _conform(self, gameId, userAssets, item, timestamp, params):
        wxOpenId = userdata.getAttr(userAssets.userId, 'wxOpenId')
        return False if not wxOpenId else True
        
class TYItemActionConditionCanOpenFlag(TYItemActionCondition):
    '''
    检查是否留过手机号
    '''
    TYPE_ID = 'item.action.cond.canOpenFlag'
    def __init__(self):
        super(TYItemActionConditionCanOpenFlag, self).__init__()
        
    def _conform(self, gameId, userAssets, item, timestamp, params):
        flagName = 'item.open.flag:%s' % (item.kindId)
        return gamedata.getGameAttrInt(userAssets.userId, HALL_GAMEID, flagName) == 1

class TYItemActionConditionTimeRange(TYItemActionCondition):
    '''
    某个时间段内
    '''
    TYPE_ID = 'item.action.cond.timeRange'
    def __init__(self):
        super(TYItemActionConditionTimeRange, self).__init__()
        self.startTime = -1
        self.stopTime = -1
        
    def _conform(self, gameId, userAssets, item, timestamp, params):
        ret = ((self.startTime < 0 or timestamp >= self.startTime)
               and (self.stopTime < 0 or timestamp < self.stopTime))
        if ftlog.is_debug():
            ftlog.debug('TYItemActionConditionTimeRange._conform',
                        'gameId=', gameId,
                        'userId=', userAssets.userId,
                        'itemId=', item.itemId,
                        'itemKindId=', item.kindId,
                        'timestamp=', timestamp,
                        'startTime=', self.startTime,
                        'stopTime=', self.stopTime,
                        'ret=', ret)
        return ret

    def decodeFromDict(self, d):
        super(TYItemActionConditionTimeRange, self).decodeFromDict(d)
        startTime = self.params.get('startTime')
        if startTime is not None:
            try:
                self.startTime = pktimestamp.timestrToTimestamp(startTime, '%Y-%m-%d %H:%M:%S')
            except:
                raise TYBizConfException(startTime, 'TYItemActionConditionTimeRange.params.startTime must be timestr')
        stopTime = self.params.get('stopTime')
        if stopTime is not None:
            try:
                self.stopTime = pktimestamp.timestrToTimestamp(stopTime, '%Y-%m-%d %H:%M:%S')
            except:
                raise TYBizConfException(stopTime, 'TYItemActionConditionTimeRange.params.stopTime must be timestr')
        return self

class TYAssembleItemEvent(UserEvent):
    def __init__(self, gameId, userId, newItem, consumedItemList):
        super(TYAssembleItemEvent, self).__init__(userId, gameId)
        self.newItem = newItem
        self.consumedItemList = consumedItemList
        
class TYSaleItemEvent(UserEvent):
    def __init__(self, gameId, userId, saledItem, gotAssetList):
        super(TYSaleItemEvent, self).__init__(userId, gameId)
        self.saledItem = saledItem
        self.gotAssetList = gotAssetList
     
class TYRepairItemEvent(UserEvent):
    def __init__(self, gameId, userId, repairdItem, consumeAssetList):
        super(TYRepairItemEvent, self).__init__(userId, gameId)
        self.repairdItem = repairdItem
        self.consumeAssetList = consumeAssetList
        
class TYOpenItemEvent(UserEvent):
    def __init__(self, gameId, userId, item, gotAssetList):
        super(TYOpenItemEvent, self).__init__(userId, gameId)
        self.item = item
        self.gotAssetList = gotAssetList
        
class TYWearItemEvent(UserEvent):
    def __init__(self, gameId, userId, item, unweardItemList):
        super(TYWearItemEvent, self).__init__(userId, gameId)
        self.item = item
        self.unweardItemList = unweardItemList
        
class TYItemActionRepairResult(TYItemActionResult):
    def __init__(self, action, item, message, consumeAssetList):
        super(TYItemActionRepairResult, self).__init__(action, item, message)
        self.consumeAssetList = consumeAssetList
        
class TYUnwearItemEvent(UserEvent):
    def __init__(self, gameId, userId, item):
        super(TYUnwearItemEvent, self).__init__(userId, gameId)
        self.item = item
        
def buildMailAndMessageAndChanged(gameId, userAssets, action, assetList, replaceParams):
    changed = TYAssetUtils.getChangeDataNames(assetList) if assetList else set()
    mail = strutil.replaceParams(action.mail, replaceParams)
    message = strutil.replaceParams(action.message, replaceParams)
    if mail:
        pkmessage.send(gameId, pkmessage.MESSAGE_TYPE_PRIVATE if gameId == 60 else pkmessage.MESSAGE_TYPE_SYSTEM, userAssets.userId, mail)
        changed.add('message')
    changed.discard('item')
    return mail, message, changed

def _handleMailAndMessageAndChanged(gameId, userAssets, action, assetList, replaceParams, extChanged=None):
    mail, message, changed = buildMailAndMessageAndChanged(gameId, userAssets, action, assetList, replaceParams)
    if isstring(extChanged):
        extChanged = [extChanged]
    if changed is None:
        changed = extChanged
    elif extChanged:
        changed.update(extChanged)
    datachangenotify.sendDataChangeNotify(gameId, userAssets.userId, changed)
    return mail, message, changed

class TYItemActionRepair(TYItemAction):
    TYPE_ID = 'common.repair'
    def __init__(self):
        super(TYItemActionRepair, self).__init__()
        self.repairContentItem = None
        self.repairAddUnitsCount = None
            
    def canDo(self, userBag, item, timestamp):
        '''
        判断是否可以对item执行本动作
        '''
        return item.isDied(timestamp)
    
    def _doActionImpl(self, gameId, userAssets, item, timestamp, params):
        # 执行具体的动作，此时各种条件已经检查完毕
        if not item.isDied(timestamp):
            raise TYItemCannotRepairException(item)
    
        userBag = userAssets.getUserBag()
        assetList = userAssets.consumeContentItemList(gameId, [self.repairContentItem], True, timestamp,
                                                      'REPAIRE_ITEM', item.kindId)
        
        repairAddUnitsCount = self.repairAddUnitsCount if item.itemKind.singleMode else 1
        userBag.addItemUnits(gameId, item, repairAddUnitsCount, timestamp,
                             'REPAIRE_ITEM', item.kindId)
        
        consumeContent = TYAssetUtils.buildContentsString(assetList)
        replaceParams = {'consumeContent':consumeContent, 'item':item.itemKind.displayName}
        _mail, message, _changed = _handleMailAndMessageAndChanged(gameId, userAssets, self, assetList, replaceParams)
        
        TGHall.getEventBus().publishEvent(TYRepairItemEvent(gameId, userBag.userId,
                                                            item, assetList))
        return TYItemActionRepairResult(self, item, message, assetList)

    def _decodeFromDictImpl(self, d):
        '''
        用于子类解析自己特有的数据
        '''
        repairContent = d.get('repairContent')
        if not repairContent:
            raise TYItemConfException(d, 'TYItemActionRepair.repairContent must be set')
        self.repairContentItem = TYContentItem.decodeFromDict(repairContent)
        if self.repairContentItem.count <= 0:
            raise TYItemConfException(d, 'TYItemActionSale.repairContent.count must > 0')
        self.repairAddUnitsCount = d.get('repairAddUnitsCount')
        if not isinstance(self.repairAddUnitsCount, int) or self.repairAddUnitsCount <= 0:
            raise TYItemConfException(d, 'TYItemActionRepair.repairAddUnitsCount must be int > 0')
  
class TYDropItemEvent(UserEvent):
    def __init__(self, gameId, userId, item):
        super(TYDropItemEvent, self).__init__(userId, gameId)
        self.item = item
              
class TYItemActionDropResult(TYItemActionResult):
    def __init__(self, action, item, message):
        super(TYItemActionDropResult, self).__init__(action, item, message)
        
class TYItemActionDrop(TYItemAction):
    TYPE_ID = 'common.drop'
    def __init__(self):
        super(TYItemActionDrop, self).__init__()

    def canDo(self, userBag, item, timestamp):
        '''
        判断是否可以对item执行本动作
        '''
        return item.isDied(timestamp)
    
    def _doActionImpl(self, gameId, userAssets, item, timestamp, params):
        # 执行具体的动作，此时各种条件已经检查完毕
        if not item.isDied(timestamp):
            raise TYItemCannotDropException(item)
    
        userBag = userAssets.getUserBag()
        userBag.removeItem(gameId, item, timestamp, 'DROP_ITEM', item.kindId)
        
        replaceParams = {'item':item.itemKind.displayName}
        _mail, message, _changed = _handleMailAndMessageAndChanged(gameId, userAssets, self, None, replaceParams)

        TGHall.getEventBus().publishEvent(TYDropItemEvent(gameId, userBag.userId, item))
        return TYItemActionDropResult(self, item, message)

    def _decodeFromDictImpl(self, d):
        '''
        用于子类解析自己特有的数据
        '''
        pass
        
class TYItemActionSaleResult(TYItemActionResult):
    def __init__(self, action, item, message, gotAssetList):
        super(TYItemActionSaleResult, self).__init__(action, item, message)
        self.gotAssetList = gotAssetList

class TYItemActionSale(TYItemAction):
    TYPE_ID = 'common.sale'
    SINGLE_MODE_NAME_TYPE_LIST = [('count', int)]
    def __init__(self):
        super(TYItemActionSale, self).__init__()
        self.contentItem = None
        self.contentAssetKind = None
        
    def canDo(self, userBag, item, timestamp):
        '''
        判断是否可以对item执行本动作
        '''
        return not item.isDied(timestamp) and item.visibleInBag(timestamp)
    
    def getParamNameTypeList(self):
        if self.itemKind.singleMode:
            return self.SINGLE_MODE_NAME_TYPE_LIST
        return None
    
    def _initWhenLoaded(self, itemKind, itemKindMap, assetKindMap):
        # 当配置解析工作完成后调用，用于初始化配置中一些itemKind相关的数据
        assetKind = assetKindMap.get(self.contentItem.assetKindId)
        if not assetKind:
            raise TYItemConfException(self.conf, 'TYItemActionSale.saleContent assetKindId Unknown %s' % (self.contentItem.assetKindId))
        self.assetKind = assetKind
        if not self._inputParams:
            self._inputParams = {
                'type':'countSale',
                'desc':'出售可获得：'
            }
        self._inputParams['price'] = self.contentItem.count
        self._inputParams['name'] = assetKind.displayName
        self._inputParams['units'] = assetKind.units
            
    def _doActionImpl(self, gameId, userAssets, item, timestamp, params):
        # 执行具体的动作，此时各种条件已经检查完毕
        userBag = userAssets.getUserBag()
        if item.isDied(timestamp):
            raise TYItemAlreadyDiedException(item)
        
        saleItem = ''
        if item.itemKind.singleMode:
            unitsCount = int(params.get('count'))
            consumeCount = userBag.consumeItemUnits(gameId, item, unitsCount, timestamp,
                                                    'SALE_ITEM', item.kindId)
            if consumeCount < unitsCount:
                raise TYItemNotEnoughException(item)
        
            assetItem = userAssets.addAsset(gameId, self.contentItem.assetKindId,
                                            self.contentItem.count * unitsCount, timestamp,
                                            'SALE_ITEM', item.kindId)
            saleItem = TYAssetUtils.buildItemContent((item.itemKind, unitsCount, 0))
        else:
            userBag.removeItem(gameId, item, timestamp, 'SALE_ITEM', item.kindId)
            assetItem = userAssets.addAsset(gameId, self.contentItem.assetKindId,
                                            self.contentItem.count, timestamp,
                                            'SALE_ITEM', item.kindId)
            saleItem = item.itemKind.displayName

        assetList = [assetItem]
        gotContent = TYAssetUtils.buildContent(assetItem)
        replaceParams = {'saleItem':saleItem, 'gotContent':gotContent}
        _mail, message, _changed = _handleMailAndMessageAndChanged(gameId, userAssets, self, assetList, replaceParams)
        TGHall.getEventBus().publishEvent(TYSaleItemEvent(gameId, userBag.userId, item, assetList))
        return TYItemActionSaleResult(self, item, message, assetList)

    def _decodeFromDictImpl(self, d):
        '''
        用于子类解析自己特有的数据
        '''
        saleContent = d.get('saleContent')
        if not saleContent:
            raise TYItemConfException(d, 'TYItemActionSale.saleContent must be set')
        self.contentItem = TYContentItem.decodeFromDict(saleContent)
        if self.contentItem.count <= 0:
            raise TYItemConfException(d, 'TYItemActionSale.saleContent.count must > 0')
        
class TYItemActionSendLed(TYItemAction):
    TYPE_ID = 'common.sendLed'
    def __init__(self):
        super(TYItemActionSendLed, self).__init__()
        self.scope = None
        self.gameId = None
        
    def canDo(self, userBag, item, timestamp):
        '''
        判断是否可以对item执行本动作
        '''
        return not item.isDied(timestamp)
    
    
    def _initWhenLoaded(self, itemKind, itemKindMap, assetKindMap):
        # 当配置解析工作完成后调用，用于初始化配置中一些itemKind相关的数据
        if ftlog.is_debug() :
            ftlog.debug('TYItemActionSendLed _initWhenLoaded')
            
    def _doActionImpl(self, gameId, userAssets, item, timestamp, params):
        # 执行具体的动作，此时各种条件已经检查完毕
        
        if ftlog.is_debug() :
            ftlog.debug('TYItemActionSendLed _doActionImpl gameId', gameId
                        ,'text =', params['text'])
        userBag = userAssets.getUserBag()
        #检验是否含有非法字符
        text = keywords.replace(params['text'])
        ledMsg = '玩家%d说'%userBag.userId +text
        #发送LED，ismgr改为1，调高大喇叭LED优先级
        hallled.sendLed(self.gameId, ledMsg, 1, self.scope)
        #消耗道具
        ftlog.debug('_doActionImpl over')
        userBag.consumeItemUnits(gameId, item, 1, timestamp, 'ITEM_USE', item.kindId)
        if ftlog.is_debug() :
            ftlog.debug('TYItemActionSendLed _doActionImpl gameId', gameId
                        ,'text =', ledMsg
                        ,'userId =', userBag.userId
                        ,'scope =', self.scope)

    def _decodeFromDictImpl(self, d):
        '''
        用于子类解析自己特有的数据
        '''
        self.scope = d.get('scope', 'global')
        self.gameId = d.get('gameId', HALL_GAMEID)
    

class TYItemActionSendMsg(TYItemAction):
    TYPE_ID = 'common.sendMsg'
    def __init__(self):
        super(TYItemActionSendMsg, self).__init__()
        
    def canDo(self, userBag, item, timestamp):
        '''
        判断是否可以对item执行本动作
        '''
        return not item.isDied(timestamp)

    def _initWhenLoaded(self, itemKind, itemKindMap, assetKindMap):
        # 当配置解析工作完成后调用，用于初始化配置中一些itemKind相关的数据
        if ftlog.is_debug() :
            ftlog.debug('TYItemActionSendMsg _initWhenLoaded')
            
    def checkParams(self, gameId, userAssets, item, timestamp, params):
        phoneNumber = None
        useBindPhone = params.get('bindPhone', 0)
        if not useBindPhone:
            # 如果没有bindPhone，则需要检查phoneNumber
            phoneNumber = params.get('phoneNumber')
            if not phoneNumber:
                raise TYItemActionParamException(self, '请输入手机号码')
            
    def _doActionImpl(self, gameId, userAssets, item, timestamp, params):
        # 执行具体的动作，此时各种条件已经检查完毕
        if ftlog.is_debug() :
            ftlog.debug('TYItemActionSendMsg _doActionImpl gameId', gameId)
            
        #手机号码的处理
        useBindPhone = params.get('bindPhone', 0)
        phoneNumber = None
        if not useBindPhone:
            # 如果没有bindPhone，则需要检查phoneNumber
            phoneNumber = params.get('phoneNumber')
            if not phoneNumber:
                raise TYItemActionParamException(self, '请输入手机号码')
        else:
            #获取绑定的手机号
            temp = pkuserdata.getAttrs(userAssets.getUserBag().userId, ['bindMobile'])
            phoneNumber = temp[0]
            if not phoneNumber:
                raise TYItemActionParamException(self, '您绑定的手机号状态有误，请联系客服电话4008098000')
            
        '''
        #获取配置
        conf = hallconf.getExchangeItemConf()
        ftlog.debug('TYItemActionSendMsg.._doActionImpl..conf', conf)
        #不同的走不同的配置池
        tempConf = conf.get('item:%d'%item.kindId)
        if int(daobase.executeMixCmd('llen',itemList)) == 0 :
            for k in tempConf.get('add',[]):
                daobase.executeMixCmd('lpush',itemList,k)
        ftlog.debug('TYItemActionSendMsg.._doActionImpl..list', daobase.executeMixCmd('llen',itemList))
        '''
        itemList = 'item:%d'%item.kindId + 'AllList'
        itemFinishList = 'item:%d'%item.kindId + 'FinishList'
        itemMap = 'item:%d'%item.kindId + 'Map'
        #处理数据
        if int(daobase.executeMixCmd('llen',itemList)) > 0 :
            exCode = daobase.executeMixCmd('rpoplpush',itemList,itemFinishList)
        else:
            exCode = False
            
        ftlog.info('TYItemActionSendMsg.._doActionImpl..useBindPhone =', useBindPhone
                    ,'gameId =', gameId
                    ,'userId =', userAssets.getUserBag().userId
                    ,'item =', item.kindId
                    ,'timestamp =',timestamp
                    ,'exCode =', exCode)
        
        paramsTemp = {
            'userId':userAssets.getUserBag().userId,
            'phoneNumber':phoneNumber,
            'time':timestamp,
            'exCode':exCode
        }
        
        daobase.executeMixCmd('hset',itemMap,'userId:%d'%userAssets.getUserBag().userId,paramsTemp)
        #短信发送
        from hall.entity import sdkclient
        if not exCode:
            content = '非常抱歉的通知您，兑换码已无库存，请联系客服电话4008098000'
            sendToMsg = '非常抱歉的通知您，兑换码已无库存，请联系客服电话4008098000'
        else :
            replaceParams = {'item':item.itemKind.displayName}
            mail,message,_ = buildMailAndMessageAndChanged(gameId, userAssets, self, None, replaceParams)
            content = mail + exCode + message
            sendToMsg = mail + exCode + '。'
        
        sdkclient.sendExCodeToUser(userAssets.getUserBag().userId, content, phoneNumber)
        #将消息下发到用户的消息列表中
        from poker.entity.biz.message import message
        message.send(gameId, message.MESSAGE_TYPE_SYSTEM, userAssets.getUserBag().userId, sendToMsg)
        #消耗item
        userBag = userAssets.getUserBag()
        userBag.removeItem(gameId, item, timestamp, 'ITEM_USE', 0)
    
    def _decodeFromDictImpl(self, d):
        '''
        用于子类解析自己特有的数据
        '''
        pass
        
class TYItemActionAssembleResult(TYItemActionResult):
    def __init__(self, action, item, message, consumedItemList, assembledItem):
        super(TYItemActionAssembleResult, self).__init__(action, item, message)
        self.consumedItemList = consumedItemList
        self.assembledItem = assembledItem
        
class TYItemActionAssemble(TYItemAction):
    TYPE_ID = 'common.assemble'
    def __init__(self):
        super(TYItemActionAssemble, self).__init__()
        
    def canDo(self, userBag, item, timestamp):
        '''
        判断是否可以对item执行本动作
        '''
        for component in item.itemKind.componentOf.componentList:
            actually = userBag.calcTotalUnitsCount(component.itemKind, timestamp)
            if actually < component.count:
                return False
        return True
    
    def _doActionImpl(self, gameId, userAssets, item, timestamp, params):
        # 执行具体的动作，此时各种条件已经检查完毕
        if not item.itemKind.componentOf:
            raise TYItemCannotAssembleException(item)
        
        userBag = userAssets.getUserBag() 
        for component in item.itemKind.componentOf.componentList:
            actually = userBag.calcTotalUnitsCount(component.itemKind, timestamp)
            if actually < component.count:
                raise TYItemKindAssembleNotEnoughException(item.itemKind.componentOf, component.itemKind, component.count, actually)
        
        consumedItemList = []
        for component in item.itemKind.componentOf.componentList:
            consumeCount = userBag.consumeUnitsCountByKind(gameId, component.itemKind, component.count, timestamp,
                                                           'ASSEMBLE_ITEM', item.itemKind.componentOf.kindId)
            if consumeCount < component.count:
                # TODO 打印错误日志，可能是没有锁住该用户的资源
                actually = userBag.calcTotalUnitsCount(component.itemKind, timestamp)
                raise TYItemKindAssembleNotEnoughException(item.itemKind.componentOf, component.itemKind, component.count, actually)
            else:
                consumedItemList.append((component.itemKind, consumeCount,
                                        userBag.calcTotalUnitsCount(component.itemKind, timestamp)))
        # 生成新道具
        assembledItem = userBag.addItemUnitsByKind(gameId, item.itemKind.componentOf, 1, timestamp, 0,
                                                   'ASSEMBLE_ITEM', item.itemKind.componentOf.kindId)[0]
        consumeContent = TYAssetUtils.buildItemContentsString(consumedItemList)
        replaceParams = {'assembledItem':assembledItem.itemKind.displayName, 'consumeContent':consumeContent}
        _mail, message, _changed = _handleMailAndMessageAndChanged(gameId, userAssets, self, None, replaceParams)
        event = TYAssembleItemEvent(gameId, userBag.userId, assembledItem, consumedItemList)
        TGHall.getEventBus().publishEvent(event)
        
        return TYItemActionAssembleResult(self, item, message, consumedItemList, assembledItem)
    
class TYItemActionPresentResult(TYItemActionResult):
    def __init__(self, action, item, message, targetUserId, count=1):
        super(TYItemActionPresentResult, self).__init__(action, item, message)
        self.targetUserId = targetUserId
        self.count = count
        
class TYItemActionPresent(TYItemAction):
    TYPE_ID = 'common.present'
    SINGLE_MODE_NAME_TYPE_LIST = [('count', int), ('userId', int)]
    NOT_SINGLE_MODE_NAME_TYPE_LIST = [('userId', int)]
    def __init__(self):
        super(TYItemActionPresent, self).__init__()
        self.receiveMail = None
        
    def canDo(self, userBag, item, timestamp):
        '''
        判断是否可以对item执行本动作
        '''
        return not item.isDied(timestamp) and item.original == 1
    
    def getParamNameTypeList(self):
        if self.itemKind.singleMode:
            return self.SINGLE_MODE_NAME_TYPE_LIST
        return self.NOT_SINGLE_MODE_NAME_TYPE_LIST
    
    def _initWhenLoaded(self, itemKind, itemKindMap, assetKindMap):
        # 当配置解析工作完成后调用，用于初始化配置中一些itemKind相关的数据
        if not self._inputParams:
            if self.itemKind.singleMode: 
                self._inputParams = {
                    'type':'countAndUserId'
                }
            else:
                self._inputParams = {
                    'type':'userId'
                }
    
    def _decodeFromDictImpl(self, d):
        self.receiveMail = d.get('receiveMail', '')
        if not isstring(self.receiveMail):
            raise TYBizConfException(d, 'TYItemActionPresent.receiveMail must be string')
        
    def _doActionImpl(self, gameId, userAssets, item, timestamp, params):
        # 执行具体的动作，此时各种条件已经检查完毕
        targetUserId = params.get('userId')
        if targetUserId == userAssets.userId:
            raise TYItemException(-1, '不能赠送给自己')

        if not userdata.checkUserData(targetUserId):
            raise TYItemException(-1, '被赠送账号不存在')

        from hall.servers.util.rpc import user_remote
        
        userBag = userAssets.getUserBag()
        if item.itemKind.singleMode:
            count = int(params.get('count'))
            consumeCount = userBag.consumeUnitsCountByKind(gameId, item.itemKind, count,
                                                           timestamp, 'PRESENT_ITEM', targetUserId)
            if consumeCount < count:
                raise TYItemNotEnoughException(item)
            
            ftlog.info('TYItemActionPresent._doActionImpl gameId=', gameId,
                       'userId=', userAssets.userId,
                       'targetUserId=', targetUserId,
                       'itemId=', item.itemId,
                       'itemKindId=', item.kindId,
                       'count=', count)
            
            presentItem = TYAssetUtils.buildItemContent((item.itemKind, count, 0))
            replaceParams = {
                'presentItem':presentItem,
                'fromUserId':str(userAssets.userId),
                'targetUserId':str(targetUserId)
            }
            
            _mail, message, _changed = _handleMailAndMessageAndChanged(gameId, userAssets, self, None, replaceParams)
            receiveMail = strutil.replaceParams(self.receiveMail, replaceParams)
            user_remote.presentItemByUnitsCount(gameId, targetUserId, userAssets.userId, item.kindId, count, receiveMail)
            return TYItemActionPresentResult(self, item, message, targetUserId, count)
        else:
            if item.original != 1:
                raise TYItemCannotPresentException(item, '不是原装的不能被赠送')
            itemData = item.encodeToItemData()
            itemDataDict = itemData.toDict()
            userBag.removeItem(gameId, item, timestamp, 'PRESENT_ITEM', targetUserId)
            
            ftlog.info('TYItemActionPresent._doActionImpl gameId=', gameId,
                       'userId=', userAssets.userId,
                       'targetUserId=', targetUserId,
                       'itemId=', item.itemId,
                       'itemKindId=', item.kindId,
                       'removed=', 1)
            
            presentItem = TYAssetUtils.buildItemContent((item.itemKind, 1, 0))
            replaceParams = {
                'presentItem':presentItem,
                'fromUserId':str(userAssets.userId),
                'targetUserId':str(targetUserId)
            }
            _mail, message, _changed = _handleMailAndMessageAndChanged(gameId, userAssets, self, None, replaceParams)
            receiveMail = strutil.replaceParams(self.receiveMail, replaceParams)
            user_remote.presentItem(gameId, targetUserId, userAssets.userId, itemDataDict, receiveMail)
            return TYItemActionPresentResult(self, item, message, targetUserId, 1)
        
class TYItemActionOpenResult(TYItemActionResult):
    def __init__(self, action, item, message, gotAssetList, todotask):
        super(TYItemActionOpenResult, self).__init__(action, item, message, todotask)
        self.gotAssetList = gotAssetList
        
class TYItemActionBoxOpen(TYItemAction):
    TYPE_ID = 'common.box.open'
    def __init__(self):
        super(TYItemActionBoxOpen, self).__init__()
        self.itemBindings = None
        self.contentList = None
        self.nextItemKindId = None
        self.nextItemKind = None
        
    def canDo(self, userBag, item, timestamp):
        '''
        判断是否可以对item执行本动作
        '''
        return not item.isDied(timestamp)
    
    def _initWhenLoaded(self, itemKind, itemKindMap, assetKindMap):
        if self.nextItemKindId:
            nextItemKind = itemKindMap.get(self.nextItemKindId)
            if not nextItemKind:
                raise TYItemConfException(self.conf, 'TYItemActionBoxOpen._initWhenLoad unknown nextItemKind %s' % (self.nextItemKindId))
            self.nextItemKind = nextItemKind
            
    def _doActionImpl(self, gameId, userAssets, item, timestamp, params):
        assert(isinstance(item, TYBoxItem))
        
        userBag = userAssets.getUserBag()

        if item.isDied(timestamp):
            raise TYItemNotEnoughException(item)
        
        if self.itemBindings:
            ok, _assetTuple = self.itemBindings.consume(gameId, item, userAssets, timestamp, 'ITEM_USE', item.kindId)
            if not ok:
                raise TYItemBindingsException(item, self.itemBindings)
            
        if not item.itemKind.singleMode:
            # 互斥型道具打开时直接删除
            userBag.removeItem(gameId, item, timestamp, 'ITEM_USE', item.kindId)
        else:
            item.openTimes += 1
            item.original = 0
            
            # 保存item
            userBag.consumeItemUnits(gameId, item, 1, timestamp, 'ITEM_USE', item.kindId)
            
        assetItemList = userAssets.sendContent(gameId, self._getContent(item), 1, True,
                                               timestamp, 'ITEM_USE', item.kindId)
        rewardsList = []
        for assetItemTuple in assetItemList:
            '''
            0 - assetItem
            1 - count
            2 - final
            '''
            assetItem = assetItemTuple[0]
            reward = {}
            reward['name'] = assetItem.displayName
            reward['pic'] = assetItem.pic
            reward['count'] = assetItemTuple[1]
            rewardsList.append(reward)
            
        if ftlog.is_debug():
            ftlog.debug('TYItemActionBoxOpen.doAction rewardsList: ', rewardsList)
        
        rewardTodotask = None
        if rewardsList:
            rewardTodotask = TodoTaskShowRewards(rewardsList) 
        
        # 如果需要生成下一个道具
        if self.nextItemKind:
            userBag.addItemUnitsByKind(gameId, self.nextItemKind, 1, timestamp, 0,
                                       'ITEM_USE', item.kindId)
        
        # 提示文案
        gotContent = TYAssetUtils.buildContentsString(assetItemList)
        # 提示消息替换参数
        replaceParams = {'item':item.itemKind.displayName, 'gotContent':gotContent}
        _mail, message, _changed = _handleMailAndMessageAndChanged(gameId, userAssets, self, assetItemList, replaceParams)
        
        TGHall.getEventBus().publishEvent(TYOpenItemEvent(gameId, userBag.userId, item, assetItemList))
        return TYItemActionOpenResult(self, item, message, assetItemList, rewardTodotask)

    def _decodeFromDictImpl(self, d):
        bindings = d.get('bindings')
        if bindings:
            self.itemBindings = TYItemBindings.decodeFromDict(bindings)
        self.contentList = self._decodeContents(d)
        self.nextItemKindId = d.get('nextItemKindId')
        if self.nextItemKindId is not None and not isinstance(self.nextItemKindId, int):
            raise TYItemConfException(d, 'TYItemActionBoxOpen.nextItemKindId must be int')
        
    def _decodeContents(self, d):
        '''
        从d中解析数据
        '''
        contentList = []
        contents = d.get('contents', [])
        if not isinstance(contents, list):
            raise TYItemConfException(d, 'TYItemActionBoxOpen.contents must be not empty list')
        for contentConf in contents:
            openTimes = contentConf.get('openTimes', {'start':0, 'stop':-1})
            if not isinstance(openTimes, dict):
                raise TYItemConfException(contentConf, 'TYItemActionBoxOpen.openTimes must be dict')
            startTimes = openTimes.get('start')
            stopTimes = openTimes.get('stop')
            if (not isinstance(startTimes, int)
                or not isinstance(stopTimes, int)):
                raise TYItemConfException(openTimes, 'TYItemActionBoxOpen.openTimes.start end must be int')
            if stopTimes >= 0 and stopTimes < startTimes:
                raise TYItemConfException(openTimes, 'TYItemActionBoxOpen.openTimes.stop must ge start')
            content = TYContentRegister.decodeFromDict(contentConf)
            contentList.append((startTimes, stopTimes, content))
        return contentList
    
    def _getContent(self, item):
        openTimes = max(item.openTimes - 1, 0)
        if self.contentList:
            for startTimes, stopTimes, content in self.contentList:
                if ((startTimes < 0 or openTimes >= startTimes)
                    and (stopTimes < 0 or openTimes <= stopTimes)):
                    return content
        return TYEmptyContent()
    
class TYItemActionWearResult(TYItemActionResult):
    def __init__(self, action, item, message, unweardItemList):
        super(TYItemActionWearResult, self).__init__(action, item, message)
        self.unweardItemList = unweardItemList
        
class TYItemActionDecroationWear(TYItemAction):
    TYPE_ID = 'common.decroation.wear'
    def __init__(self):
        super(TYItemActionDecroationWear, self).__init__()
         
    def canDo(self, userBag, item, timestamp):
        '''
        判断是否可以对item执行本动作
        '''
        return not item.isDied(timestamp) and not item.isWore
    
    def _doActionImpl(self, gameId, userAssets, item, timestamp, params):
        assert(isinstance(item, TYDecroationItem))
        
        if item.isDied(timestamp):
            raise TYItemAlreadyExpiresException(item)
        if item.isWore:
            raise TYItemAlreadyWoreException(item)
        
        # 设置为
        item.isWore = 1
        item.original = 0
        
        # 取消佩戴所有互斥的装饰品
        unweardItemList = []
        userBag = userAssets.getUserBag()
        
        decroationItemList = userBag.getAllTypeItem(TYDecroationItem)
        for decroationItem in decroationItemList:
            if (decroationItem != item
                and decroationItem.isWore
                and (item.itemKind.masks & decroationItem.itemKind.masks)):
                decroationItem.isWore = 0
                unweardItemList.append(decroationItem)
                userBag.updateItem(gameId, decroationItem, timestamp)
                ftlog.debug('ItemActionWear._doActionImpl gameId=', gameId,
                            'userId=', userAssets.userId,
                            'itemId=', item.itemId,
                            'unwearItemId=', decroationItem.itemId)
        userBag.updateItem(gameId, item, timestamp)
        replaceParams = {'item':item.itemKind.displayName}
        _mail, message, _changed = _handleMailAndMessageAndChanged(gameId, userAssets, self, None, replaceParams, 'decoration')
        TGHall.getEventBus().publishEvent(TYWearItemEvent(gameId, userBag.userId, item, unweardItemList))
        return TYItemActionWearResult(self, item, message, unweardItemList)
             
    def _decodeFromDictImpl(self, d):
        pass
      
class TYItemActionUnwearResult(TYItemActionResult):
    def __init__(self, action, item, message):
        super(TYItemActionUnwearResult, self).__init__(action, item, message)
        
class TYItemActionDecroationUnwear(TYItemAction):
    TYPE_ID = 'common.decroation.unwear'
    def __init__(self):
        super(TYItemActionDecroationUnwear, self).__init__()
         
    def canDo(self, userBag, item, timestamp):
        '''
        判断是否可以对item执行本动作
        '''
        return not item.isDied(timestamp) and item.isWore
    
    def _doActionImpl(self, gameId, userAssets, item, timestamp, params):
        assert(isinstance(item, TYDecroationItem))
        if item.isDied(timestamp):
            raise TYItemAlreadyExpiresException(item)
        if not item.isWore:
            raise TYItemNotWoreException(item)
        item.isWore = 0
        item.original = 0
        userAssets.getUserBag().updateItem(gameId, item, timestamp)
        replaceParams = {'item':item.itemKind.displayName}
        _mail, message, _changed = _handleMailAndMessageAndChanged(gameId, userAssets, self, None, replaceParams, 'decoration')
        TGHall.getEventBus().publishEvent(TYUnwearItemEvent(gameId, userAssets.userId, item))
        return TYItemActionUnwearResult(self, item, message)
     
    def _decodeFromDictImpl(self, d):
        pass
    
class TYSwitchTurnOnItemEvent(UserEvent):
    def __init__(self, gameId, userId, item):
        super(TYSwitchTurnOnItemEvent, self).__init__(userId, gameId)
        self.item = item
 
class TYSwitchTurnOffItemEvent(UserEvent):
    def __init__(self, gameId, userId, item):
        super(TYSwitchTurnOffItemEvent, self).__init__(userId, gameId)
        self.item = item
               
class TYItemActionTurnOnResult(TYItemActionResult):
    def __init__(self, action, item, message):
        super(TYItemActionTurnOnResult, self).__init__(action, item, message)
        
class TYItemActionTurnOffResult(TYItemActionResult):
    def __init__(self, action, item, message):
        super(TYItemActionTurnOffResult, self).__init__(action, item, message)
        
class TYItemActionSwitchTurnOn(TYItemAction):
    TYPE_ID = 'common.switch.turnOn'
    def __init__(self):
        super(TYItemActionSwitchTurnOn, self).__init__()
         
    def canDo(self, userBag, item, timestamp):
        '''
        判断是否可以对item执行本动作
        '''
        return not item.isDied(timestamp) and not item.isOn
    
    def _doActionImpl(self, gameId, userAssets, item, timestamp, params):
        assert(isinstance(item, TYSwitchItem))
        
        if item.isDied(timestamp):
            raise TYItemAlreadyExpiresException(item)
        if item.isOn:
            raise TYItemAlreadyOnException(item)
        
        # 设置为
        item.isOn = 1
        item.original = 0
        
        userBag = userAssets.getUserBag()
        userBag.updateItem(gameId, item, timestamp)
        
        replaceParams = {'item':item.itemKind.displayName}
        _mail, message, _changed = _handleMailAndMessageAndChanged(gameId, userAssets, self, None, replaceParams)
        TGHall.getEventBus().publishEvent(TYSwitchTurnOnItemEvent(gameId, userBag.userId, item))
        return TYItemActionTurnOnResult(self, item, message)
             
    def _decodeFromDictImpl(self, d):
        pass

class TYItemActionSwitchTurnOff(TYItemAction):
    TYPE_ID = 'common.switch.turnOff'
    def __init__(self):
        super(TYItemActionSwitchTurnOff, self).__init__()

    def canDo(self, userBag, item, timestamp):
        '''
        判断是否可以对item执行本动作
        '''
        return not item.isDied(timestamp) and item.isOn
    
    def _doActionImpl(self, gameId, userAssets, item, timestamp, params):
        assert(isinstance(item, TYSwitchItem))
        
        if item.isExpires(timestamp):
            raise TYItemAlreadyExpiresException(item)
        if not item.isOn:
            raise TYItemAlreadyOffException(item)
        
        # 设置为
        item.isOn = 0
        item.original = 0
        
        userBag = userAssets.getUserBag()
        userBag.updateItem(gameId, item, timestamp)
        
        replaceParams = {'item':item.itemKind.displayName}
        _mail, message, _changed = _handleMailAndMessageAndChanged(gameId, userAssets, self, None, replaceParams)
        TGHall.getEventBus().publishEvent(TYSwitchTurnOffItemEvent(gameId, userBag.userId, item))
        return TYItemActionTurnOffResult(self, item, message)

    def _decodeFromDictImpl(self, d):
        pass

class TYItemActionCheckinResult(TYItemActionResult):
    def __init__(self, action, item, message, gotAssetList):
        super(TYItemActionCheckinResult, self).__init__(action, item, message)
        self.gotAssetList = gotAssetList
            
class TYCheckinItemEvent(UserEvent):
    def __init__(self, gameId, userId, item, gotAssetList):
        super(TYCheckinItemEvent, self).__init__(userId, gameId)
        self.item = item
        self.gotAssetList = gotAssetList
        
class TYItemActionCheckin(TYItemAction):
    TYPE_ID = 'common.checkin'
    def __init__(self):
        super(TYItemActionCheckin, self).__init__()
        self.content = None
        
    def canDo(self, userBag, item, timestamp):
        '''
        判断是否可以对item执行本动作
        '''
        return False
    
    def _doActionImpl(self, gameId, userAssets, item, timestamp, params):
        from hall.entity import hallsubmember
        assert(isinstance(item, TYMemberCardItem))
        userBag = userAssets.getUserBag()

        if item.isExpires(timestamp):
            raise TYItemAlreadyExpiresException(item)

        if not item.canCheckin(timestamp):
            raise TYItemAlreadyCheckinException(item)
        
        # 保存item
        item.checkinTime = timestamp
        userBag.updateItem(gameId, item, timestamp)
        
        # 发放开出的奖品
        # 检查是否是订阅会员
        status = hallsubmember.loadSubMemberStatus(userAssets.userId)
        eventId = 'ITEM_USE' if status.isSubExpires(datetime.fromtimestamp(timestamp)) else 'SUB_MEMBER_CHECKIN'
        assetItemList = userAssets.sendContent(gameId, self.content, 1, True,
                                               timestamp, eventId, item.kindId)
        
        gotContent = TYAssetUtils.buildContentsString(assetItemList)
        replaceParams = {'gotContent':gotContent}
        _mail, message, _changed = _handleMailAndMessageAndChanged(gameId, userAssets, self, assetItemList, replaceParams)
        
        ftlog.debug('TYItemActionCheckin._doActionImpl gameId=', gameId,
                   'userId=', userAssets.userId,
                   'itemId=', item.itemId,
                   'itemKindId=', item.kindId,
                   'gotContent=', gotContent,
                   'mail=', _mail,
                   'message=', message,
                   'changed=', _changed)
        TGHall.getEventBus().publishEvent(TYCheckinItemEvent(gameId, userBag.userId, item, assetItemList))
        return TYItemActionCheckinResult(self, item, message, assetItemList)

    def _decodeFromDictImpl(self, d):
        content = d.get('content')
        if not content:
            raise TYItemConfException(d, 'TYItemActionCheckin.content must be set')
        self.content = TYContentRegister.decodeFromDict(content)
    
class TYItemActionBuy(TYItemAction):
    TYPE_ID = 'common.buyProduct'
    def __init__(self):
        super(TYItemActionBuy, self).__init__()
        self.payOrder = None
        self.doConditionList = None
        
    def canDo(self, userBag, item, timestamp):
        '''
        判断是否可以对item执行本动作
        '''
        from hall.entity import hallstore
        if ftlog.is_debug():
            ftlog.debug('TYItemActionBuy.canDo userId=', userBag.userId,
                        'itemId=', item.itemId,
                        'kindId=', item.kindId,
                        'payOrder=', self.payOrder,
                        'doConditionList=', self.doConditionList)
        if not self.payOrder:
            return False
        clientId = sessiondata.getClientId(userBag.userId)
        for cond in self.doConditionList:
            if not cond.check(HALL_GAMEID, userBag.userId, clientId, timestamp):
                return False
        product, _ = hallstore.findProductByPayOrder(HALL_GAMEID, userBag.userId, clientId, self.payOrder)
        if not product:
            return False
        if ftlog.is_debug():
            ftlog.debug('TYItemActionBuy.canDo userId=', userBag.userId,
                        'itemId=', item.itemId,
                        'kindId=', item.kindId,
                        'payOrder=', self.payOrder,
                        'doConditionList=', self.doConditionList,
                        'ret=', True)
        return True
    
    def _doActionImpl(self, gameId, userAssets, item, timestamp, params):
        from hall.entity import hallstore
        if ftlog.is_debug():
            ftlog.debug('TYItemActionBuy._doActionImpl gameId=', gameId,
                        'userId=', userAssets.userId,
                        'itemId=', item.itemId,
                        'kindId=', item.kindId,
                        'payOrder=', self.payOrder,
                        'doConditionList=', self.doConditionList,
                        'params=', params)
            
        clientId = sessiondata.getClientId(userAssets.userId)
        product, _ = hallstore.findProductByPayOrder(HALL_GAMEID, userAssets.userId, clientId, self.payOrder)
        if product:
            TodoTaskHelper.sendTodoTask(gameId, userAssets.userId, TodoTaskPayOrder(product))
        return TYItemActionResult(self, item, '')
    
    def _decodeFromDictImpl(self, d):
        from hall.entity.hallusercond import UserConditionRegister
        self.payOrder = d.get('payOrder')
        if not self.payOrder:
            raise TYItemConfException(d, 'TYItemActionBuy.payOrder must be dict')
        self.doConditionList = UserConditionRegister.decodeList(d.get('doConditionList', []))
    
class TYItemUnitsCount(TYItemUnits):
    TYPE_ID = 'common.count'
    def __init__(self):
        super(TYItemUnitsCount, self).__init__()
        self._seconds = 0
        
    def isTiming(self):
        return False
    
    def add(self, item, count, timestamp):
        assert(count >= 0)
        if count > 0:
            if item.remaining < 0:
                item.remaining = 0
            item.remaining += count
            if self._seconds > 0:
                if item.expiresTime <= 0:
                    item.expiresTime = timestamp
                item.expiresTime += count * self._seconds
    
    def balance(self, item, timestamp):
        '''
        剩余多少个单位
        '''
        return item.remaining
    
    def consume(self, item, count, timestamp):
        '''
        给item消耗count个单位
        '''
        assert(count >= 0)
        if count > 0:
            if item.remaining >= count:
                item.remaining -= count
                return count
        return 0
    
    def forceConsume(self, item, count, timestamp):
        '''
        强制消耗count个单位，如果不足则消耗所有
        '''
        assert(count >= 0)
        consumeCount = min(item.remaining, count)
        if consumeCount > 0:
            item.remaining -= consumeCount
        return consumeCount
    
class TYItemUnitsNatureDay(TYItemUnits):
    TYPE_ID = 'common.day.nature'
    def __init__(self):
        super(TYItemUnitsNatureDay, self).__init__()
        
    def isTiming(self):
        return True
    
    def add(self, item, count, timestamp):
        assert(count >= 0)
        if count > 0:
            if item.expiresTime <= 0 or item.expiresTime <= timestamp:
                # 从购买当天开始计算，按照自然天，如果是23:59分购买1天则有效期就1秒
                item.expiresTime = pktimestamp.getDayStartTimestamp(timestamp)
            item.expiresTime += count * 86400

    def balance(self, item, timestamp):
        '''
        剩余多少个单位
        '''
        expiresTime = item.expiresTime
        if expiresTime <= 0:
            expiresTime = timestamp
        return max(0, (pktimestamp.getDayStartTimestamp(expiresTime)
                       - pktimestamp.getDayStartTimestamp(timestamp)) / 86400)
    
    def consume(self, item, count, timestamp):
        '''
        给item消耗count个单位
        '''
        assert(count >= 0)
        if count > 0:
            balance = self.balance(item, timestamp)
            if balance >= count:
                item.expiresTime -= count * 86400
                if item.expiresTime - timestamp < 86400:
                    item.expiresTime = timestamp
                return count
        return 0
    
    def forceConsume(self, item, count, timestamp):
        '''
        强制消耗count个单位，如果不足则消耗所有
        '''
        assert(count >= 0)
        if count > 0:
            balance = self.balance(item, timestamp)
            consumeCount = min(balance, count)
            if consumeCount > 0:
                item.expiresTime -= count * 86400
                if item.expiresTime < timestamp:
                    item.expiresTime = timestamp
            return consumeCount
        return 0
    
class TYItemUnitsDay(TYItemUnits):
    TYPE_ID = 'common.day'
    def __init__(self):
        super(TYItemUnitsDay, self).__init__()
        
    def isTiming(self):
        return True
    
    def add(self, item, count, timestamp):
        assert(count >= 0)
        if count > 0:
            if item.expiresTime <= 0 or item.expiresTime <= timestamp:
                # 初始化时从购买第二天开始计时
                item.expiresTime = pktimestamp.getDayStartTimestamp(timestamp) + 86400
            item.expiresTime += count * 86400

    def balance(self, item, timestamp):
        '''
        剩余多少个单位
        '''
        expiresTime = item.expiresTime
        if expiresTime <= 0:
            expiresTime = timestamp
        return max(0, (pktimestamp.getDayStartTimestamp(expiresTime)
                       - pktimestamp.getDayStartTimestamp(timestamp + 86400 - 1)) / 86400)
    
    def consume(self, item, count, timestamp):
        '''
        给item消耗count个单位
        '''
        assert(count >= 0)
        if count > 0:
            balance = self.balance(item, timestamp)
            if balance >= count:
                item.expiresTime -= count * 86400
                if item.expiresTime - timestamp < 86400:
                    item.expiresTime = timestamp 
                return count
        return 0
    
    def forceConsume(self, item, count, timestamp):
        '''
        强制消耗count个单位，如果不足则消耗所有
        '''
        assert(count >= 0)
        if count > 0:
            balance = self.balance(item, timestamp)
            consumeCount = min(balance, count)
            if consumeCount > 0:
                item.expiresTime -= count * 86400
                if item.expiresTime < timestamp:
                    item.expiresTime = timestamp
            return consumeCount
        return 0
             
class TYItemUnitsCurrentDay(TYItemUnits):
    TYPE_ID = 'common.currentday'

    def __init__(self):
        super(TYItemUnitsCurrentDay, self).__init__()

    def isTiming(self):
        return True

    def add(self, item, count, timestamp):
        assert (count == 1)
        assert (not item.itemKind.singleMode)
        item.expiresTime = pktimestamp.getDayStartTimestamp(timestamp) + 86400

    def balance(self, item, timestamp):
        '''
        剩余多少个单位
        '''
        assert (not item.itemKind.singleMode)
        return 1

    def consume(self, item, count, timestamp):
        '''
        给item消耗count个单位
        '''
        assert (not item.itemKind.singleMode)
        return 0

    def forceConsume(self, item, count, timestamp):
        '''
        强制消耗count个单位，如果不足则消耗所有
        '''
        assert (count >= 0)
        return 0

    def _decodeFromDictImpl(self, d):
        # 子类解析自己特有的数据
        pass

class TYItemUnitsCountNDay(TYItemUnits):
    TYPE_ID = 'common.count.nday'
    def __init__(self):
        super(TYItemUnitsCountNDay, self).__init__()
        self.nday = None
         
    def isTiming(self):
        return True
    
    def add(self, item, count, timestamp):
        assert(count == 1)
        assert(not item.itemKind.singleMode)
        item.expiresTime = pktimestamp.getDayStartTimestamp(timestamp) + 86400
        item.expiresTime += self.nday * 86400
 
    def balance(self, item, timestamp):
        '''
        剩余多少个单位
        '''
        assert(not item.itemKind.singleMode)
        return 1
     
    def consume(self, item, count, timestamp):
        '''
        给item消耗count个单位
        '''
        assert(not item.itemKind.singleMode)
        return 0
     
    def forceConsume(self, item, count, timestamp):
        '''
        强制消耗count个单位，如果不足则消耗所有
        '''
        assert(count >= 0)
        return 0
     
    def _decodeFromDictImpl(self, d):
        # 子类解析自己特有的数据
        self.nday = d.get('nday')
        if not isinstance(self.nday, int) or self.nday <= 0:
            raise TYBizConfException(d, 'TYItemUnitsNDay.nday must be int > 0')
         
class TYItemUnitsHour(TYItemUnits):
    TYPE_ID = 'common.hour'
    def __init__(self):
        super(TYItemUnitsHour, self).__init__()
        
    def isTiming(self):
        return True

    def add(self, item, count, timestamp):
        assert(count >= 0)
        if count > 0:
            if item.expiresTime <= 0 or item.expiresTime < timestamp:
                # 初始化时从下一个小时开始
                item.expiresTime = pktimestamp.getHourStartTimestamp(timestamp) + 3600
            item.expiresTime += count * 3600

    def balance(self, item, timestamp):
        '''
        剩余多少个单位
        '''
        expiresTime = item.expiresTime
        if expiresTime <= 0:
            expiresTime = timestamp
        return max(0, (pktimestamp.getHourStartTimestamp(expiresTime)
                       - pktimestamp.getHourStartTimestamp(timestamp)) / 3600)
    
    def consume(self, item, count, timestamp):
        '''
        给item消耗count个单位
        '''
        assert(count >= 0)
        if count > 0:
            balance = self.balance(item, timestamp)
            consumeCount = min(balance, count)
            if consumeCount > 0:
                item.expiresTime -= count * 3600
                if item.expiresTime < timestamp:
                    item.expiresTime = timestamp
            return consumeCount
        return 0
    
    def forceConsume(self, item, count, timestamp):
        '''
        强制消耗count个单位，如果不足则消耗所有
        '''
        assert(count >= 0)
        if count >= 0:
            balance = self.balance(item, timestamp)
            consumeCount = min(balance, count)
            if consumeCount > 0:
                item.expiresTime -= count * 3600
                if item.expiresTime < timestamp:
                    item.expiresTime = timestamp
            return consumeCount
        return 0
    
class TYItemUnitsTime(TYItemUnits):
    TYPE_ID = 'common.time'
    def __init__(self):
        super(TYItemUnitsTime, self).__init__()
        self._seconds = None
        
    def isTiming(self):
        return True
    
    def add(self, item, count, timestamp):
        assert(count >= 0)
        if count > 0:
            if item.expiresTime <= 0 or item.expiresTime < timestamp:
                item.expiresTime = timestamp
            item.expiresTime += count * self._seconds
    
    def balance(self, item, timestamp):
        '''
        剩余多少个单位
        '''
        expiresTime = item.expiresTime
        if expiresTime <= 0:
            expiresTime = timestamp
        return max(0, (expiresTime - timestamp) / self._seconds)
    
    def consume(self, item, count, timestamp):
        '''
        给item消耗count个单位
        '''
        assert(count >= 0)
        if count > 0:
            balance = self.balance(item, timestamp)
            consumeCount = min(balance, count)
            if consumeCount > 0:
                item.expiresTime -= count * self._seconds
                if item.expiresTime < timestamp:
                    item.expiresTime = timestamp
            return consumeCount
        return 0
    
    def forceConsume(self, item, count, timestamp):
        '''
        强制消耗count个单位，如果不足则消耗所有
        '''
        assert(count >= 0)
        if count >= 0:
            balance = self.balance(item, timestamp)
            consumeCount = min(balance, count)
            if consumeCount > 0:
                item.expiresTime -= count * self._seconds
                if item.expiresTime < timestamp:
                    item.expiresTime = timestamp
            return consumeCount
        return 0
    
    def _decodeFromDictImpl(self, d):
        seconds = d.get('seconds')
        if not isinstance(seconds, int) or seconds <= 0:
            raise TYItemConfException(d, 'itemUnits.seconds must be int > 0')
        self._seconds = seconds
        return self

class TYItemUnitsTimeExpiresWeekDay(TYItemUnits):
    TYPE_ID = 'common.time.expires.weekDay'
    def __init__(self):
        super(TYItemUnitsTimeExpiresWeekDay, self).__init__()
        self._weekDay = 0
        
    def isTiming(self):
        return True

    def add(self, item, count, timestamp):
        assert(count >= 0)
        assert(not item.itemKind.singleMode)
        limitTime = pktimestamp.getCurrentWeekStartTimestamp(timestamp)
        limitTime += self._weekDay * 86400
        if timestamp >= limitTime:
            limitTime += 86400 * 7
        item.expiresTime = limitTime
        
    def balance(self, item, timestamp):
        '''
        剩余多少个单位
        '''
        assert(not item.itemKind.singleMode)
        return 1
    
    def consume(self, item, count, timestamp):
        '''
        给item消耗count个单位
        '''
        assert(count >= 0)
        return 0
    
    def forceConsume(self, item, count, timestamp):
        '''
        强制消耗count个单位，如果不足则消耗所有
        '''
        assert(count >= 0)
        return 0
    
    def _decodeFromDictImpl(self, d):
        self._weekDay = d.get('weekDay')
        if not isinstance(self._weekDay, int) or self._weekDay < 0 or self._weekDay > 6:
            raise TYItemConfException(d, 'TYItemUnitsTimeLimitWeekDay.weekDay must be int in[0, 6]')
        return self
    
class TYItemUnitsTimeExpiresSunday(TYItemUnitsTimeExpiresWeekDay):
    TYPE_ID = 'common.time.expires.sunday'
    def __init__(self):
        super(TYItemUnitsTimeExpiresSunday, self).__init__()
        self._weekDay = 6

    def _decodeFromDictImpl(self, d):
        return self

class TYItemUnitsCountExpires(TYItemUnits):
    '''
    数量型的单位，而且有有效期
    '''
    def __init__(self):
        super(TYItemUnitsCountExpires, self).__init__()
        
    def isTiming(self):
        return False
    
    def add(self, item, count, timestamp):
        assert(count >= 0)
        if item.isExpires(timestamp):
            item.remaining = 0
        item.remaining += count
        item.expiresTime = self._calcExpires(timestamp)
    
    def balance(self, item, timestamp):
        '''
        剩余多少个单位
        '''
        if item.isExpires(timestamp):
            return 0
        return item.remaining
    
    def consume(self, item, count, timestamp):
        '''
        给item消耗count个单位
        '''
        assert(count >= 0)
        if item.isExpires(timestamp):
            return 0
        if count > 0:
            if item.remaining >= count:
                item.remaining -= count
                return count
        return 0
    
    def forceConsume(self, item, count, timestamp):
        '''
        强制消耗count个单位，如果不足则消耗所有
        '''
        assert(count >= 0)
        if item.isExpires(timestamp):
            return 0
        consumeCount = min(item.remaining, count)
        if consumeCount > 0:
            item.remaining -= consumeCount
        return consumeCount
    
    def _calcExpires(self, timestamp):
        return 0

class TYItemUnitsCountExpiresToday(TYItemUnitsCountExpires):
    TYPE_ID = 'common.count.expires.today'
    def __init__(self):
        super(TYItemUnitsCountExpiresToday, self).__init__()
    
    def _calcExpires(self, timestamp):
        return pktimestamp.getDayStartTimestamp(timestamp + 86400)

class TYHallItemBase(TYItem):
    def __init__(self, itemKind, itemId):
        super(TYHallItemBase, self).__init__(itemKind, itemId)
        
    def visibleInBag(self, timestamp):
        if (self.needRemoveFromBag(timestamp)
            or (self.isDied(timestamp)
                and self.itemKind.findActionByName('repair') is None)):
            return False
        return True
    
class TYSimpleItemData(TYItemData):
    def __init__(self):
        super(TYSimpleItemData, self).__init__()
        
class TYSimpleItem(TYHallItemBase):
    '''
    简单道具，不能使用，只能消耗
    '''
    def __init__(self, itemKind, itemId):
        super(TYSimpleItem, self).__init__(itemKind, itemId)
        assert(isinstance(itemKind, TYSimpleItemKind))
    
class TYSimpleItemKind(TYItemKind):
    TYPE_ID = 'common.simple'
    def __init__(self):
        super(TYSimpleItemKind, self).__init__()
        
    def newItem(self, itemId, timestamp):
        '''
        产生一个本种类的道具id=itemId的道具
        @param itemId: 道具ID
        @return: SimpleItem
        '''
        item = TYSimpleItem(self, itemId)
        item.createTime = timestamp
        item.remaining = 0
        return item
    
    def newItemForDecode(self, itemId):
        '''
        从itemData中解码item
        '''
        return TYSimpleItem(self, itemId)
    
    def newItemData(self):
        '''
        产生一个ItemData
        '''
        return TYSimpleItemData()
    
class TYSwitchItemData(TYItemData):
    def __init__(self):
        super(TYSwitchItemData, self).__init__()
    
    def _getStructFormat(self):
        return 'B'
    
    def _getFieldNames(self):
        return ['isOn']
    
class TYSwitchItem(TYHallItemBase):
    '''
    简单道具，不能使用，只能消耗
    '''
    def __init__(self, itemKind, itemId):
        super(TYSwitchItem, self).__init__(itemKind, itemId)
        assert(isinstance(itemKind, TYSwitchItemKind))
        self.remaining = 0
        self.isOn = 0

    def onDied(self, timestamp):
        self.isOn = 0
    
    def _decodeFromItemData(self, itemData):
        self.isOn = itemData.isOn
    
    def _encodeToItemData(self, itemData):
        itemData.isOn = self.isOn
    
class TYSwitchItemKind(TYItemKind):
    TYPE_ID = 'common.switch'
    def __init__(self):
        super(TYSwitchItemKind, self).__init__()
        
    def newItem(self, itemId, timestamp):
        '''
        产生一个本种类的道具id=itemId的道具
        @param itemId: 道具ID
        @return: SimpleItem
        '''
        item = TYSwitchItem(self, itemId)
        item.createTime = timestamp
        item.remaining = 0
        item.isOn = 0
        return item
    
    def newItemForDecode(self, itemId):
        '''
        从itemData中解码item
        '''
        return TYSwitchItem(self, itemId)
    
    def newItemData(self):
        '''
        产生一个ItemData
        '''
        return TYSwitchItemData()
    
    def _decodeFromDictImpl(self, d):
        return self
        
class TYBoxItemData(TYItemData):
    def __init__(self):
        super(TYBoxItemData, self).__init__()
        self.openTimes = 0
        
    def _getStructFormat(self):
        return 'i'
    
    def _getFieldNames(self):
        return ['openTimes']
    
class TYBoxItem(TYHallItemBase):
    '''
    宝箱类道具，可以打开获得东西
    '''
    def __init__(self, itemKind, itemId):
        super(TYBoxItem, self).__init__(itemKind, itemId)
        assert(isinstance(itemKind, TYBoxItemKind))
        self.openTimes = 0
    
    def _decodeFromItemData(self, itemData):
        self.openTimes = itemData.openTimes
    
    def _encodeToItemData(self, itemData):
        itemData.openTimes = self.openTimes
    
class TYBoxItemKind(TYItemKind):
    TYPE_ID = 'common.box'
    def __init__(self):
        super(TYBoxItemKind, self).__init__()
        
    def newItem(self, itemId, timestamp):
        '''
        产生一个本种类的道具id=itemId的道具
        @param itemId: 道具ID
        @return: SimpleItem
        '''
        item = TYBoxItem(self, itemId)
        item.createTime = timestamp
        item.remaining = 0
        return item
    
    def newItemForDecode(self, itemId):
        '''
        从itemData中解码item
        '''
        return TYBoxItem(self, itemId)
    
    def newItemData(self):
        '''
        产生一个ItemData
        '''
        return TYBoxItemData()
    
class TYMemberCardItemData(TYItemData):
    def __init__(self):
        super(TYMemberCardItemData, self).__init__()
        self.checkinTime = 0
        
    def _getStructFormat(self):
        return 'i'
    
    def _getFieldNames(self):
        return ['checkinTime']
    
class TYMemberCardItem(TYHallItemBase):
    def __init__(self, itemKind, itemId):
        super(TYMemberCardItem, self).__init__(itemKind, itemId)
        assert(isinstance(itemKind, TYMemberCardItemKind))
        self.checkinTime = 0
        
    def canCheckin(self, timestamp):
        if self.isDied(timestamp):
            return False
        return pktimestamp.getDayStartTimestamp(timestamp) > pktimestamp.getDayStartTimestamp(self.checkinTime)
    
    def _decodeFromItemData(self, itemData):
        self.checkinTime = itemData.checkinTime
    
    def _encodeToItemData(self, itemData):
        itemData.checkinTime = self.checkinTime
    
class TYMemberCardItemKind(TYItemKind):
    TYPE_ID = 'common.memberCard'
    def __init__(self):
        super(TYMemberCardItemKind, self).__init__()
        self.checkinWhenAdded = None
        self.autoCheckinLimitVersion = -1
        
    def newItem(self, itemId, timestamp):
        '''
        产生一个新的本种类的道具，id=itemId
        @param itemId: 道具ID
        @return: Item的子类
        '''
        item = TYMemberCardItem(self, itemId)
        item.createTime = timestamp
        item.checkinTime = 0
        item.expiresTime = 0
        return item
    
    def newItemForDecode(self, itemId):
        '''
        产生一个本种类的道具，用于反序列化
        '''
        return TYMemberCardItem(self, itemId)
    
    def newItemData(self):
        '''
        产生一个ItemData
        '''
        return TYMemberCardItemData()
    
    def needAutoCheckin(self, userId):
        try:
            if self.autoCheckinLimitVersion != -1:
                clientId = sessiondata.getClientId(userId)
                _, clientVer, _ = strutil.parseClientId(clientId)
                if clientVer >= self.autoCheckinLimitVersion:
                    if ftlog.is_debug():
                        ftlog.debug('TYMemberCardItemKind.needAutoCheckin userId=', userId,
                                    'clientId=', clientId,
                                    'clientVer=', clientVer,
                                    'autoCheckinLimitVersion=', self.autoCheckinLimitVersion,
                                    'ret=', False)
                    return False
        except:
            ftlog.error('TYMemberCardItemKind.needAutoCheckin userId=', userId)
        
        if ftlog.is_debug():
            ftlog.debug('TYMemberCardItemKind.needAutoCheckin userId=', userId,
                        'ret=', True)
        return True
    
    def processWhenUserLogin(self, item, userAssets, gameId, isDayFirst, timestamp):
        if self.needAutoCheckin(userAssets.userId) and item.canCheckin(timestamp):
            checkinAction = self.findActionByName('checkin')
            return checkinAction.doAction(gameId, userAssets, item, timestamp, {})
        return None
    
    def processWhenAdded(self, item, userAssets,
                         gameId, timestamp):
        ret = None
        if item.checkinTime == 0:
            if self.checkinWhenAdded and self.needAutoCheckin(userAssets.userId):
                # 从无到有需要checkin
                checkinAction = self.findActionByName('checkin')
                ret = checkinAction.doAction(gameId, userAssets, item, timestamp, {})
            else:
                item.checkinTime = timestamp
                userAssets.getUserBag().updateItem(gameId, item, timestamp)
            datachangenotify.sendDataChangeNotify(gameId, userAssets.userId, 'decoration')
        return ret
    
    def getCheckinContent(self):
        try:
            checkinAction = self.findActionByName('checkin')
            if checkinAction:
                return checkinAction.content
        except:
            ftlog.error()
        return None
        
    def _decodeFromDictImpl(self, d):
        checkinAction = self.findActionByName('checkin')
        if not checkinAction:
            raise TYItemConfException(d, 'TYMemberCardItemKind.actions.checkin must be set')
        self.checkinWhenAdded = d.get('checkinWhenAdded', 0)
        if self.checkinWhenAdded not in (0, 1):
            raise TYItemConfException(d, 'TYMemberCardItemKind.checkinWhenAdded must be int in (0,1)')
        
        self.autoCheckinLimitVersion = d.get('autoCheckinLimitVersion', -1)
        if not isinstance(self.autoCheckinLimitVersion, (int, float)):
            raise TYItemConfException(d, 'TYMemberCardItemKind.autoCheckinLimitVersion must be int or float')
        
class TYDecroationItemData(TYItemData):
    def __init__(self):
        super(TYDecroationItemData, self).__init__()
        self.isWore = 0
        
    def _getStructFormat(self):
        return 'B'
    
    def _getFieldNames(self):
        return ['isWore']
    
class TYDecroationItem(TYHallItemBase):
    '''
    装饰类的道具，可以有content
    '''
    def __init__(self, itemKind, itemId):
        super(TYDecroationItem, self).__init__(itemKind, itemId)
        assert(isinstance(itemKind, TYDecroationItemKind))
        self.isWore = 0
        
    def onDied(self, timestamp):
        self.isWore = 0
    
    def _decodeFromItemData(self, itemData):
        self.isWore = itemData.isWore
    
    def _encodeToItemData(self, itemData):
        itemData.isWore = self.isWore
        
class TYDecroationItemKind(TYItemKind):
    '''
    装饰类道具
    '''
    TYPE_ID = 'common.decroation'
    def __init__(self):
        super(TYDecroationItemKind, self).__init__()
        # 位置掩码
        self.masks = None
        # 本地资源配置
        self.localRes = None
        # 服务器资源配置
        self.remoteRes = None
        # 位置信息
        self.pos = None

    def newItem(self, itemId, timestamp):
        '''
        产生一个本种类的道具id=itemId的道具
        @param itemId: 道具ID
        @return: SimpleItem
        '''
        item = TYDecroationItem(self, itemId)
        item.createTime = timestamp
        item.expiresTime = 0
        item.isWore = 0
        return item
    
    def newItemForDecode(self, itemId):
        return TYDecroationItem(self, itemId)
    
    def newItemData(self):
        return TYDecroationItemData()
    
    def _decodeFromDictImpl(self, d):
        '''
        从d中解析数据
        '''
        masks = d.get('masks')
        if not isinstance(masks, int):
            raise TYItemConfException(d, 'TYDecroationItemKind.masks must be int')
        pos = d.get('pos')
        localRes = d.get('localRes')
        remoteRes = d.get('remoteRes')
        if not isinstance(pos, dict):
            raise TYItemConfException(d, 'TYDecroationItemKind.pos must be dict')
        if localRes is None and remoteRes is None:
            raise TYItemConfException(d, 'TYDecroationItemKind.localRes or remoteRes require')
        if localRes is not None and not isinstance(localRes, dict):
            raise TYItemConfException(d, 'TYDecroationItemKind.localRes must be dict')
        if remoteRes is not None and not isinstance(remoteRes, dict):
            raise TYItemConfException(d, 'TYDecroationItemKind.remoteRes must be dict')
        self.masks = masks
        self.localRes = localRes
        self.remoteRes = remoteRes
        self.pos = pos
        return self
    
class TYExchangeItemData(TYItemData):
    def __init__(self):
        super(TYExchangeItemData, self).__init__()
        self.state = None
        
    def _getStructFormat(self):
        return 'B'
    
    def _getFieldNames(self):
        return ['state']
    
class TYExchangeItem(TYHallItemBase):
    '''
    简单道具，不能使用，只能消耗
    '''
    STATE_NORMAL = 0 # 未审核
    STATE_AUDIT = 1 # 审核中
    STATE_SHIPPING = 2 # 发货中
    
    def __init__(self, itemKind, itemId):
        super(TYExchangeItem, self).__init__(itemKind, itemId)
        assert(isinstance(itemKind, TYExchangeItemKind))
        self.state = TYExchangeItem.STATE_NORMAL
    
    def visibleInBag(self, timestamp):
        # 审核中的道具不显示
        visible = TYHallItemBase.visibleInBag(self, timestamp)
        if visible:
            return self.state == TYExchangeItem.STATE_NORMAL
        return visible
    
    def needRemoveFromBag(self, timestamp):
        if self.state != TYExchangeItem.STATE_NORMAL:
            return False
        return super(TYExchangeItem, self).needRemoveFromBag(timestamp)
    
    def onDied(self, timestamp):
        pass
    
    def _decodeFromItemData(self, itemData):
        self.state = itemData.state
    
    def _encodeToItemData(self, itemData):
        itemData.state = self.state
        
class TYExchangeItemKind(TYItemKind):
    TYPE_ID = 'common.exchange'
    def __init__(self):
        super(TYExchangeItemKind, self).__init__()
        
    def newItem(self, itemId, timestamp):
        '''
        产生一个本种类的道具id=itemId的道具
        @param itemId: 道具ID
        @return: SimpleItem
        '''
        item = TYExchangeItem(self, itemId)
        item.createTime = timestamp
        item.remaining = 0
        return item
    
    def newItemForDecode(self, itemId):
        '''
        从itemData中解码item
        '''
        return TYExchangeItem(self, itemId)
    
    def newItemData(self):
        '''
        产生一个ItemData
        '''
        return TYExchangeItemData()

    def _decodeFromDictImpl(self, d):
        if self.singleMode != 0:
            raise TYBizConfException(d, 'TYExchangeItemKind must not singleMode')
        return self

class TYItemExchangeEvent(UserEvent):
    def __init__(self, gameId, userId, item):
        super(TYItemExchangeEvent, self).__init__(userId, gameId)
        self.item = item
        
class TYItemExchangeResult(TYItemActionResult):
    def __init__(self, action, item, message, exchangeId):
        super(TYItemExchangeResult, self).__init__(action, item, message)
        self.exchangeId = exchangeId
        
class TYItemActionExchange(TYItemAction):
    TYPE_ID = 'common.exchange'
    SINGLE_MODE_NAME_TYPE_LIST = []
    
    def __init__(self):
        super(TYItemActionExchange, self).__init__()
        self.auditParams = None

    def isWechatRedPack(self):
        return self.auditParams.get("type") == 5

    def isJdActualProduct(self):
        return self.auditParams.get("type") == 6

    def getInputParams(self, gameId, userBag, item, timestamp):
        # 目前配置系统设计有问题,不能灵活配置InputParams的类型
        # 被迫在此黑掉配置……
        if self.isWechatRedPack():  # 微信红包,不让前端弹框输入手机号
            return {}
        if self.isJdActualProduct():  # 京东实物兑换,需要输入详细地址信息
            return {'type': 'jdActualProduct'}
        return super(TYItemActionExchange, self).getInputParams(gameId, userBag, item, timestamp)

    def checkParams(self, gameId, userAssets, item, timestamp, params):
        if self.isWechatRedPack():  # 微信红包,无需手机号
            return
        useBindPhone = params.get('bindPhone', 0)
        if not useBindPhone:
            # 如果没有bindPhone，则需要检查phoneNumber
            phoneNumber = params.get('phoneNumber')
            if not phoneNumber:
                raise TYItemActionParamException(self, '请输入手机号码')

    def getParamNameTypeList(self):
        return self.SINGLE_MODE_NAME_TYPE_LIST

    def canDo(self, userBag, item, timestamp):
        '''
        判断是否可以对item执行本动作
        '''
        return not item.isDied(timestamp) and item.state == TYExchangeItem.STATE_NORMAL

    def _doActionImpl(self, gameId, userAssets, item, timestamp, params):
        from hall.entity import hallexchange
        
        assert(isinstance(item, TYExchangeItem))
        if item.isDied(timestamp):
            raise TYItemAlreadyExpiresException(item)
        if not item.state == TYExchangeItem.STATE_NORMAL:
            raise TYItemAlreadyAuditException(item)

        wechat_red_pack = self.isWechatRedPack()  # 微信红包，无需手机号、地址
        exchangeParams = {}
        exchangeParams.update(self.auditParams)
        phone = params.get('phoneNumber') if not wechat_red_pack else 11111111111
        uName = params.get('uName', '')
        uAddres = params.get('uAddres', '')
        exchangeParams['phone'] = str(phone)
        exchangeParams['uName'] = uName
        exchangeParams['uAddres'] = uAddres
        if wechat_red_pack:
            from hall.entity import hall_wxappid
            clientId = sessiondata.getClientId(userAssets.userId)
            exchangeParams['wxappid'] = hall_wxappid.queryWXAppid(gameId, userAssets.userId, clientId)
        elif self.isJdActualProduct():
            exchangeParams['uProvince'] = params.get('uProvince', 0)
            exchangeParams['uCity'] = params.get('uCity', 0)
            exchangeParams['uDistrict'] = params.get('uDistrict', 0)
            exchangeParams['uTown'] = params.get('uTown', 0)

        # start gameid 60 fishaddon
        idCard = params.get('idCard', "")
        bank = params.get('bank','')
        bankAccount = params.get('bankAccount','')
        exchangeParams['idCard'] = str(idCard)
        exchangeParams['bank'] = str(bank)
        exchangeParams['bankAccount'] = str(bankAccount)
        # end gameid 60 fishaddon

        record, msg = hallexchange.requestExchange(userAssets.userId, item, exchangeParams, timestamp)
        item.state = TYExchangeItem.STATE_AUDIT
        item.original = 0
        userAssets.getUserBag().updateItem(gameId, item, timestamp)
        
        replaceParams = {'item': item.itemKind.displayName}
        _mail, message, _changed = _handleMailAndMessageAndChanged(gameId, userAssets, self, None, replaceParams)
        
        if not wechat_red_pack:
            msg = message
        TGHall.getEventBus().publishEvent(TYItemExchangeEvent(gameId, userAssets.userId, item))
        return TYItemExchangeResult(self, item, msg or message, record.exchangeId)
     
    def _decodeFromDictImpl(self, d):
        self.auditParams = d.get('auditParams', {})
        if not isinstance(self.auditParams, dict):
            raise TYBizConfException(d, 'TYItemActionExchange.auditParams must be dict')
        
class TYSkillItemData(TYItemData):
    def __init__(self):
        super(TYSkillItemData, self).__init__()

    
class TYSkillItem(TYHallItemBase):
    '''
    技能道具
    '''
    def __init__(self, itemKind, itemId):
        super(TYSkillItem, self).__init__(itemKind, itemId)
        assert(isinstance(itemKind, TYSkillItemKind))

    
class TYSkillItemKind(TYItemKind):
    TYPE_ID = 'common.skill'
    def __init__(self):
        super(TYSkillItemKind, self).__init__()
        
    def newItem(self, itemId, timestamp):
        '''
        产生一个本种类的道具id=itemId的道具
        @param itemId: 道具ID
        @return: SimpleItem
        '''
        item = TYSkillItem(self, itemId)
        item.createTime = timestamp
        item.remaining = 0
        return item
    
    def newItemForDecode(self, itemId):
        '''
        从itemData中解码item
        '''
        return TYSkillItem(self, itemId)
    
    def newItemData(self):
        '''
        产生一个ItemData
        '''
        return TYSkillItemData()

class TYItemActionSkillUse(TYItemAction):
    TYPE_ID = 'common.skill.use'
    def __init__(self):
        super(TYItemActionSkillUse, self).__init__()
        
    def canDo(self, userBag, item, timestamp):
        '''
        判断是否可以对item执行本动作
        '''
        return not item.isDied(timestamp)
    
    
    def _initWhenLoaded(self, itemKind, itemKindMap, assetKindMap):
        # 当配置解析工作完成后调用，用于初始化配置中一些itemKind相关的数据
        if ftlog.is_debug() :
            ftlog.debug('TYItemActionSkillUse _initWhenLoaded')
            
    def _doActionImpl(self, gameId, userAssets, item, timestamp, params):
        # 执行具体的动作，此时各种条件已经检查完毕
        
        if ftlog.is_debug() :
            ftlog.debug('TYItemActionSkillUse _doActionImpl gameId', gameId
                        ,'params =', params)
        from freetime.entity.msg import MsgPack
        from poker.protocol import router
        msg = runcmd.getMsgPack()
        roomId = params.get('roomId')
        from poker.entity.configure import gdata
        roomConf = gdata.roomIdDefineMap().get(roomId)
        if not roomConf:
            ftlog.warn("roomId invalid")
            return
        gid = roomConf.gameId

        msg1 = MsgPack()
        msg1.setCmd('table_call')
        msg1.updateParam(params) 
        msg1.setParam("action", "skill") 
        msg1.setParam("skillName", self._inputParams.get("skillName"))
        msg1.setParam("userId", msg.getParam("userId"))
        msg1.setParam("gameId", gid)
        msg1.setParam("clientId", msg.getParam("clientId"))
        router.sendTableServer(msg1, roomId)
        
        #消耗道具
        ftlog.debug('TYItemActionSkillUse over')
        userBag = userAssets.getUserBag()
        userBag.consumeItemUnits(gameId, item, 1, timestamp, 'ITEM_USE', item.kindId)


    def _decodeFromDictImpl(self, d):
        '''
        用于子类解析自己特有的数据
        '''
        pass   

        
class TYWeixinRedEnvelopPasswordItemData(TYItemData):
    '''
    微信红包道具数据
    '''
    def __init__(self):
        super(TYWeixinRedEnvelopPasswordItemData, self).__init__()
        
class TYWeixinRedEnvelopPasswordItem(TYHallItemBase):
    '''
    微信红包道具
    '''
    def __init__(self, itemKind, itemId):
        super(TYWeixinRedEnvelopPasswordItem, self).__init__(itemKind, itemId)
        assert(isinstance(itemKind, TYWeixinRedEnvelopPasswordItemKind))
        
class TYWeixinRedEnvelopPasswordItemKind(TYItemKind):
    TYPE_ID = 'common.weixin.redEnvelopPassword'
    def __init__(self):
        super(TYWeixinRedEnvelopPasswordItemKind, self).__init__()
        
    def newItem(self, itemId, timestamp):
        '''
        产生一个本种类的道具id=itemId的道具
        @param itemId: 道具ID
        @return: TYWeixinRedEnvelopPasswordItemKind
        '''
        item = TYWeixinRedEnvelopPasswordItem(self, itemId)
        item.createTime = timestamp
        item.remaining = 0
        return item
    
    def newItemForDecode(self, itemId):
        '''
        从itemData中解码item
        '''
        return TYWeixinRedEnvelopPasswordItem(self, itemId)
    
    def newItemData(self):
        '''
        产生一个ItemData
        '''
        return TYWeixinRedEnvelopPasswordItemData()

    def _decodeFromDictImpl(self, d):
        if self.singleMode != 0:
            raise TYBizConfException(d, 'TYWeixinRedEnvelopPasswordItemKind must not signleMode')
        return self
    
class TYItemActionWeixinRedEnvelopGetPasswordResult(TYItemActionResult):
    def __init__(self, action, item, message, password):
        super(TYItemActionWeixinRedEnvelopGetPasswordResult, self).__init__(action, item, message)
        self.password = password
        
class TYItemActionWeixinRedEnvelopGetPassword(TYItemAction):
    TYPE_ID = 'common.weixin.redEnvelop.getPassword'
    def __init__(self):
        super(TYItemActionWeixinRedEnvelopGetPassword, self).__init__()
        self.amount = 0
        
    def canDo(self, userBag, item, timestamp):
        '''
        判断是否可以对item执行本动作
        '''
        return not item.isDied(timestamp)
            
    def _doActionImpl(self, gameId, userAssets, item, timestamp, params):
        # 执行具体的动作，此时各种条件已经检查完毕
        from hall.entity import sdkclient
        
        assert(isinstance(item, TYWeixinRedEnvelopPasswordItem))
        
        if ftlog.is_debug() :
            ftlog.debug('TYItemActionWeixinRedEnvelopGetPassword._doActionImpl gameId=', gameId,
                        'userId=', userAssets.userId,
                        'itemId=', item.itemId,
                        'kindId=', item.kindId,
                        'params=', params)
            
        balance = item.balance(timestamp)
        if balance < 1:
            raise TYItemNotEnoughException(item)
        
        # 获取红包口令
        ec, result = sdkclient.getWeixinRedEnvelopePassword(userAssets.userId,
                                                            item.kindId,
                                                            item.itemId,
                                                            self.amount)
        if ec == 0:
            assert(result)
            #消耗item
            userBag = userAssets.getUserBag()
            userBag.removeItem(gameId, item, timestamp, 'ITEM_USE', 0)
            _mail, message, _changed = _handleMailAndMessageAndChanged(gameId, userAssets, self, None, {'password':result})
            
            ftlog.info('TYItemActionWeixinRedEnvelopGetPassword._doActionImpl OK gameId=', gameId,
                       'userId=', userAssets.userId,
                       'itemId=', item.itemId,
                       'kindId=', item.kindId,
                       'password=', result,
                       'params=', params)
            return TYItemActionWeixinRedEnvelopGetPasswordResult(self, item, message, result)
        else:
            ftlog.warn('TYItemActionWeixinRedEnvelopGetPassword._doActionImpl Fail gameId=', gameId,
                       'userId=', userAssets.userId,
                       'itemId=', item.itemId,
                       'kindId=', item.kindId,
                       'params=', params,
                       'ec=', ec,
                       'info=', result)
            raise TYBizException(-1, result)
            
    def _decodeFromDictImpl(self, d):
        self.amount = d.get('amount')
        if not isinstance(self.amount, (int, float)) or self.amount <= 0:
            raise TYBizConfException(d, 'TYItemActionWeixinRedEnvelopGetPassword.amount must be int or float > 0')
        
        return self

class TYWeixinRedEnvelopItemData(TYItemData):
    '''
    微信红包道具数据
    '''
    def __init__(self):
        super(TYWeixinRedEnvelopItemData, self).__init__()
        
class TYWeixinRedEnvelopItem(TYHallItemBase):
    '''
    微信红包道具
    '''
    def __init__(self, itemKind, itemId):
        super(TYWeixinRedEnvelopItem, self).__init__(itemKind, itemId)
        assert(isinstance(itemKind, TYWeixinRedEnvelopItemKind))
    
    def isExpires(self, timestamp):
        '''
        检查道具是否到期
        @param timestamp: 当前时间戳
        @return: 到期返回True, 否则返回False
        '''
        if self.kindId == 1086 and self.expiresTime <= 0:
            return True
        return super(TYWeixinRedEnvelopItem, self).isExpires(timestamp)

class TYWeixinRedEnvelopItemKind(TYItemKind):
    TYPE_ID = 'common.weixin.redEnvelop'
    def __init__(self):
        super(TYWeixinRedEnvelopItemKind, self).__init__()
        
    def newItem(self, itemId, timestamp):
        '''
        产生一个本种类的道具id=itemId的道具
        @param itemId: 道具ID
        @return: TYWeixinRedEnvelopItem
        '''
        item = TYWeixinRedEnvelopItem(self, itemId)
        item.createTime = timestamp
        item.remaining = 0
        return item
    
    def newItemForDecode(self, itemId):
        '''
        从itemData中解码item
        '''
        return TYWeixinRedEnvelopItem(self, itemId)
    
    def newItemData(self):
        '''
        产生一个ItemData
        '''
        return TYWeixinRedEnvelopItemData()

    def _decodeFromDictImpl(self, d):
        if self.singleMode != 0:
            raise TYBizConfException(d, 'TYWeixinRedEnvelopItemKind must not signleMode')
        return self
    
class TYItemActionWeixinRedEnvelopOpenResult(TYItemActionResult):
    def __init__(self, action, item, message):
        super(TYItemActionWeixinRedEnvelopOpenResult, self).__init__(action, item, message)
        
class TYItemActionWeixinRedEnvelopOpen(TYItemAction):
    TYPE_ID = 'common.weixin.redEnvelop.open'
    def __init__(self):
        super(TYItemActionWeixinRedEnvelopOpen, self).__init__()
        self.amount = 0
        self.showInfo = None
        
    def canDo(self, userBag, item, timestamp):
        '''
        判断是否可以对item执行本动作
        '''
        return not item.isDied(timestamp)

    def _doActionImpl(self, gameId, userAssets, item, timestamp, params):
        # 执行具体的动作，此时各种条件已经检查完毕
        from hall.entity import sdkclient
        from hall.entity import hallshare
        
        assert(isinstance(item, TYWeixinRedEnvelopItem))
        
        if ftlog.is_debug() :
            ftlog.debug('TYItemActionWeixinRedEnvelopOpen._doActionImpl gameId=', gameId,
                        'userId=', userAssets.userId,
                        'itemId=', item.itemId,
                        'kindId=', item.kindId,
                        'params=', params)
            
        if item.isDied(timestamp):
            if item.isExpires(timestamp):
                raise TYItemAlreadyExpiresException(item)
            raise TYItemNotEnoughException(item)
        
        # 发送红包
        ec, info = sdkclient.sendWeixinRedEnvelope(gameId, userAssets.userId,
                                                   item.itemId, self.amount)
        if ec == 0:
            #消耗item
            userBag = userAssets.getUserBag()
            userBag.removeItem(gameId, item, timestamp, 'ITEM_USE', 0)
            replaceParams = {'item':item.itemKind.displayName} 
            _mail, message, _changed = _handleMailAndMessageAndChanged(gameId, userAssets, self, None, replaceParams)
            
            result = TYItemActionWeixinRedEnvelopOpenResult(self, item, message)
            shareId = hallshare.getShareId('wxRedEnvelope', userAssets.userId, gameId)
            share = hallshare.findShare(shareId)
            if share:
                result.todotask = share.buildTodotask(HALL_GAMEID, userAssets.userId, 'wxRedEnvelope')
            ftlog.debug('TYItemActionWeixinRedEnvelopOpen._doActionImpl OK gameId=', gameId,
                       'userId=', userAssets.userId,
                       'itemId=', item.itemId,
                       'kindId=', item.kindId,
                       'params=', params)
            return result
        else:
            ftlog.debug('TYItemActionWeixinRedEnvelopOpen._doActionImpl Fail gameId=', gameId,
                       'userId=', userAssets.userId,
                       'itemId=', item.itemId,
                       'kindId=', item.kindId,
                       'params=', params,
                       'ec=', ec,
                       'info=', info)
            raise TYItemException(-1, info)
            
    def _decodeFromDictImpl(self, d):
        self.amount = d.get('amount')
        if not isinstance(self.amount, (int, float)) or self.amount <= 0:
            raise TYBizConfException(d, 'TYItemActionWeixinRedEnvelopOpen.amount must be int or float > 0')
        self.showInfo = d.get('showInfo')
        if not self.showInfo or not isstring(self.showInfo):
            raise TYBizConfException(d, 'TYItemActionWeixinRedEnvelopOpen.showInfo must be not empty string')
        return self


class TYChestItemKind(TYItemKind):
    TYPE_ID = 'common.chest'

    def __init__(self):
        super(TYChestItemKind, self).__init__()

    def newItem(self, itemId, timestamp):
        '''
        产生一个本种类的道具id=itemId的道具
        @param itemId: 道具ID
        @return: SimpleItem
        '''
        item = TYChestItem(self, itemId)
        item.createTime = timestamp
        return item

    def newItemForDecode(self, itemId):
        '''
        从itemData中解码item
        '''
        return TYChestItem(self, itemId)

    def newItemData(self):
        '''
        产生一个ItemData
        '''
        return TYChestItemData()


class TYChestItemData(TYItemData):
    def __init__(self):
        super(TYChestItemData, self).__init__()
        self.remaining = 1
        self.chestId = 0
        self.order = -1
        self.beginTime = 0
        self.totalTime = 0
        self.state = 0

    def _getStructFormat(self):
        return 'HBIIB'

    def _getFieldNames(self):
        return ['chestId', 'order', 'beginTime', 'totalTime', 'state']


class TYChestItem(TYHallItemBase):
    '''
    捕鱼定时宝箱类道具，到时后可以打开获得东西
    '''

    def __init__(self, itemKind, itemId):
        super(TYChestItem, self).__init__(itemKind, itemId)
        assert (isinstance(itemKind, TYChestItemKind))
        self.chestId = 0
        self.order = -1
        self.beginTime = 0
        self.totalTime = 0
        self.state = 0

    def _decodeFromItemData(self, itemData):
        self.chestId = itemData.chestId
        self.order = itemData.order
        self.beginTime = itemData.beginTime
        self.totalTime = itemData.totalTime
        self.state = itemData.state

    def _encodeToItemData(self, itemData):
        itemData.chestId = self.chestId
        itemData.order = self.order
        itemData.beginTime = self.beginTime
        itemData.totalTime = self.totalTime
        itemData.state = self.state


class TYItemActionSetGameData(TYItemAction):
    TYPE_ID = 'common.setGameData'

    def __init__(self):
        super(TYItemActionSetGameData, self).__init__()

    def canDo(self, userBag, item, timestamp):
        ''' 判断是否可以对item执行本动作 '''
        return not item.isDied(timestamp)

    def _doActionImpl(self, gameId, userAssets, item, timestamp, params):
        # 执行具体的动作，此时各种条件已经检查完毕

        userBag = userAssets.getUserBag()
        # 消耗道具
        userBag.consumeItemUnits(gameId, item, 1, timestamp, 'ITEM_USE',
                                 item.kindId)
        gamedata.setGameAttr(userBag.userId, self.gameId, self.field, self.value)

    def _decodeFromDictImpl(self, d):
        self.field = d['args']['field']
        self.value = int(d['args']['value'])
        self.gameId = int(d['args']['gameId'])

    
class TYAssetKindChip(TYAssetKind):
    TYPE_ID = 'common.chip'
    def __init__(self):
        super(TYAssetKindChip, self).__init__()
        
    def add(self, gameId, userAssets, kindId, count, timestamp, eventId, intEventParam,
            roomId=0, tableId=0, roundId=0, param01=0, param02=0):
        '''
        @return: finalCount
        '''
        assert(count >= 0)
        trueDelta, final = pkuserchip.incrChip(userAssets.userId, gameId, count,
                                               pkdaoconst.CHIP_NOT_ENOUGH_OP_MODE_NONE,
                                               eventId, intEventParam, None,
                                               roomId=roomId, tableId=tableId, roundId=roundId, param01=param01, param02=param02)
        if ftlog.is_debug():
            ftlog.debug('AssetKindChip.add gameId=', gameId,
                        'userId=', userAssets.userId,
                        'kind=', kindId,
                        'count=', count,
                        'timestamp=', timestamp,
                        'eventId=', eventId,
                        'intEventParam=', intEventParam,
                        'trueDelta=', trueDelta,
                        'final=', final)
        return final
    
    def consume(self, gameId, userAssets, kindId, count, timestamp, eventId, intEventParam,
                roomId=0, tableId=0, roundId=0, param01=0, param02=0):
        '''
        @return: consumeCount, finalCount
        '''
        assert(count >= 0)
        trueDelta, final = pkuserchip.incrChip(userAssets.userId, gameId, -count,
                                               pkdaoconst.CHIP_NOT_ENOUGH_OP_MODE_NONE,
                                               eventId, intEventParam, None,
                                               roomId=roomId, tableId=tableId, roundId=roundId,
                                               param01=param01, param02=param02)
        if ftlog.is_debug():
            ftlog.debug('AssetKindChip.consume gameId=', gameId,
                        'userId=', userAssets.userId,
                        'kind=', kindId,
                        'count=', count,
                        'timestamp=', timestamp,
                        'eventId=', eventId,
                        'intEventParam=', intEventParam,
                        'trueDelta=', trueDelta,
                        'final=', final)
        return -trueDelta, final
    
    def forceConsume(self, gameId, userAssets, kindId, count, timestamp, eventId, intEventParam):
        '''
        @return: consumeCount, finalCount
        '''
        assert(count >= 0)
        trueDelta, final = pkuserchip.incrChip(userAssets.userId, gameId, -count,
                                               pkdaoconst.CHIP_NOT_ENOUGH_OP_MODE_CLEAR_ZERO,
                                               eventId, intEventParam, None)
        if ftlog.is_debug():
            ftlog.debug('AssetKindChip.forceConsume gameId=', gameId,
                        'userId=', userAssets.userId,
                        'kind=', kindId,
                        'count=', count,
                        'timestamp=', timestamp,
                        'eventId=', eventId,
                        'intEventParam=', intEventParam,
                        'trueDelta=', trueDelta,
                        'final=', final)
        return -trueDelta, final
    
    def balance(self, userAssets, timestamp):
        '''
        @return: balance
        '''
        return pkuserchip.getChip(userAssets.userId)
    
class TYAssetKindCoupon(TYAssetKind):
    TYPE_ID = 'common.coupon'
    def __init__(self):
        super(TYAssetKindCoupon, self).__init__()
        
    def add(self, gameId, userAssets, kindId, count, timestamp, eventId, intEventParam,
            roomId=0, tableId=0, roundId=0, param01=0, param02=0):
        '''
        @return: finalCount
        '''
        assert(count >= 0)
        trueDelta, final = pkuserchip.incrCoupon(userAssets.userId, gameId, count,
                                                 pkdaoconst.CHIP_NOT_ENOUGH_OP_MODE_NONE,
                                                 eventId, intEventParam, None,
                                                 roomId=roomId, tableId=tableId,
                                                 roundId=roundId, param01=param01, param02=param02)
        if ftlog.is_debug():
            ftlog.debug('TYAssetKindCoupon.add gameId=', gameId,
                        'userId=', userAssets.userId,
                        'kind=', kindId,
                        'count=', count,
                        'timestamp=', timestamp,
                        'eventId=', eventId,
                        'intEventParam=', intEventParam,
                        'trueDelta=', trueDelta,
                        'final=', final)
        return final
    
    def consume(self, gameId, userAssets, kindId, count, timestamp, eventId, intEventParam,
                roomId=0, tableId=0, roundId=0, param01=0, param02=0):
        '''
        @return: consumeCount, finalCount
        '''
        assert(count >= 0)
        trueDelta, final = pkuserchip.incrCoupon(userAssets.userId, gameId, -count,
                                                 pkdaoconst.CHIP_NOT_ENOUGH_OP_MODE_NONE,
                                                 eventId, intEventParam, None,
                                                 roomId=roomId, tableId=tableId,
                                                 roundId=roundId, param01=param01, param02=param02)
        if ftlog.is_debug():
            ftlog.debug('TYAssetKindCoupon.consume gameId=', gameId,
                        'userId=', userAssets.userId,
                        'kind=', kindId,
                        'count=', count,
                        'timestamp=', timestamp,
                        'eventId=', eventId,
                        'intEventParam=', intEventParam,
                        'trueDelta=', trueDelta,
                        'final=', final)
        return -trueDelta, final
    
    def forceConsume(self, gameId, userAssets, kindId, count, timestamp, eventId, intEventParam):
        '''
        @return: consumeCount, finalCount
        '''
        assert(count >= 0)
        trueDelta, final = pkuserchip.incrCoupon(userAssets.userId, gameId, -count,
                                                 pkdaoconst.CHIP_NOT_ENOUGH_OP_MODE_CLEAR_ZERO,
                                                 eventId, 0, None)
        if ftlog.is_debug():
            ftlog.debug('TYAssetKindCoupon.forceConsume gameId=', gameId,
                        'userId=', userAssets.userId,
                        'kind=', kindId,
                        'count=', count,
                        'timestamp=', timestamp,
                        'eventId=', eventId,
                        'intEventParam=', intEventParam,
                        'trueDelta=', trueDelta,
                        'final=', final)
        return -trueDelta, final
    
    def balance(self, userAssets, timestamp):
        '''
        @return: balance
        '''
        return pkuserchip.getCoupon(userAssets.userId)

class TYAssetKindExp(TYAssetKind):
    TYPE_ID = 'common.exp'
    def __init__(self):
        super(TYAssetKindExp, self).__init__()
        
    def add(self, gameId, userAssets, kindId, count, timestamp, eventId, intEventParam,
            roomId=0, tableId=0, roundId=0, param01=0, param02=0):
        '''
        @return: finalCount
        '''
        assert(count >= 0)
        final = pkuserdata.incrExp(userAssets.userId, count)
        if ftlog.is_debug():
            ftlog.debug('TYAssetKindExp.add gameId=', gameId,
                        'userId=', userAssets.userId,
                        'kind=', kindId,
                        'count=', count,
                        'timestamp=', timestamp,
                        'eventId=', eventId,
                        'intEventParam=', intEventParam,
                        'final=', final)
        return final
    
    def consume(self, gameId, userAssets, kindId, count, timestamp, eventId, intEventParam,
                roomId=0, tableId=0, roundId=0, param01=0, param02=0):
        '''
        @return: consumeCount, finalCount
        '''
        assert(count >= 0)
        final = pkuserdata.incrExp(userAssets.userId, -count)
        if ftlog.is_debug():
            ftlog.debug('TYAssetKindExp.consume gameId=', gameId,
                        'userId=', userAssets.userId,
                        'kind=', kindId,
                        'count=', count,
                        'timestamp=', timestamp,
                        'eventId=', eventId,
                        'intEventParam=', intEventParam,
                        'final=', final)
        return count, final
    
    def forceConsume(self, gameId, userAssets, kindId, count, timestamp, eventId, intEventParam):
        '''
        @return: consumeCount, finalCount
        '''
        assert(count >= 0)
        final = pkuserdata.incrExp(userAssets.userId, -count)
        if ftlog.is_debug():
            ftlog.debug('TYAssetKindExp.forceConsume gameId=', gameId,
                        'userId=', userAssets.userId,
                        'kind=', kindId,
                        'count=', count,
                        'timestamp=', timestamp,
                        'eventId=', eventId,
                        'intEventParam=', intEventParam,
                        'final=', final)
        return count, final
    
    def balance(self, userAssets, timestamp):
        '''
        @return: balance
        '''
        return pkuserdata.getExp(userAssets.userId)



class TYAssetKindCharm(TYAssetKind):
    TYPE_ID = 'common.charm'
    def __init__(self):
        super(TYAssetKindCharm, self).__init__()
        
    def add(self, gameId, userAssets, kindId, count, timestamp, eventId, intEventParam,
            roomId=0, tableId=0, roundId=0, param01=0, param02=0):
        '''
        @return: finalCount
        '''
        assert(count >= 0)
        final = pkuserdata.incrCharm(userAssets.userId, count)
        if ftlog.is_debug():
            ftlog.debug('TYAssetKindCharm.add gameId=', gameId,
                        'userId=', userAssets.userId,
                        'kind=', kindId,
                        'count=', count,
                        'timestamp=', timestamp,
                        'eventId=', eventId,
                        'intEventParam=', intEventParam,
                        'final=', final)
        return final
    
    def consume(self, gameId, userAssets, kindId, count, timestamp, eventId, intEventParam,
                roomId=0, tableId=0, roundId=0, param01=0, param02=0):
        '''
        @return: consumeCount, finalCount
        '''
        assert(count >= 0)
        final = pkuserdata.incrCharm(userAssets.userId, -count)
        if ftlog.is_debug():
            ftlog.debug('TYAssetKindCharm.consume gameId=', gameId,
                        'userId=', userAssets.userId,
                        'kind=', kindId,
                        'count=', count,
                        'timestamp=', timestamp,
                        'eventId=', eventId,
                        'intEventParam=', intEventParam,
                        'final=', final)
        return -count, final
    
    def forceConsume(self, gameId, userAssets, kindId, count, timestamp, eventId, intEventParam):
        '''
        @return: consumeCount, finalCount
        '''
        assert(count >= 0)
        final = pkuserdata.incrCharm(userAssets.userId, -count)
        if ftlog.is_debug():
            ftlog.debug('TYAssetKindCharm.forceConsume gameId=', gameId,
                        'userId=', userAssets.userId,
                        'kind=', kindId,
                        'count=', count,
                        'timestamp=', timestamp,
                        'eventId=', eventId,
                        'intEventParam=', intEventParam,
                        'final=', final)
        return -count, final
    
    def balance(self, userAssets, timestamp):
        '''
        @return: balance
        '''
        return pkuserdata.getCharm(userAssets.userId)
        

class TYAssetKindVipBenefits(TYAssetKind):
    TYPE_ID = 'common.assistance'
    def __init__(self):
        super(TYAssetKindVipBenefits, self).__init__()
        
    def add(self, gameId, userAssets, kindId, count, timestamp, eventId, intEventParam,
            roomId=0, tableId=0, roundId=0, param01=0, param02=0):
        '''
        @return: finalCount
        '''
        assert(count >= 0)
        final = pkgamedata.incrGameAttr(userAssets.userId, 9999, 'vip.benefits', count)
        if ftlog.is_debug():
            ftlog.debug('AssetKindVipBenefits.add gameId=', gameId,
                        'userId=', userAssets.userId,
                        'kind=', kindId,
                        'count=', count,
                        'timestamp=', timestamp,
                        'eventId=', eventId,
                        'intEventParam=', intEventParam,
                        'final=', final)
        return final
    
    def consume(self, gameId, userAssets, kindId, count, timestamp, eventId, intEventParam,
                roomId=0, tableId=0, roundId=0, param01=0, param02=0):
        '''
        @return: consumeCount, finalCount
        '''
        assert(count >= 0)
        trueDelta, final, fixCount = pkgamedata.incrGameAttrLimit(userAssets.userId, 9999, 'vip.benefits', -count,
                                                                  - 1, -1, pkdaoconst.CHIP_NOT_ENOUGH_OP_MODE_NONE)
        if ftlog.is_debug():
            ftlog.debug('AssetKindVipBenefits.consume gameId=', gameId,
                        'userId=', userAssets.userId,
                        'kind=', kindId,
                        'count=', count,
                        'timestamp=', timestamp,
                        'eventId=', eventId,
                        'intEventParam=', intEventParam,
                        'trueDelta=', trueDelta,
                        'final=', final,
                        'fixCount=', fixCount)
        return -trueDelta, final
    
    def forceConsume(self, gameId, userAssets, kindId, count, timestamp, eventId, intEventParam):
        '''
        @return: consumeCount, finalCount
        '''
        assert(count >= 0)
        trueDelta, final, fixCount = pkgamedata.incrGameAttrLimit(userAssets.userId, 9999, 'vip.benefits', -count,
                                                                  - 1, -1, pkdaoconst.CHIP_NOT_ENOUGH_OP_MODE_CLEAR_ZERO)
        if ftlog.is_debug():
            ftlog.debug('AssetKindVipBenefits.forceConsume gameId=', gameId,
                        'userId=', userAssets.userId,
                        'kind=', kindId,
                        'count=', count,
                        'timestamp=', timestamp,
                        'eventId=', eventId,
                        'intEventParam=', intEventParam,
                        'trueDelta=', trueDelta,
                        'final=', final,
                        'fixCount=', fixCount)
        return -trueDelta, final
    
    def balance(self, userAssets, timestamp):
        '''
        @return: balance
        '''
        return pkgamedata.getGameAttrInt(userAssets.userId, 9999, 'vip.benefits')
    
class TYAssetKindDiamond(TYAssetKind):
    TYPE_ID = 'common.diamond'
    def __init__(self):
        super(TYAssetKindDiamond, self).__init__()
        
    def add(self, gameId, userAssets, kindId, count, timestamp, eventId, intEventParam,
            roomId=0, tableId=0, roundId=0, param01=0, param02=0):
        '''
        @return: finalCount
        '''
        assert(count >= 0)
        trueDelta, final = pkuserchip.incrDiamond(userAssets.userId, gameId, count,
                                                  pkdaoconst.CHIP_NOT_ENOUGH_OP_MODE_NONE,
                                                  eventId, intEventParam, None,
                                                  roomId=roomId, tableId=tableId, roundId=roundId,
                                                  param01=param01, param02=param02)
        if ftlog.is_debug():
            ftlog.debug('TYAssetKindDiamond.add gameId=', gameId,
                        'userId=', userAssets.userId,
                        'kind=', kindId,
                        'count=', count,
                        'timestamp=', timestamp,
                        'eventId=', eventId,
                        'intEventParam=', intEventParam,
                        'trueDelta=', trueDelta,
                        'final=', final)
        return final
    
    def consume(self, gameId, userAssets, kindId, count, timestamp, eventId, intEventParam,
                roomId=0, tableId=0, roundId=0, param01=0, param02=0):
        '''
        @return: consumeCount, finalCount
        '''
        assert(count >= 0)
        trueDelta, final = pkuserchip.incrDiamond(userAssets.userId, gameId, -count,
                                                  pkdaoconst.CHIP_NOT_ENOUGH_OP_MODE_NONE,
                                                  eventId, intEventParam, None)
        if ftlog.is_debug():
            ftlog.debug('TYAssetKindDiamond.consume gameId=', gameId,
                        'userId=', userAssets.userId,
                        'kind=', kindId,
                        'count=', count,
                        'timestamp=', timestamp,
                        'eventId=', eventId,
                        'intEventParam=', intEventParam,
                        'trueDelta=', trueDelta,
                        'final=', final)
        return -trueDelta, final
    
    def forceConsume(self, gameId, userAssets, kindId, count, timestamp, eventId, intEventParam):
        '''
        @return: consumeCount, finalCount
        '''
        assert(count >= 0)
        trueDelta, final = pkuserchip.incrDiamond(userAssets.userId, gameId, -count,
                                                  pkdaoconst.CHIP_NOT_ENOUGH_OP_MODE_CLEAR_ZERO,
                                                  eventId, intEventParam, None)
        if ftlog.is_debug():
            ftlog.debug('TYAssetKindDiamond.forceConsume gameId=', gameId,
                        'userId=', userAssets.userId,
                        'kind=', kindId,
                        'count=', count,
                        'timestamp=', timestamp,
                        'eventId=', eventId,
                        'intEventParam=', intEventParam,
                        'trueDelta=', trueDelta,
                        'final=', final)
        return -trueDelta, final
    
    def balance(self, userAssets, timestamp):
        '''
        @return: balance
        '''
        return pkuserchip.getDiamond(userAssets.userId)
    
class TYAssetKindEntity(TYAssetKind):
    TYPE_ID = 'common.entity'
    def __init__(self):
        super(TYAssetKindEntity, self).__init__()
        
    def add(self, gameId, userAssets, kindId, count, timestamp, eventId, intEventParam,
            roomId=0, tableId=0, roundId=0, param01=0, param02=0):
        '''
        @return: finalCount
        '''
        assert(count >= 0)
        if ftlog.is_debug():
            ftlog.debug('TYAssetKindEntity.add gameId=', gameId,
                        'userId=', userAssets.userId,
                        'kind=', kindId,
                        'count=', count,
                        'timestamp=', timestamp,
                        'eventId=', eventId,
                        'intEventParam=', intEventParam,
                        'trueDelta=', 1,
                        'final=', 1)
        return 1
    
    def consume(self, gameId, userAssets, kindId, count, timestamp, eventId, intEventParam,
                roomId=0, tableId=0, roundId=0, param01=0, param02=0):
        '''
        @return: consumeCount, finalCount
        '''
        assert(count >= 0)
        if ftlog.is_debug():
            ftlog.debug('TYAssetKindEntity.consume gameId=', gameId,
                        'userId=', userAssets.userId,
                        'kind=', kindId,
                        'count=', count,
                        'timestamp=', timestamp,
                        'eventId=', eventId,
                        'intEventParam=', intEventParam,
                        'trueDelta=', 0,
                        'final=', 0)
        return 0, 0
    
    def forceConsume(self, gameId, userAssets, kindId, count, timestamp, eventId, intEventParam):
        '''
        @return: consumeCount, finalCount
        '''
        assert(count >= 0)
        if ftlog.is_debug():
            ftlog.debug('TYAssetKindEntity.forceConsume gameId=', gameId,
                        'userId=', userAssets.userId,
                        'kind=', kindId,
                        'count=', count,
                        'timestamp=', timestamp,
                        'eventId=', eventId,
                        'intEventParam=', intEventParam,
                        'trueDelta=', 0,
                        'final=', 0)
        return 0, 0
    
    def balance(self, userAssets, timestamp):
        '''
        @return: balance
        '''
        return 0
    
class TYAssetKindCash(TYAssetKindEntity):
    TYPE_ID = 'common.cash'
    def __init__(self):
        super(TYAssetKindCash, self).__init__()
        
    def buildContentForDelivery(self, count):
        intCount = int(count)
        intFmt = '%s：%s%s'
        floatFmt = '%s：%.2f%s'
        fmt = intFmt if intCount == count else floatFmt
        return fmt % (self.displayName, count, self.units)
    
    def buildContent(self, count, needUnits=True):
        if needUnits:
            intCount = int(count)
            intFmt = '%s%s%s'
            floatFmt = '%.2f%s%s'
            fmt = intFmt if intCount == count else floatFmt
            return fmt % (count, self.units, self.displayName)
        return '%s%s' % (count, self.displayName)

class TYItemDataDaoImpl(TYItemDataDao):
    def loadAll(self, userId):
        '''
        加载用户所有道具
        @param userId: 哪个用户
        @return: list<(itemId, bytes)>
        '''
        itemList = itemdata.getItemDataAll(userId, HALL_GAMEID)
        return itemList
    
    def saveItem(self, userId, itemId, itemData):
        '''
        保存道具
        @param userId: 哪个用户
        @param itemId: 道具ID
        @param itemData: bytes 
        '''
        return itemdata.setItemData(userId, HALL_GAMEID, itemId, itemData)
        
    def removeItem(self, userId, itemId):
        '''
        删除一个道具
        @param userId: 哪个用户
        @param itemId: 道具ID
        '''
        return itemdata.delItemData(userId, HALL_GAMEID, itemId)

    def nextItemId(self):
        '''
        获取下一个道具ID
        @return: itemId
        '''
        key = 'globalid'
        field = 'itemId'
        ftlog.debug('TYItemDataDaoRedis.nextItemId key=', key,
                    'field=', field)
        return pkdao.executeMixCmd('hincrby', key, field, 1)
    
def _registerClasses():
    ftlog.debug('hallitem._registerClasses')
    
    TYItemActionConditionRegister.registerClass(TYItemActionConditionLeastOncePay.TYPE_ID, TYItemActionConditionLeastOncePay)
    TYItemActionConditionRegister.registerClass(TYItemActionConditionLeastOnceAlipay.TYPE_ID, TYItemActionConditionLeastOnceAlipay)
    TYItemActionConditionRegister.registerClass(TYItemActionConditionGotSecondDaysLater.TYPE_ID, TYItemActionConditionGotSecondDaysLater)
    TYItemActionConditionRegister.registerClass(TYItemActionConditionBindPhoneCheck.TYPE_ID, TYItemActionConditionBindPhoneCheck)
    TYItemActionConditionRegister.registerClass(TYItemActionConditionBindWeixin.TYPE_ID, TYItemActionConditionBindWeixin)
    TYItemActionConditionRegister.registerClass(TYItemActionConditionCanOpenFlag.TYPE_ID, TYItemActionConditionCanOpenFlag)
    TYItemActionConditionRegister.registerClass(ItemActionConditionGameDashifenLevel.TYPE_ID, ItemActionConditionGameDashifenLevel)
    TYItemActionConditionRegister.registerClass(TYItemActionConditionTimeRange.TYPE_ID, TYItemActionConditionTimeRange)
    
    TYItemActionRegister.registerClass(TYItemActionSale.TYPE_ID, TYItemActionSale)
    TYItemActionRegister.registerClass(TYItemActionRepair.TYPE_ID, TYItemActionRepair)
    TYItemActionRegister.registerClass(TYItemActionAssemble.TYPE_ID, TYItemActionAssemble)
    TYItemActionRegister.registerClass(TYItemActionPresent.TYPE_ID, TYItemActionPresent)
    
    TYItemActionRegister.registerClass(TYItemActionSendLed.TYPE_ID, TYItemActionSendLed)
    TYItemActionRegister.registerClass(TYItemActionSendMsg.TYPE_ID, TYItemActionSendMsg)
    
    TYItemActionRegister.registerClass(TYItemActionBoxOpen.TYPE_ID, TYItemActionBoxOpen)
    TYItemActionRegister.registerClass(TYItemActionDecroationWear.TYPE_ID, TYItemActionDecroationWear)
    TYItemActionRegister.registerClass(TYItemActionDecroationUnwear.TYPE_ID, TYItemActionDecroationUnwear)
    TYItemActionRegister.registerClass(TYItemActionSwitchTurnOn.TYPE_ID, TYItemActionSwitchTurnOn)
    TYItemActionRegister.registerClass(TYItemActionSwitchTurnOff.TYPE_ID, TYItemActionSwitchTurnOff)
    TYItemActionRegister.registerClass(TYItemActionCheckin.TYPE_ID, TYItemActionCheckin)
    TYItemActionRegister.registerClass(TYItemActionExchange.TYPE_ID, TYItemActionExchange)
    TYItemActionRegister.registerClass(TYItemActionDrop.TYPE_ID, TYItemActionDrop)
    TYItemActionRegister.registerClass(TYItemActionBuy.TYPE_ID, TYItemActionBuy)
    TYItemActionRegister.registerClass(TYItemActionWeixinRedEnvelopGetPassword.TYPE_ID, TYItemActionWeixinRedEnvelopGetPassword)
    TYItemActionRegister.registerClass(TYItemActionWeixinRedEnvelopOpen.TYPE_ID, TYItemActionWeixinRedEnvelopOpen)
    TYItemActionRegister.registerClass(TYItemActionSetGameData.TYPE_ID, TYItemActionSetGameData)
    TYItemActionRegister.registerClass(TYItemActionSkillUse.TYPE_ID, TYItemActionSkillUse)
    TYItemUnitsRegister.registerClass(TYItemUnitsCount.TYPE_ID, TYItemUnitsCount)
    TYItemUnitsRegister.registerClass(TYItemUnitsDay.TYPE_ID, TYItemUnitsDay)
    TYItemUnitsRegister.registerClass(TYItemUnitsCurrentDay.TYPE_ID, TYItemUnitsCurrentDay)
    TYItemUnitsRegister.registerClass(TYItemUnitsCountNDay.TYPE_ID, TYItemUnitsCountNDay)
    TYItemUnitsRegister.registerClass(TYItemUnitsNatureDay.TYPE_ID, TYItemUnitsNatureDay)
    TYItemUnitsRegister.registerClass(TYItemUnitsHour.TYPE_ID, TYItemUnitsHour)
    TYItemUnitsRegister.registerClass(TYItemUnitsTime.TYPE_ID, TYItemUnitsTime)
    TYItemUnitsRegister.registerClass(TYItemUnitsTimeExpiresWeekDay.TYPE_ID, TYItemUnitsTimeExpiresWeekDay)
    TYItemUnitsRegister.registerClass(TYItemUnitsTimeExpiresSunday.TYPE_ID, TYItemUnitsTimeExpiresSunday)
    TYItemUnitsRegister.registerClass(TYItemUnitsCountExpiresToday.TYPE_ID, TYItemUnitsCountExpiresToday)
    
    TYItemKindRegister.registerClass(TYSimpleItemKind.TYPE_ID, TYSimpleItemKind)
    TYItemKindRegister.registerClass(TYBoxItemKind.TYPE_ID, TYBoxItemKind)
    TYItemKindRegister.registerClass(TYMemberCardItemKind.TYPE_ID, TYMemberCardItemKind)
    TYItemKindRegister.registerClass(TYDecroationItemKind.TYPE_ID, TYDecroationItemKind)
    TYItemKindRegister.registerClass(TYSwitchItemKind.TYPE_ID, TYSwitchItemKind)
    TYItemKindRegister.registerClass(TYExchangeItemKind.TYPE_ID, TYExchangeItemKind)
    TYItemKindRegister.registerClass(TYWeixinRedEnvelopPasswordItemKind.TYPE_ID, TYWeixinRedEnvelopPasswordItemKind)
    TYItemKindRegister.registerClass(TYWeixinRedEnvelopItemKind.TYPE_ID, TYWeixinRedEnvelopItemKind)
    TYItemKindRegister.registerClass(TYChestItemKind.TYPE_ID, TYChestItemKind)
    TYItemKindRegister.registerClass(TYSkillItemKind.TYPE_ID, TYSkillItemKind)
    TYAssetKindRegister.registerClass(TYAssetKindChip.TYPE_ID, TYAssetKindChip)
    TYAssetKindRegister.registerClass(TYAssetKindCoupon.TYPE_ID, TYAssetKindCoupon)
    TYAssetKindRegister.registerClass(TYAssetKindCharm.TYPE_ID, TYAssetKindCharm)
    TYAssetKindRegister.registerClass(TYAssetKindExp.TYPE_ID, TYAssetKindExp)
    TYAssetKindRegister.registerClass(TYAssetKindVipBenefits.TYPE_ID, TYAssetKindVipBenefits)
    TYAssetKindRegister.registerClass(TYAssetKindDiamond.TYPE_ID, TYAssetKindDiamond)
    TYAssetKindRegister.registerClass(TYAssetKindEntity.TYPE_ID, TYAssetKindEntity)
    TYAssetKindRegister.registerClass(TYAssetKindCash.TYPE_ID, TYAssetKindCash)
    TYAssetKindRegister.registerClass(TYAssetKindDifangFangka.TYPE_ID, TYAssetKindDifangFangka)
    
    from hall.entity import hallsubmember
    hallsubmember._registerClasses()
    
def itemIdToAssetId(itemKindId):
    return TYAssetKindItem.buildKindIdByItemKindId(itemKindId)

ITEM_MEMBER_KIND_ID = 88 # 会员
ITEM_MEMBER_NEW_KIND_ID = 1196#89 # 会员
ITEM_NEWER_GIFT_KIND_ID = 1001 # 新手礼包
ITEM_FIRST_RECHARGE_GIFT_KIND_ID = 1002 # 首冲礼包
ITEM_ALIPAY_GIFT_KIND_ID = 1003 # 支付宝礼包
ITEM_NEWER_RAFFLE_GIFT_KIND_ID = 1004 # 新手抽奖礼包
ITEM_NEWER_RAFFLE_2DAY_GIFT_KIND_ID = 1005 # 新手次日抽奖礼包
ITEM_NEWER_RAFFLE_3DAY_GIFT_KIND_ID = 1006 # 新手三日抽奖礼包
ITEM_CARDMATCH_KIND_ID = 1007 # 参赛券
ITEM_HERO_KIND_ID = 1008 # 英雄帖
ITEM_NEIHAN_GIFT_KIND_ID = 1009 # 内涵玩家专属礼包
ITEM_S6_GIFT_KIND_ID = 1010 # 三星S6抽奖礼包
ITEM_TEHUI_GIFT_BIG_KIND_ID = 1011 # 特惠大礼包
ITEM_TEHUI_GIFT_KIND_ID = 1012 # 特惠礼包
ITEM_NEWER_GIFT_NEW_KIND_ID = 1013 # 新手礼包

ITEM_TEXAS_MTT_TICKET_CHIP_10W_KIND_ID = 1029 # 德州门票 10万金币赛
ITEM_TEXAS_MTT_TICKET_CHIP_50W_KIND_ID = 1030 # 德州门票 50万金币赛
ITEM_TEXAS_MTT_TICKET_CHIP_200W_KIND_ID = 1031 # 德州门票 200万金币赛
ITEM_TEXAS_MTT_TICKET_CHIP_500W_KIND_ID = 1032 # 德州门票 500万金币赛
ITEM_TEXAS_MTT_TICKET_HUAFEI_1K_KIND_ID = 1033 # 德州门票 千元话费赛
ITEM_TEXAS_MTT_TICKET_IPHONE6S_KIND_ID = 1034 # 德州门票 iphone6S大奖赛
ITEM_TEXAS_MTT_TICKET_CHIP_2KW_KIND_ID = 1035 # 德州门票 2000万金币赛

ITEM_CROWN_MONTHCARD_KIND_ID = 1196 #28元贵族月卡
ITEM_HONOR_MONTHCARD_KIND_ID = 1282 #荣耀月卡
ITEM_ZIYUNYING_MONTHCARD_KIND_ID = 1313 #自运营月卡

ITEM_RENAME_CARD_KIND_ID = 2001 # 改名卡
ITEM_CARD_NOTE_KIND_ID = 2003 # 记牌器
ITEM_LOTTERY_CARD_ID = 4167 # 抽奖卡
ITEM_CUSTOM_SKIN_ID = 4224#换肤卡  自定义皮肤

ITEM_MEMBER_BORDER_GOLD_KIND_ID = 4128 # 会员头像框A
ITEM_MEMBER_BORDER_SILVER_KIND_ID = 4129 # 会员头像框B
ITEM_MOUTHLY_CARD_KIND_ID = 4162 # 德州至尊月卡(对,至尊)

ITEM_VIP_LABEL_1 = 4001 # VIP标识

ASSET_CHIP_KIND_ID = 'user:chip'
ASSET_COUPON_KIND_ID = 'user:coupon'
ASSET_CHARM_KIND_ID = 'user:charm'
ASSET_EXP_KIND_ID = 'user:exp'
ASSET_DIAMOND_KIND_ID = 'user:diamond'
ASSET_ASSISTANCE_KIND_ID = 'game:assistance'

ASSET_ITEM_NEWER_GIFT_KIND_ID = itemIdToAssetId(ITEM_NEWER_GIFT_KIND_ID)
ASSET_ITEM_MEMBER_KIND_ID = itemIdToAssetId(ITEM_MEMBER_KIND_ID)
ASSET_ITEM_FIRST_RECHARGE_GIFT_KIND_ID = itemIdToAssetId(ITEM_FIRST_RECHARGE_GIFT_KIND_ID)
ASSET_ITEM_MEMBER_NEW_KIND_ID = itemIdToAssetId(ITEM_MEMBER_NEW_KIND_ID)
ASSET_RENAME_CARD_KIND_ID = itemIdToAssetId(ITEM_RENAME_CARD_KIND_ID)
ASSET_ITEM_CARD_NOT_KIND_ID = itemIdToAssetId(ITEM_CARD_NOTE_KIND_ID)
ASSET_ITEM_LOTTERY_CARD_ID = itemIdToAssetId(ITEM_LOTTERY_CARD_ID)
ASSET_ITEM_CUSTOM_SKIN_CARD_ID = itemIdToAssetId(ITEM_CUSTOM_SKIN_ID)

ASSET_ITEM_CROWN_MONTHCARD_KIND_ID = itemIdToAssetId(ITEM_CROWN_MONTHCARD_KIND_ID)
ASSET_ITEM_HONOR_MONTHCARD_KIND_ID = itemIdToAssetId(ITEM_HONOR_MONTHCARD_KIND_ID)
ASSET_ITEM_ZIYUNYING_MONTHCARD_KIND_ID = itemIdToAssetId(ITEM_ZIYUNYING_MONTHCARD_KIND_ID)

itemSystem = TYItemSystem()
_inited = False
    
def _reloadConf():
    conf = hallconf.getItemConf()
    itemSystem.reloadConf(conf)
    
def _onConfChanged(event):
    if _inited and event.isChanged('game:9999:item:0'):
        ftlog.debug('hallitem._onConfChanged')
        _reloadConf()

__timingItems = set([2003, 88, 8075, 4101, 4102, 4103, 4104, 4105, 4106, 4107, 4108, 4109, 4110, 
                     4111, 4112, 4113, 4114, 4115, 4116, 4117, 4118, 4119, 4120, 4121, 4122, 4123, 
                     4124, 4125, 4126, 4127, 4128, 4129, 4130, 4131, 4214])
    
def _tranformItems(gameId, userId, clientId, userBag):
    try:
        datas = pkgamedata.getAllAttrs(userId, gameId, 'item')
        
        ftlog.debug('hallitem._tranformItems gameId=', gameId,
                   'userId=', userId,
                   'clientId=', clientId,
                   'datas=', None if datas is None else [v for i,v in enumerate(datas) if i % 2 == 0])

        if not datas:
            return False
        
        for i in xrange(len(datas)/2):
            x = i*2
            # fid,  utime 更新时间 count道具个数 state 状态
            dataBytes = strutil.unicode2Ascii(datas[x+1])
            _fid, utime, count, _state = struct.unpack("3iB", dataBytes)
            
            timestamp = pktimestamp.getCurrentTimestamp()
            kindId = int(datas[x])
            if kindId == 0:
                continue
            
            if kindId in __timingItems:
                now_day = datetime.now().date()
                uday = datetime.fromtimestamp(utime).date()
                count -= (now_day - uday).days
                if count <= 0:
                    ftlog.debug('hallitem._tranformItems expires gameId=', gameId,
                               'userId=', userId,
                               'clientId=', clientId,
                               'kindId=', kindId,
                               'count=', count,
                               'utime=', datetime.fromtimestamp(utime).strftime('%Y-%m-%d %H:%M:%S'))
                    continue

            itemKind = itemSystem.findItemKind(kindId)
            if not itemKind:
                ftlog.debug('hallitem._tranformItems unknownKind gameId=', gameId,
                           'userId=', userId,
                           'clientId=', clientId,
                           'kindId=', kindId,
                           'count=', count,
                           'utime=', datetime.fromtimestamp(utime).strftime('%Y-%m-%d %H:%M:%S'))
                continue

            ftlog.debug('hallitem._tranformItems transOk gameId=', gameId,
                       'userId=', userId,
                       'clientId=', clientId,
                       'kindId=', kindId,
                       'count=', count,
                       'utime=', datetime.fromtimestamp(utime).strftime('%Y-%m-%d %H:%M:%S'))
            userBag.addItemUnitsByKind(gameId, itemKind,  count, timestamp,
                                       0, "DATA_TRANSFER", 0)
    except:
        ftlog.error('hallitem._tranformItems exception gameId=', gameId,
                    'userId=', userId,
                    'clientId=', clientId)
    return True

def _getInitItemsByClientId(userId, clientId):
    _, clientVer, _ = strutil.parseClientId(clientId)
    templateName = None
    clientItemConf = hallconf.getClientItemConf(clientId)
    if clientItemConf:
        templateName = clientItemConf.get('init.item.templateName')
    
    if not templateName:
        # 先找default_hall_gameId
        hallGameId = strutil.getGameIdFromHallClientId(clientId)
        templateName = 'default_hall_%s' % (hallGameId) if clientVer >= 3.5 else 'default_old_hall_%s' % (hallGameId)
    
    initItems = itemSystem.getInitItemsByTemplateName(templateName)
    if initItems is None:
        templateName = 'default' if clientVer >= 3.5 else 'default_old'
        initItems = itemSystem.getInitItemsByTemplateName(templateName)
    return initItems

def _initUserBag(gameId, userId, clientId, userBag):
    initItems = _getInitItemsByClientId(userId, clientId) or []
    timestamp = pktimestamp.getCurrentTimestamp()
    for itemKind, count in initItems:
        userBag.addItemUnitsByKind(gameId, itemKind, count, timestamp, 0, 'USER_CREATE', 0)
    ftlog.debug('hallitem._initUserBag addItemUnitsByKind gameId=', gameId,
               'userId=', userId,
               'initItems=', [(k.kindId, c) for k, c in initItems])
    return userBag

def _onUserLogin(gameId, userId, clientId, isCreate, isDayfirst):
    from hall.entity import hallsubmember
    ftlog.debug('hallitem._onUserLogin gameId=', gameId,
               'userId=', userId,
               'clientId=', clientId,
               'isCreate=', isCreate,
               'isDayfirst', isDayfirst)
    if not _inited:
        return
    
    timestamp = pktimestamp.getCurrentTimestamp()
    userAssets = itemSystem.loadUserAssets(userId)
    userBag = userAssets.getUserBag()
    if isCreate:
        pkgamedata.setGameAttr(userId, HALL_GAMEID, 'flag.item.trans', 1)
        _initUserBag(gameId, userId, clientId, userBag)
    else:
        if pkgamedata.setnxGameAttr(userId, HALL_GAMEID, 'flag.item.trans', 1) == 1:
            if not _tranformItems(gameId, userId, clientId, userBag):
                _initUserBag(gameId, userId, clientId, userBag)
        hallsubmember.checkSubMember(gameId, userId, timestamp, 'LOGIN_CHECK_SUBMEM', 0, userAssets)
    userBag.processWhenUserLogin(gameId, isDayfirst, timestamp)
    
def _initialize():
    ftlog.debug('item initialize begin')
    global itemSystem
    global _inited
    if not _inited:
        _inited = True
        itemSystem = TYItemSystemImpl(TYItemDataDaoImpl())
        _registerClasses()
        _reloadConf()
        pkeventbus.globalEventBus.subscribe(EventConfigure, _onConfChanged)
        ftlog.debug('TGHall=', TGHall, 'type=', type(TGHall))
    ftlog.debug('item initialize end')

    
def getAssetKindTupleList(content):
    assetKindTupleList = []
    contentItemList = content.getItems()
    for contentItem in contentItemList:
        assetKind = itemSystem.findAssetKind(contentItem.assetKindId)
        if assetKind:
            assetKindTupleList.append((assetKind, contentItem.count))
    return assetKindTupleList
    
def _getMemberCardCheckinChip(memberCardKind):
    return TYContentUtils.getMinFixedAssetCount(memberCardKind.getCheckinContent(), ASSET_CHIP_KIND_ID)

def getMemberCardCheckinChip():
    memberCardKind = itemSystem.findItemKind(ITEM_MEMBER_NEW_KIND_ID)
    if not memberCardKind:
        memberCardKind = itemSystem.findItemKind(ITEM_MEMBER_KIND_ID)
    if memberCardKind:
        return _getMemberCardCheckinChip(memberCardKind)
    return 0

def getMemberInfo(userId, timestamp):
    userBag = itemSystem.loadUserAssets(userId).getUserBag()
    memberCardItemOld = userBag.getItemByKindId(ITEM_MEMBER_KIND_ID)
    memberCardItemNew = userBag.getItemByKindId(ITEM_MEMBER_NEW_KIND_ID)
    remainDaysOld = remainDaysNew = 0
    
    if memberCardItemOld and not memberCardItemOld.isExpires(timestamp):
        remainDaysOld = memberCardItemOld.balance(timestamp)
    if memberCardItemNew and not memberCardItemNew.isExpires(timestamp):
        remainDaysNew = memberCardItemNew.balance(timestamp)
        
    memberItem = memberCardItemOld if remainDaysOld > remainDaysNew else memberCardItemNew
    remainDays = remainDaysOld if remainDaysOld > remainDaysNew else remainDaysNew
    
    if memberItem:
        return remainDays, _getMemberCardCheckinChip(memberItem.itemKind)
    
    return 0, getMemberCardCheckinChip()
 
def buildContent(assetKindId, count, needUnits=True):
    assetKind = itemSystem.findAssetKind(assetKindId)
    if assetKind:
        return assetKind.buildContent(count, needUnits)
    return ''

def buildContents(contentItems, needUnits=True):
    contents = []
    for contentItem in contentItems:
        contents.append(buildContent(contentItem.assetKindId, contentItem.count, needUnits))
    return contents

def buildContentsString(contentItems, needUnits=True):
    contents = buildContents(contentItems, needUnits)
    return ','.join(contents)

def buildItemInfo(assetKindId, count, needUnits):
    assetKind = itemSystem.findAssetKind(assetKindId)
    if assetKind:
        return {
            'itemId':assetKindId,
            'count':count,
            'name':assetKind.displayName,
            'url':assetKind.pic
        }
    return None
    
def buildItemInfoList(items, needUnits=True):
    ret = []
    for item in items:
        info = buildItemInfo(item.assetKindId, item.count, needUnits)
        if info:
            ret.append(info)
    return ret
        
def getTexasMouthlyCardInfo(userId, timestamp):
    userBag = itemSystem.loadUserAssets(userId).getUserBag()
    mouthlyCard = userBag.getItemByKindId(ITEM_MOUTHLY_CARD_KIND_ID)
    remainDays = 0
    
    if mouthlyCard and not mouthlyCard.isExpires(timestamp):
        remainDays = mouthlyCard.balance(timestamp)
        
    return remainDays
