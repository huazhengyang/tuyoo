# -*- coding=utf-8
'''
Created on 2015年7月2日

@author: zhaojiangang
'''
import json

import freetime.util.log as ftlog
from hall.entity import hallconf, hallitem
from poker.entity.biz.ranking.dao import TYRankingUserScoreInfoDao, \
    TYRankingUserScoreInfo, TYRankingDao
from poker.entity.biz.ranking.rankingsystem import TYRankingScoreCalc, \
    TYRankingSystemImpl, TYRankingSystem, TYRankingScoreCalcRegister, \
    TYRankingInputTypes
from poker.entity.dao import daobase, userchip, userdata
import poker.entity.dao.gamedata as pkgamedata
from poker.entity.events.tyevent import EventConfigure, EventUserLogin, \
    EventHeartBeat
import poker.entity.events.tyeventbus as pkeventbus
import poker.util.timestamp as pktimestamp
from hall.entity.hallconf import HALL_GAMEID
from hall.servers.util.rpc import user_remote
import poker.entity.biz.message.message as pkmessage
from poker.util import strutil


class TYRankingUserScoreInfoDaoImpl(TYRankingUserScoreInfoDao):
    def loadScoreInfo(self, rankingId, userId):
        '''
        获取用户的scoreInfo
        '''
        try:
            field = 'ranking.info:%s' % (rankingId)
            d = pkgamedata.getGameAttrJson(userId, 9999, field)
            if d:
                return TYRankingUserScoreInfo(d['score'], d['issueNumber'])
        except:
            ftlog.error()
        return None
    
    def saveScoreInfo(self, rankingId, userId, scoreInfo):
        '''
        保存用户的scoreInfo
        '''
        field = 'ranking.info:%s' % (rankingId)
        jstr = json.dumps({'score':scoreInfo.score, 'issueNumber':scoreInfo.issueNumber})
        pkgamedata.setGameAttr(userId, 9999, field, jstr)

