# -*- coding: utf-8 -*-
'''
Created on  2015-12-30

@author: luwei
'''
from datetime import datetime

from dizhu.activities.toolbox import UserInfo, Redis, Tool, Activity, UserBag
from dizhu.entity import dizhuconf
from dizhu.entity.skillscore import SkillScoreIncrEvent
from freetime.core.timer import FTLoopTimer
import freetime.util.log as ftlog
from hall.entity import hallconf
from hall.entity import hallranking
from hall.game import TGHall
from poker.entity.biz.activity.activity import TYActivity
from poker.entity.biz.ranking.rankingsystem import TYRankingStatus
from poker.entity.dao import daobase
from poker.entity.events.tyevent import ChargeNotifyEvent
from poker.entity.events.tyevent import EventUserLogin
from poker.util import strutil
import poker.util.timestamp as pktimestamp


# _REDIS_LUA_GETUSERBYRANK_NAME = "ddz_dumplings_ranking_getUserByRank"
# _REDIS_LUA_GETUSERBYRANK_SCRIPT = '''
#     local rankingId = KEYS[1]
#     local issueNumber = KEYS[2]
#     local index = tonumber(KEYS[3]) - 1
#     local key = 'ranking.list:'..rankingId..':'..issueNumber
#
#     return redis.call('ZREVRANGE', key, index, index, 'WITHSCORES')
# '''
# daobase.loadLuaScripts(_REDIS_LUA_GETUSERBYRANK_NAME, _REDIS_LUA_GETUSERBYRANK_SCRIPT)
#
#
def getRankingUserByRank(rankingId, issueNumber, rankingNum):
    '''
    获得指定排名的玩家和分数
    :param rankingId: 排行榜ID, '110006133'
    :param issueNumber: 期号, '20160125'
    :param rankingNum: 名次, 从1开始
    :return:[userId, score]
    '''
    key = 'ranking.list:' + rankingId + ':' + issueNumber
    index = rankingNum - 1
    ftlog.debug("getRankingUserByRank",
                "rankingId=",rankingId,
                "issueNumber=", issueNumber,
                "rankingNum=", rankingNum)
    return daobase.executeMixCmd('ZREVRANGE', key, index, index, 'WITHSCORES')
    # return daobase.executeMixLua(_REDIS_LUA_GETUSERBYRANK_NAME, 3, rankingId, issueNumber, rankingNum)


class DumplingHandler(object):
    '''
    事件监听函数集中放置
    '''

    @classmethod
    def onSkillScoreIncrease(cls, event):
        '''
        大师分增加监听,监听并更新排行,过期不会监听
        '''
        userId = event.userId

        ftlog.debug("DumplingHandler.onSkillScoreIncrease: "
                    "userId=", userId,
                    "isOutdate=", DumplingsUtil.isOutdate())
        if DumplingsUtil.isOutdate():
            return
        DumplingsUtil.updateRankingStatus(userId) # 若排行榜重置,则重置积分记录

        incr = event.newScore - event.oldScore
        rediskey = DumplingsUtil.getRedisKey()
        jsondict = Redis.readJson(userId, rediskey)

        dashifen_count = 0
        if jsondict:
            dashifen_count = jsondict.get("dashifen", 0)
        dashifen_count = dashifen_count + (incr or 0)

        jsondict['dashifen'] = dashifen_count
        Redis.writeJson(userId, rediskey, jsondict)

        DumplingsUtil.updateRankScore(userId, event.timestamp)
        ftlog.debug("DumplingHandler.onSkillScoreIncrease: "
                    "userId=", userId,
                    "event=", event)

    @classmethod
    def onChargeNotify(cls, event):
        '''
        充值监听,监听并更新排行和redis记录的RMB,过期不会监听
        '''
        userId = event.userId

        ftlog.debug("DumplingHandler.onChargeNotify: "
                    "userId=", userId,
                    "isOutdate=", DumplingsUtil.isOutdate())

        if DumplingsUtil.isOutdate():
            return

        clientGameId = strutil.getGameIdFromHallClientId(event.clientId)
        if clientGameId not in [6, 7]:
            return

        DumplingsUtil.updateRankingStatus(userId) # 若排行榜重置,则重置积分记录

        rediskey = DumplingsUtil.getRedisKey()
        jsondict = Redis.readJson(userId, rediskey)

        rmb_count = 0
        if jsondict:
            rmb_count = jsondict.get("rmb", 0)
        rmb_count = rmb_count + (event.rmbs or 0)

        jsondict['rmb'] = rmb_count
        Redis.writeJson(userId, rediskey, jsondict)

        DumplingsUtil.updateRankScore(userId, event.timestamp)
        ftlog.debug("DumplingHandler.onChargeNotify: userId=", userId, "event=", event, "jsondict=", jsondict)

    @classmethod
    def onUserLogin(cls, event):
        '''
        用户登录监听,过期不会监听
        '''
        userId = event.userId
        # OnlineLogging.loggingRanking(userId)

        isOutdate = DumplingsUtil.isOutdate()
        ftlog.debug("DumplingHandler.onUserLogin: ",
                    "userId=", userId,
                    "isOutdate:", isOutdate)
        if isOutdate:
            return
        DumplingsUtil.updateRankingStatus(userId) # 若排行榜重置,则重置积分记录
        DumplingsUtil.updateRankScore(userId, event.timestamp)

