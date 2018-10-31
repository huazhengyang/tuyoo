# -*- coding:utf-8 -*-
'''
Created on 2017年6月13日

@author: wangyonghui
'''
from dizhu.entity.dizhuconf import DIZHU_GAMEID
from dizhu.games.mix.replay import ReplayTableMix
from dizhu.games.mix.tableproto import DizhuTableProtoMix
from dizhu.games.normalbase.table import DizhuTableNormalBase, \
    DizhuTableCtrlNormalBase
from dizhucomm.core.events import CardNoteOpenedEvent
from dizhucomm.entity import emoji
from hall.entity import hallstore
from hall.entity.hallitem import ASSET_DIAMOND_KIND_ID, ITEM_CARD_NOTE_KIND_ID
from hall.entity.hallpopwnd import findTodotaskTemplate
from hall.entity.todotask import TodoTaskHelper, TodoTaskOrderShow, TodoTaskShowInfo
from hall.servers.util.rpc import user_remote
import freetime.util.log as ftlog
from poker.entity.dao import sessiondata
from poker.protocol import router
from poker.util import strutil


class DizhuTableMix(DizhuTableNormalBase):
    def __init__(self, room, tableId, dealer):
        super(DizhuTableMix, self).__init__(room, tableId, dealer)


class DizhuTableCtrlMix(DizhuTableCtrlNormalBase):
    def __init__(self, room, tableId, dealer):
        super(DizhuTableCtrlMix, self).__init__(room, tableId, dealer)
        self._replay = ReplayTableMix(self)

    def _getEmojiConf(self, seat, emojiId):
        vipLevel = seat.player.datas.get('vipInfo', {}).get('level', 0)
        emojiConf = emoji.getEmojiConf(self.gameId, seat.player.mixConf.get('roomId') or self.bigRoomId, vipLevel)
        if not emojiConf:
            return None, None, None, None, None
        conf = emojiConf.get(emojiId, None)
        if not conf:
            return None, None, None, None, None
        return conf['price'], int(conf['self_charm']), int(conf['other_charm']), conf['cd'], conf.get('bursts')

    def _openCardNote(self, seat):
        # 比赛场局记牌器在下发此消息时扣除背包金币，非比赛场局记牌器在结算时扣除带入金币
        #self.isMatch or self.table.runConf.cardNoteChipConsumeUserChip:
        if seat.player.getCardNoteCount() <= 0:
            cardNoteDiamondCount = seat.player.mixConf.get('tableConf', {}).get('cardNoteDiamond', 0)
            try:
                if cardNoteDiamondCount == 0:

                    trueDelta, _final = user_remote.incrUserChip(seat.userId,
                                                                 self.table.gameId,
                                                                 -seat.player.mixConf.get('tableConf', {}).get('cardNoteChip', 0),
                                                                 'MATCH_CARDNOTE_BETCHIP',
                                                                 0,
                                                                 seat.player.clientId)
                    if ftlog.is_debug():
                        ftlog.debug('DizhuTableCtrlMix._openCardNote',
                                    'tableId=', self.tableId,
                                    'userId=', seat.userId,
                                    'cardNoteChip=', seat.player.mixConf.get('tableConf', {}).get('cardNoteChip', 0),
                                    'chip=', seat.player.datas.get('chip'))
                    if trueDelta != -seat.player.mixConf.get('tableConf', {}).get('cardNoteChip', 0):
                        if ftlog.is_debug():
                            ftlog.warn('DizhuTableCtrlMix._openCardNote',
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

                    # 大厅版本4.56以上直接弹出贵族月卡购买弹窗
                    if clientVer > 4.56:
                        userId = seat.player.userId
                        clientId = sessiondata.getClientId(userId)
                        template, templateName = findTodotaskTemplate(DIZHU_GAMEID, userId, clientId, 'monthlyBuy')
                        todoTaskObj = template.newTodoTask(DIZHU_GAMEID, userId, clientId) if template else None
                        if ftlog.is_debug():
                            ftlog.debug('mixTable.findTodotaskTemplate.monthlyBuy', 'userId=', userId, 'template=',
                                        template, 'templateName=', templateName, 'templateDict=',
                                        todoTaskObj.toDict() if todoTaskObj else None)
                        if todoTaskObj:
                            TodoTaskHelper.sendTodoTask(DIZHU_GAMEID, userId, todoTaskObj)
                            return

                    consumeCount, final = user_remote.consumeAsset(DIZHU_GAMEID, seat.player.userId, ASSET_DIAMOND_KIND_ID, cardNoteDiamondCount, 'MATCH_CARDNOTE_BETDIAMOND', seat.player.mixConf.get('roomId') or self.roomId)
                    if consumeCount != cardNoteDiamondCount:
                        # 弹出提示商城购买钻石todotask
                        clientId = sessiondata.getClientId(seat.player.userId)
                        payOrder = {
                            "priceDiamond": {
                                "count": cardNoteDiamondCount,
                                "minCount": cardNoteDiamondCount,
                                "maxCount": -1
                            },
                            "buyTypes": ["charge"]
                        }
                        product, _shelves = hallstore.findProductByPayOrder(self.gameId, seat.player.userId, clientId, payOrder)
                        if product:
                            buyType = 'charge'
                            btnTxt = '确定'
                            orderShow = TodoTaskOrderShow.makeByProduct('您的钻石不足%s个，请去商城购买' % cardNoteDiamondCount, '', product, buyType)
                            orderShow.setParam('sub_action_btn_text', btnTxt)
                            mo = TodoTaskHelper.makeTodoTaskMsg(self.gameId, seat.player.userId, orderShow)
                            router.sendToUser(mo, seat.player.userId)
                        return
                    # 获得一日记牌器
                    user_remote.addAsset(DIZHU_GAMEID, seat.player.userId, 'item:' + str(ITEM_CARD_NOTE_KIND_ID), 1, 'MATCH_CARDNOTE_BETDIAMOND', seat.player.mixConf.get('roomId') or self.roomId)
            except:
                if ftlog.is_debug():
                    ftlog.error('DizhuTableCtrlMix._openCardNote',
                                'tableId=', self.tableId,
                                'userId=', seat.userId,
                                'cardNoteCount=', seat.player.getCardNoteCount(),
                                'chip=', seat.player.datas.get('chip'))
                return
        if seat.player.openCardNote():
            ftlog.info('DizhuTableCtrlMix._openCardNote',
                       'tableId=', self.tableId,
                       'userId=', seat.userId,
                       'cardNoteCount=', seat.player.getCardNoteCount(),
                       'buyinChip=', seat.player.datas.get('chip'))
            self.table.fire(CardNoteOpenedEvent(self.table, seat))

    def _makeTable(self, tableId, dealer):
        return DizhuTableMix(self.room, tableId, dealer)

    def _makeProto(self):
        return DizhuTableProtoMix(self)

    def _sendTodoTaskToUser(self, userId):
        tip = ''
        t = TodoTaskShowInfo(tip, True)
        try:
            if ftlog.is_debug():
                ftlog.debug('DizhuTableCtrMix._sendTodoTaskToUser userId = ', userId,
                            'roomId=', self.roomId,
                            'tableId=', self.tableId,
                            'tip=', tip)
            msg = TodoTaskHelper.makeTodoTaskMsg(DIZHU_GAMEID, userId, t)
            router.sendToUser(msg, userId)
        except:
            ftlog.error('DizhuTableCtrMix._sendTodoTaskToUser userId=', userId,
                        'roomId=', self.roomId,
                        'tableId=', self.tableId,
                        'tip=', tip)
