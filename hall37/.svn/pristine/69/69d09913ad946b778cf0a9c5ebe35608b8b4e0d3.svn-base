# -*- coding=utf-8
'''
Created on 2015年8月3日

@author: zhaojiangang
'''

from sre_compile import isstring

import freetime.util.log as ftlog
from hall.entity import hallconf
from poker.entity.biz.confobj import TYConfable, TYConfableRegister
from poker.entity.biz.exceptions import TYBizConfException
from poker.entity.events.tyevent import EventConfigure
import poker.entity.events.tyeventbus as pkeventbus
from hall.entity.todotask import TodoTaskRegister, TodoTaskHelper
from hall.entity.hallusercond import UserConditionRegister
import poker.util.timestamp as pktimestamp

class HallGameVersion(object):
    def __init__(self, game):
        self.game = game
        self.conf = None
        self.ver = None
        
    def decodeFromDict(self, d):
        self.conf = d
        self.ver = d.get('ver')
        return self
    
class HallGame(object):
    def __init__(self):
        self.gameId = None
        self.gameMark = None
        self.description = None
        self.versionMap = None
    
    def findVersion(self, ver):
        return self.versionMap.get(ver)
    
    def decodeFromDict(self, d):
        self.gameId = d.get('gameId')
        if not isinstance(self.gameId, int):
            raise TYBizConfException(d, 'HallGame.gameId must be int')
        self.gameMark = d.get('gameMark')
        if not isstring(self.gameMark) or not self.gameMark:
            raise TYBizConfException(d, 'HallGame.gameMark must be string') 
        self.description = d.get('description', list)
        if not isinstance(self.description, list):
            raise TYBizConfException(d, 'HallGame.description must be list')
        self.versionMap = {}
        for versionDict in d.get('versions'):
            version = HallGameVersion(self).decodeFromDict(versionDict)
            if version.ver in self.versionMap:
                raise TYBizConfException(d, 'Duplicate ver %s' % (version.ver))
            self.versionMap[version.ver] = version
        return self
            
class HallGameNode(TYConfable):
    EMPTY_VERSIONS = set()
    def __init__(self):
        super(HallGameNode, self).__init__()
        self.conf = None
        self.type = None
        
    def getVersions(self):
        return self.EMPTY_VERSIONS
    
    def decodeFromDict(self, d):
        self.conf = d
        self.type = d.get('type')
        if not isstring(self.type):
            raise TYBizConfException(d, 'HallGameNode.type must be string')
        self._decodeFromDictImpl(d)
        return self
    
    def initWhenLoaded(self, gameMap):
        pass
    
    def buildToDict(self, gameId, userId, clientId):
        d = {'type':self.type}
        self._buildToDictImpl(gameId, userId, clientId, d)
        return d
    
    def _decodeFromDictImpl(self, d):
        pass
    
    def _buildToDictImpl(self, gameId, userId, clientId, d):
        raise NotImplemented()
    
    def isSuitable(self, gameId, userId, clientId):
        raise NotImplemented()
    
    def getGameIds(self):
        raise NotImplemented()
    
class HallGameNodePackage(HallGameNode):
    TYPE_ID = 'hall.gamenode.package'
    def __init__(self):
        super(HallGameNodePackage, self).__init__()
        self.nodes = None
        self.params = None
        self.conditions = None
        
    def getVersions(self):
        versions = set()
        for node in self.nodes:
            versions.update(node.getVersions())
        return versions
    
    def initWhenLoaded(self, gameMap):
        for node in self.nodes:
            node.initWhenLoaded(gameMap)
    
    def _buildToDictImpl(self, gameId, userId, clientId, d):
        d['nodes'] = []
        for node in self.nodes:
            if node.isSuitable(gameId, userId, clientId):
                nodeDict = node.buildToDict(gameId, userId, clientId)
                d['nodes'].append(nodeDict)
                
        d['params'] = self.params
    
    def _decodeFromDictImpl(self, d):
        self.params = d.get('params', {})
        
        self.nodes = []
        for nodeDict in d.get('nodes', []):
            node = HallGameNodeRegister.decodeFromDict(nodeDict)
            self.nodes.append(node)
            
        self.conditions = UserConditionRegister.decodeList(d.get('conditions', []))
        
    def isSuitable(self, gameId, userId, clientId):
        return checkConditions(gameId, userId, clientId, self.conditions)
    
    def getGameIds(self):
        re = []
        for node in self.nodes:
            re.extend(node.getGameIds())
        return re
   
class HallGameNodeInnerGame(HallGameNode):
    TYPE_ID = 'hall.gamenode.inner.game'
    def __init__(self):
        super(HallGameNodeInnerGame, self).__init__()
        self.params = None
        self.version = None
        self.type = None
        self.conditions = None

    def getVersions(self):
        return set([self.version])
    
    def initWhenLoaded(self, gameMap):
        gameId = self.params.get('gameId')
