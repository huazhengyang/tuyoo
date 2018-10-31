# -*- coding:utf-8 -*-
'''
Created on 2017年2月13日

@author: zhaojiangang
'''

import binascii

from dizhu.entity.dizhuconf import DIZHU_GAMEID
from dizhu.servers.table.rpc import normal_table_room_remote
from dizhucomm.room.base import DizhuRoom
from dizhucomm.utils.msghandler import MsgHandler
from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from poker.entity.configure import gdata
from poker.entity.game.rooms.room import TYRoom
from poker.entity.game.tables.table_player import TYPlayer
from poker.protocol import router, runcmd


class DizhuCtrlRoomNormalBase(DizhuRoom, MsgHandler):
    def __init__(self, roomDefine):
        super(DizhuCtrlRoomNormalBase, self).__init__(roomDefine)
        self.shadowRoomIdOccupyList = [[shadowRoomId, 0] for shadowRoomId in self.roomDefine.shadowRoomIds]
        self.shadowRoomIdOccupyList.sort(key=lambda x: x[0])
        if ftlog.is_debug():
            ftlog.debug('DizhuCtrlRoomNormalBase.__init__',
                        'shadowRoomIdOccupyList=', self.shadowRoomIdOccupyList)

    def _do_room__quick_start(self, msg):
        '''
        用户快速开始，随机选择一个troom，把用户分发到troom
        '''
        userId = msg.getParam('userId')
        shadowRoomId = msg.getParam('clientRoomId')
        tableId = msg.getParam('tableId')
        continueBuyin = True if msg.getParam('buyin', 0) else False
        self.quickStart(userId, shadowRoomId, tableId, continueBuyin)
        if router.isQuery():
            mo = runcmd.newOkMsgPack(1)
            router.responseQurery(mo, '', str(userId))

    def _do_room__leave(self, msg):
        userId = msg.getParam('userId')
        reason = msg.getParam('reason', TYRoom.LEAVE_ROOM_REASON_ACTIVE)
        needSendRes = msg.getParam('needSendRes', True)
        clientRoomId = msg.getParam('clientRoomId', self.roomId)

        # 兼容老客户端
        bigRoomId = gdata.getBigRoomId(clientRoomId)
        if clientRoomId == bigRoomId:
            clientRoomId = self._choiceTableRoom(userId)

        if not self.leaveRoom(userId, clientRoomId, reason):
            reason = TYRoom.LEAVE_ROOM_REASON_FORBIT
        mp = MsgPack()
        mp.setCmd('room_leave')
        mp.setResult('reason', reason)
        mp.setResult('gameId', self.gameId)
        mp.setResult('roomId', clientRoomId)  # 处理结果返回给客户端时，部分游戏（例如德州、三顺）需要判断返回的roomId是否与本地一致
        mp.setResult('userId', userId)
        
        if needSendRes or TYPlayer.isRobot(userId):# 需要通知机器人stop
            router.sendToUser(mp, userId)

    def leaveRoom(self, userId, shadowRoomId, reason):
        if ftlog.is_debug():
            ftlog.debug('DizhuCtrlRoomNormalBase.leaveRoom',
                        'roomId=', self.roomId,
                        'shadowRoomId=', shadowRoomId,
                        'userId=', userId,
                        'reason=', reason)
        if shadowRoomId:
            return normal_table_room_remote.leaveRoom(DIZHU_GAMEID, userId, shadowRoomId, reason)
        return False
        
    def quickStart(self, userId, tableRoomId, tableId, continueBuyin):
        # 排序
        self.shadowRoomIdOccupyList.sort(key=lambda x: (-x[1], x[0]))
        if ftlog.is_debug():
            ftlog.debug('DizhuCtrlRoomNormalBase.quickStart',
                        'roomId=', self.roomId,
                        'userId=', userId,
                        'tableRoomId=', tableRoomId,
                        'tableId=', tableId,
                        'shadowRoomIdOccupyList=', self.shadowRoomIdOccupyList)
        if not tableRoomId:
            if self.roomConf.get('occupySwitch', 0):
                tableRoomId = self._choiceTableRoomOccupy(userId)
            else:
                tableRoomId = self._choiceTableRoom(userId)
        tableId, seatId = normal_table_room_remote.quickStart(DIZHU_GAMEID, userId, tableRoomId, tableId, continueBuyin)
        return tableRoomId, tableId, seatId
    
    def _choiceTableRoom(self, userId):
        useRoomCount = self.roomConf.get('useRoomCount', len(self.roomDefine.shadowRoomIds))
        useRoomCount = min(useRoomCount, len(self.roomDefine.shadowRoomIds))
        if ftlog.is_debug():
            ftlog.debug('DizhuCtrlRoomNormalBase._choiceTableRoom',
                        'roomId=', self.roomId,
                        'userId=', userId,
                        'useRoomCount=', useRoomCount,
                        'shadowRoomCount=', len(self.roomDefine.shadowRoomIds))
        index = binascii.crc32('%s' % (userId)) % useRoomCount
        return self.roomDefine.shadowRoomIds[index]

    def _choiceTableRoomOccupy(self, userId):
        choiceShadowRoomId = self.shadowRoomIdOccupyList[-1][0]
        for index, shadowRoomOccupy in enumerate(self.shadowRoomIdOccupyList):
            if shadowRoomOccupy[1] >= self.roomConf.get("occupyMax", 1):
                continue
            choiceShadowRoomId = self.shadowRoomIdOccupyList[index][0]
            break

        if ftlog.is_debug():
            ftlog.debug('DizhuCtrlRoomNormalBase._choiceTableRoomOccupy',
                        'roomId=', self.roomId,
                        'userId=', userId,
                        'choiceShadowRoomId=', choiceShadowRoomId,
                        'shadowRoomIdOccupyList=', self.shadowRoomIdOccupyList)
        return choiceShadowRoomId

    def roomUserOccupy(self, shadowRoomId, roomOccupy):
        for shadowRoomOccupy in self.shadowRoomIdOccupyList:
            if shadowRoomOccupy[0] == int(shadowRoomId):
                shadowRoomOccupy[1] = roomOccupy
        if ftlog.is_debug():
            ftlog.debug('DizhuCtrlRoomNormalBase.roomUserOccupy',
                        'roomId=', self.roomId,
                        'shadowRoomId=', shadowRoomId,
                        'roomOccupy=', roomOccupy,
                        'shadowRoomIdOccupyList=', self.shadowRoomIdOccupyList)
        return True

