# -*- coding=utf-8 -*-
 
# Author:        zipxing@hotmail.com
# Company:       YouXia.Inc
# Created:       2012年04月23日 星期一 16时10分35秒
# FileName:      3card.py
# Class:         3card.GameTable 

import random

T3CARD_SZ = {'2.3.4':1, '3.4.5':2, '4.5.6':3, '5.6.7':4, \
                 '6.7.8':5, '7.8.9':6, '8.9.10':7, '9.10.11':8, '10.11.12':9, \
                 '0.11.12':10}
GOODSEAT_LOOP_MIN = 4
GOODSEAT_LOOP_MAX = 9
######################################################################
# 斗地主扑克算法
#
class CardDizhu():
    @classmethod
    def getPointByPos(self, pos):
        if (pos < 8):
            return "%d" % (pos + 3)
        elif (pos == 8):
            return "J"
        elif (pos == 9):
            return "Q"
        elif (pos == 10):
            return "K"
        elif (pos == 11):
            return "A"
        elif (pos == 12):
            return "2"
        elif (pos == 13):
            return "joker"
        elif (pos == 14):
            return "JOKER"

    @classmethod
    def getGoodSeatId(self, total, config):
        goodList = []
        loop = GOODSEAT_LOOP_MIN
        #modify by zw 2013-10-25 for 随机周期发好牌
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
        if loop_bottom < GOODSEAT_LOOP_MIN:
            loop_bottom = GOODSEAT_LOOP_MIN
        if loop_top > GOODSEAT_LOOP_MAX :
            loop_top = GOODSEAT_LOOP_MAX
        for i in range(0, len(total)):
            #新手保护
            if total[i] <= newPlayCount:
                newPlayerRatio = random.randint(1, 100)
                if newPlayerRatio < newPlayLuck:
                    goodList.append(i)
                continue
            #随机周期
            if (total[i] % random.randint(loop_bottom, loop_top) == 0):
                goodList.append(i)
        #end modify by zw 2013-10-25

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
    def DDZDealCard_Base(self, config):
        # print "随机底牌"
        rand_bc1 = 50
        if (config.has_key('RAND_BC1')):
            rand_bc1 = config['RAND_BC1']
        #modify by zw 2013-10-25 for 增加底牌类型 大牌型（A、2、jocker）
        rand_bc2 = 30
        if (config.has_key('RAND_BC2')):
            rand_bc2 = config['RAND_BC2']
        rand_bc3 = 20
        if (config.has_key('RAND_BC3') ):
            rand_bc3 = config['RAND_BC3']
        total_rand_bc = rand_bc1 + rand_bc2 + rand_bc3
        if (total_rand_bc) != 100 :
            #配置错误，按比例缩放
            #if __debug__:
            #    print("Bad rand_bc[%d:%d:%d], modify its" %(rand_bc1, rand_bc2, rand_bc3))
            rand_bc1 = (rand_bc1 * 100) // total_rand_bc
            rand_bc2 = (rand_bc2 * 100) // total_rand_bc
            rand_bc3 = 100 - rand_bc1 - rand_bc2
            #if __debug__:
            #    print("modified rand_bc[%d:%d:%d]" %(rand_bc1, rand_bc2, rand_bc3))
        pool = []
        base = []
        card = [[], [], []]
        rtn = {}
        # for i in range(0, 54):
        #    pool.append(i)
        pool = range(54)
        r = random.randrange(0, 100, 1)
        #if __debug__:
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
            #大牌型底牌
            littlePool=[0, 13, 26, 39, 1, 14, 27, 40, 52, 53]
            littlePoolLen=len(littlePool)
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

    #原有火箭加飞机
    @classmethod
    def DDZDealCard_GoodSeatA(self, seatId, config):
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
#         # 发2
#         rand_two = 2
#         if (config.has_key('COUNT_TWO')):
#             rand_two = config['COUNT_TWO']
#         n = random.randrange(1, rand_two + 1, 1)
#         for i in range(0, n):
#             # print "得到一张 '2'"
#             card[seatId].append(pool[12][0])  # 按花色顺序放2
#             del pool[12][0]
#         curCardNum += n
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

    #新增火箭加双顺 by zw 2013-10-25
    @classmethod
    def DDZDealCard_GoodSeatB(self, seatId, config):
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
#         # 发2
#         rand_two = 2
#         if (config.has_key('COUNT_TWO')):
#             rand_two = config['COUNT_TWO']
#         n = random.randrange(1, rand_two + 1, 1)
#         for i in range(0, n):
#             # print "得到一张 '2'"
#             card[seatId].append(pool[12][0])  # 按花色顺序放2
#             del pool[12][0]
#         curCardNum += n
        # 发双顺
        rand_shuangshun = 40
        if (config.has_key('RAND_SHUANGSHUN')):
            rand_shuangshun = config['RAND_SHUANGSHUN']
        r = random.randrange(0, 100, 1)
        if (r < rand_shuangshun):
            plane = random.randint(0, 9)  # 双顺起点(3-Q)
            #if __debug__:
            #    print("shuangshun: start[%d] r[%d]" %(plane, r))
            # print "飞机: '%s' to '%s'"%(self.getPointByPos(plane), self.getPointByPos(plane+1))
            for i in range(0, 3):
                for j in range(0, 2):
                    #if __debug__:
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

    #新增对2加双炸弹 by zw 2013-10-25
    @classmethod
    def DDZDealCard_GoodSeatC(self, seatId, config):
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
        #n = random.randrange(1, rand_two + 1, 1)
        n=2 #对2
        for i in range(0, n):
            # print "得到一张 '2'"
            card[seatId].append(pool[12][0])  # 按花色顺序放2
            del pool[12][0]
        curCardNum += n

        #发2个炸弹
        #if __debug__:
        #    print("Bob1:")
        except_card = [4] #降低7出现砸蛋的概率
        r = random.randint(0, 11) #3~A
        while ( r in except_card):
            r = random.randint(0, 11)
        except_card.append(r)
        for j in range(0, 4):
            #if __debug__:
            #    print("Bob1 card[%d]" %(pool[r][0]))
            card[seatId].append(pool[r][0])
            del pool[r][0]

        s = random.randint(0,11)
        while (s in except_card):
            s=random.randint(0,11)
        #if __debug__:
        #    print("Bob2:")
        for j in range(0, 4):
            #if __debug__:
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

    #GoodSeat 概率选择函数
    @classmethod
    def DDZDealCard_GoodSeat(self, seatId, config):
        goodSeatRandA=40
        goodSeatRandB=40
        goodSeatRandC=20
        if (config.has_key('GOODSEATA')):
            goodSeatRandA = config['GOODSEATA']
        if (config.has_key('GOODSEATB')):
            goodSeatRandB = config['GOODSEATB']
        if (config.has_key('GOODSEATC')):
            goodSeatRandC = config['GOODSEATC']
        #如果概率不为100，按比例缩放
        total_rand = goodSeatRandA + goodSeatRandB + goodSeatRandC
        if total_rand != 100 :
            goodSeatRandA = (goodSeatRandA * 100) // total_rand
            goodSeatRandB = (goodSeatRandB * 100) // total_rand
            goodSeatRandC = 100 - goodSeatRandA - goodSeatRandB

        r = random.randint(1, 100)
        #if __debug__:
        #    print("Get randint r[%d] ABC:[%d,%d,%d]" %(r, goodSeatRandA, goodSeatRandB, goodSeatRandC))
        if r <= goodSeatRandA:
            return self.DDZDealCard_GoodSeatA(seatId, config)
        elif r <= goodSeatRandB + goodSeatRandA:
            return  self.DDZDealCard_GoodSeatB(seatId, config)
        else:
            return  self.DDZDealCard_GoodSeatC(seatId, config)


    @classmethod
    def sendCard2(self, total, config):
        seatId = self.getGoodSeatId(total, config)
        # print "goodSeat:%d"%(seatId)
        if (seatId == 0):
            return seatId, self.DDZDealCard_Base(config)
        else:
            return seatId, self.DDZDealCard_GoodSeat(seatId, config)

    # total = [random.randrange(0, 100), random.randrange(0, 100), random.randrange(0, 100)];
    # config = {'GOOD_LOOP' : 5, 'RAND_GOOD' : 70, 'RAND_BC' : 50}
    # dc.DDZDealCard(total, config)

    '''
    四个最重要的方法：
    def getCardsType(self, cards):                  给定一个cardlist，判断是否合法
    def compareCards(self, cards_1, cards_2):       比较两组cardlist的大小
    def findGreaterCards(self, cards, hand_cards):      从手牌里找到能管住cardlist的牌
    def findFirstCards(hand_cards):                  从手牌里挑一组牌出
    '''
    # 当前桌子发牌,并计算出玩家手牌的分数
    @classmethod
    def sendCard(self, seatCount, lucky):
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
    
    @classmethod
    def getShuffleCardList(self, bc):
        card_list = list(set(range(54)) - set(bc))
        random.shuffle(card_list)
        return card_list
    
    @classmethod
    def cards2bucket(self, cards):
        bucket = [[] for i in xrange(15)]
        dmap = [11, 12, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 13, 14]
        for s in cards:
            ccol, cnum = self.getCNById(s)
            bucket[dmap[cnum]].append(ccol)
        return bucket
    
    #---------------------------------------------------------------------------------
    # 底牌加倍，双王和同花顺，4倍；同花，顺子，三张3倍；大王或小王2倍
    #---------------------------------------------------------------------------------
    @classmethod
    def getBcMulti(self, basecard):
        bctype = self.getBaseCardType(basecard)
        return self.getBcMultiByBcType(bctype)
    
    @classmethod
    def getBcMultiByBcType(self, bctype):
        value = bctype / 1000000
        if value == 6 or value == 9:
            return 4
        elif value == 8:
            return 2
        else:
            if value >= 4:
                return 3
        return 1
    
    #---------------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------------
    @classmethod
    def getBaseCardType(self, basecard):
        colormap = {}
        nummap = {}
        szlist = [0] * 14
        isTonghua = 0
        isDuizi = 0
        isBaozi = 0
        isShunzi = 0
        is235 = 0
        cards = []
        color = ['a', 'b', 'c', 'd']
        
        if 52 in basecard and 53 in basecard:
            return 9000000
        else:
            if 52 in basecard:
                return 8000000 + 52
            elif 53 in basecard:
                return 8000000 + 53
        
        for c in basecard:
            # cards.append([color[c/13], c%13+2])
            cards.append([color[c / 13], c % 13])
        for c in xrange(len(cards)):
            color = cards[c][0]
            num = cards[c][1]
            # 牌点桶，用于排序
            szlist[num] = 1
            # 统计花色表
            if color in colormap:
                colormap[color] += 1
            else:
                colormap[color] = 1
                # 统计牌点表
            if num in nummap:
                nummap[num].append(color)
            else:
                nummap[num] = [color]
            # 对三张手牌进行排序
        szsort = []
        for i in xrange(14):
            if szlist[i] == 1:
                szsort.append(str(i))
        szstr = '.'.join(szsort)
        if len(colormap) == 1:
            isTonghua = 1
        if len(nummap) == 1:
            isBaozi = 1
        if len(nummap) == 2:
            isDuizi = 1
            for k in nummap:
                if len(nummap[k]) == 2:
                    dui = k
                if len(nummap[k]) == 1:
                    dan = k
            newcards = []
            newcards.append((nummap[dui][0], dui))
            newcards.append((nummap[dui][1], dui))
            newcards.append((nummap[dan][0], dan))
        if szstr in T3CARD_SZ:
            if T3CARD_SZ[szstr] == 0:
                is235 = 1
            else:
                isShunzi = T3CARD_SZ[szstr]  # 查顺子表，如果是顺子，返回顺子的大小
        if isBaozi:
            return 7000000 + cards[0][1] * 10000
        if isShunzi and isTonghua:
            return 6000000 + isShunzi * 10000
        if isTonghua and not isShunzi:
            return 5000000 + int(szsort[2]) * 10000 + int(szsort[1]) * 100 + int(szsort[0])
        if isShunzi and not isTonghua:
            return 4000000 + isShunzi * 10000
        if isDuizi:
            return 3000000 + dui * 10000 + dan * 100
        if is235 and not isTonghua:
            # if hasbaozi:
            #    return 8000000
            return 1000000
        return 2000000 + int(szsort[2]) * 10000 + int(szsort[1]) * 100 + int(szsort[0])  # 散牌

    @classmethod
    def sortCardA(self, bucket):
        cells = []
        for bi in xrange(15):
            bidx = 14 - bi
            t = bucket[bidx]
            if len(t) != 0:
                cellnum = bidx + 1
                cellcol = []
                for o in t:
                    cellcol.append(o)
                cells.append([cellnum, cellcol, 0])
        return cells
    
    @classmethod
    def sortCardB(self, bucket):
        cells = []
        for ni in xrange(4):
            nidx = 3 - ni
            for bi in xrange(15):
                bidx = 14 - bi
                t = bucket[bidx]
                if len(t) - 1 == nidx:
                    cellnum = bidx + 1
                    cellcol = []
                    for o in t:
                        cellcol.append(o)
                    cells.append([cellnum, cellcol, 0])
        return cells

    # 输入牌列表，返回牌型及是否合法
    @classmethod
    def getCardsType(self, cards):
        dmap = [11, 12, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 13, 14]
        # print cards
        clen = len(cards)
        c, n = [], []
        cellsA, cellsB = [], []
        if clen <= 3:
            for card in cards:
                tcn = self.getCNById(card)
                c.append(tcn[0])
                n.append(dmap[tcn[1]] + 1)
        else:
            bucket = self.cards2bucket(cards)
            cellsA = self.sortCardA(bucket)
            cellsB = self.sortCardB(bucket)
        # 单牌
        if clen == 1:
            return 300 + n[0]
        if clen == 2:
            if n[0] == n[1]:
                # 对子
                return 400 + n[0]
            else:
                # 火箭
                if n[0] > 13 and n[1] > 13:
                    return 100
        if clen == 3:
            if n[0] == n[1] and n[1] == n[2]:
                # 三张
                return 500 + n[0]
        if clen == 4:
            if len(cellsA) == 1:
                # 炸弹
                return 200 + cellsA[0][0]
            if len(cellsB) == 2:
                if len(cellsB[0][1]) == 3 and len(cellsB[1][1]) == 1:
                    # 三带1
                    return 600 + cellsB[0][0]
        if clen == 5:
            if len(cellsB) == 2:
                if len(cellsB[0][1]) == 3 and len(cellsB[1][1]) == 2:
                    # 三带2
                    return 700 + cellsB[0][0]
        if clen >= 5:
            if len(cellsA) == clen:
                if not cellsA[0][0] >= 13:
                    issz = 1
                    for x in xrange(clen - 1):
                        if cellsA[x][0] - cellsA[x + 1][0] != 1:
                            issz = 0
                            break
                    if issz == 1:
                        # 单顺
                        return 800 + cellsA[0][0]
        if clen >= 6 and clen % 2 == 0:
            ac2 = 1
            for cell in cellsB:
                if len(cell[1]) != 2:
                    ac2 = 0
                    break
            if ac2:
                if len(cellsB) == clen / 2:
                    if not cellsB[0][0] >= 13:
                        is2sz = 1
                        for x in xrange(clen / 2 - 1):
                            if cellsB[x][0] - cellsB[x + 1][0] != 1:
                                is2sz = 0
                                break
                        if is2sz == 1:
                            # 双顺
                            return 900 + cellsB[0][0]
        if clen >= 6 and clen % 3 == 0:
            if len(cellsB) == clen / 3:
                if not cellsB[0][0] >= 13:
                    is3sz = 1
                    for x in xrange(clen / 3 - 1):
                        if cellsB[x][0] - cellsB[x + 1][0] != 1:
                            is3sz = 0
                            break
                    if is3sz == 1:
                        # 三顺
                        return 1000 + cellsB[0][0]
        #if clen >= 8 and clen % 4 == 0:
        #    slen = clen / 4
        #    if len(cellsB) > slen:
        #        if not cellsB[0][0] >= 13:
        #            is3sz = 1
        #            for x in xrange(slen - 1):
        #                if cellsB[x][0] - cellsB[x + 1][0] != 1:
        #                    is3sz = 0
        #                    break
        #            if is3sz == 1:
        #                # 飞机带翅膀单
        #                return 1100 + cellsB[0][0]
        #if clen >= 10 and clen % 5 == 0:
        #    slen = clen / 5
        #    if len(cellsB) > slen:
        #        if not cellsB[0][0] >= 13:
        #            is3sz = 1
        #            for x in xrange(slen - 1):
        #                if cellsB[x][0] - cellsB[x + 1][0] != 1:
        #                    is3sz = 0
        #                    break
        #            if is3sz == 1:
        #                isfjc = 1
        #                for x in xrange(slen - 1):
        #                    if len(cellsB[slen + x][1]) != 2:
        #                        isfjc = 0
        #                        break
        #                if isfjc == 1:
        #                    # 飞机带翅膀对
        #                    return 1200 + cellsB[0][0]
        if clen == 6:
            if len(cellsB[0][1]) == 4:
                # 四带二
                return 1300 + cellsB[0][0]
        if clen == 8:
            if len(cellsB[0][1]) == 4:
                if len(cellsB[1][1]) == 2 and len(cellsB[2][1]) == 2:
                    # 四带二对
                    return 1400 + cellsB[0][0]
        if clen == 0:
            return 1500
        return 0

    # 比较两组牌大小
    # 返回1表示card1能管住card2,返回0表示不能管,返回-1表示不可比
    @classmethod
    def compareCards(self, cards_1, cards_2):
        s1 = self.getCardsType(cards_1)
        s2 = self.getCardsType(cards_2)
        # print s1, s2
        if s1 == 0 or s2 == 0:
            return -1
        if s1 == 100:
            return 1
        if s2 == 100:
            return 0
        if s1 / 100 == 2 and s2 / 100 == 2:
            return int(s1 > s2)
        if s1 / 100 == 2 and s2 / 100 > 2:
            return 1
        if s1 / 100 > 2 and s2 / 100 == 2:
            return 0
        if s1 / 100 > 2 and s2 / 100 > 2:
            if len(cards_1) != len(cards_2):
                return -1
            else:
                if s1 / 100 != s2 / 100:
                    return -1
                else:
                    return int(s1 > s2)
        return -1
    
    @classmethod
    def fbctool(self, hand_cards, cellsA, cellsB, cards, ctype):
        # print ctype
        if ctype / 100 == 1:
            return []
        if ctype / 100 == 2:
            for cell in cellsB:
                if len(cell[1]) < 4:
                    return []
                if cell[0] > ctype % 100:
                    return [self.getIdByCN(cell[1][0], cell[0]),
                        self.getIdByCN(cell[1][1], cell[0]),
                        self.getIdByCN(cell[1][2], cell[0]),
                        self.getIdByCN(cell[1][3], cell[0])]
        if ctype / 100 == 3:
            for cell in reversed(cellsB):
                if cell[0] > ctype % 100:
                    return [self.getIdByCN(cell[1][0], cell[0])]
        if ctype / 100 == 4:
            for cell in reversed(cellsB):
                if len(cell[1]) < 2:
                    continue
                if cell[0] > ctype % 100:
                    return [self.getIdByCN(cell[1][0], cell[0]),
                        self.getIdByCN(cell[1][1], cell[0])]
        if ctype / 100 == 5:
            for cell in reversed(cellsB):
                if len(cell[1]) < 3:
                    continue
                if cell[0] > ctype % 100:
                    return [self.getIdByCN(cell[1][0], cell[0]),
                        self.getIdByCN(cell[1][1], cell[0]),
                        self.getIdByCN(cell[1][2], cell[0])]
        if ctype / 100 == 6:
            single = None
            if len(hand_cards) < 4:
                return []
            for cell in reversed(cellsB):
                if len(cell[1]) < 3:
                    continue
                if cell[0] > ctype % 100:
                    cell[2] = 1  # 标记这个cell已经被取出，从剩下的cell里取单张
                    for ncell in reversed(cellsB):
                        if ncell[2] == 0:
                            single = self.getIdByCN(ncell[1][0], ncell[0])
                            break
                    cell[2] = 0
                    if single == None:
                        return []
                    else:
                        return [self.getIdByCN(cell[1][0], cell[0]),
                            self.getIdByCN(cell[1][1], cell[0]),
                            self.getIdByCN(cell[1][2], cell[0]), single]
        if ctype / 100 == 7:
            if len(hand_cards) < 5:
                return []
            for cell in reversed(cellsB):
                if len(cell[1]) < 3:
                    continue
                if cell[0] > ctype % 100:
                    cell[2] = 1
                    double = []
                    for ncell in reversed(cellsB):
                        if ncell[2] == 0:
                            if len(ncell[1]) < 2:
                                continue
                            double = [self.getIdByCN(ncell[1][0], ncell[0]), self.getIdByCN(ncell[1][1], ncell[0])]
                            break
                    cell[2] = 0
                    if len(double) == 2:
                        return [self.getIdByCN(cell[1][0], cell[0]),
                            self.getIdByCN(cell[1][1], cell[0]),
                            self.getIdByCN(cell[1][2], cell[0]), double[0], double[1]]
        if ctype / 100 == 8:
            if len(hand_cards) < len(cards):
                return []
            maxsstart = 0
            maxscount = 0
            sstart = 0
            scount = 0
            for ci in xrange(len(cellsA) - 1):
                if cellsA[ci][0] - cellsA[ci + 1][0] == 1 and cellsA[ci][0] < 13:
                    scount += 1
                    if scount > maxscount:
                        maxscount = scount
                        maxsstart = sstart
                else:
                    sstart = ci + 1
                    scount = 0
            scount = maxscount + 1
            sstart = maxsstart
            if scount >= len(cards):
                for si in xrange(scount - len(cards) + 1, 0, -1):
                    tops = cellsA[sstart + si - 1][0]
                    if tops > ctype % 100:
                        shunzi = []
                        for sss in xrange(len(cards)):
                            shunzi.append(self.getIdByCN(cellsA[sstart + si - 1 + sss][1][0], cellsA[sstart + si - 1 + sss][0]))
                        return shunzi
        if ctype / 100 == 9:
            if len(hand_cards) < len(cards):
                return []
            tmpcell = []
            for ci in xrange(len(cellsA)):
                if len(cellsA[ci][1]) >= 2:
                    tmpcell.append(cellsA[ci])
            if len(tmpcell) < len(cards) / 2:
                return []
            maxsstart = 0
            maxscount = 0
            sstart = 0
            scount = 0
            for ci in xrange(len(tmpcell) - 1):
                if tmpcell[ci][0] - tmpcell[ci + 1][0] == 1 and tmpcell[ci][0] < 13:
                    scount += 1
                    if scount > maxscount:
                        maxscount = scount
                        maxsstart = sstart
                else:
                    sstart = ci + 1
                    scount = 0
            scount = maxscount + 1
            sstart = maxsstart
            if scount >= len(cards) / 2:
                for si in xrange(scount - len(cards) / 2 + 1, 0, -1):
                    tops = tmpcell[sstart + si - 1][0]
                    if tops > ctype % 100:
                        shunzi = []
                        for sss in xrange(len(cards) / 2):
                            shunzi.append(self.getIdByCN(tmpcell[sstart + si - 1 + sss][1][0], tmpcell[sstart + si - 1 + sss][0]))
                            shunzi.append(self.getIdByCN(tmpcell[sstart + si - 1 + sss][1][1], tmpcell[sstart + si - 1 + sss][0]))
                        return shunzi
        if ctype / 100 == 10:
            if len(hand_cards) < len(cards):
                return []
            tmpcell = []
            for ci in xrange(len(cellsA)):
                if len(cellsA[ci][1]) >= 3:
                    tmpcell.append(cellsA[ci])
            if len(tmpcell) < len(cards) / 3:
                return []
            maxsstart = 0
            maxscount = 0
            sstart = 0
            scount = 0
            for ci in xrange(len(tmpcell) - 1):
                if tmpcell[ci][0] - tmpcell[ci + 1][0] == 1 and tmpcell[ci][0] < 13:
                    scount += 1
                    if scount > maxscount:
                        maxscount = scount
                        maxsstart = sstart
                else:
                    sstart = ci + 1
                    scount = 0
            scount = maxscount + 1
            sstart = maxsstart
            if scount >= len(cards) / 3:
                for si in xrange(scount - len(cards) / 3 + 1, 0, -1):
                    tops = tmpcell[sstart + si - 1][0]
                    if tops > ctype % 100:
                        shunzi = []
                        for sss in xrange(len(cards) / 3):
                            shunzi.append(self.getIdByCN(tmpcell[sstart + si - 1 + sss][1][0], tmpcell[sstart + si - 1 + sss][0]))
                            shunzi.append(self.getIdByCN(tmpcell[sstart + si - 1 + sss][1][1], tmpcell[sstart + si - 1 + sss][0]))
                            shunzi.append(self.getIdByCN(tmpcell[sstart + si - 1 + sss][1][2], tmpcell[sstart + si - 1 + sss][0]))
                        return shunzi
        if ctype / 100 == 11:
            if len(hand_cards) < len(cards):
                return []
            tmpcell = []
            for ci in xrange(len(cellsA)):
                if len(cellsA[ci][1]) >= 3:
                    tmpcell.append(cellsA[ci])
            if len(tmpcell) < len(cards) / 4:
                return []
            maxsstart = 0
            maxscount = 0
            sstart = 0
            scount = 0
            for ci in xrange(len(tmpcell) - 1):
                if tmpcell[ci][0] - tmpcell[ci + 1][0] == 1 and tmpcell[ci][0] < 13:
                    scount += 1
                    if scount > maxscount:
                        maxscount = scount
                        maxsstart = sstart
                else:
                    sstart = ci + 1
                    scount = 0
            scount = maxscount + 1
            sstart = maxsstart
            # print sstart, scount
            if scount >= len(cards) / 4:
                for si in xrange(scount - len(cards) / 4 + 1, 0, -1):
                    tops = tmpcell[sstart + si - 1][0]
                    if tops > ctype % 100:
                        shunzi = []
                        for sss in xrange(len(cards) / 4):
                            shunzi.append(self.getIdByCN(tmpcell[sstart + si - 1 + sss][1][0], tmpcell[sstart + si - 1 + sss][0]))
                            shunzi.append(self.getIdByCN(tmpcell[sstart + si - 1 + sss][1][1], tmpcell[sstart + si - 1 + sss][0]))
                            shunzi.append(self.getIdByCN(tmpcell[sstart + si - 1 + sss][1][2], tmpcell[sstart + si - 1 + sss][0]))
                        leftcard = list(set(hand_cards) - set(shunzi))
                        lcb = self.sortCardB(self.cards2bucket(leftcard))
                        lscount = 0
                        for leftcell in lcb:
                            for lfx in xrange(len(leftcell[1])):
                                shunzi.append(self.getIdByCN(leftcell[1][lfx], leftcell[0]))
                                lscount += 1
                                if lscount >= len(cards) / 4:
                                    return shunzi
        if ctype / 100 == 12:
            if len(hand_cards) < len(cards):
                return []
            tmpcell = []
            for ci in xrange(len(cellsA)):
                if len(cellsA[ci][1]) >= 3:
                    tmpcell.append(cellsA[ci])
            if len(tmpcell) < len(cards) / 5:
                return []
            maxsstart = 0
            maxscount = 0
            sstart = 0
            scount = 0
            for ci in xrange(len(tmpcell) - 1):
                if tmpcell[ci][0] - tmpcell[ci + 1][0] == 1:
                    scount += 1
                    if scount > maxscount:
                        maxscount = scount
                        maxsstart = sstart
                else:
                    sstart = ci + 1
                    scount = 0
            scount = maxscount + 1
            sstart = maxsstart
            if scount >= len(cards) / 5:
                for si in xrange(scount - len(cards) / 5 + 1, 0, -1):
                    tops = tmpcell[sstart + si - 1][0]
                    if tops > ctype % 100:
                        shunzi = []
                        for sss in xrange(len(cards) / 5):
                            shunzi.append(self.getIdByCN(tmpcell[sstart + si - 1 + sss][1][0], tmpcell[sstart + si - 1 + sss][0]))
                            shunzi.append(self.getIdByCN(tmpcell[sstart + si - 1 + sss][1][1], tmpcell[sstart + si - 1 + sss][0]))
                            shunzi.append(self.getIdByCN(tmpcell[sstart + si - 1 + sss][1][2], tmpcell[sstart + si - 1 + sss][0]))
                        leftcard = list(set(hand_cards) - set(shunzi))
                        lcb = self.sortCardB(self.cards2bucket(leftcard))
                        lscount = 0
                        for leftcell in reversed(lcb):
                            if len(leftcell[1]) >= 2:
                                shunzi.append(self.getIdByCN(leftcell[1][0], leftcell[0]))
                                shunzi.append(self.getIdByCN(leftcell[1][1], leftcell[0]))
                                lscount += 1
                                if lscount >= len(cards) / 5:
                                    return shunzi
        if ctype / 100 == 13:
            if len(hand_cards) < len(cards):
                return []
            tmpcell = None
            leftcell = []
            for cell in reversed(cellsB):
                if len(cell[1]) == 4 and cell[0] > ctype % 100:
                    tmpcell = cell
                else:
                    leftcell.append(cell)
            if tmpcell:
                si2dan = []
                si2dan.append(self.getIdByCN(0, tmpcell[0]))
                si2dan.append(self.getIdByCN(1, tmpcell[0]))
                si2dan.append(self.getIdByCN(2, tmpcell[0]))
                si2dan.append(self.getIdByCN(3, tmpcell[0]))
                lscount = 0
                for lf in leftcell:
                    for lfx in xrange(len(lf[1])):
                        si2dan.append(self.getIdByCN(lf[1][lfx], lf[0]))
                        lscount += 1
                        if lscount >= 2:
                            return si2dan
        if ctype / 100 == 14:
            if len(hand_cards) < len(cards):
                return []
            tmpcell = None
            leftcell = []
            for cell in reversed(cellsB):
                if len(cell[1]) == 4 and cell[0] > ctype % 100:
                    tmpcell = cell
                else:
                    leftcell.append(cell)
            if tmpcell:
                si2dui = []
                si2dui.append(self.getIdByCN(0, tmpcell[0]))
                si2dui.append(self.getIdByCN(1, tmpcell[0]))
                si2dui.append(self.getIdByCN(2, tmpcell[0]))
                si2dui.append(self.getIdByCN(3, tmpcell[0]))
                lscount = 0
                for lf in leftcell:
                    if len(lf[1]) < 2:
                        continue
                    for lfx in xrange(len(lf[1])):
                        si2dui.append(self.getIdByCN(lf[1][lfx], lf[0]))
                        lscount += 1
                        if lscount >= 4:
                            return si2dui
        return []

    # 从手牌里找出比cards大的
    @classmethod
    def findGreaterCards(self, cards, hand_cards):
        hand_type = self.getCardsType(hand_cards)
        if hand_type == 100:
            return hand_cards
        bucket = self.cards2bucket(hand_cards)
        cellsA = self.sortCardA(bucket)
        cellsB = self.sortCardB(bucket)
        huojian = 0
        zhadan = 0
        if len(cellsA) >= 2 and cellsA[0][0] == 15 and cellsA[1][0] == 14:
            huojian = 1
        for cell in cellsB:
            if len(cell[1]) == 4:
                zhadan = cell[0]
            else:
                break
        ctype = self.getCardsType(cards) 
        ret = self.fbctool(hand_cards, cellsA, cellsB, cards, ctype)
        if len(ret) == 0 and (ctype / 100) == 2:
            if huojian == 1:
                return [52, 53]
        if len(ret) == 0 and (ctype / 100) > 2:
            if zhadan != 0:
                return [self.getIdByCN(0, zhadan),
                    self.getIdByCN(1, zhadan),
                    self.getIdByCN(2, zhadan),
                    self.getIdByCN(3, zhadan)]
            if huojian == 1:
                return [52, 53]
        return ret

    # 从手牌里，选出要出的牌，放单张
    @classmethod
    def findFirstCards(self, hand_cards):
        card_type = self.getCardsType(hand_cards)
        if card_type != 0 and card_type != 1500:
            return hand_cards
        bucket = self.cards2bucket(hand_cards)
        cellsA = self.sortCardA(bucket)
        cellsB = self.sortCardB(bucket)
        retcards = []
        # 查找双顺
        tmpcell = []
        for ci in xrange(len(cellsA)):
            if len(cellsA[ci][1]) == 2:
                tmpcell.append(cellsA[ci])
        maxsstart = 0
        maxscount = 0
        sstart = 0
        scount = 0
        for ci in xrange(len(tmpcell) - 1):
            if tmpcell[ci][0] - tmpcell[ci + 1][0] == 1 and tmpcell[ci][0] < 13:
                scount += 1
                if scount > maxscount:
                    maxscount = scount
                    maxsstart = sstart
            else:
                sstart = ci + 1
                scount = 0
        scount = maxscount + 1
        sstart = maxsstart
        if scount >= 3:
            for sss in xrange(scount):
                retcards.append(self.getIdByCN(tmpcell[sstart + sss][1][0], tmpcell[sstart + sss][0]))
                retcards.append(self.getIdByCN(tmpcell[sstart + sss][1][1], tmpcell[sstart + sss][0]))
            return retcards
        # 查找顺子
        maxsstart = 0
        maxscount = 0
        sstart = 0
        scount = 0
        for ci in xrange(len(cellsA) - 1):
            if cellsA[ci][0] - cellsA[ci + 1][0] == 1 and cellsA[ci][0] < 13:
                scount += 1
                if scount > maxscount:
                    maxscount = scount
                    maxsstart = sstart
            else:
                sstart = ci + 1
                scount = 0
        scount = maxscount + 1
        sstart = maxsstart
        if scount >= 5:
            for sss in xrange(scount):
                retcards.append(self.getIdByCN(cellsA[sstart + sss][1][0], cellsA[sstart + sss][0]))
            return retcards
        # 查找三带2
        for cell in reversed(cellsB):
            if len(cell[1]) != 3:
                continue
            cell[2] = 1
            double = []
            for ncell in reversed(cellsB):
                if ncell[2] == 0:
                    if len(ncell[1]) < 2:
                        continue
                    double = [self.getIdByCN(ncell[1][0], ncell[0]), self.getIdByCN(ncell[1][1], ncell[0])]
                    break
            cell[2] = 0
            if len(double) == 2:
                return [self.getIdByCN(cell[1][0], cell[0]),
                    self.getIdByCN(cell[1][1], cell[0]),
                    self.getIdByCN(cell[1][2], cell[0]), double[0], double[1]]
        # 查找三带1
        for cell in reversed(cellsB):
            if len(cell[1]) != 3:
                continue
            cell[2] = 1  # 标记这个cell已经被取出，从剩下的cell里取单张
            single = []
            for ncell in reversed(cellsB):
                if ncell[2] == 0:
                    single = [self.getIdByCN(ncell[1][0], ncell[0])]
                    break
            cell[2] = 0
            if len(single) == 1:
                return [self.getIdByCN(cell[1][0], cell[0]),
                    self.getIdByCN(cell[1][1], cell[0]),
                    self.getIdByCN(cell[1][2], cell[0]), single[0]]
            else:
                return [self.getIdByCN(cell[1][0], cell[0]),
                    self.getIdByCN(cell[1][1], cell[0]),
                    self.getIdByCN(cell[1][2], cell[0])]
        # 查找对子
        for cell in reversed(cellsB):
            if len(cell[1]) != 2:
                continue
            return [self.getIdByCN(cell[1][0], cell[0]),
                self.getIdByCN(cell[1][1], cell[0])]

        cell = cellsB[-1]
        for x in cell[1]:
            retcards.append(self.getIdByCN(x, cell[0]))
        return retcards

    @classmethod
    def findFirstSmallCard(self, hand_cards):
        card_type = self.getCardsType(hand_cards)
        if card_type != 0 and card_type != 1500:
            return hand_cards
        bucket = self.cards2bucket(hand_cards)
        cellsB = self.sortCardB(bucket)
        retcards = []
        cell = cellsB[-1]
        for x in cell[1]:
            retcards.append(self.getIdByCN(x, cell[0]))
        return retcards
    
    @classmethod
    def getIdByCN(self, color, num):
        imap = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 0, 1]
        if color == 4:
            return num + 38
        return imap[num - 1] + color * 13
    
    @classmethod
    def getCNById(self, cid):
        if cid > 53 or cid < 0:
            return ''
        if cid < 52:
            return (cid / 13, cid % 13)  # 0~12
        else:
            return (4, cid - 52 + 13)  # 13,14

    @classmethod
    def isDoubleKing(self, cards):
        if len(cards) == 2 :
            if (cards[0] == 53 or cards[0] == 52) and(cards[1] == 53 or cards[1] == 52) :
                return True
        return False

    #测试发牌
    @classmethod
    def _test_sendCard(self):
        #test 底牌
        for i in range(0, 100000):
            print("---->No.[%d]------------------------------" %(i) )
            cards=self.DDZDealCard_Base({'RAND_BC1':20, 'RAND_BC2':40, 'RAND_BC3':40})
            print(cards[3])
        for i in range(0, 100000):
            print("---->No.[%d]------------------------------" %i)
            cards=self.DDZDealCard_GoodSeat(3, {'GOODSEATA':0, 'GOODSEATB':100, 'GOODSEATC':0, 'RAND_SHUANGSHUN':100})
            print(cards[0])
            print(cards[1])
            print(cards[2])


if __name__ == '__main__':
    #if __debug__:
    #    print("=====================================================")
    dizhu = CardDizhu()
    dizhu._test_sendCard()
    print CardDizhu.findFirstCards([3, 16, 29, 42, 0])
    print CardDizhu.findFirstSmallCard([3, 16, 29, 42, 52, 53])
    print CardDizhu.getCardsType([3, 16, 29, 42, 10])
    print CardDizhu.getCardsType([52, 53])
    print CardDizhu.findFirstSmallCard([52, 53])
    print CardDizhu.findGreaterCards([0], [3, 16, 29, 42])
