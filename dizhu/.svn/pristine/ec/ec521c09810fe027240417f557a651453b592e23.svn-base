# -*- coding=utf-8 -*-

# from dizhu.gametable.dizhu_sender import DizhuSender
# from dizhu.gametable.dizhu_table import DizhuTable
from freetime.util import log as ftlog
# from dizhu.gamecards.cardcenter import CardHappy
from dizhu.gametable.dizhu_player import DizhuPlayer


class Punish(object):

    def __init__(self, table, sender, card):
        self.table = table
        self.sender = sender
        self.card = card
#         if not table :  # table必定有值, 此处为了代码自动提示而设置
#             self.table = DizhuTable()
#         if not sender :  # table必定有值, 此处为了代码自动提示而设置
#             self.sender = DizhuSender(self.table)
#         if not card :  # table必定有值, 此处为了代码自动提示而设置
#             self.card = CardHappy()
        

    def isRobotAutoCall(self, userId, grab, call, tuoGuanType):
        '''
        叫地主之前如果选择托管，则自动不叫或不抢
        '''
        if tuoGuanType != DizhuPlayer.TUGUAN_TYPE_USERACT :
            call = self.table.runConfig.punishAutoCall
            grab = self.table.runConfig.punishAutoGrab
        return grab, call

 
    def pushRobotPunishMsg(self, seatId, issendout):
        '''
        托管时，如果牌数再2张以上，提醒玩家有可能被惩罚
        '''
        ftlog.debug('Punish->pushRobotPunishMsg', self.table.tableId, seatId, issendout)
        seat = self.table.seats[seatId - 1]
        if seat.isRobot == 1 :
            seat.robotCardCount = len(seat.cards)
        else:
            seat.robotCardCount = -1
            issendout = 0

        if issendout :
            ccount = len(seat.cards)
            pcount = self.table.runConfig.punishCardCount
            if pcount > 0 and ccount > pcount:
                self.sender.sendPunishTipRes(seatId, seat.userId,
                                             self.table.runConfig.punishTip)
 
 
    def doRobotAutoCard(self, seatId, tuoGuanType):
        '''
        托管时, 自动出牌
        必须出牌时出牌，剩一张并且能出时出牌，其它情况都不出
        '''
        handcard = self.table.seats[seatId - 1].cards
        if len(handcard) > 0:
            topseat = self.table.status.topSeatId
            topcard = self.table.status.topCardList
            ftlog.debug('doRobotAutoCard->seatId=', seatId,
                        'tuoGuanType=', tuoGuanType,
                        'topseat=', topseat,
                        'topcard=', topcard,
                        'handcard=', handcard)
            
            if topseat == 0 or topseat == seatId:
                # 必须要出牌
                if (self.table.seats[seatId - 1].robotCardCount <= self.table.runConfig.punishCardCount
                    or tuoGuanType == DizhuPlayer.TUGUAN_TYPE_SYS_FAST_CARD):
                    # 系统调度快速出牌
                    return self.card.findFirstCards(handcard)
                else:
                    return self.card.findFirstSmallCard(handcard)
            
            if len(handcard) < self.table.runConfig.punishCardCount:
                # 只剩一张牌，自动出牌
                return self.card.findGreaterCards(topcard, handcard)
        # 不出牌
        return []
