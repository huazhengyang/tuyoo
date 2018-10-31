# -*- coding=utf-8 -*-
'''
Created on 2016年12月1日

一个简单的邀请有礼模块
邀请功能在内推广模块上做了一定的简化
1）配置基于主次渠道
2）设计上，不防刷，只要用户的游戏行为符合条件即可领取
3）不要求绑定手机号
4）界面也相对简单
5）奖励不是大厅统一发，奖励配置设置在游戏中

@author: zhaol
'''

import json
from sre_compile import isstring
import freetime.util.log as ftlog
from poker.entity.biz.content import TYContentItem
from poker.entity.biz.exceptions import TYBizException, TYBizBadDataException, \
    TYBizConfException
from poker.entity.dao import userdata, gamedata
from poker.entity.events.tyevent import EventConfigure
import poker.entity.events.tyeventbus as pkeventbus
from hall.entity.hallconf import HALL_GAMEID
import poker.util.timestamp as pktimestamp
from hall.entity import hallconf

MAX_INVITEE = 30

class Invitation(object):
    '''
    邀请
    '''
    # 初始条件，未领取奖励
    STATE_NORMAL = 0
    # 可以领取奖励
    STATE_CAN_GET_REWARD = 1
    # 已领取奖励
    STATE_REWARDED = 2
    
    def __init__(self, userId, index, inviterState = STATE_NORMAL):
        # 用户ID
        self.__userId = userId
        # 排序位置
        self.__index = index
        # 推荐人是否领奖状态(根据被推荐人的状态决定)
        self.__inviterState = inviterState
        
    @property
    def userId(self):
        return self.__userId
    
    @property
    def index(self):
        return self.__index
    
    @property
    def inviterState(self):
        return self.__inviterState
    
    @inviterState.setter
    def inviterState(self, value):
        assert(isinstance(value, int))
        self.__inviterState = value
    
    def getInviterState(self, userId, clientId):
        if self.__inviterState == self.STATE_NORMAL:
            return self.STATE_CAN_GET_REWARD
        return self.__inviterState

class NeituiguangSimpleStatus(object):
    '''
    简单邀请关系，添加有效期，有效期1天
    '''
    
    INVITER = 'inviter'
    INVITEES = 'invitees'
    REWARD_STATE = 'rewardState'
    TIMESTAMP = 'timestamp'
    
    def __init__(self, userId):
        self.__userId = userId
        # 
        self.__timestamp = pktimestamp.getCurrentDayStartTimestampByTimeZone()
        # 推荐人，上线
        self.__inviter = 0
        # 下线集合，被推荐人map，key=userId, value=InvitationUser
        self.__inviteeMap = {}
        # 绑定上线奖励的状态
        self.__rewardState = Invitation.STATE_NORMAL
        
    @property
    def userId(self):
        return self.__userId
    
    def setUserId(self, userId):
        self.__userId = userId
    
    @property
    def timestamp(self):
        return self.__timestamp
    
    def setTimesTamp(self, timestamp):
        self.__timestamp = timestamp
    
    @property
    def inviter(self):
        return self.__inviter
    
    def setInviter(self, inviter):
        '''
        设置邀请者
        '''
        self.__inviter = inviter
    
    @property
    def inviteeCount(self):
        return len(self.__inviteeMap)
    
    @property
    def inviteeMap(self):
        return self.__inviteeMap
    
    def findInvitee(self, userId):
        return self.__inviteeMap.get(userId, None)
    
    @property
    def rewardState(self):
        return self.__rewardState
        
    def getRewardState(self, userId, gameId, clientId):
        """返回是否可领奖的状态"""
        if (self.__rewardState == Invitation.STATE_NORMAL):
            return Invitation.STATE_CAN_GET_REWARD
        return self.rewardState
    
    def setRewardState(self, state):
        self.__rewardState = state
    
    def addInvitee(self, userId, inviteeState):
        invitee = Invitation(userId, len(self.__inviteeMap), inviteeState)
        self.__inviteeMap[userId] = invitee
    
    def decodeFromDict(self, d):
        '''
        从数据恢复邀请状态
        '''
        timestamp = d.get(self.TIMESTAMP, 0)
        if timestamp != pktimestamp.getCurrentDayStartTimestampByTimeZone():
            return self
        
        self.setInviter(d.get(self.INVITER, 0))
        inviteeList = d.get(self.INVITEES, [])
        if not isinstance(inviteeList, list):
            raise TYBizBadDataException('InviteStatus.invitees must be list')
        for i, invitee in enumerate(inviteeList):
            invitation = Invitation(invitee['uid'], i, invitee['st'])
            self.__inviteeMap[invitation.userId] = invitation
        rewardState = d.get(self.REWARD_STATE, Invitation.STATE_NORMAL)
        self.__rewardState = rewardState
        return self
    
    def encodeToDict(self, d):
        '''
        编码保存
        '''
        d[self.TIMESTAMP] = self.timestamp
        d[self.INVITER] = self.inviter
        if self.__inviteeMap:
            sl = sorted(self.__inviteeMap.values(), key=lambda invitee:invitee.index)
            d[self.INVITEES] = [{'uid':invitee.userId, 'st':invitee.inviterState} for invitee in sl]
        d[self.REWARD_STATE] = self.__rewardState
        return d
    