class OnlineLogging(object):
    '''
    线上日志打印处理
    '''

    @classmethod
    def loggingCredit(cls, userId):
        '''
        当以达到积分获得奖励时——统计每天每个档位达到的玩家数量
        实现:每次积分更新时,统计玩家到达第几个档位
        '''
        clientconf = DumplingsUtil.getActivityConf()
        reward = Tool.dictGet(clientconf, 'config.activate.credit.rewards')
        helper = CreditRewardHelper(userId, reward)
        now = datetime.now()
        score = 0
        conf = helper.getCurrentReachedConf()
        if conf:
            score = conf.get('score', 0)

        ftlog.info("DdzDumplings.Credit,", "userId", userId, "now", now, "score", score)

#     @classmethod
#     def loggingRanking(cls, userId):
#         '''
#         当以排名发放奖励时——每期结算时获奖玩家的名次、UID、大师分提升获得的积分、充值获得的积分
#         实现:每次登陆时,统计玩家已经完结的每一期的名次、大师分提升获得的积分、充值获得的积分
#         '''
#         # rankingId = DumplingsUtil.getRankingId()
#         # if not rankingId:
#         #     return
#         # rankingDefine = hallranking.rankingSystem.findRankingDefine(rankingId)
#         rediskey = DumplingsUtil.getRedisKey()
#         jsondict = Redis.readJson(userId, rediskey)
#         history_dict = jsondict.get('history', {})
# 
#         info = ""
#         for currentIssueNumber in history_dict:
#             currentIssue = history_dict[currentIssueNumber]
#             info = info +   " issueNumber " + str(currentIssueNumber) + \
#                             " rankNumber " + str(currentIssue.get('rankNumber', -1)) + \
#                             " dashifen " + str(currentIssue.get('dashifen', 0)) + \
#                             " rmb " + str(currentIssue.get('rmb', 0))
# 
#         rankingstr = json.dumps(history_dict)
#         ftlog.info("DdzDumplings.Ranking.Number,", "userId", userId, info, "history", rankingstr)


class RankingTopNRecorder(object):
    '''
    排行榜前N名对比记录器，用于对比排行榜前N名的人员变动
    '''
    def recordTopN(self, topn):
        '''
        记录排行榜的前n名
        '''
        self.rankingId = DumplingsUtil.getRankingId()
        self.topn = topn
        self.oldRankingList = hallranking.rankingSystem.getTopN(self.rankingId, self.topn)
        return

    def updateHasChange(self):
        '''
        再次更新TopN,对比之前记录的是否存在差异,若存在则返回排名最高的升排名信息
        排行榜模块结构示意图：
        rankingList[rankingUserList{TYRankingUser(self, userId, score, rank)}]
        '''
        newRankingList = hallranking.rankingSystem.getTopN(self.rankingId, self.topn)
        ftlog.debug("RankingTopNRecorder.updateHasChange:",
                    "self.oldRankingList.rankingUserList=", self.oldRankingList.rankingUserList,
                    "newRankingList.rankingUserList=", newRankingList.rankingUserList)
        min_count = min(len(self.oldRankingList.rankingUserList), len(newRankingList.rankingUserList), self.topn)
        for i in xrange(0, min_count):
            oldRankingUser = self.oldRankingList.rankingUserList[i]
            newRankingUser = newRankingList.rankingUserList[i]
            if oldRankingUser.userId != newRankingUser.userId:
                return newRankingUser, oldRankingUser
        return False, False

