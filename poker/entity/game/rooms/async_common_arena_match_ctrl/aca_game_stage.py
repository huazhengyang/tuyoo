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
from poker.entity.game.rooms.async_common_arena_match_ctrl.aca_stage_back_fee import AAMatchStageBackFee

class AsyncCommonArenaStage(object, ):
    """
    快速赛比赛阶段
    """

    def __init__(self):
        pass

    @property
    def canBack(self):
        pass

    def setCanBack(self, canBack):
        pass

    @property
    def backFee(self):
        pass

    def setBackFee(self, backFee):
        pass

    @property
    def initRiseScore(self):
        pass

    def setInitRiseScore(self, score):
        pass

    @property
    def scores(self):
        pass

    def setScores(self, scores):
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
    def looses(self):
        pass

    def setLooses(self, looses):
        pass

    def getWorstRank(self):
        """
        获取本阶段的最差名次
        """
        pass

    def getMiddleRank(self):
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

    def isLevelUp(self, rank):
        """
        是否晋级
        """
        pass

    def winLoose(self, userId, score):
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

    def getRank(self, score):
        """
        获取排名
        """
        pass

    def _getRank(self, score):
        """
        获取排名
        自学习
        """
        pass

    def getMiddleRankScore(self):
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
    pass