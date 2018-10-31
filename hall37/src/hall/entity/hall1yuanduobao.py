# -*- coding=utf-8 -*-
# Author:        luojihui@163.com
# Created:       17/12/5 下午5:31

from freetime.core import timer
import json
from poker.entity.biz import bireport
from poker.entity.biz import exceptions
from poker.entity.biz.item import item
from poker.entity.configure import configure, gdata
from poker.entity.dao import daobase, userdata, sessiondata
from poker.entity.events import tyevent
from poker.util import strutil, timestamp as pktimestamp
import random

import freetime.util.log as ftlog
from hall.entity import datachangenotify, hallitem, hallnewnotify, \
                hall_duobao_control_users_manager, hall_jiguang_jpush, \
                hall_robot_user, hallconf, hallusercond
import poker.entity.events.tyeventbus as pkeventbus


# 进程启动标志位
_inited = False
_luckyCodeMap = {}
_duobaoMap = {}

# 一期个人最大下注上线
DUOBAO_PLAYER_BET_NUM_MAX = 100
# 单次最大下注数上限
DUOBAO_PLAYER_ONCE_BET_NUM_MAX = 20
# 夺宝过期时间清理
DUOBAO_EXPIRE_TIME = 15 * 24 * 3600

# 夺宝类型 时间到
DUOBAO_TYPE_TIME = 1
# 夺宝类型 次数到
DUOBAO_TYPE_COUNT = 2
# 夺宝类型列表
DUOBAO_TYPE_LIST = [DUOBAO_TYPE_TIME, DUOBAO_TYPE_COUNT]

# 夺宝状态 下注
STATE_DUOBAO_BET = 1
# 夺宝状态 开奖
STATE_DUOBAO_OPEN = 2
# 夺宝状态 关闭
STATE_DUOBAO_CLOSE = 3

# 客户端夺宝记录 标签
# 需要领取
DUOBAO_RECORD_TAG_WIN = 1
# 未开奖
DUOBAO_RECORD_TAG_NOOPEN = 2
# 已领奖
DUOBAO_RECORD_TAG_FINISH = 3
# 未中奖
DUOBAO_RECORD_TAG_NOWIN = 4

# 正常结算
DUOBAO_SETTLEMENT_NORMAL = 1
# 流局结算
DUOBAO_SETTLEMENT_FLOW = 2

_REDIS_LUA_BETLIST_NAME = 'hall.duobao.type.count'
_REDIS_LUA_BETLIST_SCRIPT = '''
               local userId = tonumber(KEYS[1])
               local num = tonumber(KEYS[2])
               local moreBetCount = tonumber(KEYS[3])
               local betuserkey = tostring(KEYS[4]) 
               local betcountkey = tostring(KEYS[5]) 
               
               local length = tonumber(redis.call('llen', betuserkey))
               if length >= moreBetCount then
                   return {-1, length, moreBetCount}
               end

               if length + num > moreBetCount then
                   return {-2, length + num,moreBetCount-length}
               end
               
               local totalBetCount = 0
               for k = 1, num do
                   totalBetCount = redis.call('rpush', betuserkey, userId) 
               end
               
               local myBetCount = redis.call('hincrby', betcountkey, userId, num)

               return {1, totalBetCount, myBetCount}
               '''


def getConf():
    '''夺宝配置'''
    return configure.getGameJson(hallconf.HALL_GAMEID, 'duobao', {}).get('duobaos')


def isNumByExcept(num):
    try:
        int(num)
        return True
    except ValueError:
        ftlog.warn('isNumByExcept num:%s' % num)
        return False


def _checkConf(duobaoList):
    '''检查配置'''
    for duobaoConf in duobaoList:
        if not isinstance(duobaoConf, dict):
            ftlog.warn('hall1yuanduobao._reloadConf duobaoConf not dict')
            return False
        if not duobaoConf.has_key('duobaoId'):
            ftlog.warn('hall1yuanduobao._reloadConf havenot duobaoId', duobaoConf)
            return False

        if not isinstance(duobaoConf.get('duobaoId'), basestring):
            ftlog.warn('hall1yuanduobao._reloadConf duobaoId not basestring', duobaoConf)
            return False

        if not isNumByExcept(duobaoConf.get('duobaoId')):
            ftlog.warn('hall1yuanduobao._reloadConf duobaoId not num', duobaoConf)
            return False

        if not duobaoConf.has_key('typeId'):
            ftlog.warn('hall1yuanduobao._reloadConf havenot typeId', duobaoConf)
            return False

        if duobaoConf.get('typeId') not in DUOBAO_TYPE_LIST:
            ftlog.warn('hall1yuanduobao._reloadConf error typeId', duobaoConf)
            return False

    return True

