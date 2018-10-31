# -*- coding:utf-8 -*-
'''
Created on 2017年05月31日

@author: wangyonghui
'''
from dizhu.games.erdayimatch.playmode import CallPolicyErdayi, SendCardPolicyErdayi, FirstCallPolicyErdayi, TuoguanPolicyErdayi, PLAYMODE_ERDAYI
from dizhucomm.core.const import JiabeiMode
from dizhucomm.core.playmode import DealerBase
from dizhucomm.core.policies import RoundIdGenRedis, AutoChupaiPolicyDefault
from dizhucomm.playmodes.base import SM_NORMAL, SettlementPolicyMatch


class DDZDealerErdaiyiMatch(DealerBase):
    '''发牌官，掌管桌子的状态以及各种策略'''
    def __init__(self):
        super(DDZDealerErdaiyiMatch, self).__init__(
            sm=SM_NORMAL,
            playMode=PLAYMODE_ERDAYI,
            jiabeiMode=JiabeiMode.BEFORE_FLIP_BASE_CARD,
            roundIdGenPolicy=RoundIdGenRedis(),
            callPolicy=CallPolicyErdayi(),
            sendCardsPolicy=SendCardPolicyErdayi(),
            firstCallPolicy=FirstCallPolicyErdayi(),
            tuoguanPolicy=TuoguanPolicyErdayi(),
            buyinPolicy=None,
            autoChupaiPolicy=AutoChupaiPolicyDefault(),
            settlementPolicy=SettlementPolicyMatch(),
        )

DDZDEALER_ERDAYI_MATCH = DDZDealerErdaiyiMatch()
