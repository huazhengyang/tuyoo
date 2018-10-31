# -*- coding: utf-8 -*-
"""
Created on 2017年10月30日

@author: wangyonghui
"""
import freetime.util.log as ftlog
from poker.entity.game.rooms.arena_match_ctrl.match import MatchInstance

def _doStop(self):
    pass
MatchInstance._doStop = _doStop