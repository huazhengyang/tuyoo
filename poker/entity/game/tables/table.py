# -*- coding: utf-8 -*-
"""

"""
__author__ = ['Zhaoqh"Zhouhao" <zhouhao@tuyoogame.com>']
from freetime.core.lock import locked
from freetime.util import log as ftlog
from freetime.util.log import catchedmethod
from poker.entity.game.rooms.room import TYRoom
from poker.entity.game.tables.table_state import TYTableState
from poker.entity.game.tables.table_seatlist import TYSeatList
from poker.entity.game.tables.table_observers import TYObservers
from poker.entity.game.tables.table_playerlist import TYPlayerList

class TYTable(object, ):
    """
    游戏牌桌基类, 主要提供桌子的实例对象, 挂接桌子相关的玩家,座位,玩法, 桌子状态, 计时器等功能
    不提供复杂的业务逻辑功能, 只提供简单的属性, 固有属性数据的查找, 外部消息的接入和同步处理接口
    """

    def __init__(self, room, tableId):
        """
        Args:
            room : 牌桌所属的房间对象
            tableId : 系统分配的唯一桌子ID
        """
        pass

    @property
    def gameId(self):
        pass

    @property
    def bigRoomId(self):
        pass

    @property
    def roomId(self):
        pass

    @property
    def room(self):
        pass

    @property
    def tableId(self):
        pass

    @property
    def config(self):
        pass

    @property
    def configChanged(self):
        pass

    @configChanged.setter
    def configChanged(self, value):
        pass

    @property
    def maxSeatN(self):
        pass

    @property
    def state(self):
        pass

    @property
    def seats(self):
        pass

    @property
    def players(self):
        pass

    @property
    def observers(self):
        pass

    @property
    def runConfig(self):
        """
        取得当前的基本配置, 当系统的配置内容更新时, 如果桌子再游戏中, 那么等下次开局时配置才真正的更新
        """
        pass

    def doReloadConf(self, tableConfig):
        """
        配置更新通知, 更新桌子内的配置信息
        例如斗地主的桌子: 如果已经有人坐下,那么当前桌子的配置就不再发生变化,
        当下一局开局时, 通过判定 table.configChanged 确定是否要重新载入运行配置
        即在开局后, 配置再牌局内不再发生变化, 再某一个时机(牌局结束,第一个人坐下)进行运行配置的更新
        注意: 子类若覆盖此方法, 那么要小心, 此方为非锁定方法, 即L此方法内不允许有异步IO操作, 必须为绝对同步操作
        """
        pass

    def _checkReloadRunConfig(self):
        """
        更新桌子内的配置信息
        if self.configChanged :
            runconf = self.room.roomConf
        """
        pass

    @catchedmethod
    @locked
    def doShutDown(self):
        """
        桌子同步安全操作方法
        桌子关闭, 此方法由安全进程结束的方法调用
        """
        pass

    def _doShutDown(self):
        """
        桌子同步安全操作方法
        桌子关闭, 此方法由安全进程结束的方法调用
        """
        pass

    @catchedmethod
    @locked
    def doSit(self, msg, userId, seatId, clientId):
        """
        桌子同步安全操作方法
        玩家操作, 尝试再当前的某个座位上坐下
        若 seatId为0, 那么需要桌子自动未玩家挑选一个座位
            通常此方法由客户端发送quick_start进行快速开始触发: 
                AppClient->ConnServer->UtilServer->RoomServer->ThisTableServer
                或:
                AppClient->ConnServer->RoomServer->ThisTableServer
        若 seatId为有效的座位号, 那么桌子需要保证玩家能够正常的坐下
            通常此方法由客户端发送quick_start进行断线重连触发: 
                AppClient->ConnServer->ThisTableServer
        实例桌子可以覆盖 _doSit 方法来进行自己的业务逻辑处理
        无论sit是否成功，都需要调用room.updateTableScore
        """
        pass

    def _doSit(self, msg, userId, seatId, clientId):
        """
        玩家操作, 尝试再当前的某个座位上坐下
        """
        pass

    @catchedmethod
    @locked
    def doStandUp(self, msg, userId, seatId, reason, clientId):
        """
        桌子同步安全操作方法
        玩家操作, 尝试离开当前的座位
        实例桌子可以覆盖 _standUp 方法来进行自己的业务逻辑处理
        此处不调用room.updateTableScore，由各游戏确认standup成功后调用。
        """
        pass

    def _doStandUp(self, msg, userId, seatId, reason, clientId):
        """
        玩家操作, 尝试离开当前的座位
        子类需要自行判定userId和seatId是否吻合
        """
        pass

    @catchedmethod
    @locked
    def doTableCall(self, msg, userId, seatId, action, clientId):
        """
        桌子同步安全操作方法
        桌子内部处理所有的table_call命令
        实例桌子可以覆盖 _doTableCall 方法来进行自己的业务逻辑处理
        子类需要自行判定userId和seatId是否吻合
        """
        pass

    def _doTableCall(self, msg, userId, seatId, action, clientId):
        """
        桌子内部处理所有的table_call命令
        子类需要自行判定userId和seatId是否吻合
        """
        pass

    @catchedmethod
    @locked
    def doTableManage(self, msg, action):
        """
        桌子同步安全操作方法
        桌子内部处理所有的table_manage命令
        实例桌子可以覆盖 _doTableManage 方法来进行自己的业务逻辑处理
        """
        pass

    def _doTableManage(self, msg, action):
        """
        桌子内部处理所有的table_manage命令
        """
        pass

    @catchedmethod
    @locked
    def doEnter(self, msg, userId, clientId):
        """
        桌子同步安全操作方法
        玩家操作, 尝试进入当前的桌子
        实例桌子可以覆盖 _doEnter 方法来进行自己的业务逻辑处理
        """
        pass

    def _doEnter(self, msg, userId, clientId):
        """
        玩家操作, 尝试进入当前的桌子
        """
        pass

    @catchedmethod
    @locked
    def doLeave(self, msg, userId, clientId):
        """
        桌子同步安全操作方法
        玩家操作, 尝试离开当前的桌子
        实例桌子可以覆盖 _doLeave 方法来进行自己的业务逻辑处理
        """
        pass

    def _doLeave(self, msg, userId, clientId):
        """
        玩家操作, 尝试离开当前的桌子
        实例桌子可以覆盖 _doLeave 方法来进行自己的业务逻辑处理
        """
        pass

    @property
    def playersNum(self):
        pass

    @property
    def observersNum(self):
        pass

    def getTableScore(self):
        """
        取得当前桌子的快速开始的评分
        越是最适合进入的桌子, 评分越高, 座位已满评分为0
        """
        pass

    def findIdleSeat(self, userId):
        """
        在本桌查找空闲的座位
        Returns：
            -1~n  :  玩家已经在本桌的座位号，需要断线重连
            0     :  本桌已满，没有空余的座位
            1~n   :  找到的第一个空闲座位号
        """
        pass

    def getPlayer(self, userId):
        """
        根据userId取得对应的Player对象实例
        """
        pass

    def getRobotUserCount(self):
        """
        取得当前桌子中, 机器人的数量
        """
        pass

    def getObserver(self, userId):
        """
        根据userId取得对应的Observer对象实例
        """
        pass

    def getSeatUserIds(self):
        """
        取得当前桌子的坐下的人数和每个座位的userId列表
        """
        pass