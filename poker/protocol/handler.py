# -*- coding: utf-8 -*-
"""
Created on 2015-5-12
@author: zqh
"""
import inspect
import freetime.util.log as ftlog
from poker.entity.configure import gdata
from poker.protocol import runhttp, decorator, _runenv

def _initializeCommands(gdatas):
    """
    初始化HTTP和TCP, RPC的命令入口, 获取各个游戏的实例的handler进行注册处理
    分游戏自动搜索所需要的handler
    分服务类型自动注册相应的服务handler
    """
    pass

def __isHandlerEnable(handler):
    pass

def __registerHttpMethod(gameId, fullName, handler, method, markParams):
    pass

def __registerCmdActionMethod(gameId, fullName, handler, method, markParamsOrg):
    pass

def __registerLocalRpcMethod(gameId, fullName, handler, method, markParamsOrg):
    pass

def __registerRemoteRpcMethod(gameId, serverType, fullName, handler, method, markParams):
    pass