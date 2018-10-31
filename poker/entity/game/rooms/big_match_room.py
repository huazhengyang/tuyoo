# -*- coding: utf-8 -*-
"""

"""
import functools
import random
from freetime.core.timer import FTTimer
from freetime.entity.msg import MsgPack
from freetime.util.log import getMethodName
import freetime.util.log as ftlog
from poker.entity.configure import gdata
from poker.entity.dao import onlinedata
from poker.entity.game.rooms.big_match_ctrl.config import MatchConfig
from poker.entity.game.rooms.big_match_ctrl.exceptions import MatchException
from poker.entity.game.rooms.big_match_ctrl.match import TableManager, MatchInstance
from poker.entity.game.rooms.room import TYRoom
from poker.entity.game.tables.table_player import TYPlayer
from poker.protocol import router
__author__ = ['"Zhouhao" <zhouhao@tuyoogame.com>']

class TYBigMatchRoom(TYRoom, ):
    """
    
    Attributes:
        matchPlugin： 各游戏通过定义自己的BigMatchPlugin，来扩展数据获取、下发协议、异常处理、结算等功能
        match: 比赛控制器
        bigmatchId: bigRoomId， 兼容老代码
    """

    def __init__(self, roomdefine):
        pass

    def initMatch(self):
        pass

    def doEnter(self, userId):
        pass

    def doLeave(self, userId, msg):
        pass

    def doGetDescription(self, userId):
        pass

    def __getMatchStatas(self, userId):
        pass

    def doUpdateInfo(self, userId):
        pass

    def __getUserMatchSigns(self, uid, signs):
        pass

    def doSignin(self, userId, signinParams, feeIndex=0):
        pass

    def doSignout(self, userId):
        pass

    def doGiveup(self, userId):
        pass

    def doWinlose(self, msg):
        pass

    def _findUserByTableRank(self, container, tableRank):
        pass

    def doQuickStart(self, msg):
        pass

    def __getMatchRanksQuick(self, userId):
        pass

    def __notifyRobotSigninMatch(self, player):
        pass