class RankingPriorityLedSender(object):
    '''
    排名优先LED发送器
    每次新增的LED都会发送5次，间隔1分钟(若无中断)
    若再次新增的LED玩家排名更高，则发送新增的玩家的LED，将之前的玩家LED终止
    若再次新增LED玩家排名比当前发送LED的玩家排名低，则直接抛弃新增玩家LED内容
    '''
    rankingRewardList = None
    ledFormatText = None

    currentRankingUser = None
    oldRankingUser = None
    loopTimer = None
    loopTimerCounter = 0

    @classmethod
    def addingLed(cls, newRankingUser, oldRankingUser):
        '''
        TYRankingUser(self, userId, score, rank)
        '''
        ftlog.debug("RankingPriorityLedSender.addingLed",
                    "newRankingUser.userId=", newRankingUser.userId,
                    "oldRankingUser.userId=", oldRankingUser.userId,
                    "ifok=", not not (cls.currentRankingUser and cls.currentRankingUser.rank < newRankingUser.rank))

        if cls.currentRankingUser and cls.currentRankingUser.rank < newRankingUser.rank:
            return
        cls.currentRankingUser = newRankingUser
        cls.oldRankingUser = oldRankingUser
        cls.start()
        return

    @classmethod
    def start(cls):
        if cls.loopTimer:
            cls.loopTimer.cancel()
        cls.loopTimer = FTLoopTimer(60, -1, cls.onUpdate)
        cls.loopTimerCounter = 0
        cls.loopTimer.start()
        cls.onUpdate()

    @classmethod
    def onUpdate(cls):
        ftlog.debug("RankingPriorityLedSender.onUpdate",
                    "cls.currentRankingUser=", cls.currentRankingUser,
                    "cls.rankingRewardList=", cls.rankingRewardList,
                    "cls.ledFormatText=", cls.ledFormatText,
                    "ifok=", not not (not cls.currentRankingUser or not cls.ledFormatText or not cls.rankingRewardList))

        if not cls.currentRankingUser or not cls.ledFormatText or not cls.rankingRewardList:
            cls.currentRankingUser = None
            cls.oldRankingUser = None
            cls.loopTimerCounter = 0
            if cls.loopTimer:
                cls.loopTimer.cancel()
            return
        ftlog.debug("RankingPriorityLedSender.onUpdate",
                    "userId=", cls.currentRankingUser.userId,
                    "cls.loopTimerCounter", cls.loopTimerCounter)

        helper  = RankingRewardHelper(cls.currentRankingUser.userId, cls.rankingRewardList)
        reachedlist = helper.getReachedConfList()
        currentconf = {}
        if reachedlist and len(reachedlist) > 0:
            currentconf = reachedlist[-1]
        dictionary = {}
        dictionary['ranking_current_item'] = Tool.dictGet(currentconf, 'rewardContent.desc')
        dictionary['newuser_nickname'] = UserInfo.getNickname(cls.currentRankingUser.userId)
        dictionary['newuser_ranknumber'] = str(DumplingsUtil.getRankingWithUserId(cls.currentRankingUser.userId))
        dictionary['olduser_nickname'] = UserInfo.getNickname(cls.oldRankingUser.userId)
        led = strutil.replaceParams(cls.ledFormatText, dictionary)
        Tool.sendLed(led)

        cls.loopTimerCounter += 1
        if cls.loopTimerCounter >= 5:
            ftlog.debug("RankingPriorityLedSender.onUpdate ",
                        "cls.loopTimerCounter>=5:",
                        "userId=", cls.currentRankingUser.userId)
            cls.currentRankingUser = None
            cls.oldRankingUser = None
            cls.loopTimer.cancel()
            cls.loopTimerCounter = 0


