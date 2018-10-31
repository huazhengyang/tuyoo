# -*- coding:utf-8 -*-
'''
Created on 2018年1月30日

@author: zhaojiangang
'''

import datetime

from hall.entity import hallsportlottery
from hall.entity.hallconf import HALL_GAMEID
from poker.entity.dao import daobase, sessiondata
from poker.util import strutil
import freetime.util.log as ftlog


def doMySportlottery(userId):
    option = ['主胜', '平', '客胜']
    noOpenKeyList = [hallsportlottery.noOpenHomeKey, hallsportlottery.noOpenAveKey, hallsportlottery.noOpenAwayKey]
    betKeyList = [hallsportlottery.betHomeKey, hallsportlottery.betAveKey, hallsportlottery.betAwayKey]
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

                jstr = daobase.executeMixCmd('hget', hallsportlottery.leagueDaykey % date, matchId)
                if jstr:
                    j = strutil.loads(jstr)

                    betCoins = daobase.executeUserCmd(userId, 'hget', betkey % userId, dateMatchIdStr) or 0

                    if j['status'] in hallsportlottery.CANCEL_RESULTS:
                        daobase.executeUserCmd(userId, 'hdel', betkey % userId, dateMatchIdStr)

                        if betCoins > 0:
                            hallsportlottery.addChip(userId, HALL_GAMEID, sessiondata.getClientId(userId), betCoins)
                            ftlog.hinfo('doMySportlottery addchip',
                                        'userId=', userId,
                                        'chip=', betCoins,
                                        'betkey=', betkey % userId,
                                        'dateMatchIdStr=', dateMatchIdStr)
                        continue

                    teamsMap = hallsportlottery.SportlotteryConf.teamsMap()
                    homeTeamMap = teamsMap.get(j.get('homeTeamId'))
                    homeTeamName = homeTeamMap.get('name')
                    homtTeamPic = homeTeamMap.get('pic')
                    awayTeamMap = teamsMap.get(j.get('awayTeamId'))
                    awayTeamName = awayTeamMap.get('name')
                    awayTeamPic = awayTeamMap.get('pic')

                    love0 = daobase.executeMixCmd('scard', hallsportlottery.playerLovesHomeKey % (date, matchId))
                    love1 = daobase.executeMixCmd('scard', hallsportlottery.playerLovesAwayKey % (date, matchId))

                    leagueDict = hallsportlottery.SportlotteryConf.getLeague(j.get('leagueId'))
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
                        if j['status'] in hallsportlottery.RESULTS:
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
                                daobase.executeUserCmd(userId, 'hset', hallsportlottery.waitRewardKey % userId,
                                                       '%s:%s' % (date, matchId),
                                                       strutil.dumps(d))

                            else:
                                # 未猜中
                                d['rewardstatus'] = 2

                                nowinLen = daobase.executeUserCmd(userId, 'rpush', hallsportlottery.noWinKey % userId,
                                                                  strutil.dumps(d))
                                if nowinLen > 10:
                                    daobase.executeUserCmd(userId, 'ltrim', hallsportlottery.noWinKey % userId, -10, -1)


                        else:
                            # 等待开奖
                            d['rewardstatus'] = 3

                            daobase.executeUserCmd(userId, 'hset', noOpenKeyList[betpos - 1] % userId,
                                                   dateMatchIdStr,
                                                   strutil.dumps(d))

hallsportlottery.doMySportlottery = doMySportlottery


