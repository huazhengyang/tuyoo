# -*- coding: utf-8 -*-
"""
Created on 2016年1月15日

@author: zhaojiangang
"""

class SignIF(object, ):

    def signin(self, userId, matchId, ctrlRoomId, instId, fee):
        """
        报名接口，如果不成功抛异常
        """
        pass

    def moveTo(self, userId, matchId, ctrlRoomId, instId, toInstId):
        """
        移动玩家到下一场比赛
        """
        pass

    def signout(self, userId, matchId, ctrlRoomId, instId, feeContentItem):
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

    def lockUser(self, matchId, ctrlRoomId, instId, userId, clientId=None):
        """

        """
        pass

    def unlockUser(self, matchId, ctrlRoomId, instId, userId, feeContentItem):
        """

        """
        pass

class UserInfoLoader(object, ):

    def loadUserAttrs(self, userId, attrs):
        """

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

    def notifyMatchWait(self, player, step=None, riseWait=0):
        """
        通知用户等待
        """
        pass

    def notifyMatchStart(self, group, signers):
        """
        通知用户比赛开始
        """
        pass

    def notifyStageStart(self, player):
        """
        通知用户正在配桌
        """
        pass

    def notifyMatchTimeEnd(self, player, instId):
        """
        通知报名用户比赛结束
        """
        pass

class MatchRankRewardsSelector(object, ):

    def getRewards(self, userId, rankRewards):
        """
        获取渠道奖励
        """
        pass

    def getRewardsList(self, userId, rankRewardsList):
        """
        获取渠道奖励列表
        """
        pass