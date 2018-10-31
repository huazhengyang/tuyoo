# coding=UTF-8
'''
斗地主quickstart模块
'''

from datetime import datetime

from dizhu.entity import dizhuconf, dizhuhallinfo
from dizhu.entity.dizhuconf import DIZHU_GAMEID
from dizhu.entity.dizhuversion import SessionDizhuVersion
from dizhu.gametable.dizhu_quick_start import DizhuQuickStart
from dizhu.servers.util.rpc import new_table_remote
from dizhucomm.servers.util.rpc import comm_table_remote
from freetime.entity.msg import MsgPack
from freetime.util import log as ftlog
from hall.entity.hallusercond import UserConditionRegister
from poker.entity.configure import gdata
from poker.entity.dao import onlinedata, sessiondata
from poker.entity.dao import userchip
from poker.entity.game.rooms import TYRoomMixin
from poker.entity.game.rooms.room import TYRoom
from poker.protocol import router
from poker.util import strutil
from poker.util import timestamp as pktimestamp


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
def _canQuickEnterRoom(cls, userId, roomId, innerTable=0, mixId=''):
    try:
        clientId = sessiondata.getClientId(userId)
        ret = comm_table_remote.checkUserQuitLoc(DIZHU_GAMEID, userId, roomId, clientId)
        if ret == -1:
            return ENTER_ROOM_REASON_TYPE_NORMAL, ENTER_ROOM_REASON_INNER_ERROR
        elif ret == 1:
            return ENTER_ROOM_REASON_TYPE_NORMAL, ENTER_ROOM_REASON_QUIT_ROOM_ERROR
        else:
            pass

        chip = userchip.getChip(userId)
        if ftlog.is_debug():
            ftlog.debug(gdata.roomIdDefineMap()[roomId].configure)

        roomConfig = gdata.roomIdDefineMap()[roomId].configure
        if roomConfig.get('isMix', 0):
            mixConf = cls.getMixConf(roomConfig, mixId) or roomConfig.get('mixConf')[0]
            minCoin = cls.getMixConf(roomConfig, mixId).get('minCoin', 0)
            kickOutCoin = cls.getMixConf(roomConfig, mixId).get('kickOutCoin', 0)
            roomConfig = mixConf

        elif roomConfig.get('typeName') == 'dizhu_arena_match' and roomConfig.get('matchConf', {}).get('feeRewardList', []):
            mixConf = cls.getArenaMixConf(roomConfig, mixId) or roomConfig.get('matchConf', {}).get('feeRewardList', [])[0]
            mixConfDisplayCond = mixConf.get('displayCond', {})
            if mixConfDisplayCond:
                displayCond = UserConditionRegister.decodeFromDict(mixConfDisplayCond)
                ret = displayCond.check(DIZHU_GAMEID, userId, clientId, pktimestamp.getCurrentTimestamp())
                if not ret:
                    return ENTER_ROOM_REASON_TYPE_NORMAL, ENTER_ROOM_REASON_NOT_OPEN

            # 准入时间判断
            if not cls._checkOpenTime(mixConf, datetime.now().time()):
                return ENTER_ROOM_REASON_TYPE_NORMAL, ENTER_ROOM_REASON_NOT_OPEN
            minCoin = cls.getArenaMixConf(roomConfig, mixId).get('minCoin', 0)
            kickOutCoin = cls.getArenaMixConf(roomConfig, mixId).get('kickOutCoin', 0)
            minQuickStartChip = cls.getArenaMixConf(roomConfig, mixId).get('minQuickStartChip', 0)
            userChip = userchip.getChip(userId)
            if userChip < minQuickStartChip:
                return ENTER_ROOM_REASON_TYPE_NORMAL, ENTER_ROOM_REASON_LESS_MIN
        else:
            minCoin = roomConfig['minCoin']
            kickOutCoin = roomConfig.get('kickOutCoin', 0)

        if ftlog.is_debug():
            ftlog.debug('DizhuQuickStart._canEnterRoom roomId =', roomId, 'minCoin =', minCoin,
                        'chip =', chip, caller=cls)

        if innerTable == 0:
            if minCoin > 0 and chip < minCoin:
                return ENTER_ROOM_REASON_TYPE_NORMAL, ENTER_ROOM_REASON_LESS_MIN
        else:
            if kickOutCoin > 0 and chip < kickOutCoin:
                return ENTER_ROOM_REASON_TYPE_NORMAL, ENTER_ROOM_REASON_LESS_MIN

        # 房间开放判断
        if not dizhuhallinfo.canDisplayRoom(DIZHU_GAMEID, userId, clientId, roomId, roomConfig):
            if ftlog.is_debug():
                ftlog.debug('DizhuQuickStart._canEnterRoom NotCanDisplayRoom',
                            'gameId=', DIZHU_GAMEID,
                            'userId=', userId,
                            'clientId=', clientId,
                            'roomId=', roomId)
            return ENTER_ROOM_REASON_TYPE_NORMAL, ENTER_ROOM_REASON_NOT_OPEN

        # 准入时间判断
        if not cls._checkOpenTime(roomConfig, datetime.now().time()):
            return ENTER_ROOM_REASON_TYPE_NORMAL, ENTER_ROOM_REASON_NOT_OPEN

        # 其他条件判断，比如VIP， 大师分等
        result, msg = cls._validEnterRoomConditions(DIZHU_GAMEID, userId, clientId, roomId, roomConfig)
        if not result:
            return ENTER_ROOM_REASON_TYPE_CONDITION, msg
        return ENTER_ROOM_REASON_TYPE_NORMAL, ENTER_ROOM_REASON_OK
    except Exception as e:
        ftlog.error(e)
        return ENTER_ROOM_REASON_TYPE_NORMAL, ENTER_ROOM_REASON_INNER_ERROR

