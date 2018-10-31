# -*- coding: utf-8 -*-
"""
Created on 2017年10月13日

快开赛的轮次/阶段对象
@author: zhaol

{
    "index": 1,
    "base_chip": 10,
    "cardCount": 1,
    "name": "128进64",
    "riseUserCount": 64,
    "scoreInit": 0,
    "scoreIntoRate": 1,
    "totalUserCount": 128
}

"""
import copy
from poker.entity.dao import daobase
import json
from freetime.util import log as ftlog

class QUMStage(object, ):
    """
    快速赛比赛阶段
    """

    def __init__(self):
        pass

    @property
    def maxSeat(self):
        pass

    def setTableMaxSeat(self, maxSeat):
        """
        设置每桌的人数
        """
        pass

    @property
    def matchId(self):
        pass

    def setMatchId(self, matchId):
        pass

    def initConfig(self, config):
        """
        根据配置初始化
        """
        pass

    @property
    def desc(self):
        """
        赛段描述
        """
        pass

    @property
    def index(self):
        """
        快速赛比赛阶段索引
        """
        pass

    def setIndex(self, index):
        """
        设置阶段索引
        """
        pass

    @property
    def defaultLearnLength(self):
        pass

    @property
    def wins(self):
        pass

    def setWins(self, wins):
        pass

    @property
    def looses(self):
        pass

    def setLooses(self, looses):
        pass

    @property
    def winRankStart(self):
        """
        本阶段晋级的起始名次
        """
        pass

    @property
    def winRankEnd(self):
        """
        本阶段晋级的中止名次
        """
        pass

    @property
    def looseRankStart(self):
        """
        本阶段失败的起始名次
        """
        pass

    @property
    def looseRankEnd(self):
        """
        本阶段失败的中止名次
        """
        pass

    @property
    def riseUserCountInTable(self):
        """
        每局晋级人数
        """
        pass

    def getWorstRank(self):
        """
        获取本阶段的最差名次
        """
        pass

    def getWorstLooseRank(self):
        """
        获取本阶段的最差名次
        """
        pass

    @property
    def baseChip(self):
        """
        当前阶段底注
        其他游戏根据底注去计算大小盲等信息
        """
        pass

    def setBaseChip(self, chip):
        """
        设置底注
        """
        pass

    @property
    def cardCount(self):
        """
        当前阶段局数
        """
        pass

    def setCardCount(self, count):
        """
        设置当前阶段局数
        """
        pass

    @property
    def name(self):
        """
        当前比赛阶段名称
        """
        pass

    def setName(self, name):
        """
        设置当前比赛阶段名称
        """
        pass

    @property
    def totalUserCount(self):
        """
        当前阶段的总用户数
        """
        pass

    def setTotalUserCount(self, count):
        """
        设置当前比赛阶段的总用户数
        """
        pass

    @property
    def riseUserCount(self):
        """
        当前阶段的晋级人数
        """
        pass

    @property
    def looseUserCount(self):
        """
        当前阶段的失败人数
        """
        pass

    def setRiseUserCount(self, count):
        """
        设置当前阶段的晋级人数
        """
        pass

    def setWinLooseCount(self, totalCount, riseCount):
        """
        设置本阶段的晋级人数，总人数
        """
        pass

    @property
    def initScore(self):
        """
        当前阶段的初始积分
        """
        pass

    def setInitScore(self, score):
        """
        设置当前阶段的初始积分
        """
        pass

    @property
    def scoreIntoRate(self):
        """
        由上一阶段来到当前阶段的带分比例
        """
        pass

    def setScoreIntoRate(self, rate):
        """
        设置由上一阶段到当前阶段的带分比例
        """
        pass

    def winLoose(self, userId, score, winLoose):
        """
        添加一个结算结果
        
        参数
        userId: 用户ID
        score: 用户积分
        winLoose: 晋级结果
            True 晋级
            Loose 淘汰
        """
        pass

    def getRank(self, score, winLoose, tableRank):
        """
        获取排名
        """
        pass

    def _getRank(self, score, sl, start, end, winLoose):
        """
        获取排名
        自学习
        """
        pass

    def saveRankScores(self):
        """
        将晋级分数记录保存在Redis中
        """
        pass

    def loadRankScores(self):
        """
        加载晋级分数记录
        """
        pass
if (__name__ == '__main__'):
    stage = QUMStage()
    stage.setTotalUserCount(128)
    stage.setRiseUserCount(64)
    score = 100
    rank = stage.winLoose(10001, score, True)
    print 'score:', score, ' rank:', rank
    score1 = 200
    rank1 = stage.winLoose(10002, score1, True)
    print 'score:', score1, ' rank:', rank1
    score2 = 150
    rank2 = stage.winLoose(10002, score2, True)
    print 'score:', score2, ' rank:', rank2
    score3 = 60
    rank3 = stage.winLoose(10002, score3, True)
    print 'score:', score3, ' rank:', rank3