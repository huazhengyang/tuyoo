# -*- coding: utf-8 -*-
"""

"""
import functools
from freetime.core.timer import FTTimer
__author__ = ['"Zhouhao" <zhouhao@tuyoogame.com>']
import time
from datetime import datetime
import freetime.util.log as ftlog
from poker.entity.configure import gdata
from poker.entity.game.rooms.room import TYRoom
from poker.entity.game.rooms.vip_room import TYVipRoom
from poker.entity.game.plugin import TYPluginUtils
from poker.entity.dao import daobase

class TYLtsRoom(TYVipRoom, ):
    """
    
    Attributes:
    """

    def __init__(self, roomdefine):
        pass

    def doReloadConf(self, roomDefine):
        pass

    def __initMatch(self):
        pass

    def checkSitCondition(self, userId):
        pass

    def doGetDescription(self, userId):
        pass

    def doGetRankList(self, userId, msg):
        pass

    def incrMatchScore(self, userId, score):
        """
        Note: 比赛时间结束后，还会有牌桌未完结，这些牌桌完结后也需要记录成绩。
        """
        pass

    def doAdjustTablePlayers(self, table):
        pass

    def _checkMatchEnd(self):
        pass

    def doMatchEnd(self):
        pass