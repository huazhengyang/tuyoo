# -*- coding: utf-8 -*-
"""
Created on 2016年6月7日

@author: luoguanggui
"""
import datetime
from sre_compile import isstring
from poker.entity.game.rooms.relaxation_match_ctrl.exceptions import ConfigException

class StartConfig(object, ):

    def __init__(self):
        pass

    def _checkTimeFormat(self):
        """
        检测timeStr是否属于12:22这样正常的时间格式
        """
        pass

    def checkValid(self):
        pass

    @classmethod
    def parse(cls, conf):
        pass

class RankRewards(object, ):

    def __init__(self):
        pass

    def checkValid(self):
        pass

    @classmethod
    def parse(cls, conf):
        pass

    @classmethod
    def buildRewardDescList(cls, rankRewardsList):
        pass

class MatchConfig(object, ):

    def __init__(self):
        pass

    def checkValid(self):
        pass

    @classmethod
    def getRankRewardsClass(cls):
        pass

    @classmethod
    def parse(cls, gameId, roomId, matchId, name, conf):
        pass