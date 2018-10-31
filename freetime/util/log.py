# -*- coding: utf-8 -*-
import os
"""
使用twisted的日志系统，纪录按天滚动的日志文件
对缺省日志格式做了修改：
  - 时间精确到微秒
  - 中括号里纪录了tasklet标识
"""
from datetime import datetime
from functools import wraps
import stackless
import sys
import time
import traceback
LOG_LEVEL_DEBUG = 0
LOG_LEVEL_INFO = 1
LOG_LEVEL_ERROR = 2
log_level = 0
log_file_opend = 0
_tracemsg = []

def initLog(log_file, log_path, loglevel=0):
    pass

def openNormalLogfile(log_file_fullpath):
    pass

def _log(*argl, **argd):
    pass

def trace(*argl, **argd):
    """
    这个方法仅用于initLog方法之前进行日志打印, 仅仅由freetime代码进行使用
    """
    pass

def trace_stdout(*argl, **argd):
    pass

def _logFunc(*argl, **argd):
    pass

def info(*argl, **argd):
    pass

def hinfo(*argl, **argd):
    pass

def warn(*argl, **argd):
    pass

def debug(*argl, **argd):
    pass

def error(*argl, **argd):
    pass

def errorInfo(*argl, **argd):
    pass

def _getSourceCodes(lines):
    pass

def sendException(errorInfos):
    pass
exception = error

def stack(*argl, **argd):
    pass

def format_exc(limit=None):
    pass

def is_debug():
    pass

def getMethodName():
    pass

def catchedmethod(func):
    pass

def testSendBi(url, header, data):
    pass
_log_server_idx = 0

def sendHttpLog(group, log_type, log_record):
    pass