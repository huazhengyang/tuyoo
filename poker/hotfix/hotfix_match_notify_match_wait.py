# -*- coding: utf-8 -*-
"""
Created on 2017年7月27日

@author: wangyonghui
"""
from poker.entity.biz import bireport
from poker.entity.game.rooms.group_match_ctrl.const import MatchFinishReason, WaitReason
from poker.entity.game.rooms.group_match_ctrl.match import MatchGroup
from poker.entity.game.rooms.group_match_ctrl.models import Player
from poker.entity.game.rooms.group_match_ctrl.utils import PlayerSort
import poker.util.timestamp as pktimestamp

def _doStart(self):
    pass

def _processWinlosePlayersAss(self, winlosePlayerList):
    pass

def _processWinlosePlayersDieout(self, winlosePlayerList):
    pass

def _processWaitPlayers(self):
    pass
MatchGroup._doStart = _doStart
MatchGroup._processWinlosePlayersAss = _processWinlosePlayersAss
MatchGroup._processWinlosePlayersDieout = _processWinlosePlayersDieout
MatchGroup._processWaitPlayers = _processWaitPlayers