# -*- coding:utf-8 -*-
'''
Created on 2018-08-20

@author: wangyonghui
'''
from dizhu.activities_wx.activity_wx import ActivityWx, ActivityWxRegister
import freetime.util.log as ftlog
from dizhu.entity.segment.dizhu_segment_match import SegmentMatchHelper, settlementRanking, UserSegmentDataIssue, getSegmentConf


class ActivityWxSeasonInfo(ActivityWx):
    TYPE_ID = 'ddz.act.wx.seasonInfo'
    ACTION_SEASON_INFO = 'season_info'
    ACTION_SEASON_GET_REWARD = 'season_get_reward'

    def __init__(self):
        super(ActivityWxSeasonInfo, self).__init__()

    def handleRequest(self, userId, clientId, action, msg):
        actId = self.actId
        ret = {}
        if action == self.ACTION_SEASON_INFO:
            ret = SegmentMatchHelper.getSegmentMatchRules()
        elif action == self.ACTION_SEASON_GET_REWARD:
            ret = self.getSeasonReward(userId)
        if ftlog.is_debug():
            ftlog.debug('ActivityWxSeasonInfo.handleRequest',
                        'userId=', userId,
                        'action=', action,
                        'clientId=', clientId,
                        'actId=', actId,
                        'msg=', msg,
                        'ret=', ret)
        return ret

    def hasReward(self, userId):
        ''' 是否有奖励 '''
        latestTwoIssues = SegmentMatchHelper.getIssueStateList()[-2:]
        ret = False
        for issuestate in reversed(latestTwoIssues):
            if issuestate['state'] == 0:
                continue
            # 判断用户有没有结算此赛季
            userData = SegmentMatchHelper.getUserSegmentDataIssue(userId, issuestate['issue']) or UserSegmentDataIssue()
            if userData and userData.segmentRewardsState == UserSegmentDataIssue.IDEAL:
                # 获取奖励
                rewards = getSegmentConf().getSeasonRewards(userData.segment)
                if rewards:
                    return True
        return ret

    def getSeasonReward(self, userId):
        # 检查当前已结束赛季并发放赛季奖励, 只发放上一期的
        latestTwoIssues = SegmentMatchHelper.getIssueStateList()[-2:]
        for issuestate in reversed(latestTwoIssues):
            if issuestate['state'] == 0:
                continue
            # 判断用户有没有结算此赛季
            userData = SegmentMatchHelper.getUserSegmentDataIssue(userId, issuestate['issue']) or UserSegmentDataIssue()
            if userData and userData.segmentRewardsState == UserSegmentDataIssue.IDEAL:
                # 结算 发奖
                assetList, _ = settlementRanking(userId, issuestate['issue'])
                return [{'itemId': atup[0].kindId, 'name':atup[0].displayName, 'url':atup[0].pic, 'count':atup[1]} for atup in assetList] if assetList else []
        return []


def _registerClass():
    ActivityWxRegister.registerClass(ActivityWxSeasonInfo.TYPE_ID, ActivityWxSeasonInfo)