# -*- coding: utf-8 -*-
"""
Created on 2015-5-12
@author: zqh
"""
import sys
import functools
from poker.protocol import router
from freetime.util.metaclasses import Singleton
_CLASS_MARKE = '_mark_handler_type_'
_METHOD_MARKE = '_mark_method_params_'

def markHttpHandler(clazz):
    """
    标记一个class为HTTP命令的入口类
    """
    pass

def markHttpMethod(httppath, jsonp=False, ip_filter=False, responseType='json', scope='global'):
    """
    标记一个方法为HTTP命令的入口, 与@markHttpHandler配合使用
    httppath  HTTP访问的路径
    jsonp 是否进行jsonp的处理
    ip_filter 是否进行IP过滤处理, 如果为真, 那么取得当前handler的ip_filter(ip)方法进行IP过滤处理
    responseType HTTP响应的数据格式
    注意: 使用此标记的方法必须为Class的实例方法或静态方法
    """
    pass

def markCmdActionHandler(clazz):
    """
    标记一个class为客户端发送的TCPCMD命令的入口类
    """
    pass

def markCmdActionMethod(cmd, action='', clientIdVer=0.0, lockParamName='userId', scope='global'):
    """
    标记一个方法为TCP命令的入口, 与@markCmdActionHandler配合使用
    cmd  MsgPack中的cmd
    action MsgPack中的params中的action, 若action为空, 那么以为此cmd没有action字段, 若action为*, 那么通配所有的action
    clientIdVer 当前入口的客户端起始版本号(含此版本)
    lockParamName 当前命令在执行时, 锁进行locker的名字, 
        例如: lockParamName='userId', 那么将取得MsgPack中的params['userId'] = 10001,
            建立进程内资源锁: Locker('lockcmd:10001'), 进行资源锁定后再执行相应的方法
    注意: 使用此标记的方法必须为Class的实例方法或静态方法
    """
    pass

def markRpcHandler(clazz):
    """
    标记一个class为服务器之间的RPC调用的入口类
    注意: 作为RPC的类, 那么此类的使用方法为静态类, 不进行实例化处理, 即默认所有该类的方法均是@classmethod
    """
    pass

def markRpcMethod(groupBy='userId', lockParamName='userId', syncCall=1):
    """
    标记一个方法为RPC远程命令的入口, 与@markRpcHandler配合使用
    needReturnValue 标记此远程方法是否需要返回值
    注意: 使用此标记的方法必须为Class的静态方法, 即必须使用@classmethod进行标记
    注意: 作为RPC的类, 那么此类的使用方法为静态类, 不进行实例化处理, 即默认所有该类的方法均是@classmethod
    """
    pass

def _findPyFileListUnderModule(moduleName):
    """
    查找所有的直属的py文件,并进行动态装载，只查当前所属,不递归查找py文件
    """
    pass
__DCLASS_TYPES = (type(object), Singleton)

def _loadDecoratorClass(moduleName, markName):
    """
    动态装载一个模块名称(例如: 'dizhu.servers.http')下的直属py文件(不包涵子目录和__init__.py)
    取得其中所有使用装饰器 @markName 进行装饰过的class类
    返回类集合,key为该类的完整package路径,value为class
    """
    pass

def _findDecoratorMethod(obj, markName):
    """
    再给出的obj实例中, 查找所有使用@markName进行标记的方法
    返回, 方法列表list
    """
    pass

def _loadDecoratorModuleMethods(moduleName, markName):
    pass