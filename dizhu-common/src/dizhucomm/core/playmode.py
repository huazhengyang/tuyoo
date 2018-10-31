# -*- coding:utf-8 -*-
'''
Created on 2016年12月1日

@author: zhaojiangang
'''
import random

from dizhucomm.core.const import Oper, OutCardResult, TuoguanType, \
    ClearGameReason, StandupReason, TuoguanLoction
from dizhucomm.core.events import SitdownEvent, StandupEvent, SeatReadyEvent, \
    GameReadyEvent, CurOpSeatMoveEvent, GameStartEvent, CallTimeoutEvent, CallEvent, \
    OutCardTimeoutEvent, OutCardEvent, TuoguanEvent, StartNongminJiabeiEvent, \
    StartDizhuJiabeiEvent, NongminJiabeiEvent, DizhuJiabeiEvent, StartHuanpaiEvent, \
    HuanpaiOutcardsEvent, HuanpaiIncardsEvent, HuanpaiEndEvent, GiveupEvent, \
    ShowCardEvent, GameClearEvent, GameRoundAbortEvent, GameRoundOverEvent, \
    SeatOnlineChanged, ChatEvent, GameRoundFinishEvent, AutoPlayEvent
from dizhucomm.core.exceptions import NoIdleSeatException, SeatNotIdleException, \
    EmptySeatException, BadStateException, BadOpSeatException, BadCardException, \
    BadJiabeiException, BadHuanpaiException
from dizhucomm.core.table import DizhuSeat
import freetime.util.log as ftlog
from dizhucomm.servers.util.rpc import comm_table_remote
from poker.entity.dao import onlinedata
import poker.util.timestamp as pktimestamp


class SeatStatus(object):
    def __init__(self):
        # 手牌
        self.cards = None
        # 记录出过的牌
        self.outCards = []
        # 叫分
        self.callValue = -1
        # 出牌次数
        self.outCardTimes = 0
        # 是否托管标记
        self.isTuoguan = False
        # 是否自动出牌标志
        self.isAutoPlay = -1
        # 地主/农民加倍倍数(0代表未设置，1就是不加倍)
        self.seatMulti = 0
        # 本座位总倍数
        self.totalMulti = 0
        # 是否惩罚
        self.isPunish = False
        # 记牌器使用费用
        self.cardNoteFee = 0
        # 托管超时次数(超时未操作次数，3次自动进入托管状态)
        self.timeoutCount = 0
        # 换牌中临时保存的要换的牌列表list<int>
        self.huanpaiOutcards = None
        # 换牌中临时保存要得到的牌列表list<int>
        self.huanpaiIncards = None
        # 是否显示明牌(showCard,isShow)
        self.isShowCards = False
        # 是否已经放弃了本牌局
        self.giveup = False
        # 是否托管过滤
        self.isPassedTuoguan = False
        # 是否叫牌超时
        self.isCallUpTimeout = False
        # 是否触发炸弹红包
        self.isRedEnvelope = False
        # 总出牌时间
        self.outCardSeconds = 0
        # 开始出牌时间
        self.startChupaiTimestamp = 0
        # 农民且出完牌
        self.isLeadWin = 0
        
class GameRound(object):
    RESULT_DRAW = 0
    RESULT_DIZHU_WIN = 1
    RESULT_NONGMIN_WIN = 2
    
    def __init__(self):
        # 牌桌
        self.table = None
        # 牌局相关
        self.roundId = None
        # 牌局
        self.roundNum = None
        # 出牌校验值
        self.cardCrc = 0
        # 参与本局的座位,list<SeatBase>
        self.seats = None
        # 当前操作座位
        self.curOpSeat = None
        # 底牌list<int>
        self.baseCards = None
        # 最后出牌的座位
        self.topSeat = None
        # 最后出的牌
        self.topValidCards = None
        # 首叫的座位
        self.firstCallSeat = None
        # 地主座位
        self.dizhuSeat = None
        # 叫地主历史list<(Seat, callValue)>
        self.callList = None
        self.effectiveCallList = None
        # 癞子牌（癞子玩法）
        self.wildCard = None
        self.wildCardBig = None
        # 让牌数量（二斗玩法）
        self.rangpai = 0
        # ???
        self.grabCard = -1
        # 去除的牌（二斗玩法）
        self.kickoutCards = None
        # 第一个出完牌的座位
        self.firstWinSeat = None
        
        # 基础分
        self.baseScore = 1
        # 叫抢地主倍数
        self.callMulti = 0
        # 炸弹数量
        self.bombCount = 0
        # 是否春天
        self.isChuntian = False
        # 底牌倍数
        self.baseCardMulti = 1
        # 底牌类型
        self.baseCardType = 0
        # 名牌倍数
        self.showMulti = 1
        # 让牌倍数（二斗用的）
        self.rangpaiMulti = 1
        # 总倍数
        self.totalMulti = 0
        # 牌局结果 0：流局，1：地主赢；2：农民赢
        self.result = self.RESULT_DRAW
    
    @property
    def firstEffectiveCall(self):
        return self.effectiveCallList[0] if self.effectiveCallList else None
    
    @property
    def lastEffectiveCall(self):
        return self.effectiveCallList[-1] if self.effectiveCallList else None
    
    def init(self, table, roundNum, seats):
        assert(seats)
        self.table = table
        self.roundNum = roundNum
        self.roundId = '%s_%s' % (table.roomId, roundNum)
        self.seats = []
        self.callList = []
        self.effectiveCallList = []
        self.kickoutCards = []
        self.baseScore = table.runConf.baseScore
        for seat in seats:
            seat._state = DizhuSeat.ST_PLAYING
            seat._status = self._newSeatStatus(seat)
            if seat.player and seat.player.isQuit:
                seat._status.giveup = True
            if self.seats:
                self.seats[-1]._next = seat 
            self.seats.append(seat)
        if len(self.seats) > 1:
            self.seats[-1]._next = self.seats[0]
        return self
    
    def addCall(self, seat, callValue):
        item = (seat, callValue)
        self.callList.append(item)
        if callValue != 0:
            self.effectiveCallList.append(item)
        seat.status.callValue = callValue
    
    def _newSeatStatus(self, seat):
        return SeatStatus()

