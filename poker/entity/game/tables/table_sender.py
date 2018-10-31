# -*- coding: utf-8 -*-
"""

"""
__author__ = ['Zhaoqh"Zhouhao" <zhouhao@tuyoogame.com>']
from freetime.entity.msg import MsgPack
from freetime.util import log as ftlog
from poker.protocol import router

class TYTableSender(object, ):
    """
    桌子使用的发送消息的工具集合类
    """

    def __init__(self, table):
        pass

    def createMsgPackRes(self, cmd, action=None):
        pass

    def createMsgPackRequest(self, cmd, action=None):
        pass

    def sendToAllTableUser(self, mo, exclude=None):
        pass

    def sendQuickStartRes(self, userId, clientId, result):
        pass

    @classmethod
    def sendNotifyMsg(cls, gameId, uid, showTime, content):
        """
        {
            "cmd": "notifyMsg",
            "result":
            {
                "showTime": 0.5,
                "content": [{
                    "color": "RRGGBB",
                    "text": "bababababa"
                }, {
                    "color": "RRGGBB",
                    "text": "bababababa"
                }]
            }
        }
        """
        pass

    def sendRoomLeaveReq(self, userId, reason, needSendRes=True):
        pass

    def sendRobotNotifyCallUp(self, params):
        pass

    def sendRobotNotifyShutDown(self, params):
        pass