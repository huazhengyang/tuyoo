# -*- coding=utf-8
'''
Created on 2015年7月6日

@author: zhaojiangang
'''
from datetime import datetime
import json
import random
from sre_compile import isstring

import freetime.util.log as ftlog
from hall.entity import hallitem, datachangenotify, hallconf
from poker.entity.biz.content import TYContentItem, TYContentItemGenerator
from poker.entity.biz.exceptions import TYBizConfException
from poker.entity.biz.item.item import TYAssetUtils
from poker.entity.configure import configure as pkconfigure
from poker.entity.dao import gamedata as pkgamedata
import poker.entity.dao.userdata as pkuserdata
from poker.entity.events.tyevent import EventConfigure
import poker.entity.events.tyeventbus as pkeventbus
import poker.util.timestamp as pktimestamp
from poker.entity.biz.message import message as pkmessage
from poker.util import strutil
from dizhu.entity.dizhuconf import DIZHU_GAMEID

class DizhuFlipCardConfException(TYBizConfException):
    def __init__(self, conf, message):
        super(DizhuFlipCardConfException, self).__init__(-1, message)
        self.conf = conf
        
    def __str__(self):
        return '%s:%s:%s' % (self.errorCode, self.message, self.conf)
    
    def __unicode__(self):
        return u'%s:%s:%s' % (self.errorCode, self.message, self.conf)
    
class FlipableCard(object):
    def __init__(self, contentItemGenerator):
        self._contentItemGenerator = contentItemGenerator
    
    def flip(self):
        return self._contentItemGenerator.generate()
    
class SelectCardPolicy(object):
    def selectCard(self):
        '''
        选择一张牌
        '''
        raise NotImplemented()
    
class SelectCardPolicyRandom(SelectCardPolicy):
    def __init__(self):
        # item=(minValue, maxValue, card)
        self._cards = []
        # 当前最大值
        self._maxValue = 0
        
    def addCard(self, weight, card):
        assert(isinstance(card, FlipableCard))
        nextMaxValue = self._maxValue + weight
        self._cards.append((self._maxValue, nextMaxValue, card))
        self._maxValue = nextMaxValue
    
    def selectCard(self):
        assert(self._maxValue > 0)
        value = random.randint(0, self._maxValue-1)
        for minValue, maxValue, card in self._cards:
            if value >= minValue and value < maxValue:
                return card
        return None
    
    @classmethod
    def decodeFromDict(cls, d):
        ret = SelectCardPolicyRandom()
        randomCards = d.get('randoms')
        for card in randomCards:
            weight = card.get('weight')
            if not isinstance(weight, int) or weight < 0:
                raise DizhuFlipCardConfException(card, 'weight must be int')
            item = card.get('item')
            ret.addCard(weight, FlipableCard(TYContentItemGenerator.decodeFromDict(item)))
        return ret
    
class DizhuFlipCardStatus(object):
    def __init__(self, flipTime, itemMap, paddings):
        # 翻牌时间
        self.flipTime = flipTime
        # 翻到得牌，key=index, value=TYContentItem
        self.itemMap = itemMap
        # 填充的牌，item=TYContentItem
        self.paddings = paddings
        # 最大翻牌次数
        self.maxFlipCount = 0
        # 连续登陆天数
        self.nslogin = 0
        
    def findItemByIndex(self, index):
        return self.itemMap.get(index)
    
    def addItem(self, index, item):
        assert(isinstance(item, TYContentItem))
        assert(self.findItemByIndex(index) is None)
        self.itemMap[index] = item

    def getCanFlipCount(self):
        return min(self.maxFlipCount, self.nslogin+1)
           
    def getRemFlipCount(self):
        return max(0, self.getCanFlipCount() - len(self.itemMap))
    
