# -*- coding:utf-8 -*-
'''
Created on 2018年9月20日

@author: wangyonghui
'''

from dizhu.entity import dizhuconf
from dizhu.entity.dizhuconf import DIZHU_GAMEID
from dizhu.servers.util.rpc import new_table_winlose, new_table_remote
from dizhucomm.core.playmode import GameRound
from dizhucomm.core.policies import BuyinPolicy, GameResult, SettlementPolicy
from dizhucomm.entity import gameexp
from dizhucomm.playmodes.base import PunishPolicyNormal
from dizhucomm.core.exceptions import ChipNotEnoughException
import freetime.util.log as ftlog
from poker.entity.dao import gamedata


class DefaultSettlementPolicy(SettlementPolicy):
    def __init__(self):
        super(DefaultSettlementPolicy, self).__init__()
        self._punishPolicy = PunishPolicyNormal(False)
        self.settlementPolicyNormal = SettlementPolicyNormal()
        self.settlementPolicyFree = SettlementPolicyFree()

    def calcResult(self, gameRound):
        if gameRound.table.runConf.freeFeeSwitch > 0:
            return self.settlementPolicyFree.calcResult(gameRound)
        else:
            return self.settlementPolicyNormal.calcResult(gameRound)

    def settlement(self, gameResult):
        if gameResult.gameRound.table.runConf.freeFeeSwitch > 0:
            self.settlementPolicyFree.settlement(gameResult)
        else:
            self.settlementPolicyNormal.settlement(gameResult)


class DefaultBuyinPolicy(BuyinPolicy):
    def __init__(self):
        super(DefaultBuyinPolicy, self).__init__()
        self.buyinPolicyNormal = BuyinPolicyNormal()
        self.buyinPolicyFree = BuyinPolicyFree()

    def buyin(self, table, player, seat, continueBuyin):
        # 机器人
        if player.isAI:
            return
        if table.runConf.freeFeeSwitch > 0:
            self.buyinPolicyFree.buyin(table, player, seat, continueBuyin)
        else:
            self.buyinPolicyNormal.buyin(table, player, seat, continueBuyin)

    def cashin(self, table, player, seat):
        # 机器人
        if player.isAI:
            return
        if table.runConf.freeFeeSwitch > 0:
            self.buyinPolicyFree.cashin(table, player, seat)
        else:
            self.buyinPolicyNormal.cashin(table, player, seat)


