# -*- coding:utf-8 -*-
'''
Created on 2017年2月20日

@author: zhaojiangang
'''
import time

from dizhu.entity.matchrecord import MatchRecord
from dizhu.games.tablecommonproto import DizhuTableProtoCommonBase
from freetime.core.tasklet import FTTasklet
from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from poker.protocol import router


class DizhuTableProtoErdayiMatch(DizhuTableProtoCommonBase):
    WINLOSE_SLEEP = 2
    
    def __init__(self, tableCtrl):
        super(DizhuTableProtoErdayiMatch, self).__init__(tableCtrl)

    def sendToSeat(self, mp, seat):
        if (seat.player
            and not seat.isGiveup
            and not seat.player.isAI):
            router.sendToUser(mp, seat.userId)

    def sendToAllSeat(self, mp):
        for seat in self.table.seats:
            self.sendToSeat(mp, seat)

    def buildSeatInfo(self, forSeat, seat):
        seatInfo = super(DizhuTableProtoErdayiMatch, self).buildSeatInfo(forSeat, seat)
        seatInfo['mscore'], seatInfo['mrank'] = (seat.player.score, seat.player.rank) if seat.player else (0, 0)
        if seat.player and not seat.player.isAI and self.table.matchTableInfo:
            record = MatchRecord.loadRecord(self.gameId, seat.userId, self.table.matchTableInfo['matchId'])
            if record:
                seatInfo['mrecord'] = {
                    'bestRank':record.bestRank,
                    'crownCount':record.crownCount,
                    'playCount':record.playCount
                }
            if ftlog.is_debug():
                ftlog.debug('DizhuTableProtoGroupMatch.buildSeatInfo',
                            'userId=', seat.player.userId,
                            'score=', seat.player.score,
                            'rank=', seat.player.rank)
                            
        return seatInfo
    
    def buildTableInfoResp(self, seat, isRobot):
        mp = super(DizhuTableProtoErdayiMatch, self).buildTableInfoResp(seat, isRobot)
        self.getMatchTableInfo(seat, mp)
        return mp
    
    def getMatchTableInfo(self, seat, mo):
        matchTableInfo = self.table.matchTableInfo
        if matchTableInfo:
            mo.setResult('step', {
                            'name':matchTableInfo['step']['name'],
                            'des':'%s人参赛，%s人晋级' % (matchTableInfo['step']['playerCount'], matchTableInfo['step']['riseCount']),
                            'playerCount':matchTableInfo['step']['playerCount'],
                            'note':self.buildNote(seat),
                            'basescore':matchTableInfo['step']['basescore']
                        })
    
    def buildNote(self, seat):
        '''
        Note: DizhuSender.sendTableInfoRes will invoke this func
        '''
        matchTableInfo = self.table.matchTableInfo
        return u'%s：%s人晋级，第%s副（共%s副）' % (matchTableInfo['step']['name'],
                              matchTableInfo['step']['riseCount'],
                              seat.player.matchUserInfo['cardCount'],
                              matchTableInfo['step']['cardCount'])
        return ''
    
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
        
    def _do_table_manage__m_table_start(self, msg):
        if ftlog.is_debug():
            ftlog.debug('DizhuTableProtoErdayiMatch._do_table_manage__m_table_start',
                        'msg=', msg)
        
        startTime = int(time.time())
        tableInfo = msg.getKey('params')
        ret = self.tableCtrl.startMatchTable(tableInfo)
        
        if ftlog.is_debug():
            ftlog.debug('DizhuTableProtoErdayiMatch._do_table_manage__m_table_start',
                        'msg=', msg,
                        'ret=', ret,
                        'used=', int(time.time()) - startTime)
    
    def _do_table_manage__m_table_clear(self, msg):
        if ftlog.is_debug():
            ftlog.debug('DizhuTableProtoErdayiMatch._do_table_manage__m_table_clear',
                        'msg=', msg)
        params = msg.getKey('params')
        matchId = params.get('matchId', -1)
        ccrc = params.get('ccrc', -1)
        self.tableCtrl.clearMatchTable(matchId, ccrc)

    def _onGameRoundOver(self, event):
        if ftlog.is_debug():
            ftlog.debug('DizhuTableProtoGroupMatch._onGameRoundOver',
                        'tableId=', event.table.tableId,
                        'seats=', [(s.userId, s.seatId) for s in event.table.seats])
        self.sendWinloseRes(event.gameResult)
        self._sendWinloseToMatch(event.gameResult)
        
    def _onGameRoundAbort(self, event):
        if ftlog.is_debug():
            ftlog.debug('DizhuTableProtoGroupMatch._onGameRoundAbort',
                        'tableId=', event.table.tableId,
                        'seats=', [(s.userId, s.seatId) for s in event.table.seats])
        self.sendWinloseAbortRes(event.gameResult)
        self._sendWinloseToMatch(event.gameResult)

    def _sendWinloseToMatch(self, result):
        # 发送给match manager
        users = []
        for sst in result.seatStatements:
            if not sst.seat.player.isAI:
                user = {}
                user['userId'] = sst.seat.userId
                user['deltaScore'] = sst.delta
                user['finalScore'] = sst.final 
                user['seatId'] = sst.seat.seatId
                users.append(user)
                if ftlog.is_debug():
                    ftlog.debug('DizhuTableProtoGroupMatch._sendWinloseToMatch',
                                'userId=', sst.seat.userId,
                                'delta=', sst.delta,
                                'final=', sst.final,
                                'seatId=', sst.seat.seatId)
        
        mp = MsgPack()
        mp.setCmd('room')
        mp.setParam('action', 'm_winlose')
        mp.setParam('gameId', self.gameId)
        mp.setParam('matchId', self.room.bigmatchId)
        mp.setParam('roomId', self.room.ctrlRoomId)
        mp.setParam('tableId', self.tableId)
        mp.setParam('users', users)
        mp.setParam('ccrc', self.table.matchTableInfo['ccrc'])
        
        if self.WINLOSE_SLEEP > 0:
            FTTasklet.getCurrentFTTasklet().sleepNb(self.WINLOSE_SLEEP)
        router.sendRoomServer(mp, self.room.ctrlRoomId)

    def sendTableInfoRes(self, seat):
        logUserIds = [66706022]
        if seat.player and seat.userId in logUserIds:
            ftlog.info('DizhuTableProtoErdayiMatch.sendTableInfoRes beforeSentMsg',
                       'tableId=', self.tableId,
                       'userId=', seat.userId,
                       'gameClientVer=', seat.player.gameClientVer,
                       'isGiveup=', seat.isGiveup,
                       'isQuit=', seat.player.isQuit,
                       'seats=', [(s.userId, s.seatId) for s in self.table.seats])

        if seat.player and not seat.isGiveup and not seat.player.isQuit:
            mp = self.buildTableInfoResp(seat, 0)
            router.sendToUser(mp, seat.userId)
            if seat.userId in logUserIds:
                ftlog.info('DizhuTableProtoErdayiMatch.sendTableInfoRes sentMsg',
                           'tableId=', self.tableId,
                           'userId=', seat.userId,
                           'gameClientVer=', seat.player.gameClientVer,
                           'seats=', [(seat.userId, seat.seatId) for seat in self.table.seats],
                           'mp=', mp.pack())


