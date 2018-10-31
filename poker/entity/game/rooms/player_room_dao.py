# -*- coding: utf-8 -*-
"""

"""
import freetime.util.log as ftlog
from poker.entity.dao import tabledata
import json
__author__ = ['Zhou Hao']

class PlayerRoomDao(object, ):
    """
       key: playerRoomRound:[bigRoomId]
       value: int值
       存取玩家在同一房间换桌时需要保留的信息，例如：
       key: playerRoomRecord:[bigRoomId]
       value: {tableChips: 离开上一桌时，玩家的筹码;
               timeoutCount: 连续超时弃牌的次数
               isManaged: 是否托管
                "buyinDelta": 0,  # 在开局时要补充这么多筹码(暂时只有 mtt addon/rebuy 使用)
                "buyinTo": 0,  # 在开局时要补充到这么多筹码
                "rebuyType": "",  # 补充筹码类型。详细见定义
                "isRoomNewUser": True,  # 是否刚进入房间未参与游戏
              }
    """

    @classmethod
    def clear(cls, userId, bigRoomId):
        """

        """
        pass

    @classmethod
    def _getPlayerRoomRecordKey(cls, userId):
        pass

    @classmethod
    def _getPlayerRoomRoundKey(cls, userId):
        pass

    @classmethod
    def getPlayerRoomRecord(cls, userId, bigRoomId):
        pass

    @classmethod
    def setPlayerRoomRecord(cls, userId, bigRoomId, recordDict):
        pass

    @classmethod
    def getPlayerRound(cls, userId, bigRoomId):
        pass

    @classmethod
    def incrPlayerRound(cls, userId, bigRoomId):
        pass