# -*- coding: utf-8 -*-
"""
Created on 2013-3-18

@author: Administrator
"""
from poker.servers.util.direct import dbbi

def incrGcoin(rkey, coinKey, detalCount):
    """
    增加全局金流的数值，此方法由bireport方法调用
    rkey的格式为：<gameId> + ":" + <YYYYMMDD>
    coinKey为业务逻辑的全局金流键值
    detalCount 为数据的变化量，整形数值
    """
    pass

def setConnOnLineInfo(serverId, userCount):
    """
    向BI数据库汇报当前CONN进程的在线人数
    """
    pass

def getConnOnlineUserCount():
    """
    取得当前所有在线的用户数量(链接TCP的用户数量)
    """
    pass

def setRoomOnLineInfo(gameId, roomId, userCount, playTableCount, observerCount):
    """
    设置当前的给入的房间的人数和游戏中的桌子数及旁观者的数量
    """
    pass

def getRoomOnLineUserCount(gameId, withShadowRoomInfo):
    """
    重BI数据库中取得当前的游戏的所有的在线人数信息
    return allcount, counts, details, allobcount, obcounts, obdetails
    allcount int，游戏内所有房间的人数的总和
    counts 字典dict，key为大房间ID（bigRoomId)，value为该大房间内的人数总和
    details 字典dict，key为房间实例ID（roomId），value为该房间内的人数
    allobcount, obcounts, obdetails 观察者数量，需要table类实现observersNum属性
    此数据由每个GR，GT进程每10秒钟向BI数据库进行汇报一次
    """
    pass