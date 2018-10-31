# -*- coding: utf-8 -*-
'''
Created on 2015-5-12
@author: zqh
'''
import random

from dizhu.entity import dizhuconf
from dizhu.gamecards import cardcenter
from freetime.entity.msg import MsgPack
from freetime.util import log as ftlog
from poker.entity.configure import gdata
from poker.entity.dao import userchip, daoconst
from poker.entity.game import rooms
from poker.entity.robot.robotuser import RobotUser, \
    CMD_QUICK_START, CMD_READY, CMD_GAME_READY, CMD_GAME_START, CMD_GAME_WINLOSE


class RobotUser(RobotUser):


    def __init__(self, clientId, snsId, name):
        super(RobotUser, self).__init__(clientId, snsId, name)
        self.rangPaiMode = 0
        self.base_cards = []
        self.seat_cards = []
        self.tableInfoResult = None
        self.card = None

    def _stop(self):
        self.rangPaiMode = 0
        self.base_cards = []
        self.seat_cards = []
        self.tableInfoResult = None
        self.card = None

    def getRoomConfKey(self, key):
        roomConf = gdata.getRoomConfigure(self.roomId)
        return roomConf[key]
    
    def _start(self):
        playMode = self.getRoomConfKey('playMode')
        self.card = cardcenter.getDizhuCard(playMode)
        self.rangPaiMode = 0
        if playMode == dizhuconf.PLAYMODE_ERDOU :
            self.rangPaiMode = 1

    def onMsgTableBegin(self):
        roomTypeName = self.getRoomConfKey('typeName')
        ftlog.debug('RobotUser.onMsgTableBegin roomId=', self.roomId,
                    'roomTypeName=', roomTypeName)
        if roomTypeName in (rooms.tyRoomConst.ROOM_TYPE_NAME_BIG_MATCH,
                            rooms.tyRoomConst.ROOM_TYPE_NAME_ARENA_MATCH,
                            rooms.tyRoomConst.ROOM_TYPE_NAME_GROUP_MATCH,
                            rooms.tyRoomConst.ROOM_TYPE_NAME_ERDAYI_MATCH,
                            'dizhu_group_match',
                            'dizhu_arena_match',
                            'dizhu_erdayi_match'):
            ftlog.debug('send enter and sign in match !!!')
            moEnterMatch = MsgPack()
            moEnterMatch.setCmdAction('room', 'enter')
            moEnterMatch.setParam('userId', self.userId)
            moEnterMatch.setParam('gameId', self.gameId)
            moEnterMatch.setParam('clientId', self.clientId)
            moEnterMatch.setParam('roomId', self.roomId)
            self.writeMsg(moEnterMatch)
            
            moSigninMatch = MsgPack()
            moSigninMatch.setCmdAction('room', 'signin')
            moSigninMatch.setParam('userId', self.userId)
            moSigninMatch.setParam('gameId', self.gameId)
            moSigninMatch.setParam('clientId', self.clientId)
            moSigninMatch.setParam('roomId', self.roomId)
            self.writeMsg(moSigninMatch)
        elif roomTypeName in ('dizhu_custom_match', ):
            moSigninMatch = MsgPack()
            moSigninMatch.setCmdAction('custom_match', 'signin')
            moSigninMatch.setParam('userId', self.userId)
            moSigninMatch.setParam('gameId', self.gameId)
            moSigninMatch.setParam('clientId', self.clientId)
            moSigninMatch.setParam('matchId', self.matchId)
            self.writeMsg(moSigninMatch)
        else :
            self.adjustChip()
            mo = MsgPack()
            mo.setCmdAction('game', 'quick_start')
            mo.setParam('userId', self.userId)
            mo.setParam('gameId', self.gameId)
            mo.setParam('clientId', self.clientId)
            mo.setParam('roomId', self.roomId)
            mo.setParam('tableId', self.tableId)
            ctrlRoomId = gdata.roomIdDefineMap()[self.roomId].parentId or self.roomId
            if gdata.roomIdDefineMap()[ctrlRoomId].configure.get('isMix'):
                mixId = gdata.roomIdDefineMap()[ctrlRoomId].configure.get('mixConf')[0].get('mixId')
                mo.setParam('mixId', mixId)
            ftlog.debug('send quick Start !!!',
                        'userId=', self.userId,
                        'gameId=', self.gameId,
                        'clientId=', self.clientId,
                        'roomId=', self.roomId,
                        'tableId=', self.tableId,
                        'mixId=', mo.getParam('mixId', ''))
            self.writeMsg(mo)
        return


    def onMsgTablePlay(self, msg):
        ftlog.debug('RobotUser.onMsgTablePlay snsId=', self.snsId, 'msg->', msg)
        cmd = msg.getCmd()
        if cmd == 'quick_start' :
            if self.checkState(CMD_QUICK_START) :
                roomId = msg.getResult('roomId')
                tableId = msg.getResult('tableId')
                seatId = msg.getResult('seatId')
                self.seatId = seatId
                if self._isMatch:  # 比赛场机器人初始化时的roomId是bigRoomId，tableId是0，需要重新赋值为shadowRoomId和真实tableId
                    self.roomId = roomId
                    self.tableId = tableId
                if roomId == self.roomId and tableId == self.tableId and seatId > 0 :
                    ftlog.debug('QuickStart', self.snsId, 'OK !', roomId, tableId, seatId)
                else:
                    # 快速开始失败
                    ftlog.warn('QuickStart', self.snsId, msg)
                    self.stop()
        
        action = msg.getResult('action')
        if (cmd == 'table' and action == 'info') or cmd == 'table_info' :
            if self.checkState(CMD_READY) :
                self.tableId = msg.getResult('tableId')
                mo = MsgPack()
                mo.setCmdAction('table_call', 'ready')
                mo.setParam('userId', self.userId)
                mo.setParam('gameId', self.gameId)
                mo.setParam('clientId', self.clientId)
                mo.setParam('roomId', self.roomId)
                mo.setParam('tableId', self.tableId)
                mo.setParam('seatId', self.seatId)
                self.writeMsg(mo)
            self.tableInfoResult = msg.getKey('result')

        if cmd == 'table_call' :
            if action == 'ready' :
                # ready响应不需要返回消息
                pass

            if action == 'game_ready' :
                if self.checkState(CMD_GAME_READY) :
                    # game ready 不需要返回消息
                    self.base_cards = msg.getResult('basecard')
                    self.seat_cards = []
                    i = 0
                    while 1 :
                        seatcard = msg.getResult('cards%d' % (i))
                        if seatcard :
                            self.seat_cards.append(seatcard)
                            i = i + 1
                        else:
                            break
                    pass
                ftlog.debug("game_ready | snsId, seat_cards:", self.snsId, self.seat_cards, caller=self)

            if action == 'game_start' :
                if self.checkState(CMD_GAME_START) :
                    # game start 不需要返回消息
                    # 设置地主的牌为 +底牌
                    dizhu = msg.getResult('stat', {}).get('dizhu', 0)
                    if isinstance(dizhu, int) and dizhu > 0 and dizhu <= len(self.seat_cards) :
                        self.seat_cards[dizhu - 1].extend(self.base_cards)

            if action == 'next' :
                # 更新当前的桌子状态
                if not self.tableInfoResult:
                    # 容错处理 self.tableInfoResult
                    ftlog.debug('RobotUser.onMsgTablePlay',
                                'action[next][update tables status]',
                                'cmd[table_call], tableInfoResult= None',
                                'msg.getKey(result)=', msg.getKey('result'))
                    self.tableInfoResult = msg.getKey('result')
                
                stat = self.tableInfoResult['stat']
                stat['call'] = msg.getResult('stat')['call']
                stat["topseat"] = msg.getResult('stat')['topseat']
                stat["topcard"] = msg.getResult('stat')['topcard']
                stat["ccrc"] = msg.getResult('stat')['ccrc']
                stat["rangpaiMulti"] = msg.getResult('stat')['rangpaiMulti']
                
                if msg.getResult('next') == self.seatId :
                    if self.getState(CMD_GAME_START) == 0 :
                        # 叫地主阶段
                        """
                        # 机器人不叫地主
                        """
                        # mycall = 0
                        # mygrab = 0
                        # if stat['call'] >= 0:
                        #     if self.rangPaiMode:
                        #         mygrab = 1
                        #     else:
                        #         mygrab = 1
                        """
                        # 机器人正常叫地主
                        """
                        mycall = 1
                        mygrab = 0
                        if stat['call'] >= 0 :
                            if self.rangPaiMode :
                                mygrab = 1
                                if stat["rangpaiMulti"] == 2 :
                                    mycall = stat['call'] * 2
                                else:
                                    mycall = stat['call'] + 1
                            else:
                                mygrab = 1
                                if self.tableInfoResult['config'].get('grab', 0) == 1:
                                    mycall = random.randint(0, 1)
                                else:
                                    callValues = [] if self.tableInfoResult.get('playMode') == 'erdayi' else [0]
                                    if stat['call'] < 3:
                                        callValues.extend([i for i in range(max(1, stat['call'] + 1), 3 + 1)])
                                    mycall = random.choice(callValues) if callValues else 0  


                        mo = MsgPack()
                        mo.setCmdAction('table_call', 'call')
                        mo.setParam('userId', self.userId)
                        mo.setParam('gameId', self.gameId)
                        mo.setParam('clientId', self.clientId)
                        mo.setParam('roomId', self.roomId)
                        mo.setParam('tableId', self.tableId)
                        mo.setParam('seatId', self.seatId)
                        mo.setParam('grab', mygrab)
                        mo.setParam('call', mycall)
                        self.writeDelayMsg(self.getResponseDelaySecond(), mo)
                    else :
                        # 出牌阶段
                        mycards = self.seat_cards[self.seatId - 1]
                        topseat, topcard = stat["topseat"], stat["topcard"]
                        if topseat == 0 or topseat == self.seatId:
                            if mycards:
                                cards = self.card.findFirstCards(mycards)
                            else:
                                ftlog.warn('mycards is empty BUG !!', topseat, topcard, self.seatId, mycards)
                                self.stop()
                                return
                        else:
                            cards = self.card.findGreaterCards(topcard, mycards)
                        ftlog.debug('chupai topcard->', topcard, 'mycards->', mycards, 'outcards=', cards)
                        mo = MsgPack()
                        mo.setCmdAction('table_call', 'card')
                        mo.setParam('userId', self.userId)
                        mo.setParam('gameId', self.gameId)
                        mo.setParam('clientId', self.clientId)
                        mo.setParam('roomId', self.roomId)
                        mo.setParam('tableId', self.tableId)
                        mo.setParam('seatId', self.seatId)
                        mo.setParam('cards', cards)
                        mo.setParam('ccrc', stat["ccrc"])
                        self.writeDelayMsg(self.getResponseDelaySecond(), mo)
            
            if action == 'wild_card' :
                wildCardBig = msg.getResult('wildCardBig')
                for cards in self.seat_cards:
                    for j in xrange(len(cards)):
                        if self.card.isSamePointCard(cards[j], wildCardBig):
                            cards[j] = wildCardBig
                for i in xrange(len(self.base_cards)):
                    if self.card.isSamePointCard(self.base_cards[i], wildCardBig):
                        self.base_cards[i] = wildCardBig

            if action == 'card' :
                # 出牌, 同步当前的牌
                cards = msg.getResult('cards')
                if not isinstance(cards, list):
                    cards = []
                seatId = msg.getResult('seatId')
                
                if len(self.seat_cards) >= seatId:
                    seatcards = set(self.seat_cards[seatId - 1]) - set(cards)
                    self.seat_cards[seatId - 1] = list(seatcards)
                    
                ftlog.debug("card | snsId, seatId, seat_cards, out_cards:", self.snsId, seatId, self.seat_cards, cards, caller=self)

            if action == 'game_win' :
                if not self._isMatch:
                    self.stop()
                else:
                    # 为下一局初始化部分状态
                    self.cleanState(CMD_QUICK_START, CMD_READY, CMD_GAME_READY, CMD_GAME_START, CMD_GAME_WINLOSE)
        
        if cmd == 'm_over' :
            self.stop()
            
        return

    def adjustChip(self, minCoin=None, maxCoin=None):
        if not isinstance(minCoin, int) or not isinstance(maxCoin, int) \
                or minCoin < 0 or maxCoin < 0 or minCoin >= maxCoin:
            roomDef = gdata.roomIdDefineMap()[self.roomId]
            roomConf = roomDef.configure
            if roomConf.get('isMix'):
                maxCoin = roomConf.get('mixConf')[0].get('maxCoin', 0)
                minCoin = roomConf.get('mixConf')[0].get('minCoin', 0)
                maxCoin = maxCoin if maxCoin > 0 else minCoin + 100000
            else:
                maxCoin = roomConf['maxCoin']
                minCoin = roomConf['minCoin']
                maxCoin = maxCoin if maxCoin > 0 else minCoin + 100000

        uchip = userchip.getChip(self.userId)
        ftlog.debug('adjustChip->userId, uchip, minCoin, maxCoin =', self.snsId, self.userId, uchip, minCoin, maxCoin)
        if uchip < minCoin or uchip > maxCoin:
            nchip = random.randint(minCoin + 1, minCoin + 1000)
            dchip = nchip - uchip
            trueDelta, finalCount = userchip.incrChip(self.userId, self.gameId, dchip,
                                                      daoconst.CHIP_NOT_ENOUGH_OP_MODE_NONE,
                                                      'SYSTEM_ADJUST_ROBOT_CHIP',
                                                      self.roomId, self.clientId)
            ftlog.debug('adjustChip->userId, trueDelta, finalCount=', self.snsId, self.userId, trueDelta, finalCount)
