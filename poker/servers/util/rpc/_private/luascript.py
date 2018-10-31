# -*- coding: utf-8 -*-
"""
Created on 2015-12-2
@author: zqh
"""
import freetime.util.log as ftlog
from poker.entity.dao import daobase
from poker.servers.util.rpc._private import dataswap_scripts, user_scripts

def _initialize():
    """
    初始化当前模块的业务逻辑，此方法被动态收集并调用，无需显示调用此方法
    """
    pass