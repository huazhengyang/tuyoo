# -*- coding=utf-8 -*-
import copy

import freetime.util.log as ftlog
import poker.entity.dao.statedata as sdata
import poker.entity.events.tyeventbus as pkeventbus
from hall.entity import hallconf, hallmoduletip
from hall.entity.hallactivity.activity_ddz_match import TYActivityDdzMatch
from hall.entity.hallactivity.activity_exchange_code import \
    TYActivityExchangeCode
from hall.entity.hallactivity.activity_fanfanle import TYActivityFanfanle
from hall.entity.hallactivity.activity_first_charge import TYActivityFirstCharge
from hall.entity.hallactivity.activity_jump_to_welfare import \
    TYActivityJumpToWelfare
from hall.entity.hallactivity.activity_match_quiz import TYActivityMatchQuiz
from hall.entity.hallactivity.activity_noticeImg import TYActivityNoticeImg
from hall.entity.hallactivity.activity_play_game_present_gift import \
    TYActivityPlayGamePresentGift
from hall.entity.hallactivity.activity_raffle import TYActivityRaffle
from hall.entity.hallactivity.activity_sale import TYActivitySale
from hall.entity.hallactivity.activity_vip_match import TYActivityVipMatch
from hall.game import TGHall
from hall.servers.util.moduletip_handler import ModuletipTcpHandlerHelp
from poker.entity.biz.activity.activity import TYActivitySystem, \
    TYActivityRegister
from poker.entity.biz.activity.dao import TYActivityDao
from poker.entity.events.tyevent import EventConfigure
from poker.entity.events.tyevent import OnLineGameChangedEvent
from poker.protocol import router
from poker.util import strutil
from hall.entity.hallconf import HALL_GAMEID
import poker.util.timestamp as pktimestamp
from hall.entity.hallusercond import UserConditionRegister


class TYActivityDaoImpl(TYActivityDao):
    activitiesConf = {}
    templatesConf = {}
    modulesConf = {}

    @classmethod
    def getActivitiesForClient(cls, clientId):
        '''
        1.拿到模板
        2.获取活动列表
        3.返回活动列表
        '''
        template = hallconf.getClientActivityConf(clientId)
        ftlog.debug("getActivitiesForClient template: ", template)
        listConfAll = cls.templatesConf.get(template, {})

        listConf = listConfAll.get("activities", [])
        ftlog.debug("getActivitiesForClient activity list: ", listConf)
        return listConf

    @classmethod
    def getActivityConfig(cls, activityId):
        '''
        根据活动ID获取活动详情
        '''
        tempAct = copy.copy(cls.activitiesConf.get(activityId))
        if not tempAct:
            return None
        tempAct["configURL"] = cls.modulesConf.get(tempAct["moduleId"])
        return tempAct

    @classmethod
    def getClientActivityConfig(cls, clientId, activityId):
        """
        取得客户端某个活动的配置
        @return: {}, default: None
        """
        listConfig = cls.getActivitiesForClient(clientId)
        # 有效性校验
        if not listConfig or activityId not in listConfig:
            return None
        return cls.getActivityConfig(activityId)


