# -*- coding: utf-8 -*-
"""
Created on 2016年7月13日

@author: zhaojiangang
"""
from poker.entity.game.rooms.erdayi_match_ctrl.utils import Logger

class SigninFee(object, ):

    def collectFee(self, matchId, roomId, instId, userId, fee):
        """
        收取用户报名费, 如果报名费不足则抛异常SigninFeeNotEnoughException
        """
        pass

    def returnFee(self, matchId, roomId, instId, userId, fee):
        """
        退还报名费
        """
        pass

class SigninRecord(object, ):

    def __init__(self, userId, signinTime=None, fee=None):
        pass

class SigninRecordDao(object, ):

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

class MatchUserIF(object, ):

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

class SignerInfoLoader(object, ):

    def fillSigner(self, signer):
        """

        """
        pass

class MatchRewards(object, ):

    def sendRewards(self, player, rankRewards):
        """

        """
        pass

class TableController(object, ):

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

    def userReconnect(self, table, seat):
        """
        用户坐下
        """
        pass

class PlayerNotifier(object, ):

    def notifyMatchCancelled(self, signer, reason, message=None):
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

class MatchStage(object, ):

    def __init__(self, stageConf, group):
        pass

    @property
    def matchConf(self):
        pass

    @property
    def matchingId(self):
        pass

    @property
    def matchingId3(self):
        pass

    @property
    def stageId3(self):
        pass

    @property
    def isMatchOver(self):
        pass

    @property
    def promotionMatchId(self):
        pass

    @property
    def promotionCount(self):
        pass

    @property
    def roundStages(self):
        pass

    @property
    def stageConf(self):
        pass

    @property
    def stageIndex(self):
        pass

    @property
    def group(self):
        pass

    @property
    def area(self):
        pass

    def calcUncompleteTableCount(self, player):
        pass

    def hasNextStage(self):
        pass

    def start(self):
        pass

    def kill(self, reason):
        pass

    def finish(self, reason):
        pass

    def isStageFinished(self):
        pass

    def processStage(self):
        pass

class MatchFactory(object, ):

    def newStage(self, stageConf, group):
        """
        创建阶段
        """
        pass

    def newSigner(self, userId, instId):
        """
        创建一个Signer
        """
        pass

    def newPlayer(self, signer):
        """
        创建一个Player
        """
        pass

class MatchStatus(object, ):

    def __init__(self, matchId=None, sequence=None, startTime=None):
        pass

    @property
    def instId(self):
        pass

class MatchStatusDao(object, ):

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

    def getNextMatchingSequence(self, matchId):
        """

        """
        pass