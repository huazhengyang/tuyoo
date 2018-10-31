# -*- coding=utf-8 -*-
'''
Created on 2016-05-18
@desc: 许愿池(许愿井)
@author: luwei
'''
from poker.entity.biz.activity.activity import TYActivity
import freetime.util.log as ftlog
import random
from poker.util import strutil
from datetime import datetime
from dizhu.activities.toolbox import Tool, UserBag, GamedataModel, UserInfo
from dizhu.entity.dizhuconf import DIZHU_GAMEID


class UserModel(GamedataModel):
    '''
    数据模型，封装了读写redis，序列化和反序列化操作，直接可以定义存储字段
    '''

    def __init__(self):
        ## 许愿池配置列表的指向当前可以进行的index
        self.poolStepIndex = 0
        ## 是否已经投入
        self.isAlreadyPutted = False
        ## 计时
        self.lastTimestamp = Tool.datetimeToTimestamp(datetime.now())

    def resetingCounterToCurrentTimestamp(self):
        '''
        重置计时器到当前时间戳
        '''
        self.lastTimestamp = Tool.datetimeToTimestamp(datetime.now())

    def getCountingSeconds(self):
        '''
        获得自resetCounterToCurrentTimestamp调用后到当前的时间(秒)
        '''
        return Tool.datetimeToTimestamp(datetime.now()) - self.lastTimestamp


class Utility(object):
    '''
    工具集，提供了一些繁琐操作的封装
    '''

    @classmethod
    def buildUniqueKey(cls, serverconf):
        '''
        创建唯一key
        '''
        return 'wishingwell'+serverconf.get('start', '0000-00-00 00:00:00')

    @classmethod
    def isActivityOutdate(cls, serverconf):
        '''
        是否活动已经过期
        :return: True/False
        '''
        datetime_start = serverconf.get('start')
        datetime_end = serverconf.get('end')
        ok = not Tool.checkNow(datetime_start, datetime_end)
        ftlog.debug('Utility.isActivityOutdate',
                    'datetime_start=', datetime_start,
                    'datetime_end=', datetime_end,
                    'ok=', ok)
        return ok

    @classmethod
    def isPutIntoButtonOutdate(cls, clientconf):
        '''
        是否投入按钮已经过期,先于活动过期
        :param clientconf:
        :return: True/False
        '''
        buttonconf = Tool.dictGet(clientconf, 'config.putButtonLife', {})
        datetime_start = buttonconf.get('start', '')
        datetime_end = buttonconf.get('end', '')
        ok = not Tool.checkNow(datetime_start, datetime_end)
        ftlog.debug('Utility.isPutIntoButtonOutdate',
                    'buttonconf=', buttonconf,
                    'datetime_start=', datetime_start,
                    'datetime_end=', datetime_end,
                    'ok=', ok)
        return ok

    @classmethod
    def getPoolItemWithStepIndex(cls, clientconf, poolStepIndex):
        '''
        获取许愿池进行第几个的配置
        :param clientconf:
        :param poolStepIndex:
        :return:返回None则代表没有
        '''
        pool = Tool.dictGet(clientconf, 'config.pool')
        ftlog.debug('Utility.getPoolItemWithStepIndex',
                    'poolStepIndex=', poolStepIndex,
                    'pool=', pool)

        if not pool:
            return None
        if len(pool) > poolStepIndex:
            return pool[poolStepIndex]
        return None

    @classmethod
    def buildError(self, error):
        ftlog.debug('wishingwell.Utility.buildError',
                    'error=', error)
        return {'error': error or 'unknow error'}

    @classmethod
    def getPromptTextDictionary(cls, clientconf, model):
        '''
        获得promptText的变量字典
        变量:
        assets_expenses_desc 投入花费资源描述
        duration_desc 需要等待的时间(秒)
        promptdesc 获得资源的范围描述(可以根据bottom和top自动生成)
        '''
        poolItem = Utility.getPoolItemWithStepIndex(clientconf, model.poolStepIndex)
        rewardconf = poolItem.get('reward', {})
        if 'promptdesc' not in rewardconf:
            assets_range = str(rewardconf.get('bottom', 0)) + '~' + str(rewardconf.get('top', 0))
            rewardconf['promptdesc'] = strutil.replaceParams(rewardconf.get('desc'), {'count': assets_range})
        if 'durationDesc' not in poolItem:
            poolItem['durationDesc'] = str(poolItem.get('duration', 0))
        return {
            'assets_expenses_desc': Tool.dictGet(poolItem, 'expenses.desc'),
            'duration_desc': Tool.dictGet(poolItem, 'durationDesc'),
            'promptdesc': Tool.dictGet(poolItem, 'reward.promptdesc')
        }

    @classmethod
    def richtextFormatReplaceParams(cls, richtext, dictionary):
        '''
        promptText中的变量替换
        :param richtext: promptText富文本配置
        :param dictionary: 变量字典
        :return: 替换好的富文本
        '''
        if isinstance(richtext, basestring):
            return strutil.replaceParams(richtext, dictionary)
        for line in richtext:
            for lineitem in line:
                lineitem['text'] = strutil.replaceParams(lineitem['text'], dictionary)
        return richtext

    @classmethod
    def isCountingTimeFinished(cls, poolItem, model):
        '''
        判断计时是否完成,若处于未投入状态,则必返回False
        '''
        countingSeconds = model.getCountingSeconds()
        countingDownRequire = poolItem.get('duration', 0)
        isCountdownFinished = countingSeconds >= countingDownRequire
        if not model.isAlreadyPutted:
            return False
        return isCountdownFinished

    @classmethod
    def getCountingTimeLeft(cls, poolItem, model):
        '''
        获得计时剩余的秒数,时间最小为0
        '''
        countingSeconds = model.getCountingSeconds()
        countingDownRequire = poolItem.get('duration', 0)
        return max(countingDownRequire - countingSeconds, 0)

    @classmethod
    def getPromptText(cls, poolItem, model, clientconf):
        '''
        确定并处理提示语
        :return: 提示语富文本格式
        '''
        config = clientconf.get('config', {})
        if not model.isAlreadyPutted:
            promptText = config['promptTextPutting'] ## 未投入提示语
        else:
            if not cls.isCountingTimeFinished(poolItem, model):
                promptText = config['promptTextCountingDown'] ## 已投入,未到达领取时间
            else:
                promptText = config['promptTextGetting'] ## 已投入,可领取
        promptDictionary = cls.getPromptTextDictionary(clientconf, model)
        ftlog.debug('getPromptText',
                    'promptDictionary=', promptDictionary)
        return cls.richtextFormatReplaceParams(promptText, promptDictionary)

