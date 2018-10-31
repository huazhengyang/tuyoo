# -*- coding:utf-8 -*-
'''
Created on 2017年1月23日

@author: zhaojiangang
'''
from dizhu.games.friend import dealer
from dizhu.games.friend.state import FriendActions
from dizhu.games.friend.table import DizhuTableCtrlFriend
from dizhu.games.mplayertableroom import DizhuManagerPlayerTableRoom
from dizhu.servers.util.rpc import new_table_remote
from dizhucomm.core.events import SitdownEvent, StandupEvent
from dizhucomm.core.table import DizhuPlayer
from freetime.util import log as ftlog
from poker.entity.game.rooms.room import TYRoom


class DizhuPlayerFriend(DizhuPlayer):
    def __init__(self, room, userId):
        super(DizhuPlayerFriend, self).__init__(room, userId)
        self.idleTime = 0
        self.purl = ''
        self.winCount = 0
        self.segment = 0
        self.currentStar = 0

    def updateDatas(self, datas):
        self._datas = datas
        self.clientId = datas.get('clientId', '')
        self.name = datas.get('name', '')
        self.chip = datas.get('chip', 0)
        self.gameClientVer = datas.get('gameClientVer', 0)

        segment, currentStar = new_table_remote.doGetUserSegment(self.userId)
        self.segment = segment
        self.currentStar = currentStar
        self.updateSegmentDatas()

    def updateSegmentDatas(self):
        self._datas.update({'segment': self.segment, 'currentStar': self.currentStar})

    def initPlayer(self):
        '''
        填充player信息
        '''
        datas = new_table_remote.doInitTablePlayerDatas(self.userId, self.room.roomId)
        self.datas.update(datas)
        self.clientId = datas.get('clientId', '')
        self.name = datas.get('name', '')
        self.purl = datas.get('purl', '')
        self.chip = datas.get('chip', 0)
        self.gameClientVer = datas.get('gameClientVer', 0),
        self.updateDatas(datas)


class DizhuTableRoomFriend(DizhuManagerPlayerTableRoom):
    def __init__(self, roomDefine):
        super(DizhuTableRoomFriend, self).__init__(roomDefine, 10)
        self._dealer = dealer.DIZHU_DEALER_DICT[self.roomConf['playMode']]
        # 状态机加入状态
        states = self._dealer.sm._stateMap
        for state in states.values():
            state._addAction(FriendActions.disBandAction)
        
    def newTable(self, tableId):
        tableCtrl = DizhuTableCtrlFriend(self, tableId, self._dealer)
        tableCtrl.setupTable()
        tableCtrl.table.on(SitdownEvent, self._onSitdownEvent)
        tableCtrl.table.on(StandupEvent, self._onStandupEvent)
        return tableCtrl
    
    def findPlayer(self, userId):
        return self._playerMap.get(userId)
    
    def enterFT(self, tableId, ftId, userId):
        tableCtrl = self.maptable.get(tableId)
        with self._keyLock.lock(userId):
            player = self.findPlayer(userId)
            if player:
                if player.table:
                    player.table.online(player.seat)
                    return 0, ''
            else:
                player = DizhuPlayerFriend(self, userId)
                player.initPlayer()
                self._addPlayer(player)
            return tableCtrl.enterFT(ftId, player)

    def leaveRoom(self, userId, reason):
        '''
        玩家离开房间
        '''
        with self._keyLock.lock(userId):
            player = self.findPlayer(userId)
            if ftlog.is_debug():
                ftlog.debug('DizhuTableRoomFriend.leaveRoom',
                            'roomId=', self.roomId,
                            'userId=', userId,
                            'player=', player,
                            'reason=', reason,
                            'tableId=', player.tableId if player else None,
                            'seatId=', player.seatId if player else None,
                            'tableState=', (player.table.state.name if player.table else None) if player else None)
            ret = True
            if player:
                if reason == TYRoom.LEAVE_ROOM_REASON_LOST_CONNECTION:
                    # 断线不做处理
                    if player.table:
                        player.table.offline(player.seat)
                    return False
                if not player.seat:
                    self._leaveRoom(player, reason)
            return ret
    
    def _onSitdownEvent(self, evt):
        self._removeIdlePlayer(evt.player)

    def _onStandupEvent(self, evt):
        self._addIdlePlayer(evt.player)

