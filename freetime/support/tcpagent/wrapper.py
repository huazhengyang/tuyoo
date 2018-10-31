# -*- coding: utf-8 -*-
"""
收集管理agent相关的方法:
    初始化普通进程和Agent进程的监听和连接
    以及封装send,query,response三个基本方法
"""
import random, sys
import stackless
from twisted.internet import reactor
from twisted.internet.protocol import Factory
import freetime.entity.config as ftcon
from freetime.support.tcpagent.factory import FTReconnectFactory
import freetime.support.tcpagent.msg as agentmsg
from freetime.support.tcpagent.protocol import A2AProtocol
from freetime.support.tcpagent.protocol import A2SProtocol
import freetime.util.log as ftlog
from time import time
from freetime.util import performance

def connect_agent_eachother(server_id):
    """
    Agent进程调用，监听自己的端口，并与其他Agent建立连接
    """
    pass

def connect_agent(server_id, proto_func):
    """
    Service进程调用，连接配置的Agent
    """
    pass

def send(dst, data, userheader1='', userheader2=''):
    pass
_QUERY_SLOW_TIME = 0.25

def query(dst, data, userheader1='', userheader2='', timeout=2, notimeoutex=0, returnDeffer=0):
    pass

def isQuery():
    pass

def response(data, userheader1=None, userheader2=None):
    pass

def _response(dst, data, queryid, userheader1, userheader2):
    pass
"""

#getServerId是一个例子, 说明如何取得要路由的serverid

def getServerId(cmd, server_type = '', arg_dict = {}):
    server_id = 0

    if server_type == '': # 按cmd get server_type
        server_type = ftcon.cmd_route_map.get(cmd, '')

    if server_type == '':
        ftlog.error('cmd route error, cmd=', cmd)
        return ''

    serverids = ftcon.server_type_map[server_type]

    if not arg_dict.has_key('mode'):
        ftlog.info('arg_dict not exist mode, default by random')
        server_id = random.choice(serverids)
    else:
        mode = arg_dict['mode']
        if mode == 1:
            server_id = random.choice(serverids)
        elif mode == 2:
            if arg_dict.has_key('userheader'):
                userheader = arg_dict['userheader']
                index = userheader % len(serverids)
                server_id = serverids[index]
            else:
                server_id = random.choice(serverids)
        else:
            server_id = random.choice(serverids)
    return server_id
"""