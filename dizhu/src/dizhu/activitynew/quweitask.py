# -*- coding:utf-8 -*-
'''
Created on 2016年12月14日

@author: zhaojiangang
'''
from sre_compile import isstring

from dizhu.activitynew.activity import ActivityNew
import freetime.util.log as ftlog
from hall.entity import hallitem, datachangenotify, hallpopwnd
from hall.entity.hallconf import HALL_GAMEID
from hall.entity.hallusercond import UserConditionRegister
from poker.entity.biz.confobj import TYConfable, TYConfableRegister
from poker.entity.biz.content import TYContentRegister, TYContentItem
from poker.entity.biz.exceptions import TYBizConfException, TYBizException
from poker.entity.biz.item.item import TYAssetUtils
import poker.entity.biz.message.message as pkmessage
from poker.entity.biz.task.task import TYTaskInspectorRegister
from poker.entity.configure import gdata
from poker.entity.dao import sessiondata, daobase
from poker.util import strutil
import poker.util.timestamp as pktimestamp

class ErrorCode:
    REFRESH_FEE_NOT_ENOUGH = -1
    INVALID_TASK = -2
    INCOMPLETE_TASK = -3
    PRIZE_ALREADY_GAIN = -4

class QuweiTaskKind(TYConfable):
    """
    任务种类
    """
    TYPE_ID = 'ddz.qwtask.simple'
    def __init__(self):
        # 种类ID
        self.kindId = None
        # 名称
        self.name = None
        # 需要完成的数量
        self.count = None
        # 最大能完成几次
        self.totalLimit = None
        # 说明
        self.desc = None
        # 图片
        self.pic = None
        # 完成任务后给的奖励内容TYContent
        self.rewardContent = None
        self.rewardMail = None
        # 监控者
        self.inspector = None
        self.resetProgressWhenFinish = False
        # 产生todotask
        self.todotaskFac = None
        
    def newTask(self):
        return QuweiTask(self)

    def decodeFromDict(self, d):
        self.kindId = d.get('kindId')
        if not isinstance(self.kindId, int):
            raise TYBizConfException(d, 'task.kindId must be int')

        self.name = d.get('name')
        if not isstring(self.name):
            raise TYBizConfException(d, 'task.name must be string')

        self.count = d.get('count')
        if not isinstance(self.count, int):
            raise TYBizConfException(d, 'task.count must be int')

        self.totalLimit = d.get('totalLimit', 0)
        if not isinstance(self.totalLimit, int):
            raise TYBizConfException(d, 'task.totalLimit must be int')

        self.desc = d.get('desc', '')
        if not isstring(self.desc):
            raise TYBizConfException(d, 'task.desc must be string')

        self.pic = d.get('pic', '')
        if not isstring(self.pic):
            raise TYBizConfException(d, 'task.pic must be string')

        rewardContent = d.get('rewardContent')
        if rewardContent:
            self.rewardContent = TYContentRegister.decodeFromDict(rewardContent)
            self.rewardMail = d.get('rewardMail', '')
            if not isstring(self.rewardMail):
                raise TYBizConfException(d, 'task.rewardMail must be string')
        
        self.inspector = TYTaskInspectorRegister.decodeFromDict(d.get('inspector'))
        todotask = d.get('todotask')
        if todotask:
            self.todotaskFac = hallpopwnd.decodeTodotaskFactoryByDict(todotask)
        self._decodeFromDictImpl(d)
        return self
    
    def processEvent(self, task, event):
        from poker.entity.events.tyevent import ChargeNotifyEvent
        if isinstance(event, ChargeNotifyEvent):
            if strutil.getGameIdFromHallClientId(event.clientId) != 6:
                return False, 0
        return self.inspector.processEvent(task, event)

    def _decodeFromDictImpl(self, d):
        pass

