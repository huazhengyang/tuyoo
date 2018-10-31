# -*- coding:utf-8 -*-
'''
Created on 2017年8月24日

@author: wangyonghui
'''
from dizhu.games.mix.policies import SettlementPolicyMix
from dizhucomm.core.playmode import GameRound
import freetime.util.log as ftlog


def _calcWinloseZeroSum(self, gameResult):
    assert (gameResult.dizhuStatement)
    dizhuIndex = 0
    for index, sst in enumerate(gameResult.seatStatements):
        if sst == gameResult.dizhuStatement:
            dizhuIndex = index
    dizhuBaseScore = gameResult.gameRound.baseScores[dizhuIndex]
    nongmingDelta = []
    for index, sst in enumerate(gameResult.seatStatements):
        if sst != gameResult.dizhuStatement:
            nongminBaseScore = gameResult.gameRound.baseScores[index]
            # 本农民在所有农民输赢中所占的比例
            ratio = float(sst.seat.status.totalMulti) / gameResult.dizhuStatement.seat.status.totalMulti
            # 本农民输赢积分
            if gameResult.gameRound.result == GameRound.RESULT_NONGMIN_WIN:
                seatDelta = min(sst.final, nongminBaseScore * sst.seat.status.totalMulti,
                                int(gameResult.dizhuStatement.final * float(nongminBaseScore) * ratio / dizhuBaseScore))
            else:
                seatDelta = min(sst.final, nongminBaseScore * sst.seat.status.totalMulti,
                                int(gameResult.dizhuStatement.final * float(nongminBaseScore) * ratio / dizhuBaseScore)) * -1
            sst.deltaScore(seatDelta)
            nongmingDelta.append([seatDelta, nongminBaseScore])

            ftlog.info('SettlementPolicyMix._calcWinloseZeroSum',
                       'roundId=', gameResult.gameRound.roundId,
                       'userId=', sst.seat.userId,
                       'dizhuUserId=', gameResult.dizhuStatement.seat.userId,
                       'result=', gameResult.gameRound.result,
                       'baseScore=', gameResult.baseScores[index],
                       'totalMulti=', sst.seat.status.totalMulti,
                       'seatWinlose=', seatDelta,
                       'seatDelta=', seatDelta,
                       'gameResult.systemRecovery=', seatDelta - sst.delta,
                       'systemPaid=', sst.systemPaid,
                       'delta=', sst.delta,
                       'final=', sst.final)
            assert (gameResult.dizhuStatement.final >= 0)
    dizhuTotalDeta = 0
    for delta, baseScore in nongmingDelta:
        seatDeltaDizhu = int(delta * float(dizhuBaseScore) / baseScore)
        dizhuTotalDeta += seatDeltaDizhu
    dizhuDelta = min(gameResult.dizhuStatement.final, abs(dizhuTotalDeta))
    gameResult.dizhuStatement.deltaScore(-dizhuDelta if gameResult.gameRound.result == GameRound.RESULT_NONGMIN_WIN else dizhuDelta)

SettlementPolicyMix._calcWinloseZeroSum = _calcWinloseZeroSum
