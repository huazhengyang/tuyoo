# -*- coding=utf-8 -*-
from poker.entity.biz.activity.activity import TYActivity
from hall.entity.todotask import TodoTaskEnterGame
from poker.util import strutil
from hall.entity.hallactivity.activity_type import TYActivityType

class TYActivityDdzMatch(TYActivity):
    TYPE_ID = TYActivityType.ACTIVITY_DDZ_MATCH  

    def getConfigForClient(self, gameId, userId, clientId):
        clientConf = strutil.cloneData(self._clientConf)
        jumpTodoTask = TodoTaskEnterGame("", "")
        enterParam = {}
        enterParam["type"] = "roomlist"
        enterParam["pluginParams"] = {}
        enterParam["pluginParams"]["gameType"] = 3
        
        jumpTodoTask.setParam('gameId', 6)
        jumpTodoTask.setParam('type', "roomlist")
        jumpTodoTask.setParam('enter_param', enterParam)
        clientConf["config"]["button"]["todoTask"] = jumpTodoTask.toDict()

        return clientConf
    
    
"""
{
    "action":"enter_game",
    "params":{
        gameId:6
        type:"quickstart",
        enter_param:{
            type:"quickstart",
            pluginParams:{
                roomId:
                sessionIndex:
            }
        }
    }
}
"""