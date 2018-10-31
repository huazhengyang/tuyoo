# -*- coding: utf-8 -*-
"""
Created on 2016年1月25日

@author: zhaojiangang
"""
from datetime import datetime
import time
from freetime.core.lock import locked
from poker.entity.biz import bireport
from poker.entity.biz.content import TYContentItem
from poker.entity.configure import gdata
from poker.entity.game.game import TYGame
from poker.entity.game.rooms import roominfo
from poker.entity.game.rooms.group_match_ctrl.const import FeesType, MatchFinishReason, StageType, WaitReason, GroupingType
from poker.entity.game.rooms.group_match_ctrl.events import MatchStartSigninEvent, MatchingStageStartEvent, MatchingStartEvent, MatchingFinishEvent, MatchingStageFinishEvent, MatchCancelEvent
from poker.entity.game.rooms.group_match_ctrl.exceptions import BadStateException, SigninStoppedException, SigninNotStartException, AlreadySigninException, SigninFullException, MatchStoppedException, AlreadyInMatchException, SigninException
from poker.entity.game.rooms.group_match_ctrl.interface import MatchStatus
from poker.entity.game.rooms.group_match_ctrl.models import Signer, Player, Riser
from poker.entity.game.rooms.group_match_ctrl.utils import Lockable, Logger, HeartbeatAble, PlayerScoreCalc, PlayerQueuing, PlayerSort, PlayerGrouping, GroupNameGenerator, report_bi_game_event
from poker.entity.game.rooms.roominfo import MatchRoomInfo
from poker.util import strutil
import poker.util.timestamp as pktimestamp
from freetime.core.timer import FTLoopTimer

class MatchInst(Lockable, ):
    """
    比赛实例，用于接受报名，退赛，运行在赛区中
    """
    ST_IDLE = 0
    ST_LOAD = 1
    ST_SIGNIN = 2
    ST_PREPARE = 3
    ST_STARTING = 4
    ST_START = 5
    ST_FINAL = 6

    def __init__(self, area, instId, startTime, needLoad):
        pass

    @property
    def matchId(self):
        pass

    @property
    def roomId(self):
        pass

    @property
    def state(self):
        pass

    @property
    def matchConf(self):
        pass

    @property
    def signerMap(self):
        pass

    @property
    def signerCount(self):
        pass

    def findSigner(self, userId):
        pass

    def getTotalSignerCount(self):
        pass

    def buildStatus(self):
        pass

    @locked
    def load(self):
        pass

    @locked
    def cancel(self, reason):
        pass

    @locked
    def cancelSigners(self, reason, userIds):
        pass

    @locked
    def moveTo(self, toInstId, userIds):
        pass

    @locked
    def startSignin(self):
        pass

    @locked
    def prepare(self):
        pass

    @locked
    def start(self):
        pass

    def _fillSigner(self, signer):
        pass

    def signin(self, userId, feeIndex):
        pass

    def signout(self, signer):
        pass

    def enter(self, signer):
        pass

    def leave(self, signer):
        pass

    def _doLoad(self):
        pass

    def _doMoveTo(self, toInstId, userIds):
        pass

    def _doCancel(self, reason):
        pass

    def _doStartSignin(self):
        pass

    def _doPrepare(self):
        pass

    def _doStart(self):
        pass

    def _lockSigners(self):
        pass

    def _lockSigner(self, signer):
        pass

    def _unlockSigner(self, signer, returnFees=False):
        pass

    def _prelockSigners(self, signers):
        pass

    def _kickoutSigners(self, signers):
        pass

    def _doKickoutSigners(self, signers):
        pass

    def _kickoutSigner(self, signer):
        pass

    def _cancelSigner(self, signer, reason):
        pass

    def _ensureCanSignin(self, userId):
        pass

