# -*- coding=utf-8 -*-
"""
Created on 2017年7月13日

@author: wangjifa
"""

from dizhu.entity import dizhu_util
from dizhu.entity.dizhuconf import DIZHU_GAMEID, MATCH_REWARD_REDENVELOPE, MATCH_REWARD_JIADIAN
from dizhucomm.entity.events import UserTableWinloseEvent
from poker.entity.dao import daobase, gamedata
from poker.util import strutil
import freetime.util.log as ftlog


# 取比赛曾经开过的次数
def getMatchHistoryCount(bigRoomId):
    #比赛开过的局数取定值
    historyCount = {
        "6605": 730,
        "6601": 16060,
        "6604": 14600,
        "6615": 15330,
        "6602": 2190,
        "6607": 730,
        "6608": 730,
        "6609": 730,
        "6610": 730,
        "6611": 730,
        "6612": 730,
        "6613": 730,
        "6998": 730
    }

    matchHistory = daobase.executeDizhuCmd('HGET', 'matchHistoryCount:6', bigRoomId)
    if not matchHistory:
        matchHistory = historyCount.get(str(bigRoomId), 1)
        daobase.executeDizhuCmd('HSET', 'matchHistoryCount:6', bigRoomId, matchHistory)
    return matchHistory

def addMatchHistoryCount(bigRoomId, rank):
    if rank == 1:
        daobase.executeDizhuCmd('hincrby', 'matchHistoryCount:6', bigRoomId, 1)


class ShareInfo(object):
    def __init__(self, issueNum):
        self.issueNum = issueNum
        # 连胜次数
        self.winStreak = {
            '3':0,
            '4':0,
            '5':0,
            '6':0,
            '7':0,
            '8':0,
            '9':0,
            '10':0
        }
        # 对局数据 炸弹,春天,满贯,火箭,飞机
        self.roundInfo = [0,0,0,0,0] #bomb#chuntian#slam #rocket#plane
        # 游戏局数
        self.playRound = 0
        # 获胜局数
        self.winRound = 0
        # 分组赛赢取奖励
        self.groupReward = [] #["6072", "timestamp", "des", "itemId", "count"]
        # 获得count个红包 累计获得红包金额rmb元
        self.red = {} #"count":10,"rmb":200
        # 金币桌赢取总金币数
        self.winChip = 0
        # 单局最高倍
        self.maxMulti = 0

    def toDict(self):
        return {
            'wins': self.winStreak,
            'rInfo': self.roundInfo,
            'pr': self.playRound,
            'wr': self.winRound,
            'gr': self.groupReward,
            'red': self.red,
            'chip': self.winChip,
            'multi': self.maxMulti
        }

    def fromDict(self, d):
        self.winStreak = d.get('wins', {'3': 0, '4': 0, '5': 0, '6': 0, '7': 0, '8': 0, '9': 0, '10': 0})
        self.roundInfo = d.get('rInfo', [0,0,0,0,0])
        self.playRound = d.get('pr', 0)
        self.winRound = d.get('wr', 0)
        self.groupReward = d.get('gr', [])
        self.red = d.get('red', {})
        self.winChip = d.get('chip', 0)
        self.maxMulti = d.get('multi', 0)
        return self


def getUserShareInfo(userId, weekDate):
    jstr = daobase.executeUserCmd(userId, 'HGET', 'weekShareInfo:6:' + str(userId), weekDate)
    if jstr:
        d = strutil.loads(jstr)
        if ftlog.is_debug():
            ftlog.debug('getUserShareInfo weekDate=', weekDate, 'd=', d)
        return ShareInfo(weekDate).fromDict(d)
    return ShareInfo(weekDate)

def getTimeYMDStrDiff(start, end):
    try:
        start = str(start)
        end = str(end)
    except ValueError:
        ftlog.warn('dizhu.entity.getTimeYMDStrDiff ValueError')
        return 0

    from datetime import datetime
    t1 = datetime.strptime(start, '%Y%m%d')
    t2 = datetime.strptime(end, '%Y%m%d')
    diff = t2 - t1
    return int(diff.days)

