# -*- coding:utf-8 -*-
'''
Created on 2018年10月29日

@author: wangyonghui
'''
from dizhu.entity import dizhu_util
from poker.entity.biz.confobj import TYConfableRegister
from poker.entity.biz.content import TYContentItem
from poker.entity.biz.exceptions import TYBizConfException
import freetime.util.log as ftlog


class RewardControlTypeRegister(TYConfableRegister):
    """ 奖励系统类型注册 """
    pass


class BaseRewardControlType(object):
    """ 发放奖励 cond 基类 """
    TYPE_ID = 'unknown'

    def decodeFromDict(self, d):
        raise NotImplemented()

    def toDict(self):
        raise NotImplemented()


class RewardControlTypeDirect(BaseRewardControlType):
    """ 直接发奖 """
    TYPE_ID = 'sendDirect'

    def decodeFromDict(self, d):
        return self

    def toDict(self):
        return {
            'typeId': self.TYPE_ID
        }


class RewardControlSendAsync(BaseRewardControlType):
    """ 异步发奖 """
    TYPE_ID = 'sendAsync'

    def __init__(self):
        self.expireSeconds = None

    def decodeFromDict(self, d):
        self.expireSeconds = d.get('expireSeconds')
        if not isinstance(self.expireSeconds, int) or self.expireSeconds < 0:
            raise TYBizConfException(d, 'RewardControlSendAsync.expireSeconds must be int')
        return self

    def toDict(self):
        return {
            'typeId': self.TYPE_ID,
            'expireSeconds': self.expireSeconds
        }


class RewardControlFixedPerson(BaseRewardControlType):
    """ 奖励达到配置人数解锁 """
    TYPE_ID = 'fixedPerson'

    def __init__(self):
        self.unlockSeconds = None
        self.count = None

    def decodeFromDict(self, d):
        self.unlockSeconds = d.get('unlockSeconds')
        if not isinstance(self.unlockSeconds, int) or self.unlockSeconds < 0:
            raise TYBizConfException(d, 'RewardControlFixedPerson.unlockSeconds must be int')

        self.count = d.get('count')
        if not isinstance(self.count, int) or self.count < 0:
            raise TYBizConfException(d, 'RewardControlFixedPerson.count must be int')
        return self

    def toDict(self):
        return {
            'typeId': self.TYPE_ID,
            'unlockSeconds': self.unlockSeconds,
            'count': self.count
        }


class RewardControlFixedHelp(BaseRewardControlType):
    """ 每一个好友助力获得固定奖励，达到奖励上限解锁， 倒计时到有几个助力发几份额外奖励 """
    TYPE_ID = 'fixedHelp'

    def __init__(self):
        self.unlockSeconds = None
        self.extraReward = None
        self.maxCount = None

    def decodeFromDict(self, d):
        self.unlockSeconds = d.get('unlockSeconds')
        if not isinstance(self.unlockSeconds, int) or self.unlockSeconds < 0:
            raise TYBizConfException(d, 'RewardControlFixedHelp.unlockSeconds must be int')

        self.extraReward = d.get('extraReward')
        if not isinstance(self.extraReward, dict):
            raise TYBizConfException(d, 'RewardControlFixedHelp.extraReward must be dict')
        try:
            TYContentItem.decodeList([self.extraReward])
        except Exception, e:
            raise TYBizConfException(d, 'RewardControlFixedHelp.extraReward Item error=%s' % e.message)

        self.maxCount = d.get('maxCount')
        if not isinstance(self.maxCount, int) or self.maxCount < 0:
            raise TYBizConfException(d, 'RewardControlFixedHelp.maxCount must be int')

        return self

    def toDict(self):
        return {
            'typeId': self.TYPE_ID,
            'extraReward': self.extraReward,
            'unlockSeconds': self.unlockSeconds,
            'maxCount': self.maxCount
        }


class RewardControlRandomHelp(BaseRewardControlType):
    """ 每一个好友助力获得固定奖励，达到奖励上限解锁， 倒计时到有几个助力发几份额外奖励 """
    TYPE_ID = 'randomHelp'

    def __init__(self):
        self.unlockSeconds = None
        self.extraRewardList = None  # [{"item": {"itemId": "user:coupon", "count": 1}, "weight": 10}}]
        self.maxCount = None

    def decodeFromDict(self, d):
        self.unlockSeconds = d.get('unlockSeconds')
        if not isinstance(self.unlockSeconds, int) or self.unlockSeconds < 0:
            raise TYBizConfException(d, 'RewardControlRandomHelp.unlockSeconds must be int')

        self.extraRewardList = d.get('extraRewardList')
        if not isinstance(self.extraRewardList, list):
            raise TYBizConfException(d, 'RewardControlRandomHelp.extraRewardList must be list')
        try:
            dizhu_util.getItemByWeight(self.extraRewardList)
        except Exception, e:
            raise TYBizConfException(d, 'RewardControlRandomHelp.extraRewardList Item error=%s' % e.message)

        self.maxCount = d.get('maxCount')
        if not isinstance(self.maxCount, int) or self.maxCount < 0:
            raise TYBizConfException(d, 'RewardControlRandomHelp.maxCount must be int')

        return self

    def toDict(self):
        return {
            'typeId': self.TYPE_ID,
            'extraRewardList': self.extraRewardList,
            'unlockSeconds': self.unlockSeconds,
            'maxCount': self.maxCount
        }


def _registerClasses():
    ftlog.debug('reward_control_type._registerClasses')
    RewardControlTypeRegister.registerClass(RewardControlTypeDirect.TYPE_ID, RewardControlTypeDirect)
    RewardControlTypeRegister.registerClass(RewardControlSendAsync.TYPE_ID, RewardControlSendAsync)
    RewardControlTypeRegister.registerClass(RewardControlFixedPerson.TYPE_ID, RewardControlFixedPerson)
    RewardControlTypeRegister.registerClass(RewardControlFixedHelp.TYPE_ID, RewardControlFixedHelp)
    RewardControlTypeRegister.registerClass(RewardControlRandomHelp.TYPE_ID, RewardControlRandomHelp)
