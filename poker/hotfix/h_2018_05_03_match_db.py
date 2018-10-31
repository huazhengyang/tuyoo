# -*- coding: utf-8 -*-
"""
Created on 2017年10月26日

@author: zhaoliang
"""
from poker.entity.dao import gamedata
import json
from poker.util import timestamp as pktimestamp
from poker.entity.game.rooms.async_upgrade_hero_match_ctrl.match_player import AsyncUpgradeHeroMatchPlayer

@classmethod
def loadData(cls, userId, gameId, roomId, indexes):
    """
    读取记录
    """
    pass
from poker.entity.game.rooms.async_upgrade_hero_match_ctrl.match_db import AsyncUpgradeHeroMatchDataBase
AsyncUpgradeHeroMatchDataBase.loadData = loadData