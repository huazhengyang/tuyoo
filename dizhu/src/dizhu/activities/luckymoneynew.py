# -*- coding=utf-8 -*-
'''
Created on 17-01-09

@author: luwei
'''
import copy
from datetime import datetime, timedelta
import random
import time

from dizhu.activities.toolbox import Tool, Random, UserBag, UserInfo
from dizhu.servers.util.activity_handler import ActivityTcpHelper
from freetime.core.timer import FTTimer
import freetime.util.log as ftlog
from hall.entity import hallitem, hallled, hallshare
from hall.entity.hallshare import HallShareEvent
from hall.entity.todotask import TodoTaskPopTip, TodoTaskHelper
from hall.game import TGHall
from poker.entity.biz.activity.activity import TYActivity
from poker.entity.biz.exceptions import TYBizConfException
from poker.entity.dao import daobase
from poker.entity.events.tyevent import EventConfigure
from poker.protocol import router
from poker.util import strutil


class OpenDurationItem(object):
    def __init__(self, itemConf, dateCursor):
        self.start = datetime.strptime(itemConf['start'], "%H:%M:%S")
        self.end = datetime.strptime(itemConf['end'], "%H:%M:%S")
        self.start = self.start.replace(dateCursor.year, dateCursor.month, dateCursor.day)
        self.end = self.end.replace(dateCursor.year, dateCursor.month, dateCursor.day)

    def getIssueNumber(self):
        return self.start.strftime('%Y.%m.%d.%H.%M.%S')
    
    def getStartLeftSeconds(self):
        '''
        计算当前到时间段开始时间点的剩余时间(秒)，若返回小于0则代表已经过去开始时间点
        '''
        return time.mktime(self.start.timetuple()) - time.mktime(datetime.now().timetuple())
    
    def getEndLeftSeconds(self):
        '''
        计算当前到时间段结束时间点的剩余时间(秒)，若返回小于0则代表已经过去结束时间点
        '''
        return time.mktime(self.end.timetuple()) - time.mktime(datetime.now().timetuple())

    @classmethod
    def create(cls, itemConf, dateCursor, datetimeStart, datetimeEnd):
        duration = OpenDurationItem(itemConf, dateCursor)
        if duration.start >= duration.end:
            raise TYBizConfException(itemConf, 'OpenDurationItem must start < end')
        if datetimeStart <= duration.start and duration.end < datetimeEnd:
            return duration
        return None
             
class OpenDurationList(object):
    def __init__(self, timesConf, serverConf):
        self.itemList = []
        self.datetimeStart = None
        self.datetimeEnd = None
        self.build(timesConf, serverConf)
        
    def build(self, timesConf, serverConf):
        '''
        构建时间列表，并且对时间进行排序
        '''
        self.itemList = []
        self.datetimeStart = datetime.strptime(serverConf['start'], '%Y-%m-%d %H:%M:%S')
        self.datetimeEnd = datetime.strptime(serverConf['end'], '%Y-%m-%d %H:%M:%S')
        datetimeCursor = self.datetimeStart
        while datetimeCursor.date() <= self.datetimeEnd.date():
            for timeConf in timesConf:
                item = OpenDurationItem.create(timeConf, datetimeCursor.date(), self.datetimeStart, self.datetimeEnd)
                if item:
                    self.itemList.append(item)
            datetimeCursor = datetimeCursor + timedelta(days = 1)
        self.itemList.sort(key=lambda item: item.start)
    
    def getCurrentDurationItem(self):
        '''
        获得当前时间段
        '''
        now = datetime.now()
        for item in self.itemList:
            if item.start <= now and now < item.end:
                return item
        return None
    
    def getNextDurationItem(self):
        '''
        获得下一个未到达的时间段
        '''
        now = datetime.now()
        for item in self.itemList:
            if now < item.start and now < item.end:
                return item
        return None
    
    def getLastDurationItem(self):
        '''
        获得上一个已经过去的时间段
        '''
        now = datetime.now()
        last = None
        for item in self.itemList:
            if item.start < now and item.end <= now:
                last = item
        return last
    
    def isBeforeFirstOpen(self):
        '''
        是否是在第一次开红包之前
        '''
        if len(self.itemList) >= 1:
            return datetime.now() < self.itemList[0].start
        return True 
    
    def isAfterFinalOpen(self):
        '''
        是否是在最后一次开红包之后
        '''
        if len(self.itemList) >= 1:
            return self.itemList[-1].end <= datetime.now()
        return False

