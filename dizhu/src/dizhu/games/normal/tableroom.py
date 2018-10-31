# -*- coding:utf-8 -*-
'''
Created on 2017年2月13日

@author: zhaojiangang
'''
from dizhu.games.normal.table import DizhuTableCtrlNormal
from dizhu.games.normalbase.tableroom import DizhuPlayerNormalBase, \
    DizhuTableRoomNormalBase
from dizhu.servers.util.rpc import new_table_remote
from dizhucomm.core.exceptions import ChipNotEnoughException
import freetime.util.log as ftlog


class DizhuPlayerNormal(DizhuPlayerNormalBase):
    def __init__(self, room, userId):
        super(DizhuPlayerNormal, self).__init__(room, userId)
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

    def isFirstLose(self, isWin):
        if isWin:
            return False
        if self._datas['registerDays'] < 3:
            wins = self._datas.get('winrate2', {}).get('wt', 0)
            plays = self._datas.get('winrate2', {}).get('pt', 0)
            return wins == plays

    def isFirstWin(self, isWin):
        if not isWin:
            return False
        import poker.util.timestamp as pktimestamp
        today = pktimestamp.formatTimeDayInt()
        isFirstWin = self._datas.get('firstWin', {}).get(str(today), 0)
        if not isFirstWin:
            return True
        return False

    
class DizhuTableRoomNormal(DizhuTableRoomNormalBase):
    def __init__(self, roomDefine):
        super(DizhuTableRoomNormal, self).__init__(roomDefine)
        
    def _enterRoomCheck(self, player, continueBuyin):
        '''
        检查用户是否可以进入该房间
        '''

        # 兼容老版本
        gameClientVer = player.gameClientVer
        if continueBuyin and gameClientVer < 3.818:
            if ftlog.is_debug():
                ftlog.debug('DizhuTableRoomNormal._enterRoomCheck',
                            'userId=', player.userId,
                            'roomId=', self.roomId,
                            'continueBuyin=', continueBuyin,
                            'gameClientVer=', gameClientVer)

            kickOutCoin = self.roomConf.get('kickOutCoin', 0)
            if player.chip < kickOutCoin:
                raise ChipNotEnoughException()
            return

        # 检查location
        roomMinCoin = self.roomConf.get('minCoin', 0)
        if player.chip < roomMinCoin:
            raise ChipNotEnoughException()
        
    def _makeTableCtrl(self, tableId, dealer):
        return DizhuTableCtrlNormal(self, tableId, dealer)
    
    def _makePlayer(self, userId):
        return DizhuPlayerNormal(self, userId)


