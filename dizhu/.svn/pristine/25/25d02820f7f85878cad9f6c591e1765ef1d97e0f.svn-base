# -*- coding:utf-8 -*-
'''
Created on 2018年4月15日

@author: wangyonghui
'''
from sre_compile import isstring

from dizhu.entity.dizhuconf import DIZHU_GAMEID
from dizhu.entity.segment.dizhu_segment_match import SegmentMatchHelper, getSegmentConf
from dizhu.entity.segment.watch_ad import WatchAdHelper
from dizhu.game import TGDizhu
from dizhu.games.segmentmatch.events import SegmentRecoverEvent
from freetime.entity.msg import MsgPack
from hall.servers.common.base_checker import BaseMsgPackChecker
from hall.servers.util.rpc import user_remote
from poker.protocol import router
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod
from poker.entity.configure import configure
from poker.util import timestamp as pktimestamp
import freetime.util.log as ftlog


@markCmdActionHandler
class SegmentMatchHandler(BaseMsgPackChecker):
    def __init__(self):
        super(SegmentMatchHandler, self).__init__()

    def _check_param_issue(self, msg, key, params):
        issue = msg.getParam(key, '')
        if isstring(issue):
            return None, issue
        return 'ERROR of issue !' + str(issue), None

    def _check_param_adId(self, msg, key, params):
        adId = msg.getParam(key, '')
        if isstring(adId):
            return None, adId
        return 'ERROR of adId !' + str(adId), None

    def _check_param_start(self, msg, key, params):
        start = msg.getParam(key)
        if isinstance(start, int):
            start = max(1, start)
            return None, start
        return None, 1

    def _check_param_stop(self, msg, key, params):
        stop = msg.getParam(key)
        if isinstance(stop, int):
            return None, stop
        return None, 100

    def _check_param_preIssue(self, msg, key, params):
        preIssue = msg.getParam(key)
        if isinstance(preIssue, int):
            return None, preIssue
        return None, 0

    @markCmdActionMethod(cmd='dizhu', action='segment_info', clientIdVer=0, lockParamName='', scope='game')
    def doSegmentInfo(self, userId, gameId, clientId, issue=''):
        msg = self._get_segment_info(userId, gameId, clientId, issue)
        router.sendToUser(msg, userId)

    @classmethod
    def _get_segment_info(cls, userId, gameId, clientId, issue):
        segmentInfo = SegmentMatchHelper.getUserSegmentInfo(userId, issue)
        msg = MsgPack()
        msg.setCmd('dizhu')
        msg.setResult('action', 'segment_info')
        msg.setResult('gameId', gameId)
        msg.setResult('userId', userId)
        msg.setResult('clientId', clientId)
        msg.setResult('segmentInfo', segmentInfo)
        return msg


    @markCmdActionMethod(cmd='dizhu', action='segment_rank_list', clientIdVer=0, lockParamName='', scope='game')
    def doSegmentRankList(self, userId, gameId, clientId, start, stop, preIssue):
        msg = self._get_segment_rank_list(userId, gameId, clientId, start, stop, preIssue)
        router.sendToUser(msg, userId)

    @classmethod
    def _get_segment_rank_list(cls, userId, gameId, clientId, start, stop, preIssue):
        rankList = []
        rank = -1
        issues = SegmentMatchHelper.getIssueStateList()
        if issues:
            if preIssue:
                if len(issues) > 1:
                    rankList, start, stop = SegmentMatchHelper.getSegmentRankList(issues[-2]['issue'], start, stop)
                    rank = SegmentMatchHelper.getUserRealRank(userId, issues[-2]['issue'])
                else:
                    pass
            else:
                rankList, start, stop = SegmentMatchHelper.getSegmentRankList(issues[-1]['issue'], start, stop)
                rank = SegmentMatchHelper.getUserRealRank(userId, issues[-1]['issue'])

        if ftlog.is_debug():
            ftlog.debug('SegmentMatchHandler._get_segment_rank_list',
                        'userId=', userId,
                        'gameId=', gameId,
                        'clientId=', clientId,
                        'start=', start,
                        'stop=', stop,
                        'preIssue=', preIssue,
                        'issues=', issues,
                        'rankList=', rankList)

        msg = MsgPack()
        msg.setCmd('dizhu')
        msg.setResult('action', 'segment_rank_list')
        msg.setResult('gameId', gameId)
        msg.setResult('userId', userId)
        msg.setResult('clientId', clientId)
        msg.setResult('rankList', rankList)
        msg.setResult('preIssue', preIssue)
        msg.setResult('rank', rank)
        msg.setResult('start', start)
        msg.setResult('stop', stop)
        return msg

    @markCmdActionMethod(cmd='dizhu', action='segment_rules', clientIdVer=0, lockParamName='', scope='game')
    def doGetSegmentMatchRules(self, userId, gameId, clientId):
        msg = self._get_segment_rules(userId, gameId, clientId)
        router.sendToUser(msg, userId)

    @classmethod
    def _get_segment_rules(cls, userId, gameId, clientId):
        rules = SegmentMatchHelper.getSegmentMatchRules()
        msg = MsgPack()
        msg.setCmd('dizhu')
        msg.setResult('action', 'segment_rules')
        msg.setResult('gameId', gameId)
        msg.setResult('userId', userId)
        msg.setResult('clientId', clientId)
        msg.setResult('rules', rules)
        return msg

    @markCmdActionMethod(cmd='dizhu', action='segment_recover', clientIdVer=0, lockParamName='', scope='game')
    def doGetSegmentMatchRecover(self, userId, gameId, clientId):
        msg = self._segment_recover(userId, gameId, clientId)
        router.sendToUser(msg, userId)

    @classmethod
    def _segment_recover(cls, userId, gameId, clientId):
        # 段位复活数据
        errmsg = '你的保段复活费用不足'
        success = 0
        userRecoverData = SegmentMatchHelper.getUserSegmentRecoverData(userId)
        if userRecoverData.active:
            totalRecoverCount = userRecoverData.totalRecoverCount
            recoverConf = getSegmentConf().segmentRecover
            others = recoverConf.get('buy', {}).get('itemCount', {}).get('others', 10)
            needCount = recoverConf.get('buy', {}).get('itemCount', {}).get(str(totalRecoverCount), others)
            itemId = recoverConf.get('buy', {}).get('itemId')
            # 判断用户参赛券否够
            contentItemList = [{'itemId': itemId, 'count': needCount}]
            assetKindId, count = user_remote.consumeAssets(DIZHU_GAMEID, userId, contentItemList,
                                                           'SEGMENT_MATCH_RECOVER_FEE', 0)

            ftlog.info('SegmentMatchHandler.collectFee',
                       'userId=', userId,
                       'fees=', contentItemList,
                       'assetKindId=', assetKindId,
                       'count=', count)

            if not assetKindId:
                errmsg = 'ok'
                success = 1
                # 广播事件
                TGDizhu.getEventBus().publishEvent(SegmentRecoverEvent(userId, gameId))

        msg = MsgPack()
        msg.setCmd('dizhu')
        msg.setResult('action', 'segment_recover')
        msg.setResult('gameId', gameId)
        msg.setResult('userId', userId)
        msg.setResult('success', success)
        msg.setResult('errmsg', errmsg)

        if ftlog.is_debug():
            ftlog.debug('SegmentMatchHandler._segment_recover'
                        'userId=', userId,
                        'gameId=', gameId,
                        'clientId=', clientId,
                        'userRecoverData=', userRecoverData.toDict(),
                        'msg=', msg._ht)

        return msg

    @markCmdActionMethod(cmd='dizhu', action='watch_ad', clientIdVer=0, lockParamName='', scope='game')
    def doWatchAd(self, userId, gameId, adId, clientId):
        msg = self._do_watch_ad(userId, gameId, adId, clientId)
        router.sendToUser(msg, userId)

    @classmethod
    def _do_watch_ad(cls, userId, gameId, adId, clientId):

        msg = MsgPack()
        msg.setCmd('dizhu')
        msg.setResult('action', 'watch_ad')
        msg.setResult('gameId', gameId)
        msg.setResult('userId', userId)
        msg.setResult('clientId', clientId)
        msg.setResult('adId', adId)
        reward, leftWatchAdCount = WatchAdHelper.sendWatchAdRewards(userId, adId)
        msg.setResult('reward', reward)
        msg.setResult('leftWatchAdCount', leftWatchAdCount)
        if ftlog.is_debug():
            ftlog.debug('SegmentMatchHandler._do_watch_ad'
                        'userId=', userId,
                        'gameId=', gameId,
                        'clientId=', clientId,
                        'msg=', msg._ht)
        return msg

    @markCmdActionMethod(cmd='dizhu', action='ad_info', clientIdVer=0, lockParamName='', scope='game')
    def doAdInfo(self, userId, gameId, clientId):
        msg = self._do_ad_info(userId, gameId, clientId)
        router.sendToUser(msg, userId)

    @classmethod
    def _do_ad_info(cls, userId, gameId, clientId):
        msg = MsgPack()
        msg.setCmd('dizhu')
        msg.setResult('action', 'ad_info')
        msg.setResult('gameId', gameId)
        msg.setResult('userId', userId)
        msg.setResult('clientId', clientId)
        msg.setResult('leftWatchAdCount', WatchAdHelper.getUserLeftWatchAdCount(userId))
        msg.setResult('adCDMinutes', WatchAdHelper.getCDMinutes())
        if ftlog.is_debug():
            ftlog.debug('SegmentMatchHandler.ad_info'
                        'userId=', userId,
                        'gameId=', gameId,
                        'clientId=', clientId,
                        'msg=', msg._ht)
        return msg

    @markCmdActionMethod(cmd='dizhu', action='coupon_withdraw', clientIdVer=0, lockParamName='', scope='game')
    def doGetCouponWithdraw(self, userId, gameId, clientId):
        msg = self._withdrawConf(userId, gameId, clientId)
        router.sendToUser(msg, userId)

    @classmethod
    def _withdrawConf(cls, userId, gameId, clientId):
        from hall.entity.hallusercond import UserConditionRegister
        withdrawAmount = 5
        condList = getWithdrawConf().get('withdrawAmount')
        for conditon in condList:
            conD = conditon.get('conditions')
            cond = UserConditionRegister.decodeFromDict(conD)
            retCheck = cond.check(DIZHU_GAMEID, userId, clientId, pktimestamp.getCurrentTimestamp())
            if retCheck:
                withdrawAmount = conditon.get('amount')
                break
        openTimeList = getWithdrawConf().get('openTimeList', [])
        openTimeDesc = getWithdrawConf().get('openTimeDesc', '')
        msg = MsgPack()
        msg.setCmd('dizhu')
        msg.setResult('openTimeList', openTimeList)
        msg.setResult('openTimeDesc', openTimeDesc)
        msg.setResult('action', 'coupon_withdraw')
        msg.setResult('withdrawAmount', withdrawAmount)
        if ftlog.is_debug():
            ftlog.debug('SegmentMatchHandler._withdrawConf',
                       'userId=', userId,
                       'withdrawAmount=', withdrawAmount)
        return msg


def getWithdrawConf():
    return configure.getGameJson(6, 'match.withdraw', {})