#         print 'hall.gamenode.inner.game', gameId
        ver = self.params.get('version')
#         print 'hall.gamenode.inner.game', ver
        game = gameMap.get(gameId)
#         print 'hall.gamenode.inner.game', game
        if not game:
            raise TYBizConfException(self.conf, 'Unknown gameId %s' % (gameId))
        version = game.findVersion(ver)
        if not version:
            raise TYBizConfException(self.conf, 'Unknown ver %s for gameId %s' % (ver, gameId))
        self.version = version
    
    def _decodeFromDictImpl(self, d):
        self.type = d.get('type')
        if not isstring(self.type):
            raise TYBizConfException(d, 'HallGameNode.type must be string')
        
        self.params = d.get('params', {})
        
        self.conditions = UserConditionRegister.decodeList(d.get('conditions', []))
    
    def _buildToDictImpl(self, gameId, userId, clientId, d):
        d['params'] = self.params
     
    def isSuitable(self, gameId, userId, clientId):
        return checkConditions(gameId, userId, clientId, self.conditions)
    
    def getGameIds(self):
        re = []
        re.append(self.params.get('gameId', 0))
        return re
            
class HallGameNodeNormal(HallGameNode):
    TYPE_ID = 'hall.gamenode.normal'
    def __init__(self):
        super(HallGameNodeNormal, self).__init__()
        self.params = None
        self.version = None
        self.conditions = None

    def getVersions(self):
        return set([self.version])
    
    def initWhenLoaded(self, gameMap):
        gameId = self.params.get('gameId')
        ver = self.params.get('version')
        game = gameMap.get(gameId)
        if not game:
            raise TYBizConfException(self.conf, 'Unknown gameId %s' % (gameId))
        version = game.findVersion(ver)
        if not version:
            raise TYBizConfException(self.conf, 'Unknown ver %s for gameId %s' % (ver, gameId))
        self.version = version
    
    def _decodeFromDictImpl(self, d):
        self.params = d.get('params', {})
        self.conditions = UserConditionRegister.decodeList(d.get('conditions', []))
        
    def _buildToDictImpl(self, gameId, userId, clientId, d):
        d['params'] = self.params
     
    def isSuitable(self, gameId, userId, clientId,):
        return checkConditions(gameId, userId, clientId, self.conditions)
    
    def getGameIds(self):
        re = []
        re.append(self.params.get('gameId', 0))
        return re
       
class HallGameNodeTodoTask(HallGameNode):
    TYPE_ID = 'hall.gamenode.todotask'
    def __init__(self):
        super(HallGameNodeTodoTask, self).__init__()
        self.todotasks = None
        self.conditions = []
        
    def initWhenLoaded(self, gameMap):
        pass
    
    def _buildToDictImpl(self, gameId, userId, clientId, d):
        todotasks = TodoTaskHelper.makeTodoTasksByFactory(gameId, userId, clientId, self.todotasks)
        d['tasks'] = TodoTaskHelper.encodeTodoTasks(todotasks)
        d['params'] = self.params
        
    def _decodeFromDictImpl(self, d):
        self.todotasks = []
        # 给TodoTask类型添加params参数
        self.params = d.get('params', {})
        for todotaskDict in d.get('todotasks', []):
            todotask = TodoTaskRegister.decodeFromDict(todotaskDict)
            self.todotasks.append(todotask)
            
        self.conditions = UserConditionRegister.decodeList(d.get('conditions', []))
    
    def isSuitable(self, gameId, userId, clientId):
        return checkConditions(gameId, userId, clientId, self.conditions)
    
    def getGameIds(self):
        return []
    
class HallGameNodeRegister(TYConfableRegister):
    _typeid_clz_map = {
        HallGameNodePackage.TYPE_ID: HallGameNodePackage,
        HallGameNodeNormal.TYPE_ID: HallGameNodeNormal,
        HallGameNodeTodoTask.TYPE_ID: HallGameNodeTodoTask,
        HallGameNodeInnerGame.TYPE_ID: HallGameNodeInnerGame
    }
    
class HallPage(object):
    def __init__(self):
        # list<HallGameNode>
        self.nodeList = None
    
    def decodeFromDict(self, d):
        self.nodeList = []
        for nodeDict in d.get('nodes', []):
            node = HallGameNodeRegister.decodeFromDict(nodeDict)
            self.nodeList.append(node)
        return self
    
