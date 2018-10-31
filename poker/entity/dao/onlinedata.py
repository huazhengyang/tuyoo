# -*- coding: utf-8 -*-
"""
Created on 2015-5-12
@author: zqh
"""
from poker.entity.dao import daoconst
from poker.servers.util.direct import dbuser, dbonline, dbgeo
from poker.entity.configure import gdata
OFFLINE = daoconst.OFFLINE
ONLINE = daoconst.ONLINE

def getOnlineRandUserIds(count):
    """
    随机取得count个在线用户的ID列表, 如果集合的数量不足count个, 那么返回集合所有内容
    """
    pass

def setGameOnline(userId, gameId, groupname):
    """
    设置用户再当前游戏的在线状态为"在线"
    通常再bind_game时调用此方法
    groupname为一个分组名称的列表, 例如:'chip_gt_100w', 'vipuser'
    数据库中, 存储的键值为: onlinelist:<gameId>:<groupname>
    数据onlinelist_allkeys包含了所有出现过的数据集合键值, 再删除online状态时使用, 
    因此,需要系统每个一段时间检查这个集合中的值是否是有效的键值
    """
    pass

def setGameOffline(userId, gameId, groupname):
    """
    设置用户再当前游戏的在线状态为"离线"
    groupname为一个分组名称的列表, 例如:'chip_gt_100w', 'vipuser'
    数据库中, 存储的键值为: onlinelist:<gameId>:<groupname>
    通常再unbind_game时或用户TCP断线时调用此方法,
    """
    pass

def getGameOnlineUserIds(gameId, groupname, callback):
    """
    取得当前游戏的在线分组的所有userid列表
    数据库中, 存储的键值为: onlinelist:<gameId>:<groupname>
    每次返回最多1000个userid, 调用callback函数
    例如: callback([10001, 10003, 10023])
    """
    pass

def getGameOnlineRandUserIds(gameId, groupname, count):
    """
    取得当前游戏的在线分组的所有userid列表
    数据库中, 存储的键值为: onlinelist:<gameId>:<groupname>
    随机返回count个集合中的userId列表
    """
    pass

def getGameOnlineCount(gameId, groupname):
    """
    取得当前游戏的在线分组的userId的数量
    数据库中, 存储的键值为: onlinelist:<gameId>:<groupname>
    返回集合的元素个数
    """
    pass

def setOnlineState(userId, state):
    """
    设置用户的在线状态,即TCP的链接状态
    用户ID将添加再online数据库的online:users集合
    注意: 此方法通常由CONN服务进行调用,其他人禁止调用
    """
    pass

def getOnlineState(userId):
    """
    取得用户的在线状态,即TCP的链接状态
    """
    pass

def addOnlineLoc(userId, roomId, tableId, seatId, checkConfict=True):
    """
    添加一个用户的在线位置, 
    注意: 子键值为roomId+'.'+tableId, 因此不允许用户再同一个桌子的不同桌位坐下
    通常此方法在用户真实坐在某一个桌位后调用
    """
    pass

def setBigRoomOnlineLoc(userId, roomId, tableId, seatId):
    """
    添加一个用户的在线位置, 
    注意: 子键值为roomId+'.'+tableId, 因此不允许用户再同一个桌子的不同桌位坐下
    此方法将会检查当前的所有loc，如果存在和roomId一直的bigRoomId的loc那么删除原loc设置新loc
    """
    pass

def getOnlineLocSeatId(userId, roomId, tableId):
    """
    添加一个用户的在线位置, 
    注意: 子键值为roomId+'.'+tableId, 因此不允许用户再同一个桌子的不同桌位坐下
    通常此方法在用户真实坐在某一个桌位后调用
    """
    pass

def removeOnlineLoc(userId, roomId, tableId):
    """
    移除一个用户的在线位置
    通常此方法在用户真实离开某一个桌位后调用
    """
    pass

def cleanOnlineLoc(userId):
    """
    移除一个用户的所有在线位置
    """
    pass

def getOnlineLocList(userId):
    """
    取得当前用户的所有在线位置信息list
    返回loc的数组列表, 每一项为一个3项值, 分别为: roomId, tableId, seatId
    示例 :
        return [
                [roomId1, tableId1, seatId1],
                [roomId2, tableId2, seatId2],
                ]
    """
    pass

def checkUserLoc(userId, clientId, matchGameId=0):
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

def setGameEnter(userId, gameId):
    """
    设置用户进入一个游戏
    通常再bind_game时调用此方法
    数据库中, 存储的键值为: og:<userId>
    """
    pass

def getLastGameId(userId):
    """
    取得用户最后一个进入的游戏ID
    """
    pass

def setGameLeave(userId, gameId):
    """
    设置用户进入一个游戏
    通常再leave_game时调用此方法
    数据库中, 存储的键值为: og:<userId>
    """
    pass

def getGameEnterIds(userId):
    """
    清理用户进入的游戏列表
    通常再tcp断线时调用此方法
    数据库中, 存储的键值为: og:<userId>
    """
    pass

def setUserGeoOffline(userId, gameId):
    """
    设置给出的用户GEO为离线状态, 此方法主要为配合GEO的业务
    """
    pass