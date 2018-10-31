# -*- coding:utf-8 -*-
'''
Created on 2018年9月26日

@author: wangyonghui
'''
import random

from dizhu.servers.util.rpc import user_segment_remote
from dizhucomm.core.playmode import GameRound
from dizhucomm.core.policies import GameResult, SettlementPolicy, BuyinPolicy
from dizhucomm.playmodes.base import PunishPolicyNormal
import freetime.util.log as ftlog


class SettlementPolicySegment(SettlementPolicy):
    def __init__(self):
        self._punishPolicy = PunishPolicyNormal(True)

    def calcResult(self, gameRound):
        ret = GameResult(gameRound)
        if gameRound.firstWinSeat:
            self._forGameOver(ret)
        else:
            self._forGameAbort(ret)
        return ret

    def settlement(self, gameResult):
        gameRound = gameResult.gameRound
        if gameRound.firstWinSeat:
            return self._settlementForOver(gameResult)
        return self._settlementForAbort(gameResult)

    def _calcWinlose(self, result):
        assert result.dizhuStatement
        for sst in result.seatStatements:
            if sst != result.dizhuStatement:
                # 地主输赢本农民的积分
                seatWinlose = sst.seat.status.totalMulti * result.baseScore
                ftlog.debug('SettlementPolicyFSegment._calcWinlose',
                            'roundId=', result.gameRound.roundId,
                            'userId=', sst.seat.userId,
                            'result=', (type(result.gameRound.result), result.gameRound.result),
                            'seatWinlose=', (type(seatWinlose), seatWinlose))
                # 本农民输赢积分
                seatDelta = seatWinlose if result.gameRound.result == GameRound.RESULT_NONGMIN_WIN else -seatWinlose
                sst.delta = seatDelta
                sst.final += seatDelta
                result.dizhuStatement.delta -= seatDelta
                result.dizhuStatement.final -= seatDelta

    def _forGameAbort(self, gameResult):
        return gameResult

    def _forGameOver(self, gameResult):
        # 收服务费
        # 计算输赢
        self._calcWinlose(gameResult)
        # 托管包赔
        self._punishPolicy.punish(gameResult)
        return gameResult

    def _settlementForOver(self, result):
        roomId = result.gameRound.table.roomId
        tableId = result.gameRound.table.tableId
        winUserId = result.gameRound.firstWinSeat.userId
        bombCount = result.gameRound.bombCount
        chuntian = 2 if result.gameRound.isChuntian else 1
        topCardList = result.gameRound.topValidCards.cards

        punishNM = None
        outCardTimes = []
        for sst in result.seatStatements:
            if sst != result.dizhuStatement and sst.isPunish:
                punishNM = sst
            seatStatus = sst.seat.status
            outCardTimes.append(seatStatus.outCardTimes)
        maxOutCardTimes = max(outCardTimes)
        
        punishStates = []
        for sst in result.seatStatements:
            # 机器人
            if sst.seat.player.isAI:
                punishStates.append(0)
                winloseInfo = {

                }
                rewardInfo = winloseInfo.get('tableRewards')
                segmentInfo = winloseInfo.get('segmentInfo', {})
                recoverInfo = winloseInfo.get('recoverConsume')
                winStreakRewardInfo = winloseInfo.get('winStreakRewards')
                treasureChestInfo = winloseInfo.get('treasureChest')

                sst.segmentInfo = segmentInfo
                sst.rewardInfo = rewardInfo
                sst.recoverInfo = recoverInfo
                sst.winStreakRewardInfo = winStreakRewardInfo
                sst.treasureChestInfo = treasureChestInfo

                sst.seat.player.segment = segmentInfo.get('segment', random.randint(1, 3))
                sst.seat.player.currentStar = segmentInfo.get('currentStar', 1)
                sst.seat.player._datas.update({
                    'segment': sst.seat.player.segment,
                    'currentStar': sst.seat.player.currentStar
                })
                continue
            player = sst.seat.player
            sst.skillscoreInfo = dict(player.getData('skillScoreInfo', {}))
            sst.skillscoreInfo['addScore'] = 0
            sst.winStreak = 0
            sst.expInfo = [
                player.getData('slevel', 0),
                player.getData('exp', 0),
                0,
                player.getData('nextexp', 0),
                player.getData('title', '')
            ]
            sst.seat.player.score = sst.final
            
            punishState = 0
            if sst.isPunish:
                punishState = 1
            elif punishNM and sst != punishNM and sst != result.dizhuStatement:
                punishState = 2

            punishStates.append(punishState)

            leadWin = 0
            assist = 0
            validMaxOutCard = 0

            seatStatus = sst.seat.status
            if sst != result.dizhuStatement and len(seatStatus.cards) == 0:
                leadWin = 1
            if sst != result.dizhuStatement and len(seatStatus.cards) != 0 and sst.isWin:
                assist = 1
            if seatStatus.outCardTimes == maxOutCardTimes and sst.isWin:
                validMaxOutCard = 1

            if ftlog.is_debug():
                ftlog.debug('_settlementForOver userId=', player.userId,
                            'assist', assist,
                            'validMaxOutCard', validMaxOutCard)
            winloseInfo = user_segment_remote.processSegmentTableWinlose(roomId, tableId, player.userId, sst.isWin, sst == result.dizhuStatement, winUserId,
                         sst.delta, 0, sst.seat.status.totalMulti, bombCount, chuntian, result.slam, topCardList,
                         result.gameRound.baseScore, punishState, seatStatus.outCardSeconds, leadWin, assist=assist,
                                                                         validMaxOutCard=validMaxOutCard)

            rewardInfo = winloseInfo.get('tableRewards')
            segmentInfo = winloseInfo.get('segmentInfo')
            recoverInfo = winloseInfo.get('recoverConsume')
            winStreakRewardInfo = winloseInfo.get('winStreakRewards')
            treasureChestInfo = winloseInfo.get('treasureChest')

            sst.segmentInfo = segmentInfo
            sst.rewardInfo = rewardInfo
            sst.recoverInfo = recoverInfo
            sst.winStreakRewardInfo = winStreakRewardInfo
            sst.treasureChestInfo = treasureChestInfo

            sst.seat.player.segment = segmentInfo.get('segment')
            sst.seat.player.currentStar = segmentInfo.get('currentStar')
            sst.seat.player.updateSegmentDatas()
            
        if ftlog.is_debug():
            ftlog.debug('SettlementPolicySegment._settlement',
                        'punishNM=', punishNM.seat.userId if punishNM else None,
                        'punishState=', punishStates,
                        'infos=', [(sst.seat.userId, sst.seat.player.score, sst.delta, sst.rewardInfo, sst.segmentInfo, sst.isPunish) for sst in result.seatStatements])

    def _settlementForAbort(self, result):
        pass


class BuyinPolicySegment(BuyinPolicy):
    def buyin(self, table, player, seat, continueBuyin):
        pass

    def cashin(self, table, player, seat):
        pass