class SettlementPolicyNormal(SettlementPolicy):
    def __init__(self):
        super(SettlementPolicyNormal, self).__init__()
        self._punishPolicy = PunishPolicyNormal(False)

    def calcResult(self, gameRound):
        ret = GameResult(gameRound)
        if gameRound.firstWinSeat:
            self._calcForGameOver(ret)
        else:
            self._calcForGameAbort(ret)
        return ret

    def settlement(self, gameResult):
        if gameResult.gameRound.firstWinSeat:
            self._settlementForGameOver(gameResult)
        else:
            self._settlementForGameAbort(gameResult)

    def _calcForGameAbort(self, gameResult):
        return gameResult

    def _calcForGameOver(self, gameResult):
        # 收服务费
        roomFeeConf = dizhuconf.getRoomFeeConf()
        self._calcFee(gameResult, roomFeeConf)
        # 计算输赢
        self._calcWinlose(gameResult)
        # 托管包赔
        self._punishPolicy.punish(gameResult)
        # 抽成
        self._calcWinnerTax(gameResult, roomFeeConf)
        return gameResult

    def _calcFee(self, result, roomFeeConf):
        basicRate = roomFeeConf.get('basic', 1)
        highMulti = roomFeeConf.get('high_multi', 32)

        for sst in result.seatStatements:
            sst.fee = result.gameRound.table.runConf.roomFee
            if sst.seat.status.totalMulti > highMulti and sst.isWin:
                sst.fixedFee += result.gameRound.table.runConf.fixedRoomFee
            sst.fee = min(abs(int(sst.fee * basicRate)), sst.final)
            sst.final -= sst.fee
            sst.fixedFee = min(sst.fixedFee, sst.final)
            sst.final -= sst.fixedFee
            if ftlog.is_debug():
                ftlog.debug('SettlementPolicyNormal._calcFee',
                            'userId=', sst.seat.player.userId,
                            'roomId=', result.gameRound.table.roomId,
                            'roomFee=', result.gameRound.table.runConf.roomFee,
                            'fixedRoomFee=', result.gameRound.table.runConf.fixedRoomFee,
                            'fee=', sst.fee,
                            'fixedFee=', sst.fixedFee,
                            'sst.final=', sst.final,
                            'sst.fee=', sst.fee,
                            'sst.feeMulti=', sst.feeMulti
                            )

    def _calcWinlose(self, result):
        assert (result.dizhuStatement)
        dizhuWinloseLimit = min(result.dizhuStatement.final, result.dizhuStatement.seat.status.totalMulti * result.baseScore)
        winCoinLimit = result.gameRound.table.runConf.winCoinLimit
        if winCoinLimit > 0:
            dizhuWinloseLimit = min(dizhuWinloseLimit, winCoinLimit)
        for sst in result.seatStatements:
            if sst != result.dizhuStatement:
                # 本农民在所有农民输赢中所占的比例
                ratio = float(sst.seat.status.totalMulti) / result.dizhuStatement.seat.status.totalMulti
                # 地主输赢本农民的积分
                dizhuWinloseMe = int(dizhuWinloseLimit * ratio)
                # 本农民输赢积分
                seatWinlose = min(sst.final, dizhuWinloseMe)
                seatDelta = seatWinlose if result.gameRound.result == GameRound.RESULT_NONGMIN_WIN else -seatWinlose
                if ftlog.is_debug():
                    ftlog.debug('SettlementPolicyNormal._calcWinlose',
                                'roundId=', result.gameRound.roundId,
                                'seat=', (sst.seat.userId, sst.seat.seatId),
                                'ratio=', ratio,
                                'seatFinal=', sst.final,
                                'seatDelta=', seatDelta,
                                'dizhuWinloseMe=', dizhuWinloseMe,
                                'seatWinlose=', seatWinlose)
                sst.delta = seatDelta
                sst.final += seatDelta
                result.dizhuStatement.delta -= seatDelta
                result.dizhuStatement.final -= seatDelta
                assert (result.dizhuStatement.final >= 0)

    def _calcWinnerTax(self, result, roomFeeConf):
        winnerTaxRate = roomFeeConf.get('winner_chip', 0)
        if winnerTaxRate > 0:
            for sst in result.seatStatements:
                if sst.delta > 0:
                    sst.winnerTax = min(sst.delta, int(sst.delta * winnerTaxRate))
                    if sst.winnerTax > 0:
                        sst.final -= sst.winnerTax

    def _settlementForGameAbort(self, gameResult):
        for sst in gameResult.seatStatements:
            # 机器人
            if sst.seat.player.isAI:
                continue
            sst.seat.player.score = sst.final
            new_table_remote._setLastTableChip(sst.seat.player.userId, True, sst.final)

    def _settlementForGameOver(self, gameResult):
        roomId = gameResult.gameRound.table.roomId
        tableId = gameResult.gameRound.table.tableId
        roundNum = gameResult.gameRound.roundNum
        winUserId = gameResult.gameRound.firstWinSeat.userId
        bombCount = gameResult.gameRound.bombCount
        chuntian = 2 if gameResult.gameRound.isChuntian else 1
        playMode = gameResult.gameRound.table.playMode.name
        topCardList = gameResult.gameRound.topValidCards.cards

        for sst in gameResult.seatStatements:
            # 机器人
            if sst.seat.player.isAI:
                continue
            # 服务费
            userId = sst.seat.userId
            clientId = sst.seat.player.clientId
            sst.seat.player.score = sst.final
            finalTableChip, finalChip, expInfo, skillScoreInfo \
                = new_table_winlose.doTableWinloseUT(userId, roomId, tableId, roundNum, clientId,
                                                     sst.isWin, sst.winStreak, winUserId, sst == gameResult.dizhuStatement,
                                                     sst.fee, sst.cardNoteFee, sst.delta, sst.systemPaid, sst.winnerTax,
                                                     gameResult.gameRound.baseScore, sst.seat.status.totalMulti,
                                                     bombCount, chuntian, gameResult.slam, playMode, topCardList, fixedFee=sst.fixedFee)
            ftlog.info('SettlementPolicyNormal._settlementForGameOver',
                       'roomId=', gameResult.gameRound.table.roomId,
                       'tableId=', gameResult.gameRound.table.tableId,
                       'roundId=', gameResult.gameRound.roundId,
                       'cardNoteFee=', sst.cardNoteFee,
                       'fee=', sst.fee,
                       'delta=', sst.delta,
                       'winnerTax=', sst.winnerTax,
                       'baseScore=', gameResult.gameRound.baseScore,
                       'totalMulti=', sst.seat.status.totalMulti,
                       'sstFinal=', sst.final,
                       'userId=', userId,
                       'fixedFee=', sst.fixedFee,
                       'finalTableChip=', finalTableChip,
                       'finalChip=', finalChip)
            sst.skillscoreInfo = skillScoreInfo
            sst.seat.player.chip = finalChip
            sst.seat.player.score = sst.final = finalTableChip
            explevel, title = gameexp.getLevelInfo(DIZHU_GAMEID, expInfo[0])
            nextExp = gameexp.getNextLevelExp(DIZHU_GAMEID, explevel)
            sst.expInfo = [explevel, expInfo[0], expInfo[1], nextExp, title]
            pt = sst.seat.player.datas.get('plays', 0)
            sst.seat.player.datas['plays'] = pt + 1
            if sst.isWin:
                wt = sst.seat.player.datas.get('wins', 0)
                sst.seat.player.datas['wins'] = wt + 1


