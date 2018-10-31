# -*- coding:utf-8 -*-

import time, random
import freetime.util.log as ftlog
from hall.servers.common.base_http_checker import BaseHttpMsgChecker
from poker.protocol.decorator import markHttpHandler, markHttpMethod
from poker.protocol import runhttp
from freetime.entity.msg import MsgPack
from hall.servers.util.rpc import echo


@markHttpHandler
class PerfProbeHttpHandler(BaseHttpMsgChecker):
    @markHttpMethod(httppath='/v2/game/support/echoperfprobe')
    def doPerfProbe(self):
        ftlog.debug('doPerfProbe')
        userId = runhttp.getParamInt('userId')
        mo = MsgPack()
        mo.setCmd('prefprobe')
        mo.setResult('userId', userId)
        mo.setResult('echoUT', self._doPerfEcho_UT(userId))
        mo.setResult('echoUTRedis', self._doPerfEcho2_UT(userId))
        return mo

    def _doPerfEcho_UT(self, userId):
        start = self._unixtime()
        r = echo.echo(userId, 'perf')
        end = self._unixtime()
        if r is None:
            return 'error'
        else:
            return {
                'timecost': end - start
            }

    # include redis I/O from UT
    def _doPerfEcho2_UT(self, userId):
        start = self._unixtime()
        result = echo.echoWithRedisIO(userId, str(random.randint(0, 10000)))
        end = self._unixtime()
        if result is None:
            return 'error'
        else:
            return {
                'timecost': end - start,
                'dbcosts': result
            }

    def _unixtime(self):
        return int(round(time.time() * 1000))
