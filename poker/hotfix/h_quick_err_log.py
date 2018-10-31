# -*- coding: utf-8 -*-
"""
Created on 2017年1月19日

@author: zhaojiangang
"""
import freetime.util.log as ftlog
from poker.entity.configure import gdata
from poker.entity.dao import userchip
from poker.entity.game.quick_start import BaseQuickStart
from poker.entity.game.rooms.room import TYRoom

@classmethod
def _canQuickEnterRoom(cls, userId, gameId, roomId, isOnly):
    pass
BaseQuickStart._canQuickEnterRoomOld = BaseQuickStart._canQuickEnterRoom
BaseQuickStart._canQuickEnterRoom = _canQuickEnterRoom