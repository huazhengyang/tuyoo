# -*- coding=utf-8 -*-
"""
@file  : activity_credit_exchange
@date  : 2016-09-09
@author: GongXiaobo
"""
import copy

import freetime.util.log as ftlog
from hall.entity import datachangenotify

from hall.entity import hallitem
from hall.entity import hallpopwnd
from hall.entity.hallactivity.activity import ACTIVITY_KEY
from hall.entity.hallactivity.activity_type import TYActivityType
from hall.entity.hallconf import HALL_GAMEID
from hall.entity.hallroulette import TYEventRouletteDiamond
from hall.entity.hallshare import HallShareEvent
from hall.entity.monthcheckin import MonthCheckinOkEvent, MonthSupCheckinOkEvent
from hall.game import TGHall
from poker.entity.biz.activity.activity import TYActivity
from poker.entity.biz.confobj import TYConfable, TYConfableRegister
from poker.entity.biz.content import TYContentRegister
from poker.entity.biz.item.item import TYAssetUtils
from poker.entity.configure import gdata
from poker.entity.dao import daobase
from poker.entity.events.tyevent import GameOverEvent, ChargeNotifyEvent, BetOnEvent
from poker.util import strutil
from poker.util import timestamp


class CreditSource(TYConfable):
    def __init__(self):
        super(CreditSource, self).__init__()
        self.index = None
        self.act = None
        self.limit = -1

    def decodeFromDict(self, d):
        return self

    def cleanup(self):
        pass

    def attach2act(self, act, index):
        assert isinstance(act, TYActCreditExchange) and index >= 0
        self.act = act
        self.index = index

    def _add_credit(self, userid, credit, times):
        actkey = ACTIVITY_KEY.format(HALL_GAMEID, userid, self.act.getid())
        if self.limit > 0:
            field_time = self.act.FIELD_SOURCE_TIME.format(self.index)
            field_data = self.act.FIELD_SOURCE_NUM.format(self.index)
            used = self.act.check_reset('day', userid, actkey, field_data, field_time)
            if used >= self.limit:
                return
            times = min(times, self.limit - used)
            daobase.executeUserCmd(userid, 'HINCRBY', actkey, field_data, times)
        delta = int(credit * times)
        if delta <= 0:
            return
        self.act.alter_user_credit(userid, actkey, delta)


class CreditSourceGamePlay(CreditSource):
    TYPE_ID = 'act.credit.gamePlay'

    def __init__(self):
        super(CreditSourceGamePlay, self).__init__()
        self.gameid = None
        self.play_result = None
        self.room2credit = None
        TGHall.getEventBus().subscribe(GameOverEvent, self.handle_event)

    def decodeFromDict(self, d):
        self.gameid = d.get('game')
        self.play_result = d.get('playResult')
        self.room2credit = d.get('credits')
        return self

    def cleanup(self):
        TGHall.getEventBus().unsubscribe(GameOverEvent, self.handle_event)

    def handle_event(self, event):
        if not self.act.checkOperative():
            return
        if not isinstance(event, GameOverEvent):
            return
        if self.play_result is not None and self.play_result != event.gameResult:
            return
        # 历史原因,很多插件都写成9999了,尽量纠正一把
        gameid = event.gameId if event.gameId != HALL_GAMEID else strutil.getGameIdFromHallClientId(event.clientId)
        if gameid != self.gameid:
            return

        bigRoomId = gdata.getBigRoomId(event.roomId)
        bigroom = bigRoomId if bigRoomId else event.roomId
        credit = self.room2credit.get(str(bigroom), 0)

        if ftlog.is_debug():
            ftlog.debug('CreditSourceGamePlay.handle_event userId=', event.userId,
                        'gameId=', gameid, 'self.gameId=', self.gameid,
                        'bigroom=', bigroom,
                        'credit=', credit,
                        'event.roomId=', event.roomId,
                        'room2credit', self.room2credit)
        if credit <= 0:
            return
        self._add_credit(event.userId, credit, event.roundNum)


class CreditSourceDiamondRoulette(CreditSource):
    TYPE_ID = 'act.credit.diamondRoulette'

    def __init__(self):
        super(CreditSourceDiamondRoulette, self).__init__()
        self.credit = None
        TGHall.getEventBus().subscribe(TYEventRouletteDiamond, self.handle_event)

    def decodeFromDict(self, d):
        self.limit = d.get('limitTimes', -1)
        self.credit = d.get('credit', 0)
        return self

    def cleanup(self):
        TGHall.getEventBus().unsubscribe(TYEventRouletteDiamond, self.handle_event)

    def handle_event(self, event):
        if self.credit <= 0 or self.limit == 0:
            return
        if not self.act.checkOperative():
            return
        if not isinstance(event, TYEventRouletteDiamond):
            return
        self._add_credit(event.userId, self.credit, event.number)


