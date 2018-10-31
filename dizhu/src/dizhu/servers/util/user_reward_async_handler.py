# -*- coding:utf-8 -*-
'''
Created on 2018年7月24日

@author: wangyonghui
'''
from sre_compile import isstring

import freetime.util.log as ftlog
from dizhu.entity.reward_async.reward_async import RewardAsyncHelper
from hall.servers.common.base_checker import BaseMsgPackChecker
from poker.protocol import router
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod


@markCmdActionHandler
class UserRewardAsyncHandler(BaseMsgPackChecker):
    def __init__(self):
        super(UserRewardAsyncHandler, self).__init__()

    def _check_param_rewardId(self, msg, key, params):
        rewardId = msg.getParam(key)
        if isstring(rewardId):
            return None, rewardId
        return None, {}

    @markCmdActionMethod(cmd='dizhu', action='get_reward_async', clientIdVer=0, lockParamName='', scope='game')
    def doGetRewardByRewardId(self, userId, rewardId):
        if ftlog.is_debug():
            ftlog.debug('UserRewardAsyncHandler.doGetRewardByRewardId',
                        'userId= ', userId,
                        'rewardId= ', rewardId)
        mo = RewardAsyncHelper.buildGetRewardResponse(userId, rewardId)
        router.sendToUser(mo, userId)