class Duobao(object):
    '''夺宝基类'''

    def __init__(self):
        # 期号 自然数累加
        self.issue = None
        # 是否开过奖
        self.isOpen = False
        # 夺宝id
        self.duobaoId = None
        # 类型
        self.typeId = None
        # 总局数
        self.totalIssueNum = None
        # 开始时间戳
        self.startTimestamp = None
        # 下注时长,单位:分
        self.betTime = None
        # 开奖时长,单位:分
        self.openTime = None
        # 限时开奖,需要的投注次数
        self.lessBetCount = None
        # 人满开奖,需要的投注次数
        self.moreBetCount = None
        # 显示名称
        self.displayName = None
        # 商品描述
        self.desc = None
        # 商品图片
        self.pic = None
        # 标签:秒杀、限时等
        self.tagMark = None
        # 花费:奖券等 "user:coupon"
        self.cost = None
        # 夺宝成功后给用户发的消息
        self.mail = None
        # 状态
        self.state = None
        # Timer
        self._timer = None
        #机器人定时参加夺宝
        self._timerRobot = None
        #机器人id
        self.robotId = 0
        # 有效期数
        self.validIssueNum = None
        # 奖励
        self.reward = None
        # 位置
        self.position = None
        #抑制列表最长 100行
        self.maxControllUserCount = 100
        #抑制ip段
        self.maxControllIpCount = 100
        #抑制最多随机几次
        self.maxRandomCount = 3
        #是否发送通知
        self.sendNotice = 0
        #中奖消息
        self.noticeContent = '恭喜夺宝中奖!'
        #消息推送 是否隐藏图标，按钮类型，提示时长
        self.sendNoticeCfg = None
        #显示时间段
        self.showCondition = []
        #总权重显示条件
        self.showWeight = 0
        #权重计算列表
        self.showWeightCalc = None
        #机器人 第S秒 小于N人 加M个 概率百分比参加
        self.rbSNM = []
        self.rbChance = 0
        
    @classmethod
    def create(cls, typeId):
        if typeId == DUOBAO_TYPE_TIME:
            return DuobaoLimitedTime()
        elif typeId == DUOBAO_TYPE_COUNT:
            return DuobaoMeetTimes()
        assert 0

    def __str__(self):
        return '%s:%s' % (self.duobaoId, self.issue)

    def __repr__(self):
        return self.__str__()

    def toDict(self):
        return {'issue': self.issue,
                'isOpen': self.isOpen,
                'duobaoId': self.duobaoId,
                'typeId': self.typeId,
                'totalIssueNum': self.totalIssueNum,
                'startTimestamp': self.startTimestamp,
                'betTime': self.betTime,
                'openTime': self.openTime,
                'lessBetCount': self.lessBetCount,
                'moreBetCount': self.moreBetCount,
                'displayName': self.displayName,
                'desc': self.desc,
                'pic': self.pic,
                'tagMark': self.tagMark,
                'cost': self.cost,
                'mail': self.mail,
                'state': self.state,
                'validIssueNum': self.validIssueNum,
                'reward': self.reward,
                'position': self.position,
                'maxControllUserCount': self.maxControllUserCount,
                'maxControllIpCount': self.maxControllIpCount,
                'maxRandomCount': self.maxRandomCount,
                'sendNotice': self.sendNotice,
                'noticeContent': self.noticeContent,
                'sendNoticeCfg': self.sendNoticeCfg,
                'showCondition': self.showCondition,
                'showWeight': self.showWeight,
                'showWeightCalc': self.showWeightCalc,
                'rbSNM': self.rbSNM,
                'rbChance': self.rbChance
                }

    def fromDict(self, d):
        # 是否开过奖
        self.isOpen = d.get('isOpen', False)
        # 夺宝标识
        self.duobaoId = d.get('duobaoId')
        # 总局数
        self.totalIssueNum = d.get('totalIssueNum')
        # 开始时间
        self.startTimestamp = d.get('startTimestamp')
        # 下注时长
        self.betTime = d.get('betTime')
        # 开奖时长
        self.openTime = d.get('openTime')
        # 限时开奖,需要的投注次数
        self.lessBetCount = d.get('lessBetCount')
        # 人满开奖,需要的投注次数
        self.moreBetCount = d.get('moreBetCount')
        # 显示名称
        self.displayName = d.get('displayName')
        # 商品描述
        self.desc = d.get('desc')
        # 商品图片
        self.pic = d.get('pic')
        # 标签:秒杀、限时等
        self.tagMark = d.get('tagMark')
        # 花费:红包券等 "user:coupon"
        self.cost = d.get('cost', {
            'count': 2,
            'name': '红包券',
            'itemId': 'user:coupon',
            'pic': '${http_download}/hall/pdt/imgs/goods_t300k_2.png'}
                          )
        # 夺宝成功后给用户发的消息
        self.mail = d.get('mail')
        # 奖励
        self.reward = d.get('reward')
        # 位置
        self.position = d.get('position')        
        #抑制列表最长 100行
        self.maxControllUserCount = d.get('maxControllUserCount', 100)        
        #抑制ip段
        self.maxControllIpCount = d.get('maxControllIpCount', 100)        
        #次数
        self.maxControllIpCount = d.get('maxRandomCount', 3)        
        #中奖消息
        self.noticeContent = d.get('noticeContent', '恭喜夺宝中奖')
        #是否发送中奖消息
        self.sendNotice = d.get('sendNotice', 0)    
        #消息推送 是否隐藏图标，按钮类型，提示时长
        self.sendNoticeCfg = d.get('sendNoticeCfg', {
                'hideIcon': 0,
                'buttonType': 2,
                'closeTime': 3
                })    
        #显示时间段
        self.showCondition = d.get('showCondition', [])
        #权重
        self.showWeight = d.get('showWeight', 0)
        #权重计算列表
        self.showWeightCalc = d.get('showWeightCalc')
        #机器人 第S秒 小于N人 加M个
        self.rbSNM = d.get('rbSNM', [])
        self.rbChance = d.get('rbChance', 0)
        #机器人id 确保每期只有一个机器人夺宝
        self.robotId = 0
        
        if self.showCondition:
            hallusercond.UserConditionRegister.decodeFromDict(self.showCondition)
        
        if self.showWeightCalc:
            ShowWeightCalc().decodeFromDict(self.showWeightCalc)
        
        return self

    def startNextRound(self):
        '''开启下一局'''
        raise NotImplementedError

    def fromRedis(self):
        '''从redis创建'''
        raise NotImplementedError

    def _checkConf(self, conf):
        '''检测配置'''
        raise NotImplementedError

    def _loadConf(self):
        '''加载配置'''
        conf = None
        for confDict in getConf():
            if confDict.get('duobaoId') == self.duobaoId:
                conf = confDict
                break

        if not conf or not self._checkConf(conf):
            ftlog.info('Duobao.startNextRound conf error',
                       'state', self.state,
                       'typeId=', self.typeId,
                       'self=', self)
            return None

        if self.issue > conf.get('totalIssueNum'):
            ftlog.info('Duobao.startNextRound issue equal conf.totalIssueNum',
                       'state', self.state,
                       'typeId=', self.typeId,
                       'self=', self)
            return None

        return conf

    def update(self):
        # save redis
        saveDuobaoObj(self)

    def _destruct(self):
        self.stopTimerCheckRobot()
        destructRobot('%s:%s' % (self.duobaoId, self.issue))

    def _checkExpire(self):
        if self.issue >= self.totalIssueNum:
            # 更新
            if pktimestamp.getCurrentTimestamp() - self.startTimestamp > DUOBAO_EXPIRE_TIME:
                daobase.executeMixCmd('del', 'hall.duobao.record:%s' % self.duobaoId)
                # 过期的夺宝入库
                daobase.executeMixCmd('sadd', 'hall.duobao.expire', self.duobaoId)

    def fromConf(self):
        '''从conf创建'''
        # 新商品初始化期号
        self.issue = 0
        self.validIssueNum = 0
        self.startNextRound()

    def getRobotBetLength(self):
        lengthRobot = daobase.executeMixCmd('llen', 'hall.duobao.betrobotuser:%s:%s' % (self.duobaoId, self.issue))
        if lengthRobot:
            return lengthRobot
        return 0

    def updateControllUserId(self, userIds, ips, userId, ip):
        #删除一个
        if len(userIds) >= self.maxControllUserCount:
            minKey = 0
            minValue = min(userIds.values())
            for k,v in userIds.items():
                if v == minValue:
                    minKey = k
            userIds.pop(minKey)
        if len(ips) >= self.maxControllIpCount:
            minKey = 0
            minValue = min(ips.values())
            for k,v in ips.items():
                if v == minValue:
                    minKey = k
            ips.pop(minKey)
            
        if self.maxControllUserCount > 0:
            userIds[userId] = pktimestamp.getCurrentTimestamp()
        if self.maxControllIpCount > 0:
            ips[ip] = pktimestamp.getCurrentTimestamp()

    def sendBiReport(self, bIsRobot):
        #如果有机器人 发送fbi
        robotUserId = 0
        lengthRobot = daobase.executeMixCmd('llen', 'hall.duobao.betrobotuser:%s:%s' % (self.duobaoId, self.issue))
        if lengthRobot > 0:
            robotUserId = daobase.executeMixCmd('lindex', 'hall.duobao.betrobotuser:%s:%s' % (self.duobaoId, self.issue), 0)
        if robotUserId:
            listRes = []
            result = 1 if bIsRobot else 0
            listRes.append(result)
            listRes.append(int(self.duobaoId))
            listRes.append(int(self.issue))
            bireport.reportGameEvent('DUOBAO_ROBOT_RESULT', robotUserId, hallconf.HALL_GAMEID, 
                                     0, 0, 0, 0, 0, 0, listRes, 'robot_3.7_-hall6-robot', 0, 0, 0, 0, 0)
            if ftlog.is_debug():
                ftlog.debug('hall1yuanduobao.sendBiReport:'
                            'robotUserId=', robotUserId,
                            'listRes=', listRes)
        
    def getRandomUserId(self, length):        
        #决定取那个表 机器人还是 用户的
        bIsRobot = False
        lengthRobot = self.getRobotBetLength()
        lengthUser = length - lengthRobot
        lengthReal = length
        redisKey = 'hall.duobao.betuser:%s:%s' % (self.duobaoId, self.issue)
        if lengthUser < self.lessBetCount:
            redisKey = 'hall.duobao.betrobotuser:%s:%s' % (self.duobaoId, self.issue)
            bIsRobot = True
            lengthReal = lengthRobot
        

        userIds, ips = hall_duobao_control_users_manager.getUserIdsIpsByDuoBaoId(self.duobaoId)
        
        userId = 0
        ip = ''
        count = 0
        while True:
            index = random.randint(0, lengthReal - 1)
            # 中奖的玩家
            userId = daobase.executeMixCmd('lindex', redisKey, index)
            ip = sessiondata.getClientIp(userId)
            
            if not userIds.has_key(userId) and not ips.has_key(ip):
                break
            else:
                count += 1
                if count >= self.maxRandomCount:
                    break
           
        if userId <= hall_robot_user.MAX_ROBOT_USERID:
            bIsRobot = True
                 
        if not bIsRobot:
            self.updateControllUserId(userIds, ips, userId, ip)
        
        if ftlog.is_debug():
            ftlog.debug('hall1yuanduobao.getRandomUserId=', userIds,
                'duobaoControllIps=', ips,
                'IsRobot=', bIsRobot,
                'duobaoid=', self.duobaoId, 
                'issu=', self.issue,
                'lenRobot=', lengthRobot,
                'lenUser=', lengthUser,
                'length=', length,
                'count=', count,
                'winId=', userId)
        
        return userId, bIsRobot
    
    def sendNotifys(self, userIds, content, todo):        
        typeId = hallnewnotify.NOTIFY_TYPEID_MESSAGE
        ntimeId = hallnewnotify.NOTIFY_TIME_ATONCE_ID
        ntime = '0'
        iconAddr = ''
        context = content
        platform = '3'
        passthrough = json.dumps(todo)
        buttonType = str(self.sendNoticeCfg.get('buttonType', 0))# '2' #配置
        gameId = str(hallconf.HALL_GAMEID)
        package = ''
        timelimit = str(self.sendNoticeCfg.get('closeTime', 3))#'3' #配置文件
        dictother = {'hideIcon': str(self.sendNoticeCfg.get('hideIcon', 0))}
        for userId in userIds:
            if userId > hall_robot_user.MAX_ROBOT_USERID:
                clientId = sessiondata.getClientId(userId)
                hallGameId = strutil.getGameIdFromHallClientId(clientId)
                hall = 'hall%s' % (hallGameId) if hallGameId else 'hall6'
                hallnewnotify.addNotifyInfo(typeId, ntimeId, ntime, iconAddr, 
                                            context, passthrough, platform, buttonType,
                                            hall, gameId, package, str(userId), timelimit, dictother)

    #成功开奖后立即推送消息
    def sendResult(self, winId, name):
        if self.sendNotice != 1:
            return
        
        userIds = daobase.executeMixCmd('lrange', 'hall.duobao.betuser:%s:%s' % (self.duobaoId, self.issue), 0, -1)
        if not userIds:
            return  
        
        userIds = list(set(userIds))
        content = self.noticeContent.replace('${userName}',name).replace('${duobaoName}', self.displayName)
        
        hall_jiguang_jpush.JiGuangPush.sendMessage(winId, 1, self.mail, self.mail)
        
        if userIds:
            todo = self.sendNoticeCfg.get('todo', {})
            self.sendNotifys(userIds, content, todo)

        if ftlog.is_debug():
            ftlog.debug('hall1yuanduobao.sendResult',
                        'userIds=', userIds,
                        'winId=', winId,
                        'msgWin=', self.mail,
                        'msgOther=', content,
                        'userIds=', userIds)                           
                
    def _settlement(self):
        '''结算'''
        length = daobase.executeMixCmd('llen', 'hall.duobao.betuser:%s:%s' % (self.duobaoId, self.issue))
        if length and length > 0 and length >= self.conditionBetCount:
            
            userId, bIsRobot = self.getRandomUserId(length)
            if userId <= 0:
                userId = 1
                bIsRobot = True
            
            name, purl = '','' #获取获奖者id 头像
            if bIsRobot:
                name, purl = hall_robot_user.getRandomName(), hall_robot_user.getRandomImageUrl()
            else:
                name, purl = userdata.getAttrs(userId, ['name', 'purl'])
            
            betCount = daobase.executeMixCmd('hget', 'hall.duobao.betcount:%s:%s' % (self.duobaoId, self.issue), userId)

            luckyCodeSet = daobase.executeMixCmd('smembers',
                                                 'hall.duobao.luckycode:%s:%s:%s' % (self.duobaoId, self.issue, userId))
            if luckyCodeSet and len(luckyCodeSet) > 0:
                luckyCode = random.choice(luckyCodeSet)
            else:
                luckyCode = '1001100000'
                luckyCodeSet = ['1001100000']
                ftlog.warn('DuobaoLimitedTime._settlement luckyCode error',
                           'duobao=', self,
                           'userId=', userId)

            # 有效期数
            self.validIssueNum += 1

            # 中奖的玩家-往期得主-这期账单 purl 和 name 是得主  pic商品 displayName 商品名
            duobaoRecordDict = {'duobaoId': self.duobaoId, 'issue': self.issue, 'purl': purl, 'name': name,
                                'betCount': betCount, 'luckyCode': luckyCode,
                                'luckyCodeSet': luckyCodeSet, 'endTime': pktimestamp.getCurrentTimestamp(),
                                'pic': self.pic, 'displayName': self.displayName,
                                'settlementStatus': DUOBAO_SETTLEMENT_NORMAL, 'validIssueNum': self.validIssueNum}
            daobase.executeMixCmd('hset', 'hall.duobao.record:%s' % self.duobaoId, self.issue,
                                  strutil.dumps(duobaoRecordDict))

            # 移除 玩家未开奖列表-临时表需要清除 显示用
            daobase.executeUserCmd(userId, 'zrem', 'hall.duobao.record.noopen.zset:%s' % userId,
                                   '%s:%s' % (self.duobaoId, self.issue))

            # 添加 需要领取 客户端显示用
            datas = {'duobaoId': self.duobaoId, 'pic': self.pic, 'displayName': self.displayName, 'issue': self.issue,
                     'endTime': pktimestamp.getCurrentTimestamp(),
                     'betCount': betCount, 'luckyCodeSet': luckyCodeSet, 'winPurl': purl, 'winName': name,
                     'luckyCode': luckyCode, 'reward': self.reward,
                     'settlementStatus': DUOBAO_SETTLEMENT_NORMAL, 'validIssueNum': self.validIssueNum}
            daobase.executeUserCmd(userId, 'hset', 'hall.duobao.record.win:%s' % userId,
                                   '%s:%s' % (self.duobaoId, self.issue),
                                   strutil.dumps(datas))

            # 客户端显示用, 有时间戳排序
            daobase.executeUserCmd(userId, 'zadd', 'hall.duobao.record.win.zset:%s' % userId,
                                   pktimestamp.getCurrentTimestamp(), '%s:%s' % (self.duobaoId, self.issue))
            
            # 客户端显示用 最新获奖者
            daobase.executeMixCmd('hset', 'hall.duobao.lateset.win',self.duobaoId, name)
            
            #发送推送
            self.sendResult(userId, name)
            if ftlog.is_debug():
                ftlog.debug('hall1yuanduobao.sendResult',
                           'userId=', userId,
                           'name=', name,
                           'url=', purl)
            #发送统计
            self.sendBiReport(bIsRobot)
        else:
            # 流局
            duobaoRecordDict = {'duobaoId': self.duobaoId, 'issue': self.issue,
                                'endTime': pktimestamp.getCurrentTimestamp(), 'cost': self.cost,
                                'pic': self.pic, 'displayName': self.displayName,
                                'settlementStatus': DUOBAO_SETTLEMENT_FLOW}

            daobase.executeMixCmd('hset', 'hall.duobao.record:%s' % self.duobaoId, self.issue,
                                  strutil.dumps(duobaoRecordDict))
            ftlog.info('DuobaoLimitedTime flow',
                       'duobao=', self)

    #开始的时候创建一个定时器
    def startTimerCheckRobot(self):
        self.stopTimerCheckRobot()
        
        interval = self.startTimestamp + self.betTime * 60 - pktimestamp.getCurrentTimestamp()
        self._timerRobot = timer.FTLoopTimer(1, int(interval)-1, self.onTimerCheckRobot)
        self._timerRobot.start()
    #关闭机器人定时器
    def stopTimerCheckRobot(self):
        if self._timerRobot:
            self._timerRobot.cancel()
            self._timerRobot = None
    
    def onTimerCheckRobot(self):
        #每秒检查一次
        if not self.rbSNM or len(self.rbSNM) <= 0:
            return 
        
        #计算概率百分率
        if not (self.rbChance > 0 and self.rbChance <= 100 and random.randint(0,100) <= self.rbChance):
            return
        
        secondOrder = int(pktimestamp.getCurrentTimestamp() - self.startTimestamp)
        for rbSNM in self.rbSNM:
            if len(rbSNM) == 3 and rbSNM[0] == secondOrder and rbSNM[1] >= 0 and rbSNM[2] > 0:
                self.robotBet(rbSNM[1], rbSNM[2])
        
    def robotBet(self, rbN, rbM):
        totalBetCount = daobase.executeMixCmd('llen', 'hall.duobao.betuser:%s:%s' % (self.duobaoId, self.issue))
        if totalBetCount == None or totalBetCount >= rbN:
            return
        
        #每隔机器人夺宝一次
        if self.robotId <= 0:
            self.robotId = hall_robot_user.getRandomRobotId()
        try:
            luckyCodeList, myBetCount, totalBetCount, coupon = duobaoBet(self.robotId, self.duobaoId, self.issue, rbM, True)
            if ftlog.is_debug():
                ftlog.debug('hall1yuanduobao.robotBet',
                            'robotuserid=', self.robotId,
                            'lukycodelist=', luckyCodeList,
                            'betcount=', myBetCount,
                            'totalbetCount=', totalBetCount,
                            'coupon=', coupon)
        except:
            ftlog.error('hall1yuanduobao.robotBet Error=')
            return
            
