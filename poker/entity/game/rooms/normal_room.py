# -*- coding: utf-8 -*-
"""

"""
from poker.entity.game.game import TYGame
__author__ = ['"Zhouhao" <zhouhao@tuyoogame.com>', 'Zqh']
from random import choice
from freetime.core.tasklet import FTTasklet
import freetime.util.log as ftlog
from freetime.util.log import getMethodName
from poker.entity.configure import gdata
from poker.entity.game.rooms.room import TYRoom
from poker.entity.dao import daobase
from poker.entity.dao.lua_scripts import room_scripts
from poker.util import strutil

class TYNormalRoom(TYRoom, ):
    """

    """

    def __init__(self, roomDefine):
        pass

    def getTableScoresKey(self, shadowRoomId):
        pass

    def doReloadConf(self, roomDefine):
        """

        """
        pass

    def dispatchShadowRoomsForClient(self, clientVer):
        pass

    def getShadowRoomIdx(self, roomDefine, clientId, showHuafei):
        pass

    def doQuickStart(self, msg):
        """
        Note:
            1> 由于不同游戏评分机制不同，例如德州会根据游戏阶段评分，所以把桌子评分存到redis里，方便各游戏服务器自由刷新。
            2> 为了防止同一张桌子同时被选出来分配座位，选桌时会把tableScore里选出的桌子删除，玩家坐下成功后再添加回去，添回去之前无需刷新该桌子的评分。 
            3> 玩家自选桌时，可能选中一张正在分配座位的桌子，此时需要休眠后重试，只到该桌子完成分配或者等待超时。
        """
        pass

    def getBestTableId(self, userId, shadowRoomId, exceptTableId=None):
        """
        Return:
            None: tableScores 队列为空， 所有桌子都在分配座位中
        """
        pass

    def enterOneTable(self, userId, shadowRoomId, tableId):
        """
        Returns
            False: 重试超过次数
        """
        pass

    def _updateTableScore(self, shadowRoomId, tableScore, tableId, force=False):
        pass

    def updateTableScore(self, tableScore, tableId, force=False):
        """
        Args:
            force:
                True  强制往redis里添加或更新评分，只有玩家sit时做此操作
                False 表示只有redis有该牌桌评分时，才可以更新
        """
        pass