# -*- coding=utf-8
'''
Created on 2015年8月13日

@author: zhaojiangang
'''
from poker.util import strutil
import freetime.util.log as ftlog
from hall.entity import hallconf, hallitem
from poker.entity.events.tyevent import EventConfigure
import poker.entity.events.tyeventbus as pkeventbus
from poker.entity.configure import pokerconf

_firstRechage = {}
_firstRechageVC = {}
_inited = False

def _reloadConf():
    global _firstRechage
    global _firstRechageVC
    
    _firstRechage = hallconf.getFristRechargeConf()
    _firstRechageVC = hallconf.getFristRechargeVCConf()
    
def _onConfChanged(event):
    if _inited and event.isModuleChanged('first_recharge'):
        ftlog.debug('hall_first_recharge._onConfChanged')
        _reloadConf()
        
def _initialize():
    ftlog.debug('hall_first_recharge._initialize begin')
    global _inited
    if not _inited:
        _inited = True
        _reloadConf()
        pkeventbus.globalEventBus.subscribe(EventConfigure, _onConfChanged)
    ftlog.debug('hall_first_recharge._initialize end')
    
def queryFirstRecharge(gameId, userId, clientId):
    '''
    @return: 首冲礼包道具ID
    默认值：ITEM_FIRST_RECHARGE_GIFT_KIND_ID
    '''
    
    # 首先查clientId对应的配置
    intClientId = pokerconf.clientIdToNumber(clientId)
    strClientId = str(intClientId)
    if strClientId in _firstRechageVC:
        itemId = _firstRechageVC.get(strClientId, None)
        if itemId:
            if ftlog.is_debug():
                ftlog.debug('hall_first_recharge.queryFirstRecharge clientId:', clientId, ' unique itemId:', itemId)
            return itemId
        
    # 再查gameId对应的配置
    gId = strutil.getGameIdFromHallClientId(clientId)
    strId = str(gId)
    itemId = _firstRechage.get(strId, hallitem.ITEM_FIRST_RECHARGE_GIFT_KIND_ID)
    return itemId

