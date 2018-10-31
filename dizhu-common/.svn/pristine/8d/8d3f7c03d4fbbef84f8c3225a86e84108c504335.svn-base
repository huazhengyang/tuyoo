# -*- coding:utf-8 -*-
'''
Created on 2016年12月22日

@author: zhaojiangang
'''
import random

from dizhucomm.core.base import TableStateMachine
from dizhucomm.core.const import CallResult
from dizhucomm.core.exceptions import BadCallException
from dizhucomm.core.playmode import GameRound
from dizhucomm.core.policies import CallPolicy, SendCardsPolicy, PunishPolicy, \
    SettlementPolicy, GameResult
from dizhucomm.core.state import TableStateIdle, TableStateCalling, \
    TableStatePlaying, TableStateFinal, TableStateNongminJiabei, \
    TableStateDizhuJiabei, TableStateHuanpai
from freetime.util import log as ftlog
from hall.entity import hallvip
from poker.entity.configure import gdata
from poker.entity.dao import gamedata


class CallPolicyClassic3Player(CallPolicy):
    '''
    经典三人叫地主策略
    '''
    _VALID_CALLS = [0, 1, 2, 3]
    
    def call(self, table, callValue, oper):
        gameRound = table.gameRound
        seats = gameRound.seats
        assert(len(seats) == 3)
        assert(gameRound.curOpSeat)
        # 有状态机控制，不可能>=3
        assert(len(gameRound.callList) < 3)
        
        # 必须是0-3分，0表示不叫
        if callValue not in self._VALID_CALLS:
            # TODO
            raise BadCallException()

        # if callValue == 0 and table.runConf.grab == 0 and table.room.roomConf['playMode'] in ["wild", "quick_laizi"] and oper == 1 and not gameRound.lastEffectiveCall:
        #     # 双王，或者4个2 必须叫地主
        #     raise BadCallException()

        if (gameRound.lastEffectiveCall is not None
            and callValue > 0
            and callValue <= gameRound.lastEffectiveCall[1]):
            # 叫分只能大
            raise BadCallException()
        
        gameRound.addCall(gameRound.curOpSeat, callValue)
        if callValue > 0:
            gameRound.callMulti = callValue
            
        # 所有人都叫过地主了，或者已经叫了3分
        if (len(gameRound.callList) >= 3
            or (gameRound.lastEffectiveCall and gameRound.lastEffectiveCall[1] >= 3)):
            if not gameRound.lastEffectiveCall:
                return CallResult.ABORT, None
            gameRound.dizhuSeat = gameRound.lastEffectiveCall[0]
            return CallResult.FINISH, None
        return CallResult.CALLING, gameRound.curOpSeat.next
    
class CallPolicyHappy3Player(CallPolicy):
    '''
    欢乐三人叫地主策略
    '''
    _VALID_CALLS = [0, 1]
    
    def __init__(self, isAddMulti=False):
        self.isAddMulti = isAddMulti
        
    def findCallItem(self, table, seat):
        for item in table.gameRound.callList:
            if item[0] == seat:
                return item
        return None
    
    def call(self, table, callValue, oper):
        '''
        玩家叫地主
        @return: (CallResult, NextCallSeat)
        XXX
        XXV
        XVVX
        XVVV
        VVVV
        VVVX
        VVXV
        VVXX
        VXVV
        VXVX
        '''
        gameRound = table.gameRound
        assert(gameRound.curOpSeat)
        # 有状态机控制，不可能>=4
        assert(len(gameRound.callList) < 4)
        alreadyCall = self.findCallItem(table, gameRound.curOpSeat)
        # 只有首个有效叫地主的人在别人抢了之后还有一次抢的机会
        if (alreadyCall and (len(gameRound.effectiveCallList) < 2
            or gameRound.curOpSeat != gameRound.firstEffectiveCall[0])):
            ftlog.warn('CallPolicyHappy3Player.call',
                       'roomId=', table.roomId,
                       'tableId=', table.tableId,
                       'curSeat=', (gameRound.curOpSeat.userId, gameRound.curOpSeat.seatId),
                       'callValue=', callValue,
                       'callList=', [(item[0].userId, item[0].seatId, item[1]) for item in gameRound.callList],
                       'effectiveCallList=', [(item[0].userId, item[0].seatId, item[1]) for item in gameRound.effectiveCallList])
            raise BadCallException()
        
        if callValue not in self._VALID_CALLS:
            raise BadCallException()
    
        gameRound.addCall(gameRound.curOpSeat, callValue)
        
        if callValue > 0:
            if len(gameRound.effectiveCallList) == 1:
                gameRound.callMulti = table.runConf.firstCallValue
            else:
                if self.isAddMulti:
                    gameRound.callMulti += 1
                else:
                    gameRound.callMulti *= 2

        if len(gameRound.callList) == 3:
            # 没人叫地主
            if len(gameRound.effectiveCallList) == 0:
                return CallResult.ABORT, None
            
            # 只有一个人叫了地主，这个人就是地主
            if len(gameRound.effectiveCallList) == 1:
                gameRound.dizhuSeat = gameRound.lastEffectiveCall[0]
                return CallResult.FINISH, None
            
            # 两个以上的人叫了地主，下一个叫地主的人为首个有效叫地主的人
            return CallResult.CALLING, gameRound.firstEffectiveCall[0]
        elif len(gameRound.callList) == 4:
            assert(gameRound.lastEffectiveCall)
            gameRound.dizhuSeat = gameRound.lastEffectiveCall[0]
            return CallResult.FINISH, None
        
        return CallResult.CALLING, gameRound.curOpSeat.next


class CallPolicyLaizi(CallPolicy):
    def call(self, table, callValue, oper):
        if table.runConf.grab == 0:
            # 经典玩儿法
            return CallPolicyClassic3Player().call(table, callValue, oper)
        else:
            # 欢乐玩儿法
            return CallPolicyHappy3Player().call(table, callValue, oper)

        
