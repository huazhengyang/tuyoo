# -*- coding: utf-8 -*-
import sys, os, shutil
import time, datetime
import redis
import json
import traceback
BI_RECORD_EXTRA_SIZE = 17
BIN_PATH = '/home/miaoyc/source/freetime/freetime/support/logserver/script'
redis_pool_map = {}
log_type_map = {}
global_config = {}
today = time.strftime('%Y%m%d')

def run(**argd):
    pass

def _initFromRedis(conf):
    pass

def move_old_file(datadir_path, datadir_backuppath, log_type, log_group, record_count, days_ago_move, redisHandler):
    pass

def move_and_create_file(datadir_path, datadir_backuppath, log_type_map, redis_pool_map):
    pass

def writeFile(findex, absPath, record_size, record_count):
    pass

def writeNewFiles(dir_path, log_type, group, record_size, record_count, pre_create_file_nums, redisHandler):
    pass

def getNDaysAgoLogFileIndex(n, redisHandler, log_type, group, record_count):
    pass

def getNDayAgo(n):
    pass

def _initRedis(redis_pool_map):
    pass
if (__name__ == '__main__'):
    if (len(sys.argv) != 4):
        print 'Usage:pypy daily.py <config_redis_ip> <config_redis_port> <config_redis_dbid>'
        sys.exit((-1))
    _conf_ip = sys.argv[1]
    _conf_port = int(sys.argv[2])
    _conf_dbid = int(sys.argv[3])
    run(config_redis=(_conf_ip, _conf_port, _conf_dbid))
    sys.exit(0)