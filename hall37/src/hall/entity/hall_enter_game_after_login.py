# -*- coding=utf-8
'''
Created on 2016年6月20日

快速开始行为明确化
表明具体的快开行为
比如：
1）血流成河 初级场
2）血战到底 高级场
3）斗地主 中级场

@author: zhaol
'''
import freetime.util.log as ftlog
from hall.entity import hallconf
from poker.entity.events.tyevent import EventConfigure
import poker.entity.events.tyeventbus as pkeventbus
from hall.entity.todotask import TodoTaskRegister, TodoTaskHelper
from freetime.entity.msg import MsgPack
from poker.protocol import router

_ordersMap = {}
_inited = False

def _reloadConf():
    global _ordersMap
    global _vcConfig
    
    conf = hallconf.getEnterGameAfterLoginTcConf()
    _ordersMap = conf
    ftlog.debug('hall_enter_game_after_login._reloadConf successed orders=', _ordersMap)
    
def _onConfChanged(event):
    if _inited and event.isModuleChanged('enter_game_after_login'):
        ftlog.debug('hall_enter_game_after_login._onConfChanged')
        _reloadConf()

def _initialize():
    global _inited

    ftlog.debug('hall_enter_game_after_login._initialize begin')
    if not _inited:
        _inited = True
        _reloadConf()
        pkeventbus.globalEventBus.subscribe(EventConfigure, _onConfChanged)
    ftlog.debug('hall_enter_game_after_login._initialize end')
    
def queryEnterGameAfterLogin(userId, gameId, clientId, gameIds):
    '''
    获取登录后直接进入的游戏配置
    '''
    global _ordersMap
    templateName = hallconf.getEnterGameAfterLoginTemplateName(clientId)
    ftlog.debug('templateName:', templateName)
    
    templates = _ordersMap.get('templates', [])
    for template in templates:
        ftlog.debug('template:', template)
        
        if template.get('name', '') == templateName:
            # 找到当前的模板了
            applyGame = template.get('applyGame', None)
            if not applyGame:
                sendEnterGameError(userId, gameId, clientId, -2, '配置中无游戏')
                return
            
            targetGameId = applyGame.get('gameId', 0)
            if not targetGameId or targetGameId not in gameIds:
                ftlog.debug('targetGameId:', targetGameId
                            , ' gameIds:', gameIds)
                sendEnterGameError(userId, gameId, clientId, -3, '配置游戏不可进入')
                return
            
            return sendQuickStartRecommendMsg(userId, gameId, clientId, applyGame)
    
    sendEnterGameError(userId, gameId, clientId, -1, '没有配置')            
    return '1'

def sendEnterGameError(userId, gameId, clientId, errCode, errInfo):
    '''
    返回错误消息
    '''
    mo = MsgPack()
    mo.setCmd('game')
    mo.setResult('action', 'enter_game_after_login')
    mo.setResult('clientId', clientId)
    mo.setResult('gameId', gameId)
    mo.setResult('userId', userId)
    mo.setError(errCode, errInfo)
    router.sendToUser(mo, userId)

def sendQuickStartRecommendMsg(userId, gameId, clientId, applyGame):
    '''
    发送快开配置的消息给客户端
    '''
    ftlog.debug('userId:', userId
                , ' gameId:', gameId
                , ' clientId:', clientId
                , ' applyGame:', applyGame)
    
    todotasksDict = applyGame.get('todotasks', [])
    todotasks = TodoTaskRegister.decodeList(todotasksDict)
    ftlog.debug('todotasks:', todotasks)
        
    todos = TodoTaskHelper.makeTodoTasksByFactory(gameId, userId, clientId, todotasks)
    tasks = TodoTaskHelper.encodeTodoTasks(todos)
    ftlog.debug('build tasks ok: ', tasks)
    
    return sendTodoTaskToUser(userId, gameId, applyGame.get('name', ''), tasks)   
    
def sendTodoTaskToUser(userId, gameId, name, tasks):
    '''
    发送快开的消息给前端
    '''
    mo = MsgPack()
    mo.setCmd('game')
    mo.setResult('action', 'enter_game_after_login')
    # 快速开始按钮的显示名称
    mo.setResult('name', name)
    mo.setResult('gameId', gameId)
    mo.setResult('userId', userId)
    # 快速开始按钮的行为
    mo.setResult('tasks', tasks)
    router.sendToUser(mo, userId)
            
    ftlog.debug('userId:', userId
                , ' gameId:', gameId
                , ' message:', mo)
        
    return mo