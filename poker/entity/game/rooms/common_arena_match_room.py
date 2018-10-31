# -*- coding: utf-8 -*-
"""
Created on 2017年09月29日

@author: zhaol
"""
import freetime.util.log as ftlog
from poker.entity.configure import gdata
from poker.entity.game.rooms.common_arena_match_ctrl.ca_matches import CommonArenaMatches
from freetime.core.timer import FTLoopTimer
from freetime.core.lock import locked
from poker.entity.game.rooms.normal_room import TYNormalRoom
from freetime.util.log import getMethodName

class TyCommonArenaMatchRoom(TYNormalRoom, ):
    """
    通用Arena比赛
    GR/GT之间只有有限的几个交互
    1）GR2GT 开桌命令
    2）GT2GR 汇报结果
    3）GR2GT 放弃比赛
    
    根据配置晋级规则判断玩家的晋级与否
    """
    ROOM_TIMER = 1

    def __init__(self, roomdefine):
        pass

    @property
    def loopTimer(self):
        """
        比赛管理定时器
        """
        pass

    def setLoopTimer(self, timer):
        pass

    @property
    def matches(self):
        """
        混房比赛集合
        """
        pass

    def setMatches(self, matches):
        pass

    def initMatch(self):
        """
        初始化比赛
        """
        pass

    @locked
    def handle_room_action(self):
        """
        定时调度班车
        """
        pass

    def doReloadConf(self, roomDefine):
        """
        重新加载配置
        """
        pass

    @locked
    def doSignin(self, userId, signinParams):
        """
        比赛报名
        """
        pass

    @locked
    def doSignout(self, userId):
        """
        开赛前退赛
        """
        pass

    def doEnter(self, userId):
        """
        玩家进入比赛
        成功返回：
        失败返回：
        """
        pass

    def doLeave(self, userId, msg):
        """
        快速赛不支持离开
        如果离开，可以选择退赛，giveup
        giveup后，清楚loc，牌局打完后，如果淘汰，取得被淘汰赛段的最低名次，然后淘汰。
            如果晋级，取得晋级赛段的最低名次，同时不进入下一个赛段的班车，游戏终止
        """
        pass

    def doGetDescription(self, userId):
        """
        获取比赛描述/详情
        """
        pass

    def doGetMatchDescription(self, userId, gameId, roomId, matchId, msg):
        """
        获取比赛描述/详情
        新接口
        根据matchId获取比赛信息
        不使用
        doGetDescription
        了，原接口不支持扩展参数，不支持混房
        
        参数
        userId : 用户ID
        romId : 房间ID
        matchID : 比赛ID/混房比赛ID
        msg ： 透传消息
        """
        pass

    def doUpdateInfo(self, userId):
        """
        更新比赛详情
        
        快速赛不发送update消息
        """
        pass

    def doGiveup(self, userId):
        """
        本比赛不支持这个接口
        """
        pass

    @locked
    def doMatchGiveup(self, userId, gameId, roomId, matchId, msg):
        """
        退出比赛
        
        本局打完后，如果淘汰，则淘汰
        如果晋级，则给予本轮晋级名次的最后一名，发奖，不进入班车
        """
        pass

    @locked
    def doWinlose(self, msg):
        pass

    @locked
    def doMatchTableError(self, msg):
        pass

    def doQuickStart(self, msg):
        """
        快开，比赛的断线重连
        """
        pass