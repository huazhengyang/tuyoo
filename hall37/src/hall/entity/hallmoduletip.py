# -*- coding=utf-8
'''
Created on 2015年7月30日

@author: zhaojiangang
'''
from sre_compile import isstring

import freetime.util.log as ftlog
from hall.entity import hallconf
from hall.game import TGHall
from poker.entity.biz.exceptions import TYBizConfException
import poker.entity.dao.gamedata as pkgamedata
from poker.entity.events.tyevent import EventConfigure, ModuleTipEvent
import poker.entity.events.tyeventbus as pkeventbus
from poker.protocol import router
from poker.util import strutil


class TipModule(object):
    def __init__(self):
        self.name = None
        self.type = None
        self.needReport = None
        self.hallType = None
        
    def decodeFromDict(self, d):
        self.name = d.get('name')
        if not isstring(self.name) or not self.name:
            raise TYBizConfException(d, 'TipModule.name must be not empty string')
        
        self.type = d.get('type', 0)
        if not isinstance(self.type, int):
            raise TYBizConfException(d, 'TipModule.type must be int')
        
        self.needReport = d.get('needReport', 1)
        if not isinstance(self.needReport, int):
            raise TYBizConfException(d, 'TipModule.needReport must be int')
    
        self.hallType = d.get('hallType')
        if not isstring(self.hallType) or not self.hallType:
            raise TYBizConfException(d, 'TipModule.hallType must be not empty string')
        
        return self
    
class UserTipModule(object):
    def __init__(self, tipModule, count):
        self.tipModule = tipModule
        self.count = count
        
_inited = False
_tipModuleMap = {}

def _reloadConf():
    global _tipModuleMap
    conf = hallconf.getModuleTipConf()
    tipModuleMap = {}
    for moduleConf in conf.get('modules', []):
        #{"name":"account", "type":0, "needReport":1, 'hallType':'common'},
        tipModule = TipModule().decodeFromDict(moduleConf)
        if tipModule.name in tipModuleMap:
            raise TYBizConfException(moduleConf, 'Duplicate tipModule %s' % (tipModule.name))
        tipModuleMap[tipModule.name] = tipModule
        
    _tipModuleMap = tipModuleMap
    ftlog.debug('hallmoduletip._reloadConf successed modules=', _tipModuleMap.keys())
    
def _onConfChanged(event):
    if _inited and event.isChanged('game:9999:moduletip:0'):
        ftlog.debug('hallmoduletip._onConfChanged')
        _reloadConf()

def _initialize():
    ftlog.debug('hallmoduletip initialize begin')
    global _inited
    if not _inited:
        _inited = True
        _reloadConf()
        pkeventbus.globalEventBus.subscribe(EventConfigure, _onConfChanged)
        pkeventbus.globalEventBus.subscribe(ModuleTipEvent, handleEvent)
        TGHall.getEventBus().subscribe(ModuleTipEvent, handleEvent)
    ftlog.debug('hallmoduletip initialize end')
    
'''
向客户端推送tip变更消息
不需要统计tip数的模块count始终等于1
'''
def handleEvent(event):
    if isinstance(event, ModuleTipEvent):
        setTipCount(event.userId, event.name, event.count, event.gameId)
        modules = [event.name]
        ftlog.debug('handleEvent module_tip modulename=', event.name, 'userId=', event.gameId, 'gameId=', event.gameId)
        modulesInfo = getInfo(event.userId, modules, event.gameId)
        from hall.servers.util.moduletip_handler import ModuletipTcpHandlerHelp
        mo = ModuletipTcpHandlerHelp.buildInfo('update', modulesInfo)
        router.sendToUser(mo, event.userId)
        

def sendModuleTipEvent(userId, gameId, moduleName, count):
    '''
    推送勋章状态变更事件
    @param count:当前用户未领取勋章数 
    '''

    tip = ModuleTipEvent(userId, gameId, moduleName, count)
    TGHall.getEventBus().publishEvent(tip)
    ftlog.debug('sendModuleTipEvent name=', moduleName,  'gameId=', gameId, 'userId=', userId, 'count=', count)

   
def _buildModuleTipKey(tipModule, gameId, userId):
    #if tipModule.hallType == 'common':
    return 'moduletip:%s' % (tipModule.name)
    #else:
    #    return '%s:moduletip:%s' % (gameId, tipModule.name)

def findTipModule(name):
    global _tipModuleMap
    ftlog.debug('findTipModule modules=', _tipModuleMap.keys(), name)
    return _tipModuleMap.get(name)

def setTipCount(userId, tipModuleName, count, gameId):
    tipModule = findTipModule(tipModuleName)
    if not tipModule:
        ftlog.error("not find tipModule:", tipModuleName)
        return
    pkgamedata.setGameAttr(userId, 9999, _buildModuleTipKey(tipModule, gameId, userId), count)

def getTipCount(userId, tipModule, gameId):
    count = pkgamedata.getGameAttrInt(userId, 9999, _buildModuleTipKey(tipModule, gameId, userId))
    return count

def resetTipCount(self, userId, modules, counts, subGameId):
    moduleInfo = []
    bds = zip(modules, counts)
    ftlog.debug('module_tip resetTipCount bds=', bds)
    for bd in bds:
        m = findTipModule(bd[0])
        if m and m.needReport:
            self.setTipCount(userId, bd[0], bd[1], subGameId)
            module = strutil.cloneData(m)
            module.count = bd[1]
            moduleInfo.append(module)
    return moduleInfo

def getInfo(userId, modules, subGameId):
    '''
    获取模块tip信息
    '''
    if modules:
        return getModulesInfo(userId, modules, subGameId)
    else:
        return getAllModulesInfo(userId, subGameId)
    
def getModulesInfo(userId, modules, subGameId):
    '''
    获取模块tip信息
    @param userId: 用户Id
    @param modules: 模块信息
    @return: list<ModuleTip> 
    '''
    moduleInfo = []
    for name in modules:
        m = findTipModule(name)
        if m:
            module = strutil.cloneData(m)
            module.count = getTipCount(userId, module, subGameId)
            moduleInfo.append(module)
    return moduleInfo

def getAllModulesInfo(userId, subGameId):
    '''
    获取所有模块tip信息
    '''
    global _tipModuleMap
    moduleInfo = []
    for _key, value in _tipModuleMap.iteritems():
        module = strutil.cloneData(value)
        module.count = getTipCount(userId, module, subGameId)
        moduleInfo.append(module)
    return moduleInfo

def cancelModulesTip(userId, modules, subGameId):
    '''
    将模块tip信息置为0
    @param userId: 用户Id
    @param modules: 模块信息
    @return: list<ModuleTip> 
    '''
    moduleInfo = []
    for moduleName in modules:
        m = findTipModule(moduleName)
        if m and m.needReport:
            setTipCount(userId, m.name, 0, subGameId)
            module = strutil.cloneData(m)
            module.count = 0
            moduleInfo.append(module)
    return moduleInfo


def cancelModulesTipFromSystem(userId, modules, subGameId):
    '''
    将模块tip信息置为0
    @param userId: 用户Id
    @param modules: 模块信息
    @return: list<ModuleTip>
    '''
    moduleInfo = []
    for moduleName in modules:
        m = findTipModule(moduleName)
        if m :
            setTipCount(userId, m.name, 0, subGameId)
            module = strutil.cloneData(m)
            module.count = 0
            moduleInfo.append(module)
    from hall.servers.util.moduletip_handler import ModuletipTcpHandlerHelp
    mo = ModuletipTcpHandlerHelp.buildInfo('report', moduleInfo)
    router.sendToUser(mo, userId)

