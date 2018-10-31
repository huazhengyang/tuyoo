# -*- coding: utf-8 -*-
"""
Created on 2017年10月13日

游戏记录

@author: zhaol

"""
from freetime.util import log as ftlog
from poker.entity.dao import gamedata
import json
import poker.util.timestamp as pktimestamp

class AsyncCommonArenaRecords(object, ):
    """
    快速赛比赛阶段s
    """
    RECORDS_COUNT = 10

    def __init__(self):
        pass

    @property
    def winnerCount(self):
        pass

    def setWinnerCount(self, count):
        pass

    @property
    def bestRank(self):
        pass

    def setBestRank(self, rank):
        pass

    @property
    def matchCount(self):
        pass

    def setMatchCount(self, count):
        pass

    @property
    def history(self):
        pass

    def setHistory(self, his):
        pass

    def initRecord(self, userId, gameId, matchId):
        """
        初始化记录
        """
        pass

    def getRedisID(self, matchId):
        """
        获取redis存储的key
        """
        pass

    def addMatchRecord(self, userId, gameId, matchId, rank, reward):
        """
        添加一个比赛记录
        """
        pass

    def getObject(self):
        """
        获取节点
        """
        pass
if (__name__ == '__main__'):
    pass