class CreditSourceShare(CreditSource):
    TYPE_ID = 'act.credit.share'

    def __init__(self):
        super(CreditSourceShare, self).__init__()
        self.credit = None
        self.shareids = None
        TGHall.getEventBus().subscribe(HallShareEvent, self.handle_event)

    def decodeFromDict(self, d):
        self.limit = d.get('limitTimes', -1)
        self.credit = d.get('credit', 0)
        self.shareids = set(d.get('shareIds', []))
        return self

    def cleanup(self):
        TGHall.getEventBus().unsubscribe(HallShareEvent, self.handle_event)

    def handle_event(self, event):
        if self.credit <= 0 or self.limit == 0:
            return
        if not self.act.checkOperative():
            return
        if not isinstance(event, HallShareEvent):
            return
        if event.shareid not in self.shareids:
            return
        self._add_credit(event.userId, self.credit, 1)


class CreditSourceCharge(CreditSource):
    TYPE_ID = 'act.credit.charge'

    def __init__(self):
        super(CreditSourceCharge, self).__init__()
        self.credit = None
        TGHall.getEventBus().subscribe(ChargeNotifyEvent, self.handle_event)

    def decodeFromDict(self, d):
        self.credit = d.get('credit', 0)
        return self

    def cleanup(self):
        TGHall.getEventBus().unsubscribe(ChargeNotifyEvent, self.handle_event)

    def handle_event(self, event):
        if self.credit <= 0:
            return
        if not self.act.checkOperative():
            return
        if not isinstance(event, ChargeNotifyEvent):
            return
        self._add_credit(event.userId, self.credit * event.rmbs, 1)


class CreditSourceCheckin(CreditSource):
    TYPE_ID = 'act.credit.checkin'

    def __init__(self):
        super(CreditSourceCheckin, self).__init__()
        self.credit = None
        TGHall.getEventBus().subscribe(MonthCheckinOkEvent, self.handle_event)

    def decodeFromDict(self, d):
        self.credit = d.get('credit', 0)
        return self

    def cleanup(self):
        TGHall.getEventBus().unsubscribe(MonthCheckinOkEvent, self.handle_event)

    def handle_event(self, event):
        if self.credit <= 0:
            return
        if not self.act.checkOperative():
            return
        if not isinstance(event, MonthCheckinOkEvent):
            return
        self._add_credit(event.userId, self.credit, 1)


class CreditSourceSupplementCheckin(CreditSource):
    TYPE_ID = 'act.credit.supplementCheckin'

    def __init__(self):
        super(CreditSourceSupplementCheckin, self).__init__()
        self.credit = None
        TGHall.getEventBus().subscribe(MonthSupCheckinOkEvent, self.handle_event)

    def decodeFromDict(self, d):
        self.limit = d.get('limitTimes', -1)
        self.credit = d.get('credit', 0)
        return self

    def cleanup(self):
        TGHall.getEventBus().unsubscribe(MonthSupCheckinOkEvent, self.handle_event)

    def handle_event(self, event):
        if self.credit <= 0:
            return
        if not self.act.checkOperative():
            return
        if not isinstance(event, MonthSupCheckinOkEvent):
            return
        self._add_credit(event.userId, self.credit, 1)


class CreditSourceBet(CreditSource):
    TYPE_ID = 'act.credit.bet'

    def __init__(self):
        super(CreditSourceBet, self).__init__()
        self.amount = None
        TGHall.getEventBus().subscribe(BetOnEvent, self.handle_event)

    def decodeFromDict(self, d):
        self.amount = d.get('amount', 1)
        return self

    def cleanup(self):
        TGHall.getEventBus().unsubscribe(BetOnEvent, self.handle_event)

    def handle_event(self, event):
        if self.amount <= 0:
            return
        if not self.act.checkOperative():
            return
        if not isinstance(event, BetOnEvent):
            return
        self._add_credit(event.userId, event.amount / self.amount, 1)


class CreditSourceRegister(TYConfableRegister):
    _typeid_clz_map = {
        CreditSourceGamePlay.TYPE_ID: CreditSourceGamePlay,
        CreditSourceDiamondRoulette.TYPE_ID: CreditSourceDiamondRoulette,
        CreditSourceShare.TYPE_ID: CreditSourceShare,
        CreditSourceCharge.TYPE_ID: CreditSourceCharge,
        CreditSourceCheckin.TYPE_ID: CreditSourceCheckin,
        CreditSourceSupplementCheckin.TYPE_ID: CreditSourceSupplementCheckin,
        CreditSourceBet.TYPE_ID: CreditSourceBet
    }


