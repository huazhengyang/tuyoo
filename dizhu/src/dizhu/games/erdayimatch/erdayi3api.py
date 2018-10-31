# -*- coding:utf-8 -*-
'''
Created on 2016年7月26日

@author: luwei
'''
from dizhu.entity.erdayi import HttpPostRequest, HttpGetRequest, ErrorEnum, \
    Erdayi3rdInterface, PlayerControl
from freetime.core.tasklet import FTTasklet
from freetime.core.timer import FTTimer
import freetime.util.log as ftlog
from poker.entity.dao import daobase
from poker.util import strutil


class ReportEntryModel(object):
    ReportType_EviewRound = 1 # 
    ReportType_RoundRank = 2 # 
    ReportType_Rank = 3 # 
    ReportType_RankFinish = 4 #
    ReportType_MatchReg = 5 #

    def __init__(self, urlType=None, params=None):
        self.urlType = urlType #
        self.params = params # post参数
    
    def getUrl(self):
        if self.urlType == ReportEntryModel.ReportType_EviewRound:
            return '/match/eview/round/send'
        elif self.urlType == ReportEntryModel.ReportType_RoundRank:
            return '/match/round/rank/send'
        elif self.urlType == ReportEntryModel.ReportType_Rank:
            return '/match/ranks/send'
        elif self.urlType == ReportEntryModel.ReportType_RankFinish:
            return '/match/ranks/sent'
        elif self.urlType == ReportEntryModel.ReportType_MatchReg:
            return '/match/reg'

    def fromJson(self, js):
        d = strutil.loads(js)
        self.urlType = d.get('urlType')
        self.params = d.get('params')
        return self
          
    def toJson(self):
        return strutil.dumps({
            'urlType': self.urlType,
            'params': self.params
        })
    
class ReportQueueDao(object):

    def __init__(self, roomId):
        self._redispath = 'dizhu:erdayi:reporter:%d' % int(roomId)
    
    def append(self, data):
        return daobase.executeMixCmd('rpush', self._redispath, data)
        
    def length(self):
        return daobase.executeMixCmd('llen', self._redispath)
        
    def range(self, start, end):
        ''' 返回范围内的元素，[start, end]全包含 '''
        return daobase.executeMixCmd('lrange', self._redispath, start, end)
    
    def index(self, index):
        ''' 返回index位置的元素 '''
        return daobase.executeMixCmd('lindex', self._redispath, index)
    
    def set(self, index, data):
        ''' 返回index位置的元素 '''
        return daobase.executeMixCmd('lset', self._redispath, index, data)
    
    def pophead(self):
        ''' 返回index位置的元素 '''
        return daobase.executeMixCmd('lpop', self._redispath)
    
    def clear(self):
        ''' 删除list的所有元素 '''
        return daobase.executeMixCmd('ltrim', self._redispath, -1, 0)

class FinalRankReporter(object):
    # key=roomId.matchingId, value=list<{'player_id': str(p.userId),'ranking':str(p.rank),'status':'0'}>
    _cacheMap = {}
        
    @classmethod
    def buildKey(cls, roomId, matchId):
        return '%s.%s' % (roomId, matchId)
    
    @classmethod
    def reportFinalRanks(cls, roomId, matchId, ranks):
        key = cls.buildKey(roomId, matchId)
        cache = cls._cacheMap.get(key)
        if not cache:
            cache = []
            cls._cacheMap[key] = cache
        cache.extend(ranks)
    
    @classmethod
    def finishFinalRanks(cls, roomId, matchId):
        try:
            key = cls.buildKey(roomId, matchId)
            cache = cls._cacheMap.pop(key)
            Report3rdInterface.reportRank(roomId, matchId, cache)
            Report3rdInterface.reportRankFinish(roomId, matchId)
        except:
            ftlog.error('FinalRankReporter.finishFinalRanks',
                        'roomId=', roomId,
                        'matchId=', matchId)
        