class DuobaoLimitedTime(Duobao):
    '''限时开奖 时间到'''

    def __init__(self):
        super(DuobaoLimitedTime, self).__init__()
        # 下注时长
        self.betTime = None
        # 需要的投注次数
        self.lessBetCount = None

        self.typeId = DUOBAO_TYPE_TIME

    @property
    def conditionBetCount(self):
        return self.lessBetCount

    def _checkConf(self, conf):
        '''检测配置'''
        if conf.get('typeId') != self.typeId:
            ftlog.info('DuobaoLimitedTime _checkConf typeId error',
                       'conf.typeId=', conf.get('typeId'),
                       'typeId=', self.typeId,
                       'self=', self)
            return False
        betTime = conf.get('betTime')
        if not isinstance(betTime, int) or betTime < 0:
            ftlog.info('DuobaoLimitedTime _checkConf betTime error',
                       'conf.betTime=', betTime,
                       'typeId=', self.typeId,
                       'self=', self)
            return False
        openTime = conf.get('openTime')
        if not isinstance(openTime, int) or openTime < 0:
            ftlog.info('DuobaoLimitedTime _checkConf openTime error',
                       'conf.openTime=', openTime,
                       'typeId=', self.typeId,
                       'self=', self)
            return False
        lessBetCount = conf.get('lessBetCount')
        if not isinstance(lessBetCount, int) or lessBetCount <= 0:
            ftlog.info('DuobaoLimitedTime _checkConf lessBetCount error',
                       'conf.lessBetCount=', lessBetCount,
                       'typeId=', self.typeId,
                       'self=', self)
            return False
        totalIssueNum = conf.get('totalIssueNum')
        if not isinstance(totalIssueNum, int) or totalIssueNum <= 0:
            ftlog.info('DuobaoLimitedTime _checkConf totalIssueNum error',
                       'conf.totalIssueNum=', totalIssueNum,
                       'typeId=', self.typeId,
                       'self=', self)
            return False
        return True

    def startNextRound(self):
        '''开启下一局'''
        self._destruct()

        self._checkExpire()

        conf = self._loadConf()
        if not conf:
            self.state = STATE_DUOBAO_CLOSE
            # 更新
            self.update()
            return

        if conf and self.issue + 1 > conf.get('totalIssueNum'):
            ftlog.info('Duobao.startNextRound issue equal conf.totalIssueNum',
                       'state', self.state,
                       'typeId=', self.typeId,
                       'self=', self)
            self.state = STATE_DUOBAO_CLOSE
            # 更新
            self.update()
            return

        # 装载新配置字段
        self.fromDict(conf)

        # 期号
        self.issue += 1
        self.state = STATE_DUOBAO_BET
        self.startTimestamp = pktimestamp.getCurrentTimestamp()

        # 更新
        self.update()

        timer.FTLoopTimer(self.betTime * 60, 0, self.onTimerBetStop).start()

        if ftlog.is_debug():
            ftlog.debug('DuobaoLimitedTime.startNextRound',
                        'self=', self)
            
        self.startTimerCheckRobot()

    def onTimerBetStop(self):
        self.state = STATE_DUOBAO_OPEN

        # 结算
        self._settlement()
        # 开过奖
        self.isOpen = True

        # 更新
        self.update()

        timer.FTLoopTimer(self.openTime * 60, 0, self.onTimerOpenStop).start()

        if ftlog.is_debug():
            ftlog.debug('DuobaoLimitedTime.onTimerBetStop',
                        'self=', self)

    def onTimerOpenStop(self):
        self.startNextRound()

    def fromRedis(self):
        '''从redis创建'''
        if self.isOpen is True:
            self.startNextRound()
        else:
            interval = self.startTimestamp + self.betTime * 60 - pktimestamp.getCurrentTimestamp()
            if interval > 0:
                timer.FTLoopTimer(interval, 0, self.onTimerBetStop).start()
            else:
                self.onTimerBetStop()


