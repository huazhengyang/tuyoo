# -*- coding:utf-8 -*-
'''
Created on 2018-08-20

@author: wangyonghui
'''
from sre_compile import isstring

import datetime

from dizhu.activities_wx.activity_wx import ActivityWx, ActivityWxRegister, ActivityWxHelper, ActivityWxException
import freetime.util.log as ftlog
from dizhu.entity import dizhu_util
from dizhu.entity.common.events import UserShareLoginEvent
from dizhu.entity.dizhuconf import DIZHU_GAMEID
from freetime.entity.msg import MsgPack
from hall.entity.hallconf import HALL_GAMEID
from hall.entity.usercoupon import user_coupon_details
from hall.entity.usercoupon.events import UserCouponReceiveEvent
from poker.entity.biz.content import TYContentItem
from poker.entity.biz.exceptions import TYBizConfException
from poker.entity.dao import daobase, sessiondata, userdata
from poker.protocol import router
from poker.util import strutil
from poker.util import timestamp as pktimestamp

SHARE_CHARM_REWARD_STATE_IDEAL = 0
SHARE_CHARM_REWARD_STATE_GOT = 1


class ShareCharmItem(object):

    def __init__(self):
        self.issue = None
        self.count = 0
        self.state = SHARE_CHARM_REWARD_STATE_IDEAL

    def fromDict(self, d):
        self.issue = d.get('issue')
        self.count = d.get('count', 0)
        self.state = d.get('state')
        return self

    def toDict(self):
        return {
            'issue': self.issue,
            'count': self.count,
            'state': self.state
        }


class UserShareCharmData(object):
    ''' 用户分享魅力数据 '''
    def __init__(self, userId):
        self.userId = userId
        self.timestamp = pktimestamp.getCurrentTimestamp()
        self.isShareLogin = 0
        self.charmList = []

    def loadUserData(self, actId):
        jstr = daobase.executeUserCmd(self.userId, 'hget', 'actwx:%s:%s' % (DIZHU_GAMEID, self.userId), actId)
        if jstr:
            jdict = strutil.loads(jstr)
            self.timestamp = jdict.get('timestamp', pktimestamp.getCurrentTimestamp())
            self.isShareLogin = jdict.get('isShareLogin', 0)
            charmL = jdict.get('charmList', [])
            for charm in charmL:
                self.charmList.append(ShareCharmItem().fromDict(charm))
        return self

    def saveUserData(self, actId):
        self.charmList = self.charmList[-5:]
        jstr = strutil.dumps(self.toDict())
        daobase.executeUserCmd(self.userId, 'hset', 'actwx:%s:%s' % (DIZHU_GAMEID, self.userId), actId, jstr)

    def increaseCharm(self, issue, count):
        for charm in self.charmList:
            if charm.issue == issue:
                charm.count += count
                return charm.count
        shareCharm = ShareCharmItem()
        shareCharm.issue = issue
        shareCharm.count = count
        self.charmList.append(shareCharm)
        return shareCharm.count

    def getCharmCount(self, issue):
        for charm in self.charmList:
            if charm.issue == issue:
                return charm.count
        return 0

    def getIssueData(self, issue):
        for charm in self.charmList:
            if charm.issue == issue:
                return charm
        return None

    def updateState(self, actId, issue):
        for charm in self.charmList:
            if charm.issue == issue:
                charm.state = SHARE_CHARM_REWARD_STATE_GOT
                self.saveUserData(actId)

    def toDict(self):
        return {
            'timestamp': self.timestamp,
            'isShareLogin': self.isShareLogin,
            'charmList': [c.toDict() for c in self.charmList]
        }


class RankRewardItem(object):
    ''' 排行榜奖励 '''
    def __init__(self):
        self.startRank = None
        self.endRank = None
        self.rewardDesc = None
        self.rewardPic = None
        self.rewards = None

    def decodeFromDict(self, d):
        self.startRank = d.get('startRank')
        if not isinstance(self.startRank, int):
            raise TYBizConfException(d, 'RankRewardItem.startRank must be int')

        self.endRank = d.get('endRank')
        if not isinstance(self.endRank, int):
            raise TYBizConfException(d, 'RankRewardItem.endRank must be int')

        self.rewardDesc = d.get('rewardDesc')
        if not isstring(self.rewardDesc):
            raise TYBizConfException(d, 'RankRewardItem.rewardDesc must be str')

        self.rewardPic = d.get('rewardPic')
        if not isstring(self.rewardPic):
            raise TYBizConfException(d, 'RankRewardItem.rewardPic must be str')

        rewards = d.get('rewards')
        if not isinstance(rewards, list):
            raise TYBizConfException(d, 'RankRewardItem.rewards must be list')
        try:
            TYContentItem.decodeList(rewards)
        except Exception, e:
            raise TYBizConfException(d, 'RankRewardItem.rewards must be list err=%s' % e.message)
        self.rewards = rewards
        return self