class AsyncReporter(object):
    _report_max_retry_times = 3 # 尝试最大上报次数，若上报失败次数超过此限制，则直接抛弃
    _report_retry_interval  = 3 # 尝试上报失败后的等待时间
    
    def __init__(self, roomId):
        self._roomId = roomId
        self._dao = ReportQueueDao(roomId)
        self._timer = None
        self._changed = False
        
    def enqueue(self, model):
        ftlog.debug('AsyncReporter.enqueue',
                    'model.urlType=', model.urlType,
                    'model.params=', model.params)
        self._changed = True
        self._dao.append(model.toJson())
        if not self._timer:
            self._timer = FTTimer(0, self._onTimer)
            
    def _onTimer(self):
        self._changed = False
        datas = self._dao.range(0, 9)
        if not isinstance(datas, list):
            datas = []
        ftlog.debug('AsyncReporter._onTimer:', 'datas=', datas)

        for data in datas:
            model = ReportEntryModel().fromJson(data)
            ec, info = self._tryReport(model, AsyncReporter._report_max_retry_times, AsyncReporter._report_retry_interval)
            if ec != 0:
                self._reportFailed(model, ec, info)
            self._dao.pophead()
        self._timer = None
        if len(datas) >= 10 or self._changed:
            self._timer = FTTimer(0.1, self._onTimer)

    def _tryReport(self, model, retryTimes, retryInterval):
        ftlog.debug('AsyncReporter._tryReport')
        ec, info = self._report(model)
        while (ec != 0 and retryTimes > 0):
            retryTimes -= 1
            FTTasklet.getCurrentFTTasklet().sleepNb(retryInterval)
            ec, info = self._report(model)
        return ec, info
        
    def _report(self, model):
        host = PlayerControl.getConf('3rdapi.host')
        path = model.getUrl()
        params = model.params
        ftlog.debug('AsyncReporter._report',
                    'path=', path,
                    'params=', params)
        try:
            response = HttpPostRequest.request(host, path, params)
            response = Erdayi3rdInterface.translateResponse(response)
        except:
            ftlog.error('AsyncReporter._report',
                        'path=', path,
                        'params=', params)
        ftlog.debug('AsyncReporter._report',
                    'path=', path,
                    'params=', params, 
                    'response=', response)
        
        return response.get('resp_code'), response.get('resp_msg')
        
    def _reportFailed(self, model, ec, info):
        ftlog.debug('AsyncReporter._reportFailed',
                    'url=', model.getUrl(),
                    'params=', model.params,
                    'ec=', ec,
                    'info=', info)
        
class ReporterManager(object):
    _reporterMap = {}
    
    @classmethod
    def getOrCreateReporter(cls, roomId):
        ''' 获得一个AsyncReporter对象，若不存在则创建 '''
        if not cls._reporterMap.get(roomId):
            cls._reporterMap[roomId] = AsyncReporter(roomId)
        return cls._reporterMap[roomId]
    
    @classmethod
    def removeReporter(cls, roomId):
        cls._reporterMap[roomId] = None        

class Report3rdInterface(object):

    @classmethod
    def reportEviewRound(cls, roomId, matchId, userId, tableId, cardPlayerId,
                         cardGroupId, score, mpscore,
                         mpRatio, mpRatioRank, mpRatioScore,
                         cardType, cardHole = None):
        '''
        人机对局结果上报
        match/eview/round/send                          
        '''
        params = {
            'cp_id': str(PlayerControl.getConf('3rdapi.cpid')),
            'match_id': str(matchId), # 厂商4位+ 平台自定义10位+厂商自定义6位
            'player_id':str(userId),
            'card_player_id':str(cardPlayerId), # 纯数字， 从1开始顺序排列
            'card_group_id': str(cardGroupId), # 纯数字， 从1开始顺序排列
            'card_desk_id': str(tableId), # 纯数字， 从1开始顺序排列
            'card_score': '%.4f' % score, # 纯数字，保留四位小数
            'mp_score': '%.4f' % mpscore, # 纯数字，保留四位小数
            'mp_ratio': '%.4f' % mpRatio, # 纯数字，保留四位小数
            'mp_ratio_rank': str(mpRatioRank), # 纯数字（从1开始， 可重复）
            'mp_ratio_score': '%.4f' % mpRatioScore, # 纯数字，保留四位小数
            'card_type': ','.join(map(lambda x: str(x), cardType)),
            'card_hole': ','.join(map(lambda x: str(x), cardHole)) if cardHole else cardHole,  # （如果该条数据用户为庄家则字段必传，用户为防守方则不传）见数据字典
        }
        model = ReportEntryModel(ReportEntryModel.ReportType_EviewRound, params)
        ReporterManager.getOrCreateReporter(roomId).enqueue(model)
    
    @classmethod
    def reportRoundRank(cls, roomId, matchId, stageIndex, rankList):
        '''
        移位排名结果上报        
        match/round/rank/send                        
        '''
        rank_list = rankList
        params = {
            'cp_id': str(PlayerControl.getConf('3rdapi.cpid')),
            'match_id': str(matchId), # 厂商4位+ 平台自定义10位+厂商自定义6位
            'round_id': str(stageIndex), # 纯数字， 从0开始顺序排列（每移位一次即+1）
            'rank_list': rank_list, #（最大200条）[{'player_id':0, 'card_rank':1}, 'status':'0'] //'card_rank' 从1开始的纯数字（不可重复）
        }
        model = ReportEntryModel(ReportEntryModel.ReportType_RoundRank, params)
        ReporterManager.getOrCreateReporter(roomId).enqueue(model)
    
    @classmethod
    def reportRank(cls, roomId, matchId, rankList):
        '''
        最终大排名结果上报
        match/ranks/send                
        '''
        ranks = rankList
        params = {
            'cp_id': str(PlayerControl.getConf('3rdapi.cpid')),
            'match_id': str(matchId),
            'ranks': ranks, # （最大200条）[{'player_id':0, 'ranking': 1, 'status':'0'}]
        }
        model = ReportEntryModel(ReportEntryModel.ReportType_Rank, params)
        ReporterManager.getOrCreateReporter(roomId).enqueue(model)
    
    @classmethod
    def reportRankFinish(cls, roomId, matchId):
        '''
        名次上传完毕
        match/ranks/sent
        '''
        params = {
            'cp_id': str(PlayerControl.getConf('3rdapi.cpid')),
            'match_id': str(matchId),
        }
        model = ReportEntryModel(ReportEntryModel.ReportType_RankFinish, params)
        ReporterManager.getOrCreateReporter(roomId).enqueue(model)

    @classmethod
    def matchReg(cls, roomId, matchId, userId, userName):
        '''
        比赛报名                
        match/reg                
        '''
        params = {
            'cp_id': str(PlayerControl.getConf('3rdapi.cpid')),
            'match_id': str(matchId),
            'player_name': userName,
            'player_id': str(userId)
        }
        model = ReportEntryModel(ReportEntryModel.ReportType_MatchReg, params)
        ReporterManager.getOrCreateReporter(roomId).enqueue(model)

    @classmethod
    def matchCheck(cls, matchId):
        '''
        比赛报名                
        GET:match/check               
        '''
        params = {
            'cp_id': str(PlayerControl.getConf('3rdapi.cpid')),
            'match_id': str(matchId),
        }
        host = PlayerControl.getConf('3rdapi.host')
        response = HttpGetRequest.request(host, 'match/check', params)
        ftlog.debug('Report3rdInterface.matchCheck:',
                    'matchId=', matchId,
                    'params=', params,
                    'path=match/check' 
                    'response=', response)
        response = Erdayi3rdInterface.translateResponse(response)
        return response.get('resp_code'), response.get('resp_msg')

