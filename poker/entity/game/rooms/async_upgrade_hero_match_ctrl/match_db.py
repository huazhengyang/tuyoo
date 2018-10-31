# -*- coding: utf-8 -*-
"""
Created on 2017年10月13日

比赛统计上报

@author: zhaol

"""
from poker.entity.dao import gamedata
from freetime.util import log as ftlog
from poker.util import timestamp as pktimestamp
import json
from poker.entity.game.rooms.async_upgrade_hero_match_ctrl.match_player import AsyncUpgradeHeroMatchPlayer

class AsyncUpgradeHeroMatchDataBase(object, ):

    def __init__(self):
        pass

    @classmethod
    def getDBKey(cls, roomId):
        pass

    @classmethod
    def resetGameData(cls, player, gameId, roomId):
        """
        保存记录
        """
        pass

    @classmethod
    def saveData(cls, player, gameId, roomId):
        """
        保存记录
        """
        pass

    @classmethod
    def loadData(cls, userId, gameId, roomId, indexes):
        """
        读取记录
        """
        pass
if (__name__ == '__main__'):
    pass