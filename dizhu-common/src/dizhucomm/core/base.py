# -*- coding:utf-8 -*-
'''
Created on 2016年12月22日

@author: zhaojiangang
'''
import functools
import time

from dizhucomm.utils.obser import Observable
from freetime.core.lock import FTLock, locked
from freetime.core.timer import FTTimer
import freetime.util.log as ftlog


class TableCommand(object):
    def __init__(self):
        # 
        self.table = None
        # 
        self.timestamp = None
        
    @property
    def playMode(self):
        return self.table.dealer.playMode
        
class TableStateBase(object):
    def processCommand(self, cmd):
        raise NotImplementedError 

def TableAction(cmd):
    raise NotImplementedError

class TableState(TableStateBase):
    STATE_CONTINUE = None
    STATE_DONE = TableStateBase()
    
    def __init__(self, name):
        self._name = name
        # 父状态
        self._parent = None
        # 子节点
        self._childrenList = []
        self._myTreeList = []
        # 进入该状态的action列表
        self._entryActionList = []
        # 该状态的action列表
        self._actionList = []
        # 离开该状态的action列表
        self._exitActionList = []
        # 状态机
        self._sm = None
        
    @property
    def name(self):
        return self._name
    
    @property
    def parent(self):
        return self._parent
    
    @property
    def sm(self):
        return self._sm
    
    def getMyTreeList(self):
        if not self._myTreeList:
            self._myTreeList = [self]
            parent = self._parent
            while parent:
                self._myTreeList.append(parent)
                parent = parent._parent
        return self._myTreeList
    
    def addChild(self, child):
        assert(not child._parent)
        self._childrenList.append(child)
        child._parent = self
        return self
    
    def ancestorsOf(self, other):
        while other:
            if other.parent == self:
                return True
            other = other.parent
        return False
    
    def offspringOf(self, other):
        return other.ancestorsOf(self)
        
    def processCommand(self, cmd):
        assert(cmd.table.state == self)
        nextState = TableState.STATE_CONTINUE
        for action in self._actionList:
            newState = action(cmd)
            if newState == TableState.STATE_DONE:
                break
            elif newState != TableState.STATE_CONTINUE:
                nextState = newState
                break
        
        if (nextState != TableState.STATE_CONTINUE
            and nextState != self):
            self._transform(self, nextState, cmd)
        return nextState
    
    @classmethod
    def calcExitAndEntryPath(cls, fromST, toST):
        fromTreeList = fromST.getMyTreeList()
        toTreeList = toST.getMyTreeList()
        
        exitPath = []
        entryPath = []
        
        breakST = None
        # 逐级向上返回，直到是toST或者toST的祖先节点
        for st in fromTreeList:
            if st.ancestorsOf(toST) or st == toST:
                breakST = st
                break
            exitPath.append(st)
        
        for st in toTreeList:
            if st == breakST:
                break
            entryPath.append(st)
        return exitPath, entryPath[::-1]
        
    @classmethod
    def _transform(cls, oldState, newState, cmd):
        '''
        '''
        assert(oldState != newState)
        exitPath, entryPath = cls.calcExitAndEntryPath(oldState, newState)
        for st in exitPath:
            cmd.table._state = st
            st._processExit(cmd)
        
        for st in entryPath:
            cmd.table._state = st
            st._processEntry(cmd)
 
        ftlog.info('Table state changed',
                   'tableId=', cmd.table.tableId,
                   'oldState=', oldState.name,
                   'newState=', newState.name)
        
    def _addAction(self, action):
        self._actionList.append(action)
        
    def _insertEntryAction(self, index, action):
        self._entryActionList.insert(index, action)
        
    def _addEntryAction(self, action):
        self._entryActionList.append(action)
        
    def _addExitAction(self, action):
        self._exitActionList.append(action)

    def _processExit(self, cmd):
        for action in self._exitActionList:
            action(cmd)
    
    def _processEntry(self, cmd):
        for action in self._entryActionList:
            action(cmd)

class TableStateMachine(object):
    def __init__(self):
        self._stateMap = {}
        
    def findStateByName(self, name):
        return self._stateMap.get(name)
    
    def addState(self, state):
        # 添加state和state的所有子孙
        states = [state]
        while states:
            state = states.pop(0)
            assert(not self.findStateByName(state.name))
            self._stateMap[state.name] = state
            state._sm = self
            states.extend(state._childrenList)

