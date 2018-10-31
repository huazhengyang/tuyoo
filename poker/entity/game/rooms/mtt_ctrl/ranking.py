# -*- coding: utf-8 -*-
"""

"""
from freetime.util.log import catchedmethod
from itertools import izip
from poker.entity.game.rooms.player_room_dao import PlayerRoomDao
from poker.util import strutil
__author__ = ['Zhou Hao', 'Wang Tao']
import time
from freetime.util import log as ftlog
from poker.entity.game.plugin import TYPluginCenter, TYPluginUtils
from poker.entity.dao import sessiondata, userdata, gamedata
from poker.entity.dao import daobase

def pairwise(iterable):
    """

    """
    pass

class Ranking(object, ):
    """

    """
    BUILD_RANKING_INTERVAL = 10
    SEND_RANKING_INTERVAL = 3

    def __init__(self, room, starttimestamp):
        pass

    def getUData(self, userId):
        pass

    def setUData(self, userId, name, purl, photo):
        pass

    def setHunterInfo(self, userId, rankItem):
        pass

    def __buildRankData(self):
        pass

    @catchedmethod
    def sendToUser(self, userId):
        pass

    @catchedmethod
    def sendToAll(self):
        pass

    @catchedmethod
    def _sendToAll(self):
        pass

    def beforeMatchStart(self):
        pass

    def afterMatchStart(self):
        pass