# -*- coding: utf-8 -*-
"""
Created on 2017年10月13日

@author: zhaol
"""
import random
import freetime.util.log as ftlog
from poker.entity.game.rooms.quick_upgrade_match_ctrl.exceptions import QUMError
from poker.entity.game.rooms.quick_upgrade_match_ctrl.match_fees import QUMFees
from poker.entity.game.rooms.quick_upgrade_match_ctrl.game_rewards import QUMRewards
from poker.entity.game.rooms.quick_upgrade_match_ctrl.game_stages import QUMStages
from poker.entity.game.rooms.quick_upgrade_match_ctrl.match_tips import QUMTips
from poker.entity.dao import userchip, onlinedata, userdata
from poker.entity.game.rooms.quick_upgrade_match_ctrl.game_player import QUMPlayer
from poker.entity.game.rooms.quick_upgrade_match_ctrl.match_message import QUMMessage
from poker.entity.game.rooms.quick_upgrade_match_ctrl.game_record import QUMRecords
from poker.entity.game.rooms.quick_upgrade_match_ctrl.match_report import QUMatchReport
from poker.entity.configure import gdata
from poker.util import timestamp as pktimestamp

class QUMatch(object, ):
    MAX_SEAT = 1000
    STATE_IDLE = 0
    STATE_STARTED = 1
    STATE_PREPARE_STOP = 2
    STATE_STOP = 3
    STATE_FINAL = 4
    WAIT_TIME = 2

    def __init__(self, gameId, roomId):
        pass

    @property
    def winLoseWaitTime(self):
        pass

    def setWinLoseWaitTime(self, wTime):
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
    def timeRange(self):
        pass

    def setTimeRange(self, tRange):
        pass

    @property
    def matchIntroduce(self):
        pass

    def setMatchIntrodule(self, introdule):
        pass

    @property
    def users(self):
        """
        参加比赛的用户
        """
        pass

    def setUsers(self, users):
        pass

    def initMatch(self, mConfig):
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
    def queues(self):
        """
        比赛队列
        """
        pass

    def setQueues(self, queues):
        pass

    @property
    def startTime(self):
        pass

    def setStartTime(self, st):
        pass

    @property
    def stopTime(self):
        pass

    def setStopTime(self, st):
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
    def rewards(self):
        pass

    def setRewards(self, rewards):
        pass

    @property
    def fees(self):
        pass

    def setFees(self, fees):
        pass

    @property
    def maxCoin(self):
        pass

    def setMaxCoin(self, coin):
        pass

    @property
    def maxCoinQS(self):
        pass

    def setMaxCoinQS(self, coin):
        pass

    @property
    def minCoin(self):
        pass

    def setMinCoin(self, coin):
        pass

    @property
    def minCoinQS(self):
        pass

    def setMinCoinQS(self, coin):
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

    @property
    def state(self):
        pass

    def setState(self, state):
        pass

    def handleRoomAction(self, delta):
        """
        班车调度
        """
        pass

    def randomRobotData(self, users):
        """
        随机机器人的轮次和积分
        积分在真人积分的最小值和最大值之间随机。
        
        如果积分等于第一阶段的初始积分，则轮次为第一赛段的轮次
        其他时候随机一个轮次
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

    def isInGiveUpMatch(self, userId):
        """
        是否在退赛的比赛中
        """
        pass

    def backMatchFail(self, userId):
        """
        回到比赛失败
        """
        pass

    def signIn(self, userId, feeIndex, matchId):
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

    def setTableMaxSeat(self, maxSeat):
        """
        设置每桌的人数
        """
        pass

    def getRankName(self, rank, totalCount):
        """
        获取排名的文字描述
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
        
        快速赛自动进入比赛，这里直接返回成功
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

    def giveUp(self, userId, gameId):
        """
        放弃比赛
        清除比赛loc，断线重连后不再回来
        本轮结束后，如果淘汰，正常退出比赛
        如果晋级，则给予晋级的最后一个名次，退出比赛，不再进入下一轮的班车
        """
        pass

    def winLooses(self, users):
        """
        一桌的结算结果
        添加到等待处理的牌桌队列
        
        给游戏前端留下WAIT_TIME时间用于展示本桌结算
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

    def winLoosesDelay(self, users):
        """
        一桌结算
        [
        {
            "userId": 10001,
            "seatId": 0,
            "stage": 1,
            "score": 100
        },
        {
        },
        {
        }
        ]
        
        {
            u'cmd': u'room',
            u'params': {
                u'gameId': 701,
                u'users': [
                    {
                        u'seatId': 0,
                        u'score': 400,
                        u'userId': 10788,
                        u'stage': 1
                    },
                    {
                        u'seatId': 1,
                        u'score': -260,
                        u'userId': 9393,
                        u'stage': 0
                    },
                    {
                        u'seatId': 2,
                        u'score': -120,
                        u'userId': 9719,
                        u'stage': 0
                    },
                    {
                        u'seatId': 3,
                        u'score': -20,
                        u'userId': 9336,
                        u'stage': 0
                    }
                ],
                u'matchId': 701221,
                u'tableId': 70122010010200,
                u'action': u'm_winlose',
                u'roomId': 7012201000
            }
        }
        """
        pass

    def queueTableId(self, roomId):
        """
        队列里的牌桌ID，用来标记loc状态
        """
        pass

    def back(self, userId):
        """
        回到比赛
        """
        pass

    def matchOver(self, userId, rank):
        """
        比赛结束
        """
        pass

    def buildWinInfo(self, rank, rankRewards):
        pass

    def buildLedInfo(self, userId, rank, rankRewards):
        """
        构建LED信息
        """
        pass

    def buildMatchErrorInfo(self, rank, rankRewards):
        pass

    def buildLoserInfo(self, rank):
        pass

    def getNextStage(self, stageIndex):
        """
        获取下一个赛段
        """
        pass

    def findStageByIndex(self, stageIndex):
        """
        根据index查找赛制阶段
        """
        pass

    def getFirstStageIndex(self):
        """
        获取第一个阶段的索引
        """
        pass

    def getFirstStage(self):
        """
        获取第一阶段
        """
        pass

    def getTotalUserCount(self):
        """
        获取比赛的参赛人数
        """
        pass

    def getPlayer(self, userId):
        """
        查找用户是否在比赛中
        """
        pass

    def checkCoin(self, userId):
        """
        校验用户的金币条件
        minCoin
        minCoinQS
        maxCoin
        maxCoinQS
        """
        pass

    def checkTime(self, startTime, stopTime):
        """
        检查比赛报名时间
        """
        pass