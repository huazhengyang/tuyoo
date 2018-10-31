# -*- coding: utf-8 -*-
"""
Created on 2016年5月13日

@author: zhaojiangang
"""
from poker.entity.events.tyevent import TYEvent

class MatchStartSigninEvent(TYEvent, ):

    def __init__(self, gameId, instId):
        pass

class MatchCancelEvent(TYEvent, ):

    def __init__(self, gameId, instId, reason):
        pass

class MatchingEvent(TYEvent, ):

    def __init__(self, gameId, matchId, instId, matchingId):
        pass

class MatchingStartEvent(MatchingEvent, ):

    def __init__(self, gameId, matchId, instId, matchingId):
        pass

class MatchingStageStartEvent(MatchingEvent, ):

    def __init__(self, gameId, matchId, instId, matchingId, stageIndex):
        pass

class MatchingStageFinishEvent(MatchingEvent, ):

    def __init__(self, gameId, matchId, instId, matchingId, stageIndex):
        pass

class MatchingFinishEvent(MatchingEvent, ):

    def __init__(self, gameId, matchId, instId, matchingId):
        pass