# -*- coding: utf-8 -*-
"""
Created on 2014年9月17日

@author: zjgzzz@126.com
"""
from poker.entity.game.rooms.big_match_ctrl.const import WaitReason

class Player(object, ):
    STATE_IDLE = 0
    STATE_PLAYING = 1
    STATE_WINLOSE = 2
    STATE_WAIT = 3
    STATE_OUT = 4
    WHEN_OUT_NORMAL = 0
    WHEN_OUT_ASS = 1

    def __init__(self, inst, userId, userName, signinTime, activeTime, clientId=''):
        pass

    @property
    def seat(self):
        pass

    @property
    def table(self):
        pass

    @property
    def matchId(self):
        pass

    def getSigninParam(self, name, defVal=None):
        pass

    def __repr__(self):
        pass

    def __str__(self):
        pass

    def __unicode__(self):
        pass

class Seat(object, ):

    def __init__(self, table, seatId):
        pass

    @property
    def gameId(self):
        pass

    @property
    def roomId(self):
        pass

    @property
    def tableId(self):
        pass

    @property
    def location(self):
        pass

    @property
    def player(self):
        pass

class Table(object, ):

    def __init__(self, gameId, roomId, tableId, seatCount):
        pass

    @property
    def location(self):
        pass

    @property
    def seats(self):
        pass

    def sitdown(self, player):
        """
        玩家坐下
        """
        pass

    def standup(self, player):
        """
        玩家离开桌子
        """
        pass

    @property
    def seatCount(self):
        """
        座位数量
        """
        pass

    def clear(self):
        pass

    def getIdleSeatCount(self):
        """
        空闲座位数量
        """
        pass

    def getPlayingPlayerCount(self):
        """
        获取PLAYING状态的玩家数量
        """
        pass

    def getPlayingPlayerList(self):
        pass

    def getPlayerList(self):
        pass

    def getUserIdList(self):
        pass

    def _clearSeat(self, seat):
        pass

    def _makeSeats(self, count):
        pass