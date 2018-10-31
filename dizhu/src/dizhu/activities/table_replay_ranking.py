# -*- coding=utf-8 -*-
'''
Created on 16-10-24

@author: luwei

@desc: 下注竞猜活动
'''
from __future__ import division

import copy
from datetime import datetime

from dizhu.activities.toolbox import Tool, UserBag, UserInfo
from dizhu.entity.dizhuconf import DIZHU_GAMEID
from dizhu.game import TGDizhu
from dizhu.replay import replay_service
from dizhu.replay.replay_service import ReplayViewEvent
import freetime.util.log as ftlog
from hall.entity import hallitem
from hall.entity.todotask import TodoTaskRegister
from poker.entity.biz.activity.activity import TYActivity
from poker.entity.dao import daobase, sessiondata
from poker.util import strutil
import poker.util.timestamp as pktimestamp


#
class ActivityUserModel(object):
    ''' 用户活动数据 ''' 
    def __init__(self):
        self.replayDay = 0
        self.replayDayCounter = 0
        self.prizeCounter = 0
    
    def toDict(self):
        return {
            'replayDay': self.replayDay,
            'replayDayCounter': self.replayDayCounter,
            'prizeCounter': self.prizeCounter,
        }
    
    def fromDict(self, d):
        self.replayDay = d.get('replayDay',  0)
        self.replayDayCounter = d.get('replayDayCounter', 0)
        self.prizeCounter = d.get('prizeCounter', 0)
    
    def incrReplayCount(self, ct=None):
        if ct == None:
            ct = datetime.now()
        
        # 不是同一天，则清零当天分享次数
        cday = pktimestamp.formatTimeDayInt(ct)
        if self.replayDay != cday:
            self.replayDay = cday
            self.replayDayCounter = 0
            
        self.replayDayCounter += 1
         
    @classmethod
    def buildStorageKey(cls, activityGameId, userId):
        return 'act:%s:%s' % (activityGameId, userId)
    
    @classmethod
    def saveModel(cls, model, activityGameId, activityId, userId):
        ''' 保存用户数据 '''
        jstr = strutil.dumps(model.toDict())
        rpath = cls.buildStorageKey(activityGameId, userId)
        daobase.executeUserCmd(userId, 'hset', rpath, activityId, jstr)

    @classmethod
    def loadModel(cls, activityGameId, activityId, userId):
        jstr = None
        model = ActivityUserModel()
        try:
            jstr = daobase.executeUserCmd(userId, 'hget', cls.buildStorageKey(activityGameId, userId), activityId)
            if jstr:
                model.fromDict(strutil.loads(jstr))
        except:
            ftlog.error('ActivityUserModel.load',
                        'userId=', userId,
                        'activityGameId=', activityGameId,
                        'activityId=', activityId,
                        'jstr=', jstr)
        return model
    
    
