# -*- coding: utf-8 -*-
"""
Created on 2014年9月17日

@author: zjgzzz@126.com
"""

class MatchType(object, ):
    USER_COUNT = 1
    TIMING = 2
    VALID_TYPES = (USER_COUNT, TIMING)

    @classmethod
    def isValid(cls, value):
        pass

class FeesType(object, ):
    TYPE_NO_RETURN = 0
    TYPE_RETURN = 1
    VALID_TYPES = (TYPE_NO_RETURN, TYPE_RETURN)

    @classmethod
    def isValid(cls, value):
        pass

class ScoreCalcType(object, ):
    PING_FANG_GEN = 1
    BAI_FEN_BI = 2
    KAI_FANG_FANG_DA = 3

class GroupingType(object, ):
    TYPE_NO_GROUP = 0
    TYPE_GROUP_COUNT = 1
    TYPE_USER_COUNT = 2
    VALID_TYPES = (TYPE_NO_GROUP, TYPE_GROUP_COUNT, TYPE_USER_COUNT)

    @classmethod
    def isValid(cls, value):
        pass

class MatchFinishReason(object, ):
    FINISH = 0
    USER_WIN = 1
    USER_LOSER = 2
    USER_NOT_ENOUGH = 3
    RESOURCE_NOT_ENOUGH = 4
    USER_LEAVE = 5
    OVERTIME = 7

    @classmethod
    def toString(cls, reason):
        pass

class StageType(object, ):
    ASS = 1
    DIEOUT = 2
    VALID_TYPES = (ASS, DIEOUT)

    @classmethod
    def isValid(cls, value):
        pass
MAX_CARD_COUNT = 100

class SeatQueuingType(object, ):
    RANDOM = 1
    SNAKE = 2
    SEED = 3
    SIGNIN_TIME = 4
    VALID_TYPES = (RANDOM, SNAKE, SEED, SIGNIN_TIME)

    @classmethod
    def isValid(cls, value):
        pass

class AnimationType(object, ):
    UNKNOWN = (-1)
    HAIXUAN = 0
    COUNT = 1
    FINALS = 2
    VS = 3
    ASSIGN_TABLE = 4
    VALID_TYPES = (UNKNOWN, HAIXUAN, COUNT, FINALS, VS, ASSIGN_TABLE)

    @classmethod
    def isValid(cls, value):
        pass

class WaitReason(object, ):
    UNKNOWN = 0
    WAIT = 1
    BYE = 2
    RISE = 3

class WaitCallReason(object, ):
    INIT_STAGE = 1
    WINLOSE = 2
    RISE = 3