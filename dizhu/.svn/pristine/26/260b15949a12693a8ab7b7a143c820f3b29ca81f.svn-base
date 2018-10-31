# -*- coding:utf-8 -*-
'''
Created on 2017年1月9日

@author: zhaojiangang
'''
from dizhu.games.arenamatch.tableproto import DizhuTableProtoArenaMatch
from dizhu.servers.util.rpc import new_table_remote
from dizhucomm.core.table import DizhuPlayer, DizhuTable, DizhuSeat
from dizhucomm.table.tablectrl import DizhuTableCtrl
from freetime.core.lock import locked
import freetime.util.log as ftlog


class DizhuPlayerArenaMatch(DizhuPlayer):
    def __init__(self, room, userId, matchUserInfo):
        super(DizhuPlayerArenaMatch, self).__init__(room, userId)
        self.matchUserInfo = matchUserInfo
        self.rank = 0
        self.record = None
        self.mixId = None

class DizhuTableAreanMatch(DizhuTable):
    def __init__(self, room, tableId, dealer):
        super(DizhuTableAreanMatch, self).__init__(room, tableId, dealer, True)
        self._matchTableInfo = None
    
    @property
    def replayMatchType(self):
        return 1
    
    @property
    def matchTableInfo(self):
        return self._matchTableInfo
    
    def _forceClearImpl(self):
        self._matchTableInfo = None

    def _quitClear(self, userId):
        self.playMode.removeQuitLoc(self, userId)

class DizhuTableCtrlArenaMatch(DizhuTableCtrl):
    def __init__(self, room, tableId, dealer):
        super(DizhuTableCtrlArenaMatch, self).__init__(room, tableId, dealer)

    @property
    def matchTableInfo(self):
        return self.table.matchTableInfo
    
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
        if matchId != self.room.bigmatchId:
            ftlog.error('DizhuTableCtrlGroupMatch.clearMatchTable',
                        'matchId=', matchId,
                        'tableId=', self.tableId,
                        'ccrc=', ccrc,
                        'err=', 'DiffMatchId')
            return

        if not self.matchTableInfo:
            ftlog.error('DizhuTableCtrlGroupMatch.doMatchTableClear',
                        'matchId=', matchId,
                        'tableId=', self.tableId,
                        'ccrc=', ccrc,
                        'err=', 'table match is clear')
            return
         
        if ccrc != self.matchTableInfo['ccrc']:
            ftlog.error('DizhuTableCtrlGroupMatch.clearMatchTable',
                        'matchId=', matchId,
                        'tableId=', self.tableId,
                        'ccrc=', ccrc,
                        'err=', 'DiffCcrc')
            return
        
        self.table.forceClear()
    
    def _updateMatchTableInfo(self, matchTableInfo):
        self.table._matchTableInfo = matchTableInfo
        self.table.runConf.datas['baseScore'] = matchTableInfo['baseScore']
    
    def _checkMatchTableInfo(self, matchTableInfo):
        return True
    
    def _startMatchTable(self):
        userInfos = self.matchTableInfo['userInfos']
        for userInfo in userInfos:
            player = DizhuPlayerArenaMatch(self.table.room, userInfo['userId'], userInfo)
            self._fillPlayer(player)
            player.score = userInfo['score']
            player.rank = userInfo['rank']
            player.isQuit = userInfo['isQuit']
            player.mixId = userInfo['mixId']
            player.winloseForTuoguan = userInfo['winloseForTuoguan']
            player.stageRewardTotal = userInfo['stageRewardTotal']

            segment, currentStar = self._getUserSegmentInfo(player.userId)
            player.currentStar = currentStar
            player.segment = segment
            player._datas.update({'segment': segment, 'currentStar': currentStar})
            self.table.sitdown(player, False)
    
        # 准备ready
        for seat in self.table.seats:
            if seat.player and seat.state != DizhuSeat.ST_READY:
                self.table.ready(seat, False)

    def _getUserSegmentInfo(self, userId):
        segment, currentStar = new_table_remote.doGetUserSegment(userId)
        return segment, currentStar
    
    def _fillPlayer(self, player):
        datas = new_table_remote.doInitTablePlayerDatas(player.userId, self.roomId)
        player.datas.update(datas)
        player.clientId = datas.get('clientId', '')
        player.name = datas.get('name', '')
        player.chip = datas.get('chip', 0)
        player.gameClientVer = datas.get('gameClientVer', 0)
        return player

    def _makeTable(self, tableId, dealer):
        return DizhuTableAreanMatch(self.room, tableId, dealer)

    def _makeProto(self):
        return DizhuTableProtoArenaMatch(self)


