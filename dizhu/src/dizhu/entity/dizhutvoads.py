# -*- coding=utf-8
'''
Created on 2016-8-4

@author: wanghaiping

'''

from dizhu.entity import dizhuconf
import freetime.util.log as ftlog
from hall.entity import hallpopwnd
from hall.entity.todotask import TodoTaskHelper

def getAds(gameId, userId, clientId):
    res = []
    
    alldatas = dizhuconf.getTvoAds()
    try:
        for ad in alldatas:
            item = maekItem(ad, gameId, userId, clientId)
            res.append(item)
    except:
        ftlog.debug('handle ads item error')
        ftlog.exception()
        
    return res

def maekItem(ad, gameId, userId, clientId):
    item = {}
    item['todotasks'] = []
    
    for key in ad:
        if key != 'todotasks':
            item[key] = ad[key]
            
        # make the todotask
        todostasks = []
        for task in ad.get('todotasks', []):
            taskFactory = hallpopwnd.decodeTodotaskFactoryByDict(task)
            dstTask = taskFactory.newTodoTask(gameId, userId, clientId)
            todostasks.append(dstTask)
            
        item['todotasks'] = TodoTaskHelper.encodeTodoTasks(todostasks)
        
    return item

            
            
    