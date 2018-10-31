# -*- coding: utf-8 -*-
"""
Created on 2016年5月12日

@author: zhaojiangang
"""
import random
from poker.entity.game.rooms.erdayi_match_ctrl.const import SeatQueuingType, ScoreCalcType
from poker.entity.game.rooms.erdayi_match_ctrl.utils import Logger

class Signer(object, ):

    def __init__(self, userId, instId):
        pass

class Player(object, ):
    ST_SIGNIN = 1
    ST_WAIT = 2
    ST_PLAYING = 3
    ST_WINLOSE = 4
    ST_RISE = 5
    ST_OVER = 6

    def __init__(self, userId):
        pass

    @property
    def state(self):
        pass

    @property
    def group(self):
        pass

    @property
    def stage(self):
        pass

    @property
    def seat(self):
        pass

    @property
    def seatId(self):
        pass

    @property
    def table(self):
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

class PlayerSort(object, ):

    @classmethod
    def cmpByScore(cls, p1, p2):
        pass

    @classmethod
    def cmpBySigninTime(cls, p1, p2):
        pass

    @classmethod
    def cmpByTableRanking(cls, p1, p2):
        pass

class PlayerQueuingImpl(object, ):

    def sort(self, players):
        """

        """
        pass

class PlayerQueuingRandom(PlayerQueuingImpl, ):

    def sort(self, players):
        pass

class PlayerQueuingSnake(PlayerQueuingImpl, ):

    def sort(self, players):
        pass

class PlayerQueuingScore(PlayerQueuingImpl, ):

    def sort(self, matchUserList):
        pass

class PlayerQueuingSigninTime(PlayerQueuingImpl, ):

    def sort(self, matchUserList):
        pass

class PlayerQueuing(object, ):
    _defaultQueuing = PlayerQueuingRandom()
    _queuingMap = {SeatQueuingType.RANDOM: _defaultQueuing, SeatQueuingType.SNAKE: PlayerQueuingSnake(), SeatQueuingType.SEED: PlayerQueuingScore(), SeatQueuingType.SIGNIN_TIME: PlayerQueuingSigninTime()}

    @classmethod
    def sort(cls, queuingType, players):
        pass

class PlayerScoreCalcImpl(object, ):

    def calc(self, score):
        pass

class PlayerScoreCalcFixed(PlayerScoreCalcImpl, ):

    def __init__(self, value):
        pass

    def calc(self, score):
        pass

class PlayerScoreCalcPingFangGen(PlayerScoreCalcImpl, ):

    def calc(self, score):
        pass

class PlayerScoreCalcBaiFenBi(PlayerScoreCalcImpl, ):

    def __init__(self, rate):
        pass

    def calc(self, score):
        pass

class PlayerScoreCalcKaiFangFangDa(PlayerScoreCalcImpl, ):

    def __init__(self, base, middle):
        pass

    def calc(self, score):
        pass

class PlayerScoreCalc:
    _pingFangGenInstance = PlayerScoreCalcPingFangGen()

    @classmethod
    def makeCalc(cls, stageConf, playerList):
        pass

class PlayerGrouping(object, ):

    @classmethod
    def groupingByGroupCount(cls, playerList, groupCount, tableSeatCount):
        pass

    @classmethod
    def calcFixCount(cls, userCount, tableSeatCount):
        pass

    @classmethod
    def groupingByMaxUserCountPerGroup(cls, playerList, userCount, tableSeatCount):
        pass

    @classmethod
    def groupingByFixedUserCountPerGroup(cls, playerList, userCount):
        pass

class GroupNameGenerator(object, ):
    GROUP_NAME_PREFIX = [chr(i) for i in range(ord('A'), (ord('Z') + 1))]

    @classmethod
    def generateGroupName(cls, groupCount, i):
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

    def addTable(self, table):
        pass

    def addTables(self, roomId, baseId, count):
        pass

    def borrowTables(self, count):
        pass

    def returnTables(self, tables):
        pass

    def findTable(self, roomId, tableId):
        pass