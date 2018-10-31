# -*- coding:utf-8 -*-
'''
Created on 2017年8月22日

@author: wangyonghui
'''
from dizhu.entity import dizhutask
import freetime.util.log as ftlog
from poker.util import timestamp as pktimestamp


def getTaskProgress(self, userId):
    '''
    获取玩家新手任务进度，包括当前进行的任务进度、是否完成所有任务
    如果当前任务完成，则发送奖励
    如果所有任务也完成，则发送终极奖励
    '''
    if self.expired(userId):
        return None

    kindId, completedList, completed = self.getTaskStatus(userId)
    curTask = self.getTaskByKindId(userId, kindId)
    if curTask is None:
        # 任务完成或者任务过期会把所有新手任务都删掉，所以这两种情况下都会走到这里，不需要单独处理
        return None

    if completed:
        return None

    if len(completedList) >= self.taskKindCount:
        return None

    currentTimestamp = pktimestamp.getCurrentTimestamp()
    final = 0
    if curTask and curTask.gotReward == 0 and curTask.isFinished:
        # 发送完成当前任务的奖励
        self._sendTaskReward(curTask, currentTimestamp, 'NEWBIE_TASK', curTask.kindId)
        curTask.gotReward = 1
        curTask.userTaskUnit.updateTask(curTask)
        # 尝试激活下一个任务
        final = self._tryToActiveNextTask(userId, curTask, completedList, currentTimestamp)

    if ftlog.is_debug():
        ftlog.debug('getTaskProgress',
                    'userId=', userId,
                    'curTask=', curTask,
                    'completedList=', completedList,
                    'taskKindCount=', self.taskKindCount,
                    'curTaskId=', curTask.kindId,
                    'gotReward=', curTask.gotReward,
                    'progress=', curTask.progress,
                    'final=', final)
    curInfo = {
        'index': min(len(completedList) + 1, self.taskKindCount),
        'kindId': curTask.kindId,
        'total': curTask.taskKind.count,
        'finish': curTask.progress
    }
    return {'cur': curInfo, 'final': final}


dizhutask.DizhuNewbieTaskSystem.getTaskProgress = getTaskProgress
ftlog.info('DizhuNewbieTaskSystem hot fix')
