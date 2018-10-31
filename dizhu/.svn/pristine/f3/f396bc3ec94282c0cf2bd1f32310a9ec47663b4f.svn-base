# -*- coding=utf-8 -*-
'''
Created on 2015年5月7日

@author: zqh
'''
import random


class CardDizhuLaiZi(object):
    
    # 当前桌子发牌,并计算出玩家手牌的分数
    @classmethod
    def sendCard(cls, seatCount, lucky):
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

        cl = cls.getShuffleCardList(bomb_cards)
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


    @classmethod
    def getShuffleCardList(cls, bc):
        card_list = list(set(range(54)) - set(bc))
        random.shuffle(card_list)
        return card_list


    @classmethod
    def sendCard2(cls, total, config):
        seatId = cls.getGoodSeatId(total, config)
        # print "goodSeat:%d"%(seatId)
        if (seatId == 0):
            cards = cls.DDZDealCard_Base(config)
        else:
            cards = cls.DDZDealCard_GoodSeat(seatId, config)
        return seatId, cards


    @classmethod
    def getGoodSeatId(cls, total, config):
        goodList = []
        loop = 5
        # modify by zw 2013-10-25 for 随机周期发好牌
        newPlayCount = 5
        newPlayLuck = 90
        if (config.has_key("GOOD_LOOP")):
            loop = config["GOOD_LOOP"]
        if (config.has_key("NEWPLAY_COUNT")):
            newPlayCount = config["NEWPLAY_COUNT"]
        if (config.has_key("NEWPLAY_LUCK")):
            newPlayLuck = config["NEWPLAY_LUCK"]
        loop_bottom = loop - 1
        loop_top = loop + 2
        if loop_bottom < 5:
            loop_bottom = 5
        if loop_top > 7 :
            loop_top = 7
        for i in range(0, len(total)):
            # 新手保护
            if total[i] <= newPlayCount:
                newPlayerRatio = random.randint(1, 100)
                if newPlayerRatio < newPlayLuck:
                    goodList.append(i)
                continue
            # 随机周期
            if (total[i] % random.randint(loop_bottom, loop_top) == 0):
                goodList.append(i)
        # end modify by zw 2013-10-25

        # 如果只有一个符合好牌条件,则直接返回座位号
        if (len(goodList) == 1):
            return goodList[0] + 1 
        # 如果都不符合好牌条件或有冲突，则按概率返回0
        ratio = random.randrange(0, 100, 1)
        rand_good = 70
        if (config.has_key("RAND_GOOD")):
            rand_good = config["RAND_GOOD"]
        if (ratio > rand_good):
            return 0
        # 如果都不符合好牌条件，则完全随机一个座位返回
        if (len(goodList) == 0):
            return (ratio % 3) + 1
        # 如果有冲突，则随机数值选择冲突座位
        return goodList[(ratio % len(goodList))] + 1


    @classmethod
    def DDZDealCard_Base(cls, config):
        # print "随机底牌"
        rand_bc1 = 50
        if (config.has_key('RAND_BC1')):
            rand_bc1 = config['RAND_BC1']
        # modify by zw 2013-10-25 for 增加底牌类型 大牌型（A、2、jocker）
        rand_bc2 = 30
        if (config.has_key('RAND_BC2')):
            rand_bc2 = config['RAND_BC2']
        rand_bc3 = 20
        if (config.has_key('RAND_BC3')):
            rand_bc3 = config['RAND_BC3']
        total_rand_bc = rand_bc1 + rand_bc2 + rand_bc3
        if (total_rand_bc) != 100 :
            # 配置错误，按比例缩放
            # if __debug__:
            #    print("Bad rand_bc[%d:%d:%d], modify its" %(rand_bc1, rand_bc2, rand_bc3))
            rand_bc1 = (rand_bc1 * 100) // total_rand_bc
            rand_bc2 = (rand_bc2 * 100) // total_rand_bc
            rand_bc3 = 100 - rand_bc1 - rand_bc2
            # if __debug__:
            #    print("modified rand_bc[%d:%d:%d]" %(rand_bc1, rand_bc2, rand_bc3))
#         pool = []
        base = []
        card = [[], [], []]