class InviteException(TYBizException):
    def __init__(self, ec, message):
        super(InviteException, self).__init__(ec, message)
        
class BadStateException(InviteException):
    def __init__(self, message):
        super(BadStateException, self).__init__(1, message)
        
class BadInviterException(InviteException):
    def __init__(self, message):
        super(BadInviterException, self).__init__(2, message)
        
class AlreadyInviteException(InviteException):
    def __init__(self):
        super(AlreadyInviteException, self).__init__(3, '已经推荐了该用户')
        
def getRedisKey(userId):
    '''
    获取存储的REDISKEY
    '''
    return 'simpleInvite:%d:%s' % (HALL_GAMEID, userId)
        
def loadStatus(userId):
    '''
    加载用户推广状态
    麻将先于大厅做过邀请有礼，从麻将merge数据
    '''
    d = None
    status = None
    try:
        # 优先迁移跑胡子的配置
        ftlog.debug('hall_simple_invite.loadStatus...')
        dStr = gamedata.getGameAttr(userId, HALL_GAMEID, 'simple_invite')
        if dStr:
            d = json.loads(dStr)
            status = NeituiguangSimpleStatus(userId).decodeFromDict(d)
    except:
        ftlog.error('invite.loadStatus userId=', userId, 'd=', d)
        
    if not status:
        status = NeituiguangSimpleStatus(userId)
        
    return status

def saveStatus(status):
    '''
    保存数据
    '''
    d = status.encodeToDict({})
    jstr = json.dumps(d)
    gamedata.setGameAttr(status.userId, HALL_GAMEID, 'simple_invite', jstr)
        
def ensureCanAddInviter(status, inviter):
    '''
    检查用户是否可以成为被推荐人
    '''
    if not userdata.checkUserData(inviter):
        raise BadInviterException('推荐人不存在')
    
    if status.inviter:
        raise BadStateException('已经填写了推荐人')
    
    if status.userId == inviter:
        raise BadInviterException('不能推荐自己')
    
    return True
    
def ensureCanBeInviter(status, invitee):
    if not userdata.checkUserData(invitee):
        raise BadInviterException('您的账号信息有误')
    
    if status.userId == invitee:
        raise BadInviterException('不能推荐自己')
    
    if status.findInvitee(invitee):
        raise BadInviterException('已推荐此用户')
    
    if status.inviteeCount + 1 > MAX_INVITEE:
        ftlog.info('invite.addInvitee overCountLimit userId=', status.userId,
                   'invitee=', invitee,
                   'inviteeCount=', status.inviteeCount,
                   'MAX_INVITEE=', MAX_INVITEE)
        raise BadInviterException('推荐用户达到上限')

def bindSimpleInviteRelationShip(inviter, invitee):
    '''
    设置invitee的inviter
    
    @param inviter: 上线
    @param invitee: 下线
    @return: status
    '''
    inviteeStatus = loadStatus(invitee)
    inviterStatus = loadStatus(inviter)
    
    ensureCanAddInviter(inviteeStatus, inviter)
    ensureCanBeInviter(inviterStatus, invitee)
    
    inviteeStatus.setInviter(inviter)
    saveStatus(inviteeStatus)
    
    inviterStatus.addInvitee(invitee, inviteeStatus.rewardState)
    saveStatus(inviterStatus)
    
