# -*- coding: utf-8 -*-
"""
Created on 2015-5-12
@author: zqh
"""
from poker.entity.dao import daoconst, daobase
from poker.util import strutil
from poker.servers.util.rpc._private import user_scripts
from poker.servers.util.direct import dbplaytime

def getGameAttrs(uid, gameid, attrlist, filterKeywords=False):
    """
    获取用户游戏属性列表
    """
    pass

def setGameAttrs(uid, gameid, attrlist, valuelist):
    """
    设置用户游戏属性列表
    """
    pass

def delGameAttr(uid, gameid, attrname):
    pass

def delGameAttrs(uid, gameid, attrlist):
    pass

def getGameAttr(uid, gameid, attrname, filterKeywords=False):
    """
    获取用户游戏属性
    """
    pass

def getAllAttrs(uid, gameid, key):
    pass

def getGameAttrJson(uid, gameid, attrname, defaultVal=None):
    """
    获取用户游戏属性
    """
    pass

def setGameAttr(uid, gameid, attrname, value):
    """
    设置用户游戏属性
    """
    pass

def getGameAttrInt(uid, gameid, attrname):
    pass

def setnxGameAttr(uid, gameid, attrname, value):
    pass

def incrGameAttr(uid, gameid, attrname, value):
    """
    INCR用户游戏属性
    """
    pass

def incrGameAttrLimit(uid, gameid, attrname, deltaCount, lowLimit, highLimit, chipNotEnoughOpMode):
    """
    INCR用户游戏属性
    参考: incr_chip_limit
    """
    pass

def isGameExists(uid, gameid):
    """
    判定当前的游戏数据是否存在
    """
    pass

def incrPlayTime(userId, detalTime, gameId, roomId=(-1), tableId=(-1)):
    pass