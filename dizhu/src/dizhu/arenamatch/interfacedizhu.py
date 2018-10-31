# -*- coding:utf-8 -*-
'''
Created on 2015年12月1日

@author: zhaojiangang
'''
from datetime import datetime
import time

from dizhu.entity.led_util import LedUtil
from dizhu.entity.matchrecord import MatchRecord
from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from hall.entity import datachangenotify
from hall.entity.todotask import TodoTaskShowInfo, TodoTaskHelper
from hall.servers.util.rpc import user_remote, event_remote
from poker.entity.biz import bireport
import poker.entity.biz.message.message as pkmessage
from poker.entity.dao import userdata, sessiondata, daobase, onlinedata
from poker.entity.game.rooms.arena_match_ctrl.exceptions import \
    SigninFeeNotEnoughException
from poker.entity.game.rooms.arena_match_ctrl.interfaces import \
    MatchPlayerNotifier, MatchTableController, UserInfoLoader, \
    MatchRankRewardsSender, SigninFee, SigninRecordDao, UserLocker
from poker.entity.game.rooms.big_match_ctrl.const import MatchFinishReason, \
    AnimationType
from poker.protocol import router
from dizhu.entity import dizhuonlinedata, dizhuled
from dizhu.entity.dizhuconf import DIZHU_GAMEID
from dizhu.entity import dizhudiplomashare
from poker.util import strutil

class UserLockerDizhu(UserLocker):
    def lockUser(self, userId, roomId, tableId, seatId, clientId):
        locList = dizhuonlinedata.getOnlineLocListByGameId(userId, DIZHU_GAMEID, clientId)
        if locList:
            for loc in locList:
                if (strutil.getBigRoomIdFromInstanceRoomId(loc[1])
                    == strutil.getBigRoomIdFromInstanceRoomId(roomId)):
                    ftlog.warn('UserLockerDizhu.lockUser',
                               'userId=', userId,
                               'roomId=', roomId,
                               'tableId=', tableId,
                               'seatId=', seatId,
                               'clientId=', clientId,
                               'loc=', loc,
                               'locList=', locList)
                    return False
        onlinedata.setBigRoomOnlineLoc(userId, roomId, tableId, seatId)
        return True
    
    def unlockUser(self, userId, roomId, tableId, clientId):
        onlinedata.removeOnlineLoc(userId, roomId, tableId)
    
