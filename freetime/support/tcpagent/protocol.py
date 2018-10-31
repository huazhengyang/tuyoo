# -*- coding: utf-8 -*-
"""
 server之间通过agent通信拓扑图：

 ----------      -------------              -------------      ----------
|SERVER-s2a|----|a2s-AGENT-a2a|------------|a2a-AGENT-a2s|----|s2a-Server|
 ----------      -------------              -------------      ----------

 a2a用于agent之间相连，用于listenTcp和connectTcp
 a2s用于agent listen server
 s2a用于server connect agent，s2a需要扩展挂接逻辑功能

# 2015.4.14 by zipxing@hotmail.com
# 2015.4.17 modifiedby zhouhao@tuyoogame.com
"""
import stackless
from twisted.internet import protocol, defer, reactor
from twisted.python import failure
from freetime.core.protocol import FTTCPServerProtocol, FTTimeoutException, _countProtocolPack
import freetime.entity.config as ftcon
import freetime.support.tcpagent.msg as agentmsg
import freetime.util.log as ftlog
from time import time
from freetime.core.tasklet import FTTasklet
from freetime.util import performance
from freetime.core.exception import FTMsgPackException

class AgentProtocolMixin(FTTCPServerProtocol, ):
    """

    """

    def __init__(self):
        pass

    def madeHandler(self):
        pass

    def lostHandler(self, reason):
        pass

    def register_self(self):
        pass

    def lineReceived(self, data):
        pass

class A2AProtocol(AgentProtocolMixin, ):
    """
    运行在Agent进程内，用于Agent之间连接的协议，
    既用于listenTcp，又用于connectTcp
    """
    onCommand = None

    def getTaskletFunc(self, pack):
        pass

    def onMsg(self):
        pass

class A2SProtocol(AgentProtocolMixin, ):
    """
    运行在Agent进程内，用于监听Server的连接
    用于listenTcp
    """
    onCommand = None

    def getTaskletFunc(self, pack):
        pass

    def onMsg(self):
        pass
_LIVE_MESSAGES = {}
_FAILED_MESSAGES = {}
_QUERY_ID = 0

class S2AProtocol(AgentProtocolMixin, ):

    def __init__(self):
        pass

    def lineReceived(self, data):
        pass

    def getTaskletFunc(self, pack):
        pass

    def query(self, src, dst, userheader1, userheader2, data, timeout, notimeoutex=0):
        pass

    def _clearFailed(self, deferred, query_id, msg, notimeoutex):
        pass