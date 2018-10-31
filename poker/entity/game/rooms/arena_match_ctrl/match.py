# -*- coding: utf-8 -*-
"""
Created on 2015年12月2日

@author: zhaojiangang
"""
import copy
import collections
from datetime import datetime, timedelta
import random
from sre_compile import isstring
import time
from freetime.core.timer import FTLoopTimer, FTTimer
import freetime.util.log as ftlog
from poker.entity.biz.content import TYContentItem
from poker.entity.biz.exceptions import TYBizConfException
from poker.entity.game import game
from poker.entity.game.rooms import roominfo
from poker.entity.game.rooms.arena_match_ctrl.exceptions import AlreadySigninException, AlreadyInMatchException, NotSigninException, MatchException, SigninFullException, EnterMatchLocationException, SigninNotStartException, MatchExpiredException, MatchSigninException
from poker.entity.game.rooms.big_match_ctrl.const import MatchFinishReason
from poker.entity.game.rooms.roominfo import MatchRoomInfo
from poker.util import strutil, sortedlist
import poker.util.timestamp as pktimestamp

class MatchSeat(object, ):

    def __init__(self, table, seatId):
        pass

    @property
    def table(self):
        pass

    @property
    def tableId(self):
        pass

    @property
    def seatId(self):
        pass

    @property
    def location(self):
        pass

    @property
    def player(self):
        pass

class MatchTable(object, ):

    def __init__(self, gameId, roomId, tableId, seatCount):
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
    def startTime(self):
        pass

    @property
    def seats(self):
        """
        座位列表
        """
        pass

    @property
    def seatCount(self):
        """
        座位数量
        """
        pass

    @property
    def idleSeatCount(self):
        """
        空闲座位的数量
        """
        pass

    @property
    def ccrc(self):
        pass

    @property
    def matchInst(self):
        pass

    def getPlayerList(self):
        """
        获取本桌的所有player
        """
        pass

    def getUserIdList(self):
        """
        获取本桌所有userId
        """
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

    def clear(self):
        """
        清理桌子上的所有玩家
        """
        pass

    def _clearSeat(self, seat):
        pass

    def _makeSeats(self, count):
        pass

class MatchTableManager(object, ):

    def __init__(self, gameId, tableSeatCount):
        pass

    @property
    def tableSeatCount(self):
        pass

    @property
    def roomCount(self):
        pass

    @property
    def allTableCount(self):
        pass

    @property
    def idleTableCount(self):
        pass

    @property
    def busyTableCount(self):
        pass

    def getTableCountPerRoom(self):
        pass

    def addTables(self, roomId, baseId, count):
        pass

    def borrowTables(self, count):
        pass

    def returnTables(self, tables):
        pass

    def findTable(self, roomId, tableId):
        pass

class MatchPlayer(object, ):
    STATE_SIGNIN = 0
    STATE_WAIT = 1
    STATE_PLAYING = 2
    STATE_WINLOSE = 3
    STATE_RISE = 4
    STATE_OVER = 5

    def __init__(self, matchInst, userId, signinTime):
        pass

    @property
    def match(self):
        pass

    @property
    def matchInst(self):
        pass

    @property
    def stage(self):
        pass

    @property
    def state(self):
        pass

    @property
    def table(self):
        pass

    @property
    def seat(self):
        pass

    @property
    def paidFee(self):
        pass

    @property
    def cardCount(self):
        pass

    @property
    def mixId(self):
        pass

class MatchRankLine(object, ):

    def __init__(self):
        pass

    def addInitChip(self, initChip):
        pass

    def calcRankRange(self, score):
        """
        根据score计算名次范围，名次从1开始
        @param score: 积分
        @return: [start, end)
        """
        pass

    def getMinScoreByRank(self, rank):
        pass

    def decodeFromDict(self, d):
        pass

class TipsConfig(object, ):

    def __init__(self):
        pass

    def decodeFromDict(self, conf):
        pass

