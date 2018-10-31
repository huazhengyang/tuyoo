# -*- coding=utf-8 -*-
from poker.entity.biz.activity.activity import TYActivity
from hall.entity import  hallpopwnd
from hall.entity.todotask import TodoTaskGotoShopFactory
from hall.entity.hallactivity.activity_type import TYActivityType
from poker.util import strutil

class TYActivityRaffle(TYActivity):
    TYPE_ID = TYActivityType.ACTIVITY_RAFFLE 

    def getConfigForClient(self, gameId, userId, clientId):
        '''
            用来对所有的general_btn对应的活动中的按钮
            进行统一管理
        '''
        clientConf = strutil.cloneData(self._clientConf)
        button = clientConf["config"]["button"]
        if button["visible"]:
            #true
            todoTaskDict = button["todoTask"]
            if todoTaskDict:
                todoTaskObj = hallpopwnd.decodeTodotaskFactoryByDict(todoTaskDict).newTodoTask(gameId, userId, clientId)
                if not todoTaskObj:
                    gotoShopDict = {"typeId": TodoTaskGotoShopFactory.TYPE_ID, "subStore": "coin"}
                    todoTaskObj = hallpopwnd.decodeTodotaskFactoryByDict(gotoShopDict).newTodoTask(gameId, userId, clientId)
                    
                clientConf["config"]["button"]["todoTask"] = todoTaskObj.toDict()
                
            return clientConf
        else:
            #false
            pass
    
    
