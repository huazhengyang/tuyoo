# -*- coding: utf-8 -*-
from poker.entity.configure import gdata
from poker.protocol.rpccore import markRpcCall, RPC_FIRST_SERVERID
from freetime.aio import mysql
import freetime.entity.config as ftcon
import freetime.util.log as ftlog
_MYSQLPIDS = {}

def _getServerIdOfMysql(userId, dbname):
    pass

def _queryMysql00(userId, dbname, sqlstr):
    """
    在拥有mysql的进程中，取得一个进程
    MYSQL只在UT进程进行连接,因MYSQL的请求量不大,为降低MYSQL数据库的连接数,只有ID为1~99的UT进程有MYSQL链接
    """
    pass

@markRpcCall(groupName=RPC_FIRST_SERVERID, lockName='', syncCall=1)
def _queryMysql(serverId, dbname, sqlstr):
    pass

def _get_table_data(datas, row, col):
    pass