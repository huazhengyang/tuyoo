# -*- coding:utf-8 -*-
'''
Created on 2017年2月14日

@author: zhaojiangang
'''
from poker.entity.dao import gamedata


_VERSION_KEY = 'session.dizhu.version'

def getGameClientVer(gameId, userId):
    return gamedata.getGameAttr(userId, gameId, _VERSION_KEY)

def setGameClientVer(gameId, userId, ver):
    if not isinstance(ver, (float, int)):
        version = float(ver)
    return gamedata.setGameAttr(userId, gameId, _VERSION_KEY, version)