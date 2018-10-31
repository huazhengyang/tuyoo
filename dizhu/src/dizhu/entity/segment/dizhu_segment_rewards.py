# -*- coding:utf-8 -*-
'''
Created on 2018-04-16

@author: wangyonghui
'''
import freetime.util.log as ftlog
from dizhu.entity.segment.dao import segmentdata
from dizhu.entity.segment.dizhu_segment_match import settlementRanking, SegmentMatchHelper, UserSegmentDataIssue
from dizhu.entity.dizhuconf import DIZHU_GAMEID
from dizhu.entity.segment.dizhu_segment_usercond import UserConditionSegmentWinDoubles, UserConditionSegmentChuntian
from hall.entity.hallusercond import UserConditionRegister
from hall.entity.todotask import TodoTask
from hall.game import TGHall
from hall.servers.util.rpc import user_remote
from poker.entity.biz.content import TYContentItem
from poker.entity.biz.message import message
from poker.entity.dao import gamedata, sessiondata, userdata
from poker.entity.events.tyevent import EventUserLogin
from dizhu.entity.segment.dizhu_segment_match import getSegmentConf
from poker.util import timestamp as pktimestamp


class DizhuSegmentRewardsHelper(object):
    def __init__(self):
        pass

    @classmethod
    def processEnterGame(cls, evt):
        # # 检查当前已结束赛季并发放赛季奖励, 只发放上一期的
        if ftlog.is_debug():
            ftlog.debug('============= processEnterGame userId=', evt.userId)
        _, intClientId = sessiondata.getClientIdNum(evt.userId)
        if intClientId == 24105:
            latestTwoIssues = SegmentMatchHelper.getIssueStateList()[-2:]
            for issuestate in reversed(latestTwoIssues):
                if issuestate['state'] == 0:
                    continue

                # 判断用户有没有结算此赛季
                userData = SegmentMatchHelper.getUserSegmentDataIssue(evt.userId, issuestate['issue']) or UserSegmentDataIssue()
                if userData and userData.segmentRewardsState == UserSegmentDataIssue.IDEAL:
                    # 结算 发奖
                    settlementRanking(evt.userId, issuestate['issue'])

        segmentConf = getSegmentConf()
        if segmentConf.closed:
            return

        if evt.dayFirst:
            # 检查用户是否已经发送
            if not gamedata.getGameAttrInt(evt.userId, DIZHU_GAMEID, 'wxNotice'):
                # 保存消息记录
                gamedata.setGameAttr(evt.userId, DIZHU_GAMEID, 'wxNotice', 1)

                # 新用户发送一条额外消息
                mailstr = '游戏公告#如有任何意见建议,欢迎加客服微信:Tuyoo_taozi,进入官方群反馈'
                message.send(DIZHU_GAMEID, message.MESSAGE_TYPE_SYSTEM, evt.userId, mailstr)

        # 同步钻石为用户道具
        if not segmentdata.getSegmentAttr(evt.userId, DIZHU_GAMEID, 'diamondConvert'):
            segmentdata.setSegmentAttr(evt.userId, DIZHU_GAMEID, 'diamondConvert', 1)
            userDiamond = userdata.getAttr(evt.userId, 'diamond')
            if userDiamond:
                # count
                user_remote.consumeAssets(DIZHU_GAMEID, evt.userId, [{'itemId': 'user:diamond', 'count': userDiamond}],
                                          'DIZHU_SEGMENT_DIAMOND_CONVERT', 0)
                contentItems = TYContentItem.decodeList([{'itemId': 'item:1311', 'count': userDiamond}])
                from dizhu.entity import dizhu_util
                dizhu_util.sendRewardItems(evt.userId, contentItems, None, 'DIZHU_SEGMENT_DIAMOND_CONVERT', 0)
                ftlog.info('DizhuSegmentRewardsHelper diamondConvert userId=', evt.userId,
                           'userDiamond=', userDiamond)

        # 发送10000金币，此处
        # if not segmentdata.getSegmentAttr(evt.userId, DIZHU_GAMEID, 'initChip'):
        #     segmentdata.setSegmentAttr(evt.userId, DIZHU_GAMEID, 'initChip', 1)
        #     contentItems = TYContentItem.decodeList([{'itemId': 'user:chip', 'count': 10000}])
        #     from dizhu.entity import dizhu_util
        #     dizhu_util.sendRewardItems(evt.userId, contentItems, None, 'DIZHU_LOGIN_INIT_CHIP', 0)
        #     ftlog.info('DizhuSegmentRewardsHelper initChip userId=', evt.userId,
        #                'chip=', 10000)

    @classmethod
    def processUserTableRewards(cls, userId, winlose):
        ''' 处理牌局结束用户的奖励 '''
        gameWinRewardConf = getSegmentConf().gameWinReward
        # 判断condition
        condList = gameWinRewardConf.get('conditions')
        if condList and winlose.isWin:
            for condD in condList:
                cond = UserConditionRegister.decodeFromDict(condD)
                clientId = sessiondata.getClientId(userId)
                retCheck = cond.check(DIZHU_GAMEID, userId, clientId, pktimestamp.getCurrentTimestamp(), winlose=winlose)
                if retCheck:
                    reward = gameWinRewardConf.get('reward')
                    if reward:
                        try:
                            contentItems = TYContentItem.decodeList([reward])
                            from dizhu.entity import dizhu_util
                            dizhu_util.sendRewardItems(userId, contentItems, None, 'DIZHU_SEGMENT_TABLE_WIN', 0)
                            ret = SegmentMatchHelper.addUserSegmentTableWinRewardCount(userId, reward['count'])
                            if ret:
                                retMsg = ''
                                if cond.TYPE_ID == UserConditionSegmentWinDoubles.TYPE_ID:
                                    retMsg = '满贯'
                                elif cond.TYPE_ID == UserConditionSegmentChuntian.TYPE_ID:
                                    retMsg = '春天'
                                retReward = {
                                    'itemId': reward['itemId'],
                                    'count': reward['count'],
                                    'des': retMsg
                                }
                                ftlog.info('DizhuSegmentRewardsHelper.processUserTableRewards',
                                           'userId=', userId,
                                           'typeId=', cond.TYPE_ID,
                                           'reward=', retReward)
                                return retReward
                            else:
                                return None
                        except Exception, e:
                            ftlog.error('DizhuSegmentRewardsHelper.processUserTableRewards',
                                        'userId=', userId,
                                        'gameWinRewardConf=', gameWinRewardConf,
                                        'errmsg=', e.message)
        return None


_inited = False
def _initialize():
    global _inited
    if not _inited:
        _inited = True
        TGHall.getEventBus().subscribe(EventUserLogin, DizhuSegmentRewardsHelper.processEnterGame)
        if ftlog.is_debug():
            ftlog.debug('DizhuSegmentRewardsHelper.processUserTableRewards inited ok.')


class TodoTaskShowSegmentRewards(TodoTask):
    def __init__(self, rewards, rewardType):
        super(TodoTaskShowSegmentRewards, self).__init__('show_rewards')
        self.setParam('rewards', rewards)
        self.setParam('type', rewardType)