class InviteConf(object):
    def __init__(self):
        self.inviteRewardItem = None # 每个人的奖励
        self.inviteRewardDesc = ''   # 每个人的奖励描述
        self.name = None
        self.inviteRewardsByIndex = []
        self.inviteRewardsDescByIndex = []
    
    def decodeFromDict(self, d):
        self.name = d.get('name', '')
        if not isstring(self.name):
            self.name = ''
        
        inviteRewardItem = d.get('inviteRewardItem', None)
        if inviteRewardItem:
            self.inviteRewardItem = TYContentItem.decodeFromDict(inviteRewardItem)
            self.inviteRewardDesc = inviteRewardItem.get('desc', '')
            
        rewardsByIndex = d.get('rewardsByIndex', [])
        if rewardsByIndex:
            for rIndexConfig in rewardsByIndex:
                rIndex = TYContentItem.decodeFromDict(rIndexConfig)
                self.inviteRewardsByIndex.append(rIndex) 
                self.inviteRewardsDescByIndex.append(rIndexConfig.get('desc', ''))
        
        return self
    
_inited = False
_conf = None

def _reloadConf():
    global _conf
    confMap = {}
    confs = hallconf.getAllTcDatas('simple_invite')
    ftlog.debug('hall_simple_invite confs:', confs)
    for templateDict in confs.get('templates'):
        template = InviteConf().decodeFromDict(templateDict)
        if template.name in confMap:
            raise TYBizConfException(templateDict, 'Duplicate simple_invite %s' % (template.name))
        confMap[template.name] = template
    _conf = confMap
    ftlog.info('hall_simple_invite._reloadConf conf=', _conf)
    
def _onConfChanged(event):
    if _inited and event.isModuleChanged(['simple_invite']):
        ftlog.info('hall_simple_invite._onConfChanged')
        _reloadConf() 

def initialize():
    ftlog.info('hall_simple_invite initialize begin')
    global _inited
    if not _inited:
        _inited = True
        _reloadConf()
        pkeventbus.globalEventBus.subscribe(EventConfigure, _onConfChanged)
    ftlog.info('hall_simple_invite initialize end')
    
def getSimpleInviteConf(userId, gameId, clientId):
    vcTemp = hallconf.getVcTemplateConf(clientId, 'simple_invite')
    if not vcTemp:
        ftlog.error('hall_simple_invite.getSimpleInviteConf has no template for clientId:', clientId, ' Please check...')
        
    ftlog.debug('hall_simple_invite getSimpleInviteConf:', vcTemp)
    return _conf.get(vcTemp, None)

def getSimpleInviteRewardsConf(userId, gameId, clientId):
    '''
    获取简单邀请的奖励配置
    '''
    rewards = {}
    conf = getSimpleInviteConf(userId, gameId, clientId)
    if not conf:
        return rewards
    
    if conf.inviteRewardsDescByIndex:
        rewards['rewardsByIndex'] = conf.inviteRewardsDescByIndex
        
    if conf.inviteRewardDesc:
        rewardsByUnit = {}
        rewardsByUnit['desc'] = conf.inviteRewardDesc
        rewardsByUnit['max'] = MAX_INVITEE
        rewards['rewardsByUnit'] = rewardsByUnit
    
    return rewards

def getSimpleInviteRewardByIndex(userId, gameId, index, clientId):
    '''
    获取简单邀请的奖励配置
    '''
    conf = getSimpleInviteConf(userId, gameId, clientId)
    if index > MAX_INVITEE:
        return None
    
    if conf.inviteRewardItem:
        return conf.inviteRewardItem
    
    if conf.inviteRewardsByIndex:
        if index >= len(conf.inviteRewardsByIndex):
            return None
        
        return conf.inviteRewardsByIndex[index]
    
def getSimpleInviteRewardDescByIndex(userId, gameId, index, clientId):
    '''
    获取简单邀请的奖励配置描述
    '''
    conf = getSimpleInviteConf(userId, gameId, clientId)
    if index > MAX_INVITEE:
        return None
    
    if conf.inviteRewardDesc:
        return conf.inviteRewardDesc
    
    if conf.inviteRewardsDescByIndex:
        if index >= len(conf.inviteRewardsDescByIndex):
            return None
        
        return conf.inviteRewardsDescByIndex[index]
    
