# -*- coding: utf-8 -*-
import freetime.util.log as ftlog
from poker.entity.biz import bireport
from poker.entity.dao import daoconst, daobase, userdata, gamedata
from poker.servers.util.direct import dbuser
EVENT_NAME_SYSTEM_REPAIR = 'SYSTEM_REPAIR'

class ChipNotEnoughOpMode(object, ):

    def __call__(self, *args, **argd):
        pass

    def __init__(self):
        pass
ChipNotEnoughOpMode = ChipNotEnoughOpMode()

def getChip(uid):
    pass

def getCoin(uid):
    pass

def getDiamond(uid):
    pass

def getCoupon(uid):
    pass

def getUserChipAll(uid):
    """
    取得用户的所有金币, 包含被带入的金币
    """
    pass

def getTableChip(uid, gameid, tableId):
    """
    取得用户的table_chip
    返回:
        否则返回gamedata中的tablechip
    """
    pass

def getTableChipsAll(uid):
    """
    取得用户的table_chip
    返回:
        所有的tablechip
    """
    pass

def delTableChips(uid, tableIdList):
    """
    取得用户的table_chip
    返回:
        所有的tablechip
    """
    pass

def moveAllChipToTableChip(uid, gameid, eventId, intEventParam, clientId, tableId, extentId=0, roomId=0, roundId=0, param01=0, param02=0):
    """
    转移用户所有的chip至tablechip
    参考: set_tablechip_to_range
    """
    pass

def moveAllTableChipToChip(uid, gameid, eventId, intEventParam, clientId, tableId, extentId=0, roomId=0, roundId=0, param01=0, param02=0):
    """
    转移用户所有的tablechip至chip
    参考: set_tablechip_to_range
    """
    pass

def setTableChipToN(uid, gameid, tablechip, eventId, intEventParam, clientId, tableId, extentId=0, roomId=0, roundId=0, param01=0, param02=0):
    """
    设置用户的tablechip至传入的值
    参考: set_tablechip_to_range
    """
    pass

def setTableChipToBigThanN(uid, gameid, tablechip, eventId, intEventParam, clientId, tableId, extentId=0, roomId=0, roundId=0, param01=0, param02=0):
    """
    设置用户的tablechip大于等于传入的值
    参考: set_tablechip_to_range
    """
    pass

def setTableChipToNIfLittleThan(uid, gameid, tablechip, eventId, intEventParam, clientId, tableId, extentId=0, roomId=0, roundId=0, param01=0, param02=0):
    """
    如果用户的tablechip小于传入的值, 至那么设置tablechip至传入的值
    参考: set_tablechip_to_range
    """
    pass

def setTablechipNearToNIfLittleThan(uid, gameid, tablechip, eventId, intEventParam, clientId, tableId, extentId=0, roomId=0, roundId=0, param01=0, param02=0):
    """
    tablechip 小于 n 时, 让 tablechip 尽量接近 n
    参考: set_tablechip_to_range
    """
    pass

def setTableChipToRange(uid, gameid, _min, _max, eventId, intEventParam, clientId, tableId, extentId=0, roomId=0, roundId=0, param01=0, param02=0):
    """
    chip与tablechip转换
    使得tablechip在 [_min, _max] 范围内尽量大。
    _min, _max 正常取值范围：>= 0
    特殊取值，代表redis中的当前值：
        -1: chip+tablechip
        -2: tablechip
        -3: chip
    否则设置gamedata中的tablechip
    返回: (table_chip_final, user_chip_final, delta_chip)
        table_chip_final 最终的tablechip数量
        user_chip_final 最终的userchip数量
        delta_chip 操作变化的数量
    """
    pass

def _setTableChipToRange(uid, gameid, _min, _max, eventId, intEventParam, clientId, tableId, extentId=0, roomId=0, roundId=0, param01=0, param02=0):
    pass

def _incrUserChipFiled(uid, gameid, deltaCount, lowLimit, highLimit, chipNotEnoughOpMode, eventId, chipType, intEventParam, clientId, tableId=0, extentId=0, roomId=0, roundId=0, param01=0, param02=0):
    pass

def incrTableChip(uid, gameid, deltaCount, chipNotEnoughOpMode, eventId, intEventParam, clientId, tableId, extentId=0, roomId=0, roundId=0, param01=0, param02=0):
    """
    对用户的tablechip进行INCR操作
    否则设置gamedata中的tablechip
    参考: incr_chip
    """
    pass

