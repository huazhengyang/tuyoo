# -*- coding: utf-8 -*-
import json
from twisted.enterprise import adbapi
from twisted.internet import defer, reactor
from twisted.internet.protocol import Factory
from twisted.web.http import HTTPFactory
import freetime.aio.mysql as ftmysql
import freetime.aio.redis as ftred
from freetime.core.protocol import FTUDPQueryProtocol
from freetime.util.cache import lfu_cache
import freetime.util.log as ftlog
from freetime.util.metaclasses import MultiDict, MultiList
redis_pool_map = {}
redis_config_map = {}
_redis_pool_count = 0
mysql_pool_map = {}
server_map = {}
client_query_udp_map = {}
server_type_map = MultiDict()
global_config = {}
serverid_protocol_map = {}

def initFromRedis(svrid, conf):
    pass

def _initByData(svrid, sc, rc, glc, conf):
    pass

def _initServerMap(serverconf):
    pass

@defer.inlineCallbacks
def _initRedisPool(name, h, p, dbid, size):
    pass

def _initRedisPoolMap(sid, conf, redisconf):
    pass

def _initMysqlPool(name, dbhost, dbport, dbname, dbuser, dbpwd):
    pass

def _initMysqlPoolMap(sid, conf, mysqlconf):
    pass

def getServerConf(sid):
    pass

@lfu_cache(maxsize=1000, cache_key_args_index=0)
def getConf(confname):
    pass

def getConfNoCache(*cmds):
    pass

def _init_query_udp(target_svr_id, target_pro_name):
    pass

def protoParser(protos, proto_func, ptype):
    """
        根据server.json中配置的server和client字段，进行
        监听和连接操作
        #service server protocol config example:
        "protocols": { 
            "server":{"co-udp":5000, "co-tcp":5001},
            "client":{"query-udp":["LO*:co-udp"]}
        } 
        这里只处理业务进程的protocol，
        Agent的相关处理在support.tcpagent.wrapper中
    """
    pass