class TYActivitySystemImpl(TYActivitySystem):
    def __init__(self, activityDao):
        self._dao = activityDao
        self._activities = {}

    def _getConfigForClient(self, actName, gameId, userId, clientId, activities, curstate):
        if ftlog.is_debug():
            ftlog.debug('TYActivitySystemImpl._getConfigForClient actName:', actName
                        , ' gameId:', gameId
                        , ' userId:', userId
                        , ' clientId:', clientId
                        , ' curstate:', curstate)

        actObj = self.getActivityObj(actName)
        if not actObj or not actObj.checkOperative():
            return
        
        condition = actObj._serverConf.get('condition')
        if condition is not None:
            condition = UserConditionRegister.decodeFromDict(condition)
            if not condition.check(HALL_GAMEID, userId, clientId, pktimestamp.getCurrentTimestamp()):
                return
        
        configForClient = actObj.getConfigForClient(gameId, userId, clientId)
        if configForClient:
            configForClient['state'] = curstate
            activities.append(configForClient)

    def getClientActivityConfig(self, clientId, activityId):
        return self._dao.getClientActivityConfig(clientId, activityId)

    def getActivityList(self, gameId, userId, clientId):
        if ftlog.is_debug():
            ftlog.debug('getActivityList.userId=', userId,
                        'gameId=', gameId,
                        'clientId=', clientId)

        # 活动详情list
        activityList = []
        # 活动名称list
        listConfig = self._dao.getActivitiesForClient(clientId)
        if not listConfig:
            return activityList
        else:
            for actName in listConfig:
                # 根据活动名称构造活动详情
                tempValue = self.getActState(userId, gameId, actName)
                ftlog.debug('getActivityList.userId=', userId,
                            'gameId=', gameId,
                            'actName=', actName,
                            'tempValue=', tempValue)
                self._getConfigForClient(actName, gameId, userId, clientId, activityList, tempValue)

        if ftlog.is_debug():
            ftlog.debug('TYActivitySystemImpl.getActivityList result=', activityList)

        return activityList

    def isSendModuleTip(self, gameId, userId, clientId):
        if clientId and gameId and userId:
            _, clientVer, _ = strutil.parseClientId(clientId)
            if clientVer >= 3.9:
                listConfig = self._dao.getActivitiesForClient(clientId)
                gId = strutil.getGameIdFromHallClientId(clientId)
                if listConfig:
                    for actName in listConfig:
                        self.getActState(userId, gId, actName)

    def getActState(self, userId, gameId, actName):
        tempValue = sdata.getStateAttrInt(userId, 9999, actName)
        if not tempValue:
            from poker.entity.events.tyevent import ModuleTipEvent
            tip = ModuleTipEvent(userId, gameId, 'activity', 1)
            pkeventbus.globalEventBus.publishEvent(tip)
        return tempValue

    def generateOrGetActivityObject(self, config):
        return self.getActivityObj(config['id'])

    def getActivityObj(self, actId):
        return self._activities.get(actId)

    def handleActivityRequest(self, userId, gameId, clientId, msg):
        '''
        处理活动请求
        '''
        activityId = msg.getParam("activityId")
        if not activityId:
            return {"info": "activity does not exist！"}
        actObj = self.getActivityObj(activityId)
        if not actObj:
            return {"info": "activity does not exist！"}
        if not actObj.checkOperative():
            return {"info": "activity expired！"}
        return actObj.handleRequest(msg)

    def reloadConf(self):
        confids = set(self._dao.activitiesConf.iterkeys())
        objids = set(self._activities.iterkeys())
        reloadids = confids & objids
        for actid in reloadids:  # 已有的对象
            config = self._dao.getActivityConfig(actid)
            if not config:
                continue
            actobj = self.getActivityObj(actid)
            actobj.reload(config)

        for actid in (objids - reloadids):  # 废弃对象
            actobj = self.getActivityObj(actid)
            actobj.finalize()

        for actid in (confids - reloadids):  # 新增的对象
            config = self._dao.getActivityConfig(actid)
            if not config:
                continue
            activityClass = TYActivityRegister.findClass(config["typeid"])
            if not activityClass:
                continue
            serverConf = config.pop("server_config")
            clientConf = config
            actobj = activityClass(self._dao, clientConf, serverConf)
            self._activities[actid] = actobj


