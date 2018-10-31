# -*- coding: utf-8 -*-
'''
Created on 2015年5月20日

@author: zqh
'''


import freetime.util.log as ftlog
from freetime.util.metaclasses import Singleton
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod
from poker.protocol import runcmd, router
from freetime.entity.msg import MsgPack
# from hall.entity.hallled import LedUtils


@markCmdActionHandler
class ConnTcpHandler(object):

    __metaclass__ = Singleton

    def __init__(self):
        pass


#     @markCmdActionMethod(cmd='game_public_led', action="", clientIdVer=0, lockParamName='')
#     def doConnGamePublicLed(self):
#         '''
#         给客户端游戏发送引导Led
#         '''
#         msg = runcmd.getMsgPack()
#         ftlog.debug('msg=', msg, caller=self)
#         LedUtils._doGamePublicLed(msg)
#         if router.isQuery() :
#             mo = MsgPack()
#             mo.setCmd('game_public_led')
#             mo.setResult('ok', 1)
#             router.responseQurery(mo, '', '')

