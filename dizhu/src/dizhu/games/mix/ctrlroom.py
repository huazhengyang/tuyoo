# -*- coding:utf-8 -*-
'''
Created on 2017年6月13日

@author: wangyonghui
'''
import binascii

from dizhu.entity.dizhuconf import DIZHU_GAMEID
from dizhu.games.normalbase.ctrlroom import DizhuCtrlRoomNormalBase
import freetime.util.log as ftlog
from dizhu.servers.table.rpc import normal_table_room_remote
from poker.protocol import router, runcmd


class DizhuCtrlRoomMix(DizhuCtrlRoomNormalBase):
    def __init__(self, roomDefine):
        super(DizhuCtrlRoomMix, self).__init__(roomDefine)

    def _do_room__quick_start(self, msg):
        '''
        用户快速开始，随机选择一个troom，把用户分发到troom
        '''
        userId = msg.getParam('userId')
        shadowRoomId = msg.getParam('clientRoomId')
        tableId = msg.getParam('tableId')
        continueBuyin = True if msg.getParam('buyin', 0) else False
        mixId = msg.getParam('mixId', '')
        self.quickStart(userId, shadowRoomId, tableId, continueBuyin, mixId)
        if router.isQuery():
            mo = runcmd.newOkMsgPack(1)
            router.responseQurery(mo, '', str(userId))

    def quickStart(self, userId, tableRoomId, tableId, continueBuyin, mixId=''):
        # 排序
        self.shadowRoomIdOccupyList.sort(key=lambda x: (-x[1], x[0]))
        if ftlog.is_debug():
            ftlog.debug('DizhuCtrlRoomMix.quickStart',
                        'roomId=', self.roomId,
                        'userId=', userId,
                        'mixId=', mixId,
                        'tableRoomId=', tableRoomId,
                        'tableId=', tableId,
                        'shadowRoomIdOccupyList=', self.shadowRoomIdOccupyList)
        if not tableRoomId:
            if self.roomConf.get('occupySwitch', 0):
                tableRoomId = self._choiceTableRoomOccupy(userId)
            else:
                tableRoomId = self._choiceTableRoom(userId)
        tableId, seatId = normal_table_room_remote.mixQuickStart(DIZHU_GAMEID, userId, tableRoomId, tableId, continueBuyin, mixId)
        return tableRoomId, tableId, seatId

    def _choiceTableRoom(self, userId):
        useRoomCount = self.roomConf.get('useRoomCount', len(self.roomDefine.shadowRoomIds))
        useRoomCount = min(useRoomCount, len(self.roomDefine.shadowRoomIds))
        if ftlog.is_debug():
            ftlog.debug('DizhuCtrlRoomMix._choiceTableRoom',
                        'roomId=', self.roomId,
                        'userId=', userId,
                        'useRoomCount=', useRoomCount,
                        'shadowRoomCount=', len(self.roomDefine.shadowRoomIds))
        index = binascii.crc32('%s' % (userId)) % useRoomCount
        return self.roomDefine.shadowRoomIds[index]

