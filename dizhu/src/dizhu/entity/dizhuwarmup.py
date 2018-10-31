# -*- coding=utf-8 -*-
'''
Created on 2016年4月27日

@author: luwei

热身系统功能实现
'''

from dizhu.entity import dizhuconf
import freetime.util.log as ftlog
from dizhu.activities.toolbox import UserBag, UserInfo, Redis, Tool, LotteryPool
from poker.util import strutil
from poker.entity.configure import gdata
from datetime import datetime
from poker.entity.dao import daobase

BIEVENT_ID = 'DDZ_WARMUP_SYSTEM'

def getWarmupSystemConfig():
    '''
    获得热身系统的配置
    '''
    return dizhuconf.getPublic().get('warmupSystem', {})


class WarmUpSystemLotteryPool(object):
    '''
    热身系统:抽奖奖池
    用于构造奖池,从奖池中抽奖等
    '''
    def __init__(self):
        self.lotteryPool = LotteryPool()
        self.rebuildLotteryPool()

    def randomGetPoolItem(self):
        '''
        随机获取一个奖励配置项
        '''
        return self.lotteryPool.randomChoose()

    def rebuildLotteryPool(self):
        '''
        重新构建奖励池
        '''
        self.lotteryPool.clear()
        poolConfigure = self.getPrizeListConfigure()
        ftlog.debug('WarmUpSystemLotteryPool', 'poolConfigure', poolConfigure)
        for prize in poolConfigure:
            self.lotteryPool.addingPrize(prize, prize.get('weight', 0))

    @classmethod
    def getPrizeListConfigure(cls):
        '''
        获取奖池配置
        '''
        return getWarmupSystemConfig().get('rewardPool', [])

class CountingTimer(object):
    '''
    秒计时器,用于CD(冷却)计时
    '''
    countingTimerUniqueKey = 'WarmUpSystem.CountingTimer'

    @classmethod
    def resetCounting(cls, userId):
        '''
        重置计时器到当前时间
        '''
        data = {'timestamp': Tool.datetimeToTimestamp(datetime.now())}
        Redis.writeJson(userId, cls.countingTimerUniqueKey, data)

    @classmethod
    def getCountingSeconds(cls, userId):
        '''
        获得计时的秒数
        '''
        data = Redis.readJson(userId, cls.countingTimerUniqueKey)
        laststamp = data.get('timestamp')
        if not laststamp:
            cls.resetCounting(userId)
            return -1
        return Tool.datetimeToTimestamp(datetime.now()) - laststamp

    @classmethod
    def checkCooldownFinish(cls, userId):
        '''
        检测冷却是否达到
        '''
        conf = getWarmupSystemConfig()
        cooldownRequire = conf.get('cooldown', 0)
        seconds = cls.getCountingSeconds(userId)
        ftlog.debug('WarmUpSystem.CountingTimer.checkCooldownFinish',
                    'userId=', userId,
                    'counting-sconds=', seconds,
                    'cooldownRequire=', cooldownRequire)
        if seconds < 0: ## 小于0代表,之前没有重置过,是第一次检查,直接返回True
            return True
        return seconds >= cooldownRequire

    @classmethod
    def getConfigureRequireCooldownSeconds(cls):
        '''
        获得配置的CD时间
        '''
        conf = getWarmupSystemConfig()
        return conf.get('cooldown', 0)

