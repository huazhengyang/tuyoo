# -*- coding: utf-8 -*-
"""
Created on 2017年10月13日

比赛报名费

@author: zhaol

"""
from freetime.entity.msg import MsgPack
from poker.protocol import router
from poker.entity.configure import gdata
from random import choice

class MixedRoomMessage(object, ):

    def __init__(self):
        pass

    def init(self, gameId, roomId):
        """
        初始化
        """
        pass

    @property
    def gameId(self):
        pass

    def setGameId(self, gameId):
        pass

    @property
    def roomId(self):
        pass

    def setRoomId(self, roomId):
        pass

    def roomEnterQueueSucc(self, userId, mixedRoomId):
        """
        比赛报名成功
        """
        pass

    def roomEnterQueueFail(self, userId, code, info):
        """
        比赛报名成功
        """
        pass

    def roomLeaveQueueSucc(self, userId, mixedRoomId):
        """
        比赛报名成功
        """
        pass

    def roomLeaveQueueFail(self, userId, mixedRoomId, code, info):
        """
        比赛报名成功
        """
        pass

    def createMsgPackResult(self, cmd, action=None):
        """

        """
        pass

    def roomTableStart(self, users):
        """
        比赛报名成功
        """
        pass
if (__name__ == '__main__'):
    pass