def setUserShareInfo(userId, weekDate, shareInfo):
    ret = daobase.executeUserCmd(userId, 'HSET', 'weekShareInfo:6:' + str(userId), weekDate, strutil.dumps(shareInfo))
    if ftlog.is_debug():
        ftlog.debug('setUserShareInfo userId=', userId, 'weekDate=', weekDate, 'shareInfo=', shareInfo, 'ret=', ret)

    # 新增数据时删除过期的周报数据
    if ret:
        todayWeekDate = dizhu_util.calcWeekBeginIssueNum()
        shareFields = daobase.executeUserCmd(userId, 'HKEYS', 'weekShareInfo:6:' + str(userId))

        for shareField in shareFields:
            if str(shareField).isdigit() and len(str(shareField)) == 8:
                diffTime = getTimeYMDStrDiff(shareField, todayWeekDate)
                #只保存本周和上周的
                if diffTime > 7:
                    daobase.executeUserCmd(userId, 'HDEL', 'weekShareInfo:6:' + str(userId), shareField)
                    ftlog.info('setUserShareInfo delOldWeekData userId=', userId, 'weekDate=', shareField)
    return ret

# 返回本周连胜次数
def getUserWinStreakCount(userId):
    weekDate = dizhu_util.calcWeekBeginIssueNum()
    allShareInfo = getUserShareInfo(userId, weekDate)
    winStreakCount = 0
    for info in allShareInfo.winStreak:
        winStreakCount += allShareInfo.winStreak[info]
    return winStreakCount


def initialize():
    # 监听牌桌事件
    from dizhu.game import TGDizhu
    TGDizhu.getEventBus().subscribe(UserTableWinloseEvent, _onGameRoundFinish)


def _onGameRoundFinish(event):
    weekDate = dizhu_util.calcWeekBeginIssueNum()
    _careerInfoCollect(event, weekDate)
    _careerInfoCollect(event, 'career')
    _careerInfoCollect(event, 'today')


def _careerInfoCollect(event, weekDate):
    careerInfo = getUserShareInfo(event.userId, weekDate)
    stopWinStreak = 0
    try:
        stopWinStreak = gamedata.getGameAttrInt(event.userId, DIZHU_GAMEID, 'stopwinstreak')
        for info in careerInfo.winStreak:
            if int(info) == int(stopWinStreak):
                careerInfo.winStreak[info] += 1
                break
    except:
        ftlog.error('_careerInfoCollect userId=', event.userId, 'stopwinStreak=', stopWinStreak)

    if event.winlose.nBomb:
        careerInfo.roundInfo[0] += event.winlose.nBomb
    if event.winlose.chunTian:
        careerInfo.roundInfo[1] += 1
    if event.winlose.slam:
        careerInfo.roundInfo[2] += 1
    # 玩家使用火箭次数
    # if event.huojian:
    #     careerInfo.roundInfo[3] += 1
    # 玩家使用飞机次数
    # 当局倍数
    if event.winlose.baseScore:
        nbomb = event.winlose.nBomb if event.winlose.nBomb else 1
        chuntian = event.winlose.chunTian if event.winlose.chunTian else 1
        maxMulit = event.winlose.baseScore * nbomb * chuntian
        if maxMulit > careerInfo.maxMulti:
            careerInfo.maxMulti = maxMulit

    careerInfo.playRound += 1
    if event.winlose.isWin:
        careerInfo.winRound += 1
        # 玩家赢取的金币数 （暂时不包含比赛中的排名奖励/金币桌连胜奖励/贵族月卡等金币加成等收益）
        careerInfo.winChip += event.winlose.deltaChip

    if ftlog.is_debug():
        ftlog.debug('dizhushare._onGameRoundFinish userId=', event.userId,
                    'winlose=', event.winlose,
                    'nbomb=', event.winlose.nBomb,
                    'weekShareInfo=', careerInfo.toDict())

    setUserShareInfo(event.userId, weekDate, careerInfo.toDict())


def arenaMatchRewardRecord(userId, rewardShareInfo=None, recordIndex='career'):
    careerInfo = getUserShareInfo(userId, recordIndex)
    reward_count = careerInfo.red.get('count', 0)
    reward_rmb = careerInfo.red.get('rmb', 0)

    changed = False
    if rewardShareInfo:
        if rewardShareInfo.get('type', '') == MATCH_REWARD_REDENVELOPE:
            careerInfo.red['count'] = careerInfo.red.get('count', 0) + 1
            careerInfo.red['rmb'] = rewardShareInfo.get('rmb', 0) + careerInfo.red.get('rmb', 0)
            reward_count = careerInfo.red.get('count', 0)
            reward_rmb = careerInfo.red.get('rmb', 0)
            changed = True
        elif rewardShareInfo.get('type', '') == MATCH_REWARD_JIADIAN:
            careerInfo.groupReward.append(rewardShareInfo.get('name', ''))
            changed = True

    if changed:
        setUserShareInfo(userId, recordIndex, careerInfo.toDict())

    if ftlog.is_debug():
        ftlog.debug('arenaMatchRewardRecord userId=', userId,
                    'rewardShareInfo=', rewardShareInfo,
                    'recordIndex=', recordIndex,
                    'careerInfo=', careerInfo.toDict())

    return reward_count, reward_rmb