class MatchPlayerNotifierDizhu(MatchPlayerNotifier):
    def __init__(self, room, matchIF):
        self._room = room
        self._matchIF = matchIF
        
    def notifyMatchStart(self, player):
        '''
        通知用户比赛开始了
        '''
        try:
            ftlog.info('MatchPlayerNotifierDizhu.notifyMatchStart matchId=', player.matchInst.matchId,
                       'instId=', player.matchInst.instId,
                       'userId=', player.userId)
            mo = MsgPack()
            mo.setCmd('m_start')
            mo.setResult('gameId', self._room.gameId)
            mo.setResult('roomId', self._room.bigRoomId)
            router.sendToUser(mo, player.userId)
            
            mo = MsgPack()
            mo.setCmd('m_play_animation')
            mo.setResult('gameId', self._room.gameId)
            mo.setResult('roomId', self._room.bigRoomId)
            mo.setResult('type', AnimationType.ASSIGN_TABLE)
            router.sendToUser(mo, player.userId)
            
            sequence = int(player.matchInst.instId.split('.')[1])
            self.report_bi_game_event('MATCH_START', player.userId, self._room.bigRoomId, 0, sequence, 0, 0, 0, [], 'match_start')
        except:
            ftlog.error()
            
    def notifyMatchUpdate(self, player):
        try:
            msg = MsgPack()
            msg.setCmd('m_update')
            msg.setResult('_debug_user_%d_' % (1), player.userId)
            self._matchIF.getMatchStates(self._room, player.userId, player, msg)
            router.sendToUser(msg, player.userId)
        except:
            ftlog.error()
            
    def notifyMatchWait(self, player):
        '''
        通知用户等待晋级
        '''
        try:
            ftlog.info('MatchPlayerNotifierDizhu.notifyMatchWait matchId=', player.matchInst.matchId,
                       'instId=', player.matchInst.instId,
                       'userId=', player.userId,
                       'stageIndex=', player.stage.index)
            self.notifyMatchUpdate(player)
            msg = MsgPack()
            msg.setCmd('m_wait')
            msg.setResult('gameId', self._room.gameId)
            msg.setResult('roomId', self._room.bigRoomId)
            msg.setResult('tableId', player.match.tableId)
            msg.setResult('mname', self._room.roomConf['name'])
            prevStage = player.stage.prevStage or player.stage
            msg.setResult('riseCount', prevStage.stageConf.riseUserCount)
            steps = []
            for stage in player.matchInst.stages:
                isCurrent = True if stage == prevStage else False
                des = '%s人晋级' % (stage.stageConf.riseUserCount)
                stepInfo = {'des':des}
                if isCurrent:
                    stepInfo['isCurrent'] = 1
                stepInfo['name'] = stage.stageConf.name
                steps.append(stepInfo)
                
            msg.setResult('steps', steps)
            msg.setResult('rise', player.cardCount == 0) # arena比赛已经确定升级player.stage.stageConf.cardCount
            msg.setResult('matchType', 'arena_match') # arena比赛
            router.sendToUser(msg, player.userId)
        except:
            ftlog.error()
        
    def notifyMatchRank(self, player):
        '''
        通知比赛排行榜
        '''
        try:
            assert(player.stage)
            ftlog.info('MatchPlayerNotifierDizhu.notifyMatchRank matchId=', player.matchInst.matchId,
                       'instId=', player.matchInst.instId,
                       'userId=', player.userId,
                       'stageIndex=', player.stage.index)
            msg = MsgPack()
            msg.setCmd('m_rank')
            ranktops = []
            ranktops.append({'userId':player.userId,
                             'name':player.userName,
                             'score':player.score,
                             'rank':player.rank})
            msg.setResult('mranks', ranktops)
            router.sendToUser(msg, player.userId)
        except:
            ftlog.error()
            
    def notifyMatchGiveupFailed(self, player, message):
        '''
        通知用户放弃比赛失败
        '''
        try:
            msg = MsgPack()
            msg.setCmd('room')
            msg.setError(-1, message)
            router.sendToUser(msg, player.userId)
        except:
            ftlog.error()
    
    def notifyMatchWillCancelled(self, player, reason):
        '''
        通知用户比赛即将取消
        '''
        try:
            ftlog.info('MatchPlayerNotifierDizhu.notifyMatchWillCancelled matchId=', player.matchInst.matchId,
                       'instId=', player.matchInst.instId,
                       'userId=', player.userId,
                       'stageIndex=', player.stage.index if player.stage else None,
                       'reason=', reason)
            TodoTaskHelper.sendTodoTask(6, player.userId, TodoTaskShowInfo(reason, True))
        except:
            ftlog.error()
    
    def notifyMatchCancelled(self, player, reason, info):
        '''
        通知用户比赛取消
        '''
        try:
            msg = MsgPack()
            msg.setCmd('m_over')
            msg.setResult('gameId', self._room.gameId)
            msg.setResult('roomId', self._room.bigRoomId)
            msg.setResult('reason', reason)
            msg.setResult('info', info)
            router.sendToUser(msg, player.userId)
        except:
            ftlog.error()
    
    def buildWinInfo(self, player, rankRewards):
        return '比赛：%s\n名次：第%d名\n奖励：%s\n奖励已发放，请您查收。' % (self._room.roomConf["name"], player.rank, rankRewards.desc)

    def buildLoserInfo(self, player):
        return '比赛：%s\n名次：第%d名\n胜败乃兵家常事 大侠请重新来过！' % (self._room.roomConf["name"], player.rank)

    def notifyMatchOver(self, player, reason, rankRewards):
        '''
        通知用户比赛结束了
        '''
        try:
            ftlog.info('MatchPlayerNotifierDizhu.notifyMatchOver matchId=', player.matchInst.matchId,
                       'instId=', player.matchInst.instId,
                       'userId=', player.userId,
                       'stageIndex=', player.stage.index,
                       'rank=', player.rank,
                       'reason=', reason,
                       'rankRewards=', rankRewards)

            if (reason == MatchFinishReason.USER_WIN
                or reason == MatchFinishReason.USER_LOSER):
                try:
                    event_remote.publishMatchWinloseEvent(self._room.gameId,
                                                      player.userId,
                                                      self._room.match.matchId,
                                                      reason == MatchFinishReason.USER_WIN,
                                                      player.rank,
                                                      player.matchInst.matchConf.stages[0].totalUserCount,
                                                      rankRewards.conf if rankRewards else None)
                    from dizhu.entity.matchhistory import MatchHistoryHandler
                    MatchHistoryHandler.onMatchOver(player.userId,
                                                    player.matchInst.matchConf.recordId,
                                                    player.rank,
                                                    reason == MatchFinishReason.USER_WIN,
                                                    rankRewards.conf if rankRewards else None,
                                                    False)
                except:
                    ftlog.error()

                # 比赛记录保存
                try:
                    event = {'gameId':self._room.gameId,
                            'userId':player.userId,
                            'matchId':self._room.match.matchId,
                            'rank':player.rank,
                            'isGroup': 0}
                    MatchRecord.updateAndSaveRecord(event)
                except:
                    ftlog.error()
                
            msg = MsgPack()
            msg.setCmd('m_over')
            msg.setResult('gameId', self._room.gameId)
            msg.setResult('roomId', self._room.bigRoomId)
            msg.setResult('userId', player.userId)
            msg.setResult('reason', reason)
            msg.setResult('rank', player.rank)
            
            if rankRewards:
                msg.setResult('info', self.buildWinInfo(player, rankRewards))
            else:
                msg.setResult('info', self.buildLoserInfo(player))
            msg.setResult('mucount', player.matchInst.matchConf.stages[0].totalUserCount)
            msg.setResult('date', str(datetime.now().date().today()))
            msg.setResult('time', time.strftime('%H:%M', time.localtime(time.time())))
            msg.setResult('addInfo', '')
            rewardDesc = ''
            if rankRewards:
                from dizhu.bigmatch.match import BigMatch
                msg.setResult('reward', BigMatch.buildRewards(rankRewards))
                rewardDesc = BigMatch.buildRewardsDesc(rankRewards)
                if rewardDesc:
                    msg.setResult('rewardDesc', rewardDesc)
            msg.setResult('mname', self._room.roomConf["name"])
            
            try:
                msg.setResult('beatDownUser', player.beatDownUserName)
                if rankRewards and rankRewards.todotask:
                    msg.setResult('todotask', rankRewards.todotask)
                # 设置奖状分享的todotask diplomaShare
                shareTodoTask = dizhudiplomashare.buildDiplomaShare(player.userName,
                                                               self._room.roomConf["name"], 
                                                               player.rank, 
                                                               rewardDesc, 
                                                               player.userId)
                if shareTodoTask:
                    msg.setResult('shareTodoTask', shareTodoTask)
            except:
                ftlog.debug('NobeatDownUser arena match')
                ftlog.exception()

            record = MatchRecord.loadRecord(self._room.gameId, player.userId, self._room.match.matchId)
            if record:
                msg.setResult('mrecord', {'bestRank':record.bestRank,
                                         'bestRankDate':record.bestRankDate,
                                         'isGroup':record.isGroup,
                                         'crownCount':record.crownCount,
                                         'playCount':record.playCount})
            else:
                from dizhu.activities.toolbox import Tool
                msg.setResult('mrecord', {'bestRank':player.rank,
                                         'bestRankDate':Tool.datetimeToTimestamp(datetime.now()),
                                         'isGroup': 0,
                                         'crownCount':1 if player.rank == 1 else 0,
                                         'playCount':1})

            router.sendToUser(msg, player.userId)

            if player.rank == 1 and self._room.roomConf.get('championLed'):
                # 冠军发送Led通知所有其他玩家
                ledtext = dizhuled._mk_match_champion_rich_text(
                    player.userName,
                    self._room.roomConf['name'],
                    self._room.roomConf.get('rewardShow', rewardDesc)
                )
                LedUtil.sendLed(ledtext, 'global')

            sequence = int(player.matchInst.instId.split('.')[1])
            self.report_bi_game_event('MATCH_FINISH', player.userId, player.matchInst.matchId, 0, sequence, 0, 0, 0, [], 'match_end')
        except:
            ftlog.error()

    def report_bi_game_event(self, eventId, userId, roomId, tableId, roundId, detalChip, state1, state2, cardlist, tag=''):
        try:
            clientId = sessiondata.getClientId(userId)
            bireport.reportGameEvent(eventId, userId, 6, roomId, tableId, roundId, detalChip, state1, state2, cardlist, clientId, 0, 0)
            ftlog.debug('report_bi_game_event tag=', tag, 'eventId=', eventId, 'userId=', userId, 'gameId=6', 'roomId=', roomId, 'tableId=', tableId, 'roundId=', roundId,
                        caller=self)
        except:
            ftlog.error('report_bi_game_event error tag=', tag, 'eventId=', eventId, 'userId=', userId, 'gameId=6', 'roomId=', roomId, 'tableId=', tableId, 'roundId=', roundId)