class WarmUpSystemHelper(object):
    '''
    热身系统,
    '''
    @classmethod
    def checkAssetsEnough(cls, userId):
        '''
        检测抽奖需要的花费是否足够
        '''
        conf = getWarmupSystemConfig()
        consumeAssets = conf.get('expensesAssets', {})
        requireItemId = consumeAssets.get('itemId')
        requireItemCount = consumeAssets.get('count', 0)

        if not requireItemId:
            return False

        userHaveAssetsCount = UserBag.getAssetsCount(userId, requireItemId)
        ftlog.debug('WarmUpSystemHelper.checkAssetsEnough',
                    'userId=', userId,
                    'consumeAssets=', consumeAssets,
                    'userHaveAssetsCount=', userHaveAssetsCount)

        return userHaveAssetsCount >= requireItemCount

    @classmethod
    def buildLuckyDrawMailMessage(cls, itemconf, roomId):
        '''
        构建邮箱信息
        '''
        conf = getWarmupSystemConfig()
        mail = conf.get('mail', '')
        roomconf = gdata.getRoomConfigure(roomId)
        matchName = roomconf.get('name', '')
        dictionary = {'assets_desc': itemconf.get('desc', ''), 'match_name':matchName}
        return strutil.replaceParams(mail, dictionary)

    @classmethod
    def buildLuckyDrawMessage(cls, itemconf):
        '''
        构建response中的结果说明信息
        '''
        message = itemconf.get('message', '')
        dictionary = {'assets_desc': itemconf.get('desc', '')}
        return strutil.replaceParams(message, dictionary)

    @classmethod
    def consumeLuckyDrawExpenses(cls, userId):
        '''
        消耗抽奖花费
        :return 费用不足返回False
        '''
        conf = getWarmupSystemConfig()
        consumeAssets = conf.get('expensesAssets', {})
        expensesItemId = consumeAssets.get('itemId')
        expensesItemCount = consumeAssets.get('count', 0)
        ftlog.debug('WarmUpSystemHelper.consumeLuckyDrawExpenses',
                    'userId=', userId,
                    'itemId=', expensesItemId,
                    'count=', expensesItemCount)
        return UserBag.consumeAssetsIfEnough(userId, expensesItemId, expensesItemCount, BIEVENT_ID)

    @classmethod
    def getLuckyDrawExpenses(cls):
        '''
        抽奖消耗的物品
        '''
        conf = getWarmupSystemConfig()
        return conf.get('expensesAssets', {})

    @classmethod
    def buildSuccessMessagePack(cls, userId, itemconf):
        '''
        构建抽奖成功的result结果
        @param: itemconf - 抽到的奖励项
        '''
        return {'success':True, 'message': cls.buildLuckyDrawMessage(itemconf),
                'name': UserInfo.getNickname(userId), 'mychip': UserInfo.getChip(userId)}


class LuckyDrawRecorder(object):
    '''
    热身系统:抽奖记录器
    用于处理添加记录,获取记录
    注意:前取前入后出
    '''
    leastRecordNumber = 20 # 至少存储的记录数量
    removeTriggerLimitNumber = 30 # 触发删除操作的数量(要大于等于`leastRecordNumber`)
    recordUniqueKey = 'dizhu:warmup'

    @classmethod
    def getDefaultFetchMessageNumber(cls):
        '''
        获取默认的拉取记录条数
        '''
        conf = getWarmupSystemConfig()
        return conf.get('defaultMessageNumber', 10)

    @classmethod
    def pushRecord(cls, record):
        '''
        增加一条抽奖记录
        '''
        daobase.executeMixCmd('lpush', cls.recordUniqueKey, strutil.dumps(record))
        cls.autoRemoveOvertopReocrdIfNeed()

    @classmethod
    def getRecordWithNumber(cls, number):
        '''
        获得指定数量的抽奖记录
        '''
        if number <= 0:
            number = cls.getDefaultFetchMessageNumber()
        records = daobase.executeMixCmd('lrange', cls.recordUniqueKey, 0, number - 1) or []
        for x in xrange(0, len(records)):
            records[x] = strutil.loads(records[x])
        return records

    @classmethod
    def autoRemoveOvertopReocrdIfNeed(cls):
        '''
        如果需要就会自动删除超出`leastRecordNumber`个数的元素
        '''
        length = daobase.executeMixCmd('llen', cls.recordUniqueKey)
        if length > cls.removeTriggerLimitNumber:
            daobase.executeMixCmd('ltrim', cls.recordUniqueKey, 0, cls.leastRecordNumber - 1)

    @classmethod
    def buildRecord(cls, userId, itemconf):
        return {'message': WarmUpSystemHelper.buildLuckyDrawMessage(itemconf), 'name': UserInfo.getNickname(userId)}

