# -*- coding: utf-8 -*-
"""
Created on 2017年10月13日

快速赛的比赛具体奖励
@author: zhaol

"""
from freetime.util import log as ftlog
from poker.entity.dao import userdata, daobase
import time
import random
from poker.util import strutil

class AsyncUpgradeHeroMatchWinnerRecords(object, ):
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
    def rewards(self):
        """
        获取奖励
        """
        pass

    @property
    def newUserRewards(self):
        """
        新玩家奖励
        """
        pass

    @property
    def oldUserRewards(self):
        """
        老玩家奖励
        """
        pass

    def setRewards(self, rewards):
        pass

    def setNewUserRewards(self, rewards):
        pass

    def setOldUserRewards(self, rewards):
        pass

    def getRewards(self, userId):
        """
        获取奖励
        :param userId:
        """
        pass

    def _setServerDailyData(self, key, value):
        """
        设置服务器每日数据
        :param key:
        :param value:
        """
        pass

    def _getServerDailyData(self, key, default=None):
        """
        获取服务器每日数据
        :param key:
        :param default:
        """
        pass

    def _getRewards(self, userId, isNewUser):
        pass

    def initConfig(self, config):
        """
        根据配置初始化
        """
        pass
if (__name__ == '__main__'):
    config = {'desc': '\xe5\xa4\x8d\xe6\xb4\xbb\xe8\xb5\x9b\xe9\x97\xa8\xe7\xa5\xa81\xe5\xbc\xa0+60\xe4\xb8\x87\xe9\x87\x91\xe5\xb8\x81+5000\xe5\xa5\x96\xe5\x88\xb8', 'rewards': [{'count': 1, 'itemId': 'item:3103'}, {'count': 600000, 'itemId': 'user:chip'}, {'count': 5000, 'itemId': 'user:coupon'}]}
    rewards = AsyncUpgradeHeroMatchWinnerRecords()
    rewards.initConfig(config)