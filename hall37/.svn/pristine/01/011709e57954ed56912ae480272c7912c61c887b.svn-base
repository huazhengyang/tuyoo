# -*- coding:utf-8 -*-
'''
Created on 2015年12月9日

@author: zhaojiangang
'''
import json
from sre_compile import isstring

import freetime.util.log as ftlog
from hall.entity.hallconf import HALL_GAMEID
from hall.game import TGHall
from poker.entity.biz.content import TYContentItem
from poker.entity.biz.exceptions import TYBizException, TYBizBadDataException, \
    TYBizConfException
from poker.entity.configure import configure
from poker.entity.dao import gamedata, userdata
from poker.entity.events.tyevent import EventConfigure, UserEvent, \
    EventUserLogin
import poker.entity.events.tyeventbus as pkeventbus
import poker.util.timestamp as pktimestamp
from hall.entity import datachangenotify
from poker.entity.biz.item.item import TYAssetUtils


class Invitation(object):
    '''
    邀请
    '''
    STATE_NORMAL = 0
    STATE_ACCEPT = 1
    STATE_REWARD = 2

    def __init__(self, userId, index, state=STATE_NORMAL):
        # 用户ID
        self._userId = userId
        # 排序位置
        self._index = index
        # 是否接受了邀请，已绑定手机为准
        self._state = state
        
    @property
    def userId(self):
        return self._userId
    
    @property
    def index(self):
        return self._index
    
    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value

MAX_INVITEE = 500
NEW_USER_DAYS = 7


class NeituiguangStatus(object):
    def __init__(self, userId, timestamp):
        # 用户userId
        self._userId = userId
        # 当前时间
        self._timestamp = timestamp
        # userId的推荐人
        self._inviter = None
        # 被推荐人map，key=userId, value=InvitationUser
        self._inviteeMap = {}
        # 是否绑定了手机
        self._isBindMobile = False
        # 是否通知了inviter我接受了邀请
        self._isNotifyInviterMyAccepted = False
        # 用户注册时间
        self._registerTime = None
        
    @property
    def userId(self):
        return self._userId
    
    @property
    def inviter(self):
        return self._inviter
    
    @property
    def inviteeCount(self):
        return len(self._inviteeMap)
    
    @property
    def inviteeMap(self):
        return self._inviteeMap
    
    @property
    def isNewUser(self):
        registerDays = (pktimestamp.getDayStartTimestamp(self._timestamp)
                        - pktimestamp.getDayStartTimestamp(self._registerTime)) / 86044
        return registerDays <= NEW_USER_DAYS
    
    @property
    def isBindMobile(self):
        return self._isBindMobile
    
    @property
    def isNotifyInviterMyAccepted(self):
        return self._isNotifyInviterMyAccepted
    
    def findInvitee(self, userId):
        """查询是否含有此下线"""
        return self._inviteeMap.get(userId)
    
    def _setInviter(self, userId):
        assert(self._inviter is None)
        assert(userId != self.userId)
        self._inviter = Invitation(userId, 0)
        
    def _addInvitee(self, userId, accepted):
        assert(not self.findInvitee(userId))
        assert(userId != self.userId)
        state = Invitation.STATE_NORMAL if not accepted else Invitation.STATE_ACCEPT
        invitee = Invitation(userId, len(self._inviteeMap), state)
        self._inviteeMap[userId] = invitee
    
    def decodeFromDict(self, d):
        inviterUserId = d.get('inviter', -1)
        if not isinstance(inviterUserId, int):
            raise TYBizBadDataException('NeituiguangStatus.inviter must be int')
        if inviterUserId >= 0:
            self._inviter = Invitation(inviterUserId, 0)
        inviteeList = d.get('invitees', [])
        if not isinstance(inviteeList, list):
            raise TYBizBadDataException('NeituiguangStatus.invitees must be list')
        for i, invitee in enumerate(inviteeList):
            invitation = Invitation(invitee['uid'], i, invitee['st'])
            self._inviteeMap[invitation.userId] = invitation
        return self
    
    def encodeToDict(self, d):
        if self.inviter:
            d['inviter'] = self.inviter.userId
        if self._inviteeMap:
            sl = sorted(self._inviteeMap.values(), key=lambda invitee:invitee.index)
            d['invitees'] = [{'uid':invitee.userId, 'st':invitee.state} for invitee in sl]
        return d
    
    def encodeInvitee(self):
        inviteeArr = []
        if self._inviteeMap:
            sl = sorted(self._inviteeMap.values(), key=lambda invitee:invitee.index)
            inviteeArr = [{'uid': invitee.userId} for invitee in sl]
        return inviteeArr
    