class DumplingsUtil(object):
    '''
    饺子活动工具,用于记录饺子活动所需的数据
    '''
    RANK_TYPE_DDZ_DUMPLINGS = 'ddz_dumplings'

    @classmethod
    def registerListener(cls, ddzeventbus):
        ddzeventbus.subscribe(SkillScoreIncrEvent, DumplingHandler.onSkillScoreIncrease)
        TGHall.getEventBus().subscribe(EventUserLogin, DumplingHandler.onUserLogin)
        TGHall.getEventBus().subscribe(ChargeNotifyEvent, DumplingHandler.onChargeNotify)

    @classmethod
    def getDdzActivityConf(cls):
        '''
        获得game/6/activity/0.json的ddz_dumplings配置
        '''
        return dizhuconf.getActivityConf("ddz_dumplings")

    @classmethod
    def getActivityConf(cls):
        '''
        获得game/9999/activity/0.json中的具体活动ID的配置
        '''
        dizhuconf = cls.getDdzActivityConf()
        activityId = dizhuconf.get('activityId')
        return Activity.getConfigById(activityId)

    @classmethod
    def getRankingId(cls):
        '''
        根据配置的rankingkey获取rankingId
        '''
        clientconf = cls.getActivityConf()
        rankingkey = Tool.dictGet(clientconf, 'config.activate.rankingKey')
        allrankingconf = hallconf.getRankingConf()
        ranking_templates = allrankingconf.get('rankingKeys', {})
        if not ranking_templates:
            return
        l = ranking_templates.get(rankingkey, {}).get('default')
        if l:
            return l[0]
        return

    @classmethod
    def getRankingConfigById(cls, rankingId):
        '''
        获得排行榜配置,找不到返回None
        '''
        conf = hallconf.getRankingConf()
        rankingconflist = conf.get('list')
        for rankingconf in rankingconflist:
            if rankingconf.get('rankingId') == rankingId:
                return rankingconf
        return

    @classmethod
    def getRedisKey(cls):
        '''
        获得存在记录RMB累计和起始大师分的redis key
        '''
        dizhuconf = cls.getDdzActivityConf()
        rediskey = "dumplings" + dizhuconf.get('datetime_start', "2016")
        return rediskey

    @classmethod
    def isOutdate(cls):
        '''
        获得是否过期,使用game/6/activity/0.json中的配置判断
        '''
        dizhuconf = cls.getDdzActivityConf()
        return not Tool.checkNow(dizhuconf.get('datetime_start', '2016-01-01 00:00:00'), dizhuconf.get('datetime_end', '2016-01-01 00:00:00'))

    @classmethod
    def calculateScore(cls, rmb, dashifen):
        '''
        计算排行分数
        :param rmb: 活动期间RMB消费总数
        :param dashifen: 活动期间大师分增长数量
        '''
        actconf = cls.getActivityConf()
        dashifen_ratio = Tool.dictGet(actconf, 'config.activate.dashifen_ratio', 0)
        charge_ratio = Tool.dictGet(actconf, 'config.activate.charge_ratio', 0)
        return dashifen * dashifen_ratio + rmb * charge_ratio

    @classmethod
    def getScoreNum(cls, userId):
        '''
        获得分数(饺子数目)
        '''
        rediskey = cls.getRedisKey()
        jsondict = Redis.readJson(userId, rediskey)

        rmb_count = 0
        dashifen_count = 0
        if jsondict:
            dashifen_count = jsondict.get("dashifen", 0)
            rmb_count = jsondict.get("rmb", 0)
        return cls.calculateScore(rmb_count, dashifen_count)

    @classmethod
    def updateRankScore(cls, userId, timestamp):
        '''
        更新排行分数
        :param timestamp: 时间戳
        :param rmb: 活动期间RMB消费总数
        :param dashifen: 活动期间大师分增长数量
        '''
        ## record top 10
        recorder = RankingTopNRecorder()
        recorder.recordTopN(10)

        if not recorder.oldRankingList:
            ftlog.debug("DumplingsUtil.updateRankScore: ",
                        "userId=", userId,
                        "err=", "NotOldRankingList")
            return
        
        score = cls.getScoreNum(userId)
        hallranking.rankingSystem.setUserByInputType(6, cls.RANK_TYPE_DDZ_DUMPLINGS, userId, score, timestamp)
        ftlog.debug("DumplingsUtil.updateRankScore: ",
                    "userId=", userId,
                    "score=", score)

        ## diff top 10
        newRankingUser, oldRankingUser = recorder.updateHasChange()
        ftlog.debug("DumplingsUtil.updateRankScore: updateHasChange()",
                    "userId=", userId,
                    "newRankingUser=", newRankingUser,
                    "oldRankingUser=", oldRankingUser)

        if newRankingUser and oldRankingUser:
            RankingPriorityLedSender.addingLed(newRankingUser, oldRankingUser)

        # 积分发奖类型,自动实时发奖
        cls._creditTypeSendRewardsIfNeed(userId)

        # 日志记录
        OnlineLogging.loggingCredit(userId)

    @classmethod
    def _creditTypeSendRewardsIfNeed(cls, userId):
        '''
        积分发奖类型,当积分达到发奖值后,自动发奖(仅供积分发奖类型使用:"rewardsType": "credit")
        '''
        actconf = DumplingsUtil.getActivityConf()
        isRanking = Tool.dictGet(actconf, 'config.activate.rewardsType', 'credit') == 'ranking'
        if isRanking:
            return
        rediskey = cls.getRedisKey()
        mail = Tool.dictGet(actconf, 'config.activate.mail')
        reward = Tool.dictGet(actconf, 'config.activate.credit.rewards')
        jsondict = Redis.readJson(userId, rediskey)

        helper = CreditRewardHelper(userId, reward)
        reachedlist = helper.getReachedConfList() # 达到发奖条件的所有奖励配置的list
        getlist = jsondict.get('getlist', []) # 已经领取的奖励list,使用score字段记录,score字段值不可重复

        for item in reachedlist:
            for assets in item.get('items'):
                if item['score'] not in getlist:
                    getlist.append(item['score'])
                    ranking_num = cls.getRankingWithUserId(userId)
                    mailstr = strutil.replaceParams(mail, {'assets': item.get('desc'), 'ranking_num': ranking_num})
                    UserBag.sendAssetsToUser(6, userId, assets, 'DDZ_ACT_DUMPLINGS', mailstr)

        # 记录奖励已经领取
        jsondict['getlist'] = getlist
        Redis.writeJson(userId, rediskey, jsondict)
        ftlog.debug("DumplingsUtil.creditTypeSendRewardsIfNeed: userId=", userId, "jsondict=", jsondict)

    @classmethod
    def updateRankingStatus(cls, userId):
        '''
        查看是否
        [redis gametable]
        {
            'rankissue' : '20160125',
            'dashifen':10,
            'rmb':11
        }
        '''
        key = cls.getRedisKey()
        user_props = Redis.readJson(userId, key)

        rankingId = cls.getRankingId()
        ftlog.debug("DumplingsUtil.updateRankingStatus",
                    "userId=", userId,
                    "rankingId=", rankingId)
        if not rankingId:
            return

        rankingIssueNumber = user_props.get('rankissue')
        currentRankingIssueNumber = cls.getCurrentRankingIssueNumber()
        ftlog.debug("DumplingsUtil.updateRankingStatus",
                    "userId=", userId,
                    "currentRankingIssueNumber=", currentRankingIssueNumber,
                    "rankingIssueNumber=", rankingIssueNumber,
                    "equal=", currentRankingIssueNumber == rankingIssueNumber)
        if not currentRankingIssueNumber or currentRankingIssueNumber == rankingIssueNumber:
            return

        user_props['rankissue'] = currentRankingIssueNumber
        userRankingInfo = hallranking.rankingSystem._rankingDao.getUserRankWithScore(rankingId, currentRankingIssueNumber, userId)
        rankNumber = -1
        if userRankingInfo and userRankingInfo[0] != None:
            rankNumber = userRankingInfo[0] + 1
        # history_dict = user_props.get('history', {})
        # history_dict[currentRankingIssueNumber] = {
        #     'dashifen':user_props.get('dashifen', 0),
        #     'rmb': user_props.get('rmb', 0),
        #     'rankNumber': rankNumber
        # }

        ## online logging
        ftlog.info("DdzDumplings.Ranking.Number,",
                   "userId ", userId,
                   "issueNumber ", str(currentRankingIssueNumber),
                   "rankNumber " + str(rankNumber),
                   "dashifen " + str(user_props.get('dashifen', 0)),
                   "rmb " + str(user_props.get('rmb', 0))
                   )
        ## 重置数据
        user_props['dashifen'] = 0
        user_props['rmb'] = 0
        Redis.writeJson(userId, key, user_props)
        ftlog.debug("DumplingsUtil.updateRankingStatus: "
                    "userId=", userId,
                    "user_props=", user_props)