class FixedRewardHandler(object):
    '''
    固定发奖模式处理
    '''
    TYPE_ID = 'fixed'

    def __init__(self, reward, mail):
        self.reward = reward
        self.mail = mail

    def sendToUser(self, userId):
        '''
        返回实际发送的数量
        '''
        count = self.reward.get('count')
        desc  = self.reward.get('desc')
        ftlog.debug('FixedRewardHandler.sendToUser',
                    'userId=', userId,
                    'self.reward=', self.reward,
                    'desc=', desc)
        mail = strutil.replaceParams(self.mail, {'assets_reward_desc':desc})
        UserBag.sendAssetsToUser(DIZHU_GAMEID, userId, self.reward, WishingWell.EVENT_ID, mail)
        return count

class RandomRewardHandler(object):
    '''
    随机发奖模式处理
    '''
    TYPE_ID = 'random'

    def __init__(self, reward, mail):
        self.reward = reward
        self.mail = mail

    def sendToUser(self, userId):
        '''
        返回实际发送的数量
        '''
        itemId = self.reward.get('itemId')
        desc   = self.reward.get('desc')
        bottom = self.reward.get('bottom')
        avg    = self.reward.get('avg')
        top    = self.reward.get('top')
        lteprob= self.reward.get('lteprob')

        if random.random() <= lteprob:
            count = random.randrange(bottom, avg + 1)
        else:
            count = random.randrange(avg, top + 1)

        assets = {'itemId':itemId, 'count':count}
        ftlog.debug('RandomRewardHandler.sendToUser',
                    'userId=', userId,
                    'self.reward=', self.reward,
                    'assets=', assets)
        
        desc = strutil.replaceParams(desc, {'count':count})
        mail = strutil.replaceParams(self.mail, {'assets_reward_desc':desc})

        UserBag.sendAssetsToUser(DIZHU_GAMEID, userId, assets, WishingWell.EVENT_ID, mail)

        return count


