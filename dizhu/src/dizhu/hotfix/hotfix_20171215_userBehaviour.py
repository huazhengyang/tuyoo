# -*- coding=utf-8 -*-
"""
Created on 2017年11月27日

@author: wangjifa
"""

import random, os
import datetime

import freetime.util.log as ftlog
from dizhu.entity import dizhuconf, dizhu_util
from dizhu.entity.dizhuconf import DIZHU_GAMEID
from poker.entity.biz.bireport import reportGameEvent
from poker.entity.dao import daobase, userdata, sessiondata
from poker.util import strutil

#干预行为的类型：
BEHAVIOUR_TYPE_NONE = 0     # 预测不流失
BEHAVIOUR_TYPE_REWARD = 1   # 发奖
BEHAVIOUR_TYPE_MSG = 2      # 发消息 # 已废弃
BEHAVIOUR_TYPE_NOUSE = 3    # 放置不处理
BEHAVIOUR_TYPE_REWARDED = 4 # 已发过奖
BEHAVIOUR_TYPE_NOUSEED = 5  # 已处理过的放置组

from dizhu.entity import dizhu_user_behaviour
from dizhu.entity.dizhu_user_behaviour import _checkExpectedUser, _changeUserBehaviourInfo

def _sendUserBehaviourReward(event):
    userId = event.userId
    behaviourConf = dizhuconf.getUserBehaviourReward()
    if not _checkExpectedUser(userId, behaviourConf):
        return
    try:
        ret = daobase.executeUserCmd(event.userId, 'HGET', 'userBehaviour:6:' + str(event.userId), 'info')
        if ret:
            behaviourInfo = strutil.loads(ret)
            behaviourType = behaviourInfo.get('type', 0)
            clientId = sessiondata.getClientId(event.userId)
            if behaviourType == BEHAVIOUR_TYPE_REWARD:
                _changeUserBehaviourInfo(event.userId, behaviourInfo, behaviourConf)
                reportGameEvent('DIZHU_BEHAVIOUR_GROUP', event.userId, DIZHU_GAMEID, 0, 0, 0, 0, behaviourType, 0, [],
                                clientId)
            elif behaviourType == BEHAVIOUR_TYPE_NOUSE:
                behaviourInfo['type'] = BEHAVIOUR_TYPE_NOUSEED
                behaviourInfo['date'] = int(dizhu_util.calcTodayIssueNum())
                daobase.executeUserCmd(userId, 'HSET', 'userBehaviour:6:' + str(userId), 'info',
                                       strutil.dumps(behaviourInfo))
                reportGameEvent('DIZHU_BEHAVIOUR_GROUP', event.userId, DIZHU_GAMEID, 0, 0, 0, 0, behaviourType, 0, [], clientId)
        #else #这个分支在玩家登陆时处理过了，无对应属性的玩家不处理。
        if ftlog.is_debug():
            ftlog.debug('userBehaviour.setUserData userId=', event.userId, 'ret=', ret)
    except Exception, e:
        ftlog.warn('_sendUserBehaviourReward userId=', userId, 'error=', e)


dizhu_user_behaviour._sendUserBehaviourReward = _sendUserBehaviourReward


def _saveUserToRedis(userId, status, behaviourConf):
    if not userdata.checkUserData(userId):
        if ftlog.is_debug():
            ftlog.debug('user_behaviour checkFailed userId=', userId)
        return False

    if not _checkExpectedUser(userId, behaviourConf):
        return False

    todayDate = int(dizhu_util.calcTodayIssueNum())
    behaviourInfo = {'type': BEHAVIOUR_TYPE_NONE, 'date': todayDate}
    try:
        ret = daobase.executeUserCmd(userId, 'HGET', 'userBehaviour:6:' + str(userId), 'info')
        if ret:
            ret = strutil.loads(ret)
            behaviourType = ret.get('type', BEHAVIOUR_TYPE_NONE)
            if behaviourType not in [BEHAVIOUR_TYPE_REWARDED, BEHAVIOUR_TYPE_NOUSEED]:
                behaviourInfo['type'] = random.randrange(1, 3, 1) if status == '0' else BEHAVIOUR_TYPE_NONE
                return daobase.executeUserCmd(userId, 'HSET', 'userBehaviour:6:' + str(userId), 'info', strutil.dumps(behaviourInfo))
        else:
            behaviourInfo['type'] = random.randrange(1, 3, 1) if status == '0' else BEHAVIOUR_TYPE_NONE
            return daobase.executeUserCmd(userId, 'HSET', 'userBehaviour:6:' + str(userId), 'info', strutil.dumps(behaviourInfo))
    except Exception, e:
        ftlog.warn('user_behaviour._saveUserToRedis userId=', userId, 'err=', e)
    return False

dizhu_user_behaviour._saveUserToRedis = _saveUserToRedis

ftlog.info('user_behaviour.hotfix_20171215_userBehaviour ok ')
