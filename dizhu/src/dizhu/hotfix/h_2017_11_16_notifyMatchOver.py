# -*- coding:utf-8 -*-
'''
Created on 2017年11月16日

@author: wangjifa
'''

import copy

from datetime import datetime
import time

from dizhu.entity import dizhudiplomashare, dizhuonlinedata, dizhuhallinfo
from dizhu.entity.dizhuconf import DIZHU_GAMEID, MATCH_REWARD_REDENVELOPE
from dizhu.entity.matchrecord import MatchRecord
from dizhu.entity.led_util import LedUtil
from dizhu.entity import dizhuled
from dizhu.games import matchutil
from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from hall.entity import datachangenotify
from hall.entity.hallconf import HALL_GAMEID
from hall.entity.todotask import TodoTaskShowInfo, TodoTaskHelper
from hall.servers.util.rpc import user_remote, event_remote
from poker.entity.biz import bireport
import poker.entity.biz.message.message as pkmessage
from poker.entity.configure import gdata
from poker.entity.dao import userdata, sessiondata, daobase, onlinedata, daoconst
from poker.entity.game.rooms.arena_match_ctrl.exceptions import \
    SigninFeeNotEnoughException
from poker.entity.game.rooms.arena_match_ctrl.interfaces import \
    MatchPlayerNotifier, MatchTableController, UserInfoLoader, \
    MatchRankRewardsSender, SigninFee, SigninRecordDao, UserLocker, MatchRankRewardsSelector
from poker.entity.game.rooms.arena_match_ctrl.match import MatchRankRewards
from poker.entity.game.rooms.big_match_ctrl.const import MatchFinishReason, \
    AnimationType
from poker.protocol import router
from poker.util import strutil
import poker.util.timestamp as pktimestamp
from poker.entity.events import hall51event


