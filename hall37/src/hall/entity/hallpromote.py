# -*- coding=utf-8
'''
Created on 2015年7月30日

@author: zhaojiangang
'''
from datetime import datetime
from sre_compile import isstring
import time

import freetime.util.log as ftlog
from hall.entity import hallconf, hallpopwnd, hallitem, datachangenotify
from hall.entity.hallconf import HALL_GAMEID
from hall.entity.hallusercond import UserConditionRegister
from poker.entity.biz.exceptions import TYBizConfException
from poker.entity.biz.store.store import TYOrderDeliveryEvent
from poker.entity.events.tyevent import EventConfigure
import poker.entity.events.tyeventbus as pkeventbus


class HallPromotion(object):
    def __init__(self):
        self.promotionId = None
        self.displayName = None
        self.url = None
        self.defaultRes = None
        self.animate = None
        self.todotasks = None
        #小红点判断
        self.redPoint = None
        
    def decodeFromDict(self, d):
        self.promotionId = d.get('promotionId')
        self.displayName = d.get('displayName')
        self.url = d.get('url')
        self.defaultRes = d.get('defaultRes',None)
        self.animate = d.get('animate')
        self.todotasks = []
        for todotaskDict in d.get('todotasks', []):
            self.todotasks.append(hallpopwnd.decodeTodotaskFactoryByDict(todotaskDict))
        self.redPoint = UserConditionRegister.decodeList(d.get('redPoint', []))
        return self
    
class HallPromote(object):
    def __init__(self, position):
        # HallPromotePosition
        self.position = position
        # int time or None
        self.startTime = None
        # int time or None
        self.stopTime = None
        # int
        self.weight = None
        # HallPromotion
        self.promotion = None
        # list<HallPromotionCondition>
        self.conditionList = None
        
    def decodeFromDict(self, d, promotionMap):
        self.weight = d.get('weight', 0)
        if not isinstance(self.weight, int):
            raise TYBizConfException(d, 'HallPromotePosition.weight must int')
        self.startTime = self.stopTime = -1
        startTime = d.get('startTime')
        if startTime:
            startTime = datetime.strptime(startTime, '%Y-%m-%d %H:%M:%S')
            self.startTime = int(time.mktime(startTime.timetuple()))
        stopTime = d.get('stopTime')
        if stopTime:
            stopTime = datetime.strptime(stopTime, '%Y-%m-%d %H:%M:%S')
            self.stopTime = int(time.mktime(stopTime.timetuple()))
        promotionId = d.get('promotionId')
        promotion = promotionMap.get(promotionId)
        if not promotion:
            raise TYBizConfException(d, 'Not found promotion for %s' % (promotionId))
        self.promotion = promotion
        self.conditionList = UserConditionRegister.decodeList(d.get('conditions', []))
        return self
    
class HallPromotePosition(object):
    def __init__(self):
        self.pos = None
        self.promoteList = None
    
    def decodeFromDict(self, d, promotionMap):
        self.pos = d.get('pos')
        if not isinstance(self.pos, int) or self.pos <= 0:
            raise TYBizConfException(d, 'HallPromotePosition.pos must int > 0')
        self.promoteList = []
        for promoteDict in d.get('promotes'):
            promote = HallPromote(self).decodeFromDict(promoteDict, promotionMap)
            self.promoteList.append(promote)
        return self
    
class HallPromoteTemplate(object):
    def __init__(self):
        self.name = None
        self.positionList = None
        self.positionMap = None
        
    def decodeFromDict(self, d, promotionMap):
        self.name = d.get('name')
        if not isstring(self.name) or not self.name:
            raise TYBizConfException(d, 'HallPromoteTemplate.name must be not empty string')
        self.positionList = []
        self.positionMap = {}
        for positionDict in d.get('positions', []):
            position = HallPromotePosition().decodeFromDict(positionDict, promotionMap)
            if position.pos in self.positionMap:
                raise TYBizConfException(positionDict, 'Duplicate position %s for template %s' % (position.pos, self.name))
            self.positionMap[position.pos] = position
            self.positionList.append(position)
        return self
    
