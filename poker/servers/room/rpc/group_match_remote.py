# -*- coding: utf-8 -*-
"""
Created on 2016年1月15日

@author: zhaojiangang
"""
import time
from freetime.core.exception import FTMsgPackException
from freetime.core.tasklet import FTTasklet
import freetime.util.log as ftlog
from poker.entity.configure import gdata, pokerconf
from poker.entity.game.rooms.group_match_ctrl.const import MatchFinishReason
from poker.entity.game.rooms.group_match_ctrl.match import MatchAreaStatus, MatchMasterStatus, MatchMasterStub, MatchInstStub, MatchGroupStub, MatchAreaStub
from poker.entity.game.rooms.group_match_ctrl.models import Riser, Signer, Player
from poker.protocol import rpccore

def getMaster(roomId):
    pass

def getMatchArea(roomId):
    pass

def findAreaStub(roomId, areaRoomId):
    pass

def findInstStub(roomId, areaRoomId, instId):
    pass

def findGroupStub(roomId, groupId):
    pass

def findGroup(roomId, groupId):
    pass

def decodeRiserFromDict(d):
    pass

def decodeRiserList(riserDictList):
    pass

def encodePlayerForRiserDict(player):
    pass

def clientIdToNumber(clientId):
    pass

def numberToClientId(numberId):
    pass

def cutUserName(userName):
    pass

def encodePlayerListForRiser(playerList, start, end):
    pass

def encodeSignerToDict(signer):
    pass

def encodeSignerList(signerList, start, end):
    pass

def decodeSignerFromDict(instId, d):
    pass

def decodeSignerList(instId, signerList):
    pass

def encodePlayerForAddGroup(player):
    pass

def decodePlayerFromDict(d):
    pass

def encodePlayerListForAddGroup(playerList, start, end):
    pass

def decodePlayerList(playerDictList):
    pass

@rpccore.markRpcCall(groupName=rpccore.RPC_FIRST_SERVERID, lockName='', syncCall=0)
def areaHeartbeat(serverId, roomId, areaRoomId, areaStatusDict):
    pass

@rpccore.markRpcCall(groupName=rpccore.RPC_FIRST_SERVERID, lockName='', syncCall=1)
def areaGroupRise(serverId, roomId, areaRoomId, groupId, riserDictList):
    pass

@rpccore.markRpcCall(groupName=rpccore.RPC_FIRST_SERVERID, lockName='', syncCall=1)
def areaGroupFinish(serverId, roomId, areaRoomId, groupId, finishReason):
    pass

@rpccore.markRpcCall(groupName=rpccore.RPC_FIRST_SERVERID, lockName='', syncCall=1)
def areaReportSigners(serverId, roomId, areaRoomId, instId, signerList):
    pass

@rpccore.markRpcCall(groupName=rpccore.RPC_FIRST_SERVERID, lockName='', syncCall=1)
def areaStartOK(serverId, roomId, areaRoomId, instId):
    pass

@rpccore.markRpcCall(groupName=rpccore.RPC_FIRST_SERVERID, lockName='', syncCall=0)
def instStartSignin(serverId, roomId, masterRoomId, instId):
    pass

@rpccore.markRpcCall(groupName=rpccore.RPC_FIRST_SERVERID, lockName='', syncCall=0)
def instPrepare(serverId, roomId, masterRoomId, instId):
    pass

@rpccore.markRpcCall(groupName=rpccore.RPC_FIRST_SERVERID, lockName='', syncCall=0)
def instCancel(serverId, roomId, masterRoomId, instId, reason):
    pass

@rpccore.markRpcCall(groupName=rpccore.RPC_FIRST_SERVERID, lockName='', syncCall=0)
def instStart(serverId, roomId, masterRoomId, instId):
    pass

@rpccore.markRpcCall(groupName=rpccore.RPC_FIRST_SERVERID, lockName='', syncCall=0)
def masterHeartbeat(serverId, roomId, masterRoomId, statusDict):
    pass

@rpccore.markRpcCall(groupName=rpccore.RPC_FIRST_SERVERID, lockName='', syncCall=1)
def createInst(serverId, roomId, masterRoomId, instId, startTime, needLoad):
    pass

@rpccore.markRpcCall(groupName=rpccore.RPC_FIRST_SERVERID, lockName='', syncCall=1)
def cancelInst(serverId, roomId, masterRoomId, instId, reason):
    pass

@rpccore.markRpcCall(groupName=rpccore.RPC_FIRST_SERVERID, lockName='', syncCall=1)
def createGroup(serverId, roomId, masterRoomId, instId, matchingId, groupId, groupName, stageIndex, isGrouping, totalPlayerCount, startStageIndex=0):
    pass

@rpccore.markRpcCall(groupName=rpccore.RPC_FIRST_SERVERID, lockName='', syncCall=1)
def addPlayerToGroup(serverId, roomId, masterRoomId, groupId, playerList):
    pass

@rpccore.markRpcCall(groupName=rpccore.RPC_FIRST_SERVERID, lockName='', syncCall=0)
def startGroup(serverId, roomId, masterRoomId, groupId):
    pass

@rpccore.markRpcCall(groupName=rpccore.RPC_FIRST_SERVERID, lockName='', syncCall=0)
def killGroup(serverId, roomId, masterRoomId, groupId, reason):
    pass

@rpccore.markRpcCall(groupName=rpccore.RPC_FIRST_SERVERID, lockName='', syncCall=0)
def finalGroup(serverId, roomId, masterRoomId, groupId):
    pass

class MatchMasterStubRemote(MatchMasterStub, ):
    """
    赛事在赛区控制对象，运行于赛区中
    """
    RISER_COUNT_PER_TIME = 1000
    REPORT_SIGNER_COUNT_PER_TIME = 300

    def __init__(self, roomId):
        pass

    def areaHeartbeat(self, area):
        """
        area心跳，运行
        """
        pass

    def _risePlayers(self, area, group, encodedRiserList, start):
        pass

    def areaGroupFinish(self, area, group):
        """
        向主赛区汇报
        """
        pass

    def _reportSigners(self, area, inst, encodedSignerList, start):
        pass

    def areaInstStarted(self, area, inst):
        """
        向主赛区汇报比赛实例启动成功，汇报报名用户列表
        """
        pass

class MatchInstStubRemote(MatchInstStub, ):

    def __init__(self, areaStub, instId, startTime, needLoad):
        pass

    @property
    def serverId(self):
        pass

    def _doStartSignin(self):
        pass

    def _doPrepare(self):
        pass

    def _doCancel(self):
        pass

    def _doStart(self):
        pass

class MatchGroupStubRemote(MatchGroupStub, ):
    """
    比赛分组存根对象，运行于主控进程
    """
    ADD_PLAYER_COUNT_PER_TIME = 300

    def __init__(self, areaStub, stage, groupId, groupName, playerList, isGrouping, totalPlayerCount, startStageIndex=0):
        pass

    @property
    def serverId(self):
        pass

    def _addPlayersToGroup(self, encodedPlayerList, start):
        pass

    def _doStartGroup(self):
        pass

    def _doKillGroup(self):
        pass

    def _doFinalGroup(self):
        pass

class MatchAreaStubRemote(MatchAreaStub, ):

    def __init__(self, master, roomId):
        pass

    def masterHeartbeat(self, master):
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