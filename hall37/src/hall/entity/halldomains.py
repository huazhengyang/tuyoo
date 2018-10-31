# -*- coding=utf-8
'''
Created on 2016年8月5日

@author: zhaol
'''
import freetime.util.log as ftlog
from hall.entity import hallconf
from poker.entity.events.tyevent import EventConfigure
import poker.entity.events.tyeventbus as pkeventbus
import random
from poker.util import strutil
import poker.util.timestamp as pktimestamp

_dominMap = {}
_inited = False

def _reloadConf():
    global _dominMap
    conf = hallconf.getDomainTCConf()
    
    _dominMap = conf
    if ftlog.is_debug():
        ftlog.debug('halldomains._reloadConf successed _dominMap=', _dominMap)
    
def _onConfChanged(event):
    if _inited and event.isModuleChanged('domain'):
        if ftlog.is_debug():
            ftlog.debug('halldomains._onConfChanged')
        _reloadConf()

def _initialize():
    global _inited
    
    if ftlog.is_debug():
        ftlog.debug('halldomains._initialize begin')
    
    if not _inited:
        _inited = True
        _reloadConf()
        pkeventbus.globalEventBus.subscribe(EventConfigure, _onConfChanged)
        
def getIndexBySecondInDay(count):
    nNow = pktimestamp.getDayPastSeconds()
    total = 24 * 60 * 60
    part = total / count
    if total % count != 0:
        part += 1
        
    return nNow / part
    
def replacedDomain(urlString, replaceDict):
    '''
    获取宏定义对应的域名
    如果没有对应的宏定义配置或者宏定义配置为空，会返回None
    '''
    global _dominMap
    if ftlog.is_debug():
        ftlog.debug('halldomains.replacedDomain _dominMap: ', _dominMap)
        
    for domain in _dominMap:
        domains = _dominMap[domain]
        if ftlog.is_debug():
            ftlog.debug('halldomains.replacedDomain domains: ', domains, ' length:' , len(domains))
                
        if len(domains) == 0:
            continue
        
        # 按时间平均随机
        nChoose = getIndexBySecondInDay(len(domains))
        replaceDict[domain] = domains[nChoose]
        if ftlog.is_debug():
            ftlog.debug('halldomains.replacedDomain replaceDict: ', replaceDict)
            
    if ftlog.is_debug():
        ftlog.debug('halldomains.replacedDomain ', urlString, ' replaced params: ', replaceDict)
        
    return strutil.replaceParams(urlString, replaceDict)
        