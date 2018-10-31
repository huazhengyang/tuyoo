# -*- coding: utf-8 -*-
"""
Created on 2016年7月13日

@author: zhaojiangang
"""
import time
from poker.entity.biz.content import TYContentItem
from poker.entity.game.rooms import roominfo
from poker.entity.game.rooms.erdayi_match_ctrl.const import FeeType, MatchFinishReason, GroupingType
from poker.entity.game.rooms.erdayi_match_ctrl.exceptions import SigninStoppedException, AlreadySigninException, SigninNotStartException, SigninFullException, BadStateException, MatchStoppedException, AleadyInMatchException, SigninException
from poker.entity.game.rooms.erdayi_match_ctrl.interface import SigninRecord, MatchStatus
from poker.entity.game.rooms.erdayi_match_ctrl.models import Signer, GroupNameGenerator, PlayerGrouping
from poker.entity.game.rooms.erdayi_match_ctrl.utils import HeartbeatAble, Logger
from poker.entity.game.rooms.roominfo import MatchRoomInfo
from poker.util import strutil
import poker.util.timestamp as pktimestamp
from datetime import datetime

class MatchInst(HeartbeatAble, ):
    ST_IDLE = 0
    ST_SIGNIN = 1
    ST_PREPARE = 2
    ST_STARTING = 3
    ST_STARTED = 4
    ST_FINAL = 5

    def __init__(self, area, instId, startTime, needLoad):
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
    def state(self):
        pass

    @property
    def needLoad(self):
        pass

    @property
    def signerCount(self):
        pass

    @property
    def signerMap(self):
        pass

    @property
    def master(self):
        pass

    def findSigner(self, userId):
        pass

    def getTotalSignerCount(self):
        pass

    def startSignin(self):
        """
        开始报名
        """
        pass

    def prepare(self):
        """
        准备阶段开始
        """
        pass

    def cancel(self, reason):
        """
        比赛取消
        """
        pass

    def start(self):
        """
        比赛开始
        """
        pass

    def final(self):
        """
        结束
        """
        pass

    def _doStartSignin(self):
        pass

    def _doPrepare(self):
        pass

    def _doCancel(self, reason):
        pass

    def _doStart(self):
        pass

    def _doFinal(self):
        pass

    def _doStartSigninImpl(self):
        pass

    def _doPrepareImpl(self):
        pass

    def _doCancelImpl(self, reason):
        pass

    def _doStartImpl(self):
        pass

    def _doFinalImpl(self):
        pass

class MatchInstLocal(MatchInst, ):

    def __init__(self, area, instId, startTime, needLoad):
        pass

    def addInitSigners(self, signers):
        pass

    def signin(self, userId, feeIndex):
        pass

    def signout(self, signer):
        pass

    def enter(self, signer):
        pass

    def leave(self, signer):
        pass

    def buildStatus(self):
        pass

    def _doInit(self):
        pass

    def _doStartSigninImpl(self):
        pass

    def _doPrepareImpl(self):
        pass

    def _doStartImpl(self):
        pass

    def _doCancelImpl(self, reason):
        pass

    def _doFinalImpl(self):
        pass

    def _doSignin(self, userId, fee, timestamp):
        pass

    def _fillSigner(self, signer):
        pass

    def _prelockSigners(self, signers):
        pass

    def _lockSigner(self, signer):
        pass

    def _unlockSigner(self, signer, returnFee=False):
        pass

    def _lockSigners(self):
        pass

    def _kickoutSigner(self, signer):
        pass

    def _cancelSigner(self, signer, reason):
        pass

    def _ensureCanSignin(self, userId):
        pass

    def _doHeartbeat(self):
        pass

class MatchGroup(HeartbeatAble, ):
    ST_IDLE = 0
    ST_START = 1
    ST_FINISHING = 2
    ST_FINISH = 3
    ST_FINALING = 4
    ST_FINAL = 5

    def __init__(self, area, instId, matchingId, matchingId3, groupId, groupIndex, groupName, stageIndex, isGrouping, totalPlayerCount):
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
    def playerMap(self):
        pass

    @property
    def playerCount(self):
        pass

    def getRisePlayers(self):
        pass

    def findPlayer(self, userId):
        """
        查找Player
        """
        pass

    def removePlayer(self, player):
        pass

    def addPlayers(self, players):
        """
        给该分组增加一个player，必须在开始之前调用
        """
        pass

    def finishGroup(self, reason):
        """
        杀掉该分组
        """
        pass

    def finalGroup(self):
        pass

    def _doInit(self):
        pass

    def _doFinish(self, reason):
        pass

    def _doFinal(self):
        pass

    def _doFinishImpl(self, reason):
        pass

    def _doFinalImpl(self):
        pass

    def _doHeartbeat(self):
        pass

class MatchGroupLocal(MatchGroup, ):
    """
    一个比赛分组
    """

    def __init__(self, area, instId, matchingId, matchingId3, groupId, groupIndex, groupName, stageIndex, isGrouping, totalPlayerCount):
        pass

    @property
    def match(self):
        pass

    @property
    def stage(self):
        pass

    @property
    def startPlayerCount(self):
        pass

    def setStage(self, stage):
        pass

    def calcTotalUncompleteTableCount(self, player):
        pass

    def _doInit(self):
        pass

    def _doFinishImpl(self, reason):
        pass

    def _doFinalImpl(self):
        pass

    def _doHeartbeat(self):
        pass

