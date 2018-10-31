# -*- coding:utf-8 -*-
'''
Created on 2017年5月25日

@author: wangyonghui
'''
from dizhu.entity import dizhuconf
from dizhu.gamecards.dizhu_card_quicklaizi import CardDizhuQuickLaiZi
from dizhu.games.groupmatch.policies import GroupMatchFirstCallPolicyImpl, SendCardsPolicy3PlayerChampionLimit
from dizhucomm.core.const import JiabeiMode
from dizhucomm.core.playmode import DealerBase
from dizhucomm.core.policies import RoundIdGenRedis, TuoguanPolicyDefault, AutoChupaiPolicyDefault
from dizhucomm.playmodes.base import SM_NORMAL, CallPolicyClassic3Player, CallPolicyHappy3Player, SettlementPolicyMatch, CallPolicyLaizi
from dizhucomm.playmodes.laizi import SM_LAIZI, PLAY_MODE_QUICKLAIZI
from dizhucomm.playmodes.normal import PLAY_MODE_NORMAL_CLASSIC, PLAY_MODE_NORMAL_HAPPY


class DDZDealerNormalClassic(DealerBase):
    '''发牌官，掌管桌子的状态以及各种策略'''
    def __init__(self):
        super(DDZDealerNormalClassic, self).__init__(
            sm=SM_NORMAL,
            playMode=PLAY_MODE_NORMAL_CLASSIC,
            jiabeiMode=JiabeiMode.AFTER_FLIP_BASE_CARD,
            roundIdGenPolicy=RoundIdGenRedis(),
            callPolicy=CallPolicyClassic3Player(),
            sendCardsPolicy=SendCardsPolicy3PlayerChampionLimit(),
            firstCallPolicy=GroupMatchFirstCallPolicyImpl(),
            tuoguanPolicy=TuoguanPolicyDefault(),
            buyinPolicy=None,
            autoChupaiPolicy=AutoChupaiPolicyDefault(),
            settlementPolicy=SettlementPolicyMatch(),
        )


class DDZDealerNormalHappy(DealerBase):
    '''发牌官，掌管桌子的状态以及各种策略'''
    def __init__(self):
        super(DDZDealerNormalHappy, self).__init__(
            sm=SM_NORMAL,
            playMode=PLAY_MODE_NORMAL_HAPPY,
            jiabeiMode=JiabeiMode.AFTER_FLIP_BASE_CARD,
            roundIdGenPolicy=RoundIdGenRedis(),
            callPolicy=CallPolicyHappy3Player(),
            sendCardsPolicy=SendCardsPolicy3PlayerChampionLimit(),
            firstCallPolicy=GroupMatchFirstCallPolicyImpl(),
            tuoguanPolicy=TuoguanPolicyDefault(),
            buyinPolicy=None,
            autoChupaiPolicy=AutoChupaiPolicyDefault(),
            settlementPolicy=SettlementPolicyMatch(),
        )

class DDZDealerQuickLaizi(DealerBase):
    '''发牌官，掌管桌子的状态以及各种策略'''
    def __init__(self):
        super(DDZDealerQuickLaizi, self).__init__(
            sm=SM_LAIZI,
            playMode=PLAY_MODE_QUICKLAIZI,
            jiabeiMode=JiabeiMode.AFTER_FLIP_BASE_CARD,
            roundIdGenPolicy=RoundIdGenRedis(),
            callPolicy=CallPolicyLaizi(),
            sendCardsPolicy=CardDizhuQuickLaiZi(),
            firstCallPolicy=GroupMatchFirstCallPolicyImpl(),
            tuoguanPolicy=TuoguanPolicyDefault(),
            buyinPolicy=None,
            autoChupaiPolicy=AutoChupaiPolicyDefault(),
            settlementPolicy=SettlementPolicyMatch()
        )

DIZHU_DEALER_DICT = {
    dizhuconf.PLAYMODE_123: DDZDealerNormalClassic(),
    dizhuconf.PLAYMODE_HAPPY: DDZDealerNormalHappy(),
    dizhuconf.PLAYMODE_QUICKLAIZI: DDZDealerQuickLaizi()
}