class MatchGroup(HeartbeatAble, ):
    ST_IDLE = 0
    ST_SETUP = 1
    ST_START = 2
    ST_FINISHING = 3
    ST_FINISH = 4
    ST_FINALING = 5
    ST_FINAL = 6

    def __init__(self, area, instId, matchingId, groupId, groupName, stageIndex, isGrouping, totalPlayerCount, startStageIndex=0):
        pass

    @property
    def startStageIndex(self):
        pass

    @property
    def matchId(self):
        pass

    @property
    def matchConf(self):
        pass

    @property
    def state(self):
        pass

    @property
    def playerCount(self):
        pass

    @property
    def finishReason(self):
        pass

    @property
    def playerMap(self):
        pass

    @property
    def rankList(self):
        pass

    @property
    def ranktops(self):
        pass

    @property
    def startPlayerCount(self):
        pass

    @property
    def assLoseScore(self):
        pass

    @property
    def loseBetScore(self):
        pass

    @property
    def startTime(self):
        pass

    @property
    def lastActiveTime(self):
        pass

    def findPlayer(self, userId):
        pass

    def addPlayer(self, player):
        pass

    def buildStatus(self):
        pass

    def calcNeedTableCount(self):
        pass

    def calcUncompleteTableCount(self):
        pass

    def calcTotalUncompleteTableCount(self):
        pass

    def calcRemTimes(self, timestamp=None):
        pass

    def calcTotalRemTimes(self, timestamp):
        pass

    def start(self):
        pass

    def kill(self, reason):
        pass

    def final(self):
        pass

    def giveup(self, player):
        """
        玩家放弃比赛
        """
        pass

    def winlose(self, player, deltaScore, isWin, isKill=False):
        pass

    def _doHeartbeatImpl(self):
        pass

    def _calcMaxPlayTime(self):
        pass

    def _doStart(self):
        pass

    def _doFinish(self, reason=MatchFinishReason.FINISH):
        pass

    def _doKill(self, reason):
        pass

    def _doFinal(self):
        pass

    def _releaseResource(self):
        pass

    def _isGroupFinished(self):
        pass

    def _processTimeoutTables(self):
        pass

    def _processWinlosePlayers(self):
        pass

    def _processWinlosePlayersAss(self, winlosePlayerList):
        pass

    def _processWinlosePlayersDieout(self, winlosePlayerList):
        pass

    def _processGiveupPlayers(self):
        pass

    def _processWaitPlayers(self):
        pass

    def _initPlayerDatas(self):
        pass

    def _initWaitPlayerList(self):
        pass

    def _addWinlosePlayers(self, players):
        pass

    def _addWaitPlayer(self, player):
        pass

    def _addGiveupPlayer(self, player):
        pass

    def _playerFinishCardCount(self, player):
        pass

    def _sortTableRank(self, tablePlayerList):
        pass

    def _sortMatchRanks(self):
        pass

    def _clearAndReleaseTable(self, table):
        pass

    def _clearTable(self, table):
        pass

    def _borrowTable(self):
        pass

    def _releaseTable(self, table):
        pass

    def _reclaimTables(self):
        pass

    def _calcMaxProcessPlayerCount(self):
        pass

    def _checkGrowLoseBetScore(self):
        pass

    def _growLoseBetScore(self, chipGrow):
        pass

    def _calcASSLoseScore(self):
        pass

    def _checkWaitFinishOrFinishStageASS(self):
        pass

    def _outPlayer(self, player, reason=MatchFinishReason.USER_LOSER):
        pass

    def _doPlayerMatchOver(self, player, reason):
        pass

    def _getRewards(self, player):
        pass

class MatchInstStatus(object, ):

    def __init__(self, instId, state, signerCount):
        pass

    def toDict(self):
        pass

    @classmethod
    def fromDict(cls, d):
        pass

class MatchGroupStatus(object, ):

    def __init__(self, groupId, matchingId, state, uncompleteTableCount, remTimes, lastActiveTime, playerCount):
        pass

    def toDict(self):
        pass

    @classmethod
    def fromDict(cls, d):
        pass

class MatchAreaStatus(object, ):

    def __init__(self):
        pass

    def toDict(self):
        pass

    @classmethod
    def fromDict(cls, d):
        pass

class MatchMasterStatus(object, ):

    def __init__(self):
        pass

    def toDict(self):
        pass

    @classmethod
    def fromDict(cls, d):
        pass

class MatchMasterStub(object, ):
    """
    赛事在赛区控制对象，运行于赛区中
    """

    def __init__(self, roomId):
        pass

    def areaHeartbeat(self, area):
        """
        area心跳，运行
        """
        pass

    def areaGroupStart(self, area, group):
        """
        向主赛区汇报
        """
        pass

    def areaGroupFinish(self, area, group):
        """
        向主赛区汇报
        """
        pass

    def areaInstStarted(self, area, inst):
        """
        向主赛区汇报比赛实例启动成功，汇报报名用户列表
        """
        pass

    def onMasterHeartbeat(self, masterStatus):
        """
        主赛区心跳回调
        """
        pass

