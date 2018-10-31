# -*- coding=utf-8
'''
Created on 2016年6月20日

@author: zhaol
'''
import freetime.util.log as ftlog
from hall.entity import hallconf
from poker.entity.events.tyevent import EventConfigure
import poker.entity.events.tyeventbus as pkeventbus
from hall.entity.hallusercond import UserConditionRegister
from hall.entity.hallconf import HALL_GAMEID
import poker.util.timestamp as pktimestamp
from hall.entity.todotask import TodoTaskRegister, TodoTaskHelper
from freetime.entity.msg import MsgPack
from poker.protocol import router
from poker.util import strutil
from poker.entity.configure import pokerconf

_ordersMap = {}
_vcConfig = {}
_inited = False

def _reloadConf():
    global _ordersMap
    global _vcConfig
    
    conf = hallconf.getExitRemindConf()
    _ordersMap = conf
    ftlog.debug('hall_exit_remind._reloadConf successed orders=', _ordersMap)
    
    _vcConfig = hallconf.getExitRemindVCConf()
    ftlog.debug('hall_exit_remind._reloadConf successed _vcConfig=', _vcConfig)    
    
def _onConfChanged(event):
    if _inited and event.isModuleChanged('exit_remind'):
        ftlog.debug('hall_exit_remind._onConfChanged')
        _reloadConf()

def _initialize():
    global _inited

    ftlog.debug('hall_exit_remind._initialize begin')
    if not _inited:
        _inited = True
        _reloadConf()
        pkeventbus.globalEventBus.subscribe(EventConfigure, _onConfChanged)
    ftlog.debug('hall_exit_remind._initialize end')
    
def queryExitSDK(gameId, userId, clientId):
    global _vcConfig
    
    clientIdNum = pokerconf.clientIdToNumber(clientId)        
    number = str(clientIdNum)                
    actual = _vcConfig['actual']
    if number in actual:
        return actual[number]
    return _vcConfig['default']
    
    
def queryExitRemind(gameId, userId, clientId):
    global _ordersMap
    
    exitSDK = queryExitSDK(gameId, userId, clientId)
    if ftlog.is_debug():
        ftlog.debug('queryExitRemind exitSDK:', exitSDK)
        
    gameIdInClientId = strutil.getGameIdFromHallClientId(clientId)
    if ftlog.is_debug():
        ftlog.debug('hall_exit_remind.queryExitRemind gameIdInClientId', gameIdInClientId)
        
    strGameId = str(gameIdInClientId)    
    if strGameId not in _ordersMap:
        if ftlog.is_debug():
            ftlog.debug('hall_exit_remind.queryExitRemind no this game exit remind config....')
        return
    
    orders = _ordersMap[strGameId]
    if ftlog.is_debug():
        ftlog.debug('hall_exit_remind.queryExitRemind orders:', orders)
        
    for order in orders:
        if ftlog.is_debug():
            ftlog.debug('hall_exit_remind.queryExitRemind order:', order)
        if order.get('name','') == 'checkin':
            # 是否是v4.56
            from hall.entity.localservice.localservice import checkClientVer
            if checkClientVer(userId, gameId, clientId):
                ftlog.hinfo("queryExitRemind|checkClientVer|clientVer|gt|", userId, gameId, clientId)
                continue
            
        conds = UserConditionRegister.decodeList(order.get('conditions', []))
        if ftlog.is_debug():
            ftlog.debug('hall_exit_remind.queryExitRemind conds:', conds)
         
        bCondsOK = False    
        if len(conds) == 0:
            bCondsOK = True
            
        for cond in conds:
            if cond.check(HALL_GAMEID, userId, clientId, pktimestamp.getCurrentTimestamp()):
                if ftlog.is_debug():
                    ftlog.debug('hall_exit_remind.queryExitRemind cond ok: ', cond)
                bCondsOK = True
                break
        
        if bCondsOK:    
            todotasksDict = order.get('todotasks', [])
            todotasks = TodoTaskRegister.decodeList(todotasksDict)
            if ftlog.is_debug():
                ftlog.debug('hall_exit_remind.queryExitRemind todotasks:', todotasks)
                
            todos = TodoTaskHelper.makeTodoTasksByFactory(HALL_GAMEID, userId, clientId, todotasks)
            tasks = TodoTaskHelper.encodeTodoTasks(todos)
            if ftlog.is_debug():
                ftlog.debug('hall_exit_remind.queryExitRemind build tasks ok: ', tasks)
                    
            mo = MsgPack()
            mo.setCmd('game')
            mo.setResult('action', 'get_exit_remind')
            mo.setResult('gameId', gameId)
            mo.setResult('userId', userId)
            mo.setResult('button', order.get('button', ''))
            mo.setResult('tips', order.get('tips', ''))
            mo.setResult('tasks', tasks)
            mo.setResult('exitSDK', exitSDK)
            router.sendToUser(mo, userId)
                    
            if ftlog.is_debug():
                ftlog.debug('hall_exit_remind.queryExitRemind userId:', userId, ' clientId:', clientId, ' msg:', mo)
                
            return