# -*- coding: utf-8 -*-
"""
Created on 2016年6月7日

@author: luoguanggui
"""
import freetime.util.log as ftlog
from freetime.core.timer import FTTimer
from freetime.entity.msg import MsgPack
from poker.entity.configure import gdata
from poker.entity.game.rooms.relaxation_match_ctrl.config import MatchConfig
from poker.entity.game.rooms.relaxation_match_ctrl.exceptions import MatchException
from poker.entity.game.rooms.relaxation_match_ctrl.models import Player
from poker.entity.game.rooms.room import TYRoom
from poker.protocol import router
from poker.entity.dao import userdata
from poker.entity.game.rooms.relaxation_match_ctrl.match import MatchRelaxation

class TYRelaxationMatchRoom(TYRoom, ):

    def __init__(self, roomdefine):
        pass

    def initMatch(self):
        pass

    def doEnter(self, userId):
        pass

    def doLeave(self, userId, msg):
        pass

    def doGetDescription(self, userId):
        pass

    def _getMatchStatas(self, userId):
        pass

    def doUpdateInfo(self, userId):
        pass

    def doWinlose(self, msg):
        pass

    def doQuickStart(self, msg):
        pass

    def _getMatchRanksQuick(self, userId):
        pass