# -*- coding:utf-8 -*-
'''
Created on 2016年11月8日

@author: zhaojiangang
'''
class TuoguanLoction(object):
    CALLING = 1
    OUT_CARD = 2
    SETTLEMENT = 3


class Oper(object):
    USER = 0
    ROBOT = 1
    
class TuoguanType(object):
    USERACT = 0
    TIMEOUT = 1  # 正常操作超时
    ALREADY_TUOGUAN = 2  # 已经托管后,再次出牌
    SYS_FAST_CARD = 3  # 系统调度快速出牌
    
class CallResult(object):
    CALLING = 0
    FINISH = 1
    ABORT = 2
    
    @classmethod
    def isValid(cls, value):
        return value >= cls.CALLING and value <= cls.ABORT

class OutCardResult(object):
    FINISH = 1
    PLAYING = 2
    
class ClearGameReason:
    GAME_ABORT = 0
    GAME_OVER = 1
    GAME_KILL = 2

class JiabeiMode:
    BEFORE_FLIP_BASE_CARD = 0
    AFTER_FLIP_BASE_CARD = 1
    
class StandupReason:
    USER_CLICK_BUTTON = 0  # 表示用户主动调用，离开桌子
    TCP_CLOSED = 1  # 网络系统短线，系统踢出，离开桌子
    READY_TIMEOUT = 2  # ready超时，系统踢出，离开桌子
    GAME_ABORT = 3  # 牌桌流局，全部托管状态下，系统踢出，离开桌子
    CHIP_NOT_ENOUGHT = 4  # 游戏币不够，系统踢出，离开桌子
    CHIP_TOO_MUCH = 5  # 游戏币太多了，系统踢出，离开桌子
    MATCH_AUTO = 6  # 比赛，服务器自动换桌子
    GAME_OVER = 7  # 正常牌局结束
    FORCE_CLEAR = 8 # 强制清理桌子
    SYSTEM_SHUTDOWN = 99  # 系统维护，踢出，关闭房间


class UserReportReason:
    OFFLINE = 1  # 频繁掉线
    LOW_LEVEL = 2  # 水平过低
    NEGATIVE = 3  # 态度消极
    ILLEGAL_NICKNAME = 4  # 违规昵称
    ILLEGAL_AVATAR = 5  # 违规头像

