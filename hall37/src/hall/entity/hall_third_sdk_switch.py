# -*- coding=utf-8
'''
Created on 2015年8月13日

@author: zhaol
'''
import freetime.util.log as ftlog
from hall.entity import hallconf
from poker.entity.events.tyevent import EventConfigure
import poker.entity.events.tyeventbus as pkeventbus

_thirdSDKSwitchConfig = {}
_inited = False

def _reloadConf():
    global _thirdSDKSwitchConfig
    conf = hallconf.getThirdSDKSwitchConf()
    ftlog.debug('hall_third_sdk_switch._reloadConf successed config=', conf)
    _thirdSDKSwitchConfig = conf
    
def _onConfChanged(event):
    if _inited and event.isModuleChanged('third_sdk_switch'):
        ftlog.debug('hall_third_sdk_switch._onConfChanged')
        _reloadConf()

def _initialize():
    ftlog.debug('hall_third_sdk_switch._initialize begin')
    global _inited
    if not _inited:
        _inited = True
        _reloadConf()
        pkeventbus.globalEventBus.subscribe(EventConfigure, _onConfChanged)
    ftlog.debug('hall_third_sdk_switch._initialize end')
    
def queryThirdSDKSwitch(clientId):
    return _thirdSDKSwitchConfig

