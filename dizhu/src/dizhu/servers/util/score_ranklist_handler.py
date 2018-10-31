# -*- coding:utf-8 -*-
'''
Created on 2017年7月2日

@author: zhaojiangang
'''
from sre_compile import isstring

from dizhu.entity import dizhu_score_ranking
from dizhu.entity.dizhu_score_ranking import RewardState
from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from hall.entity import hallitem
from hall.servers.common.base_checker import BaseMsgPackChecker
from poker.entity.biz.exceptions import TYBizException
from poker.protocol import router
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod
import poker.util.timestamp as pktimestamp


class RankListCache(object):
    ST_NO_LOAD = 0
    ST_LOADING = 1
    ST_LOADED = 2
    
    def __init__(self, rankId, issueNum, rankLimit, refreshInterval):
        self._rankId = rankId
        self._issueNum = issueNum
        self._rankLimit = rankLimit
        self._refreshInterval = refreshInterval
        self._rankList = []
        self._lastUpdateTime = 0
        self._state = RankListCache.ST_NO_LOAD
    
    def getRankList(self, timestamp):
        if self._state == RankListCache.ST_LOADED:
            if self._needRefresh(timestamp):
                self._state = RankListCache.ST_NO_LOAD

        if self._state == RankListCache.ST_NO_LOAD:
            self._state = RankListCache.ST_LOADING
            self._rankList = self._loadRankList()
            self._state = RankListCache.ST_LOADED
            self._lastUpdateTime = timestamp
            ftlog.info('getRankList reloadOk',
                       'rankId=', self._rankId,
                       'issueNum=', self._issueNum,
                       'timestamp=', timestamp,
                       'rankLen=', len(self._rankList))
        return self._rankList
    
    def _needRefresh(self, timestamp):
        curIssueNum = dizhu_score_ranking.calcIssueNum(timestamp)
        lastUpdateIssueNum = dizhu_score_ranking.calcIssueNum(self._lastUpdateTime)
        
        if ftlog.is_debug():
            ftlog.debug('RankListCache._needRefresh',
                        'rankId=', self._rankId,
                        'issueNum=', self._issueNum,
                        'timestamp=', timestamp,
                        'curIssueNum=', curIssueNum,
                        'lastUpdateIssueNum=', lastUpdateIssueNum)
            
        if (dizhu_score_ranking.compareIssueNum(curIssueNum, self._issueNum) > 0
            and (dizhu_score_ranking.compareIssueNum(lastUpdateIssueNum, self._issueNum) > 0)):
            # 本cache是过期的期号，并且最后从数据库读数据的时间也是过期后的时间
            return False
            
        return timestamp - self._lastUpdateTime >= self._refreshInterval
    
    def _loadRankList(self):
        ret = []
        try:
            userScoreList = dizhu_score_ranking.getRanklistWithScore(self._rankId, self._issueNum, 0, self._rankLimit - 1)
            for i, (userId, score) in enumerate(userScoreList):
                userData = dizhu_score_ranking.loadUserData(userId, self._rankId, self._issueNum)
                userName = purl = ''
                if userData:
                    userName = userData.name
                    purl = userData.purl
                ret.append((userId, score, i + 1, userName, purl))
        except:
            ftlog.error('_loadRankList',
                        'rankId=', self._rankId,
                        'issueNum=', self._issueNum)
        return ret


