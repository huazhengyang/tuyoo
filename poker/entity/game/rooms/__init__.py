# -*- coding: utf-8 -*-
"""

"""
import freetime.util.log as ftlog
from poker.entity.game.const import BaseConst
from poker.entity.game.rooms.arena_match_room import TYArenaMatchRoom
from poker.entity.game.rooms.big_match_room import TYBigMatchRoom
from poker.entity.game.rooms.custom_room import TYCustomRoom
from poker.entity.game.rooms.dtg_room import TYDTGRoom
from poker.entity.game.rooms.erdayi_match_room import TYErdayiMatchRoom
from poker.entity.game.rooms.group_match_room import TYGroupMatchRoom
from poker.entity.game.rooms.relaxation_match_room import TYRelaxationMatchRoom
from poker.entity.game.rooms.lts_room import TYLtsRoom
from poker.entity.game.rooms.mtt_room import TYMttRoom
from poker.entity.game.rooms.normal_room import TYNormalRoom
from poker.entity.game.rooms.queue_room import TYQueueRoom
from poker.entity.game.rooms.room_mixin import TYRoomMixin
from poker.entity.game.rooms.score_match_room import TYScoreMatchRoom
from poker.entity.game.rooms.sng_room import TYSngRoom
from poker.entity.game.rooms.vip_room import TYVipRoom
from poker.entity.game.rooms.hundreds_room import TYHundredsRoom
from poker.entity.game.rooms.chip_normal_room import TYChipNormalRoom
from poker.entity.game.rooms.pk_room import TYPkRoom
from poker.entity.game.rooms.quick_upgrade_match_room import TyQuickUpgradeMatchRoom
from poker.entity.game.rooms.queue_mixed_room import TYQueueMixedRoom
from poker.entity.game.rooms.common_arena_match_room import TyCommonArenaMatchRoom
from poker.entity.game.rooms.async_upgrade_hero_match import TyAsyncUpgradeHeroMatchRoom
from poker.entity.game.rooms.async_common_arena_match_room import TyAsyncCommonArenaMatchRoom
__author__ = ['"Zhouhao" <zhouhao@tuyoogame.com>']

class TYRoomConst(BaseConst, ):
    pass
tyRoomConst = TYRoomConst()
tyRoomConst.ROOM_TYPE_NAME_NORMAL = 'normal'
tyRoomConst.ROOM_TYPE_NAME_QUEUE = 'queue'
tyRoomConst.ROOM_TYPE_NAME_QUEUE_MIXED = 'queue_mixed_room'
tyRoomConst.ROOM_TYPE_NAME_VIP = 'vip'
tyRoomConst.ROOM_TYPE_NAME_LTS = 'lts'
tyRoomConst.ROOM_TYPE_NAME_SNG = 'sng'
tyRoomConst.ROOM_TYPE_NAME_MTT = 'mtt'
tyRoomConst.ROOM_TYPE_NAME_HUNDREDS = 'hundreds'
tyRoomConst.ROOM_TYPE_NAME_DTG = 'dtg'
tyRoomConst.ROOM_TYPE_NAME_CUSTOM = 'custom'
tyRoomConst.ROOM_TYPE_NAME_SCORE_MATCH = 'score_match'
tyRoomConst.ROOM_TYPE_NAME_BIG_MATCH = 'big_match'
tyRoomConst.ROOM_TYPE_NAME_ARENA_MATCH = 'arena_match'
tyRoomConst.ROOM_TYPE_NAME_GROUP_MATCH = 'group_match'
tyRoomConst.ROOM_TYPE_NAME_ERDAYI_MATCH = 'erdayi_match'
tyRoomConst.ROOM_TYPE_NAME_CHIP_NORMAL = 'chip_normal'
tyRoomConst.ROOM_TYPE_NAME_PK = 'pk'
tyRoomConst.ROOM_TYPE_NAME_QUICK_UPGRADE_MATCH = 'quick_upgrade_match'
tyRoomConst.ROOM_TYPE_NAME_COMMON_ARENA_MATCH = 'common_arena_match'
tyRoomConst.ROOM_TYPE_ASYNC_UPGRADE_HERO_MATCH = 'async_upgrade_hero_match'
tyRoomConst.ROOM_TYPE_NAME_ASYNC_COMMON_ARENA_MATCH = 'async_common_arena_match'
"""
休闲赛(一天内某个时间段，任意打N局, minN<=N<=maxN)，且遇到过的玩家当天本比赛内将不能再组局,
比赛过程中，每局胜利或者和局，会得到配置的积分N-(chip.base)
排名规则：可由自己游戏实现
"""
tyRoomConst.ROOM_TYPE_NAME_RELAXATION_MATCH = 'relaxation_match'
tyRoomConst.ROOM_CLASS_DICT = {tyRoomConst.ROOM_TYPE_NAME_NORMAL: TYNormalRoom, tyRoomConst.ROOM_TYPE_NAME_BIG_MATCH: TYBigMatchRoom, tyRoomConst.ROOM_TYPE_NAME_ARENA_MATCH: TYArenaMatchRoom, tyRoomConst.ROOM_TYPE_NAME_GROUP_MATCH: TYGroupMatchRoom, tyRoomConst.ROOM_TYPE_NAME_ERDAYI_MATCH: TYErdayiMatchRoom, tyRoomConst.ROOM_TYPE_NAME_RELAXATION_MATCH: TYRelaxationMatchRoom, tyRoomConst.ROOM_TYPE_NAME_VIP: TYVipRoom, tyRoomConst.ROOM_TYPE_NAME_QUEUE: TYQueueRoom, tyRoomConst.ROOM_TYPE_NAME_SNG: TYSngRoom, tyRoomConst.ROOM_TYPE_NAME_MTT: TYMttRoom, tyRoomConst.ROOM_TYPE_NAME_LTS: TYLtsRoom, tyRoomConst.ROOM_TYPE_NAME_HUNDREDS: TYHundredsRoom, tyRoomConst.ROOM_TYPE_NAME_DTG: TYDTGRoom, tyRoomConst.ROOM_TYPE_NAME_CUSTOM: TYCustomRoom, tyRoomConst.ROOM_TYPE_NAME_SCORE_MATCH: TYScoreMatchRoom, tyRoomConst.ROOM_TYPE_NAME_PK: TYPkRoom, tyRoomConst.ROOM_TYPE_NAME_CHIP_NORMAL: TYChipNormalRoom, tyRoomConst.ROOM_TYPE_NAME_QUICK_UPGRADE_MATCH: TyQuickUpgradeMatchRoom, tyRoomConst.ROOM_TYPE_NAME_QUEUE_MIXED: TYQueueMixedRoom, tyRoomConst.ROOM_TYPE_NAME_COMMON_ARENA_MATCH: TyCommonArenaMatchRoom, tyRoomConst.ROOM_TYPE_ASYNC_UPGRADE_HERO_MATCH: TyAsyncUpgradeHeroMatchRoom, tyRoomConst.ROOM_TYPE_NAME_ASYNC_COMMON_ARENA_MATCH: TyAsyncCommonArenaMatchRoom}

def getInstance(roomdefine):
    """
    Raise :
        KeyError : roomTypeName invalid
    """
    pass