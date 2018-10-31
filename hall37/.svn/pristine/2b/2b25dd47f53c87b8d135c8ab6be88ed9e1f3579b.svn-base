# -*- coding=utf-8
'''
Created on 2015年7月1日

@author: zhaoqh
'''

import freetime.util.log as ftlog
from hall.entity import hallconf
from poker.entity.biz import bireport
from poker.entity.dao import userdata, userchip, daoconst
from poker.entity.events.tyevent import EventConfigure
import poker.entity.events.tyeventbus as pkeventbus
from poker.util import strutil
import hall.client_ver_judge as client_ver_judge
_inited = False
newuser_startchip = 3000

def sendStartChip(userId, gameId, clientId):
    """发放启动资金
    """
    global newuser_startchip
    
    canGive = False
    startChip=0
    final = 0

    canGivestartChip=getCanGivestartChip(userId, gameId, clientId)
    try:
        count = userdata.delAttr(userId, 'sendMeGift')
        if (count == 1) and (canGivestartChip > 0):
            canGive = True
            
        if ftlog.is_debug():
            ftlog.debug('hallstartchip.sendStartChip userId=', userId,
                        'gameId=', gameId,
                        'clientId=', clientId,
                        'chip=', canGivestartChip,
                        'canGive=', canGive)  
        
        if canGive:
            startChip = canGivestartChip
            _, final = userchip.incrChip(userId, gameId, startChip, daoconst.CHIP_NOT_ENOUGH_OP_MODE_NONE,
                                         'USER_STARTUP', 0, clientId) 
            bireport.gcoin('in.chip.newuser.startchip', gameId, startChip)
            ftlog.debug('hallstartchip.sendStartChip userId=', userId,
                       'gameId=', gameId,
                       'clientId=', clientId,
                       'chip=', startChip,
                       'startChip=', startChip,
                       'final=', final)  
        return canGive, startChip, final    
    except:
        ftlog.error()
        
    return False, 0, 0
def getCanGivestartChip(userId, gameId, clientId):
    global newuser_startchip
    _, clientVer, _ = strutil.parseClientId(clientId)
    if clientVer < client_ver_judge.client_ver_397:
        return 3000
    else:
        return newuser_startchip

def needSendStartChip(userId, gameId):
    '''是否发放启动资金
    '''
    global newuser_startchip

    return (1 == userdata.getAttr(userId, 'sendMeGift')) and (newuser_startchip > 0)

def AlreadySendStartChip(userId, gameId):
    '''是否已经发放过启动资金
    '''

    return 1 != userdata.getAttr(userId, 'sendMeGift')

def _reloadConf():
    global newuser_startchip
    conf = hallconf.getHallPublic()
    newuser_startchip = conf['newuser_startchip']

def _onConfChanged(event):
    if _inited and event.isChanged('game:9999:public:0'):
        ftlog.debug('startChip._onConfChanged')
        _reloadConf()


def _initialize():
    ftlog.debug('NewUserStartChip initialize begin')
    global _inited
    if not _inited:
        _inited = True
        _reloadConf()
        pkeventbus.globalEventBus.subscribe(EventConfigure, _onConfChanged)
    ftlog.debug('NewUserStartChip initialize end')

