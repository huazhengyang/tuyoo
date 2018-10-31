# -*- coding:utf-8 -*-
'''
Created on 2018年3月30日

@author: wangyonghui
'''
from sre_compile import isstring

from datetime import datetime

from poker.entity.biz.exceptions import TYBizConfException
from poker.entity.game.rooms.arena_match_ctrl.exceptions import MatchSigninException, EnterMatchLocationException, MatchException
from poker.entity.game.rooms.arena_match_ctrl.match import MatchStageConf, MatchRankLine, MatchConf, TipsConfig, MatchRankRewards, MatchFee, FeeReward, \
    MatchStage, MatchInstance, Match, MatchPlayer
import freetime.util.log as ftlog
import poker.util.timestamp as pktimestamp


class DizhuMatchStageConf(MatchStageConf):
    def __init__(self, index):
        super(DizhuMatchStageConf, self).__init__(index)
        # rankLine, 混房阶段
        self.rankLineList = []

    def getRankLine(self, mixId=None):
        if ftlog.is_debug():
            mixRankLine = None
            if mixId:
                for rl in self.rankLineList:
                    if rl['mixId'] == mixId:
                        mixRankLine = rl['rankLine']
            ftlog.debug('DizhuMatchStageConf.getRankLine mixId=', mixId,
                        'rankLine=', self.rankLine,
                        'mixRankLine=', mixRankLine)

        if self.rankLine:
            return self.rankLine

        if mixId:
            for rl in self.rankLineList:
                if rl['mixId'] == mixId:
                    return rl['rankLine']
        return self.rankLineList[0]['rankLine']

    def addInitScoreToAll(self, initChip):
        if self.rankLine:
            self.rankLine.addInitChip(initChip)
            return

        if self.rankLineList:
            for rl in self.rankLineList:
                rl['rankLine'].addInitChip(initChip)
            return


    def decodeFromDict(self, d):
        self.name = d.get('name', '')
        if not isstring(self.name):
            raise TYBizConfException(d, 'DizhuMatchStageConf.name must string')
        self.animationType = d.get('animationType', 0)
        if not isinstance(self.animationType, int):
            raise TYBizConfException(d, 'DizhuMatchStageConf.animationType must int')
        self.cardCount = d.get('cardCount')
        if not isinstance(self.cardCount, int) or self.cardCount <= 0:
            raise TYBizConfException(d, 'DizhuMatchStageConf.cardCount must be int > 0')
        self.totalUserCount = d.get('totalUserCount')
        if not isinstance(self.totalUserCount, int) or self.totalUserCount <= 0:
            raise TYBizConfException(d, 'DizhuMatchStageConf.totalUserCount must be int > 0')
        self.riseUserCount = d.get('riseUserCount')
        if not isinstance(self.riseUserCount, int) or self.riseUserCount <= 0:
            raise TYBizConfException(d, 'DizhuMatchStageConf.riseUserCount must be int > 0')
        self.scoreInit = d.get('scoreInit')
        if not isinstance(self.scoreInit, int) or self.scoreInit < 0:
            raise TYBizConfException(d, 'DizhuMatchStageConf.scoreInit must be int >= 0')
        self.scoreIntoRate = d.get('scoreIntoRate')
        if not isinstance(self.scoreInit, (int, float)) or self.scoreIntoRate <= 0 or self.scoreIntoRate > 1:
            raise TYBizConfException(d, 'DizhuMatchStageConf.scoreInit must in (0,1]')
        self.scoreIntoRateHigh = d.get('scoreIntoRateHigh', None)
        if self.scoreIntoRateHigh:
            if not isinstance(self.scoreInit, (int, float)) or self.scoreIntoRate <= 0 or self.scoreIntoRate > 1:
                raise TYBizConfException(d, 'DizhuMatchStageConf.scoreIntoRateHigh must in (0,1]')
        rankLine = d.get('rankLine')

        if ftlog.is_debug():
            ftlog.debug('DizhuMatchStageConf.rankLine =', rankLine, 'rankList=', d.get('rankLineList'))

        if rankLine:
            self.rankLine = MatchRankLine().decodeFromDict(rankLine)
        else:
            rankLineList = d.get('rankLineList')
            try:
                self.rankLineList = [{'mixId': rankLine['mixId'], 'rankLine': MatchRankLine().decodeFromDict(rankLine['rankLine'])} for rankLine in
                                     rankLineList]
            except Exception, e:
                raise TYBizConfException(d, 'DizhuMatchStageConf.rankLineList err=' % e.message)

        self.reviveCondition = d.get('reviveCondition')
        if self.reviveCondition and not isinstance(self.reviveCondition, dict):
            raise TYBizConfException(d, 'DizhuMatchStageConf.reviveCondition must be dict')
        return self
    

