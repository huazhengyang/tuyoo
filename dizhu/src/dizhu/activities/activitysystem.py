# -*- coding: utf-8 -*-
'''
Created on Aug 4, 2015

@author: hanwf
'''
from dizhu.activities import betguess
from dizhu.activities import funact
from dizhu.activities import table_replay_ranking
from dizhu.activities import luckymoneynew
from dizhu.activities.betguess import BetGuess
from dizhu.activities.bindphonelead import BindingPhoneHandler
from dizhu.activities.choujiang_360 import ChouJiang360
from dizhu.activities.dashi_send import DashiSend
from dizhu.activities.ddz_redenvelope import TYActivityDdzRedEnvelope, DdzRedEnvelope
from dizhu.activities.ddzfund import TYActivityFund, ActivityDdzFund
from dizhu.activities.dumplings import TYActivityDumplings, DumplingsUtil
from dizhu.activities.fivestarrate import FiveStarRate
from dizhu.activities.funact import FunAct
from dizhu.activities.item_sender import ItemSender
from dizhu.activities.login30_360 import Login30
from dizhu.activities.luckymoneynew import LuckyMoneyNew
from dizhu.activities.matchled import MatchLed
from dizhu.activities.matchscore import DdzMatchScore
from dizhu.activities.month_checkin import MonthCheckinGift, MonthCheckinGiftNum
from dizhu.activities.shareplayground import SharePlayground
from dizhu.activities.skilllevel_gift import SkillLevelGift
from dizhu.activities.table_replay_ranking import TableReplayRanking
from dizhu.activities.tehuilibao import TeHuiLiBao
from dizhu.activities.vip_send import VipSend
from dizhu.activities.wishingwell import WishingWell
from dizhu.activities.xingyaoled import XingyaoLed
from dizhu.activitynew.activity_score_ranking import ActivityScoreRankingHandler
from dizhu.activitynew.christmas import ActivityChristmasHandler
from dizhu.activitynew.match_promotion_list import TYActivityMatchPromotionList
from dizhu.game import TGDizhu
from poker.entity.biz.activity.activity import TYActivityRegister


def _initialize():
    import freetime.entity.config as ftcon
    if ftcon.global_config.get('is_h5', 0):
        _initialize_h5()
        return

    eventbus = TGDizhu.getEventBus()
    SharePlayground.registerEvents(eventbus)
    FiveStarRate.initialize()
    TeHuiLiBao.registerEvents()
    MatchLed.registerEvent(eventbus)
    Login30.registerEvents()
    ChouJiang360.registerEvents(eventbus)
    VipSend.registerEvents()
    DashiSend.registerEvents()
    DdzRedEnvelope.registerListener(eventbus)
    DumplingsUtil.registerListener(eventbus)
    XingyaoLed.initialize()
    DdzMatchScore.registerListeners(eventbus)
    SkillLevelGift.registerListeners(eventbus)
    ItemSender.registerListeners(eventbus)
    MonthCheckinGift.initialize()
    MonthCheckinGiftNum.initialize()
    BindingPhoneHandler.registerListeners(eventbus)
    ActivityDdzFund.initialize()
    # 大厅活动界面显示的活动处理

    # 基金活动
    TYActivityRegister.registerClass(TYActivityFund.TYPE_ID, TYActivityFund) #20

    # 地主红包活动
    TYActivityRegister.registerClass(TYActivityDdzRedEnvelope.TYPE_ID, TYActivityDdzRedEnvelope) # 6001
    TYActivityRegister.registerClass(TYActivityDdzRedEnvelope.TYPE_ID_PC, TYActivityDdzRedEnvelope) #6002

    # 饺子活动
    TYActivityRegister.registerClass(TYActivityDumplings.TYPE_ID, TYActivityDumplings) #6003
    TYActivityRegister.registerClass(TYActivityDumplings.TYPE_ID_PC, TYActivityDumplings) #6005

    # 许愿池活动
    TYActivityRegister.registerClass(WishingWell.TYPE_ID, WishingWell) #6011
    # 竞猜活动
    TYActivityRegister.registerClass(BetGuess.TYPE_ID, BetGuess) #6012
    # 牌局分享
    TYActivityRegister.registerClass(TableReplayRanking.TYPE_ID, TableReplayRanking) #6013
    # 趣味任务活动
    TYActivityRegister.registerClass(FunAct.TYPE_ID, FunAct) #6014
    # 新版红包
    TYActivityRegister.registerClass(LuckyMoneyNew.TYPE_ID, LuckyMoneyNew) # 6015
    # 华为大师杯
    TYActivityRegister.registerClass(ActivityScoreRankingHandler.TYPE_ID, ActivityScoreRankingHandler)
    # 比赛晋级列表
    TYActivityRegister.registerClass(TYActivityMatchPromotionList.TYPE_ID, TYActivityMatchPromotionList)
    # 圣诞活动
    TYActivityRegister.registerClass(ActivityChristmasHandler.TYPE_ID, ActivityChristmasHandler)
    # 下注竞猜活动
    betguess.initialize()
    
    funact.initialize()
    table_replay_ranking.initialize()
    luckymoneynew.initialize()

def _initialize_h5():
    from dizhu.activities.h5youku import YouKu

    YouKu.initialize()
