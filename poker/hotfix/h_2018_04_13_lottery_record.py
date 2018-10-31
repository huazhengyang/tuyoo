# -*- coding: utf-8 -*-
"""
Created on 2017年10月26日

@author: zhaoliang
"""
from freetime.util import log as ftlog
import poker.util.timestamp as pktimestamp

def addMatchLotteryRecord(self, userId, gameId, matchId, curLotteryTime, rewardDesc, rewardDict):
    """
    添加一个比赛奖池分奖记录
    
    已开奖，奖励加到上一期之中
    """
    pass
from poker.entity.game.rooms.async_upgrade_hero_match_ctrl.match_record import AsyncUpgradeHeroMatchRecords
AsyncUpgradeHeroMatchRecords.addMatchLotteryRecord = addMatchLotteryRecord