# -*- coding=utf-8
'''
Created on 2016年02月25日

@author: zhaol
'''
import freetime.util.log as ftlog
from hall.entity import hallconf
from poker.entity.events.tyevent import EventConfigure
import poker.entity.events.tyeventbus as pkeventbus
from poker.util import strutil

_inited = False
_lnConfig = {}

def _reloadConf():
    global _lnConfig
    _lnConfig = hallconf.getLocalNotificationConf()
    ftlog.debug('halllocalnotification._reloadConf successed local_notification=', _lnConfig)
    
def _onConfChanged(event):
    if _inited and event.isChanged('game:9999:local_notification:0'):
        ftlog.debug('halllocalnotification._onConfChanged')
        _reloadConf()
        
def _initialize():
    ftlog.debug('halllocalnotification._initialize begin')
    global _inited
    if not _inited:
        _inited = True
        _reloadConf()
        pkeventbus.globalEventBus.subscribe(EventConfigure, _onConfChanged)
    ftlog.debug('halllocalnotification._initialize end')
    
def queryLocalNotification(gameId, userId, clientId):
    '''
    @return: TYLocalNotification array
    '''
    global _lnConfig
    game = strutil.getGameIdFromHallClientId(clientId)
    ftlog.debug('halllocalnotification.queryLocalNotification game=', game,
                'userId=', userId,
                'clientId=', clientId,
                'local_notification=', _lnConfig)
    return _lnConfig.get(str(game), [])
    

