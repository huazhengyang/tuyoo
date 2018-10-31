# -*- coding: utf-8 -*-
import json
from freetime.util.cache import lfu_time_cache
import freetime.util.log as ftlog
from poker.entity.configure import pokerconf
from poker.entity.dao import daobase, daoconst
from poker.entity.dao.daoconst import UserDataSchema, UserSessionSchema, UserLocationSchema, UserWeakSchema, UserOnlineGameSchema
from poker.protocol.rpccore import markRpcCall
from poker.servers.rpc import roommgr
from poker.servers.util.rpc import dbonline
from poker.servers.util.rpc._private import dataswap, user_scripts
from poker.util import strutil, timestamp
from time import time
from poker.servers.util.direct import dbplaytime
_CACHE_GROUP = 'userdata'
_CACHE_SIZE = daoconst.DATA_CACHE_SIZE
_CACHE_USER_ENABLE = 0

@markRpcCall(groupName='userId', lockName='', syncCall=1)
def _checkUserData(userId, clientId=None, appId=0, session={}):
    pass

@markRpcCall(groupName='userId', lockName='', syncCall=1)
def _updateUserDataAuthorTime(userId):
    pass

@markRpcCall(groupName='userId', lockName='', syncCall=1)
def _updateUserDataAliveTime(userId):
    pass

@markRpcCall(groupName='userId', lockName='', syncCall=1)
def _updateUserGameDataAuthorTime(userId, gameId):
    pass

@lfu_time_cache(maxsize=_CACHE_SIZE, mainindex=0, subindex=1, group=_CACHE_GROUP)
def _cacheSession(userId, dataKey):
    pass

def _getSessionDataRedis(userId, dataKey):
    pass

@markRpcCall(groupName='userId', lockName='', syncCall=1)
def _getSessionDatas(userId):
    pass

@markRpcCall(groupName='userId', lockName='', syncCall=1)
def _setSessionDatas(userId, datas):
    pass

@lfu_time_cache(maxsize=_CACHE_SIZE, mainindex=0, subindex=1, group=_CACHE_GROUP)
def _cacheUser(userId, dataKey):
    pass

def _getUserDataRedis(userId, dataKey):
    pass

@markRpcCall(groupName='userId', lockName='', syncCall=1)
def _getUserDatas(userId, fieldList):
    pass

@markRpcCall(groupName='userId', lockName='', syncCall=1)
def _setUserDatas(userId, datas):
    pass

@markRpcCall(groupName='userId', lockName='', syncCall=1)
def _setUserDatasNx(userId, datas):
    pass

@markRpcCall(groupName='userId', lockName='', syncCall=1)
def _setUserDatasForce(userId, datas):
    pass

@markRpcCall(groupName='userId', lockName='', syncCall=1)
def _delUserDatas(userId, datas):
    pass

@markRpcCall(groupName='userId', lockName='', syncCall=1)
def _incrUserDatas(userId, field, value):
    pass

@markRpcCall(groupName='userId', lockName='', syncCall=1)
def _incrUserDatasLimit(userId, field, value, lowLimit, highLimit, chipNotEnoughOpMode, dataKey=None):
    pass

@markRpcCall(groupName='userId', lockName='', syncCall=1)
def _setTableChipToRange(userId, gameid, _min, _max, eventId, intEventParam, clientId, tableId, rhashkey, rfield):
    pass

@lfu_time_cache(maxsize=_CACHE_SIZE, mainindex=0, subindex=1, group=_CACHE_GROUP)
def _cacheWeak(userId, dataKey):
    pass

def _getWeakDataRedis(userId, dataKey):
    pass

@markRpcCall(groupName='userId', lockName='', syncCall=1)
def _getWeakData(userId, gameId, weakname, cycleName, curCycle):
    pass

@markRpcCall(groupName='userId', lockName='', syncCall=1)
def _setWeakData(userId, gameId, weakname, datas, cycleName, curCycle, expire):
    pass

@markRpcCall(groupName='userId', lockName='', syncCall=1)
def _setOnlineState(userId, state):
    """
    设置用户的在线状态,即TCP的链接状态
    用户ID将添加再online数据库的online:users集合
    注意: 此方法通常由CONN服务进行调用,其他人禁止调用
    """
    pass

@markRpcCall(groupName='userId', lockName='', syncCall=1)
def _getOnlineState(userId):
    """
    取得用户的在线状态,即TCP的链接状态
    """
    pass

@markRpcCall(groupName='userId', lockName='', syncCall=1)
def _setGameEnter(userId, gameId):
    """
    设置用户进入一个游戏
    通常再bind_game时调用此方法
    数据库中, 存储的键值为: og:<userId>
    """
    pass

@markRpcCall(groupName='userId', lockName='', syncCall=1)
def _getLastGameId(userId):
    """
    取得用户最后进入的gameId
    """
    pass

@markRpcCall(groupName='userId', lockName='', syncCall=1)
def _setGameLeave(userId, gameId):
    """
    设置用户离开一个游戏
    通常再leave_game时调用此方法
    数据库中, 存储的键值为: og:<userId>
    """
    pass

@markRpcCall(groupName='userId', lockName='', syncCall=1)
def _getGameEnterIds(userId):
    """
    取得用户进入的游戏列表
    """
    pass

@markRpcCall(groupName='userId', lockName='', syncCall=1)
def _addOnlineLoc(userId, roomId, tableId, seatId, checkConfict):
    """
    添加一个用户的在线位置, 
    注意: 子键值为roomId+'.'+tableId, 因此不允许用户再同一个桌子的不同桌位坐下
    通常此方法在用户真实坐在某一个桌位后调用
    """
    pass

@markRpcCall(groupName='userId', lockName='', syncCall=1)
def _getOnlineLocSeatId(userId, roomId, tableId):
    """
    取得用户再桌子上的ID
    若不在桌子上返回0
    同_addOnlineLoc为配对方法
    """
    pass

@markRpcCall(groupName='userId', lockName='', syncCall=1)
def _removeOnlineLoc(userId, roomId, tableId):
    """
    移除一个用户的在线位置
    通常此方法在用户真实离开某一个桌位后调用
    """
    pass

@markRpcCall(groupName='userId', lockName='', syncCall=1)
def _cleanOnlineLoc(userId):
    """
    移除一个用户的所有在线位置
    """
    pass

@markRpcCall(groupName='userId', lockName='', syncCall=1)
def _getOnlineLocList(userId):
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

@markRpcCall(groupName='userId', lockName='', syncCall=1)
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

@markRpcCall(groupName='userId', lockName='', syncCall=1)
def _clearUserCache(userId):
    pass