# -*- coding:utf-8 -*-
'''
Created on 2016年7月18日

@author: zhaojiangang
'''
from datetime import datetime
import random
import time

from dizhu.entity.dizhuversion import SessionDizhuVersion
from dizhu.entity.erdayi import PlayerData
from dizhu.entity.matchrecord import MatchRecord
import dizhu.erdayimatch.erdayi3api as erdayi3api
from dizhu.servers.util.rpc import match_remote
from freetime.entity.msg import MsgPack
from hall.entity import datachangenotify
from hall.servers.util.rpc import user_remote, event_remote
import poker.entity.biz.message.message as pkmessage
from poker.entity.dao import userdata
from poker.entity.game.rooms.erdayi_match_ctrl.const import AnimationType, \
    MatchFinishReason, WaitReason, GroupingType
from poker.entity.game.rooms.erdayi_match_ctrl.exceptions import \
    BadStateException, SigninFeeNotEnoughException
from poker.entity.game.rooms.erdayi_match_ctrl.interface import SignerInfoLoader, \
    TableController, MatchStage, MatchFactory, PlayerNotifier, MatchRewards, \
    MatchUserIF, SigninFee
from poker.entity.game.rooms.erdayi_match_ctrl.match import MatchGroup
from poker.entity.game.rooms.erdayi_match_ctrl.models import Player, Table, \
    PlayerSort, PlayerQueuing, Signer
from poker.entity.game.rooms.erdayi_match_ctrl.utils import Logger
from poker.protocol import router
from poker.util import strutil
import poker.util.timestamp as pktimestamp
from dizhu.entity import dizhudiplomashare
import freetime.util.log as ftlog


class SigninFeeErdayi(SigninFee):
    def __init__(self, room):
        self._room = room
        self._logger = Logger()
        
    def collectFee(self, matchId, roomId, instId, userId, fee):
        '''
        收取用户报名费
        '''
        if userId <= 10000:
            return
        
        contentItemList = []
        contentItemList.append({'itemId':fee.assetKindId, 'count':fee.count})
        assetKindId, count = user_remote.consumeAssets(self._room.gameId, userId, contentItemList,
                                                       'MATCH_SIGNIN_FEE', self._room.roomId)
        
        self._logger.info('SigninFeeErdayi.collectFee matchId=', matchId,
                          'roomId=', roomId,
                          'instId=', instId,
                          'userId=', userId,
                          'fee=', fee.toDict(),
                          'assetKindId=', assetKindId,
                          'count=', count)
        if assetKindId:
            raise SigninFeeNotEnoughException(fee)
        return fee

    def returnFee(self, matchId, roomId, instId, userId, fee):
        '''
        退还报名费
        '''
        try:
            if userId <= 10000:
                return
            
            contentItemList = []
            contentItemList.append({'itemId':fee.assetKindId, 'count':fee.count})
            user_remote.addAssets(self._room.gameId, userId, contentItemList, 'MATCH_RETURN_FEE', self._room.roomId)
            self._logger.info('SigninFeeErdayi.returnFee matchId=', matchId,
                              'roomId=', roomId,
                              'instId=', instId,
                              'userId=', userId,
                              'fee=', fee.toDict())
        except:
            self._logger.error()
            
class CardResult(object):
    def __init__(self, player, score):
        self.player = player
        self.score = score
        # mp_score
        self.mpScore = 0
        # mp_ratio
        self.mpRate = 0
        # mp_ratio_score
        self.mpRatioScore = 0
        # mp_ratio_rank
        self.mpRatioRank = 0
        # 并列人数
        self.playerCount = 0
        # 排名
        self.rank = 0
        
class CardRanking(object):
    def __init__(self, cardNo):
        self._cardNo = cardNo
        # value=set<CardResult>
        self._ranking = []
        # 完成本副牌的玩家set
        self._playerSet = set()
        
    @property
    def cardNo(self):
        return self._cardNo
    
    @property
    def rankingList(self):
        return self._ranking
    
    @property
    def playerCount(self):
        return len(self._playerSet)
    
    @property
    def playerSet(self):
        return self._playerSet
    
    def addPlayer(self, player):
        assert(not player in self._playerSet)
        self._playerSet.add(player)
        self._update()
        for player in self._playerSet:
            player.updateScore()
        
    def _update(self):
        # key=score, value=set<CardResult>
        score2CardResultSet = {}
        resultCount = 0
        for player in self._playerSet:
            cardResult = player.getCardResult(self.cardNo)
            if cardResult:
                cardResultSet = score2CardResultSet.get(cardResult.score)
                if not cardResultSet:
                    cardResultSet = set()
                    score2CardResultSet[cardResult.score] = cardResultSet
                cardResultSet.add(cardResult)
                resultCount += 1
        
        greaterCount = 0
        scores = sorted(score2CardResultSet.keys(), reverse=True)
        cardResultSetList = [score2CardResultSet[score] for score in scores]
        
        for i, cardResultSet in enumerate(cardResultSetList):
            lessScore = (resultCount - greaterCount - len(cardResultSet)) * 2
            sameScore = len(cardResultSet) - 1
            playerCount = len(cardResultSet)
            for cardResult in cardResultSet:
                mpRatioRank = greaterCount + 1
                cardResult.playerCount = playerCount
                cardResult.mpScore = sameScore + lessScore
                cardResult.mpRate = float(cardResult.mpScore) / max(1, (2 * (resultCount - 1)))
                cardResult.mpRatioScore = self.calcRate(mpRatioRank) * 10000
                cardResult.mpRatioRank = mpRatioRank
                cardResult.rank = i + 1
            greaterCount += len(cardResultSet)
        self._ranking = cardResultSetList
        return self
    
    @classmethod
    def calcRate(cls, rank):
        rateMap = {
            1:1,
            2:0.7,
            3:0.5,
            4:0.35
        }
        rate = rateMap.get(rank)
        return 1.0 / rank if rate is None else rate
        
def staticsPlayerRanks(player):
    ret = {}
    for cardResult in player.cardResults:
        _, count = ret.get(cardResult.rank, (cardResult.rank, 0))
        ret[cardResult.rank] = (cardResult.rank, count + 1)
    return sorted(ret.values(), key=lambda item:item[0])

def cmpPlayers(p1, p2):
    # 分数多的排名靠前
    ret = cmp(p1.score, p2.score)
    if ret != 0:
        return -ret
    # 牌数多的玩家排名靠前
    ret = cmp(len(p1.cardResults), len(p2.cardResults))
    if ret != 0:
        return -ret
    # 先统计名次的数量
    p1Ranks = staticsPlayerRanks(p1)
    p2Ranks = staticsPlayerRanks(p2)
    i = 0
    while (i < len(p1Ranks) and i < len(p2Ranks)):
        ret = cmp(p1Ranks[i][0], p2Ranks[i][0])
        if ret != 0:
            return ret 
        ret = cmp(p1Ranks[i][1], p2Ranks[i][1])
        if ret != 0:
            return -ret
        i += 1
    # 比排名靠前的名次数量
    for i in xrange(len(p1.cardResults)):
        ret = cmp(p1.cardResults[i].rank, p2.cardResults[i].rank)
        if ret != 0:
            return ret
    
    ret = cmp(p1.playTime, p2.playTime)
    if ret != 0:
        return ret
    return cmp(p1.signinTime, p2.signinTime)
        
