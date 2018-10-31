# -*- coding=utf-8 -*-
'''
Created on 2016.12.01

@author: luwei

在CT进程运行发奖轮询，每小时整点正式检测发奖，若用户没有发奖则给用户按照昨天的排名发奖
'''

from datetime import datetime

from dizhu.entity.dizhuconf import DIZHU_GAMEID
from dizhu.replay import replay_service
from freetime.core.timer import FTTimer
import freetime.util.log as ftlog
from hall.entity import hallitem
from hall.servers.util.rpc import user_remote
import poker.entity.biz.message.message as pkmessage
from poker.entity.biz.ranking.rankingsystem import TYRankingRankReward
from poker.entity.configure import configure
from poker.entity.dao import daobase
from poker.util import strutil
import poker.util.timestamp as pktimestamp

def getRankingPrizeItemList():
    ''' 
    获得排行榜奖励对象列表list<TYRankingRankReward> 
    '''
    conf = configure.getGameJson(DIZHU_GAMEID, 'replay', {}, configure.DEFAULT_CLIENT_ID)
    rankingPrizeListConf = conf.get('rankingPrizeList', [])
    return [TYRankingRankReward.decodeFromDict(conf) for conf in rankingPrizeListConf]

def getReplayRankingPrizeSentMail():
    conf = configure.getGameJson(DIZHU_GAMEID, 'replay', {}, configure.DEFAULT_CLIENT_ID)
    return conf.get('rankingPrizeMail', '')

def getYesterdayRankingIssueNumber():
    ''' 
    获得昨天的排行榜的期号 
    '''
    yesterdayTimestamp = pktimestamp.getCurrentTimestamp() - 24*60*60
    return replay_service.getIssueNumber(yesterdayTimestamp)

def getPrizeItemByRankNumber(rankingPrizeItemList, rankNumber):
    ''' 
    根据排名获得排行榜奖励对象 
    '''
    if rankingPrizeItemList:
        for prizeItem in rankingPrizeItemList:
            if prizeItem.startRank > 0 and rankNumber < prizeItem.startRank:
                continue
            if prizeItem.endRank > 0 and rankNumber > prizeItem.endRank:
                continue
            return prizeItem
    return None

def getRankNumberMax(rankingPrizeItemList):
    ''' 
    获得排行榜奖励中排名最大的排名值 
    '''
    maxRankNumber = 0
    for prizeItem in rankingPrizeItemList:
        if prizeItem.endRank > maxRankNumber:
            maxRankNumber = prizeItem.endRank
    return maxRankNumber

def sendUserAssets(gameId, userId, contentItems, rankNumber):
    if ftlog.is_debug():
        ftlog.debug('replay_ranking_prize_sender.sendUserAssets',
                    'gameId=', gameId,
                    'userId=', userId,
                    'contentItems=', contentItems,
                    'rankNumber=', rankNumber)
    dictContentItems = [{'itemId': item.assetKindId, 'count': item.count} for item in contentItems]
    ok = user_remote.addAssets(gameId, userId, dictContentItems, 'REPLAY_RANK_PRIZE', 0)
    if ok:
        prizeContent = hallitem.buildContentsString(contentItems, True)
        mail = strutil.replaceParams(getReplayRankingPrizeSentMail(), {'prizeContent':prizeContent, 'rankNumber': rankNumber})
        if mail:
            pkmessage.sendPrivate(9999, userId, 0, mail)
    else:
        ftlog.warn('replay_ranking_prize_sender.sendUserAssets: send error',
                    'gameId=', gameId,
                    'userId=', userId,
                    'contentItems=', contentItems)
    return ok

def buildReplayRankingPrizeKey(issueNumber):
    return 'replay.rank.prize:6:%s' % (str(issueNumber))

def setVideoPrizeSentByIssueNumber(issueNumber, videoId):
    ''' 
    设置用户奖励发送标记，若成功返回True才可以发送奖励，否则代表已经发放奖励 
    '''
    isNotSent = daobase.executeRePlayCmd('HINCRBY', buildReplayRankingPrizeKey(issueNumber), videoId, 1) == 1
    if ftlog.is_debug():
        ftlog.debug('replay_ranking_prize_sender.setVideoPrizeSentByIssueNumber', 
                    'videoId=', videoId, 
                    'issueNumber=', issueNumber, 
                    'isNotSent=', isNotSent)
    return isNotSent

