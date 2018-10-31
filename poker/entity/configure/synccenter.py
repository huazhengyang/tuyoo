# -*- coding: utf-8 -*-
import time
from freetime.core.tasklet import FTTasklet
import freetime.entity.config as ftcon
import freetime.util.log as ftlog
from poker.entity.configure import gdata
from poker.util import strutil, webpage
from freetime.core.lock import locked
from freetime.core.timer import FTLoopTimer
_DEBUG = 0
if _DEBUG:

    def debug(*argl, **argd):
        pass
else:

    def debug(*argl, **argd):
        pass
_REPORT_OK = 0

def doSyncData(event):
    pass

def _doReportStatus(event):
    pass

class _lockobj:
    pass
_lockobj = _lockobj()

@locked
def _reportOnlineToSdk(_lockobj):
    """
    向当前的SDK服务汇报自己的运行状态
    """
    pass

def _doCheckReloadConfig(event):
    pass
_CHANGE_INDEX = (-1)
_CHANGE_KEYS_NAME = 'configitems.changekey.list'
_LAST_ERRORS = None

def _initialize():
    pass

@locked
def _syncConfigure(_lockobj):
    pass

def _sleepnb(sleepTime=0.01):
    pass

def _reloadConfigLocked(keylist, sleepTime=0.01):
    pass

def _updateRoomDefine(keylist, sleepTime):
    pass