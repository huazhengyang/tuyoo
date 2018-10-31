# -*- coding: utf-8 -*-
import time
from poker.util.reflection import TYClassRegister
import freetime.util.log as ftlog

class TYActivityRegister(TYClassRegister, ):
    _typeid_clz_map = {}

class TYActivityEventRegister(TYClassRegister, ):
    _typeid_clz_map = {}

class TYActivitySystem(object, ):

    def reloadConf(self):
        pass

class TYActivity(object, ):
    TYPE_ID = 0

    def __init__(self, dao, clientConfig, serverConfig):
        pass

    def checkOperative(self):
        pass

    def getConfigForClient(self, gameId, userId, clientId):
        """
        活动模板的配置
        即：
            本次活动的配置
        """
        pass

    def handleRequest(self, msg):
        pass

    def reload(self, config):
        pass

    def getid(self):
        pass

    def finalize(self):
        pass