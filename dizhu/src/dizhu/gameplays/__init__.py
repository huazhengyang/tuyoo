# coding=UTF-8
'''
'''
from dizhu.gamecards import cardcenter
from dizhu.entity import dizhuconf
from poker.entity.game.rooms import tyRoomConst

__author__ = [
    '"Zqh"',
    '"Zhouhao" <zhouhao@tuyoogame.com>',
]

from freetime.util import log as ftlog


def getInstance(table, playMode, roomTypeName=''):
    '''工场设计模式，根据playMode来创建不同类型的GamePlay对象'''
    ftlog.debug('getInstance->playMode=', playMode)
    if roomTypeName == tyRoomConst.ROOM_TYPE_ASYNC_UPGRADE_HERO_MATCH:
        from dizhu.gameplays.gameplay_million_hero import DizhuMillionHeroMatchPlay
        return DizhuMillionHeroMatchPlay(table)
    
    if playMode == dizhuconf.PLAYMODE_HAPPY :
        from dizhu.gameplays.gameplay_happy import DizhuHappyGamePlay
        return DizhuHappyGamePlay(table)
    
    if playMode == dizhuconf.PLAYMODE_LAIZI :
        from dizhu.gameplays.gameplay_laizi import DizhuLaiZiGamePlay
        return DizhuLaiZiGamePlay(table)
    
    if playMode == dizhuconf.PLAYMODE_ERDOU :
        from dizhu.gameplays.gameplay_erdou import DizhuErDouGamePlay
        return DizhuErDouGamePlay(table)
    
    if playMode == dizhuconf.PLAYMODE_123 :
        from dizhu.gameplays.gameplay_123 import Dizhu123GamePlay
        return Dizhu123GamePlay(table)
    
    if playMode == dizhuconf.PLAYMODE_ERDAYI:
        from dizhu.gameplays.gameplay_erdayi import DizhuErdayiGamePlay
        return DizhuErdayiGamePlay(table)
    
    if playMode == dizhuconf.PLAYMODE_EMPTY :
        return None
    
    raise Exception('play mode not defined !' + str(playMode))
