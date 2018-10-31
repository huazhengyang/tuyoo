'''
Created on 2016年6月20日

@author: zhaol
'''
import freetime.util.log as ftlog
from poker.entity.events.tyevent import EventConfigure
import poker.entity.events.tyeventbus as pkeventbus
from hall.entity import hallconf
import poker.util.timestamp as pktimestamp


class HallItemAutoExchange(object):

    def __init__(self):
        self.itemSrc = None
        self.itemDst = None
        self.ratio = None
        self.conditions = None
        self.message = None

    def decodeFromDict(self, d):
        from hall.entity.hallusercond import UserConditionRegister
        self.conditions = UserConditionRegister.decodeList(d.get('conditions', []))
        self.itemSrc = d.get('itemIdSrc', None)
        self.itemDst = d.get('itemIdDst', None)
        self.ratio = d.get('ratio', 0)
        self.message = d.get('message', None)
        if (not self.itemSrc) or (not self.message) or (not self.itemDst) or (not self.ratio) or (self.ratio < 1) or (not isinstance(self.ratio, int)):
            ftlog.error('HallItemAutoExchange.exchange config error. src:', self.itemSrc, ' dst:', self.itemDst, ' ratio:', self.ratio)
            return None
        if self.itemDst == self.itemSrc:
            ftlog.error('HallItemAutoExchange.exchange config error. src:', self.itemSrc, ' dst:', self.itemDst, ' ratio:', self.ratio)
            return None
        return self

    def exchange(self, userId, gameId, clientId, userBag):
        if ftlog.is_debug():
            ftlog.debug('HallItemAutoExchange.exchange src:', self.itemSrc, ' dst:', self.itemDst, ' ratio:', self.ratio)

        timestamp = pktimestamp.getCurrentTimestamp()
        for cond in self.conditions:
            if not cond.check(gameId, userId, clientId, timestamp):
                return

        from hall.entity import hallitem
        srcItemKind = hallitem.itemSystem.findItemKind(self.itemSrc)
        dstItemKind = hallitem.itemSystem.findItemKind(self.itemDst)

        if not srcItemKind :
            ftlog.info('HallItemAutoExchange.exchange srcItemKind not found ', self.itemSrc)
            return
        if not dstItemKind :
            ftlog.info('HallItemAutoExchange.exchange dstItemKind not found ', self.itemDst)
            return
        
        count = userBag.calcTotalUnitsCount(srcItemKind)
        if ftlog.is_debug():
            ftlog.debug('HallItemAutoExchange.exchange delItemKind:', srcItemKind, ' count:', count)

        delCount = 0
        newCount = 0
        while count >= self.ratio :
            count -= self.ratio
            delCount += self.ratio
            newCount += 1

        if delCount > 0 :
            ftlog.info('HallItemAutoExchange.exchange delItemKind:', srcItemKind, 'delCount:', delCount, 'addItemKind:', dstItemKind, 'addCount:', newCount)
            userBag.forceConsumeUnitsCountByKind(gameId, srcItemKind, delCount, timestamp, 'ITEM_AUTO_EXCHANGE', 0)
            userBag.addItemUnitsByKind(gameId, dstItemKind, newCount, timestamp, 0, 'ITEM_AUTO_EXCHANGE', 0)
            msg = self.message.replace('{delCount}', str(delCount))
            msg = msg.replace('{newCount}', str(newCount))
            from poker.entity.biz.message import message
            message.sendPrivate(gameId, userId, 0, msg, None)

_exchangeSettings = []
_inited = False


def _reloadConf():
    global _exchangeSettings

    _exchangeSettings = []

    conf = hallconf.getItemExchangeConf()
    exchanges = conf.get('exchanges', [])
    for change in exchanges:
        rItem = HallItemAutoExchange().decodeFromDict(change)
        if rItem :
            _exchangeSettings.append(rItem)

    ftlog.debug('hall_item_exchange._reloadConf successed config=', _exchangeSettings)


def _onConfChanged(event):
    global _inited
    if _inited and event.isModuleChanged('item_exchange'):
        ftlog.debug('hall_item_exchange._onConfChanged')
        _reloadConf()


def _initialize():
    global _inited
    ftlog.debug('hall_item_exchange._initialize begin')
    if not _inited:
        _inited = True
        _reloadConf()
        pkeventbus.globalEventBus.subscribe(EventConfigure, _onConfChanged)
    ftlog.debug('hall_item_exchange._initialize end')


def updateUserItems(userId, gameId, clientId, userBag=None):
    global _exchangeSettings
    if ftlog.is_debug():
        ftlog.debug('hall_item_exchange.updateUserItems userId:', userId, ' gameId:', gameId, ' clientId:', clientId)

    if not userBag:
        from hall.entity import hallitem
        userAssets = hallitem.itemSystem.loadUserAssets(userId)
        userBag = userAssets.getUserBag()

    for change in _exchangeSettings:
        change.exchange(userId, gameId, clientId, userBag)
