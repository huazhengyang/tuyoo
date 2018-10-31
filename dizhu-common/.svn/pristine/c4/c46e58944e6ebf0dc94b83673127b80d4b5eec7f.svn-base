# -*- coding:utf-8 -*-
'''
Created on 2016年11月24日

@author: zhaojiangang
'''
from dizhucomm.core.base import TableState
from dizhucomm.core.commands import SitdownCommand, ReadyTimeoutCommand, \
    ReadyCommand, CallTimeupCommand, CallCommand, OutCardTimeupCommand, \
    OutCardCommand, TuoguanCommand, JiabeiTimeupCommand, JiabeiCommand, \
    HuanpaiTimeupCommand, HuanpaiOutcardsCommand, StandupCommand, GiveupCommand, \
    ShowCardCommand, ClearGameCommand, AutoPlayCommand
from dizhucomm.core.const import StandupReason, Oper, CallResult, OutCardResult, \
    TuoguanType, JiabeiMode, ClearGameReason, TuoguanLoction
from dizhucomm.core.exceptions import BadOpSeatException, BadCardCrcException
from freetime.core.tasklet import FTTasklet
from freetime.util import log as ftlog
from dizhucomm.core.table import DizhuSeat
import poker.util.timestamp as pktimestamp

class BaseActions(object):
    @classmethod
    def sitdownAction(cls, cmd):
        '''
        坐下
        '''
        if not isinstance(cmd, SitdownCommand):
            return TableState.STATE_CONTINUE
            
        seat = cmd.playMode.sitdown(cmd.table, cmd.player, cmd.seat, cmd.isNextBuyin, True)
            
        # 所有座位都ready后，发牌，叫地主
        if cmd.playMode.isAllReady(cmd.table):
            if cmd.table.runConf.huanpaiCardCount > 0:
                if ftlog.is_debug():
                    ftlog.debug('BaseActions.sitdownAction',
                                'tableId=', cmd.table.tableId,
                                'isAllReady', True,
                                'stat=', cmd.table.state.name,
                                'nextStat=', 'huanpai')
                return cmd.table.sm.findStateByName('huanpai')
            else:
                return cmd.table.sm.findStateByName('calling')
        
        # 未准备且ready超时则站起
        if seat.state != DizhuSeat.ST_READY and cmd.table.runConf.readyTimeout:
            seat.startTimer(cmd.table.runConf.readyTimeout,
                            cmd.table.processCommand,
                            ReadyTimeoutCommand(seat))
            
        return TableState.STATE_DONE
    
    @classmethod
    def readyAction(cls, cmd):
        '''
        只处理ReadyCommand
        '''
        if not isinstance(cmd, ReadyCommand):
            return TableState.STATE_CONTINUE
        
        cmd.playMode.ready(cmd.table, cmd.seat, cmd.isReciveVoice)
        
        cmd.seat.cancelTimer()
        
        # 所有座位都ready后，发牌，叫地主 或者 换牌
        if cmd.playMode.isAllReady(cmd.table):
            if cmd.table.runConf.huanpaiCardCount > 0:
                if ftlog.is_debug():
                    ftlog.debug('BaseActions.readyAction',
                                'tableId=', cmd.table.tableId,
                                'isAllReady', True,
                                'stat=', cmd.table.state.name,
                                'nextStat=', 'huanpai')
                return cmd.table.sm.findStateByName('huanpai')
            else:
                return cmd.table.sm.findStateByName('calling')
        
        return TableState.STATE_DONE
    
    @classmethod
    def readyTimeoutAction(cls, cmd):
        '''
        只处理ReadyCommand
        '''
        if not isinstance(cmd, ReadyTimeoutCommand):
            return TableState.STATE_CONTINUE

        if cmd.seat.player:
            cmd.playMode.standup(cmd.table, cmd.seat, StandupReason.READY_TIMEOUT)
        
        cmd.seat.cancelTimer()
        
        return TableState.STATE_DONE
    
    @classmethod
    def standupAction(cls, cmd):
        '''
        站起，处理StandupCommand
        '''
        if not isinstance(cmd, StandupCommand):
            return TableState.STATE_CONTINUE
        
        assert(not cmd.table.gameRound)
        
        if cmd.seat.player:
            cmd.playMode.standup(cmd.table, cmd.seat, cmd.reason)
        
        cmd.seat.cancelTimer()
        
        return TableState.STATE_DONE
    
    @classmethod
    def giveupAction(cls, cmd):
        if not isinstance(cmd, GiveupCommand):
            return TableState.STATE_CONTINUE
        
        assert(cmd.table.gameRound)
        cmd.playMode.giveup(cmd.table, cmd.seat)
        
        return TableState.STATE_DONE
    
    @classmethod
    def gameReadyAction(cls, cmd):
        # 换牌
        if cmd.table.runConf.huanpaiCardCount <= 0:
            # 发牌，选择首叫
            cmd.playMode.gameReady(cmd.table)
        gameRound = cmd.table.gameRound
        # ???为什么延时，等待客户端动画吗???
        if cmd.table.runConf.firstCallDelayTimes > 0:
            FTTasklet.getCurrentFTTasklet().sleepNb(cmd.table.runConf.firstCallDelayTimes)

        seat = gameRound.firstCallSeat
        
        if seat.status.isTuoguan:
            optime = cmd.table.runConf.optimeTuoguan
        else:
            optime = cmd.table.runConf.optimeCall

        # 移动curOpSeat
        cmd.playMode.moveCurOpSeat(cmd.table, seat, optime, seat.status.isTuoguan)
        
        # 启动叫地主计时器
        seat.startTimer(optime,
                        cmd.table.processCommand,
                        CallTimeupCommand(seat))
            
        return TableState.STATE_CONTINUE

    @classmethod
    def gameReadyForHuanpaiAction(cls, cmd):
        # 发牌，选择首叫
        cmd.playMode.gameReady(cmd.table)
    
    @classmethod
    def callAction(cls, cmd):
        '''
        只处理CallCommand
        '''
        if not isinstance(cmd, (CallCommand, CallTimeupCommand)):
            return TableState.STATE_CONTINUE
        
        gameRound = cmd.table.gameRound
        # 检查是否是当前操作座位
        if cmd.seat != gameRound.curOpSeat:
            if isinstance(cmd, CallCommand):
                ftlog.warn('BaseActions.callAction',
                           'tableId=', cmd.table.tableId,
                           'cmd.seat=', (cmd.seat.userId, cmd.seat.seatId),
                           'curOpSeat=', (gameRound.curOpSeat.userId, gameRound.curOpSeat.seatId),
                           'callValue=', cmd.callValue,
                           'err=', 'BadOpSeat')
                raise BadOpSeatException()
            else:
                ftlog.warn('BaseActions.callAction',
                           'tableId=', cmd.table.tableId,
                           'cmd.seat=', (cmd.seat.userId, cmd.seat.seatId),
                           'curOpSeat=', (gameRound.curOpSeat.userId, gameRound.curOpSeat.seatId),
                           'err=', 'BadOpSeat')
                return TableState.STATE_DONE
            
        if isinstance(cmd, CallCommand):
            oper = Oper.USER
            callValue = cmd.callValue
        else:
            oper = Oper.ROBOT
            # 超时托管，前端不显示托管标记，玩家也无需进行“取消托管”操作。
            # 记录叫牌超时的标记，用户出牌超时是否置托管
            cmd.seat.status.isCallUpTimeout = True
            if cmd.seat.player.winloseForTuoguan:
                cmd.seat.player.winloseForTuoguan = False
                callValue = cmd.playMode.callTimeout(cmd.table, cmd.seat)
            else:
                callValue = cmd.table.dealer.tuoguanPolicy.callValueForTuoguan(cmd.table, cmd.seat)

        callResult, nextSeat = cmd.playMode.call(cmd.table, cmd.seat, callValue, oper)
    
        # 取消定时器
        cmd.seat.cancelTimer()
    
        if callResult == CallResult.ABORT:
            # 流局
            return cmd.table.sm.findStateByName('final')
        elif callResult == CallResult.FINISH:
            assert(cmd.table.gameRound.dizhuSeat)
            # 决定了地主
            if cmd.table.runConf.jiabei:
                # 需要加倍
                if cmd.table.dealer.jiabeiMode == JiabeiMode.AFTER_FLIP_BASE_CARD:
                    return cmd.table.sm.findStateByName('playing.nongminjiabei')
                else:
                    return cmd.table.sm.findStateByName('nongminjiabei')
            # 直接开始出牌
            return cmd.table.sm.findStateByName('playing.chupai')
        else:
            # 继续叫地主
            assert(nextSeat)
            
            optime = cmd.table.runConf.optimeTuoguan if nextSeat.status.isTuoguan else cmd.table.runConf.optimeCall

            cmd.playMode.moveCurOpSeat(cmd.table, nextSeat, optime, nextSeat.status.isTuoguan)
            
            if nextSeat.status.isTuoguan:
                callValue = cmd.table.dealer.tuoguanPolicy.callValueForTuoguan(cmd.table, cmd.seat)
                nextSeat.startTimer(optime,
                                    cmd.table.processCommand,
                                    CallCommand(gameRound.curOpSeat, callValue, Oper.ROBOT))
            else:
                nextSeat.startTimer(optime,
                                    cmd.table.processCommand,
                                    CallTimeupCommand(gameRound.curOpSeat))
            
        return TableState.STATE_DONE
    
    @classmethod
    def gameStartAction(cls, cmd):
        '''
        底牌加到地主的手牌里
        '''
        cmd.playMode.gameStart(cmd.table)
        
        return TableState.STATE_CONTINUE
    
    @classmethod
    def showCardsAction(cls, cmd):
        '''
        明牌
        '''
        if not isinstance(cmd, ShowCardCommand):
            return TableState.STATE_CONTINUE
        cmd.playMode.showCards(cmd.table, cmd.seat)
        return TableState.STATE_DONE
        
    @classmethod
    def startChupaiAction(cls, cmd):
        seat = cmd.table.gameRound.dizhuSeat
        
        optime = cmd.table.runConf.optimeTuoguan if seat.status.isTuoguan else cmd.table.runConf.optimeFirst

        # 地主变为当前操作者
        cmd.playMode.moveCurOpSeat(cmd.table, seat, optime, seat.status.isTuoguan)
        
        if seat.status.isTuoguan:
            validCards = cmd.table.dealer.tuoguanPolicy.outCardForTuoguan(cmd.table, seat, TuoguanType.ALREADY_TUOGUAN)
            seat.startTimer(optime,
                            cmd.table.processCommand,
                            OutCardCommand(seat, validCards, cmd.table.gameRound.cardCrc, Oper.ROBOT))
        else:
            # 启动出牌计时器
            seat.startTimer(optime,
                            cmd.table.processCommand,
                            OutCardTimeupCommand(seat))
            seat.status.startChupaiTimestamp = pktimestamp.getCurrentTimestamp()
        
        return TableState.STATE_CONTINUE
    
    @classmethod
    def outCardAction(cls, cmd):
        if not isinstance(cmd, (OutCardCommand, OutCardTimeupCommand)):
            return TableState.STATE_CONTINUE
        
        # 检查是否是当前操作座位
        if cmd.seat != cmd.table.gameRound.curOpSeat:
            if isinstance(cmd, OutCardCommand):
                ftlog.warn('BaseActions.outCardAction',
                           'tableId=', cmd.table.tableId,
                           'cmd.seat=', (cmd.seat.userId, cmd.seat.seatId),
                           'curOpSeat=', (cmd.table.gameRound.curOpSeat.userId, cmd.table.gameRound.curOpSeat.seatId),
                           'outCards=', cmd.playMode.cardRule.toHumanCards(cmd.validCards.cards) if cmd.validCards else [],
                           'err=', 'BadOpSeat')
                raise BadOpSeatException()
            else:
                ftlog.warn('BaseActions.outCardAction',
                           'tableId=', cmd.table.tableId,
                           'cmd.seat=', (cmd.seat.userId, cmd.seat.seatId),
                           'curOpSeat=', (cmd.table.gameRound.curOpSeat.userId, cmd.table.gameRound.curOpSeat.seatId),
                           'err=', 'BadOpSeat')
                return TableState.STATE_DONE

        if isinstance(cmd, OutCardCommand):
            if cmd.cardCrc != cmd.table.gameRound.cardCrc:
                ftlog.warn('BaseActions.outCardAction',
                           'tableId=', cmd.table.tableId,
                           'cmd.seat=', (cmd.seat.userId, cmd.seat.seatId),
                           'cardCrc=', (cmd.cardCrc, cmd.table.gameRound.cardCrc),
                           'err=', 'BadCardCRC')
                raise BadCardCrcException()
            oper = cmd.oper
            validCards = cmd.validCards
            if not cmd.seat.status.isTuoguan:
                cmd.seat.status.outCardSeconds += max(0, pktimestamp.getCurrentTimestamp() - cmd.seat.status.startChupaiTimestamp)
                if ftlog.is_debug():
                    ftlog.debug('BaseActions.outCardAction',
                                'tableId=', cmd.table.tableId,
                                'cmd.seat=', (cmd.seat.userId, cmd.seat.seatId),
                                'currentTimestamp=', pktimestamp.getCurrentTimestamp(),
                                'startChupaiTimestamp=', cmd.seat.status.startChupaiTimestamp,
                                'outCardSeconds=', cmd.seat.status.outCardSeconds)
        else:
            oper = Oper.ROBOT
            if not cmd.table.gameRound.topSeat or cmd.table.gameRound.topSeat == cmd.seat:
                # 若玩家超时，前端不显示托管标记，玩家也无需进行“取消托管”操作。
                if cmd.seat.status.isPassedTuoguan:
                    validCards = cmd.playMode.outCardTimeout(cmd.table, cmd.seat)
                else:
                    cmd.seat.status.isPassedTuoguan = True
                    validCards = cmd.table.dealer.tuoguanPolicy.outCardForTuoguan(cmd.table, cmd.seat, TuoguanType.TIMEOUT)
            else:
                if not cmd.seat.status.isCallUpTimeout and not cmd.seat.status.isPassedTuoguan:  # 第一次不出牌，且不托管
                    cmd.seat.status.isPassedTuoguan = True
                    validCards = None
                else:
                    validCards = cmd.playMode.outCardTimeout(cmd.table, cmd.seat)
            
        outCardResult, nextSeat = cmd.playMode.outCard(cmd.table, cmd.seat, validCards, oper)
        cmd.seat.cancelTimer()
        
        if outCardResult == OutCardResult.FINISH:
            return cmd.table.sm.findStateByName('final')
        
        assert(nextSeat)

        # 下一个人出牌
        autoOp = False
        optime = cmd.table.runConf.optimeOutCard
        
        autoValidCards = None
        if nextSeat.status.isTuoguan:
            autoOp, autoValidCards = True, cmd.table.dealer.tuoguanPolicy.outCardForTuoguan(cmd.table, nextSeat, TuoguanType.ALREADY_TUOGUAN)
            optime = cmd.table.runConf.optimeTuoguan
            if ftlog.is_debug():
                ftlog.debug('BaseActions.outCardAction isTuoguan',
                            'tableId=', cmd.table.tableId,
                            'cmd.seat=', (cmd.seat.userId, cmd.seat.seatId),
                            'cardCrc=', (cmd.cardCrc if isinstance(cmd, OutCardCommand) else None, cmd.table.gameRound.cardCrc),
                            'nextSeat=', (nextSeat.userId, nextSeat.seatId),
                            'autoOp=', autoOp,
                            'optime=', optime,
                            'autoValidCards=', (cmd.playMode.cardRule.toHumanCards(autoValidCards.cards) if autoValidCards else None))
        else:
            autoOp, autoValidCards = cmd.table.dealer.autoChupaiPolicy.checkAutoChupai(cmd.table, nextSeat)
            if autoOp:
                optime = cmd.table.runConf.optimeOnlyOneCard
            
                if ftlog.is_debug():
                    ftlog.debug('BaseActions.outCardAction checkAutoChupai',
                                'tableId=', cmd.table.tableId,
                                'cmd.seat=', (cmd.seat.userId, cmd.seat.seatId),
                                'cardCrc=', (cmd.cardCrc if isinstance(cmd, OutCardCommand) else None, cmd.table.gameRound.cardCrc),
                                'nextSeat=', (nextSeat.userId, nextSeat.seatId),
                                'autoOp=', autoOp,
                                'optime=', optime,
                                'autoValidCards=', (cmd.playMode.cardRule.toHumanCards(autoValidCards.cards) if autoValidCards else None))

        cmd.playMode.moveCurOpSeat(cmd.table, nextSeat, optime, autoOp)
        nextSeat.status.startChupaiTimestamp = pktimestamp.getCurrentTimestamp()
        if autoOp:
            nextSeat.startTimer(optime,
                                cmd.table.processCommand,
                                OutCardCommand(nextSeat, autoValidCards, cmd.table.gameRound.cardCrc, Oper.ROBOT))
        else:
            nextSeat.startTimer(optime,
                                cmd.table.processCommand,
                                OutCardTimeupCommand(nextSeat))
        return TableState.STATE_DONE

    @classmethod
    def clearAction(cls, cmd):
        if not isinstance(cmd, ClearGameCommand):
            return TableState.STATE_CONTINUE
        if cmd.table.gameRound.dizhuSeat or not cmd.playMode.isAbortRestart(cmd.table, cmd.table.seats):
            cmd.playMode.clearGame(cmd.table, cmd.table.keepPlayersWhenGameOver, cmd.reason)
            return cmd.table.sm.findStateByName('idle')
        cmd.playMode.abortClearGame(cmd.table)
        if cmd.table.runConf.huanpaiCardCount > 0:
            return cmd.table.sm.findStateByName('huanpai')
        return cmd.table.sm.findStateByName('calling')
    
    @classmethod
    def gameOverAction(cls, cmd):
        # 结算
        if cmd.table.gameRound.dizhuSeat:
            reason = ClearGameReason.GAME_OVER
            cmd.playMode.gameOver(cmd.table)
        else:
            reason = ClearGameReason.GAME_ABORT
            cmd.playMode.gameAbort(cmd.table)
        # 清理桌子
        cmd.table.startTimer(0,
                             cmd.table.processCommand,
                             ClearGameCommand(reason))
        return TableState.STATE_CONTINUE
    
    @classmethod
    def tuoguanAction(cls, cmd):
        ''' 
        处理托管
        '''
        if not isinstance(cmd, TuoguanCommand):
            return TableState.STATE_CONTINUE
        
        isTuoguan = cmd.isTuoguan if cmd.isTuoguan is not None else not cmd.seat.status.isTuoguan
        tuoguanLocation = 0
        if cmd.table.state.name == 'calling':
            tuoguanLocation = TuoguanLoction.CALLING
        elif cmd.table.state.name == 'playing.chupai':
            tuoguanLocation = TuoguanLoction.OUT_CARD
        else:
            pass

        cmd.playMode.tuoguan(cmd.table, cmd.seat, isTuoguan, Oper.USER, tuoguanLocation)
        
        if cmd.seat == cmd.table.gameRound.curOpSeat and cmd.seat.status.isTuoguan:
            if not cmd.table.gameRound.dizhuSeat:
                callValue = cmd.table.dealer.tuoguanPolicy.callValueForTuoguan(cmd.table, cmd.seat)
                cmd.seat.startTimer(0,
                                    cmd.table.processCommand,
                                    CallCommand(cmd.seat, callValue, Oper.ROBOT))
            else:
                validCards = cmd.table.dealer.tuoguanPolicy.outCardForTuoguan(cmd.table, cmd.seat, TuoguanType.ALREADY_TUOGUAN)
                cmd.seat.startTimer(0,
                                    cmd.table.processCommand,
                                    OutCardCommand(cmd.seat, validCards, cmd.table.gameRound.cardCrc, Oper.ROBOT))
        return TableState.STATE_DONE

    @classmethod
    def autoPlayAction(cls, cmd):
        '''
        处理自动出牌
        '''
        if not isinstance(cmd, AutoPlayCommand):
            return TableState.STATE_CONTINUE

        isAutoPlay = cmd.isAutoPlay if cmd.isAutoPlay is not None else not cmd.seat.status.isAutoPlay
        cmd.playMode.autoplay(cmd.table, cmd.seat, isAutoPlay, Oper.USER)
        if cmd.seat == cmd.table.gameRound.curOpSeat and isAutoPlay == 1:
            autoOp, autoValidCards = cmd.table.dealer.autoChupaiPolicy.checkAutoChupai(cmd.table, cmd.seat)
            if autoOp:
                cmd.seat.startTimer(0,
                                    cmd.table.processCommand,
                                    OutCardCommand(cmd.seat, autoValidCards, cmd.table.gameRound.cardCrc, Oper.ROBOT))
        return TableState.STATE_DONE
    
    @classmethod
    def startNongminJiabeiAction(cls, cmd):
        ''' 
        开始农民加倍，启动超时定时器 
        '''
        cmd.playMode.startNongminJiabei(cmd.table)
        # 超时则发送JiabeiTimeupCommand
        for seat in cmd.table.gameRound.seats:
            if not cmd.playMode.isSeatDizhu(cmd.table, seat):
                seat.startTimer(cmd.table.runConf.optimeJiabei,
                                cmd.table.processCommand,
                                JiabeiTimeupCommand(seat))
        return TableState.STATE_CONTINUE
    
    @classmethod
    def nongminJiabeiAction(cls, cmd):
        ''' 
        农民叫加倍或者农民未叫超时 
        '''
        if not isinstance(cmd, (JiabeiCommand, JiabeiTimeupCommand)):
            return TableState.STATE_CONTINUE
        
        # 玩家主动叫加倍
        if isinstance(cmd, JiabeiCommand):
            oper = Oper.USER
            mutil = cmd.mutil
        else:  # JiabeiTimeupCommand超时自动不加倍
            oper = Oper.ROBOT
            mutil = 1
            
        cmd.playMode.nongminJiabei(cmd.table, cmd.seat, mutil, oper)
        cmd.seat.cancelTimer()
        
        if cls.isAllNongminJiabeiCalled(cmd.table):  # 若所有农民都已经叫过了(加或不加都算)
            if cls.hadAnyNongminJiabei(cmd.table):  # 有农民叫加倍，地主才可以加倍
                if cmd.table.dealer.jiabeiMode == JiabeiMode.AFTER_FLIP_BASE_CARD:
                    return cmd.table.sm.findStateByName('playing.dizhujiabei')
                else:
                    return cmd.table.sm.findStateByName('dizhujiabei')
            # 配置牌桌支持换牌玩法
            if cmd.table.runConf.huanpaiCardCount > 0:
                return cmd.table.sm.findStateByName('playing.huanpai')
            return cmd.table.sm.findStateByName('playing.chupai')
        return TableState.STATE_DONE
    
    @classmethod
    def startDizhuJiabeiAction(cls, cmd):
        ''' 
        开始地主加倍，启动超时定时器 
        '''
        cmd.playMode.startDizhuJiabei(cmd.table)
        # 超时则发送JiabeiTimeupCommand
        cmd.table.startTimer(cmd.table.runConf.optimeJiabei,
                             cmd.table.processCommand,
                             JiabeiTimeupCommand(cmd.table.gameRound.dizhuSeat))
        return TableState.STATE_CONTINUE

    @classmethod
    def dizhuJiabeiAction(cls, cmd):
        ''' 
        地主叫加倍或者地主未叫超时 
        '''
        if not isinstance(cmd, (JiabeiCommand, JiabeiTimeupCommand)):
            return TableState.STATE_CONTINUE
        
        # 玩家主动叫加倍
        if isinstance(cmd, JiabeiCommand):
            oper = Oper.USER
            mutil = cmd.mutil
        else:  # JiabeiTimeupCommand超时自动不加倍
            oper = Oper.ROBOT
            mutil = 1
            
        cmd.playMode.dizhuJiabei(cmd.table, cmd.seat, mutil, oper)
        cmd.table.cancelTimer()
        if cmd.table.runConf.huanpaiCardCount > 0:
            return cmd.table.sm.findStateByName('playing.huanpai')
        return cmd.table.sm.findStateByName('playing.chupai')
        
    @classmethod
    def isAllNongminJiabeiCalled(cls, table):
        '''
        所有农民都设置过是否加倍
        '''
        for seat in table.gameRound.seats:
            # seatMulti<=0代表未设置倍数，不加倍为1
            if seat != table.gameRound.dizhuSeat and seat.status.seatMulti <= 0:
                return False
        return True

    @classmethod
    def hadAnyNongminJiabei(cls, table):
        '''
        是否有农民加倍
        '''
        for seat in table.gameRound.seats:
            if seat != table.gameRound.dizhuSeat and seat.status.seatMulti > 1:
                return True
        return False
    
    @classmethod
    def startHuanpaiAction(cls, cmd):
        '''
        开始换牌，启动超时定时器
        '''
        cmd.playMode.startHuanpai(cmd.table)
        # 超时则发送HuanpaiTimeupCommand
        for seat in cmd.table.gameRound.seats:
            seat.startTimer(cmd.table.runConf.optimeHuanpai,
                            cmd.table.processCommand,
                            HuanpaiTimeupCommand(seat))
        return TableState.STATE_CONTINUE
    
    @classmethod
    def huanpaiOutcardsAction(cls, cmd):
        '''
        换牌出牌动作
        '''
        if not isinstance(cmd, (HuanpaiOutcardsCommand, HuanpaiTimeupCommand)):
            return TableState.STATE_CONTINUE
        
        if isinstance(cmd, HuanpaiOutcardsCommand):
            oper = Oper.USER
            outCards = cmd.outCards
        else:  # HuanpaiTimeupCommand
            oper = Oper.ROBOT
            seatcards = cmd.seat.status.cards[:]
            # 按牌point排序
            seatcards.sort(key=lambda x: cmd.playMode.cardRule.cardToPoint(x))
            outCards = seatcards[0:cmd.table.runConf.huanpaiCardCount]
            
        cmd.playMode.huanpaiSeatOutcards(cmd.table, cmd.seat, outCards, oper)
        cmd.seat.cancelTimer()
        if ftlog.is_debug():
            ftlog.debug('BaseActions.huanpaiOutcardsAction',
                        'tableId=', cmd.table.tableId,
                        'userId=', cmd.seat.userId,
                        'outCards=', outCards,
                        'oper=', oper)
            
        if cls.isAllSeatsHuanpaiOutcard(cmd.table):
            # 玩家之间交换牌型
            cmd.playMode.huanpaiEnd(cmd.table)
            if ftlog.is_debug():
                ftlog.debug('BaseActions.huanpaiOutcardsAction',
                            'tableId=', cmd.table.tableId,
                            'stat=', cmd.table.state.name,
                            'nextStat=', 'calling')
            return cmd.table.sm.findStateByName('calling')
        return TableState.STATE_DONE
        
    @classmethod
    def isAllSeatsHuanpaiOutcard(cls, table):
        '''
        所有玩家都出要换牌的牌了
        '''
        for seat in table.gameRound.seats:
            if not table.playMode.isSeatHuanpaiOutcard(table, seat):
                return False
        return True
    
