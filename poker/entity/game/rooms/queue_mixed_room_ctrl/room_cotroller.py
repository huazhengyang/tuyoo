# -*- coding: utf-8 -*-
"""
Created on 2017年10月13日

队列混房房间的控制器

@author: zhaol
"""
from freetime.util import log as ftlog
from poker.entity.configure import gdata
from poker.entity.game.rooms.queue_mixed_room_ctrl.mixed_room import MixedRoom
from poker.entity.game.rooms.queue_mixed_room_ctrl.room_message import MixedRoomMessage
from poker.entity.dao import onlinedata
import copy

class QueueMixedRoomCtrl(object, ):
    """
    快速赛比赛阶段s
    """
    MAX_SEATID = 1000

    def __init__(self, gameId, roomId):
        pass

    @property
    def maxSeat(self):
        pass

    def setMaxSeat(self, maxSeat):
        pass

    @property
    def hasRobot(self):
        pass

    def setHasRobot(self, robot):
        pass

    @property
    def mixedUsers(self):
        pass

    def setMixedUsers(self, users):
        pass

    @property
    def mixedRooms(self):
        pass

    def setMixedRooms(self, mRooms):
        pass

    @property
    def gameId(self):
        pass

    @property
    def roomId(self):
        pass

    def setGameId(self, gameId):
        pass

    def setRoomId(self, roomId):
        pass

    def initRoom(self, rConfig=None):
        """
        初始化房间
        """
        pass

    def cloneAndReverseList(self, rooms):
        """
        克隆并翻转一个list
        """
        pass

    @property
    def msgSender(self):
        """
        消息发送器
        """
        pass

    def setMsgSender(self, sender):
        pass

    def getMixedRoom(self, mixedRoomId):
        """
        根据混房ID获取房间管理类
        """
        pass

    def enterRoom(self, userId, roomId, mixedRoomId):
        """
        进入房间，进入队列
        """
        pass

    def queueTableId(self, roomId):
        """
        队列里的牌桌ID，用来标记loc状态
        """
        pass

    def leaveRoom(self, userId, mixedRoomId):
        """
        离开队列
        """
        pass

    def backRoom(self, userId):
        """
        回到房间
        """
        pass

    def handleRoomAction(self, delta):
        """
        更新队列班车
        """
        pass

    def canMixedDrive(self, mRoom):
        """
        是否可以混房发车
        """
        pass

    def driveUsers(self, users):
        """
        用户分桌
        """
        pass

    def processMixedPlayers(self, mixedUsers):
        """
        分配混房的人组桌
        """
        pass