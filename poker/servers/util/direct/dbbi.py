# -*- coding: utf-8 -*-
from poker.entity.configure import gdata
from poker.entity.dao import daobase, daoconst
from poker.util import strutil

def _incrGcoin(rkey, coinKey, detalCount):
    """
    增加全局金流的数值，此方法由bireport方法调用
    rkey的格式为：<gameId> + ":" + <YYYYMMDD>
    coinKey为业务逻辑的全局金流键值
    detalCount 为数据的变化量，整形数值
    """
    pass

def _setConnOnLineInfo(serverId, userCount):
    """
    向BI数据库汇报当前CONN进程的在线人数
    """
    pass

def _getConnOnlineUserCount():
    pass
_ROOMS = {}

def _setRoomOnLineInfo(gameId, roomId, userCount, playTableCount, observerCount):
    pass

def _getRoomOnLineUserCount(gameId, withShadowRoomInfo):
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