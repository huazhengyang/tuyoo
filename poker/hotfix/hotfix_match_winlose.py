# -*- coding: utf-8 -*-
"""
Created on 2017年7月31日

@author: wangyonghui
"""
import freetime.util.log as ftlog
from poker.entity.game.rooms.arena_match_ctrl.match import MatchPlayer, MatchInstance

def _clearAndReleaseTable(self, table):
    pass

def winlose(self, player, deltaScore, isWin, isKill=False):
    pass
MatchInstance._clearAndReleaseTable = _clearAndReleaseTable
MatchInstance.winlose = winlose