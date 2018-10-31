# -*- coding=utf-8 -*-
'''
Created on 16-12-14

@author: luwei

@desc: 活动
'''
from __future__ import division

import copy

from dizhu.activities.toolbox import Tool
from dizhu.activitynew import activitysystemnew
from dizhu.activitynew.quweitask import ErrorCode
from dizhu.entity.dizhuconf import DIZHU_GAMEID
import freetime.util.log as ftlog
from hall.entity import hallstore
from hall.entity.todotask import TodoTaskLessBuyOrder, \
    TodoTaskHelper, TodoTaskPopTip
from poker.entity.biz.activity.activity import TYActivity
from poker.entity.biz.exceptions import TYBizException
from poker.entity.dao import sessiondata
from poker.protocol import router
from poker.util import strutil
import poker.util.timestamp as pktimestamp

class QuweiTaskProxy(object):
    @classmethod
    def sendPopTip(cls, userId, text):
        todotask = TodoTaskPopTip(text)
        mo = TodoTaskHelper.makeTodoTaskMsg(DIZHU_GAMEID, userId, todotask)
        router.sendToUser(mo, userId)

    @classmethod
    def getTaskContext(cls, userId, backendActivityNewActId):
        '''
        获得趣味任务上下文
        '''
        actobj = activitysystemnew.findActivity(backendActivityNewActId)
        if ftlog.is_debug():
            ftlog.debug('QuweiTaskProxy.getTaskContext',
                        'userId=', userId,
                        'backendActivityNewActId=', backendActivityNewActId,
                        'actobj=', actobj)
        taskStatus = actobj.loadStatus(userId, pktimestamp.getCurrentTimestamp())
        return taskStatus

    @classmethod
    def resetTaskListProgress(cls, userId, backendActivityNewActId):
        '''
        重置任务
        '''
        actobj = activitysystemnew.findActivity(backendActivityNewActId)
        if ftlog.is_debug():
            ftlog.debug('QuweiTaskProxy.getTaskContext',
                        'userId=', userId,
                        'backendActivityNewActId=', backendActivityNewActId,
                        'actobj=', actobj)
        taskStatus = actobj.loadStatus(userId, pktimestamp.getCurrentTimestamp())
        try:
            actobj.refresh(taskStatus, pktimestamp.getCurrentTimestamp())
        except TYBizException, ex:
            return ex.errorCode
        return 0

    @classmethod
    def gainTaskPrize(cls, userId, backendActivityNewActId, allOpenflag):
        '''
        领取任务奖励
        '''
        actobj = activitysystemnew.findActivity(backendActivityNewActId)
        if ftlog.is_debug():
            ftlog.debug('QuweiTaskProxy.getTaskContext',
                        'userId=', userId,
                        'backendActivityNewActId=', backendActivityNewActId,
                        'actobj=', actobj)
        taskStatus = actobj.loadStatus(userId, pktimestamp.getCurrentTimestamp())
        try:
            curtask = cls.getCompletedTask(taskStatus) if allOpenflag else cls.getCurrentTask(taskStatus)
            actobj.gainReward(taskStatus, curtask.kindId, pktimestamp.getCurrentTimestamp())
        except TYBizException, ex:
            cls.sendPopTip(userId, ex.message)

    @classmethod
    def getCompletedTask(cls, taskContext):
        '''
        获得当前已完成的任务的index(从0开始) 
        @return: 若未找到则返回None
        '''
        CompletedTask = None
        for task in taskContext.tasks:
            if task.progress >= task.taskKind.count and not task.gotReward:
                CompletedTask = task
        return CompletedTask
    
    @classmethod
    def getCurrentTask(cls, taskContext):
        '''
        获得当前运行的任务的index(从0开始) 
        @return: 若未找到则返回-1
        '''
        lastOpenTask = None
        for task in taskContext.tasks:
            if task.open:
                lastOpenTask = task
        return lastOpenTask

    @classmethod
    def getCurrentTaskIndex(cls, taskContext):
        '''
        获得当前运行的任务的index(从0开始) 
        @return: 若未找到则返回-1
        '''
        lastOpenKindId = -1 
        for task in taskContext.tasks:
            if task.open:
                lastOpenKindId = task.kindId
        return taskContext.indexOf(lastOpenKindId)
    
    @classmethod
    def getTaskBtnState(cls, taskContext, task, allOpenflag):
        '''
        获取对应任务的按钮状态
        btnState: get(领取奖励), goto(去完成), lock(未激活), done(已领取)
        '''
        if allOpenflag:
            if task.progress < task.taskKind.count:
                return 'goto'
            else:
                return 'done' if task.gotReward else 'get'
        
        curindex = cls.getCurrentTaskIndex(taskContext)
        index = taskContext.indexOf(task.kindId)
        if index < curindex:
            return 'done'
        elif index == curindex:
            if task.progress < task.taskKind.count:
                return 'goto'
            else:
                return 'done' if task.gotReward else 'get'
        elif index > curindex:
            return 'lock'
    
    @classmethod
    def getTaskInfo(cls, taskContext, allOpenflag):
        '''
        获得任务列表信息
        '''
        taskinfo = []
        for task in taskContext.tasks:
            clientId = sessiondata.getClientId(task.userId)
            todotask = None
            if task.taskKind.todotaskFac:
                todotask = task.taskKind.todotaskFac.newTodoTask(DIZHU_GAMEID, task.userId, clientId).toDict() 
            item = {
                'icon': task.taskKind.pic,
                'name': task.taskKind.name,
                'desc': task.taskKind.desc,
                'curProgress': task.progress,
                'totalProgress': task.taskKind.count,
                'btnState': cls.getTaskBtnState(taskContext, task, allOpenflag),
                'todotask': todotask,
            }
            taskinfo.append(item)
        return taskinfo
    
