# -*- coding:utf-8 -*-
'''
Created on 2017年12月07日

@author: wangjifa
'''
from datetime import datetime

from hall.entity.hallusercond import UserConditionUserBehaviourA
from poker.entity.dao import userdata, daobase
from poker.util import strutil

def check(self, gameId, userId, clientId, timestamp, **kwargs):
    # 新用户不属于A
    if self.newUserCond.check(gameId, userId, clientId, timestamp):
        return False

    behaviourInfo = daobase.executeUserCmd(userId, 'hget', 'userBehaviour:%s:%s' % (self.gameId, userId), 'info')
    if not behaviourInfo:
        return True

    try:
        behaviourInfo = strutil.loads(behaviourInfo)
    except:
        return False

    infoType = behaviourInfo.get('type', 0)

    if infoType == 1:
        return True

    if infoType == 0:
        todayDate = datetime.fromtimestamp(timestamp).strftime('%Y%m%d')
        if str(behaviourInfo.get('date')) != todayDate:
            return True

    return False


UserConditionUserBehaviourA.check = check