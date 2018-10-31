# -*- coding=utf-8
'''
Created on 2015年8月13日

@author: zhaojiangang
'''
from datetime import datetime
from sre_compile import isstring

import freetime.util.log as ftlog
from hall.entity import hallconf, hallpopwnd
from poker.entity.biz.exceptions import TYBizConfException
from poker.entity.events.tyevent import EventConfigure
import poker.entity.events.tyeventbus as pkeventbus
from hall.entity.hallusercond import UserConditionRegister
from hall.entity.hallconf import HALL_GAMEID

DEFAULT_INTERVAL = 5

class TYAds(object):
    def __init__(self):
        self.adsId = None
        self.clickable = None
        self.pic = None
        self.startDT = None
        self.endDT = None
        self.todotasks = None
        self.condition = None
    
    def decodeFromDict(self, d):
        self.adsId = d.get('id')
        if not isinstance(self.adsId, int):
            raise TYBizConfException(d, 'TYAds.id must be int')
        self.clickable = d.get('clickable')
        # if self.clickable not in (0, 1):
        #     raise TYBizConfException(d, 'TYAds.clickable must be int int (0,1)')
        self.pic = d.get('pic', '')
        if not isstring(self.pic):
            raise TYBizConfException(d, 'TYAds.pic must be string')
        
        self.startDT = d.get('startTime')
        if self.startDT is not None:
            self.startDT = datetime.strptime(self.startDT, '%Y-%m-%d %H:%M:%S')
        self.endDT = d.get('endTime')
        if self.endDT is not None:
            self.endDT = datetime.strptime(self.endDT, '%Y-%m-%d %H:%M:%S')
        
        self.todotasks = []
        for todotask in d.get('todotasks', []):
            self.todotasks.append(hallpopwnd.decodeTodotaskFactoryByDict(todotask))
        
        self.condition = d.get('condition')
        if self.condition is not None:
            self.condition = UserConditionRegister.decodeFromDict(self.condition)
        return self
    
class TYAdsTemplate(object):
    def __init__(self, name, interval=None, adsList=None):
        self.name = name
        self.interval = interval
        self.adsList = adsList

    def decodeFromDict(self, d, adsMap):
        self.interval = d.get('interval', DEFAULT_INTERVAL)
        if not isinstance(self.interval, int):
            raise TYBizConfException(d, 'TYAdsTemplate.interval must be int')
        self.adsList = []
        try:
            for adsId in d.get('ads'):
                ads = adsMap.get(adsId)
                if not ads:
                    raise TYBizConfException(d, 'ads not found %s for %s' % (adsId, self.name))
                self.adsList.append(ads)
        except:
            raise TYBizConfException(d, 'TYAdsTemplate decodeFromDict templateName:' + str(self.name) + ' templateDict:' + str(d) + ' adsMap:' + str(adsMap))
        return self
    
EMPTY_TEMPLATE = TYAdsTemplate('empty', DEFAULT_INTERVAL, [])

_adsMap = {}
# map<templateName,  TYAdsTemplate>           
_adsTemplateMap = {}

_inited = False

def _reloadConf():
    global _adsTemplateMap
    conf = hallconf.getAdsConf()
    
    adsMap = {}
    adsTemplateMap = {}
    
    for adsDict in conf.get('ads', []):
        ads = TYAds().decodeFromDict(adsDict)
        if ads.adsId in adsMap:
            raise TYBizConfException(adsDict, 'Duplicate ads for %s' % (ads.adsId))
        adsMap[ads.adsId] = ads
        
    for name, templateDict in conf.get('templates', {}).iteritems():
        template = TYAdsTemplate(name).decodeFromDict(templateDict, adsMap)
        adsTemplateMap[name] = template
    
    _adsMap = adsMap
    _adsTemplateMap = adsTemplateMap
    
    ftlog.debug('hallads._reloadConf successed adsIds=', _adsMap.keys(),
               'templateNames=', _adsTemplateMap.keys())
    
def _onConfChanged(event):
    if _inited and event.isModuleChanged('ads'):
        ftlog.debug('hallads._onConfChanged')
        _reloadConf()

def _initialize():
    ftlog.debug('hallads._initialize begin')
    global vipSystem
    global userVipSystem
    global _inited
    if not _inited:
        _inited = True
        _reloadConf()
        pkeventbus.globalEventBus.subscribe(EventConfigure, _onConfChanged)
    ftlog.debug('hallads._initialize end')
    
def getAdsTemplateMap():
    return _adsTemplateMap

def getAdsMap():
    return _adsMap

def queryAds(gameId, userId, clientId):
    '''
    @return: TYAdsTemplate
    '''
    templateName = hallconf.getClientAdsConf(clientId)
    if templateName:
        ret = _adsTemplateMap.get(templateName, EMPTY_TEMPLATE)
        ftlog.debug('hallads.queryAds gameId=', gameId,
                    'userId=', userId,
                    'clientId=', clientId,
                    'templateName=', templateName,
                    'contents=', ret)
        return ret
    return EMPTY_TEMPLATE
    
def checkAds(gameId, userId, clientId, ads, timestamp):
    dt = datetime.fromtimestamp(timestamp)
    if ((ads.startDT and dt < ads.startDT)
        or (ads.endDT and dt >= ads.endDT)):
        return False
    if ads.condition:
        return ads.condition.check(HALL_GAMEID, userId, clientId, timestamp)
    return True
