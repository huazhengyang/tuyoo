# -*- coding: utf-8 -*-
"""
Created on 2016年11月11日

修复快速赛未开赛提示
@author: zhaoliang
"""
import freetime.util.log as ftlog
from poker.entity.game.rooms.quick_upgrade_match_ctrl.exceptions import QUMError
from poker.entity.game.rooms.quick_upgrade_match_ctrl.match_report import QUMatchReport
from poker.entity.game.rooms.quick_upgrade_match_ctrl.game_player import QUMPlayer
import random
from poker.util import timestamp as pktimestamp

def signIn(self, userId, feeIndex, matchId):
    """
    报名比赛
    首先校验比赛开启/关闭时间
        比赛尚未开启，请稍后再来
        比赛马上结束，请稍后再来
        比赛已经结束，请稍后再来
    其次校验用户的金币条件
    第三收取服务费
    """
    pass
from poker.entity.game.rooms.quick_upgrade_match_ctrl.match import QUMatch
QUMatch.signIn = signIn