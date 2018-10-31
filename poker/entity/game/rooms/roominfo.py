# -*- coding: utf-8 -*-
"""
Created on 2016年4月22日

@author: zhaojiangang
"""
from poker.entity.dao import daobase
from poker.util import strutil
import freetime.util.log as ftlog
from poker.entity.biz.content import TYContentItem

class RoomInfo(object, ):
    clzMap = {}

    def __init__(self, roomType):
        pass

    @classmethod
    def registerRoomType(cls, typeName, clz):
        pass

    @classmethod
    def fromDict(cls, roomId, d):
        pass

    def toDict(self):
        pass

    def _toDictImpl(self, d):
        pass

class MatchRoomInfo(RoomInfo, ):

    def __init__(self):
        pass

    def fromDict(self, d):
        pass

    def _toDictImpl(self, d):
        pass
RoomInfo.registerRoomType('match', MatchRoomInfo)

def buildKey(gameId):
    pass

def decodeRoomInfo(roomId, jstr):
    pass

def loadAllRoomInfo(gameId):
    pass

def loadRoomInfo(gameId, roomId):
    pass

def saveRoomInfo(gameId, roomInfo):
    pass

def removeRoomInfo(gameId, roomId):
    pass