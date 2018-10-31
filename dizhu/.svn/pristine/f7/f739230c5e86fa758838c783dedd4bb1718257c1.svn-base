# -*- coding:utf-8 -*-
'''
Created on 2018年04月07日

@author: zhaoliang
'''
from poker.entity.game.tables.table_player import TYPlayer
from freetime.util import log as ftlog
from dizhu.gametable.dizhu_state import DizhuState
from dizhu.gametable.dizhu_player import DizhuPlayer
from poker.entity.biz import bireport
from dizhu.entity import dizhuconf
from freetime.core.tasklet import FTTasklet

def doChuPai(self, player, cards, mcrc, tuoGuanType):
    ftlog.debug('doChuPai tid=', self.table.tableId, 'the mcrc=', mcrc, 'ccrc=', self.table.status.cardCrc,
                'cards=', cards, 'mcrc=', mcrc, 'tuoGuanType=', tuoGuanType)
    if not player or self.table.status.state != DizhuState.TABLE_STATE_PLAYING :
        ftlog.warn('ERROR !!, doChuPai table.status=', self.table.status, player)
        return
    # 清理超时的次数
    seat = self.table.seats[player.seatIndex]
    #seat.robotCardCount = 0
    # 首先校验出牌的CRC
    if mcrc >= 0 and mcrc != self.table.status.cardCrc :
        ftlog.warn('doChuPai the ccrc error ! mcrc=', mcrc, 'ccrc=', self.table.status.cardCrc)
        self.sender.sendTableInfoRes(player.userId, player.clientId, 0)
        return
    # 托管出牌处理
    ftlog.debug("doChuPai userId=", player.userId, "card=", cards, "tuoGuanType=", tuoGuanType)
    if tuoGuanType != DizhuPlayer.TUGUAN_TYPE_USERACT :
        cards = self.punish.doRobotAutoCard(player.seatId, tuoGuanType)
    # 出牌数据校验
    canOutCard, cards = self._doChuPaiVerifyCard(player.seatId, cards)
    ftlog.debug('doChuPai tid=', self.table.tableId, 'canOutCard=', canOutCard, 'cards=', cards)
    if not canOutCard:
        ftlog.warn('ERROR cardOp verifyCard error')
        return
    
    if not cards and self.table.status.topSeatId == player.seatId:
        ftlog.warn('ERROR GameTable->doChuPai the top seat must chupai, but cards is none !')
        return
    precard = seat.cards[:]
    # 出牌牌型校验
    validCards = self.card.validateCards(cards, None)
    delayNextStep = False
    if cards :
        if not validCards:
            ftlog.warn('ERROR GameTable->doChuPai the cards is invalid!',
                       'tableId=', self.table.tableId,
                       'seat=', (player.userId, player.seatId),
                       'cards=', cards)
            return
        # 如果是管牌，并且(牌型不对或者牌型管不住TOPCARD)则忽略出牌
        if (self.table.status.topSeatId != 0 and self.table.status.topSeatId != player.seatId 
            and (not validCards or not self._isGreaterThan(validCards, self.table.status.topCardList))):
            ftlog.warn('doChuPai seatId=', player.seatId, 'cards=', cards,
                        'topseat=', self.table.status.topSeatId,
                        'topcards=', self.table.status.topCardList,
                        'validCards=', validCards)
            cards = []
            validCards = None

    if cards :
        if validCards:
            if validCards.isHuoJian():
                # 火箭, 倍数翻倍
                delayNextStep = True
                self.table.status.bomb += 1
                seat.couponCard[0] += 1
            elif validCards.isZhaDan():
                # 炸弹, 倍数翻倍
                delayNextStep = True
                self.table.status.bomb += 1
                seat.couponCard[1] += 1
            elif validCards.isFeiJiDai1() or validCards.isFeiJiDai2():
                # 飞机
                seat.couponCard[2] += 1
        # 出牌处理
        self._outCard(player, seat, cards)
        # 如果出的是火箭, 那么记录另外两个玩家的ID, 需要进行快速不出牌处理
        if self.card.isDoubleKing(cards):
            for x in xrange(len(self.table.seats)) :
                if x != player.seatIndex :
                    self._doubleKingNoCard[x + 1] = 1
        # 记录最后出牌的信息
        seat.outCardCount += 1
        self.table.status.topValidCard = validCards
        self.table.status.topCardList = cards
        self.table.status.topSeatId = player.seatId
    # 清除当前的计时器
    ftlog.debug('doChuPai tid=', self.table.tableId, 'seat.cards=', seat.cards, 'topSeatId=', player.seatId, 'outCards=', cards)
    self.table.tableTimer.cancel()
    # 刷新上一次出牌
    seat.lastOutCards = seat.outCards
    seat.outCards = cards
    # 发送出牌的响应消息
    self.sender.sendChuPaiRes(player.seatId, player.userId, cards, precard, tuoGuanType)
    # 牌局记录器处理
    self.table.gameRound.outCard(player.seatIndex, cards[:], self.calcCurTotalMulti())
    # BI日志汇报
    if TYPlayer.isRobot(player.userId):
        player.clientId = 'robot_3.7_-hall6-robot'
        
    bireport.reportCardEvent('TABLE_CARD', player.userId, self.table.gameId, self.table.roomId,
                         self.table.tableId, self.table.gameRound.number, 0,
                         0, 0, cards, player.clientId, 0, 0)

    if delayNextStep:
        interval = dizhuconf.getPublic().get('bombNextDelay', 0)
        if interval > 0:
            FTTasklet.getCurrentFTTasklet().sleepNb(interval)
    self.nextStep(player)
    
from dizhu.gameplays.gameplay_base import DizhuBaseGamePlay
DizhuBaseGamePlay.doChuPai = doChuPai