class LuckyMoneyGenerator(object):
    @classmethod
    def generate(cls, prizesConf):
        # [{'itemId': 'item:1000', 'count': count}, ...]
        luckyMoneys = []
        for item in prizesConf:
            itemType = item.get("type")
            itemId = item.get("itemId")
            num = item.get("num", 0)
            if itemType == "random.split":
                total = item.get("total", 1)
                minv = item.get("min", 1)
                countList = Random.getNormalDistributionRandomSequence(total, minv, num) or []
                luckyMoneys.extend([{'itemId': itemId, 'count': count} for count in countList])
            elif itemType == "random.fixed":
                count = item.get("count", 1)
                luckyMoneys.extend([{'itemId': itemId, 'count': count} for _ in xrange(num)])
        # 将红包乱序
        random.shuffle(luckyMoneys)
        return luckyMoneys

class LuckyMoneyOperator(object):
    
    @classmethod
    def buildPublishFlagKey(cls, poolId):
        return 'act:luckymoneynew:%s.pub' % str(poolId) 
    
    @classmethod
    def buildPoolKey(cls, poolId):
        return 'act:luckymoneynew:%s' % str(poolId) 

    @classmethod
    def setPublisheFlagByIssueNumber(cls, poolId, issueNumber):
        ''' 
        设置红包发布的标记，若成功返回True才可以发布红包，否则代表已经发布
        '''
        rpath = LuckyMoneyOperator.buildPublishFlagKey(poolId)
        isNotPublished = daobase.executeDizhuCmd('HINCRBY', rpath, issueNumber, 1) == 1
        if ftlog.is_debug():
            ftlog.debug('LuckyMoneyOperator.setPublisheFlagByIssueNumber', 
                        'poolId=', poolId, 
                        'issueNumber=', issueNumber, 
                        'isNotPublished=', isNotPublished)
        return isNotPublished
    
    @classmethod
    def clearPublisheFlagByIssueNumber(cls, poolId, issueNumber):
        ''' 
        清除红包发布的标记，在发送失败时调用，以便重新发布 
        '''
        if ftlog.is_debug():
            ftlog.debug('LuckyMoneyOperator.clearPublisheFlagByIssueNumber', 
                        'poolId=', poolId, 
                        'issueNumber=', issueNumber)
        rpath = LuckyMoneyOperator.buildPublishFlagKey(poolId)
        daobase.executeDizhuCmd('HDEL', rpath, issueNumber)

    @classmethod
    def publishLuckyMoneys(cls, poolId, prizeList):
        '''
        将红包数据发布到数据库中
        @param poolId: 红包池key,用于区分不同红包池
        '''
        if ftlog.is_debug():
            ftlog.debug('LuckyMoneyOperator.publishLuckyMoneys', 
                        'poolId=', poolId,
                        'prizeList.count', len(prizeList))
        try:
            rpath = LuckyMoneyOperator.buildPoolKey(poolId)
            # 分批加入到数据库中
            step = 50
            for i in range(0, len(prizeList) , step):
                seg = prizeList[i : i+step]
                jslist = map(lambda v: strutil.dumps(v), seg)
                daobase.executeDizhuCmd('LPUSH', rpath, *jslist)
            return True
        except:
            ftlog.error('LuckyMoneyOperator.publishLuckyMoneys')
            return False
        
    @classmethod
    def clearLuckyMoneys(cls, poolId):
        '''
        清空数据库中的红包数据
        @param poolId: 红包池key,用于区分不同红包池
        '''
        if ftlog.is_debug():
            ftlog.debug('LuckyMoneyOperator.clearLuckyMoneys', 
                        'poolId=', poolId)
        rpath = LuckyMoneyOperator.buildPoolKey(poolId)
        daobase.executeDizhuCmd('LTRIM', rpath, -1, 0)
        
    @classmethod
    def getLuckyMoneyNumbers(cls, poolId):
        '''
        获取剩余红包个数
        @param poolId: 红包池key,用于区分不同红包池
        '''
        rpath = LuckyMoneyOperator.buildPoolKey(poolId)
        return daobase.executeDizhuCmd('LLEN', rpath)

    @classmethod
    def gainLuckyMoney(cls, poolId):
        '''
        领取一个红包
        @param poolId: 红包池key,用于区分不同红包池
        '''
        rpath = LuckyMoneyOperator.buildPoolKey(poolId)
        js = daobase.executeDizhuCmd('RPOP', rpath)
        if js:
            return strutil.loads(js)
        return None