#     @classmethod
#     def updateRankingStatus_backup(cls, userId):
#         '''
#         [redis gametable]
#         {
#             'resetstatus': {
#                 '20160125': 0, # key=issueNumber, value=state(0代表未重置,1代表已经重置)
#                 ...
#             },
#             'history': {
#                 '20160125': {'dashifen':0, 'rmb':0} # key=issueNumber,
#             }
#         }
#         '''
#         isNeedReset = False
# 
#         key = cls.getRedisKey()
#         jsondict = Redis.readJson(userId, key)
#         resetstatus_dict = jsondict.get('resetstatus', {})
#         history_dict = jsondict.get('history', {})
# 
#         rankingId = cls.getRankingId()
#         ftlog.debug("DumplingsUtil.updateRankingStatus",
#                     "userId=", userId,
#                     "rankingId=", rankingId)
#         if not rankingId:
#             return
#         rankingDefine = hallranking.rankingSystem.findRankingDefine(rankingId)
#         rankingStatus = hallranking.rankingSystem._loadRankingStatus(rankingDefine)
# 
#         issueNumberList = []
#         for item in rankingStatus.historyList:
#             issueNumber = item.issueNumber
#             if item.state == TYRankingStatus.STATE_FINISH or item.state == TYRankingStatus.STATE_REWARDS: # 此期排行榜已经终结或者已经发奖,则可以重置
#                 resetstatus = resetstatus_dict.get(issueNumber, 0)
#                 if resetstatus == 0:
#                     isNeedReset = True
#                     issueNumberList.append(issueNumber)
#                 resetstatus_dict[issueNumber] = 1
# 
#         if isNeedReset:
#             issueNumber = issueNumberList[0]
#             userRankingInfo = hallranking.rankingSystem._rankingDao.getUserRankWithScore(rankingId, issueNumber, userId)
#             rankNumber = -1
#             if userRankingInfo and userRankingInfo[0] != None:
#                 rankNumber = userRankingInfo[0] + 1
#             history_dict[issueNumber] = {'dashifen':jsondict.get('dashifen', 0), 'rmb': jsondict.get('rmb', 0), 'rankNumber': rankNumber}
#             jsondict['dashifen'] = 0
#             jsondict['rmb'] = 0
# 
#         jsondict['resetstatus'] = resetstatus_dict
#         jsondict['history'] = history_dict
#         Redis.writeJson(userId, key, jsondict)
#         ftlog.debug("DumplingsUtil.updateRankingStatus: "
#                     "userId=", userId,
#                     "jsondict=", jsondict)

    @classmethod
    def getCurrentRankingIssueNumber(cls):
        '''
        获得当前排行榜的期号(每周期的排行开始日期),用于查询排行榜
        '''
        rankingId = cls.getRankingId()
        if not rankingId:
            return
        rankingDefine = hallranking.rankingSystem.findRankingDefine(rankingId)
        timestamp = pktimestamp.getCurrentTimestamp()
        timeCycle = rankingDefine.getCurrentCycle(timestamp)
        if not timeCycle:
            return
        issueNumber = timeCycle.buildIssueNumber()
        return issueNumber

    @classmethod
    def getCurrentIssueRankingEndTime(cls):
        '''
        获得当前这一期的排行的结束时间
        '''
        rankingId = cls.getRankingId()
        if not rankingId:
            return
        rankingDefine = hallranking.rankingSystem.findRankingDefine(rankingId)
        timestamp = pktimestamp.getCurrentTimestamp()
        endtime = rankingDefine.getCurrentCycle(timestamp).endTime
        return endtime

    @classmethod
    def getRankingWithUserId(cls, userId):
        '''
        获得玩家的排名(从1开始),若没有则返回None
        '''
        rankingId = cls.getRankingId()
        if not rankingId:
            return
        rankingDefine = hallranking.rankingSystem.findRankingDefine(rankingId)
        timestamp = pktimestamp.getCurrentTimestamp()
        timeCycle = rankingDefine.getCurrentCycle(timestamp)
        if not timeCycle:
            return
        issueNumber = timeCycle.buildIssueNumber()
        userRankingInfo = hallranking.rankingSystem._rankingDao.getUserRankWithScore(rankingId, issueNumber, userId)
        if userRankingInfo and userRankingInfo[0] != None:
            return userRankingInfo[0] + 1
        return

