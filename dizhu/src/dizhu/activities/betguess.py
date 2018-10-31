# -*- coding=utf-8 -*-
'''
Created on 16-10-24

@author: luwei

@desc: 下注竞猜活动
'''
from __future__ import division

import copy
from datetime import datetime

from dizhu.activities.toolbox import Tool
import freetime.util.log as ftlog
from hall.entity import datachangenotify
import hall.entity.hallstore as hallstore
from hall.entity.todotask import TodoTaskHelper, \
    TodoTaskLessBuyOrder
from poker.entity.biz.activity.activity import TYActivity
import poker.entity.biz.message.message as pkmessage
from poker.entity.dao import daobase, userchip, sessiondata, daoconst
from poker.entity.events.tyevent import EventConfigure
from poker.util import strutil


#
class ActivityUserModel(object):
    ''' 用户活动数据，以期号为key查询ActivityUserModel.Item ''' 
    
    class Item(object):
        def __init__(self):
            # 本期活动是否给用户发送过奖励
            self.isPrizeSent = False
            # 用户左侧押注金额
            self.leftBetValue = 0
            # 用户右侧押注金额
            self.rightBetValue = 0

    ItemNull = Item()

    def __init__(self, userId, activityGameId, activityId):
        self.items = {}
        
        self.userId = userId
        self.activityGameId = activityGameId
        self.activityId = activityId
    
    def fromDict(self, d):
        if not d:
            return self
        items = d.get('items', {})
        
        self.items = {}
        for issueNumber, v in items.iteritems():
            item = ActivityUserModel.Item()
            item.isPrizeSent = v['isPrizeSent']
            item.leftBetValue = v['leftBetValue']
            item.rightBetValue = v['rightBetValue']
            self.items[issueNumber] = item
            
        return self
    
    def toDict(self):
        items = {}
        for issueNumber, item in self.items.iteritems():
            items[issueNumber] = {
                'isPrizeSent': item.isPrizeSent,
                'leftBetValue': item.leftBetValue,
                'rightBetValue': item.rightBetValue
            }
            
        return {'items': items}
    
    def findItemByIssueNumber(self, issueNumber):
        ''' 根据期号查找数据Item，若找不到则返回None '''
        return self.items.get(issueNumber)
    
    def findOrCreateItemByIssueNumber(self, issueNumber):
        ''' 根据期号查找数据Item，若找不到则创建一个新的Item(数据都是默认的) '''
        item = self.findItemByIssueNumber(issueNumber)
        if not item:
            item = ActivityUserModel.Item()
            self.items[issueNumber] = item
        return item

    def incrChip(self, issueNumber, isLeft, chip):
        ''' 增加用户数据记录Item的押注金额 '''
        assert(chip>=0)
        item = self.findItemByIssueNumber(issueNumber)
        if isLeft:
            item.leftBetValue += chip
        else:
            item.rightBetValue += chip
        return self
    
    def save(self):
        ''' 保存用户数据 '''
        jstr = strutil.dumps(self.toDict())
        rpath = self.getRedisStoragePath(self.activityGameId, self.userId)
        daobase.executeUserCmd(self.userId, 'hset', rpath, self.activityId, jstr)

    @classmethod
    def getRedisStoragePath(cls, activityGameId, userId):
        return 'act:%s:%s' % (activityGameId, userId)

    @classmethod
    def loadModel(cls, userId, activityGameId, activityId):
        jstr = None
        model = ActivityUserModel(userId, activityGameId, activityId)
        try:
            jstr = daobase.executeUserCmd(userId, 'hget', cls.getRedisStoragePath(activityGameId, userId), activityId)
            if jstr:
                model.fromDict(strutil.loads(jstr))
        except:
            ftlog.error('ActivityUserModel.load',
                        'userId=', userId,
                        'activityGameId=', activityGameId,
                        'activityId=', activityId,
                        'jstr=', jstr)
        return model

    
