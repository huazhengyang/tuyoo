# -*- coding: utf-8 -*-
"""

"""
__author__ = ['"Zhouhao" <zhouhao@tuyoogame.com>']
from random import choice, shuffle
import json
from freetime.core.tasklet import FTTasklet
import freetime.util.log as ftlog
from freetime.util.log import getMethodName
from poker.entity.configure import gdata
from poker.entity.game.rooms.room import TYRoom
from poker.entity.dao import daobase
from poker.entity.dao.lua_scripts import room_scripts
from poker.entity.game.game import TYGame

class TYCustomRoom(TYRoom, ):
    """

    """

    def __init__(self, roomDefine):
        pass

    def _initIdleTableIds(self):
        pass

    def getIdleTableId(self):
        pass

    def _recycleTable(self, idleTableId):
        pass

    def doAdjustTablePlayers(self, msg):
        pass

    def _leave(self, userId, reason, needSendRes):
        pass