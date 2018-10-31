# -*- coding=utf-8 -*-
'''
Created on 16-2-14
@desc: 段位礼包活动
@author: luwei
'''

from dizhu.activities.toolbox import Redis, UserBag
from dizhu.entity import dizhuconf
from dizhu.entity.dizhuconf import DIZHU_GAMEID
import freetime.util.log as ftlog
from hall.game import TGHall
from poker.entity.dao import sessiondata
from poker.entity.events.tyevent import EventUserLogin
from poker.util import strutil


class SkillLevelGift(object):

    @classmethod
    def registerListeners(cls, ddzeventbus):
        ftlog.debug("SkillLevelGift.registerListeners")
        TGHall.getEventBus().subscribe(EventUserLogin, cls.onUserLogin)

    @classmethod
    def getDdzActivityConf(cls):
        return dizhuconf.getActivityConf("skilllevel_gift")

    @classmethod
    def onUserLogin(cls, event):
        ftlog.debug("SkillLevelGift.onUserLogin: event=", event)

        # gameId = 6
        userId = event.userId
        clientId = sessiondata.getClientId(userId)
        gameId = strutil.getGameIdFromHallClientId(clientId)
        ddzconf = cls.getDdzActivityConf()
        mapkey = "SkillLevelGift" + ddzconf.get("start", "")

        if gameId != DIZHU_GAMEID:
            return

        toggle = ddzconf.get("toggle", False)
        ftlog.debug("SkillLevelGift.onUserLogin: userId=", userId, "open_toggle=", toggle)
        if not toggle:
            return

        isFirst = Redis.isFirst(userId, mapkey)
        ftlog.debug("SkillLevelGift.onUserLogin: userId=", userId, "isFirst=", isFirst)
        if not isFirst:
            return

        # 发放道具
        mail = ddzconf.get("mail", "")
        assets = ddzconf.get("assets")
        UserBag.sendAssetsToUser(gameId, userId, assets, 'DDZ_ATC_SKILLLEVEL_GIFT', mail)
        ftlog.debug("SkillLevelGift.onUserLogin: userId=", userId, "send assets=", assets, "mail=", mail)
