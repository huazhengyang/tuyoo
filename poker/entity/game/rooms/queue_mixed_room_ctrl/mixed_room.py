# -*- coding: utf-8 -*-
"""
Created on 2017年10月13日

队列混房房间的控制器

@author: zhaol
"""
from poker.entity.game.rooms.queue_mixed_room_ctrl.game_queue import MixedRoomQueue
from poker.entity.game.rooms.queue_mixed_room_ctrl.game_player import MixedRoomPlayer
from poker.entity.game.rooms.queue_mixed_room_ctrl.game_open_config import MixedRoomOpenConfig
from poker.entity.game.rooms.queue_mixed_room_ctrl.room_mixed_config import RoomMixedConfig
from freetime.util import log as ftlog

class MixedRoom(object, ):
    """
    快速赛比赛阶段s
    """

    def __init__(self, gameId, roomId):
        pass

    @property
    def mixedConfig(self):
        pass

    def setMixedConfig(self, mixedConfig):
        pass

    @property
    def openConfig(self):
        """
        混房开关设置
        """
        pass

    def setOpenConfig(self, config):
        pass

    @property
    def roomQueue(self):
        pass

    def setRoomQueue(self, queue):
        pass

    @property
    def queueConfig(self):
        pass

    def setQueueConfig(self, config):
        pass

    @property
    def mixedQueue(self):
        pass

    def setMixedQueue(self, queue):
        pass

    @property
    def baseChip(self):
        pass

    def setBaseChip(self, bChip):
        pass

    @property
    def roomConfig(self):
        pass

    def setRoomConfig(self, config):
        pass

    @property
    def mixedRoomId(self):
        pass

    def setMixedRoomId(self, mRooms):
        pass

    @property
    def gameId(self):
        pass

    def roomId(self):
        pass

    def setGameId(self, gameId):
        pass

    def setRoomId(self, roomId):
        pass

    def initRoom(self, rConfig, mixedConfigDefault={}):
        """
        初始化房间
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

    def backRoom(self, userId):
        """
        回到房间队列
        """
        pass

    def enterRoom(self, userId, roomId):
        """
        进入房间，进入队列
        """
        pass

    def leaveRoom(self, userId):
        """
        离开队列
        """
        pass

    def deltaTick(self, delta):
        """
        班车tick
        """
        pass

    def isMixedOpen(self):
        """
        是否支持混房
        """
        pass

    def isDriveBus(self):
        """
        是否发车
        """
        pass

    def selfDrive(self):
        """
        班车自己发车
        不考虑机器人
        """
        pass

    def mixedDrive(self, count):
        """
        混房发车
        """
        pass

    def leftUserCount(self):
        """
        房间人数
        """
        pass

    def leftMixedUserCount(self):
        """
        剩余可以混房的人数
        """
        pass