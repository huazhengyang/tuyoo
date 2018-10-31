# -*- coding:utf-8 -*-
'''
Created on 2016年9月22日

@author: zhaojiangang
'''
from datetime import datetime

from dizhu.entity.dizhuconf import DIZHU_GAMEID
from dizhu.friendtable import ft_service
from dizhu.gametable.dizhu_friend_table_sender import DizhuFTSender
from dizhu.gametable.dizhu_player import DizhuPlayer
from dizhu.gametable.dizhu_state import DizhuState
from dizhu.gametable.dizhu_table import DizhuTable
from dizhu.servers.room.rpc import ft_room_remote
from dizhu.servers.util.rpc import event_remote
from freetime.core.lock import locked
from freetime.core.protocol import FTTimeoutException
from freetime.entity.msg import MsgPack
from freetime.util import log as ftlog
from poker.entity.biz import bireport
from poker.entity.biz.content import TYContentItem
from poker.entity.configure import pokerconf
from poker.entity.dao import onlinedata, sessiondata
from poker.entity.events.tyevent import TableStandUpEvent
from poker.entity.game.rooms.room import TYRoom
from poker.entity.game.tables.table_timer import TYTableTimer
from poker.protocol import router, runcmd
from poker.util import timestamp as pktimestamp


class DizhuPlayerFriend(DizhuPlayer):
    def __init__(self, table, seatIndex, copyData=None):
        super(DizhuPlayerFriend, self).__init__(table, seatIndex, copyData)
        self.score = 0
        
    def initUser(self, isNextBuyin, isUsingScore):
        '''
        从redis里获取并初始化player数据, 远程操作
        '''
        from dizhu.servers.util.rpc import table_remote
        isSupportBuyin, cardNoteCount, clientId, datas = table_remote.doInitTableUserData(self.userId, self.table.bigRoomId,
                                                                  self.table.tableId, isNextBuyin,
                                                                  self.table.runConfig.buyinchip,
                                                                  True)
        self.isUsingScore = isUsingScore
        self.clientId = clientId
        self.isSupportBuyin = isSupportBuyin
        self.cardNoteCount = cardNoteCount
        self.inningCardNote = 0
        self.datas = datas
        if ftlog.is_debug():
            ftlog.debug('DizhuPlayerFriend->userId=', self.userId, 'seatIndex=', self.seatIndex,
                        'isUsingScore=', self.isUsingScore, 'isSupportBuyin=', self.isSupportBuyin,
                        'clientId=', self.clientId, 'cardNoteCount=', self.cardNoteCount,
                        'inningCardNote=', self.inningCardNote,
                        'data=', self.datas,
                        'player=', self)
            
class FTTableDetails(object):
    def __init__(self):
        self.ftId = None
        self.userId = None
        self.nRound = None
        self.fee = None
        self.canDouble = None
        self.playMode = None
        self.expires = None
        self.goodCard = None
        
    def fromDict(self, d):
        self.ftId = d['ftId']
        fee = d.get('fee')
        if fee:
            self.fee = TYContentItem.decodeFromDict(d['fee'])
        self.userId = d['userId']
        self.nRound = d['nRound']
        self.canDouble = d['canDouble']
        self.playMode = d['playMode']
        self.expires = d['expires']
        self.goodCard = d['goodCard']
        return self
        