class WarmUpSystem(object):
    '''
    热身系统
    '''
    @classmethod
    def onUserLuckyDraw(cls, userId, roomId):
        '''
        热身系统:抽奖处理
        '''
        ftlog.debug('WarmUpSystem.onUserLuckyDraw',
                    'userId=', userId,
                    'roomId=', roomId)

        global warmupLotteryPool
        if not warmupLotteryPool:
            warmupLotteryPool = WarmUpSystemLotteryPool()

        ftlog.debug('WarmUpSystem.onUserLuckyDraw',
                    'userId=', userId,
                    'warmupLotteryPool.prizeList=', warmupLotteryPool.lotteryPool.prizeList)


        ## 处理抽奖花费不足
        if not WarmUpSystemHelper.checkAssetsEnough(userId):
            return {'success':False, 'mychip': UserInfo.getChip(userId)}

        ## 处理抽奖CD
        if not CountingTimer.checkCooldownFinish(userId):
            return {'success':False, 'mychip': UserInfo.getChip(userId)}

        ## 消耗抽奖花费
        if not WarmUpSystemHelper.consumeLuckyDrawExpenses(userId):
            return {'success':False, 'mychip': UserInfo.getChip(userId)}

        chooseItemConfigure = warmupLotteryPool.randomGetPoolItem()
        ftlog.debug('WarmUpSystem.onUserLuckyDraw',
                    'userId=', userId,
                    'chooseItemConfigure=', chooseItemConfigure)

        ## 重置CD时间
        CountingTimer.resetCounting(userId)

        ## 抽奖未抽中
        chooseitemId = chooseItemConfigure.get('itemId')
        if not chooseitemId or len(chooseitemId) <= 0:
            return WarmUpSystemHelper.buildSuccessMessagePack(userId, chooseItemConfigure)

        ## 发送抽奖奖励
        prizeMail = WarmUpSystemHelper.buildLuckyDrawMailMessage(chooseItemConfigure, roomId)
        UserBag.sendAssetsToUser(6, userId, chooseItemConfigure, BIEVENT_ID, prizeMail)

        ## 添加消息到抽奖记录中
        LuckyDrawRecorder.pushRecord(LuckyDrawRecorder.buildRecord(userId, chooseItemConfigure))

        return WarmUpSystemHelper.buildSuccessMessagePack(userId, chooseItemConfigure)

    @classmethod
    def onGetRecordMessage(cls, userId, number):
        '''
        获得抽奖记录处理
        '''
        messageList = LuckyDrawRecorder.getRecordWithNumber(number)
        ftlog.debug('WarmUpSystem.onGetRecordMessage',
                    'userId=', userId,
                    'number=', number,
                    'messageList=', messageList)
        return {
            'messages':messageList or [],
            'cd': CountingTimer.getConfigureRequireCooldownSeconds(),
            'chip': WarmUpSystemHelper.getLuckyDrawExpenses().get('count'), # 只会消耗金币
            'mychip': UserInfo.getChip(userId)
        }

warmupLotteryPool = None
isNotFirstTimeInitialize = False

def onConfigChanged(event):
    if event.isChanged('game:6:public:0'):
        ftlog.debug('WarmUpSystemRewardPool.onConfigChanged')
        global warmupLotteryPool
        warmupLotteryPool = None

def onModuleInitialize():
    ftlog.debug('WarmUpSystemRewardPool.onModuleInitialize')
    from poker.entity.events.tyevent import EventConfigure
    import poker.entity.events.tyeventbus as pkeventbus
    global isNotFirstTimeInitialize
    if not isNotFirstTimeInitialize:
        isNotFirstTimeInitialize = True
        pkeventbus.globalEventBus.subscribe(EventConfigure, onConfigChanged)
    ftlog.debug('WarmUpSystemRewardPool.onModuleInitialize')

onModuleInitialize()
