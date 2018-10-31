# -*- coding:utf-8 -*-
'''
Created on 2017年2月13日

@author: zhaojiangang
'''
from dizhu.replay import replay_service
from dizhucomm.core.exceptions import BadSeatException
from dizhucomm.core.table import DizhuTable
from dizhucomm.table.tablectrl import DizhuTableCtrl
from poker.entity.game.rooms.room import TYRoom
from freetime.core.timer import FTLoopTimer
from freetime.util import log as ftlog


class DizhuTableNormalBase(DizhuTable):
    def __init__(self, room, tableId, dealer):
        super(DizhuTableNormalBase, self).__init__(room, tableId, dealer, False)
        self._score = 0
        self.processing = False
        self.winStreakSection = None
        self.chipSection = None
        self.mixIdSection = None
        
    @property
    def score(self):
        return self._score
    
    def __lt__(self, other):
        return self._score < other._score

    def _quitClear(self, userId):
        self.playMode.removeQuitLoc(self, userId)
        ftlog.info('DizhuTableNormalBase._quitClear',
                   'roomId=', self.roomId,
                   'tableId=', self.tableId,
                   'userId=', userId)
        FTLoopTimer(0, 0, self.room.leaveRoom, userId, TYRoom.LEAVE_ROOM_REASON_SYSTEM).start()
    
class DizhuTableCtrlNormalBase(DizhuTableCtrl):
    def __init__(self, room, tableId, dealer):
        super(DizhuTableCtrlNormalBase, self).__init__(room, tableId, dealer)
        
    def saveReplay(self, userId, roundId):
        gameRoundInfo = self._replay.findGameRoundInfo(roundId)
        if gameRoundInfo and gameRoundInfo[0].findSeatByUserId(userId):
            if not gameRoundInfo[0].gameOverTimestamp:
                raise BadSeatException('牌局还没结束')
            if userId in gameRoundInfo[1]:
                raise BadSeatException('牌局已经保存')

            if not gameRoundInfo[0].winloseDetail:
                raise BadSeatException('牌局已流局')

            replay_service.saveVideo(userId, gameRoundInfo[0])
            gameRoundInfo[1].add(userId)
        else:
            raise BadSeatException('没有找到该牌局')

    def leaveTable(self, userId, reason):
        with self.room.keyLock.lock(userId):
            seat = self.table.getSeatByUserId(userId)
            if seat:
                if not seat.table.standup(seat):
                    return False
            return True

    def _makeProto(self):
        raise NotImplementedError
