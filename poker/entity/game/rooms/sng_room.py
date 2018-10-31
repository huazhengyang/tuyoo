# -*- coding: utf-8 -*-
"""

"""
__author__ = ['"Zhouhao" <zhouhao@tuyoogame.com>']
from datetime import datetime
import freetime.util.log as ftlog
from freetime.entity.msg import MsgPack
from poker.protocol import router
from poker.entity.configure import gdata
from poker.entity.game.rooms.room import TYRoom
from poker.entity.game.rooms.queue_room import TYQueueScheduler, TYQueueRoom
from poker.entity.game.plugin import TYPluginUtils

class TYSNGQueueScheduler(TYQueueScheduler, ):
    """
    
    Attributes:
        _state : 队列管理器状态， 
           STATE_IDLE 队列空闲状态，即关闭循环调度；
           STATE_LOOP 队列开启循环调度状态。
           STATE_START_TABLE 开桌转态，此时不允许玩家leave room，以免造成开局缺人问题。
    
    Configure：
      
    """
    pass

class TYSngRoom(TYQueueRoom, ):
    """
    
    Attributes:
    """

    def __init__(self, roomDefine):
        pass

    def doReloadConf(self, roomDefine):
        pass

    def __initMatch(self):
        pass

    def _tableType(self):
        pass

    def _tableTheme(self):
        pass

    def _onLeaveQueueOk(self, userId):
        pass

    def _onQuickStartOk(self, userId):
        pass

    def checkSitCondition(self, userId):
        pass

    def doGetMatchList(self, userId, page=0, number=10, tag='all'):
        pass

    def doGetDescription(self, userId):
        pass

    def doGetRankList(self, userId, msg):
        pass

    def doMatchStart(self, table, msg):
        pass

    def doLeaveMatch(self, userId, table, leaveReason):
        pass