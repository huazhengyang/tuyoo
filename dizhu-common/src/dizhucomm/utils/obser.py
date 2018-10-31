# -*- coding:utf-8 -*-
'''
Created on 2016年12月21日

@author: zhaojiangang
'''

import time
import freetime.util.log as ftlog

class EventBase(object):
    def __init__(self):
        self.timestamp = None

def EventHandler(event):
    pass

class Observable(object):
    # key=eventType, value=EventHandler
    _listenerMap = None

    def on(self, eventType, handler):
        self.addListener(eventType, handler)
        
    def off(self, eventType, handler):
        self.removeListener(eventType, handler)
        
    def addListener(self, eventType, handler):
        if not self._listenerMap:
            self._listenerMap = {}
        
        ls = self._listenerMap.get(eventType)
        if not ls:
            ls = []
            self._listenerMap[eventType] = ls
        
        ls.append(handler)
        return self
    
    def removeListener(self, eventType, handler):
        if self._listenerMap:
            ls = self._listenerMap.get(eventType)
            try:
                ls.remove(handler)
            except:
                pass
        return self
    
    def removeAllListener(self, eventType):
        if self._listenerMap:
            self._listenerMap.pop(eventType, None)
    
    def fire(self, event):
        assert(isinstance(event, EventBase))
        event.timestamp = time.time()
        eventType = type(event)
        if self._listenerMap:
            ls = self._listenerMap.get(eventType)
            if ls:
                for l in ls:
                    try:
                        l(event)
                    except:
                        ftlog.error('Observable.fire',
                                    'eventType=', type(event),
                                    'event=', event.__dict__)
        return self


