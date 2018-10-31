# -*- coding:utf-8 -*-
'''
Created on 2017年12月15日

@author: zhaojiangang
'''
from sre_compile import isstring

import freetime.util.log as ftlog
from hall.entity import hallpopwnd, hallitem, datachangenotify, \
    hall_red_packet_const
from hall.entity.hallconf import HALL_GAMEID
from hall.entity.hallevent import UserBindWeixinEvent, UserReceivedCouponEvent, \
    UserRedPacketTaskRewardEvent
from hall.entity.hallusercond import UserConditionNewUser
from poker.entity.biz.confobj import TYConfable
from poker.entity.biz.content import TYContentRegister
from poker.entity.biz.exceptions import TYBizConfException, TYBizException
from poker.entity.biz.item.item import TYAssetUtils
import poker.entity.biz.message.message as pkmessage
from poker.entity.biz.task.task import TYTaskInspectorRegister, TYTaskInspector
from poker.entity.configure import gdata, configure
from poker.entity.dao import daobase, sessiondata, userdata
from poker.entity.events.tyevent import EventConfigure, EventUserLogin
import poker.entity.events.tyeventbus as pkeventbus
from poker.util import strutil
import poker.util.timestamp as pktimestamp


BIND_WX_TASK_KIND_ID = 99990001


class RPTaskKind(TYConfable):
    """
    任务种类: 大厅红包任务
    """
    TYPE_ID = 'hall.rptask.simple'

    def __init__(self):
        super(RPTaskKind, self).__init__()
        # 种类ID
        self.kindId = None
        # 名称
        self.name = None
        # 需要完成的数量
        self.count = None
        self.totalLimit = 1
        # 说明
        self.desc = None
        # 图片
        self.pic = None
        # 完成任务后给的奖励内容TYContent
        self.rewardContent = None
        self.rewardMail = None
        
        # 完成任务后给邀请人的红包券奖励数量
        self.inviterReward = None
        # 监控者
        self.inspector = None
        # 产生todotask
        self.todotaskFac = None
        
    def newTask(self, status):
        ret = RPTask(self)
        ret.status = status
        return ret

    def decodeFromDict(self, d):
        self.kindId = d.get('kindId')
        if not isinstance(self.kindId, int):
            raise TYBizConfException(d, 'RPTaskKind.kindId must be int')

        self.name = d.get('name')
        if not isstring(self.name):
            raise TYBizConfException(d, 'RPTaskKind.name must be string')

        self.count = d.get('count')
        if not isinstance(self.count, int):
            raise TYBizConfException(d, 'RPTaskKind.count must be int')

        self.desc = d.get('desc', '')
        if not isstring(self.desc):
            raise TYBizConfException(d, 'RPTaskKind.desc must be string')

        self.pic = d.get('pic', '')
        if not isstring(self.pic):
            raise TYBizConfException(d, 'RPTaskKind.pic must be string')

        inviterReward = d.get('inviterReward', 0)
        if not isinstance(inviterReward, int) or inviterReward < 0:
            raise TYBizConfException(d, 'RPTaskKind.inviterReward must be int >= 0')
        self.inviterReward = inviterReward

        rewardContent = d.get('rewardContent')
        if rewardContent:
            self.rewardContent = TYContentRegister.decodeFromDict(rewardContent)
            self.rewardMail = d.get('rewardMail', '')
            if not isstring(self.rewardMail):
                raise TYBizConfException(d, 'RPTaskKind.rewardMail must be string')

        self.inspector = TYTaskInspectorRegister.decodeFromDict(d.get('inspector'))
        todotask = d.get('todotask')
        if todotask:
            self.todotaskFac = hallpopwnd.decodeTodotaskFactoryByDict(todotask)
        self._decodeFromDictImpl(d)
        return self

    def processEvent(self, task, event):
        return self.inspector.processEvent(task, event)

    def _decodeFromDictImpl(self, d):
        pass


