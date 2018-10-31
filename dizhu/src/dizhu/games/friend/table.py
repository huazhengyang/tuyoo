# -*- coding:utf-8 -*-
'''
Created on 2017年1月23日

@author: zhaojiangang
'''
from datetime import datetime
import functools

from dizhu.friendtable import ft_service
from dizhu.games.friend.event import FTDisbindEvent, FTBindEvent, \
    FTContinueEvent, FTContinueErrorEvent
from dizhu.games.friend.state import DisBandCommand
from dizhu.games.friend.tableproto import DizhuTableProtoFriend, FTLeaveReason
from dizhu.servers.room.rpc import ft_room_remote
from dizhucomm.core.const import StandupReason, ClearGameReason
from dizhucomm.core.events import GameClearEvent, GameRoundFinishEvent
from dizhucomm.core.table import DizhuTable
from dizhucomm.table.tablectrl import DizhuTableCtrl
from freetime.core.exception import FTTimeoutException
from freetime.core.lock import locked
from freetime.core.timer import FTTimer
from freetime.util import log as ftlog
from poker.entity.game.rooms.room import TYRoom
from poker.util import timestamp as pktimestamp
import copy
from poker.entity.dao import gamedata
import json
from dizhu.entity.dizhuconf import DIZHU_GAMEID


class DizhuTableFriend(DizhuTable):
    def __init__(self, room, tableId, dealer):
        super(DizhuTableFriend, self).__init__(room, tableId, dealer, True)

    @locked
    def disBand(self, reason):
        self._processCommand(DisBandCommand(reason))

    @property
    def replayMatchType(self):
        return 2
    