def clearVideoPrizeSentFlagByIssueNumber(issueNumber, videoId):
    ''' 
    清除用户发送奖励的标记，在发送失败时调用，以便重发 
    '''
    if ftlog.is_debug():
        ftlog.debug('replay_ranking_prize_sender.clearVideoPrizeSentFlagByIssueNumber', 
                    'videoId=', videoId, 
                    'issueNumber=', issueNumber)
    daobase.executeRePlayCmd('HDEL', buildReplayRankingPrizeKey(issueNumber), videoId)

def checkReplayRankingPrizeTime():
    ''' 检测重放排行榜发奖有效期 '''
    conf = configure.getGameJson(DIZHU_GAMEID, 'replay', {}, configure.DEFAULT_CLIENT_ID)
    rankingPrizeDatetime = conf.get('rankingPrizeDatetime')
    if not rankingPrizeDatetime:
        if ftlog.is_debug():
            ftlog.debug('replay_ranking_prize_sender.checkReplayRankingPrizeTime:',
                        'rankingPrizeDatetime is None')
        return False
    prizeStartTimeStr = rankingPrizeDatetime.get('datetime_start')
    prizeEndTimeStr = rankingPrizeDatetime.get('datetime_end')
    if not prizeStartTimeStr or not prizeEndTimeStr:
        if ftlog.is_debug():
            ftlog.debug('replay_ranking_prize_sender.checkReplayRankingPrizeTime:',
                        'prizeStartTimeStr or prizeEndTimeStr is None')
        return False
    
    dateNow = datetime.now()
    dateStart = pktimestamp.parseTimeSecond(prizeStartTimeStr)
    dateEnd = pktimestamp.parseTimeSecond(prizeEndTimeStr)
    if ftlog.is_debug():
        ftlog.debug('replay_ranking_prize_sender.checkReplayRankingPrizeTime:',
                    'dateNow=', dateNow, 
                    'dateStart=', dateStart, 
                    'dateEnd=', dateEnd)
    return dateStart<=dateNow and dateNow<=dateEnd

def calculateNextHourLeftSeconds():
    ''' 计算当前到整点的剩余时间 '''
    now = datetime.now()
#     return 60 * 60 - (now.minute * 60 + now.second)
    return 60
    # return 86400 - pktimestamp.getDayPastSeconds() + 2*60*60

def onReplayRankingPrizeSent():
    if ftlog.is_debug():
        ftlog.debug('replay_ranking_prize_sender.onReplayRankingPrizeSent')
        
    FTTimer(calculateNextHourLeftSeconds(), onReplayRankingPrizeSent)
    if not checkReplayRankingPrizeTime():
        if ftlog.is_debug():
            ftlog.debug('replay_ranking_prize_sender.onReplayRankingPrizeSent: overdue')
        return
    
    # 获得排行榜奖励对象list<TYRankingRankReward>
    rankingPrizeItemList = getRankingPrizeItemList()
    rankingMax = getRankNumberMax(rankingPrizeItemList)
    issueNumber = getYesterdayRankingIssueNumber()
    replays = replay_service.getTopNReplay(issueNumber, rankingMax)
    if ftlog.is_debug():
        ftlog.debug('replay_ranking_prize_sender.onReplayRankingPrizeSent:',
                    'issueNumber=', issueNumber,
                    'rankingMax=', rankingMax,
                    'replays.userIds', [r.userId for r in replays])
        
    for index, replay in enumerate(replays):
        rankNumber = index + 1
        try:
            prizeItem = getPrizeItemByRankNumber(rankingPrizeItemList, rankNumber)
            if not prizeItem or not prizeItem.rewardContent:
                continue
            contentItems = prizeItem.rewardContent.getItems()
            if ftlog.is_debug():
                ftlog.debug('replay_ranking_prize_sender.onReplayRankingPrizeSent',
                            'userId=', replay.userId, 
                            'rankNumber=', rankNumber, 
                            'contentItems=', contentItems)
            if setVideoPrizeSentByIssueNumber(issueNumber, replay.videoId):
                ok = sendUserAssets(DIZHU_GAMEID, replay.userId, contentItems, rankNumber)
                if not ok:
                    clearVideoPrizeSentFlagByIssueNumber(issueNumber, replay.videoId)
        except:
            clearVideoPrizeSentFlagByIssueNumber(issueNumber, replay.videoId)
            ftlog.error('replay_ranking_prize_sender.onReplayRankingPrizeSent: send error')

def initialize():
    ftlog.info('replay_ranking_prize_sender.initialize')
    FTTimer(calculateNextHourLeftSeconds(), onReplayRankingPrizeSent)
