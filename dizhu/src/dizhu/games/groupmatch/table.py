# -*- coding:utf-8 -*-
'''
Created on 2017年1月9日

@author: zhaojiangang
'''
from sre_compile import isstring
import time

from dizhu.entity import dizhuconf
from dizhu.servers.util.rpc import new_table_remote
from dizhucomm.core.table import DizhuPlayer, DizhuTable
from dizhucomm.table.tablectrl import DizhuTableCtrl
from freetime.core.lock import locked
from freetime.core.tasklet import FTTasklet
import freetime.util.log as ftlog
from dizhu.games.groupmatch.tableproto import DizhuTableProtoGroupMatch


class DizhuPlayerGroupMatch(DizhuPlayer):
    def __init__(self, room, userId, matchUserInfo):
        super(DizhuPlayerGroupMatch, self).__init__(room, userId)
        self.rank = 0
        self.record = None
        self.firstCallFalg = 0
        self.matchUserInfo = matchUserInfo
        self.championLimitFlag = False
        # 结算托管数量
        self.winloseForTuoguanCount = 0
        self.hasEnterRewards = False

class DizhuTableGroupMatch(DizhuTable):
    def __init__(self, room, tableId, playMode):
        super(DizhuTableGroupMatch, self).__init__(room, tableId, playMode, True)
        self._timestamp = 0
        self._matchTableInfo = None
    
    @property
    def replayMatchType(self):
        return 1
    
    @property
    def matchTableInfo(self):
        return self._matchTableInfo
    
    def _forceClearImpl(self):
        self._timestamp = 0
        self._matchTableInfo = None

    def _quitClear(self, userId):
        self.playMode.removeQuitLoc(self, userId)
    
