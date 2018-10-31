# -*- coding:utf-8 -*-
'''
Created on 2016年1月20日

@author: zhaojiangang
'''
import copy

from datetime import datetime
import json
import time

from dizhu.entity import dizhudiplomashare, dizhuhallinfo, dizhushare
from dizhu.entity.dizhuconf import DIZHU_GAMEID
from dizhu.entity.matchrecord import MatchRecord
from dizhu.entity.led_util import LedUtil
from dizhu.entity import dizhuled
from dizhu.games import matchutil, match_signin_discount
from dizhu.games.matchutil import MatchLottery
from dizhu.servers.util.rpc import match_remote
from dizhucomm.core.events import UserMatchOverEvent
from dizhucomm.entity import commconf
from freetime.core.tasklet import FTTasklet
from freetime.core.timer import FTTimer
from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from hall.entity import datachangenotify
from hall.servers.util.rpc import user_remote, event_remote
import poker.entity.biz.message.message as pkmessage
from poker.entity.biz import bireport
from poker.entity.configure import gdata
from poker.entity.dao import daobase, sessiondata, userdata, daoconst, userchip
from poker.entity.game.rooms.arena_match_ctrl.match import MatchRankRewards
from poker.entity.game.rooms.group_match_ctrl.const import StageType, \
    AnimationType, MatchFinishReason, WaitReason, GroupingType
from poker.entity.game.rooms.group_match_ctrl.exceptions import AlreadyInMatchException, AlreadySigninException, \
    SigninFeeNotEnoughException, SigninException, PopWndNotException
from poker.entity.game.rooms.group_match_ctrl.interface import SignIF, \
    MatchStatusDao, MatchStatus, MatchRewards, TableController, PlayerNotifier, \
    UserInfoLoader, MatchRankRewardsSelector
from poker.entity.game.rooms.group_match_ctrl.models import Signer
from poker.entity.game.rooms.group_match_ctrl.utils import Logger
from poker.protocol import router
from poker.util import strutil
import poker.util.timestamp as pktimestamp
from poker.entity.events import hall51event


def getMatchGroupStepInfos(group, table):
    infoscores = []
    inforanks = []
    cardCount = 0
    for seat in table.seats:
        if seat.player:
            infoscores.append(seat.player.score)
            inforanks.append(seat.player.rank)
            cardCount += seat.player.cardCount
        else:
            infoscores.append(0)
            inforanks.append(0)
    cardCount = cardCount / len(table.seats)
    step = u'当前第%d阶段,第%d副' % (group.stageIndex + 1, cardCount)
    assLoseScore = group.loseBetScore
    if group.stageConf.type == StageType.ASS :  # ASS 赛制
        mtype = u'ASS打立出局'
        upcount = group.stageConf.riseUserCount
        outScore = group.assLoseScore
        bscore = u'底分:%d,低于%d将被淘汰' % (group.loseBetScore, outScore)
        outline = ['淘汰分:', str(outScore)]
        incrnote = u'底分增加到%d低于%d将被淘汰' % (group.loseBetScore, outScore)
        assLoseScore = outScore
    else:  # 
        mtype = u'定局淘汰'
        upcount = group.stageConf.riseUserCount
        bscore = u'底分:%d,%d人晋级' % (group.loseBetScore, upcount)
        outline = ['局数:', str(cardCount) + '/' + str(group.stageConf.cardCount)]
        incrnote = u'底分增加到%d' % (group.loseBetScore)

    isStartStep = (cardCount == 1 and group.stageIndex == 0)
    isFinalStep = (cardCount == 1 and (group.stageIndex + 1 >= len(group.matchConf.stages)))

    mInfos = {'scores' : infoscores,  # 座位排序
              'rank' : inforanks,  # 名次
              'all' : len(group.rankList),  # 总人数
              'info' : [outline,
                        [ "晋级人数:", str(upcount)]
                        ],
              'basescore' : group.loseBetScore,
              'asslosechip' : assLoseScore,
              }
    return mtype, step, bscore, isStartStep, isFinalStep, incrnote, mInfos

def buildTableClearMessage(table):
    msg = MsgPack()
    msg.setCmd('table_manage')
    msg.setParam('action', 'm_table_clear')
    msg.setParam('gameId', table.gameId)
    msg.setParam('matchId', table.group.matchId)
    msg.setParam('roomId', table.roomId)
    msg.setParam('tableId', table.tableId)
    msg.setParam('ccrc', table.ccrc)
    return msg