class DizhuTableCtrlFriend(DizhuTableCtrl):
    def __init__(self, room, tableId, dealer):
        super(DizhuTableCtrlFriend, self).__init__(room, tableId, dealer)
        
        self._ftTable = None
        self._results = [] # 记录所有有效局的结果
        self._lastResult = None # 记录最后一局的结果
        self._waitContinue = False
        
        self._preDisbind = False
        self._preDisbindSeat = None
        self._preDisbindExpires = 0
        self._preDisbindSeatState = [-1 for _ in xrange(len(self.table.seats))]
        self._preDisbindTimer = None
        
        self._continueTimer = None
        self._notStartTimer = None
        self._forceDisbindTimer = None
    
    @property
    def notStartTimeout(self):
        return self.table.runConf.datas.get('notStartTimeout', 600)
    
    @property
    def ftContinueTimeout(self):
        return self.table.runConf.datas.get('ftContinueTimeout', 3)
    
    @property
    def ftId(self):
        return self.ftTable.ftId if self.ftTable else None
    
    @property
    def ftTable(self):
        return self._ftTable
    
    @property
    def nRound(self):
        return len(self._results)
    
    @property
    def results(self):
        return self._results
    
    @property
    def lastResult(self):
        return self._lastResult

    @property
    def isFinished(self):
        return self.nRound == self.ftTable.nRound
    
    @locked
    def bindFT(self, ftTable):
        self._forceClear()
        self._ftTable = ftTable
        interval = ftTable.expires - pktimestamp.getCurrentTimestamp()
        self._notStartTimer = FTTimer(self.notStartTimeout, functools.partial(self.forceDisbindFT, True, FTLeaveReason.NOT_START))
        self._forceDisbindTimer = FTTimer(interval, functools.partial(self.forceDisbindFT, False, FTLeaveReason.SYSTEM_TIME_OUT))
        ftlog.info('DizhuTableCtrlFriend.bindFT',
                   'tableId=', self.tableId,
                   'ftId=', ftTable.ftId,
                   'nRound=', ftTable.nRound,
                   'canDouble=', ftTable.canDouble,
                   'playMode=', self.table.playMode,
                   'goodCard=', ftTable.goodCard,
                   'expires=', datetime.fromtimestamp(ftTable.expires).strftime('%Y-%m-%d %H:%M:%S'))
        self.table.runConf.jiabei = ftTable.canDouble
        self.table.runConf.goodCard = ftTable.goodCard
        self.table.fire(FTBindEvent(self.table, ftTable))
    
    @locked
    def enterFT(self, ftId, player):
        assert(not player.seat)
        if ftId != self.ftTable.ftId:
            return -1, '该房间已解散'
        
        if not self.table.findIdleSeat():
            return -1, '该房间已满'
        
        seat = self.table.findIdleSeat()
        if not seat:
            return -1, '该房间人数已满'

        ftlog.info('DizhuTableCtrlFriend.enterFT',
                   'tableId=', self.tableId,
                   'ftId=', ftId,
                   'userId=', player.userId)
        
        # 坐下
        self.table.sitdown(player, False)
        return 0, ''
    
    @locked
    def forceDisbindFT(self, returnFee, reason):
        ftlog.info('DizhuTableCtrlFriend.forceDisbindFT',
                   'returnFee=', returnFee,
                   'reason=', reason)
        self._doDisbind(returnFee, reason)

    @locked
    def reqDisbind(self, userId, seatId):
        '''
        解散请求
        '''
        try:
            seat = self.checkSeatAndPlayer(seatId, userId)
        except Exception, e:
            ftlog.warn('DizhuTableCtrlFriend.reqDisbind',
                       'tableId=', self.tableId,
                       'ftId=', self.ftTable.ftId if self.ftTable else None,
                       'seatId=', seatId,
                       'userId=', userId,
                       'warn=', e.message)
            return
        if self._preDisbind:
            ftlog.warn('DizhuTableCtrlFriend.reqDisbind',
                       'tableId=', self.tableId,
                       'ftId=', self.ftTable.ftId,
                       'seatId=', seatId,
                       'userId=', userId,
                       'warn=', 'Already request')
            return
        
        if not self.ftTable:
            ftlog.warn('DizhuTableCtrlFriend.reqDisbind',
                       'tableId=', self.tableId,
                       'seatId=', seatId,
                       'userId=', userId,
                       'err=', 'ftTable Is None')
            return
        
        ftlog.info('DizhuTableCtrlFriend.reqDisbind',
                   'tableId=', self.tableId,
                   'ftId=', self.ftTable.ftId,
                   'seatId=', (userId, seatId))
        
        if self.nRound == 0 and not self.table.gameRound:
            # 一局都没开始呢
            if userId == self.ftTable.userId:
                # 创建者
                returnFee = False if self._waitContinue else True
                reason = FTLeaveReason.GAME_OVER if self._waitContinue else FTLeaveReason.CREATOR_DISBAND
                self._doDisbind(returnFee, reason)
            else:
                self.proto.sendRoomLeave(seat, FTLeaveReason.INITIATE_QUIT)
                self.table.standup(seat, StandupReason.USER_CLICK_BUTTON)
                FTTimer(0, functools.partial(self.room.leaveRoom, userId, TYRoom.LEAVE_ROOM_REASON_ACTIVE))
        else:
            self._doReqDisbind(seat)
            # 向其他玩家发送解散请求
            self.proto.sendReqDisbindAll(seat) 
    
    @locked
    def reqDisbindAnswer(self, userId, seatId, answer):
        try:
            seat = self.checkSeatAndPlayer(seatId, userId)
        except Exception, e:
            ftlog.warn('DizhuTableCtrlFriend.reqDisbindAnswer',
                       'tableId=', self.tableId,
                       'ftId=', self.ftTable.ftId if self.ftTable else None,
                       'seatId=', seatId,
                       'userId=', userId,
                       'warn=', e.message)
        if not self._preDisbind:
            ftlog.warn('DizhuTableCtrlFriend.reqDisbindAnswer:',
                       'tableId=', self.tableId,
                       'ftId=', self._ftTable.ftId,
                       'seatId=', seatId,
                       'userId=', userId,
                       'warn=', 'Not request disbind state')
            return
        if self._preDisbindSeatState[seat.seatIndex] != -1:
            ftlog.warn('DizhuTableCtrlFriend.reqDisbindAnswer:',
                       'tableId=', self.tableId,
                       'ftId=', self._ftTable.ftId,
                       'seatId=', seatId,
                       'userId=', userId,
                       'disbindState=', self._preDisbindSeatState[seat.seatIndex],
                       'warn=', 'Has answered')
            return
        
        self._doReqDisbindAnswer(seat, answer)

    @locked
    def continueFT(self, userId, seatId):
        try:
            seat = self.checkSeatAndPlayer(seatId, userId)
        except Exception, e:
            ftlog.warn('DizhuTableCtrlFriend.continueFT',
                       'tableId=', self.tableId,
                       'ftId=', self.ftTable.ftId if self.ftTable else None,
                       'seatId=', seatId,
                       'userId=', userId,
                       'warn=', e.message)
        if not self._waitContinue:
            ftlog.warn('DizhuTableCtrlFriend.continueFT tableId=', self.tableId,
                        'userId=', seat.userId,
                        'ftId=', self._ftTable.ftId,
                        'error=', '不是等待继续的状态')
            return
            
        try:
            ec, expires = ft_room_remote.continueFT(self.room.ctrlRoomId, seat.userId, self._ftTable.ftId)
            if ec != 0:
                self.table.fire(FTContinueErrorEvent(self.table, seat, ec, expires))
                return
        except:
            ftlog.error('DizhuTableCtrlFriend.continueFT Exception tableId=', self.tableId,
                        'userId=', seat.userId,
                        'ftId=', self._ftTable.ftId)
            self.table.fire(FTContinueErrorEvent(self.table, seat, -1, '继续牌桌失败'))
            return
        
        ftlog.info('DizhuTableCtrlFriend.continueFT:',
                   'tableId=', self.tableId,
                   'userId=', seat.userId,
                   'ftId=', self._ftTable.ftId,
                   'nRound=', self._ftTable.nRound,
                   'canDouble=', self._ftTable.canDouble,
                   'playMode=', self.table.playMode,
                   'expires=', expires)
        
        self._ftTable.expires = expires
        self._waitContinue = False
        if self._continueTimer:
            self._continueTimer.cancel()
            self._continueTimer = None
        
        self.table.fire(FTContinueEvent(self.table, seat))
        self.table.ready(seat, seat.isReciveVoice)
    
    @locked
    def inviteFriend(self, userId, seatId):
        try:
            self.checkSeatAndPlayer(seatId, userId)
        except Exception, e:
            ftlog.warn('DizhuTableCtrlFriend.inviteFriend',
                       'tableId=', self.tableId,
                       'ftId=', self.ftTable.ftId if self.ftTable else None,
                       'seatId=', seatId,
                       'userId=', userId,
                       'warn=', e.message)
            return
        ft_service.inviteFriend(userId, self._ftTable)

    def setupTable(self):
        super(DizhuTableCtrlFriend, self).setupTable()
        self.table.on(GameRoundFinishEvent, self._onGameRoundFinish)
        self.table.on(GameClearEvent, self._onGameClear)

    def staticsResults(self):
        '''
        好友桌结果
        '''
        if self.nRound == 0:
            return None
        bigWinners = self._calcBigWinners()
        staticsSeats = []
        for s in self.table.seats:
            bigWinner = 1 if bigWinners and s.player in bigWinners else 0
            staticsSeats.append({'win':cmp(s.player.score, 0), 'bigWinner':bigWinner, 'nickname': s.player.name, 'avatar': s.player.purl, 'winCount': s.player.winCount})
        return {'seats':staticsSeats}
    
    def calcDisbindResult(self):
        '''
        return : -1 未结束 0 解散失败 1 解散成功 
        '''
        # index = 0:不同意；1同意；2不在线；-1还没决定
        stateCount = [0, 0, 0, 0]
        for i in xrange(len(self.table.seats)):
            state = self._preDisbindSeatState[i]
            # 不在线的设置为stateCount[2]
            if state == 0 and not self.table.seats[i].player.online:
                stateCount[2] += 1
            else:
                stateCount[state] += 1
        # 还有人没回应返回-1
        if stateCount[-1] != 0:
            return -1
        
        # 1. 在线的都同意就解散
        # 2. max(2, seatCount - 1)个人同意就解散
        if ((stateCount[2] + stateCount[1] == len(self.table.seats))
             or (stateCount[1] >= max(len(self.table.seats) - 1, 2))):
            return 1
        return 0
    
    def _doReqDisbind(self, seat):
        self._preDisbind = True
        self._preDisbindSeat = seat
        self._preDisbindSeatState[seat.seatIndex] = 1
        optime = self.table.runConf.optimeDisbind
        self._preDisbindExpires = pktimestamp.getCurrentTimestamp() + optime
        self._preDisbindTimer = FTTimer(optime, functools.partial(self._doPreDisbindTimeout))

    def _doReqDisbindAnswer(self, seat, answer):
        self._preDisbindSeatState[seat.seatIndex] = answer
        disbindResult = self.calcDisbindResult()
        disbinds = self._preDisbindSeatState[:]
        ftlog.info('DizhuTableCtrlFriend.reqDisbindAnswer',
                   'tableId=', self.tableId,
                   'ftId=', self._ftTable.ftId,
                   'seatId=', seat.seatId,
                   'userId=', seat.userId,
                   'answer=', answer,
                   'disbinds=', disbinds,
                   'seatOnlines=', [s.player.online for s in self.table.seats],
                   'disbindResult=', disbindResult)
        self.proto.sendReqDisbindAnswerResAll(seat, disbinds)
        if disbindResult != -1:
            self._doClearPreDisbindState()
            self.proto.sendReqDisbindResultResAll(disbinds, disbindResult)
        if disbindResult == 1:
            self._doDisbind(self.nRound == 0, FTLeaveReason.ALL_DISBAND)

    def _doDisbind(self, returnFee, reason):
        # 解散牌局
        ftlog.info('DizhuTableCtrlFriend._doDisbind',
                   'tableId=', self.tableId,
                   'ftId=', self._ftTable.ftId,
                   'returnFee=', returnFee,
                   'results=', self._results,
                   'state=', self.table.state)
        try:
            ftlog.debug("saveFTRecord _doDestroyFT")
            self.saveFTRecord()
        except:
            ftlog.error('saveFTRecord error')
        self._doClearPreDisbindState()
        self.table.fire(FTDisbindEvent(self.table, returnFee, reason))
        userIds = [s.userId for s in self.table.seats]
        self.table.disBand(ClearGameReason.GAME_OVER)
        for uid in userIds:
            FTTimer(0, functools.partial(self.room.leaveRoom, uid, TYRoom.LEAVE_ROOM_REASON_TIMEOUT))
        self._doDestroyFT(returnFee)
        
    def _doPreDisbindTimeout(self):
        ftlog.info('DizhuTableCtrlFriend._doPreDisbindTimeout',
                   'tableId=', self.tableId,
                   'ftId=', self._ftTable.ftId)
        
        if not self._preDisbind:
            return
        
        noAnswerSeats = []
        for i, seat in enumerate(self.table.seats):
            if self._preDisbindSeatState[i] == -1:
                noAnswerSeats.append(seat)

        for seat in noAnswerSeats:
            self._doReqDisbindAnswer(seat, 0)
        
    def _doFTContinueTimeout(self):
        ftlog.info('DizhuTableCtrlFriend._doFTContinueTimeout',
                   'tableId=', self.tableId,
                   'ftId=', self._ftTable.ftId)
        if not self._waitContinue:
            return
        self._doDisbind(False, FTLeaveReason.GAME_OVER)
    
    def saveFTRecord(self):
        '''
        保存好友桌战绩记录
        '''
        copyResults = copy.deepcopy(self.results)
        totalRound = self.ftTable.nRound
        curRound = len(self.results)
        ftlog.debug("saveFTRecord self.results =", self.results, "self.table =", self.table, "totalRound =", totalRound, "curRound =", curRound)
        if curRound == 0:
            # results 为空不保存
            return

        for i in xrange(len(self.table.seats)):
            seat = self.table.seats[i]
            uid = seat.userId
            record = {}
            record["ftId"] = self.ftId
            record['totalRound'] = totalRound
            record['curRound'] = curRound
            record['curSeatId'] = seat.seatId
            record['results'] = copyResults
            timestamp = pktimestamp.getCurrentTimestamp()
            record['time'] = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M")
            records = gamedata.getGameAttr(uid, DIZHU_GAMEID, "friendTableRecords")
            if records:
                records = json.loads(records)
            else:
                records = []

            records.insert(0, record)
            if len(records) > 10:
                del records[-1]

            ftlog.debug("saveFTRecord userId =", uid, "record =", record, "records =", records)
            gamedata.setGameAttr(uid, DIZHU_GAMEID, "friendTableRecords", json.dumps(records))
    
    def _doDestroyFT(self, returnFee):
        # 清理桌子
        ftlog.info('DizhuTableCtrlFriend._doDestroyFT',
                   'tableId=', self.tableId,
                   'ftId=', self._ftTable.ftId,
                   'returnFee=', returnFee,
                   'userIds=', [s.userId for s in self.table.seats])

        ftTable = self.ftTable
        self._doClearFTTable()
        if ftTable:
            try:
                ft_room_remote.disbindFT(self.room.ctrlRoomId, ftTable.ftId, returnFee)
            except FTTimeoutException:
                ftlog.error('DizhuTableCtrlFriend._doDestroyFT',
                            'tableId=', self.tableId,
                            'ftId=', ftTable.ftId,
                            'returnFee=', returnFee)
        
    def _doClearPreDisbindState(self):
        if self._preDisbindTimer:
            self._preDisbindTimer.cancel()
            self._preDisbindTimer = None
        self._preDisbind = False
        self._preDisbindSeat = None
        self._preDisbindExpires = 0
        self._preDisbindSeatState = [-1 for _ in xrange(len(self.table.seats))]

    def _doClearFTTable(self):
        self._ftTable = None
        self._results = [] # 记录所有有效局的结果
        self._lastResult = None # 记录最后一局的结果
        self._waitContinue = False
        
        self._doClearPreDisbindState()
        
        if self._continueTimer:
            self._continueTimer.cancel()
            self._continueTimer = None
            
        if self._notStartTimer:
            self._notStartTimer.cancel()
            self._notStartTimer = None
        
        if self._forceDisbindTimer:
            self._forceDisbindTimer.cancel()
            self._forceDisbindTimer = None
        
    def _calcBigWinners(self):
        '''
        @return 大赢家数组 players
        '''
        seats = self.table.seats[:]
        seats.sort(key=lambda s:s.player.score, reverse=True)
        ret = []
        for s in seats:
            if not ret:
                ret.append(s.player)
                continue
            if s.player.score == ret[-1].score:
                ret.append(s.player)
            else:
                break
        if len(ret) == len(seats):
            return []
        return ret

    def _recordResult(self, gameResult):
        # 记录游戏结果
        ftlog.info('DizhuTableCtrlFriend.recordGameResult',
                   'tableId=', self.tableId,
                   'ftId=', self._ftTable.ftId,
                   'result=', gameResult)
        result = {}
        result['base'] = gameResult.baseScore
        winloses = []
        for sst in gameResult.seatStatements:
            if sst.isWin:
                sst.seat.player.winCount += 1

            seat_result = {}
            seat_result['delta'] = sst.delta
            seat_result['multi'] = sst.totalMulti
            seat_result['score'] = sst.final
            seat_result['isDizhu'] = sst.seat == gameResult.gameRound.dizhuSeat
            seat_result['nickname'] = sst.seat.player.name
            seat_result['avatar'] = sst.seat.player.purl
            winloses.append(seat_result)
        result['winloses'] = winloses
        self._lastResult = result
        if not gameResult.gameRound.dizhuSeat:
            self._lastResult['nowin'] = 1
        else:
            self._results.append(result)

    def _onGameRoundFinish(self, event):
        if ftlog.is_debug():
            ftlog.debug('DizhuTableCtrlFriend._onGameRoundFinish',
                        'tableId=', event.table.tableId,
                        'seats=', [(s.userId, s.seatId) for s in event.table.seats])
        self._recordResult(event.gameResult)
    
    def _onGameClear(self, event):
        if ftlog.is_debug():
            ftlog.debug('DizhuTableCtrlFriend._onGameClear',
                        'tableId=', event.table.tableId,
                        'seats=', [(s.userId, s.seatId) for s in event.table.seats])
        
        self._lastResult = None
        if self.isFinished:
            self._doFinish()
    
    def _doFinish(self):
        # 好友桌结束了
        ftlog.info('DizhuTableCtrlFriend._doFinish',
                   'tableId=', self.tableId,
                   'ftId=', self._ftTable.ftId)
        
        try:
            ftlog.debug("saveFTRecord _doFinish")
            self.saveFTRecord()
        except:
            ftlog.error('saveFTRecord error')
        
        self._results = []
        for s in self.table.seats:
            s.player.score = 0
            s.player.winCount = 0
        self._lastResult = None
        
        if not self._waitContinue:
            # 续桌倒计时
            self._continueTimer = FTTimer(self.ftContinueTimeout, functools.partial(self._doFTContinueTimeout))
            self._waitContinue = True
        
    def _forceClear(self):
        self.table.forceClear()

    def _makeTable(self, tableId, dealer):

        return DizhuTableFriend(self.room, tableId, dealer)

    def _makeProto(self):
        return DizhuTableProtoFriend(self)


