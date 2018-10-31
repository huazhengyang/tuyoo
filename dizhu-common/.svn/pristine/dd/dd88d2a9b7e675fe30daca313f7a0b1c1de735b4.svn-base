# -*- coding:utf-8 -*-
'''
Created on 2017年2月10日

@author: zhaojiangang
'''
from dizhucomm.core.events import CardNoteOpenedEvent, ThrowEmojiEvent
from dizhucomm.core.exceptions import BadSeatException, BadPlayerException, \
    BadCardException, BadStateException, NotSupportedException, \
    ChipNotEnoughException, BadCardCrcException
from dizhucomm.servers.util.rpc import comm_table_remote
from dizhucomm.table.bireport import BIReportTable
from dizhucomm.table.remotelistener import TableRemoteListener
from dizhucomm.table.replay import ReplayTable
from freetime.core.lock import locked
import freetime.util.log as ftlog
from hall.entity import hallstore
from hall.entity.hallitem import ASSET_DIAMOND_KIND_ID, ITEM_CARD_NOTE_KIND_ID
from hall.entity.hallpopwnd import findTodotaskTemplate
from hall.entity.todotask import TodoTaskHelper, TodoTaskPopTip, TodoTaskOrderShow, TodoTaskShowInfo
from hall.servers.util.rpc import user_remote
from poker.entity.biz.exceptions import TYBizException
from poker.entity.dao import sessiondata
from poker.protocol import router
from poker.util import timestamp as pktimestamp, strutil
from dizhucomm.entity import emoji


