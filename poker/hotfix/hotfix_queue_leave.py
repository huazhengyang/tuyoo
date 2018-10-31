# -*- coding: utf-8 -*-
"""
Created on 2017年10月30日

@author: wangyonghui
"""
from freetime.core.lock import locked
from poker.entity.dao import onlinedata

@locked
def doLeave(self, userId, msg):
    """
    支持离开
    """
    pass
from poker.entity.game.rooms.queue_mixed_room import TYQueueMixedRoom
TYQueueMixedRoom.doLeave = doLeave