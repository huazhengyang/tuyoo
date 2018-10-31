# -*- coding: utf-8 -*-
'''
Created on 2015年5月20日

@author: zqh
'''


import freetime.util.log as ftlog
from poker.protocol import runcmd
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod
from hall.servers.common.base_checker import BaseMsgPackChecker


@markCmdActionHandler
class ComplainTcpHandler(BaseMsgPackChecker):

    
    def __init__(self):
        pass
    
    
    @markCmdActionMethod(cmd='complain', action="complain", clientIdVer=0)
    def doComplain(self):
        msg = runcmd.getMsgPack()
        ftlog.error('NotImplementedError, doComplain, msg=', msg)
        return runcmd.newOkMsgPack(code=1)


    