class DizhuTableCtrlGroupMatch(DizhuTableCtrl):
    def __init__(self, room, tableId, dealer):
        super(DizhuTableCtrlGroupMatch, self).__init__(room, tableId, dealer)

    @locked
    def getSeatByUserId(self, userId):
        for s in self.table.seats:
            if s.userId == userId:
                return s
        return

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
        if matchId != self.room.bigmatchId:
            ftlog.error('DizhuTableCtrlGroupMatch.clearMatchTable',
                        'matchId=', matchId,
                        'ccrc=', ccrc,
                        'err=', 'DiffMatchId')
            return

        if not self.matchTableInfo:
            ftlog.error('DizhuTableCtrlGroupMatch.doMatchTableClear',
                        'matchId=', matchId,
                        'ccrc=', ccrc,
                        'err=', 'table match is clear')
            return
         
        if ccrc != self.matchTableInfo['ccrc']:
            ftlog.error('DizhuTableCtrlGroupMatch.clearMatchTable',
                        'matchId=', matchId,
                        'ccrc=', ccrc,
                        'err=', 'DiffCcrc')
            return
        
        self.table.forceClear()
    
    def _checkMNotes(self, mnotes):
        if not isinstance(mnotes, dict):
            ftlog.error('DizhuTableCtrlGroupMatch._checkMNotes',
                        'roomId=', self.roomId,
                        'tableId=', self.tableId,
                        'err=', 'matchTableInfo.mnotes must be dict')
            return False
        
        keyTypeList = [('basescore', (str, unicode)),
               ('type', (str, unicode)),
               ('step', (str, unicode)),
               ('isStartStep', (bool)),
               ('isFinalStep', (bool)),
               ('startTime', (str, unicode))]
        for k, t in keyTypeList:
            v = mnotes.get(k, None)
            if not isinstance(v, t):
                ftlog.error('DizhuTableCtrlGroupMatch._checkMNotes',
                            'roomId=', self.roomId,
                            'tableId=', self.tableId,
                            'err=', 'matchTableInfo.%s must be %s' % (k, t))
                return False
        return True
    
    def _checkSeatInfos(self, seatInfos):
        if not isinstance(seatInfos, list):
            ftlog.error('DizhuTableCtrlGroupMatch._checkSeatInfos',
                        'roomId=', self.roomId,
                        'tableId=', self.tableId, 
                        'err=', 'matchTableInfo.seats must be list')
            return False
        if len(seatInfos) != len(self.table.seats):
            ftlog.error('DizhuTableCtrlGroupMatch._checkSeatInfos',
                        'roomId=', self.roomId,
                        'tableId=', self.tableId,
                        'seatCount', len(self.table.seats), 
                        'seatInfoCount=', len(seatInfos),
                        'err=', 'BadSeatInfoCount')
            return False
        for seatInfo in seatInfos:
            if not isinstance(seatInfo, dict):
                ftlog.error('DizhuTableCtrlGroupMatch._checkSeatInfos',
                            'roomId=', self.roomId,
                            'tableId=', self.tableId,
                            'err=', 'seats.item must be dict')
                return False
            
            userId = seatInfo.get('userId')
            cardCount = seatInfo.get('cardCount')
            if not isinstance(userId, int):
                ftlog.error('DizhuTableCtrlGroupMatch._checkSeatInfos',
                            'roomId=', self.roomId,
                            'tableId=', self.tableId,
                            'err=', 'seats.item.userId must be int')
                return False
            if not isinstance(cardCount, int):
                ftlog.error('DizhuTableCtrlGroupMatch._checkSeatInfos',
                            'roomId=', self.roomId,
                            'tableId=', self.tableId,
                            'err=', 'seats.item.cardCount must be int')
                return False
        return True
    
    def _checkMInfos(self, mInfos):
        if not isinstance(mInfos, dict):
            ftlog.error('DizhuTableCtrlGroupMatch._checkMInfos',
                        'roomId=', self.roomId,
                        'tableId=', self.tableId,
                        'err=', 'matchTableInfo.mInfos must be dict')
            return False
        return True
    
    def _checkRanks(self, ranks):
        if not isinstance(ranks, list):
            ftlog.error('DizhuTableCtrlGroupMatch._checkRanks',
                        'roomId=', self.roomId,
                        'tableId=', self.tableId,
                        'err=', 'matchTableInfo.ranks must be list')
            return False
        return True
    
    def _checkStepInfo(self, stepInfo):
        if not isinstance(stepInfo, dict):
            ftlog.error('DizhuTableCtrlGroupMatch._checkStepInfo',
                        'roomId=', self.roomId,
                        'tableId=', self.tableId, 
                        'err=', 'matchTableInfo.step must be dict')
            return False
        name = stepInfo.get('name')
        playerCount = stepInfo.get('playerCount')
        riseCount = stepInfo.get('riseCount')
        cardCount = stepInfo.get('cardCount')
        if not isstring(name):
            ftlog.error('DizhuTableCtrlGroupMatch._checkStepInfo',
                        'roomId=', self.roomId,
                        'tableId=', self.tableId, 
                        'err=', 'matchTableInfo.step.name must be str')
            return False
        if not isinstance(playerCount, int):
            ftlog.error('DizhuTableCtrlGroupMatch._checkStepInfo',
                        'roomId=', self.roomId,
                        'tableId=', self.tableId, 
                        'err=', 'matchTableInfo.step.playerCount must be int')
            return False
        if not isinstance(riseCount, int):
            ftlog.error('DizhuTableCtrlGroupMatch._checkStepInfo',
                        'roomId=', self.roomId,
                        'tableId=', self.tableId, 
                        'err=', 'matchTableInfo.step.riseCount must be int')
            return False
        if not isinstance(cardCount, int):
            ftlog.error('DizhuTableCtrlGroupMatch._checkStepInfo',
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
            ftlog.error('DizhuTableCtrlGroupMatch._checkMatchTableInfo',
                        'roomId=', self.roomId,
                        'tableId=', self.tableId, 
                        'err=', 'matchTableInfo must be dict')
            return False
        roomId = tableInfo.get('roomId')
        tableId = tableInfo.get('tableId')
        matchId = tableInfo.get('matchId')
        if self.roomId != roomId or self.tableId != tableId or self.room.bigmatchId != matchId:
            ftlog.error('DizhuTableCtrlGroupMatch._checkMatchTableInfo',
                        'roomId=', self.roomId,
                        'tableId=', self.tableId, 
                        'roomIdParam=', roomId,
                        'tableIdParam=', tableId,
                        'matchIdParam=', matchId,
                        'err=', 'diff roomId or tableId or bigmatchId')
            return False
        
        ccrc = tableInfo.get('ccrc')
        if not isinstance(ccrc, int):
            ftlog.error('DizhuTableCtrlGroupMatch._checkMatchTableInfo',
                        'roomId=', self.roomId,
                        'tableId=', self.tableId, 
                        'err=', 'ccrc must be int')
            return False
        
        mnotes = tableInfo.get('mnotes')
        if not self._checkMNotes(mnotes):
            return False
        
        seatInfos = tableInfo.get('seats')
        if not self._checkSeatInfos(seatInfos):
            return False
            
        mInfos = tableInfo.get('mInfos')
        if not self._checkMInfos(mInfos):
            return False
    
        ranks = tableInfo.get('ranks')
        if not self._checkRanks(ranks):
            return False
        return True
    
        step = tableInfo.get('step')
        if not self._checkStepInfo(step):
            return False
        return True

    def _updateMatchTableInfo(self, matchTableInfo):
        self.table._timestamp = time.time()
        self.table._matchTableInfo = matchTableInfo
        self.table.runConf.datas['baseScore'] = matchTableInfo['mInfos']['basescore']
    
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
            ftlog.debug('DizhuTableCtrlGroupMatch._startMatchTable',
                        'userIds=', [seatInfo['userId'] for seatInfo in seatInfos],
                        'locker=', self.locker,
                        'tableId=', self.table.tableId,
                        'tableUserIds=', [seat.userId for seat in self.table.seats],
                        'stageRewardTotal=', [seatInfo['stageRewardTotal'] for seatInfo in seatInfos])
        inter = self._getWaitToNextMatchInter()
        if inter > 0:
            FTTasklet.getCurrentFTTasklet().sleepNb(inter)

        for seatInfo in seatInfos:
            player = DizhuPlayerGroupMatch(self.room, seatInfo['userId'], seatInfo)
            player.championLimitFlag = seatInfo['championLimitFlag']
            self._fillPlayer(player)
            player.score = seatInfo['score']
            player.firstCallFalg = seatInfo['firstCallFalg']
            player.isQuit = seatInfo['isQuit']
            player.winloseForTuoguanCount = seatInfo['winloseForTuoguanCount']
            player.hasEnterRewards = seatInfo['hasEnterRewards']
            player.stageRewardTotal = seatInfo['stageRewardTotal']
            self.table.sitdown(player, False)

        if ftlog.is_debug():
            ftlog.debug('DizhuTableCtrlGroupMatch._startMatchTable',
                        'userIds=', [(seatInfo['userId'], seatInfo['winloseForTuoguanCount']) for seatInfo in seatInfos],
                        'scores=', [seat.player.score for seat in self.table.seats])
            
        for seat in self.table.seats:
            self.table.ready(seat, False)

    def _getWaitToNextMatchInter(self):
        mnotes = self.matchTableInfo['mnotes']
        isStartStep = mnotes.get('isStartStep', False)
        if isStartStep:
            # 第一个阶段不做延迟
            return 0
        delayConf = dizhuconf.getPublic().get('matchAnimationDelay', '')
        return delayConf.get('waitToNextMatch', 3)

    def _makeTable(self, tableId, dealer):
        return DizhuTableGroupMatch(self.room, tableId, dealer)

    def _makeProto(self):
        return DizhuTableProtoGroupMatch(self)


