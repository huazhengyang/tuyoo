# -*- coding: utf-8 -*-
"""
Created on 2015-5-12
@author: zqh
"""
from poker.entity.dao.lua_scripts.util_scripts import LUA_FUN_TY_TOBMBER
ALIAS_GET_BEST_TABLE_ID_LUA = 'GET_BEST_TABLE_ID_LUA'
GET_BEST_TABLE_ID_LUA = '\n    local datas = redis.call("ZRANGE", KEYS[1], -1, -1, "WITHSCORES")\n    redis.call("ZREM", KEYS[1], datas[1])\n    return datas\n'
ALIAS_UPDATE_TABLE_SCORE_LUA = 'UPDATE_TABLE_SCORE_LUA'
UPDATE_TABLE_SCORE_LUA = (LUA_FUN_TY_TOBMBER + '\n    local tableKey = KEYS[1]\n    local tableId = KEYS[2]\n    local tableScore = KEYS[3]\n    local force = KEYS[4]\n    if force then\n        return redis.call("ZADD", tableKey, tableScore, tableId)\n    else\n        local oldScore = redis.call("ZSCORE", tableKey, tableId)\n        oldScore = ty_tonumber(oldScore)\n        if oldScore <= 0 then\n            return redis.call("ZADD", tableKey, tableScore, tableId)\n        else\n            return oldScore\n        end\n    end\n')
AlIAS_TETRIS_BEST_ID_LUA = 'GET_TETRIS_BEST_TABLE_ID'
GET_TETRIS_BEST_TABLE_ID_LUA = '\n    local minscore = KEYS[2]\n    local maxscore = KEYS[3]\n    local randint = KEYS[4]\n\n    local datas = redis.call("ZRANGEBYSCORE", KEYS[1], KEYS[2], KEYS[3], "WITHSCORES")\n    local len = #datas\n    if len == 0 then\n        datas = redis.call("ZRANGEBYSCORE", KEYS[1], 100, 5000, "WITHSCORES")\n    end\n\n    len = #datas\n    if len == 0 then\n        datas = redis.call("ZREVRANGEBYSCORE", KEYS[1], 50, 50, "WITHSCORES")\n        redis.call("ZREM", KEYS[1], datas[1])\n        return {datas[1], datas[2]}\n    else\n        local index = randint%(len/2)*2\n        redis.call("ZREM", KEYS[1], datas[index+1] )\n        return {datas[index+1], datas[index+2]}\n    end\n'