# -*- coding:utf-8 -*-
'''
Created on 2017年10月19日

@author: zhaojiangang
'''
from datetime import datetime

import freetime.util.log as ftlog
from hall.entity.hallusercond import UserConditionRegisterDay
from poker.entity.dao import userdata


def check(self, gameId, userId, clientId, timestamp, **kwargs):
    try:
        if self.startDays == -1 and self.stopDays == -1:
            return True
        nowDate = datetime.fromtimestamp(timestamp).date()
        createDate = datetime.strptime(userdata.getAttr(userId, 'createTime'), '%Y-%m-%d %H:%M:%S.%f').date()
        registerDays = max(0, (nowDate - createDate).days)
        return (self.startDays == -1 or registerDays >= self.startDays) \
               and (self.stopDays == -1 or registerDays <= self.stopDays)
    except:
        ftlog.error('UserConditionRegisterDay.check',
                    'gameId=', gameId,
                    'userId=', userId,
                    'clientId=', clientId,
                    'timestamp=', timestamp,
                    'kwargs=', kwargs,
                    'daysRange=', '[%s,%s]' % (self.startDays, self.stopDays))
        return False


UserConditionRegisterDay.check = check


