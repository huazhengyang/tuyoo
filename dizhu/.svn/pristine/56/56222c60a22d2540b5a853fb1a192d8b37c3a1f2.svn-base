# coding=UTF-8
'''
'''
from dizhu.gameplays.gameplay_base import DizhuBaseGamePlay
from dizhu.entity import dizhuconf


class Dizhu123GamePlay(DizhuBaseGamePlay):
    
    
    def __init__(self, table):
        DizhuBaseGamePlay.__init__(self, table)
        

    def getPlayMode(self):
        return dizhuconf.PLAYMODE_123


    def _doCallDizhuVerify(self, player, grab, call):
        '''
        校验,是否可以进行叫地主的操作
        '''
        if self.table.status.nowOper != player.seatId :
            return False
        # 每人只能叫一次所以不能大于3
        if len(self.table.status.callStr) > 2:
            return False
        # 叫的分数不能比已经叫过的分数小(0除外)，而且不能大于3
        if call != 0 and (call <= self.table.status.callGrade or call > 3):
            return False
        return True


    def _doCallDizhuSetCall(self, player, call):
        seat = self.table.seats[player.seatIndex]
        seat.call123 = call
        if call > 0:
            self.table.status.callGrade = call
            self.table.status.diZhu = player.seatId
        return False


    def _checkGameStart(self):
        '''
        检查当前是否叫地主的状态, 
        返回值 : 0 - 叫地主结束, 开始出牌
                < 0 都不叫, 流局
                > 0 需要继续叫地主
        '''
        # 已经叫到3分了
        if self.table.status.callGrade > 2:
            return 0
        tclen = len(self.table.status.callStr)
        if tclen < 3:
            # 没有叫3分并且还有人没有叫
            return 1
        else:
            # 没人叫地主
            if self.table.status.callGrade <= 0:
                return -1
            return 0
        
