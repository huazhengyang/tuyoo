# -*- coding: utf-8 -*-
"""
Created on 2015年11月12日

@author: zhaojiangang
"""
from poker.entity.dao import daobase
from poker.util import strutil
import freetime.util.log as ftlog

class UserLocker(object, ):

    def lockUser(self, userId, roomId, tableId, seatId):
        pass

    def unlockUser(self, roomId, tableId):
        pass

class SigninFee(object, ):

    def collectFee(self, inst, userId, fee, mixId=None):
        """
        收取用户报名费, 如果报名费不足则抛异常SigninFeeNotEnoughException
        """
        pass

    def returnFee(self, inst, userId, fee, mixId=None):
        """
        退还报名费
        """
        pass

class SigninRecordDao(object, ):

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

    def removeAll(self, matchId):
        """
        删除instId相关的所有报名信息
        """
        pass

class MatchTableController(object, ):

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

class MatchPlayerNotifier(object, ):

    def notifyMatchStart(self, player):
        """
        通知用户比赛开始了
        """
        pass

    def notifyMatchWait(self, player):
        """
        通知用户等待晋级
        """
        pass

    def notifyMatchRank(self, player):
        """
        通知比赛排行榜
        """
        pass

    def notifyMatchGiveupFailed(self, player, info):
        """
        通知用户放弃比赛失败
        """
        pass

    def notifyMatchWillCancelled(self, player, reason):
        """
        通知用户比赛即将取消
        """
        pass

    def notifyMatchCancelled(self, player, reason):
        """
        通知用户比赛取消
        """
        pass

    def notifyMatchOver(self, player, reason, rankRewards):
        """
        通知用户比赛结束了
        """
        pass

    def notifyMatchUserRevive(self, player, reviveContent):
        """
        通知用户复活
        """
        pass

class UserInfoLoader(object, ):

    def loadUserAttrs(self, userId, attrs):
        """
        获取用户属性
        """
        pass

    def getSessionClientId(self, userId):
        """
        获取用户sessionClientId
        """
        pass

    def getGameSessionVersion(self, userId):
        """
        获取用户所在Game插件版本
        """
        pass

class MatchRankRewardsSender(object, ):

    def sendRankRewards(self, player, rankRewards):
        """
        给用户发奖
        """
        pass

class MatchRankRewardsSelector(object, ):

    def getRewards(self, userId, rankRewards, mixId):
        """
        获取渠道奖励
        """
        pass

    def getRewardsList(self, userId, rankRewardsList, mixId):
        """
        获取渠道奖励列表
        """
        pass

class MatchSafeItem(object, ):

    def __init__(self, timestamp=0, count=0):
        pass

    def toDict(self):
        pass

    def fromDict(self, d):
        pass

class MatchSafe(object, ):

    def __init__(self, lifeSafe=None, dailySafe=None):
        pass

    def toDict(self):
        pass

    def fromDict(self, d):
        pass

class MatchSafeDao(object, ):

    def load(self, userId, matchId):
        pass

    def save(self, userId, matchId, matchSafe):
        pass

class MatchSafeDaoRedis(MatchSafeDao, ):

    def load(self, userId, matchId):
        pass

    def save(self, userId, matchId, matchSafe):
        pass