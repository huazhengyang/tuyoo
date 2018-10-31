# -*- coding: utf-8 -*-
"""

"""
import freetime.util.log as ftlog
from poker.entity.configure import gdata, pokerconf
from poker.entity.dao import onlinedata, userchip
from poker.entity.game.rooms.room import TYRoom
from poker.entity.game.rooms.room_mixin import TYRoomMixin
from poker.util import strutil
from freetime.entity.msg import MsgPack
__author__ = ['"Zhouhao" <zhouhao@tuyoogame.com>']
_CANDIDATE_ROOM_IDS = {}

class BaseQuickStartDispatcher(object, ):
    """

    """

    @classmethod
    def dispatchQuickStart(cls, msg, userId, gameId, roomId, tableId, playMode, clientId):
        pass

class BaseQuickStart(object, ):
    """

    """

    @classmethod
    def onCmdQuickStart(cls, msg, userId, gameId, roomId, tableId, playMode, clientId):
        """
        Args:
            msg
                cmd : quick_start
                if roomId == 0:
                    表示快速开始，服务器为玩家选择房间，然后将请求转给GR
                    
                if roomId > 0 and tableId == 0 : 
                    表示玩家选择了房间，将请求转给GR
                    
                if roomId > 0 and tableId == roomId * 10000 :
                    表示玩家在队列里断线重连，将请求转给GR
                    
                if roomId > 0 and tableId > 0:
                    if onlineSeatId > 0: 
                        表示玩家在牌桌里断线重连，将请求转给GT
                    else:
                        表示玩家选择了桌子，将请求转给GR
        """
        pass

    @classmethod
    def _chooseRoom(cls, userId, gameId, playMode):
        """

        """
        pass

    @classmethod
    def _onEnterRoomFailed(cls, msg, checkResult, userId, clientId, roomId=0):
        """

        """
        pass

    @classmethod
    def _initCandidateRoomIdsByGameId(cls, gameId):
        pass

    @classmethod
    def _initCandidateRoomIds(cls):
        pass

    @classmethod
    def _getCandidateRoomIds(cls, gameId, playMode):
        pass

    @classmethod
    def _canQuickEnterRoom(cls, userId, gameId, roomId, isOnly):
        pass