class SendCardsPolicy3PlayerRandom(SendCardsPolicy):
    def sendCards(self, table):
        seats = table.gameRound.seats
        assert(len(seats) == 3)
        cards = [i for i in xrange(54)]
        random.shuffle(cards)
        seats[0].status.cards = cards[0:17]
        seats[1].status.cards = cards[17:34]
        seats[2].status.cards = cards[34:51]
        table.gameRound.baseCards = cards[51:]

class SendCardsPolicyUserSetting(object):
    @classmethod
    def sendCardsToUserIds(cls, gameId, tableId, userIds):
        bcards = []
        final_bcards = []
        allCards = set([c for c in xrange(54)])
        if len(userIds) == 2:
            kick_out_card = set([2, 3, 15, 16, 28, 29, 41, 42])
            allCards -= kick_out_card
        ret = [[] for _ in xrange(len(userIds) + 1)]
        try:
            for i, userId in enumerate(userIds):
                cards, bcards = gamedata.getGameAttrs(userId, gameId, ['test.cards', 'test.bcards'])
                if cards:
                    cards = cls.decodeCards(cards)
                    if len(cards) > 17:
                        cards = cards[0:17]
                    cards = cls._sendCards(cards, allCards)
                    cards = cls._buqiCards(cards, allCards, 17)
                    ret[i] = list(cards)

                if not final_bcards and bcards:
                    final_bcards = cls.decodeCards(bcards)
                    if len(final_bcards) > 3:
                        final_bcards = final_bcards[0:3]

            if final_bcards:
                final_bcards = cls._sendCards(final_bcards, allCards)

            final_bcards = cls._buqiCards(final_bcards, allCards, 3)
            ret[-1] = list(final_bcards)

            for i in xrange(len(userIds)):
                if not ret[i] or len(ret[i]) != 17:
                    ret[i] = list(cls._buqiCards(ret[i], allCards, 17))

            if ftlog.is_debug():
                ftlog.debug('playmodes.base.SendCardPolicyUserId.sendCards tableId=', tableId, 'userIds=', userIds, 'cards=', ret)
            return ret
        except:
            ftlog.error('sendCards.sendCardsToAllUserIds error')
        return None
    
    @classmethod
    def decodeCards(cls, cardsStr):
        ret = set()
        cards = cardsStr.split(',')
        for c in cards:
            card = int(c.strip())
            if card < 0 or card >= 54:
                raise Exception('card must in [0, 54)')
            ret.add(card)
        return list(ret)
    
    @classmethod
    def _buqiCards(cls, cards, allCards, count):
        if not cards:
            cards = set()
        diffCount = count - len(cards)
        if diffCount > 0:
            for _ in xrange(diffCount):
                if len(allCards) > 0:
                    allCardList = list(allCards)
                    index = random.randint(0, len(allCardList) - 1)
                    c = allCardList[index]
                    cards.add(c)
                    allCards.remove(c)
        return cards
    
    @classmethod
    def _sendCards(cls, needCards, allCards):
        cards = set()
        for c in needCards:
            if c in allCards:
                cards.add(c)
                allCards.remove(c)
        return cards


