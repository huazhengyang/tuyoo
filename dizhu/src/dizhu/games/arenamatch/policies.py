# -*- coding:utf-8 -*-
'''
Created on 2018年1月18日

@author: wangyonghui
'''

from dizhucomm.core.policies import FirstCallPolicy, FirstCallPolicyRandom
import freetime.util.log as ftlog


class ArenaMatchFirstCallPolicyFinal(FirstCallPolicy):
    '''
    Arena决赛桌使用随机叫牌规则，在只打1副牌的情况下，决赛桌用户体验较差。
    调整: A用户打进Arena决赛圈后其同桌另外2名用户不一定一定为决赛圈用户，故：
    当3人中仅有1人为最后一轮时，此人名次为2、3名均首叫，名次为第1名时随机首叫
    当3人中有多人为最后一轮时，按当桌玩家排名第2、第3、第1的顺序进行首叫
    '''
    def chooseFirstCall(self, table):
        # 开关控制是否执行此次略
        if table.room.roomConf.get('finalCallSwitch', 0) != 1:
            return FirstCallPolicyRandom().chooseFirstCall(table)

        seats = sorted(table.gameRound.seats, key=lambda x: x.player.matchUserInfo['score'])
        # 获取进入决赛桌用户
        finalSeats = [seat for seat in seats if seat.player.matchUserInfo['isLastStage']]
        if not finalSeats or (len(finalSeats) == 1 and finalSeats[0].player.userId == seats[-1].player.userId):
            randomSeat = FirstCallPolicyRandom().chooseFirstCall(table)
            if ftlog.is_debug():
                ftlog.debug('ArenaMatchFirstCallPolicyFinal.chooseFirstCall randomSeat',
                            'roomId=', table.roomId,
                            'tableId=', table.tableId,
                            'userScores=', [(s.player.userId, s.player.matchUserInfo['score']) for s in seats],
                            'callPlayerUserId=', randomSeat.player.userId)
            return randomSeat

        # 按决赛桌用户积分排序
        finalSeats.sort(key=lambda x: x.player.matchUserInfo['score'])

        # 选择首叫用户，如果有一个直接返回否则返回第二个
        retSeat = finalSeats[0] if len(finalSeats) == 1 else finalSeats[1]
        if ftlog.is_debug():
            ftlog.debug('ArenaMatchFirstCallPolicyFinal.chooseFirstCall finalSeat',
                        'roomId=', table.roomId,
                        'tableId=', table.tableId,
                        'userScores=', [(s.player.userId, s.player.matchUserInfo['score']) for s in finalSeats],
                        'callPlayerUserId=', retSeat.player.userId)
        return retSeat
