# -*- coding: utf-8 -*-
"""
Created on 2015年6月3日

@author: zhaoqh
"""
import json
import urllib
from twisted.internet import protocol, reactor
from freetime.aio import http
from freetime.core.timer import FTLoopTimer
from freetime.entity.msg import MsgPack
from freetime.support.tcpagent.factory import FTReconnectFactory
import freetime.util.log as ftlog
_DEBUG = 0
debug = ftlog.info

class _HttpAdapter:

    def __init__(self, httppath, timeout, retryCount):
        pass

    def start(self):
        pass

    def isOK(self):
        pass

    def send(self, dataDict, headerDict=None):
        pass

    def close(self):
        pass

class _UdpAdapter:
    _UDPSENDER = None

    def __init__(self, udppath, timeout, retryCount):
        pass

    def start(self):
        pass

    def isOK(self):
        pass

    @staticmethod
    def packDatas(data, headerDict=None):
        pass

    def send(self, data, headerDict=None):
        pass

    def close(self):
        pass

class _TcpAdapter:

    class TcpHea4Protocol(protocol.Protocol, ):
        _buffer = ''

        def connectionMade(self):
            pass

        def connectionLost(self, reason):
            pass

        def clearLineBuffer(self):
            pass

        def dataReceived(self, data):
            pass

        def lineReceived(self, data):
            pass

        def writeData(self, data):
            pass

    @staticmethod
    def connect(ip, port, owner):
        pass

    def __init__(self, tcppath, timeout, retryCount):
        pass

    def start(self):
        pass

    def isOK(self):
        pass

    def send(self, data, headerDict=None):
        pass

    def close(self):
        pass
_clietnsmap = {}

def resetAdapters(adapterKey, newConfig):
    pass

def _closeAllAdapter(adapters):
    pass

def _startAdapter(adapterKey, newAdapters, newConfig, oldAdapters, oldConfig):
    pass

def _checkAdapter(adapterKey, newAdapters, newConfig, oldAdapters, oldConfig, checkcount):
    pass

def sendToAdapter(adapterKey, dictData, headerDict=None):
    pass

def isEnabled(adapterKey):
    pass