# -*- coding:utf-8 -*-
'''
Created on 2017年5月8日

@author: wangyonghui
'''
import random

from dizhu.games import matchutil
from dizhucomm.core import cardrule
from dizhucomm.core.policies import FirstCallPolicy, FirstCallPolicyRandom, SendCardsPolicy
import freetime.util.log as ftlog
from dizhucomm.playmodes.base import SendCardsPolicy3PlayerDefault


class GroupMatchFirstCallPolicyInturn(FirstCallPolicy):
    '''
    首叫策略，轮流首叫
    '''
    def chooseFirstCall(self, table):
        tableInfo = table.matchTableInfo
        gameRound = table.gameRound
        seats = gameRound.seats
        for seat in seats:
            if seat.player.firstCallFalg == 1:
                if ftlog.is_debug():
                    ftlog.debug('GroupMatchFirstCallPolicyInturn.chooseFirstCall',
                                'roomId=', table.roomId,
                                'tableId=', table.tableId,
                                'stepType=', tableInfo['step']['type'],
                                'matchId=', tableInfo['matchId'],
                                'currCardCount=', tableInfo['seats'][0]['cardCount'],
                                'userIds=', [s.player.userId for s in seats],
                                'callPlayerUserId=', seat.player.userId)
                seat.player.firstCallFalg = 0
                return seat

        ftlog.warn('GroupMatchFirstCallPolicyInturn.chooseFirstCall inturn calling warning',
                   'roomId=', table.roomId,
                   'tableId=', table.tableId,
                   'matchId=', tableInfo['matchId'],
                   'userIds=', [s.player.userId for s in seats])

        index = random.randint(0, len(gameRound.seats) - 1)
        return gameRound.seats[index]


class GroupMatchFirstCallPolicyImpl(FirstCallPolicy):
    '''
    首次叫策略， 依据配置文件动态选择选择不同实现
    '''
    def __init__(self):
        self._firstCallPolicyMap = {
            'inturn': GroupMatchFirstCallPolicyInturn(),
            'random': FirstCallPolicyRandom()
        }

    def chooseFirstCall(self, table):
        tableInfo = table.matchTableInfo
        firstCallPolicyConf = tableInfo['step']['callType']
        return self._firstCallPolicyMap[firstCallPolicyConf].chooseFirstCall(table)


class SendCardsPolicy3PlayerChampionLimit(SendCardsPolicy):
    '''
    发牌策略： 得过冠军一定条件内，好牌需要重新洗牌
    '''
    def sendCards(self, table):
        defaultSendCards = SendCardsPolicy3PlayerDefault()
        defaultSendCards.sendCards(table)

        limitConf = matchutil.getMatchChampionLimitConf(table.roomId)
        if limitConf.get('open', 0) == 0:
            return

        limitCount = limitConf.get('shuffleCountLimit', 3)
        cardRule = cardrule.CardDiZhuLaizi3Player()
        for i in range(limitCount):
            for index, seat in enumerate(table.gameRound.seats):
                if seat.player.championLimitFlag:
                    # 达到条件并且手牌为 ≥两炸 或 飞机+王炸 重新发牌
                    reducedCards = cardrule.ReducedCards.reduceHandCards(cardRule, seat.status.cards)
                    if (cardrule.CardFinder.findHuojian(cardRule, reducedCards) and cardrule.CardFinder.findFeijiCount(cardRule, reducedCards)) or \
                                    cardrule.CardFinder.findZhadanCount(cardRule, reducedCards) >= 2:
                        defaultSendCards.sendCards(table)
                        if ftlog.is_debug():
                            ftlog.debug('SendCardsPolicy3PlayerChampionLimit.sendCards userId=', seat.player.userId,
                                        'gameId=', table.gameId,
                                        'roomId=', table.roomId,
                                        'huojian=', cardrule.CardFinder.findHuojian(cardRule, reducedCards),
                                        'feijiCount=', cardrule.CardFinder.findFeijiCount(cardRule, reducedCards),
                                        'zhadanCount=', cardrule.CardFinder.findZhadanCount(cardRule, reducedCards),
                                        'cards=', ''.join(cardRule.toHumanCards(seat.status.cards)))
                        break
