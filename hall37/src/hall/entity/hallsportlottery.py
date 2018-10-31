# -*- coding=utf-8 -*-
# Author:        luojihui@163.com
# Created:       17/12/20 下午3:41

import json
import time
import datetime
import freetime.util.log as ftlog
from freetime.core.timer import FTLoopTimer
from poker.entity.dao import daobase, userchip, sessiondata
from poker.entity.configure import configure, pokerconf, gdata
from poker.util import strutil, webpage
from poker.entity.biz.exceptions import TYBizException
from hall.entity.hallconf import HALL_GAMEID
from hall.entity import datachangenotify


# 仿真服的SDK 服务器 125.39.93.37 公司内网：220.249.15.134／202.106.9.134 机房：125.39.218.107／125.39.220.71|10.3.0.4
# http://feed.sportsdt.com/zaixiantuyou/soccer/?type=getschedulebydate&date=2017-12-28

def http7muri():
    if gdata.mode() == gdata.RUN_MODE_ONLINE:
        return 'http://httpproxy.ywdier.com/zaixiantuyou/soccer/'
    elif gdata.mode() == gdata.RUN_MODE_TINY_TEST:
        return 'http://httpproxy.ywdier.com/zaixiantuyou/soccer/'
    elif gdata.mode() == gdata.RUN_MODE_SIMULATION:
        return 'http://httpproxy.ywdier.com/zaixiantuyou/soccer/'

    return 'http://httpproxy.ywdier.com/zaixiantuyou/soccer/'


# 几日后的
DAYS = 5
# 最多查询多少日 如果第MAX_DAYS 还没有赛事就停止查询了
MAX_DAYS = 30

# 进程启动标志位
_inited = False
# 更新日期标志
_update = None

# 体育竞猜
_sportlotteryMap = {}

# HttpGetNdayAfterMatchs
_httpMatchMap = {}

# redis keys
# 联赛日期 date
leagueDaykey = 'hall.sportlottery.league.day:%s'
# 联赛下注总人数 (date, matchId)
leagueBetPlayersKey = 'hall.sportlottery.league.betplayers:%s:%s'
# 联赛下注总钱数 (date, matchId)
leagueBetChipsKey = 'hall.sportlottery.league.betchips:%s:%s'
# 联赛加油数 (date, matchId) player home点赞 away点赞
# player home点赞 sadd playerLovesHomeKey userId
playerLovesHomeKey = 'hall.sportlottery.player.loves.home:%s:%s'
# player away点赞 sadd playerLovesAwayKey userId
playerLovesAwayKey = 'hall.sportlottery.player.loves.away:%s:%s'

# 个人下注
#  % userId
betHomeKey = 'hall.sportlottery.bet.player.home:%s'
#  % userId
betAveKey = 'hall.sportlottery.bet.player.ave:%s'
#  % userId
betAwayKey = 'hall.sportlottery.bet.player.away:%s'

# 待领取的比赛奖励 userId
waitRewardKey = 'hall.sportlottery.player.waitreward:%s'
# 猜中 userId
winkey = 'hall.sportlottery.player.win:%s'
# 未猜中 userId
noWinKey = 'hall.sportlottery.player.nowin:%s'
# 待开奖 userId
noOpenHomeKey = 'hall.sportlottery.player.noOpen.home:%s'
noOpenAveKey = 'hall.sportlottery.player.noOpen.ave:%s'
noOpenAwayKey = 'hall.sportlottery.player.noOpen.away:%s'

# 一场比赛的状态
# _STATUS = {0: '未开始', 1: '上半场', 2: '中场', 3: '下半场', 4: '完场', 5: '中断', 6: '取消', 7: '加时', 8: '加时', 9: '加时',
#            10: '完场', 11: '点球大战', 12: '全场结束', 13: '延期', 14: '腰斩', 15: '待定', 16: '金球', 17: '未开始'}
# 一场比赛的结果
RESULTS = [4, 10, 12, 5, 6, 13, 14, 15]

CANCEL_RESULTS = [5, 6, 13, 14, 15]

# 下注状态
BET_STATUS = [0, 17]


class SportlotteryConf(object):
    '''体育竞猜配置'''
    _leaguesMap = {}
    _teamsMap = {}

    @classmethod
    def conf(cls):
        '''体育配置'''
        return configure.getGameJson(HALL_GAMEID, 'sportlottery', {})

    @classmethod
    def totalBetLimit(cls):
        return cls.conf().get('totalBetLimit', 100000000)
    
    @classmethod
    def totalBetLimitTips(cls):
        return cls.conf().get('totalBetLimitTips')
    
    @classmethod
    def isClosed(cls):
        return cls.conf().get('closed', 0)
    
    @classmethod
    def leagues(cls):
        conf = cls.conf()
        if conf and len(conf) > 0:
            return conf.get('leagues')

        return []

    @classmethod
    def leaguekeys(cls):
        if len(cls._leaguesMap) > 0:
            return cls._leaguesMap.keys()

        for league in cls.leagues():
            cls._leaguesMap[league.get('key')] = league

        return cls._leaguesMap.keys()

    @classmethod
    def getLeague(cls, key):
        if key in cls.leaguekeys():
            return cls._leaguesMap[key]

        return None

    @classmethod
    def teams(cls):
        conf = cls.conf()
        if conf and len(conf) > 0:
            teams = conf.get('teams')
            if teams and len(teams) > 0:
                return teams
        return []

    @classmethod
    def teamsMap(cls):
        if len(cls._teamsMap) > 0:
            return cls._teamsMap

        for team in cls.teams():
            cls._teamsMap[team.get('key')] = team

        return cls._teamsMap

    @classmethod
    def teamskeys(cls):
        keys = []
        teams = cls.teams()
        for team in teams:
            key = team.get('key')
            if key:
                keys.append(key)
            else:
                ftlog.warn('SportlotteryConf.teamskeys key error', team)

        return keys

    @classmethod
    def focusTeamskeys(cls):
        keys = []
        teams = cls.teams()
        for team in teams:
            if team.get('tag', 0) == 0:
                continue
            key = team.get('key')
            if key:
                keys.append(key)
            else:
                ftlog.warn('SportlotteryConf.focusTeamskeys key error', team)

        return keys