class ErdayiPlayer(Player):
    def __init__(self, userId):
        super(ErdayiPlayer, self).__init__(userId)
        # 每副牌的得分信息 CardResult
        self._cardResults = []
        # 地主插件版本
        self._clientVersion = 0
        
        self.cardStartTime = 0
        self.playTime = 0
        self.waitReason = WaitReason.UNKNOWN
        
    @property
    def cardResults(self):
        return self._cardResults
    
    @property
    def cardCount(self):
        return len(self._cardResults)
    
    def updateScore(self):
        score = 0
        for cardResult in self._cardResults:
            score += cardResult.mpRatioScore
        self.score = score
        
    def getCardResult(self, cardNo):
        assert(cardNo >= 0)
        return self._cardResults[cardNo] if cardNo < self.cardCount else None
            
    def getLastCardResult(self):
        return self._cardResults[-1] if self._cardResults else None
    
    def finishCard(self, score):
        self._cardResults.append(CardResult(self, score))
        
class SignerInfoLoaderErdayi(SignerInfoLoader):
    def __init__(self):
        self._logger = Logger()
        
    def fillSigner(self, signer):
        '''
        '''
        try:
            userName, sessionClientId, _snsId = userdata.getAttrs(signer.userId, ['name', 'sessionClientId', 'snsId'])
            signer.userName = strutil.ensureString(userName)
            signer.clientId = strutil.ensureString(sessionClientId)
            signer.gameClientVersion = SessionDizhuVersion.getVersionNumber(signer.userId)
            signer.realInfo = PlayerData.getRealInfo(signer.userId)
        except:
            self._logger.error('SignerInfoLoaderErdayi.fillSigner')
        return signer
    
class ErdayiTable(Table):
    def __init__(self, gameId, roomId, tableId, seatCount):
        super(ErdayiTable, self).__init__(gameId, roomId, tableId, seatCount)
        self.cards = None
        
class TableControllerErdayi(TableController):
    def __init__(self, area):
        self.area = area
        self._logger = Logger()
        
    @classmethod
    def buildTableInfoMessage(cls, table, msg):
        seats = []
        totalCardCount = 0
        group = table.group
        stage = table.group.stage
        
        for seat in table.seats:
            # 我的战绩
            if not seat.player:
                seats.append(None)
            else:
                seatInfo = {}
                seatInfo['userId'] = seat.player.userId
                seatInfo['rank'] = seat.player.rank
                seatInfo['score'] = seat.player.score
                seatInfo['clientId'] = seat.player.clientId
                seatInfo['ddzVer'] = seat.player.gameClientVersion
                seatInfo['cardCount'] = seat.player.cardCount + 1
                seats.append(seatInfo)
        msg.setParam('seats', seats)
        msg.setParam('gameId', table.gameId)
        msg.setParam('matchId', group.area.matchId)
        msg.setParam('roomId', table.roomId)
        msg.setParam('tableId', table.tableId)
        msg.setParam('ccrc', table.ccrc)
        msg.setParam('cards', table.cards)
        
        msg.setParam('step', {
                        'name':group.groupName if group.isGrouping else stage.stageConf.name,
                        'playerCount':group.startPlayerCount,
                        'riseCount':min(stage.stageConf.riseUserCount, group.startPlayerCount),
                        'cardCount':stage.stageConf.cardCount,
                        'animationType':stage.stageConf.animationType,
                        'totalCardCount':totalCardCount,
                        'stageIndex':stage.stageIndex,
                        'stageCount':len(group.matchConf.stages),
                        'basescore':stage.stageConf.chipBase
                    })
        return msg
    
    @classmethod
    def buildTableStartMessage(cls, table):
        msg = MsgPack()
        msg.setCmd('table_manage')
        msg.setParam('action', 'm_table_start')
        return cls.buildTableInfoMessage(table, msg)

    @classmethod
    def buildTableClearMessage(cls, table):
        msg = MsgPack()
        msg.setCmd('table_manage')
        msg.setParam('action', 'm_table_clear')
        msg.setParam('gameId', table.gameId)
        msg.setParam('matchId', table.group.matchId)
        msg.setParam('roomId', table.roomId)
        msg.setParam('tableId', table.tableId)
        msg.setParam('ccrc', table.ccrc)
        return msg
    
    def startTable(self, table):
        '''
        让桌子开始
        '''
        try:
            self._logger.info('TableControllerErdayi.startTable',
                              'groupId=', table.group.groupId,
                              'tableId=', table.tableId,
                              'userIds=', table.getUserIdList())
            # 发送tableStart
            message = self.buildTableStartMessage(table)
            router.sendTableServer(message, table.roomId)
        except:
            self._logger.error('TableControllerErdayi.startTable',
                               'groupId=', table.group.groupId,
                               'tableId=', table.tableId,
                               'userIds=', table.getUserIdList())
    
    def clearTable(self, table):
        '''
        清理桌子
        '''
        # 发送tableClear
        try:
            tableClearMessage = self.buildTableClearMessage(table)
            router.sendTableServer(tableClearMessage, table.roomId)
        except:
            self._logger.error('TableControllerErdayi.clearTable',
                               'groupId=', table.group.groupId,
                               'tableId=', table.tableId,
                               'userIds=', table.getUserIdList())
        
    def userReconnect(self, table, seat):
        '''
        用户坐下
        '''
        try:
            msg = MsgPack()
            msg.setCmd('table_manage')
            msg.setParam('action', 'm_user_reconn')
            msg.setParam('gameId', table.gameId)
            msg.setParam('matchId', table.group.area.matchId)
            msg.setParam('roomId', table.roomId)
            msg.setParam('tableId', table.tableId)
            msg.setParam('userId', seat.player.userId)
            msg.setParam('seatId', seat.seatId)
            msg.setParam('ccrc', table.ccrc)
            router.sendTableServer(msg, table.roomId)
        except:
            self._logger.error('TableControllerErdayi.userReconnect',
                               'groupId=', table.group.groupId,
                               'tableId=', table.tableId,
                               'userId=', seat.player.userId if seat.player else 0,
                               'userIds=', table.getUserIdList())

class MatchRewardsErdayi(MatchRewards):
    def __init__(self, room):
        self._room = room
        self._logger = Logger()
        self._logger.add('roomId', self._room.roomId)
        
    def sendRewards(self, player, rankRewards):
        '''给用户发送奖励'''
        try:
            self._logger.info('MatchRewardsErdayi.sendRewards',
                              'groupId=', player.group.groupId if player.group else None,
                              'score=', player.score,
                              'rank=', player.rank,
                              'rankRewards=', rankRewards.rewards)
            user_remote.addAssets(self._room.gameId, player.userId, rankRewards.rewards,
                                      'MATCH_REWARD', self._room.roomId)
            if rankRewards.message:
                message = strutil.replaceParams(rankRewards.message, {'rank':player.rank,
                                                                      'rewardContent':rankRewards.desc,
                                                                      'matchName':self._room.roomConf.get('name', '')})
                pkmessage.sendPrivate(self._room.gameId, player.userId, 0, message)
                datachangenotify.sendDataChangeNotify(self._room.gameId, player.userId, 'message')
        except:
            self._logger.error('MatchRewardsErdayi.sendRewards',
                               'groupId=', player.group.groupId if player.group else None,
                               'score=', player.score,
                               'rank=', player.rank,
                               'rankRewards=', rankRewards.rewards)

