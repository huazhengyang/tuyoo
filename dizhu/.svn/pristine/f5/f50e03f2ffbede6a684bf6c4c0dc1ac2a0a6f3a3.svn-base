#-*- coding:utf-8 -*-

####################################################################################
#
# Copyright © 2017 TU. All Rights Reserved.
#
####################################################################################

"""

@File: dizhuuserdata.py

@Description: 地主游戏数据，主要封装gamedata里的一些常用数据

@Author: leiyunfei(leiyunfei@tuyoogame.com)

@Depart: 棋牌中心-斗地主项目组

@Create: 2017-05-22 12:05:41

"""


from freetime.util import log as ftlog

from poker.entity.dao import gamedata
from poker.util import strutil

from dizhu.entity.dizhuconf import DIZHU_GAMEID


def getUserPlayCount(userId):
    """
    获取用户打过的牌局数
    @return {'total': 总局数，'win': 胜局数}
    """
    swinrate = gamedata.getGameAttrs(userId, DIZHU_GAMEID, ['winrate'])
    if ftlog.is_debug():
        ftlog.debug('getUserPlayCount', 'swinrate=', swinrate[0])
    swinrate = strutil.loads(swinrate[0],
                             ignoreException=True,
                             execptionValue={'pt':0, 'wt':0})
    ftlog.debug('getUserPlayCount', 'swinrate=', swinrate)
    totalplays = swinrate.get('pt', 0)
    winplays = swinrate.get('wt', 0)
    return {'total': totalplays, 'win': winplays}
