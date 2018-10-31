# -*- coding=utf-8


import freetime.util.log as ftlog

def onVipChargeNotifyEvent(event):
    from hall.entity import newcheckin
    newcheckin.deductionVipComplement(event)
    ftlog.info("onVipChargeNotifyEvent|", event.userId, event.rmbs if event.rmbs else 1)



from hall.game import TGHall
from poker.entity.events.tyevent import ChargeNotifyEvent

TGHall.getEventBus().subscribe(ChargeNotifyEvent, onVipChargeNotifyEvent)