class MatchUserIFErdayi(MatchUserIF):
    def __init__(self, room, tableId, seatId):
        self._room = room
        self._tableId = tableId
        self._seatId = seatId
        self._logger = Logger()
        
    def createUser(self, matchId, ctrlRoomId, instId, userId, fee):
        contentItem = {'itemId':fee.assetKindId, 'count':fee.count} if fee else None
        return match_remote.createMatchUser(self._room.gameId,
                                            userId,
                                            contentItem,
                                            self._room.bigRoomId,
                                            instId,
                                            ctrlRoomId)
    
    def removeUser(self, matchId, ctrlRoomId, instId, userId):
        match_remote.removeMatchUser(self._room.gameId,
                                     userId,
                                     self._room.bigRoomId,
                                     instId,
                                     ctrlRoomId)
    
    def lockUser(self, matchId, ctrlRoomId, instId, userId, clientId):
        '''
        锁定用户
        '''
        return match_remote.lockMatchUser(self._room.gameId,
                                          userId,
                                          self._room.bigRoomId,
                                          instId,
                                          ctrlRoomId,
                                          self._tableId,
                                          self._seatId,
                                          clientId)
    
    def unlockUser(self, matchId, ctrlRoomId, instId, userId):
        '''
        解锁用户并
        '''
        match_remote.unlockMatchUser(self._room.gameId,
                                     userId,
                                     self._room.bigRoomId,
                                     instId,
                                     ctrlRoomId,
                                     self._tableId,
                                    self._seatId)
    
def getMatchName(room, player):
    if player.group.isGrouping:
        return '%s%s' % (room.roomConf['name'], player.group.groupName)
    return room.roomConf['name']

def buildLoserInfo(room, player):
    return '比赛：%s\n名次：第%d名\n胜败乃兵家常事 大侠请重新来过！' % (getMatchName(room, player), player.rank)
    
def buildWinInfo(room, player, rankRewards):
    if rankRewards:
        return '比赛：%s\n名次：第%d名\n奖励：%s\n奖励已发放，请您查收。' % (getMatchName(room, player), player.rank, rankRewards.desc)
    return '比赛：%s\n名次：第%d名\n。' % (getMatchName(room, player), player.rank)