class NeituiguangException(TYBizException):
    def __init__(self, ec, message):
        super(NeituiguangException, self).__init__(ec, message)
        
class BadStateException(NeituiguangException):
    def __init__(self, message):
        super(BadStateException, self).__init__(1, message)
        
class BadInviterException(NeituiguangException):
    def __init__(self, message):
        super(BadInviterException, self).__init__(2, message)
        
class AlreadyInviteException(NeituiguangException):
    def __init__(self):
        super(AlreadyInviteException, self).__init__(4, '已经推荐了该用户')
        
def loadStatus(userId, timestamp):
    '''
    加载用户推广状态
    '''
    d = status = None
    try:
        d = gamedata.getGameAttrJson(userId, HALL_GAMEID, 'neituiguang')
        if d:
            status = NeituiguangStatus(userId, timestamp).decodeFromDict(d)
    except:
        ftlog.error('neiguituan.loadStatus userId=', userId,
                    'd=', d)
    if not status:
        status = NeituiguangStatus(userId, timestamp)
    return _adjustStatus(status)

def _adjustStatus(status):
    try:
        bindMobile, createTimeStr = userdata.getAttrs(status.userId, ['bindMobile', 'createTime'])
        status._isBindMobile = True if bindMobile else False
        status._registerTime = pktimestamp.timestrToTimestamp(createTimeStr, '%Y-%m-%d %H:%M:%S.%f')
        if status.inviteeMap:
            sl = sorted(status.inviteeMap.values(), key=lambda invitee:invitee.index)
            removeList = sl[MAX_INVITEE:]
            for invitee in removeList:
                del status.inviteeMap[invitee.userId]
    except:
        ftlog.error('neituiguang._adjustStatus userId=', status.userId)
    return status

def _saveStatus(status):
    d = status.encodeToDict({})
    jstr = json.dumps(d)
    gamedata.setGameAttr(status.userId, HALL_GAMEID, 'neituiguang', jstr)

class NeituiguangAddInviteeEvent(UserEvent):
    def __init__(self, gameId, userId, inviteeUserId):
        super(NeituiguangAddInviteeEvent, self).__init__(userId, gameId)
        self.inviteeUserId = inviteeUserId
      
class NeituiguangSetInviterEvent(UserEvent):
    def __init__(self, gameId, userId, inviterUserId):
        super(NeituiguangSetInviterEvent, self).__init__(userId, gameId)
        self.inviterUserId = inviterUserId
        
def ensureCanBeInvitee(status, inviter):
    '''
    检查用户是否可以成为被推荐人
    '''
    if not status.isNewUser:
        raise BadStateException('老用户不能填写推荐人')
    if status.inviter:
        raise BadStateException('已经填写了推荐人')
    if status.userId == inviter:
        raise BadInviterException('不能推荐自己')
    
def ensureCanBeInviter(status, invitee):
    if status.userId == invitee:
        raise BadInviterException('不能推荐自己')
    
def setInviter(status, inviter):
    '''
    设置userId的推荐人
    @param userId: 被推荐人
    @param inviterUserId: 推荐人是谁
    @return: status
    '''
    # 确认能成为被推荐人
    ensureCanBeInvitee(status, inviter)
    
    status._setInviter(inviter)
    _saveStatus(status)
    
    # 设置好inviter后需要设置新手任务
    ftlog.info('neituiguang.setInviter userId=', status.userId,
               'inviter=', inviter)
    TGHall.getEventBus().publishEvent(NeituiguangSetInviterEvent(HALL_GAMEID, status.userId, inviter))

