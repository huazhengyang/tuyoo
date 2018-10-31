# -*- coding: utf-8 -*-
import stackless
from freetime.core.exception import FTException
from freetime.util import log as ftlog
from freetime.util import performance
from freetime.util.defertool import setDefaultCallbackSimple
_NOWAITCMDS_ = frozenset(['SET', 'SETEX', 'HSET', 'HMSET', 'LPUSH', 'SREM', 'EXPIRE', 'set', 'setex', 'hset', 'hmset', 'lpush', 'srem', 'expire'])
_REDIS_PERFORMANCE = 1

def _runCmdRedisSlow_(fun, argl, argd):
    pass

def _runCmdTxRedis(redis_conn, *argl, **argd):
    pass

def _sendCmdTxRedis(redis_conn, *argl, **argd):
    pass

def _runCmdTxRedis_(redis_conn, *argl, **argd):
    pass
sendCmd = _sendCmdTxRedis
if _REDIS_PERFORMANCE:
    runCmd = _runCmdTxRedis_
else:
    runCmd = _runCmdTxRedis

def closeAllRedis(redis_pool_map):
    pass

def doRedis(poolname, *argl, **argd):
    pass