class MatchStageConf(object, ):

    def __init__(self, index):
        pass

    def decodeFromDict(self, d):
        pass

class MatchRankRewards(object, ):

    def __init__(self):
        pass

    def decodeFromDict(self, d):
        pass

class MatchFee(object, ):

    def __init__(self):
        pass

    def getParam(self, paramName, defVal=None):
        pass

    @property
    def failure(self):
        pass

    def decodeFromDict(self, d):
        pass

    def toDict(self):
        pass

class FeeReward(object, ):

    def __init__(self, fees=[], rankRewardsList=[], roomName='', mixId=None):
        pass

class MatchConf(object, ):

    def __init__(self):
        pass

    @property
    def fees(self):
        pass

    @property
    def rankRewardsList(self):
        pass

    def getFeeReward(self, mixId):
        pass

    def getFees(self, mixId):
        pass

    def getRankRewardsList(self, mixId):
        pass

    def getRoomName(self, mixId):
        pass

    def calcNextTime(self):
        """
        @return: (startTime, endTime)
        """
        pass

    def decodeFromDict(self, d):
        pass

class MatchStage(object, ):

    def __init__(self, matchInst, index):
        pass

    @property
    def match(self):
        pass

    @property
    def matchId(self):
        pass

    @property
    def matchInst(self):
        pass

    @property
    def index(self):
        pass

    @property
    def stageConf(self):
        pass

    @property
    def prevStage(self):
        pass

    @property
    def nextStage(self):
        pass

    def calcRank(self, score):
        pass

    def canRise(self, rank):
        pass

    def calcScore(self, player):
        pass

    def rise(self, player):
        pass

    def intoBus(self, player):
        pass

    def moveRiseIntoBus(self, timeLimit):
        pass

    def removePlayer(self, player):
        pass

class Match(object, ):

    def __init__(self, matchConf):
        pass

    @property
    def gameId(self):
        pass

    @property
    def matchId(self):
        pass

    @property
    def matchConf(self):
        pass

    @property
    def roomId(self):
        pass

    @property
    def tableId(self):
        pass

    @property
    def seatId(self):
        pass

    @property
    def currentInstance(self):
        pass

    def findPlayer(self, userId):
        pass

    def findMatchingPlayer(self, userId):
        pass

    def start(self):
        pass

    def enter(self, userId):
        pass

    def leave(self, userId):
        pass

    def signin(self, userId, signinParams, feeIndex=0):
        pass

    def signout(self, userId):
        pass

    def giveup(self, userId):
        pass

    def winlose(self, tableId, ccrc, seatId, userId, deltaScore, isWin, winloseForTuoguan=0):
        pass

    def reloadConf(self, matchConf):
        pass

    def _createInstance(self):
        pass

    def _onInstanceFinal(self, inst):
        pass

    def _doHeartbeat(self):
        pass

class MatchReviveProcesser(object, ):

    def __init__(self, matchInst):
        pass

    def start(self, userId, delay):
        pass

    def reset(self, userId, delay):
        pass

    def stop(self):
        pass

    def getTimer(self):
        pass

class MatchSigninProcesser(object, ):

    def __init__(self, matchInst):
        pass

    def start(self):
        pass

    def stop(self):
        pass

class MatchWinloseProcesser(object, ):

    def __init__(self, matchInst):
        pass

    def start(self):
        pass

    def stop(self):
        pass

class MatchStagesProcesser(object, ):

    def __init__(self, matchInst):
        pass

    def start(self):
        pass

    def stop(self):
        pass

class MatchWaitProcesser(object, ):

    def __init__(self, matchInst):
        pass

    def start(self):
        pass

    def stop(self):
        pass

class MatchTableTimeoutProcesser(object, ):

    def __init__(self, matchInst):
        pass

    def start(self):
        pass

    def stop(self):
        pass

