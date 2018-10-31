# -*- coding=utf-8
'''
Created on 2017年6月26日

@author: wangzhen

地方麻将金币场发放启动资金模块 hallstartchip_fuzhou
注释：刚开始做的是抚州金币场，后缀统一用了 _fuzhou，以后后缀统一用 _dfchip

gamedata:9999
旧字段
fuzhou_start_chip    :    0或1， 是否发过启动资金
fuzhou_chip_guide    :    0或1， 是否显示过新手引导
新字段
start_chip_dfchip    :    0或1， 是否发过启动资金
newuser_guide_dfchip :    0或1， 是否显示过新手引导

以后统一使用新字段，同时兼容旧字段
'''

import freetime.util.log as ftlog
from poker.entity.biz import bireport
from poker.entity.dao import userchip, daoconst, gamedata
from poker.entity.events.tyevent import EventConfigure
import poker.entity.events.tyeventbus as pkeventbus
import poker.util.timestamp as pktimestamp
from hall.entity import hallconf, datachangenotify
import hall.entity as hallentity



_inited = False
fuzhou_startchip = 3000
fuzhou_conditions = []




def fuzhou_sendStartChip(userId, gameId, clientId):
    '''
    抚州金币场发放启动资金
    :param userId:
    :param gameId:
    :param clientId:
    '''
    global fuzhou_startchip
    
    canGive = False
    startChip = 0
    final = 0
    try:
        if fuzhou_needSendStartChip(userId, clientId):
            gamedata.setGameAttr(userId, hallconf.HALL_GAMEID, "start_chip_dfchip", 1)
            canGive = True
            
        if ftlog.is_debug():
            ftlog.debug('hallstartchip_fuzhou.fuzhou_sendStartChip userId=', userId,
                        'gameId=', gameId,
                        'clientId=', clientId,
                        'chip=', startChip,
                        'canGive=', canGive)  
        
        if canGive:
            nowChip = userchip.getChip(userId)
            startChip = fuzhou_startchip
            trueDelta, final = userchip.incrChip(userId, gameId, startChip-nowChip, daoconst.CHIP_NOT_ENOUGH_OP_MODE_NONE,
                                         'FUZHOU_START_CHIP', 0, clientId)
            datachangenotify.sendDataChangeNotify(gameId, userId, ['chip']) 
            bireport.gcoin('in.chip.newuser.startchip', gameId, startChip)
            ftlog.debug('hallstartchip_fuzhou.fuzhou_sendStartChip userId=', userId,
                       'gameId=', gameId,
                       'clientId=', clientId,
                       'chip=', startChip,
                       'startChip=', startChip,
                       'trueDelta=', trueDelta,
                       'final=', final)
        return canGive, trueDelta, final    
    except:
        ftlog.error()
        
    return False, 0, 0

def fuzhou_needSendStartChip(userId, clientId):
    '''
    是否需要发放启动资金
    :param userId:
    :param clientId:
    '''
    global fuzhou_startchip
    if not _checkConditions(userId, clientId):
        return False
    elif fuzhou_startchip <= 0:
        return False
    
    return not isSentStartChip(userId)

def isSentStartChip(userId):
    '''
    已经发放过启动资金
    :param userId:
    '''
    isSendChip = 0
    values = gamedata.getGameAttrs(userId, hallconf.HALL_GAMEID, ["fuzhou_start_chip", "start_chip_dfchip"])
    for value in values:
        if not isinstance(value, (int, float)):
            value = 0
        isSendChip += value
    if isSendChip > 0:
        return True
    
    return False

def fuzhou_checkAndSendGuide(userId, clientId):
    '''
    检测并发送抚州金币场新手引导
    :param userId:
    :param clientId:
    '''
    isSendGuide = 0
    values = gamedata.getGameAttrs(userId, hallconf.HALL_GAMEID, ["fuzhou_chip_guide", "newuser_guide_dfchip"])
    for value in values:
        if not isinstance(value, (int, float)):
            value = 0
        isSendGuide += value
    
    if _checkConditions(userId, clientId) and isSendGuide <= 0:
        return True
    return False

def onFuZhouChipGuideSuccess(userId, gameId, clientId):
    '''
    抚州金币场新手引导成功显示回调
    :param userId:
    :param gameId:
    :param clientId:
    '''
    if fuzhou_checkAndSendGuide(userId, clientId):
        gamedata.setGameAttr(userId, hallconf.HALL_GAMEID, "newuser_guide_dfchip", 1)

def _checkConditions(userId, clientId):
    '''
    检查条件
    :param userId:
    :param clientId:
    '''
    global fuzhou_conditions
    if len(fuzhou_conditions) == 0:
            return True
        
    for cond in fuzhou_conditions:
        if not cond.check(hallconf.HALL_GAMEID, userId, clientId, pktimestamp.getCurrentTimestamp()):
            return False

    return True

def _reloadConf():
    global fuzhou_startchip,fuzhou_conditions
    conf = hallconf.getHallFuZhouChip()
    if conf:
        fuzhou_startchip = conf['fuzhou_startchip']
        fuzhou_conditions = hallentity.hallusercond.UserConditionRegister.decodeList(conf['conditions'])
    else:
        ftlog.warn("hallstartchip_fuzhou config is None, please check")

def _onConfChanged(event):
    if _inited and event.isChanged('game:9999:fuzhou_chip:0'):
        ftlog.debug('fuzhou_startChip._onConfChanged')
        _reloadConf()


def _initialize():
    ftlog.debug('hallstartchip_fuzhou initialize begin')
    global _inited
    if not _inited:
        _inited = True
        _reloadConf()
        pkeventbus.globalEventBus.subscribe(EventConfigure, _onConfChanged)
    ftlog.debug('hallstartchip_fuzhou initialize end')