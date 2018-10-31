# -*- coding: utf-8 -*-
"""
Created on 2016年5月13日

@author: zhaojiangang
"""
import functools
from freetime.core.timer import FTTimer
import freetime.util.log as ftlog

class Heartbeat(object, ):
    ST_IDLE = 0
    ST_START = 1
    ST_STOP = 2

    def __init__(self, target, interval):
        pass

    def start(self):
        pass

    def stop(self):
        pass

    @property
    def count(self):
        pass

    def postCall(self, func, *args, **kwargs):
        pass

    def postTask(self, task):
        pass

    def _onInit(self):
        pass

    def _onTimeout(self):
        pass

    def _scheduleTimer(self):
        pass

    def _processPostTaskList(self):
        pass

class HeartbeatAble(object, ):

    def __init__(self, interval):
        pass

    def startHeart(self):
        pass

    def stopHeart(self):
        pass

    def onInit(self):
        pass

    def onHeartbeat(self):
        pass

    def _doInit(self):
        pass

    def _doHeartbeat(self):
        pass

class Logger(object, ):

    def __init__(self, kvs=None):
        pass

    def add(self, k, v):
        pass

    def hinfo(self, prefix=None, *args):
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