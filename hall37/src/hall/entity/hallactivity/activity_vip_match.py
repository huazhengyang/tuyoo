# -*- coding=utf-8 -*-

from poker.entity.biz.activity.activity import TYActivity
from hall.entity.todotask import TodoTaskEnterGameNewFactory, TodoTaskPayOrderFactory
import freetime.util.log as ftlog
from poker.util import strutil
from hall.entity.hallactivity.activity_type import TYActivityType

class TYActivityVipMatch(TYActivity):
    TYPE_ID = TYActivityType.ACTIVITY_VIP_MATCH

    def getConfigForClient(self, gameId, userId, clientId):
        try:
            clientConf = strutil.cloneData(self._clientConf)
            
            todoTaskDict = clientConf["config"]["firstButton"]
            todoTaskFactory = TodoTaskEnterGameNewFactory()
            todoTaskFactory.decodeFromDict(todoTaskDict)
            todoTask = todoTaskFactory.newTodoTask(0, 0, 0) 
            clientConf["config"]["firstButton"] =  todoTask.toDict()   
            clientConf["config"]["firstButton"]["visible"] = 1
            
            payOrder = clientConf["config"]["secondButton"]
            payOrderFac = TodoTaskPayOrderFactory()
            payOrderFac.decodeFromDict({"payOrder":payOrder})
            todoTaskPay = payOrderFac.newTodoTask(gameId, userId, clientId)
            if todoTaskPay:
                clientConf["config"]["secondButton"] =  todoTaskPay.toDict()   
                clientConf["config"]["secondButton"]["visible"] = 1
            else:
                return None
        except:
            ftlog.exception("getConfigForClient error, can not set todotask, clientId:", clientId)
            return None
        return clientConf
    
    
