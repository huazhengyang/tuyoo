# -*- coding: utf-8 -*-
"""

"""
__author__ = ['Zhaoqh"Zhouhao" <zhouhao@tuyoogame.com>']
import freetime.util.log as ftlog
from poker.entity.dao import onlinedata, sessiondata
from poker.entity.game.rooms.room import TYRoom
from poker.entity.game.tables.table_timer import TYTableTimer

class TYTableMixin(object, ):

    def _baseLogStr(self, des='', userId=None):
        pass

    def getValidIdleSeatId(self, userId, seatIndex, result):
        """
        
        Returns
            idleSeatId：
                >0   ：  为新玩家找到合适座位，需要继续处理
                <0   :   断线重连
                0    ：  坐下失败
        """
        pass

    def _checkSitCondition(self, userId):
        """

        """
        pass

    def onSitOk(self, userId, idleSeatId, result):
        """
        Return：
            player：新空座位上的player
        """
        pass

    def onStandUpOk(self, userId, seatId):
        """
        note: 站起后没有自动进入旁观列表
        """
        pass

    def getAllUserIds(self):
        pass

    def clearInvalidObservers(self):
        """

        """
        pass

    def callLaterFunc(self, interval, func, userId=0, timer=None, msgPackParams=None):
        """
           原理：延时调用table.doTableCall命令，通过此命令调用table对象的一个函数
           意义：table.doTableCall函数会锁定table对象，保证数据操作的同步性
        """
        pass