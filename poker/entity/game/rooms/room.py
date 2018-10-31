# -*- coding: utf-8 -*-
"""

"""
from freetime.entity.msg import MsgPack
from freetime.util.log import getMethodName, catchedmethod
import freetime.util.log as ftlog
from poker.entity.configure import gdata, pokerconf
from poker.entity.dao import sessiondata, onlinedata, userchip
from poker.entity.game import game
from poker.entity.game.plugin import TYPluginCenter, TYPluginUtils
from poker.entity.game.tables.table_player import TYPlayer
from poker.protocol import router
__author__ = ['"Zhouhao" <zhouhao@tuyoogame.com>']

class TYRoom(object, ):
    """

    Attributes:
        roomDefine： 房间配置信息
        maptable:    房间牌字典
    """
    ENTER_ROOM_REASON_OK = 0
    ENTER_ROOM_REASON_CONFLICT = 1
    ENTER_ROOM_REASON_INNER_ERROR = 2
    ENTER_ROOM_REASON_ROOM_FULL = 3
    ENTER_ROOM_REASON_LESS_MIN = 4
    ENTER_ROOM_REASON_GREATER_MAX = 5
    ENTER_ROOM_REASON_GREATER_ALL = 6
    ENTER_ROOM_REASON_TABLE_FULL = 7
    ENTER_ROOM_REASON_WRONG_TIME = 8
    ENTER_ROOM_REASON_NOT_QUALIFIED = 9
    ENTER_ROOM_REASON_ROOM_ID_ERROR = 10
    ENTER_ROOM_REASON_VIP_LEVEL = 11
    ENTER_ROOM_REASON_DASHIFEI_LEVEL = 12
    ENTER_ROOM_REASON_NOT_OPEN = 13
    ENTER_ROOM_REASON_NEED_VALIDATE = 14
    ENTER_ROOM_REASON_NEED_ENERGY = 15
    ENTER_ROOM_REASON_FRIEND_DISSOLVE = 16
    ENTER_ROOM_REASON_MAINTENANCE = 17
    LEAVE_ROOM_REASON_FORBIT = (-1)
    LEAVE_ROOM_REASON_ACTIVE = 0
    LEAVE_ROOM_REASON_LOST_CONNECTION = 1
    LEAVE_ROOM_REASON_TIMEOUT = 2
    LEAVE_ROOM_REASON_ABORT = 3
    LEAVE_ROOM_REASON_LESS_MIN = 4
    LEAVE_ROOM_REASON_GREATER_MAX = 5
    LEAVE_ROOM_REASON_MATCH_END = 6
    LEAVE_ROOM_REASON_CHANGE_TABLE = 7
    LEAVE_ROOM_REASON_GAME_START_FAIL = 8
    LEAVE_ROOM_REASON_NEED_VALIDATE = 9
    LEAVE_ROOM_REASON_SYSTEM = 99
    ROOM_STATUS_RUN = game.GAME_STATUS_RUN
    ROOM_STATUS_SHUTDOWN_GO = game.GAME_STATUS_SHUTDOWN_GO
    ROOM_STATUS_SHUTDOWN_DONE = game.GAME_STATUS_SHUTDOWN_DONE

    def __init__(self, roomDefine):
        """
        Args:
            roomDefine:
                RoomDefine.bigRoomId     int 当前房间的大房间ID, 即为game/<gameId>/room/0.json中的键
                RoomDefine.parentId      int 父级房间ID, 当前为管理房间时, 必定为0 (管理房间, 可以理解为玩家队列控制器)
                RoomDefine.roomId        int 当前房间ID
                RoomDefine.gameId        int 游戏ID
                RoomDefine.configId      int 配置分类ID
                RoomDefine.controlId     int 房间控制ID
                RoomDefine.shadowId      int 影子ID
                RoomDefine.tableCount    int 房间中桌子的数量
                RoomDefine.shadowRoomIds tuple 当房间为管理房间时, 下属的桌子实例房间的ID列表
                RoomDefine.configure     dict 房间的配置内容, 即为game/<gameId>/room/0.json中的值
        """
        pass

    @property
    def roomDefine(self):
        pass

    @property
    def bigRoomId(self):
        pass

    @property
    def ctrlRoomId(self):
        pass

    @property
    def roomId(self):
        pass

    @property
    def gameId(self):
        pass

    @property
    def roomConf(self):
        pass

    @property
    def tableConf(self):
        pass

    @property
    def matchConf(self):
        pass

    @property
    def hasRobot(self):
        pass

    @property
    def shelterShadowRoomIds(self):
        pass

    @property
    def openShadowRoomIds(self):
        pass

    @property
    def openShadowRoomIdsDispatch(self):
        pass

    def getDispatchConfigVersion(self):
        pass

    @property
    def matchId(self):
        pass

    def doReloadConf(self, roomDefine):
        pass

    def doShutDown(self):
        pass

    def _doShutDown(self):
        pass

    def doQuickStart(self, msg):
        pass

    def doCheckUserLoc(self, userId, gameId, roomId, tableId, clientId):
        """
        检查给出的玩家是否再当前的房间和桌子上,
        依照个个游戏的自己的业务逻辑进行判定,
        seatId >= 0 
        isObserving == 1|0 旁观模式
        当seatId > 0 或 isObserving == 1时表明此玩家在当前的桌子内
        """
        pass

    @catchedmethod
    def doEnter(self, userId):
        pass

    def _enter(self, userId):
        pass

    @catchedmethod
    def doLeave(self, userId, msg):
        pass

    def _leave(self, userId, reason, needSendRes):
        pass

    def _remoteTableLeave(self, userId, reason=LEAVE_ROOM_REASON_ACTIVE, locList=None):
        pass

    def updateTableScore(self, tableScore, tableId, force=False):
        pass

    def checkSitCondition(self, userId):
        pass

    def getRoomOnlineInfo(self):
        pass

    def getRoomOnlineInfoDetail(self):
        pass

    def getRoomRobotUserCount(self):
        pass