class ActivityModel(object):
    ''' 活动奖池数据，存储在mix库中 '''
    
    RESULT_STATE_NONE = 0 # 未开奖
    RESULT_STATE_LEFT = 1 # 左侧胜利
    RESULT_STATE_RIGHT = 2 # 右侧胜利
    
    def __init__(self, activityGameId, activityId, issueNumber):
        # 左侧累计投注金额
        self.countChipLeft = 0
        # 右侧累计投注金额
        self.countChipRight = 0
        # 比赛结果
        self.resultState = self.RESULT_STATE_NONE
        
        # 当前数据的期号
        self.issueNumber = issueNumber
        self.activityId = activityId
        self.activityGameId = activityGameId
    
    def incrChip(self, isLeft, chip):
        ''' 奖池增加金币, 区分左右奖池 '''
        rpath = self.getRedisStoragePath(self.activityGameId, self.activityId, self.issueNumber)
        if isLeft:
            self.countChipLeft = daobase.executeDizhuCmd('hincrby', rpath, 'countChipLeft', chip)
        else:
            self.countChipRight = daobase.executeDizhuCmd('hincrby', rpath, 'countChipRight', chip)
        return self

    @classmethod
    def getRedisStoragePath(cls, activityGameId, activityId, issueNumber):
        ''' act.betguess:${activityGameId}:${activityId}:${issueNumber} '''
        issueNumber = issueNumber.replace(':', '.').replace(' ', '.').replace('-', '.')
        return 'act.betguess.info:' + str(activityGameId) + ':' + str(activityId) + ':' + (issueNumber)

    @classmethod
    def loadModel(cls, activityGameId, activityId, issueNumber):
        ''' 加载数据，返回新的数据模型 '''
        rpath = cls.getRedisStoragePath(activityGameId, activityId, issueNumber)
        value1, value2, value3 = daobase.executeDizhuCmd('hmget', rpath, 'countChipLeft', 'countChipRight', 'resultState')

        model = ActivityModel(activityGameId, activityId, issueNumber)
        model.countChipLeft = value1 or 0
        model.countChipRight = value2 or 0
        model.resultState = value3 or cls.RESULT_STATE_NONE
        return model
        
    @classmethod
    def updateResult(cls, activityGameId, activityId, issueNumber, resultState):
        ''' 根据期号更新活动竞猜结果 '''
        if resultState != cls.RESULT_STATE_NONE and \
            resultState != cls.RESULT_STATE_LEFT and \
            resultState !=  cls.RESULT_STATE_RIGHT:
            return False
        rpath = cls.getRedisStoragePath(activityGameId, activityId, issueNumber)
        daobase.executeDizhuCmd('hset', rpath, 'resultState', resultState)
        return True

class UserRecorder(object):
    ''' 用于记录玩家userId '''
    
    @classmethod
    def getRedisStoragePath(cls, activityGameId, activityId, issueNumber):
        ''' act.betguess.userids:${activityGameId}:${activityId}:${issueNumber}:userids '''
        issueNumber = issueNumber.replace(':', '.').replace(' ', '.').replace('-', '.')
        return 'act.betguess.userids:' + str(activityGameId) + ':' + str(activityId) + ':' + (issueNumber)

    @classmethod
    def addUser(cls, userId, activityGameId, activityId, issueNumber):
        ''' 记录用户ID '''
        rpath = cls.getRedisStoragePath(activityGameId, activityId, issueNumber)
        daobase.executeDizhuCmd('sadd', rpath, userId)
        
    @classmethod
    def getUsers(cls, activityGameId, activityId, issueNumber):
        ''' 获得指定活动期号的所有参与用户userId '''
        rpath = cls.getRedisStoragePath(activityGameId, activityId, issueNumber)
        return daobase.executeDizhuCmd('smembers', rpath)

    
class IssueCalculator(object):
    ''' 期号计算器 '''
    def __init__(self, issueMap):
        self.issueMap = {}
        self.reloadIssueList(issueMap)
    
    def getCurrentIssueNumber(self, dt=None):
        dtnow = dt or datetime.now()
        issueKeys = self.issueMap.keys()
        issueKeys.sort()
        ftlog.debug('IssueCalculator.getCurrentIssueNumber:issueKeys=', issueKeys)
          
        for issue in issueKeys:
            currentIssueDatetime = datetime.strptime(issue, '%Y-%m-%d %H:%M:%S')
            if dtnow <= currentIssueDatetime:
                return issue

        return None 
    
    def getLastIssueNumber(self):
        ''' 获取最后一期的期号 '''
        issueKeys = self.issueMap.keys()
        issueKeys.sort()
        return issueKeys[len(issueKeys)-1]
    
    def getCurrentIssueConf(self, issue=None):
        issue = issue or self.getCurrentIssueNumber()
        if issue:
            return self.issueMap.get(issue)
        return None
    
    def reloadIssueList(self, issueMap):
        self.issueMap = issueMap

    def getAlreadyPastIssueNumberList(self):
        ''' 获取已经过去的期号列表 '''
        dtnow = datetime.now()
        issueList = []
        for issueKey in self.issueMap.keys():
            currentIssueDatetime = datetime.strptime(issueKey, '%Y-%m-%d %H:%M:%S')
            if dtnow > currentIssueDatetime:
                issueList.append(issueKey)
                
        issueList.sort()
        return issueList
        