class LuckyMoneyPublisher(object):
    '''
    红包发布者，在指定时间段内自动发布红包
    '''
    def __init__(self, clientConf, openList, poolId):
        '''
        @param openList: 红包开放时间段列表（OpenDurationList对象）
        @param poolId: 红包池key,用于区分不同红包池
        '''
        self.clientConf = clientConf
        self.poolId = poolId
        self.openList = openList
        self.publishTimer = None
        
        # 为了防止当前时间段的红包未发布，所以要主动调用发布(若已经发布，则不会再次发布)
        self._onLuckyMoneyPublish()
        
    def reload(self, clientConf):
        self.clientConf = clientConf
        # 时间点可能发生变化，尝试重新定时发布红包
        self._onLuckyMoneyPublish()      

    def _calculateNextSeconds(self):
        '''
        计算当前到下次发布红包的剩余时间(秒)，若返回小于0则代表没有下次
        '''
        duration = self.openList.getNextDurationItem()
        if not duration:
            return -1
        return duration.getStartLeftSeconds()
    
    def _onLuckyMoneyPublish(self):
        if self.publishTimer:
            self.publishTimer.cancel()
            self.publishTimer = None
        
        # 计算下一次发布红包的剩余秒数
        seconds = self._calculateNextSeconds()
        if seconds >= 0:
            self.publishTimer = FTTimer(seconds, self._onLuckyMoneyPublish)
        
        # 获取当前所在的红包开放时间段，为None则代表当前不处于开放时间段
        duration = self.openList.getCurrentDurationItem()
        if ftlog.is_debug():
            ftlog.debug('LuckyMoneyPublisher._onLuckyMoneyPublish',
                        'poolId=', self.poolId,
                        'seconds=', seconds,
                        'currentDuration.start', duration and duration.start)
        if not duration:
            return
        
        # 当前时间段的期号
        issueNumber = duration.getIssueNumber()
        # 此期红包是否已经发布(多进程情况下，争夺红包发布权，只有一个能返回True)
        isNotPublished = LuckyMoneyOperator.setPublisheFlagByIssueNumber(self.poolId, issueNumber)
        if isNotPublished:
            # 获取红包生成的配置
            prizesConf = Tool.dictGet(self.clientConf, 'config.server.prizes', [])
            # 生成红包列表数据
            prizeList = LuckyMoneyGenerator.generate(prizesConf)
            # 先清空数据库的红包池，防止上一期未抢完的红包污染
            LuckyMoneyOperator.clearLuckyMoneys(self.poolId)
            # 将新生成的红包数据发布到数据库中红包池里
            ok = LuckyMoneyOperator.publishLuckyMoneys(self.poolId, prizeList)
            if not ok:
                LuckyMoneyOperator.clearPublisheFlagByIssueNumber(self.poolId, issueNumber)
                FTTimer(5, self._onLuckyMoneyPublish)
            ftlog.info('LuckyMoneyPublisher._onLuckyMoneyPublish:publish',
                        'poolId=', self.poolId,
                        'issueNumber=', issueNumber,
                        'isNotPublished=', isNotPublished,
                        'currentDuration.start=', duration and duration.start,
                        'publishLuckyMoneys—ok=', ok)
