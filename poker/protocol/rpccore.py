# -*- coding: utf-8 -*-
"""
Created on 2015-5-12
@author: zqh
"""
from stackless import bomb
from time import time
import functools
import inspect
import stackless
import sys
from twisted.internet import defer
from freetime.core.exception import FTMsgPackException
from freetime.core.timer import FTLoopTimer
from freetime.support.tcpagent import wrapper
from freetime.util import performance
from poker.entity.configure import gdata
from poker.protocol import _runenv, decorator, router
from poker.util import strutil
import freetime.entity.service as ftsvr
import freetime.util.log as ftlog
_DEBUG = 0
if _DEBUG:
    debug = ftlog.info
else:

    def debug(*argl, **argd):
        pass

class RpcException(Exception, ):

    def __init__(self, msg):
        pass
_MARKED_METHOD = []
_RPC_ID_COUNT_ = 0
_SYS_RPC_PACKAGES = ['poker.servers.rpc']
RPC_FIRST_SERVERID = '_SERVERID_'

def markRpcCall(groupName, lockName, syncCall=1, future=0):
    """
    标记一个方法为RPC远程命令的入口
    注意: 使用此标记的方法必须为模块级别的方法(py文件中的顶级方法)
         RPC方法必须返回非None的结果
    """
    pass

def _initializeRpcMehodss(gdata_):
    """
    初始化RPC的命令入口, 获取各个游戏的实例的handler进行注册处理
    分游戏自动搜索自定义的RPC方法
    """
    pass

def _registerRpcCall(method, rpc=None):
    pass

def _getRpcId():
    pass

def _invokeMethodLocked(markParams, argl, argd):
    pass

def _handlerRpcCommand(msg):
    """
    处理接收到的一个远程RPC调用
    """
    pass

def _getRpcDstServerId(rsrv, groupId):
    pass

def getRpcDstRoomServerId(roomId, canChangeRoomId):
    pass

def _invokeRpcMethod(markParams, argl, argd):
    """
    进程内其它方法调用RPC方法的代理方法
    """
    pass

def _parseRpcResult(mi, jstr, rpc):
    pass

class FutureResult(object, ):
    STATUS_NONE = 0
    STATUS_RUN = 1
    STATUS_OK = 2
    STATUS_ERROR = 3

    def __init__(self):
        pass

    def _doFutureDone(self):
        pass

    def getResult(self):
        """
        如果返回None，说明有异常发生，可以查看异常日志判定原因
        """
        pass

class _FutureResultLocal(FutureResult, ):

    def __init__(self, markParams, argl, argd):
        pass

    def _invokeLocal(self, markParams, argl, argd):
        pass

class _FutureResultRemote(FutureResult, ):

    def __init__(self, rpc, dstSid, mi, rpcid, groupVal, timeout):
        pass

    def _doRemoteWrite(self, rpc, dstSid, mi, rpcid, groupVal, timeout):
        pass

    def _doRemoteSuccessful(self, remoteRet):
        pass

    def _doRemoteError(self, fault):
        pass