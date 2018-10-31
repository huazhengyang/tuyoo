# -*- coding=utf-8
'''
Created on 2015年8月14日

@author: zhaojiangang
'''

import random
from sre_compile import isstring

import freetime.util.log as ftlog
from hall.entity import hallstore, hallitem, hallvip, hallconf, datachangenotify
from poker.entity.biz.confobj import TYConfable, TYConfableRegister
from poker.entity.biz.exceptions import TYBizConfException, TYBizException
from poker.entity.configure import gdata
from poker.entity.dao import userchip
from poker.entity.events.tyevent import EventConfigure
import poker.entity.events.tyeventbus as pkeventbus
import poker.util.timestamp as pktimestamp

class FlipCardException(TYBizException):
    def __init__(self, errorCode, message):
        super(FlipCardException, self).__init__(errorCode, message)
    
DEFAULT_ROOM_MIN_CHIP = 60000

class FlipCardContext(object):
    def __init__(self, gameId, userId, clientId, roomId):
        self.gameId = gameId
        self.userId = userId
        self.clientId = clientId
        self.roomId = roomId
        self._userAllChip = None
        self._roomMinChip = None
        self._userVip = None
        
    @property
    def userAllChip(self):
        if self._userAllChip is None:
            self._userAllChip = userchip.getUserChipAll(self.userId)
        return self._userAllChip
    
    @property
    def roomMinChip(self):
        if self._roomMinChip is None:
            self._roomMinChip = self.getRoomMinChip(self.roomId)
        return self._roomMinChip
           
    @property
    def userVip(self):
        if self._userVip is None:
            self._userVip = hallvip.userVipSystem.getUserVip(self.userId)
        return self._userVip
         
    @property
    def minBuyChip(self):
        if self.roomMinChip > self.userAllChip:
            return self.roomMinChip - self.userAllChip
        return 0
    
    @classmethod
    def getRoomMinChip(self, roomId):
        return 10000
        roomDefine = gdata.roomIdDefineMap().get(self.roomId)
        if not roomDefine:
            return DEFAULT_ROOM_MIN_CHIP
        return roomDefine.configer.get('minCoin', DEFAULT_ROOM_MIN_CHIP)
    
class FlipableCard(TYConfable):
    def __init__(self, desc='', tips=''):
        self.desc = desc
        self.tips = tips
    
    def flip(self, ctx):
        '''
        @return: FlippedCard
        '''
        raise NotImplemented()
    
    def decodeFromDict(self, d):
        self.desc = d.get('desc', '')
        if not isstring(self.desc):
            raise TYBizConfException(d, 'FlipableCard.desc must be string')
        self.tips = d.get('tips', '')
        if not isstring(self.tips):
            raise TYBizConfException(d, 'FlipableCard.tips must be string')
        self._decodeFromDictImpl(d)
        return self
    
    def _decodeFromDictImpl(self, d):
        pass
    
class FlipableCardProduct(FlipableCard):
    TYPE_ID = 'product'
    def __init__(self):
        super(FlipableCardProduct, self).__init__()
        self.shelvesName = None
        self.minChip = None
        self.number = None
        
    def flip(self, ctx):
        product, _ = hallstore.findProductByContains(ctx.gameId, ctx.userId, ctx.clientId,
                                                     [self.shelvesName], None,
                                                     hallitem.ASSET_CHIP_KIND_ID,
                                                     ctx.minBuyChip)
        if product:
            return FlippedCardProduct(self, product)
        return None
    
    def _decodeFromDictImpl(self, d):
        self.shelvesName = d.get('shelves')
        if not isstring(self.shelvesName):
            raise TYBizConfException(d, 'FlipableCardProduct.shelves must be string')
        self.number = d.get('number', 0)
        if not isinstance(self.number, int):
            raise TYBizConfException(d, 'FlipableCardProduct.number must be int')
        self.minChip = d.get('minChip', 0)
        if not isinstance(self.minChip, int):
            raise TYBizConfException(d, 'FlipableCardProduct.minChip must be int')
        
