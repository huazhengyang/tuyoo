# -*- coding:utf-8 -*-
'''
Created on 2017年7月7日

@author: wangyonghui
'''
from dizhu.entity import dizhuconf
from dizhu.games.mix.policies import SettlementPolicyMix
from dizhu.servers.util.rpc import new_table_winlose
from dizhu.servers.util.rpc.new_table_winlose import buildSettlementDeltaItems, _caleSkillScoreByUser, _settlement, _reportRoomDelta, _publishWinLoseEvent, \
    _calRankInfoData
from dizhucomm.core.playmode import GameRound
import freetime.util.log as ftlog
from dizhu.entity.dizhuconf import DIZHU_GAMEID
from dizhu.games import cardrules
from dizhucomm.entity import treasurebox
from dizhucomm.servers.util.rpc import comm_table_remote
from poker.entity.dao import gamedata, userchip
from poker.util import strutil


def _calcWinlose(self, gameResult):
    assert (gameResult.dizhuStatement)
    for index, sst in enumerate(gameResult.seatStatements):
        # 地主输赢本农民的积分
        seatWinlose = sst.seat.status.totalMulti * gameResult.baseScores[index]
        # 农民\地主输赢积分
        seatDelta = seatWinlose if gameResult.gameRound.result == GameRound.RESULT_NONGMIN_WIN else -seatWinlose
        if sst == gameResult.dizhuStatement:
            seatDelta = seatWinlose if gameResult.gameRound.result == GameRound.RESULT_DIZHU_WIN else -seatWinlose

        if seatDelta >= 0:
            seatDelta = min(sst.final, seatDelta)
        else:
            seatDelta = min(abs(sst.final), abs(seatDelta)) * -1

        sst.deltaScore(seatDelta)
        gameResult.systemRecovery += seatDelta
        sst.systemPaid += seatDelta

        ftlog.info('SettlementPolicyMix._calcWinlose',
                   'roundId=', gameResult.gameRound.roundId,
                   'userId=', sst.seat.userId,
                   'dizhuUserId=', gameResult.dizhuStatement.seat.userId,
                   'result=', (type(gameResult.gameRound.result), gameResult.gameRound.result),
                   'baseScore=', gameResult.baseScores[index],
                   'totalMulti=', sst.seat.status.totalMulti,
                   'seatWinlose=', (type(seatWinlose), seatWinlose),
                   'seatDelta=', seatDelta,
                   'gameResult.systemRecovery=', seatDelta - sst.delta,
                   'systemPaid=', sst.systemPaid,
                   'delta=', sst.delta,
                   'final=', sst.final)

def _calcForGameOver(self, gameResult):
    # 计算输赢
    self._calcWinlose(gameResult)
    # 收服务费
    roomFeeConf = dizhuconf.getRoomFeeConf()
    self._calcFee(gameResult, roomFeeConf)
    # 托管包赔
    self._punishPolicy.punish(gameResult)
    # 积分排行
    self._calcRankScore(gameResult)
    # 抽成
    self._calcWinnerTax(gameResult)
    return gameResult

SettlementPolicyMix._calcForGameOver = _calcForGameOver
SettlementPolicyMix._calcWinlose = _calcWinlose



def _doTableWinloseUT(userId, roomId, tableId, roundNum, clientId,
                      isWin, winStreak, winUserId, isDizhu,
                      fee, cardNoteFee, winlose, systemPaid, winnerTax,
                      baseScore, winDoubles, bomb, chuntian,
                      winslam, playMode, topCardList, **kwargs):
    bigRoomId = strutil.getBigRoomIdFromInstanceRoomId(roomId)
    treasurebox.updateTreasureBoxWin(DIZHU_GAMEID, userId, kwargs.get('mixConfRoomId') or bigRoomId)
    exp, deltaExp, _winrate = comm_table_remote.checkSetMedal(DIZHU_GAMEID, userId, baseScore, False, winlose)
    deltaItems = buildSettlementDeltaItems(kwargs.get('mixConfRoomId') or roomId, fee, cardNoteFee, winlose, winnerTax)
    skillScoreInfo = _caleSkillScoreByUser(userId, isWin, winStreak, isDizhu, kwargs.get('mixConfRoomId') or bigRoomId, winDoubles)
    skillLevelUp = skillScoreInfo.get('isLevelUp', False)

    _reportRoomDelta(userId, roomId, bigRoomId, clientId, systemPaid)
    finalTableChip = _settlement(userId, kwargs.get('mixConfRoomId') or roomId, tableId, roundNum, clientId, deltaItems)

    # 纪录连胜
    if isWin:
        gamedata.incrGameAttr(userId, DIZHU_GAMEID, 'winstreak', 1)
    else:
        gamedata.setGameAttr(userId, DIZHU_GAMEID, 'winstreak', 0)
    if ftlog.is_debug():
        winstreaklog = gamedata.getGameAttr(userId, DIZHU_GAMEID, 'winstreak')
        ftlog.debug('_doTableWinloseUT winstreak=', winstreaklog,
                    'UserID=', userId,
                    'roomId=', roomId,
                    'tableId=', tableId,
                    'isWin=', isWin)

    # 广播用户结算事件
    card = cardrules.CARD_RULE_DICT[playMode]
    topValidCard = card.validateCards(topCardList, None)
    finalUserChip = userchip.getChip(userId)
    _publishWinLoseEvent(roomId, tableId, userId, roundNum, isWin, isDizhu, winUserId,
                         winlose, finalTableChip, winDoubles, bomb, chuntian,
                         winslam, clientId, topValidCard, skillLevelUp, **kwargs)
    # 更新排名相关数据
    _calRankInfoData(userId, winlose, winslam, winDoubles)

    return finalTableChip, finalUserChip, [exp, deltaExp], skillScoreInfo

new_table_winlose._doTableWinloseUT = _doTableWinloseUT
