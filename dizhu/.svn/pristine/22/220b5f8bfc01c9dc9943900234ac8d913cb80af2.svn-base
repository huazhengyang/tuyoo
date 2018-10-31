# -*- coding:utf-8 -*-
'''
Created on 2017年3月2日

@author: zhaojiangang
'''
from dizhu.games.events import UserEnterRoomEvent, UserLeaveRoomEvent
from dizhucomm.room.tableroom import DizhuTableRoom
from dizhucomm.utils.orderdedict import LastUpdatedOrderedDict
from freetime.core.timer import FTLoopTimer
from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from poker.entity.biz import bireport
from poker.entity.game.rooms.room import TYRoom
from poker.protocol import router
from poker.util.keylock import KeyLock
import poker.util.timestamp as pktimestamp


class DizhuManagerPlayerTableRoom(DizhuTableRoom):
    def __init__(self, roomDefine, clearIdleInterval=10):
        super(DizhuManagerPlayerTableRoom, self).__init__(roomDefine)
        # 玩家map
        self._playerMap = {}
        # 空闲的玩家Map
        self._idlePlayerMap = LastUpdatedOrderedDict()
        # 定时器清理超时的player
        self._clearIdlePlayerTimer = FTLoopTimer(clearIdleInterval, -1, self._clearIdlePlayes)
        self._clearIdlePlayerTimer.start()
        self._keyLock = KeyLock()
    
    @property
    def keyLock(self):
        return self._keyLock
    
    def _addPlayer(self, player):
        self._playerMap[player.userId] = player
        self._addIdlePlayer(player)
        self.fire(UserEnterRoomEvent(self, player))
        
    def _addIdlePlayer(self, player):
        player.idleTime = pktimestamp.getCurrentTimestamp()
        self._idlePlayerMap[player.userId] = player
        
    def _removeIdlePlayer(self, player):
        try:
            del self._idlePlayerMap[player.userId]
        except:
            pass
        
    def _leaveRoom(self, player, reason):
        assert (not player.seat)
        if player.isAI:
            return
        self._removeIdlePlayer(player)
        try:
            del self._playerMap[player.userId]
            self.fire(UserLeaveRoomEvent(self, player, reason))
            # ftlog.info('DizhuManagerPlayerTableRoom._leaveRoom',
            #            'roomId=', self.roomId,
            #            'userId=', player.userId,
            #            'reason=', reason)

            clientId = player.clientId
            bireport.reportGameEvent('LEAVE_ROOM',
                                     player.userId,
                                     self.gameId,
                                     self.roomId,
                                     0,
                                     0,
                                     0, reason, 0, [],
                                     clientId,
                                     0, 0)
        except Exception, e:
            ftlog.error('room_leave BI error',
                        'gameId=', self.gameId,
                        'roomId=', self.roomId,
                        'userId=', player.userId,
                        'err=', e.message)


    def _clearIdlePlayes(self):
        if ftlog.is_debug():
            ftlog.debug('DizhuManagerPlayerTableRoom._clearIdlePlayes',
                        'roomId=', self.roomId,
                        'idlePlayerCount=', len(self._idlePlayerMap))
        userIds = []
        curTime = pktimestamp.getCurrentTimestamp()
        idleTime = self.roomConf.get('playerIdleTime', 300)
        for player in self._idlePlayerMap.values():
            if curTime - player.idleTime >= idleTime:
                userIds.append(player.userId)
        
        kickPlayers = []
        for userId in userIds:
            with self._keyLock.lock(userId):
                player = self._idlePlayerMap.get(userId)
                if player and curTime - player.idleTime >= idleTime:
                    self._leaveRoom(player, TYRoom.LEAVE_ROOM_REASON_TIMEOUT)
                    kickPlayers.append(player)
                    mp = MsgPack()
                    mp.setCmd('room_leave')
                    # 此处由于客户端只有在LEAVE_ROOM_REASON_ACTIVE的情况下才会退出结算界面
                    mp.setResult('reason', TYRoom.LEAVE_ROOM_REASON_ACTIVE)
                    mp.setResult('gameId', self.gameId)
                    mp.setResult('roomId', self.roomId)  # 处理结果返回给客户端时，部分游戏（例如德州、三顺）需要判断返回的roomId是否与本地一致
                    mp.setResult('userId', player.userId)
                    router.sendToUser(mp, player.userId)

        if ftlog.is_debug():
            ftlog.debug('DizhuManagerPlayerTableRoom._clearIdlePlayes',
                        'roomId=', self.roomId,
                        'idlePlayerCount=', len(self._idlePlayerMap),
                        'userIds=', userIds,
                        'clears=', [p.userId for p in kickPlayers])


