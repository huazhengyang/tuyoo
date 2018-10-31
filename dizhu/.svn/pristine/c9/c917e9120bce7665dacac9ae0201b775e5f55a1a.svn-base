# -*- coding=utf-8
'''
Created on 2015年10月10日

@author: zhaojiangang
'''
from datetime import datetime

from dizhu.entity.dizhuconf import DIZHU_GAMEID
from dizhucomm.entity.events import UserTableWinloseEvent
import freetime.util.log as ftlog
from hall.entity import fivestarrate as hallfivestarrate
from poker.entity.dao import sessiondata, userdata, gamedata
from poker.entity.events.tyevent import MatchWinloseEvent
from poker.util import strutil
import poker.util.timestamp as pktimestamp
from dizhu.entity import dizhuconf


class FiveStarRate(object):
    @classmethod
    def initialize(cls):
        from dizhu.game import TGDizhu
        eventBus = TGDizhu.getEventBus()
        eventBus.subscribe(MatchWinloseEvent, cls.onMatchWinlose)
        eventBus.subscribe(UserTableWinloseEvent, cls.onWinlose)
        
    @classmethod
    def onMatchWinlose(cls, event):
        clientId = sessiondata.getClientId(event.userId)
        timestamp = pktimestamp.getCurrentTimestamp()
        if ftlog.is_debug():
            ftlog.debug('FiveStarRate.onMatchWinlose userId=', event.userId,
                        'clientId=', clientId,
                        'signinUserCount=', event.signinUserCount,
                        'rank=', event.rank)
        # 玩家在比赛场获得名次时（100人以上的比赛获得前三名，或100人以下50人以上的比赛，获得第一名）
        if ((event.signinUserCount >= 100 and event.rank <= 3)
            or (event.signinUserCount >= 50 and event.signinUserCount < 100 and event.rank == 1)):
            winDesc = dizhuconf.getPublicConf('five_star_win_desc', '')
            hallfivestarrate.triggleFiveStarRateIfNeed(event.userId, clientId, timestamp, winDesc)
    
    @classmethod
    def calcRegisterDays(cls, userId, timestamp):
        nowDate = datetime.fromtimestamp(timestamp).date()
        createDate = datetime.strptime(userdata.getAttr(userId, 'createTime'), '%Y-%m-%d %H:%M:%S.%f').date()
        return max(0, (nowDate-createDate).days)
        
    @classmethod
    def onWinlose(cls, event):
        clientId = sessiondata.getClientId(event.userId)
        timestamp = pktimestamp.getCurrentTimestamp()
        if ftlog.is_debug():
            ftlog.debug('FiveStarRate.onWinlose userId=', event.userId,
                        'clientId=', clientId,
                        'roomId=', event.roomId,
                        'tableId=', event.tableId,
                        'winlose=', event.winlose.__dict__)
        if not event.winlose.isWin:
            return
        
        winDesc = dizhuconf.getPublicConf('five_star_win_desc', '')
        # 玩家在高倍场馆单局倍数超过128倍并获胜，且获胜得到的金币大于20W时
        if event.winlose.windoubles >= 128:
            hallfivestarrate.triggleFiveStarRateIfNeed(event.userId, clientId, timestamp, winDesc)
            return
        
        # 账号注册时间大于五天、游戏局数超过20局的玩家，连续获胜3局时
        if cls.calcRegisterDays(event.userId, timestamp) > 5:
            winrate, winstreak = gamedata.getGameAttrs(event.userId, DIZHU_GAMEID, ['winrate', 'winstreak'])
            winrate = strutil.loads(winrate, ignoreException=True, execptionValue={'pt':0, 'wt':0})
            try:
                winstreak = 0 if winstreak is None else int(winstreak)
            except:
                winstreak = 0
            if winrate.get('pt', 0) > 20 and winstreak == 3:
                hallfivestarrate.triggleFiveStarRateIfNeed(event.userId, clientId, timestamp, winDesc)

