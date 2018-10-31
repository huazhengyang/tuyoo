# -*- coding=utf-8 -*-
'''
Created on 16-2-14
@author: luwei
'''
from dizhu.activities.toolbox import Tool, Redis, UserBag
from dizhu.entity import dizhuconf
from dizhu.entity.dizhuconf import DIZHU_GAMEID
import freetime.util.log as ftlog
from hall.game import TGHall
from poker.entity.dao import sessiondata
from poker.entity.events.tyevent import EventUserLogin


class ItemSender(object):

    @classmethod
    def registerListeners(cls, ddzeventbus):
        ftlog.debug("ItemSender.registerListeners")
        TGHall.getEventBus().subscribe(EventUserLogin, cls.onUserLogin)

    @classmethod
    def getDdzActivityConf(cls):
        return dizhuconf.getActivityConf("item_sender")

    @classmethod
    def isOutdate(cls):
        '''
        获得是否过期,使用game/6/activity/0.json中的配置判断
        '''
        dizhuconf = cls.getDdzActivityConf()
        return not Tool.checkNow(dizhuconf.get('datetime_start', '2016-01-01 00:00:00'), dizhuconf.get('datetime_end', '2016-01-01 00:00:00'))

    @classmethod
    def getUniqueKey(cls):
        ddzconf = cls.getDdzActivityConf()
        datetime_start = ddzconf.get("datetime_start", "")
        return "ItemSender" + datetime_start

    @classmethod
    def isClientIdSupport(cls, userId, supportContainClientIdOr):
        '''
        @param supportContainClientIdOr: 或的关系
        '''
        # 默认全支持
        clientId = sessiondata.getClientId(userId)
        ftlog.debug('ItemSender.isClientIdSupport:',
                    'userId=', userId,
                    'clientId=', clientId,
                    'supportContainClientIdOr=', supportContainClientIdOr,
                    'len(supportContainClientIdOr)=', len(supportContainClientIdOr))
        if len(supportContainClientIdOr) <= 0:
            return True
        for clientIdSegment in supportContainClientIdOr:
            if clientId.find(clientIdSegment) >= 0:
                return True
        return False

    @classmethod
    def onUserLogin(cls, event):
        ftlog.debug("ItemSender.onUserLogin: event=", event)

        userId = event.userId
        dizhuconf = cls.getDdzActivityConf()

        if not Tool.isGameDdz(userId):
            return

        if cls.isOutdate():
            ftlog.debug("ItemSender.onUserLogin: userId=", userId, "isOutdate=", True)
            return

        # 若clientId不支持，则返回
        isSupport = cls.isClientIdSupport(userId, dizhuconf.get('supportContainClientIdOr', []))
        ftlog.debug("ItemSender.onUserLogin: userId=", userId, "isSupport=", isSupport)
        if not isSupport:
            return

        isFirst = Redis.isFirst(userId, cls.getUniqueKey())
        ftlog.debug("ItemSender.onUserLogin: userId=", userId, "isFirst=", isFirst)
        if not isFirst:
            return

        # 发放道具
        ftlog.debug("ItemSender.onUserLogin: userId=", userId, "ddzconf=", dizhuconf)
        mail = dizhuconf.get("mail")
        assets = dizhuconf.get("assets")
        if not assets:
            return

        UserBag.sendAssetsToUser(DIZHU_GAMEID, userId, assets, 'DDZ_ATC_ITEM_SENDER', mail)
        ftlog.debug("ItemSender.onUserLogin: userId=", userId, "send assets=", assets, "mail=", mail)