class RPTask(object):
    """ 当前任务 """
    def __init__(self, taskKind):
        # 任务种类
        self.taskKind = taskKind
        # 本此任务进度
        self.progress = 0
        # 完成任务时间
        self.finishTime = 0
        self.finishCount = 0
        # 是否领取了奖励
        self.gotReward = 0
        # 最后更新时间
        self.updateTime = 0
        # 用户状态
        self.status = None

    @property
    def kindId(self):
        return self.taskKind.kindId

    @property
    def userId(self):
        return self.status.userId

    def setProgress(self, progress, timestamp):
        if 0 < self.taskKind.totalLimit <= self.finishCount:
            return False, 0
        
        if progress == self.progress:
            return False, 0

        self.updateTime = timestamp
        if progress < self.taskKind.count:
            self.progress = progress
            return True, 0
        self.progress = self.taskKind.count
        self.finishCount += 1
        self.finishTime = timestamp
        return True, 1

    def fromDict(self, d):
        self.progress = d.get('prog', 0)
        self.finishTime = d.get('ftm', 0)
        self.finishCount = d.get('fcnt', 0)
        self.gotReward = d.get('rwd', 0)
        self.updateTime = d.get('utm', 0)
        self._fromDictImpl(d)
        return self

    def toDict(self):
        d = {
            'prog':self.progress,
            'ftm':self.finishTime,
            'fcnt':self.finishCount,
            'rwd':self.gotReward,
            'utm':self.updateTime
        }
        self._toDictImpl(d)
        return d

    def _fromDictImpl(self, d):
        pass

    def _toDictImpl(self, d):
        pass


class RPTaskStatus(object):
    def __init__(self, userId):
        self.userId = userId
        self.isNewUser = 0
        self.isFirst = 0
        self.finished = 0
        self.task = None


class RPAct(object):
    def __init__(self):
        self.pic = None
        self.todotaskFac = None

    def fromDict(self, d):
        self.pic = d.get('pic', '')
        if not isstring(self.pic):
            raise TYBizConfException(d, 'RPAct.pic must be string')
        
        todotaskD = d.get('todotask')
        if todotaskD:
            self.todotaskFac = hallpopwnd.decodeTodotaskFactoryByDict(todotaskD)
        
        return self


