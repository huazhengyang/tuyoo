# -*- coding: utf-8 -*-
"""
Created on 2016年1月25日

@author: zhaojiangang
"""
import functools
import random
from freetime.core.lock import FTLock
from freetime.core.timer import FTTimer
import freetime.util.log as ftlog
from poker.entity.biz import bireport
from poker.entity.dao import sessiondata
from poker.entity.game.rooms.group_match_ctrl.const import ScoreCalcType, SeatQueuingType

class Lockable(object, ):

    def __init__(self):
        pass

class Logger(object, ):

    def __init__(self, kvs=None):
        pass

    def add(self, k, v):
        pass

    def info(self, prefix=None, *args):
        pass

    def hinfo(self, prefix=None, *args):
        pass

    def debug(self, prefix=None, *args):
        pass

    def warn(self, prefix=None, *args):
        pass

    def error(self, prefix=None, *args):
        pass

    def isDebug(self):
        pass

    def _log(self, prefix, func, *args):
        pass

class Heartbeat(object, ):
    ST_IDLE = 0
    ST_START = 1
    ST_STOP = 2

    def __init__(self, interval, target):
        pass

    def start(self):
        pass

    def stop(self):
        pass

    def _onTimer(self):
        pass

class HeartbeatAble(object, ):

    def __init__(self):
        pass

    def postCall(self, func, *args, **kwargs):
        pass

    def postTask(self, task):
        pass

    def _startHeartbeat(self):
        pass

    def _stopHeartbeat(self):
        pass

    def _doHeartbeat(self):
        pass

    def _processPostTaskList(self):
        pass

    def _doHeartbeatImpl(self):
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

def report_bi_game_event(eventId, userId, gameId, roomId, tableId, roundId, detalChip, state1, state2, cardlist, tag=''):
    pass