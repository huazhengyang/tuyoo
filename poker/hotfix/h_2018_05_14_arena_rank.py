# -*- coding: utf-8 -*-
"""
Created on 2018年05月12日

比赛结束的消息100%发到前端

@author: zhaoliang
"""
import copy
from freetime.util import log as ftlog

def _getRank(self, score):
    """
    获取排名
    自学习
    """
    pass
from poker.entity.game.rooms.async_common_arena_match_ctrl.aca_game_stage import AsyncCommonArenaStage
AsyncCommonArenaStage._getRank = _getRank