class QuweiTask(object):
    def __init__(self, taskKind):
        # 任务种类
        self.taskKind = taskKind
        # 本此任务进度
        self.progress = 0
        # 总共完成该任务多少次
        self.finishCount = 0
        # 完成任务时间
        self.finishTime = 0
        # 是否领取了奖励
        self.gotReward = 0
        # 最后更新时间
        self.updateTime = 0
        # 任务是否开放了
        self.open = 0
        self._status = None

    @property
    def kindId(self):
        return self.taskKind.kindId
    
    @property
    def userId(self):
        return self._status.userId
    
    def setProgress(self, progress, timestamp):
        if 0 < self.taskKind.totalLimit <= self.finishCount:
            return False, 0
        if progress == self.progress:
            return False, 0

        self.updateTime = timestamp
        if progress < self.taskKind.count:
            self.progress = progress
            return True, 0

        if self.taskKind.resetProgressWhenFinish:
            self.progress = 0
        else:
            self.progress = self.taskKind.count
            # self.progress = progress
        self.finishCount += 1
        self.finishTime = timestamp
        return True, 1
    
    def fromDict(self, d):
        self.progress = d.get('prog', 0)
        self.finishCount = d.get('fcnt', 0)
        self.finishTime = d.get('ftm', 0)
        self.gotReward = d.get('rwd', 0)
        self.updateTime = d.get('utm', 0)
        self.open = d.get('open', 0)
        self._fromDictImpl(d)
        return self
    
    def toDict(self):
        d = {
            'prog':self.progress,
            'fcnt':self.finishCount,
            'ftm':self.finishTime,
            'rwd':self.gotReward,
            'utm':self.updateTime,
            'open':self.open
        }
        self._toDictImpl(d)
        return d

    def _fromDictImpl(self, d):
        pass
    
    def _toDictImpl(self, d):
        pass

class QuweiTaskStatus(object):
    def __init__(self, userId):
        self.userId = userId
        self.lastRefreshTime = 0
        self._tasks = []
        self._taskMap = {}
    
    @property
    def tasks(self):
        return self._tasks

    def findTask(self, kindId):
        return self._taskMap.get(kindId)
    
    def indexOf(self, kindId):
        for i, task in enumerate(self._tasks):
            if task.kindId == kindId:
                return i
        return -1

    def removeAllTask(self):
        tasks = self._tasks
        self._tasks = []
        self._taskMap = {}
        return tasks

    def removeTask(self, kindId):
        exists = self.findTask(kindId)
        if exists:
            self._tasks.remove(exists)
            del self._taskMap[kindId]

    def addTask(self, task):
        self.removeTask(task.kindId)
        task._status = self
        self._tasks.append(task)
        self._taskMap[task.kindId] = task
        
def loadStatusData(gameId, userId, actId):
    return daobase.executeUserCmd(userId, 'hget', 'act:%s:%s' % (gameId, userId), actId)

def saveStatusData(gameId, userId, actId, data):
    daobase.executeUserCmd(userId, 'hset', 'act:%s:%s' % (gameId, userId), actId, data)