#         
#         if len(handcard) > 0 :
#             topseat = self.table.status.topSeatId
#             topcard = self.table.status.topCardList
#             ftlog.debug('doRobotAutoCard->seatId=', seatId, 'tuoGuanType=', tuoGuanType, 'topseat=', topseat, 'topcard=', topcard,
#                         'robotCardCount=', self.table.seats[seatId - 1].robotCardCount,
#                         'punishCardCount=', self.table.runConfig.punishCardCount)
#             # 系统调度快速出牌            
#             if tuoGuanType == DizhuPlayer.TUGUAN_TYPE_SYS_FAST_CARD:
#                 if topseat == 0 or topseat == seatId:
#                     cards = self.card.findFirstCards(handcard)
#                 else:
#                     if len(handcard) == 1 :
#                         # 只剩一张牌，自动出牌
#                         cards = self.card.findGreaterCards(topcard, handcard)
#                     else:
#                         # 上家出了火箭，不出牌
#                         cards = []
#             # 真正的托管状态
#             elif tuoGuanType == DizhuPlayer.TUGUAN_TYPE_TIMEOUT or tuoGuanType == DizhuPlayer.TUGUAN_TYPE_ALREADY_TUOGUAN :
#                 # 判定是否全部托管
#                 isAllRobot = 0
#                 for seat in self.table.seats :
#                     isAllRobot += seat.isRobot 
#                 isAllRobot = 1 if isAllRobot == len(self.table.seats) else 0
#                 isPunish = 1 if self.table.seats[seatId - 1].robotCardCount > self.table.runConfig.punishCardCount else 0
#                 # 如果托管时牌数小于等于2，那么自动出牌，否者不出牌
#                 if topseat == 0 or topseat == seatId:
#                     if isAllRobot :
#                         if isPunish :
#                             cards = self.card.findFirstSmallCard(handcard)  # 应该是出最小的牌
#                             ftlog.debug('Punish->doRobotAutoCard findFirstSmallCard 1->', cards)
#                         else:
#                             cards = self.card.findFirstCards(handcard)
#                             ftlog.debug('Punish->doRobotAutoCard findFirstCards 2->', cards)
#                     else:
#                         if isPunish :
#                             cards = self.card.findFirstSmallCard(handcard)  # 应该是出最小的牌
#                             ftlog.debug('Punish->doRobotAutoCard findFirstSmallCard 3->', cards)
#                         else:
#                             cards = self.card.findFirstCards(handcard)
#                             ftlog.debug('Punish->doRobotAutoCard findFirstCards 4->', cards)
#                 else:
#                     if isAllRobot :
#                         if isPunish :
#                             cards = []
#                             ftlog.debug('Punish->doRobotAutoCard no card 5->', cards)
#                         else:
#                             cards = self.card.findGreaterCards(topcard, handcard)
#                             ftlog.debug('Punish->doRobotAutoCard findGreaterCards 6->', cards)
#                     else:
#                         if isPunish :
#                             cards = []
#                             ftlog.debug('Punish->doRobotAutoCard no card 7->', cards)
#                         else:
#                             cards = self.card.findGreaterCards(topcard, handcard)
#                             ftlog.debug('Punish->doRobotAutoCard findGreaterCards 8->', cards)
#         return cards            


    # 结束时，手牌>2且托管的玩家会受到相应处罚
    # 一个农民托管
    # 如果农民胜利，则地主正常扣分，得分加给无托管农民。
    # 如果农民失败，则所有扣分都从托管农民方扣除，加给地主
    @classmethod
    def doWinLosePunish(cls, punishCardCount, ismatch, seat_coin, seat_delta, seat_card_count):
        # 获取牌桌结果基本信息
        pcount = punishCardCount
        if pcount <= 0 :
            return

        isDizhuWin = 0
        for delta in seat_delta:
            if delta < 0 :
                isDizhuWin = isDizhuWin + 1
        isDizhuWin = (isDizhuWin == 2)
        
        # 构造数据
        player_datas = []
        for index in xrange(len(seat_delta)):
            player_data = PunishHelper(index)
            player_data.coin = seat_coin[index]
            player_data.delta = seat_delta[index]
            player_data.isWin = player_data.delta >= 0
            player_data.isDizhu = player_data.isWin == isDizhuWin
            player_data.isPunish = seat_card_count[index] > pcount
            player_datas.append(player_data)
            ftlog.debug('Punish->doWinLosePunish before', player_data.Str())

        # 修正托管影响
        pfIndex = PunishHelper.doWinloseTune(player_datas, isDizhuWin, ismatch)
        
        for player in player_datas:
            ftlog.debug('Punish->doWinLosePunish after', player.Str())
               
        # 重置结果数据    
        for index in xrange(len(player_datas)):
            seat_coin[index] = player_datas[index].coin
            seat_delta[index] = player_datas[index].delta
            
        return pfIndex