class SendCardsPolicyFillAll(SendCardsPolicy):
    '''
    1. 从最小牌开始遍历，至少取到3张顺，但不能取到最小5顺，优先补小牌
    2. 连续牌字前2位起的双对，小对补对
    3. 连续牌字第3位起的双对，补单顺
    4. 若遍历起始为3条或炸，则从下张牌字开始执行逻辑
    5. 若遍历过程中遇炸，且此时遍历不足5张，则从下张牌字开始执行逻辑
    6. 若遍历过程中遇连续三条，且此时遍历不足5张，则从下张牌开始执行逻辑
    7. 有双炸的话，不处理
    8. 没人各发15张
    '''
    @classmethod
    def sendCards(cls, table):
        sendCardConf = table.runConf.sendCardConf
        randFillAll = sendCardConf.get('RAND_FILL_ALL', 0)
        randomCards = cls.getShuffleCardList()
        cardsA = randomCards[:15]
        cardsB = randomCards[15:30]
        cardsC = randomCards[30:45]
        cardsPool = randomCards[45:]

        if ftlog.is_debug():
            cardsA.sort(key=cls.getCardPoint)
            cardsB.sort(key=cls.getCardPoint)
            cardsC.sort(key=cls.getCardPoint)
            cardsPool.sort(key=cls.getCardPoint)
            ftlog.debug('SendCardsPolicyFillAll.sendCards init',
                        'roomId=', table.roomId,
                        'tableId=', table.tableId,
                        'randFillAll=', randFillAll,
                        'userIds=', [seat.player.userId for seat in table.gameRound.seats],
                        'cardsA=', list(map(cls.cardToHuman, cardsA)),
                        'cardsB=', list(map(cls.cardToHuman, cardsB)),
                        'cardsC=', list(map(cls.cardToHuman, cardsC)),
                        'baseCards=', list(map(cls.cardToHuman, cardsPool)))

        cardsA, cardsPool, supplyCardA = cls.supplementCard(cardsA, cardsPool)
        cardsB, cardsPool, supplyCardB = cls.supplementCard(cardsB, cardsPool)
        cardsC, cardsPool, supplyCardC = cls.supplementCard(cardsC, cardsPool)

        if ftlog.is_debug():
            cardsA.sort(key=cls.getCardPoint)
            cardsB.sort(key=cls.getCardPoint)
            cardsC.sort(key=cls.getCardPoint)
            cardsPool.sort(key=cls.getCardPoint)
            ftlog.debug('SendCardsPolicyFillAll.sendCards add',
                        'roomId=', table.roomId,
                        'tableId=', table.tableId,
                        'randFillAll=', randFillAll,
                        'userIds=', [seat.player.userId for seat in table.gameRound.seats],
                        'cardsA supply=', cls.cardToHuman(supplyCardA) if supplyCardA else None,
                        'cardsB supply=', cls.cardToHuman(supplyCardB) if supplyCardB else None,
                        'cardsC supply=', cls.cardToHuman(supplyCardC) if supplyCardC else None,
                        'baseCards=', list(map(cls.cardToHuman, cardsPool)))

        cardsA, cardsPool = cls.getLeftCards(cardsA, cardsPool, 2 if supplyCardA is None else 1)
        cardsB, cardsPool = cls.getLeftCards(cardsB, cardsPool, 2 if supplyCardB is None else 1)
        cardsC, cardsPool = cls.getLeftCards(cardsC, cardsPool, 2 if supplyCardC is None else 1)

        if ftlog.is_debug():
            cardsA.sort(key=cls.getCardPoint)
            cardsB.sort(key=cls.getCardPoint)
            cardsC.sort(key=cls.getCardPoint)
            cardsPool.sort(key=cls.getCardPoint)
            ftlog.debug('SendCardsPolicyFillAll.sendCards final',
                        'roomId=', table.roomId,
                        'tableId=', table.tableId,
                        'randFillAll=', randFillAll,
                        'userIds=', [seat.player.userId for seat in table.gameRound.seats],
                        'cardsA final=', list(map(cls.cardToHuman, cardsA)),
                        'cardsB final=', list(map(cls.cardToHuman, cardsB)),
                        'cardsC final=', list(map(cls.cardToHuman, cardsC)),
                        'baseCards=', list(map(cls.cardToHuman, cardsPool)))

        userCardsList = [cardsA, cardsB, cardsC, cardsPool]

        for index, seat in enumerate(table.gameRound.seats):
            seat.status.cards = userCardsList[index]
        # 设置底牌
        table.gameRound.baseCards = userCardsList[-1]

    @classmethod
    def supplementCard(cls, cards, pool, length=5):
        points = list(cls.handleCardsPointIntersection(cards))
        points.sort()
        if len(points) >= length:
            for i in range(0, len(points) - (length - 1)):
                tempList = points[i:length+i]
                if tempList[-1] - tempList[0] == length - 1:
                    break
                if tempList[-1] - tempList[0] == length:
                    cmpL = range(points[i], points[i] + length)
                    tempList.pop()
                    cardPoint = list(set(cmpL) ^ set(tempList))[0]
                    needCards = cls.getCardsByPoint(cardPoint)
                    for card in needCards:
                        if card in pool:
                            cards.append(card)
                            pool.remove(card)
                            return cards, pool, card
        return cards, pool, None

    @classmethod
    def getLeftCards(cls, cards, pool, needCard):
        for i in range(needCard):
            c = random.choice(pool)
            cards.append(c)
            pool.remove(c)
        return cards, pool

    @classmethod
    def getShuffleCardList(cls):
        '''洗牌'''
        cards = range(0, 54)
        random.shuffle(cards)
        return cards

    @classmethod
    def getCardPoint(cls, card):
        '''获取牌的点数'''
        if card == 52:
            return 13
        if card == 53:
            return 14
        card = card % 13
        return card - 2 if card - 2 >= 0 else card - 2 + 13

    @classmethod
    def getCardsByPoint(cls, point):
        '''获得同一点数的4张牌'''
        if point == 13:
            return 52
        if point == 14:
            return 53
        if point in [11, 12]:
            return list(map(lambda x: x*13 + point - 11, range(4)))
        return list(map(lambda x: x*13 + point + 2, range(4)))

    @classmethod
    def cardToHuman(cls, card):
        '''转换为人类视角'''
        point = cls.getCardPoint(card)
        if point == 8:
            return 'J'
        elif point == 9:
            return 'Q'
        elif point == 10:
            return 'K'
        elif point == 11:
            return 'A'
        elif point == 12:
            return '2'
        elif point == 13:
            return 'joker'
        elif point == 14:
            return 'JOKER'
        else:
            return str(point + 3)

    @classmethod
    def getValidPoints(cls):
        '''获取所有有效的point'''
        return set(range(0,8))

    @classmethod
    def handleCardsPoints(cls, cards):
        '''将手牌转换为point'''
        points = list(map(cls.getCardPoint, cards))
        points.sort()
        return set(points)

    @classmethod
    def handleCardsPointIntersection(cls, cards):
        return cls.handleCardsPoints(cards) & cls.getValidPoints()

    
