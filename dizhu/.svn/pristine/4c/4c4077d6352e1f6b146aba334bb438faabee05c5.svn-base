# -*- coding=utf-8
'''
Created on 2015年8月18日

@author: zhaojiangang
'''

import freetime.util.log as ftlog
from poker.entity.events.tyevent import EventUserLogin
from hall.entity import hallranking
from poker.entity.biz.ranking.rankingsystem import TYRankingInputTypes
from dizhu.entity import skillscore

_inited = False

def _initialize():
    from dizhu.game import TGDizhu
    global _inited
    if not _inited:
        _inited = True
        ftlog.debug('dizhuranking._initialize begin')
        TGDizhu.getEventBus().subscribe(EventUserLogin, _onUserLogin)
        ftlog.debug('dizhuranking._initialize end')
        
def _onUserLogin(event):
    score = skillscore.get_skill_score(event.userId)
    hallranking.rankingSystem.setUserByInputType(event.gameId, TYRankingInputTypes.DASHIFEN,
                                                 event.userId, score, event.timestamp)


