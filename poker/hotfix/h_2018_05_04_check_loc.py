# -*- coding: utf-8 -*-
"""
Created on 2017年10月26日

@author: zhaoliang
"""
from freetime.util import log as ftlog
from poker.entity.configure import gdata
from poker.entity.game.rooms.async_upgrade_hero_match import TyAsyncUpgradeHeroMatchRoom

def doCheckUserLoc(self, userId, gameId, roomId, tableId, clientId):
    """
        检查给出的玩家是否再当前的房间和桌子上,
        依照个个游戏的自己的业务逻辑进行判定,
        seatId >= 0 
        isObserving == 1|0 旁观模式
        当seatId > 0 或 isObserving == 1时表明此玩家在当前的桌子内
    """
    pass
TyAsyncUpgradeHeroMatchRoom.doCheckUserLoc = doCheckUserLoc