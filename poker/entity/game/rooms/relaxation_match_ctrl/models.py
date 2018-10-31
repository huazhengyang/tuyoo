# -*- coding: utf-8 -*-
"""
Created on 2016年6月7日

@author: luoguanggui
"""
from poker.entity.game.rooms.relaxation_match_ctrl.utils import Logger
from poker.entity.game.rooms.relaxation_match_ctrl.const import TOP_N
from poker.entity.dao import sessiondata
from freetime.core.tasklet import FTTasklet
from poker.entity.dao import daobase
RELAXATION_MATCH_LOCK_KEY = 'relaxation_match_lock'

class Player(object, ):
    """
    玩家
    """

    def __init__(self, userId):
        pass

    @property
    def seat(self):
        pass

    @seat.setter
    def seat(self, seat):
        pass

    def fillUserInfo(self, userName, clientId):
        pass

class Seat(object, ):

    def __init__(self, table, seatId):
        pass

    @property
    def gameId(self):
        pass

    @property
    def table(self):
        pass

    @property
    def seatId(self):
        pass

    @property
    def roomId(self):
        pass

    @property
    def tableId(self):
        pass

    @property
    def location(self):
        pass

    @property
    def player(self):
        pass

class Table(object, ):

    def __init__(self, gameId, roomId, tableId, seatCount, matchId):
        pass

    @property
    def gameId(self):
        pass

    @property
    def roomId(self):
        pass

    @property
    def tableId(self):
        pass

    @property
    def seats(self):
        pass

    @property
    def group(self):
        pass

    @property
    def location(self):
        pass

    @property
    def seatCount(self):
        pass

    @property
    def idleSeatCount(self):
        """
        空闲座位的数量
        """
        pass

    def getPlayerCount(self):
        """
        获取该桌子上玩家数量
        """
        pass

    def getPlayerList(self):
        """
        获取本桌的所有player
        """
        pass

    def getAnotherPlayer(self, player):
        pass

    def getUserIdList(self):
        """
        获取本桌所有userId
        """
        pass

    def sitdown(self, player):
        """
        玩家坐下
        """
        pass

    def standup(self, player):
        """
        玩家离开桌子
        """
        pass

    def clear(self):
        """
        清理桌子上的所有玩家
        """
        pass

    def _clearSeat(self, seat):
        pass

    def _makeSeats(self, count):
        pass

class TableManager(object, ):

    def __init__(self, room, tableSeatCount):
        pass

    @property
    def tableSeatCount(self):
        pass

    @property
    def roomCount(self):
        pass

    @property
    def gameId(self):
        pass

    @property
    def allTableCount(self):
        pass

    @property
    def idleTableCount(self):
        pass

    @property
    def busyTableCount(self):
        pass

    @property
    def waitTableCount(self):
        pass

    @property
    def waitTableList(self):
        pass

    @property
    def busyTableList(self):
        pass

    def getTableCountPerRoom(self):
        pass

    def updateMatchTime(self, todayStartTime, todayEndTime, matchConf):
        pass

    def updateMatchRank(self, topRankPlayerList):
        pass

    def addTables(self, roomId, baseId, count, matchId):
        pass

    def _borrowOneTable(self):
        pass

    def getTableSitdown(self, player):
        pass

    def returnOneTable(self, table):
        pass

    def findTable(self, tableId):
        pass

    def standupFromTable(self, table, player):
        pass