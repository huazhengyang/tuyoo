# -*- coding: utf-8 -*-
"""
Created on 2016年1月16日

@author: zhaojiangang
"""
import random
import freetime.util.log as ftlog
from poker.entity.game.rooms.erdayi_match_ctrl.interface import SigninRecordDao, MatchRewards, TableController, PlayerNotifier, SignerInfoLoader, MatchStatusDao, MatchUserIF
from poker.entity.game.rooms.erdayi_match_ctrl.utils import HeartbeatAble
from poker.util import strutil
import poker.util.timestamp as pktimestamp

class SigninRecordDaoTest(SigninRecordDao, ):

    def __init__(self):
        pass

    @classmethod
    def buildKey(cls, instId, ctrlRoomId):
        pass

    def loadAll(self, matchId, instId, ctrlRoomId):
        """
        获取所有在本ctrlRoomId下的所有报名记录
        @return: list<SigninRecord>
        """
        pass

    def add(self, matchId, instId, ctrlRoomId, record):
        """
        记录用户报名
        @return: 成功返回True，如果已经存返回False
        """
        pass

    def remove(self, matchId, instId, ctrlRoomId, userId):
        """
        删除用户报名记录
        """
        pass

    def removeAll(self, matchId, instId, ctrlRoomId):
        """
        删除所有报名记录
        """
        pass

class MatchRewardsTest(MatchRewards, ):

    def sendRewards(self, player, rankRewards):
        """

        """
        pass

class TableControllerTest(HeartbeatAble, TableController, ):

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

    def _doHeartbeat(self):
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

class SignerInfoLoaderTest(SignerInfoLoader, ):

    def __init__(self):
        pass

    def setUserAttrs(self, userId, userAttrMap):
        pass

    def fillSigner(self, signer):
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

class MatchUserIFTest(MatchUserIF, ):

    def createUser(self, matchId, ctrlRoomId, instId, userId, fee):
        """

        """
        pass

    def removeUser(self, matchId, ctrlRoomId, instId, userId):
        """

        """
        pass

    def lockUser(self, matchId, ctrlRoomId, instId, userId, clientId):
        """
        锁定用户
        """
        pass

    def unlockUser(self, matchId, ctrlRoomId, instId, userId):
        """
        解锁用户并返还报名费
        """
        pass