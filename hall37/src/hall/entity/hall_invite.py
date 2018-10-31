# -*- coding:utf-8 -*-
'''
Created on 2017年12月14日

@author: zhaojiangang
'''
import re

import freetime.util.log as ftlog
from hall.entity import datachangenotify, hallitem, hall_red_packet_task, \
    hall_red_packet_const
from hall.entity.hallconf import HALL_GAMEID
from hall.entity.hallevent import UserRedPacketTaskRewardEvent, \
    UserReceivedCouponEvent, UserReceivedInviteeRewardEvent
from hall.entity.todotask import TodoTaskRegister
from hall.game import TGHall
from poker.entity.biz.content import TYContentRegister
from poker.entity.biz.exceptions import TYBizConfException, TYBizException
from poker.entity.biz.item.item import TYAssetUtils
from poker.entity.configure import configure
from poker.entity.dao import userchip, daobase, userdata, sessiondata
from poker.entity.dao.userchip import ChipNotEnoughOpMode
from poker.entity.events.tyevent import EventConfigure, UserEvent, \
    EventUserLogin
import poker.entity.events.tyeventbus as pkeventbus
from poker.util import strutil
import poker.util.timestamp as pktimestamp
from hall.entity.hallusercond import UserConditionNewUser
from poker.entity.biz import bireport


MAX_INVITEE = 10


class UserBindInviterEvent(UserEvent):
    def __init__(self, userId, gameId, inviter, bindPoint):
        super(UserBindInviterEvent, self).__init__(userId, gameId)
        self.inviter = inviter
        self.bindPoint = bindPoint


class Invitee(object):
    def __init__(self, inviterStatus, userId=None, gotten=0, received=0, lastUpdateTime=0):
        # 被邀请人用户ID
        self.userId = userId
        # 得到未领取的奖励
        self.gotten = gotten
        # 已领取的总奖励
        self.received = received
        # 邀请者状态
        self.inviterStatus = inviterStatus
        # 最后更新时间
        self.lastUpdateTime = 0
        # 用户信息
        self.userAttrs = {}
    
    def toDict(self):
        return {
            'userId':self.userId,
            'gotten':self.gotten,
            'received':self.received,
            'lut':self.lastUpdateTime,
            'userAttrs':self.userAttrs
        }
        
    def fromDict(self, d):
        self.userId = d['userId']
        self.gotten = d.get('gotten', 0)
        self.received = d.get('received', 0)
        self.lastUpdateTime = d.get('lastUpdateTime', 0)
        self.userAttrs = d.get('userAttrs')
        return self


class UserInviteStauts(object):
    '''
    用户邀请信息
    '''
    def __init__(self, userId):
        # 用户ID
        self.userId = userId
        # 该用户的邀请人
        self.inviter = -1
        # 被邀请人map<userId, Invitee>
        self.inviteeMap = {}
    
    def fromDict(self, d):
        self.inviter = d['inviter']
        for inviteeD in d.get('invitees', []):
            invitee = Invitee(self).fromDict(inviteeD)
            self.inviteeMap[invitee.userId] = invitee
        return self
    
    def toDict(self):
        return {
            'inviter':self.inviter,
            'invitees':[invitee.toDict() for invitee in self.inviteeMap.values()]
        }
    
    def findInvitee(self, userId):
        return self.inviteeMap.get(userId)
    
    def addInvitee(self, userId, timestamp=None):
        '''
        添加一个被邀请者
        '''
        assert(not self.findInvitee(userId))
        timestamp = timestamp or pktimestamp.getCurrentTimestamp()
        invitee = Invitee(self, userId, 0, 0, timestamp)
        self.inviteeMap[userId] = invitee
        return invitee

    def addReward(self, invitee, count):
        assert(count > 0)
        assert(invitee.inviterStatus == self)
        invitee.gotten += count
    
    def receiveReward(self, invitee):
        gotten = invitee.gotten
        if gotten > 0:
            invitee.gotten = 0
            invitee.received += gotten
        return gotten
    

