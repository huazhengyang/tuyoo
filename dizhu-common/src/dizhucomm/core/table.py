# -*- coding:utf-8 -*-
'''
Created on 2017年2月7日

@author: zhaojiangang
'''
from sre_compile import isstring

from dizhucomm.core.base import PlayerBase, SeatBase, TableBase
from dizhucomm.core.commands import SitdownCommand, StandupCommand, ReadyCommand, \
    CallCommand, OutCardCommand, TuoguanCommand, JiabeiCommand, ShowCardCommand, \
    HuanpaiOutcardsCommand, AutoPlayCommand
from dizhucomm.core.const import StandupReason
from dizhucomm.core.tableconf import DizhuTableConf
from freetime.core.lock import locked
import freetime.util.log as ftlog
from poker.entity.game.tables.table_player import ROBOT_USER_ID_MAX
from poker.util import strutil


class DizhuPlayer(PlayerBase):
    def __init__(self, room, userId):
        super(DizhuPlayer, self).__init__(room, userId)
        # 是否退出
        self.isQuit = 0
        # 用户昵称
        self.name = ''
        # 当前积分
        self.score = 0
        # 当前金币
        self.chip = 0
        # 客户端版本号
        self.gameClientVer = 0
        # 客户端clientId
        self.clientId = ''
        # 在线状态
        self.online = True
        # 牌局记牌器
        self.inningCardNote = 0
        # 用户数据
        self._datas = {}
        # callOper
        self.callOper = None
        # 结算托管标志
        self.winloseForTuoguan = False
        # 累计阶段奖励
        self.stageRewardTotal = 0

    @property
    def datas(self):
        return self._datas
    
    def updateDatas(self, datas):
        self._datas = datas
        self.clientId = datas.get('clientId', '')
        self.name = datas.get('name', '')
        self.chip = datas.get('chip', 0)
        self.gameClientVer = datas.get('gameClientVer', 0)
        
    @property
    def isRobotUser(self):
        if self.userId > 0 and self.userId <= ROBOT_USER_ID_MAX :
            return True
        if (self.userId > ROBOT_USER_ID_MAX
            and isstring(self.clientId)
            and self.clientId.find('robot') >= 0):
            return True
        return False
    
    def isMember(self, timestamp):
        return timestamp < self.datas.get('memberExpires', 0)
    
    def cleanDataAfterFirstUserInfo(self):
        '''
        桌面带入的提示, 只需要显示一次, 发送第一次table_info后, 就删除提示信息
        '''
        if 'buyinTip' in self.datas:
            self.datas['buyinTip'] = ''
    
    def openCardNote(self):
        if self.getCardNoteCount() <= 0:
            self.inningCardNote = 1
            return True
        return False
    
    def getCardNoteCount(self):
        if self.inningCardNote > 0:
            return 1
        return self.cardNoteCount
    
    @property
    def cardNoteCount(self):
        return self._datas.get('cardNotCount', 0)

    def adjustCharm(self, incCharm):
        if 'charm' in self._datas:
            charm = self._datas['charm']
            charm = charm + incCharm
            charm = 0 if charm < 0 else charm
            self._datas['charm'] = charm
            
    def getData(self, key, defVal):
        return self._datas.get(key, defVal)
    
class DizhuSeat(SeatBase):
    ST_IDLE = 0
    ST_WAIT = 10
    ST_READY = 20
    ST_PLAYING = 30
    
    def __init__(self, table, seatIndex, seatId):
        super(DizhuSeat, self).__init__(table, seatIndex, seatId)
        # 状态
        self._state = self.ST_IDLE
        # 牌局状态信息
        self._status = None
        # 是否支持语音
        self.isReciveVoice = False
        # 结算界面，点击继续的带入标记，用于带入提示
        self.isNextBuyin = False
        # 最后扔表情时间
        self.throwEmojiTime = 0
        
    @property
    def state(self):
        return self._state
            
    @property
    def status(self):
        return self._status
    
    @property
    def isGiveup(self):
        return self._status and self._status.giveup

