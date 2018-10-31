# -*- coding: utf-8 -*-
"""
Created on 2017年10月13日

@author: zhaol

"""
from freetime.util import log as ftlog
from poker.entity.biz import bireport
from poker.util import timestamp as pktimestamp
from poker.entity.game.rooms.async_common_arena_match_ctrl.aca_match_db import AsyncCommonArenaMatchDataBase

class AsyncCommonArenaMatchList(object, ):

    def __init__(self):
        pass

    @classmethod
    def getMatchList(cls, roomConfig, bigRoomId, userId, gameId):
        """
        get match list from roomConfig
        @params
        roomConfig
        """
        pass

    @classmethod
    def t2s(cls, t):
        """
        时分转化为秒数
        """
        pass