# -*- coding: utf-8 -*-
"""
Created on 2015-5-12
@author: zqh
"""
import stackless
from freetime.core.protocol import _SocketOpt, FTProtocolBase, _countProtocolPack
from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from autobahn.twisted.websocket import WebSocketClientProtocol

class WebSocketRobotClientProtocol(WebSocketClientProtocol, FTProtocolBase, ):

    def __init__(self, robotUser):
        pass

    def onConnect(self, response):
        pass

    def onOpen(self):
        pass

    def onMessage(self, payload, isBinary):
        pass

    def connectionMade(self):
        pass

    def dataReceived(self, data):
        pass

    def lostHandler(self, reason):
        pass

    def getTaskletFunc(self, pack):
        pass

    def parseData(self, data):
        pass

    def onMsg(self):
        pass

    def writeMsg(self, msg):
        pass

    def startedConnecting(self, connector):
        pass