# -*- coding:utf-8 -*-
'''
Created on 2016年4月1日

@author: zhaojiangang
'''
from sre_compile import isstring

import freetime.util.log as ftlog
from hall.entity import datachangenotify
from hall.entity.hallactivity.activity_send_reward import ActivitySendReward
from hall.entity.todotask import TodoTaskDownloadApkPromote, TodoTaskGoldRain, \
    TodoTaskHelper, TodoTaskFactory, TodoTask, TodoTaskRegister
from poker.entity.biz.exceptions import TYBizConfException
from poker.entity.dao import gamedata, userchip, daoconst


class TodoTaskGeneralFactory(TodoTaskFactory):
    TYPE_ID = 'todotask.general'
    def __init__(self):
        super(TodoTaskGeneralFactory, self).__init__()
        self.action = None
        self.params = None
        self.actions = None
        
    def decodeFromDict(self, d):
        self.action = d.get('action')
        if not isstring(self.action) or not self.action:
            raise TYBizConfException(d, 'TodoTaskGeneralFactory.action must be string')
        self.params = d.get('params', {})
        self.actions = d.get('actions', [])
        return self
        
    def newTodoTask(self, gameId, userId, clientId, **kwargs):
        from hall.entity import hallpopwnd
        ret = TodoTask(self.action)
        if self.params:
            for k, v in self.params.iteritems():
                ret.setParam(k, v)
        if self.actions:
            for action in self.actions:
                name = action.get('name')
                fac = hallpopwnd.decodeTodotaskFactoryByDict(action.get('action'))
                todotask = fac.newTodoTask(gameId, userId, clientId, **kwargs)
                ret.setParam(name, todotask)
        return ret
    
@classmethod
def doSendReward(cls, gameId, userId, clientId, activityId):
    todotasks = [TodoTaskDownloadApkPromote('http://apk.dl.tuyoo.com/down/hszz/Clash_Royale.apk')]
    if gamedata.setnxGameAttr(userId, gameId, 'act.sendReward:%s' % (activityId), 1) == 1:
        # 发1完金币
        userchip.incrChip(userId, gameId, cls.REWARD_CHIP_COUNT,
                          daoconst.CHIP_NOT_ENOUGH_OP_MODE_NONE,
                          'ACTIVITY_REWARD',
                          20000,
                          clientId)
        datachangenotify.sendDataChangeNotify(gameId, userId, ['chip'])
        todotasks.append(TodoTaskGoldRain('恭喜您获得1万金币'))
        ftlog.info('ActivitySendReward.doSendReward gameId=', gameId,
                   'userId=', userId,
                   'clientId=', clientId,
                   'activityId=', activityId,
                   'rewardChip=', cls.REWARD_CHIP_COUNT)
    TodoTaskHelper.sendTodoTask(gameId, userId, todotasks)
    
ActivitySendReward.doSendReward = doSendReward
TodoTaskRegister.registerClass(TodoTaskGeneralFactory.TYPE_ID, TodoTaskGeneralFactory)