class TYActCreditExchange(TYActivity):
    TYPE_ID = TYActivityType.ACTIVITY_CREDIT_EXCHANGE
    FIELD_CREDIT_NUM = 'credit:num'
    FIELD_CREDIT_TIME = 'credit:time'
    FIELD_SOURCE_NUM = 'source:{}:num'
    FIELD_SOURCE_TIME = 'source:{}:time'
    FIELD_EXCHANGE_NUM = 'exchange:{}:num'
    FIELD_EXCHANGE_TIME = 'exchange:{}:time'

    def __init__(self, dao, clientConfig, serverConfig):
        super(TYActCreditExchange, self).__init__(dao, clientConfig, serverConfig)
        self._initial()

    def reload(self, config):
        super(TYActCreditExchange, self).reload(config)
        for source in self._sources:
            source.cleanup()
        self._initial()

    def _initial(self):
        ftlog.info('TYActCreditExchange._initial id=', self.getid())
        _sources = []
        for idx, sourcedict in enumerate(self._serverConf['creditSource']):
            sourceobj = CreditSourceRegister.decodeFromDict(sourcedict)
            if sourceobj:
                sourceobj.attach2act(self, idx)
                _sources.append(sourceobj)
        self._sources = _sources

        _exchanges = {}
        for info in self._clientConf['config']['exchange']:
            info2 = copy.copy(info)
            info2['content'] = TYContentRegister.decodeFromDict(info['content'])
            _exchanges[info2['id']] = info2
            # 原始配置填充图片信息
            content_items = info2['content'].getItems()
            assetKind = hallitem.itemSystem.findAssetKind(content_items[0].assetKindId)
            info['pic'] = assetKind.pic
        self._exchanges = _exchanges

    def finalize(self):
        for source in self._sources:
            source.cleanup()

    def getConfigForClient(self, gameId, userId, clientId):
        conf = copy.deepcopy(self._clientConf)
        button = conf["config"]["button"]
        if button["visible"]:
            todoTaskDict = button["todoTask"]
            if todoTaskDict:
                todoTaskObj = hallpopwnd.decodeTodotaskFactoryByDict(todoTaskDict).newTodoTask(gameId, userId, clientId)
                button["todoTask"] = todoTaskObj.toDict()
        else:
            del conf["config"]["button"]
        return conf

    def check_reset(self, resettype, userid, actkey, data_field, time_field):
        oldtime = daobase.executeUserCmd(userid, 'HGET', actkey, time_field)
        curtime = timestamp.getCurrentTimestamp()
        if not oldtime or (resettype == 'day' and not timestamp.is_same_day(oldtime, curtime)):
            daobase.executeUserCmd(userid, 'HMSET', actkey, time_field, curtime, data_field, 0)
            return 0
        return daobase.executeUserCmd(userid, 'HGET', actkey, data_field)

    def get_user_credit(self, userid, actkey):
        return self.check_reset(self._serverConf["creditReset"], userid, actkey, self.FIELD_CREDIT_NUM,
                                self.FIELD_CREDIT_TIME)

    def alter_user_credit(self, userid, actkey, delta):
        if not delta:
            return False
        cur = self.get_user_credit(userid, actkey)
        cur += delta
        if cur < 0:
            return False
        daobase.executeUserCmd(userid, 'HSET', actkey, self.FIELD_CREDIT_NUM, cur)
        return True

    def get_exchange_buynum(self, userid, actkey, exchange):
        return self.check_reset(exchange['limitReset'], userid, actkey, self.FIELD_EXCHANGE_NUM.format(exchange['id']),
                                self.FIELD_EXCHANGE_TIME.format(exchange['id']))

    def handleRequest(self, msg):
        userid = msg.getParam('userId')
        gameid = msg.getParam('gameId')
        action = msg.getParam("action")
        actkey = ACTIVITY_KEY.format(HALL_GAMEID, userid, self.getid())
        if action == "credit_query":
            return self._query(userid, actkey)
        if action == "credit_exchange":
            exchangeid = msg.getParam('productId')
            return self._exchange(gameid, userid, actkey, exchangeid)
        return {'result': 'fail', 'tip': "unknown action"}

    def _query(self, userid, actkey):
        products = {}
        for iid, info in self._exchanges.iteritems():
            products[iid] = self.get_exchange_buynum(userid, actkey, info)
        return {'products': products, 'credit': self.get_user_credit(userid, actkey)}

    def _exchange(self, gameid, userid, actkey, exchangeid):
        info = self._exchanges.get(exchangeid)
        if not info:
            return {'result': 'fail', 'tip': "unknown productId"}

        buynum = self.get_exchange_buynum(userid, actkey, info)
        if buynum >= info['limitTimes']:
            return {'result': 'fail', 'tip': '兑换次数已满'}

        if not self.alter_user_credit(userid, actkey, -info['price']):
            return {'result': 'fail', 'tip': '您的积分不足'}
        daobase.executeUserCmd(userid, 'HINCRBY', actkey, self.FIELD_EXCHANGE_NUM.format(exchangeid), 1)

        userAssets = hallitem.itemSystem.loadUserAssets(userid)
        assetList = userAssets.sendContent(gameid, info['content'], 1, True,
                                           timestamp.getCurrentTimestamp(), "ACTIVITY_CREDIT_EXCHANGE", exchangeid)
        response = self._query(userid, actkey)
        ftlog.debug('TYActCreditExchange._exchange gameId=', gameid,
                   'userId=', userid,
                   'activityId=', self.getid(),
                   'reward=', TYAssetUtils.buildContents(assetList),
                   'buynum=', buynum + 1,
                   'credit=', response['credit'])
        changeNames = TYAssetUtils.getChangeDataNames(assetList)
        datachangenotify.sendDataChangeNotify(gameid, userid, changeNames)
        response['result'] = 'ok'
        response['tip'] = '兑换成功，您获得' + TYAssetUtils.buildContentsString(assetList)
        return response

if __name__ == '__main__':
    pass
