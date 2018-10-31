# -*- coding:utf-8 -*-
'''
Created on 2017年2月17日

@author: zhaojiangang
'''
import functools

from dizhu.entity import dizhuconf
from dizhu.games.tablecommonproto import DizhuTableProtoCommonBase
from freetime.core.tasklet import FTTasklet
from freetime.core.timer import FTTimer
from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from poker.entity.game.rooms.group_match_ctrl.const import AnimationType, \
    StageType
from poker.entity.game.rooms.room import TYRoom
from poker.protocol import router


class DizhuTableProtoCustomMatch(DizhuTableProtoCommonBase):
    WINLOSE_SLEEP = 2
    
    def __init__(self, tableCtrl):
        super(DizhuTableProtoCustomMatch, self).__init__(tableCtrl)
        
    def getMatchTableInfo(self, seat, mo):
        matchTableInfo = self.table.matchTableInfo
        
        mo.setResult('stage', {
                        'stageIndex':matchTableInfo['stage']['stageIndex'],
                        'riseCount':matchTableInfo['stage']['riseCount'],
                        'playerCount':matchTableInfo['stage']['playerCount'],
                        'cardCount':seat.player.matchUserInfo['cardCount'],
                        'totalCardCount':matchTableInfo['stage']['cardCount']
                    })
        
    def buildTableInfoResp(self, seat, isRobot):
        mp = super(DizhuTableProtoCustomMatch, self).buildTableInfoResp(seat, isRobot)
        self.getMatchTableInfo(seat, mp)
        return mp
    
    def buildSeatInfo(self, forSeat, seat):
        seatInfo = super(DizhuTableProtoCustomMatch, self).buildSeatInfo(forSeat, seat)
        seatInfo['mscore'], seatInfo['mrank'] = (seat.player.score, seat.player.rank) if seat.player else (0, 0)
        return seatInfo
    
    def sendWinloseRes(self, result):
        mp = self.buildTableMsgRes('table_call', 'game_win')
        mp.setResult('isMatch', 1)
        mp.setResult('stat', self.buildTableStatusInfo())
        mp.setResult('slam', 0)
        mp.setResult('dizhuwin', 1 if result.isDizhuWin() else 0)
        if not result.gameRound.dizhuSeat:
            mp.setResult('nowin', 1)
        mp.setResult('cards', [seat.status.cards for seat in self.table.seats])
        for sst in result.seatStatements:
            mrank = 3
            mtableRanking = 3
            mp.setResult('seat' + str(sst.seat.seatId),
                         [
                            sst.delta,
                            sst.final,
                            0, 0, 0, 0,
                            mrank,
                            mtableRanking
                         ])
        self.sendToAllSeat(mp)

    def buildMatchStepInfo(self, seat):
        return {
            'curCount':seat.player.matchUserInfo['cardCount'],
            'totoal':self.table.matchTableInfo['stage']['cardCount']
        }
    
    def getAnimationType(self, table, clientVer):
        if clientVer < 3.37:
            return AnimationType.UNKNOWN
        return table.matchTableInfo['stage']['params'].get('animation.type')
    
    def getAnimationInter(self, animationType, isStartStep, clientVer):
        if clientVer < 3.77:
            return self.MSTART_SLEEP
        
        delayConf = dizhuconf.getPublic().get('matchAnimationDelay', '')
        if not delayConf:
            if isStartStep:
                return 5
            return 3
        valKey = 'startStep'
        if not isStartStep:
            valKey = 'type' + str(animationType)
        return delayConf.get(valKey, 3)
    
    def playAnimationIfNeed(self, table):
        playAnimation, delaySeconds = False, 0
        matchTableInfo = table.matchTableInfo
        
        for seat in table.seats:
            if seat.player:
                animationType = self.getAnimationType(table, seat.player.gameClientVer)
                if animationType != AnimationType.UNKNOWN:
                    mp = MsgPack()
                    mp.setCmd('m_play_animation')
                    mp.setResult('gameId', table.gameId)
                    mp.setResult('roomId', table.roomId)
                    mp.setResult('tableId', table.tableId)
                    mp.setResult('type', animationType)
                    mp.setResult('stage', {
                        'isStartStep':matchTableInfo['stage']['isStartStage'],
                        'cardCount':seat.player.matchUserInfo['cardCount'],
                        'totalCardCount':matchTableInfo['cardCount']
                    })
                    self.sendToSeat(mp, seat)
                    curDelay = self.getAnimationInter(animationType, matchTableInfo['stage']['isStartStage'], seat.player.gameClientVer)
                    playAnimation = True
                    delaySeconds = max(delaySeconds, curDelay)
        return playAnimation, delaySeconds
    
    def buildNote(self, seat):
        '''
        Note: DizhuSender.sendTableInfoRes will invoke this func
        '''
        tableInfo = self.table.matchTableInfo
        return u'%s人晋级，第%s副（共%s副）' % (tableInfo['stage']['riseCount'],
                                            seat.player.matchUserInfo['cardCount'],
                                            tableInfo['stage']['cardCount'])
    
    def sendRank(self, seat):
        pass
