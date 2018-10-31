# -*- coding:utf-8 -*-
'''
Created on 2015年12月10日

@author: zhaojiangang
'''
import freetime.util.log as ftlog
from hall.entity import neituiguang
from hall.entity.hallconf import HALL_GAMEID
from hall.entity.halltask import TYHallTaskModel, TYHallSubTaskSystem
from hall.entity import datachangenotify


class NewUserTaskModel(TYHallTaskModel):
    def __init__(self, newUserTaskSystem, userTaskUnit):
        super(NewUserTaskModel, self).__init__(newUserTaskSystem, userTaskUnit)
        
    def initTasksIfNeed(self, poolIndex, timestamp):
        if (poolIndex >= 0 and poolIndex < len(self.userTaskUnit.taskUnit.poolList)):
            if not self.userTaskUnit.taskList:
                pool = self.userTaskUnit.taskUnit.poolList[poolIndex]
                kindList = list(pool.taskKindList)
                for taskKind in kindList:
                    task = taskKind.newTask(None, timestamp)
                    self.userTaskUnit.addTask(task)
                ftlog.info('NewUserTaskModel.initTasksIfNeed userId=', self.userId,
                           'poolIndex=', poolIndex,
                           'kindList=', [tk.kindId for tk in kindList])
                return True
        return False


class NewUserTaskSystem(TYHallSubTaskSystem):
    def __init__(self):
        super(NewUserTaskSystem, self).__init__(HALL_GAMEID)
        
    def _loadTaskModel(self, userTaskUnit, timestamp):
        ftlog.debug('NewUserTaskSystem._loadTaskModel userId=', userTaskUnit.userId,
                    'taskIds=', [task.kindId for task in userTaskUnit.taskList])
        taskModel = NewUserTaskModel(self, userTaskUnit)
        if not taskModel.userTaskUnit.taskList:
            status = neituiguang.loadStatus(userTaskUnit.userId, timestamp)
            # 根据用户状态初始化任务
            if status.inviter and status.isNewUser:
                ftlog.info('NewUserTaskSystem._loadTaskModel userId=', userTaskUnit.userId,
                           'inviter=', status.inviter.userId)
                poolIndex = 0 if status.inviter.userId == 0 else 1
                init = taskModel.initTasksIfNeed(poolIndex, timestamp)
                if init:
                    datachangenotify.sendDataChangeNotify(HALL_GAMEID, userTaskUnit.userId, ['free', 'promotion_loc'])
        return taskModel
    
    def _onTaskUnitLoadedImpl(self, taskUnit):
        pass
    
    def _onTaskFinished(self, task, timestamp):
        # TODO publish event
        datachangenotify.sendDataChangeNotify(HALL_GAMEID, task.userId, ['free', 'promotion_loc'])
        pass


newUserTaskSystem = NewUserTaskSystem()
