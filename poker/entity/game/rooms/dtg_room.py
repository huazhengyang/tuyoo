# -*- coding: utf-8 -*-
"""

"""
from freetime.core import lock
__author__ = ['"Zhouhao" <zhouhao@tuyoogame.com>']
import random
import json
import sys
import time
from collections import OrderedDict
import freetime.util.log as ftlog
from freetime.util.log import getMethodName, catchedmethod
from freetime.entity.msg import MsgPack
from freetime.core.timer import FTTimer
from freetime.core.lock import FTLock, locked
from poker.entity.dao import sessiondata, onlinedata, userchip, gamedata
from poker.util import strutil
from poker.entity.game.tables.table_player import TYPlayer
from poker.entity.configure import gdata
from poker.entity.game.rooms.player_room_dao import PlayerRoomDao
from poker.protocol import router
from poker.entity.game.rooms.room import TYRoom
from poker.entity.game.plugin import TYPluginCenter, TYPluginUtils

class TYDTGQueueScheduler(object, ):
    """

    """
    STATE_IDLE = 0
    STATE_LOOP = 1
    QUEUE_STATE_STRS = {STATE_IDLE: 'STATE_IDLE', STATE_LOOP: 'STATE_LOOP'}

    def getStateStr(self):
        pass

    def __init__(self, room):
        pass

    def baseLogStr(self, tableId=None, userId=None):
        pass

    def _initIdleTableIds(self):
        pass

    def enter(self, userId):
        """

        """
        pass

    def leave(self, userId):
        """

        """
        pass

    def startLoop(self):
        pass

    def cancelLoop(self):
        pass

    def _tryStartNewTable(self, playerIds):
        pass

    def _startTable(self, tableId, playerIds, cardLevel):
        pass

    @catchedmethod
    def _recycleTable(self, tableId):
        pass

    def adjustTablePlayers(self, msg):
        """

        """
        pass

    def notifyRobot(self, robotN=1):
        pass

    def doHeartBeat(self):
        pass

    @catchedmethod
    def doLoop(self):
        pass

    def matchTeamMate(self, userId, strictLevel=0):
        """
           锁住队列, 避免并发操作时数据冲突
        """
        pass

    def findTeamMateWithStrictLevel(self, userId, strictLevel):
        pass

    def findOpponent(self, userId, maxCardLevel, strictLevel=0):
        """

        """
        pass

class TYDTGRoom(TYRoom, ):
    """

    Attributes:
        scheduler: 队列调度器
        _roomUsers: 进入房间的玩家集合
    """

    def __init__(self, roomDefine):
        pass

    def _baseLogStr(self, des='', userId=None):
        pass

    def _initScheduler(self):
        pass

    def _tableType(self):
        pass

    def _tableTheme(self):
        pass

    def checkSitCondition(self, userId):
        """

        """
        pass

    def _enter(self, userId):
        pass

    def _leave(self, userId, reason, needSendRes):
        pass

    def _onLeaveQueueOk(self, userId):
        pass

    def doQuickStart(self, msg):
        pass

    def _onQuickStartOk(self, userId):
        pass

    def doAdjustTablePlayers(self, msg):
        pass

    def doReturnQueue(self, userId):
        """

        """
        pass