# -*- coding=utf-8
'''
Created on 2015年7月15日

@author: zhaojiangang
'''
from datetime import datetime

from dizhu.entity import dizhutask, skillscore, dizhuasset
from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from hall.entity import hallitem
from hall.servers.common.base_checker import BaseMsgPackChecker
from poker.entity.biz.content import TYContentUtils
from poker.entity.biz.item.exceptions import TYAssetNotEnoughException
from poker.entity.biz.item.item import TYAssetUtils
from poker.entity.biz.task.exceptions import TYTaskException
from poker.protocol import router, runcmd
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod
import poker.util.timestamp as pktimestamp
from dizhu.entity.segment.task import SegmentTaskHelper


class DailyTaskHelper(object):
    @classmethod
    def buildRewardStr(cls, rewardContent, assetKindTupleList):
        if rewardContent and rewardContent.desc:
            return rewardContent.desc
        return TYAssetUtils.buildContentsString(assetKindTupleList, False)
    
    @classmethod
    def encodeDailyTaskList(cls, taskModel):
        ret = []
        index = 1
        tasks = sorted(taskModel.userTaskUnit.taskList, key=lambda x: 0 - x.taskKind.star)
        for task in tasks:
            taskName = '任务%d' % (index)
            ret.append(cls.encodeDailyTask(task, taskName))
            index += 1
        ret.sort(key=lambda x: 0 - x['state'])
        return ret
    
    @classmethod
    def encodeDailyTask(cls, task, taskName=None):
        taskState = 0
        if task.isFinished:
            taskState = 2 if task.gotReward else 1
        schedule = None
        if task.finishCount > 0:
            schedule = '%d/%d' % (task.taskKind.count, task.taskKind.count)
        else:
            schedule = '%d/%d' % (task.progress, task.taskKind.count)
        assetKindTupleList = []
        if task.taskKind.rewardContent:
            assetKindTupleList = hallitem.getAssetKindTupleList(task.taskKind.rewardContent)
        return {
            'id':task.kindId,
            'name':taskName if taskName else task.taskKind.name,
            'star':task.taskKind.star,
            'des':task.taskKind.desc,
            'schedule':schedule,
            'state':taskState,
            'reward':cls.buildRewardStr(task.taskKind.rewardContent, assetKindTupleList),
            'rewardpic':assetKindTupleList[0][0].pic if assetKindTupleList else ''
        }
        
    @classmethod
    def buildDailyTaskUpdateResponse(cls, gameId, userId, taskModel, timestamp):
        updateTime = taskModel.calcNextRefreshTime(timestamp)
        updateCoin = TYContentUtils.getMinFixedAssetCount(taskModel.subTaskSystem.refreshContent, \
                    hallitem.ASSET_CHIP_KIND_ID) if taskModel.subTaskSystem.refreshContent else 0
        mo = MsgPack()
        mo.setCmd('every_task')
        mo.setResult('action', 'update')
        mo.setResult('gameId', gameId)
        mo.setResult('userId', userId)
        mo.setResult('taskdes', '')
        mo.setResult('updatetime', updateTime)
        mo.setResult('updatecoin', updateCoin)
        tasks = cls.encodeDailyTaskList(taskModel)
        mo.setResult('tasks', tasks)
        return mo
        