class BuyinPolicyNormal(BuyinPolicy):
    def buyin(self, table, player, seat, continueBuyin):
        roomBuyInChip = table.room.roomConf.get('buyinchip', 0)
        roomMinCoin = table.room.roomConf.get('minCoin', 0)
        kickOutCoin = table.room.roomConf.get('kickOutCoin', 0)
        playerChip = player.chip

        minCoin = roomMinCoin
        # 兼容老客户端
        last_table_chip = player.score if player.score else new_table_remote._getLastTableChip(player.userId, True)
        # 根据 continueBuyin 判断 buyinChip
        buyinChip = roomBuyInChip
        if continueBuyin:
            minCoin = kickOutCoin
            buyInToRoomBuyIn = table.room.roomConf.get('continueFillUp', 0)
            if buyInToRoomBuyIn:
                # 牌局结束点击继续按钮补满金币开关,和传入的continueBuyin不同意义
                buyinChip = max(roomBuyInChip, last_table_chip)
            elif last_table_chip >= kickOutCoin:
                buyinChip = last_table_chip
            elif last_table_chip < kickOutCoin and playerChip >= minCoin:
                buyinChip = roomBuyInChip
            else:
                # last_table_chip 小于踢出值并且playerChip小于带入值，raise 错误
                ftlog.warn('policies.BuyinPolicyNormal',
                           'userId=', player.userId,
                           'roomId=', table.roomId,
                           'clientId=', player.clientId,
                           'last_table_chip=', last_table_chip,
                           'playerScore=', player.score,
                           'playerChip=', playerChip,
                           'kickOutCoin=', kickOutCoin,
                           'roomMinCoin=', roomMinCoin,
                           'roomBuyInChip=', roomBuyInChip,
                           'continueBuyin=', continueBuyin)
                raise ChipNotEnoughException('金币不足， 踢出房间')

        if ftlog.is_debug():
            ftlog.debug('policies.BuyinPolicyNormal',
                        'userId=', player.userId,
                        'roomId=', table.roomId,
                        'clientId=', player.clientId,
                        'last_table_chip=', last_table_chip,
                        'playerScore=', player.score,
                        'buyinChip=', buyinChip,
                        'continueBuyin=', continueBuyin)

        tchip, chip, _ = new_table_remote.buyin(player.userId,
                                                table.roomId,
                                                player.clientId,
                                                table.tableId,
                                                buyinChip,
                                                minCoin,
                                                continueBuyin)
        player.score = tchip
        player.chip = chip
        player.datas['chip'] = chip
        player.datas['buyinMark'] = 1
        player.datas['buyinChip'] = tchip

        if continueBuyin and (buyinChip == roomBuyInChip or last_table_chip == roomBuyInChip):
            player.datas['buyinTip'] = ''
        else:
            player.datas['buyinTip'] = self._buildBuyinTip(roomBuyInChip, tchip, chip, continueBuyin)

    def cashin(self, table, player, seat):
        final = new_table_remote.cashin(player.userId, table.roomId, player.clientId, table.tableId, player.score)
        player.chip = final
        if ftlog.is_debug():
            ftlog.debug('BuyinPolicyNormal.cashin',
                        'userId=', player.userId,
                        'roomId=', table.roomId,
                        'tableId=', table.tableId,
                        'playerScore=', player.score,
                        'playerChip=', player.chip)

    def _buildBuyinTip(self, roomBuyInChip, buyinChip, chip, continueBuyin):
        buyinConf = dizhuconf.getBuyInConf()
        if buyinChip == roomBuyInChip:
            if continueBuyin:
                return buyinConf.get('tip_auto', '')
            else:
                return buyinConf.get('tip', '').format(BUYIN_CHIP=buyinChip)
        else:
            if chip <= 0:
                if continueBuyin:
                    return buyinConf.get('tip_auto_all_next', '')
                else:
                    return buyinConf.get('tip_auto_all', '')
        return ''


