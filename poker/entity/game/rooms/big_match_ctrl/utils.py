# -*- coding: utf-8 -*-
"""
Created on 2014年9月22日

@author: zjgzzz@126.com
"""
import random
import time
from poker.entity.game.rooms.big_match_ctrl.const import ChipCalcType, SeatQueuingType
from freetime.util import log as ftlog

class Utils(object, ):
    currentTimestamp = None

    @classmethod
    def timestamp(cls):
        pass

class PlayerSort(object, ):

    @classmethod
    def cmpByChip(cls, p1, p2):
        pass

    @classmethod
    def cmpBySigninTime(cls, p1, p2):
        pass

    @classmethod
    def cmpByTableRanking(cls, p1, p2):
        pass

class PlayerChipCalcImpl(object, ):

    def calc(self, chip):
        pass

class PlayerChipCalcFixed(PlayerChipCalcImpl, ):

    def __init__(self, value):
        pass

    def calc(self, chip):
        pass

class PlayerChipCalcPingFangGen(PlayerChipCalcImpl, ):

    def calc(self, chip):
        pass

class PlayerChipCalcBaiFenBi(PlayerChipCalcImpl, ):

    def __init__(self, rate):
        pass

    def calc(self, chip):
        pass

class PlayerChipCalcKaiFangFangDa(PlayerChipCalcImpl, ):

    def __init__(self, base, middle):
        pass

    def calc(self, chip):
        pass

class PlayerChipCalc:
    __pingFangGenInstance = PlayerChipCalcPingFangGen()

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

class PlayerQueuingChip(PlayerQueuingImpl, ):

    def sort(self, matchUserList):
        pass

class PlayerQueuingSigninTime(PlayerQueuingImpl, ):

    def sort(self, matchUserList):
        pass

class PlayerQueuing(object, ):
    __defaultQueuing = PlayerQueuingRandom()
    __queuingMap = {SeatQueuingType.RANDOM: __defaultQueuing, SeatQueuingType.SNAKE: PlayerQueuingSnake(), SeatQueuingType.SEED: PlayerQueuingChip(), SeatQueuingType.SIGNIN_TIME: PlayerQueuingSigninTime()}

    @classmethod
    def sort(cls, queuingType, players):
        pass

class PlayerGrouping(object, ):

    @classmethod
    def groupingByGroupCount(cls, playerList, groupCount):
        pass

    @classmethod
    def groupingByMaxUserCountPerGroup(cls, playerList, userCount):
        pass

    @classmethod
    def groupingByFixedUserCountPerGroup(cls, playerList, userCount):
        pass