class RankListManager(object):
    def __init__(self, rankLimit, refreshInterval):
        self.rankLimit = rankLimit
        self.refreshInterval = refreshInterval
        # key=(rankId, issueNum), value=RankListCache
        self._cacheMap = {}
    
    def getRankList(self, rankId, issueNum, timestamp):
        '''
        @param timestamp: 当前时间
        '''
        # 从缓存读取
        key = (rankId, issueNum)
        cacheRank = self._cacheMap.get(key)
        if not cacheRank:
            if ftlog.is_debug():
                ftlog.debug('rankMng.getRankList getRankList rankId=', rankId, 'issueNum=', issueNum, 'timestamp=', timestamp)
            cacheRank = RankListCache(rankId, issueNum, self.rankLimit, self.refreshInterval)
            self._cacheMap[key] = cacheRank
        if ftlog.is_debug():
            ftlog.debug('rankMng.getRankList cacheRank.getRankList(timestamp)=', cacheRank.getRankList(timestamp),
                        'issueNum=', issueNum,
                        'timestamp=', timestamp)
        return cacheRank.getRankList(timestamp)


@markCmdActionHandler
class ScoreRankingHandler(BaseMsgPackChecker):
    # conf = dizhu_score_ranking.getConf()
    # rankMng = RankListManager(conf.cacheCount, conf.refreshInterval)
    rankMng = RankListManager(500, 10)

    def _check_param_rankId(self, msg, key, params):
        rankId = msg.getParam(key)
        if isstring(rankId):
            return None, rankId
        return 'ERROR of rankId !' + str(rankId), None
    
    def _check_param_issueNum(self, msg, key, params):
        issueNum = msg.getParam('issn')
        if isstring(issueNum):
            return None, issueNum
        return 'ERROR of issueNum !' + str(issueNum), None

    def _check_param_isDibao(self, msg, key, params):
        isDibao = msg.getParam('isDibao')
        if isinstance(isDibao, int):
            return None, isDibao
        return 'ERROR of isDibao !' + str(isDibao), None

    def _check_param_start(self, msg, key, params):
        start = msg.getParam('start')
        if isinstance(start, int):
            start = max(1, start)
            return None, start
        return None, 1

    def _check_param_end(self, msg, key, params):
        end = msg.getParam('end')
        if isinstance(end, int):
            end = max(100, end)
            return None, end
        return None, 100
    
    @classmethod
    def buildDibaoInfo(cls, rankingDefine, userData):
        if rankingDefine.dibaoConf:
            return {
                'state':userData.dibaoRewardState,
                'score':rankingDefine.dibaoConf.score,
                'plays':rankingDefine.dibaoConf.playCount,
                'desc':rankingDefine.dibaoConf.desc,
                'img':rankingDefine.dibaoConf.img
            }
        return None

    @classmethod
    def buildRewards(cls, items):
        ret = []
        for item in items:
            if ftlog.is_debug():
                ftlog.debug('score_ranklist_handler buildRewards item=', item)
            assetKind = hallitem.itemSystem.findAssetKind(item['itemId'])
            ret.append({
                'itemId': item['itemId'],
                'name': assetKind.displayName if assetKind else '',
                'count': item['count'],
                'img': assetKind.pic if assetKind else ''
            })
        return ret
        
    @classmethod
    def buildCurRank(cls, rankingDefine, issueNum, clientId, timestamp):
        ret = []
        rankList = cls.rankMng.getRankList(rankingDefine.rankId, issueNum, timestamp)
        rankRewardsConf = dizhu_score_ranking.getRankRewardsConf(rankingDefine.rankId, issueNum, clientId)
        if not rankRewardsConf:
            ftlog.error('ScoreRankingHandler.buildCurRank NotConfRankRewards',
                        'rankId=', rankingDefine.rankId,
                        'issueNum=', issueNum,
                        'clientId=', clientId)
            return ret
        
        defaultUserName = u"虚位以待"
        for rankReward in rankRewardsConf:
            rank = rankReward.get('begin')
            if rank is None:
                break

            rewardItems = cls.buildRewards(rankReward.get('items'))
            userName = defaultUserName
            rankUserScore = 0
            if len(rankList) >= rank:
                rankListItem = rankList[rank - 1]
                # userId, score, i + 1, userName, purl
                rankUserScore = rankListItem[1]
                userName = rankListItem[3]
            ret.append({
                'start':rank,
                'end':rankReward.get('end'),
                'userName':userName,
                'userScore':rankUserScore,
                'desc':rankReward.get('desc', ''),
                'cash':rankReward.get('cash', 0),
                'img':rankReward.get('img', '') if rewardItems else ''
            })
        return ret
    
    @classmethod
    def buildFameHall(cls, fameHall):
        ret = []
        for item in fameHall.items:
            if item.no1:
                ret.append({
                    'issn':item.issueNum,
                    'name':item.no1.get('name', ''),
                    'img':item.no1.get('purl', ''),
                    'score':item.no1.get('score')
                })
        return ret

    @classmethod
    def buildNotReceived(cls, rankId, hisotryItems, userId, clientId):
        ret = []
        for item in hisotryItems:
            userData = dizhu_score_ranking.loadUserData(userId, rankId, item.issueNum)
            if not userData:
                if ftlog.is_debug():
                    ftlog.debug('buildNotReceived userData is None. userId=', userId,
                                'rankId=', rankId,
                                'issueNum=', item.issueNum,
                                'hisotryItems=', hisotryItems)
                continue

            if userData.rewardState == RewardState.ST_HAS_REWARD:
                rankRewards = dizhu_score_ranking.findRankRewardsByRank(rankId, item.issueNum, clientId, userData.rank)
                if rankRewards:
                    ret.append({
                         'issn': item.issueNum,
                         'rank' : userData.rank,
                         'img' : rankRewards.get('img', ''),
                         'desc' : rankRewards.get('desc', ''),
                         'cash' : rankRewards.get('cash', 0)
                    })
            if ftlog.is_debug():
                ftlog.debug('buildNotReceived userId=', userId,
                            'rankId=', rankId,
                            'hisotryItems=', hisotryItems,
                            'clientId=', clientId,
                            'userData=', userData.toDict() if userData else '')
        return ret
    
    @classmethod
    def pickHistoryItems(cls, rankingInfo, curIssueNum):
        ret = []
        for item in rankingInfo.items:
            if dizhu_score_ranking.compareIssueNum(curIssueNum, item.issueNum) > 0:
                ret.append(item)
        return ret
            
    @classmethod
    def _doGetRankList(cls, userId, rankId, clientId, timestamp=None):
        try:
            mo = MsgPack()
            rankingDefine = dizhu_score_ranking.findRankingDefine(rankId)
            if not rankingDefine:
                raise TYBizException(-1, "未知的排行榜")

            rankingInfo = dizhu_score_ranking.loadRankingInfo(rankId)
            
            timestamp = timestamp if timestamp is not None else pktimestamp.getCurrentTimestamp()
            issueNum = dizhu_score_ranking.calcIssueNum(timestamp)
            
            mo.setCmd('dizhu')
            mo.setResult('action', 'scoreboard')
            mo.setResult('rankId', rankId)
            
            rank = dizhu_score_ranking.getUserRank(userId, rankId, issueNum)
            userData = dizhu_score_ranking.loadOrCreateUserData(userId, rankId, issueNum)
            userInfo = {
                'rank':rank if rank >= 0 else 0,
                'score':userData.score,
                'plays':userData.playCount
            }
            hisotryItems = cls.pickHistoryItems(rankingInfo, issueNum)
            fameHall = dizhu_score_ranking.loadFameHall(rankId)
            mo.setResult('userInfo', userInfo)
            dibaoInfo = cls.buildDibaoInfo(rankingDefine, userData)
            if dibaoInfo:
                mo.setResult('dibao', dibaoInfo)
            mo.setResult('curTime', timestamp)
            mo.setResult('curIssn', issueNum)
            mo.setResult('curRank', cls.buildCurRank(rankingDefine, issueNum, clientId, timestamp))
            hisIssns = [item.issueNum for item in hisotryItems]
            hisIssns.sort(reverse=True)
            mo.setResult('hisIssns', hisIssns)
            mo.setResult('fameHall', cls.buildFameHall(fameHall))
            mo.setResult('notReceive', cls.buildNotReceived(rankingDefine.rankId, hisotryItems, userId, clientId))
            mo.setResult('desc', rankingDefine.desc)

            return mo
        except TYBizException, e:
            mo = MsgPack()
            mo.setCmd('dizhu')
            mo.setResult('action', 'scoreboard')
            mo.setResult('code', -1)
            mo.setResult('info', e.message)
            return mo

    @markCmdActionMethod(cmd='dizhu', action='scoreboard', clientIdVer=0, scope='game')
    def doGetRankList(self, userId, rankId, clientId):
        mo = self._doGetRankList(userId, rankId, clientId)
        if ftlog.is_debug():
            ftlog.debug('doGetRankList mo=', mo,
                        'userId=', userId,
                        'rankId=', rankId,
                        'clientId=', clientId)
        router.sendToUser(mo, userId)

    @classmethod
    def _doGetRankListByIssueNum(cls, userId, rankId, issueNum, clientId, start, end, timestamp=None):
        mo = MsgPack()
        mo.setCmd('dizhu')
        mo.setResult('action', 'score_get_rank')
        mo.setResult('rankId', rankId)
        mo.setResult('issn', issueNum)
        
        timestamp = timestamp if timestamp is not None else pktimestamp.getCurrentTimestamp()
        rank = dizhu_score_ranking.getUserRank(userId, rankId, issueNum)
        userData = dizhu_score_ranking.loadOrCreateUserData(userId, rankId, issueNum)
        userInfo = {
            'rank':rank if rank >= 0 else 0,
            'score':userData.score,
            'plays':userData.playCount
        }
        mo.setResult('userInfo', userInfo)
        
        rankList = cls.rankMng.getRankList(rankId, issueNum, timestamp)
        if ftlog.is_debug():
            ftlog.debug('rankMng.getRankList len=', len(rankList), 'rankList=', rankList)

        rankIndex = 0
        rankListRet = []
        for rankItem in rankList:
            rankIndex += 1
            if rankIndex < start:
                continue
            if rankIndex > end:
                break

            rankRewards = dizhu_score_ranking.findRankRewardsByRank(rankId, issueNum, clientId, rankItem[2])
            # userId, score, i + 1, userName, purl
            rankListRet.append({
                'name':rankItem[3],
                'img':rankItem[4],
                'score':rankItem[1],
                'desc':rankRewards.get('desc', '') if rankRewards else ''
            })

            if len(rankListRet) >= 100:
                break
        
        mo.setResult('rank', rankListRet)
        mo.setResult('start', start)
        mo.setResult('end', end)
        mo.setResult('total', len(rankList))
        return mo
    
    @markCmdActionMethod(cmd='dizhu', action='score_get_rank', clientIdVer=0, scope='game')
    def doGetRanksByIssueNum(self, userId, rankId, issueNum, clientId, start, end):
        mo = self._doGetRankListByIssueNum(userId, rankId, issueNum, clientId, start, end)
        if ftlog.is_debug():
            ftlog.debug('doGetRanksByIssueNum mo=', mo,
                        'userId=', userId,
                        'rankId=', rankId,
                        'issueNum=', issueNum,
                        'clientId=', clientId,
                        'start=', start, 'end=', end)
        router.sendToUser(mo, userId)

    @classmethod
    def _doGetRankReward(cls, userId, rankId, issueNum, isDibao, clientId = None):
        try:
            rankingDefine = dizhu_score_ranking.findRankingDefine(rankId)
            if not rankingDefine:
                raise TYBizException(-1, '未知的排行榜')

            if isDibao:
                assetList = dizhu_score_ranking.gainDibaoReward(userId, rankId, issueNum)
            else:
                assetList = dizhu_score_ranking.gainUserRanklistReward(userId, rankId, issueNum, clientId)

            mo = MsgPack()
            mo.setCmd('dizhu')
            mo.setResult('action', 'score_get_reward')
            mo.setResult('rankId', rankId)
            mo.setResult('issn', issueNum)
            mo.setResult('isDibao', isDibao)
            rewards = []
            if assetList:
                for atp in assetList:
                    rewards.append({
                        'name':atp[0].displayName,
                        'img':atp[0].pic,
                        'count':atp[1]
                    })
            mo.setResult('rewards', rewards)
            return mo
        except TYBizException, e:
            mo = MsgPack()
            mo.setCmd('dizhu')
            mo.setResult('action', 'score_get_reward')
            mo.setResult('rankId', rankId)
            mo.setResult('issn', issueNum)
            mo.setResult('isDibao', isDibao)
            mo.setResult('code', -1)
            mo.setResult('info', e.message)
            return mo
    
    @markCmdActionMethod(cmd='dizhu', action='score_get_reward', clientIdVer=0, scope='game')
    def doGetRankReward(self, userId, rankId, issueNum, isDibao):
        mo = self._doGetRankReward(userId, rankId, issueNum, isDibao)
        #userId, rankId, issueNum, isDibao, clientId = None
        if ftlog.is_debug():
            ftlog.debug('doGetRankReward mo=', mo,
                        'userId=', userId,
                        'rankId=', rankId,
                        'issueNum=', issueNum,
                        'isDibao=', isDibao)
        router.sendToUser(mo, userId)

    @classmethod
    def _doGetRankRules(cls, userId, rankId):
        mo = MsgPack()
        mo.setCmd('dizhu')
        mo.setResult('action', 'score_get_rule')
        try:
            rankingDefine = dizhu_score_ranking.findRankingDefine(rankId)
            if not rankingDefine:
                raise TYBizException(-1, '未知的排行榜')
            
            mo.setResult('rankId', rankId)
            rules = rankingDefine.rules
            mo.setResult('rules', rules)
            return mo
        except TYBizException, e:
            mo.setResult('code', -1)
            mo.setResult('info', e.message)
            return mo
    
    @markCmdActionMethod(cmd='dizhu', action='score_get_rule', clientIdVer=0, scope='game')
    def doGetRankRules(self, userId, rankId):
        mo = self._doGetRankRules(userId, rankId)
        router.sendToUser(mo, userId)

    @classmethod
    def _doGetNotReceiveReward(cls, userId, clientId=None):
        mo = MsgPack()
        mo.setCmd('dizhu')
        mo.setResult('action', 'score_reward_tip')

        curIssueNum = dizhu_score_ranking.calcIssueNum()
        mo.setResult('curIssn', curIssueNum)

        rankingConf = dizhu_score_ranking.getConf()
        for rankId, rankingDefine in rankingConf.rankingDefineMap.iteritems():
            if not rankingDefine:
                raise TYBizException(-1, '未知的排行榜')

            rankingInfo = dizhu_score_ranking.loadRankingInfo(rankId)
            hisotryItems = cls.pickHistoryItems(rankingInfo, curIssueNum)
            from poker.entity.dao import sessiondata
            clientId = clientId or sessiondata.getClientId(userId)
            notReceive = cls.buildNotReceived(rankingDefine.rankId, hisotryItems, userId, clientId)
            if notReceive:
                mo.setResult('rankId', rankId)
                mo.setResult('notReceive', notReceive)
                break

        return mo

    @markCmdActionMethod(cmd='dizhu', action='score_reward_tip', clientIdVer=0, scope='game')
    def doGetNotReceiveReward(self, userId, clientId):
        '''
        二级大厅领奖弹窗协议
        :param userId: 
        :param clientId: 
        :return: 
        '''
        mo = self._doGetNotReceiveReward(userId, clientId)
        router.sendToUser(mo, userId)
        if ftlog.is_debug():
            ftlog.debug('doGetNotReceiveReward userId=', userId, 'mo=', mo)
