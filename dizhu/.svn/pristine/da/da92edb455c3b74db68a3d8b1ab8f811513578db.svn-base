# -*- coding:utf-8 -*-
'''
Created on 2018年4月15日

@author: wangyonghui
'''
import time

from dizhu.servers.util.rpc import user_segment_remote, task_remote
from dizhucomm.core.events import SitdownEvent, StandupEvent
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



class AssignTableWithSegmentPolicy(object):
    '''
    已用户段位配桌策略
    '''
    def setupTable(self, table):
        table.segmentSection = None
        table.on(SitdownEvent, self._onSitdownEvent)
        table.on(StandupEvent, self._onStandupEvent)

    def canJoin(self, table, player):
        # 空桌子可以坐下
        if table.idleSeatCount == table.seatCount:
            if ftlog.is_debug():
                ftlog.debug('AssignTableWithSegmentPolicy.canJoin EmptyTable',
                            'tableId=', table.tableId,
                            'userId=', player.userId,
                            'ret=', True)
            return True

        # 获取段位区间
        if not table.segmentSection:
            if ftlog.is_debug():
                ftlog.debug('AssignTableWithSegmentPolicy.canJoin EmptySegmentSection',
                            'tableId=', table.tableId,
                            'userId=', player.userId,
                            'ret=', True)
            return True

        # 玩家段位在该桌子的段位区间内
        segment = player.segment
        if segment in table.segmentSection:
            if ftlog.is_debug():
                ftlog.debug('AssignTableWithSegmentPolicy.canJoin InTableSegmentSection',
                            'tableId=', table.tableId,
                            'userId=', player.userId,
                            'segmentSection=', table.segmentSection,
                            'ret=', True)
            return True

        # 桌子等待时间超过阈值
        timeoutThreshold = 3

        earliesPlayer = self._getEarliestSitdownPlayer(table)
        assert earliesPlayer

        nowTime = int(time.time())
        if nowTime - earliesPlayer.sitdownTime >= timeoutThreshold:
            if ftlog.is_debug():
                ftlog.debug('AssignTableWithSegmentPolicy.canJoin OverTimeout',
                            'tableId=', table.tableId,
                            'userId=', player.userId,
                            'timeoutThreshold=', timeoutThreshold,
                            'sitdownTime=', earliesPlayer.sitdownTime,
                            'nowTime=', nowTime,
                            'ret=', True)
            return True

        return False

    def _getEarliestSitdownPlayer(self, table):
        ret = None
        for seat in table.seats:
            if not seat.player:
                continue
            if ret is None or seat.player.sitdownTime < ret.sitdownTime:
                ret = seat.player
        return ret

    def _onSitdownEvent(self, evt):
        evt.player.sitdownTime = int(time.time())
        segment = evt.player.segment
        if evt.table.segmentSection is None:
            evt.table.segmentSection = [segment - 1, segment, segment + 1]
        if ftlog.is_debug():
            ftlog.debug('AssignTableWithSegmentPolicy._onSitdownEvent',
                        'seat=', (evt.player.userId, evt.player.seatId),
                        'segment=', evt.player.segment,
                        'segmentSection=', evt.table.segmentSection)

    def _onStandupEvent(self, evt):
        if ftlog.is_debug():
            ftlog.debug('AssignTableWithSegmentPolicy._onStandupEvent',
                        'seat=', (evt.player.userId, evt.seat.seatId))
        evt.player.sitdownTime = 0
        if evt.table.idleSeatCount == evt.table.seatCount:
            # 桌子没人了
            evt.table.segmentSection = None