class SettlementPolicyFree(SettlementPolicy):
    def __init__(self):
        super(SettlementPolicyFree, self).__init__()
        self._punishPolicy = PunishPolicyNormal(True)

    def calcResult(self, gameRound):
        ret = GameResult(gameRound)
        if gameRound.firstWinSeat:
            self._calcForGameOver(ret)
        else:
            self._calcForGameAbort(ret)
        return ret

    def settlement(self, gameResult):
        if gameResult.gameRound.firstWinSeat:
            self._settlementForGameOver(gameResult)
        else:
            self._settlementForGameAbort(gameResult)

    def _calcForGameAbort(self, gameResult):
        return gameResult

    def _calcForGameOver(self, gameResult):
        # 收服务费
        if gameResult.gameRound.table.runConf.roomFee > 0:
            self._calcFee(gameResult)
        # 计算输赢
        self._calcWinloseFree(gameResult)
        # 托管包赔
        self._punishPolicy.punish(gameResult)
        # 抽成
        self._calcWinnerTax(gameResult)
        return gameResult

    def _calcFee(self, gameResult):
        roomFeeConf = dizhuconf.getRoomFeeConf()
        basicRate = roomFeeConf.get('basic', 1)
        highMulti = roomFeeConf.get('high_multi', 32)

        for sst in gameResult.seatStatements:
            sst.fee = gameResult.gameRound.table.runConf.roomFee
            if sst.seat.status.totalMulti > highMulti and sst.isWin:
                sst.fixedFee += gameResult.gameRound.table.runConf.fixedRoomFee
            sst.fee = min(abs(int(sst.fee * basicRate)), sst.final)
            sst.final -= sst.fee
            sst.fixedFee = min(sst.fixedFee, sst.final)
            sst.final -= sst.fixedFee

            if ftlog.is_debug():
                ftlog.debug('SettlementPolicyFree._calcFee',
                            'userId=', sst.seat.player.userId,
                            'roomId=', gameResult.gameRound.table.roomId,
                            'roomFee=', gameResult.gameRound.table.runConf.roomFee,
                            'fixedRoomFee=', gameResult.gameRound.table.runConf.fixedRoomFee,
                            'fixedFee=', sst.fixedFee,
                            'sst.final=', sst.final,
                            'sst.fee=', sst.fee,
                            'sst.feeMulti=', sst.feeMulti)

    def _calcWinloseFree(self, gameResult):
        assert (gameResult.dizhuStatement)
        chipControlLine = gameResult.gameRound.table.runConf.chipControlLine
        winCoinLimit = gameResult.gameRound.table.runConf.winCoinLimit
        for sst in gameResult.seatStatements:
            # 地主输赢本农民的积分
            seatWinlose = sst.seat.status.totalMulti * gameResult.baseScore
            seatWinlose = min(seatWinlose, winCoinLimit) if winCoinLimit > 0 else seatWinlose
            # 农民\地主输赢积分
            seatDelta = seatWinlose if gameResult.gameRound.result == GameRound.RESULT_NONGMIN_WIN else -seatWinlose
            if sst == gameResult.dizhuStatement:
                seatDelta = seatWinlose if gameResult.gameRound.result == GameRound.RESULT_DIZHU_WIN else -seatWinlose
            # 小于 目标金币值 赢牌奖励有上限
            if chipControlLine > 0 and sst.final < chipControlLine:
                seatDelta = min(seatDelta, chipControlLine)

            sst.deltaScore(seatDelta)
            if sst.final < 0:
                gameResult.systemRecovery += sst.final
                sst.systemPaid -= sst.final
                sst.deltaScore(-sst.final)

            ftlog.info('SettlementPolicyFree._calcWinlose',
                       'roundId=', gameResult.gameRound.roundId,
                       'userId=', sst.seat.userId,
                       'dizhuUserId=', gameResult.dizhuStatement.seat.userId,
                       'result=', (type(gameResult.gameRound.result), gameResult.gameRound.result),
                       'baseScore=', gameResult.baseScore,
                       'totalMulti=', sst.seat.status.totalMulti,
                       'seatWinlose=', (type(seatWinlose), seatWinlose),
                       'seatDelta=', seatDelta,
                       'gameResult.systemRecovery=', seatDelta - sst.delta,
                       'systemPaid=', sst.systemPaid,
                       'delta=', sst.delta,
                       'final=', sst.final)

    def _calcWinnerTax(self, result):
        winnerTaxRate = result.gameRound.table.runConf.winnerTaxMulti
        if winnerTaxRate > 0:
            for sst in result.seatStatements:
                if sst.delta > 0:
                    sst.winnerTax = min(sst.delta, int(sst.delta * winnerTaxRate))
                    if sst.winnerTax > 0:
                        sst.final -= sst.winnerTax

    def _settlementForGameAbort(self, gameResult):
        for sst in gameResult.seatStatements:
            # 机器人
            if sst.seat.player.isAI:
                continue
            sst.seat.player.score = sst.final
            new_table_remote._setLastTableChip(sst.seat.player.userId, True, sst.final)

    def _settlementForGameOver(self, gameResult):
        roomId = gameResult.gameRound.table.roomId
        tableId = gameResult.gameRound.table.tableId
        roundNum = gameResult.gameRound.roundNum
        winUserId = gameResult.gameRound.firstWinSeat.userId
        bombCount = gameResult.gameRound.bombCount
        chuntian = 2 if gameResult.gameRound.isChuntian else 1
        playMode = gameResult.gameRound.table.playMode.name
        topCardList = gameResult.gameRound.topValidCards.cards

        outCardTimes = []
        for sst in gameResult.seatStatements:
            seatStatus = sst.seat.status
            outCardTimes.append(seatStatus.outCardTimes)
        maxOutCardTimes = max(outCardTimes)

        for sst in gameResult.seatStatements:
            # 机器人
            if sst.seat.player.isAI:
                continue
            # 服务费
            userId = sst.seat.userId
            clientId = sst.seat.player.clientId
            sst.seat.player.score = sst.final

            assist = 0
            validMaxOutCard = 0
            seatStatus = sst.seat.status
            if sst != gameResult.dizhuStatement and len(seatStatus.cards) != 0 and sst.isWin:
                assist = 1
            if seatStatus.outCardTimes == maxOutCardTimes and sst.isWin:
                validMaxOutCard = 1

            finalTableChip, finalChip, expInfo, skillScoreInfo \
                = new_table_winlose.doTableWinloseUT(userId, roomId, tableId, roundNum, clientId,
                                                     sst.isWin, sst.winStreak, winUserId, sst == gameResult.dizhuStatement,
                                                     sst.fee, sst.cardNoteFee, sst.delta, sst.systemPaid, sst.winnerTax,
                                                     gameResult.gameRound.baseScore, sst.seat.status.totalMulti,
                                                     bombCount, chuntian, gameResult.slam, playMode, topCardList, fixedFee=sst.fixedFee,
                                                     assist=assist, outCardSeconds=seatStatus.outCardSeconds, validMaxOutCard=validMaxOutCard)
            ftlog.info('SettlementPolicyFree._settlementForGameOver',
                       'roomId=', gameResult.gameRound.table.roomId,
                       'tableId=', gameResult.gameRound.table.tableId,
                       'roundId=', gameResult.gameRound.roundId,
                       'resultWinLose=', gameResult.gameRound.result,
                       'cardNoteFee=', sst.cardNoteFee,
                       'fee=', sst.fee,
                       'delta=', sst.delta,
                       'winnerTax=', sst.winnerTax,
                       'baseScore=', gameResult.gameRound.baseScore,
                       'totalMulti=', sst.seat.status.totalMulti,
                       'sstFinal=', sst.final,
                       'systemPaid=', sst.systemPaid,
                       'userId=', userId,
                       'winStreak=', gamedata.getGameAttrInt(sst.seat.player.userId, DIZHU_GAMEID, 'winstreak'),
                       'finalTableChip=', finalTableChip,
                       'fixedFee=', sst.fixedFee,
                       'finalChip=', finalChip)
            sst.skillscoreInfo = skillScoreInfo
            sst.seat.player.chip = finalChip
            sst.seat.player.score = sst.final = finalTableChip
            explevel, title = gameexp.getLevelInfo(DIZHU_GAMEID, expInfo[0])
            nextExp = gameexp.getNextLevelExp(DIZHU_GAMEID, explevel)
            sst.expInfo = [explevel, expInfo[0], expInfo[1], nextExp, title]
            pt = sst.seat.player.datas.get('plays', 0)
            sst.seat.player.datas['plays'] = pt + 1
            sst.winStreak = gamedata.getGameAttrInt(sst.seat.player.userId, DIZHU_GAMEID, 'winstreak')
            if sst.isWin:
                wt = sst.seat.player.datas.get('wins', 0)
                sst.seat.player.datas['wins'] = wt + 1


