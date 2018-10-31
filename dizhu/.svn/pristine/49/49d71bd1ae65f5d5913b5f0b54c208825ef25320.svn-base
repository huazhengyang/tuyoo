# -*- coding:utf-8 -*-
'''
Created on 2017年8月7日

@author: wangyonghui
'''
from dizhu.gametable import dizhu_quick_start
from freetime.util import log as ftlog
from poker.entity.configure import gdata, pokerconf
from poker.entity.dao import onlinedata
from poker.entity.game.rooms import TYRoomMixin
from poker.util import strutil

_DIZHU_CTRL_ROOM_IDS_LIST = []

# 进入房间返回的reason常量
ENTER_ROOM_REASON_UNKNOW = -1
ENTER_ROOM_REASON_OK = 0
ENTER_ROOM_REASON_CONFLICT = 1  # 玩家在玩牌时退出，然后重新开始另一个游戏，出现gameId冲突
ENTER_ROOM_REASON_INNER_ERROR = 2  # 服务器内部错误
ENTER_ROOM_REASON_ROOM_FULL = 3  # 房间已坐满
ENTER_ROOM_REASON_LESS_MIN = 4  # 玩家所持金币数 < 该房间准入最小金币数
ENTER_ROOM_REASON_GREATER_MAX = 5  # 玩家所持金币数 > 该房间准入最大金币数
ENTER_ROOM_REASON_GREATER_ALL = 6  # 玩家所持金币数 > 该类房间所有准入最大金币数
ENTER_ROOM_REASON_TABLE_FULL = 7  # 桌子已坐满
ENTER_ROOM_REASON_WRONG_TIME = 8  # 比赛时间未到
ENTER_ROOM_REASON_NOT_QUALIFIED = 9  # 没有资格进入此房间
ENTER_ROOM_REASON_ROOM_ID_ERROR = 10  # 客户端发送的roomId参数错误

ENTER_ROOM_REASON_VIP_LEVEL = 11  # 玩家的VIP级别不够
ENTER_ROOM_REASON_DASHIFEI_LEVEL = 12  # 玩家的大师分级别不够
ENTER_ROOM_REASON_NOT_OPEN = 13  # 房间/牌桌暂未开放
ENTER_ROOM_REASON_NEED_VALIDATE = 14  # 需要验证
ENTER_ROOM_REASON_NEED_ENERGY = 15  # 体力不足
ENTER_ROOM_REASON_LESS_MIN_QUICKSTART = 16  # 玩家所持金币 < 快速开始允许最小金币
ENTER_ROOM_REASON_QUIT_ROOM_ERROR = 17  # 玩家已在房间

ENTER_ROOM_REASON_TYPE_NORMAL = 1  # 非条件类
ENTER_ROOM_REASON_TYPE_CONDITION = 2  # 条件类


@classmethod
def onCmdQuickStart(cls, msg, userId, gameId, roomId, tableId, playMode, clientId):
    # 单开, 无论何时quick_start进入都检查loc
    if not pokerconf.isOpenMoreTable(clientId):
        loc = onlinedata.checkUserLoc(userId, clientId, gameId)
        if ftlog.is_debug():
            ftlog.debug('DizhuQuickStart old client, checkUserLoc->', loc, caller=cls)
        if isinstance(loc, basestring):
            lgameId, lroomId, ltableId, lseatId = loc.split('.')
            lgameId, lroomId, ltableId, lseatId = strutil.parseInts(lgameId, lroomId, ltableId, lseatId)
            if lgameId == gameId and lroomId > 0:
                if ftlog.is_debug():
                    ftlog.debug('DizhuQuickStart _quickStart re-connected |userId, loc:', userId, loc,
                                '|roomId, tableId:', roomId, tableId, caller=cls)
                roomId = lroomId
                tableId = ltableId
                msg.setParam('isReConnected', True)
                if ftlog.is_debug():
                    ftlog.debug('DizhuQuickStart old client, reset roomId, tableId->', roomId, tableId, caller=cls)
    # 带有roomId
    if roomId:
        cls._quickStart(msg, userId, gameId, roomId, tableId, playMode, clientId)
        return

    # 不带 roomId 服务器来选择房间
    ctrlRoomIds = cls._getQuickStartRoomList(userId, playMode, rankId=msg.getParam('rankId', '-1'))  # 快开列表
    chose_roomid, ok, mixId = cls._chooseRoom(userId, ctrlRoomIds, rankId=msg.getParam('rankId', '-1'))  # 选择一个
    if ok == ENTER_ROOM_REASON_OK:
        bigroomid = gdata.getBigRoomId(chose_roomid)
        ismatch = gdata.roomIdDefineMap()[chose_roomid].configure.get('ismatch', 0)
        if ftlog.is_debug():
            ftlog.debug("DizhuQuickStart._chooseRoom: userId=", userId, "roomId=", chose_roomid, 'mixId=', mixId)
        if ismatch:
            cls.notifyQuickGotoDizhuMatch(gameId, userId, bigroomid, mixId=mixId)
        else:
            msg.setParam('mixId', mixId)
            ctrRoomIds = gdata.bigRoomidsMap()[bigroomid]
            ctrlRoomId = ctrRoomIds[userId % len(ctrRoomIds)]
            TYRoomMixin.queryRoomQuickStartReq(msg, ctrlRoomId, 0)  # 请求发给 GR
    elif ok == ENTER_ROOM_REASON_QUIT_ROOM_ERROR:
        cls._sendTodoTaskToUser(userId, ok)
    elif (ok == ENTER_ROOM_REASON_LESS_MIN or ok == ENTER_ROOM_REASON_LESS_MIN_QUICKSTART) and msg.getParam('rankId', '-1') in ['0', '1']:
        cls._sendTodoTaskBuyChip(userId, chose_roomid, clientId, mixId)
    else:
        cls._sendTodoTaskJumpHighRoom(userId, playMode, clientId, rankId='-1')
    return

dizhu_quick_start.DizhuQuickStart.onCmdQuickStart = onCmdQuickStart
