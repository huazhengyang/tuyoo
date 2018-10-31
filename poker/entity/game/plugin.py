# -*- coding: utf-8 -*-
"""

"""
__author__ = ['Wang Tao', 'Zhou Hao']
import importlib
import sys
import freetime.util.log as ftlog
from freetime.util.log import catchedmethod, getMethodName
from freetime.entity.msg import MsgPack
from poker.entity.configure import configure
from poker.protocol import router
from poker.entity.configure import gdata
_DEBUG = 0
debug = ftlog.info

class TYPluginUtils(object, ):

    @classmethod
    def updateMsg(cls, msg=None, cmd=None, params=None, result=None, **other):
        pass

    @classmethod
    def mkdict(cls, **kwargs):
        pass

    @classmethod
    def sendMessage(cls, gameId, targetUserIds, cmd, result, logInfo=True):
        pass

    @classmethod
    def makeHandlers(cls, handlerClass, events):
        """

        """
        pass

class TYPlugin(object, ):

    def __init__(self, gameId, cfg):
        pass

    @catchedmethod
    def onReload(self):
        pass

    def __str__(self):
        pass

    def __repr__(self):
        pass

class TYPluginCenter(object, ):
    plugins = {}
    config_reload_flag = {}
    map_events = {}
    EV_CHAIN_STOP = 'EV_CHAIN_STOP'

    @classmethod
    def event(cls, msg, gameId):
        """

        """
        pass

    @classmethod
    def evmsg(cls, gameId, cmd, params=None, result=None, receivers=None):
        pass

    @classmethod
    def get_plugin(cls, name, gameId):
        pass

    @classmethod
    @catchedmethod
    def reload(cls, gameId, handler_name='', handler_names=[], handlers_config=None):
        """
        reload 某个 gameId 的插件

        @handlers_names: 指定要reload哪些plugin。不指定就reload所有（plugins越来越多，会比较慢）

        不管有没有指定 reload 哪些插件，都会重新 build 事件表。
        为什么不优化为只处理指定的plugins的事件？
        没有必要，性能瓶颈不在这，而且全部重新build一定不会出问题，而且的而且，那样做会增加复杂性。
        """
        pass

    @classmethod
    @catchedmethod
    def unload(cls, gameId, handler_names=None):
        """

        """
        pass

    @classmethod
    def buildEventMap(cls, gameId, plugins, handlers_config, map_events):
        pass

    @classmethod
    def isOtherGameServer(cls, gameId):
        """

        """
        pass

    @classmethod
    def needLoadPlugin(cls):
        pass