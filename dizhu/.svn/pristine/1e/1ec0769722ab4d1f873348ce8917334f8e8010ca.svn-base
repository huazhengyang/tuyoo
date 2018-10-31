# -*- coding: utf-8 -*-
'''
Created on Nov 25, 2015

@author: hanwf
'''
from poker.entity.events.tyevent import EventUserLogin
import freetime.util.log as ftlog
from datetime import datetime
from dizhu.entity import dizhuconf
from hall.entity import hallvip, hallitem, datachangenotify
import poker.util.timestamp as pktimestamp
from poker.entity.biz.content import TYContentItem
import poker.entity.biz.message.message as pkmessage
from poker.entity.dao import gamedata, sessiondata
from poker.util import strutil

class VipSend(object):
    eventset = [EventUserLogin]
    
    @classmethod
    def registerEvents(cls):
        ftlog.debug('vipsend register events')
        from hall.game import TGHall
        TGHall.getEventBus().subscribe(EventUserLogin, cls.handleEvent)
    
    @classmethod
    def dateCheck(cls, gameId, userId, conf):
        day_now = datetime.now()
        start_datetime = datetime.strptime(conf.get('start_date', '2015-01-01 0:0:0'), '%Y-%m-%d %H:%M:%S')
        end_datetime = datetime.strptime(conf.get('end_date', '2015-01-01 0:0:0'), '%Y-%m-%d %H:%M:%S')
        
        ftlog.debug("vipsend userId=", userId, "day_now=", day_now, ";start_datetime=", start_datetime, ";end_datetime=", end_datetime)
        if day_now>=start_datetime and day_now<=end_datetime:
            ftlog.debug("VipSend.dateCheck daynow in range")
            return True
        ftlog.debug("VipSend.dateCheck daynow not in range")
        return False
    
    @classmethod
    def gameCheck(cls, userId, gameId):
        userGameId = strutil.getGameIdFromHallClientId(sessiondata.getClientId(userId))
        ftlog.debug('VipSend.gameCheck gameId=', gameId, 'userGameId=', userGameId)
        if userGameId != gameId:
            return False
        else:
            return True
        
    @classmethod
    def getFlagAttr(cls, start_date):
        return "act_vip_send:" + start_date
    
    @classmethod
    def removeVipItems(cls, gameId, userId, conf):
        '''
        删除礼包，及次日礼包等，礼包ID需要在活动中的items中配置
        '''
        # 时间
        timestamp = pktimestamp.getCurrentTimestamp()
        userAssets = hallitem.itemSystem.loadUserAssets(userId)
        userBag = userAssets.getUserBag()
        
        # 礼包群
        items = conf.get('items', [])
        ftlog.debug('VipSend.removeVipItems items=', items)
        
        # 将所有的礼包删除
        for itemId in items:
            itemKind = hallitem.itemSystem.findItemKind(itemId)
            count = userBag.calcTotalUnitsCount(itemKind)
            userBag.forceConsumeUnitsCountByKind(gameId, itemKind, count, timestamp, 'DIZHU_VIP_SEND', 0)

    @classmethod
    def handleEvent(cls, event):
        try:
            gameId = 6
            userId = event.userId
            conf = dizhuconf.getActivityConf("vip_send")
            
            if not cls.dateCheck(gameId, userId, conf):
                cls.removeVipItems(gameId, userId, conf)
                return
            
            if not cls.gameCheck(userId, gameId):
                return
            
            vipLevel = int( hallvip.userVipSystem.getUserVip(userId).vipLevel.level )
            vipLevelLimit = conf.get("vip_level", 1)
            
            ftlog.debug('VipSend.handleEvent vipLevel=', vipLevel, 'vipLevelLimit=', vipLevelLimit, 'userId=', userId)
            
            if vipLevel >= vipLevelLimit:
                attrname = cls.getFlagAttr(conf.get('start_date', '2015-01-01'))
                is_send = gamedata.getGameAttr(userId, gameId, attrname)
                
                if is_send:
                    return
                
                items = conf.get("item_send", [])
                timestamp = pktimestamp.getCurrentTimestamp()
                for item in items:
                    contentItem = TYContentItem.decodeFromDict(item)
                    userAssets = hallitem.itemSystem.loadUserAssets(userId)
                    assetKind, _, _ = userAssets.addAsset(gameId, contentItem.assetKindId,
                                                                  contentItem.count, timestamp,
                                                                  'DIZHU_VIP_SEND', 0)
                mail = conf.get("mail", "")
                if mail:
                    pkmessage.sendPrivate(9999, userId, 0, mail)
                    
                if assetKind.keyForChangeNotify:
                    datachangenotify.sendDataChangeNotify(gameId, userId, [assetKind.keyForChangeNotify, 'message'])
                
                gamedata.setGameAttr(userId, gameId, attrname, 1)
                
                ftlog.debug('vipsend vipLevel=', vipLevel, 'vipLevelLimit=', vipLevelLimit, 'userId=', userId, "attrname=", attrname)
        except:
            ftlog.exception()
        