class FlipableCardAsset(FlipableCard):
    TYPE_ID = 'asset'
    def __init__(self):
        super(FlipableCardAsset, self).__init__()
        self.assetKind = None
        self.start = None
        self.end = None
        self.step = None
    
    def flip(self, ctx):
        count = self.randomCount()
        return FlippedCardAsset(self, count)
    
    def randomCount(self):
        return random.randrange(self.start, self.end + 1, self.step)

    def _decodeFromDictImpl(self, d):
        assetKindId = d.get('assetKindId')
        if not isstring(assetKindId):
            raise TYBizConfException(d, 'assetKindId must be string')
        
        assetKind = hallitem.itemSystem.findAssetKind(assetKindId)
        if not assetKind:
            raise TYBizConfException(d, 'Unknown itemKind %s' % (assetKindId))
        
        self.assetKind = assetKind
        
        self.start = d.get('start')
        if not isinstance(self.start, int) or self.start <= 0:
            raise TYBizConfException(d, 'FlipableCardItem.start must be int > 0')
        self.end = d.get('end')
        if not isinstance(self.end, int) or self.end <= 0:
            raise TYBizConfException(d, 'FlipableCardItem.end must be int > 0')
        self.step = d.get('step', 1)
        if not isinstance(self.step, int) or self.step <= 0:
            raise TYBizConfException(d, 'FlipableCardItem.step must be int > 0')
        if self.start > self.end:
            raise TYBizConfException(d, 'end must ge than start %s %s' % (self.start, self.end))
        
class FlipableCardRegister(TYConfableRegister):
    _typeid_clz_map = {
        FlipableCardAsset.TYPE_ID:FlipableCardAsset,
        FlipableCardProduct.TYPE_ID:FlipableCardProduct
    }
    
class FlipCardPolicy(object):
    def __init__(self):
        # item = (min, max, FlipableCard)
        self._flipableCards = []
        self._totalWeight = 0
    
    def addFlipableCard(self, weight, flipableCard):
        nextWeight = self._totalWeight + int(weight * 100)
        self._flipableCards.append((self._totalWeight, nextWeight, flipableCard))
        self._totalWeight = nextWeight

    @property
    def totalWeight(self):
        return self._totalWeight
    
    def randomCard(self):
        assert(len(self._flipableCards) > 0)
        value = random.randint(0, self._totalWeight - 1)
        for minValue, maxValue, flipableCard in self._flipableCards:
            if value >= minValue and value < maxValue:
                return flipableCard
        ftlog.error('FlipCardPolicy.randomCard return None')
        return None
        
class FlipCardCondition(TYConfable):
    def check(self, ctx):
        raise NotImplemented()

class FlipCardConditionMinBuyChip(FlipCardCondition):
    TYPE_ID = 'minBuyChip'
    def __init__(self):
        super(FlipCardConditionMinBuyChip, self).__init__()
        self.start = None
        self.end = None
        
    def check(self, ctx):
        minBuyChip = ctx.minBuyChip
        return ((self.start < 0 or minBuyChip >= self.start) 
                and (self.end < 0 or minBuyChip <= self.end))

    def decodeFromDict(self, d):
        self.start = d.get('start', -1)
        if not isinstance(self.start, int) or self.start < -1:
            raise TYBizConfException(d, 'Unknown FlipCardConditionChip.start must be int >= -1')
        
        self.end = d.get('end', -1)
        if not isinstance(self.end, int) or self.end < -1:
            raise TYBizConfException(d, 'Unknown FlipCardConditionChip.end must be int >= -1')
        
        if self.end != -1 and self.start > self.end:
            raise TYBizConfException(d, 'Unknown FlipCardConditionChip.end must >= start')
        return self
    
class FlipCardConditionVipLevel(FlipCardCondition):
    TYPE_ID = 'vipLevel'
    def __init__(self):
        super(FlipCardConditionVipLevel, self).__init__()
        self.start = None
        self.end = None
        
    def check(self, ctx):
        level = ctx.userVip.vipLevel.level
        return ((self.start < 0 or level >= self.start) 
                and (self.end < 0 or level <= self.end))
    
    def decodeFromDict(self, d):
        self.start = d.get('start', -1)
        if not isinstance(self.start, int) or self.start < -1:
            raise TYBizConfException(d, 'Unknown FlipCardConditionVipLevel.start must be int >= -1')
        
        self.end = d.get('end', -1)
        if not isinstance(self.end, int) or self.end < -1:
            raise TYBizConfException(d, 'Unknown FlipCardConditionVipLevel.end must be int >= -1')
        
        if self.end != -1 and self.start > self.end:
            raise TYBizConfException(d, 'Unknown FlipCardConditionVipLevel.end must >= start')
        return self
    