class DuobaoMeetTimes(Duobao):
    '''人满开奖 满足次数'''

    def __init__(self):
        super(DuobaoMeetTimes, self).__init__()
        # 需要的投注次数
        self.moreBetCount = None

        self.typeId = DUOBAO_TYPE_COUNT

    @property
    def conditionBetCount(self):
        return self.moreBetCount

    def _checkConf(self, conf):
        '''检测配置'''
        if conf.get('typeId') != self.typeId:
            ftlog.info('DuobaoMeetTimes _checkConf typeId error',
                       'conf.typeId=', conf.get('typeId'),
                       'typeId=', self.typeId,
                       'self=', self)
            return False
        openTime = conf.get('openTime')
        if not isinstance(openTime, int) or openTime < 0:
            ftlog.info('DuobaoMeetTimes _checkConf openTime error',
                       'conf.openTime=', openTime,
                       'typeId=', self.typeId,
                       'self=', self)
            return False
        moreBetCount = conf.get('moreBetCount')
        if not isinstance(moreBetCount, int) or moreBetCount <= 0:
            ftlog.info('DuobaoMeetTimes _checkConf moreBetCount error',
                       'conf.moreBetCount=', moreBetCount,
                       'typeId=', self.typeId,
                       'self=', self)
            return False
        totalIssueNum = conf.get('totalIssueNum')
        if not isinstance(totalIssueNum, int) or totalIssueNum <= 0:
            ftlog.info('DuobaoMeetTimes _checkConf totalIssueNum error',
                       'conf.totalIssueNum=', totalIssueNum,
                       'typeId=', self.typeId,
                       'self=', self)
            return False
        return True

    def startNextRound(self):
        '''开启下一局'''
        self._destruct()

        self._checkExpire()

        conf = self._loadConf()
        if not conf:
            self.state = STATE_DUOBAO_CLOSE
            # 更新
            self.update()
            return

        if conf and self.issue + 1 > conf.get('totalIssueNum'):
            ftlog.info('Duobao.startNextRound issue equal conf.totalIssueNum',
                       'state', self.state,
                       'typeId=', self.typeId,
                       'self=', self)
            self.state = STATE_DUOBAO_CLOSE
            # 更新
            self.update()
            return

        # 装载新配置字段
        self.fromDict(conf)

        # 期号
        self.issue += 1
        self.state = STATE_DUOBAO_BET
        self.startTimestamp = pktimestamp.getCurrentTimestamp()

        # 更新
        self.update()

        self._timer = timer.FTLoopTimer(20, -1, self._checkMoreBetCount)
        self._timer.start()
        
        self.startTimerCheckRobot()

    def _checkMoreBetCount(self):
        # 检测是否满足条件：人满开奖
        length = daobase.executeMixCmd('llen', 'hall.duobao.betuser:%s:%s' % (self.duobaoId, self.issue))
        if not length or length <= 0 or length < self.moreBetCount:
            if ftlog.is_debug():
                ftlog.debug('DuobaoMeetTimes._checkMoreBetCount noopen',
                            'self=', self,
                            'length=', length,
                            'moreBetCount=', self.moreBetCount)
            return

        if ftlog.is_debug():
            ftlog.debug('DuobaoMeetTimes._checkMoreBetCount open',
                        'self=', self,
                        'length=', length,
                        'moreBetCount=', self.moreBetCount)

        if self._timer:
            self._timer.cancel()
            self._timer = None
        
        self.open()

    def open(self):
        if ftlog.is_debug():
            ftlog.debug('DuobaoMeetTimes.open',
                        'self=', self,
                        'moreBetCount=', self.moreBetCount)
        self.state = STATE_DUOBAO_OPEN

        # 结算
        self._settlement()
        # 开过奖
        self.isOpen = True

        # 更新
        self.update()

        timer.FTLoopTimer(self.openTime * 60, 0, self.onTimerOpenStop).start()

    def onTimerOpenStop(self):
        self.startNextRound()

    def fromRedis(self):
        '''从redis创建'''
        if self.isOpen is True:
            self.startNextRound()
        else:
            self._timer = timer.FTLoopTimer(20, -1, self._checkMoreBetCount)
            self._timer.start()
            self.startTimerCheckRobot()


def loadDuobaoObj(duobaokey):
    duobaoDict = None
    try:
        duobaoJstr = daobase.executeMixCmd('hget', 'hall.duobao', duobaokey)
        if duobaoJstr:
            duobaoDict = strutil.loads(duobaoJstr)
            duobaoObj = Duobao.create(duobaoDict['typeId'])
            duobaoObj.fromDict(duobaoDict)
            duobaoObj.issue = duobaoDict.get('issue', 1)
            duobaoObj.validIssueNum = duobaoDict.get('validIssueNum', 1)
            return duobaoObj
    except:
        ftlog.warn('hall1yuanduobao.loadDuobaoObj',
                   'duobaokey=', duobaokey,
                   'duobaoDict=', duobaoDict)
    return None


def saveDuobaoObj(duobaoObj):
    duobaoDict = duobaoObj.toDict()
    duobaoDictJstr = strutil.dumps(duobaoDict)
    daobase.executeMixCmd('hset', 'hall.duobao', '%s:%s' % (duobaoObj.duobaoId, duobaoObj.issue), duobaoDictJstr)

    if ftlog.is_debug():
        ftlog.debug('hall1yuanduobao.saveDuobaoObj',
                    'duobaoObj=', duobaoObj,
                    'duobaoDict=', duobaoDict)


def _reloadConf():
    global _duobaoMap

    duobaoList = getConf()
    if not duobaoList or len(duobaoList) == 0:
        ftlog.warn('hall1yuanduobao._reloadConf error')
        return

    if not _checkConf(duobaoList):
        ftlog.warn('hall1yuanduobao._reloadConf._checkConf error')
        return

    duobaoList = getConf()
    for duobaoConf in duobaoList:
        if duobaoConf.get('duobaoId') not in _duobaoMap:
            duobaoObj = Duobao.create(duobaoConf['typeId'])
            duobaoObj.fromDict(duobaoConf)
            duobaoObj.fromConf()
            _duobaoMap[duobaoObj.duobaoId] = duobaoObj

            ftlog.info('hall1yuanduobao._reloadConf',
                       'new duobaoObj=', duobaoObj)

    ftlog.info('haoll1yuanduobao._reloadConf',
               'duobaoIds=', _duobaoMap.keys(),
               'duobaovalues=', _duobaoMap)
    #如果 从redis加载de