class BuyinPolicyFree(BuyinPolicy):
    def buyin(self, table, player, seat, continueBuyin):
        roomBuyInChip = table.room.roomConf.get('buyinchip', 0)
        roomMinCoin = table.room.roomConf.get('minCoin', 0)
        # 兼容老客户端
        last_table_chip = player.score if player.score else new_table_remote._getLastTableChip(player.userId, True)
        # 根据 continueBuyin 判断 buyinChip
        buyinChip = roomBuyInChip
        if continueBuyin:
            buyInToRoomBuyIn = table.room.roomConf.get('continueFillUp', 0)
            # 牌局结束点击继续按钮补满金币开关,和传入的continueBuyin不同意义
            buyinChip = max(roomBuyInChip, last_table_chip) if buyInToRoomBuyIn else last_table_chip

        if ftlog.is_debug():
            ftlog.debug('policies.BuyinPolicyFree',
                        'userId=', player.userId,
                        'roomId=', table.roomId,
                        'clientId=', player.clientId,
                        'last_table_chip=', last_table_chip,
                        'playerScore=', player.score,
                        'buyinChip=', buyinChip,
                        'continueBuyin=', continueBuyin)

        tchip, chip, _ = new_table_remote.buyin(player.userId,
                                                table.roomId,
                                                player.clientId,
                                                table.tableId,
                                                buyinChip,
                                                roomMinCoin,
                                                continueBuyin)
        player.score = tchip
        player.chip = chip
        player.datas['chip'] = chip
        player.datas['buyinMark'] = 1
        player.datas['buyinChip'] = tchip

        if continueBuyin and (buyinChip == roomBuyInChip or last_table_chip == roomBuyInChip):
            # 继续时 频繁带入 或 桌面金币等于带入金币时 屏蔽tips
            player.datas['buyinTip'] = ''
        else:
            player.datas['buyinTip'] = self._buildBuyinTip(roomBuyInChip, tchip, chip, continueBuyin)

    def cashin(self, table, player, seat):
        final = new_table_remote.cashin(player.userId, table.roomId, player.clientId, table.tableId, player.score)
        player.chip = final
        if ftlog.is_debug():
            ftlog.debug('BuyinPolicyFree.cashin',
                        'userId=', player.userId,
                        'roomId=', table.roomId,
                        'tableId=', table.tableId,
                        'playerScore=', player.score,
                        'playerChip=', player.chip)

    def _buildBuyinTip(self, roomBuyInChip, buyinChip, chip, continueBuyin):
        buyinConf = dizhuconf.getBuyInConf()
        if buyinChip == roomBuyInChip:
            if continueBuyin:
                return buyinConf.get('tip_auto', '')
            else:
                return buyinConf.get('tip', '').format(BUYIN_CHIP=buyinChip)
        else:
            if chip <= 0:
                if continueBuyin:
                    return buyinConf.get('tip_auto_all_next', '')
                else:
                    return buyinConf.get('tip_auto_all', '')
        return ''
