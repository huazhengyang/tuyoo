# -*- coding: utf-8 -*-
"""
Created on 2015-5-12
@author: zqh
"""
from freetime.core.protocol import FTHttpRequest, FTHttpChannel
import freetime.entity.service as ftsvr
from freetime.support.tcpagent.protocol import S2AProtocol
import freetime.util.log as ftlog
from poker.entity.configure import gdata
from poker.protocol import runhttp, runcmd
from freetime.entity.msg import MsgPack
from freetime.core.tasklet import FTTasklet

class TYCommonHttpRequest(FTHttpRequest, ):
    """
    通用的HTTP协议
    """

    def handleRequest(self):
        pass

class TYCommonHttpChannel(FTHttpChannel, ):
    requestFactory = TYCommonHttpRequest

class TYCommonS2AProto(S2AProtocol, ):
    """
    通用的S2A协议
    """

    def getTaskletFunc(self, argd):
        pass

    def parseData(self, data):
        pass

    def doSomeLogic(self):
        pass

def onAgentSelfCommand(agentProtocol, src, queryid, userheader1, userheader2, message):
    pass