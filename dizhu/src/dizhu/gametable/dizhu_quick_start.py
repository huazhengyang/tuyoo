# coding=UTF-8
'''
斗地主quickstart模块
'''

from datetime import datetime

from dizhu.entity import dizhuconf, dizhuonlinedata, dizhuhallinfo, dizhuuserdata, dizhuaccount
from dizhu.entity.dizhualert import Alert
from dizhu.entity.dizhuconf import DIZHU_GAMEID
from dizhu.entity.dizhuversion import SessionDizhuVersion
from dizhu.entity import dizhu_util
from dizhu.servers.util.rpc import new_table_remote
from dizhucomm.servers.util.rpc import comm_table_remote
from freetime.entity.msg import MsgPack
from freetime.util import log as ftlog
from hall.entity import hallproductselector, hallpopwnd, hallconf
from hall.entity.hallusercond import UserConditionRegister
from hall.entity.todotask import TodoTaskShowInfo, TodoTaskHelper, \
    TodoTaskPayOrder, TodoTaskQuickStart, TodoTaskDiZhuEvent
from poker.entity.configure import gdata, pokerconf
from poker.entity.dao import onlinedata, sessiondata
from poker.entity.dao import userchip
from poker.entity.game import game
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
ENTER_ROOM_REASON_GAME_SHUTDOWN_GO = 18  # 系统维护升级

ENTER_ROOM_REASON_TYPE_NORMAL = 1  # 非条件类
ENTER_ROOM_REASON_TYPE_CONDITION = 2  # 条件类


