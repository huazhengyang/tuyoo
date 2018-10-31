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
class TaskTcpHandler(BaseMsgPackChecker):

    
    def __init__(self):
        pass
    

    @markCmdActionMethod(cmd='task', action='list', clientIdVer=0)
    def doTaskList(self):
        msg = runcmd.getMsgPack()
        ftlog.error('NotImplementedError, doTaskList, msg=', msg)
        return runcmd.newOkMsgPack(code=1)


    @markCmdActionMethod(cmd='task', action='done', clientIdVer=0)
    def doTaskDone(self):
        msg = runcmd.getMsgPack()
        ftlog.error('NotImplementedError, doTaskDone, msg=', msg)
        return runcmd.newOkMsgPack(code=1)


    @markCmdActionMethod(cmd='task', action='update', clientIdVer=0)
    def doTaskUpdate(self):
        msg = runcmd.getMsgPack()
        ftlog.error('NotImplementedError, doTaskUpdate, msg=', msg)
        return runcmd.newOkMsgPack(code=1)


    @markCmdActionMethod(cmd='task', action='change', clientIdVer=0)
    def doTaskChange(self):
        msg = runcmd.getMsgPack()
        ftlog.error('NotImplementedError, doTaskChange, msg=', msg)
        return runcmd.newOkMsgPack(code=1)


    @markCmdActionMethod(cmd='task', action='reward', clientIdVer=0)
    def doTaskReward(self):
        msg = runcmd.getMsgPack()
        ftlog.error('NotImplementedError, doTaskReward, msg=', msg)
        return runcmd.newOkMsgPack(code=1)
