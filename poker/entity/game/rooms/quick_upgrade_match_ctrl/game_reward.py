# -*- coding: utf-8 -*-
"""
Created on 2017年10月13日

快速赛的比赛具体奖励
@author: zhaol

"""
from freetime.util import log as ftlog

class QUMReward(object, ):
    """
    快速赛的比赛奖励
    """

    def __init__(self):
        pass

    @property
    def desc(self):
        """
        奖励描述
        """
        pass

    def setDesc(self, desc):
        pass

    @property
    def startRank(self):
        """
        当前奖励的起始名次
        """
        pass

    def setStartRank(self, rank):
        pass

    @property
    def endRank(self):
        """
        当前奖励的终止名次
        """
        pass

    def setEndRank(self, rank):
        pass

    @property
    def rewards(self):
        """
        奖励
        """
        pass

    def setRewards(self, rewards):
        pass

    def isFited(self, rank):
        """
        是否符合当前奖励
        """
        pass

    def initConfig(self, config):
        """
        根据配置初始化
        """
        pass

    def getDesc(self):
        """
        获取奖励描述
        """
        pass