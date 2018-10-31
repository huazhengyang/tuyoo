# -*- coding: utf-8 -*-
"""
Created on 2017年5月26日

@author: zhaojiangang
"""
from poker.entity.game.rooms.group_match_ctrl.const import MatchFinishReason
from poker.entity.game.rooms.group_match_ctrl.match import MatchGroup
import poker.util.timestamp as pktimestamp

def _doStart(self):
    pass
MatchGroup._doStart = _doStart