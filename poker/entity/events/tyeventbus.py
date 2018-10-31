# -*- coding: utf-8 -*-
"""
Created on 2014年2月20日

@author: zjgzzz@126.com
"""
import time
from freetime.util import log as ftlog
from poker.entity.configure import gdata
from poker.entity.events.tyevent import TYEvent
from freetime.core.tasklet import FTTasklet

class TYEventBus(object, ):

    def __init__(self):
        pass

    def subscribe(self, eventType, handler):
        """

        """
        pass

    def unsubscribe(self, eventType, handler):
        """

        """
        pass

    def publishEvent(self, event, handleDelay=0, eventErrors=None, **argd):
        """
        发布一个event, 同一个event不允许重复
        """
        pass

    def _sleepnb(self, handleDelay):
        pass

    def _processEvent(self, event, handleDelay=0, eventErrors=None, **argd):
        pass
globalEventBus = TYEventBus()