class DizhuQuickStart(object):
    '''
    根据用户chip进行快速开始
    '''
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

        if not tableId and game.isShutDown():
            cls._sendTodoTaskToUser(userId, ENTER_ROOM_REASON_GAME_SHUTDOWN_GO)
            return

        # 带有roomId
        if roomId:
            cls._quickStart(msg, userId, gameId, roomId, tableId, playMode, clientId)
            return

        # 不带 roomId 服务器来选择房间
        ctrlRoomIds, mixRoomReversed = cls._getQuickStartRoomList(userId, playMode, rankId=msg.getParam('rankId', '-1'))  # 快开列表
        chose_roomid, ok, mixId = cls._chooseRoom(userId, ctrlRoomIds, rankId=msg.getParam('rankId', '-1'), mixRoomReversed=mixRoomReversed)  # 选择一个
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
        elif ok == ENTER_ROOM_REASON_LESS_MIN_QUICKSTART:
            cls._sendTodoTaskBuyChip(userId, chose_roomid, clientId, mixId)
        else:
            cls._sendTodoTaskJumpHighRoom(userId, playMode, clientId, rankId='-1')
        return

    # --------------------------------------------------------------------------
    # 快速开始的核心逻辑
    # --------------------------------------------------------------------------
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
                from dizhu.entity import  dizhu_giftbag
                winSteakBuff, _ = dizhu_giftbag.checkUserGiftBuff(userId)
                if not winSteakBuff:
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
            if ftlog.is_debug():
                ftlog.debug('DizhuQuickStart._quickStart _canQuickEnterRoom userId=', userId,
                            'roomId=', ctrlRoomId,
                            'reasonType=', reasonType,
                            'reason=', reason)

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

                    # if reason == ENTER_ROOM_REASON_LESS_MIN or reason == ENTER_ROOM_REASON_GREATER_MAX:
                    #     if innerTable == 1:
                    #         ctrRoomIds = gdata.bigRoomidsMap()[bigRoomId]
                    #         ctrlRoomId = ctrRoomIds[userId % len(ctrRoomIds)]
                    #         if roomdef.configure.get('isMix', 0):
                    #             continueLuckyGift = cls.getMixConf(roomdef.configure, mixId).get('continueLuckyGift', 0)
                    #             continueLuckyVer = cls.getMixConf(roomdef.configure, mixId).get('continueLuckyVer', 0)
                    #         else:
                    #             continueLuckyGift = roomdef.configure.get('continueLuckyGift', 0)
                    #             continueLuckyVer = roomdef.configure.get('continueLuckyVer', 0)
                    #         dizhuVersion = SessionDizhuVersion.getVersionNumber(userId)
                    #         if continueLuckyGift and dizhuVersion >= continueLuckyVer:
                    #             # 发送转运礼包
                    #             if ftlog.is_debug():
                    #                 ftlog.debug('DizhuQuickStart._quickStart _less_min userId=', userId,
                    #                             'roomId=', ctrlRoomId,
                    #                             'msg=', msg,
                    #                             'playmode=', playMode,
                    #                             'continueLuckyGift=', continueLuckyGift,
                    #                             'continueLuckyVer=', continueLuckyVer,
                    #                             'dizhuVersion=', dizhuVersion)
                    #             if mixId and roomConf.get('isMix'):
                    #                 mixConf = cls.getMixConf(roomConf, mixId)
                    #                 new_table_remote.processLoseRoundOver(DIZHU_GAMEID, userId, clientId, mixConf.get('roomId'),
                    #                                                       minCoin=mixConf.get('minCoin'))
                    #             else:
                    #                 new_table_remote.processLoseRoundOver(DIZHU_GAMEID, userId, clientId, roomId)
                    #         else:
                    #             roomDef = gdata.roomIdDefineMap()[ctrlRoomId]
                    #             playMode = roomDef.configure.get('playMode', None)
                    #             if ftlog.is_debug():
                    #                 ftlog.debug('DizhuQuickStart._quickStart _less_min userId=', userId,
                    #                             'roomId=', ctrlRoomId,
                    #                             'msg=', msg,
                    #                             'playmode=', playMode)
                    #             msgpack = MsgPack()
                    #             msgpack.setCmd("quick_start")
                    #             msgpack.setParam("userId", userId)
                    #             msgpack.setParam("gameId", gameId)
                    #             msgpack.setParam("clientId", clientId)
                    #             msgpack.setParam("innerTable", 1)
                    #             msgpack.setParam("apiver", msg.getParam("apiver", 3.7))
                    #             cls.onCmdQuickStart(msgpack, userId, gameId, 0, 0, playMode, clientId)
                    #             if ftlog.is_debug():
                    #                 ftlog.debug('DizhuQuickStart._quickStart reenter_less_min userId=', userId, 'roomId=', ctrlRoomId, 'msgpack=', msgpack.pack())
                    #     else:
                    #         cls._onEnterRoomFailed(msg, reason, userId, clientId, roomId)
                    # else:
                    cls._onEnterRoomFailed(msg, reason, userId, clientId, roomId)
                else:
                    cls._sendTodoTaskToUserWithTip(userId, reason)
            return

        if tableId == roomId * 10000:  # 玩家在队列里断线重连
            TYRoomMixin.queryRoomQuickStartReq(msg, roomId, tableId)  # 请求转给GR
            return

        onlineSeat = onlinedata.getOnlineLocSeatId(userId, roomId, tableId)
        
        if cls.isAsyncUpgradeHeroMatch(roomId):
            # 异步升级赛断线重连从GR开始
            shadowRoomId = tableId / 10000
            ctrRoomId = gdata.roomIdDefineMap()[shadowRoomId].parentId
            TYRoomMixin.queryRoomQuickStartReq(msg, ctrRoomId, tableId, shadowRoomId=shadowRoomId)
        elif onlineSeat:
            # 牌桌里坐着的玩家断线重连，请求转给GT
            # TYRoomMixin.querySitReq(userId, roomId, tableId, clientId) # GT人多时会有超时异常
            TYRoomMixin.sendSitReq(userId, roomId, tableId, clientId)
        else:  # 玩家选择了桌子,
            shadowRoomId = tableId / 10000
            ctrRoomId = gdata.roomIdDefineMap()[shadowRoomId].parentId
            TYRoomMixin.queryRoomQuickStartReq(msg, ctrRoomId, tableId, shadowRoomId=shadowRoomId)  # 请求转给GR
        return

    # --------------------------------------------------------------------------
    # 检查用户所在位置
    # --------------------------------------------------------------------------
    @classmethod
    def checkUserLoc(cls, userId, gameId, roomId, tableId, clientId):
        locList = dizhuonlinedata.getOnlineLocListByGameId(userId, gameId, clientId)
        if ftlog.is_debug():
            ftlog.debug('DizhuQuickStart.checkUserLoc userId=', userId,
                        'gameId=', gameId,
                        'roomId=', roomId,
                        'tableId=', tableId,
                        'clientId=', clientId,
                        'locList=', locList)
        if not locList:
            return True, None

        loc = locList[0]

        if roomId <= 0:
            return False, loc

        if cls.isMatchRoom(loc[1]):  # 比赛场只要是同一个bigRoomId就可以
            if cls.isSameBigRoom(loc[1], roomId):
                return True, None
            return False, loc

        if roomId == loc[1]:  # 金币场roomId必须相同
            return True, loc

        return False, loc

    @classmethod
    def isMatchRoom(cls, roomId):
        roomConf = gdata.getRoomConfigure(roomId)
        return roomConf.get('typeName') in ('group_match', 'arena_match')
    
    @classmethod
    def isAsyncUpgradeHeroMatch(cls, roomId):
        '''
        是否是异步升级赛
        '''
        roomConf = gdata.getRoomConfigure(roomId)
        return (roomConf.get('typeName', '') == 'async_upgrade_hero_match')

    @classmethod
    def isSameBigRoom(cls, roomId1, roomId2):
        return strutil.getBigRoomIdFromInstanceRoomId(roomId1) == strutil.getBigRoomIdFromInstanceRoomId(roomId2)

    @classmethod
    def _checkOpenTime(cls, roomConfig, nowTime):
        openTimeList = roomConfig.get('openTimeList')
        if not openTimeList:
            return True
        timeZeroStr = '00:00:00'
        for timeRange in openTimeList:
            try:
                beginTime = datetime.strptime(timeRange.get('begin', timeZeroStr), '%H:%M:%S').time()
                endTime = datetime.strptime(timeRange.get('end', timeZeroStr), '%H:%M:%S').time()
                if beginTime == endTime:
                    return True
                elif beginTime < endTime:
                    if nowTime >= beginTime and nowTime < endTime:
                        return True
                else:
                    if nowTime >= beginTime or nowTime < endTime:
                        return True
            except:
                ftlog.error('DizhuQuickStart._checkOpenTime',
                            'openTimeList=', openTimeList,
                            'timeRange=', timeRange)
        return False


    # --------------------------------------------------------------------------
    #  获取快开房间列表
    # --------------------------------------------------------------------------
    @classmethod
    def _getQuickStartRoomList(cls, userId, playMode, **kwargs):
        # 判断userChip
        quickStartConf = dizhuconf.getQuickStart()
        userChip = userchip.getChip(userId)
        pt = dizhuaccount.getUserGamePlayTimes(userId)
        ptConf = dizhuconf.getPublicConf('newer_quick_start_play_times', 0)
        if (playMode == dizhuconf.PLAYMODE_DEFAULT or playMode == dizhuconf.PLAYMODE_123) and pt <= ptConf:
            newerStartRooms = quickStartConf.get('newerStartRooms', [])
            if newerStartRooms:
                return [bigRoomId * 10000 + 1000 for bigRoomId in newerStartRooms], 0
        isMatch = 0
        # 比赛快开
        if playMode == dizhuconf.PLAYMODE_STRAIGHT_MATCH:
            matchStartChip = quickStartConf.get('matchStartChip', 0)
            isMatch = 1
            if userChip < matchStartChip:
                startRooms = quickStartConf.get('matchStartRooms', [])
                if startRooms:
                    return [bigRoomId * 10000 + 1000 for bigRoomId in startRooms], 1
        # 大厅快开
        elif playMode == dizhuconf.PLAYMODE_DEFAULT:
            # 新手大厅快开必须进入配置指定的房间
            bigRoomIds = cls._getNewComerBigRoomIds(userId)
            if bigRoomIds:
                try:
                    sessionRoomIds = cls.getMatchSessionRoomIds(userId)
                    if not sessionRoomIds:  # 提审用
                        return [bigRoomIds[-1] * 10000 + 1000], 1
                except Exception, e:
                    ftlog.error('DizhuQuickStart._getQuickStartRoomList',
                                'userId=', userId,
                                'playMode=', playMode,
                                'kwargs=', kwargs,
                                'bigRoomIds=', bigRoomIds,
                                'err=', e.message)
                return [bigRoomId * 10000 + 1000 for bigRoomId in bigRoomIds], 1
            hallStartChip = quickStartConf.get('hallStartChip', 0)
            if hallStartChip and userChip >= hallStartChip:
                playMode = dizhuconf.PLAYMODE_123
            else:
                startRooms = quickStartConf.get('hallStartRooms', [])
                if startRooms:
                    try:
                        sessionRoomIds = cls.getMatchSessionRoomIds(userId)
                        if not sessionRoomIds:  # 提审用
                            return [startRooms[-1] * 10000 + 1000], 1
                    except Exception, e:
                        ftlog.error('DizhuQuickStart._getQuickStartRoomList',
                                    'userId=', userId,
                                    'playMode=', playMode,
                                    'kwargs=', kwargs,
                                    'startRooms=', startRooms,
                                    'err=', e.message)
                    return [bigRoomId * 10000 + 1000 for bigRoomId in startRooms], 1

        ctrlroomid_quickstartchip_list = []

        global _DIZHU_CTRL_ROOM_IDS_LIST
        if not _DIZHU_CTRL_ROOM_IDS_LIST:
            # 生成的控制房间的房间id列表，ctrlroomid = bigRoomId * 10000 + 1000
            _DIZHU_CTRL_ROOM_IDS_LIST = [bigRoomId * 10000 + 1000 for bigRoomId in gdata.gameIdBigRoomidsMap().get(DIZHU_GAMEID, [])]

        rankId = kwargs.get('rankId', '-1')
        for ctrlroomid in _DIZHU_CTRL_ROOM_IDS_LIST:
            roomdef = gdata.roomIdDefineMap()[ctrlroomid]
            ismatch = roomdef.configure.get('ismatch', 0)

            if roomdef.configure.get('segment') == 1:
                continue

            if ismatch != isMatch:
                continue

            # 过滤玩法
            playmode = roomdef.configure.get('playMode', '')
            if not ismatch and playmode != playMode:
                if playMode == dizhuconf.PLAYMODE_LAIZI and playmode == dizhuconf.PLAYMODE_QUICKLAIZI:
                    pass
                else:
                    continue

            # 过滤积分榜
            scoreboardFlag = roomdef.configure.get('scoreboardFlag', '-1')

            if rankId == '1':
                if ismatch or scoreboardFlag != '1':
                    continue
                # 只选择允许快开的房间
                if roomdef.configure.get('isMix'):
                    minQuickStartChip = roomdef.configure.get('mixConf')[0].get('minCoin', -1)
                else:
                    minQuickStartChip = roomdef.configure.get('minCoin', -1)
                if minQuickStartChip == -1:
                    continue
                ctrlroomid_quickstartchip_list.append([ctrlroomid, minQuickStartChip])
            elif rankId == '0':
                if ismatch or scoreboardFlag != '0':
                    continue
                # 只选择允许快开的房间
                if roomdef.configure.get('isMix'):
                    minQuickStartChip = roomdef.configure.get('mixConf')[0].get('minCoin', -1)
                else:
                    minQuickStartChip = roomdef.configure.get('minCoin', -1)
                if minQuickStartChip == -1:
                    continue
                ctrlroomid_quickstartchip_list.append([ctrlroomid, minQuickStartChip])
            else:
                if roomdef.configure.get('isMix'):
                    startChip = roomdef.configure.get('mixConf')[0].get('minQuickStartChip', 0)
                    minQuickStartChip = roomdef.configure.get('mixConf')[0].get('minQuickStartChip', -1)
                elif ismatch and roomdef.configure.get('typeName') == 'dizhu_arena_match' and roomdef.configure.get('matchConf', {}).get('feeRewardList', []):
                    startChip = roomdef.configure.get('matchConf', {}).get('feeRewardList', [])[0].get('minQuickStartChip', 0)
                    minQuickStartChip = roomdef.configure.get('matchConf', {}).get('feeRewardList', [])[0].get('minQuickStartChip', -1)
                else:
                    startChip = roomdef.configure.get('minQuickStartChip', 0)
                    minQuickStartChip = roomdef.configure.get('minQuickStartChip', -1)

                if userchip.getChip(userId) < startChip:
                    continue
                if minQuickStartChip == -1:
                    continue
                ctrlroomid_quickstartchip_list.append([ctrlroomid, minQuickStartChip])

        ctrlroomid_quickstartchip_list.sort(key=lambda x: x[1] * -1)
        ctrlRoomIds = []
        for ctrlRoom in ctrlroomid_quickstartchip_list:
            ctrlRoomIds.append(ctrlRoom[0])

        if ftlog.is_debug():
            ftlog.debug("DizhuQuickStart <<|selected candidateRoomIds:", ctrlRoomIds, 'playMode=', playMode, caller=cls)
        return ctrlRoomIds, 1

    @classmethod
    def _getNewComerBigRoomIds(cls, userId):
        """
        获取大厅快开新手进入的房间列表
        新手的定义：打牌局数小于指定的数值
        """
        newGuideConf = dizhuconf.getQuickStart().get('newguide', {})
        plays = dizhuuserdata.getUserPlayCount(userId).get('total')
        if plays < newGuideConf.get('rounds.limit', 0):
            # 新手大厅快开必须进入指定的房间
            roomIdProbList = newGuideConf.get('roomid.problist', [])
            pickedItem = dizhu_util.getItemByWeight(roomIdProbList)
            if ftlog.is_debug():
                ftlog.debug('_getNewComerBigRoomIds',
                            'plays=', plays,
                            'conf=', newGuideConf,
                            'pickedItem=', pickedItem,
                            'plays=', plays,
                            'round.limit=', newGuideConf.get('rounds.limit'),
                            caller=cls)
            return pickedItem.get('roomids', [])
        return []

    # --------------------------------------------------------------------------
    # 检查用户是否可以进入房间
    # --------------------------------------------------------------------------
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
    def _validEnterRoomConditions(cls, gameId, userId, clientId, roomId, roomConfig):
        enterRoomCondList = roomConfig.get('enterRoomCond')
        if enterRoomCondList:
            try:
                for enterCond in enterRoomCondList:
                    cond = enterCond['cond']
                    msg = enterCond['msg']
                    result = UserConditionRegister.decodeFromDict(cond).check(gameId, userId, clientId, pktimestamp.getCurrentTimestamp())
                    if not result:
                        if ftlog.is_debug():
                            ftlog.debug('DizhuQuickStart._validEnterRoomConditions',
                                        'gameId=', gameId,
                                        'userId=', userId,
                                        'clientId=', clientId,
                                        'roomId=', roomId,
                                        'enterRoomCond=', enterRoomCondList,
                                        'ret=', msg)
                        return result, msg
                return True, 'ok'
            except:
                ftlog.error('DizhuQuickStart._validEnterRoomConditions',
                            'gameId=', gameId,
                            'userId=', userId,
                            'clientId=', clientId,
                            'roomId=', roomId,
                            'enterRoomCond=', enterRoomCondList)
                return False, 'error'
        return True, 0


    # --------------------------------------------------------------------------
    # 服务端为玩家选择房间
    # --------------------------------------------------------------------------
    @classmethod
    def _chooseRoom(cls, userId, startRooms, **kwargs):
        inRoom = False
        reasonType = None
        reason = None
        mixId = ''
        lastCtrRoomId = 0
        mixRoomReversed = kwargs.get('mixRoomReversed', 1)
        userChip = userchip.getChip(userId)
        for ctrRoomId in startRooms:
            lastCtrRoomId = ctrRoomId
            roomConfig = gdata.roomIdDefineMap()[ctrRoomId].configure

            if roomConfig.get('segment') == 1:
                continue

            if not mixRoomReversed:
                maxCoin = roomConfig.get('maxCoin', -1)
                if maxCoin > 0 and userChip >= maxCoin:
                    continue

            if roomConfig.get('isMix', 0):
                mixrooms = reversed(roomConfig.get('mixConf', [])) if mixRoomReversed else roomConfig.get('mixConf', [])
                for mixConf in mixrooms:
                    mixId = mixConf.get('mixId')
                    # 兼容积分榜
                    if kwargs.get('rankId', '-1') == '0':
                        minQuickStartChip = mixConf.get('minCoin', -1)
                    else:
                        minQuickStartChip = mixConf.get('minQuickStartChip', -1)
                    if userChip < minQuickStartChip:
                        continue
                    reasonType, reason = cls._canQuickEnterRoom(userId, ctrRoomId, mixId=mixConf.get('mixId'))
                    if reason == ENTER_ROOM_REASON_OK:
                        return ctrRoomId, ENTER_ROOM_REASON_OK, mixId
            elif roomConfig.get('typeName') == 'dizhu_arena_match' and roomConfig.get('matchConf', {}).get('feeRewardList', []):
                for i in reversed(roomConfig.get('matchConf', {}).get('feeRewardList', [])):
                    reasonType, reason = cls._canQuickEnterRoom(userId, ctrRoomId, mixId=i.get('mixId'))
                    if reason == ENTER_ROOM_REASON_OK:
                        mixId = i.get('mixId')
                        return ctrRoomId, ENTER_ROOM_REASON_OK, mixId
                    else:
                        mixId = ''
            else:
                if kwargs.get('rankId', '-1') == '1':
                    maxCoin = roomConfig.get('maxCoin', -1)
                    if maxCoin > 0 and userChip >= maxCoin:
                        return 0, ENTER_ROOM_REASON_GREATER_MAX, mixId
                reasonType, reason = cls._canQuickEnterRoom(userId, ctrRoomId)
            if ftlog.is_debug():
                ftlog.debug("|roomId, ret:", ctrRoomId, (reasonType, reason), caller=cls)
            if reason == ENTER_ROOM_REASON_OK:
                return ctrRoomId, ENTER_ROOM_REASON_OK, mixId
            # 中途退出在房间内
            if reason == ENTER_ROOM_REASON_QUIT_ROOM_ERROR:
                inRoom = True
        # 大积分排行榜
        if kwargs.get('rankId', '-1') in ['0', '1']:
            return lastCtrRoomId, ENTER_ROOM_REASON_LESS_MIN, mixId
        return lastCtrRoomId, ENTER_ROOM_REASON_QUIT_ROOM_ERROR if inRoom else ENTER_ROOM_REASON_LESS_MIN_QUICKSTART, mixId

    # --------------------------------------------------------------------------
    # 进入房间失败进行的后续处理
    # --------------------------------------------------------------------------
    @classmethod
    def _onEnterRoomFailed(cls, msg, checkResult, userId, clientId, roomId=0):
        # PC的补丁，需要返回一个失败的quick_start消息
        mixId = msg.getParam('mixId')
        # mo = MsgPack()
        # mo.setCmd('quick_start')
        # mo.setResult('gameId', DIZHU_GAMEID)
        # mo.setResult('userId', userId)
        # mo.setResult('roomId', 0)
        # mo.setResult('seatId', 0)
        # mo.setResult('tableId', 0)
        # router.sendToUser(mo, userId)

        if checkResult == ENTER_ROOM_REASON_CONFLICT:
            cls._sendTodoTaskToUser(userId, checkResult)

        elif checkResult == ENTER_ROOM_REASON_INNER_ERROR:
            cls._sendTodoTaskToUser(userId, checkResult)

        elif checkResult == ENTER_ROOM_REASON_QUIT_ROOM_ERROR:
            cls._sendTodoTaskToUser(userId, checkResult)

        elif checkResult == ENTER_ROOM_REASON_ROOM_FULL:
            cls._sendTodoTaskToUser(userId, checkResult)

        elif checkResult == ENTER_ROOM_REASON_LESS_MIN:
            innerTable = msg.getParam("innerTable", 0)
            if ftlog.is_debug():
                ftlog.debug('DizhuQuickStart enter_less_min msg=', msg, 'innerTable=', innerTable)
            if innerTable == 1:
                return cls._sendToDoTaskJumpToStore(userId)

            if roomId <= 0:
                roomId = msg.getParam('roomId')
                if not roomId:
                    roomId = msg.getParam('candidateRoomId')
                if not roomId:
                    return
            cls._sendTodoTaskBuyChip(userId, roomId, clientId, mixId)
            # cls._sendChargeLeadTodoTask(userId, roomId, clientId)

        elif checkResult == ENTER_ROOM_REASON_GREATER_MAX:
            playMode = msg.getParam('playMode')
            if not playMode:
                # 找到当前要进入的房间的玩法
                if roomId <= 0:
                    roomId = msg.getParam('roomId')
                    if not roomId:
                        roomId = msg.getParam('candidateRoomId')
                if roomId > 0:
                    if roomId in gdata.roomIdDefineMap():
                        playMode = gdata.roomIdDefineMap()[roomId].configure.get('playMode', None)
                    elif roomId in gdata.bigRoomidsMap():
                        roomId = gdata.bigRoomidsMap()[roomId][0]
                        playMode = gdata.roomIdDefineMap()[roomId].configure.get('playMode', None)

            cls._sendTodoTaskJumpHighRoom(userId, playMode, clientId)

        elif checkResult == ENTER_ROOM_REASON_GREATER_ALL:
            cls._sendTodoTaskToUser(userId, checkResult)

        elif checkResult == ENTER_ROOM_REASON_TABLE_FULL:
            cls._sendTodoTaskToUser(userId, checkResult)

        elif checkResult == ENTER_ROOM_REASON_WRONG_TIME:
            cls._sendTodoTaskToUser(userId, checkResult)

        elif checkResult == ENTER_ROOM_REASON_NOT_QUALIFIED:
            cls._sendTodoTaskToUser(userId, checkResult)

        elif checkResult == ENTER_ROOM_REASON_ROOM_ID_ERROR:
            cls._sendTodoTaskToUser(userId, checkResult)

        elif checkResult == ENTER_ROOM_REASON_DASHIFEI_LEVEL:
            if cls._sendTodoTaskToUserWithRoomKey(userId, roomId, msg, "vipOrDashifenTip"):
                return
            cls._sendTodoTaskToUser(userId, checkResult)

        elif checkResult == ENTER_ROOM_REASON_NOT_OPEN:
            if cls._sendTodoTaskToUserWithRoomKey(userId, roomId, msg, "openTimeListTip"):
                return
            cls._sendTodoTaskToUser(userId, checkResult)

        elif checkResult == ENTER_ROOM_REASON_VIP_LEVEL:
            if cls._sendTodoTaskToUserWithRoomKey(userId, roomId, msg, "vipOrDashifenTip"):
                return
            cls._sendTodoTaskToUser(userId, checkResult)
        elif checkResult == ENTER_ROOM_REASON_LESS_MIN_QUICKSTART:
            cls._sendTodoTaskBuyChip(userId, roomId, clientId, mixId)
        else:  # TYRoom.ENTER_ROOM_REASON_INNER_ERROR :
            cls._sendTodoTaskToUser(userId, ENTER_ROOM_REASON_INNER_ERROR)

    @classmethod
    def _useSelfPopWnd(cls, userId):
        dizhuVersion = SessionDizhuVersion.getVersionNumber(userId)
        return dizhuVersion >= 3.812

    @classmethod
    def _sendTodoTaskToUser(cls, userId, errorCode):
        tip = dizhuconf.getQuickStartErrorMsg(errorCode)
        t = TodoTaskShowInfo(tip, True)
        try:
            if ftlog.is_debug():
                ftlog.debug('DizhuQuickStart test ddz pop TodoTaskShowInfo come in userId = ', userId)
            if cls._useSelfPopWnd(userId):
                Alert.sendNormalAlert(DIZHU_GAMEID, userId, '提示', tip, None, '确定')
                return
        except:
            ftlog.error('DizhuQuickStart _sendTodoTaskToUser userId=', userId,
                        'tip=', tip)
        msg = TodoTaskHelper.makeTodoTaskMsg(DIZHU_GAMEID, userId, t)
        router.sendToUser(msg, userId)

    @classmethod
    def _sendTodoTaskToUserWithTip(cls, userId, tip):
        t = TodoTaskShowInfo(tip, True)
        try:
            if cls._useSelfPopWnd(userId):
                Alert.sendNormalAlert(DIZHU_GAMEID, userId, '提示', tip, None, '确定')
                return
        except:
            ftlog.error('DizhuQuickStart _sendTodoTaskToUserWithTip userId = ', userId,
                        'tip = ', tip)
        msg = TodoTaskHelper.makeTodoTaskMsg(DIZHU_GAMEID, userId, t)
        router.sendToUser(msg, userId)

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
    def _sendTodoTaskBuyChip(cls, userId, roomId, clientId, mixId):
        if ftlog.is_debug():
            ftlog.debug('DizhuQuickStart._sendTodoTaskBuyChip',
                        'userId=', userId,
                        'roomId=', roomId,
                        'clientId=', clientId,
                        'mixId=', mixId)
        bigRoomId = gdata.getBigRoomId(roomId)
        ctrRoomId = bigRoomId * 10000 + 1000
        roomConfig = gdata.roomIdDefineMap()[ctrRoomId].configure
        mixConfRoomId = cls.getMixConf(roomConfig, mixId).get('roomId', 0)
        if roomConfig.get('isMix', 0) and mixConfRoomId:
            roomId = mixConfRoomId
        todotask = hallpopwnd.makeTodoTaskLessbuyChip(DIZHU_GAMEID, userId, clientId, roomId, minCoin=cls.getMixConf(roomConfig, mixId).get('minCoin', None))
        if todotask:
            TodoTaskHelper.sendTodoTask(DIZHU_GAMEID, userId, todotask)

    @classmethod
    def _sendChargeLeadTodoTask(cls, userId, roomId, clientId, mixId):
        bigRoomId = gdata.getBigRoomId(roomId)
        ctrRoomId = bigRoomId * 10000 + 1000
        roomConfig = gdata.roomIdDefineMap()[ctrRoomId].configure
        mixConfRoomId = cls.getMixConf(roomConfig, mixId).get('roomId', 0)
        if roomConfig.get('isMix', 0) and mixConfRoomId:
            roomId = mixConfRoomId
        product, _ = hallproductselector.selectLessbuyProduct(DIZHU_GAMEID, userId, clientId, roomId)
        t = TodoTaskPayOrder(product)
        msg = TodoTaskHelper.makeTodoTaskMsg(DIZHU_GAMEID, userId, t)
        router.sendToUser(msg, userId)

    @classmethod
    def _sendTodoTaskJumpHighRoom(cls, userId, playMode, clientId, **kwargs):
        if not playMode in dizhuconf.PLAYMODE_ALLSET:
            playMode = dizhuconf.PLAYMODE_DEFAULT
        ctrlRoomIds, _ = cls._getQuickStartRoomList(userId, playMode, rankId=kwargs.get('rankId', '-1'))  # 快开列表
        chosenRoomId, reason, mixId = cls._chooseRoom(userId, ctrlRoomIds, rankId=kwargs.get('rankId', '-1'))
        if chosenRoomId and reason == ENTER_ROOM_REASON_OK:
            quick_start_ = TodoTaskQuickStart(DIZHU_GAMEID, chosenRoomId)
            quick_start_.setParam('mixId', mixId)
            info_str_ = dizhuconf.getQuickStartErrorMsg(ENTER_ROOM_REASON_GREATER_MAX)
            show_info_ = TodoTaskShowInfo(info_str_, True)
            show_info_.setSubCmd(quick_start_)
            try:
                if cls._useSelfPopWnd(userId):
                    todoTaskObj = TodoTaskHelper.encodeTodoTasks(quick_start_)
                    Alert.sendNormalAlert2Button(DIZHU_GAMEID, userId, '提示', info_str_, todoTaskObj[0], '确定', None, '取消')
                    return
            except:
                ftlog.error('DizhuQuickStart _sendTodoTaskJumpHighRoom error userId = ', userId,
                            ' clientId = ', clientId,
                            'playMode = ', playMode)
            msg = TodoTaskHelper.makeTodoTaskMsg(DIZHU_GAMEID, userId, show_info_)
            router.sendToUser(msg, userId)
        else:
            cls._sendTodoTaskToUser(userId, ENTER_ROOM_REASON_GREATER_ALL)

    @classmethod
    def _sendToDoTaskJumpToStore(cls, userId):
        if not cls._useSelfPopWnd(userId):
            win = hallpopwnd.makeTodotaskJumpToStoreOrHall("您的金币不足，请购买金币或参加免费比赛~")
            msg = TodoTaskHelper.makeTodoTaskMsg(DIZHU_GAMEID, userId, win)
            router.sendToUser(msg, userId)
            return

        message = "您的金币不足，请购买金币或参加免费比赛~"
        confirmTodotask = TodoTaskDiZhuEvent('dizhu_goto_store')
        cancelTodotask = TodoTaskDiZhuEvent('dizhu_back_hall')
        if ftlog.is_debug():
            ftlog.debug('DizhuQuickStart _sendToDoTaskJumpToStore',
                        'userId=', userId,
                        'confirmTodotask=', confirmTodotask,
                        'cancelTodotask=', cancelTodotask.toDict())
        Alert.sendNormalAlert2Button(DIZHU_GAMEID, userId, '提示', message,
                                     confirmTodotask.toDict(), '确定',
                                     cancelTodotask.toDict(), '取消')

    # --------------------------------------------------------------------------
    # 通知客户端选择结果
    # --------------------------------------------------------------------------
    @classmethod
    def notifyQuickGotoDizhuMatch(cls, gameId, userId, roomId, **kwargs):
        mixId = kwargs.get('mixId', '')
        if ftlog.is_debug():
            ftlog.debug("DizhuQuickStart.onCmdQuickStart.notifyQuickGotoDizhuMatch:notify|", "userId=", userId, "gameId=", gameId, "roomId=", roomId, "mixId=", mixId)
        mo = MsgPack()
        mo.setCmd('quick_start')
        mo.setResult('gameId', gameId)
        mo.setResult('userId', userId)
        mo.setResult('roomId', roomId)
        mo.setResult('seatId', 0)
        mo.setResult('isOK', True)
        mo.setResult('mixId', mixId)
        mo.setResult('isMatch', 1)
        router.sendToUser(mo, userId)

    @classmethod
    def getMixConf(cls, conf, mixId):
        for mixConf in conf.get('mixConf', []):
            if mixConf.get('mixId') == mixId:
                return mixConf
        return {}

    @classmethod
    def getArenaMixConf(cls, conf, mixId):
        for mixConf in conf.get('matchConf', {}).get('feeRewardList', []):
            if mixConf.get('mixId') == mixId:
                return mixConf
        return {}

    @classmethod
    def getMatchSessionRoomIds(cls, userId):   # 提审用
        clientId = sessiondata.getClientId(userId)
        sessions = hallconf.getHallSessionInfo(DIZHU_GAMEID, clientId)
        matchSession = {}
        matchSessionRoomIds = []
        for session in sessions:
            if session.get('match') == 1:
                matchSession = session
                break
        for room in matchSession.get('rooms', []):
            roomId = room.get('id')
            matchSessionRoomIds.append(roomId)
        return matchSessionRoomIds

