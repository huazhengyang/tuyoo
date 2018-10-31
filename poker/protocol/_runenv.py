# -*- coding: utf-8 -*-
"""
Created on 2015-5-12
@author: zqh
"""
from freetime.core.lock import FTLock
import freetime.util.log as ftlog
_CMD_RPC_ = 'rpc'
_RPC_TIME_OUT = 6
_rpc_methods = {}
_FTLOCKS = {}
_cmd_path_methods = {}
_cmd_path_rpc_methods = {}

def _lockResource(lockName, lockval, relockKey):
    pass

def _unLockResource(ftlock):
    pass