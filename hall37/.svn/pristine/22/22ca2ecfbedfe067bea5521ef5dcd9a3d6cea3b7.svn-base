# -*- coding:utf-8 -*-
'''
Created on 2017年11月27日

@author: zhaoliang
'''
from hall.entity import hallconf, hall_exit_plugin_remind
from freetime.util import log as ftlog
from poker.entity.dao import gamedata
import poker.util.timestamp as pktimestamp
import random

def queryExitPluginRemind(userId, _gameId, clientId, gamesUserCanSee):
    '''
    获取推荐的快开配置
    '''
    templateName = hallconf.getExitPluginRemindTemplateName(clientId)
    ftlog.debug('templateName:', templateName)
    
    templates = hall_exit_plugin_remind._ordersMap.get('templates', [])
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
                choices.append(hall_exit_plugin_remind.TYPE_MOST)
            if lastGameId:
                choices.append(hall_exit_plugin_remind.TYPE_LAST)
            if leastGameId:
                choices.append(hall_exit_plugin_remind.TYPE_LEAST)
            if neverGames:
                choices.append(hall_exit_plugin_remind.TYPE_NEVER)
            
            if not choices:
                return
            
            cType = random.choice(choices)
            cGame = 0
            if hall_exit_plugin_remind.TYPE_MOST == cType:
                cGame = mostGameId
            elif hall_exit_plugin_remind.TYPE_LAST == cType:
                cGame = lastGameId
            elif hall_exit_plugin_remind.TYPE_LEAST == cType:
                cGame = leastGameId
            elif hall_exit_plugin_remind.TYPE_NEVER == cType:
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
                return hall_exit_plugin_remind.sendExitPluginRemindMsg(userId, _gameId, clientId, remind, cType)
                
    return '1'

hall_exit_plugin_remind.queryExitPluginRemind = queryExitPluginRemind