def destructRobot(duobaokey):
    daobase.executeMixCmd('hdel', 'hall.duobao', duobaokey)
    daobase.executeMixCmd('del', 'hall.duobao.betuser:%s' % (duobaokey))
    daobase.executeMixCmd('del', 'hall.duobao.betrobotuser:%s' % (duobaokey))

def _initDuobaoFromRedis():
    global _duobaoMap

    duobaoKeys = daobase.executeMixCmd('hkeys', 'hall.duobao')
    for duobaokey in duobaoKeys:
        duobaoObj = loadDuobaoObj(duobaokey)
        if duobaoObj:
            if duobaoObj.duobaoId in _duobaoMap.keys():
                destructRobot(duobaokey)
                continue
            duobaoObj.fromRedis()
            _duobaoMap[duobaoObj.duobaoId] = duobaoObj

    ftlog.info('haoll1yuanduobao._initDuobaoFromRedis',
               'duobaoIds=', _duobaoMap.keys(),
               'redisduobaokey=', duobaoKeys)

def _onConfChanged(event):
    if _inited and event.isChanged('game:9999:duobao:0'):
        _reloadConf()
        
        ftlog.info('haoll1yuanduobao._onDuobaoConfChanged',
           'duobaoIds=', _duobaoMap.keys())

def _initialize():
    '''初始化在CT进程'''
    global _inited
    if not _inited:
        _inited = True

        serverType = gdata.serverType()
        if serverType == gdata.SRV_TYPE_UTIL:
            # 加载夺宝人满开奖Lua脚本
            daobase.loadLuaScripts(_REDIS_LUA_BETLIST_NAME, _REDIS_LUA_BETLIST_SCRIPT)
        elif serverType == gdata.SRV_TYPE_CENTER:
            _initDuobaoFromRedis()
            _reloadConf()
            pkeventbus.globalEventBus.subscribe(tyevent.EventConfigure, _onConfChanged)
            ftlog.info('haoll1yuanduobao._initialize',
               'duobaoIds=', _duobaoMap.keys())


class DuobaoCostNotEnoughException(exceptions.TYBizException):
    def __init__(self, message='夺宝费用不足'):
        super(DuobaoCostNotEnoughException, self).__init__(-1, message)


class DuobaoIdAndIssueNotMatchException(exceptions.TYBizException):
    def __init__(self, message='夺宝ID和期号不匹配'):
        super(DuobaoIdAndIssueNotMatchException, self).__init__(-1, message)


class DuobaoIdAndIssueNotExistException(exceptions.TYBizException):
    def __init__(self, message='不存在此夺宝ID和期号'):
        super(DuobaoIdAndIssueNotExistException, self).__init__(-1, message)


class DuobaoNotInBetStateException(exceptions.TYBizException):
    def __init__(self, message='不在下注状态,禁止下注'):
        super(DuobaoNotInBetStateException, self).__init__(-1, message)


class DuobaoMaxBetUplimitException(exceptions.TYBizException):
    def __init__(self, message='本次下注已经超过本期夺宝总下注数上限,下注失败'):
        super(DuobaoMaxBetUplimitException, self).__init__(-1, message)


class DuobaoBeToMaxBetUplimitException(exceptions.TYBizException):
    def __init__(self, message='本期夺宝已达总下注数上限,下注失败'):
        super(DuobaoBeToMaxBetUplimitException, self).__init__(-1, message)


class DuobaoPlayerMaxBetUplimitException(exceptions.TYBizException):
    def __init__(self, message='已经达到本期夺宝个人最大下注上限,禁止下注'):
        super(DuobaoPlayerMaxBetUplimitException, self).__init__(-1, message)


class DuobaoPlayerBetNumGreaterOnceMaxNumException(exceptions.TYBizException):
    def __init__(self, message='您的下注数超过了单次最大下注数'):
        super(DuobaoPlayerBetNumGreaterOnceMaxNumException, self).__init__(-1, message)


class DuobaoPlayerBetNumErrorException(exceptions.TYBizException):
    def __init__(self, message='投注数量错误'):
        super(DuobaoPlayerBetNumErrorException, self).__init__(-1, message)


class DuobaoPlayerFinishRewardException(exceptions.TYBizException):
    def __init__(self, message='您已经领取过此期夺宝奖励'):
        super(DuobaoPlayerFinishRewardException, self).__init__(-1, message)


class DuobaoPageIdErrorException(exceptions.TYBizException):
    def __init__(self, message='页码错误'):
        super(DuobaoPageIdErrorException, self).__init__(-1, message)


def payForDuobao(userId, itemId, count, duobaoId, issue, lessbetCount, startTime):
    timestamp = pktimestamp.getCurrentTimestamp()
    userAssets = hallitem.itemSystem.loadUserAssets(userId)
    assetTuple = userAssets.consumeAsset(hallconf.HALL_GAMEID,
                                         itemId,
                                         count,
                                         timestamp,
                                         'HALL_DUOBAO_COST',
                                         int(duobaoId),
                                         int(issue), #期号
                                         int(lessbetCount), #最少开奖人次
                                         int(startTime)) #夺宝开始时间)

    if assetTuple[1] < count:
        ftlog.warn('hall1yuanduobao.payForDuobao',
                   'gameId=', hallconf.HALL_GAMEID,
                   'userId=', userId,
                   'cost=', (itemId, count),
                   'consumedCount=', assetTuple[1],
                   'err=', 'CostNotEnough')

        raise DuobaoCostNotEnoughException()

    ftlog.info('hall1yuanduobao.payForDuobao',
               'gameId=', hallconf.HALL_GAMEID,
               'userId=', userId,
               'cost=', (itemId, count),
               'consumedCount=', assetTuple[1],
               'duobaoId=', duobaoId,
               'issue=', issue)

    datachangenotify.sendDataChangeNotify(hallconf.HALL_GAMEID, userId, item.TYAssetUtils.getChangeDataNames([assetTuple]))


def addForDuobao(userId, itemId, count, duobaoId, issue, eventId, lessbetCount, startTime):
    timestamp = pktimestamp.getCurrentTimestamp()
    userAssets = hallitem.itemSystem.loadUserAssets(userId)
    assetKind, consumedCount, final = userAssets.addAsset(hallconf.HALL_GAMEID,
                                                          itemId,
                                                          count,
                                                          timestamp,
                                                          eventId,
                                                          int(duobaoId),
                                                          int(issue), #期号
                                                          int(lessbetCount), #最少开奖人次
                                                          int(startTime)) #夺宝开始时间)

    ftlog.info('hall1yuanduobao.addForDuobao',
               'gameId=', hallconf.HALL_GAMEID,
               'userId=', userId,
               'cost=', (itemId, count),
               'consumedCount=', consumedCount,
               'duobaoId=', duobaoId,
               'issue=', issue,
               'eventId=', eventId)

    if assetKind.keyForChangeNotify:
        datachangenotify.sendDataChangeNotify(hallconf.HALL_GAMEID, userId,
                                              item.TYAssetUtils.getChangeDataNames([(assetKind, consumedCount, final)]))


def genLuckyCode(duobaoId, issue):
    '''生成luckycode 线上UT9999000001 ~ UT9999000800'''
    global _luckyCodeMap
    u1001_1800 = '1' + gdata.serverNum()[-6:]

    if duobaoId in _luckyCodeMap:
        if issue in _luckyCodeMap[duobaoId]:
            _luckyCodeMap[duobaoId][issue] += 1
        else:
            _luckyCodeMap[duobaoId] = {issue: 1}
    else:
        _luckyCodeMap[duobaoId] = {issue: 1}

    # 拼接 10000011001累加
    return u1001_1800 + str(int(duobaoId) + _luckyCodeMap[duobaoId][issue])