@markCmdActionHandler
class DailyTaskHandler(BaseMsgPackChecker):
    def _check_param_taskId(self, msg, key, params):
        paramId = msg.getParam('id')
        if paramId and isinstance(paramId, int) :
            return None, paramId
        return 'ERROR of id !' + str(paramId), None
    
    def sendErrorResponse(self, userId, errorCode, errorInfo):
        mo = MsgPack()
        mo.setCmd('every_task')
        mo.setError(errorCode, errorInfo)
        router.sendToUser(mo, userId)
            
    @markCmdActionMethod(cmd='every_task', action="update", clientIdVer=0, scope='game')
    def doDailyTaskUpdate(self, userId, gameId):
        timestamp = pktimestamp.getCurrentTimestamp()
        taskModel = dizhutask.dailyTaskSystem.loadTaskModel(userId, timestamp)
        mo = DailyTaskHelper.buildDailyTaskUpdateResponse(gameId, userId, taskModel, timestamp)
        router.sendToUser(mo, userId)
        
    @markCmdActionMethod(cmd='every_task', action="change", clientIdVer=0, scope='game')
    def doDailyTaskRefresh(self, userId, gameId):
        try:
            timestamp = pktimestamp.getCurrentTimestamp()
            taskModel = dizhutask.dailyTaskSystem.loadTaskModel(userId, timestamp)
            taskModel.refresh(timestamp)
            mo = DailyTaskHelper.buildDailyTaskUpdateResponse(gameId, userId, taskModel, timestamp)
            router.sendToUser(mo, userId)
        except TYAssetNotEnoughException, _:
            self.sendErrorResponse(userId, 1, '金币不足')
        
    @markCmdActionMethod(cmd='every_task', action="taskdone", clientIdVer=0, scope='game')
    def doDailyTaskGetReward(self, userId, gameId, taskId):
        try:
            timestamp = pktimestamp.getCurrentTimestamp()
            taskModel = dizhutask.dailyTaskSystem.loadTaskModel(userId, timestamp)
            task = taskModel.userTaskUnit.findTask(taskId)
            if not task:
                raise TYTaskException(-1, 'Not found task: %s' % (taskId))
            dizhutask.dailyTaskSystem.getTaskReward(task, timestamp, 'DTASK_REWARD', taskId)
            mo = DailyTaskHelper.buildDailyTaskUpdateResponse(gameId, userId, taskModel, timestamp)
            router.sendToUser(mo, userId)
        except TYTaskException, e:
            self.sendErrorResponse(userId, e.errorCode, e.message)

class MedalTaskHelper(object):
    @classmethod
    def encodeMedalTask(cls, task, iswear):
        assetKindTupleList = []
        if task.taskKind.rewardContent:
            assetKindTupleList = hallitem.getAssetKindTupleList(task.taskKind.rewardContent)
        return {
           'id':task.kindId,
           'name':task.taskKind.name,
           'pic':task.taskKind.pic,
           'des':task.taskKind.desc,
           'reward':DailyTaskHelper.buildRewardStr(task.taskKind.rewardContent, assetKindTupleList),
           'alreadynum':task.progress,
           'totalnum':task.taskKind.count,
           'num':task.finishCount,
           'isgetreward':True if task.gotReward != 0 else False,
           'iswear':iswear,
           'getmedaltime':datetime.fromtimestamp(task.finishTime).strftime('%Y-%m-%d %H:%M:%S') if task.finishTime else '' 
        }
    
    @classmethod
    def encodeMedalTasks(cls, tasks, weardTaskId):
        ret = []
        for task in tasks:
            ret.append(cls.encodeMedalTask(task, weardTaskId == task.kindId))
        return ret
    
    @classmethod
    def buildMedalUpdateResponse(cls, gameId, userId, taskModel, timestamp):
        mo = MsgPack()
        mo.setCmd('medal_info')
        mo.setResult('action', 'update')
        mo.setResult('userId', userId)
        mo.setResult('gameId', gameId)
        mo.setResult('medals', cls.encodeMedalTasks(taskModel.userTaskUnit.taskList, taskModel.wearedId))
        return mo
    
