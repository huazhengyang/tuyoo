# -*- coding=utf-8
'''
Created on 2015年9月18日
重构menulist，改为使用模板
@author: zhaol
'''

import freetime.util.log as ftlog
from hall.entity import hallconf
from poker.entity.events.tyevent import EventConfigure
import poker.entity.events.tyeventbus as pkeventbus
from hall.entity.todotask import TodoTaskRegister, TodoTaskHelper

# menulist的模板特别简单
# 直接就是模板内容
# 全局变量    
# map<templateName,  TYMenuListTemplate>           
_menuTemplateMap = {}
_menuCustomMap = {}
_inited = False

def _reloadConf():
    global _menuTemplateMap
    global _menuCustomMap
    
    # 0.json配置
    conf = hallconf.getMenuListDefaultConf()
    
    _menuTemplateMap = {}
    _menuCustomMap = {}
    
    for name, templateDict in conf.get('templates', {}).iteritems():
        _menuTemplateMap[name] = templateDict
        
    _menuCustomMap = conf.get('custom_menus', {})
    
    ftlog.debug('hall.menulist._reloadConf successed templateNames=', _menuTemplateMap.keys(), ' custom menus=', _menuCustomMap)
    
def _onConfChanged(event):
    if _inited and event.isModuleChanged(['menulist']):
        ftlog.debug('hall.menulist._onConfChanged')
        _reloadConf()
        
def _initialize():
    ftlog.debug('hall.menulist._initialize begin')
    global vipSystem
    global userVipSystem
    global _inited
    if not _inited:
        _inited = True
        _reloadConf()
        pkeventbus.globalEventBus.subscribe(EventConfigure, _onConfChanged)
    ftlog.debug('hall.menulist._initialize end')
    
def getClientMenuList(clientId):
    '''
    @return: TYMenuListTemplate
    '''
    templateName = hallconf.getMenuListClientConf(clientId)
    ftlog.debug('hall.menulist.queryMenuList clientId=', clientId,
                'templateName=', templateName)
    return _menuTemplateMap.get(templateName)

def getClientCustomMenuSetting(gameId, userId, clientId, menus):
    ''' 获取自定义菜单设置
    '''
    settings = {}
    
    for menu in menus:
        if menu in _menuCustomMap:
            ms = {}
            # 图片
            ms['picUrl'] = _menuCustomMap[menu].get('picUrl', '')
            # 行为
            todotasks = []
            for todotaskDict in _menuCustomMap[menu].get('todotasks', []):
                todotask = TodoTaskRegister.decodeFromDict(todotaskDict)
                todotasks.append(todotask)
                
            todotasks = TodoTaskHelper.makeTodoTasksByFactory(gameId, userId, clientId, todotasks)
            ms['tasks'] = TodoTaskHelper.encodeTodoTasks(todotasks)
            
            settings[menu] = ms
            
    if ftlog.is_debug():
        ftlog.debug('hallmenulist.getClientCustomMenuSetting settings=', settings)
        
    return settings
    