class DizhuFriendTable(DizhuTable):
    def __init__(self, room, tableId):
        self._ftTable = None
        self._waitContinue = False
        self.preDisbindTimer = TYTableTimer(self)
        self.continueTimer = TYTableTimer(self)
        self.notStartGameTimer = TYTableTimer(self)
        self.forceDisbindTimer = TYTableTimer(self)
        super(DizhuFriendTable, self).__init__(room, tableId)
        self.gamePlay.sender = DizhuFTSender(self)
        
    @property
    def ftId(self):
        return self.ftTable.ftId if self.ftTable else None
    
    @property
    def ftTable(self):
        return self._ftTable
    
    def cancelTimerAll(self):
        '''
        清理所有的计时器
        '''
        super(DizhuFriendTable, self).cancelTimerAll()
        self.preDisbindTimer.cancel()
        self.continueTimer.cancel()
    
    def goodCardLucky(self):
        return self.runConfig.lucky if self.ftTable and self.ftTable.goodCard else 0
    
    def isFriendTable(self):
        return True
    
    def canJiabei(self):
        return self.ftTable and self.ftTable.canDouble
    
    def huanpaiCount(self):
        if not self.ftTable:
            return 0
        if self.ftTable.playMode.get('name') == 'change3':
            return 3
        return 0
    
    def isGameReady(self):
        return not self._waitContinue and self.isAllReady()
    
    def isFinishAllRound(self):
        return len(self.results) >= self.ftTable.nRound
    
    def _makePlayer(self, seatIndex):
        return DizhuPlayerFriend(self, seatIndex)
    
    def _processStatics(self, statics):
        # 大赢家发奖
        for i, seat in enumerate(statics.get('seats', [])):
            if seat.get('bigWinner', 0) == 1:
                seat['bigReward'] = 1
                ft_service.sendBigWinnerRewards(self.players[i].userId, self.roomId)

    def _doGameWin(self, player, result):
        results = self.results[:]
        results.append(result)
        if player:
            self.results.append(result)
        statics = None
        if self.isFinishAllRound():
            statics = self.staticsResults()
            self._processStatics(statics)
        self.gamePlay.sender.sendGameWinRes(player, statics, results)
        self.clearStatus()
        if self.isFinishAllRound():
            try:
                event_remote.publishMyFTFinishEvent(self.gameId, self.ftTable.userId, self.roomId, self.tableId, self.ftId)
            except:
                ftlog.error('DizhuFriendTable._doGameWin publishMyFTFinishEvent Error')
            self.results = []
            self._waitContinue = True
            for p in self.players:
                p.score = 0
            self.continueTimer.setup(self.runConfig.ftContinueTimeout, 'FT_CONTINUE_TIMEOUT', {})
        
    def _canDoLeave(self, userId):
        player = self.getPlayer(userId)
        if not self.ftTable or not player:
            return True
        # 创建者不可以站起，已经打了一局的不可以执行站起
        return self.ftTable.userId != player.userId and len(self.results) <= 0
    
    def _doLeave(self, msg, userId, clientId):
        '''
        玩家操作, 尝试离开当前的桌子
        实例桌子可以覆盖 _doLeave 方法来进行自己的业务逻辑处理
        '''
        result = {'gameId':self.gameId, 'userId':userId,
                  'roomId':self.roomId, 'tableId':self.tableId}
        
        player = self.getPlayer(userId)
        
        if msg.getParam('reason') == TYRoom.LEAVE_ROOM_REASON_LOST_CONNECTION:
            # 断线不做处理
            result['reason'] = TYRoom.LEAVE_ROOM_REASON_FORBIT
            self.gamePlay.sender.sendTableLeaveRes(userId, clientId, result)
            if player:
                self.seats[player.seatIndex].online = False
                self.gamePlay.sender.sendOnlineChanged(player)
            return
        
        if player and self.ftTable:
            # 如果是处于等待继续状态
            if self._waitContinue:
                # 创建者需要解散自建桌
                if userId == self.ftTable.userId:
                    # 直接解散
                    ftlog.info('DizhuFriendTable._doLeave DisbindTableWaitContinue userId=', userId,
                               'ftId=', self.ftId)
                    self._doDisbind(False)
                    result['reason'] = TYRoom.LEAVE_ROOM_REASON_ACTIVE
                    self.gamePlay.sender.sendTableLeaveRes(userId, clientId, result)
                    return
            else:
                # 已经开局了不能离开，只能发请求解散
                if len(self.results) > 0 or self.status.state > DizhuState.TABLE_STATE_IDEL:
                    result['reason'] = TYRoom.LEAVE_ROOM_REASON_FORBIT
                    self.gamePlay.sender.sendTableLeaveRes(userId, clientId, result) 
                    return
        self.gamePlay.doLeave(userId, clientId, True)
        
    def doGameAbort(self):
        result = {
            'base':1,
            'nowin':1
        }
        winloses = []
        for player in self.players:
            winlose = {
                'delta':0,
                'multi':0,
                'score':player.score          
            }
            winloses.append(winlose)
            try:
                self.room.reportBiGameEvent('TABLE_WIN', player.userId, self.roomId, self.tableId,
                                            self.gameRound.number, 0, 0, 0, [],
                                            'table_win')
            except:
                if ftlog.is_debug():
                    ftlog.exception()
        result['winloses'] = winloses
        self.gameRound.gameAbort()
        self._doGameWin(None, result)
    
    def doWinlose(self, player):
        # 计算春天
        dizhuseatId = self.status.diZhu
        if player.seatId != dizhuseatId: 
            if self.seats[dizhuseatId - 1].outCardCount == 1:
                self.status.chuntian = 2
        else:
            chuntian = True
            for i, seat in enumerate(self.seats):
                if i + 1 != dizhuseatId and seat.outCardCount > 0:
                    chuntian = False
                    break
            self.status.chuntian = 2 if chuntian else 1
    
        # 翻倍计算 叫地主的倍数
        windoubles = self.status.callGrade
        # 炸弹倍数
        windoubles *= pow(2, self.status.bomb)
        # 春天倍数
        windoubles *= self.status.chuntian
        # 底牌倍数
        windoubles *= self.status.baseCardMulti
        # 明牌倍数
        windoubles *= self.status.show
             
        dizhuwin = player.seatId == dizhuseatId
        windoubles = abs(windoubles)
        
        userIds = []
        baseScore = 1
        deltaScores = [0] * len(self.seats)
        multis = [0] * len(self.seats)
        
        # 计算所有农民的输赢
        for i, p in enumerate(self.players):
            userIds.append(p.userId)
            
            if i + 1 == dizhuseatId:
                gameRes = 1 if dizhuwin else -1
                try:
                    event_remote.publishGameOverEvent(p.userId,
                                                      DIZHU_GAMEID,
                                                      p.clientId,
                                                      self.roomId,
                                                      self.tableId,
                                                      gameRes,
                                                      0)
                except:
                    ftlog.error('DizhuFriendTable.doWinlose',
                                'userId=', p.userId,
                                'clientId=', p.clientId,
                                'roomId=', self.roomId,
                                'tableId=', self.tableId)
                continue
            
            seatMulti = max(self.seats[i].seatMulti, 1) * max(self.seats[dizhuseatId - 1].seatMulti, 1)
            seatMulti *= windoubles
            multis[i] = seatMulti
            multis[dizhuseatId - 1] += seatMulti
            
            deltaScore = baseScore * seatMulti
            
            if dizhuwin:
                deltaScore *= -1
    
            deltaScores[i] = deltaScore
            p.score += deltaScore
            
            deltaScores[dizhuseatId - 1] -= deltaScore
            self.players[dizhuseatId - 1].score -= deltaScore
            
            gameRes = -1 if dizhuwin else 1
            try:
                event_remote.publishGameOverEvent(p.userId,
                                                  DIZHU_GAMEID,
                                                  p.clientId,
                                                  self.roomId,
                                                  self.tableId,
                                                  gameRes,
                                                  0)
            except:
                ftlog.error('DizhuFriendTable.doWinlose',
                            'userId=', p.userId,
                            'clientId=', p.clientId,
                            'roomId=', self.roomId,
                            'tableId=', self.tableId)
                
        result = {
            'base':baseScore,
        }
        winloses = []
        for i, p in enumerate(self.players):
            winlose = {
                'delta':deltaScores[i],
                'multi':multis[i],
                'score':p.score          
            }
            winloses.append(winlose)
            try:
                self.room.reportBiGameEvent('TABLE_WIN', p.userId, self.roomId, self.tableId,
                                            self.gameRound.number, deltaScores[i], 0, 0, [],
                                            'table_win')
            except:
                if ftlog.is_debug():
                    ftlog.exception()
                
        result['winloses'] = winloses
