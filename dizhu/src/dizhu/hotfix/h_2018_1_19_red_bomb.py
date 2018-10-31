# -*- coding:utf-8 -*-
'''
Created on 2018年1月19日

@author: wangyonghui
'''

import freetime.util.log as ftlog
from dizhu.entity import dizhu_red_envelope_bomb


def getTableBombReward(bigRoomId, timestamp):
    """
    牌桌炸弹奖励, 牌桌一个炸弹就获取炸弹奖励， 如果有在后续roll点来进行分配策略
    """
    rateControl, countRateControl = dizhu_red_envelope_bomb.getInstance()._calculateRoomRedEnvelopeRate(bigRoomId, timestamp)
    # 进行概率判断
    ret = dizhu_red_envelope_bomb.getInstance()._rateChoice(rateControl)
    if not ret or not countRateControl:
        return None, False

    # 获取奖励
    rewardDict, isDouble = dizhu_red_envelope_bomb.getInstance()._getTemplateReward(bigRoomId)
    if not rewardDict:
        return None, False
    if rewardDict['type'] == 'redEnvelope':
        rewardDict['count'] = int(round(countRateControl * rewardDict['count'] + 0.5))

    if ftlog.is_debug():
        ftlog.debug('dizhu_red_envelope_bomb.getTableBombReward',
                    'bigRoomId=', bigRoomId,
                    'reward=', rewardDict,
                    'rateControl=', rateControl,
                    'countRateControl=', countRateControl,
                    'isDouble=', isDouble)
    return rewardDict, isDouble

dizhu_red_envelope_bomb.getInstance().getTableBombReward = getTableBombReward