class SportOdds(object):
    '''欧指筛选'''
    ODDS = ['17', '308', '255', '256', '254']

    def __init__(self, sportlottery):
        self.sportlottery = sportlottery

        self.timer = FTLoopTimer(10, -1, self._getHttpOdds)
        self.timer.start()

        if ftlog.is_debug():
            ftlog.debug('SportOdds',
                        'sportObj=', self.sportlottery.toDict())

    def _getHttpOdds(self):
        if ftlog.is_debug():
            ftlog.debug('SportOdds',
                        '_getHttpOdds=', self.sportlottery.toDict())

        contents = http7Mgethdaoddsinfo(self.sportlottery.matchId)
        if not contents or len(contents) == 0:
            return

        if contents.get('GameId') != str(self.sportlottery.matchId):
            ftlog.warn('SportOdds httpOdds GameId not match',
                       'matchId=', self.sportlottery.matchId,
                       'GameId=', contents.get('GameId'))
            return

        Datas = contents.get('Datas')
        if not Datas or len(Datas) == 0:
            ftlog.warn('SportOdds httpOdds Datas empty',
                       'Datas=', Datas,
                       'contents=', contents)
            return

        tag = 0
        for data in Datas:
            if data.get('Cid') in self.ODDS:
                odds = data.get('Data', [])
                if odds and len(odds) >= 3:
                    self.sportlottery.odds = odds[:3]
                    self.sportlottery.save()
                    if self.timer:
                        self.timer.cancel()

                    tag = 1
                    break
        if self.sportlottery and tag == 1:
            self.sportlottery.clearSportOdds()


class SportResult(object):
    '''赛果'''

    def __init__(self, sportlottery):
        self.sportlottery = sportlottery
        self.date = datetime.datetime.fromtimestamp(self.sportlottery.timestamp).strftime('%Y-%m-%d')

        interval = self.sportlottery.timestamp - int(time.time())
        if interval > 0:
            FTLoopTimer(interval + (45 + 15 + 45 + 5) * 60, 0, self._startTimer).start()
        else:
            if interval + (45 + 15 + 45 + 5) * 60 <= 0:
                self._startTimer()
            else:
                FTLoopTimer(interval + (45 + 15 + 45 + 5) * 60, 0, self._startTimer).start()

        if ftlog.is_debug():
            ftlog.debug('SportResult',
                        'sportObj=', self.sportlottery.toDict())

    def _startTimer(self):
        self.timer = FTLoopTimer(60, -1, self._getHttp)
        self.timer.start()

    def _getHttp(self):
        if ftlog.is_debug():
            ftlog.debug('SportResult',
                        '_getHttp=', self.sportlottery.toDict())

        contents = http7Mgetschedulebydate(self.date)
        if not contents or len(contents) == 0:
            return

        tag = 0
        schedule = contents.get('Schedule')
        if not schedule or len(schedule) == 0:
            return

        for matchDict in schedule:
            match = matchDict.get('Id')
            if not match or len(match) < 4:
                continue
            if match[0] == int(self.sportlottery.matchId):
                if 'Score' in matchDict:
                    self.sportlottery.score = matchDict['Score']
                    if self.sportlottery.score and len(
                            self.sportlottery.score) > 0 and self.sportlottery.status not in RESULTS:
                        self.sportlottery.status = 4

                    self.sportlottery.save()

                    if self.sportlottery.isResult:
                        if self.timer:
                            self.timer.cancel()

                        tag = 1
                    break

        if self.sportlottery and tag == 1:
            self.sportlottery.clearSportResult()