class SendCardsPolicy3PlayerDefault(SendCardsPolicy):
    GOODSEAT_LOOP_MIN = 4
    GOODSEAT_LOOP_MAX = 9
    
    def sendCards(self, table):
        seats = table.gameRound.seats
        assert (len(seats) == 3)
        goodCard = table.runConf.goodCard
        lucky = table.runConf.lucky
        sendCardConf = table.runConf.sendCardConf
        cards = None
        if gdata.enableTestHtml():
            userIds = [seat.userId for seat in table.gameRound.seats if seat.player]
            cards = SendCardsPolicyUserSetting.sendCardsToUserIds(table.gameId, table.tableId, userIds)

        if ftlog.is_debug():
            ftlog.debug('SendCardsPolicy3PlayerDefault.sendCards begin ......... tableId=', table.tableId,
                        'sendCardConf=', sendCardConf,
                        'goodCard=', goodCard,
                        'lucky=', lucky,
                        'enableTestHtml=', gdata.enableTestHtml(),
                        'cards=', cards)

        randFillAll = sendCardConf.get('RAND_FILL_ALL', 0)

        if not cards and random.randint(0, 100) < randFillAll and table.room.isMatch:
            SendCardsPolicyFillAll.sendCards(table)
        else:
            if not cards:
                if goodCard and not table.room.isMatch:
                    goodCardSeat, cards = self.sendCard2(table, sendCardConf)
                    if ftlog.is_debug():
                        ftlog.debug('SendCardsPolicy3PlayerDefault.sendCards',
                                    'tableId=', table.tableId,
                                    'sendCardConf=', sendCardConf,
                                    'cards=', cards,
                                    'goodCardSeat=', (goodCardSeat.userId, goodCardSeat.seatId) if goodCardSeat else None)
                else:
                    cards = self.sendCard1(3, lucky)
                    if ftlog.is_debug():
                        ftlog.debug('SendCardsPolicy3PlayerDefault.sendCards',
                                    'tableId=', table.tableId,
                                    'sendCardConf=', sendCardConf,
                                    'lucky=', lucky,
                                    'cards=', cards)
            for i, seat in enumerate(table.gameRound.seats):
                seat.status.cards = cards[i]
            # 设置底牌
            table.gameRound.baseCards = cards[-1]

    def getGoodSeatIndex(self, playCountList, config, otherPlayersCareerRound):
        goodList = []
        #modify by zw 2013-10-25 for 随机周期发好牌
        newPlayCount = config.get('NEWPLAY_COUNT', 5)
        newPlayLuck = config.get('NEWPLAY_LUCK', 90)
        loop = config.get('GOOD_LOOP', self.GOODSEAT_LOOP_MIN)
        loop_bottom = loop - 1
        loop_top = loop + 2
        
        if loop_bottom < self.GOODSEAT_LOOP_MIN:
            loop_bottom = self.GOODSEAT_LOOP_MIN
        if loop_top > self.GOODSEAT_LOOP_MAX :
            loop_top = self.GOODSEAT_LOOP_MAX

        newPlayerList = []
        otherPlayerList = []
        for i, playCount in enumerate(playCountList):
            #新手保护
            if playCount <= otherPlayersCareerRound and playCount != 0:
                otherPlayerList.append(i)
            if playCount == 0:  # 生涯第一局
                goodList.append(i)
                newPlayerList.append(i)
                if ftlog.is_debug():
                    ftlog.debug('SendCardsPolicy3PlayerDefault.getGoodSeatIndex newPlayerList',
                                'playCount=', playCount,
                                'addIndex=', i)
                continue
            elif playCount <= newPlayCount:
                newPlayerRatio = random.randint(1, 100)
                if newPlayerRatio < newPlayLuck:
                    goodList.append(i)
                    
                if ftlog.is_debug():
                    ftlog.debug('SendCardsPolicy3PlayerDefault.getGoodSeatIndex NewerSafe',
                                'playCountList=', playCountList,
                                'config=', config,
                                'newPlayCount=', newPlayCount,
                                'newPlayLuck=', newPlayLuck,
                                'loop=', (loop, loop_bottom, loop_top),
                                'playCount=', playCount,
                                'addIndex=', i)
                continue
            #随机周期
            if playCount % random.randint(loop_bottom, loop_top) == 0:
                if ftlog.is_debug():
                    ftlog.debug('SendCardsPolicy3PlayerDefault.getGoodSeatIndex Random',
                                'playCountList=', playCountList,
                                'config=', config,
                                'newPlayCount=', newPlayCount,
                                'newPlayLuck=', newPlayLuck,
                                'loop=', (loop, loop_bottom, loop_top),
                                'playCount=', playCount,
                                'addIndex=', i)
                goodList.append(i)

        if ftlog.is_debug():
            ftlog.debug('SendCardsPolicy3PlayerDefault.getGoodSeatIndex',
                        'playCountList=', playCountList,
                        'config=', config,
                        'newPlayCount=', newPlayCount,
                        'newPlayLuck=', newPlayLuck,
                        'loop=', (loop, loop_bottom, loop_top),
                        'goodList=', goodList,
                        'newPlayerList=', newPlayerList)
            
        # 如果只有一个符合好牌条件,则直接返回座位号
        if len(goodList) == 1:
            return goodList[0]
        
        # 优待生涯第一局的玩家，若有多个则随机选择
        if len(newPlayerList) > 0 and len(otherPlayerList) == 0:
            return newPlayerList[0] if len(newPlayerList) == 1 else random.choice(newPlayerList)
        
        # 如果都不符合好牌条件或有冲突，则按概率返回0
        ratio = random.randrange(0, 100, 1)
        rand_good = config.get('RAND_GOOD', 70)
        if ratio > rand_good:
            return -1
        
        # 如果都不符合好牌条件，则完全随机一个座位返回
        if len(goodList) == 0:
            return (ratio % 3)

        # 如果有冲突，则随机数值选择冲突座位
        return goodList[(ratio % len(goodList))]
    
    def sendCard1(self, seatCount, lucky):
        bomb_cards = []  # 预先发的炸弹扑克列表
        bomb_count = 0
        luck_seat = random.randint(0, 2)

        cards = []
        for i in xrange(seatCount + 1):
            cards.append([])
        cardindex = 0

        # 判断制造炸弹
        x = random.randint(1, 100)
        if x <= lucky:
            bomb_count = random.randint(1, 3)
            ls = [luck_seat, (luck_seat + 1) % 3, (luck_seat + 2) % 3]
            sbc = random.randint(1, 11)
            for bn in xrange(bomb_count):
                for cn in xrange(4): 
                    cards[ls[bn]].append(sbc + bn + cn * 13)
                    bomb_cards.append(sbc + bn + cn * 13)
            # print 'bomb_count=', bomb_count, 'luck_seat', luck_seat

        cl = self.getShuffleCardList(bomb_cards)
        for i in xrange(17):
            for j in xrange(seatCount):
                if i < 4:
                    if bomb_count == 0 or \
                        (bomb_count == 1 and j != luck_seat) or \
                        (bomb_count == 2 and j == (luck_seat + 2) % 3) or \
                        (bomb_count == 3 and j < 0):
                        cards[j].append(cl[cardindex])
                        cardindex += 1
                else:
                    cards[j].append(cl[cardindex])
                    cardindex += 1

        # 发送底牌
        for i in xrange(3):
            cards[seatCount].append(cl[cardindex])
            cardindex += 1
        return cards


    def sendCard2(self, table, config):
        '''
        tatal=[]
        '''
        otherPlayersCareerRound = table.runConf.datas.get('otherPlayersCareerRound', 3)
        #playCounts = [seat.player.datas.get('plays', 0) for seat in table.seats]
        #newPlayCount = config.get('NEWPLAY_COUNT', 5)
        playCounts = []
        for seat in table.seats:
            _seatPlayCount = seat.player.datas.get('plays', 0)
            vipLevel = hallvip.userVipSystem.getUserVip(seat.player.userId).vipLevel
            if vipLevel > 0:
                _seatPlayCount += config.get('NEWPLAY_COUNT', 5)
            playCounts.append(_seatPlayCount)


        seatIndex = self.getGoodSeatIndex(playCounts, config, otherPlayersCareerRound)
        
        if -1 == seatIndex:
            return None, self.DDZDealCard_Base(config)
        else:
            seatPlayCount = table.gameRound.seats[seatIndex].player.datas.get('plays', 0)
            # 生涯第一局好牌条件为 生涯第一局 且 无VIP
            newPlayer = False
            if seatPlayCount == 0 and not table.gameRound.seats[seatIndex].player.isRobotUser:
                userId = table.gameRound.seats[seatIndex].player.userId
                #from hall.entity import hallvip
                vipLevel = hallvip.userVipSystem.getUserVip(userId).vipLevel
                if not vipLevel:
                    newPlayer = True

                if ftlog.is_debug:
                    ftlog.debug('sendCard2. career first round. userId=', userId,
                                'seatPlayCount=', seatPlayCount,
                                'uservip=', vipLevel,
                                'newPlayer=', newPlayer)
                
            return table.gameRound.seats[seatIndex], self.DDZDealCard_GoodSeat(seatIndex, config, newPlayer)
    
    def getShuffleCardList(self, bc):
        card_list = list(set(range(54)) - set(bc))
        random.shuffle(card_list)
        return card_list
    
    def DDZDealCard_Base(self, config):
        # print "随机底牌"
        rand_bc1 = config.get('RAND_BC1', 50)
        rand_bc2 = config.get('RAND_BC2', 30)
        rand_bc3 = config.get('RAND_BC3', 20)
        
        total_rand_bc = rand_bc1 + rand_bc2 + rand_bc3
        if (total_rand_bc) != 100:
            rand_bc1 = (rand_bc1 * 100) // total_rand_bc
            rand_bc2 = (rand_bc2 * 100) // total_rand_bc
            rand_bc3 = 100 - rand_bc1 - rand_bc2
        base = []
        card = [[], [], []]
        pool = range(54)
        
        r = random.randrange(0, 100, 1)
        if r < rand_bc1:
            # print "三张相同底牌"
            basePoint = r % 13
            for i in range(0, 3):
                base.append(pool[basePoint + i * 13 - i])
                del pool[basePoint + i * 13 - i]
        elif r < (rand_bc2 + rand_bc1):
            # 底牌大王
            # print "双王底牌"
            base.append(53)
            del pool[53]
            base.append(52)
            del pool[52]
            base.append(r % 52)
            del pool[ r % 52]
        else:
            #大牌型底牌
            littlePool = [0, 13, 26, 39, 1, 14, 27, 40, 52, 53]
            littlePoolLen = len(littlePool)
            for i in range(0, 3):
                r = random.randint(1, littlePoolLen) - 1
                curCard=littlePool[r]
                base.append(curCard)
                for j in range(0, len(pool)):
                    if pool[j] == curCard:
                        del pool[j]
                        break
                del littlePool[r]
                if curCard == 52 or curCard == 53:
                    littlePoolLen = len(littlePool)
                    del littlePool[littlePoolLen - 1]   #最后一张是另一个王
                littlePoolLen = len(littlePool)

        #end modify by zw 2013-10-25 for 增加底牌类型 大牌型（A、2、jocker）

        # 随机剩下的牌
        random.shuffle(pool)
        randFill = config.get('RAND_FILL', 0)
        if random.randint(0, 100) < randFill:
            # 提取7与10，发给玩家
            if ftlog.is_debug():
                ftlog.debug('RAND_FILL.DDZDealCard_Base randFill =', randFill)
            pool.sort(key=lambda x: (-(x % 13 == 6), -(x % 13 == 9)))

        while len(pool) > 0:
            for i in range(0, 3):
                if len(card[i]) < 17:
                    card[i].append(pool[0])
                    pool.pop(0)

        card.append(base)
        return card

    # 生涯第一局拿双王+[5-K]飞机
    def DDZDealCard_NewPlayer(self, seatIndex, config):
        # print "发好牌"
        pool = []
        # 将A和2放到K后面
        polist = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 0, 1]
        for i in polist:
            pool.append([i, i + 13, i + 26, i + 39])
        pool.append([52])
        pool.append([53])
        # 此时pool中为:
        # [['3'], ['4'], ... , ['K'], ['A'], ['2'], ['joker'], ['JOKER']
        # [  0  ,   1  ,     ,   10 ,   11 ,  12  ,    13    ,    14]
        # 手牌
        card = [[], [], []]
        # 手牌数量
        curCardNum = 0
        
        # 直接拿大王
        card[seatIndex].append(53)
        del pool[14][0]  # 删除池中的大王
        curCardNum += 1
        # 直接拿小王
        card[seatIndex].append(52)
        del pool[13][0]  # 删除池中的小王
        curCardNum += 1
        # 直接拿[5-K]飞机
        plane = random.randrange(2, 11)  # 飞机起点(5-K)
        for i in range(0, 2):
            for _ in range(0, 3):
                card[seatIndex].append(pool[plane + i][0])
                del pool[plane + i][0]
        curCardNum += 6

        # 整理剩下的牌，随机发出
        left = []
        for arr in pool:
            for c in arr:
                left.append(c)
        random.shuffle(left)
        randFill = config.get('RAND_FILL', 0)
        if random.randint(0, 100) < randFill:
            # 提取7与10，发给玩家
            if ftlog.is_debug():
                ftlog.debug('RAND_FILL.DDZDealCard_NewPlayer randFill =', randFill)
            left.sort(key=lambda x: (-(x % 13 == 6), -(x % 13 == 9)))

        while len(left) > 3:
            for i in range(0, 3):
                if len(card[i]) < 17:
                    card[i].append(left[0])
                    left.pop(0)

        card.append(left)
        return card
        
    #原有火箭加飞机
    def DDZDealCard_GoodSeatA(self, seatIndex, config):
        # print "发好牌"
        pool = []
        # 将A和2放到K后面
        polist = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 0, 1]
        for i in polist:
            pool.append([i, i + 13, i + 26, i + 39])
        pool.append([52])
        pool.append([53])
        # 此时pool中为:
        # [['3'], ['4'], ... , ['K'], ['A'], ['2'], ['joker'], ['JOKER']
        # [  0  ,   1  ,     ,   10 ,   11 ,  12  ,    13    ,    14]
        # 手牌
        card = [[], [], []]
        # 手牌数量
        curCardNum = 0
        # 好牌的定义:
        #   1. 'RAND_JOKER1'%的概率给大王
        #   2. 'RAND_JOKER2'%的概率给小王
        #   3. 从1和'RAND_TWO'中随机给2
        #   4. 'RAND_FEIJI'%的概率发一个飞机
        # 大王
        rand_joker1 = config.get('RAND_JOKER1', 90)
        r = random.randrange(0, 100, 1)
        if r < rand_joker1:  # 大王的概率
            # print "得到大王"
            card[seatIndex].append(53)
            del pool[14][0]  # 删除池中的大王
            curCardNum += 1
        # 小王
        rand_joker2 = config.get('RAND_JOKER2', 80)
        r = random.randrange(0, 100, 1)
        if (r < rand_joker2):  # 小王的概率
            # print "得到小王"
            card[seatIndex].append(52)
            del pool[13][0]  # 删除池中的小王
            curCardNum += 1
        # 发飞机
        rand_feiji = config.get('RAND_FEIJI', 40)
        r = random.randrange(0, 100, 1)
        if (r < rand_feiji):
            plane = random.randrange(0, 11)  # 飞机起点(3-K)
            # print "飞机: '%s' to '%s'"%(self.getPointByPos(plane), self.getPointByPos(plane+1))
            for i in range(0, 2):
                for _ in range(0, 3):
                    card[seatIndex].append(pool[plane + i][0])
                    del pool[plane + i][0]
            curCardNum += 6
        else:
            pass
            # print "没有飞机"
        # 再随机一人一个三张

        for i in range(0, 3):
            if i == seatIndex:
                continue
            r = random.randrange(0, 100, 1) % 13
            while (len(pool[r]) < 3):
                r = (r + 1) % 13
            for _ in range(0, 3):
                card[i].append(pool[r][0])
                del pool[r][0]

        # 还剩下8个4张
        # 再随机每人两个对子
        duicount = config.get('COUNT_DUI', 3)
        for i in range(0, 3):
            for _ in range(0, duicount):
                if i == seatIndex:
                    if (curCardNum > 15):
                        continue
                    else:
                        curCardNum += 2
                r = random.randrange(0, 100, 1) % 13
                while (len(pool[r]) < 2):
                    r = (r + 1) % 13
                for _ in range(0, 2):
                    card[i].append(pool[r][0])
                    del pool[r][0]
        # 整理剩下的牌，随机发出
        left = []
        for arr in pool:
            for c in arr:
                left.append(c)
        random.shuffle(left)

        randFill = config.get('RAND_FILL', 0)
        if random.randint(0, 100) < randFill:
            # 提取7与10，发给玩家
            if ftlog.is_debug():
                ftlog.debug('RAND_FILL.DDZDealCard_GoodSeatA randFill =', randFill)
            left.sort(key=lambda x: (-(x % 13 == 6), -(x % 13 == 9)))

        while len(left) > 3:
            for i in range(0, 3):
                if len(card[i]) < 17:
                    card[i].append(left[0])
                    left.pop(0)

        card.append(left)
        return card

    #新增火箭加双顺 by zw 2013-10-25
    def DDZDealCard_GoodSeatB(self, seatIndex, config):
        pool = []

        # 将A和2放到K后面
        polist = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 0, 1]
        for i in polist:
            pool.append([i, i + 13, i + 26, i + 39])
        pool.append([52])
        pool.append([53])
        # 此时pool中为:
        # [['3'], ['4'], ... , ['K'], ['A'], ['2'], ['joker'], ['JOKER']
        # [  0  ,   1  ,     ,   10 ,   11 ,  12  ,    13    ,    14]
        # 手牌
        card = [[], [], []]
        # 手牌数量
        curCardNum = 0
        # 好牌的定义:
        #   1. 'RAND_JOKER1'%的概率给大王
        #   2. 'RAND_JOKER2'%的概率给小王
        #   3. 从1和'RAND_TWO'中随机给2
        #   4. 'RAND_FEIJI'%的概率发一个飞机
        # 大王
        rand_joker1 = config.get('RAND_JOKER1', 90)
        r = random.randrange(0, 100, 1)
        if (r < rand_joker1):  # 大王的概率
            # print "得到大王"
            card[seatIndex].append(53)
            del pool[14][0]  # 删除池中的大王
            curCardNum += 1
        # 小王
        rand_joker2 = config.get('RAND_JOKER2', 80)
        r = random.randrange(0, 100, 1)
        if (r < rand_joker2):  # 小王的概率
            # print "得到小王"
            card[seatIndex].append(52)
            del pool[13][0]  # 删除池中的小王
            curCardNum += 1
        # 发双顺
        rand_shuangshun = config.get('RAND_SHUANGSHUN', 40)
        r = random.randrange(0, 100, 1)
        if (r < rand_shuangshun):
            plane = random.randint(0, 9)  # 双顺起点(3-Q)
            for i in range(0, 3):
                for _ in range(0, 2):
                    card[seatIndex].append(pool[plane + i][0])
                    del pool[plane + i][0]
            curCardNum += 6
        else:
            pass
        # 再随机一人一个三张

        for i in range(0, 3):
            if i == seatIndex:
                continue
            r = random.randrange(0, 100, 1) % 13
            while (len(pool[r]) < 3):
                r = (r + 1) % 13
            for _ in range(0, 3):
                card[i].append(pool[r][0])
                del pool[r][0]

        # 还剩下8个4张
        # 再随机每人两个对子
        duicount = config.get('COUNT_DUI', 3)
        for i in range(0, 3):
            for _ in range(0, duicount):
                if i == seatIndex:
                    if (curCardNum > 15):
                        continue
                    else:
                        curCardNum += 2
                r = random.randrange(0, 100, 1) % 13
                while (len(pool[r]) < 2):
                    r = (r + 1) % 13
                for _ in range(0, 2):
                    card[i].append(pool[r][0])
                    del pool[r][0]
        # 整理剩下的牌，随机发出
        left = []
        for arr in pool:
            for c in arr:
                left.append(c)
        random.shuffle(left)

        randFill = config.get('RAND_FILL', 0)
        if random.randint(0, 100) < randFill:
            # 提取7与10，发给玩家
            if ftlog.is_debug():
                ftlog.debug('RAND_FILL.DDZDealCard_GoodSeatB randFill =', randFill)
            left.sort(key=lambda x: (-(x % 13 == 6), -(x % 13 == 9)))

        while len(left) > 3:
            for i in range(0, 3):
                if len(card[i]) < 17:
                    card[i].append(left[0])
                    left.pop(0)

        card.append(left)
        return card

    #新增对2加双炸弹 by zw 2013-10-25
    def DDZDealCard_GoodSeatC(self, seatIndex, config):
        # print "发好牌"
        pool = []

        # 将A和2放到K后面
        polist = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 0, 1]
        for i in polist:
            pool.append([i, i + 13, i + 26, i + 39])
        pool.append([52])
        pool.append([53])
        # 此时pool中为:
        # [['3'], ['4'], ... , ['K'], ['A'], ['2'], ['joker'], ['JOKER']
        # [  0  ,   1  ,     ,   10 ,   11 ,  12  ,    13    ,    14]
        # 手牌
        card = [[], [], []]
        # 手牌数量
        curCardNum = 0
        # 好牌的定义:
        #   1. 对2
        #   2. 双炸弹

        # 发2
        _rand_two = config.get('COUNT_TWO', 2)
        #n = random.randrange(1, rand_two + 1, 1)
        n=2 #对2
        for i in range(0, n):
            # print "得到一张 '2'"
            card[seatIndex].append(pool[12][0])  # 按花色顺序放2
            del pool[12][0]
        curCardNum += n

        #发2个炸弹
        except_card = [4] #降低7出现砸蛋的概率
        r = random.randint(0, 11) #3~A
        while ( r in except_card):
            r = random.randint(0, 11)
        except_card.append(r)
        for _ in range(0, 4):
            card[seatIndex].append(pool[r][0])
            del pool[r][0]

        s = random.randint(0,11)
        while (s in except_card):
            s=random.randint(0,11)
        for _ in range(0, 4):
            card[seatIndex].append(pool[s][0])
            del pool[s][0]

        # 整理剩下的牌，随机发出
        left = []
        for arr in pool:
            for c in arr:
                left.append(c)
        random.shuffle(left)

        randFill = config.get('RAND_FILL', 0)
        if random.randint(0, 100) < randFill:
            # 提取7与10，发给玩家
            if ftlog.is_debug():
                ftlog.debug('RAND_FILL.DDZDealCard_GoodSeatC randFill =', randFill)
            left.sort(key=lambda x: (-(x % 13 == 6), -(x % 13 == 9)))

        while len(left) > 3:
            for i in range(0, 3):
                if len(card[i]) < 17:
                    card[i].append(left[0])
                    left.pop(0)

        card.append(left)
        return card

    #GoodSeat 概率选择函数
    def DDZDealCard_GoodSeat(self, seatIndex, config, newPlayer=False):
        if newPlayer:
            return self.DDZDealCard_NewPlayer(seatIndex, config)
        
        goodSeatRandA = config.get('GOODSEATA', 40)
        goodSeatRandB = config.get('GOODSEATB', 40)
        goodSeatRandC = config.get('GOODSEATC', 20)

        #如果概率不为100，按比例缩放
        total_rand = goodSeatRandA + goodSeatRandB + goodSeatRandC
        if total_rand != 100 :
            goodSeatRandA = (goodSeatRandA * 100) // total_rand
            goodSeatRandB = (goodSeatRandB * 100) // total_rand
            goodSeatRandC = 100 - goodSeatRandA - goodSeatRandB

        r = random.randint(1, 100)
        if r <= goodSeatRandA:
            return self.DDZDealCard_GoodSeatA(seatIndex, config)
        elif r <= goodSeatRandB + goodSeatRandA:
            return  self.DDZDealCard_GoodSeatB(seatIndex, config)
        else:
            return  self.DDZDealCard_GoodSeatC(seatIndex, config)

