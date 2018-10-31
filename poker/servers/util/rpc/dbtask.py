# -*- coding: utf-8 -*-
import base64
from freetime.util.cache import lfu_time_cache
from poker.entity.dao import daobase
from poker.entity.dao.daoconst import GameTaskSchema
from poker.protocol.rpccore import markRpcCall
from poker.servers.util.rpc.dbuser import _CACHE_SIZE, _CACHE_GROUP
_CACHE_TASK_ENABLE = 0

@lfu_time_cache(maxsize=_CACHE_SIZE, mainindex=0, subindex=1, group=_CACHE_GROUP)
def _cacheTask(userId, dataKey):
    pass

def _getTaskDataRedis(userId, dataKey):
    pass

def _getTaskDataAll(userId, gameId):
    pass

@markRpcCall(groupName='userId', lockName='', syncCall=1)
def _getTaskDataAll_(userId, gameId):
    """
    取得用户所有的道具数据
    """
    pass

def _setTaskData(userId, gameId, taskId, taskData):
    pass

@markRpcCall(groupName='userId', lockName='', syncCall=1)
def _setTaskData_(userId, gameId, taskId, taskDataB64):
    """
    设置用户的一个道具的数据
    """
    pass

@markRpcCall(groupName='userId', lockName='', syncCall=1)
def _delTaskData(userId, gameId, taskId):
    """
    删除用户的一个道具的数据
    """
    pass