class ActivityWxShareCharm(ActivityWx):
    TYPE_ID = 'ddz.act.wx.shareCharm'
    ACTION_SHARE_CHARM_RANK_LIST = 'share_charm_rankList'
    ACTION_SHARE_CHARM_REWARD = 'share_charm_reward'

    def __init__(self):
        super(ActivityWxShareCharm, self).__init__()
        self.maxRankNum = None  # 最多记录前N名次用户
        self.rankRewards = None  # 排行榜奖励

    def init(self):
        from dizhu.game import TGDizhu
        TGDizhu.getEventBus().subscribe(UserShareLoginEvent, _processUserShareLoginEvent)

    def cleanup(self):
        from dizhu.game import TGDizhu
        TGDizhu.getEventBus().unsubscribe(UserShareLoginEvent, _processUserShareLoginEvent)

    def handleRequest(self, userId, clientId, action, msg):
        if action == self.ACTION_SHARE_CHARM_RANK_LIST:
            return self.getRankRewardList(userId)
        elif action == self.ACTION_SHARE_CHARM_REWARD:
            # 更改用户领奖状态
            issue = calculateLastIssue(self.settleDayOrWeek)
            realRank = getUserRealRank(userId, self.actId, issue)
            rankRewardItem = self.getUserRankRewardItem(userId, realRank)
            userData = UserShareCharmData(userId).loadUserData(self.actId)
            issueData = userData.getIssueData(issue)

            if not issueData:
                raise ActivityWxException(-6, '您没有参与%s活动哦~' % issue)

            if issueData.state == SHARE_CHARM_REWARD_STATE_GOT:
                raise ActivityWxException(-4, '您已领取奖励哦~')
            # 发奖
            if rankRewardItem:
                userData.updateState(self.actId, issue)
                rewards = rankRewardItem.rewards
                rewardsItems = TYContentItem.decodeList(rewards)
                dizhu_util.sendRewardItems(userId, rewardsItems, '', 'ACT_WX_SHARE_CHARM', self.intActId)
                for reward in rewards:
                    if reward['itemId'] == 'user:coupon':
                        from hall.game import TGHall
                        TGHall.getEventBus().publishEvent(
                            UserCouponReceiveEvent(HALL_GAMEID, userId, reward['count'], user_coupon_details.USER_COUPON_SHARE_CHARM))
                return rewards
            raise ActivityWxException(-5, '您没有奖励可领取哦~')
        return None

    def _decodeFromDictImpl(self, d):
        self.maxRankNum = d.get('maxRankNum')
        if not isinstance(self.maxRankNum, int):
            raise TYBizConfException(d, 'ActivityWxShareCharm.maxRankNum must be int')

        rankRewards = d.get('rankRewards')
        if not isinstance(rankRewards, list):
            raise TYBizConfException(d, 'ActivityWxShareCharm.rankRewards must be list')
        self.rankRewards = [RankRewardItem().decodeFromDict(r) for r in rankRewards]

        settleDayOrWeek = d.get('settleDayOrWeek', 'week')
        if not isstring(settleDayOrWeek) or (settleDayOrWeek not in ['day', 'week']):
            raise TYBizConfException(d, 'ActivityWxShareCharm.settleDayOrWeek must be str and in ["day", "week"]')
        self.settleDayOrWeek = settleDayOrWeek
        if ftlog.is_debug():
            ftlog.debug('ActivityWxShareCharm._decodeFromDictImpl maxRankNum=', self.maxRankNum,
                        'rankRewards=', rankRewards,
                        'settleDayOrWeek=', self.settleDayOrWeek)
        return self

    def getRankRewardList(self, userId):
        ''' 获取奖励排行榜 '''
        ret = []
        for rankReward in self.rankRewards:
            nickname, purl, count = '', '', 0
            startRankUserIdList = getRankList(self.actId, calculateCurrentIssue(self.settleDayOrWeek), rankReward.startRank-1, rankReward.startRank-1)
            if startRankUserIdList:
                startRankUserId = startRankUserIdList[0]
                userdata.checkUserData(startRankUserId)
                nickname, purl = userdata.getAttrs(startRankUserId, ['name', 'purl'])
                issue = calculateCurrentIssue(self.settleDayOrWeek)
                userData = UserShareCharmData(startRankUserId).loadUserData(self.actId)
                issueData = userData.getIssueData(issue)
                count = issueData.count if issueData else 0
            ret.append({
                'startRank': rankReward.startRank,
                'endRank': rankReward.endRank,
                'rewardDesc': rankReward.rewardDesc,
                'rewardPic': rankReward.rewardPic,
                'userInfo': {
                    'name': nickname,
                    'purl': purl,
                    'count': count
                }
            })

        currentIssue = calculateCurrentIssue(self.settleDayOrWeek)
        lastIssue = calculateLastIssue(self.settleDayOrWeek)
        rank = getUserRealRank(userId, self.actId, currentIssue)
        count = UserShareCharmData(userId).loadUserData(self.actId).getCharmCount(currentIssue)
        lastRank = getUserRealRank(userId, self.actId, lastIssue)
        lastCount = UserShareCharmData(userId).loadUserData(self.actId).getCharmCount(lastIssue)

        retRes = {
            'userInfo': {
                'rank': rank,
                'count': count,
                'lastRank': lastRank,
                'lastCount': lastCount
            },
            'rankList': ret,
            'startDate': calculateCurrentIssue(self.settleDayOrWeek),
            'endDate': calculateEndDayStr(self.settleDayOrWeek)
        }
        if ftlog.is_debug():
            ftlog.debug('ActivityWxShareCharm.getRankRewardList',
                        'retRes=', retRes)
        return retRes

    def getUserRankRewardItem(self, userId, rank):
        ''' 获取用户奖励 '''
        for rankReward in self.rankRewards:
            if rankReward.startRank <= rank <= rankReward.endRank:
                if ftlog.is_debug():
                    ftlog.debug('ActivityWxShareCharm.getUserRankRewardItem',
                                'userId=', userId,
                                'rank=', rank,
                                'reward=', rankReward)
                return rankReward
        return None

    def hasReward(self, userId):
        ''' 是否有上期奖励 '''
        issue = calculateLastIssue(self.settleDayOrWeek)
        realRank = getUserRealRank(userId, self.actId, issue)
        rankRewardItem = self.getUserRankRewardItem(userId, realRank)
        userData = UserShareCharmData(userId).loadUserData(self.actId)
        issueData = userData.getIssueData(issue)
        if ftlog.is_debug():
            ftlog.debug('ActivityWxShareCharm.hasReward',
                        'userId=', userId,
                        'issue=', issue,
                        'realRank=', realRank,
                        'rankRewardItem=', rankRewardItem,
                        'state=', issueData.state if issueData else None)
        if rankRewardItem and issueData and issueData.state == SHARE_CHARM_REWARD_STATE_IDEAL:
            return True
        return False