class CreditRewardHelper(object):
    def __init__(self, userId, rewards):
        self.userId = userId
        self.rewards = rewards
        self.score_current = DumplingsUtil.getScoreNum(userId)
        self.rewards.sort(cmp=lambda l,r:cmp(l['score'], r['score']))

    def getHigherLevelConf(self):
        '''
        获得更高一级的奖励配置,若不存(已经处于最高)在则返回None
        '''
        score_current = self.score_current
        for i in xrange(0, len(self.rewards)):
            cur = self.rewards[i]
            if cur and cur['score'] > score_current:
                return self.rewards[i]
        return

    def getReachedConfList(self):
        '''
        获得已经达到的等级的奖励配置列表
        '''
        score_current = self.score_current
        reachs = []
        for i in xrange(0, len(self.rewards)):
            cur = self.rewards[i]
            if cur and cur['score'] <= score_current:
                reachs.append(self.rewards[i])
        return reachs

    def getCurrentReachedConf(self):
        '''
        获得已经达到的最高等级的奖励配置,若没有则返回None
        '''
        l = self.getReachedConfList()
        if l and len(l) > 0:
            return l[-1]
        return

    def isTopLevel(self):
        '''
        是否已经是最高奖励等级
        '''
        return self.score_current >= self.getMaxLevelRequireScore()

    def getHigherLevelScoreDV(self):
        '''
        获得距离更高一级奖励的分数差距
        '''
        score_current = self.score_current
        conf = self.getHigherLevelConf()
        if not conf:
            return
        score_higher = conf['score']
        return score_higher - score_current

    def getMaxLevelRequireScore(self):
        '''
        获得最高级奖励的分数要求
        '''
        return self.rewards[-1]['score']

class RankingRewardHelper(object):
    def __init__(self, userId, rewards):
        self.userId = userId
        self.rewards = rewards
        self.ranking_current = DumplingsUtil.getRankingWithUserId(userId) or 99999999999999999999999999999
        self.rewards.sort(cmp=lambda l,r:cmp(l['start'], r['start']), reverse=True)

    def getHigherLevelConf(self):
        '''
        获得更高等级的奖励配置
        '''
        ranking_current = self.ranking_current
        for i in xrange(0, len(self.rewards)):
            cur = self.rewards[i]
            if cur and cur['end'] < ranking_current:
                return self.rewards[i]
        return

    def getReachedConfList(self):
        '''
        获得已经达成的奖励配置列表
        '''
        ranking_current = self.ranking_current
        reachs = []
        for i in xrange(0, len(self.rewards)):
            cur = self.rewards[i]
            if cur and ranking_current <= cur['end']:
                reachs.append(self.rewards[i])
        return reachs

    def isTopLevel(self):
        '''
        达到最高等级奖励
        '''
        first = self.rewards[-1]
        return first['start'] <= self.ranking_current and self.ranking_current <= first['end']

    def getHigherLevelDV(self):
        '''
        获得距离更高等级奖励最低排名的差值,若已经是最高等级则返回None
        '''
        ranking_current = self.ranking_current
        conf = self.getHigherLevelConf()
        if not conf:
            return
        ranking_higher = conf['end']
        return ranking_current - ranking_higher

    def getMinLevelRequire(self):
        '''
        获得最低级奖励的最低要求名次
        '''
        return self.rewards[0]['end']