class FlipCardConditionRegister(TYConfableRegister):
    _typeid_clz_map = {
        FlipCardConditionMinBuyChip.TYPE_ID:FlipCardConditionMinBuyChip,
        FlipCardConditionVipLevel.TYPE_ID:FlipCardConditionVipLevel
    }

class FlipCardPolicyTable(object):
    def __init__(self):
        self._table = []
        
    def addPolicy(self, conditions, policy):
        self._table.append((conditions, policy))
        
    def selectPolicy(self, ctx):
        assert(len(self._table) > 0)
        for conditions, policy in self._table:
            if self.checkConditions(ctx, conditions):
                return policy
        return self._table[0][1]
        
    def checkConditions(self, ctx, conditions):
        for condition in conditions:
            if not condition.check(ctx):
                return False
        return True
    
class FlippedCard(object):
    def __init__(self, flipableCard):
        self.flipableCard = flipableCard

class FlippedCardAsset(FlippedCard):
    def __init__(self, flipableCard, count):
        assert(isinstance(flipableCard, FlipableCardAsset))
        super(FlippedCardAsset, self).__init__(flipableCard)
        self.count = count
    
    @property
    def assetKind(self):
        return self.flipableCard.assetKind
    
    def __str__(self):
        return '%s%s%s' % (self.count, self.assetKind.units, self.assetKind.displayName) 
    
    def __unicode__(self):
        return u'%s%s%s' % (self.count, self.assetKind.units, self.assetKind.displayName) 
    
class FlippedCardProduct(FlippedCard):
    def __init__(self, flipableCard, product):
        assert(isinstance(flipableCard, FlipableCardProduct))
        super(FlippedCardProduct, self).__init__(flipableCard)
        self.product = product
    
    def __str__(self):
        return u'%s:%s' % (self.product.displayName, self.product.productId) 
    
    def __unicode__(self):
        return u'%s:%s' % (self.product.displayName, self.product.productId) 
    
_flipCardPolicyTable = None
_paddingsCardPolicy = None
_stringsMap = {}
_inited = False

def _reloadConf():
    global _flipCardPolicyTable
    global _paddingsCardPolicy
    global _stringsMap
    
    conf = hallconf.getFlipCardLuckConf()
    
    stringsMap = conf.get('strings', {})
    if not isinstance(stringsMap, dict):
        raise TYBizConfException(conf, 'strings must be dict')
    
    flipCardPolicyTable = FlipCardPolicyTable()
    table = conf.get('table')
    if not isinstance(table, list) or not table:
        raise TYBizConfException(conf, 'conf.table must be not empty list')
    for policyConf in table:
        conditions = FlipCardConditionRegister.decodeList(policyConf.get('conditions', []))
        policy = FlipCardPolicy()
        for cardConf in policyConf.get('randoms'):
            weight = cardConf.get('weight')
            if not isinstance(weight, (int, float)) or weight < 0:
                raise TYBizConfException(cardConf, 'weight must be int or float')
            card = FlipableCardRegister.decodeFromDict(cardConf)
            policy.addFlipableCard(weight, card)
        if policy.totalWeight <= 0:
            raise TYBizConfException(policyConf, 'totalWeight must be > 0')
        flipCardPolicyTable.addPolicy(conditions, policy)
        
    paddingsPolicy = FlipCardPolicy()
    paddings = conf.get('paddings')
    if not isinstance(paddings, list) or not paddings:
        raise TYBizConfException(conf, 'conf.paddings must be not empty list')
    for cardConf in paddings:
        weight = cardConf.get('weight')
        if not isinstance(weight, (int, float)) or weight < 0:
            raise TYBizConfException(cardConf, 'weight must be int or float')
        card = FlipableCardRegister.decodeFromDict(cardConf)
        paddingsPolicy.addFlipableCard(weight, card)
        
    if paddingsPolicy.totalWeight <= 0:
        raise TYBizConfException(policyConf, 'paddings.totalWeight must be > 0')
    
    _flipCardPolicyTable = flipCardPolicyTable
    _paddingsCardPolicy = paddingsPolicy
    _stringsMap = stringsMap
    
    ftlog.debug('hallflipcardluck._reloadConf successed')
    