def duobaoBet(userId, duobaoId, issue, num, bRobot = False):
    '''夺宝下注在UT进程'''
    if not isinstance(num, int) or num <= 0:
        raise DuobaoPlayerBetNumErrorException()

    duobaoObjDict = daobase.executeMixCmd('hget', 'hall.duobao', '%s:%s' % (duobaoId, issue))
    if not duobaoObjDict:
        raise DuobaoIdAndIssueNotExistException()

    duobaoObjDict = strutil.loads(duobaoObjDict)
    if duobaoObjDict.get('duobaoId') != duobaoId or duobaoObjDict.get('issue') != issue:
        raise DuobaoIdAndIssueNotMatchException()

    if duobaoObjDict.get('state') != STATE_DUOBAO_BET:
        raise DuobaoNotInBetStateException()

    betCount = daobase.executeMixCmd('hget', 'hall.duobao.betcount:%s:%s' % (duobaoId, issue), userId) or 0

    if betCount >= DUOBAO_PLAYER_BET_NUM_MAX:
        raise DuobaoPlayerMaxBetUplimitException()

    if betCount + num > DUOBAO_PLAYER_BET_NUM_MAX:
        if not bRobot:
            raise DuobaoPlayerMaxBetUplimitException(message='您在本期剩余下注数:%s次' % (DUOBAO_PLAYER_BET_NUM_MAX - betCount))
        else:
            num = DUOBAO_PLAYER_BET_NUM_MAX-betCount

    if num > DUOBAO_PLAYER_ONCE_BET_NUM_MAX:
        if not bRobot:
            raise DuobaoPlayerBetNumGreaterOnceMaxNumException(message='您的下注数超过了单次最大下注数%s' % DUOBAO_PLAYER_ONCE_BET_NUM_MAX)
        else:
            num = DUOBAO_PLAYER_ONCE_BET_NUM_MAX

    cost = duobaoObjDict.get('cost')
    # 扣除费用
    if not bRobot:
        payForDuobao(userId, cost.get('itemId'), cost.get('count') * num, duobaoId, issue,
                         duobaoObjDict.get('lessBetCount', 0), duobaoObjDict.get('startTimestamp', 0))

    # 幸运码
    luckyCodeList = [genLuckyCode(duobaoId, issue) for _ in xrange(num)]
    totalBetCount, myBetCount = 0, 0
    if duobaoObjDict.get('typeId') == DUOBAO_TYPE_TIME:
        # 下注玩家入list-临时表需要清除 结算用
        totalBetCount = daobase.executeMixCmd('rpush', 'hall.duobao.betuser:%s:%s' % (duobaoId, issue), *[userId] * num)
        # 下注次数-临时表需要清除 显示用
        myBetCount = daobase.executeMixCmd('hincrby', 'hall.duobao.betcount:%s:%s' % (duobaoId, issue), userId, num)
        # 玩家未开奖列表-临时表需要清除 显示用
        daobase.executeUserCmd(userId, 'zadd', 'hall.duobao.record.noopen.zset:%s' % userId,
                               pktimestamp.getCurrentTimestamp(), '%s:%s' % (duobaoId, issue))
        # 玩家下注幸运码入库
        daobase.executeMixCmd('sadd', 'hall.duobao.luckycode:%s:%s:%s' % (duobaoId, issue, userId), *luckyCodeList)
        #放到机器人库中
        if bRobot:
            daobase.executeMixCmd('rpush', 'hall.duobao.betrobotuser:%s:%s' % (duobaoId, issue), *[userId] * num)
    elif duobaoObjDict.get('typeId') == DUOBAO_TYPE_COUNT:
        if ftlog.is_debug():
            ftlog.debug('hall1yuanduobao.duobaoBet type=count',
                        'duobaoId=', duobaoId,
                        'issue=', issue,
                        'userId=', userId,
                        'num=', num,
                        'moreBetCount=', duobaoObjDict.get('moreBetCount'),
                        'timestamp=', pktimestamp.getCurrentTimestamp())

        luaStatus, length, count = daobase.executeMixLua(_REDIS_LUA_BETLIST_NAME,
                                                         5,
                                                         userId,
                                                         num,
                                                         duobaoObjDict.get('moreBetCount'),
                                                         'hall.duobao.betuser:%s:%s' % (duobaoId, issue),
                                                         'hall.duobao.betcount:%s:%s' % (duobaoId, issue))
        # luaStatus=-1 本身长度已经到达最大上限了  luaStatus=-2 加上本场下注次数 num 之后超过最大上限
        if luaStatus == -1 and not bRobot:
            # 退还费用
            addForDuobao(userId, cost.get('itemId'), cost.get('count') * num, duobaoId, issue, 'HALL_DUOBAO_COST',
                         duobaoObjDict.get('lessBetCount', 0), duobaoObjDict.get('startTimestamp', 0))
            raise DuobaoBeToMaxBetUplimitException()

        elif luaStatus == -2 and not bRobot:
            # 退还费用
            addForDuobao(userId, cost.get('itemId'), cost.get('count') * num, duobaoId, issue, 'HALL_DUOBAO_COST',
                         duobaoObjDict.get('lessBetCount', 0), duobaoObjDict.get('startTimestamp', 0))
            raise DuobaoMaxBetUplimitException(message='本期再下%s注就达到开奖下注数上限' % count)

        elif luaStatus == 1:
            totalBetCount, myBetCount = length, count
            # 玩家未开奖列表-临时表需要清除 显示用
            daobase.executeUserCmd(userId, 'zadd', 'hall.duobao.record.noopen.zset:%s' % userId,
                                   pktimestamp.getCurrentTimestamp(), '%s:%s' % (duobaoId, issue))
            # 玩家下注幸运码入库
            daobase.executeMixCmd('sadd', 'hall.duobao.luckycode:%s:%s:%s' % (duobaoId, issue, userId), *luckyCodeList)
            #放到机器人库中
            if bRobot:
                daobase.executeMixCmd('rpush', 'hall.duobao.betrobotuser:%s:%s' % (duobaoId, issue), *[userId] * num)
    
    coupon = 0
    if not bRobot:
        coupon = userdata.getAttr(userId, 'coupon')

    return luckyCodeList, myBetCount, totalBetCount, coupon
    

def duobaoReward(userId, duobaoId, issue):
    '''夺宝领取奖励在UT进程'''
    # 需要领取 客户端显示用
    jstr = daobase.executeUserCmd(userId, 'hget', 'hall.duobao.record.win:%s' % userId, '%s:%s' % (duobaoId, issue))
    if jstr:
        datas = strutil.loads(jstr)
        # 删除需要领取
        daobase.executeUserCmd(userId, 'hdel', 'hall.duobao.record.win:%s' % userId, '%s:%s' % (duobaoId, issue))
        # 删除需要领取 显示用
        daobase.executeUserCmd(userId, 'zrem', 'hall.duobao.record.win.zset:%s' % userId, '%s:%s' % (duobaoId, issue))
        reward = datas.get('reward')
        # 加奖励
        addForDuobao(userId, reward, 1, duobaoId, issue, 'HALL_DUOBAO_COST',
                         datas.get('lessBetCount', 0), datas.get('startTimestamp', 0))

        # 添加 已领取 保存10条 每次添加的时候判断长度，如果大于10条，只截取后10条
        recordRewardLen = daobase.executeUserCmd(userId, 'rpush', 'hall.duobao.record.reward:%s' % userId,
                                                 strutil.dumps(datas))
        if recordRewardLen > 10:
            daobase.executeUserCmd(userId, 'ltrim', 'hall.duobao.record.reward:%s' % userId, -10, -1)

        assetKind = hallitem.itemSystem.findAssetKind(reward)
        if assetKind:
            return {'url': assetKind.pic, 'name': assetKind.displayName, 'count': 1}

        return {'url': '', 'name': '', 'count': 0}
    else:
        raise DuobaoPlayerFinishRewardException()


def isShowCondition(duobaoDict, userId, clientId, timestamp):
    condD = duobaoDict.get('showCondition')
    if condD:
        cond = hallusercond.UserConditionRegister.decodeFromDict(condD)
        return cond.check(hallconf.HALL_GAMEID, userId, clientId, timestamp)
    return True


class ShowWeightCalc(object):
    def __init__(self):
        self.weights = []
    
    def calcWeight(self, gameId, userId, clientId, timestamp, **kw):
        ret = 0
        for cond, weight in self.weights:
            if cond.check(gameId, userId, clientId, timestamp, **kw):
                ret += weight
        return ret
                
    def decodeFromDict(self, d):
        for item in d:
            cond = hallusercond.UserConditionRegister.decodeFromDict(item['condition'])
            weight = item.get('weight', 0)
            if not isinstance(weight, int):
                raise exceptions.TYBizConfException(d, 'ShowWeightCalc.item.weight must be int')
            self.weights.append((cond, weight))
        return self


def isShowByWeight(duobaoDict, userId, clientId, timestamp):
    showWeightCalcD = duobaoDict.get('showWeightCalc')
    if not showWeightCalcD:
        return True, 0
    clientId = sessiondata.getClientId(userId)
    try:
        showWeightCalc = ShowWeightCalc().decodeFromDict(showWeightCalcD)
        showWeight = duobaoDict.get('showWeight', 0)
        sumWeight = showWeightCalc.calcWeight(hallconf.HALL_GAMEID, userId, clientId, pktimestamp.getCurrentTimestamp())
        if ftlog.is_debug():
            ftlog.debug('isShowByWeight,duobaoid,sum,show=', duobaoDict['typeId'], sumWeight, showWeight)
        return sumWeight > showWeight, sumWeight
    except exceptions.TYBizConfException, e:
        ftlog.error('isShowByWeight failed'
                    'msg=', e.message,
                    'dict=', duobaoDict,
                    'userId=', userId)
        return True, 0

