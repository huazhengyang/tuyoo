# -*- coding:utf-8 -*-
'''
Created on 2016年12月1日

@author: zhaojiangang
'''
import random

from dizhucomm.core import cardrule
from dizhucomm.core.cardrule import CardFinder
from dizhucomm.core.playmode import GameRound
from poker.entity.dao import daobase


class CallPolicy(object):
    '''
    叫地主策略
    '''
    def call(self, table, callValue, oper):
        '''
        玩家叫地主
        @return: (CallResult, NextCallSeat)
        '''
        raise NotImplementedError

class SendCardsPolicy(object):
    '''
    发牌策略
    '''
    def sendCards(self, table):
        raise NotImplementedError
    
class FirstCallPolicy(object):
    '''
    首叫策略
    '''
    def chooseFirstCall(self, table):
        '''
        选择首叫的座位
        @return: Seat
        '''
        raise NotImplementedError
    
class FirstCallPolicyRandom(FirstCallPolicy):
    def chooseFirstCall(self, table):
        gameRound = table.gameRound
        index = random.randint(0, len(gameRound.seats) - 1)
        return gameRound.seats[index]
    
class TuoguanPolicy(object):
    '''
    托管时如何叫地主出牌的策略
    '''
    def callValueForTuoguan(self, table, seat):
        '''
        托管如何叫地主, 如果是急速类型且双王或4个2必须叫地主
        @return: callValue
        '''
        if table.runConf.grab == 0 and table.room.roomConf['playMode'] in ["wild", "quick_laizi"]:
            if table.gameRound.lastEffectiveCall:
                return 0
            cardRule = cardrule.CardDiZhuLaizi3Player()
            reducedCards = cardrule.ReducedCards.reduceHandCards(cardRule, table.gameRound.curOpSeat.status.cards)
            if CardFinder.findHuojianAndZhadan2(cardRule, reducedCards):
                return 1
        return 0
    
    def outCardForTuoguan(self, table, seat, tuoguanType):
        '''
        托管时如何出牌
        @return: ValidCards or None
        '''
        raise NotImplementedError

class AutoChupaiPolicy(object):
    '''
    自动出牌策略
    '''
    def checkAutoChupai(self, table, seat):
        '''
        检查是否可以自动出牌了，如果可以返回ValidCards
        @return: (True/False, ValidCards/None)
        '''
        raise NotImplementedError

class AutoChupaiPolicyDefault(AutoChupaiPolicy):
    def checkAutoChupai(self, table, seat):
        '''
        检查是否可以自动出牌了，如果可以返回ValidCards
        @return: (True/False, ValidCards/None)
        '''
        # topValidCards是火箭则不出
        if (seat != table.gameRound.topSeat
            and table.gameRound.topValidCards
            and table.gameRound.topValidCards.isHuoJian()):
            return True, None
        
        autoValidCards = None
        autoChupai = False
        # 一手牌，且转换癞子牌为对应牌
        handValidCards = table.playMode.cardRule.checkMaxValidCardsWithHandCards(seat.status.cards)

        # 用户主动选择自动出牌
        # 地主拥有牌权能一手出就出
        if (seat.status.isAutoPlay == 1
            or (handValidCards and len(handValidCards.cards) == 1)
            or ((seat == table.gameRound.dizhuSeat == table.gameRound.topSeat)
                and handValidCards
                and handValidCards.isLastDizhuAutoOutCard())):
            autoChupai = True
            if seat == table.gameRound.topSeat:
                # 主动出牌
                autoValidCards = handValidCards or table.playMode.cardRule.findFirstSmallCard(seat.status.cards)
            else:
                # 被动出牌
                assert(table.gameRound.topValidCards)
                autoValidCards = handValidCards if (handValidCards and handValidCards.isGreaterThan(table.gameRound.topValidCards)) \
                                else table.playMode.cardRule.findGreaterValidCards(table.gameRound.topValidCards, seat.status.cards)
        if autoValidCards:
            autoValidCards.reducedCards.cards = autoValidCards.sortedCards
        return autoChupai, autoValidCards

