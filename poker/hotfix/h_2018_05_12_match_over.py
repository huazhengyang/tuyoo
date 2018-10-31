# -*- coding: utf-8 -*-
"""
Created on 2018年05月12日

比赛结束的消息100%发到前端

@author: zhaoliang
"""
from freetime.util import log as ftlog
from poker.entity.dao import onlinedata
from poker.entity.game.rooms.async_common_arena_match_ctrl.aca_game_player import AsyncCommonArenaPlayer
from poker.entity.game.rooms.async_common_arena_match_ctrl.aca_match_db import AsyncCommonArenaMatchDataBase
from poker.entity.game.rooms.async_common_arena_match_ctrl.aca_match_report import AsyncCommonArenaReport
from poker.entity.game.rooms.async_common_arena_match_ctrl.aca_game_record import AsyncCommonArenaRecords

def matchOver(self, userId, rank):
    """
    比赛结束
    """
    pass
from poker.entity.game.rooms.async_common_arena_match_ctrl.aca_match import AsyncCommonArenaMatch
AsyncCommonArenaMatch.matchOver = matchOver