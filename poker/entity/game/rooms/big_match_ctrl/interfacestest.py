# -*- coding: utf-8 -*-
"""
Created on 2014年9月24日

@author: zjgzzz@126.com
"""
import freetime.util.log as ftlog
from poker.entity.game.rooms.big_match_ctrl.exceptions import MatchException
from poker.entity.game.rooms.big_match_ctrl.interfaces import TableController, PlayerNotifier, SigninRecordDao, MatchStatusDao, SigninFee, MatchRewards, UserInfoLoader, PlayerLocation
from poker.entity.dao import userdata

class User(object, ):

    def __init__(self, userId, name):
        pass

    def addItem(self, name, count):
        pass

class UserDatabase(object, ):

    def __init__(self):
        pass

    def addUser(self, userId, name):
        pass

    def findUser(self, userId):
        pass

class PlayerLocationTest(PlayerLocation, ):

    def __init__(self, userdb):
        pass

    def getLocation(self, userId):
        """
        获取用户的location
        """
        pass

    def setLocationForce(self, userId, gameId, roomId, tableId, seatId):
        """
        设置location
        """
        pass

    def clearLocationForce(self, userId, gameId, roomId):
        """
        清除location
        """
        pass

    def redictToLocation(self, userId):
        """
        重定向用户
        """
        pass

class TableControllerTest(TableController, ):

    def __init__(self, userdb):
        pass

    def startTable(self, table):
        """
        让player在具体的游戏中坐到seat上
        """
        pass

    def clearTable(self, table):
        """

        """
        pass

class PlayerNotifierTest(PlayerNotifier, ):

    def notifyMatchCancelled(self, player, inst, reason):
        """
        通知用户比赛由于reason取消了
        """
        pass

    def notifyMatchOver(self, player, group, reason, rankRewards):
        """
        通知用户比赛结束了
        """
        pass

    def notifyMatchIncrNote(self, group, table):
        """
        通知比赛更新
        """
        pass

    def notifyMatchUpdate(self, player):
        """
        通知比赛更新
        """
        pass

    def notifyMatchWait(self, players, group, step=None):
        """
        通知用户等待
        """
        pass

class SigninDatabase(object, ):

    def __init__(self):
        pass

    def set(self, instId, userId, signinTime):
        pass

    def remove(self, instId, userId):
        pass

    def removeAll(self, instId):
        pass

class SigninRecordDaoTest(SigninRecordDao, ):

    def __init__(self, signindb):
        pass

    def load(self, matchId, instId):
        """
        加载所有报名记录
        @return: list((userId, signinTime))
        """
        pass

    def recordSignin(self, matchId, instId, userId, timestamp):
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

        """
        pass

class MatchStatus(object, ):

    def __init__(self):
        pass

class MatchStatusDaoTest(MatchStatusDao, ):

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

class SigninFeeTest(SigninFee, ):

    def __init__(self, userdb):
        pass

    def collectFees(self, inst, userId, fees):
        """
        收取用户报名费
        """
        pass

    def returnFees(self, inst, userId, fees):
        """
        退还报名费
        """
        pass

class MatchRewardsTest(MatchRewards, ):

    def __init__(self, userdb):
        pass

    def sendRewards(self, player, group, rankRewards):
        """

        """
        pass

class UserInfoLoaderTest(UserInfoLoader, ):

    def __init__(self, userdb):
        pass

    def loadUserName(self, userId):
        """
        获取用户名称
        """
        pass

    def loadUserAttrs(self, userId, attrs):
        """

        """
        pass