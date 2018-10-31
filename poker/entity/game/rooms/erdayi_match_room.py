# -*- coding: utf-8 -*-
"""
Created on 2016年1月15日

@author: zhaojiangang
"""
import functools
import random
from freetime.core.timer import FTTimer
from freetime.entity.msg import MsgPack
from poker.entity.configure import gdata
from poker.entity.dao import onlinedata
from poker.entity.game.rooms.erdayi_match_ctrl.config import MatchConfig
from poker.entity.game.rooms.erdayi_match_ctrl.exceptions import MatchException
from poker.entity.game.rooms.erdayi_match_ctrl.models import TableManager, Table
from poker.entity.game.rooms.erdayi_match_ctrl.utils import Logger
from poker.entity.game.rooms.room import TYRoom
from poker.entity.game.tables.table_player import TYPlayer
from poker.protocol import router

class ErdayiTable(Table, ):

    def __init__(self, gameId, roomId, tableId, seatCount):
        pass

class TYErdayiMatchRoom(TYRoom, ):

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

    def _getUserMatchSigns(self, uid, signs):
        pass

    def doSignin(self, userId, signinParams, feeIndex=0):
        pass

    def doSignout(self, userId):
        pass

    def doGiveup(self, userId):
        pass

    def doWinlose(self, msg):
        pass

    def doQuickStart(self, msg):
        pass

    def _getMatchRanksQuick(self, userId):
        pass

    def _notifyRobotSigninMatch(self, signer):
        pass