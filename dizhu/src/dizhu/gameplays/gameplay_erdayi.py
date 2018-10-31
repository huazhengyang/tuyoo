# -*- coding:utf-8 -*-
'''
Created on 2016年7月20日

@author: zhaojiangang
'''
import random

from dizhu.entity import dizhuconf
from dizhu.gameplays.gameplay_base import DizhuBaseGamePlay
from dizhu.gametable.dizhu_player import DizhuPlayer
from dizhu.gametable.dizhu_seat import DizhuSeat
from dizhu.gametable.dizhu_state import DizhuState
from dizhu.servers.util.rpc import table_winlose, event_remote
from freetime.util import log as ftlog

class DizhuErdayiGamePlay(DizhuBaseGamePlay):
    def __init__(self, table):
        super(DizhuErdayiGamePlay, self).__init__(table)
        
    @property
    def isVsAI(self):
        return self.table.isVsAI
    
    def getPlayMode(self):
        return dizhuconf.PLAYMODE_ERDAYI

    def doAIOutCard(self, player, ccrc):
        if (not player
            or self.table.status.state != DizhuState.TABLE_STATE_PLAYING):
            ftlog.warn('ERROR !!, doChuPai table.status=', self.table.status, player)
            return
        
        #seat.robotCardCount = 0
        # 首先校验出牌的CRC
        if ccrc >= 0 and ccrc != self.table.status.cardCrc :
            ftlog.warn('doChuPai the ccrc error ! mcrc=', ccrc, 'ccrc=', self.table.status.cardCrc)
            self.sender.sendTableInfoRes(player.userId, player.clientId, 0)
            return
        
        if (self.table.status.topSeatId == 0 or self.table.status.topSeatId == player.seatId):
            cards = player.doActiveOutCard()
        else:
            cards = player.doPassiveOutCard()
            
