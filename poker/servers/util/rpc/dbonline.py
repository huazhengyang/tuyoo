# -*- coding: utf-8 -*-
"""
Created on 2015-5-12
@author: zqh
"""
from poker.entity.dao import daobase, daoconst
from poker.protocol.rpccore import markRpcCall
_ONLINE_LIST_ALLKEYS = None

def _checkOnlineKeys(newKey=None):
    pass

@markRpcCall(groupName='userId', lockName='', syncCall=1)
def _setOnlineState(userId, state):
    pass

@markRpcCall(groupName='userId', lockName='', syncCall=1)
def _setGameOnline(userId, gameId, groupname):
    """
    设置用户再当前游戏的在线状态为"在线"
    通常再bind_game时调用此方法
    groupname为一个分组名称的列表, 例如:'chip_gt_100w', 'vipuser'
    数据库中, 存储的键值为: onlinelist:<gameId>:<groupname>
    数据onlinelist_allkeys包含了所有出现过的数据集合键值, 再删除online状态时使用, 
    因此,需要系统每个一段时间检查这个集合中的值是否是有效的键值
    """
    pass

@markRpcCall(groupName='userId', lockName='', syncCall=1)
def _setGameOffline(userId, gameId, groupname):
    """
    设置用户再当前游戏的在线状态为"离线"
    groupname为一个分组名称的列表, 例如:'chip_gt_100w', 'vipuser'
    数据库中, 存储的键值为: onlinelist:<gameId>:<groupname>
    通常再unbind_game时或用户TCP断线时调用此方法,
    """
    pass

@markRpcCall(groupName='', lockName='', syncCall=1)
def _executeOnlineSet(*cmds):
    pass

def _getOnlineRandUserIds(count):
    """
    随机取得count个在线用户的ID列表, 如果集合的数量不足count个, 那么返回集合所有内容
    """
    pass

def _getGameOnlineUserIds(gameId, groupname, callback):
    """
    取得当前游戏的在线分组的所有userid列表
    数据库中, 存储的键值为: onlinelist:<gameId>:<groupname>
    每次返回最多1000个userid, 调用callback函数
    例如: callback([10001, 10003, 10023])
    """
    pass

def _getGameOnlineRandUserIds(gameId, groupname, count):
    """
    取得当前游戏的在线分组的所有userid列表
    数据库中, 存储的键值为: onlinelist:<gameId>:<groupname>
    随机返回count个集合中的userId列表
    """
    pass

def _getGameOnlineCount(gameId, groupname):
    """
    取得当前游戏的在线分组的userId的数量
    数据库中, 存储的键值为: onlinelist:<gameId>:<groupname>
    返回集合的元素个数
    """
    pass