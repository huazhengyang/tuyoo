# -*- coding:utf-8 -*-
'''
Created on 2017年01月19日

@author: luwei
'''
import functools
import time

from dizhu.entity import dizhuconf
from dizhu.games.erdayimatch.aiplayer import AIPlayer
from dizhu.servers.util.rpc import new_table_remote
from dizhucomm.core.events import CurOpSeatMoveEvent, StartNongminJiabeiEvent
from dizhucomm.core.table import DizhuPlayer, DizhuTable
from dizhucomm.entity import skillscore
from dizhucomm.entity.skillscore import UserSkillScore
from dizhucomm.table.tablectrl import DizhuTableCtrl
from freetime.core.lock import locked
from freetime.core.tasklet import FTTasklet
from freetime.core.timer import FTTimer
import freetime.util.log as ftlog
from hall.entity import hallvip
from poker.entity.game.rooms.erdayi_match_ctrl.const import WaitReason
from poker.util import strutil
from dizhu.games.erdayimatch.tableproto import DizhuTableProtoErdayiMatch


class DizhuPlayerErdayiMatch(DizhuPlayer):
    def __init__(self, room, userId, isAI, matchUserInfo):
        super(DizhuPlayerErdayiMatch, self).__init__(room, userId)
        self.matchUserInfo = matchUserInfo
        self.rank = 0
        self.isAI = isAI
        self.waitReason = WaitReason.UNKNOWN
        self.ai = None
        self._timer = None
        if self.isAI:
            self.ai = AIPlayer(self)
    
    def startTimer(self, delay, func, *args, **kw):
        assert(self.isAI)
        self.cancelTimer()
        self._timer = FTTimer(delay, functools.partial(func, *args, **kw))
    
    def cancelTimer(self):
        if self._timer:
            self._timer.cancel()
            self._timer = None
    
    def doActiveOutCard(self):
        assert(self.isAI)
        return self.ai.doActiveOutCard()
        
    def doPassiveOutCard(self):
        assert(self.isAI)
        return self.ai.doPassiveOutCard()
        
class DizhuTableErdayiMatch(DizhuTable):
    def __init__(self, room, tableId, dealer):
        super(DizhuTableErdayiMatch, self).__init__(room, tableId, dealer, True)
        self._timestamp = 0
        self._matchTableInfo = None
    
    @property
    def replayMatchType(self):
        return 1
    
    @property
    def matchTableInfo(self):
        return self._matchTableInfo
    
    def reloadConf(self):
        super(DizhuTableErdayiMatch, self).reloadConf()
        self._runConf.jiabei = 1
    
    def _forceClearImpl(self):
        self._timestamp = 0
        self._matchTableInfo = None

    def _quitClear(self, userId):
        self.playMode.removeQuitLoc(self, userId)


