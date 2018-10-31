# -*- coding:utf-8 -*-
'''
Created on 2017年11月09日

@author: wangjifa
'''
import copy

from dizhu.entity import dizhu_score_ranking, dizhuconf
from dizhu.entity.dizhuconf import DIZHU_GAMEID
from dizhucomm import playmodes
from dizhucomm.core import bug_fix
from hall.entity import hallconf, hallitem
from hall.entity.hallconf import HALL_GAMEID
from hall.entity.hallpopwnd import makeTodoTaskLessbuyChip
from hall.entity.hallpopwnd import makeTodoTaskLuckBuy
from dizhu.servers.util.rpc import new_table_remote, task_remote
from dizhu.servers.util.rpc import new_table_winlose
from dizhu.games.normalbase.tableproto import DizhuTableProtoNormalBase
from poker.entity.configure import gdata
from poker.protocol import router
import poker.util.timestamp as pktimestamp
from dizhucomm.entity import commconf, tablepay, emoji
import freetime.util.log as ftlog
import dizhu.entity.skillscore as skillscore
from dizhucomm.entity import treasurebox
from poker.util import strutil
from datetime import time, datetime
from poker.entity.dao import sessiondata
from freetime.entity.msg import MsgPack


def sendWinloseResMix(self, result):
    details = self.buildResultDetails(result)
    mp = self.buildWinloseRes(result, details, 1)
    # 免费场开关
    freeFeeSwitch = self.table.room.roomConf.get('freeFeeSwitch', 0)
    mp.setResult('free', freeFeeSwitch)
    for index, seat in enumerate(self.table.seats):
        isKickOutCoin = 0

        # 每次进来需要重新初始化
        realSeats = []
        seatIndexes = []
        for i, seatDetails in enumerate(details.get('seatDetails', [])):
            copyDetail = copy.copy(seatDetails)
            realSeats.append(copyDetail)
            seatIndexes.append(i)
            mp.setResult('seat%s' % (i + 1), copyDetail)
        seatIndexes.remove(index)

        if self.table.room.roomConf.get('zeroSumFlag', 0) == 1:
            currentBaseScore = result.gameRound.baseScores[index]
            for seatIndex in seatIndexes:
                otherBaseScore = result.gameRound.baseScores[seatIndex]
                realSeats[seatIndex][0] = int(float(currentBaseScore) / otherBaseScore * realSeats[seatIndex][0])
                realSeats[seatIndex][1] = int(float(currentBaseScore) / otherBaseScore * realSeats[seatIndex][1])
        else:
            # 显示以当前seat为基准做假数据
            dizhuIndex = mp.getResult('stat').get('dizhu')
            currentSeat = realSeats[index]
            windoubles = mp.getResult('windoubles')
            currentBaseScore = self.table.gameRound.baseScores[index]
            currentIsDizhu = dizhuIndex == index + 1
            dizhuwin = mp.getResult('dizhuwin')
            realDeltas = [realSeat[0] for realSeat in realSeats]
            if ftlog.is_debug():
                ftlog.debug('DizhuTableProtoMix.sendWinloseRes realDeltas=', realDeltas,
                            'userId=', seat.player.userId,
                            'mixId=', seat.player.mixConf.get('mixId'), 'index=', index)

            if len(realDeltas) == 2:
                for index2, realSeat in enumerate(realSeats):
                    if index != index2:
                        realSeat[0] = abs(currentSeat[0]) * (realSeat[0] / abs(realSeat[0]))
            else:
                if realDeltas.count(0) == 0:
                    for index2, realSeat in enumerate(realSeats):
                        if index != index2:
                            if currentIsDizhu:
                                realSeat[0] = abs(currentSeat[0] / 2) * (realSeat[0] / abs(realSeat[0]))
                            else:
                                if dizhuIndex == index2 + 1:
                                    realSeat[0] = abs(currentSeat[0] * 2) * (realSeat[0] / abs(realSeat[0]))
                                else:
                                    realSeat[0] = abs(currentSeat[0]) * (realSeat[0] / abs(realSeat[0]))

                elif realDeltas.count(0) == 1:  # 一个人托管
                    for index2, realSeat in enumerate(realSeats):
                        if index != index2:
                            if currentIsDizhu:  # 地主肯定有值
                                if realSeat[0] != 0:
                                    if dizhuwin:
                                        realSeat[0] = abs(currentSeat[0]) * (realSeat[0] / abs(realSeat[0]))
                                    else:
                                        realSeat[0] = abs(currentSeat[0] / 2) * (realSeat[0] / abs(realSeat[0]))
                            else:
                                if currentSeat[0] == 0:
                                    if dizhuIndex == index2 + 1:
                                        realSeat[0] = abs(windoubles * 2 * currentBaseScore) * \
                                        (realSeat[0] / abs(realSeat[0]))
                                    else:
                                        if dizhuwin:
                                            realSeat[0] = abs(windoubles * 2 * currentBaseScore) * (
                                            realSeat[0] / abs(realSeat[0]))
                                        else:
                                            realSeat[0] = abs(windoubles * currentBaseScore) * (
                                            realSeat[0] / abs(realSeat[0]))
                                else:
                                    if dizhuIndex == index2 + 1:
                                        if dizhuwin:
                                            realSeat[0] = abs(currentSeat[0]) * 1 * (realSeat[0] / abs(realSeat[0]))
                                        else:
                                            realSeat[0] = abs(currentSeat[0]) * 2 * (realSeat[0] / abs(realSeat[0]))
                else:
                    for index2, realSeat in enumerate(realSeats):
                        if realSeat[0]:
                            realSeat[0] = abs(windoubles * 2 * currentBaseScore) * (realSeat[0] / abs(realSeat[0]))

            if ftlog.is_debug():
                fakeDeltas = []
                for i, seatDetails in enumerate(details.get('seatDetails', [])):
                    fakeDeltas.append(mp.getResult('seat%s' % (i + 1))[0])
                ftlog.debug('DizhuTableProtoMix.sendWinloseRes fakeDeltas=', fakeDeltas, 'userId=', seat.player.userId,
                            'mixId=', seat.player.mixConf.get('mixId'), 'index=', index)

        if seat.player and not seat.isGiveup:
            ssts = result.seatStatements

            # 兼容老版本
            mp.setResult('tasks', details.get('tableTasks')[index])

            # 是否达到踢出值
            isLowerKickOutCoin = True if ssts[index].final < seat.player.mixConf.get('kickOutCoin', 0) else False

            # 不踢出
            if isLowerKickOutCoin and seat.player.chip < seat.player.mixConf.get('buyinchip', 0):
                isKickOutCoin = 1

            mp.setResult('kickOutCoinTip', '')
            if isLowerKickOutCoin and seat.player.chip >= seat.player.mixConf.get('buyinchip', 0):
                mp.setResult('kickOutCoinTip', '点击继续，将自动将您\n桌面金币补充至%s。\n继续努力吧！' % seat.player.mixConf.get('buyinchip'))

            # 积分排行榜
            scoreboard = dizhu_score_ranking.fillScoreRankListInfo(self.table.roomId, ssts[index].seat.userId,
                                                                   ssts[index].delta)
            if scoreboard:
                mp.setResult('scoreboard', scoreboard)

            # 荣耀月卡金币奖励
            mp.rmResult('honorCard')
            honorCardAddChip, rate = self._fillHonorCardInfo(ssts[index].seat.userId, self.table.roomId,
                                                             ssts[index].delta, seat.player.clientId)
            if honorCardAddChip:
                mp.setResult('honorCard', rate)
                ssts[index].delta += honorCardAddChip

            # 新手任务
            mp.rmResult('newertask')
            status = task_remote.getTaskProgress(DIZHU_GAMEID, seat.userId)
            if status:
                mp.setResult('newertask', status)

            # 分享时的二维码等信息
            mp.setResult('share', commconf.getGamewinShareinfo(self.gameId, seat.player.clientId))

            # 是否达到踢出值
            mp.setResult('isKickOutCoin', 0)

            self._fillWinsTask(mp, seat)
            self._fillDailyPlayTimesWinsTask(mp, seat, index)
            self._fillLuckyGiftInfo(mp, seat, self.gameId, seat.player.mixConf.get('roomId'), freeFeeSwitch,
                                    seat.player.mixConf.get('luckeyGiftBaseLine', 1000))

            mp.rmResult('playShare')
            playShare = seat.player.playShare.getShareInfo(seat.player.mixConf, seat.player.clientId)
            if playShare:
                mp.setResult('playShare', playShare)

            if ftlog.is_debug():
                ftlog.debug('DizhuTableProtoNormal.playShare userId=', seat.player.userId, 'roomId=', self.roomId,
                            'winCount=', seat.player.playShare.winCount, 'loseCount=', seat.player.playShare.loseCount,
                            'firstChip=', seat.player.playShare.fistChip, 'lastChip=', seat.player.playShare.lastChip,
                            'deltaChip=', seat.player.playShare.deltaChip, 'maxWinDoubles=',
                            seat.player.playShare.maxWinDoubles, 'mixId=', seat.player.mixConf.get('mixId'),
                            'playShare=', playShare)

            router.sendToUser(mp, seat.userId)

        # 发送转运大礼包(弹窗) # 继续逻辑屏蔽转运礼包
        if isKickOutCoin and not seat.player.mixConf.get('continueLuckyGift', 0):
            new_table_remote.processLoseRoundOver(self.gameId, seat.player.userId, seat.player.clientId,
                                                  seat.player.mixConf.get('roomId'),
                                                  minCoin=seat.player.mixConf.get('minCoin'))