class DizhuMatchConf(MatchConf):
    def __init__(self):
        super(DizhuMatchConf, self).__init__()

    def decodeFromDict(self, d):
        self.matchId = d.get('matchId')
        if not isinstance(self.matchId, int):
            raise TYBizConfException(d, 'DizhuMatchConf.matchId must be int')

        self.recordId = d.get('recordId', self.matchId)
        if not isinstance(self.recordId, int):
            raise TYBizConfException(d, 'DizhuMatchConf.recordId must be int')

        self.baseScore = d.get('baseScore')
        if not isinstance(self.baseScore, int) or self.baseScore <= 0:
            raise TYBizConfException(d, 'DizhuMatchConf.baseScore must be int > 0')

        stages = d.get('stages')
        if not isinstance(stages, list) or not stages:
            raise TYBizConfException(d, 'DizhuMatchConf.stages must not emptylist')

        for i, stageConf in enumerate(stages):
            stage = DizhuMatchStageConf(i).decodeFromDict(stageConf)
            self.stages.append(stage)

        initChip = self.stages[0].scoreInit
        for stage in self.stages:
            initChip = int(initChip * stage.scoreIntoRate)
            # stage.getRankLine().addInitChip(initChip)
            stage.addInitScoreToAll(initChip)

        self.tableSeatCount = d.get('tableSeatCount')
        if not isinstance(self.tableSeatCount, int) or self.tableSeatCount <= 0:
            raise TYBizConfException(d, 'DizhuMatchConf.tableSeatCount must be int > 0')

        self.tableMaxTimes = d.get('tableMaxTimes', 480)
        if not isinstance(self.tableMaxTimes, int) or self.tableMaxTimes <= 0:
            raise TYBizConfException(d, 'DizhuMatchConf.tableMaxTimes must be int > 0')

        self.prepareStopSeconds = d.get('prepareStopSeconds', 5 * 60)
        if not isinstance(self.prepareStopSeconds, int) or self.prepareStopSeconds <= 0:
            raise TYBizConfException(d, 'DizhuMatchConf.prepareStopSeconds must be int > 0')

        self.minSigninCount = d.get('minSigninCount')
        if not isinstance(self.minSigninCount, int) or self.minSigninCount < self.tableSeatCount:
            raise TYBizConfException(d, 'DizhuMatchConf.minSigninCount must be int > %s' % self.tableSeatCount)

        self.maxSigninCount = d.get('maxSigninCount')
        if not isinstance(self.maxSigninCount, int) or self.maxSigninCount < self.minSigninCount:
            raise TYBizConfException(d, 'DizhuMatchConf.maxSigninCount must be int > %s' % self.minSigninCount)

        self.maxPlayerCount = d.get('maxPlayerCount')
        if not isinstance(self.maxPlayerCount, int):
            raise TYBizConfException(d, 'DizhuMatchConf.maxPlayerCount must be int > 0')

        self.processSigninIntervalSeconds = d.get('processSigninIntervalSeconds')
        if not isinstance(self.processSigninIntervalSeconds, int) or self.processSigninIntervalSeconds <= 0:
            raise TYBizConfException(d, 'DizhuMatchConf.processSigninIntervalSeconds must be int > 0')

        self.processSigninCountPerTime = d.get('processSigninCountPerTime')
        if not isinstance(self.processSigninCountPerTime, int) or self.processSigninCountPerTime <= 0:
            raise TYBizConfException(d, 'DizhuMatchConf.processSigninCountPerTime must be int > 0')

        # 每次处理座位数的倍数
        self.processSigninCountPerTime = (self.processSigninCountPerTime + self.tableSeatCount - 1) * self.tableSeatCount / self.tableSeatCount

        tips = d.get('tips', {})
        self.tips = TipsConfig().decodeFromDict(tips)

        startTime = stopTime = None
        try:
            startTime = d.get('startTime')
            startTime = datetime.strptime(startTime, '%H:%M').time()
        except Exception, e:
            raise TYBizConfException(d, 'DizhuMatchConf.startTime must be time HH:MM %s' % startTime)

        try:
            stopTime = d.get('stopTime')
            stopTime = datetime.strptime(stopTime, '%H:%M').time()
        except Exception, e:
            raise TYBizConfException(d, 'DizhuMatchConf.stopTime must be time HH:MM %s' % stopTime)

        self.startTime = startTime
        self.stopTime = stopTime

        self.tipsForNotSignin = d.get('tipsForNotSignin')
        if not isstring(self.tipsForNotSignin) or not self.tipsForNotSignin:
            raise TYBizConfException(d, 'DizhuMatchConf.tipsForNotSignin must not empty string')

        self.tipsForWillStopInfo = d.get('tipsForWillStopInfo')
        if not isstring(self.tipsForWillStopInfo) or not self.tipsForWillStopInfo:
            raise TYBizConfException(d, 'DizhuMatchConf.tipsForWillStopInfo must not empty string')

        self.lifeSafeCount = d.get('lifeSafeCount', 0)
        if not isinstance(self.lifeSafeCount, (int, float)):
            raise TYBizConfException(d, 'DizhuMatchConf.lifeSafeCount must be int or float')
        self.dailySafeCount = d.get('dailySafeCount', 0)
        if not isinstance(self.dailySafeCount, (int, float)):
            raise TYBizConfException(d, 'DizhuMatchConf.dailySafeCount must be int or float')
        self.safeAddScore = d.get('safeAddScore', 0)
        if not isinstance(self.safeAddScore, (int, float)):
            raise TYBizConfException(d, 'DizhuMatchConf.safeAddScore must be int or float')

        feeRewardConfList = d.get('feeRewardList', [])
        if not feeRewardConfList:
            rankRewardsList = []
            for rankRewardsConf in d.get('rank.rewards', []):
                rankRewardsList.append(MatchRankRewards().decodeFromDict(rankRewardsConf))

            fees = []
            # 多种报名条件，当前的多种报名条件是都扣取的，是个报名费用集合而非多种报名条件
            # 是与的关系非或的关系
            for fee in d.get('fees', []):
                fees.append(MatchFee().decodeFromDict(fee))

            self.feeRewardList.append(FeeReward(fees, rankRewardsList, ''))
        else:
            for feeRewardConf in feeRewardConfList:
                fees = []
                for fee in feeRewardConf.get('fees', []):
                    fees.append(MatchFee().decodeFromDict(fee))
                rankRewardsList = []
                for rankRewardsConf in feeRewardConf.get('rank.rewards', []):
                    rankRewardsList.append(MatchRankRewards().decodeFromDict(rankRewardsConf))
                roomName = feeRewardConf.get('roomName', '')
                mixId = feeRewardConf.get('mixId')

                self.feeRewardList.append(FeeReward(fees, rankRewardsList, roomName, mixId))
        if ftlog.is_debug():
            ftlog.debug('DizhuMatchConf.feeRewardList=', [(fr.roomName, fr.mixId) for fr in self.feeRewardList],
                        'feeRewardConfList=', feeRewardConfList)
        return self


