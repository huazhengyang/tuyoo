# -*- coding: utf-8 -*-
"""
Created on 2017年10月13日

快速赛的比赛奖励
@author: zhaol

"""
from freetime.util import log as ftlog
from poker.entity.game.rooms.common_arena_match_ctrl.ca_game_reward import CommonArenaReward

class CommonArenaRewards(object, ):
    """
    快速赛的比赛奖励
    """

    def __init__(self):
        pass

    @property
    def rewards(self):
        """
        奖励集合
        """
        pass

    def setRewards(self, rewards):
        """
        设置奖励集合
        """
        pass

    def getRewards(self, rank):
        """
        根据排名获取奖励
        """
        pass

    def initConfig(self, config):
        """
        根据配置初始化
        """
        pass

    def printRewards(self):
        """
        打印奖励信息
        """
        pass

    def getDesc(self):
        """
        获取奖励描述
        """
        pass