class Sportlottery(object):
    '''体育竞猜一场比赛实例'''

    def __init__(self):
        # 比赛id
        self.matchId = None
        # 联赛id
        self.leagueId = None
        # 主队id
        self.homeTeamId = None
        # 客队id
        self.awayTeamId = None
        # 比赛时间戳
        self.timestamp = None
        # 比赛状态
        self.status = None
        # 定时器
        self.timer = None
        # 比分
        self.score = None
        # 欧盘指数
        self.sportOdds = None
        # 赛果
        self.sportResult = None

    def fromDict(self, d):
        self.matchId = d['matchId']
        self.leagueId = d['leagueId']
        self.homeTeamId = d['homeTeamId']
        self.awayTeamId = d['awayTeamId']
        self.timestamp = d['timestamp']
        self.status = d.get('status', 0)  # 未开始
        self.score = d.get('score', [0, 0])  # 比分
        self.odds = d.get('odds', ['0', '0', '0'])

    def toDict(self):
        return {'matchId': self.matchId, 'leagueId': self.leagueId, 'homeTeamId': self.homeTeamId,
                'awayTeamId': self.awayTeamId, 'timestamp': self.timestamp, 'status': self.status,
                'score': self.score,
                'odds': self.odds}

    def save(self):
        date = datetime.datetime.fromtimestamp(self.timestamp).strftime('%Y-%m-%d')
        daobase.executeMixCmd('hset', leagueDaykey % date, self.matchId, strutil.dumps(self.toDict()))

        if ftlog.is_debug():
            ftlog.debug('Sportlottery save',
                        'date=', date,
                        'matchId=', self.matchId,
                        'toDict=', self.toDict())

    def clearSportOdds(self):
        if self.sportOdds:
            del self.sportOdds
            self.sportOdds = None

    def clearSportResult(self):
        if self.sportResult:
            del self.sportResult
            self.sportResult = None

    def start(self):
        if self.isResult:
            return

        if ftlog.is_debug():
            ftlog.debug('Sportlottery start',
                        'toDict=', self.toDict())

        if self.odds == ['0', '0', '0']:
            self.sportOdds = SportOdds(self)

        self.sportResult = SportResult(self)

        interval = self.timestamp - int(time.time())
        if interval > 0:
            FTLoopTimer(interval, 0, self._startTimer).start()
        else:
            self._startTimer()

    def _startTimer(self):
        self.timer = FTLoopTimer(5 * 60, -1, self._getHttpStatus)
        self.timer.start()

    @property
    def isResult(self):
        return self.status in RESULTS

    def _getHttpStatus(self):
        contents = http7Mgetlivedata()

        if ftlog.is_debug():
            ftlog.debug('Sportlottery _getHttpStatus',
                        'toDict=', self.toDict())

        if not contents or len(contents) == 0:
            ftlog.info('Sportlottery._getHttpStatus',
                       'http7Mgetlivedata contents empty', contents)
            return

        liveData = contents.get('LiveData')
        if not liveData or len(liveData) == 0:
            ftlog.info('Sportlottery._getHttpStatus',
                       'http7Mgetlivedata LiveData empty', liveData)
            return

        matchD = liveData.get(str(self.matchId))
        if matchD:
            self.score = matchD.get('Score', [0, 0])
            self.status = matchD.get('Status', 0)
            if self.status != 0:
                self.save()

            if self.status in RESULTS:
                if self.timer:
                    self.timer.cancel()
        else:
            ftlog.warn('Sportlottery._getHttpStatus',
                       'liveData havenot matchId=', self.matchId,
                       'obj=', self)

    def __str__(self):
        return '%s:%s:%s:%s:%s' % (self.matchId, self.leagueId, self.homeTeamId, self.awayTeamId, self.timestamp)

    def __repr__(self):
        return self.__str__()

    def destructor(self):
        if self.timer:
            self.timer.cancel()

        ftlog.info('Sportlottery=', self)


def http7Mgetschedulebydate(dateStr):
    # 赛程赛果

    contents = {}

    _match_uri = http7muri() + '?type=getschedulebydate&date=%s'

    hbody = 'test'
    try:
        hbody, httpurl = webpage.webget(_match_uri % dateStr, method_='GET')
        ftlog.info('http7Mgetschedulebydate webget',
                   'hbody=', hbody,
                   'httpurl=', httpurl)

        contents = json.loads(hbody)
    except Exception, e:
        ftlog.warn('http7Mgetschedulebydate except',
                   'dateStr=', dateStr,
                   '_match_uri=', _match_uri,
                   'hbody=', hbody,
                   'warn=', e.message)

    if ftlog.is_debug():
        ftlog.debug('http7Mgetschedulebydate',
                    'dateStr=', dateStr,
                    '_match_uri=', _match_uri,
                    'contents=', contents)

    return contents


def http7Mgetlivedata():
    # 实时比分

    contents = {}

    _status_uri = http7muri() + '?type=getlivedata'

    try:
        hbody, httpurl = webpage.webget(_status_uri, method_='GET')
        contents = json.loads(hbody)
    except Exception, e:
        ftlog.warn('http7Mgetlivedata except',
                   '_status_uri=', _status_uri,
                   'warn=', e.message)

    if ftlog.is_debug():
        ftlog.debug('http7Mgetlivedata',
                    '_status_uri=', _status_uri,
                    'contents=', contents)

    return contents


def http7Mgethdaoddsinfo(matchId):
    # 欧盘指数

    contents = {}

    _cid_uri = http7muri() + '?type=gethdaoddsinfo&gameid=%s'

    try:
        hbody, httpurl = webpage.webget(_cid_uri % matchId, method_='GET')
        contents = json.loads(hbody)
    except Exception, e:
        ftlog.warn('http7Mgethdaoddsinfo except',
                   '_cid_uri=', _cid_uri,
                   'matchId=', matchId,
                   'warn=', e.message)

    if ftlog.is_debug():
        ftlog.debug('http7Mgethdaoddsinfo',
                    'matchId=', matchId,
                    '_cid_uri=', _cid_uri,
                    'contents=', contents)

    return contents