class DizhuFlipCardStatusDao(object):
    def loadStatus(self, userId):
        try:
            itemMap = {}
            paddingList = []
            d = pkgamedata.getGameAttrJson(userId, 6, 'flipcard')
            if d:
                flipTime = int(d['ut'])
                items = d.get('items', [])
                for item in items:
                    itemMap[item['idx']] = TYContentItem(item['assetId'], item['count'])
                paddings = d.get('paddings', [])
                for item in paddings:
                    paddingList.append(TYContentItem(item['assetId'], item['count']))
                return DizhuFlipCardStatus(flipTime, itemMap, paddingList) 
        except:
            ftlog.error()
        return None
    
    def saveStatus(self, userId, status):
        d = {'ut':status.flipTime}
        if status.itemMap:
            items = []
            for index, item in status.itemMap.iteritems():
                items.append({'idx':index, 'assetId':item.assetKindId, 'count':item.count})
            d['items'] = items
        if status.paddings:
            items = []
            for item in status.paddings:
                items.append({'assetId':item.assetKindId, 'count':item.count})
            d['paddings'] = items
        jstr = json.dumps(d)
        pkgamedata.setGameAttr(userId, 6, 'flipcard', jstr)
    
class DizhuFlipCard(object):
    def loadStatus(self, userId, timestamp=None):
        raise NotImplemented()
    
    def flipCard(self, userId, index, timestamp=None):
        raise NotImplemented()
    
class DizhuFlipCardImpl(DizhuFlipCard):
    def __init__(self, dao):
        # item = (startRegDays, stopRegDays, SelectCardPolicy)
        self._policies = None
        # 填充策略
        self._paddingPolicy = None
        # 最多翻牌次数
        self._maxFlipCount = 3
        # 
        self._rewardMail = None
        # 
        self._dao = dao

    def reloadConf(self, conf):
        flipPolicies = conf.get('flipPolicies')
        policies = []
        for policyConf in flipPolicies:
            registerDays = policyConf.get('registerDays')
            if not registerDays or not isinstance(registerDays, dict):
                raise DizhuFlipCardConfException(policyConf, 'registerDays must be dict')
            startRegDays = registerDays.get('start')
            if not isinstance(startRegDays, int) or startRegDays < -1:
                raise DizhuFlipCardConfException(policyConf, 'registerDays.start must be int >= -1')
            stopRegDays = registerDays.get('stop')
            if not isinstance(stopRegDays, int) or stopRegDays < -1:
                raise DizhuFlipCardConfException(policyConf, 'registerDays.stop must be int >= -1')
            if stopRegDays != -1 and stopRegDays < startRegDays:
                raise DizhuFlipCardConfException(policyConf, 'registerDays.start must be >= stop')
            policy = SelectCardPolicyRandom.decodeFromDict(policyConf)
            policies.append((startRegDays, stopRegDays, policy))
        
        paddings = conf.get('paddings')
        if not isinstance(paddings, dict):
            raise DizhuFlipCardConfException(policyConf, 'paddings must be dict')
        paddingsPolicy = SelectCardPolicyRandom.decodeFromDict(paddings)
        rewardMail = conf.get('rewardMail', '')
        if not isstring(rewardMail):
            raise DizhuFlipCardConfException(conf, 'rewardMail must be string')
        
        self._rewardMail = rewardMail
        self._policies = policies
        self._paddingPolicy = paddingsPolicy
        
        ftlog.debug('DizhuFlipCardImpl.reloadConf successed conf=', conf)
        
    def loadStatus(self, userId, timestamp=None):
        if timestamp is None:
            timestamp = pktimestamp.getCurrentTimestamp()
        status = self._dao.loadStatus(userId)
        if (not status
            or (pktimestamp.getDayStartTimestamp(status.flipTime)
                != pktimestamp.getDayStartTimestamp(timestamp))):
            status = DizhuFlipCardStatus(timestamp, {}, [])
        status.maxFlipCount = self._maxFlipCount
        status.nslogin = pkgamedata.getGameAttrInt(userId, 6, 'nslogin')
        return status
    
    def flipCard(self, userId, index, timestamp=None):
        if timestamp is None:
            timestamp = pktimestamp.getCurrentTimestamp()
        status = self.loadStatus(userId, timestamp)
        remFlipCount = status.getRemFlipCount()
        if remFlipCount <= 0:
            ftlog.debug('DizhuFlipCard.flipCard userId=', userId,
                        'index=', index,
                        'nslogin=', status.nslogin,
                        'timestamp=', datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S'),
                        'remFlipCount=', remFlipCount)
            return False, status, None
        
        contentItem = status.findItemByIndex(index)
        if contentItem:
            ftlog.debug('DizhuFlipCard.flipCard userId=', userId,
                        'index=', index,
                        'nslogin=', status.nslogin,
                        'timestamp=', datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S'),
                        'alreadyFlipped=', '%s:%s' % (contentItem.assetKindId, contentItem.count))
            return False, status, None
        
        regDays = self._calcRegDays(userId, timestamp)
        contentItem = self._flipCard(regDays)
        if not contentItem:
            ftlog.debug('DizhuFlipCard.flipCard userId=', userId,
                        'index=', index,
                        'nslogin=', status.nslogin,
                        'regDays=', regDays,
                        'timestamp=', datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S'),
                        'flipped=', None)
            return False, status, None
        
        status.addItem(index, contentItem)
        status.flipTime = timestamp
        remFlipCount = status.getRemFlipCount()
        if remFlipCount <= 0:
            status.paddings = self._makePaddings(userId)
        self._dao.saveStatus(userId, status)
        userAssets = hallitem.itemSystem.loadUserAssets(userId)
        assetItem = userAssets.addAsset(DIZHU_GAMEID, contentItem.assetKindId, contentItem.count,
                                        timestamp, 'NSLOGIN_REWARD', status.nslogin)
        contentString = TYAssetUtils.buildContent(assetItem)
        if self._rewardMail:
            mail = strutil.replaceParams(self._rewardMail, {'rewardContent':contentString})
            pkmessage.sendPrivate(DIZHU_GAMEID, userId, 0, mail)
            datachangenotify.sendDataChangeNotify(DIZHU_GAMEID, userId, 'message')
            
        ftlog.debug('DizhuFlipCard.flipCard userId=', userId,
                   'index=', index,
                   'nslogin=', status.nslogin,
                   'regDays=', regDays,
                   'timestamp=', datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S'),
                   'reward=', contentString)
        return True, status, assetItem
            
    def addPolicy(self, minRegDays, maxRegDays, selectCardPolicy):
        assert(isinstance(selectCardPolicy, SelectCardPolicy))
        self._policies.append((minRegDays, maxRegDays, selectCardPolicy))
        
    def _selectPolicy(self, regDays):
        for startRegDays, endRegDays, selectCardPolicy in self._policies:
            if ((startRegDays < 0 or regDays >= startRegDays)
                and (endRegDays < 0 or regDays <= endRegDays)):
                return selectCardPolicy
        return None
    
    def _flipCard(self, regDays):
        policy = self._selectPolicy(regDays)
        if policy:
            card = policy.selectCard()
            if card:
                return card.flip()
        return None
    
    def _calcRegDays(self, userId, timestamp):
        registerTimeStr = pkuserdata.getAttr(userId, 'createTime')
        nowDT = datetime.fromtimestamp(timestamp)
        try:
            registerTime = datetime.strptime(registerTimeStr, '%Y-%m-%d %H:%M:%S.%f')
        except:
            registerTime = nowDT
        
        return max(0, (nowDT.date() - registerTime.date()).days)

    def _makePaddings(self, userId):
        paddings = []
        for _ in xrange(7):
            card = self._paddingPolicy.selectCard()
            if card:
                contentItem = card.flip()
                if contentItem:
                    paddings.append(contentItem)
        return paddings


