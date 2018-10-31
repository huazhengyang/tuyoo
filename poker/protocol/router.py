# -*- coding: utf-8 -*-
"""
Created on 2015-5-12
@author: zqh
"""
import random
from freetime.entity.msg import MsgPack
from freetime.support.tcpagent import wrapper
import freetime.util.log as ftlog
from poker.entity.configure import gdata, pokerconf, configure
from poker.protocol import oldcmd, _runenv
import stackless
from poker.util import strutil

class _RouterServer:

    def __init__(self, sids=None, srvType=None):
        pass
_connServer = _RouterServer()
_utilServer = _RouterServer()
_httpServer = _RouterServer()
_sdkHttpServer = _RouterServer()
_gatewayHttpServer = _RouterServer()
_robotServer = _RouterServer()
_centerServer = _RouterServer()
_agentServer = _RouterServer()
_cmd_route_map = {}
_cmd_notuse_map = set()
_cmd_group_match_set = set()

def _initialize():
    """
    初始化命令路由
    """
    pass

def _initialize_udp():
    pass

def sendToAll(msgpack, serverType='', head2=''):
    pass

def isQuery():
    pass

def responseQurery(msgpack, userheader1=None, userheader2=None):
    """
    响应"查询请求"的进程内部消息命令, 即: query->response
    """
    pass

def _communicateServer(rsrv, groupId, userId, msgpack, head1, isQuery, timeout=None, notimeoutex=0):
    pass

def sendToUser(msgpack, userId):
    """
    发送消息至用户的客户端
    """
    pass

def sendToUsers(msgpack, userIdList):
    """
    发送消息至一组用户的客户端
    """
    pass

def sendConnServer(msgpack, userId=0):
    """
    发送消息至CONN服务, 若userId大于0, 那么按照userId取模获得CONN进程, 否则随机选择一个CONN进程进行发送
    """
    pass

def queryConnServer(msgpack, userId=0):
    """
    发送查询请求消息至CONN服务, 若userId大于0, 那么按照userId取模获得CONN进程, 否则随机选择一个CONN进程进行发送
    返回CONN的响应消息
    """
    pass

def sendUtilServer(msgpack, userId=0):
    """
    发送消息至UTIL服务, 若userId大于0, 那么按照userId取模获得UTIL进程, 否则随机选择一个UTIL进程进行发送
    """
    pass

def queryUtilServer(msgpack, userId=0):
    """
    发送查询请求消息至UTIL服务, 若userId大于0, 那么按照userId取模获得UTIL进程, 否则随机选择一个UTIL进程进行发送
    返回UTIL的响应消息
    """
    pass

def sendRobotServer(msgpack, userId=0):
    """
    发送消息至ROBOT服务, 若userId大于0, 那么按照userId取模获得ROBOT进程, 否则随机选择一个ROBOT进程进行发送
    """
    pass

def queryRobotServer(msgpack, userId=0):
    """
    发送查询请求消息至ROBOT服务, 若userId大于0, 那么按照userId取模获得ROBOT进程, 否则随机选择一个ROBOT进程进行发送
    返回ROBOT的响应消息
    """
    pass

def sendCenterServer(msgpack, logicName):
    """
    发送消息至CENTER服务
    """
    pass

def sendCenterServerBySid(msgpack, sid, logicName):
    """
    发送消息至CENTER服务, 指定sid
    """
    pass

def queryCenterServer(msgpack, logicName):
    """
    发送查询请求消息至CENTER服务
    返回CENTER的响应消息
    """
    pass

def sendHttpServer(msgpack, userId=0):
    """
    发送消息至HTTP服务, 若userId大于0, 那么按照userId取模获得HTTP进程, 否则随机选择一个HTTP进程进行发送
    """
    pass

def queryHttpServer(msgpack, userId=0):
    """
    发送查询请求消息至HTTP服务, 若userId大于0, 那么按照userId取模获得HTTP进程, 否则随机选择一个HTTP进程进行发送
    返回HTTP的响应消息
    """
    pass

def __changeMsgRoomId(msgpack, newRoomId, clientRoomId):
    """

    """
    pass

def _communicateRoomServer(userId, roomId, msgpack, head1, isQuery, timeout=None, notimeoutex=0):
    pass

def sendRoomServer(msgpack, roomId):
    """
    发送一个消息至指定的房间处理进程
    """
    pass

def queryRoomServer(msgpack, roomId):
    """
    发送一个查询请求消息至指定的房间处理进程, 并返回目标进程的响应消息
    """
    pass

def sendTableServer(msgpack, roomId):
    """
    发送一个消息至指定的桌子处理进程
    """
    pass

def queryTableServer(msgpack, roomId):
    """
    发送一个查询请求消息至指定的桌子处理进程, 并返回目标进程的响应消息
    """
    pass

def __getRoomIdByTableId(msgpack):
    """

    """
    pass

def _communicateTableServer(userId, roomId, msgpack, head1, isQuery, timeout=None, notimeoutex=0):
    pass

def routeConnTcpMsg(cmd, userId, roomId, msgpack):
    """
    CONN服务调用, 路由消息到其他的服务
    """
    pass

def filterCmdAct(cmd, userId, roomId, msgpack):
    pass

def routeConnTcpMsgQuery(cmd, userId, roomId, msgpack):
    """
    CONN服务调用, 路由消息到其他的服务
    """
    pass

def _remoteCall(markParams, argl, argd):
    pass