# -*- coding: utf-8 -*-
from freetime.support.logserver.protocol import http
from freetime.support.logserver.protocol import tcp
"""
from http import MyHttpChannel
from udp import MyProto
from udp import EchoProto
from tcp import S2AProto
"""
"""
demo.protocol模块是开发业务逻辑的主要扩展点,
您需要在_class_map中，给您自己扩展出的protocol指定一个shortname，
然后在server.json里，针对端口配置这个shortname，
例如：
   ... "protocols": { "co-udp":5002, "co-tcp":5003 }, ...

注：对于通过tcpagent跟外界通信的服务，server2agent协议必须实现
    并配置到server.json的protocols.client字段，例如:
        "protocols": {
            "server":...
            "client":{"s2a":"AG02:a4s",...}
        }
    framework会使用s2a这个名字对应的protocol去连接指定的Agent
"""
_class_map = {'indexer-http': http.IndexHttpChannel, 's2a': tcp.WriteTcpRequest}

def getProtoClassByName(name):
    pass