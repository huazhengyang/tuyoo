import freetime.util.log as ftlog
from poker.entity.events.tyevent import EventConfigure
import poker.entity.events.tyeventbus as pkeventbus
from hall.entity import hallconf
import poker.util.timestamp as pktimestamp
from hall.entity.hallconf import HALL_GAMEID


def exchange(self, userId, gameId, clientId):

    from hall.entity import hallitem

    if (not self.itemSrc) or (not self.itemDst) or (not self.ratio):
        ftlog.error('HallItemAutoExchange.exchange info error. src:',
                    self.itemSrc
                    , ' dst:', self.itemDst
                    , ' ratio:', self.ratio)
        return

    if ftlog.is_debug():
        ftlog.debug('HallItemAutoExchange.exchange src:', self.itemSrc
                    , ' dst:', self.itemDst
                    , ' ratio:', self.ratio)

    timestamp = pktimestamp.getCurrentTimestamp()
    for cond in self.conditions:
        if not cond.check(gameId, userId, clientId, timestamp):
            return

    userAssets = hallitem.itemSystem.loadUserAssets(userId)
    userBag = userAssets.getUserBag()

    srcItemKind = hallitem.itemSystem.findItemKind(self.itemSrc)
    dstItemKind = hallitem.itemSystem.findItemKind(self.itemDst)

    count = userBag.calcTotalUnitsCount(srcItemKind)
    if ftlog.is_debug():
        ftlog.debug('HallItemAutoExchange.exchange itemSrc:', self.itemSrc,
                    ' count:', count)

    if count <= 0:
        return

    if self.isReversed:
        newCount, remain = divmod(count, self.ratio)
        count -= remain
    else:
        newCount = int(count * self.ratio)

    if ftlog.is_debug():
        ftlog.debug('HallItemAutoExchange.exchange itemDst:', self.itemDst,
                    ' newCount:', newCount)

    userBag.forceConsumeUnitsCountByKind(gameId, srcItemKind, count,
                                         timestamp, 'ITEM_AUTO_EXCHANGE', 0)
    if newCount:
        userBag.addItemUnitsByKind(gameId, dstItemKind, newCount, timestamp,
                                   0, 'ITEM_AUTO_EXCHANGE', 0)

from hall.entity.hall_item_exchange import HallItemAutoExchange
HallItemAutoExchange.exchange = exchange