class MatchWatcher(object, ):

    def __init__(self, matchInst):
        pass

    def start(self):
        pass

    def stop(self):
        pass

    def _doStart(self):
        pass

    def _doPrepareStop(self):
        pass

    def _doStop(self):
        pass

class MatchInstance(object, ):
    STATE_IDLE = 0
    STATE_STARTED = 1
    STATE_PREPARE_STOP = 2
    STATE_STOP = 3
    STATE_FINAL = 4

    def __init__(self, match, instId, matchConf, startDT, stopDT):
        pass

    @property
    def match(self):
        pass

    @property
    def matchId(self):
        pass

    @property
    def instId(self):
        pass

    @property
    def matchConf(self):
        pass

    @property
    def state(self):
        pass

    @property
    def stages(self):
        pass

    def findPlayer(self, userId):
        pass

    def findSigninPlayer(self, userId):
        pass

    def findMatchingPlayer(self, userId):
        pass

    def getSigninCount(self):
        pass

    def canSignin(self):
        pass

    def start(self):
        pass

    def enter(self, userId):
        pass

    def leave(self, userId):
        pass

    def signin(self, userId, signinParams, feeIndex):
        pass

    def signout(self, userId):
        pass

    def giveup(self, player):
        pass

    def checkLifeSafe(self, player):
        pass

    def checkDailySafe(self, player):
        pass

    def checkSafe(self, player):
        """
        @return: 0没有保护，1生涯保护，2每日保护
        """
        pass

    def winlose(self, player, deltaScore, isWin, isKill=False):
        pass

    def buildRoomInfo(self):
        pass

    def _doStart(self):
        pass

    def _doPrepareStop(self):
        pass

    def _doStop(self):
        pass

    def _doFinal(self):
        pass

    def _ensureCanSignin(self, userId):
        pass

    def _collectFee(self, player, fees, feeIndex):
        pass

    def _returnFee(self, player):
        pass

    def _fillPlayer(self, player):
        pass

    def _addWaitRevivePlayer(self, player):
        pass

    def _resetReviveTimer(self):
        """
        重置复活定时器
        """
        pass

    def _processRevive(self):
        """
        处理超时玩家
        """
        pass

    def doUserRevive(self, player, isRevive):
        """

        """
        pass

    def _processSignin(self):
        """
        处理报名的玩家
        """
        pass

    def _processWinlose(self):
        """
        处理刚玩完一局的玩家
        """
        pass

    def _processWait(self):
        pass

    def _processTimeoutTables(self):
        pass

    def _processStages(self):
        """
        处理所有阶段
        """
        pass

    def _processStage(self, stage):
        """
        处理阶段班车
        """
        pass

    def _canRise(self, player):
        pass

    def _outPlayer(self, player):
        pass

    def _risePlayer(self, player):
        pass

    def _playerOverMatch(self, player, reason=0):
        pass

    def _findRankRewards(self, rankRewardsList, rank):
        pass

    def _initTables(self):
        pass

    def _borrowTable(self):
        pass

    def _returnTable(self, table):
        pass

    @classmethod
    def calcRankInPlayers(cls, player, players):
        pass

    def _calcTableDisplayRank(self, i, players):
        pass

    def _startTable(self, players):
        pass

    def _clearTable(self, table):
        pass

    def _releaseTables(self):
        pass

    def _clearAndReleaseTable(self, table):
        pass

    def _createStages(self):
        pass

    def _nextStage(self, stage):
        pass

    def _isFirstStage(self, stage):
        pass

    def _isSecondStage(self, stage):
        pass

    def _isLastStage(self, stage):
        pass

    def _getPlayersFromPrevStages(self, stage, count):
        pass

    def _addToWinloseList(self, playerList):
        pass

    def _sortTableRank(self, playerList):
        pass

    def _sortPlayerSnake(self, players):
        pass

    def _isAllPlayerWinlose(self, table):
        pass

    def _lockPlayer(self, player):
        pass

    def _unlockPlayer(self, player):
        pass