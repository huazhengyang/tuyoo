# -*- coding:utf-8 -*-
'''
Created on 2015年12月1日

@author: zhaojiangang
'''
from dizhu.entity import dizhuconf
from dizhu.gametable.dizhu_sender import DizhuSender
from poker.entity.configure import gdata
from poker.entity.dao import sessiondata
from dizhu.entity.matchrecord import MatchRecord
from poker.entity.game.rooms.group_match_ctrl.utils import Logger
from poker.protocol import router
from poker.util import strutil


class DizhuGroupMatchSender(DizhuSender):
    def __init__(self, table):
        super(DizhuGroupMatchSender, self).__init__(table)
        if not self.table :
            from dizhu.gametable.dizhu_table import DizhuTable
            self.table = DizhuTable()
        self._logger = Logger()
        self._logger.add('roomId', self.table.roomId)
        self._logger.add('tableId', self.table.tableId)
        
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
            oseat = seat.toInfoDict()
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
        mo.setResult('mnotes', tableInfo['mnotes'])
        mo.setResult('mInfos', tableInfo['mInfos'])
        mo.setResult('step', {
                        'name':tableInfo['step']['name'],
                        'des':'%s人参赛，%s人晋级' % (tableInfo['step']['playerCount'],
                                               tableInfo['step']['riseCount']),
                        'playerCount':tableInfo['step']['playerCount'],
                        'note':self.table._buildNote(userId, tableInfo)
                    })
        
    def getMatchUserInfo(self, userId, tableInfo, oseat):
        oseat['mscore'] = 0
        oseat['mrank'] = 0
        try:
            for userInfo in tableInfo['seats']:
                if userInfo['userId'] == userId:
                    oseat['mscore'] = userInfo['score']
                    oseat['mrank'] = userInfo['rank']
                    
                    record = MatchRecord.loadRecord(self.table.gameId, userId, tableInfo.get('recordId', tableInfo['matchId']))
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
        

