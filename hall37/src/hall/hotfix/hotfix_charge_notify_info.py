# -*- coding:utf-8 -*-
'''
Created on 2017年1月17日

@author: zhaojiangang
'''
import freetime.util.log as ftlog
from hall.entity import hallstore, datachangenotify
from hall.entity.hallconf import HALL_GAMEID
from hall.entity.hallstore import UserFirstRecharedEvent
from hall.game import TGHall
import poker.entity.dao.gamedata as pkgamedata


def _onChargeNotify(event):
    ftlog.info('hallstore._onChargeNotify gameId=', event.gameId,
               'userId=', event.userId,
               'diamonds=', event.diamonds,
               'rmbs=', event.rmbs,
               'firstRechargeThreshold=', hallstore.storeSystem.firstRechargeThreshold)
    if event.diamonds >= hallstore.storeSystem.firstRechargeThreshold:
        count = pkgamedata.incrGameAttr(event.userId, HALL_GAMEID, 'first_recharge', 1)
        if count == 1:
            TGHall.getEventBus().publishEvent(UserFirstRecharedEvent(HALL_GAMEID, event.userId))
            datachangenotify.sendDataChangeNotify(HALL_GAMEID, event.userId, 'promotion_loc')

hallstore._onChargeNotify = _onChargeNotify