_inited = False
flipCard = DizhuFlipCard()

def _reloadConf():
    global flipCard
    conf = pkconfigure.getGameJson(6, 'flipcard', {})
    flipCard.reloadConf(conf)

def _onConfChanged(event):
    if _inited and event.isChanged('game:6:flipcard:0'):
        ftlog.debug('DizhuFlipCard._onConfChanged')
        _reloadConf()

def _initialize():
    ftlog.debug('DizhuFlipCard initialize begin')
    global _inited
    global flipCard
    if not _inited:
        _inited = True
        flipCard = DizhuFlipCardImpl(DizhuFlipCardStatusDao())
        _reloadConf()
        pkeventbus.globalEventBus.subscribe(EventConfigure, _onConfChanged)
    ftlog.debug('DizhuFlipCard initialize end')


def encodeFlipCardMap(flipMap):
    ret = []
    for index, contentItem in flipMap.iteritems():
        rewardName = hallconf.translateAssetKindIdToOld(contentItem.assetKindId)
        if rewardName:
            ret.append((rewardName, contentItem.count, index)) 
    return ret


def encodePaddings(paddings):
    ret = []
    for contentItem in paddings:
        rewardName = hallconf.translateAssetKindIdToOld(contentItem.assetKindId)
        if rewardName:
            ret.append((rewardName, contentItem.count))
    return ret

