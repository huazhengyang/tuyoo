# -*- coding: utf-8 -*-
"""

"""
from datetime import datetime
__author__ = ['"Zhouhao" <zhouhao@tuyoogame.com>']
import random
import json
import sys
import time
import copy
from collections import OrderedDict
import freetime.util.log as ftlog
from freetime.util.log import getMethodName, catchedmethod
from freetime.entity.msg import MsgPack
from freetime.core.timer import FTTimer
from freetime.core.lock import FTLock, locked
from poker.entity.game.game import TYGame
from poker.entity.dao import sessiondata, onlinedata, userchip, gamedata, daobase
from poker.util import tools
from poker.entity.game.tables.table_player import TYPlayer
from poker.entity.configure import gdata
from poker.entity.game.rooms.player_room_dao import PlayerRoomDao
from poker.protocol import router
from poker.entity.game.rooms.room import TYRoom
from poker.entity.game.plugin import TYPluginCenter, TYPluginUtils
from poker.entity.game import plugin
from poker.entity.game.rooms.match_mixin import TYMatchMixin

class TYScoreMatchQueueScheduler(object, ):
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

    def _isValidUser(self, userId):
        pass

    def _popOneUser(self):
        """

        """
        pass

    def _tryStartNewTable(self, playersN=0):
        pass

    def table_start_log(self, users_copy, table_users):
        """
        牌桌开始时,打印玩家匹配时间详细日志
        @param users_copy:
        @param table_users:
        @return:
        """
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

    def doLoop(self):
        pass

    def shuffleQueue(self):
        pass

class TYScoreMatchRoom(TYRoom, TYMatchMixin, ):
    """

    Attributes:
        scheduler: 队列调度器
        _roomUsers: 进入房间的玩家集合
    """

    def __init__(self, roomDefine):
        pass

    def doReloadConf(self, roomDefine):
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

    def checkMatchEnd(self):
        pass

    def _isSigninTime(self):
        pass

    def _resetVar(self):
        """

        """
        pass

    def match_ready_init(self):
        """

        """
        pass

    def doHeartBeat(self):
        """

        """
        pass