class MatchArea(HeartbeatAble, ):
    """
    赛区是一个分组管理器
    """
    ST_IDLE = 0
    ST_START = 1
    HEARTBEAT_TO_MASTER_INTERVAL = 5

    def __init__(self, room, matchId, matchConf, masterStub):
        pass

    @property
    def tableSeatCount(self):
        pass

    @property
    def gameId(self):
        pass

    @property
    def roomId(self):
        pass

    @property
    def curInst(self):
        pass

    @property
    def state(self):
        pass

    @property
    def tableId(self):
        pass

    @property
    def seatId(self):
        pass

    @property
    def matchName(self):
        pass

    def start(self):
        pass

    def findSigner(self, userId):
        pass

    def findPlayer(self, userId):
        pass

    def findGroup(self, groupId):
        pass

    @classmethod
    def parseStageId(cls, matchingId, groupId):
        pass

    def calcTotalUncompleteTableCount(self, group):
        pass

    def calcTotalRemTimes(self, group):
        pass

    def getTotalSignerCount(self, inst):
        pass

    def buildStatus(self):
        pass

    def signin(self, userId, signinParams, feeIndex=0):
        """
        玩家报名
        """
        pass

    def signout(self, userId):
        """
        玩家退赛，转到主赛区处理
        """
        pass

    def giveup(self, userId):
        """
        玩家放弃比赛
        """
        pass

    def enter(self, userId):
        """
        进入报名页
        """
        pass

    def leave(self, userId):
        """
        离开报名页
        """
        pass

    def winlose(self, tableId, ccrc, seatId, userId, deltaScore, isWin, tuoguanCountStatus=0):
        """
        玩家一局结束, tuoguanCountStatus 0: 不处理， 1：player.winloseForTuoguanCount + 1 2: 达到临界值，踢出用户
        """
        pass

    def createInst(self, instId, startTime, needLoad):
        pass

    def cancelInst(self, instId, reason):
        pass

    def createGroup(self, instId, matchingId, groupId, groupName, stageIndex, isGrouping, totalPlayerCount, startStageIndex=0):
        """
        创建分组
        """
        pass

    def onInstStarted(self, inst):
        pass

    def onGroupFinish(self, group):
        pass

    def _processGroups(self):
        pass

    def _doHeartbeatImpl(self):
        pass

class MatchInstStub(object, ):
    """
    比赛实例存根，运行于主控进程
    """

    def __init__(self, areaStub, instId, startTime, needLoad):
        pass

    @property
    def roomId(self):
        pass

    @property
    def master(self):
        pass

    @property
    def state(self):
        pass

    @property
    def signerMap(self):
        pass

    @property
    def signerCount(self):
        pass

    @property
    def finishReason(self):
        pass

    def startSignin(self):
        """
        开始报名
        """
        pass

    def prepare(self):
        """
        开始准备开赛
        """
        pass

    def cancel(self, reason):
        """
        取消比赛
        """
        pass

    def cancelSigners(self, reason, signers):
        """
        取消比赛
        """
        pass

    def moveTo(self, toInstId, signers):
        pass

    def start(self):
        """
        开始比赛
        """
        pass

    def onSignin(self, signers):
        """
        主对象汇报报名列表
        """
        pass

    def onStart(self):
        """
        赛区中的实例启动完成
        """
        pass

    def _doCancelSigners(self, reason, userIds):
        pass

    def _doMoveTo(self, toInstId, userIds):
        pass

    def _doStartSignin(self):
        pass

    def _doPrepare(self):
        pass

    def _doCancel(self):
        pass

    def _doStart(self):
        pass

class MatchInstStubLocal(MatchInstStub, ):

    def __init__(self, areaStub, instId, startTime, needLoad, inst):
        pass

    def _doCancelSigners(self, reason, userIds):
        pass

    def _doMoveTo(self, toInstId, userIds):
        pass

    def _doStartSignin(self):
        pass

    def _doPrepare(self):
        pass

    def _doCancel(self):
        pass

    def _doStart(self):
        pass

