# -*- coding:utf-8 -*-
'''
Created on 2016年5月23日

@author: zhaojiangang
'''
import calendar

from dizhu.activities.toolbox import Tool
from dizhu.entity import dizhuconf
from dizhu.entity.dizhuconf import DIZHU_GAMEID
import freetime.util.log as ftlog
from hall.entity import hallitem, datachangenotify
from hall.entity.hallactivity import activity
from hall.entity.hallactivity.activity_play_game_present_gift import \
    TYActivityPlayGamePresentGift
from hall.entity.hallconf import HALL_GAMEID
from hall.entity.monthcheckin import MonthCheckinOkEvent, MonthSupCheckinOkEvent
from poker.entity.biz.activity.activity import TYActivityRegister
from poker.entity.biz.content import TYContentRegister
from poker.entity.biz.item.item import TYAssetUtils
from poker.entity.biz.message import message
from poker.entity.dao import sessiondata
from poker.util import strutil
import poker.util.timestamp as pktimestamp


class MonthCheckinGift(object):
    ACTIVITY_ID = 10044
    
    @classmethod
    def initialize(cls):
        from hall.game import TGHall
        TGHall.getEventBus().subscribe(MonthCheckinOkEvent, cls.handleEvent)
        TGHall.getEventBus().subscribe(MonthSupCheckinOkEvent, cls.handleEvent)
        
    @classmethod
    def handleEvent(cls, event):
        conf = dizhuconf.getActivityConf('month_checkin_gift')
        monthDayCount = calendar.monthrange(event.checkinDate.year, event.checkinDate.month)[1]
        giftDayCount = conf.get('giftDayCount', -1)
        if giftDayCount <= 0:
            giftDayCount = monthDayCount
        giftDayCount = min(giftDayCount, monthDayCount)
        
        clientId = sessiondata.getClientId(event.userId)
        hallGameId = strutil.getGameIdFromHallClientId(clientId)
        
        if hallGameId != DIZHU_GAMEID:
            return
        
        if ftlog.is_debug():
            ftlog.debug('MonthCheckinGift.handleEvent userId=', event.userId,
                        'gameId=', event.gameId,
                        'eventType=', type(event),
                        'checkinDate=', event.checkinDate,
                        'allCheckinCount=', event.status.allCheckinCount,
                        'giftDayCount=', giftDayCount,
                        'monthDayCount=', monthDayCount)
        
        giftContent = None
        try:
            if not Tool.checkNow(conf.get('datetime_start'), conf.get('datetime_end')):
                ftlog.debug('MonthCheckinGift.handleEvent outOfDate userId=', event.userId,
                            'gameId=', event.gameId,
                            'eventType=', type(event),
                            'checkinDate=', event.checkinDate,
                            'allCheckinCount=', event.status.allCheckinCount,
                            'giftDayCount=', giftDayCount,
                            'monthDayCount=', monthDayCount)
                return
            
            giftContent = TYContentRegister.decodeFromDict(conf.get('giftContent'))
        except:
            ftlog.error('MonthCheckinGift.handleEvent userId=', event.userId,
                        'gameId=', event.gameId,
                        'eventType=', type(event),
                        'checkinDate=', event.checkinDate,
                        'allCheckinCount=', event.status.allCheckinCount,
                        'giftDayCount=', giftDayCount,
                        'monthDayCount=', monthDayCount)
            return
        
        if event.status.allCheckinCount >= giftDayCount:
            assetList = None
            if giftContent:
                userAssets = hallitem.itemSystem.loadUserAssets(event.userId)
                assetList = userAssets.sendContent(DIZHU_GAMEID, giftContent, 1, True,
                                                   pktimestamp.getCurrentTimestamp(),
                                                   'ACTIVITY_REWARD', cls.ACTIVITY_ID)
                changed = TYAssetUtils.getChangeDataNames(assetList)
                mail = conf.get('mail', '')
                if mail:
                    gotContent = giftContent.desc if giftContent.desc else TYAssetUtils.buildContentsString(assetList)
                    mail = strutil.replaceParams(mail, {'gotContent':gotContent})
                    message.sendPrivate(HALL_GAMEID, event.userId, 0, mail)
                    changed.add('message')
                datachangenotify.sendDataChangeNotify(HALL_GAMEID, event.userId, changed)
                
            ftlog.info('MonthCheckinGift.statics sendGift userId=', event.userId,
                       'gameId=', event.gameId,
                       'eventType=', type(event),
                       'checkinDate=', event.checkinDate,
                       'allCheckinCount=', event.status.allCheckinCount,
                       'giftDayCount=', giftDayCount,
                       'monthDayCount=', monthDayCount,
                       'rewards=', [(a[0].kindId, a[1]) for a in assetList] if assetList else None)
    

class MonthCheckinGiftNum(object):
    activityId = 'activity_ddz_zhongqiujifen_0913'
    presentNum = 10
    
    @classmethod
    def initialize(cls):
        from hall.game import TGHall
        TGHall.getEventBus().subscribe(MonthCheckinOkEvent, cls.handleEvent)
    
    @classmethod
    def handleEvent(cls, event):
        clientId = sessiondata.getClientId(event.userId)
        hallGameId = strutil.getGameIdFromHallClientId(clientId)
        
        if hallGameId != DIZHU_GAMEID:
            return
        
        actObj = cls._findActObj(event.gameId, event.userId, clientId)
        if actObj:
            actObj.addPresentNum(HALL_GAMEID, event.userId, clientId, cls.presentNum)
            ftlog.info('MonthCheckinGiftNum.handleEvent gameId=', event.gameId,
                       'userId=', event.userId,
                       'presentNumActId=', cls.activityId,
                       'clientId=', clientId,
                       'sendPresentNum=', cls.presentNum)

    @classmethod
    def _findActObj(cls, gameId, userId, clientId):
        actConf = activity.activitySystem.getClientActivityConfig(clientId, cls.activityId)
        ftlog.debug('MonthCheckinGiftNum._findActObj gameId=', gameId,
                   'userId=', userId,
                   'presentNumActId=', cls.activityId,
                   'clientId=', clientId,
                   'actConf=', actConf)
        if actConf and TYActivityRegister.findClass(actConf.get('typeid')) == TYActivityPlayGamePresentGift:
            return activity.activitySystem.generateOrGetActivityObject(actConf)
        return None
    

