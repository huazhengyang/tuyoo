# -*- coding: utf-8 -*-
from poker.entity.dao import daoconst, daobase
from poker.servers.util.rpc._private import user_scripts

def getTableAttrs(roomId, tableId, attrlist, filterKeywords=True):
    """
    获取用户游戏属性列表
    """
    pass

def setTableAttrs(roomId, tableId, attrlist, valuelist):
    """
    设置用户游戏属性列表
    """
    pass

def delTableAttrs(roomId, tableId, attrlist):
    """
    删除用户游戏属性列表
    """
    pass

def getTableAttr(roomId, tableId, attrname, filterKeywords=True):
    """
    获取用户游戏属性
    """
    pass

def setTableAttr(roomId, tableId, attrname, value):
    """
    设置用户游戏属性
    """
    pass

def incrTableAttr(roomId, tableId, attrname, value):
    """
    INCR用户游戏属性
    """
    pass

def incrTableAttrLimit(roomId, tableId, attrname, deltaCount, lowLimit, highLimit, chipNotEnoughOpMode):
    """
    INCR用户游戏属性
    参考: incr_chip_limit
    """
    pass