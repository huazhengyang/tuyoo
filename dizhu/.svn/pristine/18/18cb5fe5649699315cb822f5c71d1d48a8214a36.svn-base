# -*- coding:utf-8 -*-
'''
Created on 2017年6月23日

@author: wangyonghui
'''
from dizhu.entity import dizhuconf, dizhutask
import freetime.util.log as ftlog
from poker.entity.biz.content import TYContentRegister
from poker.entity.dao import sessiondata
from poker.util import timestamp as pktimestamp


def isNewer(userId):
    clientId = sessiondata.getClientId(userId)
    return dizhuconf.getNewbieTaskConf().get('open', 0) == 1 and clientId not in dizhuconf.getNewbieTaskConf().get('closes', [])


def getTaskInfo(self, userId):
    '''
    新手任务信息，table_info协议调用
    '''
    if not isNewer(userId):
        return None
    kindId, completedList = self.getTaskStatus(userId)
    if len(completedList) >= self.taskKindCount \
            or pktimestamp.getCurrentTimestamp() >= self.getDeadlineTimestamp(userId):
        return None
    curTask = self.getTaskByKindId(userId, kindId)
    if curTask is None:
        return None
    if ftlog.is_debug():
        ftlog.debug('DizhuNewbieTaskSystem.getTaskInfo',
                    'userId=', userId,
                    'kindId=', kindId,
                    'curTask=', curTask,
                    'completelist=', completedList,
                    caller=self)
    finalRewordConf = dizhuconf.getNewbieTaskConf().get('rewardContent', {})
    finalRewordContent = TYContentRegister.decodeFromDict(finalRewordConf)
    tasksInfo = {
        'details': self._encodeTaskList(userId, list(set(completedList+[curTask.kindId]))),
        'final': self._encodeRewardContent(finalRewordContent),
        'count': self.taskKindCount,
        'deadline': max(self.getDeadlineTimestamp(userId) - pktimestamp.getCurrentTimestamp(), 0)
    }
    return tasksInfo

dizhutask.isNewer = isNewer
dizhutask.DizhuNewbieTaskSystem.getTaskInfo = getTaskInfo
ftlog.info('DizhuNewbieTaskSystem hot fix')