class HttpGetNdayAfterMatchs(object):
    '''N日后的比赛列表'''

    def __init__(self, interval, ndays, callback):
        self.httpContents = []
        self.callback = callback

        self.now = datetime.datetime.now()
        self._afterday = (self.now + datetime.timedelta(days=ndays)).strftime('%Y-%m-%d')

        self.timer = FTLoopTimer(interval, -1, self._checkResult)
        self.timer.start()

    def __str__(self):
        return '%s:%s' % (self.now, self._afterday)

    def __repr__(self):
        return self.__str__()

    @property
    def key(self):
        return self.__str__()

    def _checkDate(self):
        return self.now.date() == datetime.datetime.now().date()

    def _checkResult(self):
        if ftlog.is_debug():
            ftlog.debug('HttpGetNdayAfterMatchs',
                        'now=', self.now,
                        '_afterday=', self._afterday)

        if not self._checkDate():
            ftlog.info('hallsportlottery.HttpNdayAfterMatchList',
                       '_checkDate=', self.now.date(),
                       'nowDate=', datetime.datetime.now().date())
            if self.timer:
                self.timer.cancel()

            if self.callback:
                self.callback(self)

            return

        contents = http7Mgetschedulebydate(self._afterday)
        if contents and len(contents) > 0:
            if self.timer:
                self.timer.cancel()

            self.doContents(contents)

            if self.callback:
                self.callback(self)

    def doContents(self, contents):
        leagues = SportlotteryConf.leaguekeys()
        teams = SportlotteryConf.teamskeys()
        focusTeams = SportlotteryConf.focusTeamskeys()

        schedule = contents.get('Schedule')
        if schedule and len(schedule) > 0:
            for matchDict in schedule:
                match = matchDict['Id']
                if match and len(match) >= 4:
                    if match[1] not in leagues:
                        continue
                    if match[2] not in teams or match[3] not in teams:
                        continue
                    if match[2] not in focusTeams and match[3] not in focusTeams:
                        continue

                    d = {'matchId': match[0], 'leagueId': match[1], 'homeTeamId': match[2], 'awayTeamId': match[3],
                         'timestamp': matchDict['Date'] / 1000}

                    self.httpContents.append(d)


def clearall():
    _31deltadays = datetime.timedelta(days=31)
    now = datetime.datetime.now()
    _30beforeday = (now - _31deltadays).strftime('%Y-%m-%d')

    global leagueBetPlayersKey, leagueBetChipsKey, playerLovesHomeKey, playerLovesAwayKey
    global leagueDaykey

    keys = daobase.executeMixCmd('hkeys', leagueDaykey % _30beforeday)
    if keys:
        for matchId in keys:
            daobase.executeMixCmd('del', leagueBetPlayersKey % (_30beforeday, matchId))
            daobase.executeMixCmd('del', leagueBetChipsKey % (_30beforeday, matchId))
            daobase.executeMixCmd('del', playerLovesHomeKey % (_30beforeday, matchId))
            daobase.executeMixCmd('del', playerLovesAwayKey % (_30beforeday, matchId))

        daobase.executeMixCmd('del', leagueDaykey % _30beforeday)


def http5DayAfterCallback(httpObj):
    if httpObj:
        ftlog.info('hallsportlottery.http5DayAfterCallback',
                   'httpObj=', httpObj,
                   'httpContents=', httpObj.httpContents)

        global _sportlotteryMap, _httpMatchMap

        for match in httpObj.httpContents:
            date = datetime.datetime.fromtimestamp(match['timestamp']).strftime('%Y-%m-%d')
            daobase.executeMixCmd('hset', leagueDaykey % date, match['matchId'], strutil.dumps(match))

            if int(match['matchId']) in _sportlotteryMap:
                continue

            try:
                sportObj = Sportlottery()
                sportObj.fromDict(match)
                sportObj.start()
                _sportlotteryMap[sportObj.matchId] = sportObj

                if ftlog.is_debug():
                    ftlog.debug('http5DayAfterCallback',
                                'sportObj=', sportObj)
            except:
                ftlog.warn('hallsportlottery.http5DayAfterCallback',
                           'match=', match)

        if httpObj.key in _httpMatchMap:
            del _httpMatchMap[httpObj.key]


def httpTodayCallback(httpObj):
    if httpObj:
        ftlog.info('hallsportlottery.httpTodayCallback',
                   'httpObj=', httpObj,
                   'httpContents=', httpObj.httpContents)

        global _sportlotteryMap

        for match in httpObj.httpContents:
            timestamp = match['timestamp']
            if time.time() >= timestamp or time.time() + 7200 >= timestamp:
                continue

            date = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
            daobase.executeMixCmd('hset', leagueDaykey % date, match['matchId'], strutil.dumps(match))

            if int(match['matchId']) in _sportlotteryMap:
                continue

            try:
                sportObj = Sportlottery()
                sportObj.fromDict(match)
                sportObj.start()
                _sportlotteryMap[sportObj.matchId] = sportObj

                if ftlog.is_debug():
                    ftlog.debug('httpTodayCallback',
                                'sportObj=', sportObj)
            except:
                ftlog.warn('hallsportlottery.httpTodayCallback',
                           'match=', match)

        del httpObj


def startSportlottery():
    global _sportlotteryMap
    now = datetime.datetime.now()
    for n in range(DAYS + 1):
        _afterday = (now + datetime.timedelta(days=n)).strftime('%Y-%m-%d')
        datas = daobase.executeMixCmd('hgetall', leagueDaykey % _afterday)
        if datas:
            for i in xrange(len(datas) / 2):
                matchId = datas[i * 2]

                if int(matchId) in _sportlotteryMap:
                    continue

                jstr = datas[i * 2 + 1]
                try:
                    d = strutil.loads(jstr)
                    sportObj = Sportlottery()
                    sportObj.fromDict(d)
                    sportObj.start()
                    _sportlotteryMap[sportObj.matchId] = sportObj

                    if ftlog.is_debug():
                        ftlog.debug('startSportlottery',
                                    'sportObj=', sportObj)
                except:
                    ftlog.warn('hallsportlottery.startSportlottery',
                               'matchId=', matchId)

        if ftlog.is_debug():
            ftlog.debug('startSportlottery date',
                        'n=', n,
                        '_sportlotteryMap key=', _sportlotteryMap.keys(),
                        'datas=', datas)