class RPTaskSystem(object):
    """ 大厅红包任务系统 """
    def __init__(self):
        self._taskKindMap = {}
        self._taskKindList = []
        self._acts = []
        self._closed = 0

    @property
    def gameId(self):
        return HALL_GAMEID

    @property
    def taskKindList(self):
        return self._taskKindList

    def reloadConf(self):
        taskKindMap = {}
        taskKindList = []
        acts = []
        
        conf = configure.getGameJson(HALL_GAMEID, 'red_packet_task', {})
        
        closed = conf.get('closed', 0)
        if not isinstance(closed, int) or closed not in (0, 1):
            raise TYBizConfException(conf, 'closed must be int in (0, 1)')
        
        for actD in conf.get('acts', []):
            act = RPAct().fromDict(actD)
            acts.append(act)
        
        for taskKindConf in conf.get('tasks', []):
            taskKind = RPTaskKind().decodeFromDict(taskKindConf)
            if taskKind.kindId in taskKindMap:
                raise TYBizConfException(conf, 'Duplicate taskKind %s' % (taskKind.kindId))
            taskKindMap[taskKindConf['kindId']] = taskKind
            taskKindList.append(taskKind)
        
        self._unregisterEvents(self._taskKindList)
        self._registerEvents(taskKindList)
        
        self._taskKindList = taskKindList
        self._taskKindMap = taskKindMap
        self._acts = acts
        self._closed = closed
        
        ftlog.info('RPTaskSystem.reloadConf ok',
                   'closed=', self._closed,
                   'taskList=', [taskKind.kindId for taskKind in self._taskKindList],
                   'acts=', [act.todotaskFac for act in self._acts])

    def findTaskKind(self, kindId):
        return self._taskKindMap.get(kindId)

    def getActs(self):
        return self._acts
    
    def loadStatus(self, userId, timestamp):
        jstr = None
        status = RPTaskStatus(userId)
        try:
            jstr = daobase.executeUserCmd(userId, 'hget', 'rptask:%s:%s' % (HALL_GAMEID, userId), 'status')
            if ftlog.is_debug():
                ftlog.debug('RPTaskSystem.loadStatus',
                            'gameId=', self.gameId,
                            'userId=', userId,
                            'jstr=', jstr)
            if jstr:
                d = strutil.loads(jstr)
                self._decodeStatus(status, d)
                # 没有任务或者当前任务不是微信绑定任务则设置为所有任务完成状态
                if not status.finished:
                    clientId = sessiondata.getClientId(status.userId)
                    if not UserConditionNewUser().check(HALL_GAMEID, status.userId, clientId, timestamp):
                        status.finished = 1
            else:
                self._initStatus(status, timestamp)
                self.saveStatus(status)
        except Exception, e:
            ftlog.error('RPTaskSystem.loadStatus',
                        'gameId=', self.gameId,
                        'userId=', userId,
                        'jstr=', jstr,
                        'err=', e.message)
        return status

    def saveStatus(self, status):
        d = self._encodeStatus(status)
        jstr = strutil.dumps(d)
        daobase.executeUserCmd(status.userId, 'hset', 'rptask:%s:%s' % (HALL_GAMEID, status.userId), 'status', jstr)
        if ftlog.is_debug():
            ftlog.debug('RPTaskSystem.saveStatus',
                        'gameId=', self.gameId,
                        'userId=', status.userId,
                        'jstr=', jstr)

    def _encodeStatus(self, status):
        ret = {
            'finished':status.finished,
            'newUser':status.isNewUser,
            'isFirst':status.isFirst
        }
        if status.task:
            ret['task'] = self._encodeTask(status.task)
        return ret

    def _decodeStatus(self, status, d):
        status.lastRefreshTime = d.get('lrtm', 0)
        taskD = d.get('task')
        status.finished = d.get('finished', 0)
        status.isNewUser = d.get('newUser', 0)
        status.isFirst = d.get('isFirst', 0)
        if taskD:
            try:
                task = self._decodeTask(status, taskD)
                status.task = task
            except Exception, e:
                ftlog.error('RPTaskSystem._decodeStatus',
                            'userId=', status.userId,
                            'taskD=', taskD,
                            'err=', e.message)
        return status

    def gainReward(self, status, timestamp):
        if ftlog.is_debug():
            ftlog.debug('RPTaskSystem.gainReward',
                        'gameId=', self.gameId,
                        'userId=', status.userId,
                        'kindId=', status.task.kindId if status.task else None)
        
        task = status.task
        
        if not task:
            raise TYBizException(-1, '没有任务可以领取')
    
        if task.finishCount <= 0:
            raise TYBizException(-1, '任务还没有完成')
        
        if task.gotReward:
            raise TYBizException(-1, '奖励已经领取')
        
        task.gotReward = 1
        task.updateTime = timestamp
        
        clientId = sessiondata.getClientId(status.userId)
        isNewUser = UserConditionNewUser().check(HALL_GAMEID, status.userId, clientId, timestamp)
        
        if not isNewUser:
            status.finished = 1
        else:
            nextKind = self._getNextTask(status)
            if nextKind:
                # 打开下一个任务
                nextTask = nextKind.newTask(status)
                nextTask.updateTime = timestamp
                status.task = nextTask
            else:
                # 全部完成
                status.finished = 1

        status.isFirst = 0
        self.saveStatus(status)
        
        if task.taskKind.rewardContent:
            return self._sendRewards(status, task, timestamp)
        return None

    def _indexOfTask(self, kindId, taskKinds):
        for i, task in enumerate(taskKinds):
            if task.kindId == kindId:
                return i
        return -1
    
    def _getNextTask(self, status):
        """ 激活下一个任务 """
        clientId = sessiondata.getClientId(status.userId)
        taskKinds = self._getNewUserTasks(status.userId, clientId) if status.isNewUser else self._getOldUserTasks(status.userId, clientId)
        index = self._indexOfTask(status.task.kindId, taskKinds)
        if index >= 0 and index + 1 < len(taskKinds):
            return taskKinds[index + 1]
        return None

    def _sendRewards(self, status, task, timestamp):
        from hall.game import TGHall
        
        userAssets = hallitem.itemSystem.loadUserAssets(status.userId)
        assetList = userAssets.sendContent(self.gameId,
                                           task.taskKind.rewardContent,
                                           1,
                                           True,
                                           timestamp,
                                           'HALL_RP_TASK_REWARD',
                                           task.kindId)
        ftlog.info('RPTaskSystem._sendRewards',
                   'gameId=', self.gameId,
                   'userId=', status.userId,
                   'kindId=', task.kindId,
                   'assets=', [(atup[0].kindId, atup[1]) for atup in assetList])
        changed = TYAssetUtils.getChangeDataNames(assetList)
        datachangenotify.sendDataChangeNotify(self.gameId, status.userId, changed)

        if task.taskKind.rewardMail:
            contents = TYAssetUtils.buildContentsString(assetList)
            mail = strutil.replaceParams(task.taskKind.rewardMail, {'rewardContent': contents})
            pkmessage.sendPrivate(HALL_GAMEID, status.userId, 0, mail)
        
        TGHall.getEventBus().publishEvent(UserRedPacketTaskRewardEvent(status.userId, HALL_GAMEID, task.taskKind, assetList))
        
        couponCount = TYAssetUtils.getAssetCount(assetList, hallitem.ASSET_COUPON_KIND_ID)
        if couponCount > 0:
            TGHall.getEventBus().publishEvent(UserReceivedCouponEvent(HALL_GAMEID,
                                                                      status.userId,
                                                                      couponCount,
                                                                      hall_red_packet_const.RP_SOURCE_RP_TASK))

    def _getUserTasks(self, userId, clientId, key):
        ret = []
        temp = configure.getTcContentByGameId('red_packet_task', None, HALL_GAMEID, clientId)
        kindIds = temp.get(key) if temp else None
        if kindIds:
            for kindId in kindIds:
                taskKind = self.findTaskKind(kindId)
                if taskKind:
                    ret.append(taskKind)
                else:
                    ftlog.warn('RPTaskSystem._getUserTasks UnknownTask',
                               'userId=', userId,
                               'clientId=', clientId,
                               'kindId=', kindId)
        return ret

    def _getTaskTips(self, userId, clientId):
        temp = configure.getTcContentByGameId('red_packet_task', None, HALL_GAMEID, clientId)
        if ftlog.is_debug():
            ftlog.debug('RPTaskSystem._getTaskTips',
                        'userId=', userId,
                        'clientId=', clientId,
                        'temp=', temp)
        return temp.get('tips') if temp else []

    def _getHelpUrl(self, userId, clientId):
        temp = configure.getTcContentByGameId('red_packet_task', None, HALL_GAMEID, clientId)
        if ftlog.is_debug():
            ftlog.debug('RPTaskSystem._getHelpUrl',
                        'userId=', userId,
                        'clientId=', clientId,
                        'temp=', temp)
        return temp.get('helpUrl') if temp else ''

    def _getBoardTip(self, userId, clientId):
        temp = configure.getTcContentByGameId('red_packet_task', None, HALL_GAMEID, clientId)
        if ftlog.is_debug():
            ftlog.debug('RPTaskSystem._getBoardTip',
                        'userId=', userId,
                        'clientId=', clientId,
                        'temp=', temp)
        return temp.get('boardTip') if temp else ''
    
    def _getNewUserTasks(self, userId, clientId):
        return self._getUserTasks(userId, clientId, 'newUserTasks')
        
    def _getOldUserTasks(self, userId, clientId):
        return self._getUserTasks(userId, clientId, 'oldUserTasks')
    
    def _initStatus(self, status, timestamp):
        clientId = sessiondata.getClientId(status.userId)
        status.isNewUser = 1 if UserConditionNewUser().check(HALL_GAMEID, status.userId, clientId, timestamp) else 0
        taskKinds = self._getNewUserTasks(status.userId, clientId) if status.isNewUser else self._getOldUserTasks(status.userId, clientId)
        self._initTasks(status, taskKinds, timestamp)
        
        ftlog.info('RPTaskSystem._initStatus',
                   'userId=', status.userId,
                   'isNewUser=', status.isNewUser,
                   'finished=', status.finished,
                   'isFirst=', status.isFirst,
                   'tasks=', [taskKind.kindId for taskKind in taskKinds] if taskKinds else [],
                   'task=', status.task.kindId if status.task else None)
    
    def _initTasks(self, status, taskKinds, timestamp):
        if taskKinds:
            taskKind = taskKinds[0]
            task = taskKind.newTask(status)
            task.updateTime = timestamp
            status.task = task
            status.isFirst = 1
        else:
            status.finished = 1

    def _decodeTask(self, status, d):
        kindId = d.get('kindId')
        taskKind = self.findTaskKind(kindId)
        if not taskKind:
            ftlog.warn('RPTaskSystem._decodeTask',
                       'd=', d,
                       'err=', 'UnknownTaskKind')
            return None
        task = taskKind.newTask(status)
        task.fromDict(d)
        return task

    def _encodeTask(self, task):
        d = task.toDict()
        d['kindId'] = task.kindId
        return d

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
                        ftlog.debug('RPTaskSystem._registerEvents gameId=', gameId,
                                    'eventType=', eventType)
                    game.getEventBus().subscribe(eventType, self._handleEvent)
                else:
                    ftlog.warn('RPTaskSystem._registerEvents gameId=', gameId,
                               'eventType=', eventType,
                               'err=', 'Not find game')

    def _unregisterEvents(self, taskKinds):
        interestEventMap = self._collectInterestEventMap(taskKinds)
        for eventType, gameIds in interestEventMap.iteritems():
            for gameId in gameIds:
                game = gdata.games().get(gameId)
                if game:
                    if ftlog.is_debug():
                        ftlog.debug('RPTaskSystem._unregisterEvents gameId=', gameId,
                                    'eventType=', eventType)
                    game.getEventBus().unsubscribe(eventType, self._handleEvent)
                else:
                    ftlog.warn('RPTaskSystem._unregisterEvents gameId=', gameId,
                               'eventType=', eventType,
                               'err=', 'Not find game')

    def _handleEvent(self, event):
        if ftlog.is_debug():
            ftlog.debug('RPTaskSystem._handleEvent',
                        'userId=', event.userId,
                        'event=', event,
                        'closed=', self._closed)
        
        if self._closed:
            return
        
        status = self.loadStatus(event.userId, event.timestamp)
        if status.finished:
            if ftlog.is_debug():
                ftlog.debug('RPTaskSystem._handleEvent',
                            'userId=', event.userId,
                            'task all finished')
            return
        
        if not status.task:
            if ftlog.is_debug():
                ftlog.debug('RPTaskSystem._handleEvent',
                            'userId=', event.userId,
                            'NoTask')
            return
        
        task = status.task
        
        taskChanged, finishCount = task.taskKind.processEvent(task, event)
        if ftlog.is_debug:
            ftlog.debug('RPTaskSystem._handleEvent',
                        'kindId=', task.kindId,
                        'process=', task.progress,
                        'kindIDCount=', task.taskKind.count,
                        'task.gotReward=', task.gotReward,
                        'userId=', event.userId,
                        'taskChanged=', taskChanged,
                        'finishCount=', finishCount)
        
        if taskChanged:
            self.saveStatus(status)
            datachangenotify.sendDataChangeNotify(HALL_GAMEID, status.userId, 'rptask')
            
        if ftlog.is_debug():
            ftlog.debug('RPTaskSystem._handleEvent',
                        'userId=', event.userId,
                        'gameId=', event.gameId,
                        'event=', event,
                        'changed=', taskChanged)


