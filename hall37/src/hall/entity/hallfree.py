# -*- coding=utf-8 -*-

from datetime import datetime
from sre_compile import isstring

import freetime.util.log as ftlog
from hall.entity import hallconf, hallpopwnd, datachangenotify
from hall.entity.hallconf import HALL_GAMEID
from hall.entity.hallusercond import UserConditionRegister
from poker.entity.biz.exceptions import TYBizConfException
from poker.entity.events.tyevent import EventConfigure, ItemCountChangeEvent
import poker.entity.events.tyeventbus as pkeventbus


class HallFree(object):
    def __init__(self):
        self.freeItemId = None
        self.iconRes = None
        self.itemName = None  # 前端图片上显示的字
        self.states = []

    def decodeFromDict(self, d):
        self.freeItemId = d.get('freeItemId')
        self.iconRes = d.get('iconRes')
        self.itemName = d.get("itemName", "")
        self.states = []
        for state in d.get('states', []):
            self.states.append(HallFreeState().decodeFromDict(state))
        return self


class HallFreeState(object):
    def __init__(self):
        # str
        self.desc = ''
        # str 
        self.btnText = ''
        # bool
        self.hasMark = False
        # int
        self.enable = True
        # bool
        self.visible = True
        # 条件
        self.conditionList = None
        # todotask
        self.todotaskList = None

    def decodeFromDict(self, d):
        self.desc = d.get('desc', '')
        self.btnText = d.get('btnText', '')
        self.hasMark = d.get('hasMark', False)
        self.enable = d.get('enable', True)
        self.visible = d.get('visible', True)

        self.conditionList = UserConditionRegister.decodeList(d.get('conditions', []))

        self.todotaskList = []
        for todotaskDict in d.get('todotasks', []):
            self.todotaskList.append(hallpopwnd.decodeTodotaskFactoryByDict(todotaskDict))

        return self


class HallFreeTemplate(object):
    def __init__(self):
        self.name = None
        self.freeItems = None

    def decodeFromDict(self, d, freeItemMap):
        self.name = d.get('name')
        if not isstring(self.name) or not self.name:
            raise TYBizConfException(d, 'HallFreeTemplate.name must be not empty string')

        self.freeItems = []
        for itemId in d.get('freeItems', []):
            if freeItemMap.has_key(itemId):
                self.freeItems.append(freeItemMap[itemId])
        return self


_inited = False
# key=promotionId, value=HallPromotion
_freeItemMap = {}
# key=templateName, value=HallPromoteTemplate
_templateMap = {}


def _reloadConf():
    global _freeItemMap
    global _templateMap
    freeItemMap = {}
    templateMap = {}
    conf = hallconf.getFreeConf()
    for freeDict in conf.get('freeItems', []):
        freeItem = HallFree().decodeFromDict(freeDict)
        if freeItem.freeItemId in freeItemMap:
            raise TYBizConfException(freeDict, 'Duplicate freeId %s' % (freeItem.freeItemId))
        freeItemMap[freeItem.freeItemId] = freeItem

    if ftlog.is_debug():
        ftlog.debug('hallfree._reloadConf freeIds=', freeItemMap.keys())
    for templateDict in conf.get('templates', []):
        template = HallFreeTemplate().decodeFromDict(templateDict, freeItemMap)
        if template.name in templateMap:
            raise TYBizConfException(templateDict, 'Duplicate templateName %s' % (template.name))
        templateMap[template.name] = template
    _freeItemMap = freeItemMap
    _templateMap = templateMap
    ftlog.debug('hallfree._reloadConf successed freeIds=', _freeItemMap.keys(),
               'templateNames=', _templateMap.keys())


def _onConfChanged(event):
    if _inited and event.isChanged('game:9999:free:tc'):
        ftlog.debug('hallfree._onConfChanged')
        _reloadConf()


def _onItemCountChanged(event):
    if _inited:
        ftlog.debug('hallfree._onItemCountChanged', event.userId)
        datachangenotify.sendDataChangeNotify(HALL_GAMEID, event.userId, ['free', 'promotion_loc'])


def _initialize():
    ftlog.debug('hallfree._initialize begin')
    global _inited
    if not _inited:
        _inited = True
        _reloadConf()
        pkeventbus.globalEventBus.subscribe(EventConfigure, _onConfChanged)
        pkeventbus.globalEventBus.subscribe(ItemCountChangeEvent, _onItemCountChanged)
    ftlog.debug('hallfree._initialize end')


# 获取用户对应的免费列表配置数据
def getFree(gameId, userId, clientId, timestamp):
    ret = []
    templateName = hallconf.getFreeTemplateName(clientId)
    template = _templateMap.get(templateName)
    if ftlog.is_debug():
        ftlog.debug('hallfree.getFree gameId=', gameId,
                    'userId=', userId,
                    'clientId=', clientId,
                    'timestamp=', datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S'),
                    'templateName=', templateName)
    if not template:
        template = _templateMap.get('default')
    if ftlog.is_debug():
        ftlog.debug('hallfree.getFree gameId=', gameId,
                    'userId=', userId,
                    'clientId=', clientId,
                    'timestamp=', datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S'),
                    'freeItems=', [fi.freeItemId for fi in template.freeItems] if template else [])
    if template:
        for freeItem in template.freeItems:
            ret.append(freeItem)
    return ret
