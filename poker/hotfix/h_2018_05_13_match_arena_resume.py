# -*- coding: utf-8 -*-
"""
Created on 2018年05月12日

比赛结束的消息100%发到前端

@author: zhaoliang
"""
from poker.entity.dao import sessiondata
from freetime.core.lock import locked
from poker.entity.game.rooms import quick_save_async_match
from poker.entity.configure import gdata

@locked
def doMatchResume(self, userId, gameId, roomId, matchId, msg):
    """
    比赛进度恢复
    确认恢复数据有效
    重新设置比赛loc
    返回前端具体的wait消息，等待其下一步操作
    """
    pass
from poker.entity.game.rooms.async_common_arena_match_room import TyAsyncCommonArenaMatchRoom
TyAsyncCommonArenaMatchRoom.doMatchResume = doMatchResume