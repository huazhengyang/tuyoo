# -*- coding: utf-8 -*-
"""
Created on 2017年10月13日

@author: zhaol
"""
import time
import freetime.util.log as ftlog
from poker.entity.game.rooms.async_upgrade_hero_match_ctrl.exceptions import AsyncUpgradeHeroMatchError
from poker.entity.game.rooms.async_upgrade_hero_match_ctrl.match_fees import AsyncUpgradeHeroMatchFees
from poker.entity.game.rooms.async_upgrade_hero_match_ctrl.match_tips import AsyncUpgradeHeroMatchTips
from poker.entity.dao import userdata, onlinedata, daobase, sessiondata
from poker.entity.game.rooms.async_upgrade_hero_match_ctrl.match_player import AsyncUpgradeHeroMatchPlayer
from poker.entity.game.rooms.async_upgrade_hero_match_ctrl.match_message import AsyncUpgradeHeroMatchMessage
from poker.entity.game.rooms.async_upgrade_hero_match_ctrl.match_record import AsyncUpgradeHeroMatchRecords
from poker.entity.game.rooms.async_upgrade_hero_match_ctrl.match_report import AsyncUpgradeHeroMatchReport
from poker.entity.configure import gdata
from poker.util import timestamp as pktimestamp, strutil
from poker.entity.game.rooms.async_upgrade_hero_match_ctrl.match_winner_rewards import AsyncUpgradeHeroMatchWinnerRecords
from poker.entity.game.rooms.async_upgrade_hero_match_ctrl.match_stages import AsyncUpgradeHeroMatchStages
from poker.entity.game.rooms.async_upgrade_hero_match_ctrl.match_lottery_rewards import AsyncUpgradeHeroMatchLotteryRecords
from poker.entity.game.rooms.async_upgrade_hero_match_ctrl.match_queue import AsyncUpgradeHeroMatchQueue
from freetime.core.tasklet import FTTasklet
from poker.entity.biz import bireport
from poker.entity.game.rooms.async_upgrade_hero_match_ctrl.match_db import AsyncUpgradeHeroMatchDataBase