@classmethod
def _sendTodoTaskToUserWithRoomKey(cls, userId, roomId, msg, roomkey):
    if roomId <= 0:
        roomId = msg.getParam('roomId')
        if not roomId:
            return False
    roomconf = gdata.getRoomConfigure(roomId)
    if msg.getParam('mixId'):
        roomconf = cls.getMixConf(roomconf, msg.getParam('mixId'))

    if ftlog.is_debug():
        ftlog.debug("DizhuQuickStart._sendTodoTaskToUserWithRoomKey: roomId=", roomId, "userId=", userId, "roomconf=", roomconf)

    if not roomconf:
        return False
    tip = roomconf.get(roomkey)
    if not tip:
        return False
    cls._sendTodoTaskToUserWithTip(userId, tip)
    return True


@classmethod
def _quickStart(cls, msg, userId, gameId, roomId, tableId, playMode, clientId):
    '''UT server中处理来自客户端的quick_start请求
            Args:
                msg
                    cmd : quick_start
                    if roomId == 0:
                        表示快速开始，服务器为玩家选择房间，然后将请求转给GR

                    if roomId > 0 and tableId == 0 :
                        表示玩家选择了房间，将请求转给GR

                    if roomId > 0 and tableId == roomId * 10000 :
                        表示玩家在队列里断线重连，将请求转给GR

                    if roomId > 0 and tableId > 0:
                        if onlineSeatId > 0:
                            表示玩家在牌桌里断线重连，将请求转给GT
                        else:
                            表示玩家选择了桌子，将请求转给GR
            '''
    assert isinstance(userId, int) and userId > 0
    assert isinstance(roomId, int) and roomId >= 0
    assert isinstance(tableId, int) and tableId >= 0

    mixId = msg.getParam('mixId', '')
    _, version, _ = strutil.parseClientId(clientId)
    if ftlog.is_debug():
        ftlog.debug("DizhuQuickStart._quickStart: clientId=", clientId, "userId=", userId, "roomId=", roomId, "tableId=", tableId, "mixId=", mixId, "version=", version, "type:", type(version), "playMode=",playMode)

    if playMode == "match":
        playMode = dizhuconf.PLAYMODE_123

    if ftlog.is_debug():
        ftlog.debug("DizhuQuickStart << |clientId:", clientId,
                    "mixId:", mixId,
                    "|userId, roomId, tableId:", userId, roomId, tableId,
                    "|gameId, playMode:", gameId, playMode, caller=cls)


    bigRoomId = gdata.getBigRoomId(roomId)
    if ftlog.is_debug():
        ftlog.debug('DizhuQuickStart bigRoomId:', bigRoomId)
    if bigRoomId == 0:
        cls._onEnterRoomFailed(msg, ENTER_ROOM_REASON_ROOM_ID_ERROR, userId, clientId, roomId)
        return

    if strutil.getGameIdFromBigRoomId(bigRoomId) != gameId:
        cls._onEnterRoomFailed(msg, ENTER_ROOM_REASON_ROOM_ID_ERROR, userId, clientId, roomId)
        return

    if tableId == 0:  # 玩家只选择了房间
        if roomId != bigRoomId:
            ctrlRoomId = gdata.roomIdDefineMap()[roomId].parentId or roomId
            queryRoomId = roomId
        else:
            ctrRoomIds = gdata.bigRoomidsMap()[bigRoomId]
            ctrlRoomId = ctrRoomIds[userId % len(ctrRoomIds)]
            queryRoomId = ctrlRoomId

        buyin = msg.getParam("buyin", 0)  # 兼容 pc
        innerTable = msg.getParam("innerTable", 0)  # innerTable 区分不同版本弹窗

        if ftlog.is_debug():
            ftlog.debug('DizhuQuickStart._quickStart', 'buyin=', buyin, 'innerTable=', innerTable, 'mixId=', mixId)

        if buyin:
            innerTable = 1

        roomdef = gdata.roomIdDefineMap()[ctrlRoomId]
        roomConf = roomdef.configure

        # 免费场重起maxCoin配置
        maxCoin = roomConf.get('maxCoin', 0)
        userChip = userchip.getChip(userId)
        if maxCoin > 0 and userChip >= maxCoin and innerTable == 0:
            cls._onEnterRoomFailed(msg, ENTER_ROOM_REASON_GREATER_MAX, userId, clientId, roomId)
            return
        # 混房的话从大到小选择一个mixId
        if roomConf.get('isMix') and not mixId:
            _, _, mixId = cls._chooseRoom(userId, [ctrlRoomId])
            if mixId:
                msg.setParam('mixId', mixId)
            else:
                msg.setParam('mixId', roomConf.get('mixConf')[0].get('mixId'))
                if innerTable == 0:
                    cls._onEnterRoomFailed(msg, ENTER_ROOM_REASON_LESS_MIN, userId, clientId, roomId)
                else:
                    mixConf = cls.getMixConf(roomConf, roomConf.get('mixConf')[0].get('mixId'))
                    new_table_remote.processLoseRoundOver(DIZHU_GAMEID, userId, clientId, mixConf.get('roomId'),
                                                          minCoin=mixConf.get('minCoin'))
                return
        reasonType, reason = cls._canQuickEnterRoom(userId, ctrlRoomId, innerTable, mixId)
        if reason == ENTER_ROOM_REASON_OK:
            TYRoomMixin.queryRoomQuickStartReq(msg, queryRoomId, 0)  # 请求转给GR或GT
        else:
            if reasonType == ENTER_ROOM_REASON_TYPE_NORMAL:
                if reason == ENTER_ROOM_REASON_NOT_OPEN and innerTable == 1:
                    if ftlog.is_debug():
                        ftlog.debug('DizhuQuickStart._quickStart not open userId=', userId,
                                    'roomId=', ctrlRoomId,
                                    'msg=', msg,
                                    'playmode=', playMode)
                    # 直接踢出房间
                    mp = MsgPack()
                    mp.setCmd('room')
                    mp.setParam('action', 'leave')
                    mp.setParam('reason', TYRoom.LEAVE_ROOM_REASON_ACTIVE)
                    mp.setParam('gameId', gameId)
                    mp.setParam('roomId', roomId)
                    mp.setParam('userId', userId)
                    router.sendRoomServer(mp, roomId)
                    return

                if reason == ENTER_ROOM_REASON_LESS_MIN or reason == ENTER_ROOM_REASON_GREATER_MAX:
                    if innerTable == 1:
                        ctrRoomIds = gdata.bigRoomidsMap()[bigRoomId]
                        ctrlRoomId = ctrRoomIds[userId % len(ctrRoomIds)]
                        if roomdef.configure.get('isMix', 0):
                            continueLuckyGift = cls.getMixConf(roomdef.configure, mixId).get('continueLuckyGift', 0)
                            continueLuckyVer = cls.getMixConf(roomdef.configure, mixId).get('continueLuckyVer', 0)
                        else:
                            continueLuckyGift = roomdef.configure.get('continueLuckyGift', 0)
                            continueLuckyVer = roomdef.configure.get('continueLuckyVer', 0)
                        dizhuVersion = SessionDizhuVersion.getVersionNumber(userId)
                        if continueLuckyGift and dizhuVersion >= continueLuckyVer:
                            # 发送转运礼包
                            if ftlog.is_debug():
                                ftlog.debug('DizhuQuickStart._quickStart _less_min userId=', userId,
                                            'roomId=', ctrlRoomId,
                                            'msg=', msg,
                                            'playmode=', playMode,
                                            'continueLuckyGift=', continueLuckyGift,
                                            'continueLuckyVer=', continueLuckyVer,
                                            'dizhuVersion=', dizhuVersion)
                            if mixId and roomConf.get('isMix'):
                                mixConf = cls.getMixConf(roomConf, mixId)
                                new_table_remote.processLoseRoundOver(DIZHU_GAMEID, userId, clientId, mixConf.get('roomId'),
                                                                      minCoin=mixConf.get('minCoin'))
                            else:
                                new_table_remote.processLoseRoundOver(DIZHU_GAMEID, userId, clientId, roomId)
                        else:
                            roomDef = gdata.roomIdDefineMap()[ctrlRoomId]
                            playMode = roomDef.configure.get('playMode', None)
                            if ftlog.is_debug():
                                ftlog.debug('DizhuQuickStart._quickStart _less_min userId=', userId,
                                            'roomId=', ctrlRoomId,
                                            'msg=', msg,
                                            'playmode=', playMode)
                            msgpack = MsgPack()
                            msgpack.setCmd("quick_start")
                            msgpack.setParam("userId", userId)
                            msgpack.setParam("gameId", gameId)
                            msgpack.setParam("clientId", clientId)
                            msgpack.setParam("innerTable", 1)
                            msgpack.setParam("apiver", msg.getParam("apiver", 3.7))
                            cls.onCmdQuickStart(msgpack, userId, gameId, 0, 0, playMode, clientId)
                            if ftlog.is_debug():
                                ftlog.debug('DizhuQuickStart._quickStart reenter_less_min userId=', userId, 'roomId=', ctrlRoomId, 'msgpack=', msgpack.pack())
                    else:
                        cls._onEnterRoomFailed(msg, reason, userId, clientId, roomId)
                else:
                    cls._onEnterRoomFailed(msg, reason, userId, clientId, roomId)
            else:
                cls._sendTodoTaskToUserWithTip(userId, reason)
        return

    if tableId == roomId * 10000:  # 玩家在队列里断线重连
        TYRoomMixin.queryRoomQuickStartReq(msg, roomId, tableId)  # 请求转给GR
        return

    onlineSeat = onlinedata.getOnlineLocSeatId(userId, roomId, tableId)

    if onlineSeat:
        # 牌桌里坐着的玩家断线重连，请求转给GT
        # TYRoomMixin.querySitReq(userId, roomId, tableId, clientId) # GT人多时会有超时异常
        TYRoomMixin.sendSitReq(userId, roomId, tableId, clientId)
    else:  # 玩家选择了桌子,
        shadowRoomId = tableId / 10000
        ctrRoomId = gdata.roomIdDefineMap()[shadowRoomId].parentId
        TYRoomMixin.queryRoomQuickStartReq(msg, ctrRoomId, tableId, shadowRoomId=shadowRoomId)  # 请求转给GR
    return


DizhuQuickStart._canQuickEnterRoom = _canQuickEnterRoom
DizhuQuickStart._sendTodoTaskToUserWithRoomKey = _sendTodoTaskToUserWithRoomKey
DizhuQuickStart._quickStart = _quickStart
