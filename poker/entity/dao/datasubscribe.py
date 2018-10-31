# -*- coding: utf-8 -*-
"""
Created on 2013-3-18

@author: Administrator
"""
from freetime.core.timer import FTLoopTimer
from freetime.entity import config
import freetime.util.log as ftlog
from freetime.util.txredis import subscribe
from poker.entity.configure import gdata
from poker.entity.dao import userdata

def _initialize():
    pass

def _userdatachange(userId):
    pass

def _onSubMessage(channel, message):
    pass