# -*- coding:utf-8 -*-
'''
Created on 2017年1月9日

@author: zhaojiangang
'''
import time

from dizhu.entity import dizhuconf
from dizhu.games.custom_match.tableproto import DizhuTableProtoCustomMatch
from dizhu.servers.util.rpc import new_table_remote
from dizhucomm.core.table import DizhuPlayer, DizhuTable
from dizhucomm.table.tablectrl import DizhuTableCtrl
from freetime.core.lock import locked
from freetime.core.tasklet import FTTasklet
import freetime.util.log as ftlog


class DizhuPlayerCustomMatch(DizhuPlayer):
    def __init__(self, room, userId, matchUserInfo):
        super(DizhuPlayerCustomMatch, self).__init__(room, userId)
        self.rank = 0
        self.matchUserInfo = matchUserInfo


class DizhuTableCustomMatch(DizhuTable):
    def __init__(self, room, tableId, playMode):
        super(DizhuTableCustomMatch, self).__init__(room, tableId, playMode, True)
        self._timestamp = 0
        self._matchTableInfo = None
    
    @property
    def matchTableInfo(self):
        return self._matchTableInfo
    
    def _forceClearImpl(self):
        self._timestamp = 0
        self._matchTableInfo = None

    def _quitClear(self, userId):
        self.playMode.removeQuitLoc(self, userId)
    
