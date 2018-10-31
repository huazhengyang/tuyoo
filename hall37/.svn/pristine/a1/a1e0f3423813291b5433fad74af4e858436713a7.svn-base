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
from hall.entity.hallusercond import UserConditionRegister
import poker.util.timestamp as pktimestamp
from hall.entity.todotask import TodoTaskRegister, TodoTaskHelper,\
    TodoTaskEnterGameNew
from freetime.entity.msg import MsgPack
from poker.protocol import router
from poker.entity.dao import gamedata
from hall.entity.hallconf import HALL_GAMEID
import json

KEY_QUICK_START_RECOMMEND_GAME = 'quick_start_recommend_game'
KEY_QUICK_START_RECOMMEND_PARAMS = 'quick_start_recommend_params'
KEY_QUICK_START_RECOMMEND_NAME = 'quick_start_recommend_name'

_ordersMap = {}
_inited = False

def _reloadConf():
    global _ordersMap
    global _vcConfig
    
    conf = hallconf.getQuickStartRecommendTcConf()
    _ordersMap = conf
    ftlog.debug('hall_quick_start_recommend._reloadConf successed orders=', _ordersMap)
    
def _onConfChanged(event):
    if _inited and event.isModuleChanged('quick_start_recommend'):
        ftlog.debug('hall_quick_start_recommend._onConfChanged')
        _reloadConf()

def _initialize():
    global _inited

    ftlog.debug('hall_quick_start_recommend._initialize begin')
    if not _inited:
        _inited = True
        _reloadConf()
        pkeventbus.globalEventBus.subscribe(EventConfigure, _onConfChanged)
    ftlog.debug('hall_quick_start_recommend._initialize end')
    
def queryQuickStartRecommend(userId, gameId, clientId):
    '''
    获取推荐的快开配置
    '''
    # 首先检查改玩家有米有上次快开的信息，如果有的话，继续引导玩家进入
    qsrGameStr = gamedata.getGameAttr(userId, HALL_GAMEID, KEY_QUICK_START_RECOMMEND_GAME)
    qsrGame = 0
    if qsrGameStr:
        qsrGame = int(qsrGameStr)
    ftlog.debug('quickStartRecommendGame:', qsrGame)
    
    if qsrGame > 0:
        qsrParamStr = gamedata.getGameAttr(userId, qsrGame, KEY_QUICK_START_RECOMMEND_PARAMS)
        ftlog.debug('quickStartRecommendParams:', qsrParamStr)
        qsrName = gamedata.getGameAttr(userId, qsrGame, KEY_QUICK_START_RECOMMEND_NAME)
        ftlog.debug('quickStartRecommendName:', qsrName)
        
        if qsrParamStr:
            qsrParams = json.loads(qsrParamStr)
            todo = TodoTaskEnterGameNew(qsrGame, qsrParams)
            todos = TodoTaskHelper.encodeTodoTasks(todo)
            return sendTodoTaskToUser(userId, gameId, qsrName, todos)
    
    global _ordersMap
    templateName = hallconf.getQuickStartRecommendTemplateName(clientId)
    ftlog.debug('templateName:', templateName)
    
    templates = _ordersMap.get('templates', [])
    for template in templates:
        ftlog.debug('template:', template)
        
        if template.get('name', '') == templateName:
            # 找到当前的模板了
            applyGames = template.get('applyGames', [])
            for applyGame in applyGames:
                ftlog.debug('applyGame:', applyGame)
                
                if applyGame.get('pushToNewUser', 0):
                    quickList = applyGame.get('list', [])
                    return sendQuickStartRecommendMsg(userId, gameId, clientId, quickList)
                
    return '1'

def sendQuickStartRecommendMsg(userId, gameId, clientId, quickList):
    '''
    发送快开配置的消息给客户端
    '''
    ftlog.debug('userId:', userId
                , ' gameId:', gameId
                , ' clientId:', clientId
                , ' quickList:', quickList)
    
    for quickConf in quickList:
        conds = UserConditionRegister.decodeList(quickConf.get('conditions', []))
        ftlog.debug('conds:', conds)
           
        bCondsOK = False
        if not conds:
            bCondsOK = True
        else:
            for cond in conds: 
                if cond.check(gameId, userId, clientId, pktimestamp.getCurrentTimestamp()):
                    bCondsOK = True
                    break
    
        if not bCondsOK:
            ftlog.debug('bCondsOK if false, this user check cond error, return...')
            return
        
        todotasksDict = quickConf.get('todotasks', [])
        todotasks = TodoTaskRegister.decodeList(todotasksDict)
        ftlog.debug('todotasks:', todotasks)
            
        todos = TodoTaskHelper.makeTodoTasksByFactory(gameId, userId, clientId, todotasks)
        tasks = TodoTaskHelper.encodeTodoTasks(todos)
        ftlog.debug('build tasks ok: ', tasks)
        
        return sendTodoTaskToUser(userId, gameId, quickConf.get('name', ''), tasks)   
    
def sendTodoTaskToUser(userId, gameId, name, tasks):
    '''
    发送快开的消息给前端
    '''
    mo = MsgPack()
    mo.setCmd('game')
    mo.setResult('action', 'get_quick_start_recommend')
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