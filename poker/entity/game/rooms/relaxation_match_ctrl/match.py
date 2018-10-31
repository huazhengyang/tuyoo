# -*- coding: utf-8 -*-
"""
Created on 2016年6月7日

@author: luoguanggui
"""
from datetime import datetime
import time
from freetime.core.lock import locked
from poker.entity.biz import bireport
from poker.entity.biz.content import TYContentItem
from poker.entity.configure import gdata
from poker.entity.game.game import TYGame
from poker.entity.game.rooms import roominfo
from poker.entity.game.rooms.relaxation_match_ctrl.models import Player
from poker.entity.game.rooms.relaxation_match_ctrl.utils import HeartbeatAble
from poker.entity.game.rooms.relaxation_match_ctrl.models import TableManager
from poker.entity.game.rooms.roominfo import MatchRoomInfo
from poker.util import strutil
import poker.util.timestamp as pktimestamp
from poker.entity.game.rooms.relaxation_match_ctrl.utils import Logger
from poker.entity.game.rooms.relaxation_match_ctrl.const import TOP_N
from poker.entity.game.rooms.relaxation_match_ctrl.events import MatchStartEvent, MatchOverEvent

class MatchRelaxation(HeartbeatAble, ):
    ST_IDLE = 0
    ST_START = 2

    def __init__(self, conf, room):
        pass

    @property
    def state(self):
        pass

    @property
    def matchConf(self):
        pass

    @property
    def playerCount(self):
        pass

    @property
    def playerMap(self):
        pass

    @property
    def ranktops(self):
        pass

    @property
    def startTime(self):
        pass

    @property
    def endTime(self):
        pass

    def findTable(self, tableId):
        pass

    def clear(self):
        pass

    def initTableManager(self, room, tableSeatCount, matchId):
        pass

    def findPlayer(self, userId):
        pass

    def addPlayer(self, player):
        pass

    def enter(self, userId):
        pass

    def leave(self, userId):
        pass

    def start(self):
        pass

    def winlose(self, player, deltaScore, isWin):
        pass

    def returnTable(self, table):
        pass

    def _doHeartbeatImpl(self):
        pass

    def _doStart(self, todayStartTime, todayEndTime):
        pass

    def _doFinish(self):
        pass

    def _sortMatchTopRanks(self, player):
        pass

    def _sortMatchRanks(self):
        pass

    def _doPlayerMatchOver(self, player):
        pass

    def _getRewards(self, player):
        pass

    def onPlayerSitdown(self, player, table, isNewPlayer):
        pass