def duobaoProduct(userId):       
    '''夺宝商品列表'''
    productList = []
    datas = daobase.executeMixCmd('hgetall', 'hall.duobao')
    if datas:
        if ftlog.is_debug():
            ftlog.debug('duobaoProduct.duobaoProduct,allKeys=', datas)
        clientId = sessiondata.getClientId(userId)
        timestamp = pktimestamp.getCurrentTimestamp()
        for i in xrange(len(datas) / 2):
            duobaoIdIssueField = datas[i * 2]
            jstr = datas[i * 2 + 1]
            try:                
                duobaoId, issue = duobaoIdIssueField.split(':')[0], duobaoIdIssueField.split(':')[1]
                d = strutil.loads(jstr)
                if not d:
                    if ftlog.is_debug():
                        ftlog.debug('duobaoloads jstr failed id=', duobaoIdIssueField)
                    continue
                
                if not isShowCondition(d, userId, clientId, timestamp):
                    if ftlog.is_debug():
                        ftlog.debug('isShowCondition failed id=', duobaoIdIssueField)
                    continue
                
                bShowByWeight, weight = isShowByWeight(d, userId, clientId, timestamp)
                if not bShowByWeight:
                    if ftlog.is_debug():
                        ftlog.debug('isShowByWeight failed id=', duobaoIdIssueField)
                    continue
                d['weight'] = weight
                d['totalBetCount'] = daobase.executeMixCmd('llen', 'hall.duobao.betuser:%s:%s' % (duobaoId, issue))
                d['myBetCount'] = daobase.executeMixCmd('hget', 'hall.duobao.betcount:%s:%s' % (duobaoId, issue),
                                                        userId) or 0
                d['luckyCodeSet'] = daobase.executeMixCmd('smembers',
                                                          'hall.duobao.luckycode:%s:%s:%s' % (duobaoId, issue, userId))
                #需要返回上次的得主
                lastwinName = daobase.executeMixCmd('hget', 'hall.duobao.lateset.win',duobaoId)
                if lastwinName:
                    d['lastWinner'] = lastwinName
                else:
                    d['lastWinner'] = ''
               
                #删除省带宽
                d.pop('showWeightCalc', None)
                d.pop('showCondition', None)
                d.pop('sendNoticeCfg', None)
                
                productList.append(d)
            except Exception:
                ftlog.error('hall1yuanduobao.doubaoProduct',
                            'userId=', userId,
                            'duobaoIdIssueField=', duobaoIdIssueField,
                            'productList=', productList,
                            'jstr=', jstr)
    else:
        ftlog.warn('hall1yuanduobao.doubaoProduct none',
                   'userId=', userId)
        
    return productList


def duobaoHistory(userId, duobaoId, pageId):
    '''往期得主 按页获取 pageId 从1开始'''
    # 中奖的玩家-往期得主-这期账单
    historyList = []

    if not pageId or pageId <= 0:
        raise DuobaoPageIdErrorException()

    hlen = daobase.executeMixCmd('hlen', 'hall.duobao.record:%s' % duobaoId)
    if hlen == 0:
        return historyList

    pageCount = 50

    for issue in xrange(hlen, 0, -1):
        jstr = daobase.executeMixCmd('hget', 'hall.duobao.record:%s' % duobaoId, issue)
        if jstr:
            duobaoRecordDict = strutil.loads(jstr)
            if duobaoRecordDict.get('settlementStatus') == DUOBAO_SETTLEMENT_NORMAL:
                if 'luckyCodeSet' in duobaoRecordDict:
                    duobaoRecordDict.pop('luckyCodeSet')
                historyList.append(duobaoRecordDict)

        if len(historyList) >= pageId * pageCount:
            break

    return historyList[(pageId - 1) * pageCount:pageId * pageCount]


def duobaoGetWinRecord(userId, duobaoId, issue):
    # 1是没有开奖 2是已开奖 3是过期
    jstr = daobase.executeMixCmd('hget', 'hall.duobao.record:%s' % duobaoId, issue)
    if jstr:
        d = strutil.loads(jstr)
        d['state'] = 2
        return d
    else:
        jstr = daobase.executeMixCmd('hget', 'hall.duobao', '%s:%s' % (duobaoId, issue))
        if jstr:
            duobaoDict = strutil.loads(jstr)
            if duobaoDict['state'] == STATE_DUOBAO_CLOSE:
                return {'state': 3}

    return {'state': 1}


def duobaoRewardRecord(userId):
    '''领奖记录 最多10条'''
    recordList = []
    jstrList = daobase.executeUserCmd(userId, 'lrange', 'hall.duobao.record.reward:%s' % userId, 0, -1)
    if jstrList:
        for jstr in jstrList:
            rewardRecord = strutil.loads(jstr)
            recordList.append(rewardRecord)

    return recordList


def doMyNoOpenDuobao(userId):
    '''已经开过奖的 添加到未中奖'''
    # 玩家未开奖列表 元素数量
    idStrList = daobase.executeUserCmd(userId, 'zrange', 'hall.duobao.record.noopen.zset:%s' % userId, 0, -1)
    if idStrList and len(idStrList) > 0:
        for idStr in idStrList:
            duobaoId, issue = idStr.split(':')[0], idStr.split(':')[1]

            # duobaoId 过期redis处理
            if 1 == daobase.executeMixCmd('sismember', 'hall.duobao.expire', duobaoId):
                # 移除
                daobase.executeUserCmd(userId, 'zrem', 'hall.duobao.record.noopen.zset:%s' % userId,
                                       '%s:%s' % (duobaoId, issue))
                daobase.executeMixCmd('hdel', 'hall.duobao.betcount:%s:%s' % (duobaoId, issue), userId)

                daobase.executeMixCmd('del', 'hall.duobao.luckycode:%s:%s:%s' % (duobaoId, issue, userId))

                if ftlog.is_debug():
                    ftlog.debug('hall1yuanduobao.doMyNoOpenDuobao expire',
                                'duobaoId=', duobaoId,
                                'issue=', issue,
                                'userId=', userId)

                continue

            jstr = daobase.executeMixCmd('hget', 'hall.duobao.record:%s' % duobaoId, int(issue))
            if jstr:
                # 已经开过奖的
                duobaoRecordDict = strutil.loads(jstr)
                # 中奖的玩家-往期得主-这期账单 字段都是得主的 purl 和 name 是得主  pic商品 displayName 商品名
                # duobaoRecordDict = {'issue': self.issue, 'purl': purl, 'name': name, 'betCount': betCount,
                #                     'luckyCode': luckyCode,
                #                     'luckyCodeSet': luckyCodeSet, 'endTime': pktimestamp.getCurrentTimestamp(),
                #                     'pic': self.pic, 'displayName': self.displayName}

                duobaoRecordDict['betCount'] = daobase.executeMixCmd('hget',
                                                                     'hall.duobao.betcount:%s:%s' % (duobaoId, issue),
                                                                     userId)
                duobaoRecordDict['luckyCodeSet'] = daobase.executeMixCmd('smembers',
                                                                         'hall.duobao.luckycode:%s:%s:%s' % (
                                                                             duobaoId, issue, userId))

                if duobaoRecordDict['settlementStatus'] == DUOBAO_SETTLEMENT_FLOW:
                    # 流局返钱
                    # 退还费用
                    cost = duobaoRecordDict['cost']
                    addForDuobao(userId, cost.get('itemId'), cost.get('count') * duobaoRecordDict['betCount'], duobaoId,
                                 issue,'HALL_DUOBAO_COST',
                         duobaoRecordDict.get('lessBetCount', 0), duobaoRecordDict.get('startTimestamp', 0))

                # 添加到未中奖
                nowinLen = daobase.executeUserCmd(userId, 'rpush', 'hall.duobao.record.nowin:%s' % userId,
                                                  strutil.dumps(duobaoRecordDict))
                if nowinLen > 10:
                    daobase.executeUserCmd(userId, 'ltrim', 'hall.duobao.record.nowin:%s' % userId, -10, -1)

                # 移除
                daobase.executeUserCmd(userId, 'zrem', 'hall.duobao.record.noopen.zset:%s' % userId,
                                       '%s:%s' % (duobaoId, issue))
                daobase.executeMixCmd('hdel', 'hall.duobao.betcount:%s:%s' % (duobaoId, issue), userId)

                daobase.executeMixCmd('del', 'hall.duobao.luckycode:%s:%s:%s' % (duobaoId, issue, userId))
            else:
                pass
                # 未开奖的 显示需要的数据 通过以下的组装 在调用的地方组装即可
                # daobase.executeUserCmd(userId, 'zadd', 'hall.duobao.record.noopen.zset:%s' % userId,
                #                        pktimestamp.getCurrentTimestamp(), '%s:%s' % (duobaoId, issue))