def _buildTableInfoMessage(table, msg):
    msg.setParam('gameId', table.gameId)
    msg.setParam('matchId', table.group.area.matchId)
    msg.setParam('matchingId', table.group.matchingId)
    msg.setParam('roomId', table.roomId)
    msg.setParam('tableId', table.tableId)
    msg.setParam('ccrc', table.ccrc)
    msg.setParam('stageType', table.group.stageConf.type)
    msg.setParam('recordId', table.group.matchConf.recordId)
    if table.group:
        startTimeStr = datetime.fromtimestamp(table.group.startTime).strftime('%Y-%m-%d %H:%M')
        mtype, step, bscore, isStartStep, isFinalStep, incrnote, mInfos = getMatchGroupStepInfos(table.group, table)
        notes = {'basescore' : bscore, 'type' : mtype, 'step': step,
                 'isStartStep' : isStartStep, 'isFinalStep': isFinalStep,
                 'startTime': startTimeStr, 'incrnote':incrnote}
        
        msg.setParam('mnotes', notes)
        msg.setParam('mInfos', mInfos)
        msg.setParam('ranks', table.group._ranktops)
        
        seats = []
        totalCardCount = 0
        for seat in table.seats:
            if seat.player:
                totalCardCount += max(0, seat.player.cardCount - 1)

                hasEnterRewards = False
                try:
                    roomConf = gdata.getRoomConfigure(table.roomId)
                    if ftlog.is_debug():
                        ftlog.debug('startTable userId=', seat.player.userId,
                                    'stageIndex=', table.group.stageIndex,
                                    'hasRewardIndex=', roomConf.get('hasRewardIndex'),
                                    'cardCount=', seat.player.cardCount)
                    if seat.player.cardCount == 1 and not seat.player.isQuit and table.group.stageIndex == roomConf.get('hasRewardIndex'):
                        hasEnterRewards = True
                except Exception, e:
                    ftlog.error('hasEnterRewards err=',
                                'matchId=', table.group.area.matchId,
                                'roomId=', table.roomId,
                                'err=', e.message)

                seats.append({
                        'userId':seat.player.userId,
                        'cardCount':seat.player.cardCount,
                        'rank':seat.player.rank,
                        'chiprank':seat.player.scoreRank,
                        'userName':seat.player.userName,
                        'score':seat.player.score,
                        'isQuit':seat.player.isQuit,
                        'winloseForTuoguanCount': seat.player.winloseForTuoguanCount,
                        'championLimitFlag':seat.player.championLimitFlag,
                        'firstCallFalg': seat.player.firstCallFalg,
                        'hasEnterRewards': hasEnterRewards,
                        'stageRewardTotal': seat.player.stageRewardTotal
                    })
            else:
                seats.append({
                        'userId':0,
                        'cardCount':0,
                        'rank':0,
                        'chiprank':0,
                        'userName':'',
                        'score':0,
                        'isQuit':0,
                        'championLimitFlag':False,
                        'firstCallFalg': 0,
                        'hasEnterRewards': False
                    })
                
        animationType = table.group.stageConf.animationType \
            if totalCardCount == 0 else AnimationType.UNKNOWN
        msg.setParam('seats', seats)
        msg.setParam('step', {
                        'name':table.group.groupName if table.group.isGrouping else table.group.stageConf.name,
                        'type':table.group.stageConf.type,
                        'playerCount':table.group.startPlayerCount,
                        'riseCount':min(table.group.stageConf.riseUserCount, table.group.startPlayerCount),
                        'cardCount':table.group.stageConf.cardCount,
                        'callType': table.group.stageConf.conf.get('call.type', 'random'),
                        'animationType':animationType,
                        'stageIndex':table.group.stageIndex,
                        # 3.77版本的要求VS之外的动画每次都播放，加入原始动画信息
                        'rawAnimationType': {'type':table.group.stageConf.animationType,
                                             'totalCardCount':totalCardCount}
                    })
    return msg

def buildTableInfoMessage(table):
    msg = MsgPack()
    msg.setCmd('table_manage')
    msg.setParam('action', 'm_table_info')
    return _buildTableInfoMessage(table, msg)

def buildTableStartMessage(table):
    msg = MsgPack()
    msg.setCmd('table_manage')
    msg.setParam('action', 'm_table_start')
    return _buildTableInfoMessage(table, msg)