class QuweiTaskActivity(ActivityNew):
    TYPE_ID = 'ddz.act.quweitask'
    
    def __init__(self):
        super(QuweiTaskActivity, self).__init__()
        # 游戏ID
        self._gameId = None
        # 任务池
        self._taskKindMap = None
        # 初始化的任务池list<(condition, list<TaskKind>)
        self._initPools = None
        # 刷新任务需要的费用
        self._refreshFee = None
        # 任务数量
        self._taskCount = None
        # 是否每日自动刷新
        self._autoRefresh = False
        # 是否能同时完成所有任务
        self._allOpen = False
        
    @property
    def gameId(self):
        return self._gameId
    
    def init(self):
        try:
            self._registerEvents(self._taskKindMap.values())
        except:
            self._unregisterEvents(self._taskKindMap.values())
    
    def cleanup(self):
        self._unregisterEvents(self._taskKindMap.values())
    
    def findTaskKind(self, kindId):
        return self._taskKindMap.get(kindId)
    
    def refresh(self, status, timestamp):
        '''
        刷新任务
        '''
        if ftlog.is_debug():
            ftlog.debug('QuweiTaskActivity.refresh',
                        'gameId=', self.gameId,
                        'actId=', self.actId,
                        'userId=', status.userId)
        self._collectRefreshFee(status, timestamp)
        self._refreshTasks(status, timestamp)
        self.saveStatus(status)
    
    def loadStatus(self, userId, timestamp):
        jstr = None
        status = QuweiTaskStatus(userId)
        try:
            jstr = loadStatusData(self.gameId, userId, self.actId)
            if ftlog.is_debug():
                ftlog.debug('QuweiTaskActivity.loadStatus',
                            'gameId=', self.gameId,
                            'actId=', self.actId,
                            'userId=', userId,
                            'jstr=', jstr)
            if jstr:
                d = strutil.loads(jstr)
                self._decodeStatus(status, d)
            else:
                self._initStatus(status, timestamp)
                self.saveStatus(status)
        except:
            ftlog.error('QuweiTaskActivity.loadStatus',
                        'gameId=', self.gameId,
                        'actId=', self.actId,
                        'userId=', userId,
                        'jstr=', jstr)
        if self.needRefresh(status, timestamp):
            self._refreshTasks(status, timestamp)
            self.saveStatus(status)
        return status

    def saveStatus(self, status):
        d = self._encodeStatus(status)
        jstr = strutil.dumps(d)
        if ftlog.is_debug():
            ftlog.debug('QuweiTaskActivity.saveStatus',
                        'gameId=', self.gameId,
                        'actId=', self.actId,
                        'userId=', status.userId,
                        'jstr=', jstr)
        saveStatusData(self.gameId, status.userId, self.actId, jstr)
    
    def needRefresh(self, status, timestamp):
        need = (self._autoRefresh
                and (not pktimestamp.is_same_day(status.lastRefreshTime, timestamp)
                     or (not status.tasks and self._taskKindMap)))
        if ftlog.is_debug():
            ftlog.debug('QuweiTaskActivity.needRefresh',
                        'gameId=', self.gameId,
                        'actId=', self.actId,
                        'userId=', status.userId,
                        'need=', need,
                        'lastRefreshTime=', status.lastRefreshTime)
        return need

    def gainReward(self, status, kindId, timestamp):
        if ftlog.is_debug():
            ftlog.debug('QuweiTaskActivity.gainReward',
                        'gameId=', self.gameId,
                        'actId=', self.actId,
                        'userId=', status.userId,
                        'kindId=', kindId)
        index = status.indexOf(kindId)
        if index == -1:
            raise TYBizException(ErrorCode.INVALID_TASK, '不能识别的任务')
        task = status.tasks[index]
        if task.finishCount <= 0:
            raise TYBizException(ErrorCode.INCOMPLETE_TASK, '任务没有完成不能领取奖励')
        if task.gotReward:
            raise TYBizException(ErrorCode.PRIZE_ALREADY_GAIN, '奖励已经领取')
        task.gotReward = 1
        task.updateTime = timestamp
        index += 1
        if index < len(status.tasks):
            # 打开下一个任务
            status.tasks[index].open = 1
        self.saveStatus(status)
        if task.taskKind.rewardContent:
            self._sendRewards(status, task, timestamp)
    
    def _sendRewards(self, status, task, timestamp):
        userAssets = hallitem.itemSystem.loadUserAssets(status.userId)
        assetList = userAssets.sendContent(self.gameId,
                                           task.taskKind.rewardContent,
                                           1,
                                           True,
                                           timestamp,
                                           'ACTIVITY_REWARD',
                                           self.intActId)
        ftlog.debug('QuweiTaskActivity._sendRewards',
                    'gameId=', self.gameId,
                    'actId=', self.actId,
                    'userId=', status.userId,
                    'assets=', [(atup[0].kindId, atup[1]) for atup in assetList])
        changed = TYAssetUtils.getChangeDataNames(assetList)
        datachangenotify.sendDataChangeNotify(self.gameId, status.userId, changed)
        
        if task.taskKind.rewardMail:
            contents = TYAssetUtils.buildContentsString(assetList)
            mail = strutil.replaceParams(task.taskKind.rewardMail, {'rewardContent':contents})
            pkmessage.sendPrivate(HALL_GAMEID, status.userId, 0, mail)
            
    def _collectRefreshFee(self, status, timestamp):
        if self._refreshFee:
            userAssets = hallitem.itemSystem.loadUserAssets(status.userId)
            #def consumeAsset(self, gameId, assetKindId, count, timestamp, eventId, intEventParam):
            assetKind, consumeCount, _finalCount = userAssets.consumeAsset(self.gameId,
                                                                           self._refreshFee.assetKindId,
                                                                           self._refreshFee.count,
                                                                           timestamp,
                                                                           'ACTIVITY_CONSUME',
                                                                           self.intActId)
            if consumeCount < self._refreshFee.count:
                raise TYBizException(ErrorCode.REFRESH_FEE_NOT_ENOUGH, '费用不足')
    
            ftlog.info('QuweiTaskActivity._collectRefreshFee',
                       'gameId=', self.gameId,
                       'actId=', self.actId,
                       'userId=', status.userId,
                       'fee=', (self._refreshFee.assetKindId, self._refreshFee.count))

            if assetKind.keyForChangeNotify:
                datachangenotify.sendDataChangeNotify(self.gameId, status.userId, assetKind.keyForChangeNotify)
    
    def _initStatus(self, status, timestamp):
        status.lastRefreshTime = timestamp
        self._initTasks(status, timestamp)
            
    def _genInitTaskKindList(self, status, timestamp):
        clientId = sessiondata.getClientId(status.userId)
        for cond, taskKindList in self._initPools:
            if not cond or cond.check(self.gameId, status.userId, clientId, timestamp):
                return taskKindList
        return self._genRefreshTaskKindList(status, timestamp)
    
    def _genRefreshTaskKindList(self, status, timestamp):
        taskKinds = self._taskKindMap.values()[:]
        return taskKinds[0:self._taskCount]
        
    def _initTasks(self, status, timestamp):
        initTaskKindList = self._genInitTaskKindList(status, timestamp)
        if initTaskKindList:
            for taskKind in initTaskKindList:
                task = taskKind.newTask()
                task.updateTime = timestamp
                status.addTask(task)
            
            '''
            if self._allOpen and status.tasks:
                for taskstu in status.tasks:
                    taskstu.open = 1
            el
            '''
            if status.tasks:
                status.tasks[0].open = 1
        ftlog.info('QuweiTaskActivity._initTasks',
                   'gameId=', self.gameId,
                   'actId=', self.actId,
                   'userId=', status.userId,
                   'initTasks=', [t.kindId for t in status.tasks])
    
    def _refreshTasks(self, status, timestamp):
        oldTasks = status.removeAllTask()
        for task in oldTasks:
            task = task.taskKind.newTask()
            task.updateTime = timestamp
            status.addTask(task)
        if status.tasks:
            status.tasks[0].open = 1
        status.lastRefreshTime = timestamp
        ftlog.info('QuweiTaskActivity._refreshTasks',
                   'gameId=', self.gameId,
                   'actId=', self.actId,
                   'userId=', status.userId,
                   'oldTasks=', [t.kindId for t in oldTasks],
                   'newTasks=', [t.kindId for t in status.tasks])
    
    def _decodeStatus(self, status, d):
        status.lastRefreshTime = d.get('lrtm', 0)
        tasks = d.get('tasks', [])
        for taskD in tasks:
            try:
                task = self._decodeTask(status, taskD)
                if task:
                    #if self._allOpen:
                    #    task.open = 1
                    status.addTask(task)
            except:
                ftlog.error('QuweiTaskActivity._decodeStatus',
                            'actId=', self.actId,
                            'userId=', status.userId,
                            'taskD=', taskD,
                            'err=', 'BadTaskData')
        return status
    
    def _encodeStatus(self, status):
        tasks = []
        for task in status.tasks:
            tasks.append(self._encodeTask(status, task))
        return {
            'lrtm':status.lastRefreshTime,
            'tasks':tasks
        }
    
    def _decodeTask(self, status, d):
        kindId = d.get('kindId')
        taskKind = self.findTaskKind(kindId)
        if not taskKind:
            ftlog.warn('QuweiTaskActivity._decodeTask',
                       'actId=', self.actId,
                       'userId=', status.userId,
                       'd=', d,
                       'err=', 'UnknownTaskKind')
            return None
        task = taskKind.newTask()
        task.fromDict(d)
        return task
    
    def _encodeTask(self, status, task):
        d = task.toDict()
        d['kindId'] = task.kindId
        return d

    def _decodeFromDictImpl(self, d):
        self._gameId = d.get('gameId')
        if not isinstance(self._gameId, int):
            raise TYBizConfException(d, 'QuweiTaskActivity.gameId must be int')
        refreshFee = d.get('refreshFee')
        if refreshFee is not None:
            refreshFee = TYContentItem.decodeFromDict(refreshFee)
        taskKindMap = {}
        for taskKindConf in d.get('tasks', []):
            taskKind = QuweiTaskKindRegister.decodeFromDict(taskKindConf)
            if taskKind.kindId in taskKindMap:
                raise TYBizConfException(taskKindConf, 'Duplicate taskKind: %s' % (taskKind.kindId))
            taskKindMap[taskKind.kindId] = taskKind
        
        taskCount = d.get('taskCount')
        if not isinstance(taskCount, int) or taskCount <= 0:
            raise TYBizConfException(taskCount, 'QuweiTaskActivity.taskCount must be int > 0')
        
        autoRefresh = d.get('autoRefresh', 0)
        initPools = []
        for poolConf in d.get('initPools', []):
            cond = poolConf.get('condition')
            if cond is not None:
                cond = UserConditionRegister.decodeFromDict(cond)
            taskKindList = []
            taskKindIds = poolConf.get('kindIds', [])
            for kindId in taskKindIds:
                taskKind = taskKindMap.get(kindId)
                if not taskKind:
                    raise TYBizConfException(poolConf, 'Unknown kindId: %s' % (kindId))
                taskKindList.append(taskKind)
            initPools.append((cond, taskKindList))
        
        self._taskKindMap = taskKindMap
        self._refreshFee = refreshFee
        self._initPools = initPools
        self._taskCount = taskCount
        self._autoRefresh = autoRefresh
        self._allOpen = d.get('open', 0)
        
        ftlog.info('QuweiTaskActivity._decodeFromDictImpl',
                   'gameId=', self.gameId,
                   'actId=', self.actId,
                   'taskCount=', self._taskCount,
                   'autoRefresh=', self._autoRefresh,
                   'tasks=', self._taskKindMap.keys(),
                   'refreshFee=', self._refreshFee.toDict() if self._refreshFee else None,
                   'allOpen=', self._allOpen,
                   'initPools=', [(p[0], [tk.kindId for tk in p[1]]) for p in self._initPools])
    
    def _collectInterestEventMap(self, taskKinds):
        interestEventMap = {}
        for taskKind in taskKinds:
            for eventType, gameIds in taskKind.inspector.interestEventMap.iteritems():
                gameIds = gameIds or gdata.gameIds()
                existsGameIds = interestEventMap.get(eventType)
                if not existsGameIds:
                    existsGameIds = set()
                    interestEventMap[eventType] = existsGameIds
                existsGameIds.update(gameIds)
        return interestEventMap
    
    def _registerEvents(self, taskKinds):
        interestEventMap = self._collectInterestEventMap(taskKinds)
        for eventType, gameIds in interestEventMap.iteritems():
            for gameId in gameIds:
                game = gdata.games().get(gameId)
                if game:
                    if ftlog.is_debug():
                        ftlog.debug('QuweiTaskSystem._registerEvents gameId=', gameId,
                                    'eventType=', eventType)
                    game.getEventBus().subscribe(eventType, self._handleEvent)
                else:
                    ftlog.warn('QuweiTaskSystem._registerEvents gameId=', gameId,
                               'eventType=', eventType,
                               'err=', 'Not find game')

    def _unregisterEvents(self, taskKinds):
        interestEventMap = self._collectInterestEventMap(taskKinds)
        for eventType, gameIds in interestEventMap.iteritems():
            for gameId in gameIds:
                game = gdata.games().get(gameId)
                if game:
                    if ftlog.is_debug():
                        ftlog.debug('QuweiTaskSystem._unregisterEvents gameId=', gameId,
                                    'eventType=', eventType)
                    game.getEventBus().unsubscribe(eventType, self._handleEvent)
                else:
                    ftlog.warn('QuweiTaskSystem._unregisterEvents gameId=', gameId,
                               'eventType=', eventType,
                               'err=', 'Not find game')
    
    def _handleEvent(self, event):
        status = self.loadStatus(event.userId, event.timestamp)
        tasks = status.tasks[:]
        changed = False
        for task in tasks:
            if task.open or self._allOpen:
                taskChanged, _finishCount = task.taskKind.processEvent(task, event)
                if ftlog.is_debug:
                    ftlog.debug('_handleEvent',
                                'kindId=', task.kindId,
                                'process=', task.progress,
                                'kindIDCount=', task.taskKind.count,
                                'task.gotReward=', task.gotReward,
                                'userId=', event.userId)
                if taskChanged:
                    changed = True
        if changed:
            self.saveStatus(status)
        if ftlog.is_debug():
            ftlog.debug('QuweiTaskSystem._handleEvent',
                        'actId=', self.actId,
                        'userId=', event.userId,
                        'gameId=', event.gameId,
                        'event=', event,
                        'changed=', changed)

class QuweiTaskKindRegister(TYConfableRegister):
    _typeid_clz_map = {
        QuweiTaskKind.TYPE_ID:QuweiTaskKind
    }


