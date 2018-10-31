# -*- coding: utf-8 -*-
"""
Created on 2015-5-12
@author: zqh
"""
from freetime.core.protocol import FTZipEncryServerProtocol, FTWebSocketServerProtocol, _countProtocolPack
from freetime.core.tasklet import FTTasklet
from freetime.entity.msg import MsgPack
import freetime.entity.service as ftsvr
from freetime.support.tcpagent.protocol import S2AProtocol
import freetime.util.log as ftlog
from poker.entity.biz import bireport
from poker.entity.configure import gdata, pokerconf
from poker.entity.dao import userdata
from poker.protocol import router, runcmd
from poker.protocol.conn.tcpuser import TcpUser
from poker.util import strutil
from poker.protocol.conn import structProtocolHelper, conn_bridge
ERROR_SYS_LOGOUT_USERID_ERROR = 1
ERROR_SYS_LOGOUT_DATASWAP_ERROR = 2
ERROR_SYS_LOGOUT_FIRST_CMD_ERROR = 3
ERROR_SYS_LOGOUT_OTHER_LOGIN = 4
ERROR_SYS_LOGOUT_TIME_OUT = 5
ERROR_SYS_LOGOUT_FORCE_LOGOUT = 6
ERROR_SYS_LOGOUT_CLIENTID_ERROR = 7
_ONLINE_USERS = {}
_NEW_PROTOCOLS = {}
_MSG_QUEUES = {}
_MSG_QUEUES_MAX_LEN = 60
_HEART_BEAT_MOD = 5
_EMPTY_TCP_CHECK_TIMES = 5
_EMPTY_TCP_TIMEOUT_COUNT = 6
_EMPTY_USER_TIMEOUT_COUNT = 6
_DISABLE_GAMEIDS = set([])

class COS2AProto(S2AProtocol, ):

    def getTaskletFunc(self, argd):
        pass

    def doServerTcpMsg(self):
        """
        其他服务发送至CONN服务的消息处理 
        绝大部分需要转发至用户客户端
        """
        pass

class COTCPProto(object, ):
    """
    TCP的协议类, 其基类可以是FTWebSocketServerProtocol也可以是FTZipEncryServerProtocol
    再startup时,判定是否用COTCPProtoZIP还是COTCPProtoWS
    """

    def lostHandler(self, reason):
        """
        TCP链接断开处理
        """
        pass

    def madeHandler(self):
        """
        TCP链接建立处理
        """
        pass

    def getTaskletFunc(self, pack):
        pass

    def parseData(self, data):
        """
        CONN服务接到客户端的消息, 不进行JSON解析, 避免过高的CPU
        """
        pass

    def writeEncodeMsg(self, msg):
        """
        向用户客户端发送一个加密消息
        """
        pass

    def doClientTcpMsg(self):
        """
        接收到一个的用户客户端的TCP消息
        """
        pass

    def _processUserMessage(self, userId, msgstr):
        pass

    def _doUserConnect(self, userId, gameId, clientId):
        """
        更新用户的TCP链接
        """
        pass

    def _doUserAlive(self, cmd):
        """
        用户客户端发送的心跳处理
        """
        pass

    def _doUserClosed(self):
        """
        用户掉线处理
        """
        pass

class COTCPProtoZIP(COTCPProto, FTZipEncryServerProtocol, ):
    pass

class COTCPProtoWS(COTCPProto, FTWebSocketServerProtocol, ):
    pass

def _sendLogOutMsg(protocol, errorCode, isabort):
    """
    发送一个强制logout的消息后, 关闭用户的TCP的链接
    """
    pass

def forceUserLogOut(userId, logoutmsg):
    """
    管理员发送强制关闭TCP链接的消息, 
    发送logout消息后,关闭用户的TCP的链接
    """
    pass

def _notifyUserOnlineStatus(user, isOnline):
    """
    发送用户的上下线通知到UTIL服务
    """
    pass

def doCleanUpEmptyTcp(event):
    """
    检查当前进程内的空闲的TCP链接, 
    关闭空闲的TCP, 释放资源
    """
    pass

def sendCarryMessage(msg, userids=[]):
    """
    发送延迟的携带消息
    """
    pass

def _proxyCheck(msgstr, protocol):
    pass

def _checkLastedConnId(userId):
    pass