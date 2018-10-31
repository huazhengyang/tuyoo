# -*- coding=utf-8 -*-
# Author:        luojihui@163.com
# Created:       17/12/20 下午3:41
import datetime
from poker.entity.dao import daobase
from poker.util import  strutil

import freetime.util.log as ftlog
from hall.entity import hallsportlottery
from hall.entity.hallsportlottery import leagueDaykey


def endSprotManual(res):
    ftlog.info('hall_sport_manual_end start...'
                'matchId=', res.matchId,
               'resultlist=', res.score,
               'status=', res.status)

    if hallsportlottery._sportlotteryMap:
        spl = hallsportlottery._sportlotteryMap.get(res.matchId, None)
        if not spl:
            date = datetime.datetime.fromtimestamp(res.timestamp).strftime('%Y-%m-%d')
            jstr = daobase.executeMixCmd('hget', leagueDaykey % date, res.matchId)
            if jstr:
                j = strutil.loads(jstr)
                if j.get('status', -1) not in hallsportlottery.RESULTS:
                    return -2
                spl = hallsportlottery.Sportlottery()
                spl.fromDict(j)
        if spl:
            if spl.sportOdds and getattr(spl.sportOdds, 'timer', None):
                spl.sportOdds.timer.cancel()
            if spl.sportResult and getattr(spl.sportResult, 'timer', None):
                spl.sportResult.timer.cancel()
            if getattr(spl, 'timer', None):
                spl.timer.cancel()

            spl.score = res.score
            spl.status = res.status
            spl.odds = res.odds
            spl.save()
            hallsportlottery._sportlotteryMap.pop(res.matchId, None)
        else:
            return -4
                
                    
    ftlog.info('hall_sport_manual_end.endSprotManual OK'
               'spl', spl)
    return 0


class Result(object):
    def __init__(self, matchId=0, leagueId=0, homeTeamId=0, awayTeamId=0, timestamp=0, score=[], odds=[], status=0):
        self.matchId = matchId
        self.leagueId = leagueId
        self.homeTeamId = homeTeamId
        self.awayTeamId = awayTeamId
        self.timestamp = timestamp
        self.score = score
        self.odds = odds
        self.status = status

    @classmethod
    def decodeFromDict(cls, d):
        res = Result()
        res.matchId = d.get('matchId', 0)
        res.leagueId = d.get('leagueId', 0)
        res.homeTeamId = d.get('homeTeamId', 0)
        res.awayTeamId = d.get('awayTeamId', 0)
        res.timestamp = d.get('timestamp', 0)
        res.timestamp = d.get('status', 0)
        res.score = d.get('score', [0, 0])
        res.odds = d.get('odds', ['0', '0', '0'])
        
        return res.check()

    def check(self):
        if isinstance(self.matchId, int) and \
            isinstance(self.leagueId, int) and \
            isinstance(self.homeTeamId, int) and \
            isinstance(self.awayTeamId, int) and \
            isinstance(self.timestamp, int) and \
            isinstance(self.score, list) and \
            isinstance(self.odds, list) and \
            isinstance(self.status, int) and \
            self.matchId > 0 and self.leagueId > 0 and \
            self.homeTeamId > 0 and self.awayTeamId > 0 and \
            self.timestamp > 0 and len(self.score) == 2 and \
            len(self.odds) == 3:
            
            return self
        
        return None


#matchId, leagueId, homeTeamId, awayTeamId, timestamp, score, odds, status
def doResultOne(matchId, leagueId, homeTeamId, awayTeamId, timestamp, score, odds, status):
    try:
        res = Result(matchId, leagueId, homeTeamId, awayTeamId, timestamp, score, odds, status).check()
        if res:
            return endSprotManual(res)
    except:
        ftlog.error('hall_sport_manual_End.testOne Error')
        return -3



    