# -*- coding:utf-8 -*-
'''
Created on 2017年3月6日

@author: zhaojiangang
'''
from dizhucomm.room.events import RoomEvent

class UserEnterRoomEvent(RoomEvent):
    def __init__(self, room, player):
        super(UserEnterRoomEvent, self).__init__(room)
        self.player = player

class UserLeaveRoomEvent(RoomEvent):
    def __init__(self, room, player, reason):
        super(UserLeaveRoomEvent, self).__init__(room)
        self.player = player
        self.reason = reason


