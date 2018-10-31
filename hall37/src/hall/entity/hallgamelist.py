# -*- coding=utf-8
'''
Created on 2015年7月30日

@author: zhaojiangang
'''
import freetime.util.log as ftlog
from hall.entity import hallconf
from poker.entity.events.tyevent import EventConfigure
import poker.entity.events.tyeventbus as pkeventbus
from poker.entity.biz.exceptions import TYBizConfException

_inited = False
# key=name, value=pages
_templateMap = {}

def _reloadConf():
    global _templateMap
    conf = hallconf.getGameListConf()
    templateMap = {}
    templateDict = conf.get('templates', {})
    nodeDict = conf.get('nodes', {})
    for name, pages in templateDict.iteritems():
        fullPages = []
        for page in pages:
            nodes = []
            for nodeName in page.get('nodes', []):
                node = nodeDict.get(nodeName)
                if not node:
                    raise TYBizConfException(page, 'Not found node name %s' % (nodeName))
                nodes.append(node)
            fullPage = {}
            fullPage.update(page)
            fullPage['nodes'] = nodes
            fullPages.append(fullPage)
        templateMap[name] = fullPages
    _templateMap = templateMap
    ftlog.debug('hallgamelist._reloadConf successed templateNames=', _templateMap.keys())
    
def _onConfChanged(event):
    if _inited and event.isChanged('game:9999:gamelist:0'):
        ftlog.debug('hallgamelist._onConfChanged')
        _reloadConf()
        
def _initialize():
    ftlog.debug('hallgamelist initialize begin')
    global _inited
    if not _inited:
        _inited = True
        _reloadConf()
        pkeventbus.globalEventBus.subscribe(EventConfigure, _onConfChanged)
    ftlog.debug('hallgamelist initialize end')
    
def getGameList(gameId, userId, clientId):
    '''
    获取大厅游戏按钮列表
    @param clientId
    @return: list<page>
    '''
    templateName = hallconf.getGameListTemplateName(clientId)
    if ftlog.is_debug():
        ftlog.debug('hallgamelist.getGameList gameId=', gameId,
                    'userId=', userId,
                    'clientId=', clientId,
                    'templateName=', templateName)
    return _templateMap.get(templateName, [])


    