class PlayerNotifierErday(PlayerNotifier):
    def __init__(self, room):
        self._room = room
        self._logger = Logger()
        
    def notifyMatchCancelled(self, signer, reason, message=None):
        '''
        通知用户比赛由于reason取消了
        '''
        try:
            msg = MsgPack()
            msg.setCmd('m_over')
            msg.setResult('gameId', self._room.gameId)
            msg.setResult('roomId', self._room.bigRoomId)
            msg.setResult('reason', reason)
            msg.setResult('info', message or MatchFinishReason.toString(reason))
            router.sendToUser(msg, signer.userId)
            
            mo = MsgPack()
            mo.setCmd('m_signs')
            mo.setResult('gameId', self._room.gameId)
            mo.setResult('roomId', self._room.bigRoomId)
            mo.setResult('userId', signer.userId)
            mo.setResult('signs', {self._room.bigRoomId:0})
            router.sendToUser(mo, signer.userId)
        except:
            self._logger.error('PlayerNotifierErday.notifyMatchCancelled',
                               'userId=', signer.userId,
                               'instId=', signer.instId,
                               'reason=', reason,
                               'message=', message)
    
    def notifyMatchOver(self, player, reason, rankRewards):
        '''
        通知用户比赛结束了
        '''
        try:
            if (reason == MatchFinishReason.USER_WIN
                or reason == MatchFinishReason.USER_LOSER):
                try:
                    event_remote.publishMatchWinloseEvent(self._room.gameId,
                                                            player.userId, 
                                                            self._room.match.matchId,
                                                            reason == MatchFinishReason.USER_WIN,
                                                            player.rank,
                                                            player.group.startPlayerCount,
                                                            rankRewards.conf if rankRewards else None)
                    from dizhu.entity.matchhistory import MatchHistoryHandler
                    MatchHistoryHandler.onMatchOver(player.userId,
                                                player.group.matchConf.recordId,
                                                player.rank,
                                                reason == MatchFinishReason.USER_WIN,
                                                rankRewards.conf if rankRewards else None,
                                                player.group.isGrouping)
                except:
                    self._logger.error('PlayerNotifierDizhu.notifyMatchOver',
                                       'userId=', player.userId,
                                       'groupId=', player.group.groupId,
                                       'reason=', reason,
                                       'rankRewards=', rankRewards.rewards)


                # 比赛记录保存
                try:
                    event = {'gameId':self._room.gameId,
                            'userId':player.userId,
                            'matchId':self._room.match.matchId,
                            'rank':player.rank,
                            'isGroup': 1 if player.group.isGrouping else 0}
                    MatchRecord.updateAndSaveRecord(event)
                except:
                    self._logger.error('PlayerNotifierDizhu.notifyMatchOver',
                                       'gameId=', self._room.gameId,
                                       'userId=', player.userId,
                                       'reason=', reason,
                                       'matchId=', self._room.match.matchId,
                                       'rank=', player.rank)

            msg = MsgPack()
            msg.setCmd('m_over')
            msg.setResult('gameId', self._room.gameId)
            msg.setResult('roomId', self._room.bigRoomId)
            msg.setResult('userId', player.userId)
            msg.setResult('reason', reason)
            msg.setResult('rank', player.rank)
            if player.beatDownUserName:
                msg.setResult('beatDownUser', player.beatDownUserName) # 击败了谁(昵称)，拼接富文本使用

            if rankRewards and reason == MatchFinishReason.USER_WIN:
                msg.setResult('info', buildWinInfo(self._room, player, rankRewards)) # 前端实现是用来提取其奖励信息，用于显示在奖状上
                if rankRewards.todotask:
                    msg.setResult('todotask', rankRewards.todotask)          
            else:
                msg.setResult('info', buildLoserInfo(self._room, player))
            
            msg.setResult('mucount', player.group.startPlayerCount if player.group.isGrouping else player.group.totalPlayerCount)
            msg.setResult('date', str(datetime.now().date().today())) # //奖状界面日期+时间
            msg.setResult('time', time.strftime('%H:%M', time.localtime(time.time()))) # //奖状界面日期+时间
            # msg.setResult('addInfo', '') # 无用
            rewardDesc = ''
            if rankRewards:
                from dizhu.bigmatch.match import BigMatch
                msg.setResult('reward', BigMatch.buildRewards(rankRewards))
                rewardDesc = BigMatch.buildRewardsDesc(rankRewards)
                if rewardDesc:
                    msg.setResult('rewardDesc', rewardDesc)
            msg.setResult('mname', getMatchName(self._room, player)) # 比赛名称

            record = MatchRecord.loadRecord(self._room.gameId, player.userId, self._room.match.matchId)
            if record:
                msg.setResult('mrecord', {'bestRank':record.bestRank,
                                        #'bestRankDate':record.bestRankDate,
                                        #'isGroup':record.isGroup,
                                        #'crownCount':record.crownCount,
                                        # 'playCount':record.playCount
                                        })
            else:
                msg.setResult('mrecord', {'bestRank':player.rank,
                                         #'bestRankDate':Tool.datetimeToTimestamp(datetime.now()),
                                         #'isGroup':1 if player.group.isGrouping else 0,
                                         #'crownCount':1 if player.rank == 1 else 0,
                                         #'playCount':1
                                         })
            try:
                # 设置奖状分享的todotask diplomaShare
                shareTodoTask = dizhudiplomashare.buildDiplomaShare(player.userName,
                                                               getMatchName(self._room, player), 
                                                               player.rank, 
                                                               rewardDesc, 
                                                               player.userId)
                if shareTodoTask:
                    msg.setResult('shareTodoTask', shareTodoTask)
            except:
                ftlog.exception()
                    
            router.sendToUser(msg, player.userId)
            
            if reason in (MatchFinishReason.USER_NOT_ENOUGH, MatchFinishReason.RESOURCE_NOT_ENOUGH):
                mo = MsgPack()
                mo.setCmd('m_signs')
                mo.setResult('gameId', self._room.gameId)
                mo.setResult('roomId', self._room.bigRoomId)
                mo.setResult('userId', player.userId)
                mo.setResult('signs', {self._room.bigRoomId:0})
                router.sendToUser(mo, player.userId)
            
            #sequence = int(player.group.instId.split('.')[1])
            #self.report_bi_game_event("MATCH_FINISH", player.userId, player.group.matchId, 0, sequence, 0, 0, 0, [], 'match_end')#_stage.matchingId
        except:
            self._logger.error('PlayerNotifierDizhu.notifyMatchOver',
                               'userId=', player.userId,
                               'groupId=', player.group.groupId,
                               'reason=', reason,
                               'rankRewards=', rankRewards.rewards if rankRewards else None)

    def notifyMatchGiveupFailed(self, player, message):
        '''
        通知用户不能放弃比赛
        '''
        try:
            msg = MsgPack()
            msg.setCmd('room')
            msg.setError(-1, message)
            router.sendToUser(msg, player.userId)
        except:
            self._logger.error('PlayerNotifierDizhu.notifyMatchGiveupFailed',
                               'userId=', player.userId,
                               'groupId=', player.group.groupId,
                               'message=', message)
    
    def notifyMatchUpdate(self, player):
        '''
        通知比赛更新
        '''
        from dizhu.erdayimatch.match import ErdayiMatch
        try:
            msg = MsgPack()
            msg.setCmd('m_update')
            msg.setResult('_debug_user_%d_' % (1), player.userId)
            ErdayiMatch.getMatchStates(self._room, player.userId, msg)
            router.sendToUser(msg, player.userId)
        except:
            self._logger.error('PlayerNotifierDizhu.notifyMatchUpdate',
                               'userId=', player.userId,
                               'groupId=', player.group.groupId)
    
    def notifyMatchRank(self, player):
        '''
        通知比赛排行榜
        '''
        from dizhu.erdayimatch.match import ErdayiMatch
        if self._logger.isDebug():
            self._logger.debug('PlayerNotifierDizhu.notifyMatchRank',
                               'userId=', player.userId,
                               'rankList=', [p.userId for p in player.stage.rankList])
        msg = MsgPack()
        msg.setCmd('m_rank')
        ranktops = []
        lastCardResult = player.getLastCardResult()
        ranktops.append({'userId':player.userId,
                         'name':player.userName,
                         'score':ErdayiMatch.fmtScore(player.score),
                         'rank':str(player.rank),
                         'curScore':ErdayiMatch.fmtScore(lastCardResult.mpRatioScore if lastCardResult else 0)})
        for rp in player.stage.rankList:
            lastCardResult = rp.getLastCardResult()
            ranktops.append({'userId':rp.userId,
                             'name':rp.userName,
                             'score':ErdayiMatch.fmtScore(rp.score),
                             'rank':str(rp.rank),
                             'curScore':ErdayiMatch.fmtScore(lastCardResult.mpRatioScore if lastCardResult else 0)})
            msg.setResult('mranks', ranktops)
        router.sendToUser(msg, player.userId)
        
    def notifyMatchWait(self, player, step=None):
        '''
        通知用户等待
        '''
        self.notifyMatchRank(player)
        self.notifyMatchUpdate(player)
        msg = MsgPack()
        msg.setCmd('m_wait')
        msg.setResult('gameId', self._room.gameId)
        msg.setResult('roomId', self._room.bigRoomId)
        msg.setResult('playMode', self._room.roomConf['playMode'])
        msg.setResult('tableId', player.group.area.tableId)
        msg.setResult('mname', self._room.roomConf['name'])
        steps = []
        for i, stageConf in enumerate(player.group.matchConf.stages):
            isCurrent = True if i == player.group.stageIndex else False
            if stageConf.groupingType != GroupingType.TYPE_NO_GROUP:
                des = '每组%s人晋级' % (stageConf.riseUserCount)
            else:
                des = '%s人晋级' % (stageConf.riseUserCount)
            stepInfo = {'des':des}
            if isCurrent:
                stepInfo['isCurrent'] = 1
            stepInfo['name'] = stageConf.name
            steps.append(stepInfo)
        msg.setResult('steps', steps)
        router.sendToUser(msg, player.userId)
    
    def notifyMatchStart(self, instId, signers):
        '''
        通知用户比赛开始
        '''        
        try:
            self._logger.info('PlayerNotifierDizhu.notifyMatchStart',
                              'instId=', instId,
                              'userCount=', len(signers))
            mstart = MsgPack()
            mstart.setCmd('m_start')
            mstart.setResult('gameId', self._room.gameId)
            mstart.setResult('roomId', self._room.bigRoomId)
            
            userIds = [p.userId for p in signers]
            self._logger.info('PlayerNotifierDizhu.notifyMatchStart begin send tcp m_start'
                              'instId=', instId,
                              'userCount=', len(signers))
            if userIds:
                router.sendToUsers(mstart, userIds)
                self._logger.info('PlayerNotifierDizhu.notifyMatchStart end send tcp m_start'
                                  'instId=', instId,
                                  'userCount=', len(signers))
                
                self._logger.info('PlayerNotifierDizhu.notifyMatchStart begin send bi report'
                                  'instId=', instId,
                                  'userCount=', len(signers))
        except:
            self._logger.error('PlayerNotifierDizhu.notifyMatchStart'
                               'instId=', instId,
                               'userCount=', len(signers))
    
    def notifyStageStart(self, player):
        '''
        通知用户正在配桌
        '''
        if player.group.stageIndex == 0:
            if player.waitReason == WaitReason.BYE:
                self.notifyMatchWait(player, 0)
            else:
                mo = MsgPack()
                mo.setCmd('m_play_animation')
                mo.setResult('gameId', self._room.gameId)
                mo.setResult('roomId', self._room.bigRoomId)
                mo.setResult('type', AnimationType.ASSIGN_TABLE)
                router.sendToUser(mo, player.userId)
        else:
            mo = MsgPack()
            mo.setCmd('m_rise')
            mo.setResult('gameId', self._room.gameId)
            mo.setResult('roomId', self._room.bigRoomId)
            router.sendToUser(mo, player.userId)
    
