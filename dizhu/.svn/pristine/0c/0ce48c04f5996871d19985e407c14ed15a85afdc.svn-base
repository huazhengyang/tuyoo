# -*- coding=utf-8 -*-
"""
Created on 2017年8月31日

@author: wangjifa
"""
import random
import freetime.util.log as ftlog
from dizhu.gamecards import dizhu_card_quicklaizi

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

dizhu_card_quicklaizi.CardDizhuQuickLaiZi.DDZDealCard_GoodSeatA = DDZDealCard_GoodSeatA

