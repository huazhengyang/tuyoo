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
class PromoteTcpHandler(BaseMsgPackChecker):

    
    def __init__(self):
        pass
    

    @markCmdActionMethod(cmd='promote', action="cancel_code_check", clientIdVer=0)
    def doPromoteInfo(self):
        msg = runcmd.getMsgPack()
        ftlog.error('NotImplementedError, doPromoteInfo, msg=', msg)
        return runcmd.newOkMsgPack(code=1)


    @markCmdActionMethod(cmd='promote', action="code_check", clientIdVer=0)
    def doPromoteCodeCheck(self):
        msg = runcmd.getMsgPack()
        ftlog.error('NotImplementedError, doPromoteCodeCheck, msg=', msg)
        return runcmd.newOkMsgPack(code=1)


    @markCmdActionMethod(cmd='promote', action="get_friend_prize", clientIdVer=0)
    def doPromoteGetFriendPrize(self):
        msg = runcmd.getMsgPack()
        ftlog.error('NotImplementedError, doPromoteGetFriendPrize, msg=', msg)
        return runcmd.newOkMsgPack(code=1)


    @markCmdActionMethod(cmd='promote', action="get_prize", clientIdVer=0)
    def doPromoteGetPrize(self):
        msg = runcmd.getMsgPack()
        ftlog.error('NotImplementedError, doPromoteGetPrize, msg=', msg)
        return runcmd.newOkMsgPack(code=1)


    @markCmdActionMethod(cmd='promote', action="query_prize", clientIdVer=0)
    def doPromoteQueryPrize(self):
        msg = runcmd.getMsgPack()
        ftlog.error('NotImplementedError, doPromoteQueryPrize, msg=', msg)
        return runcmd.newOkMsgPack(code=1)


    @markCmdActionMethod(cmd='promote', action="query_state", clientIdVer=0)
    def doPromoteQueryState(self):
        msg = runcmd.getMsgPack()
        ftlog.error('NotImplementedError, doPromoteQueryState, msg=', msg)
        return runcmd.newOkMsgPack(code=1)

