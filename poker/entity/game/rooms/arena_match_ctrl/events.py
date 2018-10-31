# -*- coding: utf-8 -*-
"""
Created on 2017年11月17日

@author: wangyonghui
"""
from poker.entity.events.tyevent import TYEvent

class MatchingEvent(TYEvent, ):

    def __init__(self, gameId, matchId, instId):
        pass

class MatchingReviveEvent(MatchingEvent, ):

    def __init__(self, gameId, matchId, instId, userId, success):
        pass