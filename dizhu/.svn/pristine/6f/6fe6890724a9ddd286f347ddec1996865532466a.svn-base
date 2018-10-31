# -*- coding=utf-8 -*-
"""
Created on 2017年8月11日

@author: wangjifa
"""
import random
import freetime.util.log as ftlog
from dizhucomm.playmodes.base import SendCardsPolicy3PlayerDefault, SendCardsPolicyUserSetting
from poker.entity.configure import gdata
from poker.entity.dao import gamedata


class CardDizhuQuickLaiZi(SendCardsPolicy3PlayerDefault):
    @classmethod
    def getQuickPokerList(cls):
        # 急速癞子牌池去掉3、4、5
        # 将A和2放到K后面
        pool = []
        polist = [5, 6, 7, 8, 9, 10, 11, 12, 0, 1]
        for i in polist:
            pool.append([i, i + 13, i + 26, i + 39])
        pool.append([52])
        pool.append([53])
        assert (len(pool), 12)
        return pool

    @classmethod
    def getQuickPokers(cls):
        pool = cls.getQuickPokerList()
        pools = []
        for index in range(len(pool)):
            pools += pool[index]
        return pools

    @classmethod
    def getQuickShuffleCardList(cls, bc):
        pool = cls.getQuickPokerList()
        pools = []
        for index in range(len(pool)):
            pools += pool[index]

        card_list = list(set(pools) - set(bc))
        random.shuffle(card_list)
        return card_list

    def sendCards(self, table):
        seats = table.gameRound.seats
        assert(len(seats) == 3)
        goodCard = table.runConf.goodCard
        lucky = table.runConf.lucky
        sendCardConf = table.runConf.sendCardConf
        cards = None

        if gdata.enableTestHtml():
            userIds = [seat.userId for seat in table.gameRound.seats if seat.player]
            cards = self.sendCardsToAllUserIds(table.gameId, userIds)
            if ftlog.is_debug():
                ftlog.debug('QuickLaiZiSendCardsPolicy.enableTestHtml.cards=', cards)

        if not cards:
            if goodCard and not table.room.isMatch:
                pcount = []
                for seatIndex in range(len(seats)):
                    seatPlayCount = seats[seatIndex].player.datas.get('plays', 0)
                    pcount.append(seatPlayCount)

                goodCardSeat, cards = self.sendCard2(pcount, sendCardConf)
            else:
                cards = self.sendCard1(3, lucky)

        if not cards:
            cards = self.sendCard(len(seats), lucky)

        for i, seat in enumerate(table.gameRound.seats):
            seat.status.cards = cards[i]

        # 设置底牌
        table.gameRound.baseCards = cards[-1]

        if ftlog.is_debug():
            ftlog.debug('QuickLaiZiSendCardsPolicy.over',
                        'tableId=', table.tableId,
                        'sendCardConf=', sendCardConf,
                        'lucky=', lucky,
                        'cards=', cards)

    ########配牌逻辑
    @classmethod
    def decodeCards(cls, cardsStr):
        ret = set()
        cards = cardsStr.split(',')
        for c in cards:
            card = int(c.strip())
            if card < 0 or card >= 54 or card in [2,15,28,41,3,16,29,42,4,17,30,43]:
                raise Exception('quick_laizi_card must in [0, 54) and not in[2,15,28,41,3,16,29,42,4,17,30,43]')
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

    @classmethod
    def sendCardsToAllUserIds(cls, gameId, userIds):
        bcards = []
        allCards = cls.getQuickPokers()
        ret = [None for _ in xrange(len(userIds) + 1)]
        try:
            for i, userId in enumerate(userIds):
                cards, bcards = gamedata.getGameAttrs(userId, gameId, ['test.cards', 'test.bcards'])
                if cards:
                    cards = cls.decodeCards(cards)
                    if len(cards) > 13:
                        cards = cards[0:13]
                    cards = cls._sendCards(cards, allCards)
                    cards = cls._buqiCards(cards, allCards, 13)
                    ret[i] = list(cards)

                if bcards:
                    bcards = cls.decodeCards(bcards)
                    if len(bcards) > 3:
                        bcards = bcards[0:3]

            if bcards:
                bcards = cls._sendCards(bcards, allCards)

            bcards = cls._buqiCards(bcards, allCards, 3)
            ret[-1] = list(bcards)

            for i in xrange(len(userIds)):
                if not ret[i] or len(ret[i]) != 13:
                    ret[i] = list(cls._buqiCards(ret[i], allCards, 13))

            return ret
        except:
            ftlog.error('dizhu_quick_laizi_sendCardsToAllUserIds error')
        return None
    ########

    # 当前桌子发牌,并计算出玩家手牌的分数
    @classmethod
    def sendCard(cls, seatCount, lucky):
        bomb_cards = []  # 预先发的炸弹扑克列表
        bomb_count = 0
        luck_seat = random.randint(0, 2)

        cards = []
        for i in xrange(seatCount):
            cards.append([])

        # 判断制造炸弹
        x = random.randint(1, 100)
        if x <= lucky:
            bomb_count = random.randint(1, 3)
            ls = [luck_seat, (luck_seat + 1) % 3, (luck_seat + 2) % 3]
            #sbc = random.randint(1, 11)#随机出炸弹的点数2345678910JQ
            sbc = random.choice([5, 6, 7, 8, 9, 10, 11, 1]) #no 3 & 4 & 5 & K & A
            #sbc = random.choice([5, 6, 7, 8, 9, 10, 11, 12, 0, 1]) #6-K-A-2
            for bn in xrange(bomb_count): #0 #0 1 #0 1 2#好牌玩家的牌桌索引
                for cn in xrange(4): #0 1 2 3
                    cards[ls[bn]].append(sbc + bn + cn * 13)
                    bomb_cards.append(sbc + bn + cn * 13)

        cardindex = 0
        cl = cls.getQuickShuffleCardList(bomb_cards)
        for i in xrange(13):
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
        baseCard = []
        for index in xrange(seatCount):
            baseCard.append(cl[cardindex])
            cardindex += 1
        cards.append(baseCard)

        if ftlog.is_debug():
            ftlog.debug('QuickLaiZiSendCardsPolicy.sendCard cards=', cards, 'x=', x, 'lucky=', lucky)

        return cards


    @classmethod
    def sendCard2(cls, total, config):
        seatId = cls.getGoodSeatId(total, config)

        if seatId == 0:
            cards = cls.DDZDealCard_Base(config)
        else:
            cards = cls.DDZDealCard_GoodSeat(seatId, config)
        return seatId, cards

    @classmethod
    def getGoodSeatId(cls, total, config):
        goodList = []
        # 随机周期发好牌
        loop = config["GOOD_LOOP"] if config.has_key("GOOD_LOOP") else 5
        newPlayCount = config["NEWPLAY_COUNT"] if config.has_key("NEWPLAY_COUNT") else 5
        newPlayLuck = config["NEWPLAY_LUCK"] if config.has_key("NEWPLAY_LUCK") else 90

        loop_bottom = max(5, loop - 1)
        loop_top = max(7, loop + 2)

        for i in range(0, len(total)):
            # 新手保护
            if total[i] <= newPlayCount:
                newPlayerRatio = random.randint(1, 100)
                if newPlayerRatio < newPlayLuck:
                    goodList.append(i)
                continue
            # 随机周期
            if total[i] % random.randint(loop_bottom, loop_top) == 0:
                goodList.append(i)

        # 如果只有一个符合好牌条件,则直接返回座位号
        if len(goodList) == 1:
            return goodList[0] + 1
        # 如果都不符合好牌条件或有冲突，则按概率返回0
        ratio = random.randrange(0, 100, 1)
        rand_good = config["RAND_GOOD"] if config.has_key("RAND_GOOD") else 70
        if ratio > rand_good:
            return 0
        # 如果都不符合好牌条件，则完全随机一个座位返回
        if len(goodList) == 0:
            return (ratio % 3) + 1
        # 如果有冲突，则随机数值选择冲突座位

        if ftlog.is_debug():
            ftlog.debug('QuickLaiZiSendCardsPolicy.getGoodSeatId total=', total,
                        'newPlayCount=', newPlayCount,
                        'newPlayLuck=', newPlayLuck,
                        'loop=', loop,
                        'loop_bottom=', loop_bottom,
                        'loop_top=', loop_top,
                        'goodList=', goodList,
                        'ratio=', ratio,
                        'lenGoodList=', len(goodList),
                        'return=', goodList[(ratio % len(goodList))] + 1)

        return goodList[(ratio % len(goodList))] + 1

    @classmethod
    def DDZDealCard_Base(cls, config):
        # print "随机底牌"
        rand_bc1 = config['RAND_BC1'] if config.has_key('RAND_BC1') else 50
        rand_bc2 = config['RAND_BC2'] if config.has_key('RAND_BC2') else 30
        rand_bc3 = config['RAND_BC3'] if config.has_key('RAND_BC3') else 20
        total_rand_bc = rand_bc1 + rand_bc2 + rand_bc3
        if total_rand_bc != 100:
            # 配置错误，按比例缩放
            rand_bc1 = (rand_bc1 * 100) // total_rand_bc
            rand_bc2 = (rand_bc2 * 100) // total_rand_bc
            rand_bc3 = 100 - rand_bc1 - rand_bc2

        base = []
        card = [[], [], []]

        pool = cls.getQuickPokers()#range(54)
        r = random.randrange(0, 100, 1)

        if ftlog.is_debug():
            ftlog.debug('QuickLaiZiSendCardsPolicy.DDZDealCard_Base r=', r,
                        'pool=', pool,
                        'card=', card,
                        'base=', base,
                        'rand_bc1_bc2_bc3=', rand_bc1, rand_bc2, rand_bc3)

        if r < rand_bc1:
            # print "三张相同底牌"
            basePoint = r % 10
            basePoint = basePoint * 4
            for i in range(0, 3):
                base.append(pool[basePoint + i])
                del pool[basePoint + i]

        elif r < rand_bc2 + rand_bc1:
            # print "双王底牌"
            base.append(53)
            base.append(52)
            pool = pool[:-2]
            randCard = random.choice(pool)
            base.append(randCard)
            for index in range(len(pool)):
                if pool[index] == randCard:
                    del pool[index]
                    break

        else:
            # 大牌型底牌
            bigCardPool = [0, 13, 26, 39, 1, 14, 27, 40, 52, 53]
            for i in range(0, 3):
                poolLen = len(bigCardPool)
                r = random.randint(1, poolLen) - 1
                curCard = bigCardPool[r]
                base.append(curCard)
                for j in range(0, len(pool)):
                    if pool[j] == curCard:
                        del pool[j]
                        break
                del bigCardPool[r]
                # if curCard == 52 or curCard == 53:
                #     poolLen = len(bigCardPool)
                #     del bigCardPool[poolLen - 1]  # 最后一张是另一个王
                #     poolLen = len(bigCardPool)

        if ftlog.is_debug():
            ftlog.debug('QuickLaiZiSendCardsPolicy.DDZDealCard_Base r=', r,
                        'pool=', pool,
                        'card=', card,
                        'base=', base)

        # 随机剩下的牌
        random.shuffle(pool)
        for i in range(0, 3):
            while len(card[i]) < 13:
                card[i].append(pool[0])
                del pool[0]
        card.append(base)

        if ftlog.is_debug():
            ftlog.debug('QuickLaiZiSendCardsPolicy.DDZDealCard_Base r=', r,
                        'pool=', pool,
                        'card=', card,
                        'base=', base)

        return card

    # GoodSeat 概率选择函数
    @classmethod
    def DDZDealCard_GoodSeat(cls, seatIndex, config, newPlayer=False):
        # if newPlayer:
        #     return self.DDZDealCard_NewPlayer(seatIndex, config)

        goodSeatRandA = config.get('GOODSEATA', 40)
        goodSeatRandB = config.get('GOODSEATB', 40)
        goodSeatRandC = config.get('GOODSEATC', 20)

        # 如果概率不为100，按比例缩放
        total_rand = goodSeatRandA + goodSeatRandB + goodSeatRandC
        if total_rand != 100:
            goodSeatRandA = (goodSeatRandA * 100) // total_rand
            goodSeatRandB = (goodSeatRandB * 100) // total_rand
            goodSeatRandC = 100 - goodSeatRandA - goodSeatRandB

        r = random.randint(1, 100)

        if ftlog.is_debug():
            ftlog.debug('QuickLaiZiSendCardsPolicy.DDZDealCard_GoodSeat r=', r,
                        'seatIndex=', seatIndex,
                        'goodSeatRand.A_B_C=', goodSeatRandA, goodSeatRandB, goodSeatRandC)

        if r <= goodSeatRandA:
            return cls.DDZDealCard_GoodSeatA(seatIndex, config)
        elif r <= goodSeatRandB + goodSeatRandA:
            return cls.DDZDealCard_GoodSeatB(seatIndex, config)
        else:
            return cls.DDZDealCard_GoodSeatC(seatIndex, config)

    # 原有火箭加飞机
    @classmethod
    def DDZDealCard_GoodSeatA(cls, seatId, config):
        if seatId > 0:  # seatId传入时应为1-3，下标为0-2.
            seatId -= 1
        seatId = min(2, seatId)# 容错

        pool = cls.getQuickPokerList()
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
        rand_joker1 = config['RAND_JOKER1'] if (config.has_key('RAND_JOKER1')) else 90
        r = random.randrange(0, 100, 1)
        if r < rand_joker1:  # 大王的概率
            # print "得到大王"
            card[seatId].append(53)
            del pool[11][0]  # 删除池中的大王
            curCardNum += 1

        # 小王
        rand_joker2 = config['RAND_JOKER2'] if (config.has_key('RAND_JOKER2')) else 80
        r = random.randrange(0, 100, 1)
        if r < rand_joker2:  # 小王的概率
            # print "得到小王"
            card[seatId].append(52)
            del pool[10][0]  # 删除池中的小王
            curCardNum += 1

        # 发2
        rand_two = config['COUNT_TWO'] if (config.has_key('COUNT_TWO')) else 2
        n = random.randrange(1, rand_two + 1, 1)
        for i in range(0, n):
            # print "得到一张 '2'"
            card[seatId].append(pool[9][0])  # 按花色顺序放2
            del pool[9][0]
        curCardNum += n

        # 发飞机
        rand_feiji = config['RAND_FEIJI'] if (config.has_key('RAND_FEIJI')) else 40
        r = random.randrange(0, 100, 1)

        if ftlog.is_debug():
            ftlog.debug('QuickLaiZiSendCardsPolicy.DDZDealCard_GoodSeatA [over J j 2] r=', r,
                        'rand_feiji=', rand_feiji,
                        'pool=', pool,
                        'card=', card)

        if r < rand_feiji:
            # 发6-K飞机
            # plane = random.randrange(0, 7)  # 飞机起点(6-K)
            # # print "飞机: '%s' to '%s'"%(self.getPointByPos(plane), self.getPointByPos(plane+1))
            # for i in range(0, 2):
            #     for j in range(0, 3):
            #         card[seatId].append(pool[plane + i][0])
            #         del pool[plane + i][0]
            # curCardNum += 6

            # 发6-K的随机2个三条
            for i in range(0,2):
                r = random.randrange(0, 100, 1) % 9
                while len(pool[r]) < 3:
                    r = (r + 1) % 9
                for j in range(0, 3):
                    card[seatId].append(pool[r][0])
                    del pool[r][0]
            curCardNum += 6
        else:
            pass
            # print "没有飞机"

        if ftlog.is_debug():
            ftlog.debug('QuickLaiZiSendCardsPolicy.DDZDealCard_GoodSeatA [over feiji] r=', r,
                        'pool=', pool,
                        'card=', card)

        # 再给非好牌的座位 一人一个三张
        for i in range(0, 3):
            if i == seatId:
                continue
            r = random.randrange(0, 100, 1) % 9
            while len(pool[r]) < 3:
                r = (r + 1) % 9
            for j in range(0, 3):
                card[i].append(pool[r][0])
                del pool[r][0]

        if ftlog.is_debug():
            ftlog.debug('QuickLaiZiSendCardsPolicy.DDZDealCard_GoodSeatA [over xxx] r=', r,
                        'pool=', pool,
                        'card=', card)

        # 还剩下5个4张
        # 再随机每人两个对子
        duicount = config['COUNT_DUI'] if (config.has_key('COUNT_DUI')) else 2
        for i in range(0, 3):
            for j in range(0, duicount):

                if len(card[i]) > 11:
                    continue

                # print "得到一个对子"
                r = random.randrange(0, 100, 1) % 9
                while len(pool[r]) < 2:
                    r = (r + 1) % 9
                for k in range(0, 2):
                    card[i].append(pool[r][0])
                    del pool[r][0]

        if ftlog.is_debug():
            ftlog.debug('QuickLaiZiSendCardsPolicy.DDZDealCard_GoodSeatA [over 2pair] r=', r,
                        'pool=', pool,
                        'card=', card)

        # 整理剩下的牌，随机发出
        left = []
        for arr in pool:
            for c in arr:
                left.append(c)
        random.shuffle(left)
        for i in range(0, 3):
            while len(card[i]) < 13:
                card[i].append(left[0])
                del left[0]

        card.append(left)
        return card

    # 火箭加双顺
    @classmethod
    def DDZDealCard_GoodSeatB(cls, seatId, config):
        if seatId > 0:  # seatId传入时应为1-3，下标为0-2.
            seatId -= 1
        seatId = min(2, seatId)# 容错

        pool = cls.getQuickPokerList()
        # 手牌
        card = [[], [], []]
        # 手牌数量
        curCardNum = 0
        # 好牌的定义:
        #   1. 'RAND_JOKER1'%的概率给大王
        #   2. 'RAND_JOKER2'%的概率给小王
        #   3. 从1和'RAND_TWO'中随机给2
        #   4. 'RAND_FEIJI'%的概率发一个飞机

        if ftlog.is_debug():
            ftlog.debug('QuickLaiZiSendCardsPolicy.DDZDealCard_GoodSeatB [begin] seatId=', seatId,
                        'pool=', pool,
                        'card=', card)

        # 大王
        rand_joker1 = config['RAND_JOKER1'] if (config.has_key('RAND_JOKER1')) else 90
        r = random.randrange(0, 100, 1)
        if r < rand_joker1:  # 大王的概率
            # print "得到大王"
            card[seatId].append(53)
            del pool[11][0]  # 删除池中的大王
            curCardNum += 1

        # 小王
        rand_joker2 = config['RAND_JOKER2'] if (config.has_key('RAND_JOKER2')) else 80
        r = random.randrange(0, 100, 1)
        if r < rand_joker2:  # 小王的概率
            # print "得到小王"
            card[seatId].append(52)
            del pool[10][0]  # 删除池中的小王
            curCardNum += 1

        # 发2
        rand_two = config['COUNT_TWO'] if (config.has_key('COUNT_TWO')) else 2
        n = random.randrange(1, rand_two + 1, 1)
        for i in range(0, n):
            # print "得到一张 '2'"
            card[seatId].append(pool[9][0])  # 按花色顺序放2
            del pool[9][0]
        curCardNum += n

        if ftlog.is_debug():
            ftlog.debug('QuickLaiZiSendCardsPolicy.DDZDealCard_GoodSeatB [over J j 2] seatId=', seatId,
                        'pool=', pool,
                        'card=', card)

        # 发连对
        rand_shuangshun = config['RAND_SHUANGSHUN'] if (config.has_key('RAND_SHUANGSHUN')) else 40
        r = random.randrange(0, 100, 1)
        if (r < rand_shuangshun):
            plane = random.randint(0, 6)  # 双顺起点(6-Q)
            for i in range(0, 3):
                for j in range(0, 2):
                    card[seatId].append(pool[plane + i][0])
                    del pool[plane + i][0]
            curCardNum += 6
        else:
            pass
            # print "没有连对"

        if ftlog.is_debug():
            ftlog.debug('QuickLaiZiSendCardsPolicy.DDZDealCard_GoodSeatB [over AABBCC] r=', r,
                        'pool=', pool,
                        'card=', card,
                        'curCardNum=', curCardNum)

        # 再随机一人一个三张
        for i in range(0, 3):
            if (i == seatId):
                continue
            r = random.randrange(0, 100, 1) % 9
            while (len(pool[r]) < 3):
                r = (r + 1) % 9
            for j in range(0, 3):
                card[i].append(pool[r][0])
                del pool[r][0]

        if ftlog.is_debug():
            ftlog.debug('QuickLaiZiSendCardsPolicy.DDZDealCard_GoodSeatB [over xxx] r=', r,
                        'pool=', pool,
                        'card=', card,
                        'curCardNum=', curCardNum)

        # 整理剩下的牌，随机发出
        left = []
        for arr in pool:
            for c in arr:
                left.append(c)
        random.shuffle(left)
        for i in range(0, 3):
            while (len(card[i]) < 13):
                card[i].append(left[0])
                del left[0]

        card.append(left)
        return card

    # 对2加双炸弹
    @classmethod
    def DDZDealCard_GoodSeatC(cls, seatId, config):
        if (seatId > 0):  # seatId传入时应为1-3，下标为0-2.
            seatId -= 1
        if (seatId > 2):  # 容错
            seatId = 2

        pool = cls.getQuickPokerList()
        # 手牌
        card = [[], [], []]
        # 手牌数量
        curCardNum = 0
        # 好牌的定义:
        #   1. 对2
        #   2. 双炸弹

        # 发2
        rand_two = config['COUNT_TWO'] if (config.has_key('COUNT_TWO')) else 2
        n = random.randrange(1, rand_two + 1, 1)
        for i in range(0, n):
            # print "得到一张 '2'"
            card[seatId].append(pool[9][0])  # 按花色顺序放2
            del pool[9][0]
        curCardNum += n

        # 发2个炸弹
        r = random.randint(0, 8)  # 6~A
        for j in range(0, 4):
            card[seatId].append(pool[r][0])
            del pool[r][0]
        s = random.randint(0, 8)
        while (s == r):
            s = random.randint(0, 8)
        for j in range(0, 4):
            card[seatId].append(pool[s][0])
            del pool[s][0]

        # 整理剩下的牌，随机发出
        left = []
        for arr in pool:
            for c in arr:
                left.append(c)
        random.shuffle(left)
        for i in range(0, 3):
            while len(card[i]) < 13:
                card[i].append(left[0])
                del left[0]

        card.append(left)
        return card

    # 去3、4、5发牌
    def DDZDealCard_QuickWild(self, card):
        pool = self.getQuickPokerList()

        # 随机发出
        left = []
        for arr in pool:
            for c in arr:
                left.append(c)
        random.shuffle(left)
        for i in range(0, 3):
            while len(card[i]) < 13:
                card[i].append(left[0])
                del left[0]

        card.append(left)
        return card