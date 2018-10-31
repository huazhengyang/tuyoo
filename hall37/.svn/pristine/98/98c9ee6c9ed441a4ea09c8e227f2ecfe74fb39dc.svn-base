# -*- coding=utf-8
'''
Created on 2016年1月11日
@keyword 默认配置
@note: 按照游戏+主版本号配置
版本号精确到小数点后2位，不足者补0
只读取该版本的默认配置，不负责校验有效性
本配置与具体的模板配置是解耦的，无直接关系
如果有，则返回，返回后需校验有效性
如果无，则返回None
@author: zhaol
'''

import freetime.util.log as ftlog
from poker.entity.configure import configure
from poker.entity.events.tyevent import EventConfigure
import poker.entity.events.tyeventbus as pkeventbus
from poker.util import strutil

HALL_GAMEID = 9999

# 默认配置的模板特别简单
# 只有一个文件0.json

_defaultTemplateMap = {}
_inited = False

def _reloadConf():
    global _defaultTemplateMap
    # 0.json配置
    _defaultTemplateMap = configure.getGameJson(HALL_GAMEID, 'module_default')
    ftlog.debug('hall.module_default._reloadConf successed : ', _defaultTemplateMap)
    
def _onConfChanged(event):
    if _inited and event.isChanged('game:9999:module_default:0'):
        ftlog.debug('hall.module_default._onConfChanged')
        _reloadConf()
        
def _initialize():
    ftlog.debug('hall.module_default._initialize begin')
    global _inited
    if not _inited:
        _inited = True
        _reloadConf()
        pkeventbus.globalEventBus.subscribe(EventConfigure, _onConfChanged)
    ftlog.debug('hall.module_default._initialize end')
    
def getClientModuleDefaultConf(clientId, moduleName):
    '''
    @return: 默认配置 如果没有 返回None
    '''
    
    # 提取版本号 提取游戏ID
    clientOS, ver, info = strutil.parseClientId(clientId)
    ftlog.debug('getClientModuleDefaultConf clientOS:', clientOS, ' ver:', ver, ' info:', info)
    gameId = strutil.getGameIdFromHallClientId(clientId)
    tName = 'hall' + str(gameId) + '_' + str("%.2f" % ver)
    ftlog.debug('getClientModuleDefaultConf tName:', tName)
    
    if tName in _defaultTemplateMap:
        tConf = _defaultTemplateMap[tName]
        if moduleName in tConf:
            # 格式化返回数据
            conf = {}
            conf['template'] = tConf[moduleName]
            return conf
        else:
            ftlog.debug('No default module, module:', moduleName)
    else:
        ftlog.debug('No default module config, clientId:', clientId)
    return None