class MatchGroupStub(HeartbeatAble, ):
    """
    比赛分组存根对象，运行于主控进程
    """
    HEARTBEAT_INTERVAL = 1
    ACTIVE_TIME_COUNT = 36

    def __init__(self, areaStub, stage, groupId, groupName, playerList, isGrouping, totalPlayerCount, startStageIndex=0):
        pass

    @property
    def startStageIndex(self):
        pass

    @property
    def instId(self):
        pass

    @property
    def roomId(self):
        pass

    @property
    def master(self):
        pass

    @property
    def playerMap(self):
        pass

    @property
    def playerCount(self):
        pass

    @property
    def matchId(self):
        pass

    @property
    def matchingId(self):
        pass

    @property
    def stageIndex(self):
        pass

    @property
    def risePlayerSet(self):
        pass

    @property
    def finishReason(self):
        pass

    @property
    def state(self):
        pass

    def buildStatus(self):
        pass

    def start(self):
        pass

    def kill(self, reason):
        pass

    def final(self):
        pass

    def onRise(self, risers):
        pass

    def onFinish(self, reason):
        pass

    def onStart(self):
        pass

    def onHeartbeat(self, status):
        pass

    def _doStart(self):
        pass

    def _doKill(self, reason):
        pass

    def _doFinal(self):
        pass

    def _doFinish(self, reason):
        pass

    def _doHeartbeatImpl(self):
        pass

    def _isActiveTimeout(self):
        pass

    def _doStartGroup(self):
        pass

    def _doKillGroup(self):
        pass

    def _doFinalGroup(self):
        pass

class MatchGroupStubLocal(MatchGroupStub, ):
    """
    比赛分组存根对象，运行于主控进程
    """

    def __init__(self, areaStub, stage, groupId, groupName, playerList, isGrouping, totalPlayerCount, area, startStageIndex=0):
        pass

    def _doStartGroup(self):
        pass

    def _doKillGroup(self):
        pass

    def _doFinalGroup(self):
        pass

class GroupCreateInfo(object, ):

    def __init__(self, stage, groupId, groupName, playerList):
        pass

class MatchStage(object, ):
    """
    比赛阶段，运行于中控进程
    """
    ST_IDLE = 0
    ST_START = 1
    ST_FINISH = 2
    ST_FINAL = 3
    GROUP_NAME_PREFIX = [chr(i) for i in range(ord('A'), (ord('Z') + 1))]

    def __init__(self, matching, stageConf):
        pass

    @property
    def matchId(self):
        pass

    @property
    def instId(self):
        pass

    @property
    def matchingId(self):
        pass

    @property
    def master(self):
        pass

    @property
    def matchConf(self):
        pass

    @property
    def state(self):
        pass

    def findGroupStub(self, groupId):
        pass

    def start(self, playerList):
        pass

    def final(self):
        pass

    def getAllRisePlayerList(self):
        pass

    @classmethod
    def groupingPlayerList(self, playerList, stageConf, tableSeatCount):
        pass

    def _processStage(self):
        pass

    def _isAllGroupStubFinish(self):
        pass

class Matching(HeartbeatAble, ):
    """
    一场比赛，运行于主控进程
    """
    ST_IDLE = 0
    ST_START = 1
    ST_FINISH = 2
    HEARTBEAT_INTERVAL = 2

    def __init__(self, master, instId, matchingId):
        pass

    @property
    def matchId(self):
        pass

    @property
    def matchConf(self):
        pass

    @property
    def state(self):
        pass

    @property
    def startPlayerCount(self):
        pass

    @property
    def startStageIndex(self):
        pass

    def findGroupStub(self, groupId):
        pass

    def findFirstStage(self, signerCount):
        pass

    def start(self, signers):
        pass

    def _doHeartbeatImpl(self):
        pass

    def _startNextStage(self):
        pass

    def _getNextStage(self, stage):
        pass

    def _createStages(self, stageConfs):
        pass

    def _signersToPlayerList(self, signers):
        pass

    def _doFinish(self):
        pass

class MatchAreaStub(HeartbeatAble, ):
    """
    赛区存根对象，用于控制分赛区，运行于主控进程
    """
    ST_OFFLINE = 0
    ST_ONLINE = 1
    ST_TIMEOUT = 2
    HEARTBEAT_TIMEOUT_TIMES = 3

    def __init__(self, master, roomId):
        pass

    @property
    def matchId(self):
        pass

    @property
    def matchConf(self):
        pass

    @property
    def curInstStub(self):
        pass

    @property
    def groupStubMap(self):
        pass

    def findInstStub(self, instId):
        pass

    def findGroupStub(self, groupId):
        pass

    def isOnline(self):
        """
        是否上线了
        """
        pass

    def buildStatus(self):
        pass

    def start(self):
        pass

    def createInst(self, instId, startTime, needLoad):
        """
        让分赛区创建比赛实例
        """
        pass

    def createGroup(self, stage, groupId, groupName, playerList, isGrouping, totalPlayerCount, startStageIndex=0):
        pass

    def cancelInst(self, instId, reason):
        """
        分赛区取消比赛实例
        """
        pass

    def masterHeartbeat(self, master):
        """
        向分赛区发送，主赛区心跳
        """
        pass

    def onAreaHeartbeat(self, areaStatus):
        """
        area心跳回调
        """
        pass

    def _doHeartbeatImpl(self):
        pass

    def _processGroupStubs(self):
        pass

    def _createInstStubImpl(self, instId, startTime, needLoad):
        pass

    def _createGroupStubImpl(self, stage, groupId, groupName, playerList, isGrouping, totalPlayerCount, startStageIndex):
        pass