def _onConfChanged(event):
    if _inited and event.isChanged('game:9999:flipcardluck:0'):
        ftlog.debug('hallflipcardluck._onConfChanged')
        _reloadConf()
        
def _initialize():
    ftlog.debug('hallflipcardluck._initialize begin')
    global vipSystem
    global userVipSystem
    global _inited
    if not _inited:
        _inited = True
        _reloadConf()
        pkeventbus.globalEventBus.subscribe(EventConfigure, _onConfChanged)
    ftlog.debug('hallflipcardluck._initialize end')
    
def _paddingCard(ctx, count):
    '''
    获取填充的牌
    @return: list<(FlippedCard, count)>
    '''
    flippedCardList = []
    for _ in xrange(count):
        flippedCard = _paddingsCardPolicy.randomCard().flip(ctx)
        if flippedCard:
            flippedCardList.append(flippedCard)
        else:
            ftlog.error('hallflipcardluck._paddingCard no card')
            break
    return flippedCardList

def getString(key, defVal):
    return _stringsMap.get(key, defVal)

def flipCard(gameId, userId, clientId, roomId, paddingsCount):
    '''
    翻牌
    @return: flippedCard, paddingsCardList
    '''
    timestamp = pktimestamp.getCurrentTimestamp()
    ctx = FlipCardContext(gameId, userId, clientId, roomId)
    
    flipableCard = _flipCardPolicyTable.selectPolicy(ctx).randomCard()
    if ftlog.is_debug():
        ftlog.debug('FlipCardService.flipCard gameId=', gameId,
                    'userId=', userId,
                    'roomId=', roomId,
                    'roomMinChip=', ctx.roomMinChip,
                    'userAllChip=', ctx.userAllChip,
                    'userVipLevel=', ctx.userVip.vipLevel.level,
                    'minBuyChip=', ctx.minBuyChip,
                    'flipableCard=', flipableCard)

    flippedCard = flipableCard.flip(ctx)
    if not flippedCard:
        ftlog.debug('FlipCardService.flipCard gameId=', gameId,
                    'userId=', userId,
                    'roomId=', roomId,
                    'roomMinChip=', ctx.roomMinChip,
                    'userAllChip=', ctx.userAllChip,
                    'userVipLevel=', ctx.userVip.vipLevel.level,
                    'minBuyChip=', ctx.minBuyChip,
                    'flipableCard=', flipableCard,
                    'err=', 'NoFlippedCard')
        raise FlipCardException(-1, 'System error')
    
    if isinstance(flippedCard, FlippedCardAsset):
        userAssets = hallitem.itemSystem.loadUserAssets(userId)
        userAssets.addAsset(gameId, flippedCard.assetKind.assetKindId,
                            timestamp, 'ACTIVITY_FAN_PAI', 0)
        if flippedCard.assetKind.keyForChangeNotify:
            datachangenotify.sendDataChangeNotify(gameId, userId, flippedCard.assetKind.keyForChangeNotify)
    paddingsCardList = _paddingCard(ctx, paddingsCount)
    
    if ftlog.is_debug():
        paddingsCardsStrs = []
        for paddingsCard in paddingsCardList:
            paddingsCardsStrs.append(str(paddingsCard))
        ftlog.debug('FlipCardService.flipCard gameId=', gameId,
                    'userId=', userId,
                    'roomId=', roomId,
                    'roomMinChip=', ctx.roomMinChip,
                    'userAllChip=', ctx.userAllChip,
                    'userVipLevel=', ctx.userVip.vipLevel.level,
                    'minBuyChip=', ctx.minBuyChip,
                    'flipableCard=', flipableCard,
                    'paddingsCards', paddingsCardsStrs)
        
    while len(paddingsCardList) < paddingsCount:
        paddingsCardList.append(flippedCard)
    
    return flippedCard, paddingsCardList


