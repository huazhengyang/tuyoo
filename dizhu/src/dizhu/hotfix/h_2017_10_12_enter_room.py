# -*- coding:utf-8 -*-
'''
Created on 2017年10月12日

@author: wangyonghui
'''
from dizhu.games.normalbase.tableroom import DizhuTableRoomNormalBase
import freetime.util.log as ftlog


def enterRoom(self, userId, continueBuyin):
    '''
    用户进入房间，带入，取用户信息等
    '''
    with self._keyLock.lock(userId):
        exists = self.findPlayer(userId)
        if exists:
            exists.continueBuyin = True
            ftlog.info('DizhuTableRoomNormalBase.enterRoom',
                       'userId=', userId,
                       'clientId=', exists.clientId,
                       'dizhuVersion=', exists.gameClientVer,
                       'idlePlayerCount=', len(self._idlePlayerMap),
                       'playerCount=', len(self._playerMap),
                       'tableCount=', len(self._tableList),
                       'continueBuyin=', True,
                       'roomId=', self.roomId)
            return exists

        player = self._makePlayer(userId)
        player.initPlayer()

        # 检查准入
        self._enterRoomCheck(player, continueBuyin)

        self.ensureNotInSeat(userId)

        self._addPlayer(player)
        ftlog.info('DizhuTableRoomNormalBase.enterRoom',
                   'userId=', userId,
                   'clientId=', player.clientId,
                   'dizhuVersion=', player.gameClientVer,
                   'idlePlayerCount=', len(self._idlePlayerMap),
                   'playerCount=', len(self._playerMap),
                   'tableCount=', len(self._tableList),
                   'continueBuyin=', continueBuyin,
                   'roomId=', self.roomId)
        return player

DizhuTableRoomNormalBase.enterRoom = enterRoom