class TYRankingDaoImpl(TYRankingDao):
    _set_user_score_alias = 'TYRankingSystemImpl.set_user_score'
    _set_user_score_script = '''
    local rankingId = KEYS[1]
    local issueNumber = KEYS[2]
    local userId = KEYS[3]
    local score = tonumber(KEYS[4])
    local maxCount = tonumber(KEYS[5])
    local listKey = 'ranking.list:'..rankingId..':'..issueNumber
    local addCount = redis.call('zadd', listKey, score, userId)
    local rank = redis.call('zrevrank', listKey, userId)
    -- 检查排行榜人数，如果超出则删除最小的
    local count = redis.call('zcard', listKey)
    if count > maxCount then
        local userIds = redis.call('zrange', listKey, 0, 0)
        redis.call('zrem', listKey, userIds[1])
        if userIds[1] == userId then
            return -1
        end
    end
    return rank
    '''
    
    _remove_user_alias = 'TYRankingSystemImpl.remove_user'
    _remove_user_script = '''
    local rankingId = KEYS[1]
    local issueNumber = KEYS[2]
    local userId = KEYS[3]
    local listKey = 'ranking.list:'..rankingId..':'..issueNumber
    return redis.call('zrem', listKey, userId)
    '''
    
    _get_user_alias = 'TYRankingSystemImpl.get_user'
    _get_user_script = '''
    local rankingId = KEYS[1]
    local issueNumber = KEYS[2]
    local userId = KEYS[3]
    local listKey = 'ranking.list:'..rankingId..':'..issueNumber
    local score = 0
    local rank = redis.call('zrevrank', listKey, userId)
    if rank == nil then
        return {-1, score}
    end
    score = redis.call('zscore', listKey, userId)
    return {rank, score}
    '''
    
    _get_topn_alias = 'TYRankingSystemImpl.get_topn'
    _get_topn_script = '''
    local rankingId = KEYS[1]
    local issueNumber = KEYS[2]
    local topN = tonumber(KEYS[3])
    local listKey = 'ranking.list:'..rankingId..':'..issueNumber
    return redis.call('zrevrange', listKey, 0, topN-1, 'withscores')
    '''
    
    def __init__(self):
        daobase.loadLuaScripts(self._set_user_score_alias, self._set_user_score_script)
        daobase.loadLuaScripts(self._get_user_alias, self._get_user_script)
        daobase.loadLuaScripts(self._remove_user_alias, self._remove_user_script)
        daobase.loadLuaScripts(self._get_topn_alias, self._get_topn_script)
        
    def loadRankingStatusData(self, rankingId):
        '''
        加载ranking信息
        '''
        return daobase.executeRankCmd('get', 'ranking.status:%s' % (rankingId))
    
    def removeRankingStatus(self, rankingId):
        '''
        删除ranking信息
        '''
        daobase.executeRankCmd('del', 'ranking.status:%s' % (rankingId))
    
    def saveRankingStatusData(self, rankingId, data):
        '''
        保存ranking信息
        '''
        daobase.executeRankCmd('set', 'ranking.status:%s' % (rankingId), data)
    
    def removeRankingList(self, rankingId, issueNumber):
        '''
        删除raking榜单
        '''
        rankingListKey = 'ranking.list:%s:%s' % (rankingId, issueNumber)
        daobase.executeRankCmd('del', rankingListKey)
    
    def setUserScore(self, rankingId, issueNumber, userId, score, totalN):
        '''
        设置用户积分
        @return: rank
        '''
        return daobase.executeRankLua(self._set_user_score_alias, 5,
                                      rankingId,
                                      issueNumber,
                                      userId,
                                      score,
                                      totalN)
    
    def removeUser(self, rankingId, issueNumber, userId):
        '''
        删除用户
        '''
        return daobase.executeRankLua(self._remove_user_alias, 3,
                                      rankingId,
                                      issueNumber,
                                      userId) > 0
    
    def getUserRankWithScore(self, rankingId, issueNumber, userId):
        '''
        获取用户排名和积分
        @return: (rank, score)
        '''
        return daobase.executeRankLua(self._get_user_alias, 3,
                                      rankingId,
                                      issueNumber,
                                      userId)
        
    def getTopN(self, rankingId, issueNumber, topN):
        '''
        获取topN
        @return: [userId1, score1, userId2, score2,...] 
        '''
        return daobase.executeRankLua(self._get_topn_alias, 3,
                                      rankingId,
                                      issueNumber,
                                      topN)
    
class TYRankingScoreCalcMax(TYRankingScoreCalc):
    TYPE_ID = 'max'
    def __init__(self):
        super(TYRankingScoreCalcMax, self).__init__()
        
    def calcScore(self, oldScore, opScore):
        '''
        根据老的socre和当前操作的score
        '''
        return max(oldScore, opScore)
  
class TYRankingScoreCalcIncr(TYRankingScoreCalc):
    TYPE_ID = 'incr'
    def __init__(self):
        super(TYRankingScoreCalcIncr, self).__init__()

    def calcScore(self, oldScore, opScore):
        '''
        根据老的socre和当前操作的score
        '''
        return oldScore + opScore

class TYRankingScoreNormal(TYRankingScoreCalc):
    TYPE_ID = 'normal'
    def __init__(self):
        super(TYRankingScoreNormal, self).__init__()
    def calcScore(self, oldScore, opScore):
        '''
        根据老的socre和当前操作的score
        '''
        return opScore
    
rankingSystem = TYRankingSystem()
_inited = False
_prevProcessRankingTime = None
_processRankingInterval = 60

def _registerClasses():
    TYRankingScoreCalcRegister.registerClass(TYRankingScoreNormal.TYPE_ID, TYRankingScoreNormal)
    TYRankingScoreCalcRegister.registerClass(TYRankingScoreCalcIncr.TYPE_ID, TYRankingScoreCalcIncr)
    TYRankingScoreCalcRegister.registerClass(TYRankingScoreCalcMax.TYPE_ID, TYRankingScoreCalcMax)
        
