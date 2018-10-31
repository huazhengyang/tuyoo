# -*- coding: utf-8 -*-
"""

"""
__author__ = ['"Zhouhao" <zhouhao@tuyoogame.com>']
import freetime.util.log as ftlog
from freetime.util.log import getMethodName
from freetime.entity.msg import MsgPack
from poker.protocol import router
from poker.entity.dao import userchip, sessiondata
from poker.entity.biz import bireport
from poker.entity.configure import gdata
from poker.util import strutil

class TYRoomMixin(object, ):
    """
    
    """

    def _baseLogStr(self, des='', userId=None):
        pass

    @classmethod
    def sendRoomQuickStartReq(cls, msg, roomId, tableId, **kwargs):
        pass

    @classmethod
    def queryRoomQuickStartReq(cls, msg, roomId, tableId, **kwargs):
        pass

    @classmethod
    def queryRoomGetPlayingTableListReq(cls, shadowRoomId, **kwargs):
        pass

    @classmethod
    def makeSitReq(cls, userId, shadowRoomId, tableId, clientId):
        pass

    @classmethod
    def sendSitReq(cls, userId, shadowRoomId, tableId, clientId, extParams=None):
        pass

    @classmethod
    def querySitReq(cls, userId, shadowRoomId, tableId, clientId, extParams=None):
        pass

    @classmethod
    def sendTableCallObserveReq(cls, userId, shadowRoomId, tableId, clientId):
        pass

    @classmethod
    def makeTableManageReq(cls, userId, shadowRoomId, tableId, clientId, action, params=None):
        pass

    @classmethod
    def queryTableManageSitReq(cls, userId, shadowRoomId, tableId, clientId):
        pass

    @classmethod
    def queryTableManageTableStandupReq(cls, userId, shadowRoomId, tableId, seatId, clientId, reason):
        pass

    @classmethod
    def queryTableManageTableLeaveReq(cls, userId, shadowRoomId, tableId, clientId, params=None):
        pass

    def sendTableManageGameStartReq(self, shadowRoomId, tableId, userIds, recyclePlayersN=0, params=None):
        """

        """
        pass

    @classmethod
    def queryTableManageClearPlayersReq(cls, shadowRoomId, tableId):
        pass

    @classmethod
    def sendChangeBetsConfReq(cls, shadowRoomId, betsConf):
        pass

    @classmethod
    def sendChangeBetsConfReqToAllShadowRoom(cls, ctrlRoomId, betsConf):
        pass

    @classmethod
    def sendTableClothRes(cls, gameId, userId, tableType, tableTheme=None):
        pass

    @classmethod
    def sendQuickStartRes(cls, gameId, userId, reason, roomId=0, tableId=0, info=''):
        pass

    def reportBiGameEvent(self, eventId, userId, roomId, tableId, roundId, detalChip, state1, state2, cardlist, tag=''):
        pass