# -*- coding: utf-8 -*-
"""
Created on 2015-5-12
@author: zqh
"""
import stackless
import zlib
from freetime.core.protocol import FTZipEncryServerProtocol, _SocketOpt, _countProtocolPack
from freetime.entity.msg import MsgPack
import freetime.util.encry as ftenc

class RobotClientProtocol(FTZipEncryServerProtocol, ):

    def __init__(self, robotUser):
        pass

    def connectionMade(self):
        pass

    def dataReceived(self, data):
        pass

    def lineReceived(self, data):
        pass

    def lostHandler(self, reason):
        pass

    def getTaskletFunc(self, pack):
        pass

    def onMsg(self):
        pass

    def writeMsg(self, msg):
        pass