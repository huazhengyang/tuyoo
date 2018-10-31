# -*- coding: utf-8 -*-
"""
Created on 2015-5-12
@author: zqh
每个配置项必须是JSON格式
"""
import freetime.entity.config as ftcon
import freetime.util.log as ftlog
from datetime import datetime
from poker.util import strutil
from freetime.core.lock import FTLock, lock
UNKNOW_ID = 0
DEFAULT_CLIENT_ID = 0
CLIENT_ID_TEMPLATE = 'tc'
CLIENT_ID_MATCHER = 'vc'
CLIENTID_RPC = 'Android_3.7_-hall6-RPC'
CLIENTID_SYSCMD = 'Android_3.7_-hall6-SYSCMD'
CLIENTID_ROBOT = 'robot_3.7_-hall6-robot'
_CONFIG_CMD_PPS_ = 0
_CONFIG_CMDS_ = {}
_CONFIG_COUNT_ = 0
_CONFIG_COUNT_TIME_ = datetime.now()

def _configCmdPps(ckey):
    pass

def ppsCountConfigCmds():
    pass

def reloadKeys(keylist):
    pass

def _get(redisfullkey, defaultvalue=None, intClientidNum=None):
    pass

def getUuid():
    """
    取得配置内容的更新的标记, 即配置内容每发生一次变化(由配置脚本或配置界面更新), 此标记变化一次
    其值为一个UUID字符串
    """
    pass

def getJson(redisfullkey, defaultVal=None, intClientidNum=None):
    """
    取得配置系统的一个键值的json对象值(list或dict类型)
    """
    pass

def getGameJson(gameId, key, defaultVal=None, intClientidNum=0):
    """
    取得配置系统的一个游戏相关的键值的json对象值(list或dict类型)
    """
    pass

def stringIdToNumber(datakey, stringid):
    pass
_numDictRevertd = {}

def numberToStringId(datakey, numberId):
    pass

def getTemplateInfo(redisfullkey, intClientId, funconvert=None):
    pass

def getGameTemplateInfo(gameId, key, intClientId, funconvert=None):
    pass

def getTemplates(key, funconvert=None):
    pass

def getGameTemplates(gameId, key, funconvert=None):
    pass

def getConfigGameIds():
    pass

def clientIdToNumber(clientId):
    """
    转换clientID的字符串定义至INTEGER_ID的定义
    """
    pass

def numberToClientId(numberId):
    """
    转换clientID的字符串定义至INTEGER_ID的定义
    """
    pass
_templatesCache = {}
_templatesLockers = {}

def getTcTemplates(moduleKey, funDecode):
    """
    取得配置系统的一个游戏相关的键值的json对象值(list或dict类型)
    """
    pass

def _getTcTemplates(moduleKey, funDecode):
    pass

def getVcTemplate(moduleKey, clientId, gameId=None):
    """
    http://192.168.10.93:8090/pages/viewpage.action?pageId=1868148
    """
    pass

def getTcTemplatesByClientId(moduleKey, funDecode, clientId):
    """
    取得配置系统的一个游戏相关的键值的json对象值(list或dict类型)
    """
    pass

def getTcTemplatesByGameId(moduleKey, funDecode, gameId):
    """
    取得配置系统的一个游戏相关的键值的json对象值(list或dict类型)
    """
    pass

def _getTcTemplatesByModuleKey(moduleKey, funDecode):
    pass

def getTcContent(moduleKey, funDecode, clientId):
    pass

def getTcContentByClientId(moduleKey, funDecode, clientId, defaultVal=None):
    """
    使用clientId中指向的gameId，进行数据查询
    """
    pass

def getTcContentByGameId(moduleKey, funDecode, gameId, clientId, defaultVal=None):
    """
    忽律clientId中指向的gameId，直接使用参数中的gameId进行数据查询
    """
    pass