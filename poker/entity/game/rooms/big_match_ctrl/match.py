# -*- coding: utf-8 -*-
"""
Created on 2014年9月23日

@author: zjgzzz@126.com
"""
from datetime import datetime
import functools
import time
from freetime.core.timer import FTTimer, FTLoopTimer
import freetime.util.log as ftlog
from poker.entity.biz.content import TYContentItem
from poker.entity.configure import gdata
from poker.entity.dao import sessiondata, onlinedata
from poker.entity.events.tyevent import MatchPlayerSigninEvent, MatchPlayerSignoutEvent, MatchPlayerOverEvent
import poker.entity.events.tyeventbus as pkeventbus
from poker.entity.game.rooms import roominfo
from poker.entity.game.rooms.big_match_ctrl.const import MatchFinishReason, FeesType, StageType, GroupingType, WaitReason
from poker.entity.game.rooms.big_match_ctrl.exceptions import MatchExpiredException, AlreadySigninException, MatchAlreadyStartedException, SigninStoppedException, SigninNotStartException, AlreadyInMatchException, SigninFullException
from poker.entity.game.rooms.big_match_ctrl.interfaces import MatchStatus
from poker.entity.game.rooms.big_match_ctrl.models import Table, Player
from poker.entity.game.rooms.big_match_ctrl.utils import PlayerSort, PlayerGrouping, PlayerChipCalc, PlayerQueuing, Utils
from poker.entity.game.rooms.roominfo import MatchRoomInfo
from poker.util import strutil

class TableManager(object, ):

    def __init__(self, gameId, tableSeatCount):
        pass

    @property
    def tableSeatCount(self):
        pass

    def getRoomCount(self):
        pass

    def getAllTableCount(self):
        pass

    def getTableCountPerRoom(self):
        pass

    def addTables(self, roomId, baseId, count):
        pass

    def borrowTables(self, count):
        pass

    def returnTables(self, tables):
        pass

    def idleTableCount(self):
        pass

    def usedTableCount(self):
        pass

    def findTable(self, roomId, tableId):
        pass

class MatchStageFactory(object, ):

    def newMatchStage(self, matching, conf, index):
        pass

class MatchGroupFactory(object, ):

    def newMatchGroup(self, groupId, groupName, playerList):
        pass

class Match(object, ):
    """
    赛事
    """
    STATE_IDLE = 0
    STATE_LOADING = 1
    STATE_LOADED = 2

    def __init__(self, conf):
        pass

    @property
    def gameId(self):
        pass

    @property
    def matchId(self):
        pass

    @property
    def conf(self):
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

    @property
    def tableSeatCount(self):
        pass

    @property
    def tick(self):
        pass

    def getMatchingPlayerCount(self):
        pass

    def signin(self, userId, signinParams, feeIndex=0):
        """
        比赛报名
        """
        pass

    def signout(self, userId):
        """
        退赛
        """
        pass

    def giveup(self, userId):
        pass

    def winlose(self, tableId, ccrc, seatId, userId, deltaChip, isWin):
        pass

    def enter(self, userId):
        pass

    def leave(self, userId):
        pass

    def findPlayer(self, userId):
        pass

    def findMatchingPlayer(self, userId):
        """
        查找正在比赛的玩家
        """
        pass

    def setHeartBeatInterval(self, interval):
        pass

    def doHeartBeat(self):
        pass

    def load(self):
        pass

    def fillPlayer(self, player):
        pass

    def _calcMatchingPlayerCount(self):
        pass

    def _calcTotalSignerCount(self):
        pass

    def _buildRoomInfo(self):
        pass

    def _doRoomInfoUpdate(self):
        pass

    def _load(self, matchStatus, timestamp):
        pass

    def _createInstance(self, matchStatus, timestamp):
        pass

    def _cancelMatch(self, matchStatus):
        pass

    def setupNextInstance(self, timestamp=None):
        pass

    def _finishInstance(self, inst):
        pass

class SigninState(object, ):
    STATE_IDLE = 0
    STATE_SIGNIN = 1
    STATE_STOP = 2

class MatchInstance(object, ):
    """
    一个赛事实例
    """
    STATE_IDLE = 0
    STATE_SIGNIN = 1
    STATE_PREPARE = 2
    STATE_STARTING = 4
    STATE_STARTED = 5
    STATE_FINISH = 6
    STATE_FINAL = 7

    def __init__(self, match, instId, conf):
        pass

    @property
    def instId(self):
        pass

    @property
    def matchId(self):
        pass

    @property
    def match(self):
        pass

    @property
    def conf(self):
        pass

    @property
    def state(self):
        pass

    @property
    def startTime(self):
        pass

    @property
    def startTimeStr(self):
        pass

    @property
    def playerMap(self):
        pass

    def getMatchingPlayerCount(self):
        pass

    def signin(self, userId, feeIndex, signinParams):
        pass

    def signout(self, userId):
        pass

    def enter(self, userId):
        pass

    def leave(self, userId):
        pass

    def findMatchingPlayer(self, userId):
        """
        查找所有的
        """
        pass

    def doHeartBeat(self):
        pass

    def _moveTo(self, players, toInst):
        pass

    def _doStart(self):
        pass

    def _newMatching(self):
        pass

    def _finishMatching(self, matching):
        pass

    def _doStartAbort(self, playerList, reason):
        pass

    def _doStartSignin(self):
        pass

    def _doPrepare(self):
        pass

    def _doStartAbortPlayers(self, playerList, reason):
        pass

    def _setEnterLoc(self, userId):
        pass

    def _setLeaveLoc(self, userId):
        pass

    def _prelockPlayers(self, playerList):
        pass

    def _lockPlayers(self, playerList):
        """

        """
        pass

    def _lockPlayer(self, player):
        pass

    def _unlockPlayer(self, player):
        pass

    def _unlockPlayers(self, playerList):
        pass

    def _collectFees(self, userId):
        pass

    def _returnFees(self, userId):
        pass

    def _isPlayersEnough(self, playerCount):
        pass

    def _addPlayers(self, playerList):
        pass

    def _ensureCanSignin(self, userId):
        pass

    def _groupingPlayers(self, playerList):
        pass

