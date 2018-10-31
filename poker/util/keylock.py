# -*- coding: utf-8 -*-
"""
Created on 2017年3月2日

@author: zhaojiangang
"""
from contextlib import contextmanager
import functools
from stackless import tasklet
import stackless
from freetime.core.lock import FTLock
from freetime.core.reactor import mainloop
from freetime.core.tasklet import FTTasklet
from freetime.core.timer import FTLoopTimer

class KeyLock(object, ):

    def __init__(self):
        pass

    @contextmanager
    def lock(self, key):
        pass

    def _findOrCreateLocker(self, key):
        pass
if (__name__ == '__main__'):

    def needLockFunc(lk, flag, userId):
        pass
    klk = KeyLock()
    FTLoopTimer(1, 1, functools.partial(needLockFunc, klk, 'a', 1)).start()
    FTLoopTimer(2, 1, functools.partial(needLockFunc, klk, 'b', 1)).start()
    stackless.tasklet(mainloop)()
    stackless.run()