@markCmdActionHandler
class MedalTaskHandler(BaseMsgPackChecker):
    def _check_param_taskId(self, msg, key, params):
        paramId = msg.getParam('id')
        if paramId and isinstance(paramId, int) :
            return None, paramId
        return 'ERROR of id !' + str(paramId), None
    
    def sendErrorResponse(self, userId, errorCode, errorInfo):
        ftlog.warn('ERROR, MedalTaskHandler userId=', userId, 'error=', errorCode, errorInfo)
        mo = MsgPack()
        mo.setCmd('medal_info')
        mo.setError(errorCode, errorInfo)
        router.sendToUser(mo, userId)
            
    @markCmdActionMethod(cmd='medal_info', action="update", clientIdVer=0, scope='game')
    def doMedalTaskUpdate(self, userId, gameId):
        timestamp = pktimestamp.getCurrentTimestamp()
        taskModel = dizhutask.medalTaskSystem.loadTaskModel(userId, timestamp)
        mo = MedalTaskHelper.buildMedalUpdateResponse(gameId, userId, taskModel, timestamp)
        router.sendToUser(mo, userId)
        
    @markCmdActionMethod(cmd='medal_info', action="towear", clientIdVer=0, scope='game')
    def doMedalTaskWear(self, userId, gameId, taskId):
        try:
            timestamp = pktimestamp.getCurrentTimestamp()
            taskModel = dizhutask.medalTaskSystem.loadTaskModel(userId, timestamp)
            task = taskModel.userTaskUnit.findTask(taskId)
            if not task:
                raise TYTaskException(-1, 'Not found task: %s' % (taskId))
            taskModel.wear(task)
            mo = MedalTaskHelper.buildMedalUpdateResponse(gameId, userId, taskModel, timestamp)
            router.sendToUser(mo, userId)
        except TYTaskException, e:
            self.sendErrorResponse(userId, e.errorCode, e.message)
        
    @markCmdActionMethod(cmd='medal_info', action="unwear", clientIdVer=0, scope='game')
    def doMedalTaskUnwear(self, userId, gameId, taskId):
        try:
            timestamp = pktimestamp.getCurrentTimestamp()
            taskModel = dizhutask.medalTaskSystem.loadTaskModel(userId, timestamp)
            task = taskModel.userTaskUnit.findTask(taskId)
            if not task:
                raise TYTaskException(-1, 'Not found task: %s' % (taskId))
            taskModel.unwear(task)
            mo = MedalTaskHelper.buildMedalUpdateResponse(gameId, userId, taskModel, timestamp)
            router.sendToUser(mo, userId)
        except TYTaskException, e:
            self.sendErrorResponse(userId, e.errorCode, e.message)
            
    @markCmdActionMethod(cmd='medal_info', action="getreward", clientIdVer=0, scope='game')
    def doMedalTaskGetReward(self, userId, gameId, taskId):
        try:
            timestamp = pktimestamp.getCurrentTimestamp()
            taskModel = dizhutask.medalTaskSystem.loadTaskModel(userId, timestamp)
            task = taskModel.userTaskUnit.findTask(taskId)
            if not task:
                raise TYTaskException(-1, 'Not found task: %s' % (taskId))
            dizhutask.medalTaskSystem.getTaskReward(task, timestamp, 'MEDAL2_REWARD', taskId)
            mo = MedalTaskHelper.buildMedalUpdateResponse(gameId, userId, taskModel, timestamp)
            router.sendToUser(mo, userId)
        except TYTaskException, e:
            self.sendErrorResponse(userId, e.errorCode, e.message)

class TableTaskHelper(object):
    @classmethod
    def buildTableTasks(cls, taskModel):
        tasks = []
        taskList = sorted(taskModel.userTaskUnit.taskList, key=lambda v:v.taskKind.taskKindPool.index)
        for task in taskList:
            ftlog.debug('TableTaskHelper.buildTableTasks userId=', taskModel.userId,
                        'taskId=', task.kindId,
                        'task=', task.__dict__)
            tasks.append({
                'id':task.kindId,
                'name':task.taskKind.name,
                'progress':task.progress,
                'total':task.taskKind.count,
                'state':1 if task.isFinished else 0,
                'reward':task.taskKind.rewardContent.desc if task.taskKind.rewardContent else '',
                'label': task.taskKind.taskKindPool.conf.get('taskLabel'),
                'rewardPic': task.taskKind.rewardPic
            })
            ftlog.debug('TableTaskHelper.buildTableTasks result tasklist | userId=', taskModel.userId, 'tasks=', tasks)
        return tasks

    @classmethod
    def buildTableTasksRewardMessage(cls, task):
        ftlog.debug("buildTableTasksRewardMessage task=", task)
        return task.taskKind.rewardContent.desc if task.taskKind.rewardContent else ''

    @classmethod
    def buildTableTaskGetRewardResponse(cls, gameId, userId, task, assetList, taskModel):
        mo = MsgPack()
        mo.setCmd('table_task')
        mo.setResult('gameId', gameId)
        mo.setResult('userId', userId)
        mo.setResult('action', 'taskList')
        rewards = {}
        if assetList :
            for assetKind, _, _ in assetList:
                if assetKind.kindId == dizhuasset.ASSET_MASTER_SCORE_KIND_ID:
                    scoreInfo = skillscore.score_info(userId)
                    rewards['skillScoreInfo'] = scoreInfo
        mo.setResult('rewards', rewards)

        if taskModel:
            mo.setResult('rewardMessage', cls.buildTableTasksRewardMessage(task)) # 奖励信息字符串
            mo.setResult('rewardPic', task.taskKind.rewardPic) # 奖励的图片 add by wuyangwei
            mo.setResult('tasks', cls.buildTableTasks(taskModel)) # 领取完毕后的任务列表

        return mo
    
    @classmethod
    def buildTableTaskListResponse(cls, gameId, userId, taskModel):
        mo = MsgPack()
        mo.setCmd('table_task')
        mo.setResult('gameId', gameId)
        mo.setResult('userId', userId)
        mo.setResult('action', 'taskList')
        mo.setResult('tasks', cls.buildTableTasks(taskModel))
        return mo

    @classmethod
    def buildTableGetTasksResponse(cls, gameId, userId, taskModel):
        mo = MsgPack()
        mo.setCmd('table_task')
        mo.setResult('gameId', gameId)
        mo.setResult('userId', userId)
        mo.setResult('action', 'getTasks')
        mo.setResult('tasks', cls.buildTableTasks(taskModel))
        return mo