class PunishHelper():
    def __init__(self, index):
        self.isDizhu = False
        self.isWin = False
        self.isPunish = False
        self.coin = 0
        self.delta = 0
        self.index = index
    
    def Tune(self):
        if self.isPunish and self.isWin:
            self.coin = self.coin - self.delta
            self.delta = 0
    
    def Str(self):
        return 'punish_helper:%d %d %d %d %d %d' % (self.index, self.coin, self.delta, self.isDizhu, self.isWin, self.isPunish)
    
    @classmethod            
    def doWinloseTune(cls, players, dizhu_win, canNagtive=False):
        punish_index = []
        dizhu_index = 0
        for index in xrange(len(players)):
            if players[index].isPunish and not players[index].isDizhu:
                punish_index.append(index)
            if players[index].isDizhu:
                dizhu_index = index
                
        pf_index = -1
        player_count = len(players)
        if player_count == 2:
            for index in xrange(len(players)):
                players[index].Tune()
            
        elif player_count == 3:            
            # 普通托管处理是:如果胜利了 则不赢; 如果失败了 则正常扣除
            # 特殊情况是:如果地主胜利并且有一个农民是托管,那么尽量把正常玩牌农民损失转移到托管农民     
            if not(len(punish_index) == 1 and dizhu_win):
                for index in xrange(len(players)):
                    players[index].Tune()
            else:
                # 托管农民索引和另外一农民索引
                pf_index = punish_index[0]
                of_index = 3 - dizhu_index - pf_index
                
                # 查看是否可以正常转嫁 delta是负值
                remain_coin = players[pf_index].coin + players[of_index].delta
                
                # 地主最终获得可获得的筹码
                finily_coin = 0
                
                # 先给正常农民恢复到结算前数据
                players[of_index].coin -= players[of_index].delta
                of_index_delta = players[of_index].delta
                players[of_index].delta = 0
                
                # 判断损失是否可以正常转嫁
                # 如果可以,则损失全部有托管农民负担
                # 如果不可以,先将托管农民负担,剩余的又正常农民负担
                if remain_coin >= 0 or canNagtive:
                    players[pf_index].coin += of_index_delta
                    players[pf_index].delta += of_index_delta
                else:
                    # 处理托管农民
                    finily_coin = players[pf_index].coin
                    players[pf_index].delta -= players[pf_index].coin
                    players[pf_index].coin = 0
                    # 处理非托管农民
                    if remain_coin * -1 > players[of_index].coin:
                        finily_coin += players[of_index].coin
                        players[of_index].delta = players[of_index].coin * -1
                        players[of_index].coin = 0
                    else:
                        players[of_index].delta = remain_coin
                        players[of_index].coin += remain_coin
                        finily_coin = 0
                
                # 处理地主
                if players[dizhu_index].isPunish:
                    players[dizhu_index].Tune()
                elif finily_coin != 0:
                    players[dizhu_index].coin -= players[dizhu_index].delta - finily_coin
                    players[dizhu_index].delta = finily_coin
        return pf_index
    
if __name__ == '__main__':
    seat_coin = [900, 100, 100]
    seat_delta = [184938, -92496, -92496]
    isDizhuWin = True
    is_punish = [False, True, False]
    player_datas = []
    print('before punish process')
    for index in xrange(3):
        player_data = PunishHelper(index)
        player_data.coin = seat_coin[index]
        player_data.delta = seat_delta[index]
        player_data.isWin = player_data.delta > 0
        player_data.isDizhu = player_data.isWin and isDizhuWin
        player_data.isPunish = is_punish[index]
        player_datas.append(player_data)
        print(player_data.Str())
        
    PunishHelper.doWinloseTune(player_datas, isDizhuWin, False)
    
    print('after punish process')
    for helper in player_datas:
        print(helper.Str())
    
    pass
