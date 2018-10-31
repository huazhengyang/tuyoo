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
from poker.protocol import router
from poker.entity.configure import gdata, configure
from poker.entity.dao import userchip
from poker.entity.game.rooms.normal_room import TYNormalRoom
from poker.entity.game.rooms.player_room_dao import PlayerRoomDao
from poker.entity.game.rooms.room import TYRoom
from poker.entity.dao import sessiondata
from poker.entity.game.plugin import TYPluginUtils, TYPluginCenter
from poker.entity.game.rooms.vip_room import TYVipRoom

def doGetVipTableList(self, userId, clientId):
    """

    """
    pass
TYVipRoom.doGetVipTableList = doGetVipTableList