class TYTaskInspectorBindWeixin(TYTaskInspector):
    TYPE_ID = 'hall.bindWeixin'
    EVENT_GAMEID_MAP = {UserBindWeixinEvent: (HALL_GAMEID,),
                        EventUserLogin: (HALL_GAMEID,)}

    def __init__(self):
        super(TYTaskInspectorBindWeixin, self).__init__(self.EVENT_GAMEID_MAP)

    def _processEventImpl(self, task, event):
        if isinstance(event, (UserBindWeixinEvent, EventUserLogin)):
            wxopenid = userdata.getAttr(event.userId, 'wxopenid')
            if wxopenid:
                return task.setProgress(task.progress + 1, event.timestamp)
            snsLoginType = userdata.getAttr(event.userId, 'snsLoginType')
            if snsLoginType and snsLoginType == 'wx':
                return task.setProgress(task.progress + 1, event.timestamp)
                
        return False, 0


_rpTaskSystem = None
_inited = None


def loadUserStatus(userId, timestamp=None):
    timestamp = timestamp or pktimestamp.getCurrentTimestamp()
    return _rpTaskSystem.loadStatus(userId, timestamp)


def findTaskKind(kindId):
    return _rpTaskSystem.findTaskKind(kindId)


def getFirstTask(userId, clientId, timestamp):
    status = _rpTaskSystem.loadStatus(userId, timestamp)
    key = 'newUserTasks' if status.isNewUser else 'oldUserTasks'
    tasks = _rpTaskSystem._getUserTasks(status.userId, clientId, key)
    return tasks[0] if tasks else None


