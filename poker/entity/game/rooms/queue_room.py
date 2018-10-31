# -*- coding: utf-8 -*-
"""

"""
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
from freetime.core.lock import FTLock
from poker.entity.dao import sessiondata, onlinedata, userchip
from poker.util import strutil
from poker.entity.game.tables.table_player import TYPlayer
from poker.entity.configure import gdata
from poker.entity.game.rooms.player_room_dao import PlayerRoomDao
from poker.protocol import router
from poker.entity.game.rooms.room import TYRoom
from poker.entity.game.plugin import TYPluginCenter, TYPluginUtils

class TYQueueScheduler(object, ):
    """
    
    Attributes:
        _state : 队列管理器状态， 
           STATE_IDLE 队列空闲状态，即关闭循环调度；
           STATE_LOOP 队列开启循环调度状态。
           STATE_START_TABLE 开桌转态，此时不允许玩家leave room，以免造成开局缺人问题。
        users/waitingUsers : 等待分桌的玩家队列, OrdinaryDict类型
        sittingUsers : 正在分桌的玩家集合，set类型
        activeTableIds : 使用的桌子，set类型
        idleTableIds : 空闲牌桌，list类型
    
    Configure：
        n_start :达到这个人数马上开新桌
        n_recycle : 少于这个人数拆桌
        wait_time : 超过这个时间还凑不齐n_start个玩家，但达到minTriggerLen人数，也会开新桌
        minTriggerLen : 参见wait_time
    """
    STATE_IDLE = 0
    STATE_LOOP = 1
    STATE_START_TABLE = 2
    QUEUE_STATE_STRS = {STATE_IDLE: 'STATE_IDLE', STATE_LOOP: 'STATE_LOOP', STATE_START_TABLE: 'STATE_START_TABLE'}

    def getStateStr(self):
        pass

    def __init__(self, room):
        pass

    def _initIdleTableIds(self):
        pass

    def startLoop(self):
        pass

    def cancelLoop(self):
        pass

    @property
    def n_start(self):
        pass

    @property
    def n_recycle(self):
        pass

    @property
    def wait_time(self):
        pass

    @property
    def minTriggerLen(self):
        pass

    def baseLogStr(self, tableId=None, userId=None):
        pass

    def enter(self, userId):
        """

        """
        pass

    def leave(self, userId):
        """

        """
        pass

    def adjustTablePlayers(self, msg):
        """

        """
        pass

    def notifyRobot(self, robotN=1):
        pass

    def doHeartBeat(self):
        pass

    def _startTable(self, tableId, playerN=0, recyclePlayersN=0):
        """
            recyclePlayersN表示需要从牌桌回收到队列的人数
        """
        pass

    def _recycleTable(self, tableId):
        pass

    def _tryStartNewTable(self, minPlayersN):
        pass

    def _isValidUser(self, userId):
        pass

    def _popOneUser(self):
        """

        """
        pass

class TYQueueRoom(TYRoom, ):
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

    def doRoomUpdateRankOfAll(self):
        pass

    def doGetDescription(self, userId):
        pass

    def doGetMatchStatus(self, userId):
        pass