from dizhu.games.mix.tableproto import DizhuTableProtoMix
DizhuTableProtoMix.sendWinloseRes = sendWinloseResMix
ftlog.info('hotfix h_2017_11_09_sendWinloseResMix ok')

def sendWinloseRes(self, result):
    details = self.buildResultDetails(result)
    mp = self.buildWinloseRes(result, details, 1)
    # 免费场开关
    freeFeeSwitch = self.table.room.roomConf.get('freeFeeSwitch', 0)
    mp.setResult('free', freeFeeSwitch)

    for index, seat in enumerate(self.table.seats):
        isKickOutCoin = 0
        isNewGift = False
        if seat.player and not seat.isGiveup:
            # 兼容老版本
            mp.setResult('tasks', details.get('tableTasks')[index])

            ssts = result.seatStatements
            # 是否达到踢出值
            isLowerKickOutCoin = True if ssts[index].final < self.table.room.roomConf.get('kickOutCoin', 0) else False

            # 不踢出
            if isLowerKickOutCoin and seat.player.chip < self.table.room.roomConf['buyinchip']:
                isKickOutCoin = 1

            # 点击继续的提醒
            mp.rmResult('kickOutCoinTip')
            if isLowerKickOutCoin and seat.player.chip >= self.table.room.roomConf['buyinchip']:
                mp.setResult('kickOutCoinTip', details.get('kickOutCoinTip'))

            # 积分排行榜
            scoreboard = dizhu_score_ranking.fillScoreRankListInfo(self.table.roomId, ssts[index].seat.userId,
                                                                   ssts[index].delta)
            if scoreboard:
                mp.setResult('scoreboard', scoreboard)

            # 荣耀月卡金币奖励
            mp.rmResult('honorCard')
            honorCardAddChip, rate = self._fillHonorCardInfo(ssts[index].seat.userId, self.table.roomId,
                                                             ssts[index].delta, seat.player.clientId)
            if honorCardAddChip:
                mp.setResult('honorCard', rate)
                ssts[index].delta += honorCardAddChip

            # 新手任务
            mp.rmResult('newertask')
            status = task_remote.getTaskProgress(DIZHU_GAMEID, seat.userId)
            if status:
                mp.setResult('newertask', status)

            # 分享时的二维码等信息
            mp.setResult('share', commconf.getGamewinShareinfo(self.gameId, seat.player.clientId))

            # 是否达到踢出值
            mp.setResult('isKickOutCoin', 0)

            self._fillWinsTask(mp, seat)
            self._fillDailyPlayTimesWinsTask(mp, seat, index)

            # 礼包buff
            isBuyInGift = result.isChuntian or result.slam
            isNewGift = self._fillGiftBuffInfo(mp, ssts[index], seat.player, isBuyInGift)
            if not isNewGift:
                self._fillLuckyGiftInfo(mp, seat, self.gameId, self.table.room.roomId, freeFeeSwitch,
                                        self.table.room.roomConf.get('luckeyGiftBaseLine', 1000))

            mp.rmResult('playShare')
            playShare = seat.player.playShare.getShareInfo(self.table.room.roomConf, seat.player.clientId)
            if playShare:
                mp.setResult('playShare', playShare)

            if ftlog.is_debug():
                ftlog.debug('DizhuTableProtoNormal.playShare userId=', seat.player.userId, 'roomId=', self.roomId,
                            'winCount=', seat.player.playShare.winCount, 'loseCount=', seat.player.playShare.loseCount,
                            'firstChip=', seat.player.playShare.fistChip, 'lastChip=', seat.player.playShare.lastChip,
                            'deltaChip=', seat.player.playShare.deltaChip, 'maxWinDoubles=',
                            seat.player.playShare.maxWinDoubles, 'playShare=', playShare)

            router.sendToUser(mp, seat.userId)

        # 发送转运大礼包(弹窗) # 继续逻辑屏蔽转运礼包
        if not isNewGift:
            if isKickOutCoin and not self.table.runConf.continueLuckyGift:
                new_table_remote.processLoseRoundOver(self.gameId, seat.player.userId, seat.player.clientId,
                                                      self.table.room.roomId)

from dizhu.games.normal.tableproto import DizhuTableProtoNormal
DizhuTableProtoNormal.sendWinloseRes = sendWinloseRes
ftlog.info('hotfix h_2017_11_09_sendWinloseRes ok')