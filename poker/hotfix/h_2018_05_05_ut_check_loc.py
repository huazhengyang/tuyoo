# -*- coding: utf-8 -*-
"""
Created on 2017年10月26日

@author: zhaoliang
"""
from poker.servers.util.direct import dbuser
from poker.util import strutil
from poker.entity.configure import gdata, pokerconf
from poker.servers.rpc import roommgr
from freetime.util import log as ftlog

def _checkUserLoc(userId, clientId, matchGameId=0):
    """
           玩家断线重连时，loc的信息可能与table不一致，conn server需要与table server通讯检查一致性；
           导致不一致的原因：服务端重启（特别是roomId、tableId变更）
           如果玩家在队列房间或者比赛房间的等待队列中, 此处不做一致性检查，等玩家发起quick_start时由room server检查
       What：
           与table server通讯检查桌子对象里是否有这个玩家的数据
           如果不一致，则回收牌桌金币并清空loc；
       Return：
           如果玩家在房间队列里，返回gameId.roomId.roomId*10000.1
           如果玩家在座位上，返回gameId.roomId.tableId.seatId
           如果玩家在旁观，返回gameId.roomId.tableId.0
           玩家不在table对象里，返回0.0.0.0
    """
    pass
dbuser._checkUserLoc = _checkUserLoc