class ErdayiStage(MatchStage):
    def __init__(self, stageConf, group):
        super(ErdayiStage, self).__init__(stageConf, group)
        # value=list<Player>
        self._winlosePlayersList = []
        # 等待开局的玩家
        self._waitPlayerList = []
        # 正在使用的桌子
        self._busyTableSet = set()
        # 空闲的桌子
        self._idleTableList = []
        # 所有桌子
        self._allTableSet = set()
        # 完成所有牌局的玩家
        self._finishCardCountPlayerSet = set()
        
        # 最后一次检查超时桌子的时间
        self._lastCheckTimeoutTableTime = None
        self._hasTimeoutTable = False
        self._processWaitPlayerCount = 0
        # 总排行榜，按照player.si从大到小排序
        self._rankList = []
        # 每副牌的排行榜
        self._cardRankingMap = {}
        # value = [seat1Cards, seat2Cards, seat3Cards, baseCards]
        self._cards = []
        
    @property
    def matchId(self):
        return self.group.matchId
        
    @property
    def roomId(self):
        return self.area.roomId
    
    @property
    def instId(self):
        return self.group.instId
    
    @property
    def playerCount(self):
        return self.group.playerCount
    
    @property
    def isGrouping(self):
        return self.group.isGrouping
    
    @property
    def rankList(self):
        return self._rankList
    
    def calcUncompleteTableCount(self, player):
        busyTableCount = len(self._busyTableSet)
        waitUserCount = len(self._waitPlayerList)
        ret = int(busyTableCount + waitUserCount / self.matchConf.tableSeatCount)
        if self._logger.isDebug():
            self._logger.debug('ErdayiStage.calcUncompleteTableCount',
                               'userId=', player.userId,
                               'busyTableCount=', busyTableCount,
                               'waitUserCount=', waitUserCount,
                               'ret=', ret)
        return ret
     
    def calcTotalRemTimes(self, timestamp):
        # TODO
        return 100
    
    @property
    def isLastStage(self):
        return self.stageIndex + 1 >= len(self.matchConf.stages)
    
    def findCardRanking(self, cardNo):
        return self._cardRankingMap.get(cardNo)
    
    def findOrCreateRanking(self, cardNo):
        cardRanking = self.findCardRanking(cardNo)
        if not cardRanking:
            cardRanking = CardRanking(cardNo)
            self._cardRankingMap[cardNo] = cardRanking
        return cardRanking
    
    def getCards(self, cardNo):
        if self._logger.isDebug():
            self._logger.debug('ErdayiStage.getCards'
                               'cardNo=', cardNo)
        assert(cardNo >= 0 and cardNo <= len(self._cards))
        if cardNo >= len(self._cards):
            cards = [i for i in xrange(54)]
            random.shuffle(cards)
            self._cards.append((cards[0:17], cards[17:34], cards[34:51], cards[51:]))
        return self._cards[cardNo]
        
    def _sortMatchRanks(self):
        self._rankList.sort(cmp=cmpPlayers)
        for i, player in enumerate(self._rankList):
            player.rank = i + 1
        
    def winlose(self, player, deltaScore, isWin, isKill=False):
        assert(player.group == self.group)
        table = player.table
        
        if self.group.state != MatchGroup.ST_START:
            self._logger.error('ErdayiStage.winlose fail',
                               'groupState=', self.group.state,
                               'userId=', player.userId,
                               'tableId=', table.tableId if table else None,
                               'deltaScore=', deltaScore,
                               'isWin=', isWin,
                               'isKill=', isKill,
                               'busyTableCount=', len(self._busyTableSet))
            raise BadStateException()
            
        player._state = Player.ST_WINLOSE
        player.playTime += max(0, time.time() - player.cardStartTime)
        cardRanking = self.findOrCreateRanking(player.cardCount)
        player.finishCard(deltaScore)
        cardRanking.addPlayer(player)
        self._sortMatchRanks()
        assert(player.table)
        
        # reportEviewRound
        if self.stageId3:
            if cardRanking.playerCount >= len(self._rankList):
                cards = self.getCards(cardRanking.cardNo)
                for player in self._rankList:
                    erdayi3api.reportEviewRound(self.roomId,
                                                player,
                                                cardRanking.cardNo,
                                                cards[0],
                                                cards[3]) 
        
        self._logger.info('ErdayiStage.winlose ok',
                          'groupState=', self.group.state,
                          'userId=', player.userId,
                          'tableId=', table.tableId if table else None,
                          'seatId=', player.seat.seatId if player.seat else None,
                          'deltaScore=', deltaScore,
                          'isWin=', isWin,
                          'isKill=', isKill,
                          'cardNo=', cardRanking.cardNo,
                          'finishCount=', cardRanking.playerCount,
                          'rankListCount=', len(self._rankList),
                          'busyTableCount=', len(self._busyTableSet))
        
        if not table:
            # 添加到winlose列表
            self._addWinlosePlayers([player])
            self.area.playerNotifier.notifyMatchWait(player)
        elif table.getPlayingPlayerCount() <= 0:
            playerList = table.getPlayerList()
            # 让该桌子上的用户站起并释放桌子
            self._clearAndReleaseTable(table)
            # 添加到winlose列表
            self._addWinlosePlayers(playerList)
            self.area.playerNotifier.notifyMatchWait(player)
    
    def start(self):
        self._rankList = sorted(self.group._playerMap.values(), cmp=PlayerSort.cmpBySigninTime)
        self._logger.info('ErdayiStage.start ...',
                          'groupState=', self.group.state,
                          'playerCount=', self.playerCount,
                          'idleTableCount=', self.area.tableManager.idleTableCount)
        
        if self.playerCount < self.matchConf.tableSeatCount:
            # 人数不足
            self._logger.info('ErdayiStage.start fail',
                              'groupState=', self.group.state,
                              'userCount=', self.playerCount,
                              'err=', 'NotEnoughUser')
            return False, MatchFinishReason.USER_NOT_ENOUGH
        
        needTableCount = self.calcNeedTableCount()
        if self.area.tableManager.idleTableCount < needTableCount:
            # 桌子资源不足
            self._logger.error('ErdayiStage.start fail',
                               'groupState=', self.group.state,
                               'playerCount=', self.playerCount,
                               'idleTableCount=', self.area.tableManager.idleTableCount,
                               'err=', 'NotEnoughTable')
            return False, MatchFinishReason.RESOURCE_NOT_ENOUGH
        
        timestamp = pktimestamp.getCurrentTimestamp()
        
        try:
            erdayi3api.reportSignin(self.roomId, self)
        except:
            self._logger.error('ErdayiStage.start reportSignin')
        
        # 借桌子
        self._idleTableList = self.area.tableManager.borrowTables(needTableCount)
        self._allTableSet = set(self._idleTableList)

        # 初始化用户数据
        if self.stageIndex == 0:
            self._sortMatchRanks()
        self._initPlayerDatas()
        self._initWaitPlayerList()
        
        self._lastCheckTimeoutTableTime = timestamp + self.matchConf.start.tableTimes
        
        for player in self._waitPlayerList:
            self.area.playerNotifier.notifyStageStart(player)
        
        nwait = len(self.group.playerMap) % self.matchConf.tableSeatCount
        if nwait < self.matchConf.tableSeatCount:
            for i in range(-1, -1 - nwait, -1):
                player = self._waitPlayerList[i]
                self._processWaitPlayerCount += 1
                self.area.matchUserIF.lockUser(self.matchId, self.roomId, self.instId, player.userId, player.clientId)
                self.area.playerNotifier.notifyMatchWait(player)
                self._logger.info('ErdayiStage.start bye',
                                  'groupState=', self.group.state,
                                  'playerCount=', self.playerCount,
                                  'userId=', player.userId,
                                  'index=', i)
        
        self._logger.info('ErdayiStage.start ok',
                          'groupState=', self.group.state,
                          'playerCount=', self.playerCount,
                          'idleTableCount=', self.area.tableManager.idleTableCount)
        return True, None
    
    def kill(self, reason):
        self.finish(reason)
    
    def finish(self, reason):
        self._finishReason = reason
        
        self._logger.info('ErdayiStage.finish ...',
                          'groupState=', self.group.state,
                          'busyTableCount=', len(self._busyTableSet),
                          'winlosePlayersCount=', len(self._winlosePlayersList),
                          'reason=', reason)
        
        riseUserCount = 0
        if reason == MatchFinishReason.FINISH:
            riseUserCount = min(self.stageConf.riseUserCount, len(self._rankList))
            if len(self._busyTableSet) > 0:
                self._logger.error('ErdayiStage.finish issue',
                                   'groupState=', self.group.state,
                                   'busyTableCount=', len(self._busyTableSet),
                                   'winlosePlayersCount=', len(self._winlosePlayersList),
                                   'reason=', reason,
                                   'err=', 'HaveBusyTable')
            
            if len(self._winlosePlayersList) != 0:
                self._logger.error('ErdayiStage.finish issue',
                                   'groupState=', self.group.state,
                                   'busyTableCount=', len(self._busyTableSet),
                                   'winlosePlayersCount=', len(self._winlosePlayersList),
                                   'reason=', reason,
                                   'err=', 'HaveWinlosePlayer')
            # reportRoundRank
            if self.stageId3:
                erdayi3api.reportRoundRank(self.roomId, self, self._rankList, riseUserCount)
            
            while len(self._rankList) > riseUserCount:
                self._outPlayer(self._rankList[-1], MatchFinishReason.USER_LOSER)

            if self.stageIndex + 1 >= len(self.matchConf.stages):
                # 最后一个阶段, 给晋级的人发奖
                while self._rankList:
                    self._outPlayer(self._rankList[-1], MatchFinishReason.USER_WIN)
        else:
            # 释放所有桌子
            for table in self._busyTableSet:
                self._clearTable(table)
            self._busyTableSet.clear()
            
            while self._rankList:
                self._outPlayer(self._rankList[-1], reason)
        
        self._releaseResource()
        
        self._logger.info('ErdayiStage._doFinish ok',
                          'groupState=', self.group.state,
                          'reason=', reason)
    
    def isStageFinished(self):
        return len(self._finishCardCountPlayerSet) >= len(self._rankList)
    
    def processStage(self):
        if self._logger.isDebug():
            self._logger.debug('ErdayiStage.processStage',
                               'groupState=', self.group.state)
            
        self._lastActiveTime = pktimestamp.getCurrentTimestamp()
        
        self._processTimeoutTables()
        self._processWinlosePlayers()
        self._processWaitPlayers()
        self._reclaimTables()
        
        if len(self._waitPlayerList) >= self.matchConf.tableSeatCount:
            return 0.08
        return 1
    
    def calcNeedTableCount(self):
        return (self.playerCount + self.matchConf.tableSeatCount - 1) / self.matchConf.tableSeatCount
    
    def _outPlayer(self, player, reason=MatchFinishReason.USER_LOSER):
        if self._logger.isDebug():
            self._logger.debug('ErdayiStage._outPlayer',
                               'userId=', player.userId,
                               'reason=', reason)
        player._state = Player.ST_OVER
        assert(player.seat is None)

        # 删除player
        self.group.removePlayer(player)
        self._rankList.remove(player)
        # 删除已完成cardCount的用户
        self._finishCardCountPlayerSet.discard(player)
        # 玩家完成比赛
        self._doPlayerMatchOver(player, reason)
        
    def _doPlayerMatchOver(self, player, reason):
        # 解锁玩家
        rankRewards = None
        
        if (reason == MatchFinishReason.USER_WIN
            or reason == MatchFinishReason.USER_LOSER):
            rankRewards = self._getRewards(player)
            if rankRewards:
                self.area.matchRewards.sendRewards(player, rankRewards)
                if reason == MatchFinishReason.USER_LOSER:
                    reason = MatchFinishReason.USER_WIN
        
        self._logger.info('UserMatchOver',
                          'matchId=', self.matchId,
                          'instId=', self.instId,
                          'stageIndex=', self.stageIndex,
                          'userId=', player.userId,
                          'score=', player.score,
                          'rank=', player.rank,
                          'reason=', reason,
                          'remUserCount=', len(self._rankList),
                          'cardCount=', player.cardCount,
                          'stageCardCount=', self.stageConf.cardCount,
                          'rankRewards=', rankRewards.rewards if rankRewards else None)
        
        self.area.playerNotifier.notifyMatchOver(player, reason, rankRewards)
        self.area.matchUserIF.unlockUser(self.matchId, self.roomId, self.instId, player.userId)
        
    def _getRewards(self, player):
        # 看当前阶段是否有配置奖励
        rankRewardsList = self.stageConf.rankRewardsList if self.isGrouping else self.matchConf.rankRewardsList
        if self._logger.isDebug():
            self._logger.debug('ErdayiStage._getRewards',
                               'userId=', player.userId,
                               'rank=', player.rank,
                               'rankRewardsList=', rankRewardsList,
                               'stageConf.rankRewards=', self.stageConf.rankRewardsList)
        if rankRewardsList:
            for rankRewards in rankRewardsList:
                if ((rankRewards.startRank == -1 or player.rank >= rankRewards.startRank)
                    and (rankRewards.endRank == -1 or player.rank <= rankRewards.endRank)):
                    return rankRewards
        return None
    
    def _initWaitPlayerList(self):
        # 排序
        if self._logger.isDebug():
            self._logger.debug('ErdayiStage._initWaitPlayerList',
                               'groupState=', self.group.state,
                               'userIds=', [p.userId for p in self._rankList])
        self._waitPlayerList = []
        
        waitPlayers = PlayerQueuing.sort(self.stageConf.seatQueuing, self._rankList)
        byeCount = len(waitPlayers) % self.matchConf.tableSeatCount
        
        for player in waitPlayers:
            self._addWaitPlayer(player)
        
        for i in xrange(byeCount):
            self._waitPlayerList[-1 - i].waitReason = WaitReason.BYE
            
    def _initPlayerDatas(self):
        for i, player in enumerate(self._rankList):
            player.waitTimes = 0
            player.score = 0
            player.rank = i + 1
            player.playTime = player.cardStartTime = 0
            player._cardResults = []
            if self._logger.isDebug():
                self._logger.debug('ErdayiStage._initPlayerDatas',
                                   'state=', self.group.state,
                                   'userId=', player.userId,
                                   'score=', player.score)
                
    def _addWinlosePlayers(self, playerList):
        self._winlosePlayersList.append(playerList)
        
    def _addWaitPlayer(self, player):
        player._state = Player.ST_WAIT
        player.waitReason = WaitReason.WAIT
        self._waitPlayerList.append(player)
        
    def _playerFinishCardCount(self, player):
        player._state = Player.ST_WAIT
        player.waitReason = WaitReason.RISE
        self._finishCardCountPlayerSet.add(player)
        self._logger.info('ErdayiStage._playerFinishCardCount',
                          'userId=', player.userId,
                          'cardCount=', player.cardCount,
                          'totalFinishUserCount=', len(self._finishCardCountPlayerSet))
        
    def _borrowTable(self):
        # 借用桌子
        assert(len(self._idleTableList) > 0)
        table = self._idleTableList.pop(0)
        self._busyTableSet.add(table)
        self._logger.info('ErdayiStage._borrowTable',
                          'tableId=', table.tableId,
                          'idleTableCount=', len(self._idleTableList))
        return table
    
    def _releaseTable(self, table):
        # 释放桌子
        assert(table.idleSeatCount == table.seatCount)
        self._logger.info('ErdayiStage._releaseTable',
                          'tableId=', table.tableId)
        table._group = None
        table.playTime = None
        self._busyTableSet.remove(table)
        self._idleTableList.append(table)
        
    def _clearTable(self, table):
        if self._logger.isDebug():
            self._logger.debug('ErdayiStage._clearTable',
                               'tableId=', table.tableId)
        players = []
        self.area.tableController.clearTable(table)
        for seat in table.seats:
            if seat.player:
                players.append(seat.player)
                if self._logger.isDebug():
                    self._logger.debug('ErdayiStage._clearTable standup',
                                       'tableId=', table.tableId,
                                       'seatId=', seat.seatId,
                                       'userId=', seat.player.userId)
                table.standup(seat.player)

        for player in players:
            try:
                self.area.matchUserIF.lockUser(self.matchId, self.roomId, self.instId, player.userId, player.clientId)
            except:
                self._logger.error('ErdayiStage._clearTable lockUserFail',
                                   'tableId=', table.tableId,
                                   'userId=', player.userId)
                
    def _clearAndReleaseTable(self, table):
        if self._logger.isDebug():
            self._logger.debug('ErdayiStage._clearAndReleaseTable',
                               'tableId=', table.tableId)
        players = []
        self.area.tableController.clearTable(table)
        for seat in table.seats:
            if seat.player:
                players.append(seat.player)
                if self._logger.isDebug():
                    self._logger.debug('ErdayiStage._clearAndReleaseTable standup',
                                       'tableId=', table.tableId,
                                       'seatId=', seat.seatId,
                                       'userId=', seat.player.userId)
                table.standup(seat.player)
                
        self._logger.info('ErdayiStage._clearAndReleaseTable',
                          'tableId=', table.tableId)
        table._group = None
        table.playTime = None
        self._busyTableSet.remove(table)
        self._idleTableList.append(table)
        
        for player in players:
            try:
                self.area.matchUserIF.lockUser(self.matchId, self.roomId, self.instId, player.userId, player.clientId)
            except:
                self._logger.error('ErdayiStage._clearAndReleaseTable lockUserFail',
                                   'tableId=', table.tableId,
                                   'userId=', player.userId)
    
    def _releaseResource(self):
        self._finishCardCountPlayerSet.clear()
        self._winlosePlayerList = []
        for table in self._busyTableSet:
            self._clearTable(table)
        self._busyTableSet.clear()
        self._idleTableList = []
        self.area.tableManager.returnTables(self._allTableSet)
        self._allTableSet.clear()
        
    def _reclaimTables(self):
        needCount = self.calcNeedTableCount()
        reclaimCount = len(self._allTableSet) - needCount
        if self._logger.isDebug():
            self._logger.debug('ErdayiStage._reclaimTables',
                               'needCount=', needCount,
                               'reclaimCount=', reclaimCount,
                               'allCount=', len(self._allTableSet),
                               'tableManager.idleCount=', self.area.tableManager.idleTableCount)
            
        if reclaimCount > 0:
            count = min(reclaimCount, len(self._idleTableList))
            tables = self._idleTableList[0:count]
            self._idleTableList = self._idleTableList[count:]
            self.area.tableManager.returnTables(tables)
            for table in tables:
                self._allTableSet.remove(table)
            self._logger.info('ErdayiStage._reclaimTables',
                              'needCount=', needCount,
                              'reclaimCount=', reclaimCount,
                              'realReclaimCount=', count,
                              'allCount=', len(self._allTableSet),
                              'tableManager.idleCount=', self.area.tableManager.idleTableCount)
            
    def _calcMaxProcessPlayerCount(self):
        count = 200
        try:
            maxPlayerPerRoom = self.area.tableManager.getTableCountPerRoom() * self.matchConf.tableSeatCount
            countPerRoom = int((maxPlayerPerRoom / self.matchConf.start.startMatchSpeed + 10) / 10)
            count = min(200, self.area.tableManager.roomCount * countPerRoom)
            if self._logger.isDebug():
                self._logger.debug('ErdayiStage._calcMaxProcessPlayerCount',
                                   'maxPlayerPerRoom=', maxPlayerPerRoom,
                                   'startMatchSpeed=', self.matchConf.start.startMatchSpeed,
                                   'countPerRoom=', countPerRoom,
                                   'count=', count)
        except:
            self._logger.error('ErdayiStage._calcMaxProcessPlayerCount')
        return count
    
    def _processTimeoutTables(self):
        if self._logger.isDebug():
            self._logger.debug('ErdayiStage._processTimeoutTables',
                               'groupState=', self.group.state,
                               'busyTableCount=', len(self._busyTableSet),
                               'hasTimeoutTable=', self._hasTimeoutTable,
                               'lastCheckTimeoutTableTime=', self._lastCheckTimeoutTableTime)
        timestamp = pktimestamp.getCurrentTimestamp()
        # 每tableTimeoutCheckInterval秒检查一次
        if (self._hasTimeoutTable
            or (timestamp - self._lastCheckTimeoutTableTime >= self.stageConf.tableTimeoutCheckInterval)):
            self._lastCheckTimeoutTableTime = timestamp
            overtimeTables = []
            for table in self._busyTableSet:
                if timestamp - table.playTime >= self.matchConf.start.tableTimes:
                    overtimeTables.append(table)
            processCount = min(len(overtimeTables), 10)
            for table in overtimeTables:
                processCount -= 1
                if not table.playTime:
                    self._logger.warn('ErdayiStage._processTimeoutTables notPlayTime',
                                      'groupState=', self.group.state,
                                      'tableId=', table.tableId,
                                      'timestamp=', timestamp)
                else:
                    self._logger.info('ErdayiStage._processTimeoutTables tableTimeout',
                                      'groupState=', self.group.state,
                                      'tableId=', table.tableId,
                                      'playTimes=', (timestamp - table.playTime))
                    if timestamp - table.playTime >= self.matchConf.start.tableTimes:
                        playerList = table.getPlayingPlayerList()
                        for player in playerList:
                            self.winlose(player, 0, True, True)
                if processCount <= 0:
                    break
            self._hasTimeoutTable = processCount < len(overtimeTables)
    
    def _processWinlosePlayers(self):
        if self._logger.isDebug():
            self._logger.debug('ErdayiStage._processWinlosePlayers',
                               'groupState=', self.group.state,
                               'winlosePlayersCount=', len(self._winlosePlayersList))

        # 等待所有人完成
        if self._winlosePlayersList and len(self._winlosePlayersList) >= len(self._rankList):
            winlosePlayersList = self._winlosePlayersList
            self._winlosePlayersList = []
    
            for players in winlosePlayersList:
                self._logger.info('ErdayiStage._processWinlosePlayers',
                                  'groupState=', self.group.state,
                                  'userIds=', [p.userId for p in players])
                for player in players:
                    # 如果打的牌数达到最大定义的牌数，等待阶段结束排名
                    if player.cardCount < self.stageConf.cardCount:
                        # 否则放入等待队列，等待再次开始
                        self._addWaitPlayer(player)
                        self.area.playerNotifier.notifyMatchWait(player)
                    else:
                        self._playerFinishCardCount(player)
                        self.area.playerNotifier.notifyMatchWait(player)
    
    def _processWaitPlayers(self):
        if self._logger.isDebug():
            self._logger.debug('ErdayiStage._processWaitPlayers',
                               'groupState=', self.group.state,
                               'processWaitPlayerCount=', self._processWaitPlayerCount,
                               'startPlayerCount=', self.group.startPlayerCount,
                               'waitUserIds=', [p.userId for p in self._waitPlayerList])
        
        isAllProcess = self._processWaitPlayerCount >= self.group.startPlayerCount
        
        # 检查剩余的玩家能不能凑够一桌
        waitCount = len(self._waitPlayerList)
        if waitCount < self.matchConf.tableSeatCount:
            if (waitCount > 0
                and (len(self._finishCardCountPlayerSet) + waitCount) >= len(self._rankList)):
                # 凑不够一桌，直接结算轮空的用户完成
                self._logger.info('ErdayiStage._processWaitPlayers',
                                  'groupState=', self.group.state,
                                  'playerCount=', self.playerCount,
                                  'waitUserIds=', [p.userId for p in self._waitPlayerList],
                                  'err=', 'UserNotEnough')
                waitPlayerList = self._waitPlayerList
                self._waitPlayerList = []
                for player in waitPlayerList:
                    player.cardCount += 1
                    self.winlose(player, 0, True, True)
            return
        
        # 计算本次处理多少玩家
        processCount = max(self._calcMaxProcessPlayerCount(), self.matchConf.tableSeatCount)
        processCount =  min(processCount - processCount % self.matchConf.tableSeatCount, len(self._waitPlayerList))
        processPlayerList = self._waitPlayerList[0:processCount]
        self._waitPlayerList = self._waitPlayerList[processCount:]
        processedCount = 0
        if self._logger.isDebug():
            self._logger.debug('ErdayiStage._processWaitPlayers',
                               'groupState=', self.group.state,
                               'playerCount=', self.playerCount,
                               'processCount=', processCount)
        while (processedCount < processCount):
            players = processPlayerList[processedCount:processedCount + self.matchConf.tableSeatCount]
            processedCount += self.matchConf.tableSeatCount
            self._startTable(players)
            self._processWaitPlayerCount += self.matchConf.tableSeatCount
        
        if not isAllProcess and self._processWaitPlayerCount >= self.group.startPlayerCount:
            self._logger.info('ErdayiStage._processWaitPlayers',
                              'groupState=', self.group.state,
                              'processWaitPlayerCount=', self._processWaitPlayerCount,
                              'startPlayerCount=', self.group.startPlayerCount,
                              'isAllProcessFinish=', True)
            
    def _startTable(self, players):
        # 分配桌子
        table = self._borrowTable()
        assert(table is not None)
        table._group = self.group
        table.playTime = pktimestamp.getCurrentTimestamp()
        table.ccrc += 1
        table.cards = self.getCards(players[0].cardCount)
        for i in xrange(self.matchConf.tableSeatCount):
            player = players[i]
            if player.state != Player.ST_WAIT:
                self._logger.error('ErdayiStage._processWaitPlayers',
                                   'groupState=', self.group.state,
                                   'userId=', player.userId,
                                   'playerState=', player.state,
                                   'err=', 'BadUserState')
                assert(player.state == Player.ST_WAIT)
                
            player._state = Player.ST_PLAYING
            player.cardStartTime = time.time()
            player.waitReason = WaitReason.UNKNOWN
            if player.seat:
                self._logger.error('ErdayiStage._startTable',
                                   'groupState=', self.group.state,
                                   'userId=', player.userId,
                                   'seatLoc=', player.seat.location,
                                    'err=', 'SeatNotEmpty')
                assert(player.seat is None)
            table.sitdown(player)
            assert(player.seat)
            
            if self._logger.isDebug():
                self._logger.debug('ErdayiStage._startTable',
                                   'groupState=', self.group.state,
                                   'userId=', player.userId,
                                   'sitdown=', player.seat.location)
                    
            self.area.tableController.startTable(table)
            self._logger.info('ErdayiStage._startTable',
                              'groupState=', self.group.state,
                              'tableId=', table.tableId,
                              'userIds=', table.getUserIdList(),
                              'processWaitPlayerCount=', self._processWaitPlayerCount,
                              'startPlayerCount=', self.group.startPlayerCount)
                    
class ErdayiMatchFactory(MatchFactory):
    def newStage(self, stageConf, group):
        '''
        创建阶段
        '''
        return ErdayiStage(stageConf, group)
    
    def newSigner(self, userId, instId):
        return Signer(userId, instId)
    
    def newPlayer(self, signer):
        '''
        创建一个Player
        '''
        player = ErdayiPlayer(signer.userId)
        player.instId = signer.instId
        player.userName = signer.userName
        player.fee = signer.fee
        player.signinTime = signer.signinTime
        player.clientId = signer.clientId
        player.realInfo = signer.realInfo
        return player