def groupMatchRewardRecord(userId, rewards, recordIndex='career'):
    careerInfo = getUserShareInfo(userId, recordIndex)
    rewardShareInfo = rewards.get('shareInfo', {})

    rewardCount = 0
    if rewardShareInfo and rewardShareInfo.get('type', '') == MATCH_REWARD_REDENVELOPE:
        careerInfo.red['count'] = careerInfo.red.get('count', 0) + 1
        careerInfo.red['rmb'] = rewardShareInfo.get('rmb', 0) + careerInfo.red.get('rmb', 0)
        rewardCount = careerInfo.red.get('count', 0)
    elif rewardShareInfo and rewardShareInfo.get('type', '') == MATCH_REWARD_JIADIAN:
        careerInfo.groupReward.append(rewardShareInfo.get('name', ''))
        rewardCount = len(careerInfo.groupReward)

    if ftlog.is_debug():
        ftlog.debug('groupMatchRewardRecord userId=', userId,
                    'rewards=', rewards,
                    'recordIndex=', recordIndex,
                    'careerInfo=', careerInfo.toDict())

    setUserShareInfo(userId, recordIndex, careerInfo.toDict())
    return rewardCount

def getGroupShareInfoNew(shareNum, roomConf, rankRewards, rankRewardsList):
    '''
    比赛结束后 返回客户端的分享内容
    :param shareNum: 玩家分享过的次数，在dizhushare中保存过
    :param roomConf: 比赛房间的配置
    :param rankRewards: 玩家本场比赛的奖励
    :param rankRewardsList: 本比赛的奖励列表
    :return:
        matchShareType：比赛的分享类型
        shareBigImg：分享的大图
        get：玩家在本场比赛是否获得了冠军奖励
    '''
    if not rankRewardsList:
        rankRewardsList = roomConf.get('matchConf', {}).get('rank.rewards', [])
    championShareInfo = rankRewardsList[0].get('shareInfo', {})
    championRewardType = championShareInfo.get('type', '')
    shareBigImg = rankRewardsList[0].get('bigImg', '')

    rewardShareInfo = rankRewards.conf.get('shareInfo', {}) if rankRewards else {}
    rewardType = rewardShareInfo.get('type', '')
    rewardRmb = rewardShareInfo.get('rmb', 0)

    newShareInfo = {
        "matchShareType": 1 if rewardType == 'redEnvelope' else 2,
        "shareNum": shareNum,
        "get": 1 if str(rewardType) == championRewardType else 0,
        "shareName": championShareInfo.get('name', ''),
        "shareTotalNum": 0,
        "shareBigImg": shareBigImg,
        "rmb": '{0:.2f}'.format(rewardRmb)
    }
    return rewardType, newShareInfo

def getArenaShareInfoNew(userId, championRewards, arenaContent, userShareInfo):
    try:
        championShareInfo = championRewards[0].rankRewardsList[0].conf.get('shareInfo', {})
        # 分ip奖励配置 若分ip则需要判断是否有冠军奖励
        if arenaContent:
            championRewards = arenaContent.get('rank.rewards', [])
            if championRewards[0].get('ranking', {}).get('start', 0) == 1:
                championShareInfo = championRewards[0].get('shareInfo', {})
        rewardType = championShareInfo.get('type', '')
        userRewardType = userShareInfo.get('type', '')
        rmb = userShareInfo.get('rmb', 0) if userRewardType == MATCH_REWARD_REDENVELOPE else championShareInfo.get('rmb', 0)
        matchShareType = 2 if cmp(rewardType, MATCH_REWARD_REDENVELOPE) else 1
        shareNum, shareTotalNum = arenaMatchRewardRecord(userId, userShareInfo)
        newShareInfo = {
            "matchShareType": matchShareType,
            "shareNum": shareNum,
            "get": 0 if cmp(userRewardType, MATCH_REWARD_REDENVELOPE) else 1,
            "shareName": userShareInfo.get('name', 0),
            "shareTotalNum": shareTotalNum,
            "rmb": '{0:.2f}'.format(rmb)
        }
        return rewardType, newShareInfo
    except Exception, e:
        ftlog.error('notifyMatchOver.getArenaShareInfoNew',
                    'userId=', userId,
                    'err=', e.message)
        return None, None



