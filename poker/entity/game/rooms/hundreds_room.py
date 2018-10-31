# -*- coding: utf-8 -*-
"""

"""
__author__ = ['"Zhouhao" <zhouhao@tuyoogame.com>']
import math
from random import choice
from freetime.util import log as ftlog
from freetime.entity.msg import MsgPack
from freetime.util.log import catchedmethod, getMethodName
from freetime.core.lock import locked
from freetime.core.tasklet import FTTasklet
from poker.protocol import router
from poker.entity.configure import gdata, configure
from poker.entity.dao import userchip, onlinedata
from poker.entity.game.rooms.normal_room import TYNormalRoom
from poker.entity.game.rooms.player_room_dao import PlayerRoomDao
from poker.entity.game.rooms.room import TYRoom
from poker.entity.dao import sessiondata
from poker.entity.game.plugin import TYPluginUtils, TYPluginCenter

class TYHundredsRoom(TYNormalRoom, ):
    """

    """

    def __init__(self, roomdefine):
        pass

    def initData(self):
        pass

    @catchedmethod
    @locked
    def doQuickStart(self, msg):
        """
        Note:
            1> 每个房间一张桌子
            2> 房间分为激活和非激活状态
            3> 选择激活房间中人数最少的
        """
        pass

    def _enter(self, userId):
        pass

    def _leave(self, userId, reason, needSendRes):
        pass