class WishingWell(TYActivity):
    TYPE_ID = 6011
    EVENT_ID = 'DDZ_ACT_WISHING'

    def __init__(self, dao, clientConfig, serverConfig):
        super(WishingWell, self).__init__(dao, clientConfig, serverConfig)
        self.rewardHandlerMap = {
            FixedRewardHandler.TYPE_ID : FixedRewardHandler,
            RandomRewardHandler.TYPE_ID : RandomRewardHandler
        }

    def getConfigForClient(self, gameId, userId, clientId):
        '''
        获取客户端要用的活动配置，由TYActivitySystemImpl调用
        '''
        clientconf = strutil.deepcopy(self._clientConf)
        serverconf = self._serverConf
        ftlog.debug('WishingWell.getConfigForClient:',
                    'userId=', userId,
                    'gameId=', gameId,
                    'clientId=', clientId,
                    'serverconf=',serverconf,
                    'clientconf=', clientconf)

        uniquekey = Utility.buildUniqueKey(serverconf)
        model     = UserModel().loadsFromRedis(userId, uniquekey)
        config    = clientconf.get('config',{})

        response  = self.getActivityUserStatus(userId, model)
        config.update(response)

        ## 去掉客户端无用数据
        ignorelist = ['pool', 'nothingPoolItemError', 'countingDownError', 'expensesNotEnoughError',
                      'mail', 'led', 'putButtonLife', 'puttingSuccess', 'wishingOverError', 'promptTextPutting',
                      'promptTextCountingDown', 'promptTextGetting','expensesAssets', 'gettingSuccess']
        for key in ignorelist:
            if key in config:
                config.pop(key)

        ftlog.debug('WishingWell.getConfigForClient:end',
                    'userId=', userId,
                    'clientconf.config=', config)

        return clientconf

    def getActivityUserStatus(self, userId, model):
        '''
        获取用户活动的最新状态
        :param userId: 
        :param model: 
        :return: 
        '''
        clientconf = strutil.deepcopy(self._clientConf)
        response = {}

        poolItem = Utility.getPoolItemWithStepIndex(clientconf, model.poolStepIndex)
        ftlog.debug('WishingWell.getActivityUserStatus',
                    'userId=', userId,
                    'poolItem=', poolItem,
                    'model=', model.dict())

        if not poolItem:
            response['canPutOutdate'] = True
            response['isAlreadyPutted'] = False
            response['isCountintFinished'] = True
            response['countingTimeLeft'] = 0
            response['promptText'] = [[{'text':Tool.dictGet(clientconf, 'config.nothingPoolItemError')}]]
        else:
            ## 判断许愿池投入按钮是否过期
            response['canPutOutdate'] = Utility.isPutIntoButtonOutdate(clientconf)

            ## 当前是领取还是投入
            response['isAlreadyPutted'] = model.isAlreadyPutted

            ## 判断计时是否完成
            response['isCountintFinished'] = Utility.isCountingTimeFinished(poolItem, model)

            ## 计时剩余时间
            response['countingTimeLeft'] = Utility.getCountingTimeLeft(poolItem, model)

            ## 确定提示语
            response['promptText'] = Utility.getPromptText(poolItem, model, clientconf)

        ftlog.debug('WishingWell.getActivityUserStatus',
                    'userId=', userId,
                    'response=', response)
        return response

    def handleRequest(self, msg):
        clientconf = strutil.deepcopy(self._clientConf)
        serverconf = self._serverConf

        userId = msg.getParam('userId')
        activityId = msg.getParam('activityId')
        action = msg.getParam('action')

        ftlog.debug('WishingWell.handleRequest',
                    'userId=', userId,
                    'activityId=', activityId,
                    'action=', action)

        uniquekey = Utility.buildUniqueKey(serverconf)
        model = UserModel().loadsFromRedis(userId, uniquekey)

        if action == 'ddz.wishing.update':
            return self.handleRequestUpdateStatus(model, userId)

        poolItem = Utility.getPoolItemWithStepIndex(clientconf, model.poolStepIndex)
        ftlog.debug('WishingWell.handleRequest',
                    'userId=', userId,
                    'poolItem=', poolItem,
                    'model=', model.dict())

        ## 许愿池已经全部领光
        if not poolItem:
            return Utility.buildError(Tool.dictGet(clientconf, 'config.nothingPoolItemError'))

        ## 已经投入,则逻辑走领取
        if model.isAlreadyPutted:
            return self.handleRequestGetting(model, userId, poolItem)

        ## 未投入,则走投入逻辑
        return self.handleRequestPutting(model, userId, poolItem)

    def handleRequestUpdateStatus(self, model, userId):
        '''
        获取用户活动的最新状态
        :param model:
        :param userId:
        :return:
        '''
        response = self.getActivityUserStatus(userId, model)
        response['operate'] = 'update'
        return response

    def handleRequestGetting(self, model, userId, poolItem):
        '''
        已经投入资本,领取奖励
        :param userId:
        :return:
        '''
        clientconf = strutil.deepcopy(self._clientConf)
        serverconf = self._serverConf
        uniquekey = Utility.buildUniqueKey(serverconf)
        ftlog.debug('WishingWell.handleRequestGetting:start',
                    'userId=', userId,
                    'model=', model.dict())

        ## 判断计时是否完成
        countingSeconds = model.getCountingSeconds()
        if countingSeconds < poolItem.get('duration', 0):  ## 计时未完成
            return Utility.buildError(Tool.dictGet(clientconf, 'config.countingDownError'))

        ## 发送用户奖励
        led = Tool.dictGet(clientconf, 'config.led')
        mail = Tool.dictGet(clientconf, 'config.mail')
        rewardconf = poolItem.get('reward', {})
        rtype = rewardconf.get('type', 'fixed')
        clz = self.rewardHandlerMap[rtype]
        ftlog.debug('WishingWell.handleRequestGetting:send',
                    'userId=', userId,
                    'rewardconf=', rewardconf,
                    'rtype=', rtype,
                    'clz=', clz)
        if not clz:
            return Utility.buildError(None)
        sendcount = clz(rewardconf, mail).sendToUser(userId)

        ## 是否触发LED
        ledTrigger = poolItem.get('ledTrigger', -1)
        if ledTrigger>=0 and ledTrigger<=sendcount:
            nickname = UserInfo.getNickname(userId)
            Tool.sendLed(strutil.replaceParams(led, {'nickname':nickname}))
        ftlog.debug('WishingWell.handleRequestGetting:led',
                    'userId=', userId,
                    'ledTrigger=', ledTrigger,
                    'sendcount=', sendcount,
                    'led-trigger-ok', (ledTrigger>=0 and ledTrigger<=sendcount))

        ftlog.info('WishingWell.handleRequestGetting, ',
                   'userId', userId,
                   'poolstepindex', model.poolStepIndex,
                   'sendcount', sendcount,
                   'model=', model.dict())

        model.isAlreadyPutted = False
        model.poolStepIndex += 1
        model.dumpsToRedis(userId, uniquekey)
        ftlog.debug('WishingWell.handleRequestGetting:end',
                    'userId=', userId,
                    'model=', model.dict())

        response = self.getActivityUserStatus(userId, model)
        gettingSuccess = Tool.dictGet(clientconf, 'config.gettingSuccess')
        rewardDescription = strutil.replaceParams(Tool.dictGet(poolItem, 'reward.desc'), {'count': sendcount})
        if gettingSuccess and len(gettingSuccess) > 0:
            response['message'] = strutil.replaceParams(gettingSuccess, {'assets_reward_desc':rewardDescription})
        response['operate'] = 'getting'
        return response

    def handleRequestPutting(self, model, userId, poolItem):
        '''
        投入资本
        :param userId:
        :return:
        '''
        clientconf = strutil.deepcopy(self._clientConf)
        serverconf = self._serverConf
        uniquekey = Utility.buildUniqueKey(serverconf)
        ftlog.debug('WishingWell.handleRequestPutting:start',
                    'userId=', userId,
                    'model=', model.dict())

        ## 判断许愿池投入按钮是否过期
        if Utility.isPutIntoButtonOutdate(clientconf):
            return Utility.buildError(Tool.dictGet(clientconf, 'config.wishingOverError'))

        ## 许愿消耗费用
        expensesConfig = poolItem.get('expenses')
        expensesItemId = expensesConfig.get('itemId', 'user:chip')
        expensesItemCount = expensesConfig.get('count', 0)
        ftlog.debug('WishingWell.handleRequestPutting:consume',
                    'userId=', userId,
                    'poolItem=', poolItem,
                    'expensesItemId=', expensesItemId,
                    'expensesItemCount=', expensesItemCount)
        if not UserBag.consumeAssetsIfEnough(userId, expensesItemId, expensesItemCount, self.EVENT_ID): ## 费用不足
            return Utility.buildError(Tool.dictGet(clientconf, 'config.expensesNotEnoughError'))

        ## 更新Model
        model.isAlreadyPutted = True
        ## 重置计时,重新开始计时
        model.resetingCounterToCurrentTimestamp()
        model.dumpsToRedis(userId, uniquekey)

        ftlog.info('WishingWell.handleRequestPutting, ',
                   'userId', userId,
                   'poolstepindex', model.poolStepIndex,
                   'model=', model.dict())

        response = self.getActivityUserStatus(userId, model)

        puttingSuccess = Tool.dictGet(clientconf, 'config.puttingSuccess')
        if puttingSuccess and len(puttingSuccess) > 0:
            response['message'] = puttingSuccess
        response['operate'] = 'putting'
        return response