def loadUserInviteStatus(userId):
    jstr = daobase.executeUserCmd(userId, 'hget', 'invite:9999:%s' % (userId), 'status')
    if ftlog.is_debug():
        ftlog.debug('hall_invite.loadUserInviteStatus',
                    'userId=', userId,
                    'jstr=', jstr)
    if jstr:
        try:
            d = strutil.loads(jstr)
            return UserInviteStauts(userId).fromDict(d)
        except:
            ftlog.error('hall_invite.loadUserInviteStatus',
                        'userId=', userId)
    return UserInviteStauts(userId)


def saveUserInviteStatus(status):
    jstr = strutil.dumps(status.toDict())
    daobase.executeUserCmd(status.userId, 'hset', 'invite:9999:%s' % (status.userId), 'status', jstr)
    
    if ftlog.is_debug():
        ftlog.debug('hall_invite.saveUserInviteStatus',
                    'userId=', status.userId,
                    'jstr=', jstr)


def _sendReward(userId, invitee, count):
    userchip.incrCoupon(userId, HALL_GAMEID, count,
                        ChipNotEnoughOpMode.NOOP,
                        'HALL_INVITEE_TASK_REWARD',
                        invitee,
                        None)
    datachangenotify.sendDataChangeNotify(HALL_GAMEID, userId, 'coupon')
    
    ftlog.info('SendInviteeTaskReward',
               'userId=', userId,
               'invitee=', invitee,
               'count=', count)


def receiveInviteeReward(status, inviteeUserId, timestamp=None):
    invitee = status.findInvitee(inviteeUserId)
    if invitee:
        timestamp = timestamp or pktimestamp.getCurrentTimestamp()
        received = status.receiveReward(invitee)
        status.lastUpdateTime = timestamp
        saveUserInviteStatus(status)
        _sendReward(status.userId, inviteeUserId, received)
        
        TGHall.getEventBus().publishEvent(UserReceivedInviteeRewardEvent(HALL_GAMEID, status.userId, inviteeUserId, received))
        TGHall.getEventBus().publishEvent(UserReceivedCouponEvent(HALL_GAMEID, status.userId, received, hall_red_packet_const.RP_SOURCE_RP_INVITEE))
        
        ftlog.info('hall_invite.receiveInviteeReward',
                   'userId=', status.userId,
                   'invitee=', inviteeUserId,
                   'received=', received,
                   'timestamp=', timestamp)
        return received
    return 0


def _updateUserAttrs(invitee):
    name, purl = userdata.getAttrs(invitee.userId, ['name', 'purl'])
    name = str(name) if name else ''
    purl = str(purl) if purl else ''
    invitee.userAttrs['name'] = name
    invitee.userAttrs['purl'] = purl


def sendInviteeReward(status, inviteeUserId, rewardCount, timestamp=None):
    invitee = status.findInvitee(inviteeUserId)
    if invitee and rewardCount > 0:
        timestamp = timestamp or pktimestamp.getCurrentTimestamp()
        status.addReward(invitee, rewardCount)
        # 更新invitee的用户属性
        _updateUserAttrs(invitee)
        invitee.lastUpdateTime = timestamp
        status.lastUpdateTime = timestamp
        saveUserInviteStatus(status)
    
        ftlog.info('hall_invite.sendInviteeReward',
                   'userId=', status.userId,
                   'invitee=', inviteeUserId,
                   'rewardCount=', rewardCount,
                   'timestamp=', timestamp)


def sendBindInviterReward(status):
    if _bindInviterReward:
        userAssets = hallitem.itemSystem.loadUserAssets(status.userId)
        assetList = userAssets.sendContent(HALL_GAMEID,
                                           _bindInviterReward,
                                           1,
                                           True,
                                           pktimestamp.getCurrentTimestamp(),
                                           'HALL_BIND_INVITER_REWARD',
                                           status.inviter)
        changedDataNames = TYAssetUtils.getChangeDataNames(assetList)
        datachangenotify.sendDataChangeNotify(HALL_GAMEID, status.userId, changedDataNames)
        ftlog.info('hall_invite.sendBindInviterReward',
                   'userId=', status.userId,
                   'rewards=', [(atup[0].kindId, atup[1]) for atup in assetList])
        return assetList
    return None
        

BIND_POINT_LOGIN = 1
BIND_POINT_REGISTER_LOGIN = 2
BIND_POINT_MANUAL = 3


channelUserIdSection = [900000000, 900500000]


