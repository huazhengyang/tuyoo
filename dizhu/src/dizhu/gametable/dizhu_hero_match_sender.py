# -*- coding:utf-8 -*-
'''
Created on 2015年12月1日

@author: zhaoliang
'''
from dizhu.entity import dizhuconf
from dizhu.gametable.dizhu_sender import DizhuSender
from freetime.util import log as ftlog
from poker.entity.configure import gdata
from poker.entity.dao import sessiondata
from poker.protocol import router
from poker.entity.game.tables.table_player import TYPlayer
import random

class DizhuMillionHeroMatchSender(DizhuSender):
    def __init__(self, table):
        super(DizhuMillionHeroMatchSender, self).__init__(table)
        if not self.table :
            from dizhu.gametable.dizhu_table import DizhuTable
            self.table = DizhuTable()
            
    def sendChuPaiNextRes(self, seatId, opTime):
        super(DizhuMillionHeroMatchSender, self).sendChuPaiNextRes(seatId, opTime)
        # 收到next命令cancel所有的seatOpTimer
        self.table.cancelAllSeatOpTimers()
        # 机器人出牌，延时2秒
        player = self.table.players[seatId - 1]
        if TYPlayer.isRobot(player.userId):
            params = {
                'seatId' : seatId,
                'userId' : player.userId,
                'ccrc' : self.table.status.cardCrc
            }
            self.table.seatOpTimers[seatId - 1].setup(random.randint(2,4), 'AI_OUTCARD_TIMEUP', params)
            
    def sendTableInfoRes(self, userId, clientId, isrobot):
        '''
        给牌桌上的人发送tableInfo
        '''
        if TYPlayer.isRobot(userId):
            return
        
        ftlog.debug('userId', userId, "|clientId", clientId, 'isrobot=', isrobot, caller=self)
        tableInfo = self.table._match_table_info
        if not tableInfo:
            ftlog.error('DizhuArenaSender.sendTableInfoRes NoMatchTableInfo',
                        'userId=', userId,
                        'clientId=', clientId,
                        'isrobot=', isrobot)
            return
        
        player = self.table.getPlayer(userId)
        if not player:
            ftlog.error('DizhuArenaSender.sendTableInfoRes NoPlayer',
                        'userId=', userId,
                        'clientId=', clientId,
                        'isrobot=', isrobot)
            return
        
        baseinfo = self.table.buildBasicInfo(False, userId, clientId)
        mo = self.createMsgPackRes("table_info")
        playMode = self.table.gamePlay.getPlayMode()
        isMatch = self.table.isMatch
        mo.setResult('isrobot', isrobot)
        mo.setResult('playMode', playMode)
        
        roomLevel = gdata.roomIdDefineMap()[self.table.roomId].configure.get('roomLevel', 1)
        mo.setResult('roomLevel', roomLevel)
        roomName = self.table.room.roomConf['name'] if self.table.room else ''
        mo.setResult('roomName', roomName)
        mo.setResult('isMatch', isMatch)
        mo.setResult('notShowRank', 1)
        mo.setResult('info', baseinfo['info'])
        mo.setResult('config', baseinfo['config'])
        mo.setResult('stat', self.buildStatusInfoDict(player))
        mo.setResult('myCardNote', self.buildCardNote(player.seatIndex))
        if self.table.gameRound:
            mo.setResult('roundId', self.table.gameRound.roundId)
            
        if self.table._complain_open:
            clientIdVer = sessiondata.getClientIdVer(userId)
            clientIdLimit = dizhuconf.getAllComplainInfo().get("clientIdLimit", 3.72)
            if clientIdVer >= clientIdLimit:
                mo.setResult('complain', self.table._complain)
        
        for i in xrange(len(self.table.seats)):
            seat = self.table.seats[i]
            oseat = self.buildSeatInfo(player, seat)
            seatuid = seat.userId
            if seatuid :
                seatPlayer = self.table.players[i]
                oseat.update(seatPlayer.datas)
                oseat['cardNote'] = seatPlayer.getCardNoteCount()
                seatPlayer.cleanDataAfterFirstUserInfo()
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

    def sendRobotNotifyCallUp(self, params):
        '''
        召唤机器人
        '''
        ucount, uids = self.table.getSeatUserIds()
        mo = self.createMsgPackRequest("robotmgr")
        if params :
            mo.updateParam(params)
        mo.setAction('callup')
        mo.setParam('userCount', ucount)
        mo.setParam('seatCount', len(uids))
        mo.setParam('users', uids)
        router.sendRobotServer(mo, self.table.tableId)
        
    def sendTuoGuanRes(self, seatId):
        robots = []
        for seat in self.table.seats:
            if TYPlayer.isRobot(seat.userId):
                continue
            
            robots.append(seat.isRobot)
            
        mo = self.createMsgPackRes('table_call', 'rb')
        mo.setResult('robots', robots)
        mo.setResult('seatId', seatId)

        ccount = len(self.table.seats[seatId - 1].cards)
        if ccount > 2:
            mo.setResult('tuoguantip', "我托管，我包赔！有钱就是这么任性！！")
        self.sendToAllTableUser(mo)