class FunAct(TYActivity):
    '''
    牌局重放排行榜活动
    '''
    TYPE_ID = 6014
    ACTION_RESET = 'ddz.act.funact.reset'
    ACTION_GETPRIZE = 'ddz.act.funact.getprize' 

    def __init__(self, dao, clientConfig, serverConfig):
        super(self.__class__, self).__init__(dao, clientConfig, serverConfig)
        ftlog.debug('FunAct.__init__')

    def buildActivityInfo(self, userId):
        if ftlog.is_debug():
            ftlog.debug('FunAct.buildActivityInfo',
                        'userId=', userId)
        clientconf = copy.deepcopy(self._clientConf)
        backendActivityNewActId = clientconf['config']['server']['backendActivityNewActId']
        
        # 测试专用
        debug_reset = clientconf['config']['client'].get('debug.reset', False)
        
        taskContext = QuweiTaskProxy.getTaskContext(userId, backendActivityNewActId)
        currentTaskIndex = QuweiTaskProxy.getCurrentTaskIndex(taskContext)
        
        # 是否允许用户重置任务
        clientconf['config']['client']['buttonReset']['enabled'] = (currentTaskIndex >= (len(taskContext.tasks) - 1) ) or debug_reset
        # 构建任务列表数据
        allOpenflag = clientconf.get('all_open', 0)
        if allOpenflag:
            for task in taskContext.tasks:
                task.open = 1
        
        clientconf['config']['client']['tasks'] = QuweiTaskProxy.getTaskInfo(taskContext, allOpenflag)
        
        if ftlog.is_debug():
            ftlog.debug('FunAct.buildActivityInfo',
                        'userId=', userId,
                        'clientconf=', clientconf)
        return clientconf
    
    def getConfigForClient(self, gameId, userId, clientId):
        if ftlog.is_debug():
            ftlog.debug('FunAct.getConfigForClient:',
                'userId=', userId, 
                'gameId=', gameId,  
                'clientId', clientId, 
                'serverconf=', self._serverConf, 
                'clientconf=', self._clientConf)
        return self.buildActivityInfo(userId)

    def handleRequest(self, msg):
        userId = msg.getParam('userId')
        action = msg.getParam("action")
        if ftlog.is_debug():
            ftlog.debug('FunAct.handleRequest',
                        'userId=', userId,
                        'action=', action)

        if self.ACTION_RESET == action:
            return self.onActionReset(userId)
        elif self.ACTION_GETPRIZE == action:
            return self.onActionGetPrize(userId)
        return self.buildActivityInfo(userId)
    
    def recommendProductIfCan(self, gameId, userId):
        # 没有配置推荐商品，则不推荐
        payOrder = Tool.dictGet(self._clientConf, 'config.server.payOrder')
        if not payOrder:
            return False
        
        clientId = sessiondata.getClientId(userId)
        product, _ = hallstore.findProductByPayOrder(gameId, userId, clientId, payOrder)
        ftlog.debug('FunAct.recommendProductIfCan:',
                    'userId=', userId,
                    'product=', product)
        # 没有在货架中找到商品
        if not product:
            return False
        
        translateMap = {
            'product.displayName': product.displayName,
            'product.price': product.price,
            'count': payOrder.get('contains',{}).get('count',0)
        }
        desc = Tool.dictGet(self._clientConf, 'config.server.lessBuyChipDesc')
        note = Tool.dictGet(self._clientConf, 'config.server.lessBuyChipNote')
        desc = strutil.replaceParams(desc, translateMap)
        note = strutil.replaceParams(note, translateMap)
        todotask = TodoTaskLessBuyOrder(desc, None, note, product)
        TodoTaskHelper.sendTodoTask(gameId, userId, todotask)
        return True
    
    def onActionReset(self, userId):
        backendActivityNewActId = self._clientConf['config']['server']['backendActivityNewActId']
        errcode = QuweiTaskProxy.resetTaskListProgress(userId, backendActivityNewActId)
        # 重置费用不足
        if errcode == ErrorCode.REFRESH_FEE_NOT_ENOUGH:
            self.recommendProductIfCan(DIZHU_GAMEID, userId)
        return self.buildActivityInfo(userId)
    
    def onActionGetPrize(self, userId):
        backendActivityNewActId = self._clientConf['config']['server']['backendActivityNewActId']
        allOpenflag = self._clientConf.get('all_open', 0)
        QuweiTaskProxy.gainTaskPrize(userId, backendActivityNewActId, allOpenflag)
        return self.buildActivityInfo(userId)

def initialize():
    ftlog.info('funact.initialize ... ok')
    
