# -*- coding:utf-8 -*-
'''
Created on 2016年12月21日

@author: zhaojiangang
'''
from dizhucomm.room.events import RoomConfReloadEvent
from dizhucomm.utils.obser import Observable
from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from poker.entity.game.game import GAME_STATUS_RUN
from poker.protocol import router


class DizhuRoom(Observable):
    def __init__(self, roomDefine):
        # 房间配置
        self._roomDefine = roomDefine
        self.runStatus = GAME_STATUS_RUN
    
    @property
    def gameId(self):
        return self.roomDefine.gameId
    
    @property
    def roomId(self):
        return self.roomDefine.roomId
  
    @property
    def bigRoomId(self):
        return self.roomDefine.bigRoomId
    
    @property
    def roomDefine(self):
        return self._roomDefine
    
    @property
    def roomConf(self):
        return self.roomDefine.configure
    
    @property
    def tableConf(self):
        return self.roomConf['tableConf']
    
    @property
    def isMatch(self):
        return self.roomConf.get('ismatch', 0)
    
    @property
    def matchId(self):
        # TODO 返回当前房间的比赛ID, 若为非比赛房间,返回0
        return 0
    
    @property
    def matchConf(self):
        return self.roomConf.get('matchConf')
    
    @property
    def ctrlRoomId(self):
        return self.roomDefine.parentId or self.roomId
    
    def getRoomOnlineInfo(self):
        return 0, 0, 0

    def getRoomOnlineInfoDetail(self):
        return 0, 0, {}

    def getRobotUserCount(self):
        return 0
    
    def doCheckUserLoc(self, userId, gameId, roomId, tableId, clientId):
        return -1, 0
    
    def doReloadConf(self, roomDefine):
        if ftlog.is_debug():
            ftlog.debug('DizhuRoom.doReloadConf',
                        'roomId=', self.roomId,
                        'roomDefine.configure=', roomDefine.configure)
        self._roomDefine = roomDefine
        self._onConfReload()
        self.fire(RoomConfReloadEvent(self))
            
    def sendQuickStartRes(self, gameId, userId, reason, roomId=0, tableId=0, info=""):
        mp = MsgPack()
        mp.setCmd('quick_start')
        mp.setResult('info', info)
        mp.setResult('userId', userId)
        mp.setResult('gameId', gameId)
        mp.setResult('roomId', roomId)
        mp.setResult('tableId', tableId)
        mp.setResult('seatId', 0) # 兼容检查seatId参数的地主客户端
        mp.setResult('reason', reason)
        router.sendToUser(mp, userId)
        
    def _onConfReload(self):
        pass

    def doShutDown(self):
        pass
    

