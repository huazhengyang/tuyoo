# -*- coding: utf-8 -*-
'''
Created on 2015年5月20日

@author: zqh
'''

import freetime.util.log as ftlog
from hall.entity import hallconf, hallitem, hallbenefits, hallstartchip,\
    hall_login_reward, hall_item_exchange
from hall.entity.hallconf import HALL_GAMEID
from poker.entity.configure import gdata
from poker.entity.dao import gamedata
from poker.entity.game.game import TYGame
import poker.util.timestamp as pktimestamp


def getInitDataKeys():
    '''
    取得游戏数据初始化的字段列表
    '''
    return ['lastlogin', 'nslogin', 'loginsum']


def getInitDataValues():
    '''
    取得游戏数据初始化的字段缺省值列表
    '''
    return [0, 0, 0]


def createGameData(userId, clientId):
    ftlog.debug('hall.createGameData', userId, clientId)
    # 初始化基本数据
    gdkeys = getInitDataKeys()
    gdata = getInitDataValues()
    gamedata.setGameAttrs(userId, HALL_GAMEID, gdkeys, gdata)
    # 初始化用户大厅道具
    # 初始化用户大厅勋章
    # 初始化用户大厅任务
    return gdkeys, gdata


def getDaShiFen(userId, clientId):
    '''
    取得当前用户的游戏账户的大师分信息
    '''
    ftlog.debug('hall.getDaShiFen', userId, clientId)
    return {}


def getGameInfo(userId, clientId):
    '''
    取得当前用户的游戏账户信息dict
    '''
    ftlog.debug('hall.getGameInfo', userId, clientId)
    # 大厅游戏, 获取所有游戏的大师分
    gameids = hallconf.getDaShiFenFilter(clientId)
    allGameIds = gdata.gameIds()
    dashifen = {}
    i = 0
    for gid in gameids :
        if gid in allGameIds :
            infos = TYGame(gid).getDaShiFen(userId, clientId)
            if infos :
                infos['index'] = i
                dashifen[gid] = infos
                i = i + 1
    return {'dashifen' : dashifen}


def loginGame(userId, gameId, clientId, iscreate, isdayfirst):
    ftlog.debug('hall.loginGame', userId, gameId, clientId, iscreate, isdayfirst)
    
    if isdayfirst:
        # 游戏登录天数加1
        gamedata.incrGameAttr(userId, HALL_GAMEID, 'loginDays', 1)
        # 检测发送登录奖励
        hall_login_reward.sendLoginReward(userId, HALL_GAMEID, clientId)

        if gameId == HALL_GAMEID:
            from hall.entity import newcheckin
            newcheckin.complementByVip(userId, gameId, clientId)
            
    hallitem._onUserLogin(gameId, userId, clientId, iscreate, isdayfirst)
    # 自动更新用户道具
    hall_item_exchange.updateUserItems(userId, gameId, clientId)
    if not (iscreate or hallstartchip.needSendStartChip(userId, gameId)):
        hallbenefits.benefitsSystem.sendBenefits(gameId, userId, pktimestamp.getCurrentTimestamp())

