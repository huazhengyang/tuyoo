# -*- coding: utf-8 -*-
"""
Created on 2017年10月30日

@author: wangyonghui
"""

def selfDrive(self):
    """
    自有队列班车发车
    返回结果为一桌一桌已经分好的玩家
    """
    pass
from poker.entity.game.rooms.queue_mixed_room_ctrl.game_queue import MixedRoomQueue
MixedRoomQueue.selfDrive = selfDrive