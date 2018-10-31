# -*- coding: utf-8 -*-
"""
Created on 2014年2月20日

@author: zjgzzz@126.com
"""
from freetime.util import log as ftlog
ISHALL51 = 0
try:
    from tuyoo5.core import tyrpchall
    from tuyoo5.core import tygame
    ISHALL51 = 1
except:
    ISHALL51 = 0
ftlog.info('ISHALL51->', ISHALL51)

def sendToHall51GameOverEvent(userId=0, gameId=0, roomId=0, tableId=0, gameResult=0, roomLevel=0, roundNum=0, winningStreak=0, **kwargs):
    """
    发送普通游戏一局结束的事件至hall51服务
    @param userId: 玩家ID
    @param gameId: 游戏ID
    @param roomId: 房间ID
    @param tableId: 桌子ID
    @param gameResult: 游戏结果 0 平 1 胜 -1 负
    @param roomLevel: 房间级别
    @param roundNum: 牌局ID
    @param winningStreak: 连胜次数
    @param kwargs: 扩展参数集合
    """
    pass

def sendToHall51MatchOverEvent(userId=0, gameId=0, roomId=0, gameResult=0, roomLevel=0, roundNum=0, **kwargs):
    """
    发送比赛游戏一局结束的事件至hall51服务
    @param userId: 玩家ID
    @param gameId: 游戏ID
    @param roomId: 房间ID
    @param gameResult: 游戏结果 0 平 1 胜 -1 负
    @param roomLevel: 房间级别
    @param roundNum: 牌局ID
    @param kwargs: 扩展参数集合
    """
    pass

def sendToHall51GameDataEvent(userId=0, gameId=0, filedName=0, filedValue=0, **kwargs):
    """
    发送玩家游戏数据变化的事件至hall51服务，只有特殊的hall51需要的才发送
    @param userId: 玩家ID
    @param gameId: 游戏ID
    @param filedName: 数据字段名称
    @param filedValue: 数据值
    @param kwargs: 扩展参数集合
    """
    pass