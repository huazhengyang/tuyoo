# -*- coding=utf-8
'''
Created on 2016年6月20日

@author: zhaol
'''
import freetime.util.log as ftlog
from hall.entity import hallconf, hall_exit_remind
from hall.entity.hallusercond import UserConditionRegister
from hall.entity.hallconf import HALL_GAMEID
import poker.util.timestamp as pktimestamp
from hall.entity.todotask import TodoTaskRegister, TodoTaskHelper
from freetime.entity.msg import MsgPack
from poker.protocol import router
from poker.util import strutil
from poker.entity.configure import pokerconf
from poker.entity.configure import configure
from hall.entity import hallconf

def _reloadConf():
    conf = hallconf.getExitRemindConf()
    hall_exit_remind._ordersMap = conf
    ftlog.debug('hall_exit_remind._reloadConf successed orders=', hall_exit_remind._ordersMap)
    
    hall_exit_remind._vcConfig = hallconf.getExitRemindVCConf()
    ftlog.debug('hall_exit_remind._reloadConf successed _vcConfig=', hall_exit_remind._vcConfig)    
    
def queryExitSDK(gameId, userId, clientId):
    clientIdNum = pokerconf.clientIdToNumber(clientId)        
    number = str(clientIdNum)                
    actual = hall_exit_remind._vcConfig['actual']
    if number in actual:
        return actual[number]
    return hall_exit_remind._vcConfig['default']
    
    
def queryExitRemind(gameId, userId, clientId):
    exitSDK = queryExitSDK(gameId, userId, clientId)
    if ftlog.is_debug():
        ftlog.debug('queryExitRemind exitSDK:', exitSDK)
        
    gameIdInClientId = strutil.getGameIdFromHallClientId(clientId)
    if ftlog.is_debug():
        ftlog.debug('hall_exit_remind.queryExitRemind gameIdInClientId', gameIdInClientId)
        
    strGameId = str(gameIdInClientId)    
    if strGameId not in hall_exit_remind._ordersMap:
        if ftlog.is_debug():
            ftlog.debug('hall_exit_remind.queryExitRemind no this game exit remind config....')
        return
    
    orders = hall_exit_remind._ordersMap[strGameId]
    if ftlog.is_debug():
        ftlog.debug('hall_exit_remind.queryExitRemind orders:', orders)
        
    for order in orders:
        if ftlog.is_debug():
            ftlog.debug('hall_exit_remind.queryExitRemind order:', order)
            
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

HALL_GAMEID = 9999

def getExitRemindVCConf():
    return configure.getGameJson(HALL_GAMEID, 'exit_remind', {}, configure.CLIENT_ID_MATCHER)

hallconf.getExitRemindVCConf = getExitRemindVCConf

hall_exit_remind._vcConfig = {}
hall_exit_remind._reloadConf = _reloadConf
hall_exit_remind.queryExitSDK = queryExitSDK   
hall_exit_remind.queryExitRemind = queryExitRemind
