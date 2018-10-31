# -*- coding=utf-8
'''
Created on 2016年6月20日

退出插件时候的挽留
支持范围：
1）在本游戏内的引导，比如金币去比赛，比赛去金币
2）支持游戏间的引导，比如麻将引导人竞猜麻将/中发白/德州扑克

@author: zhaol
'''
import freetime.util.log as ftlog
from hall.entity import hallconf
from poker.entity.events.tyevent import EventConfigure
import poker.entity.events.tyeventbus as pkeventbus
import poker.util.timestamp as pktimestamp
from freetime.entity.msg import MsgPack
from poker.protocol import router
from poker.entity.dao import gamedata
import random

_ordersMap = {}
_inited = False
TYPE_MOST = 1
TYPE_LAST = 2
TYPE_LEAST = 3
TYPE_NEVER = 4

def _reloadConf():
    global _ordersMap
    global _vcConfig
    
    conf = hallconf.getExitPluginRemindTcConf()
    _ordersMap = conf
    ftlog.debug('_reloadConf successed orders=', _ordersMap)
    
def _onConfChanged(event):
    if _inited and event.isModuleChanged('exit_plugin_remind'):
        ftlog.debug('_onConfChanged')
        _reloadConf()

def _initialize():
    global _inited

    ftlog.debug('_initialize begin')
    if not _inited:
        _inited = True
        _reloadConf()
        pkeventbus.globalEventBus.subscribe(EventConfigure, _onConfChanged)
    ftlog.debug('_initialize end')
    
def queryExitPluginRemind(userId, _gameId, clientId, gamesUserCanSee):
    '''
    获取推荐的快开配置
    '''
    global _ordersMap
    templateName = hallconf.getExitPluginRemindTemplateName(clientId)
    ftlog.debug('templateName:', templateName)
    
    templates = _ordersMap.get('templates', [])
    for template in templates:
        ftlog.debug('template:', template)
        
        if template.get('name', '') == templateName:
            # 找到当前的模板了
            remindGames = template.get('remindGames', [])
            
            # 首先获取可以引导去哪些游戏
            gameIds = []
            for remindGame in remindGames:
                gameId = remindGame.get('gameId', 0)
                if (gameId != 0) and (gameId not in gameIds) and (gameId in gamesUserCanSee) and (gameId != _gameId):
                    gameIds.append(gameId)
                    
            # 第二，获取目标游戏的游戏行为
            mostGameId = 0 # 玩儿的最多的游戏一个，进入次数最多的游戏
            mostGameLoginSum = 0
            
            lastGameId = 0 # 上次玩儿的游戏一个，通过游戏的进入时间判断，时间最大的
            lastAuthTime = 0
            
            leastGameId = 0 # 最长时间没玩儿的游戏一个，通过游戏进入时间判断，时间最小的
            leastAuthTime = 0
            
            neverGames = [] # 没玩儿的游戏若干，没有游戏记录的，游戏登录次数为0的
            for game in gameIds:
                loginSum = gamedata.getGameAttr(userId, game, 'loginsum')
                if 0 == loginSum:
                    neverGames.append(game)
                else:
                    if loginSum > mostGameLoginSum:
                        mostGameId = game
                        mostGameLoginSum = loginSum
                    
                    authorTimeStr = gamedata.getGameAttr(userId, game, 'authorTime')
                    _lastAuthTime = 0
                    if authorTimeStr:
                        _lastAuthTime = pktimestamp.timestrToTimestamp(authorTimeStr, '%Y-%m-%d %H:%M:%S.%f')
                        
                    if _lastAuthTime and (_lastAuthTime > lastAuthTime):
                        lastGameId = game
                        lastAuthTime = _lastAuthTime
                        
                    if 0 == leastAuthTime or (_lastAuthTime and (_lastAuthTime < leastAuthTime)):
                        leastAuthTime = _lastAuthTime
                        leastGameId = game
            
            ftlog.debug('mostGameId:', mostGameId
                        , ' lastGameId:', lastGameId
                        , ' leastGameId:', leastGameId
                        , ' neverGames:', neverGames)
            
            choices = []
            if mostGameId:
                choices.append(TYPE_MOST)
            if lastGameId:
                choices.append(TYPE_LAST)
            if leastGameId:
                choices.append(TYPE_LEAST)
            if neverGames:
                choices.append(TYPE_NEVER)
            
            if not choices:
                return
            
            cType = random.choice(choices)
            cGame = 0
            if TYPE_MOST == cType:
                cGame = mostGameId
            elif TYPE_LAST == cType:
                cGame = lastGameId
            elif TYPE_LEAST == cType:
                cGame = leastGameId
            elif TYPE_NEVER == cType:
                cGame = random.choice(neverGames)
                
            ftlog.debug('cType:', cType
                        , ' cGame:', cGame)
            
            reminds = []
            for remindGame in remindGames:
                gameId = remindGame.get('gameId', 0)
                if gameId == cGame:
                    reminds.append(remindGame)
            
            if reminds:
                remind = random.choice(reminds)
                ftlog.debug('remind:', remind)
                # 第四，选择游戏进行引导挽留
                return sendExitPluginRemindMsg(userId, _gameId, clientId, remind, cType)
                
    return '1'

def sendExitPluginRemindMsg(userId, gameId, clientId, remindGame, cType):
    '''
    发送快开配置的消息给客户端
    '''
    ftlog.debug('userId:', userId
                , ' gameId:', gameId
                , ' clientId:', clientId
                , ' remindGame:', remindGame
                , ' cType:', cType)
    
    mo = MsgPack()
    mo.setCmd('game')
    mo.setResult('action', 'get_exit_plugin_remind')
    # 快速开始按钮的显示名称
    mo.setResult('name', remindGame.get('name', ''))
    mo.setResult('gameId', gameId)
    mo.setResult('enterGameId', remindGame.get('gameId', 0))
    mo.setResult('userId', userId)
    # 快速开始按钮的行为
    mo.setResult('enter_param', remindGame.get('enter_param', {}))
    # 文案提示
    tips = remindGame.get('tips', {})
    if TYPE_MOST == cType:
        mo.setResult('tips', tips.get('most', ''))
    elif TYPE_LAST == cType:
        mo.setResult('tips', tips.get('last', ''))
    elif TYPE_LEAST == cType:
        mo.setResult('tips', tips.get('least', ''))
    elif TYPE_NEVER == cType:
        mo.setResult('tips', tips.get('never', ''))
        
    router.sendToUser(mo, userId)
            
    ftlog.debug('userId:', userId
                , ' gameId:', gameId
                , ' clientId:', clientId
                , ' message:', mo)
            
    return mo