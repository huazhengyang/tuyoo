# coding=UTF-8

import random

from dizhu.entity import dizhuconf
from dizhu.gamecards import cardcenter
from dizhu.gamecards.sendcard import SendCardPolicyUserId
from dizhu.gameplays.gameround import GameRoundCodecDictComplain
from dizhu.gameplays.punish import Punish
from dizhu.gametable.dizhu_player import DizhuPlayer
from dizhu.gametable.dizhu_seat import DizhuSeat
from dizhu.gametable.dizhu_sender import DizhuSender
from dizhu.gametable.dizhu_state import DizhuState
from dizhu.gametable.dizhu_table import DizhuTable
from dizhu.replay.gameround import WinloseDetail, SeatWinloseDetail
from dizhu.servers.util.rpc import event_remote, table_remote, table_winlose
from freetime.core.tasklet import FTTasklet
from freetime.util import log as ftlog
from freetime.util.log import getMethodName
from hall.servers.util.rpc import user_remote
from poker.entity.biz import bireport
from poker.entity.configure import gdata
from poker.entity.dao import onlinedata
from poker.entity.events.tyevent import TableStandUpEvent
from poker.entity.game.rooms.big_match_ctrl.const import StageType
from poker.entity.game.rooms.room import TYRoom
from poker.util import strutil
from poker.util import timestamp as pktimestamp
from poker.entity.game.tables.table_player import TYPlayer

__author__ = [
    '"Zqh"',
    '"Zhouhao" <zhouhao@tuyoogame.com>',
]


class DizhuBaseGamePlay(object):
    def __init__(self, table):
        if not table :  # table必定有值, 此处为了代码自动提示而设置
            self.table = DizhuTable()
        self.table = table
        self.sender = DizhuSender(table)
        self.card = cardcenter.getDizhuCard(self.table.runConfig.playMode)
        self.punish = Punish(table, self.sender, self.card)
        self._doubleKingNoCard = {}

    def clearGamePlay(self):
        # 清理玩法的状态
        self._doubleKingNoCard = {}

    def getPlayMode(self):
        raise NotImplementedError

    def doEnter(self, userId, clientId):
        '''
        玩家操作, 尝试进入当前的桌子
        '''
        pass


    def doLeave(self, userId, clientId, needResponse):
        '''
        玩家操作, 尝试离开当前的桌子
        实例桌子可以覆盖 _doLeave 方法来进行自己的业务逻辑处理
        '''
        isOK = True
        result = {"gameId":self.table.gameId, "userId":userId, "roomId":self.table.roomId, "tableId":self.table.tableId}
        player = self.table.getPlayer(userId)
        if player:
            isOK = self.doStandUp(userId, player.seatId, TYRoom.LEAVE_ROOM_REASON_ACTIVE, clientId)
            if isOK :
                result['reason'] = TYRoom.LEAVE_ROOM_REASON_ACTIVE
            else:
                result['reason'] = TYRoom.LEAVE_ROOM_REASON_FORBIT
        else:
            result['reason'] = TYRoom.LEAVE_ROOM_REASON_ACTIVE
            ftlog.warn(getMethodName(), "empty seat", "|tableId, userId:", self.table.tableId, userId)

        if userId in self.table.observers:
            del self.table.observers[userId]
            
        if needResponse :
            self.sender.sendTableLeaveRes(userId, clientId, result)
        return isOK, result


    def doSitDown(self, userId, seatId, clientId, continuityBuyin, doBuyin=True):
        '''
        玩家入座, 启动table_call#ready命令的超时检查
        '''
        result = {"isOK":True}
        if DizhuPlayer.isRobot(userId, clientId) :
            if not self.table._isRobotCanSit() :
                result["isOK"] = False
                result["reason"] = TYRoom.ENTER_ROOM_REASON_NOT_QUALIFIED
                self.sender.sendQuickStartRes(userId, clientId, result)
                return

        player = self.table.getPlayer(userId)
        if player:
            result["seatId"] = player.seatId
            result["reason"] = TYRoom.ENTER_ROOM_REASON_OK
            self.table.seats[player.seatIndex].online = True
            self.sender.sendQuickStartRes(userId, clientId, result)
            self.sender.sendTableInfoRes(userId, clientId, 0)
            self.sender.sendOnlineChanged(player)
            return
        
        onlineSeatId = onlinedata.getOnlineLocSeatId(userId, self.table.roomId, self.table.tableId)
        if onlineSeatId or player:  # 断线重连
            result["seatId"] = onlineSeatId
            result["reason"] = TYRoom.ENTER_ROOM_REASON_OK
            # self.sendSitRes(userId, clientId, result)
            self.sender.sendQuickStartRes(userId, clientId, result)
            self.sender.sendTableInfoRes(userId, clientId, 0)
            return

        idleSeatId = self.table.findIdleSeat(userId)
        ftlog.debug('doSitDown findIdleSeat-> ', userId, idleSeatId)
        if idleSeatId == 0:
            for s in self.table.seats :
                ftlog.debug('doSitDown full ', s.userId)
            # 座位已经满了, 返回失败消息
            result["isOK"] = False
            result["reason"] = TYRoom.ENTER_ROOM_REASON_TABLE_FULL
            # self.sendSitRes(userId, clientId, result)
            self.sender.sendQuickStartRes(userId, clientId, result)
            return

        if idleSeatId < 0 :
            # 断线重连机制出错了??
            # 已经在座位上坐下, 返回成功消息和桌子信息
            ftlog.warn(getMethodName(), "idleSeatId < 0",
                       "|userId, roomId, tableId, idleSeatId:", userId, self.table.roomId, self.table.tableId, idleSeatId)
            result["seatId"] = abs(idleSeatId)
            result["reason"] = TYRoom.ENTER_ROOM_REASON_OK
            # self.sendSitRes(userId, clientId, result)
            self.sender.sendQuickStartRes(userId, clientId, result)
            self.sender.sendTableInfoRes(userId, clientId, 0)
            return

        # 可以坐下
        if userId in self.table.observers:
            del self.table.observers[userId]
