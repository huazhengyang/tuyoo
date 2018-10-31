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
class ProductTcpHandler(BaseMsgPackChecker):

    
    def __init__(self):
        pass
    
    
    @markCmdActionMethod(cmd='product', action="list", clientIdVer=0)
    def doProductList(self):
        msg = runcmd.getMsgPack()
        ftlog.error('NotImplementedError, doProductList,, msg=', msg)
        return runcmd.newOkMsgPack(code=1)


    @markCmdActionMethod(cmd='product', action="quick", clientIdVer=0)
    def doProductQuick(self):
        msg = runcmd.getMsgPack()
        ftlog.error('NotImplementedError, doProductQuick, msg=', msg)
        return runcmd.newOkMsgPack(code=1)


    @markCmdActionMethod(cmd='product', action="notify", clientIdVer=0)
    def doProductNotify(self):
        msg = runcmd.getMsgPack()
        ftlog.error('NotImplementedError, doProductNotify, msg=', msg)
        return runcmd.newOkMsgPack(code=1)


    @markCmdActionMethod(cmd='product', action="delivery", clientIdVer=0)
    def doProductDelivery(self):
        msg = runcmd.getMsgPack()
        ftlog.error('NotImplementedError, doProductDelivery, msg=', msg)
        return runcmd.newOkMsgPack(code=1)

