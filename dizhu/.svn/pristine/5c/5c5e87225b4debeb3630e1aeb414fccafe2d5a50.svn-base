# -*- coding:utf-8 -*-
'''
Created on 2016年7月19日

@author: zhaojiangang
'''
from dizhu.entity import dizhuconf
from dizhu.entity.matchrecord import MatchRecord
from dizhu.gametable.dizhu_sender import DizhuSender
from dizhu.gametable.dizhu_state import DizhuState
from poker.entity.configure import gdata
from poker.entity.dao import sessiondata
from poker.entity.game.rooms.erdayi_match_ctrl.utils import Logger
from poker.protocol import router
from poker.util import strutil


class DizhuErdayiMatchSender(DizhuSender):
    def __init__(self, table):
        super(DizhuErdayiMatchSender, self).__init__(table)
        assert(table)
        
        self._logger = Logger()
        self._logger.add('roomId', self.table.roomId)
        self._logger.add('tableId', self.table.tableId)
        
    def sendJiabeiRes(self, seatId, jiabei):
        mo = self.createMsgPackRes('table_call', 'jiabei')
        mo.setResult('jiabei', jiabei)
        mo.setResult('seatId', seatId)
        mo.setResult('userId', self.table.seats[seatId-1].userId)
        self.sendToAllTableUser(mo)
        
    def sendWaitJiabei(self, optime):
        if self.table.status.state == DizhuState.TABLE_STATE_NM_DOUBLE:
            mo = self.createMsgPackRes('table_call', 'wait_nm_jiabei')
        else:
            mo = self.createMsgPackRes('table_call', 'wait_dz_jiabei')
        mo.setResult('optime', optime)
        self.sendToAllTableUser(mo)
    
    def sendToAllTableUser(self, mo):
        for p in self.table.players :
            if not p.isAI:
                router.sendToUser(mo, p.userId)
            
    def sendChuPaiNextRes(self, seatId, opTime):
        if self._logger.isDebug():
            self._logger.debug('DizhuGroupMatchSender.sendChuPaiNextRes',
                               'seatId=', seatId,
                               'opTime=', opTime)
        mo = self.createMsgPackRes('table_call', 'next')
        mo.setResult('next', seatId)
        mo.setResult('seatId', seatId)
        mo.setResult('stat', self.table.status.toInfoDict())
        mo.setResult('opTime', opTime)
        self.sendToAllTableUser(mo)
        
        # 收到next命令cancel所有的seatOpTimer
        self.table.cancelAllSeatOpTimers()

        # 机器人出牌，延时2秒
        player = self.table.players[seatId - 1]
        if player.isAI:
            params = {
                'seatId' : seatId,
                'userId' : player.userId,
                'ccrc' : self.table.status.cardCrc
            }
            self.table.seatOpTimers[seatId - 1].setup(2, 'AI_OUTCARD_TIMEUP', params)
        
    def sendTableInfoRes(self, userId, clientId, isrobot):
        if self._logger.isDebug():
            self._logger.debug('DizhuGroupMatchSender.sendTableInfoRes',
                               'userId=', userId,
                               'clientId=', clientId,
                               'isrobot=', isrobot)
        tableInfo = self.table._match_table_info
        if not tableInfo:
            self._logger.error('DizhuGroupMatchSender.sendTableInfoRes NoMatchTableInfo',
                               'userId=', userId,
                               'clientId=', clientId,
                               'isrobot=', isrobot)
            return
        
        player = self.table.getPlayer(userId)
        
        if not player:
            self._logger.error('DizhuGroupMatchSender.sendTableInfoRes NoPlayer',
                               'userId=', userId,
                               'clientId=', clientId,
                               'isrobot=', isrobot)
            return
        
        baseinfo = self.table.buildBasicInfo(False, userId, clientId)
        _, clientVer, _ = strutil.parseClientId(clientId)
        mo = self.createMsgPackRes('table_info')
        playMode = self.table.gamePlay.getPlayMode()
        if clientVer <= 3.7:
            if playMode == dizhuconf.PLAYMODE_HAPPY or playMode == dizhuconf.PLAYMODE_123 :
                playMode = 'normal'  # FIX, 客户端happy和123都是normal, grab=1就是欢乐
        isMatch = self.table.isMatch
        mo.setResult('isrobot', isrobot)
        mo.setResult('playMode', playMode)
         
        roomLevel = gdata.roomIdDefineMap()[self.table.roomId].configure.get('roomLevel', 1)
        mo.setResult('roomLevel', roomLevel)
        roomName = self.table.room.roomConf['name'] if self.table.room else ''
        mo.setResult('roomName', roomName)
        mo.setResult('isMatch', isMatch)
        mo.setResult('info', baseinfo['info'])
        mo.setResult('config', baseinfo['config'])
        mo.setResult('stat', self.buildStatusInfoDict(player))
        mo.setResult('myCardNote', self.buildCardNote(player.seatIndex))
        if self.table.gameRound:
            mo.setResult('roundId', self.table.gameRound.roundId)
            
        if self.table._complain_open:
            clientIdVer = sessiondata.getClientIdVer(userId)
            clientIdLimit = dizhuconf.getAllComplainInfo().get('clientIdLimit', 3.72)
            if clientIdVer >= clientIdLimit:
                mo.setResult('complain', self.table._complain)
         
        if self._logger.isDebug():
            self._logger.debug('DizhuGroupMatchSender.sendTableInfoRes before getMatchTableInfo',
                               'mo=', mo)
        self.getMatchTableInfo(userId, tableInfo, mo)
        if self._logger.isDebug():
            self._logger.debug('DizhuGroupMatchSender.sendTableInfoRes after getMatchTableInfo',
                               'mo=', mo)
         
        for i in xrange(len(self.table.seats)):
            seat = self.table.seats[i]
            oseat = self.buildSeatInfo(player, seat)
            seatuid = seat.userId
            if seatuid :
                seatPlayer = self.table.players[i]
                oseat.update(seatPlayer.datas)
                oseat['cardNote'] = seatPlayer.getCardNoteCount()
                seatPlayer.cleanDataAfterFirstUserInfo()
                self.getMatchUserInfo(seatPlayer.userId, tableInfo, oseat)
            else:
                oseat['uid'] = 0
            mo.setResult('seat' + str(i + 1), oseat)
 
        tmpobsr = []
        for _, obuser in self.table.observers.items() :
            if obuser :
                tmpobsr.append((obuser.userId, obuser.name))
        mo.setResult('obsr', tmpobsr)
         
        mo.setResult('betpoolClose', 1)
 
        if player and player.getCardNoteCount() < 1:
            tableConf = self.table.room.roomConf.get('tableConf') if self.table.room else None
            cardNoteChip = tableConf.get('cardNoteChip', 0)
            cardNoteDiamod = tableConf.get('cardNoteDiamond', 0)
            cardNote = dizhuconf.getCardNoteTips(userId, player.datas.get('chip', 0),
                                                 clientId, cardNoteChip, cardNoteDiamod)
            if cardNote:
                mo.setResult('cardNote', cardNote)
 
        # 发送消息至客户端
        router.sendToUser(mo, userId)
 
    def getMatchTableInfo(self, userId, tableInfo, mo):
        mo.setResult('step', {
                        'name':tableInfo['step']['name'],
                        'des':'%s人参赛，%s人晋级' % (tableInfo['step']['playerCount'], tableInfo['step']['riseCount']),
                        'playerCount':tableInfo['step']['playerCount'],
                        'note':self.table._buildNote(userId, tableInfo),
                        'basescore':tableInfo['step']['basescore']
                    })
         
    def getMatchUserInfo(self, userId, tableInfo, oseat):
        from dizhu.erdayimatch.match import ErdayiMatch
        oseat['mscore'] = 0
        oseat['mrank'] = 0
        try:
            for userInfo in tableInfo['seats']:
                if userInfo['userId'] == userId:
                    oseat['mscore'] = ErdayiMatch.fmtScore(userInfo['score'])
                    oseat['mrank'] = userInfo['rank']
                     
                    matchId = tableInfo.get('recordId', tableInfo['matchId'])
                    record = MatchRecord.loadRecord(self.table.gameId, userId, matchId)
                    if record:
                        oseat['mrecord'] = {
                            'bestRank':record.bestRank,
                            'crownCount':record.crownCount,
                            'playCount':record.playCount
                        }
        except:
            self._logger.error('DizhuGroupMatchSender.getMatchUserInfo',
                               'userId=', userId,
                               'tableInfo=', tableInfo,
                               'oseat=', oseat)