def _reloadConf():
    conf = hallconf.getRankingConf()
    rankingSystem.reloadConf(conf)
    
def _onConfChanged(event):
    if _inited and event.isChanged('game:9999:ranking:0'):
        ftlog.debug('hallranking._onConfChanged')
        _reloadConf()
        
class RankRewardSender(object):
    def sendReward(self, rankingDefine, issueNumber, rankingUser, content):
        contentItemList = []
        contentItems = content.getItems()
        for contentItem in contentItems:
            contentItemList.append({'itemId':contentItem.assetKindId, 'count':contentItem.count})
        try:
            intRankingId = int(rankingDefine.rankingId)
            ret = user_remote.addAssets(HALL_GAMEID, rankingUser.userId, contentItemList, 'RANK_REWARD', intRankingId)
            if ret:
                mail = None
                if rankingDefine.rewardMail:
                    rewardContent = hallitem.buildContentsString(contentItems)
                    if rewardContent:
                        params = {
                            'rankingName':rankingDefine.name,
                            'rank':rankingUser.rank + 1,
                            'rewardContent':hallitem.buildContentsString(contentItems)
                        }
                        mail = strutil.replaceParams(rankingDefine.rewardMail, params)
                        if mail:
                            gameId = rankingDefine.gameIds[0] if rankingDefine.gameIds else 0
                            if gameId == 0:
                                gameId = 9999
                            pkmessage.sendPrivate(gameId, rankingUser.userId, 0, mail)
                ftlog.info('RankRewardSender.sendReward Succ userId=', rankingUser.userId,
                           'rankingId=', intRankingId,
                           'issueNumber=', issueNumber,
                           'rank=', rankingUser.rank + 1,
                           'rewards=', contentItemList,
                           'mail=', mail)
            else:
                ftlog.warn('RankRewardSender.sendReward Fail userId=', rankingUser.userId,
                           'rankingId=', intRankingId,
                           'issueNumber=', issueNumber,
                           'rank=', rankingUser.rank + 1,
                           'rewards=', contentItemList)
        except:
            ftlog.error('RankRewardSender.sendReward Exception userId=', rankingUser.userId,
                        'rankingId=', intRankingId,
                        'issueNumber=', issueNumber,
                        'rank=', rankingUser.rank + 1,
                        'rewards=', contentItemList)

def _initialize(isCenter):
    from hall.game import TGHall
    ftlog.debug('Ranking initialize begin', isCenter)
    global rankingSystem
    global _inited
    if not _inited:
        _inited = True
        rankingSystem = TYRankingSystemImpl(TYRankingUserScoreInfoDaoImpl(), TYRankingDaoImpl(), RankRewardSender())
        _registerClasses()
        _reloadConf()
        TGHall.getEventBus().subscribe(EventUserLogin, _onUserLogin)
        pkeventbus.globalEventBus.subscribe(EventConfigure, _onConfChanged)
        
        if isCenter :
            from poker.entity.events.tyeventbus import globalEventBus
            globalEventBus.subscribe(EventHeartBeat, onTimer)

    ftlog.debug('Ranking initialize end')
    
def _onUserLogin(event):
    timestamp = pktimestamp.getCurrentTimestamp()
    chip = userchip.getChip(event.userId)
    rankingSystem.setUserByInputType(event.gameId, TYRankingInputTypes.CHIP,
                                     event.userId, chip, timestamp)
    charm = userdata.getCharm(event.userId)
    rankingSystem.setUserByInputType(event.gameId, TYRankingInputTypes.CHARM,
                                     event.userId, charm, timestamp)
        

def onTimer(evt):
    global _prevProcessRankingTime
    timestamp = pktimestamp.getCurrentTimestamp()
    if (not _prevProcessRankingTime
        or timestamp - _prevProcessRankingTime > _processRankingInterval):
        _prevProcessRankingTime = timestamp
        rankingSystem.processRankings(timestamp)


