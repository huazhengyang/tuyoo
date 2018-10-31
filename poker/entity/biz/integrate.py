# -*- coding: utf-8 -*-
"""
Created on 2015年6月3日

@author: zhaoqh
"""
from freetime.entity import clients
import freetime.util.log as ftlog
from poker.entity.configure import pokerconf, gdata
_DEBUG = 0
debug = ftlog.info
_inited = 0

def _initialize():
    pass

def _onConfChanged(event):
    pass

def _reloadConf():
    pass

def _resetIntegrate(adapterKey, integrates):
    pass

def sendTo(adapterKey, dictData, headerDict=None):
    pass

def isEnabled(adapterKey):
    pass