# -*- coding: utf-8 -*-
'''
Created on Oct 10, 2015

@author: hanwf
'''
import freetime.util.log as ftlog
from poker.entity.events.tyevent import ChargeNotifyEvent
from datetime import datetime
from dizhu.entity import dizhuconf
from poker.entity.dao import userchip, daoconst, sessiondata
from hall.entity import datachangenotify, hallitem
import poker.util.timestamp as pktimestamp
import poker.entity.biz.message.message as pkmessage

class TeHuiLiBao():
    eventset = [ChargeNotifyEvent]
    
    @classmethod
    def registerEvents(cls):
        ftlog.debug('tehuilibao register event')
        from hall.game import TGHall
        TGHall.getEventBus().subscribe(ChargeNotifyEvent, cls.handleEvent)
    
    @classmethod
    def dateCheck(cls, gameId, userId):
        conf = dizhuconf.getTeHuiLiBaoConf()
        day_now = datetime.now()
        startdate = datetime.strptime(conf.get('start_date', '2015-01-01'), '%Y-%m-%d').date()
        enddate = datetime.strptime(conf.get('end_date', '2015-01-01'), '%Y-%m-%d').date()
        
        ftlog.debug("tehuilibao userId=", userId, "day_now=", day_now, "startdate=", startdate, "enddate=", enddate)
        if day_now.date()>=startdate and day_now.date()<=enddate:
            return True
        return False
    
    @classmethod
    def handleEvent(cls, event):
        try:
            gameId = 6
            userId = event.userId
            if not cls.dateCheck(gameId, userId):
                return
            conf = dizhuconf.getTeHuiLiBaoConf()
            diamonds = conf.get('diamonds', 1000)
            itemId = conf.get('itemId', -1)
            if event.diamonds >= diamonds:
                itemKind = hallitem.itemSystem.findItemKind(itemId)
                if not itemKind:
                    ftlog.error('tehuilibao itemId not found itemId=', itemId)
                    return
                
                userBag = hallitem.itemSystem.loadUserAssets(userId).getUserBag()
                count = userBag.calcTotalUnitsCount(itemKind)
                ftlog.info('tehuilibao gameId=', gameId, 'userId=', userId, 'itemId=', itemId, 'diamonds=', event.diamonds, 'itemcount=', count)
                if count > 0:
                    oldchip = userchip.getChip(userId)
                    
                    count = userBag.consumeUnitsCountByKind(gameId, itemKind, 1, pktimestamp.getCurrentTimestamp(), 'TE_HUI_LI_BAO', 0)
                    chip = conf.get('chip', 0)

                    userchip.incrChip(userId, gameId, chip, daoconst.CHIP_NOT_ENOUGH_OP_MODE_CLEAR_ZERO, 'TE_HUI_LI_BAO', 0, sessiondata.getClientId(userId))
                    datachangenotify.sendDataChangeNotify(gameId, userId, 'chip')
                    
                    newchip = userchip.getChip(userId)
                    pkmessage.sendPrivate(9999, userId, 0, "恭喜您获得%s金币特惠礼包奖励！" % chip)
                    datachangenotify.sendDataChangeNotify(gameId, userId, 'message')
                    ftlog.info('tehuilibao gameId=', gameId, 'userId=', userId, 'itemId=', itemId, 'diamonds=', event.diamonds, 'oldchip=', oldchip, 'newchip=', newchip)
        except:
            ftlog.exception()
            ftlog.info('tehuilibao handleEvent error gameId=', event.gameId, 'userId=', event.userId)
    