class SigninRecordDaoDizhu(SigninRecordDao):
    def __init__(self, room):
        self._room = room
        
    def recordSignin(self, matchId, instId, userId, timestamp, signinParams):
        '''
        记录报名信息
        '''
        try:
            daobase.executeTableCmd(self._room.roomId, 0, 'SADD', 'signs:' + str(self._room.roomId), userId)
        except:
            ftlog.error()
    
    def removeSignin(self, matchId, instId, userId):
        '''
        删除报名信息
        '''
        try:
            daobase.executeTableCmd(self._room.roomId, 0, 'SREM', 'signs:' + str(self._room.roomId), userId)
        except:
            ftlog.error()
    
    def removeAll(self, matchId):
        '''
        删除instId相关的所有报名信息
        '''
        try:
            daobase.executeTableCmd(self._room.roomId, 0, 'DEL', 'signs:' + str(self._room.roomId))
        except:
            ftlog.error()
            
class MatchTableControllerDizhu(MatchTableController):
    def __init__(self, room):
        self._room = room
        
    def startTable(self, table):
        '''
        让桌子开始
        '''
        try:
            mo = MsgPack()
            mo.setCmd('table_manage')
            mo.setAction('m_table_start')
            mo.setParam('roomId', table.roomId)
            mo.setParam('tableId', table.tableId)
            mo.setParam('matchId', table.matchInst.matchId)
            mo.setParam('ccrc', table.ccrc)
            mo.setParam('baseScore', table.matchInst.matchConf.baseScore)
            userInfos = []
            ranks = []
            for seat in table.seats:
                player = seat.player
                if player:
                    ranks.append(player.tableDisplayRank)
                    userInfo = {
                        'userId':player.userId,
                        'seatId':seat.seatId,
                        'score':player.score,
                        'cardCount':player.cardCount,
                        'rank':player.tableDisplayRank,
                        'chiprank':player.tableDisplayRank,
                        'userName':player.userName,
                        'clientId':player.clientId,
                        'ranks':ranks,
                        'stage':{
                            'name':player.stage.stageConf.name,
                            'index':player.stage.stageConf.index,
                            'cardCount':player.stage.stageConf.cardCount,
                            'playerCount':player.stage.stageConf.totalUserCount,
                            'riseCount':player.stage.stageConf.riseUserCount,
                            'animationType':player.stage.stageConf.animationType
                        }
                    }
                else:
                    userInfo = None
                userInfos.append(userInfo)
            mo.setParam('userInfos', userInfos)
            if ftlog.is_debug():
                ftlog.debug('MatchTableControllerDizhu.startTable matchId=', table.matchInst.matchId,
                            'instId=', table.matchInst.instId,
                            'roomId=', table.roomId,
                            'tableId=', table.tableId,
                            'mo=', mo)
            router.sendTableServer(mo, table.roomId)
        except:
            ftlog.error()
            
    def clearTable(self, table):
        '''
        清理桌子
        '''
        try:
            msg = MsgPack()
            msg.setCmd('table_manage')
            msg.setParam('action', 'm_table_clear')
            msg.setParam('gameId', table.gameId)
            msg.setParam('matchId', table.matchInst.matchId)
            msg.setParam('roomId', table.roomId)
            msg.setParam('tableId', table.tableId)
            msg.setParam('ccrc', table.ccrc)
            if ftlog.is_debug():
                ftlog.debug('MatchTableControllerDizhu.clearTable matchId=', table.matchInst.matchId,
                            'instId=', table.matchInst.instId,
                            'roomId=', table.roomId,
                            'tableId=', table.tableId,
                            'mo=', msg)
            router.sendTableServer(msg, table.roomId)
        except:
            ftlog.error()
    