class AssignTableWinStreakPolicy(object):
    def setupTable(self, table):
        table.winStreakSection = None
        table.on(SitdownEvent, self._onSitdownEvent)
        table.on(StandupEvent, self._onStandupEvent)

    def getPlayerWinStreak(self, table, player):
        return task_remote.doSegmentTableWinStreak(player.userId)

    def getWinStreakSection(self, table, winStreak):
        winStreakAssignTableConf = None
        try:
            winStreakAssignTableConf = self.getWinStreakAssignTableConf(table)
            if winStreakAssignTableConf:
                for section in winStreakAssignTableConf.get('sections', []):
                    if winStreak >= section[0] and winStreak <= section[1]:
                        if ftlog.is_debug():
                            ftlog.debug('AssignTableWinStreakPolicy.getWinStreakSection',
                                        'tableId=', table.tableId,
                                        'winStreak=', winStreak,
                                        'section=', section,
                                        'winStreakAssignTableConf=', winStreakAssignTableConf)
                        return section
            return None
        except:
            ftlog.error('AssignTableWinStreakPolicy.getWinStreakSection',
                        'tableId=', table.tableId,
                        'winStreakAssignTableConf=', winStreakAssignTableConf)
            return None

    def getWinStreakAssignTableConf(self, table):
        return table.runConf.datas.get('winStreakAssignTable')

    def getTimeoutThreshold(self, table):
        winStreakAssignTableConf = self.getWinStreakAssignTableConf(table)
        if not winStreakAssignTableConf:
            return 0
        return winStreakAssignTableConf.get('timeout', -1)

    def canJoin(self, table, player):
        # 空桌子可以坐下
        if table.idleSeatCount == table.seatCount:
            if ftlog.is_debug():
                ftlog.debug('AssignTableWinStreakPolicy.canJoin EmptyTable',
                            'tableId=', table.tableId,
                            'userId=', player.userId,
                            'ret=', True)
            return True

        # 获取连胜区间
        if not table.winStreakSection:
            if ftlog.is_debug():
                ftlog.debug('AssignTableWinStreakPolicy.canJoin EmptyTableWinStreakSection',
                            'tableId=', table.tableId,
                            'userId=', player.userId,
                            'ret=', True)
            return True

        # 玩家连胜在该桌子的连胜区间内
        winStreak = self.getPlayerWinStreak(table, player)
        if (winStreak >= table.winStreakSection[0]
                and winStreak <= table.winStreakSection[1]):
            if ftlog.is_debug():
                ftlog.debug('AssignTableWinStreakPolicy.canJoin InTableWinStreakSection',
                            'tableId=', table.tableId,
                            'userId=', player.userId,
                            'winStreak=', winStreak,
                            'tableWinStreakSection=', table.winStreakSection,
                            'ret=', True)
            return True

        # 桌子等待时间超过阈值 -1 表示无限大
        timeoutThreshold = self.getTimeoutThreshold(table)
        if timeoutThreshold < 0:
            if ftlog.is_debug():
                ftlog.debug('AssignTableWinStreakPolicy.canJoin InfinityTimeout',
                            'tableId=', table.tableId,
                            'userId=', player.userId,
                            'timeoutThreshold=', timeoutThreshold,
                            'ret=', False)
            return False

        earliesPlayer = self._getEarliestSitdownPlayer(table)
        assert (earliesPlayer)

        nowTime = int(time.time())
        if nowTime - earliesPlayer.sitdownTime >= timeoutThreshold:
            if ftlog.is_debug():
                ftlog.debug('AssignTableWinStreakPolicy.canJoin OverTimeout',
                            'tableId=', table.tableId,
                            'userId=', player.userId,
                            'timeoutThreshold=', timeoutThreshold,
                            'sitdownTime=', earliesPlayer.sitdownTime,
                            'nowTime=', nowTime,
                            'ret=', True)
            return True
        return False

    def _getEarliestSitdownPlayer(self, table):
        ret = None
        for seat in table.seats:
            if not seat.player:
                continue
            if ret is None or seat.player.sitdownTime < ret.sitdownTime:
                ret = seat.player
        return ret

    def _onSitdownEvent(self, evt):
        evt.player.sitdownTime = int(time.time())
        winStreak = self.getPlayerWinStreak(evt.table, evt.player)
        evt.table.winStreakSection = self.getWinStreakSection(evt.table, winStreak)
        if ftlog.is_debug():
            ftlog.debug('AssignTableWinStreakPolicy._onSitdownEvent',
                        'seat=', (evt.player.userId, evt.player.seatId),
                        'winStreak=', winStreak,
                        'winStreakSeaction=', evt.table.winStreakSection)

    def _onStandupEvent(self, evt):
        if ftlog.is_debug():
            ftlog.debug('AssignTableWinStreakPolicy._onStandupEvent',
                        'seat=', (evt.player.userId, evt.seat.seatId))
        evt.player.sitdownTime = 0
        if evt.table.idleSeatCount == evt.table.seatCount:
            # 桌子没人了
            evt.table.winStreakSection = None