class BetGuess(TYActivity):
    '''
    NBA竞猜活动
    '''
    TYPE_ID = 6012

    def __init__(self, dao, clientConfig, serverConfig):
        super(self.__class__, self).__init__(dao, clientConfig, serverConfig)
        ftlog.debug('BetGuess.__init__')
        
        issueMap = Tool.dictGet(clientConfig, 'config.issueMap', {})
        ftlog.debug('BetGuess.__init__:issueMap=', issueMap)
        self.issueCalculator = IssueCalculator(issueMap)
        
        # 注册监听事件
        self.registerEvents()
        
    def registerEvents(self):
        import poker.entity.events.tyeventbus as pkeventbus
        pkeventbus.globalEventBus.subscribe(EventConfigure, self.onConfigChanged)

    def onConfigChanged(self, event):
        ftlog.debug('BetGuess.onConfigChanged')
        # 此活动有可能在不通的游戏活动中配置
        issueMap = Tool.dictGet(self._clientConf, 'config.issueMap', {})
        self.issueCalculator.reloadIssueList(issueMap)
        ftlog.debug('BetGuess.onConfigChanged: ok')

    def getConfigForClient(self, gameId, userId, clientId):
        clientconf = self._clientConf
        serverconf = self._serverConf
        ftlog.debug('BetGuess.getConfigForClient:',
            'userId=', userId, 
            'gameId=', gameId,  
            'clientId', clientId, 
            'serverconf=',serverconf, 
            'clientconf=', clientconf)
        return self.buildActivityInfo(userId)

    def getPrizeStatus(self, activityModel, userModelItem):
        ''' 获取发奖状态 '''
        clientconf = self._clientConf
        
        # 用户数据记录：未发奖
        if activityModel.resultState == activityModel.RESULT_STATE_NONE:
            return Tool.dictGet(clientconf, 'config.server.recordCellWaitingResultTip', '未开奖')
        
        if activityModel.resultState == activityModel.RESULT_STATE_LEFT and userModelItem.leftBetValue > 0:
            return Tool.dictGet(clientconf, 'config.server.recordCellResultWinTip', '猜中')
        if activityModel.resultState == activityModel.RESULT_STATE_RIGHT and userModelItem.rightBetValue > 0:
            return Tool.dictGet(clientconf, 'config.server.recordCellResultWinTip', '猜中')
        
        return Tool.dictGet(clientconf, 'config.server.recordCellResultLoseTip', '未猜中')

    def getPrizeNumber(self, bankerPumping, activityModel, userModelItem):       
        ''' 计算奖金金额 ''' 
        # 奖池金额
        betPoolChip = (activityModel.countChipLeft+activityModel.countChipRight)*(1-bankerPumping)
        # 左赔率
        leftBetOdds = betPoolChip/activityModel.countChipLeft if activityModel.countChipLeft>0 else 0
        # 右赔率
        rightBetOdds = betPoolChip/activityModel.countChipRight if activityModel.countChipRight>0 else 0

        if activityModel.resultState == activityModel.RESULT_STATE_LEFT and userModelItem.leftBetValue > 0:
            return int(userModelItem.leftBetValue * leftBetOdds)
        if activityModel.resultState == activityModel.RESULT_STATE_RIGHT and userModelItem.rightBetValue > 0:
            return int(userModelItem.rightBetValue * rightBetOdds)
        
        return 0

    def buildHistoryRecordList(self, activityGameId, activityId, userModel):
        ftlog.debug('Betguess.buildHistoryRecordList')
        clientconf = self._clientConf
        records = []
        
        # 从配置中获得所有已经过去的期号列表
        issueList = self.issueCalculator.getAlreadyPastIssueNumberList()
        for issueKey in issueList:
            recordItem = {}
            # 用户的历史押注记录(ActivityUserModel)
            userModelItem = userModel.findItemByIssueNumber(issueKey) or ActivityUserModel.ItemNull
            # 指定期号的活动数据记录(ActivityModel)
            activityModel = ActivityModel.loadModel(activityGameId, activityId, issueKey)
            
            # 本期的配置
            issueConf = self.issueCalculator.getCurrentIssueConf(issueKey)
            # 本期的抽水比例
            bankerPumping = issueConf.get('bankerPumping', 0)
            # 两边的名字
            leftSideName = issueConf['leftSide']['displayName']
            rightSideName = issueConf['rightSide']['displayName']

            # 奖励金额,发奖状态
            recordItem['prizeNumber'] = 0 
            recordItem['prizeStatus'] = Tool.dictGet(clientconf, 'config.server.recordCellWaitingResultTip', '未开奖')
            # 已经设置结果，并且已经发奖，才能显示结果值
            if activityModel.resultState != activityModel.RESULT_STATE_NONE: 
                recordItem['prizeNumber'] = self.getPrizeNumber(bankerPumping, activityModel, userModelItem)
                recordItem['prizeStatus'] = self.getPrizeStatus(activityModel, userModelItem)
                
            # 标题
            issueDatetime = datetime.strptime(issueKey, '%Y-%m-%d %H:%M:%S')
            titleFormat = Tool.dictGet(clientconf, 'config.server.recordCellIssueTitleFormat', '%m月%d日%H:%M \\${leftSideName}VS\\${rightSideName}')
            issueTitle = issueDatetime.strftime(titleFormat)
            recordItem['issueTitle'] = strutil.replaceParams(issueTitle, {'leftSideName':leftSideName, 'rightSideName':rightSideName})
            
            # 双方信息
            recordItem['itemtop'] = {
                'result': leftSideName, 
                'betValue': userModelItem.leftBetValue,
                'isWin': activityModel.resultState == activityModel.RESULT_STATE_LEFT
            }
            recordItem['itembot'] = {
                'result': rightSideName, 
                'betValue': userModelItem.rightBetValue,
                'isWin': activityModel.resultState == activityModel.RESULT_STATE_RIGHT
            }
            records.append(recordItem)
        return records
                        

    def handleRequest(self, msg):
        userId = msg.getParam('userId')
        gameId = msg.getParam('gameId')
        clientId = msg.getParam('clientId')
        activityId = msg.getParam('activityId')
        ftlog.debug('BetGuess.handleRequest:',
                    'userId=', userId, 
                    'gameId=', gameId,
                    'clientId=', clientId,
                    'activityId=', activityId,
                    'msg=', msg)

        action = msg.getParam('action')
        if action == 'ddz.act.betguess.betchip':
            betChip = msg.getParam('betChip', 0)
            isLeft = msg.getParam('isLeft')
            issueNumber = msg.getParam('issueNumber')
            return self.onActionBetChip(userId, betChip, isLeft, issueNumber)
        elif action == 'ddz.act.betguess.update':
            return self.buildActivityInfo(userId)
        else:
            ftlog.info('BetGuess.handleRequest:', 'userId=', userId, 'action not match')
            return {}

    def makeResponseMessage(self, userId, upconf):
        response = self.buildActivityInfo(userId)
        if upconf:
            response.update(upconf)
        return response

    def recommendProductIfNeed(self, gameId, userId, chip):
        # 当前金币足够则不用推荐商品
        curchip = userchip.getChip(userId)
        ftlog.debug('BetGuess.recommendProductIfNeed:',
                    'userId=', userId,
                    'curchip=', curchip,
                    'chip=', chip)
        if curchip >= chip:
            return False
        
        # 没有配置推荐商品，则不推荐
        payOrderMap = Tool.dictGet(self._clientConf, 'config.server.payOrderMap')
        if not payOrderMap:
            return False
        
        # 没有找到推荐商品配置，则不推荐
        payOrder = payOrderMap.get(str(int(chip)))
        ftlog.debug('BetGuess.recommendProductIfNeed:',
                    'userId=', userId,
                    'payOrder=', payOrder)
        if not payOrder:
            return False
        
        clientId = sessiondata.getClientId(userId)
        product, _ = hallstore.findProductByPayOrder(gameId, userId, clientId, payOrder)
        ftlog.debug('BetGuess.recommendProductIfNeed:',
                    'userId=', userId,
                    'product=', product)
        # 没有在货架中找到商品
        if not product:
            return False
        
        translateMap = {
            'product.displayName': product.displayName,
            'product.price': product.price,
            'betchip': chip,
        }
        desc = Tool.dictGet(self._clientConf, 'config.server.lessBuyChipDesc')
        note = Tool.dictGet(self._clientConf, 'config.server.lessBuyChipNote')
        desc = strutil.replaceParams(desc, translateMap)
        note = strutil.replaceParams(note, translateMap)
        todotask = TodoTaskLessBuyOrder(desc, None, note, product)
        TodoTaskHelper.sendTodoTask(gameId, userId, todotask)
        return True
    
    def userBetChip(self, userId, activityGameId, issueNumber, userModel, isLeft, betChip):
        # 加载用户活动数据
        ftlog.debug('BetGuess.userBetChip:',
                    'userId=', userId,
                    'activityGameId=', activityGameId,
                    'issueNumber=', issueNumber,
                    'isLeft=', isLeft,
                    'betChip=', betChip)

        # 先查看玩家投注是否超额
        issueConf = self.issueCalculator.getCurrentIssueConf(issueNumber)
        userMaxBetChip = issueConf.get('userMaxBetChip', -1)
        item = userModel.findOrCreateItemByIssueNumber(issueNumber)
        if userMaxBetChip and userMaxBetChip > 0 and \
            (item.leftBetValue + item.rightBetValue + betChip) > userMaxBetChip:
            return Tool.dictGet(self._clientConf, 'config.server.betChipOverflow')

        # 消耗玩家金币
        clientId = sessiondata.getClientId(userId)
        trueDelta, _ = userchip.incrChip(userId, activityGameId, -betChip, 
                                         daoconst.CHIP_NOT_ENOUGH_OP_MODE_NONE, 'ACT_BETGUESS_CHIP', 0, clientId)
        datachangenotify.sendDataChangeNotify(activityGameId, userId, 'chip')
        ftlog.debug('BetGuess.userBetChip:', 'userId=', userId, 'trueDelta=', trueDelta)
        if trueDelta != -betChip:
            ftlog.debug('BetGuess.userBetChip:chipNotEnough')
            return Tool.dictGet(self._clientConf, 'config.server.chipNotEnough')

        # 玩家记录数据
        userModel.incrChip(issueNumber, isLeft, betChip)
        userModel.save()
        
        # 日志记录每个UID每场的下注额及下注项
        packageGameId = strutil.getGameIdFromHallClientId(sessiondata.getClientId(userId))
        ftlog.info('BetGuess.userBetChip',
                   'userId', userId, 
                   'packageGameId', packageGameId,
                   'activityGameId', activityGameId,
                   'activityId', self.getid(),
                   'issueNumber', issueNumber,
                   'isLeft', isLeft, 
                   'betChip', betChip)
        return None
    
    def buildActivityInfo(self, userId, activityModel=None, userModel=None):
        clientconf = copy.deepcopy(self._clientConf)
        serverconf = self._serverConf
        ftlog.debug('BetGuess.buildActivityInfo:',
                    'userId=', userId, 
                    'serverconf=', serverconf, 
                    'clientconf=', clientconf)
        
        activityGameId = clientconf.get('activityGameId')
        activityId = self.getid()

        # 计算当前最新的期号(当前要执行的期)
        issueNumber = self.issueCalculator.getCurrentIssueNumber() or self.issueCalculator.getLastIssueNumber()
        ftlog.debug('BetGuess.buildActivityInfo:issueNumber=', issueNumber)
        
        # 加载活动数据
        activityModel = activityModel or ActivityModel.loadModel(activityGameId, activityId, issueNumber)
        userModel = userModel or ActivityUserModel.loadModel(userId, activityGameId, activityId)
        userModelItem = userModel.findOrCreateItemByIssueNumber(issueNumber)
        
        ftlog.debug('BetGuess.buildActivityInfo:activityModel=', activityModel.__dict__)
        ftlog.debug('BetGuess.buildActivityInfo:userModel=', userModel.__dict__)
        
        # 单期的配置
        issueConf = copy.deepcopy(self.issueCalculator.getCurrentIssueConf(issueNumber))
        ftlog.debug('BetGuess.buildActivityInfo:issueConf=', issueConf)
        
        # 抽水比例
        bankerPumping = issueConf.get('bankerPumping', 0)
        issueConf.pop('bankerPumping')
        # 奖池金额
        betPoolChip = int((activityModel.countChipLeft+activityModel.countChipRight)*(1-bankerPumping))
        # 左赔率
        leftBetOdds = betPoolChip/activityModel.countChipLeft if activityModel.countChipLeft>0 else 0
        # 右赔率
        rightBetOdds = betPoolChip/activityModel.countChipRight if activityModel.countChipRight>0 else 0
        
        activityClient = {}
        activityClient.update(issueConf)
        
        activityClient['leftSide']['betChip'] = userModelItem.leftBetValue
        activityClient['leftSide']['betOdds'] = leftBetOdds
        
        activityClient['rightSide']['betChip'] = userModelItem.rightBetValue
        activityClient['rightSide']['betOdds'] = rightBetOdds
        
        activityClient['userChip'] = userchip.getChip(userId)
        activityClient['betPoolChip'] = betPoolChip
        activityClient['currentIssueNumber'] = issueNumber

        issueDateFormat = Tool.dictGet(clientconf, 'config.server.issueDateFormat', '%m月%d日%H:%M')
        issueDatetime = Tool.datetimeFromString(issueNumber)
        activityClient['issueDate'] = issueDatetime.strftime(issueDateFormat)
        activityClient['betRecords'] = self.buildHistoryRecordList(activityGameId, activityId, userModel)
        
        ftlog.debug('BetGuess.buildActivityInfo:activityClient=', activityClient)
        
        clientconf['config']['client'].update(activityClient)
        return clientconf 
    
    def onActionBetChip(self, userId, betChip, isLeft, issueNumber):
        ftlog.debug('BetGuess.onActionBetChip:', 
                    'userId=', userId, 
                    'betChip=', betChip, 
                    'isLeft=', isLeft, 
                    'issueNumber=', issueNumber)
        clientconf = self._clientConf
        activityGameId = clientconf.get('activityGameId')        
        issueNumberNow = self.issueCalculator.getCurrentIssueNumber()
        ftlog.debug('BetGuess.onActionBetChip:',
                    'userId=', userId,
                    'issueNumberNow=', issueNumberNow,
                    'issueNumber=', issueNumber)

        # 参数合理性判断，不合理直接忽略
        if betChip <= 0 or isLeft == None:
            return self.buildActivityInfo(userId)
        # 没有当前一期的竞猜
        if not issueNumberNow:
            return self.makeResponseMessage(userId, {'message': Tool.dictGet(clientconf, 'config.server.allIssueOutdate')})
        # 客户端展示的期号与当前不一致，强制刷新
        if issueNumber != issueNumberNow:
            return self.makeResponseMessage(userId, {'message': Tool.dictGet(clientconf, 'config.server.issueOutdate')})        
        
        # 若推荐商品，则代表金币不足，直接返回
        if self.recommendProductIfNeed(activityGameId, userId, betChip):
            return self.buildActivityInfo(userId)
        
        # 消耗用户金币，增加用户存储的活动数据金币
        userModel = ActivityUserModel.loadModel(userId, activityGameId, self.getid())
        err = self.userBetChip(userId, activityGameId, issueNumber, userModel, isLeft, betChip)
        if err:
            return self.makeResponseMessage(userId, {'message': err})  
        
        # 记录玩家
        UserRecorder.addUser(userId, activityGameId, self.getid(), issueNumber)
        
        # 增加活动奖池记录数据
        activityModel = ActivityModel.loadModel(activityGameId, self.getid(), issueNumber)
        activityModel.incrChip(isLeft, betChip)
        ftlog.info('BetGuess.onActionBetChip', 
                   'userId=', userId,
                   'activityGameId=', activityGameId,
                   'activityId=', self.getid(),
                   'issueNumber=', issueNumber,
                   'activityModel.resultState=', activityModel.resultState,
                   'activityModel.countChipLeft=', activityModel.countChipLeft,
                   'activityModel.countChipRight=', activityModel.countChipRight)
        
        return self.buildActivityInfo(userId, activityModel, userModel)
    
    def sendRewardToUser(self, userId, countChipLeft, countChipRight, resultState, activityGameId, activityId, issueNumber):
        ftlog.debug('BetGuess.sendRewardToUser', 
                    'userId=', userId)
        
        userModel = ActivityUserModel.loadModel(userId, activityGameId, activityId)
        userModelItem = userModel.findItemByIssueNumber(issueNumber)
        
        # 若玩家没有下注的记录，但是有记录的userid，此处可能存在问题
        if not userModelItem:
            ftlog.warn('BetGuess.sendRewardToUser: userModel issueNumber not found', 
                       'userId=', userId,
                       'activityGameId', activityGameId,
                       'activityId', activityId,
                       'issueNumber', issueNumber)
            return 0
                
        # 已经发送过了
        if userModelItem.isPrizeSent:
            ftlog.warn('BetGuess.sendRewardToUser: user issueNumber has sent',
                       'userId=', userId,
                       'activityGameId', activityGameId,
                       'activityId', activityId,
                       'issueNumber', issueNumber)
            return 0
        
        # 若未发奖，则返回0
        if resultState == ActivityModel.RESULT_STATE_NONE:
            return 0
        
        # 单期的配置
        issueConf = copy.deepcopy(self.issueCalculator.getCurrentIssueConf(issueNumber))
        ftlog.debug('BetGuess.sendRewardToUser:issueConf=', issueConf)
        if not issueConf:
            return 0
        
        # 抽水比例
        bankerPumping = issueConf.get('bankerPumping', 0)
        # 奖池金额
        betPoolChip = int((countChipLeft+countChipRight)*(1-bankerPumping))
        # 左赔率
        leftBetOdds = betPoolChip/countChipLeft if countChipLeft>0 else 0
        # 右赔率
        rightBetOdds = betPoolChip/countChipRight if countChipRight>0 else 0

        prizeNumber = 0 # 本期活动，赢取金额
        issueWinSideName = None # 本期活动，胜利一侧名称
        issueFinalOdds = 0  # 本期活动，胜利一侧最终赔率
        issueWinBetNumber = 0 # 本期活动，胜利一侧下注额
        if resultState == ActivityModel.RESULT_STATE_LEFT:
            prizeNumber = int(userModelItem.leftBetValue * leftBetOdds)
            issueWinSideName = issueConf['leftSide']['displayName']
            issueFinalOdds = leftBetOdds
            issueWinBetNumber = userModelItem.leftBetValue
        elif resultState == ActivityModel.RESULT_STATE_RIGHT:
            prizeNumber = int(userModelItem.rightBetValue * rightBetOdds)
            issueWinSideName = issueConf['rightSide']['displayName']
            issueFinalOdds = rightBetOdds
            issueWinBetNumber = userModelItem.rightBetValue
        
        # 发放金币奖励
        if prizeNumber <= 0:
            # 记录是否发奖
            userModelItem.isPrizeSent = True
            userModel.save()
            return prizeNumber
        
        clientId = sessiondata.getClientId(userId)
        trueDelta, _ = userchip.incrChip(userId, activityGameId, prizeNumber, 
                                         daoconst.CHIP_NOT_ENOUGH_OP_MODE_NONE, 'ACT_BETGUESS_CHIP', 0, clientId)
        datachangenotify.sendDataChangeNotify(activityGameId, userId, 'chip')
        ftlog.debug('BetGuess.sendRewardToUser:', 'userId=', userId, 'trueDelta=', trueDelta)
        if trueDelta != prizeNumber:
            return 0
         
        # 发送玩家系统邮件
        mail = Tool.dictGet(self._clientConf, 'config.server.mail')
        if mail:
            issueDatetime = Tool.datetimeFromString(issueNumber)
            mailMessage = strutil.replaceParams(mail, {
                'issueMonth': issueDatetime.month,
                'issueDay': issueDatetime.day,
                'issueLeftSideName': issueConf['leftSide']['displayName'],
                'issueRightSideName': issueConf['rightSide']['displayName'],
                'issueWinBetNumber': issueWinBetNumber,
                'issueWinSideName': issueWinSideName,
                'issueFinalOdds': float(issueFinalOdds*100)/100,
                'issuePrizeChipNumber': prizeNumber
            })
            pkmessage.sendPrivate(9999, userId, 0, mailMessage)
        
        # 记录是否发奖
        userModelItem.isPrizeSent = True
        userModel.save()
        
        ftlog.info('BetGuess.sendRewardToUser:', 
                   'userId=', userId, 
                   'activityGameId=', activityGameId,
                   'activityId=', activityId,
                   'issueNumber=', issueNumber,
                   'prizeNumber=', prizeNumber,
                   'resultState=', resultState)
        
        return prizeNumber


def initialize():
    ftlog.info('betguess.initialize')
    pass