def doRedis():
    global _sportlotteryMap, _httpMatchMap
    # 只保留30天，超过的都清除
    clearall()

    for matchId in _sportlotteryMap.keys():
        obj = _sportlotteryMap[matchId]
        if obj.isResult:
            obj.destructor()
            del obj

    now = datetime.datetime.now()
    _afterday = (now + datetime.timedelta(days=DAYS)).strftime('%Y-%m-%d')
    if 0 == daobase.executeMixCmd('exists', leagueDaykey % _afterday):
        obj = HttpGetNdayAfterMatchs(10, DAYS, http5DayAfterCallback)
        _httpMatchMap[obj.key] = obj

    if 0 == daobase.executeMixCmd('exists', leagueDaykey % now.strftime('%Y-%m-%d')):
        obj = HttpGetNdayAfterMatchs(10, 0, httpTodayCallback)
        _httpMatchMap[obj.key] = obj

    startSportlottery()


def _initialize():
    ftlog.info('sport lottery initialize begin', datetime.datetime.now())
    global _inited
    if not _inited:
        _inited = True
        sportRedis()
        ftlog.info('sport lottery initialize end', datetime.datetime.now())


def sportRedis():
    global _update
    if not SportlotteryConf.isClosed():
        now = datetime.datetime.now()
        if not _update or _update != now.date():
            _update = now.date()
            doRedis()
            ftlog.info('sportRedis',
                       'nowDate=', now)


def onEventHeartBeat(event):
    sportRedis()


def nDateProduct(userId, date):
    retList = []
    datas = daobase.executeMixCmd('hgetall', leagueDaykey % date)
    if datas:
        for i in xrange(len(datas) / 2):
            matchId = datas[i * 2]
            jstr = datas[i * 2 + 1]
            try:
                j = strutil.loads(jstr)

                if j.get('status') in RESULTS:
                    continue

                teamsMap = SportlotteryConf.teamsMap()
                homeTeamMap = teamsMap.get(j.get('homeTeamId'))
                homeTeamName = homeTeamMap.get('name')
                homtTeamPic = homeTeamMap.get('pic')
                awayTeamMap = teamsMap.get(j.get('awayTeamId'))
                awayTeamName = awayTeamMap.get('name')
                awayTeamPic = awayTeamMap.get('pic')

                leagueDict = SportlotteryConf.getLeague(j.get('leagueId'))
                location = leagueDict.get('shortName')

                odds = j.get('odds', ['0', '0', '0'])
                matchId = j.get('matchId')
                betcounts = daobase.executeMixCmd('scard', leagueBetPlayersKey % (date, matchId))

                betCoins = 0
                for pos in [1, 2, 3]:
                    betCoins += daobase.executeMixCmd('hget', leagueBetChipsKey % (date, matchId), pos) or 0

                love0 = daobase.executeMixCmd('scard', playerLovesHomeKey % (date, matchId))
                love1 = daobase.executeMixCmd('scard', playerLovesAwayKey % (date, matchId))

                homebetcoin = daobase.executeUserCmd(userId, 'hget', betHomeKey % userId,
                                                     '%s:%s' % (date, matchId)) or 0
                avebetcoin = daobase.executeUserCmd(userId, 'hget', betAveKey % userId, '%s:%s' % (date, matchId)) or 0
                awaybetcoin = daobase.executeUserCmd(userId, 'hget', betAwayKey % userId,
                                                     '%s:%s' % (date, matchId)) or 0
                totalBetCoin = homebetcoin + avebetcoin + awaybetcoin
                d = {'cell_type': 'main_list', 'date': date, 'datetime': j.get('timestamp'), 'type': 1,
                     'teamname0': homeTeamName, 'teampic0': homtTeamPic, 'teamname1': awayTeamName,
                     'teampic1': awayTeamPic, 'location': location, 'matchTime': j.get('timestamp'),
                     'homewin': odds[0], 'ave': odds[1], 'awaywin': odds[2], 'betcounts': betcounts,
                     'betCoins': betCoins, 'uuid': matchId, 'love0': love0, 'love1': love1, 'isBet': totalBetCoin > 0}

                if odds == ['0', '0', '0']:
                    continue
                retList.append(d)
            except:
                ftlog.warn('hallsportlottery.nDateProduct',
                           'matchId=', matchId)

    retList.sort(key=lambda item: item['datetime'])
    return retList


# 协议
def sportlotteryProduct(userId):
    retList = []
    now = datetime.datetime.now()
    sumday = DAYS
    for DAY in xrange(sumday + 1):
        ndate = (now + datetime.timedelta(days=DAY)).strftime('%Y-%m-%d')
        retList.extend(nDateProduct(userId, ndate))
        
    #如果上面没有赛事，继续查询直到有数据或者查到30天之后
    while len(retList) <= 0 and sumday <= MAX_DAYS:
        ndate = (now + datetime.timedelta(days=sumday)).strftime('%Y-%m-%d')
        retList.extend(nDateProduct(userId, ndate))
        sumday += 1
    
    return retList