class PunishPolicyNormal(PunishPolicy):
    def __init__(self, canNagtive):
        self._canNagtive = canNagtive

    def punish(self, gameResult):
        '''
        根据gameResult进行惩罚
        '''
        punishNM = []
        notPunishNM = []
        for sst in gameResult.seatStatements:
            if sst != gameResult.dizhuStatement:
                if sst.seat.status.isPunish:
                    punishNM.append(sst)
                else:
                    notPunishNM.append(sst)
        
        # 地主胜利，一个农民托管
        if (len(punishNM) == 1
            and len(notPunishNM) == 1
            and gameResult.gameRound.result == GameRound.RESULT_DIZHU_WIN):
            punishNM[0].isPunish = True
            if self._canNagtive:
                # 直接转嫁
                if notPunishNM[0].delta < 0:
                    punishNM[0].deltaScore(notPunishNM[0].delta)
                    notPunishNM[0].deltaScore(-notPunishNM[0].delta)
            else:
                # 计算可以转嫁多少, 当托管金币不足时， 非托管不扣钱
                score = min(punishNM[0].final, -notPunishNM[0].delta)
                if score > 0:
                    gameResult.dizhuStatement.deltaScore(score)
                    punishNM[0].deltaScore(-score)
                gameResult.dizhuStatement.deltaScore(notPunishNM[0].delta)
                notPunishNM[0].deltaScore(-notPunishNM[0].delta)
            
            # 地主不赢
            if gameResult.dizhuStatement.isPunish:
                gameResult.systemRecovery += gameResult.dizhuStatement.delta
                gameResult.dizhuStatement.deltaScore(-gameResult.dizhuStatement.delta)
        elif (len(punishNM) == 1
              and len(notPunishNM) == 1
              and gameResult.gameRound.result == GameRound.RESULT_NONGMIN_WIN
              and gameResult.gameRound.table.runConf.nongminWinAlone):
            # 农民胜利 一个农民托管
            # 比赛中(arena/group):积分可为负数，另一个农民托管下，获胜农民赢得地主输掉的所有积分
            punishNM[0].isPunish = True
            notPunishNM[0].deltaScore(punishNM[0].delta)
            punishNM[0].deltaScore(-punishNM[0].delta)
            
        else:
            for sst in gameResult.seatStatements:
                if sst.seat.status.isPunish and sst.isWin:
                    gameResult.systemRecovery += sst.delta
                    sst.systemPaid -= sst.delta
                    sst.deltaScore(-sst.delta)