class AsyncUpgradeHeroMatch(object, ):
    WAIT_TIME = 2
    ROOM_TIMER = 1
    MAX_SEAT_ID = 1000

    def __init__(self, gameId, roomId):
        pass

    @property
    def lotteryRewards(self):
        pass

    def setLotteryRewards(self, rewards):
        pass

    @property
    def tableSeatCount(self):
        pass

    def setTableSeatCount(self, count):
        pass

    @property
    def msgSender(self):
        """
        消息发送器
        """
        pass

    def setMsgSender(self, sender):
        pass

    @property
    def waitTable(self):
        pass

    def setWaitTable(self, table):
        pass

    def addWaitTable(self, users, timeOut):
        """
        等待处理的牌桌结果
        """
        pass

    @property
    def waitUsers(self):
        """
        等待进入队列的玩家
        """
        pass

    def setWaitUsers(self, users):
        pass

    def addWaitUser(self, player):
        pass

    @property
    def users(self):
        """
        参加比赛的用户
        """
        pass

    def setUsers(self, users):
        pass

    def initMatch(self, config):
        """
        初始化比赛配置
        """
        pass

    @property
    def matchPlugin(self):
        """
        比赛游戏的接口对象
        """
        pass

    def setMatchPlugin(self, plugin):
        pass

    @property
    def gameId(self):
        pass

    def setGameId(self, gameId):
        pass

    @property
    def roomId(self):
        """
        房间ID
        """
        pass

    def setRoomId(self, roomId):
        pass

    @property
    def queue(self):
        """
        比赛队列
        """
        pass

    def setQueue(self, queue):
        pass

    @property
    def tips(self):
        pass

    def setTips(self, tips):
        pass

    @property
    def stages(self):
        pass

    def setStage(self, stage):
        pass

    @property
    def winnerRewards(self):
        pass

    def setWinnerRewards(self, rewards):
        pass

    @property
    def fees(self):
        pass

    def setFees(self, fees):
        pass

    @property
    def name(self):
        pass

    def setName(self, name):
        pass

    @property
    def desc(self):
        pass

    def setDesc(self, desc):
        pass

    @property
    def matchId(self):
        pass

    def setMatchId(self, matchId):
        pass

    def handleRoomAction(self, delta):
        """
        1）班车调度
        2）奖池开奖
        """
        pass

    def buildLotteryInfo(self, lotteryRewards):
        """
        构建奖池说明
        """
        pass

    def checkUserLoc(self, userId):
        """
        检查loc，确定用户是否在比赛中
        用户的loc要么是在GR中
        要么是在GT中
        如果哪儿都没有，用户就不再当前比赛中了，需要从当前比赛中清楚此用户
        """
        pass

    def checkGameLoc(self, userId, gameId):
        """
        检查用户的游戏LOC，如有该游戏的LOC，报名失败，提示正在其他房间/比赛中
        """
        pass

    def signIn(self, userId, signinParams):
        """
        报名比赛
        首先校验比赛开启/关闭时间
            比赛尚未开启，请稍后再来
            比赛马上结束，请稍后再来
            比赛已经结束，请稍后再来
        其次校验用户的金币条件
        第三收取服务费
        """
        pass

    def matchUpdate(self, userId):
        """
        比赛更新
        发送当前比赛的奖池信息，参与评分奖池的人数
        """
        pass

    def matchChallenge(self, userId, gameId):
        """
        继续挑战
        """
        pass

    def matchBack(self, userId, gameId):
        """
        比赛复活
        """
        pass

    def matchBackNextLevel(self, userId, gameId):
        """
        比赛直接晋级到下一关，目前只支持第2关,防被刷
        """
        pass

    def signOut(self, userId):
        """
        退出比赛
        """
        pass

    def enter(self, userId):
        """
        进入比赛
        
        闯关赛赛自动进入比赛，这里直接返回成功
        """
        pass

    def grSpecialTableId(self):
        """
        队列里的牌桌ID，用来标记loc状态
        """
        pass

    def des(self, userId, gameId):
        """
        获取比赛描述信息
        比赛名称
        比赛赛段
        比赛奖励
        """
        pass

    def getMatchSaveInfo(self, userId, gameId):
        """
        获取比赛记录的详细信息
        """
        pass

    def matchSave(self, userId, gameId):
        """
        保存比赛
        前提，用户在比赛中且用户不在牌桌中
        在牌桌中，比赛保存失败
        """
        pass

    def matchResume(self, userId, gameId):
        """
        比赛恢复
        前提，用户不在比赛中，且用户不在牌桌中
        在比赛内存中，恢复失败
        在牌桌中，恢复失败
        
        恢复成功后，给前端返回wait，等待其下一步操作
        """
        pass

    def giveUp(self, userId, gameId):
        """
        放弃比赛
        清除比赛loc，断线重连后不再回来
        本轮结束后，如果淘汰，正常退出比赛
        如果晋级，则给予晋级的最后一个名次，退出比赛，不再进入下一轮的班车
        """
        pass

    def winLooses(self, tableId, users):
        """
        比赛结算
        """
        pass

    def matchTableError(self, users):
        """
        比赛出现错误
        给每个人发一个可能获得的最低名次
        退还报名费
        
        不发奖状
        发消息，说明情况
        """
        pass

    def back(self, userId):
        """
        断线重连 重新回到比赛
        
        断线重连不需要存比赛进度
        """
        pass

    def matchOver(self, userId, winLose):
        """
        比赛结束
        """
        pass

    def buildWinInfo(self, couponCount):
        pass

    def buildLedInfo(self, userId, couponCount):
        """
        构建LED信息
        """
        pass

    def buildLotteryLedInfo(self, lotteryInfo):
        """
        构建奖池开奖的LED信息
        """
        pass

    def getUserName(self, userId):
        """
        获取用户姓名
        """
        pass

    def buildLoserInfo(self):
        pass

    def findStageByIndex(self, stageIndex):
        """
        根据index查找赛制阶段
        """
        pass

    def getInitStageIndex(self):
        """
        获取报名的初始阶段
        """
        pass

    def getFirstStageIndex(self):
        """
        获取第一个阶段的索引
        """
        pass

    def getLastStageIndex(self):
        """
        获取最后一个阶段的索引
        """
        pass

    def getFirstStage(self):
        """
        获取第一阶段
        """
        pass

    def getPlayer(self, userId):
        """
        查找用户是否在比赛中
        """
        pass

    def reportBiGameEvent(self, eventId, userId, roomId, tableId, roundId, detalChip, state1, state2, cardlist, tag=''):
        pass
if (__name__ == '__main__'):
    print 'ok'