class RankingProxy(object):
    
    @classmethod
    def getRankingListByRankNumberList(cls, rankingMax, rankNumberList):
        '''
        获得指定排名的玩家和分数
        :param rankingMax: 最大排名，加载的TopN人数
        :param rankNumberList: 指定名次的列表, 从1开始[1,2,3,10,50]
        '''
        issueNum = cls.getYesterdayRankingIssueNumber()
        replays = replay_service.getTopNReplayWithViewsCount(issueNum, rankingMax)
        if ftlog.is_debug():
            ftlog.debug('RankingProxy.getRankingListByRankNumberList:',
                        'issueNum=', issueNum,
                        'rankingMax=', rankingMax,
                        'rankNumberList=', rankNumberList,
                        'replays.length', len(replays))
        
        rankingList = []
        for index, item in enumerate(replays):
            replay, replayCount = item
            rankNumber = index + 1
            if rankNumber in rankNumberList: 
                if ftlog.is_debug():
                    ftlog.debug('RankingProxy.getRankingListByRankNumberList',
                                'replay.userId=', replay.userId,
                                'replayCount=', replayCount)
                rankingList.append({
                    'rankNumber': rankNumber,
                    'nickname': UserInfo.getNickname(replay.userId),
                    'rankValue': replayCount,
                })
        if ftlog.is_debug():
            ftlog.debug('RankingProxy.getRankingListByRankNumberList:rankingList=', rankingList)
        return rankingList

    @classmethod
    def getRankNumberByUserId(cls, rankingMax, userId):
        '''
        获取用户排名(从1开始，若未上榜则返回-1)
        :param rankingMax: 最大排名，加载的TopN人数
        '''
        issueNum = cls.getYesterdayRankingIssueNumber()
        replays = replay_service.getTopNReplay(issueNum, rankingMax)
        for i, replay in enumerate(replays):
            if replay.userId == userId:
                return i + 1
        return -1

    @classmethod
    def getYesterdayRankingIssueNumber(cls):
        '''
        获得昨天的排行榜的期号
        @return: issueNumber
        '''
        yesterdayTimestamp = pktimestamp.getCurrentTimestamp() - 24*60*60
        return replay_service.getIssueNumber(yesterdayTimestamp)
        
    
#     @classmethod
#     def getRankingPrizesByRankNumber(cls, rankingId, rankNumber):
#         ''' 
#         根据名次获得其奖励
#         @return: None/{"itemId":"item:1901", "count":1} 
#         '''
#         rankingDefine = hallranking.rankingSystem.findRankingDefine(rankingId)
#         if not rankingDefine:
#             return None
#         rankingRankRewards = rankingDefine.getRewardsByRank(rankNumber)
#         if not rankingRankRewards:
#             return None
#         return rankingRankRewards.rewardContent.toDict()

