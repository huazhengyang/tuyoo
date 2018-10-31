# -*- coding=utf-8
'''
Created on 2016年12月23日

@author: zhaol
'''
import freetime.util.log as ftlog
from hall.entity import hallconf
from poker.entity.events.tyevent import EventConfigure
import poker.entity.events.tyeventbus as pkeventbus
from hall.entity.todotask import TodoTaskHelper, TodoTaskRegister


DEFAULT_INTERVAL = 5

class TYFangKaBuyInfoTemplate(object):
    def __init__(self):
        self.name = ''
        self.todotasks = []

    def decodeFromDict(self, d ):
        self.name = d.get('name', '')
        self.todotasks = d.get('todotasks', [])
        return self
    
_fbTemplateMap = {}
_inited = False

def _reloadConf():
    global _fbTemplateMap
    conf = hallconf.getFangKaBuyConf()
    
    _fbTemplateMap = {}
    for templateDict in conf.get('templates', []):
        template = TYFangKaBuyInfoTemplate().decodeFromDict(templateDict)
        _fbTemplateMap[template.name] = template
    
    ftlog.debug('hall_fangka_buy_info._reloadConf successed templateNames=', _fbTemplateMap.keys())
    
def _onConfChanged(event):
    if _inited and event.isModuleChanged('fangka_buy_info'):
        ftlog.debug('hall_fangka_buy_info._onConfChanged')
        _reloadConf()

def _initialize():
    ftlog.debug('hall_fangka_buy_info._initialize begin')
    global vipSystem
    global userVipSystem
    global _inited
    if not _inited:
        _inited = True
        _reloadConf()
        pkeventbus.globalEventBus.subscribe(EventConfigure, _onConfChanged)
    ftlog.debug('hall_fangka_buy_info._initialize end')
    
def queryFangKaBuyInfo(gameId, userId, clientId):
    templateName = hallconf.getFangKaBuyInfoCliengConf(clientId)
    if templateName:
        ret = _fbTemplateMap.get(templateName, None)
        if not ret:
            return
        
        # 执行todotask
        ftlog.debug('hall_fangka_buy_info.queryFangKaBuyInfo gameId=', gameId,
                    'userId=', userId,
                    'clientId=', clientId,
                    'templateName=', templateName,
                    'tasks=', ret.todotasks)
        todotasks = TodoTaskRegister.decodeList(ret.todotasks)
        tasks = TodoTaskHelper.makeTodoTasksByFactory(gameId, userId, clientId, todotasks)
        TodoTaskHelper.sendTodoTask(gameId, userId, tasks)