class UserInfoLoaderDizhu(UserInfoLoader):
    def loadUserAttrs(self, userId, attrs):
        '''
        获取用户属性
        '''
        return userdata.getAttrs(userId, attrs)
    
    def getSessionClientId(self, userId):
        '''
        获取用户sessionClientId
        '''
        return sessiondata.getClientId(userId)
    
class MatchRankRewardsSenderDizhu(MatchRankRewardsSender):
    def __init__(self, room):
        self._room = room
        
    def sendRankRewards(self, player, rankRewards):
        '''
        给用户发奖
        '''
        try:
            ftlog.info('MatchRankRewardsSenderDizhu.sendRankRewards matchId=', player.matchInst.matchId,
                       'instId=', player.matchInst.instId,
                       'userId=', player.userId,
                       'rank=', player.rank,
                       'rewards=', rankRewards.rewards)
            user_remote.addAssets(self._room.gameId, player.userId, rankRewards.rewards,
                                  'MATCH_REWARD', player.matchInst.matchId)
            if rankRewards.message:
                pkmessage.sendPrivate(self._room.gameId, player.userId, 0, rankRewards.message)
                datachangenotify.sendDataChangeNotify(self._room.gameId, player.userId, 'message')
        except:
            ftlog.error()
    
class SigninFeeDizhu(SigninFee):
    def __init__(self, room):
        self._room = room
        
    def collectFee(self, inst, userId, fee):
        '''
        收取用户报名费
        '''
        if userId <= 10000:
            return
        
        contentItemList = []
        contentItemList.append({'itemId':fee.assetKindId, 'count':fee.count})
        assetKindId, count = user_remote.consumeAssets(self._room.gameId, userId, contentItemList,
                                                           'MATCH_SIGNIN_FEE', self._room.roomId)
        
        ftlog.info('SigninFeeDizhu.collectFee matchId=', inst.matchId,
                   'userId=', userId,
                   'fees=', contentItemList,
                   'assetKindId=', assetKindId,
                   'count=', count)
        if assetKindId:
            raise SigninFeeNotEnoughException(inst, fee)
        return fee

    def returnFee(self, inst, userId, fee):
        '''
        退还报名费
        '''
        try:
            if userId <= 10000:
                return
            
            contentItemList = []
            contentItemList.append({'itemId':fee.assetKindId, 'count':fee.count})
            user_remote.addAssets(self._room.gameId, userId, contentItemList, 'MATCH_RETURN_FEE', self._room.roomId)
            ftlog.info('SigninFeeDizhu.returnFee matchId=', inst.matchId,
                       'userId=', userId,
                       'fees=', contentItemList)
        except:
            ftlog.error()
            
            
