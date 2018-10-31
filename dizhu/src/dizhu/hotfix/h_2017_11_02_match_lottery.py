# -*- coding:utf-8 -*-
'''
Created on 2017年11月2日

@author: wangjifa
'''

import random

from dizhu.activities.toolbox import UserBag
from dizhu.entity import dizhu_util, dizhuconf
from dizhu.entity.dizhuconf import DIZHU_GAMEID
from dizhu.entity.dizhuversion import SessionDizhuVersion
from dizhu.entity.matchhistory import MatchHistoryHandler
from dizhucomm.entity import commconf
from hall.entity import hallconf, hallitem
import poker.util.timestamp as pktimestamp
import freetime.util.log as ftlog
from hall.entity.hallitem import ASSET_CHIP_KIND_ID, ASSET_COUPON_KIND_ID, ASSET_DIAMOND_KIND_ID
from poker.entity.biz.content import TYContentItem
from poker.entity.biz.exceptions import TYBizException, TYBizConfException
from poker.entity.configure import configure, gdata
from poker.entity.dao import sessiondata, daoconst, gamedata, userdata, daobase
from poker.entity.biz import bireport
from poker.util import strutil


def chooseReward(self, userId, matchId, rank):
    if ftlog.is_debug():
        ftlog.debug('MatchLottery userId=', userId, 'matchId=', matchId, 'rank=', rank)

    if not self.matchList:
        d = dizhuconf.getMatchLotteryConf()
        self.decodeFromDict(d)

    if not self.checkMatchRank(userId, matchId):
        ftlog.warn('MatchLottery.checkMatchRank failed. userId=', userId, 'matchId=', matchId, 'rank=', rank)
        return None, None

    items = self.getMatchLotteryConf(matchId, rank)
    if not items:
        ftlog.warn('MatchLottery.checkMatchRank failed. no items. userId=', userId, 'matchId=', matchId, 'rank=', rank)
        return None, None

    weights = 0
    for item in items:
        weights += item.get('weight', 0)
    r = random.randint(0, weights)
    lotteryReward = []
    weightTotal = 0
    for item in items:
        weightTotal += item.get('weight', 0)
        if r <= weightTotal:
            lotteryReward.append({'itemId': str(item.get('itemId')), 'count': item.get('count')})
            break
    lotteryReward = items[-1] if not lotteryReward else lotteryReward

    if ftlog.is_debug():
        ftlog.debug('MatchLottery weights=', weights, 'r=', r, 'userId=', userId, 'lotteryReward=', lotteryReward)

    if lotteryReward:
        contentItems = TYContentItem.decodeList(lotteryReward)
        assetList = dizhu_util.sendRewardItems(userId, contentItems, '', 'DIZHU_MATCH_LOTTERY', 0)

        ftlog.info('MatchLottery.chooseReward userId=', userId, 'matchId=', matchId, 'lotteryReward=', lotteryReward,
                   'assetList=', assetList)

    for i in items:
        assetKind = hallitem.itemSystem.findAssetKind(i['itemId'])
        i['img'] = assetKind.pic
        i['des'] = assetKind.desc
        i['name'] = assetKind.displayName

    if ftlog.is_debug():
        ftlog.debug('MatchLottery.chooseReward userId=', userId, 'matchId=', matchId, 'rank=', rank, 'lotteryReward=',
                    lotteryReward)

    return lotteryReward, items

from dizhu.games.matchutil import MatchLottery
MatchLottery.chooseReward = chooseReward
ftlog.info('h_2017_11_02_match_lottery ok')