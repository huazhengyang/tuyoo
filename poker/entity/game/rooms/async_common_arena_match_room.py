# -*- coding: utf-8 -*-
"""
Created on 2017年09月29日

异步的通用Arena比赛，每局一阶段
可随时保存进度
重启GR/增加GR进度依然有效

每一阶段需前端主动发起，开始游戏

支持复活

@author: zhaol
"""
import freetime.util.log as ftlog
from poker.entity.configure import gdata
from poker.entity.game.rooms.async_common_arena_match_ctrl.aca_matches import AsyncCommonArenaMatches
from freetime.core.timer import FTLoopTimer
from freetime.core.lock import locked
from poker.entity.game.rooms.normal_room import TYNormalRoom
from freetime.util.log import getMethodName
from poker.entity.game.rooms import quick_save_async_match
from poker.entity.dao import sessiondata

class TyAsyncCommonArenaMatchRoom(TYNormalRoom, ):
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
    def doSignin(self, userId, signinParams, feeIndex=0):
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
    def doMatchChallenge(self, userId, gameId, roomId, matchId, msg):
        """
        比赛继续挑战
        """
        pass

    @locked
    def doMatchBack(self, userId, gameId, roomId, matchId, msg):
        """
        比赛复活
        """
        pass

    @locked
    def doMatchSave(self, userId, gameId, roomId, matchId, msg):
        """
        比赛进度保存，保存成功后，用户就可以去别的房间/玩法玩儿了
        
        清楚比赛loc
        
        清楚后，下次恢复，需主动resume
        """
        pass

    @locked
    def doMatchResume(self, userId, gameId, roomId, matchId, msg):
        """
        比赛进度恢复
        确认恢复数据有效
        重新设置比赛loc
        返回前端具体的wait消息，等待其下一步操作
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

    def findMatchIdByUser(self, userId):
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