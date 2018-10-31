# -*- coding: utf-8 -*-
"""
Created on 2014年9月17日

@author: zjgzzz@126.com
"""

class PlayerLocation(object, ):
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

    def notifyMatchCancelled(self, player, inst, reason, message=None):
        """
        通知用户比赛由于reason取消了
        """
        pass

    def notifyMatchOver(self, player, group, reason, rankRewards):
        """
        通知用户比赛结束了
        """
        pass

    def notifyMatchGiveupFailed(self, player, group, message):
        """
        通知用户不能放弃比赛
        """
        pass

    def notifyMatchUpdate(self, player, group):
        """
        通知比赛更新
        """
        pass

    def notifyMatchRank(self, player, group):
        """
        通知比赛排行榜
        """
        pass

    def notifyMatchWait(self, player, group, step=None):
        """
        通知用户等待
        """
        pass

    def notifyMatchStart(self, players, group):
        """
        通知用户比赛开始
        """
        pass

    def notifyStageStart(self, player, group):
        """
        通知用户正在配桌
        """
        pass

class SigninRecordDao(object, ):

    def load(self, matchId, instId):
        """
        加载所有报名记录
        @return: list((userId, signinTime))
        """
        pass

    def recordSignin(self, matchId, instId, userId, timestamp, signinParams):
        """
        记录报名信息
        """
        pass

    def removeSignin(self, matchId, instId, userId):
        """
        删除报名信息
        """
        pass

    def removeAll(self, matchId, instId):
        """
        删除instId相关的所有报名信息
        """
        pass

class MatchRewards(object, ):

    def sendRewards(self, player, group, rankRewards):
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

class SigninFee(object, ):

    def collectFees(self, inst, userId, fees):
        """
        收取用户报名费, 如果报名费不足则抛异常SigninFeeNotEnoughException
        """
        pass

    def returnFees(self, inst, userId, fees):
        """
        退还报名费
        """
        pass

class UserInfoLoader(object, ):

    def loadUserName(self, userId):
        """
        获取用户名称
        """
        pass

    def loadUserAttrs(self, userId, attrs):
        """

        """
        pass