def incrTableChipLimit(uid, gameid, deltaCount, lowLimit, highLimit, chipNotEnoughOpMode, eventId, intEventParam, clientId, tableId, extentId=0, roomId=0, roundId=0, param01=0, param02=0):
    """
    对用户的tablechip进行INCR操作
    否则设置gamedata中的tablechip
    参考: incr_chip_limit
    """
    pass

def incrChipLimit(uid, gameid, deltaCount, lowLimit, highLimit, chipNotEnoughOpMode, eventId, intEventParam, clientId, extentId=0, roomId=0, tableId=0, roundId=0, param01=0, param02=0):
    """
    对用户的金币进行INCR操作
    @param uid: userId
    @param gameid: 游戏ID
    @param deltaCount: 变化的值可以是负数
    @param lowLimit 用户最低金币数，-1表示没有最低限制
    @param highLimit 用户最高金币数，-1表示没有最高限制
    @param mode: 当INCR动作会变成负数时的处理模式, 0表示不进行操作; 1会给金币清零
    @param eventId: 触发INCR的事件ID
    @param argdict: 需要根据事件传入intEventParam
    @return (trueDelta, final) trueDelta表示实际变化的值, final表示变化后的最终数量

    地主收房间服务费示例
    地主每玩完一局需要收服务费, 对用户金币没有上下限，如果用户的金币不够服务费就收取用户所有金币, 所以mode=ChipNotEnoughOpMode.CLEAR_ZERO
    用户10001当前金币为100, 在地主601房间(服务费为500)玩了一局, 收服务费代码为
    trueDelta, final = UserProps.incr_chip_limit(10001, 6, -500, -1, -1,
                                                            ChipNotEnoughOpMode.CLEAR_ZERO,
                                                            BIEvent.ROOM_GAME_FEE, roomId=601)
    此时trueDelta=-100, final=0

    地主收报名费示例
    用户10001当前金币为100, 报名610房间的比赛(需要报名费1000金币), 对用户金币没有上下限, 报名费不足则不处理，所以mode=ChipNotEnoughOpMode.NOOP
    trueDelta, final = UserProps.incr_chip_limit(10001, 6, -1000, -1, -1,
                                                            ChipNotEnoughOpMode.NOOP,
                                                            BIEvent.MATCH_SIGNIN_FEE, roomId=610)
    if trueDelta == -1000:
        # 收取报名费成功进行报名操作
        pass
    else:
        # 报名费不足，给客户端返回错误
        pass

    有上下限的示例
    在地主601房间最低准入为1000金币，扔鸡蛋价格为10金币，用户10001的当前金币为1000, 此时的delta为10下限为1010, 没有上限
    trueDelta, final = UserProps.incr_chip_limit(10001, 6, -10, 1010, -1,
                                                            ChipNotEnoughOpMode.NOOP,
                                                            BIEvent.EMOTICON_EGG_CONSUME, roomId=610)
    if trueDelta == -10:
        # 收取扔鸡蛋金币成功
        pass
    else:
        # 扔鸡蛋金币不足，给客户端返回错误
        pass
    """
    pass

def incrChip(uid, gameid, deltaCount, chipNotEnoughOpMode, eventId, intEventParam, clientId, extentId=0, roomId=0, tableId=0, roundId=0, param01=0, param02=0):
    """
    对用户的金币进行INCR操作
    @param uid: userId
    @param gameid: 游戏ID
    @param deltaCount: 变化的值可以是负数
    @param chipNotEnoughOpMode: 当INCR动作会变成负数时的处理模式, 0表示不进行操作; 1会给金币清零
    @param eventId: 触发INCR的事件ID
    @param argdict: 需要根据事件传入intEventParam
    @return (trueDelta, final) trueDelta表示实际变化的值, final表示变化后的最终数量
    参考incr_chip_limit的调用，此方法相当于用lowLimit, highLimit都是-1去调用incr_chip_limit
    """
    pass

def incrCoin(uid, gameid, deltaCount, chipNotEnoughOpMode, eventId, intEventParam, clientId, extentId=0, roomId=0, tableId=0, roundId=0, param01=0, param02=0):
    """
    对用户的COIN进行INCR操作
    参考: incr_chip
    """
    pass

def incrDiamond(uid, gameid, deltaCount, chipNotEnoughOpMode, eventId, intEventParam, clientId, extentId=0, roomId=0, tableId=0, roundId=0, param01=0, param02=0):
    """
    对用户的钻石进行INCR操作
    参考: incr_chip
    """
    pass

def incrCoupon(uid, gameid, deltaCount, chipNotEnoughOpMode, eventId, intEventParam, clientId, extentId=0, roomId=0, tableId=0, roundId=0, param01=0, param02=0):
    """
    对用户的兑换券进行INCR操作
    参考: incr_chip
    """
    pass