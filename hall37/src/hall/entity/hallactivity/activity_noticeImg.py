# -*- coding=utf-8 -*-
from poker.entity.biz.activity.activity import TYActivity
import freetime.util.log as ftlog
from hall.entity import  hallpopwnd
from poker.util import strutil
from hall.entity.hallactivity.activity_type import TYActivityType

class TYActivityNoticeImg(TYActivity):
    TYPE_ID = TYActivityType.ACTIVITY_NOTICE_IMG

    def getConfigForClient(self, gameId, userId, clientId):
        clientConf = strutil.cloneData(self._clientConf)
        if clientConf["config"]["firstButton"]["visible"] :
            '''
                处理第1个按钮的todotask
            '''
            todoTask = clientConf["config"]["firstButton"]
            todoTaskObj = hallpopwnd.decodeTodotaskFactoryByDict(todoTask).newTodoTask(gameId, userId, clientId)
            clientConf["config"]["firstButton"] = todoTaskObj.toDict()
            clientConf["config"]["firstButton"]["visible"] = 1
        else :
            pass
        
        if clientConf["config"]["secondButton"]["visible"] :
            '''
                处理第2个按钮的todotask
            '''
            todoTask = clientConf["config"]["secondButton"]
            todoTaskObj = hallpopwnd.decodeTodotaskFactoryByDict(todoTask).newTodoTask(gameId, userId, clientId)
            clientConf["config"]["secondButton"] = todoTaskObj.toDict()
            clientConf["config"]["secondButton"]["visible"] = 1
        else :
            pass
        ftlog.debug("the noticeImg client config : " ,clientConf)
        return clientConf
