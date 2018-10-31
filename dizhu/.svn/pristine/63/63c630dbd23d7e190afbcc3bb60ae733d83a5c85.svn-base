# -*- coding=utf-8
'''
Created on 2015年7月28日

@author: zhaojiangang
'''
from dizhu.entity import dizhutask
from dizhu.entity.segment.dizhu_segment_match import SegmentWinStreakTaskHelper
from dizhu.servers.util.task_handler import TableTaskHelper, DailyTaskHelper
import freetime.util.log as ftlog
from poker.entity.biz.item.item import TYAssetUtils
from poker.entity.biz.task.exceptions import TYTaskException
from poker.entity.game.game import TYGame
from poker.protocol.rpccore import markRpcCall
import poker.util.timestamp as pktimestamp
from dizhu.entity.segment.task import (SegmentTaskData, UserTaskData,
                                       SegmentNewbieTaskKind,
                                       SegmentDailyTaskKind,
                                       SegmentTaskHelper, TaskTimeManager
                                       )


@markRpcCall(groupName="userId", lockName="userId", syncCall=1)
def setTableTasks(gameId, userId, taskIdList):
    ftlog.info('setTableTask gameId=', gameId,
               'userId=', userId,
               'taskIdList=', taskIdList)
    timestamp = pktimestamp.getCurrentTimestamp()
    taskModel = dizhutask.tableTaskSystem.loadTaskModel(userId, timestamp)
    taskModel.userTaskUnit.removeAllTask()
    for taskId in taskIdList:
        taskKind = taskModel.userTaskUnit.taskUnit.findTaskKind(taskId)
        if not taskKind:
            raise TYTaskException(-1, 'Not found taskKind %s' % (taskId))
        task = taskKind.newTask(None, timestamp)
        taskModel.userTaskUnit.addTask(task)
    return [task.kindId for task in taskModel.userTaskUnit.taskList]


@markRpcCall(groupName="userId", lockName="userId", syncCall=1)
def setTableTaskProgress(gameId, userId, taskId, progress):
    ftlog.info('setTableTaskProgress gameId=', gameId,
               'userId=', userId,
               'taskId=', taskId)
    timestamp = pktimestamp.getCurrentTimestamp()
    taskModel = dizhutask.tableTaskSystem.loadTaskModel(userId, timestamp)
    task = taskModel.userTaskUnit.findTask(taskId)
    if not task:
        raise TYTaskException(-1, 'Not found task: %s' % (taskId))
    changed, finishCount = task.setProgress(progress, timestamp)
    if changed:
        taskModel.userTaskUnit.updateTask(task)
    return changed, finishCount, task.progress


@markRpcCall(groupName="userId", lockName="userId", syncCall=1)
def setTableTaskProgressHack(gameId, userId, taskId, progress):
    ftlog.info('setTableTaskProgressHack gameId=', gameId,
               'userId=', userId,
               'taskId=', taskId)
    timestamp = pktimestamp.getCurrentTimestamp()
    taskModel = dizhutask.tableTaskSystem.loadTaskModel(userId, timestamp)
    task = taskModel.userTaskUnit.findTask(taskId)
    if not task:
        raise TYTaskException(-1, 'Not found task: %s' % (taskId))
    task.progress = progress
    taskModel.userTaskUnit.updateTask(task)
    return task.progress


@markRpcCall(groupName="userId", lockName="userId", syncCall=1)
def getTableTaskReward(gameId, userId, taskId):
    timestamp = pktimestamp.getCurrentTimestamp()
    taskModel = dizhutask.tableTaskSystem.loadTaskModel(userId, timestamp)
    task = taskModel.userTaskUnit.findTask(taskId)
    if not task:
        raise TYTaskException(-1, 'Not found task: %s' % (taskId))
    assetList = dizhutask.tableTaskSystem.getTaskReward(task, timestamp, 'TASK_REWARD', taskId)
    return TYAssetUtils.buildContentsString(assetList)


@markRpcCall(groupName="userId", lockName="userId", syncCall=1)
def getTableTasks(gameId, userId):
    timestamp = pktimestamp.getCurrentTimestamp()
    taskModel = dizhutask.tableTaskSystem.loadTaskModel(userId, timestamp)
    return TableTaskHelper.buildTableTasks(taskModel)


@markRpcCall(groupName="userId", lockName="userId", syncCall=1)
def setDailyTaskProgress(gameId, userId, taskId, progress):
    ftlog.info('setDailyTaskProgress.setTableTaskProgress gameId=', gameId,
               'userId=', userId,
               'taskId=', taskId)
    timestamp = pktimestamp.getCurrentTimestamp()
    taskModel = dizhutask.dailyTaskSystem.loadTaskModel(userId, timestamp)
    task = taskModel.userTaskUnit.findTask(taskId)
    if not task:
        raise TYTaskException(-1, 'Not found task: %s' % (taskId))
    changed, finishCount = task.setProgress(progress, timestamp)
    if changed:
        taskModel.userTaskUnit.updateTask(task)
    return changed, finishCount, task.progress


@markRpcCall(groupName="userId", lockName="userId", syncCall=1)
def getDailyTaskReward(gameId, userId, taskId):
    timestamp = pktimestamp.getCurrentTimestamp()
    taskModel = dizhutask.dailyTaskSystem.loadTaskModel(userId, timestamp)
    task = taskModel.userTaskUnit.findTask(taskId)
    if not task:
        raise TYTaskException(-1, 'Not found task: %s' % (taskId))
    assetList = dizhutask.dailyTaskSystem.getTaskReward(task, timestamp, 'DTASK_REWARD', taskId)
    return TYAssetUtils.buildContentsString(assetList)