def sportlotteryDetail(userId, date, matchId, type):
    d = {}
    jstr = daobase.executeMixCmd('hget', leagueDaykey % date, matchId)
    if jstr:
        try:
            j = strutil.loads(jstr)

            teamsMap = SportlotteryConf.teamsMap()
            homeTeamMap = teamsMap.get(j.get('homeTeamId'))
            homeTeamName = homeTeamMap.get('name')
            homtTeamPic = homeTeamMap.get('pic')
            awayTeamMap = teamsMap.get(j.get('awayTeamId'))
            awayTeamName = awayTeamMap.get('name')
            awayTeamPic = awayTeamMap.get('pic')

            leagueDict = SportlotteryConf.getLeague(j.get('leagueId'))
            location = leagueDict.get('shortName')

            odds = j.get('odds', ['0', '0', '0'])
            matchId = j.get('matchId')
            betcounts = daobase.executeMixCmd('scard', leagueBetPlayersKey % (date, matchId))

            betCoinsPos1 = daobase.executeMixCmd('hget', leagueBetChipsKey % (date, matchId), 1) or 0
            betCoinsPos2 = daobase.executeMixCmd('hget', leagueBetChipsKey % (date, matchId), 2) or 0
            betCoinsPos3 = daobase.executeMixCmd('hget', leagueBetChipsKey % (date, matchId), 3) or 0
            betCoins = betCoinsPos1 + betCoinsPos2 + betCoinsPos3

            love0 = daobase.executeMixCmd('scard', playerLovesHomeKey % (date, matchId))
            love1 = daobase.executeMixCmd('scard', playerLovesAwayKey % (date, matchId))

            lovestatus0 = daobase.executeMixCmd('sismember', playerLovesHomeKey % (date, matchId), userId)
            lovestatus1 = daobase.executeMixCmd('sismember', playerLovesAwayKey % (date, matchId), userId)

            homebetcoin = daobase.executeUserCmd(userId, 'hget', betHomeKey % userId,
                                                 '%s:%s' % (date, matchId)) or 0
            avebetcoin = daobase.executeUserCmd(userId, 'hget', betAveKey % userId, '%s:%s' % (date, matchId)) or 0
            awaybetcoin = daobase.executeUserCmd(userId, 'hget', betAwayKey % userId,
                                                 '%s:%s' % (date, matchId)) or 0

            homesupportrate = '0%支持'
            avesupportrate = '0%支持'
            awaysupportrate = '0%支持'

            if betCoins > 0:
                homesupportrate = '%.f' % (float(betCoinsPos1) * 100 / betCoins) + '%支持'
                avesupportrate = '%.f' % (float(betCoinsPos2) * 100 / betCoins) + '%支持'
                awaysupportrate = '%.f' % (float(betCoinsPos3) * 100 / betCoins) + '%支持'

            d = {'cell_type': 'main_list', 'date': date, 'datetime': j.get('timestamp'), 'type': 1,
                 'teamname0': homeTeamName, 'teampic0': homtTeamPic, 'teamname1': awayTeamName,
                 'teampic1': awayTeamPic, 'location': location, 'matchTime': j.get('timestamp'),
                 'homewin': odds[0], 'ave': odds[1], 'awaywin': odds[2], 'betcounts': betcounts,
                 'betCoins': betCoins, 'uuid': matchId, 'love0': love0, 'love1': love1, 'lovestatus0': lovestatus0,
                 'lovestatus1': lovestatus1, 'homesupportrate': homesupportrate, 'avesupportrate': avesupportrate,
                 'awaysupportrate': awaysupportrate, 'homebetcoin': homebetcoin, 'avebetcoin': avebetcoin,
                 'awaybetcoin': awaybetcoin}


        except:
            ftlog.warn('hallsportlottery.sportlotteryDetail',
                       'userId=', userId,
                       'date=', date,
                       'matchId=', matchId,
                       'type=', type)

    return d


class SportlotteryBadBetException(TYBizException):
    def __init__(self, message='请先选择下注金额'):
        super(SportlotteryBadBetException, self).__init__(-1, message)


class SportlotteryBetOverLimitException(TYBizException):
    def __init__(self, message='下注金额超过限制'):
        super(SportlotteryBetOverLimitException, self).__init__(-1, message)


class SportlotteryChipNotEnoughException(TYBizException):
    def __init__(self, message='费用不足'):
        super(SportlotteryChipNotEnoughException, self).__init__(-1, message)


class SportlotteryBetPosErrorException(TYBizException):
    def __init__(self, message='押注位置错误'):
        super(SportlotteryBetPosErrorException, self).__init__(-1, message)


class SportlotteryLovePosErrorException(TYBizException):
    def __init__(self, message='点赞位置错误'):
        super(SportlotteryLovePosErrorException, self).__init__(-1, message)


class SportlotteryBeGetRewardException(TYBizException):
    def __init__(self, message='您已经领取过此奖励'):
        super(SportlotteryBeGetRewardException, self).__init__(-1, message)


class SportlotteryForbidBetException(TYBizException):
    def __init__(self, message='不在下注状态，禁止下注'):
        super(SportlotteryForbidBetException, self).__init__(-1, message)


class SportlotteryMatchOverException(TYBizException):
    def __init__(self, message='比赛已经结束'):
        super(SportlotteryMatchOverException, self).__init__(-1, message)


def addChip(userId, gameId, clientId, chip, leagueId, homewin, winPos):
    trueDelta, final = userchip.incrChip(userId, gameId, chip,
                                         userchip.ChipNotEnoughOpMode.NOOP,
                                         pokerconf.biEventIdToNumber("HALL_SPORTLOTTERY"),
                                         leagueId, clientId, 0, int(homewin*100), winPos)
    if trueDelta != 0:
        datachangenotify.sendDataChangeNotify(gameId, userId, 'udata')

    ftlog.hinfo('sportlottery addchip',
                'userId=', userId,
                'chip=', chip,
                'trueDelta=', trueDelta,
                'final=', final)

    return trueDelta, final


