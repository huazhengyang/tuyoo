# -*- coding: utf-8 -*-
"""
Created on 2017年10月26日

@author: zhaoliang
"""
from freetime.core.lock import locked
from freetime.util import log as ftlog

@locked
def doWinlose(self, msg):
    pass
from poker.entity.game.rooms.async_common_arena_match_room import TyAsyncCommonArenaMatchRoom
TyAsyncCommonArenaMatchRoom.doWinlose = doWinlose