def isChannelUserId(userId):
    return userId >= channelUserIdSection[0] and userId < channelUserIdSection[1]


def setInviter(status, inviter, bindPoint=BIND_POINT_MANUAL):
    '''
    为userId设置推荐人
    '''
    from hall.servers.util.rpc import hall_invite_remote
    
    if status.inviter >= 0:
        raise TYBizConfException(-1, '您已经设置了邀请人')

    if inviter <= 0:
        raise TYBizConfException(-1, '邀请人错误')
    
    if status.userId == inviter:
        raise TYBizConfException(-1, '自己不能邀请自己')
    
    invitee = status.findInvitee(inviter)
    if invitee:
        raise TYBizConfException(-1, '不能互相邀请')
    
    isBindChannel = isChannelUserId(inviter)
    
    if not isBindChannel:
        # 真实用户
        ec, info = hall_invite_remote.addInvitee(inviter, status.userId)
        if ec != 0:
            raise TYBizException(ec, info)
        status.inviter = inviter
    else:
        # 推广渠道推广的
        status.inviter = 0

    saveUserInviteStatus(status)
    
    # 发放绑定推荐人奖励
    sendBindInviterReward(status)
    
    # 如果是注册时不需要通知
    if bindPoint not in (BIND_POINT_LOGIN, BIND_POINT_REGISTER_LOGIN):
        datachangenotify.sendDataChangeNotify(HALL_GAMEID, inviter, 'udata')
    
    clientId = sessiondata.getClientId(status.userId)
    
    bireport.reportGameEvent('HALL_BIND_INVITER', status.userId, HALL_GAMEID,
                             0, 0, 0, 0, bindPoint, 0, [inviter], clientId)
    
    ftlog.info('Set inviter ok', status.userId, inviter, bindPoint, isBindChannel)
    
    TGHall.getEventBus().publishEvent(UserBindInviterEvent(status.userId, HALL_GAMEID, inviter, bindPoint))
    
    if not isBindChannel:
        isWXTaskFinished = hall_red_packet_task.isWXTaskFinished(status.userId)
        if ftlog.is_debug():
            ftlog.debug('hall_invite.setInviter',
                        'userId=', status.userId,
                        'inviter=', inviter,
                        'bindPoint=', bindPoint,
                        'isWXTaskFinished=', isWXTaskFinished)
        if isWXTaskFinished:
            taskKind = hall_red_packet_task.getFirstTask(status.userId, clientId, pktimestamp.getCurrentTimestamp())
            if taskKind and taskKind.inviterReward > 0:
                _asyncSendInviteeReward(status.inviter, status.userId, taskKind.inviterReward)

    
def addInvitee(status, invitee):
    '''
    为status添加下线
    '''
    if status.userId == invitee:
        raise TYBizException(-1, '自己不能邀请自己')
    
    if len(status.inviteeMap) >= MAX_INVITEE:
        raise TYBizException(-1, '他已邀请%s人，不能再邀请了' % (MAX_INVITEE))
    
    inviteeObj = status.addInvitee(invitee)
    _updateUserAttrs(inviteeObj)
    saveUserInviteStatus(status)
    
    ftlog.info('Add invitee ok', status.userId, invitee)


_inited = False
_bindInviterReward = None
_remindTodotask = None
_oldRemindTodotask = None

invitePattern = re.compile('#途游游戏#您的好友(\d+)为你准备了邀请好礼')


def getBindInviterReward():
    return _bindInviterReward


def getRemindTodotask(clientId):
    _, clientVer, _ = strutil.parseClientId(clientId)
    if clientVer >= 4.58:
        return _remindTodotask
    return _oldRemindTodotask


