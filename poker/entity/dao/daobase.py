# -*- coding: utf-8 -*-
"""
Created on 2015-5-12
@author: zqh
"""
from datetime import datetime
import json
import freetime.aio.redis as ftred
import freetime.entity.config as ftcon
import freetime.util.log as ftlog
from poker.entity.dao import daoconst
from poker.entity.dao.lua_scripts import room_scripts
from poker.util import keywords
from poker.util import reflection
__luascripts = {}
__user_redis_conns = []
__user_redis_conns_len = 0
__table_redis_conns = []
__table_redis_conns_len = 0
__mix_redis_conn = None
__forbidden_redis_conn = None
__keymap_redis_conns = []
__keymap_redis_conns_len = 0
__paydata_redis_conn = None
__geo_redis_conn = None
__config_redis_conn = None
__online_redis_conn = None
__replay_redis_conn = None
__rank_redis_conn = None
__dizhu_redis_conn = None
__bi_redis_conn = None
_REDIS_CMD_PPS_ = 0
_REDIS_CMDS_ = {}
_REDIS_COUNT_ = 0
_REDIS_COUNT_TIME_ = datetime.now()

def _redisCmdPps(group, cmds):
    pass

def ppsCountRedisCmd():
    pass

def _initialize():
    pass

def _getRedisCluster(dbnamehead):
    pass

def preLoadLuaScript(scriptModule, luaScript):
    pass

def loadLuaScripts(luaName, luaScript):
    pass

def getLuaScriptsShaVal(luaName):
    pass

def filterValue(attr, value):
    pass

def filterValues(attrlist, values):
    pass

def executeUserCmd(uid, *cmds):
    pass

def sendUserCmd(uid, *cmds):
    pass

def executeUserLua(uid, luaName, *cmds):
    pass

def _getUserDbClusterSize():
    pass

def executeTableCmd(roomId, tableId, *cmds):
    pass

def executeTableLua(roomId, tableId, luaName, *cmds):
    pass

def executeForbiddenCmd(*cmds):
    pass

def executeMixCmd(*cmds):
    pass

def executeMixLua(luaName, *cmds):
    pass

def executeRePlayCmd(*cmds):
    pass

def executeRePlayLua(luaName, *cmds):
    pass

def _executeOnlineCmd(*cmds):
    pass

def _executeOnlineLua(luaName, *cmds):
    pass

def _executeBiCmd(*cmds):
    pass

def _sendBiCmd(*cmds):
    pass

def _executeBiLua(luaName, *cmds):
    pass

def _executeKeyMapCmd(*cmds):
    pass

def _executeKeyMapLua(luaName, *cmds):
    pass

def _executePayDataCmd(*cmds):
    pass

def _executePayDataLua(luaName, *cmds):
    pass

def _executeGeoCmd(*cmds):
    pass

def _sendGeoCmd(*cmds):
    pass

def _executeGeoLua(luaName, *cmds):
    pass

def sendRankCmd(*cmds):
    pass

def executeRankCmd(*cmds):
    pass

def executeRankLua(luaName, *cmds):
    pass

def sendDizhuCmd(*cmds):
    pass

def executeDizhuCmd(*cmds):
    pass

def executeDizhuLua(luaName, *cmds):
    pass