class SignIFDizhu(SignIF):
    def __init__(self, room, tableId, seatId):
        self._room = room
        self._tableId = tableId
        self._seatId = seatId
        self._logger = Logger()
        self._logger.add('roomId', room.roomId)
        
    def signin(self, userId, matchId, ctrlRoomId, instId, fee):
        '''
        报名接口，如果不成功抛异常
        '''
        # 去UT收取报名费，并记录用户所在房间为ctrlRoomId
        # 记录用户报名记录
        contentItem = {'itemId':fee.assetKindId, 'count':fee.count} if fee else None
        ec, result = match_remote.signinMatch(DIZHU_GAMEID, userId, contentItem,
                                              self._room.bigRoomId, instId, self._room.roomId)
        if ec == 0:
            try:
                daobase.executeTableCmd(ctrlRoomId, 0, 'sadd', 'signs:' + str(ctrlRoomId), userId)
                key = 'msignin3:%s:%s:%s' % (self._room.gameId, instId, ctrlRoomId)
                daobase.executeMixCmd('zadd', key, pktimestamp.getCurrentTimestamp(), userId)
            except:
                self._logger.error()
            self._logger.info('SignIFDizhu.signin ok',
                              'userId=', userId,
                              'instId=', instId,
                              'fee=', contentItem)
            return
        if ec == match_remote.ERR_ALREADY_IN_MATCH:
            self._logger.warn('SignIFDizhu.signin fail',
                              'userId=', userId,
                              'instId=', instId,
                              'fee=', contentItem,
                              'err=', 'ERR_ALREADY_IN_MATCH')
            raise AlreadyInMatchException()
        elif ec == match_remote.ERR_ALREADY_SIGNIN:
            self._logger.warn('SignIFDizhu.signin fail',
                              'userId=', userId,
                              'instId=', instId,
                              'fee=', contentItem,
                              'err=', 'ERR_ALREADY_SIGNIN')
            raise AlreadySigninException()
        elif ec == match_remote.ERR_FEE_NOT_ENOUGH:
            self._logger.warn('SignIFDizhu.signin fail',
                              'userId=', userId,
                              'instId=', instId,
                              'fee=', contentItem,
                              'result=', result,
                              'err=', 'ERR_FEE_NOT_ENOUGH')
            raise SigninFeeNotEnoughException(fee)
        elif ec == match_remote.ERR_POPWND:
            self._logger.info('SignIFDizhu.signin fail',
                              'userId=', userId,
                              'instId=', instId,
                              'fee=', contentItem,
                              'result=', result,
                              'err=', 'ERR_POPWND')
            # 返回商城弹窗后不报错
            raise PopWndNotException()
        self._logger.warn('SignIFDizhu.signin fail',
                          'userId=', userId,
                          'instId=', instId,
                          'fee=', contentItem,
                          'err=', 'Unknown')
        raise SigninException('报名失败')
    
    def moveTo(self, userId, matchId, ctrlRoomId, instId, toInstId):
        '''
        移动玩家到下一场比赛
        '''
        try:
            if match_remote.moveTo(DIZHU_GAMEID, userId, self._room.bigRoomId, instId, ctrlRoomId, toInstId):
                daobase.executeTableCmd(ctrlRoomId, 0, 'sadd', 'signs:' + str(ctrlRoomId), userId)
                key = 'msignin3:%s:%s:%s' % (self._room.gameId, toInstId, ctrlRoomId)
                daobase.executeMixCmd('zadd', key, pktimestamp.getCurrentTimestamp(), userId)
        except:
            self._logger.error()
            
    def signout(self, userId, matchId, ctrlRoomId, instId, feeContentItem):
        '''
        '''
        # 去UT退报名费，并删除用户报名记录
        # 删除用户报名记录
        contentItem = {'itemId':feeContentItem.assetKindId, 'count':feeContentItem.count} if feeContentItem else None
        try:
            key = 'msignin3:%s:%s:%s' % (self._room.gameId, instId, ctrlRoomId)
            daobase.executeMixCmd('zrem', key, userId)
            daobase.executeTableCmd(self._room.roomId, 0, 'SREM', 'signs:' + str(self._room.roomId), userId)
        except:
            self._logger.error('SignIFDizhu.signout error',
                               'userId=', userId,
                               'matchId=', matchId,
                               'ctrlRoomId=', ctrlRoomId,
                               'instId=', instId,
                               'fee=', contentItem)
        try:
            match_remote.signoutMatch(DIZHU_GAMEID, userId, contentItem,
                                      self._room.bigRoomId, instId, self._room.roomId)
            self._logger.info('SignIFDizhu.signout ok',
                              'userId=', userId,
                              'matchId=', matchId,
                              'ctrlRoomId=', ctrlRoomId,
                              'instId=', instId,
                              'fee=', contentItem)
        except:
            self._logger.error('SignIFDizhu.signout fail',
                               'userId=', userId,
                               'matchId=', matchId,
                               'ctrlRoomId=', ctrlRoomId,
                               'instId=', instId,
                               'fee=', contentItem)
    
    def _loadSigninFee(self, matchId, ctrlRoomId, instId, userId):
        try:
            info = match_remote.loadUserMatchInfo(self._room.gameId, userId, self._room.bigRoomId)
            if info:
                return info.feeItem
        except:
            self._logger.error('SignIFDizhu._loadSigninFee fail',
                               'userId=', userId,
                               'matchId=', matchId,
                               'ctrlRoomId=', ctrlRoomId,
                               'instId=', instId)
        return None
    
    def loadAllUsers(self, matchId, ctrlRoomId, instId):
        '''
        '''
        # 加载所有用户报名记录
        ret = []
        key = 'msignin3:%s:%s:%s' % (self._room.gameId, instId, ctrlRoomId)
        datas = daobase.executeMixCmd('zrange', key, 0, -1, 'WITHSCORES')
        if datas:
            i = 0
            while (i + 1 < len(datas)):
                userId = int(datas[i])
                signinTime = int(datas[i+1])
                signer = Signer(userId, instId, signinTime)
                signer.feeItem = self._loadSigninFee(matchId, ctrlRoomId, instId, userId)
                ret.append(signer)
                i += 2
        return ret
    
    def removeAllUsers(self, matchId, ctrlRoomId, instId):
        key = 'msignin3:%s:%s:%s' % (self._room.gameId, instId, ctrlRoomId)
        daobase.executeMixCmd('del', key)
        daobase.executeTableCmd(self._room.roomId, 0, 'del', 'signs:' + str(ctrlRoomId))
        
    def lockUser(self, matchId, ctrlRoomId, instId, userId, clientId=None):
        '''
        '''
        try:
            if match_remote.lockUserForMatch(DIZHU_GAMEID, userId, self._room.bigRoomId, instId,
                                             self._room.roomId, self._tableId, self._seatId, clientId):
                return True
            return False
        except:
            self._logger.error('SignIFDizhu.lockUser fail',
                               'userId=', userId,
                               'matchId=', matchId,
                               'ctrlRoomId=', ctrlRoomId,
                               'instId=', instId)
            return False
    
    def unlockUser(self, matchId, ctrlRoomId, instId, userId, feeContentItem):
        '''
        '''
        contentItem = {'itemId':feeContentItem.assetKindId, 'count':feeContentItem.count} if feeContentItem else None
        try:
            match_remote.unlockUserForMatch(DIZHU_GAMEID, userId, self._room.bigRoomId, instId,
                                            self._room.roomId, self._tableId, self._seatId, contentItem)
        except:
            self._logger.error('SignIFDizhu.unlockUser fail',
                               'userId=', userId,
                               'matchId=', matchId,
                               'ctrlRoomId=', ctrlRoomId,
                               'instId=', instId)
    
