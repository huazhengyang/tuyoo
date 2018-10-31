# -*- coding=utf-8

import freetime.util.log as ftlog
from poker.entity.events.tyevent import EventHeartBeat


_initialize_ok = 0

def _initialize(isCenter):
    ftlog.debug('HallLotter initialize begin', isCenter)
    global _initialize_ok
    if not _initialize_ok :
        _initialize_ok = 1
        if isCenter :
            from poker.entity.events.tyeventbus import globalEventBus
            globalEventBus.subscribe(EventHeartBeat, onTimer)
    ftlog.debug('HallLotter initialize end')


def onTimer(evt):
    ftlog.debug('halllottery', evt.count)
