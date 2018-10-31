# -*- coding:utf-8 -*-
'''
Created on 2018年2月8日

@author: zhaojiangang
'''
from hall.entity.halltask import HallTaskKindPoolWithCond, \
    HallNewUserSubTaskSystem, HallChargeSubTaskSystem
from poker.entity.biz.task.task import TYUserTaskUnit


# def _fix_user_task_unit(self, user_task_unit, timestamp):
#     from poker.entity.dao import sessiondata
#     task_pool = user_task_unit.taskUnit.poolList[0]
#     assert isinstance(task_pool, HallTaskKindPoolWithCond)
#     clientId = sessiondata.getClientId(user_task_unit.userId)
#     
#     # 检查过期条件
#     if task_pool.visible_cond and \
#             not task_pool.visible_cond.check(self.gameId, user_task_unit.userId, clientId, timestamp):
#         return TYUserTaskUnit(user_task_unit.userId, user_task_unit.taskUnit)
#     tasklist = user_task_unit.taskList
#     if tasklist:
#         for task in tasklist:
#             if not task.gotReward:
#                 return user_task_unit  # 还有任务没领奖
#     else:  # 身上没任务
#         # 检查接取条件
#         if task_pool.accepted_cond and not task_pool.accepted_cond.check(
#                 self.gameId, user_task_unit.userId, clientId, timestamp):
#             return user_task_unit
# 
#     # 接新任务
#     task_kind = task_pool.nextTaskKind(task_order=len(tasklist))
#     if task_kind:
#         task = task_kind.newTask(None, timestamp)
#         user_task_unit.addTask(task)
#     return user_task_unit
# 
# 
# HallNewUserSubTaskSystem._fix_user_task_unit = _fix_user_task_unit
def _taskpool_expire(self, task_pool, userId, curtime):
    from poker.entity.dao import sessiondata
    clientId = sessiondata.getClientId(userId)
    return task_pool.visible_cond and not task_pool.visible_cond.check(self.gameId, userId, clientId, curtime)

def _taskpool_get_first(self, task_pool, userId, curtime):
    assert isinstance(task_pool, HallTaskKindPoolWithCond)
    from poker.entity.dao import sessiondata
    clientId = sessiondata.getClientId(userId)
    # 过期条件
    if self._taskpool_expire(task_pool, userId, curtime):
        return
    # 检查接取条件
    if task_pool.accepted_cond and not task_pool.accepted_cond.check(self.gameId, userId, clientId, curtime):
        return
    return task_pool.nextTaskKind()

HallChargeSubTaskSystem._taskpool_expire = _taskpool_expire
HallChargeSubTaskSystem._taskpool_get_first = _taskpool_get_first