def reportEviewRound(roomId, player, cardNo, playerCards, baseCards):
    cardGroupId = player.group.groupIndex+1 # 第三方要求：纯数字， 从1开始顺序排列
    cardResult = player.getCardResult(cardNo)
    Report3rdInterface.reportEviewRound(roomId, player.stage.stageId3, player.userId, player.playerNo, player.playerNo,
                                        cardGroupId, cardResult.score, cardResult.mpScore, cardResult.mpRate,
                                        cardResult.mpRatioRank, cardResult.mpRatioScore,
                                        playerCards, baseCards)

def reportRoundRank(roomId, stage, rankList, riseUserCount):
    # rankList是player列表
    if ftlog.is_debug():
        ftlog.debug('erdayi3api.reportRoundRank roomId=', roomId,
                    'stageIndex=', stage.stageIndex,
                    'stageId3=', stage.stageId3,
                    'riseUserCount=', riseUserCount,
                    'rankList=', [(p.userId, p.rank) for p in rankList])
    if len(rankList) <= 0:
        return
    
    # 每次最大上报的rank个数
    reportCount = 150
    matchId = stage.stageId3
        
    needReportList = [{'player_id': str(p.userId),'ranking':str(p.rank),'status':'0'} for p in rankList]
    # 由于reportList存在最长限制，所以分批次上传
    for i in range(0, len(needReportList), reportCount):
        reportingList = needReportList[i : i+reportCount]   
        Report3rdInterface.reportRank(roomId, matchId, reportingList)
    Report3rdInterface.reportRankFinish(roomId, matchId)
    
    # 不止一个阶段
    if len(stage.matchConf.stages) > 1:
        finalRankList = needReportList[riseUserCount:] if not stage.isLastStage else needReportList 
        if finalRankList:
            FinalRankReporter.reportFinalRanks(roomId, stage.matchingId3, finalRankList)
        if stage.isLastStage:
            FinalRankReporter.finishFinalRanks(roomId, stage.matchingId3)
        
def reportSignin(roomId, stage):
    playerList = stage.group.playerMap.values()
    matchId = stage.stageId3
    for p in playerList:
        name = p.realInfo.get('realname', p.userName) if p.realInfo else p.userName
        Report3rdInterface.matchReg(roomId, matchId, p.userId, name)

def matchCheck(matchId):
    code, msg = Report3rdInterface.matchCheck(matchId)
    return code == ErrorEnum.ERR_OK, msg

def fmtScore(score, n=2):
    fmt = '%d' if int(score) == score else '%%.%sf' % (n)
    return fmt % score