#         _, clientVer, clientChannel = strutil.parseClientId(seat.player.clientId)
#         ranks = self.table.matchTableInfo['ranks']
#         if not ranks:
#             ftlog.warn('DizhuTableProtoCustomMatch.sendRank',
#                        'userId=', seat.userId,
#                        'TODO the _match_table_info[\'ranks\'] is empty why !!')
#             return
#         mp = MsgPack()
#         mp.setCmd('m_rank')
#         if clientVer >= 3.37:
#             ranktops = []
#             ranktops.append({
#                 'userId':seat.userId,
#                 'name':seat.player.matchUserInfo['userName'],
#                 'score':seat.player.matchUserInfo['score'],
#                 'rank':seat.player.matchUserInfo['chiprank']
#             })
#             for i, r in enumerate(ranks):
#                 ranktops.append({'userId':r[0], 'name':str(r[1]), 'score':r[2], 'rank':i + 1})
#             mp.setResult('mranks', ranktops)
#         else:
#             ranktops = []
#             for r in ranks:
#                 ranktops.append((r[0], r[1], r[2]))
#             mp.setResult('mranks', ranktops)
#         self.sendToSeat(mp, seat)
        
    def sendMNoteMsg(self, noteInfos):
        for seat, userId, note in noteInfos:
            if seat.userId == userId:
                mp = MsgPack()
                mp.setCmd('m_note')
                mp.setResult('note', note)
                self.sendToSeat(mp, seat)

    def _onSitdown(self, event):
        if ftlog.is_debug():
            ftlog.debug('DizhuTableProtoCustomMatch._onSitdown',
                        'tableId=', event.table.tableId,
                        'seatId=', event.seat.seatId,
                        'userId=', event.seat.userId)
        
        self.sendQuickStartRes(event.seat, True, TYRoom.ENTER_ROOM_REASON_OK)
        if event.table.idleSeatCount == 0:
            # 所有人都坐下后发tableInfo
            self.sendTableInfoResAll()
            
            # 延迟1秒进行animation Info相关处理
            FTTasklet.getCurrentFTTasklet().sleepNb(1)
    
            playAnmi, delaySeconds = self.playAnimationIfNeed(event.table)
            
            if playAnmi and delaySeconds > 0:
                FTTasklet.getCurrentFTTasklet().sleepNb(playAnmi['delaySeconds'])

        self.sendRobotNotifyCallUp(None)
    
    def _onGameReady(self, event):
        super(DizhuTableProtoCustomMatch, self)._onGameReady(event)
        matchTableInfo = event.table.matchTableInfo
        isStartStep = matchTableInfo['stage']['isStartStage']

        if isStartStep:
            noteInfos = []
            for seat in event.table.seats:
                note = self.buildNote(seat)
                mn = MsgPack()
                mn.setCmd('m_note')
                mn.setResult('note', note)
                self.sendToSeat(mn, seat)
                noteInfos.append((seat, seat.userId, note))
            func = functools.partial(self.sendMNoteMsg, noteInfos)
            FTTimer(3, func)
        
        for seat in event.table.seats:
            self.sendRank(seat)
    
    def _sendWinloseToMatch(self, result):
        # 发送给match manager
        seatWinloses = []
        for sst in result.seatStatements:
            seatWinloses.append(sst.delta)

        mp = MsgPack()
        mp.setCmd('custom_match')
        mp.setParam('action', 'winlose')
        mp.setParam('gameId', self.gameId)
        mp.setParam('matchId', self.table.matchTableInfo['matchId'])
        mp.setParam('roomId', self.room.ctrlRoomId)
        mp.setParam('tableId', self.tableId)
        mp.setParam('seatWinloses', seatWinloses)
        mp.setParam('ccrc', self.table.matchTableInfo['ccrc'])
        
        if self.WINLOSE_SLEEP > 0:
            FTTasklet.getCurrentFTTasklet().sleepNb(self.WINLOSE_SLEEP)
        
        router.sendRoomServer(mp, self.room.ctrlRoomId)
        
    def _onGameRoundOver(self, event):
        if ftlog.is_debug():
            ftlog.debug('DizhuTableProtoCustomMatch._onGameRoundOver',
                        'tableId=', event.table.tableId,
                        'seats=', [(s.userId, s.seatId) for s in event.table.seats])
        self.sendWinloseRes(event.gameResult)
        self._sendWinloseToMatch(event.gameResult)

    def _onGameRoundAbort(self, event):
        if ftlog.is_debug():
            ftlog.debug('DizhuTableProtoCustomMatch._onGameRoundAbort',
                        'tableId=', event.table.tableId,
                        'seats=', [(s.userId, s.seatId) for s in event.table.seats])
        self.sendWinloseAbortRes(event.gameResult)
        self._sendWinloseToMatch(event.gameResult)

    def sendTableInfoRes(self, seat):
        if seat.player and not seat.isGiveup and not seat.player.isQuit:
            mp = self.buildTableInfoResp(seat, 0)
            router.sendToUser(mp, seat.userId)


