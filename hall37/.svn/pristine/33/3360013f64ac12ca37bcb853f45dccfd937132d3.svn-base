# -*- coding:utf-8 -*-
'''
Created on 2017年3月31日

@author: zhaojiangang
'''
import freetime.util.log as ftlog
from poker.entity.biz.task.task import TYUserTaskUnit
from hall.entity.halltask import HallTaskKindPoolWithCond

def _fix_user_task_unit(self, user_task_unit, timestamp):
    from poker.entity.dao import sessiondata
    clientId = sessiondata.getClientId(user_task_unit.userId)
    
    # 所有任务池的检查过期条件是一样的
    task_pool_0 = user_task_unit.taskUnit.poolList[0]
    if task_pool_0.visible_cond and \
            not task_pool_0.visible_cond.check(self.gameId, user_task_unit.userId, clientId, timestamp):
        ftlog.debug('task pool not match visible cond, return...')
        return TYUserTaskUnit(user_task_unit.userId, user_task_unit.taskUnit)
    
    tasklist = user_task_unit.taskList
    if tasklist:
        for task in tasklist:
            if not task.gotReward:
                return user_task_unit  # 还有任务没领奖

    
    for task_pool in user_task_unit.taskUnit.poolList:
        assert isinstance(task_pool, HallTaskKindPoolWithCond)
        # 检查接取条件
        if task_pool.accepted_cond and not task_pool.accepted_cond.check(self.gameId, user_task_unit.userId, clientId, timestamp):
            ftlog.debug('can not accept this task pool, continue...')
            continue

        # 接新任务
        task_kind = task_pool.nextTaskKind(task_order=len(tasklist))
        if task_kind:
            task = task_kind.newTask(None, timestamp)
            user_task_unit.addTask(task)
            ftlog.debug('find task pool, break...')
            break
        
    return user_task_unit

from hall.entity.halltask import HallChargeSubTaskSystem
HallChargeSubTaskSystem._fix_user_task_unit = _fix_user_task_unit