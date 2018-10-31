# -*- coding:utf-8 -*-
'''
Created on 2016年7月20日

@author: zhaoliang
'''
import random
from dizhu.entity import dizhuconf
from dizhu.gameplays.gameplay_base import DizhuBaseGamePlay
from dizhu.gametable.dizhu_player import DizhuPlayer
from dizhu.gametable.dizhu_state import DizhuState
from dizhu.servers.util.rpc import event_remote
from freetime.util import log as ftlog
from poker.entity.game.tables.table_player import TYPlayer
from poker.entity.configure import gdata
from dizhu.gamecards.sendcard import SendCardPolicyUserId


class DizhuMillionHeroMatchPlay(DizhuBaseGamePlay):
    def __init__(self, table):
        super(DizhuMillionHeroMatchPlay, self).__init__(table)
        
    def getPlayMode(self):
        return dizhuconf.PLAYMODE_ERDAYI
    
    def _doNext(self, isFirst):
        ftlog.debug('_doNext-->isFirst=', isFirst, 'self.table.status.nowOper=', self.table.status.nowOper)
        # 查找下一个出牌的玩家座位ID
        if isFirst == 0:
            # 非第一次出牌, 查找
            nsid = self._findNextPlayerSeatId()
        else:
            # 第一次, 出牌, 固定为地主出牌
            self.table.status.nowOper = self.table.status.diZhu
            nsid = self.table.status.nowOper
        if nsid <= 0:
            ftlog.warn('doNext can not found next player...')
            return
        ftlog.debug('_doNext-->isFirst=', isFirst, 'nsid=', nsid)
        # 出牌的简单的crc校验码处理
        self.table.status.cardCrc += 1
        self.table.status.nowOper = nsid
        # 出牌计时器处理
        tuoGuanType = DizhuPlayer.TUGUAN_TYPE_USERACT
        autocard = 0
        seat = self.table.seats[nsid - 1]
        opTime = self.table.runConfig.optimeFirst if isFirst else self.table.runConfig.optime
        opTime -= self.opTimePunishMatch(seat)
                        
        if (seat.isRobot == 1) and TYPlayer.isHuman(seat.userId):
            # 如果是托管状态, 那么最短时间超时, 由超时处理中,处理是否出牌
            tuoGuanType = DizhuPlayer.TUGUAN_TYPE_ALREADY_TUOGUAN
            latetime = self.table.runConfig.optimeAlreadyTuoGuan
            ftlog.debug('autocard 1...')
            autocard = 1
        else:
            # 正常出牌超时控制
            tuoGuanType = DizhuPlayer.TUGUAN_TYPE_TIMEOUT
            latetime = opTime
            
        # 只剩一张牌时，自动出牌
        if len(seat.cards) == 1 :
            tuoGuanType = DizhuPlayer.TUGUAN_TYPE_SYS_FAST_CARD
            latetime = self.table.runConfig.optimeOnlyOneCard
            ftlog.debug('autocard 2...')
            autocard = 1
            
        # 如果上家出的是火箭, 那么自动不出牌
        if nsid in self._doubleKingNoCard :
            tuoGuanType = DizhuPlayer.TUGUAN_TYPE_SYS_FAST_CARD
            latetime = self.table.runConfig.optimeDoubleKing
            ftlog.debug('autocard 3...')
            autocard = 1
            del self._doubleKingNoCard[nsid]
            
        params = {'tuoGuanType' : tuoGuanType,
                  'seatId' : nsid,
                  'userId' : seat.userId,
                  'ccrc' : self.table.status.cardCrc
                  }
        ftlog.debug('params:', params, ' latetime:', latetime, ' autocard:', autocard)
        if autocard or (not TYPlayer.isRobot(seat.userId)):
            # 真实玩家启动出牌超时计时器
            self.table.tableTimer.setup(latetime, 'CL_TIMEUP', params)
            
        # 牌局记录器处理
        self.table.gameRound.next(nsid - 1, 0, opTime)
        if autocard :
            # 自动出牌, 不发送next消息
            return
        # 发送下一个出牌的消息至客户端
        self.sender.sendChuPaiNextRes(nsid, opTime)
    
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
        self.doChuPai(player, cards, ccrc, DizhuPlayer.TUGUAN_TYPE_USERACT)
        
    def _checkIfForceRobot(self, player, tuoGuanType):
        '''
        每次超时均检查是否需要强制进入托管状态
        '''
        if TYPlayer.isRobot(player.userId):
            return
        
        seat = self.table.seats[player.seatIndex]
        if tuoGuanType == DizhuPlayer.TUGUAN_TYPE_USERACT :  # 用户出牌
            seat.timeOutCount = 0
        elif tuoGuanType == DizhuPlayer.TUGUAN_TYPE_TIMEOUT :  # 正常操作超时
            seat.timeOutCount = seat.timeOutCount + 1
            ftlog.debug('_checkIfForceRobot->userId=', player.userId,
                        'seat.timeOutCount=', seat.timeOutCount, 'die=', self.table.runConfig.robotTimes)
            if seat.timeOutCount >= self.table.runConfig.robotTimes :
                self._doTuoGuan(player, True)

    
    def doFirstCallDizhu(self, player):
        '''
        延迟发送, 触发第一个叫地主的玩家
        '''
        ftlog.debug('doFirstCallDizhu...')
        
        if self.table.status.state != DizhuState.TABLE_STATE_CALLING :
            ftlog.warn('ERROR !!, doFirstCallDizhu table.status=', self.table.status, player)
            return
        
        for seat in self.table.seats:
            if TYPlayer.isRobot(seat.userId):
                seat.isRobot = 1
                
        self._doNextCall(0)
        
    def _doNextCall(self, nctype):
        '''
        找到下一个叫地主的玩家, 发送开始叫地主的事件消息
        '''
        nsid = self._findNextCaller()
        if ftlog.is_debug():
            ftlog.debug('DizhuBaseGamePlay._doNextCall nctype=', nctype,
                        'nsid=', nsid)
        if nsid > 0:
            self.table.status.nowOper = nsid
            grab = 1 if nctype == 0 or nctype == 1 else 0
            # 发送下一个操作的命令
            self.sender.sendCallNextRes(nsid, grab)
            # 启动叫地主计时器
            seat = self.table.seats[nsid - 1]
            params = {'robot' : seat.isRobot,
                      'seatId' : nsid,
                      'userId' : seat.userId
                      }
            interval = random.randint(1,3) if seat.isRobot else self.table.runConfig.optime
            self.table.tableTimer.setup(interval, 'CL_TIMEUP_CALL', params)
            # 牌局记录器处理
            self.table.gameRound.next(nsid - 1, grab, interval)
        else:
            ftlog.warn('_doNextCall can not found next caller...')

    def doCallDizhuTimeOut(self, player):
        '''
        叫地主超时
        '''
        ftlog.debug('doCallDizhuTimeOut...')
        
        if not player or self.table.status.state != DizhuState.TABLE_STATE_CALLING :
            ftlog.warn('ERROR !!, doCallDizhuTimeOut table.status=', self.table.status, player)
            return
        
        assert(self.table.status.callGrade < 3)
            
        if TYPlayer.isHuman(player.userId):
            # 真实玩家超时默认不叫地主
            call = 0
        else:
            # AI必须叫地主
            if self.table.status.callGrade <= 0:
                call = 1
            else:
                call = self.table.status.callGrade + 1
            
        # 系统主动替玩家进行叫地主, 1分
        self.doCallDizhu(player, -1, call, DizhuPlayer.TUGUAN_TYPE_TIMEOUT)
        
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
            ftlog.warn('DizhuMillionHeroMatchPlay.doJiabei',
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
                ftlog.warn('DizhuMillionHeroMatchPlay.doJiabei',
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
                ftlog.warn('DizhuMillionHeroMatchPlay.doJiabei',
                           'userId=', player.userId,
                           'seatId=', player.seatId,
                           'oper=', oper,
                           'expect=', DizhuState.TABLE_STATE_NM_DOUBLE,
                           'state=', self.table.status.state,
                           'err=', 'BadState')
                return
            
            if self._isSeatMultiSet(player.seatIndex):
                ftlog.warn('DizhuMillionHeroMatchPlay.doJiabei',
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
                    ftlog.info('DizhuMillionHeroMatchPlay.doJiabei isNMDouble',
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
        
    def _chooseFirstCall(self):
        userIds = []
        for p in self.table.players:
            userIds.append(p.userId)
            
        firstCallSeatId = 1 if len(userIds) <= 1 else random.randint(1, len(userIds))
        if ftlog.is_debug():
            ftlog.debug('DizhuMillionHeroMatchPlay._chooseFirstCall userIds=', userIds,
                        'firstCallSeatId=', firstCallSeatId)
        self.table.status.nowOper = firstCallSeatId
        
    def _doCallDizhuVerify(self, player, grab, call):
        '''
        校验,是否可以进行叫地主的操作
        '''
        if ftlog.is_debug():
            ftlog.debug('DizhuMillionHeroMatchPlay._doCallDizhuVerify userId=', player.userId,
                        'grab=', grab,
                        'call=', call)
            
        if self.table.status.nowOper != player.seatId :
            return False
            
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
        
    def _sendCard(self):
        '''
        发牌处理
        '''
        userCount, userids = self.table.getSeatUserIds()
        pcount = []
        for player in self.table.players :
            pcount.append(player.winratePlays)
        # 发牌处理
        goodSeatId = 0
        cards = None
        if gdata.enableTestHtml() :
            cards = SendCardPolicyUserId.getInstance().sendCards(self.table.tableId, userids)
            
        if not cards:
            lucky = self.table.goodCardLucky()
            goodCard = self.table.runConfig.goodCard
            if ftlog.is_debug():
                ftlog.debug('DizhuMillionHeroMatchPlay._sendCard',
                            'tableId=', self.table.tableId,
                            'lucky=', lucky,
                            'goodCard=', goodCard)
            goodSeatId, cards = self.card.generateLuckCard(userids, pcount,
                                                           goodCard,
                                                           lucky,
                                                           self.table.runConfig.sendCardConfig)
        # 设置取得的好牌座位号
        self.table.status.goodSeatId = goodSeatId if goodSeatId > 0 else 0
        # 设置每个玩家的手牌
        for x in xrange(len(self.table.seats)):
            self.table.seats[x].cards = cards[x]
        # 设置底牌
        self.table.status.baseCardList = cards[userCount]
        # 废弃牌
        if len(cards) == userCount + 2 :
            self.table.status.kickOutCardList = cards[-1]
        
        bctype, bcmulti = self.card.getBaseCardInfo(self.table.status.baseCardList)
        self.table.status.baseCardType = bctype
        if self.table.isMatch or self.table.isFriendTable():
            self.table.status.baseCardMulti = 1
        else:
            self.table.status.baseCardMulti = bcmulti