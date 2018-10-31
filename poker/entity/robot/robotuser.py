# -*- coding: utf-8 -*-
"""
Created on 2015-5-12
@author: zqh
"""
import random
from freetime.entity.msg import MsgPack
from freetime.util import log as ftlog
from poker.entity.configure import gdata, configure
from poker.entity.dao import userchip, daoconst
from poker.entity.robot.robotprotocol import RobotClientProtocol
try:
    from poker.entity.robot.robotprotocol_ws import WebSocketRobotClientProtocol
except:
    pass
from poker.util import strutil, webpage
CMD_LOGIN = 0
CMD_TCP_CONNECTED = 1
CMD_BIND_USER = 2
CMD_GANEDATA_9999 = 3
CMD_GANEDATA_CUR_GAMEID = 4
CMD_QUICK_START = 5
CMD_READY = 6
CMD_GAME_READY = 7
CMD_GAME_START = 9
CMD_GAME_WINLOSE = 10
CMD_TCP_CLOSED = 11
from autobahn.twisted.websocket import WebSocketClientFactory

class H5WebSocketClientFactory(WebSocketClientFactory, ):

    def startedConnecting(self, connector):
        pass

class RobotUser(object, ):
    TCPSRV = None

    def __init__(self, clientId, snsId, name):
        pass

    def getResponseDelaySecond(self):
        pass

    @property
    def msgQueue(self):
        pass

    def doShutDown(self):
        pass

    def stop(self):
        pass

    def start(self, roomId, tableId, isMatch=False):
        pass

    def _start(self):
        pass

    def _doLogin(self):
        pass

    def _makeRoboProtocloWs(self):
        pass

    def _makeRoboProtoclo(self):
        pass

    def _createClientFactory(self, tcpip=None, tcpport=None):
        pass

    def _doConnTcp(self):
        pass

    def _onTimer(self, event):
        pass

    def onTimer(self, event):
        pass

    def writeDelayMsg(self, delay, msg):
        pass

    def writeMsg(self, msg):
        pass

    def checkState(self, state):
        pass

    def getState(self, state):
        pass

    def cleanState(self, *stateList):
        pass

    def onMsgLogin(self, msg):
        pass

    def onMsg(self, msg):
        pass

    def onMsgTableBegin(self):
        pass

    def onMsgTablePlay(self, msg):
        pass

    def adjustChip(self, minCoin=None, maxCoin=None):
        pass