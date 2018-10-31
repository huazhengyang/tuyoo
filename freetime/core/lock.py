# -*- coding: utf-8 -*-
from contextlib import contextmanager
import functools
import inspect
import stackless
import time
import uuid
from functools import wraps
from freetime.aio.redis import doRedis
import freetime.util.log as ftlog
from twisted.internet import reactor
_NEED_TIMEOUT = 1

class FTLockTimeOutException(Exception, ):
    pass

class FTLock(stackless.channel, ):

    def __init__(self, lockkey, relockKey=None):
        pass

    @property
    def isLocked(self):
        pass

    def lock(self, relockKey=None, lockTimeout=60):
        pass

    def _timeOut(self):
        pass

    def unlock(self):
        pass

def locked(func):
    """
       only used for object method
       
       e.g :
        
        class Room(object) : 
            def __init__(self):
                self.locker = FTLock(self.__class__.__name__ + "_%d" % id(self))
                
            @locked
            def syncChooseTableAndSit(self, userId):
                pass
    """
    pass

@contextmanager
def lock(locker):
    """
        with lock(room.locker) :
            ...
    """
    pass

class FTRedLockException(Exception, ):
    pass

class FTRedLock:
    UNLOCK_LUA = 'if redis.call("get",KEYS[1]) == ARGV[1] then\n        return redis.call("del",KEYS[1])\n    else\n        return 0\n    end\n    '
    UNLOCK_SHA = None

    def __init__(self, lockname, timeout=150.0):
        pass

    def lock(self):
        pass

    def unlock(self):
        pass

def ftredlock(lock_name_head, lock_name_tails=[], timeout=150.0):
    """
       
       e.g : 
        @ftredlock('table_data_lock', ['gameid', 'roomid', 'tableid'], 3.0)
        def syncChooseTableAndSit(self, gameid, roomid, tableid, userid):
    """
    pass