class UserModel(object):
    ''' 用户活动数据 ''' 
    def __init__(self):
        # 记录红包的领取记录Map<issueNumber, 0/1>
        self.history = {}
        # 分享记录Map<issueNumber, 0/1>
        self.shares = {}
        # 上次的奖励，抢红包奖励或者分享奖励
        self.lastPrize = None
    
    def setShared(self, issueNumber, prize):
        '''
        设置分享记录
        '''
        self.shares[issueNumber] = 1
        self.lastPrize = prize
        
    def hadShared(self, issueNumber):
        '''
        判断是否分享过
        '''
        return bool(self.shares.get(issueNumber, 0))
    
    def hadGrabbed(self, issueNumber):
        '''
        是否已经抢过红包
        '''
        return bool(self.history.get(issueNumber, 0))
    
    def setGrabbed(self, issueNumber, prize):
        '''
        设置已经抢过红包
        '''
        self.history[issueNumber] = 1
        self.lastPrize = prize
    
    def toDict(self):
        return {
            'history': self.history,
            'lastPrize': self.lastPrize,
            'shares': self.shares,
        }
    
    def fromDict(self, d):
        self.history = d.get('history',  {})
        self.lastPrize = d.get('lastPrize')
        self.shares = d.get('shares', {})
    
    def save(self, activityGameId, activityId, userId):
        js = strutil.dumps(self.toDict())
        rkey = self.buildKey(activityGameId, userId)
        daobase.executeUserCmd(userId, 'hset', rkey, activityId, js)
        
    @classmethod
    def buildKey(cls, activityGameId, userId):
        return 'act:%s:%s' % (activityGameId, userId)

    @classmethod
    def loadModel(cls, activityGameId, activityId, userId):
        js = None
        model = UserModel()
        try:
            js = daobase.executeUserCmd(userId, 'hget', cls.buildKey(activityGameId, userId), activityId)
            if js:
                model.fromDict(strutil.loads(js))
        except:
            ftlog.error('UserModel.loadModel',
                        'activityGameId=', activityGameId,
                        'activityId=', activityId,
                        'userId=', userId,
                        'js=', js)
        return model

