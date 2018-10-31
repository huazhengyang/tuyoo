# -*- coding: utf-8 -*-
"""
Created on 2017年10月26日

@author: zhaoliang
"""
from datetime import datetime

def isOpen(self):
    """
    混房是否开放
    """
    pass
from poker.entity.game.rooms.queue_mixed_room_ctrl.game_open_config import MixedRoomOpenConfig
MixedRoomOpenConfig.isOpen = isOpen