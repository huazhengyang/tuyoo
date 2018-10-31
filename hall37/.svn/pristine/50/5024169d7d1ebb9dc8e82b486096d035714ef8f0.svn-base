# -*- coding:utf-8 -*-
'''
Created on 2018年1月9日

@author: zhaojiangang
'''
from datetime import datetime

import freetime.util.log as ftlog
from hall.entity import hallitem, datachangenotify, hall_red_packet_const
from hall.entity.hallconf import HALL_GAMEID
from hall.entity.hallevent import UserReceivedCouponEvent
from hall.entity.hallusercond import UserConditionRegister, UserCondition
from hall.entity.todotask import TodoTaskRegister
from poker.entity.biz.content import TYContentRegister
from poker.entity.biz.item.item import TYAssetUtils
from poker.entity.configure import configure
from poker.entity.dao import daobase
from poker.entity.events.tyevent import EventConfigure
import poker.entity.events.tyeventbus as pkeventbus
import poker.util.timestamp as pktimestamp


_inited = False
_conf = None


class RPMainConf(object):
    def __init__(self):
        self.startDT = None
        self.stopDT = None
        self.inviteTodotaskFac = None
        self.oldInviteTodotaskFac = None
        self.rewards = None


def getConf():
    return _conf


def hasReward(userId):
    return daobase.executeUserCmd(userId, 'hget', 'rpmain:%s:%s' % (HALL_GAMEID, userId), 'gainReward') is None


def sendReward(userId, clientId, timestamp):
    from hall.game import TGHall
    
    for cond, rewardContent in _conf.rewards:
        if cond and not cond.check(HALL_GAMEID, userId, clientId, timestamp):
            continue
        
        userAssets = hallitem.itemSystem.loadUserAssets(userId)
        assetList = userAssets.sendContent(HALL_GAMEID,
                                           rewardContent,
                                           1,
                                           True,
                                           timestamp,
                                           'HALL_RP_REWARD',
                                           0)
        ftlog.info('hall_red_packet_main.sendReward',
                   'userId=', userId,
                   'assets=', [(atup[0].kindId, atup[1]) for atup in assetList])
        changed = TYAssetUtils.getChangeDataNames(assetList)
        datachangenotify.sendDataChangeNotify(HALL_GAMEID, userId, changed)
        count = TYAssetUtils.getAssetCount(assetList, hallitem.ASSET_COUPON_KIND_ID)
        if count > 0:
            TGHall.getEventBus().publishEvent(UserReceivedCouponEvent(HALL_GAMEID,
                                                                      userId,
                                                                      count,
                                                                      hall_red_packet_const.RP_SOURCE_RP_MAIN))
        return assetList
    return None


def gainReward(userId, clientId, timestamp=None):
    timestamp = timestamp or pktimestamp.getCurrentTimestamp()
    ok = daobase.executeUserCmd(userId, 'hsetnx', 'rpmain:%s:%s' % (HALL_GAMEID, userId), 'gainReward', 1)
    if ftlog.is_debug():
        ftlog.debug('hall_red_packet_main.gainReward',
                    'userId=', userId,
                    'clientId=', clientId,
                    'timestamp=', timestamp,
                    'ok=', ok)
    if ok:
        return sendReward(userId, clientId, timestamp)
    return None


class UserConditionHasRedPacketReward(UserCondition):
    TYPE_ID = 'user.cond.hasRedPacketReward'

    def __init__(self):
        super(UserConditionHasRedPacketReward, self).__init__()

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        return hasReward(userId)

    def decodeFromDict(self, d):
        return self


def _reloadConf():
    global _conf
    newConf = RPMainConf()
    
    conf = configure.getGameJson(HALL_GAMEID, 'red_packet_main', {})
    startDT = conf.get('startTime')
    if startDT is not None:
        newConf.startDT = datetime.strptime(startDT, '%Y-%m-%d %H:%M:%S')
    stopDT = conf.get('stopTime')
    if stopDT is not None:
        newConf.stopDT = datetime.strptime(stopDT, '%Y-%m-%d %H:%M:%S')
    inviteTodotaskD = conf.get('inviteTodotask')
    if inviteTodotaskD is not None:
        newConf.inviteTodotaskFac = TodoTaskRegister.decodeFromDict(inviteTodotaskD)

    oldInviteTodotaskD = conf.get('oldInviteTodotask')
    if oldInviteTodotaskD:
        newConf.oldInviteTodotaskFac = TodoTaskRegister.decodeFromDict(oldInviteTodotaskD)

    newConf.rewards = []
    for reward in conf.get('rewards', []):
        cond = None
        content = None
        condD = reward.get('condition')
        if condD:
            cond = UserConditionRegister.decodeFromDict(condD)
        content = TYContentRegister.decodeFromDict(reward.get('content'))
        newConf.rewards.append((cond, content))
    
    _conf = newConf    
    
    ftlog.info('hall_red_packet_main._reloadConf ok',
               'startDT=', newConf.startDT,
               'stopDT=', newConf.stopDT,
               'inviteTodotaskFac=', newConf.inviteTodotaskFac,
               'oldInviteTodotaskFac=', newConf.oldInviteTodotaskFac)


def _registerClasses():
    UserConditionRegister.registerClass(UserConditionHasRedPacketReward.TYPE_ID, UserConditionHasRedPacketReward)


def _onConfChanged(event):
    if _inited and event.isChanged('game:9999:red_packet_main:0'):
        _reloadConf()


def _initialize():
    global _inited
    if not _inited:
        _inited = True
        _reloadConf()
        pkeventbus.globalEventBus.subscribe(EventConfigure, _onConfChanged)
        if ftlog.is_debug():
            ftlog.debug('hall_red_packet_main._initialized ok')


