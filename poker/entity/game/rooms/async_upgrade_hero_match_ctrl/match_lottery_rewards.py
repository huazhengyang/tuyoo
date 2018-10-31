# -*- coding: utf-8 -*-
"""
Created on 2017年10月13日

快速赛的比赛具体奖励
@author: zhaol

"""
from freetime.util import log as ftlog
from poker.entity.dao import daobase
import poker.util.timestamp as pktimestamp
from datetime import timedelta
import copy

class MillionLotteryRewardOpenModule(object, ):
    """
    一期奖池
    """
    GROUP_COUNT = 1000

    def __init__(self):
        pass

    @property
    def dateStr(self):
        pass

    def setDateStr(self, dateStr):
        pass

    @property
    def roomId(self):
        pass

    def setRoomId(self, roomId):
        pass

    def initConfig(self, config):
        """
        解析奖池配置
        """
        pass

    def getCurLotteryTime(self):
        """
        获取当前奖池时间
        """
        pass

    def initTotalWeight(self):
        """
        初始化开奖weight
        """
        pass

    def printLotteryInfo(self):
        """
        打印奖池信息
        """
        pass

    @property
    def matchId(self):
        pass

    def setMatchId(self, matchId):
        pass

    @property
    def desc(self):
        pass

    def setDesc(self, desc):
        pass

    @property
    def maxUnitReward(self):
        pass

    def setMaxUnitReward(self, reward):
        pass

    @property
    def maxUnitRewardCopy(self):
        pass

    @property
    def leastWinnerCount(self):
        pass

    def setLeastWinnerCount(self, count):
        pass

    @property
    def lotteryTime(self):
        pass

    def setLotteryTime(self, time):
        pass

    @property
    def initedFakeWinnerCount(self):
        pass

    def setInitedFakeWinnerCount(self, count):
        pass

    @property
    def totalWeight(self):
        pass

    def setTotalWeight(self, weight):
        pass

    @property
    def mainKey(self):
        pass

    def setMainKey(self, mainKey):
        pass

    def calcLeftSeconds(self):
        """
        计算到开局的剩余秒数，用于倒计时
        """
        pass

    def getLotteryInfo(self):
        """
        获取奖池信息
        """
        pass

    def update_winner_count(self):
        """
        刷新晋级人数
        """
        pass

    def calcWeight(self):
        """
        计算过奖人数权重
        """
        pass

    def calcRewards(self):
        """
        计算奖励
        """
        pass

    def getFakeWinnerCount(self):
        """
        获取假的晋级人数
        """
        pass

    def getTotalWinnerCount(self):
        """
        获取当前比赛实例的中奖人数
        """
        pass

    def getCurInsWinnerCount(self):
        """
        获取当前比赛实例的中奖人数
        """
        pass

    def addWinner(self, userId):
        """
        添加一个赢家
        """
        pass

    def addWinnerCount(self):
        """
        赢家存储增加
        """
        pass

    def initWinnerStorage(self):
        """
        初始化赢家存储
        """
        pass

    def getCurInsWinnerLinksKey(self, count):
        """
        获取当前存放赢家的KEY
        """
        pass

    def getTotalWinnerCountKey(self):
        """
        获取比赛赢家的总数
        """
        pass

    def getCurRoomWinnerCountKey(self):
        """
        获取当前比赛实例赢家的总数 地址存放KEY
        """
        pass

    def getFakeWinnerCountKey(self):
        """
        获取经过调整的赢家总数，用于控制奖励
        """
        pass

    def openLottery(self):
        """
        开奖
        """
        pass

    def isLotteryOpen(self):
        """
        是否开奖
        """
        pass

    def getMixMainKey(self):
        """
        获取mix主键
        """
        pass

    def getCurLotteryDateStr(self):
        """
        获取当前奖池日期
        """
        pass

class AsyncUpgradeHeroMatchLotteryRecords(object, ):
    """
    奖池奖励
    """

    def __init__(self):
        pass

    @property
    def curLottery(self):
        pass

    def setCurLottery(self, lottery):
        pass

    @property
    def lotteries(self):
        pass

    def setLotteries(self, lotteries):
        pass

    def initConfig(self, nodes, roomId):
        """
        根据配置初始化
        """
        pass

    def isLotteryOpen(self):
        """
        是否开奖
        """
        pass

    def openLottery(self):
        """
        开奖
        选择下一期奖励
        """
        pass

    def calcCurLottery(self):
        """
        获取当前的奖池
        """
        pass
if (__name__ == '__main__'):
    config = [{'matchId': 67891, 'desc': '12\xe7\x82\xb9\xe5\xbc\x80\xe5\xa5\x96\xef\xbc\x8c\xe9\x97\xaf\xe5\x85\xb3\xe6\x88\x90\xe5\x8a\x9f\xe5\xb9\xb3\xe5\x88\x8610\xe4\xb8\x87\xe5\x85\x83\xe5\xa5\x96\xe9\x87\x91', 'maxUnitReward': [{'count': 123, 'itemId': 'user:coupon'}], 'leastWinnerCount': 81300, 'lotteryTime': '12:00'}, {'matchId': 67892, 'desc': '21\xe7\x82\xb9\xe5\xbc\x80\xe5\xa5\x96\xef\xbc\x8c\xe9\x97\xaf\xe5\x85\xb3\xe6\x88\x90\xe5\x8a\x9f\xe5\xb9\xb3\xe5\x88\x8620\xe4\xb8\x87\xe5\x85\x83', 'maxUnitReward': [{'count': 134, 'itemId': 'user:coupon'}], 'leastWinnerCount': 149253, 'lotteryTime': '21:00'}]
    rewards = AsyncUpgradeHeroMatchLotteryRecords()
    rewards.initConfig(config)