def _reloadConf():
    global _bindInviterReward
    global _remindTodotask
    global _oldRemindTodotask
    
    bindInviterReward = None
    inviteeBindWXRewardCount = 0
    remindTodotask = None
    oldRemindTodotask = None
    
    conf = configure.getGameJson(HALL_GAMEID, 'invite', {}, 0)
    if conf:
        bindInviterRewardD = conf.get('bindInviterReward')
        if bindInviterRewardD:
            bindInviterReward = TYContentRegister.decodeFromDict(bindInviterRewardD)
        
        inviteeBindWXRewardCount = conf.get('inviteeBindWXRewardCount', 0)
        if not isinstance(inviteeBindWXRewardCount, int) or inviteeBindWXRewardCount < 0:
            raise TYBizConfException(conf, 'inviteeBindWXRewardCount must be int >= 0')

        remindTodotask = conf.get('remindTodotask')
        if remindTodotask:
            remindTodotask = TodoTaskRegister.decodeFromDict(remindTodotask)
            
        oldRemindTodotask = conf.get('oldRemindTodotask')
        if oldRemindTodotask:
            oldRemindTodotask = TodoTaskRegister.decodeFromDict(oldRemindTodotask)
     
    _bindInviterReward = bindInviterReward
    _remindTodotask = remindTodotask
    _oldRemindTodotask = oldRemindTodotask
    
    ftlog.info('hall_invite._reloadConf ok',
               'bindInviterReward=', [item.toDict() for item in _bindInviterReward.getItems()] if _bindInviterReward else None,
               'remindTodotask=', _remindTodotask.TYPE_ID if _remindTodotask else None,
               'oldRemindTodotask=', _oldRemindTodotask.TYPE_ID if _oldRemindTodotask else None)


def _onConfChanged(event):
    if _inited and event.isChanged('game:9999:invite:0'):
        _reloadConf()


def _onUserLogin(event):
    if not _inited:
        return
    
    timestamp = pktimestamp.getCurrentTimestamp()
    status = loadUserInviteStatus(event.userId)
    isNewUser = UserConditionNewUser().check(HALL_GAMEID, event.userId, event.clientId, timestamp)
    
    if ftlog.is_debug():
        ftlog.debug('hall_invite._onUserLogin',
                    'inited=', _inited,
                    'userId=', event.userId,
                    'clipboardContent=', event.clipboard.content if event and event.clipboard else None,
                    'isNewUser=', isNewUser,
                    'inviter=', status.inviter)

    if not isNewUser:
        # 老用户邀请人设置为0
        if status.inviter < 0:
            status.inviter = 0
            ftlog.info('Set inviter to system',
                       'userId=', event.userId)
            saveUserInviteStatus(status)
    else:
        if event.clipboard and event.clipboard.cmd == '邀请':
            try:
                inviter = int(event.clipboard.urlParams.get('uid', 0))
                if inviter > 0:
                    setInviter(status, int(inviter), BIND_POINT_REGISTER_LOGIN if not event.isCreate else BIND_POINT_LOGIN)
            except ValueError:
                pass
            except TYBizException, e:
                ftlog.warn('hall_invite._onUserLogin',
                           'userId=', event.userId,
                           'clipboardContent=', event.clipboard.content,
                           'ec=', e.errorCode,
                           'info=', e.message)


def _asyncSendInviteeReward(userId, invitee, rewardCount):
    if ftlog.is_debug():
        ftlog.debug('hall_invite._asyncSendInviteeReward',
                    'userId=', userId,
                    'invitee=', invitee,
                    'rewardCount=', rewardCount)
    try:
        from hall.servers.util.rpc import hall_invite_remote
        hall_invite_remote.sendInviteeReward(userId, invitee, rewardCount)
    except:
        ftlog.error('hall_invite._asyncSendInviteeReward',
                    'userId=', userId,
                    'invitee=', invitee,
                    'rewardCount=', rewardCount)


def _onUserRedPacketTaskReward(event):
    if ftlog.is_debug():
        ftlog.debug('hall_invite._onUserRedPacketTaskReward',
                    'userId=', event.userId,
                    'taskKindId=', event.taskKind.kindId)
    if event.taskKind.inviterReward:
        status = loadUserInviteStatus(event.userId)
        if status.inviter > 0:
            _asyncSendInviteeReward(status.inviter, event.userId, event.taskKind.inviterReward)


def _initialize():
    global _inited
    if not _inited:
        _inited = True
        _reloadConf()
        pkeventbus.globalEventBus.subscribe(EventConfigure, _onConfChanged)
        TGHall.getEventBus().subscribe(EventUserLogin, _onUserLogin)
        TGHall.getEventBus().subscribe(UserRedPacketTaskRewardEvent, _onUserRedPacketTaskReward)


