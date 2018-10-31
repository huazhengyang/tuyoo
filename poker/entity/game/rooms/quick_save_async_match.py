# -*- coding: utf-8 -*-
from freetime.util import log as ftlog
from poker.entity.dao import onlinedata
from poker.util import strutil
from poker.entity.configure import gdata
from poker.servers.room.rpc import async_upgrade_hero_match_remote, async_common_arena_match_remote
from freetime.entity.msg import MsgPack
from poker.protocol import router

def doSaveAsyncMatch(userId, gameId, clientId, version, filterBigRoomId=0):
    """
    保存异步比赛
    """
    pass

def _isAsyncUpgradeMatch(roomId):
    pass

def _isAsyncCommonArenaMatch(roomId):
    pass