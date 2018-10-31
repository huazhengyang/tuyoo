# -*- coding: utf-8 -*-
"""
Created on 2014年2月20日

@author: zjgzzz@126.com
"""
import time
from freetime.util.metaclasses import Singleton
from freetime.util import log as ftlog

class TYEvent(object, ):
    """
    事件基类
    """

    def __init__(self):
        pass

class EventConfigure(TYEvent, ):
    """
    当配置信息发生变化时, 触发此事件, 
    """

    def __init__(self, keylist, reloadlist):
        pass

    def isModuleChanged(self, keys):
        pass

    def isChanged(self, keys):
        pass

class EventHeartBeat(TYEvent, ):
    """
    每秒钟系统服务心跳处理
    每秒钟一次的心跳事件广播, 执行之后间隔一秒再次启动, 即: 这个每秒心跳是个大约值,非准确值
    """
    __metaclass__ = Singleton
    count = 0

    def __init__(self):
        pass

class UserEvent(TYEvent, ):

    def __init__(self, userId, gameId):
        pass

    @property
    def gameId(self):
        pass

    @property
    def userId(self):
        pass

class EventUserLogin(UserEvent, ):
    """
    用户登录一个游戏的事件
    由Account.loginGame方法发送至游戏实例的tygame.getEventBus()
    """

    def __init__(self, userId, gameId, dayFirst, isCreate, clientId):
        pass

class MatchEvent(UserEvent, ):

    def __init__(self, userId, gameId, matchId):
        pass

    @property
    def matchId(self):
        pass

class MatchPlayerEvent(MatchEvent, ):

    def __init__(self, userId, gameId, matchId, player):
        pass

class MatchPlayerSigninEvent(MatchPlayerEvent, ):

    def __init__(self, userId, gameId, matchId, player):
        pass

class MatchPlayerSignoutEvent(MatchPlayerEvent, ):

    def __init__(self, userId, gameId, matchId, player):
        pass

class MatchPlayerOverEvent(MatchPlayerEvent, ):

    def __init__(self, userId, gameId, matchId, player, reason, rankRewards):
        pass

class MatchWinloseEvent(MatchEvent, ):

    def __init__(self, userId, gameId, matchId, isWin, rank, signinUserCount, rewards=None, mixId=None):
        pass

    @property
    def isWin(self):
        pass

    @property
    def rank(self):
        pass

    @property
    def signinUserCount(self):
        pass

class DataChangeEvent(UserEvent, ):

    def __init__(self, userId, gameId, reason):
        pass

    def addDataType(self, dataType):
        pass

    @property
    def dataTypes(self):
        pass

    @property
    def reason(self):
        pass

class DelvieryProduct(UserEvent, ):

    def __init__(self, userId, gameId, productId, count, buyGameId=0):
        pass

class RaffleEvent(DelvieryProduct, ):

    def __init__(self, userId, gameId, productId, count, buyGameId=0):
        pass

class ItemUsedEvent(UserEvent, ):

    def __init__(self, userId, gameId, itemUseResult):
        pass

class OnLineTcpChangedEvent(UserEvent, ):

    def __init__(self, userId, gameId, isOnline):
        pass

class OnLineGameChangedEvent(UserEvent, ):

    def __init__(self, userId, gameId, isEnter, clientId=None):
        pass

class OnLineRoomChangedEvent(UserEvent, ):

    def __init__(self, userId, gameId, roomId, isEnter):
        pass

class OnLineAttrChangedEvent(UserEvent, ):

    def __init__(self, userId, gameId, attName, attFinalValue, attDetalValue):
        pass

class ModuleTipEvent(UserEvent, ):

    def __init__(self, userId, gameId, name, count=1):
        pass

class ChargeNotifyEvent(UserEvent, ):

    def __init__(self, userId, gameId, rmbs, diamonds, productId, clientId):
        pass

class ActivityEvent(TYEvent, ):

    def __init__(self, userId, gameId, clientId, attrDict={}):
        pass

    def get(self, attr):
        pass

class GameOverEvent(ActivityEvent, ):

    def __init__(self, userId, gameId, clientId, roomId, tableId, gameResult, roomLevel=0, role='', roundNum=1, attrDict={}):
        pass

class GameBeginEvent(UserEvent, ):
    """
    牌桌开始的事件
    通用的牌桌开始，用在大厅任务时，需结合inspector的condition使用，控制任务完成的范围
    """

    def __init__(self, userId, gameId, roomId, tableId):
        pass

class TableStandUpEvent(UserEvent, ):
    """
    当用户离开座位,站起时,发送此事件
    在此事件的监听者中, 处理例如: 江湖救急, 救济金发放, 购买金币提示等信息
    """
    REASON_USER_CLICK_BUTTON = 0
    REASON_TCP_CLOSED = 1
    REASON_READY_TIMEOUT = 2
    REASON_GAME_ABORT = 3
    REASON_CHIP_NOT_ENOUGHT = 4
    REASON_CHIP_TOO_MUCH = 5
    REASON_MATCH_AUTO = 6
    REASON_GAME_OVER = 7
    REASON_SYSTEM_SHUTDOWN = 99

    def __init__(self, userId, gameId, roomId, tableId, reason):
        pass

class ItemCountChangeEvent(TYEvent, ):
    """
    道具数量变化
    """

    def __init__(self, userId):
        pass

class BetOnEvent(UserEvent, ):
    """
    小游戏下注事件
    """

    def __init__(self, userId, gameId, amount):
        pass

class BenefitSentEvent(UserEvent, ):

    def __init__(self, userId, gameId):
        pass