def sportlotteryBet(gameId, clientId, userId, date, matchId, party, coin):
    if coin <= 0:
        raise SportlotteryBadBetException()
    
    if party not in (1, 2, 3):
        raise SportlotteryBetPosErrorException()
    
    jstr = daobase.executeMixCmd('hget', leagueDaykey % date, matchId)
    leagueId = 0 #
    homewin = 0.0
    if jstr:
        j = strutil.loads(jstr)
        leagueId = int(j.get('leagueId', 0))
        homewin = float(j.get('odds', ['0', '0', '0'])[0])
        if j.get('status') not in BET_STATUS:
            raise SportlotteryForbidBetException()
    else:
        raise SportlotteryMatchOverException()

    homeBet = daobase.executeUserCmd(userId, 'hget', betHomeKey % userId, '%s:%s' % (date, matchId)) or 0
    aveBet = daobase.executeUserCmd(userId, 'hget', betAveKey % userId, '%s:%s' % (date, matchId)) or 0
    awayBet = daobase.executeUserCmd(userId, 'hget', betAwayKey % userId, '%s:%s' % (date, matchId)) or 0
    
    # 获取总金额
    totalBet = int(homeBet) + int(aveBet) + int(awayBet)
    if totalBet + coin > SportlotteryConf.totalBetLimit():
        tips = SportlotteryConf.totalBetLimitTips()
        if tips:
            raise SportlotteryBetOverLimitException(tips)
        raise SportlotteryBetOverLimitException()
    
    trueDelta, final = addChip(userId, gameId, clientId, -coin, leagueId, homewin, party)

    if abs(trueDelta) < coin:
        raise SportlotteryChipNotEnoughException()
        
    if party == 1:
        daobase.executeUserCmd(userId, 'hincrby', betHomeKey % userId, '%s:%s' % (date, matchId), coin)
    elif party == 2:
        daobase.executeUserCmd(userId, 'hincrby', betAveKey % userId, '%s:%s' % (date, matchId), coin)
    elif party == 3:
        daobase.executeUserCmd(userId, 'hincrby', betAwayKey % userId, '%s:%s' % (date, matchId), coin)
    else:
        raise SportlotteryBetPosErrorException()

    # 联赛下注总人数
    daobase.executeMixCmd('sadd', leagueBetPlayersKey % (date, matchId), userId)
    # 联赛下注总钱数
    daobase.executeMixCmd('hincrby', leagueBetChipsKey % (date, matchId), party, coin)

    return final


def sportlotteryLove(userId, date, matchId, love):
    jstr = daobase.executeMixCmd('hget', leagueDaykey % date, matchId)
    if jstr:
        j = strutil.loads(jstr)
        if j['status'] not in BET_STATUS:
            raise SportlotteryForbidBetException()
    else:
        raise SportlotteryMatchOverException()

    if love == 0:
        if 1 == daobase.executeMixCmd('sismember', playerLovesHomeKey % (date, matchId), userId):
            return -1, '已经点过赞了'
        else:
            daobase.executeMixCmd('sadd', playerLovesHomeKey % (date, matchId), userId)

    elif love == 1:
        if 1 == daobase.executeMixCmd('sismember', playerLovesAwayKey % (date, matchId), userId):
            return -1, '已经点过赞了'
        else:
            daobase.executeMixCmd('sadd', playerLovesAwayKey % (date, matchId), userId)

    else:
        raise SportlotteryLovePosErrorException()

    return 0, '点赞成功'