class TableStateIdle(TableState):
    def __init__(self):
        super(TableStateIdle, self).__init__('idle')
        self._addAction(BaseActions.sitdownAction)
        self._addAction(BaseActions.standupAction)
        self._addAction(BaseActions.readyAction)
        self._addAction(BaseActions.readyTimeoutAction)

class TableStateCalling(TableState):
    def __init__(self):
        super(TableStateCalling, self).__init__('calling')
        self._addEntryAction(BaseActions.gameReadyAction)
        self._addAction(BaseActions.tuoguanAction)
        self._addAction(BaseActions.callAction)

class TableStateNongminJiabei(TableState):
    def __init__(self):
        super(TableStateNongminJiabei, self).__init__('nongminjiabei')
        self._addEntryAction(BaseActions.startNongminJiabeiAction)
        self._addAction(BaseActions.nongminJiabeiAction)
       
class TableStateDizhuJiabei(TableState):
    def __init__(self):
        super(TableStateDizhuJiabei, self).__init__('dizhujiabei')
        self._addEntryAction(BaseActions.startDizhuJiabeiAction)
        self._addAction(BaseActions.dizhuJiabeiAction)
        
class TableStatePlayingNongminJiabei(TableState):
    def __init__(self):
        super(TableStatePlayingNongminJiabei, self).__init__('playing.nongminjiabei')
        self._addEntryAction(BaseActions.startNongminJiabeiAction)
        self._addAction(BaseActions.nongminJiabeiAction)
       