class MatchStatusDaoDizhu(MatchStatusDao):
    def __init__(self, room):
        self._room = room
        self._logger = Logger()
        self._logger.add('roomId', self._room.roomId)
        
    def load(self, matchId):
        '''
        加载比赛信息
        @return: MatchStatus
        '''
        key = 'mstatus:%s' % (self._room.gameId)
        jstr = daobase.executeMixCmd('hget', key, matchId)
        if jstr:
            d = json.loads(jstr)
            return MatchStatus(matchId, d['seq'], d['startTime'])
        return None
    
    def save(self, status):
        '''
        保存比赛信息
        '''
        try:
            key = 'mstatus:%s' % (self._room.gameId)
            d = {'seq':status.sequence, 'startTime':status.startTime}
            jstr = json.dumps(d)
            daobase.executeMixCmd('hset', key, status.matchId, jstr)
        except:
            self._logger.error('MatchStatusDaoDizhu.save',
                               'matchId=', status.matchId,
                               'instId=', status.instId,
                               'startTime=', status.startTime)
    
class MatchRewardsDizhu(MatchRewards):
    def __init__(self, room):
        self._room = room
        self._logger = Logger()
        self._logger.add('roomId', self._room.roomId)
        
    def sendRewards(self, player, rankRewards):
        '''给用户发送奖励'''
        try:
            if player.isQuit:
                return
            self._logger.info('MatchRewardsDizhu.sendRewards',
                              'groupId=', player.group.groupId if player.group else None,
                              'score=', player.score,
                              'rank=', player.rank,
                              'rankRewards=', rankRewards.rewards)
            user_remote.addAssets(self._room.gameId, player.userId, rankRewards.rewards,
                                      'MATCH_REWARD', self._room.roomId)
            if rankRewards.message:
                pkmessage.sendPrivate(self._room.gameId, player.userId, 0, rankRewards.message)
                datachangenotify.sendDataChangeNotify(self._room.gameId, player.userId, 'message')

            sequence = int(player.group.instId.split('.')[1])
            rewardsLen = len(rankRewards.rewards)
            for reward in rankRewards.rewards:
                chipType = matchutil.getBiChipType(reward['itemId'])
                kindId = 0
                if chipType == daoconst.CHIP_TYPE_ITEM:
                    kindId = reward['itemId'].strip('item:')
                matchutil.report_bi_game_event('MATCH_REWARD', player.userId, self._room.match.matchId, 0, sequence, 0, 0, 0,
                                               [chipType, reward['count'], kindId, player.rank, 0, rewardsLen], 'match_reward')

        except:
            self._logger.error('MatchRewardsDizhu.sendRewards',
                               'groupId=', player.group.groupId if player.group else None,
                               'score=', player.score,
                               'rank=', player.rank,
                               'rankRewards=', rankRewards.rewards)
    