@markRpcCall(groupName="userId", lockName="userId", syncCall=1)
def getDailyTasks(gameId, userId):
    timestamp = pktimestamp.getCurrentTimestamp()
    taskModel = dizhutask.dailyTaskSystem.loadTaskModel(userId, timestamp)
    return DailyTaskHelper.encodeDailyTaskList(taskModel)


@markRpcCall(groupName="userId", lockName="userId", syncCall=1)
def refreshDailyTasks(gameId, userId):
    timestamp = pktimestamp.getCurrentTimestamp()
    taskModel = dizhutask.dailyTaskSystem.loadTaskModel(userId, timestamp)
    taskModel._refreshImpl(timestamp)
    return DailyTaskHelper.encodeDailyTaskList(taskModel)


@markRpcCall(groupName="userId", lockName="userId", syncCall=1)
def getNewbieTaskInfo(gameId, userId, roomPlayTimes=None):
    return dizhutask.newbieTaskSystem.getTaskInfo(userId, roomPlayTimes)


@markRpcCall(groupName="userId", lockName="userId", syncCall=1)
def getTaskProgress(gameId, userId):
    if ftlog.is_debug():
        ftlog.debug('RPC->Call: task_remote.getTaskProgress, userId=', userId)
    return dizhutask.newbieTaskSystem.getTaskProgress(userId)

@markRpcCall(groupName="userId", lockName="userId", syncCall=1)
def setNewbieTasks(gameId, userId, taskIdList, withFullProgress=False):
    ftlog.info('setNewbieTask gameId=', gameId,
               'userId=', userId,
               'taskIdList=', taskIdList,
               'withFullProgress=', withFullProgress)
    timestamp = pktimestamp.getCurrentTimestamp()
    taskModel = dizhutask.newbieTaskSystem.loadTaskModel(userId, timestamp)
    taskModel.userTaskUnit.removeAllTask()
    for taskId in taskIdList:
        taskKind = taskModel.userTaskUnit.taskUnit.findTaskKind(taskId)
        if not taskKind:
            raise TYTaskException(-1, 'Not found taskKind %s' % (taskId))
        task = taskKind.newTask(None, timestamp)
        if withFullProgress:
            if taskId == taskIdList[-1]:
                task.setProgress(taskKind.count - 1, timestamp)
            else:
                task.setProgress(taskKind.count, timestamp)
        taskModel.userTaskUnit.addTask(task)
    return [task.kindId for task in taskModel.userTaskUnit.taskList]


@markRpcCall(groupName="userId", lockName="userId", syncCall=1)
def setNewbieTaskProgress(gameId, userId, taskId, progress):
    ftlog.info('setNewbieTaskProgress gameId=', gameId,
               'userId=', userId,
               'taskId=', taskId)
    timestamp = pktimestamp.getCurrentTimestamp()
    taskModel = dizhutask.newbieTaskSystem.loadTaskModel(userId, timestamp)
    task = taskModel.userTaskUnit.findTask(taskId)
    if not task:
        raise TYTaskException(-1, 'Not found task: %s' % (taskId))
    changed, finishCount = task.setProgress(progress, timestamp)
    if changed:
        taskModel.userTaskUnit.updateTask(task)
    return changed, finishCount, task.progress


@markRpcCall(groupName="userId", lockName="userId", syncCall=1)
def setSegmentTaskProgress(gameId, userId, progress):
    ftlog.info('setSegmentTaskProgress gameId=', gameId,
               'userId=', userId,
               'progress=', progress)
    taskInfo = UserTaskData.get_cur_task(userId)
    if not taskInfo:
        return False, 'no task'
    taskId = str(taskInfo["taskId"])
    taskKind = SegmentTaskData.task_kind_map[taskId]
    if taskKind.TYPE_ID == SegmentNewbieTaskKind.TYPE_ID:
        UserTaskData.update_newbie_task(userId, taskId, progress)
    elif taskKind.TYPE_ID == SegmentDailyTaskKind.TYPE_ID:
        UserTaskData.update_daily_task(userId, progress)

    SegmentTaskHelper.send_get_task_response(gameId, userId)
    return True, ''

@markRpcCall(groupName="", lockName="", syncCall=1)
def doSegmentTaskTimeSet(gameId, ts):
    ftlog.info('doSegmentTaskTimeSet gameId=', gameId,
               'ts=', ts)
    TaskTimeManager._reset_daily_task_expire(ts)
    return True, 'success'



@markRpcCall(groupName="userId", lockName="userId", syncCall=1)
def doSegmentTableWinStreakTask(userId):
    userdata, _, progressInfo = SegmentWinStreakTaskHelper.getUserProgressInfo(userId)
    if ftlog.is_debug():
        ftlog.debug('RPC->Call: task_remote.doSegmentTableWinStreakTask, userId=', userId,
                    'winStreak=', userdata.winStreak,
                    'progressInfo=', progressInfo)

    return {
        'winStreak': userdata.winStreak,
        'progressInfo': progressInfo
    }


@markRpcCall(groupName="userId", lockName="userId", syncCall=1)
def doSyncUserWinStreakBackUp(userId):
    if ftlog.is_debug():
        ftlog.debug('RPC->Call: task_remote.doSyncUserWinStreakBackUp, userId=', userId)

    SegmentWinStreakTaskHelper.syncUserWinStreakBackUp(userId)


@markRpcCall(groupName="userId", lockName="userId", syncCall=1)
def doSegmentTableWinStreak(userId):
    winStreak = SegmentWinStreakTaskHelper.getUserWinStreak(userId)
    if ftlog.is_debug():
        ftlog.debug('RPC->Call: task_remote.doSegmentTableWinStreak, userId=', userId,
                    'winStreak=', winStreak)
    return winStreak