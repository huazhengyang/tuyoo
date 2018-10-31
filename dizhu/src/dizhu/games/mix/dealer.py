# -*- coding:utf-8 -*-
'''
Created on 2017年5月25日

@author: wangyonghui
'''
from dizhu.entity import dizhuconf
from dizhu.gamecards.dizhu_card_quicklaizi import CardDizhuQuickLaiZi
from dizhu.games.mix.playmode import GameRoundMix
from dizhu.games.mix.policies import BuyinPolicyMix, SettlementPolicyMix, CallPolicyErdouMix
from dizhu.games.normalbase.policies import FirstCallPolicyImpl
from dizhucomm.core.const import JiabeiMode
from dizhucomm.core.playmode import DealerBase
from dizhucomm.core.policies import RoundIdGenRedis, TuoguanPolicyDefault, AutoChupaiPolicyDefault
from dizhucomm.playmodes.base import SM_NORMAL, CallPolicyClassic3Player, SendCardsPolicy3PlayerDefault, \
    CallPolicyHappy3Player, CallPolicyLaizi
from dizhucomm.playmodes.erdou import SendCardsPolicyErdou, PLAY_MODE_ERDOU
from dizhucomm.playmodes.laizi import SM_LAIZI, PLAY_MODE_LAIZI, PLAY_MODE_QUICKLAIZI
from dizhucomm.playmodes.normal import PLAY_MODE_NORMAL_CLASSIC, PLAY_MODE_NORMAL_HAPPY


class DDZDealerMixClassic(DealerBase):
    '''发牌官，掌管桌子的状态以及各种策略'''
    def __init__(self):
        super(DDZDealerMixClassic, self).__init__(
            sm=SM_NORMAL,
            playMode=PLAY_MODE_NORMAL_CLASSIC,
            jiabeiMode=JiabeiMode.AFTER_FLIP_BASE_CARD,
            roundIdGenPolicy=RoundIdGenRedis(),
            callPolicy=CallPolicyClassic3Player(),
            sendCardsPolicy=SendCardsPolicy3PlayerDefault(),
            firstCallPolicy=FirstCallPolicyImpl(),
            tuoguanPolicy=TuoguanPolicyDefault(),
            buyinPolicy=BuyinPolicyMix(),
            autoChupaiPolicy=AutoChupaiPolicyDefault(),
            settlementPolicy=SettlementPolicyMix()
        )

    def newGameRound(self, table):
        '''
        创建一局游戏
        '''
        roundId = self.roundIdGenPolicy.genRoundId(table)
        gameRound = GameRoundMix()
        gameRound.init(table, roundId, table.seats[:])
        table._gameRound = gameRound
        return gameRound



class DDZDealerMixHappy(DealerBase):
    '''发牌官，掌管桌子的状态以及各种策略'''
    def __init__(self):
        super(DDZDealerMixHappy, self).__init__(
            sm=SM_NORMAL,
            playMode=PLAY_MODE_NORMAL_HAPPY,
            jiabeiMode=JiabeiMode.AFTER_FLIP_BASE_CARD,
            roundIdGenPolicy=RoundIdGenRedis(),
            callPolicy=CallPolicyHappy3Player(),
            sendCardsPolicy=SendCardsPolicy3PlayerDefault(),
            firstCallPolicy=FirstCallPolicyImpl(),
            tuoguanPolicy=TuoguanPolicyDefault(),
            buyinPolicy=BuyinPolicyMix(),
            autoChupaiPolicy=AutoChupaiPolicyDefault(),
            settlementPolicy=SettlementPolicyMix()
        )

    def newGameRound(self, table):
        '''
        创建一局游戏
        '''
        roundId = self.roundIdGenPolicy.genRoundId(table)
        gameRound = GameRoundMix()
        gameRound.init(table, roundId, table.seats[:])
        table._gameRound = gameRound
        return gameRound


class DDZDealerMixErdou(DealerBase):
    '''发牌官，掌管桌子的状态以及各种策略'''
    def __init__(self):
        super(DDZDealerMixErdou, self).__init__(
            sm=SM_NORMAL,
            playMode=PLAY_MODE_ERDOU,
            jiabeiMode=JiabeiMode.AFTER_FLIP_BASE_CARD,
            roundIdGenPolicy=RoundIdGenRedis(),
            callPolicy=CallPolicyErdouMix(),
            sendCardsPolicy=SendCardsPolicyErdou(),
            firstCallPolicy=FirstCallPolicyImpl(),
            tuoguanPolicy=TuoguanPolicyDefault(),
            buyinPolicy=BuyinPolicyMix(),
            autoChupaiPolicy=AutoChupaiPolicyDefault(),
            settlementPolicy=SettlementPolicyMix()
        )

    def newGameRound(self, table):
        '''
        创建一局游戏
        '''
        roundId = self.roundIdGenPolicy.genRoundId(table)
        gameRound = GameRoundMix()
        gameRound.init(table, roundId, table.seats[:])
        table._gameRound = gameRound
        return gameRound


class DDZDealerMixLaizi(DealerBase):
    '''发牌官，掌管桌子的状态以及各种策略'''
    def __init__(self):
        super(DDZDealerMixLaizi, self).__init__(
            sm=SM_LAIZI,
            playMode=PLAY_MODE_LAIZI,
            jiabeiMode=JiabeiMode.AFTER_FLIP_BASE_CARD,
            roundIdGenPolicy=RoundIdGenRedis(),
            callPolicy=CallPolicyLaizi(),
            sendCardsPolicy=SendCardsPolicy3PlayerDefault(),
            firstCallPolicy=FirstCallPolicyImpl(),
            tuoguanPolicy=TuoguanPolicyDefault(),
            buyinPolicy=BuyinPolicyMix(),
            autoChupaiPolicy=AutoChupaiPolicyDefault(),
            settlementPolicy=SettlementPolicyMix()
        )

    def newGameRound(self, table):
        '''
        创建一局游戏
        '''
        roundId = self.roundIdGenPolicy.genRoundId(table)
        gameRound = GameRoundMix()
        gameRound.init(table, roundId, table.seats[:])
        table._gameRound = gameRound
        return gameRound

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
            firstCallPolicy=FirstCallPolicyImpl(),
            tuoguanPolicy=TuoguanPolicyDefault(),
            buyinPolicy=BuyinPolicyMix(),
            autoChupaiPolicy=AutoChupaiPolicyDefault(),
            settlementPolicy=SettlementPolicyMix()
        )

    def newGameRound(self, table):
        '''
        创建一局游戏
        '''
        roundId = self.roundIdGenPolicy.genRoundId(table)
        gameRound = GameRoundMix()
        gameRound.init(table, roundId, table.seats[:])
        table._gameRound = gameRound
        return gameRound

DIZHU_DEALER_DICT = {
    dizhuconf.PLAYMODE_123: DDZDealerMixClassic(),
    dizhuconf.PLAYMODE_HAPPY: DDZDealerMixHappy(),
    dizhuconf.PLAYMODE_ERDOU: DDZDealerMixErdou(),
    dizhuconf.PLAYMODE_LAIZI: DDZDealerMixLaizi(),
    dizhuconf.PLAYMODE_QUICKLAIZI: DDZDealerQuickLaizi()
}