def isWXTaskFinished(userId, timestamp=None):
    timestamp = timestamp or pktimestamp.getCurrentTimestamp()
    status = _rpTaskSystem.loadStatus(userId, timestamp)
    
    # 没有任务算完成
    if not status.task:
        return True
    
    return not status.isFirst
    

def getActs():
    return _rpTaskSystem.getActs()

def getTaskTips(userId, clientId):
    return _rpTaskSystem._getTaskTips(userId, clientId)

def getBoardTip(userId, clientId):
    return _rpTaskSystem._getBoardTip(userId, clientId)

def getHelpUrl(userId, clientId):
    return _rpTaskSystem._getHelpUrl(userId, clientId)

def gainReward(userId, timestamp=None):
    status = loadUserStatus(userId, timestamp)
    return _rpTaskSystem.gainReward(status, timestamp)


def _reloadConf():
    global _rpTaskSystem
    _rpTaskSystem.reloadConf()


def _onConfChanged(event):
    if _inited and event.isChanged('game:9999:red_packet_task:0'):
        _reloadConf()


def _registerClasses():
    TYTaskInspectorRegister.registerClass(TYTaskInspectorBindWeixin.TYPE_ID, TYTaskInspectorBindWeixin)


def _initialize():
    global _inited
    global _rpTaskSystem
    if not _inited:
        _inited = True
        _rpTaskSystem = RPTaskSystem()
        _reloadConf()
        pkeventbus.globalEventBus.subscribe(EventConfigure, _onConfChanged)
        if ftlog.is_debug():
            ftlog.debug('hall_red_packet_task._initialized ok')