class LuckyMoneyNew(TYActivity):
    '''
    新版红包活动
    '''
    TYPE_ID = 6015
    EVENT_ID = 'DDZ_ACT_LUCKYMONEYNEW_PRIZE'
    ACTION_UPDATE = 'ddz.act.luckymoneynew.update'
    ACTION_GAIN = 'ddz.act.luckymoneynew.gain'
    
    def __init__(self, dao, clientConf, serverConf):
        super(self.__class__, self).__init__(dao, clientConf, serverConf)
        
        # 红包池key,用于区分不同红包池，每个活动对应不同(直接使用活动ID)
        self.poolId = clientConf['id']
        
        # 配置的活动游戏ID，用于存储用户数据，金流日志记录等
        self.activityGameId = Tool.dictGet(clientConf, 'config.server.activityGameId', 6)
        
        # 红包开启时间列表
        timesConf = Tool.dictGet(clientConf, 'config.server.times', [])
        self.openList = OpenDurationList(timesConf, serverConf)
        
        # 红包发布对象，用于定时发布红包
        self.publisher = LuckyMoneyPublisher(clientConf, self.openList, self.poolId)

        # 注册监听事件
        self.registerEvents()
        
        if ftlog.is_debug():
            ftlog.debug('LuckyMoneyNew.__init__:'
                        'activityId=', clientConf['id'],
                        'openList=', [(item.start, item.end) for item in self.openList.itemList])
        
    def registerEvents(self):
        import poker.entity.events.tyeventbus as pkeventbus
        pkeventbus.globalEventBus.subscribe(EventConfigure, self.onConfigChanged)
        TGHall.getEventBus().subscribe(HallShareEvent, self.onEventTableShare)

    def onConfigChanged(self, event):
        clientConf = self._clientConf
        serverConf = self._serverConf
        timesConf = Tool.dictGet(self._clientConf, 'config.server.times', [])
        self.openList.build(timesConf, serverConf)
        self.publisher.reload(clientConf)
        if ftlog.is_debug():
            ftlog.debug('LuckyMoneyNew.onConfigChanged:'
                        'event.keylist=', event.keylist,
                        'poolId=', self.poolId,
                        'activityId=', clientConf['id'],
                        'openList=', [(item.start, item.end) for item in self.openList.itemList])
        ftlog.info('LuckyMoneyNew.onConfigChanged: ok')
       
    def onEventTableShare(self, event):
        if ftlog.is_debug():
            ftlog.debug('LuckyMoneyNew.onEventTableShare:'
                        'event=', event,
                        'event.shareid=', event.shareid)
        activityId = self._clientConf['id']
        shareId = self._clientConf['config']['server']['shareId']
        if event.shareid == shareId: 
            currentDuration = self.openList.getCurrentDurationItem()
            if currentDuration:
                issueNumber = currentDuration.getIssueNumber()
                usermodel = UserModel.loadModel(self.activityGameId, activityId, event.userId)
                # 此期抽奖没有分享过并且已经抢过红包，才算分享成功且给其发奖
                if (not usermodel.hadShared(issueNumber)) and usermodel.hadGrabbed(issueNumber):
                    sharePrize = self._clientConf['config']['server']['sharePrize']
                    shareMail = self._clientConf['config']['server']['shareMail']
                    prizeContent = hallitem.buildContent(sharePrize['itemId'], sharePrize['count'], True)
                    shareMail = strutil.replaceParams(shareMail, {'prizeContent': prizeContent})
                    self.sendPrizeToUser(self.activityGameId, event.userId, sharePrize, shareMail)  
                                      
                    usermodel.setShared(issueNumber, sharePrize)
                    usermodel.save(self.activityGameId, activityId, event.userId)
                    
                    # 给客户端主动推送最新的活动信息
                    activityInfo = self.buildActivityInfo(event.userId, usermodel)
                    mo = ActivityTcpHelper.getOldResponseMsg(activityInfo, event.gameId, event.userId, activityId, self.ACTION_UPDATE)
                    router.sendToUser(mo, event.userId)

            ftlog.info('LuckyMoneyNew.onEventTableShare:'
                       'activityGameId=', self.activityGameId,
                       'shareid=', event.shareid,
                       'activityId=', activityId,
                       'userId=', event.userId,
                       'issueNumber=', currentDuration and currentDuration.getIssueNumber())

    def getConfigForClient(self, gameId, userId, clientId):
        if ftlog.is_debug():
            ftlog.debug('LuckyMoneyNew.getConfigForClient',
                        'gameId=', gameId,
                        'userId=', userId,
                        'clientId=', clientId,
                        'clientConf=', self._clientConf)
        return self.buildActivityInfo(userId)
 
    def sendTip(self, activityGameId, userId, tip):
        todotask = TodoTaskPopTip(tip)
        mo = TodoTaskHelper.makeTodoTaskMsg(activityGameId, userId, todotask)
        router.sendToUser(mo, userId)
           
    def handleRequest(self, msg):
        userId = msg.getParam('userId')
        activityId = msg.getParam("activityId")
        action = msg.getParam("action")
        if ftlog.is_debug():
            ftlog.debug('LuckyMoneyNew.handleRequest',
                        'activityGameId=', self.activityGameId,
                        'activityId=', activityId,
                        'userId=', userId,
                        'action=', action)
        if action == self.ACTION_GAIN:
            return self.onActionGain(userId, activityId)
        elif action == self.ACTION_UPDATE:
            return self.buildActivityInfo(userId)
        return self.buildActivityInfo(userId)
 
    def buildActivityInfo(self, userId, usermodel=None):
        clientconf = copy.deepcopy(self._clientConf)
        if not usermodel:
            usermodel = UserModel.loadModel(self.activityGameId, self._clientConf['id'], userId)

        # 分享按钮显示与消失
        # 小红包按钮上的文字显示
        # 倒计时时间
        # 大红包按钮上的文字显示
        # 小红包上的提示文字显示
        
        # 默认不显示分享按钮
        clientconf['config']['client']['buttonShare']['visible'] = False
        
        currentDuration = self.openList.getCurrentDurationItem()
        if currentDuration:
            # 正在抢红包时间段
            clientconf['config']['client']['secondsStart'] = 0
            clientconf['config']['client']['secondsStop'] = currentDuration.getEndLeftSeconds()
            # 是否已经抢过红包
            issueNumber = currentDuration.getIssueNumber()
            if ftlog.is_debug():
                ftlog.debug('LuckyMoneyNew.buildActivityInfo:currentDuration',
                            'userId=', userId,
                            'activityId=', clientconf['id'],
                            'issueNumber=', issueNumber,
                            'hadGrabbed=', usermodel.hadGrabbed(issueNumber),
                            'hadShared=', usermodel.hadShared(issueNumber),
                            'lastPrize=', usermodel.lastPrize)
            # 若玩家已经已抢过此期红包
            if usermodel.hadGrabbed(issueNumber):
                # 主按钮提示已抢到
                clientconf['config']['client']['buttonMain']['title'] = clientconf['config']['client']['buttonMain']['title.grabbed']
                # 抢到的红包奖励，分享奖励，或者啥也没抢到的信息
                clientconf['config']['client']['prizeInfo'] = self.buildPrizeContent(usermodel.lastPrize)
                # 存在已经抢到的奖励或者分享获得的奖励
                if not usermodel.lastPrize:
                    clientconf['config']['client']['buttonShare']['visible'] = True
                    share = hallshare.findShare(clientconf['config']['server']['shareId'])
                    if share:
                        todotask = share.buildTodotask(self.activityGameId, userId, None)
                        clientconf['config']['client']['buttonShare']['todotask'] = todotask.toDict()
                    # 红包被抢光，用户没有奖励
                    clientconf['config']['client']['labelTip'] = clientconf['config']['client']['labelTip.grabbed_null']
                else:
                    if usermodel.hadShared(issueNumber):
                        clientconf['config']['client']['labelTip'] = clientconf['config']['client']['labelTip.shared']
                    else:
                        clientconf['config']['client']['labelTip'] = clientconf['config']['client']['labelTip.gained']
            else:
                # 抢红包
                clientconf['config']['client']['buttonMain']['title'] = clientconf['config']['client']['buttonMain']['title.grab']
        else: 
            nextDuration = self.openList.getNextDurationItem()
            clientconf['config']['client']['secondsStart'] = nextDuration.getStartLeftSeconds() if nextDuration else 0
            clientconf['config']['client']['secondsStop'] = nextDuration.getEndLeftSeconds() if nextDuration else 0
            if nextDuration:
                # 未开始
                clientconf['config']['client']['buttonMain']['title'] = clientconf['config']['client']['buttonMain']['title.unstart']
            else:
                # 已结束
                clientconf['config']['client']['buttonMain']['title'] = clientconf['config']['client']['buttonMain']['title.final']
        return clientconf
        
    def onActionGain(self, userId, activityId):
        clientConf = self._clientConf
        
        # 检测活动是否过期
        if not self.checkOperative():
            tip = Tool.dictGet(clientConf, "config.server.outdateTip")
            self.sendTip(self.activityGameId, userId, tip)
            return self.buildActivityInfo(userId)

        # 获取当前所在的红包开放时间段
        duration = self.openList.getCurrentDurationItem()
        if not duration:
            if self.openList.isAfterFinalOpen(): 
                tip = Tool.dictGet(clientConf, "config.server.finalTip")
            else:
                tip = Tool.dictGet(clientConf, "config.server.beforeGainTip")
            self.sendTip(self.activityGameId, userId, tip)
            return self.buildActivityInfo(userId)
        
        issueNumber = duration.getIssueNumber()
        model = UserModel.loadModel(self.activityGameId, activityId, userId)
        if ftlog.is_debug():
            ftlog.debug('LuckyMoneyNew.onActionGain',
                        'activityId=', activityId,
                        'userId=', activityId,
                        'issueNumber=', issueNumber,
                        'hadGrabbed=', model.hadGrabbed(issueNumber),
                        'hadShared=', model.hadShared(issueNumber))
        # 是否已经抢过红包
        if model.hadGrabbed(issueNumber):
            tip = Tool.dictGet(clientConf, "config.server.alreadyGainedTip")
            self.sendTip(self.activityGameId, userId, tip)
            return self.buildActivityInfo(userId, model)
        
        # 从红包池中领取红包，若返回None，则代表红包已派发完毕
        prize = LuckyMoneyOperator.gainLuckyMoney(self.poolId)
        if ftlog.is_debug():
            ftlog.debug('LuckyMoneyNew.onActionGain:gain',
                        'activityId=', activityId,
                        'userId=', activityId,
                        'issueNumber=', issueNumber,
                        'prize=', prize)
        if not prize:
            model.setGrabbed(issueNumber, prize)
            model.save(self.activityGameId, activityId, userId)
            tip = Tool.dictGet(clientConf, "config.server.emptyGetTip")
            self.sendTip(self.activityGameId, userId, tip)
            return self.buildActivityInfo(userId, model)
        
        # 给用户发奖，并记录红包领取，发送LED
        mail = Tool.dictGet(clientConf, "config.server.mail")
        count = self.sendPrizeToUser(self.activityGameId, userId, prize, mail)
        if ftlog.is_debug():
            ftlog.debug('LuckyMoneyNew.onActionGain:sent',
                        'activityId=', activityId,
                        'userId=', activityId,
                        'issueNumber=', issueNumber,
                        'count=', count)
        if count > 0:
            model.setGrabbed(issueNumber, prize)
            model.save(self.activityGameId, activityId, userId)
            self.sendLedText(self.activityGameId, userId, prize)
            ftlog.info('LuckyMoneyNew.onActionGain',
                       'activityGameId=', self.activityGameId,
                       'issueNumber=', issueNumber,
                       'activityId=', activityId,
                       'poolId=', self.poolId,
                       'userId=', userId,
                       'prize=', prize)
        return self.buildActivityInfo(userId, model)
    
    def buildPrizeContent(self, prize):
        if prize:
            assetKindId = prize['itemId']
            count = prize['count']
            assetKind = hallitem.itemSystem.findAssetKind(assetKindId)
            if assetKind:
                intCount = int(count)
                intFmt = '%s%s\n%s'
                floatFmt = '%.2f%s\n%s'
                fmt = intFmt if intCount == count else floatFmt
                return fmt % (count, assetKind.units, assetKind.displayName)
            return ''
        return self._clientConf['config']['server']['prizeInfo.grabbed_null']
    
    def sendLedText(self, activityGameId, userId, prize):
        ledsMap = Tool.dictGet(self._clientConf, 'config.server.ledsMap', {})
        prizes = Tool.dictGet(self._clientConf, 'config.server.prizes', [])
        
        for item in prizes:
            # 根据奖励itemId找到奖励配置
            if item['itemId'] != prize['itemId']:
                continue
            # 获取led发送的配置
            ledItem = ledsMap.get(item.get('ledKey'))
            if not ledItem:
                continue
            # 查看是否满足LED发送条件
            if ledItem.get('minCount', 0) > prize['count']:
                continue
            text = ledItem.get('text')
            if not text:
                continue
            prizeContent = hallitem.buildContent(prize['itemId'], prize['count'], True)
            ledtext = strutil.replaceParams(text, {'nickname': UserInfo.getNickname(userId), 
                                                   'prizeContent': prizeContent})
            hallled.sendLed(activityGameId, ledtext, 0, scope='hall6')
            if ftlog.is_debug():
                ftlog.debug('LuckyMoneyNew.sendLedText',
                            'activityGameId=', activityGameId,
                            'activityId=', self._clientConf['id'],
                            'userId=', userId,
                            'ledtext=', ledtext)
            break
        
    def sendPrizeToUser(self, activityGameId, userId, prize, mail):
        prizeContent = hallitem.buildContent(prize['itemId'], prize['count'], True)
        mailmessage = strutil.replaceParams(mail, {'prizeContent': prizeContent})
        _, addcount, _ = UserBag.sendAssetsToUser(activityGameId, userId, prize, self.EVENT_ID, mailmessage, 0)
        if ftlog.is_debug():
            ftlog.debug('LuckyMoneyNew.sendPrizeToUser',
                        'activityGameId=', activityGameId,
                        'userId=', userId,
                        'prize=', prize,
                        'addcount=', addcount)
        return addcount

def initialize():
    ftlog.info('luckymoneynew.initialize')