# -*- coding=utf-8
'''
Created on 2016年6月20日

@author: zhaol
'''
import freetime.util.log as ftlog
from hall.entity import hallconf
from poker.entity.events.tyevent import EventConfigure
import poker.entity.events.tyeventbus as pkeventbus
from freetime.entity.msg import MsgPack
from poker.protocol import router

_updatesMap = {}
_inited = False

def _reloadConf():
    global _updatesMap

    conf = hallconf.getGameUpdateConf()
    _updatesMap = conf

    ftlog.debug('hall_game_update._reloadConf successed config=', _updatesMap)
    
def _onConfChanged(event):
    if _inited and event.isModuleChanged('update'):
        ftlog.debug('hall_game_update._onConfChanged')
        _reloadConf()

def _initialize():
    global _inited

    ftlog.debug('hall_game_update._initialize begin')
    if not _inited:
        _inited = True
        _reloadConf()
        pkeventbus.globalEventBus.subscribe(EventConfigure, _onConfChanged)
    ftlog.debug('hall_game_update._initialize end')


def _doGetUpdateInfo(gameId, version, updateVersion):
    updates = []

    strGameId = str(gameId)
    if strGameId in _updatesMap:
        gUpdates = _updatesMap[strGameId]
        if version in gUpdates:
            vUpdates = gUpdates[version]
            for u in vUpdates:
                if updateVersion < int(u['updateVersion']):
                    updates.append(u)

    return updates


def getUpdateInfo2(gameId, version, updateVersion):
    return _doGetUpdateInfo(gameId, version, updateVersion)


def getUpdateInfo(gameId, userId, clientId, version, updateVersion):
    global _updatesMap

    mo = MsgPack()
    mo.setCmd('game')
    mo.setResult('action', 'get_game_update_info')
    mo.setResult('gameId', gameId)
    mo.setResult('userId', userId)
    mo.setResult('clientId', clientId)

    updates = _doGetUpdateInfo(gameId, version, updateVersion)

    if ftlog.is_debug():
        ftlog.debug('hall_game_update.getUpdateInfo gameId:', gameId
                    , ' userId:', userId
                    , ' clientId:', clientId
                    , ' version:', version
                    , ' updateVersion:', updateVersion
                    , ' updates:', updates
                    )

    mo.setResult('updates', updates)
    router.sendToUser(mo, userId)

    return updates