#         handcard = self.table.seats[player.seatId - 1].cards
#         if (self.table.status.topSeatId == 0 or self.table.status.topSeatId == player.seatId):
#             # 主动出牌
#             cards = self.card.findFirstCards(handcard)
#         else:
#             topcard = self.table.status.topCardList
#             cards = self.card.findGreaterCards(topcard, handcard)
         
        self.doChuPai(player, cards, ccrc, DizhuPlayer.TUGUAN_TYPE_USERACT)
        
    def doCallDizhuTimeOut(self, player):
        '''
        叫地主超时
        '''
        if ftlog.is_debug():
            ftlog.debug('DizhuErdayiGamePlay.doCallDizhuTimeOut userId=', player.userId,
                        'isVsAI=', self.isVsAI,
                        'isAI=', player.isAI,
                        'tableState=', self.table.status.state)
        if not player or self.table.status.state != DizhuState.TABLE_STATE_CALLING :
            ftlog.warn('ERROR !!, doCallDizhuTimeOut table.status=', self.table.status, player)
            return
        
        if self.isVsAI:
            # 玩家必须叫地主
            call = 1 if not player.isAI else 0
            if ftlog.is_debug():
                ftlog.debug('DizhuErdayiGamePlay.doCallDizhuTimeOut adjustCall userId=', player.userId,
                            'isVsAI=', self.isVsAI,
                            'isAI=', player.isAI,
                            'tableState=', self.table.status.state,
                            'call=', call)
            # 系统主动替玩家进行叫地主, 1分
            self.doCallDizhu(player, -1, call, DizhuPlayer.TUGUAN_TYPE_TIMEOUT)
        else:
            # 叫地主超时, 直接进入托管状态
            self._checkIfForceRobot(player, DizhuPlayer.TUGUAN_TYPE_TIMEOUT)
            # 系统主动替玩家进行叫地主
            self.doCallDizhu(player, -1, -1, DizhuPlayer.TUGUAN_TYPE_TIMEOUT)
            
    def doCallDizhu(self, player, grab, call, tuoGuanType):
        '''
        叫地主操作
        callType = 1 客户端点击"叫地主"按钮
        callType = 2 客户端超时,系统托管叫地主
        '''
        if not player or self.table.status.state != DizhuState.TABLE_STATE_CALLING :
            ftlog.warn('ERROR !!, doCallDizhu table.status=', self.table.status, player)
            return
        
        # 校验当前是否可以叫地主
        if not self._doCallDizhuVerify(player, grab, call) :
            ftlog.warn('callOp->verifyCall error', grab, call, tuoGuanType, player.userId, self.table.status.nowOper)
            return

        # 取消当前的操作计时器
        self.table.tableTimer.cancel()
        # 保存叫地主的标记
        self.table.status.callStr += str(call)
        # 计算地主座位号以及叫的分数
        isTrueGrab = self._doCallDizhuSetCall(player, call)
        # 发送叫地主的客户端响应
        self.sender.sendCallRes(player.seatId, player.userId, call)
        # 发送叫地主的系统事件
        if call > 0 :
            event_remote.publishUserTableCallEvent(self.table.gameId, player.userId,
                                                             self.table.roomId, self.table.tableId,
                                                             call, isTrueGrab)
        # 牌局记录器处理
        self.table.gameRound.call(player.seatIndex, call, self.calcCurTotalMulti(), self.table.status.rangPai)

        cgs = self._checkGameStart()
        ftlog.debug('checkGameStart cgs==', cgs)
        if cgs == 0:
            # 0 已经决定了地主，开始游戏
            self._gameStart()
        elif cgs > 0 :
            # > 0 需要继续叫地主
            self._doNextCall(cgs)
        else:
            # 大家都不叫，当前牌桌流局
            self._doGameAbort()
            
    def doJiabeiTimeout(self):
        dizhuSeatId = self.table.status.diZhu
        self.table.tableTimer.cancel()
        if self.table.status.state == DizhuState.TABLE_STATE_NM_DOUBLE:
            for i in xrange(len(self.table.seats)):
                if (self.table.status.state == DizhuState.TABLE_STATE_NM_DOUBLE
                    and (dizhuSeatId != i + 1)
                    and (not self._isSeatMultiSet(i))):
                    player = self.table.players[i]
                    self.doJiabei(player, 0, 'server')
        elif self.table.status.state == DizhuState.TABLE_STATE_DIZHU_DOUBLE:
            dizhuSeatId = self.table.status.diZhu
            player = self.table.players[dizhuSeatId - 1]
            self.doJiabei(player, 0, 'server')
    
    def doJiabei(self, player, jiabei, oper='user'):
        if (self.table.status.state <= DizhuState.TABLE_STATE_CALLING
            or self.table.status.state >= DizhuState.TABLE_STATE_PLAYING):
            ftlog.warn('DizhuErdayiGamePlay.doJiabei',
                       'userId=', player.userId,
                       'seatId=', player.seatId,
                       'oper=', oper,
                       'state=', self.table.status.state,
                       'err=', 'BadState')
            return
        
        dizhuSeatId = self.table.status.diZhu
        if dizhuSeatId == player.seatId:
            # 地主加倍
            if self.table.status.state != DizhuState.TABLE_STATE_DIZHU_DOUBLE:
                ftlog.warn('DizhuErdayiGamePlay.doJiabei',
                           'userId=', player.userId,
                           'seatId=', player.seatId,
                           'oper=', oper,
                           'expect=', DizhuState.TABLE_STATE_DIZHU_DOUBLE,
                           'state=', self.table.status.state,
                           'err=', 'BadState')
                return
            
            # 地主加倍完毕
            self._setSeatMulti(player.seatIndex, 2 if jiabei else 1)
            self.sender.sendJiabeiRes(player.seatId, jiabei)
            self._gameStartImpl()
        else:
            if self.table.status.state != DizhuState.TABLE_STATE_NM_DOUBLE:
                ftlog.warn('DizhuErdayiGamePlay.doJiabei',
                           'userId=', player.userId,
                           'seatId=', player.seatId,
                           'oper=', oper,
                           'expect=', DizhuState.TABLE_STATE_NM_DOUBLE,
                           'state=', self.table.status.state,
                           'err=', 'BadState')
                return
            
            if self._isSeatMultiSet(player.seatIndex):
                ftlog.warn('DizhuErdayiGamePlay.doJiabei',
                           'userId=', player.userId,
                           'seatId=', player.seatId,
                           'oper=', oper,
                           'state=', self.table.status.state,
                           'err=', 'AlreadyJiabei')
                return
            
            self._setSeatMulti(player.seatIndex, 2 if jiabei else 1)
            self.sender.sendJiabeiRes(player.seatId, jiabei)
            
            if self._isAllNMSetMulti():
                self.table.tableTimer.cancel()
                # 农民加倍了
                if self._isNMDouble():
                    ftlog.info('DizhuErdayiGamePlay.doJiabei isNMDouble',
                               'userId=', player.userId,
                               'seatId=', player.seatId,
                               'oper=', oper,
                               'state=', self.table.status.state)
                    self.table.status.state = DizhuState.TABLE_STATE_DIZHU_DOUBLE
                    params = {
                    }
                    optime = self.table.runConfig.datas.get('jiabei.optime', 25)
                    self.table.tableTimer.setup(optime, 'JIABEI_TIMEUP', params)
                    self.sender.sendWaitJiabei(optime)
                else:
                    self._gameStartImpl()
    
    def _gameStartImpl(self):
        self.table.cancelTimerAll()
        self.table.status.state = DizhuState.TABLE_STATE_PLAYING
        # 开始地主出牌
        self.sender.sendGameStartRes()
        self._doNext(1)
        
    def _gameStart(self):
        ftlog.debug('call finish, start game !!')
        # 取消所有的计数器
        self.table.cancelTimerAll()
        # 转换桌子的状态到加倍状态，此状态只能农民加倍
        self.table.status.state = DizhuState.TABLE_STATE_NM_DOUBLE
        # 更新座位状态
        for seat in self.table.seats:
            if seat.userId > 0 :
                seat.state = DizhuSeat.SEAT_STATE_PLAYING
        # 把底牌给地主
        dizhuSeatId = self.table.status.diZhu
        dizhuSeat = self.table.seats[dizhuSeatId - 1]
        dizhuSeat.cards.extend(self.table.status.baseCardList)
        
        # 扩展的游戏开始方法
        self._gameStartAfter()
        # 牌局记录器处理
        seatCards = []
        for x in xrange(len(self.table.seats)):
            seatCards.append(self.table.seats[x].cards[:])
        self.table.gameRound.gameStart(dizhuSeatId - 1,
                                       seatCards,
                                       self.table.status.baseCardList,
                                       self.table.status.baseCardMulti,
                                       self.calcCurTotalMulti())
        # 游戏开始处理
        _, userIds = self.table.getSeatUserIds()
