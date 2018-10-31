# coding=UTF-8
'''
'''
from dizhu.gameplays.gameplay_base import DizhuBaseGamePlay
from freetime.util import log as ftlog
import random
from dizhu.entity import dizhuconf


class DizhuErDouGamePlay(DizhuBaseGamePlay):


    def __init__(self, table):
        DizhuBaseGamePlay.__init__(self, table)
        self.max_rangpai = 4  # 不能改！


    def getPlayMode(self):
        return dizhuconf.PLAYMODE_ERDOU


    def _getRangpaiMultiWinLose(self):
        rangpai = self.table.status.rangPai
        diZhu = self.table.status.diZhu
        for x in xrange(len(self.table.seats)):
            seat = self.table.seats[x]
            if x + 1 == diZhu :
                if len(seat.cards) == 0:
                    return 1
            else:
                cardcount = len(seat.cards)
                if cardcount <= rangpai:
                    return rangpai - cardcount + 1 
        return 1


    def _doCallDizhuVerify(self, player, grab, call):
        '''
        校验,是否可以进行叫地主的操作
        '''
        if self.table.status.nowOper != player.seatId :
            return False

        callStr = self.table.status.callStr
        if  self.table.runConfig.rangpaiMultiType == 2 and len(callStr) > 0:
            if int(callStr[-2:None]) == 16:
                return False

        if len(callStr) >= self.max_rangpai + 1:
            return False

        if len(callStr) > 0:
            last_ = int(callStr[-1])
            if last_ == 0:
                if call in (0, 1):
                    return True
                else:
                    return False
            else:
                if self.table.runConfig.rangpaiMultiType == 1:
                    if call in (last_ + 1, 0):
                        return True
                    else:
                        return False
                else:
                    if call in (last_ * 2, 0):
                        return True
                    else:
                        return False                
        else:
            if call in (0, 1):
                return True
            else:
                return False
        return True


    def _doCallDizhuSetCall(self, player, call):
        oldCall = self.table.status.callGrade   
        seat = self.table.seats[player.seatIndex]
        seat.call123 = call
        if call > 0:
            self.table.status.diZhu = player.seatId
            self.table.status.callGrade = call
            callStr = self.table.status.callStr
            if len(callStr) > 1 and int(callStr[0]) > 0:
                self.table.status.rangPai += 1             
        return True if oldCall > 0 else False


    def _checkGameStart(self):
        '''
        检查当前是否叫地主的状态, 
        返回值 : 0 - 叫地主结束, 开始出牌
                < 0 都不叫, 流局
                > 0 需要继续叫地主
        '''
        callStr = self.table.status.callStr
        tclen = len(callStr)
        if tclen < 2:
            return 1
        
        if self.table.runConfig.rangpaiMultiType == 2 :
            if int(callStr[-2:None]) == 16:
                return 0
            
        if tclen == self.max_rangpai + 1:
            return 0
        
        if callStr[0] == '0':
            if callStr[1] == '0':
                return -1
            else:
                return 0
        else:
            if callStr[-1] == '0':
                return 0
            else:
                return 1


    def _chooseFirstCall(self):
        nowop = random.randint(1, 2)
        self.table.status.nowOper = nowop
        self.grabCard = random.choice(self.table.seats[nowop - 1].cards)
        # 第一次的nowop仅是初始化,真正的第一个叫地主者为下一个人

        
    def _checkWinLose(self, player):
        ftlog.debug('player->', player.userId)
        if self.table.status.diZhu == player.seatId:
            if len(self.table.seats[player.seatIndex].cards) == 0:
                return True
        else:
            if len(self.table.seats[player.seatIndex].cards) <= self.table.status.rangPai:
                return True
        return False

