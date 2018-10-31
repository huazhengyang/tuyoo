# -*- coding: utf-8 -*-
"""
Created on 2016年1月16日

@author: zhaojiangang
"""
import random
import freetime.util.log as ftlog
from poker.entity.game.rooms.group_match_ctrl.interface import SignIF, MatchRewards, TableController, PlayerNotifier, UserInfoLoader, MatchStatusDao
from poker.entity.game.rooms.group_match_ctrl.models import Signer
from poker.entity.game.rooms.group_match_ctrl.utils import Heartbeat
import poker.util.timestamp as pktimestamp

class SignIFMem(SignIF, ):

    def __init__(self):
        pass

    def findSigner(self, instId, userId):
        pass

    def signin(self, userId, matchId, ctrlRoomId, instId, fees):
        """
        报名接口，如果不成功抛异常
        """
        pass

    def signout(self, userId, matchId, ctrlRoomId, instId, fees):
        """

        """
        pass

    def loadAllUsers(self, matchId, ctrlRoomId, instId):
        """

        """
        pass

    def removeAllUsers(self, matchId, ctrlRoomId, instId):
        """

        """
        pass

    def lockUser(self, matchId, ctrlRoomId, instId, userId):
        """

        """
        pass

    def unlockUser(self, matchId, ctrlRoomId, instId, userId, fees):
        """

        """
        pass

class MatchRewardsTest(MatchRewards, ):

    def sendRewards(self, player, rankRewards):
        """

        """
        pass

class TableControllerTest(TableController, ):

    def __init__(self, match):
        pass

    def startTable(self, table):
        """
        让桌子开始
        """
        pass

    def clearTable(self, table):
        """
        清理桌子
        """
        pass

    def updateTableInfo(self, table):
        """
        桌子信息变化
        """
        pass

    def userReconnect(self, table, seat):
        """
        用户坐下
        """
        pass

    def _processTables(self):
        pass

    def _randomUserWinlose(self, table):
        pass

class PlayerNotifierTest(PlayerNotifier, ):

    def notifyMatchCancelled(self, signinUser, reason, message=None):
        """
        通知用户比赛由于reason取消了
        """
        pass

    def notifyMatchOver(self, player, reason, rankRewards):
        """
        通知用户比赛结束了
        """
        pass

    def notifyMatchGiveupFailed(self, player, message):
        """
        通知用户不能放弃比赛
        """
        pass

    def notifyMatchUpdate(self, player):
        """
        通知比赛更新
        """
        pass

    def notifyMatchRank(self, player):
        """
        通知比赛排行榜
        """
        pass

    def notifyMatchWait(self, player, step=None):
        """
        通知用户等待
        """
        pass

    def notifyMatchStart(self, instId, signers):
        """
        通知用户比赛开始
        """
        pass

    def notifyStageStart(self, player):
        """
        通知用户正在配桌
        """
        pass

class UserInfoLoaderTest(UserInfoLoader, ):

    def __init__(self):
        pass

    def setUserAttrs(self, userId, userAttrMap):
        pass

    def loadUserAttrs(self, userId, attrs):
        """

        """
        pass

class MatchStatusDaoMem(MatchStatusDao, ):

    def __init__(self):
        pass

    def load(self, matchId):
        """
        加载比赛信息
        @return: MatchStatus
        """
        pass

    def save(self, status):
        """
        保存比赛信息
        """
        pass