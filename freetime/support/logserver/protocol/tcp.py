# -*- coding: utf-8 -*-
import struct
import time
import base64
import freetime.entity.config as ftcon
import freetime.entity.service as ftsvr
import freetime.util.log as ftlog
import freetime.util.pio as ftpio
from freetime.support.logserver.protocol import startup
from freetime.support.tcpagent.protocol import S2AProtocol

class WriteTcpRequest(S2AProtocol, ):
    HEAD_SIZE = 256
    EXTRA_SIZE = 17
    FILE_INFO = {}

    def doSomeLogic(self):
        pass

    def checkFileRecord(self, f, rec_id, log_size, record_count):
        pass

    def writeFile(self, data_dir, _type, _group, rec_id, record_count, log_size, record):
        pass

    def switchFile(self, data_dir, _type, _group, rec_id, record_count):
        pass

    def getTaskletFunc(self, argd):
        pass