class DizhuMatchStage(MatchStage):
    def __init__(self, matchInst, index):
        super(DizhuMatchStage, self).__init__(matchInst, index)

    def calcRank(self, score, mixId=None):
        startRank, _endRank = self.stageConf.getRankLine(mixId).calcRankRange(score)
        return startRank


class DizhuMatchInstance(MatchInstance):
    def __init__(self, match, instId, matchConf, startDT, stopDT):
        super(DizhuMatchInstance, self).__init__(match, instId, matchConf, startDT, stopDT)

    def doUserRevive(self, player, isRevive):
        ''' 如果是第一个用户reset '''
        if player.userId not in self._waitRevivePlayersMap:
            ftlog.warn('MatchInstance.revive doUserRevive matchId=', self.matchId,
                       'instd=', self.instId,
                       'userId=', player.userId,
                       'isRevive=', isRevive,
                       'revivePlayer=', self._waitRevivePlayersMap.keys())
            return False

        # 删除等待用户
        del self._waitRevivePlayersMap[player.userId]

        # 正好是当前timer处理用户， 需要重置
        if self._reviveProcesser._currentUserId == player.userId:
            self._resetReviveTimer()

        # 复活或者出局
        if isRevive:
            player.score = player.stage.stageConf.getRankLine(player.mixId).getMinScoreByRank(player.stage.stageConf.reviveCondition.get('rank'))
            player.isFromRevive = True
            player.rank = player.stage.calcRank(player.score, player.mixId)
            self._winlosePlayerList.append(player)
        else:
            self._outPlayer(player)

        ftlog.info('MatchInstance.revive doUserRevive matchId=', self.matchId,
                   'instd=', self.instId,
                   'userId=', player.userId,
                   'isRevive=', isRevive,
                   'revivePlayer=', len(self._waitRevivePlayersMap))
        return True

    def winlose(self, player, deltaScore, isWin, isKill=False):
        # 处理分数和状态，加入到winlose列表
        ftlog.hinfo('MatchInstance.winlose matchId=', self.matchId,
                    'instId=', self.instId,
                    'stageIndex=', player.stage.index,
                    'state=', self.state,
                    'userId=', player.userId,
                    'signinParams=', player.signinParams,
                    'tableId=', player.table.tableId if player.table else None,
                    'curScore=', player.score,
                    'deltaScore=', deltaScore,
                    'isWin=', isWin,
                    'isKill=', isKill)
        assert (player.state == MatchPlayer.STATE_PLAYING)
        # 比赛即将结束，此时不处理输赢事件了
        if self.state >= MatchInstance.STATE_STOP:
            return
        player.score += deltaScore
        player._state = MatchPlayer.STATE_WINLOSE
        player.isWin = isWin
        table = player.table

        # 生涯保护或者每日保护，首轮加积分
        if self._isFirstStage(player.stage):
            safe = self.checkSafe(player)
            if safe:
                player.matchSafeChanged = True
                player.score += self.matchConf.safeAddScore
                ftlog.hinfo('AddSafeScore matchId=', self.matchId,
                            'instId=', self.instId,
                            'stageIndex=', player.stage.index,
                            'state=', self.state,
                            'userId=', player.userId,
                            'signinParams=', player.signinParams,
                            'tableId=', player.table.tableId if player.table else None,
                            'curScore=', player.score,
                            'deltaScore=', deltaScore,
                            'checkSafe=', safe,
                            'lifeSafe=', (player.matchSafe.lifeSafe.count, player.matchSafe.lifeSafe.timestamp),
                            'dailySafe=', (player.matchSafe.dailySafe.count, player.matchSafe.dailySafe.timestamp),
                            'safeAddScore=', self.matchConf.safeAddScore,
                            'isWin=', isWin,
                            'isKill=', isKill)

        if not table:
            playerList = [player]
            player.tableRank = 3
            if self._isLastStage(player.stage):
                # 最后一个阶段按照桌子分数排名
                player.rank = player.tableRank
            else:
                # 其它阶段按照分数线排名
                player.rank = player.stage.calcRank(player.score, player.mixId)
            self._addToWinloseList(playerList)
        elif self._isAllPlayerWinlose(table):
            playerList = table.getPlayerList()
            self._sortTableRank(playerList)

            for player in playerList:
                # 记录上次排名
                player.prevRank = player.rank
                if self._isLastStage(player.stage):
                    # 最后一个阶段按照桌子分数排名
                    player.rank = player.tableRank
                else:
                    # 其它阶段按照分数线排名
                    player.rank = player.stage.calcRank(player.score, player.mixId)

            # 让该桌子上的用户站起, 释放桌子
            self._clearAndReleaseTable(table)

            # 添加到一局完成列表
            self._addToWinloseList(playerList)

    def _createStages(self):
        self._stages = []
        for index in xrange(len(self.matchConf.stages)):
            stage = DizhuMatchStage(self, index)
            self._stages.append(stage)

    def signin(self, userId, signinParams, feeIndex):
        player = None
        mixId = signinParams.get('mixId', 0)
        try:
            fees = self.matchConf.getFees(mixId)
            if fees and (feeIndex < 0 or feeIndex >= len(fees)):
                ftlog.warn('MatchInstance.signin failed matchId=', self.matchId,
                           'instId=', self.instId,
                           'userId=', userId,
                           'signinParams=', signinParams,
                           'feeIndex=', feeIndex)
                raise MatchSigninException(self.matchId, 4, '请选择报名费')

            # 确认可以报名
            self._ensureCanSignin(userId)

            # 生成玩家对象
            player = MatchPlayer(self, userId, pktimestamp.getCurrentTimestamp())
            player.isenter = True
            player.signinParams = signinParams

            # 标志用户是否需要大衰减(对于“已获奖玩家”，一定时间及局数内)
            if hasattr(self.match.playerNotifier, 'getUserChampionLimitFlag'):
                championLimitFlag = self.match.playerNotifier.getUserChampionLimitFlag(player)
                player.championLimitFlag = championLimitFlag
                if ftlog.is_debug():
                    ftlog.debug('MatchInstance.signin userId=', player.userId,
                                'instId=', self.instId,
                                'championLimitFlag=', championLimitFlag)
            # 收取报名费
            self._collectFee(player, fees, feeIndex)
            if not self._lockPlayer(player):
                raise EnterMatchLocationException(self.matchId)

            # 此处需要再次确认可以报名，因为collectFees可能是异步的
            self._ensureCanSignin(userId)

            # 加入报名队列
            self._signinMap[userId] = player

            self._match.signinRecordDao.recordSignin(self.matchId, self.instId, userId,
                                                     pktimestamp.getCurrentTimestamp(), signinParams)
            # TODO publish event
            ftlog.info('MatchInstance.signin ok matchId=', self.matchId,
                       'instId=', self.instId,
                       'userId=', userId,
                       'signinParams=', player.signinParams,
                       'fee=', player.paidFee.toDict() if player.paidFee else None,
                       'signinCount=', len(self._signinMap))

            # 填充用户信息
            self._fillPlayer(player)
            return player
        except MatchException:
            if player:
                self._returnFee(player)
                self._unlockPlayer(player)
            raise


class DizhuMatch(Match):
    def __init__(self, matchConf):
        super(DizhuMatch, self).__init__(matchConf)

    def _createInstance(self):
        startDT, stopDT = self.matchConf.calcNextTime()
        instId = '%s.%s' % (self.matchId, startDT.strftime('%y%m%d%H%M'))
        ftlog.info('Match._createInstance matchId=', self.matchId,
                   'startTime=', startDT.strftime('%Y-%m-%d %H:%M:%S'),
                   'stopDT=', stopDT.strftime('%Y-%m-%d %H:%M:%S'),
                   'instId=', instId)
        return DizhuMatchInstance(self, instId, self.matchConf, startDT, stopDT)