def _registerClass():
    ActivityWxRegister.registerClass(ActivityWxShareCharm.TYPE_ID, ActivityWxShareCharm)


# 数据库Key管理, Reply 库
def buildRankListKey(actId, issue):   # 排行榜
    return 'actwx.%s.rankList:%s:%s' % (actId, DIZHU_GAMEID, issue)


def insertRankList(actId, issue, userId, shareCharm, rankLimit=500):
    ''' 插入排行榜 '''
    assert (rankLimit > 0)
    try:
        key = buildRankListKey(actId, issue)
        if daobase.executeRePlayCmd('EXISTS', key):
            if ftlog.is_debug():
                ftlog.debug('activity_wx_share_charm.insertRankList userId=', userId,
                            'actId=', actId,
                            'key=', key,
                            'exists=', 1)
            daobase.executeRePlayCmd('ZADD', key, shareCharm, userId)
        else:
            daobase.executeRePlayCmd('ZADD', key, shareCharm, userId)
            daobase.executeRePlayCmd('EXPIRE', key, 86400 * 30)
            if ftlog.is_debug():
                ftlog.debug('activity_wx_share_charm.insertRankList userId=', userId,
                            'actId=', actId,
                            'key=', key,
                            'exists=', 0)
        removed = daobase.executeRePlayCmd('ZREMRANGEBYRANK', str(key), 0, -rankLimit - 1)
        if ftlog.is_debug():
            ftlog.debug('activity_wx_share_charm.insertRankList',
                        'userId=', userId,
                        'issue=', issue,
                        'shareCharm=', shareCharm,
                        'rankLimit=', rankLimit,
                        'removed=', removed)
    except Exception, e:
        ftlog.error('activity_wx_share_charm.insertRankList',
                    'userId=', userId,
                    'issue=', issue,
                    'shareCharm=', shareCharm,
                    'rankLimit=', rankLimit,
                    'err=', e.message)


