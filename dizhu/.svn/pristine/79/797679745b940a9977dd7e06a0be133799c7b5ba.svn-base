# -*- coding=utf-8 -*-
'''
Created on 16-5-31

@author: luwei
'''
from dizhu.activities.toolbox import Tool, Redis, UserBag
from dizhu.entity import dizhuconf
from dizhu.entity.dizhuconf import DIZHU_GAMEID
import freetime.util.log as ftlog
from hall.entity.hallevent import UserBindPhoneEvent
from hall.game import TGHall
from poker.entity.dao import userdata
from poker.entity.events.tyevent import EventUserLogin
from poker.entity.dao import sessiondata

class BindingPhoneHandler(object):
    '''
    绑定手机引导事件监听
    '''
    ACTIVITY_ID = 10045 ## 'ACT_BINDPHONE_LEAD'
    EVENT_ID = 'ACTIVITY_REWARD'

    @classmethod
    def registerListeners(cls, dizhuEventBus):
        TGHall.getEventBus().subscribe(UserBindPhoneEvent, cls.onPhoneBinding)
        TGHall.getEventBus().subscribe(EventUserLogin, cls.onUserLogin)
        return True

    @classmethod
    def getActivityConfig(cls):
        '''
        game/6/activity/0.json
        '''
        return dizhuconf.getActivityConf('bindphonelead')

    @classmethod
    def isOutdate(cls):
        '''
        获得是否过期,使用game/6/activity/0.json中的配置判断
        '''
        dizhuconf = cls.getActivityConfig()
        return not Tool.checkNow(dizhuconf.get('datetime_start', '2016-01-01 00:00:00'),
                                 dizhuconf.get('datetime_end', '2016-01-01 00:00:00'))

    @classmethod
    def getFieldKey(cls):
        '''
        获得redis,gamedata的hashmap中存储的key
        '''
        dizhuconf = cls.getActivityConfig()
        datetime_start = dizhuconf.get('datetime_start', '')
        return 'act.bingphone.issend.' + datetime_start

    @classmethod
    def isUserAlreadyBindingPhone(cls, userId):
        '''
        用户是否已经绑定了手机
        '''
        bindmobile = userdata.getAttr(userId, 'bindMobile')
        return True if bindmobile else False

    @classmethod
    def onPhoneBinding(cls, event):
        ftlog.debug('BindingPhoneHandler.onBingdingPhone:',
                    'userId=', event.userId,
                    'event=', event)

        ## 如果可以发送奖励,则发送给用户
        cls.sendingRewardOnceIfNeed(event.userId)

    @classmethod
    def onUserLogin(cls, event):

        ## 检测是否已经绑定手机
        isBindingPhone = cls.isUserAlreadyBindingPhone(event.userId)
        ftlog.debug('BindingPhoneHandler.onUserLogin:',
                    'userId=', event.userId,
                    'isBindingPhone=', isBindingPhone)
        if not isBindingPhone:
            return None

        ## 如果可以发送奖励,则发送给用户
        cls.sendingRewardOnceIfNeed(event.userId)
        return None


    @classmethod
    def sendingRewardOnceIfNeed(cls, userId):
        ftlog.debug('BindingPhoneHandler.sendingRewardOnceIfNeed:start',
                    'userId=', userId,
                    'isOutdate=', cls.isOutdate())
        if cls.isOutdate():
            return None

        ## 是否在clientId集合中
        dizhuconf = cls.getActivityConfig()
        clientIdList = dizhuconf.get('clientIdList', [])
        clientId = sessiondata.getClientId(userId)
        ftlog.debug('BindingPhoneHandler.sendingRewardOnceIfNeed:clientId',
                    'userId=', userId,
                    'clientId=', clientId,
                    'ok=', clientId in clientIdList)
        if clientId not in clientIdList:
            return None

        ## 是否是第一次领取
        isFirst = Redis.isFirst(userId, cls.getFieldKey())
        ftlog.debug('BindingPhoneHandler.sendingRewardOnceIfNeed:isFirst',
                    'userId=', userId,
                    'isFirst=', isFirst)
        if not isFirst:
            return None

        ## 发放奖励
        mail = dizhuconf.get('mail')
        assetsList = dizhuconf.get('assets')

        ftlog.debug('BindingPhoneHandler.sendingRewardOnceIfNeed:send',
                    'userId=', userId,
                    'dizhuconf=', dizhuconf)
        if not assetsList:
            return None
        
        UserBag.sendAssetsListToUser(DIZHU_GAMEID, userId, assetsList, cls.EVENT_ID, mail, cls.ACTIVITY_ID)
        ftlog.debug('BindingPhoneHandler.sendingRewardOnceIfNeed:end',
                    'userId=', userId,
                    'assetsList=', assetsList,
                    'mail=', mail)

        return None