def getNoOpenMyDatas(userId, num):
    # 未开奖的 显示需要的数据 通过以下的组装 在调用的地方组装即可
    # daobase.executeUserCmd(userId, 'zadd', 'hall.duobao.record.noopen.zset:%s' % userId,
    #                        pktimestamp.getCurrentTimestamp(), '%s:%s' % (duobaoId, issue))

    # 客户端显示用, 有时间戳排序
    datas = {}

    if num < 0:
        return datas

    indexStrList = daobase.executeUserCmd(userId, 'zrange', 'hall.duobao.record.noopen.zset:%s' % userId, num, num)
    if not indexStrList or len(indexStrList) == 0:
        return datas

    indexStr = indexStrList[0]
    duobaoId = indexStr.split(':')[0]
    issue = indexStr.split(':')[1]

    jstr = daobase.executeMixCmd('hget', 'hall.duobao', '%s:%s' % (duobaoId, issue))
    if jstr:
        duobaoDict = strutil.loads(jstr)
        endTime = pktimestamp.getCurrentTimestamp()
        typeId = duobaoDict['typeId']
        if typeId == DUOBAO_TYPE_TIME:
            endTimestamp = duobaoDict['startTimestamp'] + duobaoDict['betTime'] * 60
            endTime = endTimestamp
        betCount = daobase.executeMixCmd('hget', 'hall.duobao.betcount:%s:%s' % (duobaoId, issue), userId)
        luckyCodeSet = daobase.executeMixCmd('smembers', 'hall.duobao.luckycode:%s:%s:%s' % (duobaoId, issue, userId))

        datas = {'pic': duobaoDict['pic'], 'displayName': duobaoDict['displayName'], 'issue': duobaoDict['issue'],
                 'endTime': endTime,
                 'betCount': betCount, 'luckyCodeSet': luckyCodeSet, 'duobaoId': duobaoId}

    if ftlog.is_debug():
        ftlog.debug('getNoOpenMyDatas=',
                    'userId=', userId,
                    'num=', num,
                    'duobaoId=', duobaoId,
                    'issue=', issue)

    return datas


def duobaoMyRecord(userId, pageId):
    '''我的夺宝记录：需要领取、未开奖、已领取、未中奖'''
    # 需要领取
    global DUOBAO_RECORD_TAG_WIN
    # 未开奖
    global DUOBAO_RECORD_TAG_NOOPEN
    # 已领奖
    global DUOBAO_RECORD_TAG_FINISH
    # 未中奖
    global DUOBAO_RECORD_TAG_NOWIN
    # 对我的未开奖中 已经开过奖的进行处理
    doMyNoOpenDuobao(userId)

    # 添加 需要领取 客户端显示用
    # datas = {'pic': self.pic, 'displayName': self.displayName, 'issue': self.issue,
    #          'endTime': pktimestamp.getCurrentTimestamp(),
    #          'betCount': betCount, 'luckyCodeSet': luckyCodeSet, 'winPurl': purl, 'winName': name,
    #          'luckyCode': luckyCode, 'reward': self.reward}
    # daobase.executeUserCmd(userId, 'hset', 'hall.duobao.record.win:%s' % userId, '%s:%s' % (duobaoId, issue)

    if not pageId or pageId <= 0:
        raise DuobaoPageIdErrorException()

    needCount = 20

    indexList = [i for i in xrange((pageId - 1) * needCount, pageId * needCount)]

    retList = []

    # 需要领取的长度
    winLength = daobase.executeUserCmd(userId, 'zcard', 'hall.duobao.record.win.zset:%s' % userId)

    # 未开奖的长度
    noopenLength = daobase.executeUserCmd(userId, 'zcard', 'hall.duobao.record.noopen.zset:%s' % userId)

    # 已领取过的长度 小于10
    beRewardLength = daobase.executeUserCmd(userId, 'llen', 'hall.duobao.record.reward:%s' % userId)

    # 未中奖的长度 小于10
    nowinLength = daobase.executeUserCmd(userId, 'llen', 'hall.duobao.record.nowin:%s' % userId)

    totalLength = winLength + noopenLength + beRewardLength + nowinLength

    if ftlog.is_debug():
        ftlog.debug('duobaoMyRecord enter',
                    'userId=', userId,
                    'pageId=', pageId,
                    'winLength=', winLength,
                    'noopenLength=', noopenLength,
                    'beRewardLength=', beRewardLength,
                    'nowinLength=', nowinLength,
                    'totalLength=', totalLength,
                    'indexList=', indexList)

    for i in xrange(needCount):
        num = indexList[i]
        if num + 1 <= winLength:
            # 客户端显示用, 有时间戳排序
            indexStrList = daobase.executeUserCmd(userId, 'zrange', 'hall.duobao.record.win.zset:%s' % userId, num, num)
            if indexStrList and len(indexStrList) > 0:
                indexStr = indexStrList[0]
                duobaoId = indexStr.split(':')[0]
                issue = indexStr.split(':')[1]
                jstr = daobase.executeUserCmd(userId, 'hget', 'hall.duobao.record.win:%s' % userId,
                                              '%s:%s' % (duobaoId, issue))
                if jstr:
                    datas = strutil.loads(jstr)
                    datas['duobaoId'] = duobaoId
                    datas['issue'] = issue
                    datas['tag'] = DUOBAO_RECORD_TAG_WIN
                    retList.append(datas)

    if len(retList) == needCount:
        return retList, totalLength

    for i in xrange(len(retList), needCount):
        num = indexList[i]
        if num + 1 <= winLength + noopenLength:
            if num - winLength < 0:
                continue
            datas = getNoOpenMyDatas(userId, num - winLength)
            if len(datas) > 0:
                datas['tag'] = DUOBAO_RECORD_TAG_NOOPEN
                retList.append(datas)

        if len(retList) == needCount:
            return retList, totalLength

    for i in xrange(len(retList), needCount):
        num = indexList[i]
        if num + 1 <= winLength + noopenLength + beRewardLength:
            if num - winLength - noopenLength < 0:
                continue
            jstr = daobase.executeUserCmd(userId, 'lindex', 'hall.duobao.record.reward:%s' % userId,
                                          num - winLength - noopenLength)
            if jstr:
                datas = strutil.loads(jstr)
                datas['tag'] = DUOBAO_RECORD_TAG_FINISH
                retList.append(datas)

        if len(retList) == needCount:
            return retList, totalLength

    for i in xrange(len(retList), needCount):
        num = indexList[i]
        if num + 1 <= winLength + noopenLength + beRewardLength + nowinLength:
            if num - winLength - noopenLength - beRewardLength < 0:
                continue
            jstr = daobase.executeUserCmd(userId, 'lindex', 'hall.duobao.record.nowin:%s' % userId,
                                          num - winLength - noopenLength - beRewardLength)
            if jstr:
                datas = strutil.loads(jstr)
                datas['tag'] = DUOBAO_RECORD_TAG_NOWIN
                retList.append(datas)

        if len(retList) == needCount:
            return retList, totalLength

    if ftlog.is_debug():
        ftlog.debug('duobaoMyRecord',
                    'userId=', userId,
                    'pageId=', pageId,
                    'retList=', retList)

    return retList, totalLength


def testDuobaoClearall(userId):
    global _duobaoMap

    datas = daobase.executeMixCmd('hgetall', 'hall.duobao')
    if datas:
        for i in xrange(len(datas) / 2):
            duobaoIdIssueField = datas[i * 2]
            duobaoId, issue = duobaoIdIssueField.split(':')[0], duobaoIdIssueField.split(':')[1]
            if duobaoId in _duobaoMap:
                del _duobaoMap[duobaoId]

            for j in xrange(1, int(issue) + 1):
                daobase.executeMixCmd('del', 'hall.duobao.betuser:%s:%s' % (duobaoId, j))
                daobase.executeMixCmd('del', 'hall.duobao.betcount:%s:%s' % (duobaoId, j))
                daobase.executeMixCmd('del', 'hall.duobao.luckycode:%s:%s:%s' % (duobaoId, j, userId))
            daobase.executeMixCmd('del', 'hall.duobao.record:%s' % duobaoId)

    daobase.executeUserCmd(userId, 'del', 'hall.duobao.record.noopen.zset:%s' % userId)
    daobase.executeUserCmd(userId, 'del', 'hall.duobao.record.nowin:%s' % userId)
    daobase.executeUserCmd(userId, 'del', 'hall.duobao.record.reward:%s' % userId)
    daobase.executeUserCmd(userId, 'del', 'hall.duobao.record.win.zset:%s' % userId)
    daobase.executeUserCmd(userId, 'del', 'hall.duobao.record.win:%s' % userId)
    daobase.executeMixCmd('del', 'hall.duobao')

    _duobaoMap = {}
    
    if ftlog.is_debug():
        ftlog.debug('testDuobaoClearall',
                '_duobaoMap=', _duobaoMap.keys())
    return userId
