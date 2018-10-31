# -*- coding: utf-8 -*-
import stackless
from freetime.core.timer import FTTimer
from freetime.util import log as ftlog, defertool
_keep_count = 0
_keep_alive_seconds = 60

def query(mysqlconn, sqlstr, sql_arg_list=[]):
    pass

def _keepAlive():
    pass

def keepAlive(mysql_pool_map):
    pass

def closeAllMysql(mysql_pool_map):
    pass