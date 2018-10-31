# -*- coding: utf-8 -*-
"""
Created on 2017年10月13日

比赛统计上报

@author: zhaol

"""
from poker.entity.dao import userchip, sessiondata
from poker.entity.biz import bireport
from freetime.util import log as ftlog

class CommonArenaReport(object, ):

    def __init__(self):
        pass

    @classmethod
    def reportMatchEvent(cls, eventId, userId, gameId, matchId, tableId, roundId, score, details=[]):
        pass
if (__name__ == '__main__'):
    pass