class DizhuTableCtrlCustomMatch(DizhuTableCtrl):
    def __init__(self, room, tableId, dealer):
        super(DizhuTableCtrlCustomMatch, self).__init__(room, tableId, dealer)

    @locked
    def getSeatByUserId(self, userId):
        for s in self.table.seats:
            if s.userId == userId:
                return s
        return None

    @property
    def matchTableInfo(self):
        return self.table._matchTableInfo
    
    @locked
    def startMatchTable(self, tableInfo):
        if not self._checkMatchTableInfo(tableInfo):
            return False
        self._updateMatchTableInfo(tableInfo)
        self._startMatchTable()
        return True

    @locked
    def updateMatchTableInfo(self, matchTableInfo):
        self._updateMatchTableInfo(matchTableInfo)

    @locked
    def clearMatchTable(self, matchId, ccrc):
        if not self.matchTableInfo:
            ftlog.error('DizhuTableCtrlCustomMatch.doMatchTableClear',
                        'matchId=', matchId,
                        'ccrc=', ccrc,
                        'err=', 'table match is clear')
            return
        
        if matchId != self.matchTableInfo['matchId']:
            ftlog.error('DizhuTableCtrlCustomMatch.doMatchTableClear',
                        'matchIdParam=', matchId,
                        'matchId=', self.matchTableInfo['matchId'],
                        'ccrc=', ccrc,
                        'err=', 'DiffMatchId')
            return
        
        if ccrc != self.matchTableInfo['ccrc']:
            ftlog.error('DizhuTableCtrlCustomMatch.clearMatchTable',
                        'matchId=', matchId,
                        'ccrc=', ccrc,
                        'err=', 'DiffCcrc')
            return
        
        self.table.forceClear()
    
    def _checkSeatInfos(self, seatInfos):
        if not isinstance(seatInfos, list):
            ftlog.error('DizhuTableCtrlCustomMatch._checkSeatInfos',
                        'roomId=', self.roomId,
                        'tableId=', self.tableId, 
                        'err=', 'matchTableInfo.seats must be list')
            return False
        if len(seatInfos) != len(self.table.seats):
            ftlog.error('DizhuTableCtrlCustomMatch._checkSeatInfos',
                        'roomId=', self.roomId,
                        'tableId=', self.tableId,
                        'seatCount', len(self.table.seats), 
                        'seatInfoCount=', len(seatInfos),
                        'err=', 'BadSeatInfoCount')
            return False
        for seatInfo in seatInfos:
            if not isinstance(seatInfo, dict):
                ftlog.error('DizhuTableCtrlCustomMatch._checkSeatInfos',
                            'roomId=', self.roomId,
                            'tableId=', self.tableId,
                            'err=', 'seats.item must be dict')
                return False
            
            userId = seatInfo.get('userId')
            cardCount = seatInfo.get('cardCount')
            if not isinstance(userId, int):
                ftlog.error('DizhuTableCtrlCustomMatch._checkSeatInfos',
                            'roomId=', self.roomId,
                            'tableId=', self.tableId,
                            'err=', 'seats.item.userId must be int')
                return False
            if not isinstance(cardCount, int):
                ftlog.error('DizhuTableCtrlCustomMatch._checkSeatInfos',
                            'roomId=', self.roomId,
                            'tableId=', self.tableId,
                            'err=', 'seats.item.cardCount must be int')
                return False
        return True
    
    def _checkStage(self, stageInfo):
        if not isinstance(stageInfo, dict):
            ftlog.error('DizhuTableCtrlCustomMatch._checkStage',
                        'roomId=', self.roomId,
                        'tableId=', self.tableId, 
                        'err=', 'matchTableInfo.step must be dict')
            return False
        playerCount = stageInfo.get('playerCount')
        riseCount = stageInfo.get('riseCount')
        cardCount = stageInfo.get('cardCount')
        if not isinstance(playerCount, int):
            ftlog.error('DizhuTableCtrlCustomMatch._checkStage',
                        'roomId=', self.roomId,
                        'tableId=', self.tableId, 
                        'err=', 'matchTableInfo.step.playerCount must be int')
            return False
        if not isinstance(riseCount, int):
            ftlog.error('DizhuTableCtrlCustomMatch._checkStage',
                        'roomId=', self.roomId,
                        'tableId=', self.tableId, 
                        'err=', 'matchTableInfo.step.riseCount must be int')
            return False
        if not isinstance(cardCount, int):
            ftlog.error('DizhuTableCtrlCustomMatch._checkStage',
                        'roomId=', self.roomId,
                        'tableId=', self.tableId, 
                        'err=', 'matchTableInfo.step.cardCount must be int')
            return False
        return True
    
    def _getUserIdsFromTableInfo(self, tableInfo):
        userIds = []
        for seatInfo in tableInfo['seats']:
            userIds.append(seatInfo['userId'])
        return userIds
        
    def _checkMatchTableInfo(self, tableInfo):
        if not isinstance(tableInfo, dict):
            ftlog.error('DizhuTableCtrlCustomMatch._checkMatchTableInfo',
                        'roomId=', self.roomId,
                        'tableId=', self.tableId, 
                        'err=', 'matchTableInfo must be dict')
            return False
        roomId = tableInfo.get('roomId')
        tableId = tableInfo.get('tableId')
        if self.roomId != roomId or self.tableId != tableId:
            ftlog.error('DizhuTableCtrlCustomMatch._checkMatchTableInfo',
                        'roomId=', self.roomId,
                        'tableId=', self.tableId, 
                        'roomIdParam=', roomId,
                        'tableIdParam=', tableId,
                        'err=', 'diff roomId or tableId')
            return False
        
        ccrc = tableInfo.get('ccrc')
        if not isinstance(ccrc, int):
            ftlog.error('DizhuTableCtrlCustomMatch._checkMatchTableInfo',
                        'roomId=', self.roomId,
                        'tableId=', self.tableId, 
                        'err=', 'ccrc must be int')
            return False
        
        seatInfos = tableInfo.get('seats')
        if not self._checkSeatInfos(seatInfos):
            return False
    
        stage = tableInfo.get('stage')
        if not self._checkStage(stage):
            return False
        return True

    def _updateMatchTableInfo(self, matchTableInfo):
        self.table._timestamp = time.time()
        self.table._matchTableInfo = matchTableInfo
        self.table.runConf.datas['baseScore'] = matchTableInfo['stage']['baseScore']
    
    def _fillPlayer(self, player):
        '''
        填充player信息
        '''
        datas = new_table_remote.doInitTablePlayerDatas(player.userId, self.roomId)
        player.datas.update(datas)
        player.clientId = datas.get('clientId', '')
        player.name = datas.get('name', '')
        player.chip = datas.get('chip', 0)
        player.gameClientVer = datas.get('gameClientVer', 0)
        return player
    
    def _startMatchTable(self):
        tableInfo = self.table.matchTableInfo
        seatInfos = tableInfo['seats']
        if ftlog.is_debug():
            ftlog.debug('DizhuTableCtrlCustomMatch._startMatchTable',
                        'userIds=', [seatInfo['userId'] for seatInfo in seatInfos],
                        'locker=', self.locker,
                        'tableId=', self.table.tableId,
                        'tableUserIds=', [seat.userId for seat in self.table.seats])
        inter = self._getWaitToNextMatchInter()
        if inter > 0:
            FTTasklet.getCurrentFTTasklet().sleepNb(inter)

        for seatInfo in seatInfos:
            player = DizhuPlayerCustomMatch(self.room, seatInfo['userId'], seatInfo)
            self._fillPlayer(player)
            player.score = seatInfo['score']
            self.table.sitdown(player, False)

        if ftlog.is_debug():
            ftlog.debug('DizhuTableCtrlCustomMatch._startMatchTable',
                        'userIds=', [seatInfo['userId'] for seatInfo in seatInfos],
                        'scores=', [seat.player.score for seat in self.table.seats])
            
        for seat in self.table.seats:
            self.table.ready(seat, False)

    def _getWaitToNextMatchInter(self):
        tableInfo = self.table.matchTableInfo
        isStartStage = tableInfo.get('stage', {}).get('isStartStage', False)
        if isStartStage:
            # 第一个阶段不做延迟
            return 0
        delayConf = dizhuconf.getPublic().get('matchAnimationDelay', '')
        return delayConf.get('waitToNextMatch', 3)

    def _makeTable(self, tableId, dealer):
        return DizhuTableCustomMatch(self.room, tableId, dealer)

    def _makeProto(self):
        return DizhuTableProtoCustomMatch(self)