class TableControllerDizhu(TableController):
    def __init__(self, room):
        self._room = room
        self._logger = Logger()
        self._logger.add('roomId', self._room.roomId)
        
    def startTable(self, table):
        '''
        让player在具体的游戏中坐到seat上
        '''
        try:
            callType = table.group.stageConf.conf.get('call.type', 'random')
            callPlayer = None
            if callType == 'inturn':
                callPlayer = self._chooseFirstCallPlayer(table)
                if callPlayer:
                    callPlayer.firstCallFalg = 1

            self._logger.info('TableControllerDizhu.startTable',
                              'groupId=', table.group.groupId,
                              'tableId=', table.tableId,
                              'firstCallPlayerId=', callPlayer.userId if callPlayer else 0,
                              'stepType=', table.group.stageConf.type,
                              'currentCardCount=', table.seats[0].player.cardCount,
                              'cardCount=', table.group.stageConf.cardCount,
                              'callType=', callType,
                              'userScores=', [(s.player.userId, s.player.score, s.player.isQuit) for s in table.seats],
                              'userIds=', table.getUserIdList())

            # 统计阶段的局数
            sequence = int(table.group.instId.split('.')[1])
            groupNum = table.group.groupId.split('.')[-1]
            userIds = table.getUserIdList()
            matchutil.report_bi_game_event("MATCH_START_TABLE", userIds[0] if userIds else 0, table.group.matchId, table.tableId, sequence, 0, 0, 0, [table.group.stageIndex, groupNum, table.group.startPlayerCount, table.group.stageConf.cardCount], 'match_start_table')  # _stage.matchingId

            # 发送tableStart
            message = buildTableStartMessage(table)
            router.sendTableServer(message, table.roomId)
        except:
            self._logger.error('TableControllerDizhu.startTable',
                               'groupId=', table.group.groupId,
                               'tableId=', table.tableId,
                               'userIds=', table.getUserIdList())

    def _chooseFirstCallPlayer(self, table):
        # 选择首先要叫地主的人
        stepType = table.group.stageConf.type
        cardCount = table.seats[0].player.cardCount
        if stepType == 2:  # 定局阶段
            if cardCount == 1:  # 选择首先叫的用户设置下一个首先叫的用户
                players = [seat.player for seat in table.seats]
                players.sort(key=lambda p: (p.score, p.userId), reverse=True)
                return players[1]
            else:
                players = [seat.player for seat in table.seats]
                players.sort(key=lambda p: p.userId)
                for index, player in enumerate(players):
                    if player.firstCallFalg == 1:
                        player.firstCallFalg = 0
                        nextCallIndex = index + 1
                        if nextCallIndex > len(table.seats) - 1:
                            nextCallIndex = 0
                        nextCallPlayer = players[nextCallIndex]
                        return nextCallPlayer
        return None

    
    def clearTable(self, table):
        '''
        清理桌子
        '''
        # 发送tableClear
        try:
            tableClearMessage = buildTableClearMessage(table)
            router.sendTableServer(tableClearMessage, table.roomId)
        except:
            self._logger.error('TableControllerDizhu.clearTable',
                               'groupId=', table.group.groupId,
                               'tableId=', table.tableId,
                               'userIds=', table.getUserIdList())
    
    def updateTableInfo(self, table):
        '''
        桌子信息变化
        '''
        # 发送tableInfo
        try:
            tableInfoMessage = buildTableInfoMessage(table)
            router.sendTableServer(tableInfoMessage, table.roomId)
        except:
            self._logger.error('TableControllerDizhu.updateTableInfo',
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
            self._logger.error('TableControllerDizhu.userReconnect',
                               'groupId=', table.group.groupId,
                               'tableId=', table.tableId,
                               'userId=', seat.player.userId if seat.player else 0,
                               'userIds=', table.getUserIdList())

def getMatchName(room, player):
    if player.group.isGrouping:
        return '%s%s' % (room.roomConf['name'], player.group.groupName)
    return room.roomConf['name']

def buildLoserInfo(room, player):
    info = None
    if player.group.stageConf.type == StageType.ASS:
        checkScore = player.group.assLoseScore
        if player.score < checkScore:
            info = u'由于积分低于' + str(checkScore) + u',您已经被淘汰出局.请再接再厉,争取取得更好名次!'
    if info is None:
        info = u'比赛：%s\n名次：第%d名\n胜败乃兵家常事 大侠请重新来过！' % (getMatchName(room, player), player.rank)
    return info
    
def buildWinInfo(room, player, rankRewards):
    if rankRewards:
        return u'比赛：%s\n名次：第%d名\n奖励：%s\n奖励已发放，请您查收。' % (getMatchName(room, player), player.rank, rankRewards.desc)
    return u'比赛：%s\n名次：第%d名\n奖励：%s\n奖励已发放，请您查收。' % (getMatchName(room, player), player.rank)

class PlayerNotifierDizhu(PlayerNotifier):
    def __init__(self, room):
        self._room = room
        self._logger = Logger()
        
    def notifyMatchCancelled(self, signer, reason, message=None):
        '''
        通知用户比赛由于reason取消了
        '''
        try:
            userId = signer.userId
            player = self._room.match.findPlayer(userId)
            if player and player.isQuit:
                return
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
            self._logger.error('PlayerNotifierDizhu.notifyMatchCancelled',
                               'userId=', signer.userId,
                               'instId=', signer.instId,
                               'reason=', reason,
                               'message=', message)
    
    def notifyMatchOver(self, player, reason, rankRewards):
        '''
        通知用户比赛结束了
        '''
        try:
            lastBestRank = None
            record = MatchRecord.loadRecord(self._room.gameId, player.userId, self._room.match.matchId)
            if record:
                lastBestRank = record.bestRank
            if (reason == MatchFinishReason.USER_WIN
                or reason == MatchFinishReason.USER_LOSER):
                try:
                    if player.isQuit:
                        rankRewards = None

                    # 发送用户比赛结束事件， 用于持久化比赛数据
                    self._room.fire(UserMatchOverEvent(self._room, player, rankRewards.conf.get('desc') if rankRewards else None))

                    event_remote.publishMatchWinloseEvent(self._room.gameId,
                                                          player.userId,
                                                          self._room.match.matchId,
                                                          reason == MatchFinishReason.USER_WIN,
                                                          player.rank,
                                                          player.group.startPlayerCount,
                                                          rankRewards.conf if rankRewards else None)

                    tempGameResult = 1 if reason == MatchFinishReason.USER_WIN else -1
                    hall51event.sendToHall51MatchOverEvent(player.userId, self._room.gameId, self._room.bigRoomId, tempGameResult, -1, -1)


                    from dizhu.entity.matchhistory import MatchHistoryHandler
                    MatchHistoryHandler.onMatchOver(player.userId,
                                                    player.group.matchConf.recordId,
                                                    player.rank,
                                                    reason == MatchFinishReason.USER_WIN,
                                                    rankRewards.conf if rankRewards else None,
                                                    player.group.isGrouping)

                    if not rankRewards:
                        matchutil.report_bi_game_event('MATCH_REWARD', player.userId, self._room.match.matchId, 0, int(player.group.instId.split('.')[1]),
                                                       0, 0, 0,
                                                       [0, 0, 0, player.rank, 0, 0],
                                                       'match_reward')
                except Exception, e:
                    self._logger.error('PlayerNotifierDizhu.notifyMatchOver',
                                       'userId=', player.userId,
                                       'groupId=', player.group.groupId,
                                       'reason=', reason,
                                       'err=', e.message,
                                       'rankRewards=', rankRewards.rewards if rankRewards else None)


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
            try:
                msg.setResult('beatDownUser', player.beatDownUserName)
            except:
                ftlog.debug('NobeatDownUser group match')
                ftlog.exception()

            if rankRewards or reason == MatchFinishReason.USER_WIN:
                msg.setResult('info', buildWinInfo(self._room, player, rankRewards))
                if rankRewards.todotask:
                    msg.setResult('todotask', rankRewards.todotask)
            else:
                msg.setResult('info', buildLoserInfo(self._room, player))

            msg.setResult('mucount', player.group.startPlayerCount if player.group.isGrouping else player.group.totalPlayerCount)
            msg.setResult('date', str(datetime.now().date().today()))
            msg.setResult('time', time.strftime('%H:%M', time.localtime(time.time())))
            msg.setResult('addInfo', '')
            rewardDesc = ''
            if rankRewards:
                msg.setResult('reward', matchutil.buildRewards(rankRewards))
                rewardDesc = matchutil.buildRewardsDesc(rankRewards)
                if rewardDesc:
                    msg.setResult('rewardDesc', rewardDesc)
            msg.setResult('mname', getMatchName(self._room, player))

            clientId = sessiondata.getClientId(player.userId)

            shareInfo = commconf.getNewShareInfoByCondiction(self._room.gameId, clientId)
            msg.setResult('shareInfo', {'erweima': shareInfo.get('erweima', '') if shareInfo else {}})

            record = MatchRecord.loadRecord(self._room.gameId, player.userId, self._room.match.matchId)
            if record:
                msg.setResult('mrecord', {'bestRank':record.bestRank,
                                          'lastBestRank':lastBestRank,
                                          'bestRankDate':record.bestRankDate,
                                          'isGroup':record.isGroup,
                                          'crownCount':record.crownCount,
                                          'playCount':record.playCount})
            else:
                from dizhu.activities.toolbox import Tool
                msg.setResult('mrecord', {'bestRank':player.rank,
                                          'lastBestRank':lastBestRank,
                                          'bestRankDate':Tool.datetimeToTimestamp(datetime.now()),
                                          'isGroup':1 if player.group.isGrouping else 0,
                                          'crownCount':1 if player.rank == 1 else 0,
                                          'playCount':1})

            try:
                # 玩家奖励信息记录
                dizhushare.addMatchHistoryCount(self._room.bigRoomId, player.rank)
                if rankRewards:
                    dizhushare.groupMatchRewardRecord(player.userId, rankRewards.conf)

                # 获取新分享内容
                shareNum = dizhushare.getMatchHistoryCount(self._room.bigRoomId)
                rankRewardsList = dizhuhallinfo.getMatchSessionRankRewards(DIZHU_GAMEID, clientId, self._room.bigRoomId)
                rewardType, shareInfoNew = dizhushare.getGroupShareInfoNew(shareNum, self._room.roomConf, rankRewards,
                                                                           rankRewardsList)
                if shareInfoNew:
                    msg.setResult('shareInfoNew', shareInfoNew)

                # 设置奖状分享的todotask diplomaShare
                matchShareType = 'arena' if rewardType == 'redEnvelope' else 'group'
                shareTodoTask = commconf.getMatchShareInfo(player.userName,
                                                           getMatchName(self._room, player),
                                                           player.rank,
                                                           rewardDesc,
                                                           player.userId,
                                                           matchShareType,
                                                           clientId)
                if shareTodoTask:
                    msg.setResult('shareTodoTask', shareTodoTask)

                # 设置奖状分享大图, 判断当前用户奖励有没有配置大图
                if rankRewards:
                    bigImg = rankRewards.conf.get('bigImg', '')
                    if bigImg:
                        msg.setResult('bidImg', bigImg)

                    if ftlog.is_debug():
                        ftlog.debug('MatchPlayerNotifierDizhu.notifyMatchOver userId=', player.userId,
                                    'roomId=', self._room.roomId,
                                    'bigImg=', bigImg,
                                    'rank=', player.rank,
                                    'rankRewards.conf=', rankRewards.conf)
                # 冠军触发抽奖逻辑
                match_lottery = MatchLottery()
                ret = match_lottery.checkMatchRank(player.userId, self._room.match.matchId, player.rank)
                if ret:
                    msg.setResult('match_lottery', 1)

                # 局间奖励总数
                if player.stageRewardTotal:
                    msg.setResult('stageReward', {'count': player.stageRewardTotal})
                if ftlog.is_debug():
                    ftlog.debug('PlayerNotifierDizhu.notifyMatchOver',
                                'userId=', player.userId,
                                'stageReward=', player.stageRewardTotal)

            except Exception, e:
                ftlog.error('MatchPlayerNotifierDizhu.notifyMatchOver.',
                            'userId=', player.userId,
                            'roomId=', self._room.roomId,
                            'matchId=', self._room.match.matchId,
                            'err=', e.message)
            ###########################

            if not player.isQuit:
                router.sendToUser(msg, player.userId)

            if player.rank == 1 and self._room.roomConf.get('championLed') and not player.isQuit:
                # 冠军发送Led通知所有其他玩家
                ledtext = dizhuled._mk_match_champion_rich_text(
                    player.userName,
                    self._room.roomConf['name'],
                    self._room.roomConf.get('rewardShow', rewardDesc)
                )
                LedUtil.sendLed(ledtext, 'global')

            if reason in (MatchFinishReason.USER_NOT_ENOUGH, MatchFinishReason.RESOURCE_NOT_ENOUGH) and not player.isQuit:
                mo = MsgPack()
                mo.setCmd('m_signs')
                mo.setResult('gameId', self._room.gameId)
                mo.setResult('roomId', self._room.bigRoomId)
                mo.setResult('userId', player.userId)
                mo.setResult('signs', {self._room.bigRoomId:0})
                router.sendToUser(mo, player.userId)

            sequence = int(player.group.instId.split('.')[1])
            matchutil.report_bi_game_event("MATCH_FINISH", player.userId, player.group.matchId, 0, sequence, 0, 0, 0, [], 'match_end')  #_stage.matchingId
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
            if player.isQuit:
                return

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
        try:
            if player.isQuit:
                return
            self._room.sendMatchStatas(player.userId)
        except:
            self._logger.error('PlayerNotifierDizhu.notifyMatchUpdate',
                               'userId=', player.userId,
                               'groupId=', player.group.groupId)

    def _notifyMatchRank(self, player):
        if player.isQuit:
            return
        msg = MsgPack()
        msg.setCmd('m_rank')
        msg.setResult('mranks', player.group.ranktops)
        router.sendToUser(msg, player.userId)
        
    def _notifyMatchRank2(self, player):
        if player.isQuit:
            return
        msg = MsgPack()
        msg.setCmd('m_rank')
        ranktops = []
        ranktops.append({'userId':player.userId,
                         'name':player.userName,
                         'score':player.score,
                         'rank':player.scoreRank})
        for i, r in enumerate(player.group.ranktops):
            ranktops.append({'userId':r[0], 'name':r[1], 'score':r[2], 'rank':i+1})
        if 'momo' in player.clientId: # 解决 momo3.372客户端bug:比赛等待页面JS错误
            for _ in xrange(len(ranktops), 10):
                ranktops.append({'userId':0, 'name':'', 'score':'', 'rank':0})
        msg.setResult('mranks', ranktops)
        router.sendToUser(msg, player.userId)
        
    def notifyMatchRank(self, player):
        '''
        通知比赛排行榜
        '''
        try:
            _, clientVer, _ = strutil.parseClientId(player.clientId)
            if self._logger.isDebug():
                self._logger.debug('PlayerNotifierDizhu.notifyMatchRank',
                                   'userId=', player.userId,
                                   'groupId=', player.group.groupId,
                                   'clientId=', player.clientId)
            if clientVer >= 3.37:
                self._notifyMatchRank2(player)
            else:
                self._notifyMatchRank(player)
        except:
            self._logger.error('PlayerNotifierDizhu.notifyMatchRank',
                               'userId=', player.userId,
                               'groupId=', player.group.groupId,
                               'clientId=', player.clientId)
        
    def _notifyMatchWait(self, player, step=None, riseWait=0):
        if player.isQuit:
            return
        self.notifyMatchUpdate(player)
        self._notifyMatchRank(player)

        msg = MsgPack()
        msg.setCmd('m_wait')
        msg.setResult('gameId', self._room.gameId)
        msg.setResult('roomId', self._room.bigRoomId)
        msg.setResult('tableId', player.group.area.tableId)
        msg.setResult('mname', self._room.roomConf["name"])
        msg.setResult('riseWait', riseWait)
        msg.setResult('riseCount', player.group.stageConf.riseUserCount)
        if step != None:
            msg.setResult('step', 0)  # 0 - 请稍后  1- 晋级等待
        router.sendToUser(msg, player.userId)
            
    def _notifyMatchWait2(self, player, step=None, riseWait=0):
        if player.isQuit:
            return
        self.notifyMatchUpdate(player)
        self._notifyMatchRank2(player)
        
        msg = MsgPack()
        msg.setCmd('m_wait')
        msg.setResult('gameId', self._room.gameId)
        msg.setResult('roomId', self._room.bigRoomId)
        msg.setResult('tableId', player.group.area.tableId)
        msg.setResult('riseWait', riseWait)
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
        
    def notifyMatchWait(self, player, step=None, riseWait=0):
        '''
        通知用户等待
        '''
        try:
            if player.isQuit:
                return
            self._logger.debug('PlayerNotifierDizhu.notifyMatchWait userId=', player.userId,
                               'clientId=', player.clientId,
                               'groupId=', player.group.groupId)
            
            _, clientVer, _ = strutil.parseClientId(player.clientId)
            if clientVer >= 3.37:
                self._notifyMatchWait2(player, step, riseWait)
            else:
                self._notifyMatchWait(player, step, riseWait)
        except:
            self._logger.error('PlayerNotifierDizhu.notifyMatchRank',
                               'userId=', player.userId,
                               'groupId=', player.group.groupId,
                               'clientId=', player.clientId)
    
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

            for signer in signers:
                # 保存用户折扣次数
                roomDiscountConf = match_signin_discount.getRoomDiscountConf(self._room.bigRoomId)
                if roomDiscountConf and signer.feeItem:
                    ret, _, _ = match_signin_discount.canMatchDiscount(signer.userId, self._room.bigRoomId,
                                                                    signer.feeItem.assetKindId)
                    if ret:
                        match_signin_discount.saveUserMatchDiscountCount(signer.userId, self._room.bigRoomId,
                                                                         signer.feeItem.assetKindId)

            userIds = [p.userId for p in signers]
            self._logger.info('PlayerNotifierDizhu.notifyMatchStart begin send tcp m_start'
                              'instId=', instId,
                              'userCount=', len(signers))
            if userIds:
                newUserIds = []
                for uId in userIds:
                    player = self._room.match.findPlayer(uId)
                    if player and player.isQuit:
                        continue
                    newUserIds.append(uId)
                router.sendToUsers(mstart, newUserIds)
                self._logger.info('PlayerNotifierDizhu.notifyMatchStart end send tcp m_start'
                                  'instId=', instId,
                                  'userCount=', len(signers))
                
                self._logger.info('PlayerNotifierDizhu.notifyMatchStart begin send bi report'
                                  'instId=', instId,
                                  'userCount=', len(signers))
                sequence = int(instId.split('.')[1])
                datas = {'userIds' : userIds, 'roomId' : self._room.roomId, 'sequence' : sequence, 'index' : 0}
                FTTimer(2, self.notifyMatchStartDelayReport_, datas)
                self._logger.info('PlayerNotifierDizhu.notifyMatchStart begin send bi report async'
                                  'instId=', instId,
                                  'userCount=', len(signers))
        except:
            self._logger.error('PlayerNotifierDizhu.notifyMatchStart'
                               'instId=', instId,
                               'userCount=', len(signers))
    
    def _notifyStageStart(self, player):
        if player.isQuit:
            return
        if player.group.stageIndex == 0:
            self._notifyMatchWait(player, 0)
            
    def _notifyStageStart2(self, player):
        if player.isQuit:
            return
        if player.group.stageIndex == 0:
            if player.waitReason == WaitReason.BYE:
                self._notifyMatchWait2(player, 0)
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
                
    def notifyStageStart(self, player):
        '''
        通知用户正在配桌
        '''
        try:
            if player.isQuit:
                return
            if self._logger.isDebug():
                self._logger.debug('PlayerNotifierDizhu.notifyStageStart',
                                   'userId=', player.userId,
                                   'isQuit=', player.isQuit,
                                   'clientId=', player.clientId,
                                   'groupId=', player.group.groupId)
            _, clientVer, _ = strutil.parseClientId(player.clientId)
            if clientVer >= 3.37:
                self._notifyStageStart2(player)
            else:
                self._notifyStageStart(player)
        except:
            self._logger.error('PlayerNotifierDizhu.notifyStageStart',
                               'userId=', player.userId,
                               'clientId=', player.clientId,
                               'groupId=', player.group.groupId)
    
    def notifyMatchStartDelayReport_(self):
        argl = FTTasklet.getCurrentFTTasklet().run_argl
        datas = argl[0]
        userIds = datas['userIds']
        roomId = datas['roomId']
        sequence = datas['sequence']
        index = datas['index']
        self._logger.info('PlayerNotifierDizhu.notifyMatchStartDelayReport_',
                          'index=', index,
                          'total=', len(userIds))
        nindex = self.notifyMatchStartDelayReport(userIds, roomId, sequence, index)
        if nindex < 0 :
            self._logger.info('PlayerNotifierDizhu.notifyMatchStartDelayReport_ end')
        else:
            datas['index'] = nindex 
            FTTimer(0.1, self.notifyMatchStartDelayReport_, datas)
    
    def notifyMatchStartDelayReport(self, userIds, roomId, sequence, index):
        ulen = len(userIds)
        blockc = 0
        while index < ulen :
            userId = userIds[index]
            matchutil.report_bi_game_event('MATCH_START', userId, roomId, 0, sequence, 0, 0, 0, [], 'match_start')  # _stage.matchingId
            index += 1
            blockc += 1
            if blockc > 10 :
                return index
        return -1

    def getUserChampionLimitFlag(self, signer):
        '''
        是否冠军重新发牌
        '''
        return matchutil.getUserChampionLimitFlag(signer.userId, signer.inst.roomId, signer.inst.area.matchConf.recordId)

    def notifyMatchTimeEnd(self, player, instId):
        '''
        通知用户退赛成功
        '''
        try:
            if self._logger.isDebug():
                self._logger.debug('PlayerNotifierDizhu.notifyMatchSignout',
                                   'clientId=', player.clientId,
                                   'userId=', player.userId)
            mo = MsgPack()
            mo.setCmd('m_signout')
            mo.setResult('gameId', DIZHU_GAMEID)
            mo.setResult('roomId', self._room.roomId)
            mo.setResult('userId', player.userId)
            try:
                sequence = int(instId.split('.')[1])
            except:
                sequence = 0
            finalUserChip = userchip.getChip(player.userId)
            router.sendToUser(mo, player.userId)
            bireport.reportGameEvent('MATCH_SIGN_OUT', player.userId, DIZHU_GAMEID, self._room.roomId,
                                     0, sequence, 0, 0, 0, [], player.clientId, 0, finalUserChip)

        except:
            self._logger.error('PlayerNotifierDizhu.notifyMatchSignout',
                               'clientId=', player.clientId,
                               'userId=', player.userId)
    
class UserInfoLoaderDizhu(UserInfoLoader):
    def loadUserAttrs(self, userId, attrList):
        '''
        '''
        return userdata.getAttrs(userId, attrList)


class MatchRankRewardsSelectorDizhu(MatchRankRewardsSelector):
    def __init__(self, room):
        self._room = room
        self._logger = Logger()
        self._logger.add('roomId', self._room.roomId)

    def getRewards(self, userId, rankRewards):
        '''
        获取渠道奖励
        '''
        ret = rankRewards
        if not ret:
            return ret
        clientId = sessiondata.getClientId(userId)
        rankRewardsChannelList = [MatchRankRewards().decodeFromDict(r) for r in
                                  dizhuhallinfo.getMatchSessionRankRewards(DIZHU_GAMEID, clientId, self._room.bigRoomId)]
        for rankRewardsChannel in rankRewardsChannelList:
            if rankRewards.startRank == rankRewardsChannel.startRank and rankRewards.endRank == rankRewardsChannel.endRank:
                ret = rankRewardsChannel
                break
        return ret

    def getRewardsList(self, userId, rankRewardsList):
        '''
        获取渠道奖励列表
        '''
        clientId = sessiondata.getClientId(userId)
        rankRewardsChannelList = [MatchRankRewards().decodeFromDict(r) for r in
                                  dizhuhallinfo.getMatchSessionRankRewards(DIZHU_GAMEID, clientId, self._room.bigRoomId)]

        rankRewardsListCopy = copy.deepcopy(rankRewardsList)
        for index, rankRewards in enumerate(rankRewardsListCopy):
            for rankRewardsChannel in rankRewardsChannelList:
                if rankRewards.startRank == rankRewardsChannel.startRank and rankRewards.endRank == rankRewardsChannel.endRank:
                    rankRewardsListCopy[index] = rankRewardsChannel
        return rankRewardsListCopy