class MatchStage(object, ):
    STATE_IDLE = 0
    STATE_SETUP = 1
    STATE_STARTING = 2
    STATE_STARTED = 3
    STATE_FINISHED = 4

    def __init__(self, matching, conf, index):
        pass

    @property
    def index(self):
        pass

    @property
    def name(self):
        pass

    @property
    def matching(self):
        pass

    @property
    def matchingId(self):
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
    def instId(self):
        pass

    @property
    def conf(self):
        pass

    @property
    def next(self):
        pass

    @property
    def stageId(self):
        pass

    @property
    def playerCountPerGroup(self):
        pass

    @property
    def totalRisePlayerCount(self):
        pass

    def getLoseBetChip(self):
        pass

    def getAssLoseChip(self):
        pass

    def getGroupCount(self):
        pass

    def getMatchingPlayerCount(self):
        pass

    def hasNextStage(self):
        pass

    def calcNeedTableCount(self):
        pass

    def findMatchingPlayer(self, userId):
        """
        查找所有的
        """
        pass

    def setupStage(self, groups):
        pass

    def _startStage(self):
        pass

    def winlose(self, group, player, deltaChip, isWin, isKill=False):
        pass

    def giveup(self, group, player):
        pass

    def doHeartBeat(self):
        pass

    def _calcLastTablePlayTime(self, group, table=None):
        pass

    def calcRemTimes(self, group):
        pass

    def calcUncompleteTableCount(self, group):
        pass

    def _calcUncompleteTableCount(self, group):
        pass

    def _calcRemTimesForGroup(self, group, timestamp):
        pass

    def _releaseTable(self, group, table):
        pass

    def _finishGroup(self, group):
        pass

    def _finishStage(self):
        pass

    def _killStage(self, reason):
        pass

    def _isGroupFinished(self, group):
        pass

    def _processGroup(self, group, maxCount=2000):
        pass

    def _processTimeoutTables(self, group):
        pass

    def _sortMatchRanks(self, group):
        pass

    def _initPlayerDatas(self, group):
        pass

    def _initWaitPlayerList(self, group):
        pass

    def _processWaitUserList(self, group, maxCount=2000):
        pass

    def _processGiveupUsers(self, group):
        pass

    def _processWinloseUserList(self, group):
        pass

    def _checkWaitFinishOrFinishStageASS(self, group):
        pass

    def _playerFinishCardCount(self, group, player):
        pass

    def _processWinlosePlayerListASS(self, group, winLosePlayerList):
        pass

    def _processWinlosePlayerListDieout(self, group, winLosePlayerList):
        pass

    def _outPlayer(self, group, player):
        pass

    def _appendWaitPlayerList(self, group, player):
        pass

    def _sortTableRank(self, tablePlayers):
        pass

    def _clearTable(self, table, changeLoc=True):
        pass

    def _checkGrowLoseBetChip(self):
        pass

    def _growLoseBetChip(self, chipGrow):
        pass

    def _calcASSLoseChip(self):
        pass

    def _doPlayerMatchOver(self, group, player, reason):
        pass

    def _getRewards(self, player):
        pass

class Matching(object, ):
    """
    一个赛事的一场比赛
    """
    STATE_IDLE = 0
    STATE_STARTING = 1
    STATE_STARTED = 2
    STATE_FINISHED = 3
    STATE_FINAL = 4

    def __init__(self, matchInst, matchingId, stageConfs):
        pass

    @property
    def matchingId(self):
        pass

    @property
    def match(self):
        pass

    @property
    def matchInst(self):
        pass

    @property
    def stageCount(self):
        pass

    @property
    def startPlayerCount(self):
        pass

    def getStage(self, index):
        pass

    def getMatchingPlayerCount(self):
        pass

    def findMatchingPlayer(self, userId):
        """
        查找所有的
        """
        pass

    def findFirstStage(self, playerCount):
        pass

    def start(self, playerList):
        pass

    def borrowTable(self):
        pass

    def returnTable(self, table):
        pass

    def doHeartBeat(self):
        pass

    def startNextStage(self):
        pass

    def _reclaimTables(self):
        pass

    def _killMatching(self):
        pass

    def _finishMatching(self):
        pass

    def _doFinal(self):
        pass

    def _lockTables(self, playerList):
        pass

    def _releaseTables(self):
        pass

    def _groupingPlayers(self, playerList, stage):
        pass

    def _createStages(self, stageConfs):
        pass

class MatchGroup(object, ):
    """
    分组, 每个组会打N个阶段的比赛
    """

    def __init__(self, groupId, groupName, playerList):
        pass

    @property
    def groupId(self):
        pass

    @property
    def groupName(self):
        pass

    @property
    def stage(self):
        pass

    @property
    def match(self):
        pass

    @property
    def matchInst(self):
        pass

    @property
    def startTime(self):
        pass

    @property
    def rankList(self):
        pass

    @property
    def ranktops(self):
        pass

    @property
    def allPlayerCount(self):
        pass

    @property
    def busyTableCount(self):
        pass

    def getStartPlayerCount(self):
        pass

    def findMatchingPlayer(self, userId):
        """
        查找所有的
        """
        pass

    def addGiveupPlayer(self, player):
        pass

    def addWinlosePlayerList(self, playerList):
        pass

    def nextTickWinlosePlayerList(self):
        pass

    def _initPlayerMap(self, playerList):
        pass