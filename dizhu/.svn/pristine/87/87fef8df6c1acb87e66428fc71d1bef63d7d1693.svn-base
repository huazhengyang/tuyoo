# -*- coding: utf-8 -*-
'''
Created on 2015年5月20日

@author: zqh, Zhouhao
'''


import freetime.util.log as ftlog
from poker.entity.configure import gdata
from poker.protocol import runcmd, router
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod
from hall.servers.common.base_checker import BaseMsgPackChecker


@markCmdActionHandler
class TableTcpHandler(BaseMsgPackChecker):
    @markCmdActionMethod(cmd='room', action="quick_start", clientIdVer=0, scope='game')
    def doRoomQuickStart(self, roomId, tableId0, userId):
        msg = runcmd.getMsgPack()
        ftlog.debug('msg=', msg, caller=self)
        gdata.rooms()[roomId].doQuickStart(msg)
        if router.isQuery() :
            mo = runcmd.newOkMsgPack(1)
            router.responseQurery(mo, '', str(userId))
        
