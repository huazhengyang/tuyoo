# -*- coding: utf-8 -*-
"""

"""
__author__ = ['"Zhouhao" <zhouhao@tuyoogame.com>', 'WangTao']
import math
from random import choice
from freetime.util import log as ftlog
from freetime.entity.msg import MsgPack
from freetime.util.log import catchedmethod, getMethodName
from freetime.core.lock import locked
from freetime.core.tasklet import FTTasklet
from freetime.core.timer import FTTimer
from poker.util import strutil
from poker.protocol import router
from poker.entity.configure import gdata, configure
from poker.entity.dao import userchip
from poker.entity.game.rooms.normal_room import TYNormalRoom
from poker.entity.game.rooms.player_room_dao import PlayerRoomDao
from poker.entity.game.rooms.room import TYRoom
from poker.entity.dao import sessiondata
from poker.entity.game.plugin import TYPluginUtils, TYPluginCenter
from poker.entity.dao import daobase

class TYVipRoom(TYNormalRoom, ):
    """

    """
    VIP_ROOM_LIST_REVERSE_CHIPS = 10000000

    def __init__(self, roomdefine):
        pass

    @catchedmethod
    @locked
    def doQuickStart(self, msg):
        """
        Note:
            1> 由于不同游戏评分机制不同，例如德州会根据游戏阶段评分，所以把桌子评分存到redis里，方便各游戏服务器自由刷新。
            2> 为了防止同一张桌子同时被选出来分配座位，选桌时会把tableScore里选出的桌子删除，玩家坐下成功后再添加回去，添回去之前无需刷新该桌子的评分。 
            3> 玩家自选桌时，可能选中一张正在分配座位的桌子，此时需要休眠后重试，只到该桌子完成分配或者等待超时。
            4> 贵宾室为了凑桌，当一张桌子被取走需要等待返回，这样需要锁一下房间对象。
        """
        pass

    def _enter(self, userId):
        pass

    def _leave(self, userId, reason, needSendRes):
        pass

    def _initActiveTables(self):
        pass

    def sortedActiveTablesWithId(self):
        pass

    def sortedActiveTables(self):
        pass

    def isActiveTable(self, table):
        pass

    def hotTablesWithId(self, hotTablePlayersCount):
        pass

    def hotTables(self, hotTablePlayersCount):
        pass

    def checkAddTable(self, hotTablePlayersCount):
        """

        """
        pass

    @catchedmethod
    def checkHideTable(self, table, hotTablePlayersCount):
        """

        """
        pass

    def appendOneActiveTable(self):
        pass

    def getLastActiveTable(self):
        pass

    def isSecretRoom(self):
        pass

    def isAutoQueueRoom(self):
        pass

    def isLiveShowRoom(self):
        pass

    def doHeartBeat(self):
        """

        """
        pass

    def genVipTableList(self):
        """

        """
        pass

    def doGetVipTableList(self, userId, clientId):
        """

        """
        pass

    def doGetMasterTableList(self, userId, clientId):
        """

        """
        pass

    def doGetLiveShowTableList(self, userId, clientId):
        """

        """
        pass

    def _getVipTableList(self, userId, clientId, tag='', isMasterRoom=False, isLiveShowRoom=False):
        """

        """
        pass

    def doGetPlayingTableList(self):
        pass

    def doChooseRoom(self, userId, clientId):
        pass