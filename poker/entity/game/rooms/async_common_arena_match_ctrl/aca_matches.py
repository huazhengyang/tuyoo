# -*- coding: utf-8 -*-
"""
Created on 2017年10月13日

比赛tips
@author: zhaol

"""
from poker.entity.game.rooms.async_common_arena_match_ctrl.aca_match import AsyncCommonArenaMatch
from poker.entity.game.rooms.async_common_arena_match_ctrl.aca_game_queues import AsyncCommonArenaQueues
from freetime.util import log as ftlog
from poker.entity.game.rooms.async_common_arena_match_ctrl.aca_match_report import AsyncCommonArenaReport
from poker.entity.dao import onlinedata
from poker.entity.game.rooms.async_common_arena_match_ctrl.aca_game_player import AsyncCommonArenaPlayer
from poker.util import strutil
from poker.entity.configure import gdata
from poker.entity.game.rooms.async_common_arena_match_ctrl.aca_exceptions import AsyncCommonArenaError

class AsyncCommonArenaMatches(object, ):
    MAX_SEAT = 1000

    def __init__(self, gameId, roomId):
        pass

    @property
    def queues(self):
        """
        比赛队列
        """
        pass

    def setQueues(self, queues):
        pass

    @property
    def gameId(self):
        pass

    def setGameId(self, gameId):
        pass

    @property
    def roomId(self):
        pass

    def setRoomId(self, roomId):
        pass

    @property
    def matches(self):
        pass

    def setMatches(self, matches):
        pass

    @property
    def buyinChip(self):
        pass

    def setBuyinChip(self, bChip):
        pass

    def initMatches(self, config):
        """
        初始化比赛
        """
        pass

    def queueTableId(self, roomId):
        """
        队列里的牌桌ID，用来标记loc状态
        """
        pass

    def isInGiveUpMatch(self, userId):
        """
        是否在退赛的比赛中
        """
        pass

    def checkGameLoc(self, userId, gameId):
        """
        检查用户的游戏LOC，如有该游戏的LOC，报名失败，提示正在其他房间/比赛中
        """
        pass

    def signIn(self, userId, signinParams):
        """
        报名比赛
        """
        pass

    def signOut(self, userId):
        """
        退出比赛
        """
        pass

    def enter(self, userId):
        """
        进入比赛
        """
        pass

    def des(self, userId, gameId, matchId):
        """
        获取比赛信息
        """
        pass

    def giveUp(self, userId, gameId, matchId):
        """
        放弃比赛
        """
        pass

    def matchChallenge(self, userId, gameId, matchId):
        """
        继续比赛
        """
        pass

    def matchBack(self, userId, gameId, matchId):
        """
        match back
        """
        pass

    def matchSave(self, userId, gameId, matchId):
        pass

    def matchResume(self, userId, gameId, matchId):
        pass

    def winLooses(self, tableId, users):
        """
        结算
        """
        pass

    def matchTableError(self, tableId, users):
        """
        比赛出现错误
        """
        pass

    def backMatch(self, userId):
        """
        回到比赛，补发wait消息
        """
        pass

    def findMatchByUser(self, userId):
        """
        查到当前用户在哪个比赛中
        """
        pass

    def findMatch(self, matchId):
        """
        查找比赛
        """
        pass

    def firstMatch(self):
        """
        第一个比赛
        """
        pass

    def handleRoomAction(self, delta):
        """
        班车调度
        """
        pass
if (__name__ == '__main__'):
    pass