def addInvitee(status, invitee, accepted):
    '''
    给userId的推荐列表增加inviteeUserId
    @param userId: 给哪个用户增加
    @param inviteeUserId: 被推荐人
    @return: status
    '''
    # 确认可以成为推荐人
    ensureCanBeInviter(status, invitee)
    if status.inviteeCount + 1 > MAX_INVITEE:
        ftlog.info('neituiguang.addInvitee overCountLimit userId=', status.userId,
                   'invitee=', invitee,
                   'inviteeCount=', status.inviteeCount,
                   'MAX_INVITEE=', MAX_INVITEE)
        return
    # 添加被推荐人
    status._addInvitee(invitee, accepted)
    _saveStatus(status)
    ftlog.info('neituiguang.addInvitee userId=', status.userId,
               'invitee=', invitee,
               'accepted=', accepted)
    TGHall.getEventBus().publishEvent(NeituiguangAddInviteeEvent(HALL_GAMEID, status.userId, invitee))

def onNotifyInviterOk(status):
    if not status.isNotifyInviterMyAccepted:
        status._isNotifyInviterMyAccepted = True
        _saveStatus(status)
        ftlog.info('neituiguang.onNotifyInviterOk userId=', status.userId,
                   'inviter=', status.inviter.userId if status.inviter else -1)
        
def onInvitationAccepted(status, invitation):
    found = status.findInvitee(invitation.userId)
    assert(found == invitation)
    if invitation.state != Invitation.STATE_NORMAL:
        return False
    invitation._state = Invitation.STATE_ACCEPT
    _saveStatus(status)
    ftlog.info('neituiguang.accept userId=', status.userId,
               'invitee=', invitation.userId)

def getAllReward(status):
    from hall.entity import hallitem
    count = 0
    for invitation in status.inviteeMap.values():
        if invitation.state == Invitation.STATE_ACCEPT:
            invitation.state = Invitation.STATE_REWARD
            count += 1
    assetTupleList = []
    if count > 0:
        _saveStatus(status)
    
        timestamp = pktimestamp.getCurrentTimestamp()
        if _conf.prizeRewardItem:
            ftlog.info('neituiguang.getAllReward userId=', status.userId,
                       'assetKindId=', _conf.prizeRewardItem.assetKindId,
                       'assetCount=', _conf.prizeRewardItem.count,
                       'invitationCount=', count)
            assetTuple = hallitem.itemSystem.loadUserAssets(status.userId).addAsset(HALL_GAMEID,
                                                                                    _conf.prizeRewardItem.assetKindId,
                                                                                    _conf.prizeRewardItem.count,
                                                                                    timestamp, 'PROMOTE_REWARD', 0)
            assetTupleList.append(assetTuple)
            datachangenotify.sendDataChangeNotify(HALL_GAMEID, status.userId, TYAssetUtils.getChangeDataNames(assetTupleList))
    return count, assetTupleList

