# -*- coding: utf-8 -*-
"""
Created on 2017年10月13日

快开赛的玩家对象
@author: zhaol

"""
from poker.util import timestamp as pktimestamp

class MixedRoomPlayer(object, ):

    def __init__(self):
        pass

    @property
    def baseChip(self):
        pass

    def setBaseChip(self, baseChip):
        pass

    def initPlayer(self, userId, roomId, mixedRoomId, baseChip):
        """
        初始化用户
        """
        pass

    @property
    def mixedRoomId(self):
        pass

    def setMixedRoomId(self, roomId):
        pass

    @property
    def enterTime(self):
        pass

    def setEnterTime(self, time):
        pass

    @property
    def roomId(self):
        pass

    def setRoomId(self, roomId):
        pass

    @property
    def tableId(self):
        """
        比赛时候的牌桌ID
        """
        pass

    def setTableId(self, tableId):
        pass

    def getObject(self):
        """
        获取player的对象
        """
        pass

    @property
    def userId(self):
        """
        用户ID
        """
        pass

    def setUserId(self, userId):
        pass