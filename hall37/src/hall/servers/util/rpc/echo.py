# -*- coding=utf-8

from poker.protocol.rpccore import markRpcCall
from poker.entity.dao import daobase
import time, json


@markRpcCall(groupName="userId", lockName="userId", syncCall=1)
def echo(userId, whatever):
    if whatever is None:
        whatever = ''
    return whatever


@markRpcCall(groupName="userId", lockName="userId", syncCall=1)
def echoWithRedisIO(userId, toRedis):
    if not isinstance(toRedis, (int, str)):
        toRedis = json.dumps(toRedis)
    ret = {}

    def _unixtime():
        return int(round(time.time() * 1000))

    def _recordPref(name, redisExecutor):
        perfkey = 'echo:perf:%s' % name
        try:
            start = _unixtime()
            redisExecutor('HSET', perfkey, 'content', toRedis)
            end = _unixtime()
            writetime = end - start
            start = _unixtime()
            redisExecutor('HGET', perfkey, 'content')
            end = _unixtime()
            readtime = end - start

            ret[name] = (writetime, readtime)
        except Exception, e:
            ret[name] = 'error'
        finally:
            redisExecutor('DEL', perfkey)

    _recordPref('dizhu', daobase.executeDizhuCmd)
    _recordPref('mix', daobase.executeMixCmd)
    _recordPref('rank', daobase.executeRankCmd)

    def executeUserCmdWrapper(*cmds):
        daobase.executeUserCmd(int(userId), *cmds)

    def executeTableCmdWrapper(*cmds):
        daobase.executeTableCmd(1, 1, *cmds)

    _recordPref('user', executeUserCmdWrapper)
    _recordPref('table', executeTableCmdWrapper)
    _recordPref('replay', daobase.executeRePlayCmd)
    _recordPref('online', daobase._executeOnlineCmd)
    _recordPref('bi', daobase._executeBiCmd)
    _recordPref('keymap', daobase._executeKeyMapCmd)
    _recordPref('paydata', daobase._executePayDataCmd)
    _recordPref('geo', daobase._executeGeoCmd)

    return ret