@markCmdActionHandler
class TableTaskHandler(BaseMsgPackChecker):
    def _check_param_taskId(self, msg, key, params):
        paramId = msg.getParam(key)
        try:
            return None, int(paramId)
        except:
            return 'ERROR of id !' + str(paramId), None


    @markCmdActionMethod(cmd='table_task', action="getReward", clientIdVer=0, scope='game')
    def doTableTaskGetReward(self, userId, gameId, taskId):
        ftlog.debug('TableTaskHandler.doTableTaskGetReward userId=', userId, "taskId=", taskId)
        try:
            timestamp = pktimestamp.getCurrentTimestamp()
            taskModel = dizhutask.tableTaskSystem.loadTaskModel(userId, timestamp)
            task = taskModel.userTaskUnit.findTask(taskId)
            if not task:
                raise TYTaskException(-1, 'Not found task: %s' % (taskId))
            assetList = dizhutask.tableTaskSystem.getTaskReward(task, timestamp, 'TASK_REWARD', taskId)
            mo = TableTaskHelper.buildTableTaskGetRewardResponse(gameId, userId, task, assetList, taskModel)
            router.sendToUser(mo, userId)
            
            # mo = TableTaskHelper.buildTableTaskListResponse(gameId, userId, taskModel)
            # router.sendToUser(mo, userId)
        except TYTaskException, e:
            ftlog.warn('ERROR, doTableTaskGetReward userId=', userId, 'gameId=', gameId, 'taskId=', taskId, 'error=', e.errorCode, e.message)
            mo = TableTaskHelper.buildTableTaskGetRewardResponse(gameId, userId, taskId, None, None)
            mo.setError(e.errorCode, e.message)
            router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd='table_task', action="getTasks", clientIdVer=0, scope='game')
    def doTableTaskGetTasks(self, userId, gameId, taskId):
        ftlog.debug('TableTaskHandler.doTableTaskGetTasks userId=', userId)
        timestamp = pktimestamp.getCurrentTimestamp()
        taskModel = dizhutask.tableTaskSystem.loadTaskModel(userId, timestamp)
        for task in taskModel.userTaskUnit.taskList:
            if task.progress >= task.taskKind.count:
                changed, _finishCount = task.setProgress(task.taskKind.count, timestamp)
                if changed:
                    task.userTaskUnit.updateTask(task)
        mo = TableTaskHelper.buildTableGetTasksResponse(gameId, userId, taskModel)
        router.sendToUser(mo, userId)


@markCmdActionHandler
class SegmentTaskHandler(BaseMsgPackChecker):
    @markCmdActionMethod(cmd='dizhu', action="get_segment_task", clientIdVer=0,
                         scope='game')
    def doGetSegmentTask(self, userId, gameId):
        SegmentTaskHelper.send_get_task_response(gameId, userId)

    @markCmdActionMethod(cmd='dizhu', action="get_segment_task_award", clientIdVer=0,
                         scope='game')
    def doSegmentTaskReward(self, userId, gameId):
        msg = runcmd.getMsgPack()
        multi = msg.getParam("rewardMulti", 0)
        taskId = msg.getParam("taskId", 0)
        if not taskId:
            ftlog.warn("doSegmentTaskReward taskId err")
        SegmentTaskHelper.send_get_award_response(gameId, userId, taskId, multi)