#         winloseDetail = WinloseDetail(self.table.status.bomb,
#                                           1 if self.table.status.chuntian > 1 else 0,
#                                           self.table.status.show,
#                                           self.table.status.baseCardMulti,
#                                           self.table.status.rangpaiMultiWinLose,
#                                           self.table.status.callGrade,
#                                           self.calcWinloseTotalMulti(),
#                                           1 if player.seatId == self.table.status.diZhu else 0,
#                                           result['winslam'],
#                                           self.table.runConfig.gslam,
#                                           seatWinloseDetails)
#         self.table.gameRound.gameWinlose(winloseDetail)
        self.gameRound.gameOverTimestamp = pktimestamp.getCurrentTimestamp()
        try:
            round_number = self.gameRound.roundId if self.gameRound else 0
            bireport.tableWinLose(self.gameId, self.roomId, self.tableId, 
                                  round_number, {})
        except:
            pass
        self._doGameWin(player, result)
        
    def destroyFT(self, returnFee):
        # 清理桌子
        ftlog.info('DizhuFriendTable.destroyFT',
                   'tableId=', self.tableId,
                   'ftId=', self.ftId,
                   'returnFee=', returnFee,
                   'userIds=', [p.userId for p in self.players])
        ftTable = self.ftTable
        self.clearStatus()
        for p in self.players :
            if p.userId > 0:
                self._doStandupAndRoomLeave(p, p.clientId, TYRoom.LEAVE_ROOM_REASON_MATCH_END)
        self.clear(None)
        
        if ftTable:
            try:
                ft_room_remote.disbindFT(self.room.ctrlRoomId, ftTable.ftId, returnFee)
            except FTTimeoutException:
                ftlog.error('DizhuFriendTable.destroyFT',
                            'tableId=', self.tableId,
                            'ftId=', ftTable.ftId)
        
    def clearStatus(self):
        if ftlog.is_debug():
            ftlog.debug('>>> DizhuFriendTable.clearStatus',
                        'tableId=', self.tableId,
                        'ftId=', self.ftId)
        self._resetTableConf()  
        # 桌子数据恢复
        self._complain = None  # 桌内投诉配置
        self._complain_open = 0  # 桌内投诉是否开启
        self._base_table_info = None  # 基本的信息, 用于快速返回table_info
        self.gameRound = None  # 桌子的牌局控制
        self._clearReplayRound()
        # 重置牌局记录器
        # 重置所有的计时器
        self.cancelTimerAll()
        # 清理桌子状态
        self.status.clear()
        # 清理座位状态, 玩家信息
        for seat in self.seats:
            seat.clearStatus()
            
        self.gamePlay.clearGamePlay()
        
        self.preDisbind = False
        self.preDisbindSeatId = 0
        self.preDisbindExpires = 0
        self.preDisbindSeatState = [-1 for _ in xrange(len(self.seats))]
        self._waitContinue = False
        if ftlog.is_debug():
            ftlog.debug('<<< DizhuFriendTable.clearStatus',
                        'tableId=', self.tableId,
                        'ftId=', self.ftId)

    def clear(self, userids):
        '''
        完全清理桌子数据和状态, 恢复到初始化的状态
        '''
        if ftlog.is_debug():
            ftlog.debug('>>> DizhuFriendTable.clear',
                        'tableId=', self.tableId,
                        'ftId=', self.ftId)
            
        self._resetTableConf()  
        # 桌子数据恢复
        self._complain = None  # 桌内投诉配置
        self._complain_open = 0  # 桌内投诉是否开启
        self._base_table_info = None  # 基本的信息, 用于快速返回table_info
        self.gameRound = None  # 桌子的牌局控制
        self._clearReplayRound()
        # 重置牌局记录器
        # 重置所有的计时器
        self.cancelTimerAll()
        self.forceDisbindTimer.cancel()
        self.notStartGameTimer.cancel()
        # 清理桌子状态
        self.status.clear()
        # 清理座位状态, 玩家信息
        for x in xrange(len(self.seats)) :
            seat = self.seats[x]
            player = self.players[x]
            seat.clear()
            player.clear()
            player.score = 0
        
        self.gamePlay.clearGamePlay()
        
        self._ftTable = None
        self.results = []
        self.preDisbind = False
        self.preDisbindSeatId = 0
        self.preDisbindExpires = 0
        self.preDisbindSeatState = [-1 for _ in xrange(len(self.seats))]
        self._waitContinue = False
        
        if ftlog.is_debug():
            ftlog.debug('<<< DizhuFriendTable.clear',
                        'tableId=', self.tableId,
                        'ftId=', self.ftId)

    def calcBigWinners(self):
        players = self.players[:]
        players.sort(key=lambda p:p.score, reverse=True)
        ret = []
        for p in players:
            if not ret:
                ret.append(p)
                continue
            if p.score == ret[-1].score:
                ret.append(p)
            else:
                break
        if len(ret) == len(players):
            return []
        return ret
    
    def staticsResults(self):
        bigWinners = self.calcBigWinners()
        staticsSeats = []
        for p in self.players:
            bigWinner = 1 if bigWinners and p in bigWinners else 0
            staticsSeats.append({'win':cmp(p.score, 0), 'bigWinner':bigWinner})
        return {'seats':staticsSeats}
    
    def _doStandupAndRoomLeave(self, player, clientId, reason=TableStandUpEvent.REASON_GAME_OVER):
        userId = player.userId
        self.gamePlay.doStandUp(player.userId, player.seatId, reason, clientId)
        msgRes = MsgPack()
        if not pokerconf.isOpenMoreTable(clientId) :
            msgRes.setCmd("room_leave")
        else :
            msgRes.setCmd("room")
            msgRes.setResult("action", "leave")
        msgRes.setResult("reason", TableStandUpEvent.REASON_GAME_OVER)
        msgRes.setResult("gameId", self.gameId)
        msgRes.setResult("roomId", self.roomId)  # 处理结果返回给客户端时，部分游戏（例如德州、三顺）需要判断返回的roomId是否与本地一致
        msgRes.setResult("userId", userId)
        router.sendToUser(msgRes, userId)
    
    def _doReqDisbind(self, player, clientId):
        if self.preDisbind:
            ftlog.warn('DizhuFriendTable._doReqDisbind',
                       'tableId=', self.tableId,
                       'ftId=', self.ftId,
                       'seatId=', player.seatId,
                       'userId=', player.userId,
                       'err=', 'Already request')
            return
        
        if not self.ftTable:
            ftlog.warn('DizhuFriendTable._doReqDisbind',
                       'tableId=', self.tableId,
                       'ftId=', self.ftId,
                       'seatId=', player.seatId,
                       'userId=', player.userId,
                       'err=', 'ftTableIsNone')
            return
        
        ftlog.info('DizhuFriendTable._doReqDisbind',
                   'tableId=', self.tableId,
                   'ftId=', self.ftId,
                   'seatId=', player.seatId,
                   'userId=', player.userId)
        
        if len(self.results) == 0 and self.status.state <= DizhuState.TABLE_STATE_IDEL:
            if player.userId == self.ftTable.userId:
                returnFee = False if self._waitContinue else True
                self._doDisbind(returnFee)
            else:
                self._doStandupAndRoomLeave(player, clientId)
            return
        
        self.preDisbind = True
        self.preDisbindSeatId = player.seatId
        self.preDisbindSeatState[player.seatIndex] = 1
        optime = self.runConfig.optimeDisbind
        self.preDisbindExpires = pktimestamp.getCurrentTimestamp() + optime
        self.preDisbindTimer.setup(optime, 'FT_DISBIND_SURE_TIMEOUT', {})
        self.gamePlay.sender.sendReqDisbindRes(player, optime)
        
    def _calcDisbindStateCount(self):
        ret = [0,0,0]
        for state in self.preDisbindSeatState:
            ret[state] += 1
        return ret
    
    def _clearPreDisbindState(self):
        self.preDisbindTimer.cancel()
        self.preDisbind = False
        self.preDisbindSeatId = 0
        self.preDisbindExpires = 0
        for i in xrange(len(self.preDisbindSeatState)):
            self.preDisbindSeatState[i] = -1
    
    @locked
    def doFTEnter(self, ftId, userId):
        ftlog.info('DizhuFriendTable.doFTEnter',
                   'tableId=', self.tableId,
                   'ftId=', ftId,
                   'tableFtId=', self.ftId)
        if ftId != self.ftId:
            return -1, '该房间已经解散'
        
        player = self.getPlayer(userId)
        if player:
            return 0, ''
        
        idleSeatId = self.findIdleSeat(userId)
        if idleSeatId == 0:
            return -1, '该房间人数已满'
        
        if userId in self.observers:
            del self.observers[userId]
        
        seat = self.seats[idleSeatId - 1]
        seat.userId = userId
        seat.online = True
        # 设置玩家的在线状态
        onlinedata.addOnlineLoc(userId, self.roomId, self.tableId, idleSeatId)
        
        self.gamePlay.sender.sendQuickStartRes(userId, sessiondata.getClientId(userId),
                                               {'seatId':idleSeatId, 'reason':TYRoom.ENTER_ROOM_REASON_OK})
        
        player = self.players[idleSeatId - 1]
        player.initUser(0, 0)
        
        # 向桌子上所有发送table_info
        self.gamePlay.sender.sendTableInfoResAll(0)
        
        # 启动ready的计时器
        msgPackParams = {'seatId' : player.seatId,
                         'userId' : player.userId
                         }
        interval = self.runConfig.actionReadyTimeOut
        if interval > 0:
            self.seatTimers[player.seatIndex].setup(interval, 'CL_READY_TIMEUP', msgPackParams)
        
        return 0, ''
    
    def _doSit(self, msg, userId, seatId, clientId): 
        '''
        玩家操作, 尝试再当前的某个座位上坐下
        '''
        continuityBuyin = msg.getParam('buyin')
        continuityBuyin = 1 if continuityBuyin else 0
        self.gamePlay.doSitDown(userId, seatId, clientId, continuityBuyin, False)
        
    def _doDisbind(self, returnFee):
        # 解散牌局
        ftlog.info('DizhuFriendTable._doDisbind',
                   'tableId=', self.tableId,
                   'ftId=', self.ftId,
                   'returnFee=', returnFee,
                   'results=', self.results,
                   'state=', self.status.state)
        self._clearPreDisbindState()
        if self.results:
            statics = self.staticsResults()
            self.gamePlay.sender.sendDisbindRes(statics)
        self.destroyFT(returnFee)

    def _calcDisbindResult(self):
        # 0:不同意；1同意；2不在线；-1还没决定
        stateCount = [0, 0, 0, 0]
        for i in xrange(len(self.seats)):
            state = self.preDisbindSeatState[i]
            # 不在线的设置为stateCount[2]
            if state == 0 and not self.seats[i].online:
                stateCount[2] += 1
            else:
                stateCount[state] += 1
        # 还有人没回应返回-1
        if stateCount[-1] != 0:
            return -1
        
        # 1. 在线的都同意就解散
        # 2. max(2, seatCount - 1)个人同意就解散
        if ((stateCount[2] + stateCount[1] == len(self.seats))
             or (stateCount[1] >= max(len(self.seats) - 1, 2))):
            return 1
        return 0
        
    def _doReqDisbindAnswer(self, player, clientId, disbind):
        if self.preDisbind and self.preDisbindSeatState[player.seatIndex] == -1:
            self.preDisbindSeatState[player.seatIndex] = disbind
            disbindResult = self._calcDisbindResult()
            disbinds = self.preDisbindSeatState[:]
            ftlog.info('DizhuFriendTable._doReqDisbindAnswer',
                       'tableId=', self.tableId,
                       'ftId=', self.ftId,
                       'seatId=', player.seatId,
                       'userId=', player.userId,
                       'disbind=', disbind,
                       'disbinds=', disbinds,
                       'seatOnlines=', [s.online for s in self.seats],
                       'disbindResult=', disbindResult)
            if disbindResult != -1:
                self._clearPreDisbindState()
            self.gamePlay.sender.sendReqDisbindAnswerRes(player, disbinds)
            if disbindResult != -1:
                self.gamePlay.sender.sendReqDisbindResultRes(disbinds, disbindResult)
            if disbindResult == 1:
                self._doDisbind(len(self.results) == 0)
                
    def _doPreDisbindTimeout(self):
        ftlog.info('DizhuFriendTable._doPreDisbindTimeout',
                   'tableId=', self.tableId,
                   'ftId=', self.ftId)
        if self.preDisbind:
            noAnswerPlayers = []
            for player in self.players:
                if self.preDisbindSeatState[player.seatIndex] == -1:
                    noAnswerPlayers.append(player)
            for player in noAnswerPlayers:
                self._doReqDisbindAnswer(player, player.clientId, 0)
        
    def _doContinueTimeout(self):
        ftlog.info('DizhuFriendTable._doContinueTimeout',
                   'tableId=', self.tableId,
                   'ftId=', self.ftId)
        self._doDisbind(False)
        
    def _doReqInvite(self, player):
        ftlog.info('DizhuFriendTable._doReqInvite',
                   'userId=', player.userId,
                   'tableId=', self.tableId,
                   'ftId=', self.ftId)
        if self.ftTable:
            ft_service.inviteFriend(player.userId, self.ftTable)
    
    def _doOtherAction(self, msg, player, seatId, action, clientId):
        if action == 'ft_req_disbind':
            # 解散牌桌
            self._doReqDisbind(player, clientId)
        elif action == 'ft_req_disbind_answer':
            # 用户对解散牌桌请求的回应
            answer = msg.getParam('answer', 0)
            self._doReqDisbindAnswer(player, clientId, answer)
        elif action == 'FT_DISBIND_SURE_TIMEOUT':
            self._doPreDisbindTimeout()
        elif action == 'FT_FORCE_DISBIND_TIMEOUT':
            ftlog.info('DizhuFriendTable._doOtherAction disbindTable',
                       'reason=', 'FT_FORCE_DISBIND_TIMEOUT')
            self._doDisbind(False)
        elif action == 'FT_NOT_START_TIMEOUT':
            ftlog.info('DizhuFriendTable._doOtherAction disbindTable',
                       'reason=', 'FT_NOT_START_TIMEOUT')
            self._doDisbind(False)
        elif action == 'FT_CONTINUE_TIMEOUT':
            self._doContinueTimeout()
        elif action == 'ft_req_invite':
            self._doReqInvite(player)
        elif action == 'ft_continue':
            self._doFTContinue(player)

    def _doTableManage(self, msg, action):
        '''
        桌子内部处理所有的table_manage命令
        '''
        result = {'action' : action, 'isOK' : True}
        if action == 'ft_bind':
            ftTable = FTTableDetails().fromDict(msg.getParam('ftTable'))
            self._doFTBind(ftTable)
        elif action == 'ft_unbind':
            self._doFTUnbind(msg.get('ftId'))
        elif action == 'leave':
            userId = msg.getParam('userId')
            clientId = runcmd.getClientId(msg)
            self._doLeave(msg, userId, clientId)
        else:
            return super(DizhuFriendTable, self)._doTableManage(msg, action)
        return result
    
    def _doTableClear(self):
        self.clearStatus()
        for p in self.players:
            if p.userId > 0:
                self.gamePlay.doStandUp(p.userId, p.seatId, TableStandUpEvent.REASON_GAME_OVER, p.clientId)
        self.clear(None)
    
    def _doFTUnbind(self, ftId):
        if not self._ftTable or ftId != self.ftId:
            ftlog.warn('DizhuFriendTable._doFTUnbind DiffFTId tableId=', self.tableId,
                       'ftId=', ftId,
                       'tableFTId=', self.ftId)
            return
        self._doTableClear()
        ftlog.info('DizhuFriendTable._doFTUnbind',
                   'tableId=', self.tableId,
                   'ftId=', self._ftTable.ftId,
                   'nRound=', self._ftTable.nRound,
                   'canDouble=', self._ftTable.canDouble,
                   'playMode=', self._ftTable.playMode,
                   'expires=', datetime.fromtimestamp(self._ftTable.expires).strftime('%Y-%m-%d %H:%M:%S'))
        self._ftTable = None
        
    def _doFTBind(self, ftTable):
        self._doTableClear()
        self._ftTable = ftTable
        interval = ftTable.expires - pktimestamp.getCurrentTimestamp()
        self.notStartGameTimer.setup(self.runConfig.notStartTimeout, 'FT_NOT_START_TIMEOUT', {})
        self.forceDisbindTimer.setup(interval, 'FT_FORCE_DISBIND_TIMEOUT', {})
        ftlog.info('DizhuFriendTable._doFTBind',
                   'tableId=', self.tableId,
                   'ftId=', ftTable.ftId,
                   'nRound=', ftTable.nRound,
                   'canDouble=', ftTable.canDouble,
                   'playMode=', ftTable.playMode,
                   'goodCard=', ftTable.goodCard,
                   'expires=', datetime.fromtimestamp(ftTable.expires).strftime('%Y-%m-%d %H:%M:%S'))
    
    def _doFTContinue(self, player):
        if not self._waitContinue:
            ftlog.warn('DizhuFriendTable._doFTContinue BadWaitState tableId=', self.tableId,
                       'userId=', player.userId,
                       'ftId=', self.ftId)
            return
        
        if player.userId != self.ftTable.userId:
            ftlog.warn('DizhuFriendTable._doFTContinue BadCreator tableId=', self.tableId,
                       'userId=', player.userId,
                       'ftId=', self.ftId)
            return
        
        try:
            ec, expires = ft_room_remote.continueFT(self.room.ctrlRoomId, player.userId, self.ftId)
            if ec != 0:
                self.gamePlay.sender.sendFTContinueResError(ec, expires)
                return
        except:
            ftlog.error('DizhuFriendTable._doFTContinue Exception tableId=', self.tableId,
                        'userId=', player.userId,
                        'ftId=', self.ftId)
            self.gamePlay.sender.sendFTContinueResError(-1, '继续牌桌失败')
            return
        
        ftlog.info('DizhuFriendTable._doFTContinue',
                   'tableId=', self.tableId,
                   'userId=', player.userId,
                   'ftId=', self.ftId,
                   'nRound=', self._ftTable.nRound,
                   'canDouble=', self._ftTable.canDouble,
                   'playMode=', self._ftTable.playMode,
                   'expires=', expires)
        # 重置积分等信息
        self._ftTable.expires = expires
        self._waitContinue = False
        self.continueTimer.cancel()
        self.results = []
        for p in self.players:
            p.score = 0
        
        self.gamePlay.sender.sendFTContinueResOk(player, ft_service.getCardCount(player.userId))
        self.gamePlay.doReady(player, 1)
        if self.isAllReady():
            self.gamePlay._doGameReady()