#         rtn = {}
        # for i in range(0, 54):
        #    pool.append(i)
        pool = range(54)
        r = random.randrange(0, 100, 1)
        # if __debug__:
        #    print{"--r[%d]" %r}
        if (r < rand_bc1):
            # print "三张相同底牌"
            basePoint = r % 13
            for i in range(0, 3):
                base.append(pool[basePoint + i * 13 - i])
                del pool[basePoint + i * 13 - i]
        elif (r < rand_bc2 + rand_bc1):
            # 底牌大王
            # print "双王底牌"
            base.append(53)
            del pool[53]
            base.append(52)
            del pool[52]
            base.append(r % 52)
            del pool[ r % 52]
        else:
            # 大牌型底牌
            littlePool = [0, 13, 26, 39, 1, 14, 27, 40, 52, 53]
            littlePoolLen = len(littlePool)
            for i in range(0, 3):
                r = random.randint(1, littlePoolLen) - 1
                curCard = littlePool[r]
                base.append(curCard)
                for j in range(0, len(pool)):
                    if pool[j] == curCard:
                        del pool[j]
                        break
                del littlePool[r]
                if curCard == 52 or curCard == 53:
                    littlePoolLen = len(littlePool)
                    del littlePool[littlePoolLen - 1]  # 最后一张是另一个王
                littlePoolLen = len(littlePool)

        # end modify by zw 2013-10-25 for 增加底牌类型 大牌型（A、2、jocker）

        # 随机剩下的牌
        random.shuffle(pool)
        for i in range(0, 3):
            for j in range(0, 17):
                card[i].append(pool[j + i * 17])
        card.append(base)
        return card
        # rtn['base'] = base
        # rtn['card1']= card[0]
        # rtn['card2']= card[1]
        # rtn['card3']= card[2]
        # print rtn
        

    @classmethod
    def DDZDealCard_GoodSeat(cls, seatId, config):
        goodSeatRandA = 40
        goodSeatRandB = 40
        goodSeatRandC = 20
        if (config.has_key('GOODSEATA')):
            goodSeatRandA = config['GOODSEATA']
        if (config.has_key('GOODSEATB')):
            goodSeatRandB = config['GOODSEATB']
        if (config.has_key('GOODSEATC')):
            goodSeatRandC = config['GOODSEATC']
        # 如果概率不为100，按比例缩放
        total_rand = goodSeatRandA + goodSeatRandB + goodSeatRandC
        if total_rand != 100 :
            goodSeatRandA = (goodSeatRandA * 100) // total_rand
            goodSeatRandB = (goodSeatRandB * 100) // total_rand
            goodSeatRandC = 100 - goodSeatRandA - goodSeatRandB

        r = random.randint(1, 100)
        # if __debug__:
        #    print("Get randint r[%d] ABC:[%d,%d,%d]" %(r, goodSeatRandA, goodSeatRandB, goodSeatRandC))
        if r <= goodSeatRandA:
            return cls.DDZDealCard_GoodSeatA(seatId, config)
        elif r <= goodSeatRandB + goodSeatRandA:
            return  cls.DDZDealCard_GoodSeatB(seatId, config)
        else:
            return  cls.DDZDealCard_GoodSeatC(seatId, config)
        

    # 原有火箭加飞机
    @classmethod
    def DDZDealCard_GoodSeatA(cls, seatId, config):
        if (seatId > 0):  # seatId传入时应为1-3，下标为0-2.
            seatId -= 1
        if (seatId > 2):  # 容错
            seatId = 2
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
        rand_joker1 = 90
        if (config.has_key('RAND_JOKER1')):
            rand_joker1 = config['RAND_JOKER1']
        r = random.randrange(0, 100, 1)
        if (r < rand_joker1):  # 大王的概率
            # print "得到大王"
            card[seatId].append(53)
            del pool[14][0]  # 删除池中的大王
            curCardNum += 1
        # 小王
        rand_joker2 = 80
        if (config.has_key('RAND_JOKER2')):
            rand_joker2 = config['RAND_JOKER2']
        r = random.randrange(0, 100, 1)
        if (r < rand_joker2):  # 小王的概率
            # print "得到小王"
            card[seatId].append(52)
            del pool[13][0]  # 删除池中的小王
            curCardNum += 1
        # 发2
        rand_two = 2
        if (config.has_key('COUNT_TWO')):
            rand_two = config['COUNT_TWO']
        n = random.randrange(1, rand_two + 1, 1)
        for i in range(0, n):
            # print "得到一张 '2'"
            card[seatId].append(pool[12][0])  # 按花色顺序放2
            del pool[12][0]
        curCardNum += n
        # 发飞机
        rand_feiji = 40
        if (config.has_key('RAND_FEIJI')):
            rand_feiji = config['RAND_FEIJI']
        r = random.randrange(0, 100, 1)
        if (r < rand_feiji):
            plane = random.randrange(0, 11)  # 飞机起点(3-K)
            # print "飞机: '%s' to '%s'"%(self.getPointByPos(plane), self.getPointByPos(plane+1))
            for i in range(0, 2):
                for j in range(0, 3):
                    card[seatId].append(pool[plane + i][0])
                    del pool[plane + i][0]
            curCardNum += 6
        else:
            pass
            # print "没有飞机"
        # 再随机一人一个三张

        for i in range(0, 3):
            if (i == seatId):
                continue
                # if (curCardNum > 14):
                #    continue
                # else:
                    # print "得到一个三张"
                #    curCardNum += 3
            r = random.randrange(0, 100, 1) % 13
            while (len(pool[r]) < 3):
                r = (r + 1) % 13
            for j in range(0, 3):
                card[i].append(pool[r][0])
                del pool[r][0]

        # 还剩下8个4张
        # 再随机每人两个对子
        duicount = 3
        if (config.has_key('COUNT_DUI')):
            duicount = config['COUNT_DUI']
        for i in range(0, 3):
            for j in range(0, duicount):
                if (i == seatId):
                    if (curCardNum > 15):
                        continue
                    else:
                        # print "得到一个对子"
                        curCardNum += 2
                r = random.randrange(0, 100, 1) % 13
                while (len(pool[r]) < 2):
                    r = (r + 1) % 13
                for k in range(0, 2):
                    card[i].append(pool[r][0])
                    del pool[r][0]
        # 整理剩下的牌，随机发出
        left = []
        for arr in pool:
            for c in arr:
                left.append(c)
        random.shuffle(left)
        for i in range(0, 3):
            while (len(card[i]) < 17):
                card[i].append(left[0])
                del left[0]

        # print card[seatId]
        # print pool
        # print left
        # rtn['base'] = left
        # rtn['card1']= card[0]
        # rtn['card2']= card[1]
        # rtn['card3']= card[2]
        card.append(left)
        return card
        # print rtn

    # 新增火箭加双顺 by zw 2013-10-25
    @classmethod
    def DDZDealCard_GoodSeatB(cls, seatId, config):
        if (seatId > 0):  # seatId传入时应为1-3，下标为0-2.
            seatId -= 1
        if (seatId > 2):  # 容错
            seatId = 2
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
        rand_joker1 = 90
        if (config.has_key('RAND_JOKER1')):
            rand_joker1 = config['RAND_JOKER1']
        r = random.randrange(0, 100, 1)
        if (r < rand_joker1):  # 大王的概率
            # print "得到大王"
            card[seatId].append(53)
            del pool[14][0]  # 删除池中的大王
            curCardNum += 1
        # 小王
        rand_joker2 = 80
        if (config.has_key('RAND_JOKER2')):
            rand_joker2 = config['RAND_JOKER2']
        r = random.randrange(0, 100, 1)
        if (r < rand_joker2):  # 小王的概率
            # print "得到小王"
            card[seatId].append(52)
            del pool[13][0]  # 删除池中的小王
            curCardNum += 1
        # 发2
        rand_two = 2
        if (config.has_key('COUNT_TWO')):
            rand_two = config['COUNT_TWO']
        n = random.randrange(1, rand_two + 1, 1)
        for i in range(0, n):
            # print "得到一张 '2'"
            card[seatId].append(pool[12][0])  # 按花色顺序放2
            del pool[12][0]
        curCardNum += n
        # 发双顺
        rand_shuangshun = 40
        if (config.has_key('RAND_SHUANGSHUN')):
            rand_shuangshun = config['RAND_SHUANGSHUN']
        r = random.randrange(0, 100, 1)
        if (r < rand_shuangshun):
            plane = random.randint(0, 9)  # 双顺起点(3-Q)
            # if __debug__:
            #    print("shuangshun: start[%d] r[%d]" %(plane, r))
            # print "飞机: '%s' to '%s'"%(self.getPointByPos(plane), self.getPointByPos(plane+1))
            for i in range(0, 3):
                for j in range(0, 2):
                    # if __debug__:
                    #    print("Get shuangshun card[%d]" %(pool[plane + i][0]))
                    card[seatId].append(pool[plane + i][0])
                    del pool[plane + i][0]
            curCardNum += 6
        else:
            pass
            # print "没有飞机"
        # 再随机一人一个三张

        for i in range(0, 3):
            if (i == seatId):
                continue
                # if (curCardNum > 14):
                #    continue
                # else:
                    # print "得到一个三张"
                #    curCardNum += 3
            r = random.randrange(0, 100, 1) % 13
            while (len(pool[r]) < 3):
                r = (r + 1) % 13
            for j in range(0, 3):
                card[i].append(pool[r][0])
                del pool[r][0]

        # 还剩下8个4张
        # 再随机每人两个对子
        duicount = 3
        if (config.has_key('COUNT_DUI')):
            duicount = config['COUNT_DUI']
        for i in range(0, 3):
            for j in range(0, duicount):
                if (i == seatId):
                    if (curCardNum > 15):
                        continue
                    else:
                        # print "得到一个对子"
                        curCardNum += 2
                r = random.randrange(0, 100, 1) % 13
                while (len(pool[r]) < 2):
                    r = (r + 1) % 13
                for k in range(0, 2):
                    card[i].append(pool[r][0])
                    del pool[r][0]
        # 整理剩下的牌，随机发出
        left = []
        for arr in pool:
            for c in arr:
                left.append(c)
        random.shuffle(left)
        for i in range(0, 3):
            while (len(card[i]) < 17):
                card[i].append(left[0])
                del left[0]

        # print card[seatId]
        # print pool
        # print left
        # rtn['base'] = left
        # rtn['card1']= card[0]
        # rtn['card2']= card[1]
        # rtn['card3']= card[2]
        card.append(left)
        return card
        # print rtn

    # 新增对2加双炸弹 by zw 2013-10-25
    @classmethod
    def DDZDealCard_GoodSeatC(cls, seatId, config):
        if (seatId > 0):  # seatId传入时应为1-3，下标为0-2.
            seatId -= 1
        if (seatId > 2):  # 容错
            seatId = 2
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
        rand_two = 2
        if (config.has_key('COUNT_TWO')):
            rand_two = config['COUNT_TWO']
        # n = random.randrange(1, rand_two + 1, 1)
        n = 2  # 对2
        for i in range(0, n):
            # print "得到一张 '2'"
            card[seatId].append(pool[12][0])  # 按花色顺序放2
            del pool[12][0]
        curCardNum += n

        # 发2个炸弹
        # if __debug__:
        #    print("Bob1:")

        r = random.randint(0, 11)  # 3~A
        for j in range(0, 4):
            # if __debug__:
            #    print("Bob1 card[%d]" %(pool[r][0]))
            card[seatId].append(pool[r][0])
            del pool[r][0]

        s = random.randint(0, 11)
        while (s == r):
            s = random.randint(0, 11)
        # if __debug__:
        #    print("Bob2:")
        for j in range(0, 4):
            # if __debug__:
            #    print("Bob2 card[%d]" %(pool[s][0]))
            card[seatId].append(pool[s][0])
            del pool[s][0]

        '''
        # 发飞机
        rand_feiji = 40
        if (config.has_key('RAND_FEIJI')):
            rand_feiji = config['RAND_FEIJI']
        r = random.randrange(0, 100, 1)
        if (r < rand_feiji):
            plane = random.randrange(0, 11)  # 飞机起点(3-K)
            # print "飞机: '%s' to '%s'"%(self.getPointByPos(plane), self.getPointByPos(plane+1))
            for i in range(0, 2):
                for j in range(0, 3):
                    card[seatId].append(pool[plane + i][0])
                    del pool[plane + i][0]
            curCardNum += 6
        else:
            pass
            # print "没有飞机"
        # 再随机一人一个三张

        for i in range(0, 3):
            if (i == seatId):
                continue
                #if (curCardNum > 14):
                #    continue
                #else:
                    #print "得到一个三张"
                #    curCardNum += 3
            r = random.randrange(0, 100, 1) % 13
            while (len(pool[r]) < 3):
                r = (r + 1) % 13
            for j in range(0, 3):
                card[i].append(pool[r][0])
                del pool[r][0]

        # 还剩下8个4张
        # 再随机每人两个对子
        duicount = 3
        if (config.has_key('COUNT_DUI')):
            duicount = config['COUNT_DUI']
        for i in range(0, 3):
            for j in range(0, duicount):
                if (i == seatId):
                    if (curCardNum > 15):
                        continue
                    else:
                        # print "得到一个对子"
                        curCardNum += 2
                r = random.randrange(0, 100, 1) % 13
                while (len(pool[r]) < 2):
                    r = (r + 1) % 13
                for k in range(0, 2):
                    card[i].append(pool[r][0])
                    del pool[r][0]'''

        # 整理剩下的牌，随机发出
        left = []
        for arr in pool:
            for c in arr:
                left.append(c)
        random.shuffle(left)
        for i in range(0, 3):
            while (len(card[i]) < 17):
                card[i].append(left[0])
                del left[0]

        # print card[seatId]
        # print pool
        # print left
        # rtn['base'] = left
        # rtn['card1']= card[0]
        # rtn['card2']= card[1]
        # rtn['card3']= card[2]
        card.append(left)
        return card
        # print rtn