class PlayMode(object):
    def __init__(self, name, cardRule, seatCount):
        self.name = name
        self.cardRule = cardRule
        self.seatCount = seatCount

    def isAllReady(self, table):
        '''
        是否所有的座位全部Ready
        '''
        for seat in table.seats:
            if seat.state != DizhuSeat.ST_READY:
                return False
        return True

    def quit(self, table, seat):
        assert (seat.table == table)
        ftlog.info('PlayMode.quit',
                   'roomId=', table.roomId,
                   'tableId=', table.tableId,
                   'seatId=', seat.seatId,
                   'userId=', seat.userId)
        # 将用户位置信息存到redis, 清空大厅的位置信息
        if seat._status:
            seat._status.giveup = True
        if seat.player:
            seat.player.isQuit = 1
        timestamp = pktimestamp.getCurrentTimestamp()
        try:
            if seat.userId:
                onlinedata.removeOnlineLoc(seat.userId, table.roomId, table.tableId)
        except Exception, e:
            ftlog.warn('DizhuTableRoomNormalBase.leaveRoom removeOnlineLoc',
                       'roomId=', table.roomId,
                       'userId=', seat.userId,
                       'ex=', str(e))
        try:
            if seat.userId:
                comm_table_remote.addUserQuitLoc(table.gameId, seat.userId, table.roomId, table.tableId, seat.seatId, timestamp)
        except Exception, e:
            ftlog.warn('DizhuTableRoomNormalBase.leaveRoom addUserQuitLoc',
                       'roomId=', table.roomId,
                       'userId=', seat.userId,
                       'ex=', str(e))

    def removeQuitLoc(self, table, userId):
        try:
            comm_table_remote.removeUserQuitLoc(table.gameId, userId, table.roomId)
        except Exception, e:
            ftlog.debug('DizhuTableRoomNormalBase.leaveRoom removeQuitLoc',
                        'roomId=', table.roomId,
                        'userId=', userId,
                        'ex=', str(e))

    def seatOnlineChanged(self, table, seat, online):
        assert(seat.table == table)
        if ftlog.is_debug():
            ftlog.debug('PlayMode.seatOnlineChanged',
                        'tableId=', table.tableId,
                        'seatId=', seat.seatId,
                        'userId=', seat.userId,
                        'online=', online,
                        'playerOnline=', seat.player.online if seat.player else None)
        if seat.player:
            seat.player.online = online
            table.fire(SeatOnlineChanged(table, seat))

    def sitdown(self, table, player, seat, continueBuyin, isReciveVoice=False):
        '''
        找空闲的座位坐下
        @param isNextBuyin: 结算界面，点击继续的带入标记
        '''
        assert(not seat or seat.table == table)
        if player.seat:
            return player.seat
        
        if not seat:
            seat = table.findIdleSeat()
        
        if not seat:
            raise NoIdleSeatException()
        
        if seat.player:
            raise SeatNotIdleException()
        
        if table.dealer.buyinPolicy:
            table.dealer.buyinPolicy.buyin(table, player, seat, continueBuyin)

        if not player.isQuit:
            onlinedata.setBigRoomOnlineLoc(player.userId, table.roomId, table.tableId, seat.seatId)
        
        # 坐下后自动ready
        seat._state = DizhuSeat.ST_READY if table.runConf.isSitDownAutoReady else DizhuSeat.ST_WAIT
        seat.isReciveVoice = isReciveVoice

        player._seat = seat
        seat._player = player
        
        # 结算界面，点击继续的带入标记
        seat.isNextBuyin = continueBuyin

        if ftlog.is_debug():
            ftlog.info('User sitdown',
                       'tableId=', table.tableId,
                       'seatId=', seat.seatId,
                       'userId=', player.userId,
                       'seatState=', seat.state,
                       'isNextBuyin=', continueBuyin)

        table.fire(SitdownEvent(table, seat, player, continueBuyin))
        
        return seat
    
    def giveup(self, table, seat):
        '''
        放弃牌局
        '''
        assert(seat.table == table)
        if not seat.player:
            raise EmptySeatException()
        
        assert(table.gameRound)
        if not seat.status.giveup:
            seat.status.giveup = True
            if ftlog.is_debug():
                ftlog.info('Seat giveup',
                           'tableId=', table.tableId,
                           'seatId=', seat.seatId,
                           'userId=', seat.userId)

            table.fire(GiveupEvent(table, seat))
            
    def standup(self, table, seat, reason):
        '''
        清空站起的座位
        '''
        assert(seat.table == table)
        
        if not seat.player:
            ftlog.warn('PlayMode.standup',
                       'tableId=', table.tableId,
                       'seatId=', seat.seatId)
            raise EmptySeatException()
        
        assert(table.gameRound is None)
        
        player = seat._player
        
        if table.dealer.buyinPolicy:
            try:
                table.dealer.buyinPolicy.cashin(table, player, seat)
            except Exception, e:
                ftlog.warn('PlayMode.standup cashin',
                           'tableId=', table.tableId,
                           'seatId=', seat.seatId,
                           'userId=', player.userId,
                           'ex=', str(e))
            
        try:
            onlinedata.removeOnlineLoc(player.userId, table.roomId, table.tableId)
        except Exception, e:
            ftlog.warn('PlayMode.standup removeOnlineLoc',
                       'tableId=', table.tableId,
                       'seatId=', seat.seatId,
                       'userId=', player.userId,
                       'ex=', str(e))
        
        seat._player = None
        seat._state = DizhuSeat.ST_IDLE
        seat.isNextBuyin = False
        player._seat = None

        if ftlog.is_debug():
            ftlog.info('Seat standup',
                       'tableId=', table.tableId,
                       'seatId=', seat.seatId,
                       'userId=', player.userId,
                       'reason=', reason)

        table.fire(StandupEvent(table, seat, player, reason))
        
        return player
    
    def ready(self, table, seat, isReciveVoice=False):
        '''
        座位进入ready状态
        '''
        assert(seat.table == table)
        
        if seat.state != DizhuSeat.ST_WAIT:
            ftlog.warn('PlayMode.ready',
                       'tableId=', seat.tableId,
                       'seatId=', seat.seatId,
                       'userId=', seat.player.userId,
                       'seatState=', seat.state,
                       'err=', 'BadState')
            raise BadStateException()
        
        if not seat.player:
            ftlog.warn('PlayMode.ready',
                       'tableId=', seat.tableId,
                       'seatId=', seat.seatId,
                       'userId=', seat.player.userId,
                       'seatState=', seat.state,
                       'err=', 'EmptySeatException')
            raise EmptySeatException()
        
        seat._state = DizhuSeat.ST_READY
        seat.isReciveVoice = isReciveVoice

        if ftlog.is_debug():
            ftlog.info('Seat ready',
                       'tableId=', seat.tableId,
                       'seatId=', seat.seatId,
                       'userId=', seat.player.userId)
        # 发送玩家准备事件
        table.fire(SeatReadyEvent(table, seat))
        
        return seat
    
    def gameReady(self, table):
        '''
        发牌，选择首叫，初始化gameRound
        '''
        gameRound = table.dealer.newGameRound(table)
        table.dealer.sendCardsPolicy.sendCards(table)
        
        seatCards = [seat.status.cards[:] for seat in gameRound.seats]
        baseCards = gameRound.baseCards[:]
        
        gameRound.firstCallSeat = table.dealer.firstCallPolicy.chooseFirstCall(table)

        if ftlog.is_debug():
            ftlog.info('Table gameReady',
                       'tableId=', table.tableId,
                       'roundId=', gameRound.roundId,
                       'seatCards=', seatCards,
                       'baseCards=', baseCards,
                       'firstCallSeat=', gameRound.firstCallSeat.seatId)
        
        table.fire(GameReadyEvent(table, seatCards, baseCards, gameRound.firstCallSeat))
        
    def moveCurOpSeat(self, table, seat, optime, autoOp):
        '''
        移动当前操作者
        '''
        gameRound = table.gameRound
        prevOpSeat = gameRound.curOpSeat
        gameRound.curOpSeat = seat

        if ftlog.is_debug():
            ftlog.info('Table moveCurOpSeat',
                       'tableId=', table.tableId,
                       'roundId=', gameRound.roundId,
                       'seat=', seat.seatId,
                       'optime=', optime,
                       'autoOp=', autoOp)
        
        table.fire(CurOpSeatMoveEvent(table, prevOpSeat, seat, optime, autoOp))
    
    def gameStart(self, table):
        '''
        底牌加到地主的手牌里
        '''
        gameRound = table.gameRound

        # 底牌插入地主手牌
        gameRound.dizhuSeat.status.cards.extend(gameRound.baseCards)
        
        ftlog.info('Table gameStart',
                   'tableId=', table.tableId,
                   'roundId=', gameRound.roundId,
                   'dizhuSeat=', gameRound.dizhuSeat.seatId,
                   'seatUsers=', [seat.userId for seat in gameRound.seats])
        
        table.fire(GameStartEvent(table))
        
    def showCards(self, table, seat):
        assert(seat.table == table)
        if not seat.status.isShowCards:
            seat.status.isShowCards = True
            table.gameRound.showMulti = 2
            ftlog.info('Table showCards',
                       'tableId=', table.tableId,
                       'userId=', seat.userId,
                       'seatId=', seat.seatId)
            table.fire(ShowCardEvent(table, seat))
    
    def callTimeout(self, table, seat):
        assert(seat.table == table)
        
        gameRound = table.gameRound
        # 检查是否是当前操作座位
        if seat != gameRound.curOpSeat:
            raise BadOpSeatException()
        
        seat.status.timeoutCount += 1
        
        if seat.status.timeoutCount >= table.runConf.robotTimes:
            # 超过robotTimes则托管
            table.dealer.playMode.tuoguan(table, seat, True, Oper.ROBOT, TuoguanLoction.CALLING)

        callValue = table.dealer.tuoguanPolicy.callValueForTuoguan(table, seat)
        
        ftlog.info('User callTimeout',
                   'tableId=', seat.tableId,
                   'roundId=', gameRound.roundId,
                   'seatId=', seat.seatId,
                   'userId=', seat.player.userId,
                   'timeoutCount=', seat.status.timeoutCount,
                   'callValue=', callValue)
        
        table.fire(CallTimeoutEvent(table, seat))
        
        return callValue
    
    def call(self, table, seat, callValue, oper):
        '''
        叫地主
        '''
        assert(seat.table == table)
        
        gameRound = table.gameRound
        # 检查是否是当前操作座位
        if seat != gameRound.curOpSeat:
            raise BadOpSeatException()

        seat.player.callOper = oper
        callResult, nextSeat = table.dealer.callPolicy.call(table, callValue, oper)
            
        ftlog.info('User call',
                   'userId=', seat.player.userId,
                   'tableId=', seat.tableId,
                   'roundId=', gameRound.roundId,
                   'seatId=', seat.seatId,
                   'callValue=', callValue,
                   'oper=', oper,
                   'callResult=', callResult,
                   'nextSeatId=', nextSeat.seatId if nextSeat else None)
        
        table.fire(CallEvent(table, seat, callValue, oper, callResult))
        
        return callResult, nextSeat
    
    def tuoguanOutCard(self, table, seat, tuoguanType):
        '''
        托管出牌牌型获取
        '''
        assert(seat.table == table)
        
        gameRound = table.gameRound
        # 检查是否是当前操作座位
        if seat != gameRound.curOpSeat:
            raise BadOpSeatException()
        
        validCards = table.dealer.tuoguanPolicy.outCardForTuoguan(table, seat, tuoguanType)

        if ftlog.is_debug():
            ftlog.info('User tuoguanOutCard',
                       'tableId=', seat.tableId,
                       'roundId=', gameRound.roundId,
                       'seatId=', seat.seatId,
                       'userId=', seat.player.userId,
                       'tuoguanType=', tuoguanType,
                       'cards=', validCards.cards if validCards else None)
        return validCards
        
    def outCardTimeout(self, table, seat):
        '''
        超时出牌牌型获取
        '''
        assert(seat.table == table)
        
        gameRound = table.gameRound
        # 检查是否是当前操作座位
        if seat != gameRound.curOpSeat:
            raise BadOpSeatException()
        
        seat.status.timeoutCount += 1
        
        if seat.status.timeoutCount >= table.runConf.robotTimes:
            # 超过robotTimes则托管
            table.dealer.playMode.tuoguan(table, seat, True, Oper.ROBOT, TuoguanLoction.OUT_CARD)

        validCards = table.dealer.tuoguanPolicy.outCardForTuoguan(table, seat, TuoguanType.TIMEOUT)
        
        if ftlog.is_debug():
            ftlog.info('User outCardTimeout',
                       'tableId=', seat.tableId,
                       'roundId=', gameRound.roundId,
                       'seatId=', seat.seatId,
                       'userId=', seat.player.userId,
                       'timeoutCount=', seat.status.timeoutCount,
                       'cards=', validCards.cards if validCards else None)
        
        table.fire(OutCardTimeoutEvent(table, seat))
        return validCards
    
    def outCard(self, table, seat, validCards, oper):
        '''
        出牌
        '''
        assert(seat.table == table)
        
        gameRound = table.gameRound
        # 检查是否是当前操作座位
        if seat != gameRound.curOpSeat:
            raise BadOpSeatException()
        
        # 主动出牌(没有上家出牌，或者上家也是自己出牌)
        if not gameRound.topSeat or gameRound.topSeat == seat:
            # 主动出牌，必须出
            if not validCards:
                # TODO log
                raise BadCardException()
        else:
            # 被动出牌要么不出，要么出牌必须能管住topValidCards
            if (validCards
                and not validCards.isGreaterThan(gameRound.topValidCards)):
                ftlog.warn('BadCard',
                           'tableId=', seat.tableId,
                           'roundId=', gameRound.roundId,
                           'seatId=', seat.seatId,
                           'userId=', seat.player.userId,
                           'oper=', oper,
                           'topValidCards=', gameRound.topValidCards.cards,
                           'topValidCardsHuman=', self.cardRule.toHumanCards(gameRound.topValidCards.cards),
                           'cards=', validCards.cards if validCards else None,
                           'cardsHuman=', self.cardRule.toHumanCards(validCards.cards) if validCards else None)
                raise BadCardException()
        
        # 记录出牌之前的牌型
        prevCards = seat.status.cards[:]
        
        if validCards:
            # 从手牌中减去cards
            seatCards = seat.status.cards[:]
            realCards = self._changeToRealCards(table, validCards.cards)
            
            if not self._removeCards(seatCards, realCards):
                # TODO log
                raise BadCardException()
            
            # 设置手牌为出牌后的牌
            seat.status.outCardTimes += 1
            seat.status.cards = seatCards
            gameRound.topSeat = seat
            gameRound.topValidCards = validCards
            if validCards.isHuoJian() or validCards.isZhaDan():
                gameRound.bombCount += 1

        seat.status.outCards.append(validCards.cards if validCards else [])
        gameRound.cardCrc += 1

        if ftlog.is_debug():
            ftlog.info('User outCard',
                       'tableId=', seat.tableId,
                       'roundId=', gameRound.roundId,
                       'seatId=', seat.seatId,
                       'userId=', seat.userId,
                       'oper=', oper,
                       'cardCrc=', gameRound.cardCrc,
                       'cards=', validCards.cards if validCards else [],
                       'seatCards=', seat.status.cards,
                       'outCards=', seat.status.outCards
                       )
        
        table.fire(OutCardEvent(table, seat, validCards, prevCards, oper))

        if not self._isGameOver(table):
            return OutCardResult.PLAYING, seat.next
        
        gameRound.firstWinSeat = seat
        
        return OutCardResult.FINISH, None
        
    def clearGame(self, table, keepPlayer, reason):
        table.cancelTimer()
        gameRound, table._gameRound = table._gameRound, None

        usersForQuit = []
        for seat in table.seats:
            seat.cancelTimer()
            seat._status = None
            seat._state = DizhuSeat.ST_WAIT if seat.player else DizhuSeat.ST_IDLE
            if seat.player:
                if seat.player.isQuit:
                    usersForQuit.append(seat.userId)
                seat.player.inningCardNote = 0

        if not keepPlayer:
            if reason == ClearGameReason.GAME_KILL:
                standupReason = StandupReason.FORCE_CLEAR
            else:
                standupReason = StandupReason.GAME_OVER if ClearGameReason.GAME_OVER == reason else StandupReason.GAME_ABORT
            for seat in table.seats:
                if seat.player:
                    isQuit = seat.player.isQuit
                    userId = seat.player.userId
                    self.standup(table, seat, standupReason)
                    if isQuit:
                        table._quitClear(userId)

        ftlog.info('ClearGame',
                   'usersForQuit=', usersForQuit,
                   'tableId=', table.tableId,
                   'roundId=', gameRound.roundId if gameRound else None,
                   'keepPlayer=', keepPlayer,
                   'reason=', reason)
        table.fire(GameClearEvent(table, reason))
    
    @staticmethod
    def isAbortRestart(table, seats):
        if table.runConf.abortRestartSwitch <= 0:
            return False
        
        '''判断3个座位的clientVer是否满足'''
        for seat in seats:
            if seat.player.gameClientVer < table.runConf.abortRestartMinVer:
                if ftlog.is_debug():
                    ftlog.debug('Abort ClientVerTooOld'
                                'tableId=', table.tableId,
                                'roundId=', table.gameRound.roundId,
                                'clientVer=', seat.player.gameClientVer,
                                'targetVer=', table.runConf.abortRestartMinVer,
                                'userId=', seat.userId)
                if not seat.player.isRobotUser:
                    return False

        operForRobot = 0
        for seat in seats:
            if seat.player.callOper == Oper.ROBOT or seat.player.isRobotUser:
                operForRobot += 1
            if operForRobot >= 2:
                return False

        tuoguanNum = 0
        for seat in seats:
            if seat.status.isTuoguan:
                tuoguanNum += 1
            if tuoguanNum >= 2:
                return False
            
        return True
    
    def abortClearGame(self, table):
        '''流局清理'''
        if ftlog.is_debug():    
            ftlog.debug('Abort GameRoundClear '
                        'tableId=', table.tableId,
                        'roundId=', table.gameRound.roundId)
            
        for seat in table.seats:
            seat.cancelTimer()
            seat._status = None
            seat._state = DizhuSeat.ST_READY
            seat.player.inningCardNote = 0
            
        table.cancelTimer()
        table._gameRound = None
        table.fire(GameClearEvent(table, ClearGameReason.GAME_ABORT))
        
    def gameAbort(self, table):
        '''
        流局
        '''
        ftlog.info('GameRoundAbort',
                   'tableId=', table.tableId,
                   'roundId=', table.gameRound.roundId)
        
        gameResult = table.dealer.settlementPolicy.calcResult(table.gameRound)
        
        table.fire(GameRoundFinishEvent(table, gameResult))
        
        try:
            table.dealer.settlementPolicy.settlement(gameResult)
        except Exception, e:
            ftlog.warn('GameRoundAbort',
                       'tableId=', table.tableId,
                       'roundId=', table.gameRound.roundId,
                       'statement=', [(sst.cardNoteFee, sst.fee, sst.winnerTax, sst.delta, sst.final) for sst in gameResult.seatStatements],
                       'ex=', str(e))

        table.fire(GameRoundAbortEvent(table, gameResult))
        
    def gameOver(self, table):
        '''
        游戏结束
        '''
        ftlog.info('GameRoundOver',
                   'tableId=', table.tableId,
                   'roundId=', table.gameRound.roundId,
                   'winSeat=', (table.gameRound.curOpSeat.userId, table.gameRound.curOpSeat.seatId))
        
        self._finishGameRound(table)

        gameResult = table.dealer.settlementPolicy.calcResult(table.gameRound)
        
        table.fire(GameRoundFinishEvent(table, gameResult))

        try:
            table.dealer.settlementPolicy.settlement(gameResult)
        except Exception, e:
            ftlog.warn('GameRoundOver',
                       'tableId=', table.tableId,
                       'roundId=', table.gameRound.roundId,
                       'statement=', [(sst.cardNoteFee, sst.fee, sst.winnerTax, sst.delta, sst.final) for sst in gameResult.seatStatements],
                       'ex=', str(e))
        
        table.fire(GameRoundOverEvent(table, gameResult))
        
    def tuoguan(self, table, seat, isTuoguan, oper, location=0):
        ''' 
        托管
        '''
        if seat.status.isTuoguan == isTuoguan:
            return False
        
        seat.status.isTuoguan = isTuoguan
        
        if not isTuoguan:
            seat.status.timeoutCount = 0
            seat.status.isPunish = False
        else:
            if len(seat.status.cards) > table.runConf.punishCardCount:
                seat.status.isPunish = True

        if ftlog.is_debug():
            ftlog.info('Tuoguan',
                       'tableId=', table.tableId,
                       'roundId=', table.gameRound.roundId,
                       'seatId=', seat.seatId,
                       'isTuoguan=', seat.status.isTuoguan,
                       'oper=', oper,
                       'isPunish=', seat.status.isPunish)
        
        table.fire(TuoguanEvent(table, seat, isTuoguan, oper, location))
        return True

    def autoplay(self, table, seat, isAutoPlay, oper):
        '''
        农民最后一手自动出牌
        '''
        if seat.status.isAutoPlay == isAutoPlay:
            return False

        if seat == seat.table.gameRound.dizhuSeat:
            return False

        ftlog.info('Autoplay',
                   'tableId=', table.tableId,
                   'roundId=', table.gameRound.roundId,
                   'seat=', (seat.userId, seat.seatId),
                   'isAutoPlay=', seat.status.isAutoPlay,
                   'oper=', oper)
        seat.status.isAutoPlay = isAutoPlay
        table.fire(AutoPlayEvent(table, seat, isAutoPlay, oper))
        return True
    
    def startNongminJiabei(self, table):
        '''
        开始农民加倍
        '''
        ftlog.info('StartNongminJiabei',
                   'tableId=', table.tableId,
                   'roundId=', table.gameRound.roundId)
        
        table.fire(StartNongminJiabeiEvent(table))
    
    def startDizhuJiabei(self, table):
        '''
        开始农民加倍
        '''
        ftlog.info('StartDizhuJiabei',
                   'tableId=', table.tableId,
                   'roundId=', table.gameRound.roundId)
        
        table.fire(StartDizhuJiabeiEvent(table))

    def isSeatJiabei(self, seat):
        '''
        座位是否已经加倍 
        '''
        return seat.status.seatMulti > 0
    
    def nongminJiabei(self, table, seat, multi, oper):
        ''' 
        农民加倍
        @param multi: 倍数
        '''
        # 若已经加倍则发生错误
        if seat == table.gameRound.dizhuSeat or self.isSeatJiabei(seat):
            raise BadJiabeiException()
        
        seat.status.seatMulti = multi
        
        ftlog.info('NongminJiabei',
                   'tableId=', table.tableId,
                   'roundId=', table.gameRound.roundId,
                   'seatId=', seat.seatId,
                   'multi=', multi)
         
        table.fire(NongminJiabeiEvent(table, seat, multi, oper))
    
    def dizhuJiabei(self, table, seat, multi, oper):
        ''' 
        地主加倍
        @param multi: 倍数
        '''
        # 若已经加倍则发生错误
        if seat != table.gameRound.dizhuSeat or self.isSeatJiabei(seat):
            raise BadJiabeiException()
        
        seat.status.seatMulti = multi
        
        ftlog.info('DizhuJiabei',
                   'tableId=', table.tableId,
                   'roundId=', table.gameRound.roundId,
                   'seatId=', seat.seatId,
                   'multi=', multi)
         
        table.fire(DizhuJiabeiEvent(table, seat, multi, oper))
    
    def isSeatDizhu(self, table, seat):
        ''' 是否是地主 '''
        return table.gameRound.dizhuSeat == seat
    
    def isSeatHuanpaiOutcard(self, table, seat):
        ''' 座位是否已经出牌了 '''
        return bool(seat.status.huanpaiOutcards)
    
    def isSeatHuanpaiIncard(self, table, seat):
        ''' 座位是否已经取得交换牌了 '''
        return bool(seat.status.huanpaiIncards)
    
    def startHuanpai(self, table):
        ''' 
        开始换牌
        '''
        if ftlog.is_debug():
            ftlog.info('StartHuanpai',
                       'tableId=', table.tableId,
                       'roundId=', table.gameRound.roundId)
        
        table.fire(StartHuanpaiEvent(table))

    def huanpaiSeatOutcards(self, table, seat, outCards, oper):
        ''' 
        换牌出牌
        '''
        if self.isSeatHuanpaiOutcard(table, seat):
            raise BadHuanpaiException('seat already out cards')
        if table.runConf.huanpaiCardCount != len(outCards):
            raise BadHuanpaiException('outCards num not match')
        
        seatCards = seat.status.cards[:]
        if not self._removeCards(seatCards, outCards):
            raise BadHuanpaiException('seat not have outCards')
        
        seat.status.cards = seatCards
        seat.status.huanpaiOutcards = outCards

        if ftlog.is_debug():
            ftlog.info('HuanpaiSeatOutcards',
                       'tableId=', table.tableId,
                       'roundId=', table.gameRound.roundId,
                       'seatId=', seat.seatId,
                       'outCards=', outCards,
                       'seatCards=', seatCards)

        table.fire(HuanpaiOutcardsEvent(table, seat, outCards, oper))

    def huanpaiEnd(self, table):
        ''' 换牌结束阶段，真实交换牌型 '''
        # 交换牌
        for seat in table.gameRound.seats:
            if not self.isSeatHuanpaiOutcard(table, seat) or self.isSeatHuanpaiIncard(table, seat):
                raise BadHuanpaiException()

        gameRound = table.gameRound
        seats = gameRound.seats[:]
        # 旋转方向，顺时针逆时针概率各50%, 0: 顺时针， 1: 逆时针
        turnDirection = random.randint(0, 1)
        if turnDirection == 1:
            seats.reverse()
        seats.append(seats[0])
        
        for i in xrange(len(seats) - 1):
            inSeat, outSeat = seats[i + 1], seats[i]
            inSeat.status.huanpaiIncards = outSeat.status.huanpaiOutcards
            inSeat.status.cards.extend(inSeat.status.huanpaiIncards)
            if ftlog.is_debug():
                ftlog.info('HuanpaiEnd',
                           'tableId=', table.tableId,
                           'roundId=', table.gameRound.roundId,
                           'outCards=', inSeat.status.huanpaiOutcards,
                           'incards=', inSeat.status.huanpaiIncards,
                           'seatCards=', inSeat.status.cards)
            table.fire(HuanpaiIncardsEvent(table, inSeat, inSeat.status.huanpaiIncards))
        table.fire(HuanpaiEndEvent(table, turnDirection=turnDirection))
            
    def chat(self, table, seat, isFace, msg, voiceIdx):
        '''
        聊天
        '''
        if isFace == 2:
            table.fire(ChatEvent(table, seat, isFace, voiceIdx, msg))
            return
        
        chatMsg = msg[:80]  # 80个字符长度限制
        if isFace == 0:
            table.fire(ChatEvent(table, seat, isFace, voiceIdx, chatMsg))
            return

        if isFace == 1: 
            # 表情图片
            table.fire(ChatEvent(table, seat, isFace, voiceIdx, chatMsg))
            
    def _changeToRealCards(self, table, cards):
        return cards
    
    def _removeCards(self, srcCards, cards):
        for c in cards:
            try:
                srcCards.remove(c)
            except:
                return False
        return True
    
    def _newGameRound(self, table):
        return GameRound()
    
    def _isGameOver(self, table):
        return len(table.gameRound.curOpSeat.status.cards) == 0

    def _calcChuntian(self, gameRound):
        if not gameRound.dizhuSeat:
            return False
        if gameRound.curOpSeat == gameRound.dizhuSeat:
            # 地主胜利
            for seat in gameRound.seats:
                if (seat != gameRound.dizhuSeat
                    and seat.status.outCardTimes > 0):
                    return False
            return True
        # 农民胜利
        if gameRound.dizhuSeat.status.outCardTimes > 1:
            return False
        return True

    def _calcRangpaiMulti(self, gameRound):
        return 1
        
    def calcTotalMulti(self, gameRound):
        totalMulti = max(1, gameRound.callMulti)
        totalMulti *= pow(2, gameRound.bombCount)
        if gameRound.isChuntian:
            totalMulti *= 2
        totalMulti *= gameRound.baseCardMulti
        totalMulti *= gameRound.showMulti
        totalMulti *= gameRound.rangpaiMulti
        if ftlog.is_debug():
            ftlog.debug('PlayMode.calcTotalMulti',
                        'tableId=', gameRound.table.tableId,
                        'roundId=', gameRound.roundId,
                        'callMulti=', gameRound.callMulti,
                        'bombMulti=', pow(2, gameRound.bombCount),
                        'chuntianMulti=', 2 if gameRound.isChuntian else 1,
                        'baseCardMulti=', gameRound.baseCardMulti,
                        'showMulti=', gameRound.showMulti,
                        'rangpaiMulti=', gameRound.rangpaiMulti,
                        'ret=', totalMulti)
        return totalMulti
    
    def _finishGameRound(self, table):
        # 计算春天
        gameRound = table.gameRound
        assert gameRound.dizhuSeat
        gameRound.isChuntian = self._calcChuntian(gameRound)
        gameRound.result = GameRound.RESULT_DIZHU_WIN if gameRound.curOpSeat == gameRound.dizhuSeat else GameRound.RESULT_NONGMIN_WIN
        gameRound.rangpaiMulti = self._calcRangpaiMulti(gameRound)
        gameRound.totalMulti = self.calcTotalMulti(gameRound)
        for seat in gameRound.seats:
            if seat != gameRound.dizhuSeat:
                seat.status.totalMulti = gameRound.totalMulti
                if seat.status.seatMulti > 1:
                    seat.status.totalMulti *= seat.status.seatMulti
                    if gameRound.dizhuSeat.status.seatMulti > 1:
                        seat.status.totalMulti *= gameRound.dizhuSeat.status.seatMulti
                gameRound.dizhuSeat.status.totalMulti += seat.status.totalMulti

        if ftlog.is_debug():
            ftlog.debug('PlayMode._finishGameRound',
                        'tableId=', gameRound.table.tableId,
                        'roundId=', gameRound.roundId,
                        'isChuntian=', gameRound.isChuntian,
                        'rangpaiMulti=', gameRound.rangpaiMulti,
                        'baseCardMulti=', gameRound.baseCardMulti,
                        'totalMulti=', gameRound.totalMulti,
                        'result=', gameRound.result,
                        'seats=', [(s.userId, s.seatId, s.status.seatMulti, s.status.totalMulti) for s in gameRound.seats])


class DealerBase(object):
    def __init__(self, sm, playMode, jiabeiMode, roundIdGenPolicy, callPolicy, sendCardsPolicy, firstCallPolicy, tuoguanPolicy, buyinPolicy, autoChupaiPolicy, settlementPolicy):
        self.sm = sm
        self.playMode = playMode
        self.jiabeiMode = jiabeiMode
        self.roundIdGenPolicy = roundIdGenPolicy
        self.callPolicy = callPolicy
        self.sendCardsPolicy = sendCardsPolicy
        self.firstCallPolicy = firstCallPolicy
        self.tuoguanPolicy = tuoguanPolicy
        self.buyinPolicy = buyinPolicy
        self.autoChupaiPolicy = autoChupaiPolicy
        self.settlementPolicy = settlementPolicy

    def newGameRound(self, table):
        '''
        创建一局游戏
        '''
        roundId = self.roundIdGenPolicy.genRoundId(table)
        gameRound = GameRound()
        gameRound.init(table, roundId, table.seats[:])
        table._gameRound = gameRound
        return gameRound
