# -*- coding: utf-8 -*-
"""
Created on 2016年6月7日

@author: luoguanggui
"""
import functools
from freetime.core.lock import FTLock
from freetime.core.timer import FTTimer
import freetime.util.log as ftlog

class Logger(object, ):

    def __init__(self, kvs=None):
        pass

    def add(self, k, v):
        pass

    def info(self, prefix=None, *args):
        pass

    def debug(self, prefix=None, *args):
        pass

    def warn(self, prefix=None, *args):
        pass

    def error(self, prefix=None, *args):
        pass

    def isDebug(self):
        pass

    def _log(self, prefix, func, *args):
        pass

class Heartbeat(object, ):
    ST_IDLE = 0
    ST_START = 1
    ST_STOP = 2

    def __init__(self, interval, target):
        pass

    def start(self):
        pass

    def stop(self):
        pass

    def _onTimer(self):
        pass

class HeartbeatAble(object, ):

    def __init__(self):
        pass

    def postCall(self, func, *args, **kwargs):
        pass

    def postTask(self, task):
        pass

    def _startHeartbeat(self):
        pass

    def _stopHeartbeat(self):
        pass

    def _doHeartbeat(self):
        pass

    def _processPostTaskList(self):
        pass

    def _doHeartbeatImpl(self):
        pass