# -*- coding: utf-8 -*-
"""
Created on 2015年3月11日

@author: zhaojiangang, zhouhao
"""
import json
from poker.entity.events.tyevent import MatchWinloseEvent
import freetime.util.log as ftlog
from poker.entity.dao import gamedata

class MatchRecord(object, ):

    class Record(object, ):

        def __init__(self, bestRank, crownCount, playCount):
            pass

        def update(self, rank):
            pass

        @classmethod
        def fromDict(cls, d):
            pass

        def toDict(self):
            pass

    @classmethod
    def initialize(cls, eventBus):
        pass

    @classmethod
    def onMatchWinlose(cls, event):
        pass

    @classmethod
    def loadRecord(cls, gameId, userId, matchId):
        pass

    @classmethod
    def saveRecord(cls, gameId, userId, matchId, record):
        pass

    @classmethod
    def __buildField(cls, matchId):
        pass