class HallUITemplate(object):
    def __init__(self):
        self.name = None
        self.pageList = None
        self.versionList = None
        self.innerGames = None
        
    def initWhenLoaded(self, gameMap):
        #key=gameId,value=version
        versionMap = {}
        for page in self.pageList:
            for node in page.nodeList:
                node.initWhenLoaded(gameMap)
                versions = node.getVersions()
                if versions:
                    for version in versions:
                        foundVersion = versionMap.get(version.game.gameId)
                        if not foundVersion:
                            versionMap[version.game.gameId] = version
                        elif foundVersion != version:
                            raise TYBizConfException(node.conf, 'Muliti version in template %s for game %s %s %s' % (self.name, version.game.gameId, foundVersion.ver, version.ver))
                        
        for inner in self.innerGames:
            inner.initWhenLoaded(gameMap)
            versions = inner.getVersions()
#             print 'AAAAAAAAAAAAA', versions
            if versions:
                for version in versions:
                    foundVersion = versionMap.get(version.game.gameId)
                    if not foundVersion:
                        versionMap[version.game.gameId] = version
                    elif foundVersion != version:
                        raise TYBizConfException(node.conf, 'Muliti version in template %s for game %s %s %s' % (self.name, version.game.gameId, foundVersion.ver, version.ver))
                    
        self.versionList = versionMap.values()
#         print 'versionList', pickle.dumps(self.versionList)
        
    def decodeFromDict(self, d):
        self.name = d.get('name')
        if not isstring(self.name) or not self.name:
            raise TYBizConfException(d, 'HallUITemplate.name must be string')
        self.pageList = []
        for pageDict in d.get('pages', []):
            page = HallPage().decodeFromDict(pageDict)
            self.pageList.append(page)
            
        self.innerGames = []
        for innerDict in d.get('innerGames', []):
#             print 'innerDict', innerDict
            innerGame = HallGameNodeRegister.decodeFromDict(innerDict)
#             print 'innerGame', innerGame
            self.innerGames.append(innerGame)
            
        return self
    
_inited = False
# list<HallGame>
_gameMap = {}
# key=name, value=HallUITemplate
_templateMap = {}

def _reloadConf():
    global _gameMap
    global _templateMap
    gameMap = {}
    templateMap = {}
    conf = hallconf.getGameList2Conf()
    for gameDict in conf.get('games', []):
        hallGame = HallGame().decodeFromDict(gameDict)
        if hallGame.gameId in gameMap:
            raise TYBizConfException(gameDict, 'Duplicate game %s' % (hallGame.gameId))
        gameMap[hallGame.gameId] = hallGame
    
    for templateDict in conf.get('templates', []):
        template = HallUITemplate().decodeFromDict(templateDict)
        if template.name in templateMap:
            raise TYBizConfException(templateDict, 'Duplicate template name %s' % (template.name))
        templateMap[template.name] = template
    
    for template in templateMap.values():
        template.initWhenLoaded(gameMap)
    
    _gameMap = gameMap
    _templateMap = templateMap
    ftlog.debug('hallgamelist2._reloadConf successed gameIds=', gameMap.keys(),
               'templateNames=', _templateMap.keys())
    
def _onConfChanged(event):
    if _inited and event.isModuleChanged(['gamelist2']):
        ftlog.debug('hallgamelist2._onConfChanged')
        _reloadConf()
        
def _initialize():
    ftlog.debug('hallgamelist2 initialize begin')
    global _inited
    if not _inited:
        _inited = True
        _reloadConf()
        pkeventbus.globalEventBus.subscribe(EventConfigure, _onConfChanged)
    ftlog.debug('hallgamelist2 initialize end')
    
def getGameList(gameId, userId, clientId):
    '''
    获取大厅游戏按钮列表
    @param clientId
    @return: list<HallPage>
    '''
    template = getUITemplate(gameId, userId, clientId)
    if ftlog.is_debug():
        ftlog.debug('hallgamelist2.getGameList gameId=', gameId,
                    'userId=', userId,
                    'clientId=', clientId,
                    'template=', template.name if template else None)
    return template.pageList if template else []

def getUITemplate(gameId, userId, clientId):
    '''
    获取大厅游戏按钮列表
    @param clientId
    @return: HallUITemplate or None
    '''
    templateName = hallconf.getGameList2TemplateName(clientId)
    if ftlog.is_debug():
        ftlog.debug('hallgamelist2.getUITemplate gameId=', gameId,
                    'userId=', userId,
                    'clientId=', clientId,
                    'templateName=', templateName)
    return _templateMap.get(templateName, None)

def checkConditions(gameId, userId, clientId, conds):
    if len(conds) == 0:
            return True
        
    for cond in conds:
        if not cond.check(gameId, userId, clientId, pktimestamp.getCurrentTimestamp()):
            return False
                     
    return True
