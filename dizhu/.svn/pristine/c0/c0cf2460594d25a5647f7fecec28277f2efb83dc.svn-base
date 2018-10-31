# -*- coding:utf-8 -*-
'''
Created on 2017年2月20日

@author: tuyoo
'''
from dizhucomm.core.policies import SettlementPolicy, GameResult, BuyinPolicy
from dizhucomm.playmodes.base import PunishPolicyNormal
from dizhucomm.core.playmode import GameRound
import freetime.util.log as ftlog

class SettlementPolicyFriendTable(SettlementPolicy):
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
        assert(result.dizhuStatement)
        for sst in result.seatStatements:
            if sst != result.dizhuStatement:
                # 地主输赢本农民的积分
                seatWinlose = sst.seat.status.totalMulti * result.baseScore
                ftlog.debug('SettlementPolicyFriendTable._calcWinlose',
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
        for sst in result.seatStatements:
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
        if ftlog.is_debug():
            ftlog.debug('SettlementPolicyFriendTable._settlement',
                        'infos=', [(sst.seat.userId, sst.seat.player.score, sst.delta) for sst in result.seatStatements])

    def _settlementForAbort(self, result):
        pass


class BuyinPolicyFriend(BuyinPolicy):
    def buyin(self, table, player, seat, continueBuyin):
        pass
    
    def cashin(self, table, player, seat):
        pass