class TYActivityDumplings(TYActivity):
    TYPE_ID = 6003
    TYPE_ID_PC = 6005

    def getConfigForClient(self, gameId, userId, clientId):
        '''
        获取客户端要用的活动配置，由TYActivitySystemImpl调用
        '''
        clientconf = self._clientConf
        serverconf = self._serverConf
        ftlog.debug("TYActivityDumplings.getConfigForClient: ",
                    "userId=", userId,
                    "gameId=", gameId,
                    "clientId=", clientId,
                    "serverconf=",serverconf,
                    "clientconf=", clientconf)

        rankingId = DumplingsUtil.getRankingId()
        if not rankingId:
            return
        rankingconf = DumplingsUtil.getRankingConfigById(rankingId)
        rewardlist = rankingconf.get('rankRewardList', [])
        RankingPriorityLedSender.rankingRewardList = rewardlist

        actconf = DumplingsUtil.getActivityConf()
        RankingPriorityLedSender.ledFormatText = Tool.dictGet(actconf, 'config.activate.ranking.userLed')
        ftlog.debug("TYActivityDumplings.getConfigForClient: ",
                    "userId=", userId,
                    "rewardlist=", rewardlist,
                    "ledFormatText=", RankingPriorityLedSender.ledFormatText)

        return clientconf

    def handleRequest(self, msg):
        userId = msg.getParam('userId')
        gameId = msg.getParam('gameId')
        clientId = msg.getParam("clientId")
        activityId = msg.getParam("activityId")
        action = msg.getParam("action")

        if action == "ddz.dumplings.update":
            return self.update(userId, gameId, clientId, activityId)
        else:
            ftlog.debug("TYActivityDumplings.handleRequest: userId=", userId, "action not found")
            return {"isOK":False}

    def getUserinfoDictionary(self, userId, isRanking):
        '''
        score_num - 分数(饺子数)
        score_name - 分数的名字(积分,饺子...)
        credit_higher_dv - 积分方式: 距离更高一级奖励的积分差值
        credit_higher_item - 积分方式: 更高一级奖励的奖励描述
        credit_max_score - 积分方式: 最高级奖励的积分要求

        ranking_num - 排名
        ranking_higher_dv - 排行榜方式: 距离更高一级奖励的名次差值
        ranking_higher_item - 排行榜方式: 更高一级奖励的描述
        ranking_current_item - 排行榜方式: 当前奖励描述
        ranking_higher_score_dv - 排行榜方式: 距离更高一级奖励的积分(饺子)差距
        '''
        clientconf = self._clientConf

        score_num = DumplingsUtil.getScoreNum(userId)
        score_name = Tool.dictGet(clientconf, 'config.activate.scoreName')

        rconf = {
            'score_num': int(score_num),
            'score_name': score_name,
        }

        if isRanking:
            rankingId = DumplingsUtil.getRankingId()
            if not rankingId:
                return
            rankingconf = DumplingsUtil.getRankingConfigById(rankingId)
            ftlog.debug("TYActivityDumplings.getUserinfoDictionary: ",
                        "userId=", userId,
                        "rankingId=", rankingId,
                        "rankingconf=", rankingconf)

            rewardlist = rankingconf.get('rankRewardList', [])
            helper  = RankingRewardHelper(userId, rewardlist)
            ftlog.debug("lTYActivityDumpings.getUserinfoDictionary: ",
                        "userId=", userId,
                        "isRanking=", isRanking,
                        "rewardlist=", rewardlist)

            higherconf = helper.getHigherLevelConf() or {}
            reachedlist = helper.getReachedConfList()
            ftlog.debug("lTYActivityDumpings.getUserinfoDictionary: ",
                        "userId=", userId,
                        "higherconf=", higherconf,
                        "reachedlist=", reachedlist)

            currentconf = {}
            if reachedlist and len(reachedlist) > 0:
                currentconf = reachedlist[-1]

            issueNumber = DumplingsUtil.getCurrentRankingIssueNumber()
            if not issueNumber:
                ftlog.debug("lTYActivityDumpings.getUserinfoDictionary: ",
                            "userId=", userId,
                            "higherconf=", higherconf,
                            "reachedlist=", reachedlist,
                            "err=", "NotIssueNumber")
                return
            ## 排行榜奖励的最低名次
            min_ranking_num = helper.getMinLevelRequire() # 容错使用
            higherconf_end = higherconf.get('end', min_ranking_num)
            ## 获取更高一档的奖励的最低名次的用户的分数,返回值(userId, score)
            rankingUser = getRankingUserByRank(rankingId, issueNumber, higherconf_end)
            ranking_higher_score_dv = 0
            if rankingUser and len(rankingUser) >= 2:
                my_score = DumplingsUtil.getScoreNum(userId)
                higher_user_score = rankingUser[1]
                ranking_higher_score_dv = higher_user_score - my_score
                ftlog.debug("lTYActivityDumpings.getUserinfoDictionary: ",
                            "userId=", userId,
                            "my_score=", my_score,
                            "higher_user_score=", higher_user_score)

            if ranking_higher_score_dv <= 0:
                ranking_higher_score_dv = 1

            ftlog.debug("lTYActivityDumpings.getUserinfoDictionary: ",
                        "userId=", userId,
                        "rankingId=", rankingId,
                        "issueNumber=",issueNumber,
                        "min_ranking_num=", min_ranking_num,
                        "higherconf_end=", higherconf_end,
                        "rankingUser=", rankingUser)

            rconf.update({
                'ranking_num': DumplingsUtil.getRankingWithUserId(userId),
                'ranking_higher_dv': int(helper.getHigherLevelDV() or 0),
                'ranking_higher_item': Tool.dictGet(higherconf, 'rewardContent.desc'),
                'ranking_current_item': Tool.dictGet(currentconf, 'rewardContent.desc'),
                'ranking_higher_score_dv': ranking_higher_score_dv and int(ranking_higher_score_dv),
                'is_first': helper.isTopLevel()
            })
            return rconf
        else:
            reward = Tool.dictGet(clientconf, 'config.activate.credit.rewards')
            helper = CreditRewardHelper(userId, reward)
            rconf.update({
                'credit_higher_dv': helper.getHigherLevelScoreDV() or 0,
                'credit_higher_item': (helper.getHigherLevelConf() or {}).get('desc'),
                'credit_max_score': helper.getMaxLevelRequireScore() or 0,
                'is_first': helper.isTopLevel()
            })
            return rconf

    def update(self, userId, gameId, clientId, activityId):
        '''
        result={
            'gameId': 6,
            'userId': 10002,
            'activityId': u'activity_ddz_dumplings_160119',
            'action': u'ddz.dumplings.update',

            'isOK': False,
            'tip': u'\u6d3b\u52a8\u5df2\u8fc7\u671f',
            'userinfoHave':
            'userinfoRanking':
            'userinfoHigherRewards':
        }
        '''
        actconf = DumplingsUtil.getActivityConf()
        ftlog.debug('TYActivityDumplings.update: ',
                    'userId=', userId,
                    'actconf=',actconf)

        isRanking = Tool.dictGet(actconf, 'config.activate.rewardsType', 'credit') == 'ranking'
        userinfoDictionary = self.getUserinfoDictionary(userId, isRanking)
        ftlog.debug('TYActivityDumplings.update: ',
                    'userId=', userId,
                    'isRanking=',isRanking,
                    'userinfoDictionary=', userinfoDictionary)

        if not isRanking:
            conf = Tool.dictGet(actconf, 'config.activate.credit')
        else:
            conf = Tool.dictGet(actconf, 'config.activate.ranking')
        ftlog.debug('TYActivityDumplings.update: userId=', userId, 'conf=',conf)

        rconf = {"isOK":True}
        userinfoHave = conf.get('userinfoHave',"")
        userinfoRanking = conf.get('userinfoRanking', '')
        userinfoRankingNotFound = conf.get('userinfoRankingNotFound', '')
        userinfoNoHigher = conf.get('userinfoNoHigher', '')
        userinfoHigherRewards = conf.get('userinfoHigherRewards', '')
        userinfoHigherRewards2 = conf.get('userinfoHigherRewards2', '')
        ftlog.debug("TYActivityDumplings.update: userId=", userId,
                    "userinfoHave=", userinfoHave,
                    "userinfoRanking=", userinfoRanking,
                    "userinfoRankingNotFound=", userinfoRankingNotFound,
                    "userinfoNoHigher=", userinfoNoHigher,
                    "userinfoHigherRewards=", userinfoHigherRewards,
                    "userinfoHigherRewards2=", userinfoHigherRewards2)

        rconf.update({
            'userinfoHave': strutil.replaceParams(userinfoHave, userinfoDictionary),
            'userinfoRanking': strutil.replaceParams(userinfoRanking, userinfoDictionary),
            'userinfoHigherRewards': strutil.replaceParams(userinfoHigherRewards, userinfoDictionary)
        })

        ##### 判断是否是第一名,或者第一档奖励
        if userinfoDictionary.get('is_first', False):
            rconf.update({
                'userinfoHigherRewards': strutil.replaceParams(userinfoNoHigher, userinfoDictionary)
            })

        #### 排行未入榜
        if isRanking and userinfoDictionary.get('ranking_num') == None:
            rconf.update({
                'userinfoRanking': userinfoRankingNotFound,
                'userinfoHigherRewards': strutil.replaceParams(userinfoHigherRewards2, userinfoDictionary)
            })
            if userinfoDictionary.get('ranking_higher_score_dv') <= 0:
                rconf.update({ 'userinfoHigherRewards': '' })

        ftlog.debug("TYActivityDumplings.update: ",
                    "userId=", userId,
                    "rconf=", rconf)
        return rconf