class MatchAreaStubLocal(MatchAreaStub, ):

    def __init__(self, master, area):
        pass

    def masterHeartbeat(self, master):
        """
        向分赛区发送，主赛区心跳
        """
        pass

    def cancelInst(self, instId, reason):
        """
        分赛区取消比赛实例
        """
        pass

    def _createInstStubImpl(self, instId, startTime, needLoad):
        pass

    def _createGroupStubImpl(self, stage, groupId, groupName, playerList, isGrouping, totalPlayerCount, startStageIndex=0):
        pass

class MatchMasterStubLocal(MatchMasterStub, ):
    """
    赛事在赛区控制对象，运行于赛区中
    """

    def __init__(self, master):
        pass

    def areaHeartbeat(self, area):
        """
        area心跳，运行
        """
        pass

    def areaGroupStart(self, area, group):
        """
        向主赛区汇报
        """
        pass

    def areaGroupFinish(self, area, group):
        """
        向主赛区汇报
        """
        pass

    def areaInstStarted(self, area, inst):
        """
        向主赛区汇报比赛实例启动成功，汇报报名用户列表
        """
        pass

class MatchInstCtrl(HeartbeatAble, ):
    STARTING_TIMEOUT = 90

    def __init__(self, master, status, needLoad):
        pass

    @property
    def matchId(self):
        pass

    @property
    def state(self):
        pass

    @property
    def matchConf(self):
        pass

    @property
    def instId(self):
        pass

    @property
    def startTime(self):
        pass

    def start(self):
        pass

    def final(self):
        pass

    def _doHeartbeat(self):
        pass

    def _collectSignerMap(self):
        pass

    def _doLoad(self):
        pass

    def _cancel(self, reason):
        pass

    def _moveToNext(self, nextInstId, signers):
        pass

    def _cancelSigners(self, reason, signers):
        pass

    def _doStartSignin(self):
        pass

    def _doPrepare(self):
        pass

    def _doStart(self):
        pass

    def _doOutSigners(self):
        pass

    def _doFinal(self):
        pass

    def _isAllStarted(self):
        pass

    def _isStartingTimeout(self):
        pass

    def _cancelNotStartInst(self):
        pass

    def _calcTotalSignerCount(self):
        pass

class MatchMaster(HeartbeatAble, ):
    ST_IDLE = 0
    ST_START = 1
    ST_ALL_AREA_ONLINE = 2
    ST_LOAD = 3
    HEARTBEAT_TO_AREA_INTERVAL = 5

    def __init__(self, room, matchId, matchConf):
        pass

    @property
    def areaCount(self):
        pass

    @property
    def areaStubMap(self):
        pass

    @property
    def areaStubList(self):
        pass

    @property
    def instCtrl(self):
        pass

    @property
    def gameId(self):
        pass

    @property
    def roomId(self):
        pass

    @property
    def matchName(self):
        pass

    def findMatching(self, matchingId):
        pass

    def findAreaStub(self, roomId):
        pass

    def findInstStub(self, roomId, instId):
        pass

    def addAreaStub(self, areaStub):
        pass

    def findGroupStubWithMatchingId(self, matchingId, groupId):
        pass

    def findGroupStub(self, groupId):
        pass

    def buildStatus(self):
        pass

    def start(self):
        pass

    def createGroupStubs(self, stage, groupCreateInfos, isGrouping, startStageIndex=0):
        pass

    def _doHeartbeatImpl(self):
        pass

    def _processMatching(self):
        pass

    def _heartbeatToAllArea(self):
        pass

    def _isAllAreaOnline(self):
        pass

    def _calcMatchingPlayerCount(self):
        pass

    def _buildRoomInfo(self):
        pass

    def _doLoad(self):
        pass

    def _cancelInst(self, instId, reason):
        pass

    def _startMatching(self, instCtrl, num, signers):
        pass

    def _setupNextInst(self, instCtrl, signers):
        pass