class PlayerBase(object):
    def __init__(self, room, userId):
        self._room = room
        self._userId = userId
        self._seat = None
        
    @property
    def userId(self):
        return self._userId
    
    @property
    def room(self):
        return self._room
    
    @property
    def seat(self):
        return self._seat
    
    @property
    def table(self):
        return self._seat.table if self._seat else None
    
    @property
    def tableId(self):
        return self.table.tableId if self.table else None
    
    @property
    def seatId(self):
        return self._seat.seatId if self._seat else 0
        
class SeatBase(object):
    def __init__(self, table, seatIndex, seatId):
        # 属于哪个桌子
        self._table = table
        # 座位index
        self._seatIndex = seatIndex
        # seatId
        self._seatId = seatId
        # 该座位的玩家
        self._player = None
        # 下一个座位
        self._next = None
        # 该座位定时器
        self._timer = None
        
    @property
    def table(self):
        return self._table
    
    @property
    def tableId(self):
        return self._table.tableId
    
    @property
    def seatId(self):
        return self._seatId
    
    @property
    def seatIndex(self):
        return self._seatIndex
    
    @property
    def state(self):
        return self._state
    
    @property
    def player(self):
        return self._player
    
    @property
    def next(self):
        return self._next
    
    @property
    def userId(self):
        return self._player.userId if self._player else 0
    
    def startTimer(self, delay, func, *args, **kw):
        self.cancelTimer()
        self._timer = FTTimer(delay, functools.partial(func, *args, **kw))
    
    def cancelTimer(self):
        if self._timer:
            self._timer.cancel()
            self._timer = None
        
class TableBase(Observable):
    def __init__(self, room, tableId, dealer):
        super(TableBase, self).__init__()
        # 房间
        self._room = room
        # 当前状态
        self._state = dealer.sm.findStateByName('idle')
        # 桌子ID
        self._tableId = tableId
        # 玩法
        self._dealer = dealer
        # 桌子定时器
        self._timer = None
        # 所有座位
        self._seats = []
        # 锁
        self.locker = FTLock(self.__class__.__name__ + "_%d" % id(self))
    
    @property
    def sm(self):
        return self._dealer.sm

    @property
    def playMode(self):
        return self._dealer.playMode

    @property
    def state(self):
        return self._state
    
    @property
    def gameId(self):
        return self.room.gameId
    
    @property
    def room(self):
        return self._room
    
    @property
    def roomId(self):
        return self.room.roomId
    
    @property
    def bigRoomId(self):
        return self.room.bigRoomId
    
    @property
    def tableId(self):
        return self._tableId
    
    @property
    def dealer(self):
        return self._dealer
    
    @property
    def seats(self):
        return self._seats
    
    @property
    def seatCount(self):
        return len(self._seats)
    
    @property
    def idleSeatCount(self):
        count = 0
        for seat in self._seats:
            if not seat.player:
                count += 1
        return count
        
    @locked
    def processCommand(self, cmd):
        self._processCommand(cmd)

    def getSeat(self, seatId):
        if seatId > 0 and seatId <= len(self._seats):
            return self._seats[seatId - 1]
        return None
    
    def getSeatByUserId(self, userId):
        for seat in self._seats:
            if seat.userId == userId:
                return seat
        return None

    def getPlayers(self):
        ret = []
        for seat in self._seats:
            if seat.player:
                ret.append(seat.player)
        return ret
    
    def getSeatUserIds(self):
        ret = []
        for seat in self._seats:
            ret.append(seat.userId)
        return ret
    
    def findIdleSeat(self):
        for seat in self._seats:
            if seat.player is None:
                return seat
        return None
    
    def init(self):
        self._makeSeats(self.playMode.seatCount)
        self._initImpl()
        return self
    
    def fire(self, event):
        event.table = self
        super(TableBase, self).fire(event)
        
    def startTimer(self, delay, func, *args, **kw):
        self.cancelTimer()
        self._timer = FTTimer(delay, functools.partial(func, *args, **kw))
    
    def cancelTimer(self):
        if self._timer:
            self._timer.cancel()
            self._timer = None
        
    def _processCommand(self, cmd):
        assert(isinstance(cmd, TableCommand))
        cmd.table = self
        cmd.timestamp = time.time()
        self.state.processCommand(cmd)
        
    def _makeSeats(self, seatCount):
        for i in xrange(seatCount):
            seat = self._newSeat(i, i + 1)
            assert(seat.table == self)
            assert(seat.seatId == i + 1)
            self._seats.append(seat)

    def _newSeat(self, seatIndex, seatId):
        raise NotImplementedError
    
    def _initImpl(self):
        pass

