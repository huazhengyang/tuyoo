# -*- coding: utf-8 -*-
"""
Created on 2016年6月7日

@author: luoguanggui
"""
from poker.entity.events.tyevent import TYEvent

class MatchStartEvent(TYEvent, ):

    def __init__(self, gameId, bigRoomId):
        pass

class MatchOverEvent(TYEvent, ):

    def __init__(self, gameId, bigRoomId):
        pass