#         # 桌面带入金币的检查
#         lastUserId = self.table.getLastSeatUserId(idleSeatId)
#         if lastUserId and lastUserId != userId :
#             ftlog.warn('ERROR, seat Userid is not clean up !! tid=', self.table.tableId,
#                         'seatId=', idleSeatId, 'olduid=', lastUserId, 'newuid=', userId)
#             # 带入金币不足, 返回失败消息
#             result["isOK"] = False
#             result["reason"] = TYRoom.ENTER_ROOM_REASON_INNER_ERROR
#             # self.sendSitRes(userId, clientId, result)
#             self.sender.sendQuickStartRes(userId, clientId, result)
#             return

        if doBuyin:
            # 初始化, 当前用户带入的金币
            isSupportBuyin = dizhuconf.isSupportBuyin(clientId)
            roomBuyInChip = self.table.runConfig.buyinchip
            roomMinCoin = self.table.runConfig.minCoin
            buyin_chip = table_remote.setUpTableChipOnSitDown(userId, self.table.roomId, self.table.tableId,
                                                     idleSeatId, clientId, isSupportBuyin, continuityBuyin,
                                                     roomBuyInChip, roomMinCoin)
    
            ftlog.debug('doSitDown->userId=', userId, 'buyin_chip=', buyin_chip, self.table.roomId, self.table.tableId, idleSeatId)
            if buyin_chip <= 0 :
                # 带入金币不足, 返回失败消息
                result["isOK"] = False
                result["reason"] = TYRoom.ENTER_ROOM_REASON_LESS_MIN
                # self.sendSitRes(userId, clientId, result)
                self.sender.sendQuickStartRes(userId, clientId, result)
                return
        # 记录当前座位的userId, 以便对玩家的金币做恢复处理
        self.table.recordSeatUserId(idleSeatId, userId)
        # 设置玩家坐在座位上
        seat = self.table.seats[idleSeatId - 1]
        seat.userId = userId
        seat.online = True
        # 设置玩家的在线状态
        onlinedata.addOnlineLoc(userId, self.table.roomId, self.table.tableId, idleSeatId)
        result["seatId"] = idleSeatId
        result["reason"] = TYRoom.ENTER_ROOM_REASON_OK
        # 必须发送quick_start的成功消息, 客户端才能进入牌桌界面
        self.sender.sendQuickStartRes(userId, clientId, result)
        # 忽略sit的返回消息, 以table_info命令替代
        # self.sendSitRes(userId, clientId, result)
        # 初始化当前玩家的信息, 玩家的基本信息一旦建立,在当前牌桌内就不更改了
        player = self.table.players[idleSeatId - 1]
        player.initUser(continuityBuyin, 0)  # TODO isUsingScore 参数需要携带进来 
        
        # 向桌子上所有发送table_info
        self.sender.sendTableInfoResAll(0)
        # 发送机器人的邀请通知
        self.sender.sendRobotNotifyCallUp(None)
        # 启动ready的计时器
        msgPackParams = {'seatId' : player.seatId,
                         'userId' : player.userId
                         }
        interval = self.table.runConfig.actionReadyTimeOut
        if interval > 0:
            self.table.seatTimers[player.seatIndex].setup(interval, 'CL_READY_TIMEUP', msgPackParams)


    def doStandUp(self, userId, seatId, reason, clientId):
        '''
        玩家站起
        '''
        '''
        玩家的站起操作
        # 用户被踢出,用户断线
        # reason=0 表示用户主动调用，离开桌子
        # reason=1 网络系统短线，系统踢出，离开桌子
        # reason=2 ready超时，系统踢出，离开桌子
        # reason=3 牌桌流局，全部托管状态下，系统踢出，离开桌子
        # reason=4 游戏币不够，系统踢出，离开桌子
        # reason=5 游戏币太多了，系统踢出，离开桌子
        # reason=6 比赛，服务器换桌子
        # reason=99 系统维护，踢出，关闭房间
        '''
        seatIndex = seatId - 1
        player = self.table.players[seatIndex]
        if player.userId != userId :
            ftlog.warn('ERROR, doStandUp, the seat userId not match userId=', userId, 'seat.userId=', player.userId)
            return False
        
        tstate = self.table.status.state
        if tstate == DizhuState.TABLE_STATE_IDEL :
            '''
            空闲状态, 允许站起, 离开桌子
            '''
            ftlog.debug('the state is TABLE_STATE_IDEL, standup !', self.table.tableId, userId, seatId, reason)
            # 清理计时器
            self.table.seatTimers[seatIndex].cancel()
            # 清理座位信息
            self.table.seats[seatIndex].clear()
            # 清理玩家信息
            player.clear()
            try:
                # 清理在线信息
                if ftlog.is_debug() :
                    ftlog.debug("|locList:", onlinedata.getOnlineLocList(userId), caller=self)
                onlinedata.removeOnlineLoc(userId, self.table.roomId, self.table.tableId)
                if ftlog.is_debug() :
                    ftlog.debug("|locList:", onlinedata.getOnlineLocList(userId), caller=self)
                # 清理带入的金币
                table_remote.cleanUpTableChipOnStandUp(userId, self.table.roomId, self.table.tableId, clientId)
                # 清理当前座位的userId
                self.table.recordSeatUserId(seatId, 0)
                # 向桌子上所有发送table_info, 比赛阶段清理牌桌时无需刷新客户端
                if reason != TYRoom.LEAVE_ROOM_REASON_MATCH_END:
                    self.sender.sendTableInfoResAll(0)
                # 发送机器人通知
                self.sender.sendRobotNotifyShutDown(None)
                # 触发站起事件, 在事件处理器中, 处理: 江湖救急, 救济金发放, 购买金币提示等信息等业务逻辑
                if reason != TYRoom.LEAVE_ROOM_REASON_MATCH_END:
                    table_remote.doUserStandUp(userId, self.table.roomId, self.table.tableId, clientId, reason)
                # 更新当前桌子的快速开始积分
                self.table.room.updateTableScore(self.table.getTableScore(), self.table.tableId, force=True)
            except:
                ftlog.error('ERROR doStandUp TABLE_STATE_IDEL')
            return True

        if tstate == DizhuState.TABLE_STATE_CALLING :
            '''
            游戏进行中状态, 不允许站起, 不允许离开桌子
            等待超时的timer, 自动进入托管管状态
            '''
            if reason == TableStandUpEvent.REASON_GAME_ABORT :  # 叫牌阶段, 牌桌流局, 强制站起
                try:
                    ftlog.debug('the state is TABLE_STATE_IDEL, standup !', self.table.tableId, userId, seatId, reason)
                    # 清理在线信息
                    onlinedata.removeOnlineLoc(userId, self.table.roomId, self.table.tableId)
                    # 清理带入的金币
                    table_remote.cleanUpTableChipOnStandUp(userId, self.table.roomId, self.table.tableId, clientId)
                    # 清理当前座位的userId
                    self.table.recordSeatUserId(seatId, 0)
                    # 发送机器人通知
                    self.sender.sendRobotNotifyShutDown(None)
                    # 触发站起事件, 在事件处理器中, 处理: 江湖救急, 救济金发放, 购买金币提示等信息等业务逻辑
                    table_remote.doUserStandUp(userId, self.table.roomId, self.table.tableId, clientId, reason)
                    # 更新当前桌子的快速开始积分, 外层统一一次调用即可
                except:
                    ftlog.error('ERROR doStandUp TABLE_STATE_CALLING')
                return True
            else:
                ftlog.warn('the state is TABLE_STATE_CALLING, can not standup !', self.table.tableId, userId, seatId, reason)
            return

        if tstate == DizhuState.TABLE_STATE_PLAYING :
            '''
            游戏进行中状态, 不允许站起, 不允许离开桌子
            等待超时的timer, 自动进入托管管状态
            '''
            if reason == TableStandUpEvent.REASON_GAME_OVER :  # 叫牌阶段, 牌桌流局, 强制站起
                try:
                    ftlog.debug('the state is TABLE_STATE_PLAYING, standup !', self.table.tableId, userId, seatId, reason)
                    # 清理在线信息
                    onlinedata.removeOnlineLoc(userId, self.table.roomId, self.table.tableId)
                    # 清理带入的金币
                    table_remote.cleanUpTableChipOnStandUp(userId, self.table.roomId, self.table.tableId, clientId)
                    # 清理当前座位的userId
                    self.table.recordSeatUserId(seatId, 0)
                    # 发送机器人通知
                    self.sender.sendRobotNotifyShutDown(None)
                    # 触发站起事件, 在事件处理器中, 处理: 江湖救急, 救济金发放, 购买金币提示等信息等业务逻辑
                    table_remote.doUserStandUp(userId, self.table.roomId, self.table.tableId, clientId, reason)
                except:
                    ftlog.error('ERROR doStandUp REASON_GAME_OVER')
                return True
            else:
                ftlog.warn('the state is TABLE_STATE_PLAYING, can not standup !', self.table.tableId, userId, seatId, reason)
            return
        return


    def doReady(self, player, recvVoice):
        '''
        客户端, 准备
        '''
        if not player or self.table.status.state != DizhuState.TABLE_STATE_IDEL :
            ftlog.info('ERROR !!, doReady table.status=', self.table.status, player)
            return
        
        seat = self.table.seats[player.seatIndex]
        if seat.state == DizhuSeat.SEAT_STATE_READY :
            ftlog.info('ERROR !!,doReady, the seat state is already SEAT_STATE_READY', player.seatIndex, player.userId)
            return

        if seat.state != DizhuSeat.SEAT_STATE_WAIT :
            ftlog.info('ERROR !!,doReady, the seat state is not SEAT_STAT_WAIT', player.seatIndex,  player.userId)
            return

        # 切换座位的状态
        seat.state = DizhuSeat.SEAT_STATE_READY
        seat.call123 = -1
        seat.isReciveVoice = 1 if recvVoice else 0
        self.table.seatTimers[player.seatIndex].cancel()
        self.sender.sendUserReadyRes(player)

        # 检查是否所有座位都已经ready, 是否可以开局发牌
        if not self.table.isGameReady():
            return
        
        if self.table.isFriendTable():
            self.table.notStartGameTimer.cancel()

        self._doGameReady()
        
    def _doGameReady(self):
        # 所有座位均已经Ready, 开始发牌
        ftlog.debug('doGameReady ! all user is ready !!')
        # 取消所有的定时器
        self.table.cancelTimerAll()
        # 切换桌子状态至CALLING
        self.table.status.state = DizhuState.TABLE_STATE_CALLING
        # 发牌
        self._sendCard()
        # 选择第一个叫地主或叫分的玩家
        self._chooseFirstCall()
        uids = []
        cards = []
        for x in xrange(len(self.table.seats)) :
            seat = self.table.seats[x]
            uids.append(seat.userId)
            cards.append(seat.cards[:])
        
        self.table._createGameRound()
        self.table.gameRound.gameReady(cards, self.table.status.baseCardList[:])
        # 发送game_ready, 客户端展示手牌
        self.sender.sendGameReadyRes()
        # 启动第一个叫地主的倒计时
        readyNextDelay = self.table.runConfig.actionFirstCallDelayTimes
        self.table.tableTimer.setup(readyNextDelay, 'CL_READY_NEXT_DELAY', {})
        # 牌局记录器处理
        # BI数据汇报
        for player in self.table.players :
            self._reportBiGameEvent('TABLE_START', player, 0, 0, 0, [], '')
        # BI日志
        bireport.tableStart(self.table.gameId, self.table.roomId, self.table.tableId,
                            self.table.gameRound.roundId, uids, cards,
                            self.table.status.baseCardMulti,
                            self.table.status.baseCardType)


    def doReadyTimeOut(self, player):
        '''
        客户端, 准备超时
        '''
        if not player or self.table.status.state != DizhuState.TABLE_STATE_IDEL :
            ftlog.warn('ERROR !!, doReadyTimeOut table.status=', self.table.status, player)
            return
        self.doStandUp(player.userId, player.seatId, TableStandUpEvent.REASON_READY_TIMEOUT, player.clientId)


    def doFirstCallDizhu(self, player):
        '''
        延迟发送, 触发第一个叫地主的玩家
        '''
        if self.table.status.state != DizhuState.TABLE_STATE_CALLING :
            ftlog.warn('ERROR !!, doFirstCallDizhu table.status=', self.table.status, player)
            return
        self._doNextCall(0)


    def doCallDizhuTimeOut(self, player):
        '''
        叫地主超时
        '''
        if not player or self.table.status.state != DizhuState.TABLE_STATE_CALLING :
            ftlog.warn('ERROR !!, doCallDizhuTimeOut table.status=', self.table.status, player)
            return
        # 叫地主超时, 直接进入托管状态
        self._checkIfForceRobot(player, DizhuPlayer.TUGUAN_TYPE_TIMEOUT)
        # 系统主动替玩家进行叫地主
        self.doCallDizhu(player, -1, -1, DizhuPlayer.TUGUAN_TYPE_TIMEOUT)


    def _doCallDizhuVerify(self, player, grab, call):
        '''
        校验,是否可以进行叫地主的操作
        '''
        if self.table.status.nowOper != player.seatId :
            return False
        if call not in (0, 1):
            return False
        if len(self.table.status.callStr) == 4:
            return False
        return True


    def _doCallDizhuSetCall(self, player, call):
        seat = self.table.seats[player.seatIndex]
        if self.table.status.callGrade == -1:
            isTrueGrab = False
            seat.call123 = call
            if call == 1:
                self.table.status.diZhu = player.seatId
                self.table.status.callGrade = self.table.runConfig.firstCallValue
        else:
            isTrueGrab = True
            seat.call123 += call
            if call == 1:
                self.table.status.diZhu = player.seatId
                if self.table.isMatch:
                    self.table.status.callGrade += 1  # 比赛时, 分数加1
                else:
                    self.table.status.callGrade *= 2  # 非比赛, 分数翻倍
        return isTrueGrab

    def calcCurTotalMulti(self):
        return (self.table.status.callGrade
                * self.table.status.baseCardMulti
                * self.table.status.show
                * pow(2, self.table.status.bomb))

    def calcWinloseTotalMulti(self):
        return (self.table.status.callGrade
                * self.table.status.baseCardMulti
                * self.table.status.show
                * self.table.status.rangpaiMultiWinLose
                * pow(2, self.table.status.bomb)
                * self.table.status.chuntian)
        
    def doCallDizhu(self, player, grab, call, tuoGuanType):
        '''
        叫地主操作
        callType = 1 客户端点击"叫地主"按钮
        callType = 2 客户端超时,系统托管叫地主
        '''
        if not player or self.table.status.state != DizhuState.TABLE_STATE_CALLING :
            ftlog.warn('ERROR !!, doCallDizhu table.status=', self.table.status, player)
            return
        # 对于托管操作,进行call和grab的转换
        grab, call = self.punish.isRobotAutoCall(player.userId, grab, call, tuoGuanType) 
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
            try:
                event_remote.publishUserTableCallEvent(self.table.gameId, player.userId,
                                                       self.table.roomId, self.table.tableId,
                                                       call, isTrueGrab)
            except:
                ftlog.error('DizhuBaseGamePlay.doCallDizhu publishUserTableCallEvent')
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


    def doChuPaiTimeOut(self, player, cards, mcrc, tuoGuanType):
        if not player or self.table.status.state != DizhuState.TABLE_STATE_PLAYING :
            ftlog.warn('ERROR !!, doChuPaiTimeOut table.status=', self.table.status, player)
            return
        # 叫地主超时, 直接进入托管状态
        ftlog.debug('doChuPaiTimeOut->userId=', player.userId, 'tuoGuanType=', tuoGuanType)
        self._checkIfForceRobot(player, tuoGuanType)
        # 系统主动替玩家进行叫地主
        self.doChuPai(player, cards, mcrc, tuoGuanType)


    def _changeToRealCard(self, card):
        '''
        转换到实际的牌, 癞子玩法需要扩展
        '''
        return card


    def _doChuPaiVerifyCard(self, seatId, cards):
        if self.table.status.state != DizhuState.TABLE_STATE_PLAYING :
            return False, cards
        if seatId != self.table.status.nowOper :
            return False, cards
        
        if ((self.table.status.topSeatId == 0 or self.table.status.topSeatId == seatId)
            and not cards):
            ftlog.warn('_doChuPaiVerifyCard emptyCards seatId=', seatId, 'tableId=', self.table.tableId,
                        'seatId=', seatId, 'orgCard=', cards)
            return False, cards
            
        if cards is None:
            ftlog.warn('_doChuPaiVerifyCard badCards seatId=', seatId, 'tableId=', self.table.tableId,
                        'seatId=', seatId, 'orgCard=', cards)
            return False, cards
        
        cardErr = 0
        seat = self.table.seats[seatId - 1]
        seatCards = seat.cards[:]
        for c in cards:
            realCard = self._changeToRealCard(c)
            ftlog.debug('_doChuPaiVerifyCard->c=', c, 'realCard=', realCard, 'seatCards=', seatCards, 'cards=', cards)
            try:
                seatCards.remove(realCard)
            except:
                cardErr = 1
                break

        if cardErr:
            # 必须要出牌，则出最小的牌, 否则不出牌
            orgCard = cards
            if self.table.status.topSeatId == 0 or self.table.status.topSeatId == seatId:
                cards = self.card.findFirstCards(seat.cards)
            else:
                cards = []
            ftlog.warn('_doChuPaiVerifyCard seatId=', seatId, 'tableId=', self.table.tableId,
                        'seatId=', seatId, 'orgCard=', orgCard, 'serverChangeCards=', cards)
        return True, cards


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

    def nextStep(self, player):
        self.table.tableTimer.cancel();
        # 检查当前牌局是否结束
        if self._checkWinLose(player):
            # 牌局结束, 进行结算处理
            self._doWinLose(player)
        else:
            # 触发下一家操作的消息
            self._doNext(0)


    def _isGreaterThan(self, validCard, topCards):
        if not topCards:
            return True
        topValidCard = self.card.validateCards(topCards)
        if not topValidCard:
            return True
        return validCard.isCreaterThan(topValidCard)


    def _outCard(self, player, seat, cards):
        # 将玩家的手牌减去出的牌
        seat.cards = list(set(seat.cards) - set(cards))


    def doTuoGuan(self, player):
        if not player or (self.table.status.state != DizhuState.TABLE_STATE_CALLING and 
                          self.table.status.state != DizhuState.TABLE_STATE_PLAYING):
            ftlog.warn('ERROR !!, doTuoGuan table.status=', self.table.status, player)
            return
        ftlog.debug('doTuoGuan->userId=', player.userId)
        seatId = player.seatId
        seat = self.table.seats[seatId - 1]
        if not seat.isRobot :
            tc = seat.tuoguanCount
            maxtc = dizhuconf.getPublic().get('max_table_robot_count', 3)
            if tc < maxtc :
                seat.tuoguanCount += 1
            else:
                ftlog.info('ERROR, doTuoGuan client robot action reach max count !', tc, maxtc)
                self.sender.sendTuoGuanErrorRes(player.userId)
                return
        return self._doTuoGuan(player, False)


    def _doTuoGuan(self, player, isForceRobot):
        '''
        用户托管
        isForceRobot :  True 服务器端超时, 强制托管
                        False 客户端切换托管状态
        '''
        if not player or (self.table.status.state != DizhuState.TABLE_STATE_CALLING and 
                          self.table.status.state != DizhuState.TABLE_STATE_PLAYING):
            ftlog.warn('ERROR !!, doTuoGuan table.status=', self.table.status, player)
            return
        ftlog.debug('doTuoGuan->isForceRobot=', isForceRobot, 'userId=', player.userId)
        seatId = player.seatId
        seat = self.table.seats[seatId - 1]
        if isForceRobot:
            # 用户操作超时, 强制进入托管状态, 后续操作不再此方法内进行, 由调用者决定后续的操作
            seat.isRobot = 1
            self.punish.pushRobotPunishMsg(seatId, 1)
            if (self.table.isMatch and 'stageType' in self.table._match_table_info
                and self.table._match_table_info["stageType"] == StageType.ASS):
                if hasattr(seat, "forceTimeoutCount"):
                    seat.forceTimeoutCount += 1
                else:
                    seat.forceTimeoutCount = 1
                ftlog.debug('_doTuoGuan forceTimeoutCount=', seat.forceTimeoutCount, 'userId=', player.userId)
        else:
            # 用户点击 托管按钮, 切换托管的状态
            isRobot = seat.isRobot
            seat.isRobot = 1 if isRobot == 0 else 0
            self.punish.pushRobotPunishMsg(seatId, 1)
            if seat.isRobot == 0:
                seat.timeOutCount = 0
            # 如果是当前的操作者, 那么立即进行当前操作的超时处理, 代替玩家进行动作
            elif seatId == self.table.status.nowOper:
                if self.table.status.state == DizhuState.TABLE_STATE_CALLING :
                    # 系统主动替玩家进行叫地主
                    ftlog.debug('doTuoGuan->call -> doCallDizhu', 'userId=', player.userId)
                    self.doCallDizhu(player, -1, -1, DizhuPlayer.TUGUAN_TYPE_ALREADY_TUOGUAN)
                elif self.table.status.state == DizhuState.TABLE_STATE_PLAYING :
                    # 系统主动替玩家出牌
                    ftlog.debug('doTuoGuan->call -> doChuPai', 'userId=', player.userId)
                    self.doChuPai(player, [], self.table.status.cardCrc, DizhuPlayer.TUGUAN_TYPE_ALREADY_TUOGUAN)
        if (self.table.status.state != DizhuState.TABLE_STATE_CALLING and 
            self.table.status.state != DizhuState.TABLE_STATE_PLAYING) :
            # 如果是托管造成出牌导致winlose，此时状态已经变化，不需要在进行发送托管的消息了
            return
        # 给当前托管的玩家发送tableinfo
        # 2016-04-12取消tableInfo发送
        # self.sender.sendTableInfoRes(player.userId, player.clientId, 1)
        # 发送玩家托管消息
        self.table.gameRound.robot(seatId - 1, seat.isRobot)
        self.sender.sendTuoGuanRes(seatId)


    def _doShowCardVerify(self, player):
        if not self.table.runConfig.showCard :
            return 0
        seat = self.table.seats[player.seatIndex]
        if seat.isShow != 0:
            return 0
        if self.table.status.state == DizhuState.TABLE_STATE_PLAYING \
            and player.seatId == self.table.status.diZhu :
            c = 0
            for s in self.table.seats :
                c += s.outCardCount
            if c == 0 :
                return 2
        return 0


    def doShowCard(self, player):
        if not player or (self.table.status.state != DizhuState.TABLE_STATE_CALLING and 
                          self.table.status.state != DizhuState.TABLE_STATE_PLAYING):
            ftlog.warn('ERROR !!, doShowCard table.status=', self.table.status, player)
            return
        ftlog.debug('doShowCard userId=', player.userId)
        vs = self._doShowCardVerify(player)
        if vs > 0:
            seat = self.table.seats[player.seatIndex]
            if vs == 1:
                seat.isShow = 5
                if self.table.status.firstShow == 0 :
                    self.table.status.firstShow = player.seatId
            if vs == 2:
                seat.isShow = 2
            if vs == 1 or vs == 2 :
                m = 0
                for s in self.table.seats :
                    m = max(m, s.isShow)
                self.table.status.show = m

            self.sender.sendShowCardRes(player)

            # 记录牌局消息
            self.table.gameRound.show(player.seatIndex, self.table.status.show, self.calcCurTotalMulti())


    def doTreasurebox(self, player):
        pass
    
    def doOpenCardNote(self, player):
        isMatch = self.table.isMatch
        # 比赛场局记牌器在下发此消息时扣除背包金币，非比赛场局记牌器在结算时扣除带入金币
        if isMatch:
            if player.getCardNoteCount() <= 0:
                try:
                    if self.table.runConfig.cardNoteChip > 0:
                        trueDelta, _final = user_remote.incrUserChip(player.userId, self.table.gameId, -self.table.runConfig.cardNoteChip, 'MATCH_CARDNOTE_BETCHIP', 0, player.clientId)
                        if trueDelta == -self.table.runConfig.cardNoteChip:
                            if player.openCardNote():
                                ftlog.info('DizhuBaseGamePlay.doOpenCardNote isMatch userId=', player.userId,
                                           'cardNoteCount=', player.getCardNoteCount(),
                                           'buyinChip=', player.datas.get('chip'))
                                self.sender.sendCardNoteOpened(player)
                except:
                    pass
        else:
            if player.openCardNote():
                ftlog.info('DizhuBaseGamePlay.doOpenCardNote not isMatch userId=', player.userId,
                           'cardNoteCount=', player.getCardNoteCount(),
                           'buyinChip=', player.datas.get('buyinChip'))
                self.sender.sendCardNoteOpened(player)


    def _reportBiGameEvent(self, eventId, player, detalChip, state1, state2, cardlist, tag=''):
        '''
        汇报牌桌的游戏BI日志
        '''
        try:
            finalTableChip, finalUserChip = table_remote.doGetUserChips(player.userId, self.table.tableId, player.isSupportBuyin)
            bireport.reportGameEvent(eventId, player.userId, self.table.gameId, self.table.roomId,
                                     self.table.tableId, self.table.gameRound.number, detalChip,
                                     state1, state2, cardlist, player.clientId, finalTableChip, finalUserChip)
        except:
            ftlog.error()

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
            goodCard = self.table.runConfig.goodCard and not self.table.isMatch
            if ftlog.is_debug():
                ftlog.debug('DizhuBaseGamePlay._sendCard',
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


    def _chooseFirstCall(self):
        '''
        选择第一个叫地主或叫分的玩家座位ID
        '''
        slen = len(self.table.seats)
        if self.table.status.firstShow != 0:
            lop = []
            for x in xrange(slen):
                lop.append(x)
            lop[0] = slen
            self.table.status.nowOper = lop[self.table.status.firstShow - 1 ]
        else:
            firstCallSeatId = random.randint(1, slen)
            if self.table.status.goodSeatId != 0 and firstCallSeatId != self.table.status.goodSeatId:
                if self.table.runConfig.goodSeatRerandom :
                    firstCallSeatId = random.randint(1, slen)
            self.table.status.nowOper = firstCallSeatId


    def _getKickOutCard(self):
        '''
        由二斗地主进行扩展覆盖
        '''
        return []


    def _findNextCaller(self):
        nowopsid = self.table.status.nowOper
        if self.table.status.callStr == '' and nowopsid > 0:
            return nowopsid
        slen = len(self.table.seats)
        for i in xrange(len(self.table.seats)):
            nsid = (nowopsid + i) % slen
            seat = self.table.seats[nsid]
            if seat.userId != 0 and seat.state == DizhuSeat.SEAT_STATE_READY:
                if seat.call123 == 0:
                    continue
                return nsid + 1
        return 0


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
            interval = 0.1 if seat.isRobot else self.table.runConfig.optime
            self.table.tableTimer.setup(interval, 'CL_TIMEUP_CALL', params)
            # 牌局记录器处理
            self.table.gameRound.next(nsid - 1, grab, interval)
        else:
            ftlog.warn('_doNextCall can not found next caller...')


    def _checkGameStart(self):
        '''
        检查当前是否叫地主的状态, 
        返回值 : 0 - 叫地主结束, 开始出牌
                < 0 都不叫, 流局
                > 0 需要继续叫地主
        a叫 b叫 c叫 a叫 开局a地主
        a叫 b叫 c叫 a不 开局c地主
        a叫 b叫 c不 a叫 开局a地主
        a叫 b叫 c不 a不 开局b地主
        a叫 b不 c叫 a叫 开局a地主
        a叫 b不 c叫 a不 开局c地主
        a叫 b不 c不       开局a地主
        a不 b叫 c叫 b叫 开局b地主
        a不 b叫 c叫 b不 开局c地主
        a不 b叫 c不       开局b地主
        a不 b不 c叫       开局c地主
        a不 b不 c不       流局
        '''
        callstr = self.table.status.callStr
        if len(callstr) == 4 :
            return 0
        if callstr == '100' or callstr == '010' or callstr == '001' :
            return 0
        if callstr == '000' :
            return -1
        return 1
#         
#         tclen = len(callstr)
#         tc = int(callstr, 2)
#         if tclen < 3:
#             return 1
#         else:
#             if tc == 0:
#                 return -1
#             else:
#                 if tc <= 4 and tclen == 3:
#                     return 0
#                 if tc > 4 and tclen == 3:
#                     return 1
#                 if tclen == 4:
#                     return 0
#                 return -1


    def _gameStart(self):
        ftlog.debug('call finish, start game !!')
        # 取消所有的计数器
        self.table.cancelTimerAll()
        # 转换桌子的状态
        self.table.status.state = DizhuState.TABLE_STATE_PLAYING
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

        # 发送游戏开始的消息
        self.sender.sendGameStartRes()
        
        if not self.table.canJiabei():
            if self.table.huanpaiCount() > 0:
                self._startHuanpai()
            else:
                self._startChupai()
        else:
            # 进入农民加倍状态
            self.table.status.playingState = DizhuState.PLAYING_STATE_NM_JIABEI
            optime = self.table.runConfig.datas.get('jiabei.optime', 25)
            params = {
            }
            self.table.tableTimer.setup(optime, 'JIABEI_TIMEUP', params)
            self.sender.sendWaitJiabei(optime)
            
    def _startHuanpai(self):
        self.table.status.playingState = DizhuState.PLAYING_STATE_HUANPAI
        params = {}
        optime = self.table.runConfig.datas.get('huanpai.optime', 25)
        self.table.tableTimer.setup(optime, 'HUANPAI_TIMEUP', params)
        self.sender.sendStartHuanpaiRes(optime)
        
    def _startChupai(self):
        self.table.status.playingState = DizhuState.PLAYING_STATE_CHUPAI
        self._doNext(1)
    
    def _isAllNMSetMulti(self):
        for i, seat in enumerate(self.table.seats):
            if (i + 1 != self.table.status.diZhu
                and seat.seatMulti <= 0):
                return False
        return True
        
    def _isNMDouble(self):
        for i, seat in enumerate(self.table.seats):
            if (i + 1 != self.table.status.diZhu
                and seat.seatMulti > 1):
                return True
        return False
    
    def _isSeatMultiSet(self, seatIndex):
        return self.table.seats[seatIndex].seatMulti > 0
    
    def _setSeatMulti(self, seatIndex, multi):
        assert(not self._isSeatMultiSet(seatIndex))
        assert(multi > 0)
        self.table.seats[seatIndex].seatMulti = multi
        
    def doJiabei(self, player, jiabei, oper='user'):
        if self.table.status.state < DizhuState.TABLE_STATE_PLAYING:
            ftlog.warn('DizhuBaseGamePlay.doJiabei',
                       'userId=', player.userId,
                       'seatId=', player.seatId,
                       'oper=', oper,
                       'expect=', DizhuState.TABLE_STATE_PLAYING,
                       'state=', self.table.status.state,
                       'err=', 'BadState')
            return
        
        dizhuSeatId = self.table.status.diZhu
        if dizhuSeatId == player.seatId:
            # 地主加倍
            if self.table.status.playingState != DizhuState.PLAYING_STATE_DZ_JIABEI:
                ftlog.warn('DizhuBaseGamePlay.doJiabei',
                           'userId=', player.userId,
                           'seatId=', player.seatId,
                           'oper=', oper,
                           'playingState=', self.table.status.playingState,
                           'expect=', DizhuState.PLAYING_STATE_DZ_JIABEI,
                           'err=', 'BadPlayingState')
                return
            # 地主加倍完毕
            assert(not self._isSeatMultiSet(player.seatIndex))
            self._setSeatMulti(player.seatIndex, 2 if jiabei else 1)
            self.sender.sendJiabeiRes(player.seatId, jiabei)
            if self.table.huanpaiCount() > 0:
                self._startHuanpai()
            else:
                self._startChupai()
        else:
            if self.table.status.playingState != DizhuState.PLAYING_STATE_NM_JIABEI:
                ftlog.warn('DizhuBaseGamePlay.doJiabei',
                           'userId=', player.userId,
                           'seatId=', player.seatId,
                           'oper=', oper,
                           'playingState=', self.table.status.playingState,
                           'expect=', DizhuState.PLAYING_STATE_NM_JIABEI,
                           'err=', 'BadPlayingState')
                return
            if self._isSeatMultiSet(player.seatIndex):
                ftlog.warn('DizhuBaseGamePlay.doJiabei',
                           'userId=', player.userId,
                           'seatId=', player.seatId,
                           'oper=', oper,
                           'playingState=', self.table.status.playingState,
                           'err=', 'AlreadyJiabei')
                return
            
            self._setSeatMulti(player.seatIndex, 2 if jiabei else 1)
            self.sender.sendJiabeiRes(player.seatId, jiabei)
            
            if self._isAllNMSetMulti():
                self.table.tableTimer.cancel()
                # 农民加倍了
                if self._isNMDouble():
                    ftlog.info('DizhuBaseGamePlay.doJiabei isNMDouble',
                               'userId=', player.userId,
                               'seatId=', player.seatId,
                               'oper=', oper,
                               'playingState=', self.table.status.playingState)
                    self.table.status.playingState = DizhuState.PLAYING_STATE_DZ_JIABEI
                    params = {
                    }
                    optime = self.table.runConfig.datas.get('jiabei.optime', 25)
                    self.table.tableTimer.setup(optime, 'JIABEI_TIMEUP', params)
                    self.sender.sendWaitJiabei(optime)
                else:
                    if self.table.huanpaiCount() > 0:
                        self._startHuanpai()
                    else:
                        self._startChupai()
                     
    def doJiabeiTimeout(self):
        if ftlog.is_debug():
            ftlog.debug('DizhuBaseGamePlay.doJiabeiTimeout',
                        'tableId=', self.table.tableId,
                        'state=', self.table.status.state,
                        'playingState=', self.table.status.playingState)
        dizhuSeatId = self.table.status.diZhu
        self.table.tableTimer.cancel()
        if self.table.status.state == DizhuState.TABLE_STATE_PLAYING:
            if self.table.status.playingState == DizhuState.PLAYING_STATE_NM_JIABEI:
                for i in xrange(len(self.table.seats)):
                    if (dizhuSeatId != i + 1
                        and not self._isSeatMultiSet(i)):
                        player = self.table.players[i]
                        self.doJiabei(player, 0, 'server')
            elif self.table.status.playingState == DizhuState.PLAYING_STATE_DZ_JIABEI:
                dizhuSeatId = self.table.status.diZhu
                player = self.table.players[dizhuSeatId - 1]
                self.doJiabei(player, 0, 'server')
            
    def isAllSeatHuanpai(self):
        for seat in self.table.seats:
            if not seat.huanpaiOut:
                return False
        return True
    
    def removeCards(self, srcCards, cards):
        for card in cards:
            try:
                srcCards.remove(card)
            except:
                return False
        return True
            
    def setSeatCards(self, seatCards):
        for i, cards in seatCards:
            self.table.seats[i].cards = cards
            
    def doHuanpaiTimeout(self):
        if ftlog.is_debug():
            ftlog.debug('DizhuBaseGamePlay.doHuanpaiTimeout',
                        'tableId=', self.table.tableId,
                        'state=', self.table.status.state,
                        'playingState=', self.table.status.playingState)
        self.table.cancelTimerAll()
        for i, seat in enumerate(self.table.seats):
            if not seat.huanpaiOut:
                seatCards = seat.cards[:]
                random.shuffle(seatCards)
                seat.huanpaiOut = seatCards[0:self.table.huanpaiCount()]
                player = self.table.players[i]
                if player:
                    self.sender.sendHuanpaiRes(player)
        self.doEndHuanpai()
    
    def doEndHuanpai(self):
        self.table.cancelTimerAll()
        seats = self.table.seats[:]
        random.shuffle(seats)
        # 开始换牌
        seats.append(seats[0])
        for i in xrange(len(self.table.seats)):
            seats[i + 1].huanpaiIn = seats[i].huanpaiOut
            
        seatCardsOrg = [seat.cards[:] for seat in self.table.seats]
        for i, seat in enumerate(self.table.seats):
            # 移除huanpaiOut
            if not self.removeCards(seat.cards, seat.huanpaiOut):
                self.setSeatCards(seatCardsOrg)
                ftlog.error('DizhuBaseGamePlay.doEndHuanpai BadOutCard',
                            'tableId=', self.table.tableId,
                            'userId=', self.table.players[i].userId,
                            'seatId=', i + 1,
                            'seatOrgCards=', seatCardsOrg[i],
                            'huanpaiOut=', seat.huanpaiOut)
                break
            # 增加huanpaiIn
            seat.cards.extend(seat.huanpaiIn)
            ftlog.info('DizhuBaseGamePlay.doEndHuanpai',
                       'tableId=', self.table.tableId,
                       'userId=', self.table.players[i].userId,
                       'seatId=', i + 1,
                       'seatOrgCards=', seatCardsOrg[i],
                       'seatNowCards=', seat.cards,
                       'huanpaiOut=', seat.huanpaiOut,
                       'huanpaiIn=', seat.huanpaiIn)
        self.sender.sendEndHuanpaiRes()
        self._startChupai()
        
    def doHuanpai(self, player, cards):
        if ftlog.is_debug():
            ftlog.debug('DizhuBaseGamePlay.doHuanpai',
                        'userId=', player.userId,
                        'seatId=', player.seatId,
                        'cards=', cards,
                        'huanpaiOut=', self.table.seats[player.seatIndex].huanpaiOut,
                        'huanpaiCount=', self.table.huanpaiCount(),
                        'state=', self.table.status.state,
                        'playingState=', self.table.status.playingState)
        if len(cards) != self.table.huanpaiCount():
            ftlog.error('DizhuBaseGamePlay.doHuanpai BadCardLen',
                        'userId=', player.userId,
                        'seatId=', player.seatId,
                        'cards=', cards,
                        'huanpaiOut=', self.table.seats[player.seatIndex].huanpaiOut,
                        'huanpaiCount=', self.table.huanpaiCount(), 
                        'state=', self.table.status.state,
                        'playingState=', self.table.status.playingState)
            return
        
        if self.table.seats[player.seatIndex].huanpaiOut:
            ftlog.error('DizhuBaseGamePlay.doHuanpai AlreayHuanpai',
                        'userId=', player.userId,
                        'seatId=', player.seatId,
                        'cards=', cards,
                        'huanpaiOut=', self.table.seats[player.seatIndex].huanpaiOut,
                        'huanpaiCount=', self.table.huanpaiCount(), 
                        'state=', self.table.status.state,
                        'playingState=', self.table.status.playingState)
            return
        
        # 检查cards是否在座位的牌里
        seatCards = self.table.seats[player.seatIndex].cards[:]
        for card in cards:
            try:
                seatCards.remove(card)
            except:
                ftlog.error('DizhuBaseGamePlay.doHuanpai CardNoteInSeat',
                            'userId=', player.userId,
                            'seatId=', player.seatId,
                            'cards=', cards,
                            'card=', card,
                            'seatCards=', self.table.seats[player.seatIndex].cards,
                            'huanpaiOut=', self.table.seats[player.seatIndex].huanpaiOut,
                            'huanpaiCount=', self.table.huanpaiCount(), 
                            'state=', self.table.status.state,
                            'playingState=', self.table.status.playingState)
                return
            
        self.table.seats[player.seatIndex].huanpaiOut = cards
        ftlog.info('DizhuBaseGamePlay.doHuanpai Succ',
                   'userId=', player.userId,
                   'seatId=', player.seatId,
                   'cards=', cards,
                   'seatCards=', self.table.seats[player.seatIndex].cards,
                   'huanpaiOut=', self.table.seats[player.seatIndex].huanpaiOut,
                   'huanpaiCount=', self.table.huanpaiCount(), 
                   'state=', self.table.status.state,
                   'playingState=', self.table.status.playingState)
        
        self.sender.sendHuanpaiRes(player)
        
        if self.isAllSeatHuanpai():
            # 所有人换牌完毕
            self.doEndHuanpai()
        
    def _gameStartAfter(self):
        '''
        可扩展的游戏开始方法
        '''
        pass


    def _checkIfForceRobot(self, player, tuoGuanType):
        '''
        每次超时均检查是否需要强制进入托管状态
        '''
        seat = self.table.seats[player.seatIndex]
        if tuoGuanType == DizhuPlayer.TUGUAN_TYPE_USERACT :  # 用户出牌
            seat.timeOutCount = 0
        elif tuoGuanType == DizhuPlayer.TUGUAN_TYPE_TIMEOUT :  # 正常操作超时
            seat.timeOutCount = seat.timeOutCount + 1
            ftlog.debug('_checkIfForceRobot->userId=', player.userId,
                        'seat.timeOutCount=', seat.timeOutCount, 'die=', self.table.runConfig.robotTimes)
            if seat.timeOutCount >= self.table.runConfig.robotTimes :
                self._doTuoGuan(player, True)
            #else:
            #    if self.table.isMatch and  self.table._match_table_info["stageType"] == StageType.ASS:
            #        if hasattr(seat, "forceTimeoutCount"):
            #            seat.forceTimeoutCount += 1
            #        else:
            #            seat.forceTimeoutCount = 1
            #        ftlog.debug('_checkIfForceRobot calldizhu forceTimeoutCount=', seat.forceTimeoutCount, 'userId=', player.userId)


    def _findNextPlayerSeatId(self):
        nowopsid = self.table.status.nowOper
        slen = len(self.table.seats)
        for i in xrange(slen):
            index = (nowopsid + i) % slen
            seat = self.table.seats[index]
            if seat.userId > 0 and seat.state == DizhuSeat.SEAT_STATE_PLAYING :
                return index + 1
        return 0

    
    def opTimePunishMatch(self, seat):
        if (self.table.isMatch and 'stageType' in self.table._match_table_info
            and self.table._match_table_info["stageType"] == StageType.ASS):
            if hasattr(seat, "forceTimeoutCount"):
                ftlog.debug('opTimePunishMatch forceTimeoutCount=', seat.forceTimeoutCount, 'userId=', seat.userId)
                if hasattr(seat, "deltaOpTime"):
                    if seat.deltaOpTime < 10:
                        if seat.forceTimeoutCount % 2 == 0:
                            seat.deltaOpTime = (seat.forceTimeoutCount/2) * 5
                    
                    ftlog.debug('opTimePunishMatch forceTimeoutCount=', seat.forceTimeoutCount, 'seat.deltaOpTime=', seat.deltaOpTime, 'userId=', seat.userId)
                    return seat.deltaOpTime
                else:
                    if seat.forceTimeoutCount % 2 == 0:
                        seat.deltaOpTime = 5
                        ftlog.debug('opTimePunishMatch forceTimeoutCount=', seat.forceTimeoutCount, 'seat.deltaOpTime=', seat.deltaOpTime, 'userId=', seat.userId)
                        return seat.deltaOpTime
        return 0
    
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
                        
        if seat.isRobot == 1:
            # 如果是托管状态, 那么最短时间超时, 由超时处理中,处理是否出牌
            tuoGuanType = DizhuPlayer.TUGUAN_TYPE_ALREADY_TUOGUAN
            latetime = self.table.runConfig.optimeAlreadyTuoGuan
            autocard = 1
        else:
            # 正常出牌超时控制
            tuoGuanType = DizhuPlayer.TUGUAN_TYPE_TIMEOUT
            latetime = opTime
        # 只剩一张牌时，自动出牌
        if len(seat.cards) == 1 :
            tuoGuanType = DizhuPlayer.TUGUAN_TYPE_SYS_FAST_CARD
            latetime = self.table.runConfig.optimeOnlyOneCard
            autocard = 1
        # 如果上家出的是火箭, 那么自动不出牌
        if nsid in self._doubleKingNoCard :
            tuoGuanType = DizhuPlayer.TUGUAN_TYPE_SYS_FAST_CARD
            latetime = self.table.runConfig.optimeDoubleKing
            autocard = 1
            del self._doubleKingNoCard[nsid]
        # 启动出牌超时计时器
        params = {'tuoGuanType' : tuoGuanType,
                  'seatId' : nsid,
                  'userId' : seat.userId,
                  'ccrc' : self.table.status.cardCrc
                  }
        self.table.tableTimer.setup(latetime, 'CL_TIMEUP', params)
        # 牌局记录器处理
        self.table.gameRound.next(nsid - 1, 0, opTime)
        if autocard :
            # 自动出牌, 不发送next消息
            return
        # 发送下一个出牌的消息至客户端
        self.sender.sendChuPaiNextRes(nsid, opTime)


    def _checkWinLose(self, player):
        ftlog.debug('player->', player.userId)
        if len(self.table.seats[player.seatIndex].cards) == 0:
            return True
        else:
            return False


    def _doGameAbort(self):
        ftlog.debug('_doGameAbort, ismatch=', self.table.isMatch)
        if self.table.isMatch :
            self.table.room.matchPlugin.doWinLose(self.table.room, self.table, 0)
            return
        if self.table.isFriendTable():
            self.table.doGameAbort()
            return
        # 发送结算消息
        self.sender.sendWinLoseAbortRes()
        # 牌局记录器处理
        self.table.gameRound.gameAbort()
        self.table.gameRound.gameOverTimestamp = pktimestamp.getCurrentTimestamp()
        # 将所有人进行站起操作
        for p in self.table.players:
            self.doStandUp(p.userId, p.seatId, TableStandUpEvent.REASON_GAME_ABORT, p.clientId)
        # 清理当前的桌子
        self.table.clear(None)
        self.table.room.updateTableScore(self.table.getTableScore(), self.table.tableId, force=True)

        self.clearGamePlay()


    def _getRangpaiMultiWinLose(self):
        return 1

    def _doWinLose(self, player):
        ftlog.debug('_doWinLose player->', player.userId, player.seatId, self.table.isMatch)
        
        self.table.status.rangpaiMultiWinLose = self._getRangpaiMultiWinLose()
        
        if self.table.isMatch:
            self.table.room.matchPlugin.doWinLose(self.table.room, self.table, player.seatId)
            self.clearGamePlay()
            return
        
        if self.table.isFriendTable():
            self.table.doWinlose(player)
            return
        
        try: 
            ftlog.debug('tableConf_=', strutil.dumps(self.table.runConfig.datas))
            ftlog.debug('tableStatus_=', strutil.dumps(self.table.status.toInfoDictExt()))

            result = table_winlose.doTableWinLoseGT(self.table.roomId, self.table.tableId, 
                                                    self.table.gameRound.number, player.seatId, self)

            ftlog.debug('_doWinLose remote rpc return->', result)
            self.table.status.chuntian = result['chuntian']
            seatWinloseDetails = []
            totalMulti = self.calcWinloseTotalMulti()
            for i in xrange(len(self.table.seats)):
                skillInfo = result['skillScoreInfos'][i]
                seatWinloseDetails.append(SeatWinloseDetail({
                                                'score':skillInfo['score'],
                                                'level':skillInfo['level'],
                                                'premax':skillInfo['premaxscore'],
                                                'curmax':skillInfo['curmaxscore'],
                                                'add':skillInfo['addScore']
                                            },
                                            totalMulti,
                                            result['winStreak'][i],
                                            result['seat_delta'][i],
                                            result['seat_coin'][i]))
                
            winloseDetail = WinloseDetail(self.table.status.bomb,
                                          1 if self.table.status.chuntian > 1 else 0,
                                          self.table.status.show,
                                          self.table.status.baseCardMulti,
                                          self.table.status.rangpaiMultiWinLose,
                                          self.table.status.callGrade,
                                          self.calcWinloseTotalMulti(),
                                          1 if player.seatId == self.table.status.diZhu else 0,
                                          result['winslam'],
                                          self.table.runConfig.gslam,
                                          seatWinloseDetails)
            self.table.gameRound.gameWinlose(winloseDetail)
            self.table.gameRound.gameOverTimestamp = pktimestamp.getCurrentTimestamp()
            json_record = GameRoundCodecDictComplain().encode(self.table.gameRound)
            round_number = self.table.gameRound.roundId
            bireport.tableWinLose(self.table.gameId, self.table.roomId, self.table.tableId, 
                                  round_number, json_record)
            self.sender.sendWinLoseRes(result)
            
            for p in self.table.players :
                self.doStandUp(p.userId, p.seatId, TableStandUpEvent.REASON_GAME_OVER, p.clientId)
            self.table.clear(None)
            self.table.room.updateTableScore(self.table.getTableScore(), self.table.tableId, force=True)

            if dizhuconf.getPublic().get('enable_test_robot', 0) :
                self.sender.sendRobotNotifyCallUp(None)

            self.clearGamePlay()
        except:
            ftlog.exception()
            roundId = self.table.gameRound.number
            self._doGameAbort()
            bireport.tableWinLose(self.table.gameId, self.table.roomId, self.table.tableId, 
                                  roundId, '{"error":"exception abort !!"}')


