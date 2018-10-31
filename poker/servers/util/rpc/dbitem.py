# -*- coding: utf-8 -*-
import base64
from freetime.util.cache import lfu_time_cache
from poker.entity.dao import daobase
from poker.entity.dao.daoconst import GameItemSchema
from poker.protocol.rpccore import markRpcCall
from poker.servers.util.rpc.dbuser import _CACHE_SIZE, _CACHE_GROUP
_CACHE_ITEM_ENABLE = 0

@lfu_time_cache(maxsize=_CACHE_SIZE, mainindex=0, subindex=1, group=_CACHE_GROUP)
def _cacheItem(userId, dataKey):
    pass

def _getItemDataRedis(userId, dataKey):
    pass

def _getItemDataAll(userId, gameId):
    pass

@markRpcCall(groupName='userId', lockName='', syncCall=1)
def _getItemDataAll_(userId, gameId):
    """
    取得用户所有的道具数据
    """
    pass

def _setItemData(userId, gameId, itemId, itemData):
    pass

@markRpcCall(groupName='userId', lockName='', syncCall=1)
def _setItemData_(userId, gameId, itemId, itemDataB64):
    """
    设置用户的一个道具的数据
    """
    pass

@markRpcCall(groupName='userId', lockName='', syncCall=1)
def _delItemData(userId, gameId, itemId):
    """
    删除用户的一个道具的数据
    """
    pass