def getRankList(actId, issue, start, stop):
    '''获取排行榜前N名的用户信息'''
    key = buildRankListKey(actId, issue)
    return daobase.executeRePlayCmd('ZREVRANGE', key, start, stop)


def getUserRealRank(userId, actId, issue):
    ''' 获取实时排名 '''
    userIds = getRankList(actId, issue, 0, -1)
    for rank, uId in enumerate(userIds, 1):
        if uId == userId:
            return rank
    return -1


def calculateCurrentIssue(settleDayOrWeek='week'):
    ''' 计算当前期号 '''
    if settleDayOrWeek == 'day':
        now = datetime.datetime.now()
        return now.strftime('%Y%m%d')
    else:
        now = datetime.datetime.now()
        thisWeekStart = now - datetime.timedelta(days=now.weekday())
        return thisWeekStart.strftime('%Y%m%d')


def calculateEndDayStr(settleDayOrWeek='week'):
    ''' 计算当前期号最后一天 '''
    if settleDayOrWeek == 'day':
        now = datetime.datetime.now()
        return now.strftime('%Y%m%d')
    else:
        now = datetime.datetime.now()
        thisWeekStart = now - datetime.timedelta(days=now.weekday())
        thisWeekEnd = thisWeekStart + datetime.timedelta(days=6)
        return thisWeekEnd.strftime('%Y%m%d')


def calculateLastIssue(settleDayOrWeek='week'):
    ''' 计算上一期号 '''
    if settleDayOrWeek == 'day':
        now = datetime.datetime.now()
        lastDayStart = now - datetime.timedelta(days=1)
        return lastDayStart.strftime('%Y%m%d')
    else:
        now = datetime.datetime.now()
        lastWeekStart = now - datetime.timedelta(days=now.weekday() + 7)
        return lastWeekStart.strftime('%Y%m%d')


def _processUserShareLoginEvent(evt):
    _processUserShareLoginEventImpl(evt)


def _processUserShareLoginEventImpl(evt):
    clientId = sessiondata.getClientId(evt.shareUserId)
    actList = ActivityWxHelper.getActivityList(evt.shareUserId, clientId)
    if ftlog.is_debug():
        ftlog.debug('activity_wx_share_charm._processUserShareLoginEventImpl',
                    'userId=', evt.userId,
                    'shareUserId=', evt.shareUserId,
                    'actList=', actList)
    for act in actList:
        if act['typeId'] == ActivityWxShareCharm.TYPE_ID:
            actId = act['actId']
            actInstance = ActivityWxHelper.findActivity(actId)
            if actInstance:
                if ftlog.is_debug():
                    ftlog.debug('activity_wx_share_charm._processUserShareLoginEventImpl',
                                'userId=', evt.userId,
                                'shareUserId=', evt.shareUserId,
                                'actInstance=', actInstance)
                # 判断用户是否已经帮助过别人了
                timestamp = pktimestamp.getCurrentTimestamp()
                userData = UserShareCharmData(evt.userId).loadUserData(actId)
                saveUserData = False
                if not pktimestamp.is_same_day(userData.timestamp, timestamp):
                    userData.timestamp = timestamp
                    userData.isShareLogin = 0
                    saveUserData = True

                if userData.isShareLogin == 0:
                    # 获取当前期号
                    shareUserData = UserShareCharmData(evt.shareUserId).loadUserData(actId)
                    currentIssue = calculateCurrentIssue(actInstance.settleDayOrWeek)
                    # 增加魅力值
                    totalCount = shareUserData.increaseCharm(currentIssue, 1)
                    shareUserData.saveUserData(actId)
                    # 插入排行榜
                    insertRankList(actId, currentIssue, evt.shareUserId, totalCount, actInstance.maxRankNum)

                    # 更新帮助用户信息
                    userData.isShareLogin = 1
                    saveUserData = True

                if saveUserData:
                    userData.saveUserData(actId)
                    name, _ = userdata.getAttrs(evt.shareUserId, ['name', 'purl'])
                    mo = MsgPack()
                    mo.setCmd('act_wx')
                    mo.setResult('action', 'share_charm_login')
                    mo.setResult('loginMsg', '感谢您帮助【%s】增加1点魅力值哦~' % name)
                    router.sendToUser(mo, evt.userId)

                    if ftlog.is_debug():
                        ftlog.debug('activity_wx_share_charm._processUserShareLoginEventImpl',
                                    'userId=', evt.userId,
                                    'shareUserId=', evt.shareUserId,
                                    'mo=', mo)
