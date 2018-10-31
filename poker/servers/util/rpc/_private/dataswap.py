# -*- coding: utf-8 -*-
"""
Created on 2015-12-2
@author: zqh
"""
import freetime.util.log as ftlog
from poker.entity.configure import pokerconf, configure
from poker.entity.dao import daobase, daoconst
from poker.servers.util.rpc import dbmysql
from poker.servers.util.rpc._private import dataswap_scripts
from poker.util import strutil, timestamp
from freetime.entity import config
mysqlsize = (-1)

def getMysqlSize():
    pass

def checkUserData(userId, clientId=None, appId=0):
    """
    检查当前用户的数据是否是热数据(即存储在REDIS), 
    如果不是热数据, 那么重MYSQL中读取冷数据导入至热数据中
    同时更新当前用户的数据生命时间
    导入导出的用户数据包括user和个个游戏的所有数据
    返回:
        如果用户数据的最终状态为热数据,返回1
        如果用户数据不存在,返回0
    """
    pass

def _tryReadDataFromMySql(userId, intClientId, appId, ctfull):
    pass