class DizhuTableCtrl(object):
    def __init__(self, room, tableId, dealer):
        self._room = room
        # 桌子
        self._table = self._makeTable(tableId, dealer)
        self._table.init()
        # 牌局记录
        self._replay = ReplayTable(self)
        # bi汇报
        self._bireport = BIReportTable(self)
        # 
        self._remoteListener = TableRemoteListener(self)
        # 协议
        self._proto = self._makeProto()
        
    @property
    def locker(self):
        return self._table.locker

    @property
    def gameId(self):
        return self.room.gameId

    @property
    def room(self):
        return self._room
    
    @property
    def roomId(self):
        return self.room.roomId
    
    @property
    def bigRoomId(self):
        return self.room.bigRoomId
    
    @property
    def table(self):
        return self._table
    
    @property
    def tableId(self):
        return self.table.tableId
    
    @property
    def isMatch(self):
        return False
    
    @property
    def replay(self):
        return self._replay

    @property
    def proto(self):
        return self._proto

    @locked
    def quit(self, userId, seatId):
        seat = self.checkSeatAndPlayer(seatId, userId)
        self.table.quit(seat)

    @locked
    def userOnline(self, userId):
        seat = self.table.getSeatByUserId(userId)
        if seat:
            self.table.online(seat)
    
    @locked
    def throwEmoji(self, userId, seatId, toSeatId, emojiId, count=1):
        seatFrom = self.checkSeatAndPlayer(seatId, userId)
        seatTo = self.checkSeat(toSeatId)
        try:
            self._throwEmoji(seatFrom, seatTo, emojiId, count)
        except ChipNotEnoughException:
            TodoTaskHelper.sendTodoTask(self.table.gameId, userId, TodoTaskPopTip('背包剩余金币不足无法使用互动表情'))
        except TYBizException, e:
            self.proto.sendSmilesResError(userId, e.message)
    
    @locked
    def chat(self, userId, seatId, isFace, msg, voiceIdx):
        seat = self.checkSeatAndPlayer(seatId, userId)
        self.table.chat(seat, isFace, msg, voiceIdx)
    
    @locked
    def ready(self, userId, seatId, isReciveVoice):
        seat = self.checkSeatAndPlayer(seatId, userId)
        try:
            self.table.ready(seat, isReciveVoice)
        except BadStateException:
            ftlog.warn('DizhuTableCtrl.ready',
                       'userId=', userId,
                       'tableId=', self.tableId,
                       'seatId=', seatId,
                       'isReciveVoice=', isReciveVoice,
                       'seatState=', seat.state,
                       'err=', 'AlreadyReady')
        
    @locked
    def call(self, userId, seatId, callValue):
        seat = self.checkSeatAndPlayer(seatId, userId)
        self.table.call(seat, callValue)
    
    @locked
    def outCard(self, userId, seatId, cards, ccrc):
        seat = self.checkSeatAndPlayer(seatId, userId)
        try:
            if cards:
                validCards = self.table.playMode.cardRule.validateCards(cards)
                if not validCards:
                    raise BadCardException()
            else:
                validCards = None
            self.table.outCard(seat, validCards, ccrc)
        except (BadCardException, BadCardCrcException), e:
            ftlog.warn('DizhuTableCtrl.outCard',
                       'tableId=', self.tableId,
                       'seat=', (userId, seatId),
                       'cards=', cards,
                       'ccrc=', ccrc,
                       'exc=', e)
            self.proto.sendTableInfoRes(seat)

    @locked
    def tuoguan(self, userId, seatId):
        seat = self.checkSeatAndPlayer(seatId, userId)
        self.table.tuoguan(seat)

    @locked
    def autoplay(self, userId, seatId, isAutoPlay):
        seat = self.checkSeatAndPlayer(seatId, userId)
        self.table.autoplay(seat, isAutoPlay)

    @locked
    def showCard(self, userId, seatId):
        seat = self.checkSeatAndPlayer(seatId, userId)
        self.table.showCard(seat)

    @locked
    def openCardNote(self, userId, seatId):
        seat = self.checkSeatAndPlayer(seatId, userId)
        self._openCardNote(seat)

    @locked
    def jiabei(self, userId, seatId, jiabei):
        seat = self.checkSeatAndPlayer(seatId, userId)
        self.table.jiabei(seat, 2 if jiabei else 1)

    @locked
    def huanpaiOutCards(self, userId, seatId, cards):
        seat = self.checkSeatAndPlayer(seatId, userId)
        self.table.huanpaiOutCards(seat, cards)
    
    def checkSeat(self, seatId):
        seat = self.table.getSeat(seatId)
        if not seat:
            raise BadSeatException()
        return seat
    
    def checkSeatAndPlayer(self, seatId, userId):
        seat = self.checkSeat(seatId)
        if seat.userId != userId:
            raise BadPlayerException()
        return seat
    
    def _getEmojiConf(self, seat, emojiId):
        vipLevel = seat.player.datas.get('vipInfo', {}).get('level', 0)
        emojiConf = emoji.getEmojiConf(self.gameId, self.bigRoomId, vipLevel)
        if not emojiConf:
            return None, None, None, None, None
        conf = emojiConf.get(emojiId, None)
        if not conf:
            return None, None, None, None, None
        return conf['price'], int(conf['self_charm']), int(conf['other_charm']), conf['cd'], conf.get('bursts')

    def _throwEmoji(self, seatFrom, seatTo, emojiId, count):
        if not seatTo.player:
            return

        coolTimeExpires = pktimestamp.getCurrentTimestamp() >= seatFrom.throwEmojiTime
        price, selfCharm, otherCharm, cdTime, bursts = self._getEmojiConf(seatFrom, emojiId)
        _, _, otherCharmTo, _, _ = self._getEmojiConf(seatTo, emojiId)
        if price == None:
            raise NotSupportedException('该房间不支持互动表情')

        if ftlog.is_debug():
            ftlog.debug('DizhuTableCtrl._throwEmoji seatFrom.userId=', seatFrom.userId,
                        'seatTo.userId=', seatTo.userId,
                        'price, selfCharm, otherCharm, cdTime, bursts=', price, selfCharm, otherCharm, cdTime, bursts)

        if bursts and bursts.get('cost') and count > 1:
            # 小游戏连发表情需要单独处理
            realCount = comm_table_remote.doTableThrowEmojiFromBursts(self.gameId, seatFrom.userId, self.roomId, self.tableId, emojiId, selfCharm, bursts)
            if realCount == 0 and not coolTimeExpires:
                raise BadStateException('互动表情冷却时间未到')
            if realCount == 0:
                seatFrom.throwEmojiTime = pktimestamp.getCurrentTimestamp() + cdTime

            if realCount != 0:
                seatFrom.player.adjustCharm(selfCharm)
                comm_table_remote.doTableThrowEmojiTo(self.gameId, seatTo.userId, otherCharmTo, realCount)
                seatTo.player.adjustCharm(otherCharmTo)
            else:
                selfCharm = 0
                otherCharmTo = 0
            self.table.fire(ThrowEmojiEvent(self.table, seatFrom, seatTo,
                                            emojiId, realCount, realCount,
                                            0, selfCharm, otherCharmTo, cdTime))
            return


        realCount, trueDelta, final = \
            comm_table_remote.doTableThrowEmojiFrom_3_775(self.gameId,
                                                          seatFrom.userId,
                                                          self.roomId,
                                                          self.bigRoomId,
                                                          self.tableId,
                                                          emojiId,
                                                          0,
                                                          price,
                                                          selfCharm,
                                                          seatFrom.player.clientId,
                                                          count,
                                                          coolTimeExpires)
        # 用户没有金币
        if realCount == 0 and not coolTimeExpires:
            raise BadStateException('互动表情冷却时间未到')
        if trueDelta == 0:
            seatFrom.throwEmojiTime = pktimestamp.getCurrentTimestamp() + cdTime
        
        seatFrom.player.datas['chip'] = final
        if trueDelta != 0:
            seatFrom.player.adjustCharm(selfCharm)
            comm_table_remote.doTableThrowEmojiTo(self.gameId, seatTo.userId, otherCharmTo, realCount)
            seatTo.player.adjustCharm(otherCharmTo)
        else:
            selfCharm = 0
            otherCharmTo = 0
        self.table.fire(ThrowEmojiEvent(self.table, seatFrom, seatTo,
                                        emojiId, realCount, trueDelta,
                                        final, selfCharm, otherCharmTo, cdTime))

    def _openCardNote(self, seat):
        # 比赛场局记牌器在下发此消息时扣除背包金币，非比赛场局记牌器在结算时扣除带入金币
        #self.isMatch or self.table.runConf.cardNoteChipConsumeUserChip:
        if seat.player.getCardNoteCount() <= 0:
            try:
                if self.table.runConf.cardNoteDiamond == 0:
                    trueDelta, _final = user_remote.incrUserChip(seat.userId,
                                                                 self.table.gameId,
                                                                 -self.table.runConf.cardNoteChip,
                                                                 'MATCH_CARDNOTE_BETCHIP',
                                                                 0,
                                                                 seat.player.clientId)
                    if trueDelta != -self.table.runConf.cardNoteChip:
                        if ftlog.is_debug():
                            ftlog.warn('DizhuTableCtrl._openCardNote',
                                       'tableId=', self.tableId,
                                       'userId=', seat.userId,
                                       'cardNoteCount=', seat.player.getCardNoteCount(),
                                       'chip=', seat.player.datas.get('chip'),
                                       'err=', 'ChipNotEnough')
                        return
                else:
                    # 钻石购买 10钻石 = 1日记牌器
                    # 兼容pc端
                    clientOs, clientVer, _ = strutil.parseClientId(seat.player.clientId)
                    clientOs = clientOs.lower()
                    if clientOs == 'winpc':
                        self._sendTodoTaskToUser(seat.player.userId)
                        return

                    userId = seat.player.userId
                    clientId = sessiondata.getClientId(userId)
                    # 大厅版本4.56以上直接弹出贵族月卡购买弹窗 # 弹出月卡购买todotask
                    if clientVer > 4.56:
                        template, templateName = findTodotaskTemplate(self.gameId, userId, clientId, 'monthlyBuy')
                        todoTaskObj = template.newTodoTask(self.gameId, userId, clientId) if template else None
                        if ftlog.is_debug():
                            ftlog.debug('match_remote.findTodotaskTemplate.monthlyBuy', 'userId=', userId, 'template=',
                                        template, 'templateName=', templateName, 'templateDict=',
                                        todoTaskObj.toDict() if todoTaskObj else None)
                        if todoTaskObj:
                            TodoTaskHelper.sendTodoTask(self.gameId, userId, todoTaskObj)
                            return

                    consumeCount, final = user_remote.consumeAsset(self.gameId,
                                                                   seat.player.userId,
                                                                   ASSET_DIAMOND_KIND_ID,
                                                                   self.table.runConf.cardNoteDiamond,
                                                                   'MATCH_CARDNOTE_BETDIAMOND',
                                                                   self.roomId)
                    if consumeCount != self.table.runConf.cardNoteDiamond:
                        # 弹出提示商城购买钻石todotask
                        payOrder = {
                            "priceDiamond": {
                                "count": self.table.runConf.cardNoteDiamond,
                                "minCount": self.table.runConf.cardNoteDiamond,
                                "maxCount": -1
                            },
                            "buyTypes":["charge"]
                        }
                        product, _shelves = hallstore.findProductByPayOrder(self.gameId, seat.player.userId, clientId, payOrder)
                        if product:
                            buyType = 'charge'
                            btnTxt = '确定'
                            cardNoteTips = '您的钻石不足%s个，请去商城购买' % self.table.runConf.cardNoteDiamond
                            orderShow = TodoTaskOrderShow.makeByProduct(cardNoteTips, '', product, buyType)
                            orderShow.setParam('sub_action_btn_text', btnTxt)
                            mo = TodoTaskHelper.makeTodoTaskMsg(self.gameId, seat.player.userId, orderShow)
                            router.sendToUser(mo, seat.player.userId)
                        return
                    # 获得一日记牌器
                    user_remote.addAsset(self.gameId, seat.player.userId, 'item:' + str(ITEM_CARD_NOTE_KIND_ID), 1, 'MATCH_CARDNOTE_BETDIAMOND', self.roomId)
            except:
                if ftlog.is_debug():
                    ftlog.error('DizhuTableCtrl._openCardNote',
                                'tableId=', self.tableId,
                                'userId=', seat.userId,
                                'cardNoteCount=', seat.player.getCardNoteCount(),
                                'chip=', seat.player.datas.get('chip'))
                return
        if seat.player.openCardNote():
            ftlog.info('DizhuTableCtrl._openCardNote',
                       'tableId=', self.tableId,
                       'userId=', seat.userId,
                       'cardNoteCount=', seat.player.getCardNoteCount(),
                       'buyinChip=', seat.player.datas.get('chip'))
            self.table.fire(CardNoteOpenedEvent(self.table, seat))

    def setupTable(self):
        self._replay.setupTable()
        self._bireport.setupTable()
        self._remoteListener.setupTable()
        self._proto.setupTable()
    
    def reloadConf(self):
        self._table.reloadConf()

    def _makeTable(self, tableId, playMode):
        raise NotImplementedError
    
    def _makeProto(self):
        raise NotImplementedError

    def _sendTodoTaskToUser(self, userId):
        tip = '当前版本较低，请前往商城购买记牌器~'
        t = TodoTaskShowInfo(tip, True)
        try:
            if ftlog.is_debug():
                ftlog.debug('DizhuTableCtr._sendTodoTaskToUser userId = ', userId,
                            'roomId=', self.roomId,
                            'tableId=', self.tableId,
                            'tip=', tip)
            msg = TodoTaskHelper.makeTodoTaskMsg(self.gameId, userId, t)
            router.sendToUser(msg, userId)
        except:
            ftlog.error('DizhuTableCtr._sendTodoTaskToUser userId=', userId,
                        'roomId=', self.roomId,
                        'tableId=', self.tableId,
                        'tip=', tip)


