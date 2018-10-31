# -*- coding: utf-8 -*-
import struct
import time
import base64
from freetime.core.protocol import FTHttpRequest, FTHttpChannel
import freetime.entity.config as ftcon
import freetime.entity.service as ftsvr
import freetime.util.log as ftlog
import freetime.support.tcpagent.wrapper as ftagent
from freetime.support.logserver.protocol import startup

class IndexHttpRequest(FTHttpRequest, ):

    def handleRequest(self):
        pass

    def _doHttpManager(self, request):
        pass

    def updateIndex(self, _type, _group, logid, pbody):
        pass

    def sendToWriter(self, _type, _group, logid, body):
        pass

    def parseBody(self, body, _type):
        pass

class IndexHttpChannel(FTHttpChannel, ):
    requestFactory = IndexHttpRequest