#         datas = table_remote.doTableGameStart(self.table.roomId, self.table.tableId, self.table.gameRound.roundId,
#                              dizhuSeat.userId, self.table.status.baseCardType,
#                              self.table.runConfig.roomMutil, self.table.runConfig.basebet,
#                              self.table.runConfig.basemulti, userIds)
        datas = table_winlose.doTableGameStartGT(self.table.roomId, self.table.tableId, self.table.gameRound.number,
                             dizhuSeat.userId, self.table.status.baseCardType,
                             self.table.runConfig.roomMutil, self.table.runConfig.basebet,
                             self.table.runConfig.basemulti, userIds)
        ftlog.debug('doTableGameStart->', datas)
        tbinfos = datas['tbinfos']
        for p in self.table.players :
            tbinfo = tbinfos.get(str(p.userId))
            ftlog.debug('update->tbinfos->', p.userId, tbinfo)
            if tbinfo :
                p.datas['tbc'] = tbinfo['tbplaycount']
                p.datas['tbt'] = tbinfo['tbplaytimes']

        # 启动加倍计时器
        params = {
        }
        self.table.tableTimer.setup(2, 'JIABEI_TIMEUP', params)
        
        # 发送游戏开始的消息
        #self.sender.sendGameStartRes()
        # 农民自动加倍或不加倍操作
        dizhuSeatId = self.table.status.diZhu
        delay = 1
        for i, seat in enumerate(self.table.seats):
            if i + 1 != dizhuSeatId:
                params = {
                    'seatId' : i + 1,
                    'userId' : seat.userId,
                    'jiabei' : 1 if self.table.canJiabei(seat) else 0,
                }
                self.table.seatOpTimers[i].setup(delay, 'AI_JIABEI', params)
                delay += 1
        self.sender.sendWaitJiabei(2)
        
    def _sendCard(self):
        self.table.status.goodSeatId = 0
        for i, seat in enumerate(self.table.seats):
            seat.cards = self.table._match_table_info['cards'][i]
        self.table.status.baseCardList = self.table._match_table_info['cards'][-1]
        self.table.status.baseCardMulti = 1

    def _chooseFirstCall(self):
        userIds = []
        for p in self.table.players:
            if not p.isAI:
                userIds.append(p.userId)
        firstCallSeatId = 1 if len(userIds) <= 1 else random.randint(1, len(userIds))
        if ftlog.is_debug():
            ftlog.debug('DizhuErdayiGamePlay._chooseFirstCall userIds=', userIds,
                        'firstCallSeatId=', firstCallSeatId)
        self.table.status.nowOper = firstCallSeatId
        
    def _doCallDizhuVerify(self, player, grab, call):
        '''
        校验,是否可以进行叫地主的操作
        '''
        if ftlog.is_debug():
            ftlog.debug('DizhuErdayiGamePlay._doCallDizhuVerify userId=', player.userId,
                        'grab=', grab,
                        'call=', call)
            
        if self.table.status.nowOper != player.seatId :
            return False
            
        if self.isVsAI:
            # 非机器人不能不叫，只能非机器人叫地主
            if not player.isAI:
                if call <= 0:
                    return False
                return True
            return False
        else:
            # 每人只能叫一次所以不能大于3
            if len(self.table.status.callStr) > 2:
                return False
            # 叫的分数不能比已经叫过的分数小(0除外)，而且不能大于3
            if call != 0 and (call <= self.table.status.callGrade or call > 3):
                return False
            return True

    def _doCallDizhuSetCall(self, player, call):
        seat = self.table.seats[player.seatIndex]
        seat.call123 = call
        if call > 0:
            self.table.status.callGrade = call
            self.table.status.diZhu = player.seatId
        return False

    def _checkGameStart(self):
        '''
        检查当前是否叫地主的状态, 
        返回值 : 0 - 叫地主结束, 开始出牌
                < 0 都不叫, 流局
                > 0 需要继续叫地主
        '''
        if self.isVsAI:
            # 有人叫了地主
            if self.table.status.callGrade > 0:
                return 0
            return 1
        else:
            # 已经叫到3分了
            if self.table.status.callGrade > 2:
                return 0
            tclen = len(self.table.status.callStr)
            if tclen < 3:
                # 没有叫3分并且还有人没有叫
                return 1
            else:
                # 没人叫地主
                if self.table.status.callGrade <= 0:
                    return -1
                return 0
    

