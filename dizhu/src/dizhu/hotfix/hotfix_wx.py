# -*- coding:utf-8 -*-
'''
Created on 2016年12月22日

@author: zhaojiangang
'''

from dizhucomm.playmodes.base import SendCardsPolicy3PlayerDefault
from freetime.util import log as ftlog
from hall.entity import hallvip


def sendCard2(self, table, config):
    '''
    tatal=[]
    '''
    # 机器人房间好牌
    if table.room.roomConf.get('isAI'):
        for index, seat in enumerate(table.seats):
            if not seat.player.isAI:
                seatPlayCount = seat.player.datas.get('plays', 0)
                if ftlog.is_debug():
                    ftlog.debug('SendCardsPolicy3PlayerDefault choiceGoodCardSeat userId=', seat.userId,
                                'seatPlayCount=', seatPlayCount)
                return seat, self.DDZDealCard_GoodSeat(index, config, True if not seatPlayCount else False)

    otherPlayersCareerRound = table.runConf.datas.get('otherPlayersCareerRound', 3)
    # playCounts = [seat.player.datas.get('plays', 0) for seat in table.seats]
    # newPlayCount = config.get('NEWPLAY_COUNT', 5)
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
            # from hall.entity import hallvip
            vipLevel = hallvip.userVipSystem.getUserVip(userId).vipLevel
            if not vipLevel:
                newPlayer = True

            if ftlog.is_debug:
                ftlog.debug('sendCard2. career first round. userId=', userId,
                            'seatPlayCount=', seatPlayCount,
                            'uservip=', vipLevel,
                            'newPlayer=', newPlayer)

        return table.gameRound.seats[seatIndex], self.DDZDealCard_GoodSeat(seatIndex, config, newPlayer)


SendCardsPolicy3PlayerDefault.sendCard2 = sendCard2