class MatchArea(HeartbeatAble, ):

    def __init__(self, matchConf, interval):
        pass

    @property
    def matchId(self):
        pass

    @property
    def tableId(self):
        pass

    @property
    def groupMap(self):
        pass

    def findPlayer(self, userId):
        pass

    def isOnline(self):
        """
        赛区是否在线
        """
        pass

    def newInst(self, instId, startTime, needLoad):
        """
        新建一个新的比赛实例
        """
        pass

    def newGroup(self, instId, matchingId, groupId, groupName, stageIndex, isGrouping, totalPlayerCount):
        """
        创建一个新的分组
        """
        pass

    def findGroup(self, groupId):
        """
        根据groupId查找Group
        """
        pass

class MatchAreaLocal(MatchArea, ):

    def __init__(self, master, room, matchConf):
        pass

    @property
    def roomId(self):
        pass

    @property
    def gameId(self):
        pass

    @property
    def curInst(self):
        pass

    @property
    def findInst(self, instId):
        pass

    def isOnline(self):
        """
        本地的赛区始终在线
        """
        pass

    def newInst(self, instId, startTime, needLoad):
        pass

    def newGroup(self, instId, matchingId, matchingId3, groupId, groupIndex, groupName, stageIndex, isGrouping, totalPlayerCount):
        pass

    def findGroup(self, groupId):
        """
        根据groupId查找Group
        """
        pass

    def findSigner(self, userId):
        """
        根据userId查找Signer
        """
        pass

    def findPlayer(self, userId):
        """
        根据userId查找Player
        """
        pass

    def signin(self, userId, feeIndex):
        """
        玩家报名
        """
        pass

    def signout(self, userId):
        """
        玩家退赛
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

    def onInstStarted(self, inst):
        """
        暂时不做处理，因为只处理本地
        """
        pass

    def _doInit(self):
        pass

    def _doHeartbeat(self):
        pass

class MatchInstCtrl(HeartbeatAble, ):
    STARTING_TIMEOUT = 180

    def __init__(self, master, status, needLoad, signers=None):
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

    def cancel(self, reason):
        pass

    def calcTotalSignerCount(self):
        pass

    def _doInit(self):
        pass

    def _doStartSignin(self):
        pass

    def _doPrepare(self):
        pass

    def _doStart(self):
        pass

    def _doCancel(self, reason):
        pass

    def _doFinal(self):
        pass

    def _isAllStarted(self):
        pass

    def _isStartingTimeout(self):
        pass

    def _cancelTimeoutInst(self):
        pass

    def _collectSignerMap(self):
        pass

    def _doHeartbeat(self):
        pass

class MatchStageCtrl(object, ):
    ST_IDLE = 0
    ST_START = 1
    ST_FINISH = 2
    ST_FINAL = 3

    def __init__(self, matching, stageConf):
        pass

    @property
    def instId(self):
        pass

    @property
    def matchingId(self):
        pass

    @property
    def matchingId3(self):
        pass

    @property
    def master(self):
        pass

    @property
    def stageIndex(self):
        pass

    @property
    def matchConf(self):
        pass

    @property
    def state(self):
        pass

    def getAllRisePlayerList(self):
        pass

    def startStage(self, playerList):
        """
        启动该阶段
        """
        pass

    def finalStage(self):
        """
        完成该阶段
        """
        pass

    @classmethod
    def groupingPlayerList(self, playerList, stageConf, tableSeatCount):
        pass

    def _isAllGroupFinish(self):
        pass

    def _processStage(self):
        pass

class Matching(HeartbeatAble, ):
    """
    一个发奖单元
    """
    ST_IDLE = 0
    ST_START = 1
    ST_FINISH = 2
    HEARTBEAT_INTERVAL = 2

    def __init__(self, master, instId, matchingId, matchingId3, signers):
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
    def signers(self):
        pass

    def findFirstStage(self, signerCount):
        pass

    def signersToPlayers(self, signers):
        pass

    def _createStages(self, stageConfs):
        pass

    def _doInit(self):
        pass

    def _doHeartbeat(self):
        pass

    def _startNextStage(self):
        pass

    def _getNextStage(self, stage):
        pass

    def _doFinish(self):
        pass

class MatchMaster(HeartbeatAble, ):
    ST_IDLE = 0
    ST_ALL_AREA_ONLINE = 1
    ST_LOAD = 2
    HEARTBEAT_TO_AREA_INTERVAL = 5

    def __init__(self, room, matchConf):
        pass

    @property
    def areas(self):
        pass

    @property
    def areaCount(self):
        pass

    @property
    def roomId(self):
        pass

    @property
    def gameId(self):
        pass

    def findArea(self, roomId):
        pass

    def addArea(self, area):
        pass

    def _doInit(self):
        pass

    def _startMatching(self, instCtrl, num, signers):
        pass

    def _setupNextInst(self, instCtrl, signers, matchingCount):
        pass

    def _isAllAreaOnline(self):
        pass

    def _doLoad(self):
        pass

    def _processMatching(self):
        pass

    def _calcMatchingPlayerCount(self):
        pass

    def _buildRoomInfo(self):
        pass

    def _heartbeatToAllArea(self):
        pass

    def _doHeartbeat(self):
        pass