class NeituiguangConf(object):
    def __init__(self):
        self.prizeDetail = None
        self.prizeImgUrl = None
        self.prizeRewardItem = None
        self.prizeRewardDesc = None
        self.prizeNotGotRewardDesc = None
        self.prizeGotTotalRewardDesc = None
        self.prizeAvailableRewardDesc = None
        self.prizeRewardTips = None
        self.shareLoc = None
        self.taskDetail = None
        
        self.pleaseBindPhone = None
        self.defaultShareId = None
    
    def decodeFromDict(self, d):
        self.prizeDetail = d.get('prizeDetail', '')
        if not isstring(self.prizeDetail):
            raise TYBizConfException(d, 'NeituiguangConf.prizeDetail must be string')
        self.prizeImgUrl = d.get('prizeImgUrl', '')
        if not isstring(self.prizeImgUrl):
            raise TYBizConfException(d, 'NeituiguangConf.prizeImgUrl must be string')
        self.prizeRewardDesc = d.get('prizeRewardDesc', '')
        if not isstring(self.prizeRewardDesc):
            raise TYBizConfException(d, 'NeituiguangConf.prizeRewardDesc must be string')
        self.prizeNotGotRewardDesc = d.get('prizeNotGotRewardDesc', '')
        if not isstring(self.prizeNotGotRewardDesc):
            raise TYBizConfException(d, 'NeituiguangConf.prizeNotGotRewardDesc must be string')
        self.prizeGotTotalRewardDesc = d.get('prizeGotTotalRewardDesc', '')
        if not isstring(self.prizeGotTotalRewardDesc):
            raise TYBizConfException(d, 'NeituiguangConf.prizeGotTotalRewardDesc must be string')
        self.prizeAvailableRewardDesc = d.get('prizeAvailableRewardDesc', '')
        if not isstring(self.prizeAvailableRewardDesc):
            raise TYBizConfException(d, 'NeituiguangConf.prizeAvailableRewardDesc must be string')
        self.prizeRewardTips = d.get('prizeRewardTips', '')
        if not isstring(self.prizeRewardTips):
            raise TYBizConfException(d, 'NeituiguangConf.prizeRewardTips must be string')
        prizeRewardItem = d.get('prizeRewardItem', {})
        if not isinstance(prizeRewardItem, dict):
            raise TYBizConfException(d, 'NeituiguangConf.prizeRewardItem must be dict')
        if prizeRewardItem:
            self.prizeRewardItem = TYContentItem.decodeFromDict(prizeRewardItem)
        self.shareLoc = d.get('shareLoc', '')
        if not isstring(self.shareLoc):
            raise TYBizConfException(d, 'NeituiguangConf.shareLoc must be string')
        self.taskDetail = d.get('taskDetail', '')
        if not isstring(self.taskDetail):
            raise TYBizConfException(d, 'NeituiguangConf.taskDetail must be string')
        self.pleaseBindPhone = d.get('pleaseBindPhone', '')
        if not isstring(self.pleaseBindPhone):
            raise TYBizConfException(d, 'NeituiguangConf.pleaseBindPhone must be string')
        self.defaultShareId = d.get('defaultShareId')
        if self.defaultShareId is not None and not isinstance(self.defaultShareId, int):
            raise TYBizConfException(d, 'NeituiguangConf.defaultShareId must be int')
        return self
    
_inited = False
_conf = None

def _reloadConf():
    global _conf
    confDict = configure.getGameJson(HALL_GAMEID, 'neituiguang2', {}, configure.DEFAULT_CLIENT_ID)
    conf = NeituiguangConf().decodeFromDict(confDict)
    _conf = conf
    ftlog.debug('neiguituang._reloadConf conf=', confDict)
    
def _onConfChanged(event):
    if _inited and event.isChanged('game:9999:neituiguang2:0'):
        ftlog.debug('neituiguang._onConfChanged')
        _reloadConf()
        
def _onUserLogin(event):
    from hall.servers.util.rpc import neituiguang_remote
    status = loadStatus(event.userId, event.timestamp)
    if (status.isBindMobile
        and not status.isNotifyInviterMyAccepted
        and status.inviter
        and status.inviter.userId > 0):
        ftlog.debug('neiguiguang._onUserLogin notifyInvitationAccepted userId=', event.userId,
                   'inviter=', status.inviter.userId)
        neituiguang_remote.onInvitationAccepted(status.inviter.userId, status.userId) 

def _initialize():
    ftlog.debug('neituiguang initialize begin')
    global _inited
    if not _inited:
        _inited = True
        _reloadConf()
        pkeventbus.globalEventBus.subscribe(EventConfigure, _onConfChanged)
        TGHall.getEventBus().subscribe(EventUserLogin, _onUserLogin)
    ftlog.debug('neituiguang initialize end')
    
def getConf():
    return _conf
