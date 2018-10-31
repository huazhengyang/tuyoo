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
class MasterTcpHandler(BaseMsgPackChecker):

    
    def __init__(self):
        pass
    
    
    @markCmdActionMethod(cmd='master', action="get_rank", clientIdVer=0)
    def doMasterGetRank(self):
        msg = runcmd.getMsgPack()
        ftlog.error('NotImplementedError, doMasterGetRank, msg=', msg)
        return runcmd.newOkMsgPack(code=1)