def _registerClasses():
    TYActivityRegister.registerClass(TYActivityJumpToWelfare.TYPE_ID, TYActivityJumpToWelfare)
    TYActivityRegister.registerClass(TYActivityPlayGamePresentGift.TYPE_ID, TYActivityPlayGamePresentGift)
    TYActivityRegister.registerClass(TYActivityExchangeCode.TYPE_ID, TYActivityExchangeCode)
    TYActivityRegister.registerClass(TYActivityRaffle.TYPE_ID, TYActivityRaffle)
    TYActivityRegister.registerClass(TYActivityFirstCharge.TYPE_ID, TYActivityFirstCharge)
    TYActivityRegister.registerClass(TYActivityNoticeImg.TYPE_ID, TYActivityNoticeImg)
    TYActivityRegister.registerClass(TYActivityVipMatch.TYPE_ID, TYActivityVipMatch)
    TYActivityRegister.registerClass(TYActivityDdzMatch.TYPE_ID, TYActivityDdzMatch)
    TYActivityRegister.registerClass(TYActivityFanfanle.TYPE_ID, TYActivityFanfanle)
    TYActivityRegister.registerClass(TYActivitySale.TYPE_ID, TYActivitySale)
    TYActivityRegister.registerClass(TYActivityMatchQuiz.TYPE_ID, TYActivityMatchQuiz)
    from hall.entity.hallactivity.activity_share_click import TYActShareClick
    TYActivityRegister.registerClass(TYActShareClick.TYPE_ID, TYActShareClick)
    from hall.entity.hallactivity.activity_credit_exchange import TYActCreditExchange
    TYActivityRegister.registerClass(TYActCreditExchange.TYPE_ID, TYActCreditExchange)
    from hall.entity.hallactivity.activity_newfriend_invite import TYActNewFriendInvite
    TYActivityRegister.registerClass(TYActNewFriendInvite.TYPE_ID, TYActNewFriendInvite)
    from hall.entity.hallactivity.activity_item_exchange import TYActItemExchange
    TYActivityRegister.registerClass(TYActItemExchange.TYPE_ID, TYActItemExchange)

activitySystem = TYActivitySystem()
_inited = False
ACTIVITY_KEY = 'activity:{}:{}:{}'


def _reloadConf():
    conf = hallconf.getActivityConf()
    # 活动
    TYActivityDaoImpl.activitiesConf = conf.get("activities", {})
    if ftlog.is_debug():
        ftlog.debug("activity system reloadconf activitiesConf:", TYActivityDaoImpl.activitiesConf)

    # 活动配置模板
    TYActivityDaoImpl.templatesConf = conf.get("templates", {})
    if ftlog.is_debug():
        ftlog.debug("activity system reloadconf templatesConf:", TYActivityDaoImpl.templatesConf)

    # 活动模板类配置
    TYActivityDaoImpl.modulesConf = conf.get("modules", {})
    if ftlog.is_debug():
        ftlog.debug("activity system reloadconf modulesConf:", TYActivityDaoImpl.modulesConf)


def _onConfChanged(event):
    global _inited
    if _inited and event.isModuleChanged('activity'):
        ftlog.debug('hallactivity._onConfChanged')
        if _inited:
            _reloadConf()
            activitySystem.reloadConf()


def _initialize():
    ftlog.debug('activity initialize begin')
    global activitySystem
    global _inited
    if not _inited:
        _inited = True
        _registerClasses()
        activitySystem = TYActivitySystemImpl(TYActivityDaoImpl())
        _reloadConf()
        pkeventbus.globalEventBus.subscribe(EventConfigure, _onConfChanged)
        TGHall.getEventBus().subscribe(OnLineGameChangedEvent, handleActivityStateChangedEvent)
    ftlog.debug('activity initialize end')


def initAfter():
    # 需要等所有插件的活动类注册完毕
    activitySystem.reloadConf()


def handleActivityStateChangedEvent(evt):
    '''
    统一处理活动状态
    '''
    userId = evt.userId
    gameId = evt.gameId
    clientId = evt.clientId
    activitySystem.isSendModuleTip(gameId, userId, clientId)


def changeActStateForUser(userId, gameId, clientId, actList):
    if not actList:
        return

    listConfig = activitySystem._dao.getActivitiesForClient(clientId)
    if not listConfig:
        return

    all_read = True
    for actName in actList:
        if actName in listConfig:
            sdata.setStateAttr(userId, 9999, actName, 1)
        elif all_read:
            all_read = sdata.getStateAttr(userId, 9999, actName)
    if all_read:
        module_info = hallmoduletip.cancelModulesTip(userId, ['activity'], gameId)
        mo = ModuletipTcpHandlerHelp.buildInfo('update', module_info)
        router.sendToUser(mo, userId)
