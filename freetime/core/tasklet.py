# -*- coding: utf-8 -*-
import stackless
from twisted.internet import defer, reactor
from channel import FTChannel
import freetime.util.log as ftlog
from freetime.core.reactor import REACTOR_RUN_NORMAL
from time import time
from datetime import datetime
DEBUG_TASK_MAIN_TIME = 0
DEBUG_TASK_SCHEDULE = 0
DEBUG_TASK_MAP = {}
SLOW_TASK_TIMES = 0.2

def _tasklet_schedule_cb(prevTask, nextTask):
    pass

class FTTasklet:
    BUSY_FLAG = 0
    concurrent_task_count = 0
    MAX_CONCURRENT = 4000
    PEAKVALUE = 0
    PEAKTIME = datetime.now()

    def __init__(self, argl, argd):
        pass

    def tasklet(self):
        pass

    def sleepNb(self, timeout):
        pass

    def waitDefer(self, deferred, timeout=0):
        pass

    def _timeout(self, d):
        pass

    @classmethod
    def create(cls, argl, argd):
        pass

    @classmethod
    def _checkBusy(self):
        pass

    @classmethod
    def getCurrentFTTasklet(cls):
        pass

    def _successful(self, resmsg):
        pass

    def _wait_channel(self):
        pass

    def _error(self, fault):
        pass