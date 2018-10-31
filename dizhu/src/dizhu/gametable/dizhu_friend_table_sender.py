# -*- coding:utf-8 -*-
'''
Created on 2016年9月22日

@author: zhaojiangang
'''
from dizhu.gametable.dizhu_sender import DizhuSender
from dizhu.gametable.dizhu_state import DizhuState
from freetime.entity.msg import MsgPack
from freetime.util import log as ftlog
from poker.entity.configure import gdata
from poker.protocol import router
from poker.util import strutil
import poker.util.timestamp as pktimestamp


class DizhuFTSender(DizhuSender):
    OPTIME_CHUPAI_MIN = 25
    OPTIME_CALL_MIN = 25
    
    def __init__(self, table):
        super(DizhuFTSender, self).__init__(table)
        
    def sendUserReadyRes(self, player):
        mo = self.createMsgPackRes('table_call', 'ready')
        mo.setResult('seatId', player.seatId)
        mo.setResult('userId', player.userId)
        mo.setResult('mscore', player.score)
        self.sendToAllTableUser(mo)
        
    def sendQuickStartRes(self, userId, clientId, result):
        ftlog.debug("|params", userId, clientId, result, caller=self)
        mpSitRes = self.createMsgPackRes("quick_start")
        mpSitRes.setResult('tableType', 'friend')
        mpSitRes.updateResult(result)
        router.sendToUser(mpSitRes, userId)
        
    def sendChuPaiNextRes(self, seatId, opTime):
        mo = self.createMsgPackRes('table_call', 'next')
        mo.setResult('next', seatId)
        mo.setResult('seatId', seatId)
        mo.setResult('stat', self.table.status.toInfoDict())
        mo.setResult('opTime', min(self.OPTIME_CHUPAI_MIN, opTime))
        self.sendToAllTableUser(mo)
    
    def sendCallNextRes(self, nextSid, grab):
        mo = self.createMsgPackRes('table_call', 'next')
        mo.setResult('seatId', nextSid)
        mo.setResult('next', nextSid)
        mo.setResult('grab', grab)
        mo.setResult('stat', self.table.status.toInfoDict())
        mo.setResult('opTime', min(self.OPTIME_CALL_MIN, self.table.runConfig.optime))
        self.sendToAllTableUser(mo)

    def sendReqDisbindRes(self, player, optime):
        if ftlog.is_debug():
            ftlog.debug('DizhuFTSender.sendReqAbort',
                        'tableId=', self.table.tableId,
                        'ftId=', self.table.ftTable.ftId,
                        'userId=', player.userId,
                        'seatId=', player.seatId)
        mo = self.createMsgPackRes('table_call', 'ft_req_disbind')
        mo.setResult('seatId', player.seatId)
        mo.setResult('userId', player.userId)
        mo.setResult('optime', optime)
        mo.setResult('disbinds', self.table.preDisbindSeatState[:])
        for p in self.table.players:
            if p.userId > 0:
                router.sendToUser(mo, p.userId)
        
    def sendFTContinueResError(self, player, ec, info):
        mo = self.createMsgPackRes('table_call', 'ft_continue')
        mo.setResult('seatId', player.seatId)
        mo.setResult('userId', player.userId)
        mo.setResult('code', ec)
        mo.setResult('info', info)
        self.sendToAllTableUser(mo)
    
    def sendFTContinueResOk(self, player, cardCount):
        mo = self.createMsgPackRes('table_call', 'ft_continue')
        mo.setResult('seatId', player.seatId)
        mo.setResult('userId', player.userId)
        mo.setResult('cardCount', cardCount)
        self.sendToAllTableUser(mo)

    def sendReqDisbindAnswerRes(self, player, disbinds):
        if ftlog.is_debug():
            ftlog.debug('DizhuFTSender.sendReqDisbindAnswerRes',
                        'tableId=', self.table.tableId,
                        'ftId=', self.table.ftTable.ftId,
                        'userId=', player.userId,
                        'seatId=', player.seatId)
        mo = self.createMsgPackRes('table_call', 'ft_req_disbind_answer')
        mo.setResult('seatId', player.seatId)
        mo.setResult('userId', player.userId)
        mo.setResult('disbinds', disbinds)
        self.sendToAllTableUser(mo)
        
    def sendReqDisbindResultRes(self, disbinds, disbindResult):
        if ftlog.is_debug():
            ftlog.debug('DizhuFTSender.sendReqDisbindResultRes',
                        'tableId=', self.table.tableId,
                        'ftId=', self.table.ftTable.ftId)
        mo = self.createMsgPackRes('table_call', 'ft_req_disbind_result')
        mo.setResult('disbinds', disbinds)
        mo.setResult('disbindResult', disbindResult)
        self.sendToAllTableUser(mo)
        
    def sendDisbindRes(self, statics):
        if ftlog.is_debug():
            ftlog.debug('DizhuFTSender.sendDisbindRes',
                        'tableId=', self.table.tableId,
                        'ftId=', self.table.ftId)
        mo = self.createMsgPackRes('table_call', 'ft_disbind')
        mo.setResult('ftId', self.table.ftId)
        mo.setResult('results', self.table.results)
        if statics:
            mo.setResult('statics', statics)
        self.sendToAllTableUser(mo)
    
    def sendGameWinRes(self, player, statics, results):
        moWin = MsgPack()
        moWin.setCmd('table_call')
        moWin.setResult('action', 'game_win')
        moWin.setResult('isMatch', 1)
        moWin.setResult('gameId', self.table.gameId)
        moWin.setResult('roomId', self.table.roomId)
        moWin.setResult('tableId', self.table.tableId)
        moWin.setResult('stat', self.table.status.toInfoDictExt())
        moWin.setResult('dizhuwin', 1 if player and player.seatId == self.table.status.diZhu else 0)
        moWin.setResult('slam', 0)
        if not player:
            moWin.setResult('nowin', 1)
        moWin.setResult('ftId', self.table.ftId)
        curRound = len(results) if player else max(0, len(results) - 1)
        moWin.setResult('curRound', curRound)
        moWin.setResult('totalRound', self.table.ftTable.nRound)
        moWin.setResult('cards', [seat.cards for seat in self.table.seats])
        moWin.setResult('results', results)
        if self.table.isFinishAllRound():
            moWin.setResult('finish', 1)
        if statics:
            moWin.setResult('statics', statics)
        self.sendToAllTableUser(moWin)
        
    def buildFTInfo(self, curRound):
        ret = {
            'ftId':self.table.ftTable.ftId,
            'creator':self.table.ftTable.userId,
            'curRound':curRound,
            'playMode':self.table.ftTable.playMode,
            'totalRound':self.table.ftTable.nRound,
            'double':self.table.ftTable.canDouble,
            'goodCard':self.table.ftTable.goodCard,
            'fee':self.table.ftTable.fee.count if self.table.ftTable.fee else 0,
            'ftContinueTimeout': self.table.runConfig.ftContinueTimeout
        }
        return ret
    
    def sendGameReadyResForSeat(self, seatIndex):
        mo = self.createMsgPackRes('table_call', 'game_ready')
        for i, seat in enumerate(self.table.seats):
            cards = seat.cards
            if (self.table.players[seatIndex].gameClientVer >= DizhuSender.HIDE_CARD_VER
                and i != seatIndex
                and not seat.isShow):
                # 隐藏没有明牌人的牌的牌
                cards = [-1 for _ in xrange(len(seat.cards))]
            mo.setResult('cards' + str(i), cards)
        basecard = self.table.status.baseCardList
        kickoutCard = self.table.status.kickOutCardList
        if self.table.players[seatIndex].gameClientVer >= DizhuSender.HIDE_CARD_VER:
            # 隐藏底牌，剔除的牌
            basecard = [-1 for _ in xrange(len(basecard))]
            kickoutCard = [-1 for _ in xrange(len(kickoutCard))]
        mo.setResult('basecard', basecard)
        mo.setResult('kickoutCard', kickoutCard)
        mo.setResult('rangpai', self.table.status.rangPai)
        mo.setResult('grabCard', self.table.status.grabCard)
        mo.setResult('myCardNote', self.buildCardNote(seatIndex))
        if self.table.gameRound:
            mo.setResult('roundId', self.table.gameRound.roundId)
        if self.table._complain:
            mo.setResult('gameNum', self.table.gameRound.roundId)
        
        mo.setResult('ftInfo', self.buildFTInfo(len(self.table.results) + 1))
        router.sendToUser(mo, self.table.seats[seatIndex].userId)
        
    def sendFTContinueRes(self, player, ec, info):
        mo = self.createMsgPackRes('table_call', 'ft_continue')
        if ec != 0:
            mo.setResult('code', ec)
            mo.setResult('info', info)
        router.sendToUser(mo, player.userId)
        
    def sendTableInfoRes(self, userId, clientId, isrobot):
        if ftlog.is_debug():
            ftlog.debug('DizhuFTSender.sendTableInfoRes',
                        'tableId=', self.table.tableId,
                        'ftId=', self.table.ftTable.ftId,
                        'userId=', userId,
                        'clientId=', clientId,
                        'isrobot=', isrobot)
        player = self.table.getPlayer(userId)
        if not player:
            ftlog.warn('DizhuFTSender.sendTableInfoRes NotPlayer',
                       'tableId=', self.table.tableId,
                       'ftId=', self.table.ftTable.ftId,
                       'userId=', userId,
                       'clientId=', clientId,
                       'isrobot=', isrobot)
            return
        baseinfo = self.table.buildBasicInfo(False, userId, clientId)
        _, clientVer, _ = strutil.parseClientId(clientId)
        mo = self.createMsgPackRes("table_info")
        isMatch = self.table.isMatch
        mo.setResult('isrobot', isrobot)
        mo.setResult('playMode', self.table.gamePlay.getPlayMode())
        mo.setResult('results', self.table.results or [])
        
        roomLevel = gdata.roomIdDefineMap()[self.table.roomId].configure.get('roomLevel', 1)
        mo.setResult('roomLevel', roomLevel)
        roomName = self.table.room.roomConf['name'] if self.table.room else ''
        mo.setResult('roomName', roomName)
        mo.setResult('isMatch', isMatch)
        mo.setResult('info', baseinfo['info'])
        mo.setResult('config', baseinfo['config'])
        mo.setResult('stat', self.buildStatusInfoDict(player))
        mo.setResult('myCardNote', self.buildCardNote(player.seatIndex))
        if self.table.preDisbind:
            mo.setResult('disbind', {
                'reqSeatId':self.table.preDisbindSeatId,
                'states':self.table.preDisbindSeatState[:],
                'optime':max(0, self.table.preDisbindExpires - pktimestamp.getCurrentTimestamp())
            })
        if self.table.ftTable:
            curRound = len(self.table.results)
            if self.table.status.state >= DizhuState.TABLE_STATE_CALLING:
                curRound += 1
            mo.setResult('ftInfo', self.buildFTInfo(curRound))
        
        for i in xrange(len(self.table.seats)):
            seat = self.table.seats[i]
            oseat = self.buildSeatInfo(player, seat)
            seatuid = seat.userId
            if seatuid :
                seatPlayer = self.table.players[i]
                oseat.update(seatPlayer.datas)
                oseat['cardNote'] = seatPlayer.getCardNoteCount()
                oseat['mscore'] = seatPlayer.score
                seatPlayer.cleanDataAfterFirstUserInfo()
            else:
                oseat['uid'] = 0
            mo.setResult('seat' + str(i + 1), oseat)
            
        router.sendToUser(mo, userId)
            