class DizhuTable(TableBase):
    def __init__(self, room, tableId, dealer, keepPlayersWhenGameOver):
        super(DizhuTable, self).__init__(room, tableId, dealer)
        # 桌子配置
        self._runConf = None
        # 牌局信息(gameReady后才会创建)
        self._gameRound = None
        # bool值 是否直到游戏结束后才清理players
        self._keepPlayersWhenGameOver = keepPlayersWhenGameOver
        # 加载桌子配置
        self.reloadConf()
    
    @property
    def runConf(self):
        return self._runConf
    
    @property
    def gameRound(self):
        return self._gameRound
    
    @property
    def keepPlayersWhenGameOver(self):
        return self._keepPlayersWhenGameOver
    
    @property
    def replayMatchType(self):
        return 0

    @locked
    def forceClear(self):
        self.cancelTimer()

        gameRound, self._gameRound = self._gameRound, None
        for seat in self.seats:
            seat.cancelTimer()
            seat._status = None
            seat._state = DizhuSeat.ST_WAIT if seat.player else DizhuSeat.ST_IDLE

        usersForQuit = []
        for _, seat in enumerate(self.seats):
            if seat.player:
                isQuit = seat.player.isQuit
                userId = seat.player.userId
                self.playMode.standup(self, seat, StandupReason.FORCE_CLEAR)
                if isQuit:
                    usersForQuit.append(userId)
                    self._quitClear(userId)
        self._forceClearImpl()
        self._state = self.dealer.sm.findStateByName('idle')
        
        ftlog.info('DizhuTable.forceClear',
                   'usersForQuit=', usersForQuit,
                   'tableId=', self.tableId,
                   'roundId=', gameRound.roundId if gameRound else None)

    @locked
    def quit(self, seat):
        '''
        牌桌退出
        '''
        self.playMode.quit(self, seat)

    @locked
    def online(self, seat):
        '''
        用户上线
        '''
        self.playMode.seatOnlineChanged(self, seat, True)
    
    @locked
    def offline(self, seat):
        '''
        用户下线
        '''
        self.playMode.seatOnlineChanged(self, seat, False)
    
    @locked
    def sitdown(self, player, isNextBuyin):
        '''
        用户坐下
        '''
        self._processCommand(SitdownCommand(player, None, isNextBuyin))
        return player.seat is not None
    
    @locked
    def standup(self, seat, reason=StandupReason.USER_CLICK_BUTTON):
        '''
        用户站起
        '''
        assert(seat.table == self)
        if not seat.player:
            return True
        if self.gameRound:
            ftlog.warn('DizhuTable.standup',
                       'tableId=', self.tableId,
                       'userId=', seat.userId,
                       'reason=', reason,
                       'err=', 'InPlaying')
            return False
        self._processCommand(StandupCommand(seat, reason))
        return True
        
    @locked
    def chat(self, seat, isFace, msg, voiceIndex):
        '''
        用户聊天(语音/文字/表情)
        '''
        assert(seat.table == self)
        self.playMode.chat(self, seat, isFace, msg, voiceIndex)
    
    @locked
    def ready(self, seat, isReciveVoice):
        '''
        座位ready
        '''
        assert(seat.table == self)
        self._processCommand(ReadyCommand(seat, isReciveVoice))
    
    @locked
    def call(self, seat, callValue):
        assert(seat.table == self)
        self._processCommand(CallCommand(seat, callValue))
    
    @locked
    def outCard(self, seat, validCards, cardCrc):
        assert(seat.table == self)
        self._processCommand(OutCardCommand(seat, validCards, cardCrc))
    
    @locked
    def tuoguan(self, seat):
        assert(seat.table == self)
        self._processCommand(TuoguanCommand(seat))

    @locked
    def autoplay(self, seat, isAutoPlay):
        assert (seat.table == self)
        self._processCommand(AutoPlayCommand(seat, isAutoPlay))
    
    @locked
    def jiabei(self, seat, multi):
        assert(seat.table == self)
        self._processCommand(JiabeiCommand(seat, multi))
        
    @locked
    def showCard(self, seat):
        assert(seat.table == self)
        self._processCommand(ShowCardCommand(seat))
        
    @locked
    def huanpaiOutCards(self, seat, outCards):
        assert(seat.table == self)
        self._processCommand(HuanpaiOutcardsCommand(seat, outCards))
        
    def reloadConf(self):
        runconf = strutil.cloneData(self.room.roomConf)
        runconf.update(strutil.cloneData(self.room.tableConf))
        self._runConf = DizhuTableConf(runconf)
    
    def _newSeat(self, seatIndex, seatId):
        return DizhuSeat(self, seatIndex, seatId)
    
    def _forceClearImpl(self):
        pass

    def _quitClear(self, userId):
        pass


