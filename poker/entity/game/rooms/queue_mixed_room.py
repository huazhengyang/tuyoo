# -*- coding: utf-8 -*-
"""

"""
from poker.entity.game.rooms.normal_room import TYNormalRoom
from poker.entity.game.rooms.queue_mixed_room_ctrl.room_cotroller import QueueMixedRoomCtrl
from freetime.core.timer import FTLoopTimer
from freetime.core.lock import locked
from poker.entity.dao import onlinedata
__author__ = ['zhaoliang']
import freetime.util.log as ftlog
from poker.entity.configure import gdata

class TYQueueMixedRoom(TYNormalRoom, ):
    """
    队列混房
    
    适用于固定玩家数量组桌的休闲棋牌游戏
    比如斗地主 麻将
    """
    ROOM_TIMER = 1

    def __init__(self, roomDefine):
        pass

    @property
    def loopTimer(self):
        pass

    def setLoopTimer(self, timer):
        pass

    @property
    def roomController(self):
        pass

    def setRoomController(self, controlelr):
        pass

    def initRoom(self, rConfig=None):
        """
        初始化房间
        """
        pass

    def doReloadConf(self, roomDefine):
        """
        重新加载配置
        """
        pass

    @locked
    def handle_room_action(self):
        """
        定时调度班车
        """
        pass

    @locked
    def doQuickStart(self, msg):
        """
        先进入队列
        等候分配
        
        1）快开进来的人
        roomId / mixedRoomId
        
        2）进入队列是，loc中的tableId为shadowRoomId * 10000
        
        3）在队列的断线重连，tableId = shadowRoomId * 10000
        
        4）在房间的断线重连，tableId为正常牌桌的
        """
        pass

    @locked
    def doLeave(self, userId, msg):
        """
        支持离开
        """
        pass