class TuoguanPolicyDefault(TuoguanPolicy):
    def outCardForTuoguan(self, table, seat, tuoguanType):
        if not table.gameRound.topSeat or table.gameRound.topSeat == seat:
            return table.playMode.cardRule.findFirstSmallCard(seat.status.cards)
        return None
    
class RoundIdGen(object):
    '''
    牌局ID生成策略
    '''
    def genRoundId(self, table):
        '''
        @return: roundId
        '''
        raise NotImplementedError

class RoundIdGenRedis(object):
    def genRoundId(self, table):
        '''
        @return: roundId
        '''
        return daobase.executeTableCmd(table.roomId, table.tableId, 'HINCRBY', 'game.round.number', table.roomId, 1)
    
class SeatStatement(object):
    def __init__(self, seat):
        # 座位
        self.seat = seat
        # 服务费
        self.fee = 0
        # 固定服务费
        self.fixedFee = 0
        # 服务费倍数
        self.feeMulti = 1.0
        # 记牌器使用费用
        self.cardNoteFee = 0
        # 输赢
        self.delta = 0
        # 赢家税
        self.winnerTax = 0
        # 余额
        self.final = seat.player.score
        # 是否惩罚(包赔)
        self.isPunish = False
        # 是否赢了
        self.isWin = False
        # 连胜次数
        self.winStreak = 0
        # 连败次数
        self.loseStreak = 0
        # 连胜中断次数
        self.stopWinStreak = 0
        # 经验信息
        self.expInfo = []
        # 大师分信息
        self.skillscoreInfo = None
        # 是否是地主
        self.isDizhu = False
        # 总倍数
        self.totalMulti = seat.status.totalMulti
        # 系统为我付出的
        self.systemPaid = 0
        
    def deltaScore(self, delta):
        self.delta += delta
        self.final += delta
        
class GameResult(object):
    def __init__(self, gameRound):
        self.gameRound = gameRound
        self.seatStatements = []
        self.systemRecovery = 0
        self.dizhuStatement = None
        self.slamMulti = gameRound.table.runConf.gslam
        self.slam = gameRound.totalMulti >= self.slamMulti
        self.baseScore = gameRound.baseScore
        self.isChuntian = gameRound.isChuntian
        for seat in gameRound.seats:
            sst = SeatStatement(seat)
            if ((seat == gameRound.dizhuSeat and gameRound.result == GameRound.RESULT_DIZHU_WIN)
                or (seat != gameRound.dizhuSeat and gameRound.result == GameRound.RESULT_NONGMIN_WIN)):
                sst.isWin = True
            if seat == gameRound.dizhuSeat:
                self.dizhuStatement = sst
                sst.isDizhu = True
            
            sst.skillscoreInfo = dict(sst.seat.player.getData('skillScoreInfo', {}))
            sst.skillscoreInfo['addScore'] = 0
            sst.winStreak = 0
            sst.loseStreak = 0
            sst.stopWinStreak = 0
            sst.expInfo = [
                sst.seat.player.getData('slevel', 0),
                sst.seat.player.getData('exp', 0),
                0,
                sst.seat.player.getData('nextexp', 0),
                sst.seat.player.getData('title', '')
            ]
            
            self.seatStatements.append(sst)
    
    def getSeatStatement(self, seatId):
        for seatstat in self.seatStatements:
            if seatstat.seat.seatId == seatId:
                return seatstat
        return None 
    
    def isDizhuWin(self):
        for seatstat in self.seatStatements:
            if seatstat.seat == self.gameRound.dizhuSeat:
                return seatstat.isWin
        return False

class BuyinPolicy(object):
    def buyin(self, table, player, seat, continueBuyin):
        raise NotImplementedError
    
    def cashin(self, table, player, seat):
        raise NotImplementedError
     
class PunishPolicy(object):
    def punish(self, gameResult):
        '''
        根据gameResult进行惩罚
        '''
        raise NotImplementedError

class SettlementPolicy(object):
    def calcResult(self, gameRound):
        '''
        结账信息
        @return: GameResult
        '''
        raise NotImplementedError

    def settlement(self, gameResult):
        '''
        结账
        @param gameResult: GameResult
        '''
        raise NotImplementedError


