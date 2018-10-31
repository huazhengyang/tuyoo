# -*- coding=utf-8 -*-
'''
Created on 2018年8月23日

@author: wangyonghui
'''
from dizhu.activities_wx.activity_wx import ActivityWxHelper, ActivityWxException
from dizhu.activities_wx.activity_wx_share_charm import getUserRealRank, calculateLastIssue, UserShareCharmData, insertRankList, SHARE_CHARM_REWARD_STATE_GOT
from dizhu.entity import dizhu_util
from freetime.entity.msg import MsgPack
from hall.servers.common.base_http_checker import BaseHttpMsgChecker
from poker.protocol import runhttp
from poker.protocol.decorator import markHttpHandler, markHttpMethod


@markHttpHandler
class TestDiZhuActWxShareCharmHttpHandler(BaseHttpMsgChecker):
    def __init__(self):
        pass

    def _check_param_issue(self, key, params):
        try:
            issue = runhttp.getParamStr(key)
            return None, issue
        except:
            return 'the issue params is not a str Format !!', None

    def _check_param_actId(self, key, params):

        try:
            actId = runhttp.getParamStr(key)
            return None, actId
        except:
            return 'the actId params is not a str Format !!', None

    def _check_param_shareUserId(self, key, params):
        shareUserId = runhttp.getParamInt(key)
        if isinstance(shareUserId, int):
            return None, shareUserId
        return 'ERROR of shareUserId !' + str(shareUserId), None

    def _check_param_count(self, key, params):
        count = runhttp.getParamInt(key)
        if isinstance(count, int):
            return None, count
        return 'ERROR of count !' + str(count), None

    def _check_param_isTest(self, key, params):
        isTest = runhttp.getParamInt(key)
        if isinstance(isTest, int):
            return None, isTest
        return 'ERROR of isTest !' + str(isTest), None

    @markHttpMethod(httppath='/gtest/dizhu/actwx/sharecharm/list')
    def doGetShareCharmList(self, userId):
        errCode = 0
        errMsg = None
        result = None
        try:
            result = ActivityWxHelper.handleActivityRequest(userId, '', 'shareCharm', 'share_charm_rankList', {})
        except ActivityWxException as e:
            errCode, errMsg = e.errCode, e.errMsg
        mo = MsgPack()
        mo.setCmd('act_wx')
        mo.setResult('action', 'share_charm_rankList')
        mo.setResult('userId', userId)
        mo.setResult('actId', 'shareCharm')
        mo.setResult('gameId', 6)
        mo.setResult('errcode', errCode)
        mo.setResult('errmsg', errMsg)
        mo.setResult('result', result)
        return mo

    @markHttpMethod(httppath='/gtest/dizhu/actwx/sharecharm/add')
    def doShareCharmAdd(self, userId, issue, count):
        # 增加魅力值
        act = ActivityWxHelper.findActivity('shareCharm')
        if act:
            userData = UserShareCharmData(userId).loadUserData(act.actId)
            totalCount = userData.increaseCharm(issue, count)
            userData.saveUserData(act.actId)
            # 插入排行榜
            insertRankList(act.actId, issue, userId, totalCount, act.maxRankNum)

        mo = MsgPack()
        mo.setCmd('act_wx')
        mo.setResult('action', 'share_charm_add')
        mo.setResult('userId', userId)
        mo.setResult('actId', 'shareCharm')
        mo.setResult('gameId', 6)
        mo.setResult('issue', issue)
        mo.setResult('count', count)
        return mo

    @markHttpMethod(httppath='/gtest/dizhu/actwx/sharecharm/reward')
    def doShareCharmReward(self, userId, isTest):
        errCode = 0
        errMsg = None
        rewards = []
        try:
            act = ActivityWxHelper.findActivity('shareCharm')
            if act:
                # 更改用户领奖状态
                issue = calculateLastIssue(isTest)
                realRank = getUserRealRank(userId, act.actId, issue)
                rankRewardItem = act.getUserRankRewardItem(userId, realRank)
                userData = UserShareCharmData(userId).loadUserData(act.actId)
                issueData = userData.getIssueData(issue)
                if not issueData:
                    raise ActivityWxException(-6, '您没有参与%s活动哦~' % issue)

                if issueData.state == SHARE_CHARM_REWARD_STATE_GOT:
                    raise ActivityWxException(-4, '您已领取奖励哦~')
                # 发奖
                if rankRewardItem:
                    userData.updateState(act.actId, issue)
                    rewards = rankRewardItem.rewards
                    dizhu_util.sendRewardItems(userId, rewards, '', 'ACT_WX_SHARE_CHARM', act.intActId)
                else:
                    raise ActivityWxException(-5, '您没有奖励可领取哦~')
        except ActivityWxException as e:
            errCode, errMsg = e.errCode, e.errMsg
        mo = MsgPack()
        mo.setCmd('act_wx')
        mo.setResult('action', 'share_charm_rankList')
        mo.setResult('userId', userId)
        mo.setResult('actId', 'shareCharm')
        mo.setResult('gameId', 6)
        mo.setResult('errcode', errCode)
        mo.setResult('errmsg', errMsg)
        mo.setResult('result', [{'itemId': r.assetKindId, 'count': r.count} for r in rewards])
        return mo