_inited = False
# key=promotionId, value=HallPromotion
_promotionMap = {}
# key=templateName, value=HallPromoteTemplate
_templateMap = {}

def _reloadConf():
    global _promotionMap
    global _templateMap
    promotionMap = {}
    templateMap = {}
    conf = hallconf.getPromoteConf()
    for promotionDict in conf.get('promotions', []):
        promotion = HallPromotion().decodeFromDict(promotionDict)
        if promotion.promotionId in promotionMap:
            raise TYBizConfException(promotionDict, 'Duplicate promotionId %s' % (promotion.promotionId))
        promotionMap[promotion.promotionId] = promotion
    
    if ftlog.is_debug():
        ftlog.debug('hallpromote._reloadConf promotionIds=', promotionMap.keys())
    for templateDict in conf.get('templates', []):
        template = HallPromoteTemplate().decodeFromDict(templateDict, promotionMap)
        if template.name in templateMap:
            raise TYBizConfException(templateDict, 'Duplicate templateName %s' % (template.name))
        templateMap[template.name] = template
    _promotionMap = promotionMap
    _templateMap = templateMap
    ftlog.debug('hallpromote._reloadConf successed promotionIds=', _promotionMap.keys(),
               'templateNames=', _templateMap.keys())
    
def _onConfChanged(event):
    if _inited and event.isModuleChanged('promote'):
        ftlog.debug('hallpromote._onConfChanged')
        _reloadConf()
        
def _initialize():
    ftlog.debug('hallpromote initialize begin')
    from hall.game import TGHall
    global _inited
    if not _inited:
        _inited = True
        _reloadConf()
        pkeventbus.globalEventBus.subscribe(EventConfigure, _onConfChanged)
        TGHall.getEventBus().subscribe(TYOrderDeliveryEvent, _onOrderDelivery)
    ftlog.debug('hallpromote initialize end')
    
def _onOrderDelivery(event):
    if hasattr(event, 'assetItems') and event.assetItems:
        for assetKind, count, final in event.assetItems:
            # 从无到有或者从有到无需要发送推广位变化
            if (assetKind.kindId in (hallitem.ASSET_ITEM_MEMBER_KIND_ID, hallitem.ASSET_ITEM_MEMBER_NEW_KIND_ID)
                and (count == final)):
                datachangenotify.sendDataChangeNotify(HALL_GAMEID, event.userId, 'promotion_loc')

def _checkPromote(gameId, userId, clientId, promote, timestamp):
    if ((promote.startTime != -1 and timestamp < promote.startTime)
        or (promote.stopTime != -1 and timestamp >= promote.stopTime)):
        return False
    for condition in promote.conditionList:
        if not condition.check(HALL_GAMEID, userId, clientId, timestamp):
            return False
    return True

def _getPromote(gameId, userId, clientId, position, timestamp):
    promotes = []
    for promote in position.promoteList:
        if _checkPromote(gameId, userId, clientId, promote, timestamp):
            promotes.append(promote)
    promotes.sort(key=lambda promote:promote.weight, reverse=True)
    return promotes[0] if promotes else None

def getPromotes(gameId, userId, clientId, timestamp):
    ret = []
    templateName = hallconf.getPromoteTemplateName(clientId)
    template = _templateMap.get(templateName)
    if ftlog.is_debug():
        ftlog.debug('hallpromote.getPromotes gameId=', gameId,
                    'userId=', userId,
                    'clientId=', clientId,
                    'timestamp=', datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S'),
                    'templateName=', templateName)
    if template:
        for position in template.positionList:
            promote = _getPromote(gameId, userId, clientId, position, timestamp)
            if promote:
                ret.append(promote)
    return ret