class TableReplayRanking(TYActivity):
    '''
    牌局重放排行榜活动
    '''
    TYPE_ID = 6013

    def __init__(self, dao, clientConfig, serverConfig):
        super(self.__class__, self).__init__(dao, clientConfig, serverConfig)
        ftlog.debug('TableReplayRanking.__init__')
        
        # 注册监听事件
        self.registerEvents()
        
    def registerEvents(self):
        ftlog.debug('TableReplayRanking.registerEvents')
        TGDizhu.getEventBus().subscribe(ReplayViewEvent, self.onTableReplay)
        
    def onTableReplay(self, event):
        if ftlog.is_debug():
            ftlog.debug('TableReplayRanking.onTableReplay',
                        'userId=', event.userId)
        
        # 检测活动是否过期
        if not self.checkOperative():
            ftlog.debug('TableReplayRanking.onTableReplay:checkOperative()->False',
                        'userId=', event.userId)
            return
        
        # 加载最新的活动数据，并且当天重放次数加一
        model = ActivityUserModel.loadModel(DIZHU_GAMEID, self.getid(), event.userId)
        model.incrReplayCount()
        
        # 同时满足日上限
        replayPrizeDayUpperLimit = Tool.dictGet(self._clientConf, 'config.server.replayPrizeDayUpperLimit', 50)
        if ftlog.is_debug():
            ftlog.debug('TableReplayRanking.onTableReplay',
                        'userId=', event.userId,
                        'replayPrizeDayUpperLimit=', replayPrizeDayUpperLimit,
                        'model.replayDayCounter=', model.replayDayCounter)
        if model.replayDayCounter <= replayPrizeDayUpperLimit:
            mail = Tool.dictGet(self._clientConf, 'config.server.mail')
            replayPrizeList = Tool.dictGet(self._clientConf, 'config.server.replayPrizeList', [])
            prizeCount = self.sendPrizeToUser(event.userId, replayPrizeList, mail)
            model.prizeCounter += prizeCount
            if ftlog.is_debug():
                ftlog.debug('TableReplayRanking.onTableReplay',
                            'userId=', event.userId,
                            'replayPrizeList=', replayPrizeList,
                            'prizeCount=', prizeCount,
                            'model.prizeCounter=', model.prizeCounter)
        
        # 存储用户活动数据
        ActivityUserModel.saveModel(model, DIZHU_GAMEID, self.getid(), event.userId)
        
    def sendPrizeToUser(self, userId, prizeList, mail):
        counter = 0
        for prize in prizeList:
            prizeContent = hallitem.buildContent(prize['itemId'], prize['count'], True)
            mailmessage = strutil.replaceParams(mail, {'prizeContent': prizeContent})
            UserBag.sendAssetsToUser(DIZHU_GAMEID, userId, prize, 'ACT_TABLE_REPLAY_RANKING_PRIZE', mailmessage, 0)
            ftlog.info('TableReplayRanking.sendPrizeToUser',
                       'userId=', userId,
                       'prize=', prize)
            counter += prize['count']
        return counter

    def buildActivityInfo(self, userId):
        if ftlog.is_debug():
            ftlog.debug('TableReplayRanking.buildActivityInfo',
                        'userId=', userId)
        clientconf = copy.deepcopy(self._clientConf)
        
        # 分享按钮的todotask
        todoconf = clientconf['config']['client']['buttonShare'].get('todotask')
        if todoconf:
            clientId = sessiondata.getClientId(userId)
            todotask = TodoTaskRegister.decodeFromDict(todoconf).newTodoTask(DIZHU_GAMEID, userId, clientId)
            clientconf['config']['client']['buttonShare']['todotask'] = todotask.toDict()
        
        # 活动期间奖励累计总数
        model = ActivityUserModel.loadModel(DIZHU_GAMEID, self.getid(), userId)
        clientconf['config']['client']['myPrizeCount'] = model.prizeCounter

        rankingDisplayRankNumberList = Tool.dictGet(self._clientConf, 'config.server.rankingDisplayRankNumberList', [])
        myRankNumberNotOnRanking = Tool.dictGet(self._clientConf, 'config.server.myRankNumberNotOnRanking', '')
        myRankNumberFormat = Tool.dictGet(self._clientConf, 'config.server.myRankNumberFormat', '')
        rankingMax = Tool.dictGet(self._clientConf, 'config.server.rankingMax', 50)

        # 获得玩家排名信息
        clientconf['config']['client']['myRankNumber'] = myRankNumberNotOnRanking
        rankNumber = RankingProxy.getRankNumberByUserId(rankingMax, userId)
        if ftlog.is_debug():
            ftlog.debug('TableReplayRanking.buildActivityInfo',
                        'userId=', userId,
                        'rankNumber=', rankNumber)
        if rankNumber > 0:
            myRankNumber = strutil.replaceParams(myRankNumberFormat, {'rankNumber': rankNumber})
            clientconf['config']['client']['myRankNumber'] = myRankNumber

        # 摘取固定的几个排名数据
        rankingList = RankingProxy.getRankingListByRankNumberList(rankingMax, rankingDisplayRankNumberList)
        clientconf['config']['client']['rankingList'] = rankingList
        if ftlog.is_debug():
            ftlog.debug('TableReplayRanking.buildActivityInfo',
                        'userId=', userId,
                        'clientInfo=', clientconf['config']['client'])
        return clientconf
    
    def getConfigForClient(self, gameId, userId, clientId):
        if ftlog.is_debug():
            ftlog.debug('TableReplayRanking.getConfigForClient:',
                'userId=', userId, 
                'gameId=', gameId,  
                'clientId', clientId, 
                'serverconf=', self._serverConf, 
                'clientconf=', self._clientConf)
        return self.buildActivityInfo(userId)

    def handleRequest(self, msg):
        if ftlog.is_debug():
            ftlog.debug('TableReplayRanking.handleRequest')
        userId = msg.getParam('userId')
        return self.buildActivityInfo(userId)

def initialize():
    ftlog.info('table_replay_ranking.initialize')
    