class DizhuTableCtrlErdayiMatch(DizhuTableCtrl):
    MSTART_SLEEP = 3
    AI_USER_IDS = [1, 2]

    def __init__(self, room, tableId, dealer):
        super(DizhuTableCtrlErdayiMatch, self).__init__(room, tableId, dealer)
        self.table.on(CurOpSeatMoveEvent, self._onCurOpSeatMove)
        self.table.on(StartNongminJiabeiEvent, self._onStartNongminJiabei)
        
    @property
    def matchTableInfo(self):
        return self.table.matchTableInfo

    @property
    def isVsAI(self):
        return self.runConf.datas.get('isVsAI', 1)
    
    def canJiabei(self, seat):
        point2score = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 3]
        # 按大牌来吧 计算大牌多就加倍王=3 2=2 A=1 8点及以上加倍
        score = 0
        for card in seat.status.cards:
            point = self.table.playMode.cardRule.cardToPoint(card)
            score += point2score[point]
        return score >= 8

    @locked
    def startMatchTable(self, tableInfo):
        if ftlog.is_debug():
            ftlog.debug('DizhuTableCtrlErdayiMatch.startMatchTable:',
                        'tableInfo=', strutil.dumps(tableInfo))
        self._doClearMatchTable()
        self._updateMatchTableInfo(tableInfo)
        self._startMatchTable()

    @locked
    def clearMatchTable(self, matchId, ccrc):
        if matchId != self.room.bigmatchId:
            ftlog.error('DizhuTableCtrlErdayiMatch.clearMatchTable',
                        'matchId=', matchId,
                        'ccrc=', ccrc,
                        'err=', 'DiffMatchId')
            return

        if not self.matchTableInfo:
            ftlog.error('DizhuTableCtrlErdayiMatch.doMatchTableClear',
                        'matchId=', matchId,
                        'ccrc=', ccrc,
                        'err=', 'table match is clear')
            return
         
        if ccrc != self.matchTableInfo['ccrc']:
            ftlog.error('DizhuTableCtrlErdayiMatch.clearMatchTable',
                        'matchId=', matchId,
                        'ccrc=', ccrc,
                        'err=', 'DiffCcrc')
            return
        
        self._doClearMatchTable()
        
    def _doClearMatchTable(self):
        for seat in self.table.seats:
            if seat.player:
                seat.player.cancelTimer()
        self.table.forceClear()

    def _checkSeatInfo(self, seatInfo):
        if seatInfo['userId'] == 0:
            ftlog.error('DizhuTableCtrlErdayiMatch._checkSeatInfo',
                        'err=', 'userId must not 0')
            return False
        return True

    def _checkMatchTableInfo(self, tableInfo):
        if ftlog.is_debug():
            ftlog.debug('DizhuTableCtrlErdayiMatch._checkMatchTableInfo')
            
        if not isinstance(tableInfo, dict):
            ftlog.error('DizhuTableCtrlErdayiMatch._checkMatchTableInfo',
                        'err=', 'matchTableInfo must be dict')
            return False
        gameId = tableInfo.get('gameId')
        roomId = tableInfo.get('roomId')
        tableId = tableInfo.get('tableId')
        matchId = tableInfo.get('matchId')
        if (self.gameId != gameId
            or self.roomId != roomId
            or self.tableId != tableId
            or self.room.bigmatchId != matchId):
            ftlog.error('DizhuTableCtrlErdayiMatch._checkMatchTableInfo',
                        'gameIdParam=', gameId,
                        'roomIdParam=', roomId,
                        'tableIdParam=', tableId,
                        'matchIdParam=', matchId,
                        'err=', 'diff roomId or tableId or bigmatchId')
            return False
         
        ccrc = tableInfo.get('ccrc')
        if not isinstance(ccrc, int):
            ftlog.error('DizhuTableCtrlErdayiMatch._checkMatchTableInfo',
                        'err=', 'ccrc must be int')
            return False
         
        seatInfos = tableInfo.get('seats')
        if len(seatInfos) != 1:
            ftlog.error('DizhuTableCtrlErdayiMatch._checkMatchTableInfo',
                        'err=', 'len(seatInfos) must == 1')
            return False
        
        for seatInfo in seatInfos:
            if not self._checkSeatInfo(seatInfo):
                return False
            
        return True
              
    def _updateMatchTableInfo(self, matchTableInfo):
        self.table._timestamp = time.time()
        self.table._matchTableInfo = matchTableInfo
        self.table.runConf.datas['baseScore'] = matchTableInfo['step']['basescore']

    def _startMatchTable(self):
        seatInfos = self.matchTableInfo['seats'][:]
        if ftlog.is_debug():
            ftlog.debug('DizhuTableCtrlErdayiMatch._startMatchTable',
                        'tableInfo=', self.matchTableInfo,
                        'userIds=', [seatInfo['userId'] for seatInfo in seatInfos],
                        'tableUserIds=', [seat.userId for seat in self.table.seats])
        
        inter = self._getWaitToNextMatchInter()
        if inter > 0:
            FTTasklet.getCurrentFTTasklet().sleepNb(inter)

        for seatInfo in seatInfos:
            player = DizhuPlayerErdayiMatch(self.room, seatInfo['userId'], False, seatInfo)
            self._fillPlayer(player)
            player.score = seatInfo['score']
            player.rank = seatInfo['rank']
            player.isQuit = seatInfo['isQuit']
            self.table.sitdown(player, False)
            if ftlog.is_debug():
                ftlog.debug('DizhuTableCtrlErdayiMatch._startMatchTable',
                            'userId=', player.userId,
                            'score=', player.score,
                            'rank=', player.rank,
                            'seatInfos=', self.matchTableInfo)
        
        for userId in self.AI_USER_IDS:
            seatInfo = {
                'userId':userId,
                'name':'机器人',
                'rank':0,
                'score':0,
                'clientId':'robot_3.7_-hall6-robot',
                'ddzVer':0,
                'cardCount':seatInfos[0].get('cardCard', 0)
            }
            player = DizhuPlayerErdayiMatch(self.room, userId, True, seatInfo)
            self._fillPlayer(player)
            player.score = 0
            self.table.sitdown(player, False)
            
        for seat in self.table.seats:
            self.table.ready(seat, False)

    def _fillPlayer(self, player):
        '''
        填充player信息
        '''
        if not player.isAI:
            datas = new_table_remote.doInitTablePlayerDatas(player.userId, self.roomId)
        else:
            datas = {
                'uid':player.userId,
                'clientId':player.matchUserInfo.get('clientId'),
                'address':'',
                'sex':0,
                'name':player.matchUserInfo.get('name'),
                'coin':0,
                'headUrl':'',
                'purl':'', # TODO
                'isBeauty':False,
                'chip':0,
                'gold':0,
                'vipzuan':[],
                'tbc':0,
                'tbt':0,
                'level':0,
                'wins':0,
                'plays':0,
                'winchips':0,
                'nextexp':0,
                'title':'',
                'medals':[],
                'skillScoreInfo':self.getDefaultSkillScoreInfo(player.userId),
                'charm':0,
                'vipInfo':self.getDefaultVipInfo(0),
                'startid':0,
                'winstreak':0,
                'gameClientVer':0,
                'wearedItems':[],
                'memberExpires':0
            }
        player.datas.update(datas)
        player.clientId = datas.get('clientId', '')
        player.name = datas.get('name', '')
        player.chip = datas.get('chip', 0)
        player.gameClientVer = datas.get('gameClientVer', 0)
        return player
    
    def getDefaultSkillScoreInfo(self, userId):
        level = skillscore.getLevel(self.gameId, 0)
        uss = UserSkillScore(userId, 0, level)
        return skillscore.buildUserSkillScoreInfo(uss)
    
    def getDefaultVipInfo(self, vipExp):
        vipLevel = hallvip.vipSystem.findVipLevelByVipExp(vipExp)
        return {
            'level':vipLevel.level,
            'name':vipLevel.name,
            'exp':0,
            'expCurrent':vipLevel.vipExp,
            'expNext':vipLevel.nextVipLevel.vipExp if vipLevel.nextVipLevel else vipLevel.vipExp
        }
        
    def _getWaitToNextMatchInter(self):
        if self.matchTableInfo['step']['stageIndex'] == 0:
            # 第一个阶段不做延迟
            return 0
        delayConf = dizhuconf.getPublic().get('matchAnimationDelay', {})
        return delayConf.get('waitToNextMatch', 3)
    
    def _onStartNongminJiabei(self, event):
        if ftlog.is_debug():
            ftlog.debug('DizhuTableProto._onStartNongminJiabei',
                        'tableId=', event.table.tableId)
        for seat in event.table.gameRound.seats:
            if seat.player.isAI:
                jiebei = 1 if self.canJiabei(seat) else 0
                seat.player.startTimer(2, self.jiabei, seat.userId, seat.seatId, jiebei)
    
    def _onCurOpSeatMove(self, event):
        if ftlog.is_debug():
            ftlog.debug('DizhuTableCtrlErdayiMatch._onCurOpSeatMove',
                        'tableId=', event.table.tableId,
                        'prevOpSeat=', (event.prevOpSeat.userId, event.prevOpSeat.seatId) if event.prevOpSeat else None,
                        'curOpSeat=', (event.curOpSeat.userId, event.curOpSeat.seatId),
                        'optime=', event.optime,
                        'autoOp=', event.autoOp,
                        'dizhuSeat=', (event.table.gameRound.curOpSeat.userId, event.table.gameRound.curOpSeat.seatId))
        if (event.table.gameRound.dizhuSeat
            and event.curOpSeat.player.isAI
            and not event.autoOp):
            cards = self._aiOutCards(event.curOpSeat)
            event.curOpSeat.player.startTimer(2, self.outCard, event.curOpSeat.userId, event.curOpSeat.seatId, cards, event.table.gameRound.cardCrc)
    
    def _aiOutCards(self, seat):
        if ftlog.is_debug():
            ftlog.debug('DizhuTableCtrlErdayiMatch._aiOutCards',
                        'tableId=', self.tableId,
                        'seat=', (seat.userId, seat.seatId))
        if (seat.table.gameRound.topSeat == None or seat.table.gameRound.topSeat == seat):
            cards = seat.player.doActiveOutCard()
        else:
            cards = seat.player.doPassiveOutCard()

        if ftlog.is_debug():
            ftlog.debug('DizhuTableCtrlErdayiMatch._aiOutCards',
                        'tableId=', self.tableId,
                        'seat=', (seat.userId, seat.seatId),
                        'cards=', cards)
        
        return cards if cards is not None else []

    def _makeTable(self, tableId, dealer):
        return DizhuTableErdayiMatch(self.room, tableId, dealer)
        
    def _makeProto(self):
        return DizhuTableProtoErdayiMatch(self)