def doMySportlottery(userId):
    option = ['主胜', '平', '客胜']
    noOpenKeyList = [noOpenHomeKey, noOpenAveKey, noOpenAwayKey]
    betKeyList = [betHomeKey, betAveKey, betAwayKey]
    for betkey in betKeyList:
        betpos = betKeyList.index(betkey) + 1
        dateMatchIdList = daobase.executeUserCmd(userId, 'hkeys', betkey % userId)
        if len(dateMatchIdList) > 0:
            _31deltadays = datetime.timedelta(days=31)
            now = datetime.datetime.now()
            _30beforeday = (now - _31deltadays).strftime('%Y-%m-%d')

            nowDate = now.strftime('%Y-%m-%d')

            for dateMatchIdStr in dateMatchIdList:
                date, matchId = dateMatchIdStr.split(':')[0], dateMatchIdStr.split(':')[1]
                matchId = int(matchId)
                if date <= _30beforeday:
                    daobase.executeUserCmd(userId, 'hdel', betkey % userId, dateMatchIdStr)
                    continue

                jstr = daobase.executeMixCmd('hget', leagueDaykey % date, matchId)
                if jstr:
                    j = strutil.loads(jstr)

                    betCoins = daobase.executeUserCmd(userId, 'hget', betkey % userId, dateMatchIdStr) or 0

                    if j['status'] in CANCEL_RESULTS:
                        daobase.executeUserCmd(userId, 'hdel', betkey % userId, dateMatchIdStr)

                        if betCoins > 0:
                            leagueId = int(j.get('leagueId', 0))
                            homewin = float(j.get('odds', ['0', '0', '0'])[0])
                            addChip(userId, HALL_GAMEID, sessiondata.getClientId(userId), betCoins, leagueId, homewin, betpos)
                            ftlog.hinfo('doMySportlottery addchip',
                                        'userId=', userId,
                                        'chip=', betCoins,
                                        'betkey=', betkey % userId,
                                        'dateMatchIdStr=', dateMatchIdStr)
                        continue

                    teamsMap = SportlotteryConf.teamsMap()
                    homeTeamMap = teamsMap.get(j.get('homeTeamId'))
                    homeTeamName = homeTeamMap.get('name')
                    homtTeamPic = homeTeamMap.get('pic')
                    awayTeamMap = teamsMap.get(j.get('awayTeamId'))
                    awayTeamName = awayTeamMap.get('name')
                    awayTeamPic = awayTeamMap.get('pic')

                    love0 = daobase.executeMixCmd('scard', playerLovesHomeKey % (date, matchId))
                    love1 = daobase.executeMixCmd('scard', playerLovesAwayKey % (date, matchId))

                    leagueDict = SportlotteryConf.getLeague(j.get('leagueId'))
                    location = leagueDict.get('shortName')

                    odds = j.get('odds', ['0', '0', '0'])

                    d = {'cell_type': 'reward_list', 'date': date, 'type': 1,
                         'teamname0': homeTeamName, 'teampic0': homtTeamPic, 'teamname1': awayTeamName,
                         'teampic1': awayTeamPic, 'location': location, 'love0': love0, 'love1': love1,
                         'matchTime': j.get('timestamp'), 'uuid': matchId, 'option': option[betpos - 1],
                         'odds': odds[betpos - 1], 'betCoins': betCoins}

                    if date > nowDate:
                        # 等待开奖
                        d['rewardstatus'] = 3

                        daobase.executeUserCmd(userId, 'hset', noOpenKeyList[betpos - 1] % userId, dateMatchIdStr,
                                               strutil.dumps(d))
                    elif date <= nowDate:
                        if j['status'] in RESULTS:
                            hscore, ascore = j['score'][0], j['score'][1]

                            daobase.executeUserCmd(userId, 'hdel', betkey % userId, dateMatchIdStr)

                            daobase.executeUserCmd(userId, 'hdel', noOpenKeyList[betpos - 1] % userId,
                                                   dateMatchIdStr)
                            if ((betpos == 1 and hscore > ascore)
                                or (betpos == 2 and hscore == ascore)
                                or (betpos == 3 and hscore < ascore)):
                                # 主胜
                                # 领取奖励
                                d['rewardstatus'] = 1
                                daobase.executeUserCmd(userId, 'hset', waitRewardKey % userId,
                                                       '%s:%s' % (date, matchId),
                                                       strutil.dumps(d))

                            else:
                                # 未猜中
                                d['rewardstatus'] = 2

                                nowinLen = daobase.executeUserCmd(userId, 'rpush', noWinKey % userId,
                                                                  strutil.dumps(d))
                                if nowinLen > 10:
                                    daobase.executeUserCmd(userId, 'ltrim', noWinKey % userId, -10, -1)


                        else:
                            # 等待开奖
                            d['rewardstatus'] = 3

                            daobase.executeUserCmd(userId, 'hset', noOpenKeyList[betpos - 1] % userId,
                                                   dateMatchIdStr,
                                                   strutil.dumps(d))


def sportlotteryRewardList(userId):
    # 对我的竞猜记录进行处理
    doMySportlottery(userId)

    rewardList = []


    noWinList = daobase.executeUserCmd(userId, 'lrange', noWinKey % userId, 0, -1)
    if len(noWinList) > 0:
        for nowin in noWinList:
            d = strutil.loads(nowin)
            rewardList.append(d)
    winList = daobase.executeUserCmd(userId, 'lrange', winkey % userId, 0, -1)
    if len(winList) > 0:
        for win in winList:
            d = strutil.loads(win)
            rewardList.append(d)

    for noOpenKey in [noOpenHomeKey, noOpenAveKey, noOpenAwayKey]:
        dateMatchIdList = daobase.executeUserCmd(userId, 'hkeys', noOpenKey % userId)
        if len(dateMatchIdList) > 0:
            for dateMatchIdStr in dateMatchIdList:
                jstr = daobase.executeUserCmd(userId, 'hget', noOpenKey % userId, dateMatchIdStr)
                if jstr:
                    j = strutil.loads(jstr)
                    rewardList.append(j)

    dateMatchIdList = daobase.executeUserCmd(userId, 'hkeys', waitRewardKey % userId)
    if len(dateMatchIdList) > 0:
        for dateMatchIdStr in dateMatchIdList:
            jstr = daobase.executeUserCmd(userId, 'hget', waitRewardKey % userId, dateMatchIdStr)
            if jstr:
                j = strutil.loads(jstr)
                rewardList.append(j)

    return rewardList[-30:]


_winResult = {
                '主胜':1,
                '平':2,
                '客胜':3
              }
def sportlotteryGetReward(gameId, clientId, userId, date, matchId):
    jstr = daobase.executeUserCmd(userId, 'hget', waitRewardKey % userId, '%s:%s' % (date, matchId))
    if jstr:
        d = strutil.loads(jstr)
        betCoins = d['betCoins']
        odds = d['odds']
        delta = int(betCoins) * float(odds)
        leagueId = int(d.get('leagueId', 0))
        homewin = float(d.get('odds', ['0', '0', '0'])[0])
        betpos = _winResult.get(d.get('option', ''), 0)
            
        _, final = addChip(userId, gameId, clientId, int(delta), leagueId, homewin, betpos)
        daobase.executeUserCmd(userId, 'hdel', waitRewardKey % userId, '%s:%s' % (date, matchId))
        # 猜中
        d['rewardstatus'] = 4
        winLen = daobase.executeUserCmd(userId, 'rpush', winkey % userId, strutil.dumps(d))
        if winLen > 10:
            daobase.executeUserCmd(userId, 'ltrim', winkey % userId, -10, -1)

        return final
    else:
        raise SportlotteryBeGetRewardException()
