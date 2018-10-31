# -*- coding: utf-8 -*-
"""
Created on 2017年8月10日

@author: zhaojiangang
"""
from poker.entity.game.rooms.group_match_ctrl.const import MatchFinishReason
from poker.entity.game.rooms.group_match_ctrl.match import MatchGroup

def _doFinish(self, reason=MatchFinishReason.FINISH):
    pass
MatchGroup._doFinish = _doFinish