# -*- coding: utf-8 -*-
from twisted.internet import reactor
import stackless
import freetime.aio.http as fthttp
import freetime.aio.redis as ftred
import freetime.aio.mysql as ftmysql
import freetime.aio.udp as ftudp
from freetime.core.reactor import mainloop, exitmainloop, REACTOR_RUN_NORMAL
from freetime.core.tasklet import FTTasklet, _tasklet_schedule_cb
import freetime.entity.config as ftcon
import freetime.support.tcpagent.wrapper as ftagent
import freetime.util.log as ftlog
from freetime.core.exception import FTException
_init_fun = None

def doMySql(poolname, sqlstr, sql_arg_list=[]):
    pass

def doRedis(poolname, *argl, **argd):
    pass

def doHttp(method, url, header={}, body='', conntimeout=2, timeout=2):
    pass

def doUdpQuery(target_server_id, data, timeout=1):
    pass

def getId():
    pass

def getTaskUdpSrc():
    pass

def getTaskPack():
    pass

def getTaskRunArg():
    pass

def getConcurrentTaskCount():
    pass

def _initProtocol(sid, proto_func):
    pass

def _runServiceById(sid, proto_func):
    pass

def _runInitFun():
    pass

def run(*argl, **argd):
    pass

def terminate():
    pass