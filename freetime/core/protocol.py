# -*- coding: utf-8 -*-
from datetime import datetime
import socket
import zlib
import random
import struct
import hashlib
import base64
import array
import os
from twisted.internet import defer
from twisted.internet import protocol, reactor
from twisted.internet.protocol import DatagramProtocol
from twisted.protocols.basic import LineReceiver
from twisted.python import failure
import twisted.web.http
import freetime.util.encry as ftenc
import freetime.util.log as ftlog
from tasklet import FTTasklet

class FTTimeoutException(Exception, ):
    pass
_COUNT_PPS = 0
_COUNT_COUNT = 0
_COUNT_TIME = datetime.now()
_COUNT_PACKS = {}

def _countProtocolPack(ptype, proto, count_block=10000):
    pass

def ppsCountProtocolPack():
    pass

class FTProtocolBase(object, ):
    """
    FreeTime协议的公共抽象，封装了“为每个请求派生一个tasklet”的机制

    定义了lostHandler和madeHandler接口,用于实现建立连接和连接丢失的处理逻辑
    (对于udp协议，startProtocol和stopProtocol时触发)

    定义了getTaskletFunc接口，业务逻辑层通过这个接口管理消息和消息处理函数
    的映射,框架会传入启动tasklet时的参数字典，业务逻辑层通过这些参数分配合
    适的tasklet方法，可以实现诸如消息注册等方式

    定义了parseData接口，用于实现解析网络原始包，解析后的pack后续
    可以通过ftsvr.getTaskPack()得到
    对于格式非法的数据，parseData需要返回None

    另外，还实现了请求包个数和每秒处理包速度PPS等基本统计功能
    """

    def lostHandler(self, reason):
        pass

    def madeHandler(self):
        pass

    def getTaskletFunc(self, pack):
        pass

    def parseData(self, data):
        pass

    def closeConnection(self, isabort=0):
        pass

    def _runTasklet(self, *argl, **argd):
        pass

class _SocketOpt:
    """
    常用socket设置
    """
    UDP_BUFFER_SIZE = ((2 * 1024) * 1024)
    TCP_LINE_MAX_LENGTH = (1024 * 63)

    @classmethod
    def udp(cls, p):
        pass

    @classmethod
    def tcp(cls, p):
        pass

class FTUDPSenderProtocol(DatagramProtocol, FTProtocolBase, ):

    def startProtocol(self):
        pass

    def datagramReceived(self, data, address):
        pass

    def sendTo(self, data, toAddress):
        pass

class FTUDPServerProtocol(DatagramProtocol, FTProtocolBase, ):

    def startProtocol(self):
        pass

    def stopProtocol(self):
        pass

    def datagramReceived(self, data, address):
        pass

class FTUDPQueryProtocol(DatagramProtocol, FTProtocolBase, ):
    QUERYID = 0

    def __init__(self, dsthost, dstport):
        pass

    def startProtocol(self):
        pass

    def stopProtocol(self):
        pass

    def datagramReceived(self, data, address):
        pass

    def query(self, data, timeout=1):
        pass

    def _clearFailed(self, deferred, mid):
        pass

class FTTCPServerProtocol(LineReceiver, FTProtocolBase, ):

    def connectionMade(self):
        pass

    def connectionLost(self, reason):
        pass

    def lineReceived(self, data):
        pass

    def lineLengthExceeded(self, line):
        pass

class FTZipEncryServerProtocol(protocol.Protocol, FTProtocolBase, ):
    """
    一个压缩加密的tcp协议基类
    客户端建立连接后，首先回应一个%04X的随机数作为种子
    然后双方会使用（种子+长度）对数据加密压缩，然后用"%04X%s"%(len, data)的格式交换数据
    加密算法用cffi实现
    """
    _buffer = ''

    def connectionMade(self):
        pass

    def connectionLost(self, reason):
        pass

    def _encode(self, src):
        pass

    def _decode(self, dst):
        pass

    def clearLineBuffer(self):
        pass

    def dataReceived(self, data):
        pass

    def lineReceived(self, data):
        pass

class FTHead4ServerProtocol(protocol.Protocol, FTProtocolBase, ):
    """
    一个tcp协议基类, 4字节的数据长度+数据体
    """
    _buffer = ''

    def connectionMade(self):
        pass

    def connectionLost(self, reason):
        pass

    def _encode(self, src):
        pass

    def clearLineBuffer(self):
        pass

    def dataReceived(self, data):
        pass

    def lineReceived(self, data):
        pass

class FTWebSocketServerProtocol(protocol.Protocol, FTProtocolBase, ):
    """
    WebSocket加密的tcp协议基类
    客户端建立连接后，首先回应一个%04X的随机数作为种子
    """
    _buffer = ''
    isNewVersion = True
    handshaken = False

    def connectionMade(self):
        pass

    def connectionLost(self, reason):
        pass

    def _encode(self, src):
        pass

    def encode_message(self, src):
        pass

    def mask_message(self, mask_key, data):
        """
        mask or unmask data. Just do xor for each byte
        mask_key: 4 byte string(byte).
        data: data to mask/unmask.
        """
        pass

    def _decode(self, dst):
        pass

    def clearLineBuffer(self):
        pass

    def dataReceived(self, data):
        pass

    def lineReceived(self, data):
        pass

    def on_handshake(self, msg):
        pass

    def h5_generate_token(self, key1, key2, key3):
        pass

    def h5_generate_token2(self, key):
        pass

class FTHttpRequest(twisted.web.http.Request, FTProtocolBase, ):

    def process(self):
        pass

    def getTaskletFunc(self, pack):
        pass

    def handleRequest(self):
        pass

class FTHttpChannel(twisted.web.http.HTTPChannel, ):
    requestFactory = FTHttpRequest