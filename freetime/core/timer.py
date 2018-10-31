# -*- coding: utf-8 -*-
import sys
from twisted.internet import reactor
from tasklet import FTTasklet
import freetime.util.log as ftlog
import functools
from time import time

class FTTimer:
    """
    封装calllater,启动tasklet的机制...
    """

    def __init__(self, interval, task_handler, *argl, **argd):
        pass

    def _onTime(self):
        pass

    def cancel(self):
        pass

    def isActive(self):
        pass

    def getTimeOut(self):
        pass

    def reset(self, interval):
        pass

class FTLoopTimer:
    """
    封装calllater,启动tasklet的机制...
    loopCount 为－1时，不停止的进行timer触发调用
    loopCount 大于0时，循环触发loopCount次调用
    每次触发均使用新的tasklet进行调用 task_handler(*argl, **argd)
    必须显示调用timer.start()才能启动此timer
    """

    def __init__(self, interval, loopCount, task_handler, *argl, **argd):
        pass

    def __repr__(self):
        pass

    def start(self):
        pass

    def _start(self):
        pass

    def _onTime(self):
        pass

    def _invoke(self):
        pass

    def cancel(self):
        pass

    def getTimeOut(self):
        pass

    def reset(self, interval):
        pass