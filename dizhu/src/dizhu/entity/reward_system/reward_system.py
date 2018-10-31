# -*- coding:utf-8 -*-
'''
Created on 2018年10月29日

@author: wangyonghui
'''
import datetime

from dizhu.entity.reward_system.dao.reward_system_dao import RewardIdGenRedis
import poker.util.timestamp as pktimestamp
from dizhu.entity.reward_system.reward_control_type import RewardControlTypeRegister

REWARD_STATE_AS_LOCK = 1
REWARD_STATE_AS_UNLOCK = 2


class BaseRewardItemData(object):
    """ 奖励对象基类 """
    TYPE_ID = 'unknown'

    def __init__(self):
        self.rewardId = None
        self.rewardState = REWARD_STATE_AS_LOCK
        self.isShowForUser = False
        self.rewards = None
        self.rewardsControl = None
        self.unLockTimestamp = None

    def sendRewards(self):
        """ 发奖 """
        raise NotImplementedError

    def initRewards(self, rewards, rewardsControl):
        """ 初始化奖励: 负责生成 rewardId, 持久化 rewards, rewardsControl"""

    def processOtherLogin(self):
        """ 处理他人点击分享链接 """
        raise NotImplementedError

    def decodeFromDict(self):
        raise NotImplementedError

    def toDict(self):
        raise NotImplementedError


class RewardItemSendAsyncData(BaseRewardItemData):
    """ 异步发奖 """
    TYPE_ID = 'sendAsync'

    def __init__(self):
        super(RewardItemSendAsyncData, self).__init__()
        self.isShowForUser = False
        self.expireTimestamp = 0

    def sendRewards(self):
        """ 发奖 """
        pass

    def decodeFromDict(self):
        pass

    def toDict(self):
        pass


class UserRewardsTotalData(object):
    """ 用户所有奖励 """
    def __init__(self, userId):
        self.userId = userId
        self.rewardList = []

    def decodeFromDict(self):
        pass

    def toDict(self):
        pass

    def getRewardByRewardId(self, rewardId):
        pass


class RewardSystemHelper(object):
    """ 对外接口 """
    @classmethod
    def genRewardId(cls):
        """ 生成奖励唯一标志 """
        nowTimeStamp = pktimestamp.getCurrentTimestamp()
        intId = RewardIdGenRedis.genRewardId(nowTimeStamp)
        ret = datetime.datetime.fromtimestamp(nowTimeStamp).strftime('%Y%m%d') + str(intId)
        return ret

    @classmethod
    def sendInitRewards(cls, rewards, rewardsControl):
        """ 发奖入口函数，根据不同的 rewardsControl 采取不容发奖策略，例如直接发放或者持久化数据 """
        rewardId = cls.genRewardId()
        rewardObj = RewardControlTypeRegister.decodeFromDict(rewardsControl)
        rewardcls = None
        for r in ALL_REWARDS_DICT:
            if ALL_REWARDS_DICT[r].TYPE_ID == rewardObj.TYPE_ID:
                rewardcls = ALL_REWARDS_DICT[r]
                break
        if rewardcls:
            rewardcls().sendRewards()
            return rewardId

    @classmethod
    def sendUserRewardsByRewardId(cls, userId, reward):
        """ 根据 rewardId 获取相应的奖励 """
        pass

    @classmethod
    def getUserRewardsShowList(cls, userId, reward):
        """ 获取用户奖励展示列表 """
        pass


# 监听分享链接登录事件（带有 rewardId 的）


ALL_REWARDS_DICT = {
    'sendAsync': RewardItemSendAsyncData
}