def notifyMatchOver(self, player, reason, rankRewards):
    '''
    通知用户比赛结束了
    '''
    try:
        ftlog.info('MatchPlayerNotifierDizhu.notifyMatchOver matchId=', player.matchInst.matchId, 'instId=',
                   player.matchInst.instId, 'userId=', player.userId, 'signinParams=', player.signinParams,
                   'stageIndex=', player.stage.index, 'rank=', player.rank, 'reason=', reason, 'rankRewards=',
                   rankRewards)

        if (reason == MatchFinishReason.USER_WIN or reason == MatchFinishReason.USER_LOSER):
            try:
                if player.isQuit:
                    rankRewards = None
                event_remote.publishMatchWinloseEvent(self._room.gameId, player.userId, self._room.match.matchId,
                                                      reason == MatchFinishReason.USER_WIN, player.rank,
                                                      player.matchInst.matchConf.stages[0].totalUserCount,
                                                      rankRewards.conf if rankRewards else None)

                tempGameResult = 1 if reason == MatchFinishReason.USER_WIN else -1
                hall51event.sendToHall51MatchOverEvent(player.userId, self._room.gameId, self._room.bigRoomId,
                                                       tempGameResult, -1, -1)

                from dizhu.entity.matchhistory import MatchHistoryHandler
                MatchHistoryHandler.onMatchOver(player.userId, player.matchInst.matchConf.recordId, player.rank,
                                                reason == MatchFinishReason.USER_WIN,
                                                rankRewards.conf if rankRewards else None, False, player.mixId)

                if not rankRewards:
                    matchutil.report_bi_game_event('MATCH_REWARD', player.userId, player.matchInst.matchId, 0,
                                                   int(player.matchInst.instId.split('.')[1]), 0, 0, 0,
                                                   [0, 0, 0, player.rank, int(player.mixId) if player.mixId else 0, 0],
                                                   'match_reward')

            except:
                ftlog.error()

            # 比赛记录保存
            try:
                event = {'gameId': self._room.gameId, 'userId': player.userId, 'matchId': self._room.match.matchId,
                         'rank': player.rank, 'isGroup': 0, 'mixId': player.mixId}
                MatchRecord.updateAndSaveRecord(event)
            except:
                ftlog.error()

        msg = MsgPack()
        msg.setCmd('m_over')
        msg.setResult('mixId', player.mixId)
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
            msg.setResult('reward', matchutil.buildRewards(rankRewards))
            rewardDesc = matchutil.buildRewardsDesc(rankRewards)
            if rewardDesc:
                msg.setResult('rewardDesc', rewardDesc)

        roomName = player.matchInst.matchConf.getRoomName(player.mixId)
        arenaContent = dizhuhallinfo.getArenaMatchProvinceContent(player.userId, int(
            player.mixId) if player.mixId else self._room.bigRoomId, None)
        if arenaContent:
            roomName = arenaContent.get('showName') or roomName
        msg.setResult('mname', roomName)

        shareInfo = matchutil.buildShareInfo(self._room.gameId, sessiondata.getClientId(player.userId))
        msg.setResult('shareInfo', {'erweima': shareInfo['erweima'] if shareInfo else {}})

        try:
            msg.setResult('beatDownUser', player.beatDownUserName)
            if rankRewards and rankRewards.todotask:
                msg.setResult('todotask', rankRewards.todotask)
            # 设置奖状分享的todotask diplomaShare
            shareTodoTask = dizhudiplomashare.buildDiplomaShare(player.userName, roomName, player.rank, rewardDesc,
                                                                player.userId)
            if shareTodoTask:
                msg.setResult('shareTodoTask', shareTodoTask)

            if rankRewards:
                bigImg = rankRewards.conf.get('bigImg', '')
                if bigImg:
                    msg.setResult('bidImg', bigImg)

                if ftlog.is_debug():
                    ftlog.debug('MatchPlayerNotifierDizhu.notifyMatchOver userId=', player.userId, 'roomId=',
                                self._room.roomId, 'bigImg=', bigImg, 'rank=', player.rank, 'rankRewards.conf=',
                                rankRewards.conf)
        except:
            ftlog.debug('NobeatDownUser arena match')
            ftlog.exception()

        # 冠军触发抽奖逻辑
        try:
            from dizhu.games.matchutil import MatchLottery
            match_lottery = MatchLottery()
            ret = match_lottery.checkMatchRank(player.userId, self._room.match.matchId, player.rank)
            if ret:
                msg.setResult('match_lottery', 1)
        except:
            ftlog.debug('MatchLottery arena match')
            ftlog.exception()
        ###########################

        # 玩家红包记录
        try:
            from dizhu.entity import dizhushare
            shareInfoConf = rankRewards.conf.get('shareInfo', {}) if rankRewards else {}
            rewardType = shareInfoConf.get('type', '') if shareInfoConf else ''

            shareNum, shareTotalNum = dizhushare.arenaMatchRewardRecord(player.userId, shareInfoConf)

            # 常规配置
            championRewards = player.matchInst.matchConf.feeRewardList
            championShareInfo = championRewards[0].rankRewardsList[0].conf.get('shareInfo', {})
            if arenaContent:
                # 分ip奖励配置
                championRewards = arenaContent.get('rank.rewards', [])
                if championRewards and championRewards[0].get('ranking', {}).get('start', 0) == 1:
                    championShareInfo = championRewards[0].get('shareInfo', {})

            rmb = 0
            matchShareType = 0
            if championShareInfo and championShareInfo.get('type', '') == MATCH_REWARD_REDENVELOPE:
                # 冠军奖励金额
                rmb = championShareInfo.get('rmb', 0)
                matchShareType = 1

            if shareInfoConf and str(rewardType) == MATCH_REWARD_REDENVELOPE:
                rmb = shareInfoConf.get('rmb', 0)

            shareInfoNew = {"matchShareType": matchShareType, "shareNum": shareNum if shareNum else 0,
                "shareTotalNum": shareTotalNum if shareTotalNum else 0,
                "get": 1 if str(rewardType) == MATCH_REWARD_REDENVELOPE else 0, "rmb": '{0:.2f}'.format(rmb)}
            msg.setResult('shareInfoNew', shareInfoNew)
        except Exception, e:
            ftlog.error('MatchPlayerNotifierDizhu.notifyMatchOver', 'gameId=', self._room.gameId, 'userId=',
                        player.userId, 'roomId=', self._room.roomId, 'matchId=', self._room.match.matchId, 'err=',
                        e.message)
        ###########################

        record = MatchRecord.loadRecord(self._room.gameId, player.userId, self._room.match.matchId)
        if record:
            msg.setResult('mrecord',
                          {'bestRank': record.bestRank, 'bestRankDate': record.bestRankDate, 'isGroup': record.isGroup,
                           'crownCount': record.crownCount, 'playCount': record.playCount})
        else:
            from dizhu.activities.toolbox import Tool
            msg.setResult('mrecord', {'bestRank': player.rank, 'bestRankDate': Tool.datetimeToTimestamp(datetime.now()),
                                      'isGroup': 0, 'crownCount': 1 if player.rank == 1 else 0, 'playCount': 1})

        if not player.isQuit:
            router.sendToUser(msg, player.userId)

        # 混房冠军LED
        mixId = player.mixId
        if mixId:
            mixConf = MatchPlayerNotifierDizhu.getArenaMixConf(self._room.roomConf, mixId)
            if player.rank == 1 and mixConf.get('championLed'):
                clientId = sessiondata.getClientId(player.userId)
                arenaContent = dizhuhallinfo.getArenaMatchProvinceContent(player.userId,
                                                                          int(mixId) if mixId else self._room.roomId,
                                                                          clientId)
                if ftlog.is_debug():
                    ftlog.debug('MatchPlayerNotifierDizhu.notifyMatchOver', 'userId=', player.userId, 'roomId=',
                                self._room.roomId, 'mixId=', mixId, 'roomName', mixConf.get('roomName'), 'rewardShow=',
                                mixConf.get('rewardShow', rewardDesc), 'mixConf=', mixConf)
                # 冠军发送Led通知所有其他玩家
                ledtext = dizhuled._mk_match_champion_rich_text(player.userName,
                    arenaContent.get('name') if arenaContent else mixConf.get('roomName'),
                    arenaContent.get('rewardShow') if arenaContent else mixConf.get('rewardShow', rewardDesc))
                LedUtil.sendLed(ledtext, 'global')
        else:
            if player.rank == 1 and self._room.roomConf.get('championLed') and not player.isQuit:
                clientId = sessiondata.getClientId(player.userId)
                arenaContent = dizhuhallinfo.getArenaMatchProvinceContent(player.userId,
                                                                          int(mixId) if mixId else self._room.roomId,
                                                                          clientId)
                # 冠军发送Led通知所有其他玩家
                ledtext = dizhuled._mk_match_champion_rich_text(player.userName,
                    arenaContent.get('name') if arenaContent else roomName,
                    arenaContent.get('rewardShow') if arenaContent else self._room.roomConf.get('rewardShow',
                                                                                                rewardDesc))
                LedUtil.sendLed(ledtext, 'global')

        sequence = int(player.matchInst.instId.split('.')[1])
        matchutil.report_bi_game_event('MATCH_FINISH', player.userId, player.matchInst.matchId, 0, sequence, 0, 0, 0,
                                       [int(player.mixId) if player.mixId else 255], 'match_end')
    except:
        ftlog.error()

from dizhu.games.arenamatch.interfacedizhu import MatchPlayerNotifierDizhu
MatchPlayerNotifierDizhu.notifyMatchOver = notifyMatchOver
ftlog.info('dizhu/hotfix/h_2017_11_16_notifyMatchOver ok')