# -*- coding: utf-8 -*-
"""
Created on 2015-5-12
@author: zqh
"""
LUA_FUN_TY_TOBMBER = '\nlocal function ty_tonumber(val)\n    val = tonumber(val)\n    if val == nil then\n        return 0\n    end\n    return val\nend\n'
FUN_INCR_HASH_CHIP_FIELD = (LUA_FUN_TY_TOBMBER + "\nlocal function incr_hash_field(key, field, delta, mode, lowLimit, highLimit)\n    local cur = ty_tonumber(redis.call('hget', key, field))\n    local final = cur\n    local fixed = 0\n    if cur < 0 then\n        fixed = -cur\n        final = ty_tonumber(redis.call('hincrby', key, field, fixed))\n        cur = final\n    end\n    if lowLimit ~= -1 and cur < lowLimit then\n        return {0, final, fixed}\n    end\n    if highLimit ~= -1 and cur > highLimit then\n        return {0, final, fixed}\n    end\n    if delta >= 0 or cur + delta >= 0 then\n        final = ty_tonumber(redis.call('hincrby', key, field, delta))\n        return {delta, final, fixed}\n    end\n    if mode == 0 or cur == 0 then\n        return {0, cur, fixed}\n    end\n    final = ty_tonumber(redis.call('hincrby', key, field, -cur))\n    return {-cur, final, fixed}\nend\n")