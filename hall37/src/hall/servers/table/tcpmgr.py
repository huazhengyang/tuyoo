# -*- coding: utf-8 -*-
'''
Created on 2015年5月20日

@author: zqh
'''


from hall.servers.common.mgr_tcp_handler import BaseManagerTcpHandler
from poker.protocol.decorator import markCmdActionHandler


@markCmdActionHandler
class ManagerTcpHandler(BaseManagerTcpHandler):


    def __init__(self):
        pass
    
