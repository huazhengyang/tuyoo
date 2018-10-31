# -*- coding:utf-8 -*-
'''
Created on 2016年12月1日

@author: zhaojiangang
'''
from dizhucomm.core.base import TableCommand
from dizhucomm.core.const import Oper


class SitdownCommand(TableCommand):
    '''
    @param isNextBuyin: 结算界面，点击继续的带入标记(原字段名buyin)
    '''
    def __init__(self, player, seat=None, isNextBuyin=False):
        super(SitdownCommand, self).__init__()
        self.player = player
        self.seat = seat
        self.isNextBuyin = isNextBuyin

class StandupCommand(TableCommand):
    def __init__(self, seat, reason):
        super(StandupCommand, self).__init__()
        self.seat = seat
        self.reason = reason

class GiveupCommand(TableCommand):
    def __init__(self, seat):
        super(GiveupCommand, self).__init__()
        self.seat = seat
        
class ReadyCommand(TableCommand):
    def __init__(self, seat, isReciveVoice=False):
        super(ReadyCommand, self).__init__()
        self.seat = seat
        self.isReciveVoice = isReciveVoice
    
class ReadyTimeoutCommand(TableCommand):
    def __init__(self, seat):
        super(ReadyTimeoutCommand, self).__init__()
        self.seat = seat
        
class CallCommand(TableCommand):
    def __init__(self, seat, callValue, oper=Oper.USER):
        super(CallCommand, self).__init__()
        self.seat = seat
        self.callValue = callValue
        self.oper = oper

class CallTimeupCommand(TableCommand):
    def __init__(self, seat):
        super(CallTimeupCommand, self).__init__()
        self.seat = seat

class OutCardCommand(TableCommand):
    def __init__(self, seat, validCards, cardCrc, oper=Oper.USER):
        super(OutCardCommand, self).__init__()
        self.seat = seat
        self.validCards = validCards
        self.cardCrc = cardCrc
        self.oper = oper

class OutCardTimeupCommand(TableCommand):
    def __init__(self, seat):
        super(OutCardTimeupCommand, self).__init__()
        self.seat = seat

class ClearGameCommand(TableCommand):
    def __init__(self, reason):
        super(ClearGameCommand, self).__init__()
        self.reason = reason

class TuoguanCommand(TableCommand):
    ''' 
    @param isTuoguan: 若为None，则反转托管状态 
    '''
    def __init__(self, seat, isTuoguan=None):
        super(TuoguanCommand, self).__init__()
        self.seat = seat
        self.isTuoguan = isTuoguan

class AutoPlayCommand(TableCommand):
    '''
    @param isAutoPlay: 若为None，则反转自动出牌状态
    '''
    def __init__(self, seat, isAutoPlay=None):
        super(AutoPlayCommand, self).__init__()
        self.seat = seat
        self.isAutoPlay = isAutoPlay

class JiabeiTimeupCommand(TableCommand):
    ''' 加倍超时（农民加倍或者地主加倍） '''
    def __init__(self, seat):
        super(JiabeiTimeupCommand, self).__init__()
        self.seat = seat
        
class JiabeiCommand(TableCommand):
    ''' 加倍（农民加倍或者地主加倍） '''
    def __init__(self, seat, mutil):
        super(JiabeiCommand, self).__init__()
        assert(mutil > 0)
        self.seat = seat
        self.mutil = mutil
        
class ShowCardCommand(TableCommand):
    ''' 明牌 '''
    def __init__(self, seat):
        super(ShowCardCommand, self).__init__()
        self.seat = seat

class HuanpaiTimeupCommand(TableCommand):
    ''' 换牌超时 '''
    def __init__(self, seat):
        super(HuanpaiTimeupCommand, self).__init__()
        self.seat = seat
        
class HuanpaiOutcardsCommand(TableCommand):
    ''' 换牌出牌 '''
    def __init__(self, seat, outCards):
        super(HuanpaiOutcardsCommand, self).__init__()
        self.seat = seat
        self.outCards = outCards