class SettlementPolicyMatch(SettlementPolicy):
    def __init__(self):
        self._punishPolicy = PunishPolicyNormal(True)
    
    def calcResult(self, gameRound):
        ret = GameResult(gameRound)
        if gameRound.firstWinSeat:
            self._calcForGameOver(ret)
        else:
            self._calcForGameAbort(ret)
        return ret
    
    def settlement(self, gameResult):
        for sst in gameResult.seatStatements:
            player = sst.seat.player
            sst.skillscoreInfo = dict(player.getData('skillScoreInfo', {}))
            sst.skillscoreInfo['addScore'] = 0
            sst.winStreak = 0
            sst.expInfo = [
                player.getData('slevel', 0),
                player.getData('exp', 0),
                0,
                player.getData('nextexp', 0),
                player.getData('title', '')
            ]
            sst.seat.player.score = sst.final
        ftlog.info('BaseSettlementPolicy._settlement',
                   'roomId=', gameResult.gameRound.table.roomId,
                   'tableId=', gameResult.gameRound.table.tableId,
                   'roundId=', gameResult.gameRound.roundId,
                   'infos=', [(sst.seat.userId, sst.seat.player.score, sst.delta) for sst in gameResult.seatStatements])
    
    
    def _calcWinlose(self, result):
        assert(result.dizhuStatement)
        for sst in result.seatStatements:
            if sst != result.dizhuStatement:
                # 地主输赢本农民的积分
                seatWinlose = sst.seat.status.totalMulti * result.baseScore
                # 本农民输赢积分
                seatDelta = seatWinlose if result.gameRound.result == GameRound.RESULT_NONGMIN_WIN else -seatWinlose
                sst.delta = seatDelta
                sst.final += seatDelta
                result.dizhuStatement.delta -= seatDelta
                result.dizhuStatement.final -= seatDelta
                
                if ftlog.is_debug():
                    ftlog.debug('BaseSettlementPolicyMatch._calcWinlose',
                                'roundId=', result.gameRound.roundId,
                                'userId=', sst.seat.userId,
                                'dizhuUserId=', result.dizhuStatement.seat.userId,
                                'result=', (type(result.gameRound.result), result.gameRound.result),
                                'baseScore=', result.baseScore,
                                'totalMulti=', sst.seat.status.totalMulti,
                                'seatWinlose=', (type(seatWinlose), seatWinlose), 
                                'delta=', sst.delta,
                                'final=', sst.final,
                                'dizhufinal=', result.dizhuStatement.final)

    def _calcForGameAbort(self, result):
        # 所有人都输1倍
        result.gameRound.totalMulti = 1
        for sst in result.seatStatements:
            sst.deltaScore(-result.baseScore)
        return result
    
    def _calcForGameOver(self, result):
        # 收服务费
        # 计算输赢
        self._calcWinlose(result)
        # 托管包赔
        self._punishPolicy.punish(result)
        return result
    
class TableStateMachineNormal(TableStateMachine):
    def __init__(self):
        super(TableStateMachineNormal, self).__init__()
        self.addState(TableStateIdle())
        self.addState(TableStateNongminJiabei())
        self.addState(TableStateDizhuJiabei())
        self.addState(TableStateCalling())
        self.addState(TableStatePlaying())
        self.addState(TableStateHuanpai())
        self.addState(TableStateFinal())

SM_NORMAL = TableStateMachineNormal()


