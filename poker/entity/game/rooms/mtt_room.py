# -*- coding: utf-8 -*-
"""

"""
from freetime.core.timer import FTTimer
import time
from freetime.util.log import getMethodName
import functools
from poker.entity.dao import userdata, onlinedata
from poker.entity.game.rooms.player_room_dao import PlayerRoomDao
from poker.entity.dao import daobase
from poker.entity.biz import bireport
from poker.entity.game.rooms.mtt_ctrl.ranking import Ranking
import random
from poker.util import strutil
from datetime import datetime, timedelta
import freetime.util.log as ftlog
from freetime.entity.msg import MsgPack
from poker.protocol import router
from poker.entity.configure import gdata
from poker.entity.game.rooms.room import TYRoom
from poker.entity.game.rooms.queue_room import TYQueueScheduler, TYQueueRoom
from poker.entity.game.plugin import TYPluginUtils, TYPluginCenter
__author__ = ['"Zhouhao" <zhouhao@tuyoogame.com>']

class TYSMttQueueScheduler(TYQueueScheduler, ):
    """
    
    Attributes:
        _state : 队列管理器状态， 
           STATE_IDLE 队列空闲状态，即关闭循环调度；
           STATE_LOOP 队列开启循环调度状态。
    Configure：
      
    """

    def shuffleQueue(self):
        pass

    def startLoop(self, needShuffleQueue=True):
        pass

    def _isValidUser(self, userId):
        pass

    def doHeartBeat(self):
        pass

    def adjustTablePlayers(self, msg, isFinal=False):
        """

        """
        pass

class TYMttRoom(TYQueueRoom, ):
    """
    
    Attributes:
        state : MTT当前阶段
    """
    MTT_STATE_IDLE = 0
    MTT_STATE_READY = 1
    MTT_STATE_SIGNIN = 2
    MTT_STATE_ENTER = 3
    MTT_STATE_FORBIT_SIGNOUT = 4
    MTT_STATE_START = 5
    MTT_STATE_QUALIFIER = 6
    MTT_STATE_PREFINALS = 7
    MTT_STATE_FINALS = 8
    MTT_STATE_DAY1_END = 9
    mttStateStrs = {MTT_STATE_IDLE: 'IDLE', MTT_STATE_READY: 'READY', MTT_STATE_SIGNIN: 'SIGNIN', MTT_STATE_ENTER: 'ENTER', MTT_STATE_FORBIT_SIGNOUT: 'FORBIT_SIGNOUT', MTT_STATE_START: 'START', MTT_STATE_QUALIFIER: 'QUALIFIER', MTT_STATE_PREFINALS: 'PREFINALS', MTT_STATE_FINALS: 'FINALS', MTT_STATE_DAY1_END: 'MTT_STATE_DAY1_END'}

    def __init__(self, roomdefine):
        pass

    def doReloadConf(self, roomDefine):
        pass

    def __initMatch(self):
        pass

    def __initRedisLua(self):
        pass

    def getStateStr(self):
        pass

    def _initScheduler(self):
        pass

    def _tableType(self):
        pass

    def _tableTheme(self):
        pass

    def checkSitCondition(self, userId):
        pass

    def doGetMatchStatus(self, userId):
        pass

    def doGetDescription(self, userId):
        pass

    def doGetRankList(self, userId, msg):
        pass

    def doRoomUpdateRankOfAll(self):
        pass

    def doSignin(self, userId, signinParams):
        pass

    def doAdjustTablePlayers(self, msg):
        pass

    def __notifyFinalTable(self):
        pass

    def __startFinalTableLater(self):
        pass

    def __sendFinalTableInfo(self, finalTableStartTime):
        pass

    def _onQuickStartOk(self, userId):
        pass

    def allowExit(self):
        """
        筹码大于0时，是否允许退出
        """
        pass

    def _leave(self, userId, reason, needSendRes):
        pass

    def doSignout(self, userId):
        pass

    def doHeartBeat(self):
        """

        """
        pass

    def getPlayingLen(self):
        """

        """
        pass

    def doLeaveMatch(self, userId, tableId):
        pass

    def __leaveMatch(self, userId, tableId=0, needSendRewardTodoTask=True):
        pass

    def __onMatchEnd(self):
        pass

    def doChangeBetsConf(self, betsConf):
        """

        """
        pass

    def doGetMatchBuyin(self, userId):
        """

        """
        pass

    def doMatchBuyin(self, userId, buy):
        """

        """
        pass

    def doTryNotifyRebuy(self, userId):
        pass

    def getDay1EndConf(self):
        pass

    def getDay2StartConf(self):
        pass

    def isDay1Match(self):
        pass

    def isDay2Match(self):
        pass