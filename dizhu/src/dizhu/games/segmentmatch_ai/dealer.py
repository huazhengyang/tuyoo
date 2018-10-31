# -*- coding:utf-8 -*-
'''
Created on 2018年9月26日

@author: wangyonghui
'''
from dizhu.entity import dizhuconf
from dizhu.games.normalbase.policies import FirstCallPolicyImpl
from dizhu.games.segmentmatch_ai.policies import BuyinPolicySegment, SettlementPolicySegment
from dizhucomm.core.const import JiabeiMode
from dizhucomm.core.playmode import DealerBase
from dizhucomm.core.policies import RoundIdGenRedis, TuoguanPolicyDefault, AutoChupaiPolicyDefault
from dizhucomm.playmodes.base import SM_NORMAL, CallPolicyClassic3Player, SendCardsPolicy3PlayerDefault

from dizhucomm.playmodes.normal import PLAY_MODE_NORMAL_CLASSIC


class DDZDealerNormalClassic(DealerBase):
    '''发牌官，掌管桌子的状态以及各种策略'''
    def __init__(self):
        super(DDZDealerNormalClassic, self).__init__(
            sm=SM_NORMAL,
            playMode=PLAY_MODE_NORMAL_CLASSIC,
            jiabeiMode=JiabeiMode.AFTER_FLIP_BASE_CARD,
            roundIdGenPolicy=RoundIdGenRedis(),
            callPolicy=CallPolicyClassic3Player(),
            sendCardsPolicy=SendCardsPolicy3PlayerDefault(),
            firstCallPolicy=FirstCallPolicyImpl(),
            tuoguanPolicy=TuoguanPolicyDefault(),
            buyinPolicy=BuyinPolicySegment(),
            autoChupaiPolicy=AutoChupaiPolicyDefault(),
            settlementPolicy=SettlementPolicySegment()
        )

DIZHU_DEALER_DICT = {
    dizhuconf.PLAYMODE_123: DDZDealerNormalClassic(),
}