class TableStatePlayingDizhuJiabei(TableState):
    def __init__(self):
        super(TableStatePlayingDizhuJiabei, self).__init__('playing.dizhujiabei')
        self._addEntryAction(BaseActions.startDizhuJiabeiAction)
        self._addAction(BaseActions.dizhuJiabeiAction)

class TableStateHuanpai(TableState):
    def __init__(self):
        super(TableStateHuanpai, self).__init__('huanpai')
        self._addEntryAction(BaseActions.gameReadyForHuanpaiAction)
        self._addEntryAction(BaseActions.startHuanpaiAction)
        self._addAction(BaseActions.huanpaiOutcardsAction)
        
class TableStateChupai(TableState):
    def __init__(self):
        super(TableStateChupai, self).__init__('playing.chupai')
        self._addEntryAction(BaseActions.startChupaiAction)
        self._addAction(BaseActions.showCardsAction)
        self._addAction(BaseActions.tuoguanAction)
        self._addAction(BaseActions.autoPlayAction)
        self._addAction(BaseActions.outCardAction)
        
class TableStatePlaying(TableState):
    def __init__(self):
        super(TableStatePlaying, self).__init__('playing')
        self._addEntryAction(BaseActions.gameStartAction)
        self.addChild(TableStatePlayingNongminJiabei())
        self.addChild(TableStatePlayingDizhuJiabei())
        self.addChild(TableStateChupai())
        
class TableStateFinal(TableState):
    def __init__(self):
        super(TableStateFinal, self).__init__('final')
        self._addEntryAction(BaseActions.gameOverAction)
        self._addAction(BaseActions.clearAction)


