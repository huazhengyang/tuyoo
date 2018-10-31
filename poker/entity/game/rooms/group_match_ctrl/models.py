# -*- coding: utf-8 -*-
"""
Created on 2016年1月15日

@author: zhaojiangang
"""
from poker.entity.game.rooms.group_match_ctrl.const import WaitReason
from poker.entity.game.rooms.group_match_ctrl.utils import Logger

class Signer(object, ):
    """
    报名用户
    """

    def __init__(self, userId, instId, signinTime):
        pass

class Riser(object, ):
    """
    晋级用户
    """

    def __init__(self, userId, score, rank, tableRank):
        pass

    @classmethod
    def fromPlayer(cls, player):
        pass

class Player(Signer, ):
    """
    比赛中的用户
    """
    STATE_IDLE = 0
    STATE_PLAYING = 1
    STATE_WINLOSE = 2
    STATE_WAIT = 3
    STATE_OUT = 4
    WHEN_OUT_NORMAL = 0
    WHEN_OUT_ASS = 1

    def __init__(self, userId, instId, signinTime):
        pass

    @property
    def state(self):
        pass

    @property
    def table(self):
        pass

    @property
    def seat(self):
        pass

    @property
    def group(self):
        pass

    def updateByRiser(self, riser):
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

    def __init__(self, gameId, roomId, tableId, seatCount):
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

    def getPlayingPlayerCount(self):
        """
        获取PLAYING状态的玩家数量
        """
        pass

    def getPlayingPlayerList(self):
        pass

    def getPlayerList(self):
        """
        获取本桌的所有player
        """
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

    def getTableCountPerRoom(self):
        pass

    def addTables(self, roomId, baseId, count):
        pass

    def borrowTables(self, count):
        pass

    def returnTables(self, tables):
        pass

    def findTable(self, roomId, tableId):
        pass