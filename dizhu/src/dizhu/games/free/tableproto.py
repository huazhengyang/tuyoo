# -*- coding:utf-8 -*-
'''
Created on 2017年3月7日

@author: zhaojiangang
'''
from dizhu.games.normalbase.tableproto import DizhuTableProtoNormalBase


class DizhuTableProtoNormalFree(DizhuTableProtoNormalBase):
    def __init__(self, tableCtrl):
        super(DizhuTableProtoNormalFree, self).__init__(tableCtrl)
    
    def buildQuickStartResp(self, seat, isOK, reason):
        mp = super(DizhuTableProtoNormalFree, self).buildQuickStartResp(seat, isOK, reason)
        mp.setResult('tableType', 'free')
        return mp
    
    def buildResultDetails(self, result):
        luckyItemArgs = []
        winStreak = []
        skillScoreInfos = []
        cards = []
        addCoupons = []
        seatDetails = []
        seatInfos = []
        tableTasks = []
        for sst in result.seatStatements:
            waittime = self.table.runConf.optimeCall
            if sst.final < self.table.runConf.minCoin:
                waittime = int(waittime/3)
            details = [
                sst.delta,
                sst.seat.player.chip,
                0,
                waittime,
                0,
                0,
                sst.expInfo[0], sst.expInfo[1], sst.expInfo[2], sst.expInfo[3], sst.expInfo[4],
                sst.final
            ]
            seatDetails.append(details)
            luckyItemArgs.append({})
            winStreak.append(sst.winStreak)
            skillScoreInfos.append(sst.skillscoreInfo)
            cards.append(sst.seat.status.cards)
            addCoupons.append(0)
            tableTasks.append([])
            seatInfos.append({'punished': 1} if sst.isPunish else {})
        
        return {
            'winStreak':winStreak,
            'luckyItemArgs':luckyItemArgs,
            'skillScoreInfos':skillScoreInfos,
            'addcoupons':addCoupons,
            'cards':cards,
            'seatDetails':seatDetails,
            'seatInfos':seatInfos,
            'tableTasks':tableTasks
        }


