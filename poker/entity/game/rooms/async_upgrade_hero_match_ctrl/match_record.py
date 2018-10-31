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

class AsyncUpgradeHeroMatchRecords(object, ):
    """
    快速赛比赛阶段s
    """
    RECORDS_COUNT = 3

    def __init__(self):
        pass

    @property
    def weekInfo(self):
        pass

    def setWeekInfo(self, weekInfo):
        pass

    @property
    def yestodayMatchInfo(self):
        pass

    def setYesTodayMatchInfo(self, yestodayMatchInfo):
        pass

    @property
    def todayMatchInfo(self):
        pass

    def setTodayMatchInfo(self, todayMatchInfo):
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

    def initRecord(self, userId, gameId, matchId, curLotteryTime):
        """
        初始化记录
        """
        pass

    def getRedisID(self, matchId):
        """
        获取redis存储的key
        """
        pass

    def addMatchLotteryRecord(self, userId, gameId, matchId, curLotteryTime, rewardDesc, rewardDict):
        """
        添加一个比赛奖池分奖记录
        
        已开奖，奖励加到上一期之中
        """
        pass

    def initTodayMatchInfo(self, curLotteryTime):
        """
        初始化今日比赛信息
        """
        pass

    def saveMatchRecord(self, userId, gameId, matchId):
        """
        保存比赛记录
        """
        pass

    def addMatchSuccRecord(self, userId, gameId, matchId, curLotteryTime, rewardDesc, rewardDict):
        """
        添加一个比赛通关记录
        """
        pass

    def addMatchFailRecord(self, userId, gameId, matchId, curLotteryTime):
        """
        添加一个比赛闯关失败记录
        """
        pass

    def getObject(self):
        """
        获取节点
        """
        pass

    def mergeReward(self, rewards, rMerges):
        """
        合并奖励
        """
        pass
if (__name__ == '__main__'):
    pass