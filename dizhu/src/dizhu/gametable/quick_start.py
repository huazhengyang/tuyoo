# coding=UTF-8
'''
斗地主quickstart模块
'''

from datetime import datetime

from dizhu.entity import dizhuconf, dizhuonlinedata, dizhuhallinfo
from dizhu.entity.dizhualert import Alert
from dizhu.entity.dizhuconf import DIZHU_GAMEID
from dizhu.entity.dizhuversion import SessionDizhuVersion
from freetime.entity.msg import MsgPack
from freetime.util import log as ftlog
from freetime.util.log import getMethodName
from hall.entity import hallproductselector, hallpopwnd, hallvip
from hall.entity.todotask import TodoTaskShowInfo, TodoTaskHelper, \
    TodoTaskPayOrder, TodoTaskQuickStart, TodoTaskDiZhuEvent
from poker.entity.configure import gdata, pokerconf
from poker.entity.dao import onlinedata, sessiondata
from poker.entity.dao import userchip
from poker.entity.game.quick_start import BaseQuickStart, \
    BaseQuickStartDispatcher
from poker.entity.game.rooms.room import TYRoom
from poker.protocol import router
from poker.util import strutil


__author__ = [
    '"Zhouhao" <zhouhao@tuyoogame.com>',
]

_DIZHU_QMATCH_CANDIDATE_ROOM_IDS = {}

_DIZHU_QMATCH_V3_73_IGNORE = [
    "Android_3.73_360.360,yisdkpay.0-hall6.360.win",
    "Android_3.73_360.360,yisdkpay.0-hall6.360.kuaile",
    "Android_3.73_360.360,yisdkpay.0-hall6.360.people",
    "Android_3.73_360.360,yisdkpay.0-hall6.360.rich",
    "Android_3.73_360.360,yisdkpay.0-hall6.360.day",
    "Android_3.73_360.360,yisdkpay.0-hall6.360.fk",
    "Android_3.73_360.360,yisdkpay4.0-hall6.360.laizi",
    "Android_3.73_360.360,yisdkpay4.0-hall6.360.tu",
    "IOS_3.730_tyGuest,tyAccount,weixin.appStore.0-hall6.tuyoo.huanle"
]

class DizhuQuickStartDispatcher(BaseQuickStartDispatcher):
    '''
    按clientId分发快速开始请求
    '''
    @classmethod
    def dispatchQuickStart(cls, msg, userId, gameId, roomId, tableId, playMode, clientId):
        clientVersion = 4.0
        if clientVersion >= 4.0 :
            return DizhuQuickStartV4_0.onCmdQuickStart(msg, userId, gameId, roomId, tableId, playMode, clientId)
        ftlog.error(getMethodName(), "unsupported client:", clientVersion)


class DizhuQuickStartV4_0(BaseQuickStart):
    
    @classmethod
    def _useSelfPopWnd(cls, userId):
        dizhuVersion = SessionDizhuVersion.getVersionNumber(userId)
        return dizhuVersion >= 3.812
    
    @classmethod
    def _getDizhuMatchCandidateRoomIds(cls):
        '''
        初始化地主比赛的待选房间列表
        '''
        # 若存在初始化好的地主比赛房间列表，则直接返回
        global _DIZHU_QMATCH_CANDIDATE_ROOM_IDS
        if _DIZHU_QMATCH_CANDIDATE_ROOM_IDS:
            return _DIZHU_QMATCH_CANDIDATE_ROOM_IDS

        gameId = 6
        # ctrlroomid_list = [
        #    [ ctrlroomid, quickindex],
        #    ...
        # ]
        ctrlroomid_quickindex_list = []
        # 生成的控制房间的房间id列表，ctrlroomid = bigRoomId * 10000 + 1000
        ctrlroomid_list = [bigRoomId * 10000 + 1000 for bigRoomId in gdata.gameIdBigRoomidsMap().get(gameId, [])]
        for ctrlroomid in ctrlroomid_list :
            roomdef = gdata.roomIdDefineMap()[ctrlroomid]
            ismatch = roomdef.configure.get('ismatch', 0)
            # 只选择比赛场,ismatch!=0为比赛场
            if ismatch != 0 :
                quickindex = roomdef.configure.get('quickIndex', 0)
                ctrlroomid_quickindex_list.append([ctrlroomid, quickindex])

        # 默认是升序
        ctrlroomid_quickindex_list.sort(key=lambda x : x[1])

        _DIZHU_QMATCH_CANDIDATE_ROOM_IDS = [x[0] for x in ctrlroomid_quickindex_list];
        return _DIZHU_QMATCH_CANDIDATE_ROOM_IDS

    @classmethod
    def _canQuickStartDizhuMatch(cls, userId, gameId, roomId, playMode):
        '''
        检测比赛房间是否符合快开条件
        @return ok{Bool} 是否满足条件进入地主比赛
        '''
        roomconf = gdata.roomIdDefineMap()[roomId].configure

        bigRoomId = gdata.getBigRoomId(roomId)
        ctrRoomIds = gdata.bigRoomidsMap()[bigRoomId]
        ctrlRoomId = ctrRoomIds[userId % len(ctrRoomIds)]
        reason = cls._canQuickEnterMatchRoom(userId, gameId, ctrlRoomId, 1)
        ftlog.debug("DizhuQuickStartV4_0._canQuickStartDizhuMatch: roomCond|userId=", userId, "roomId=", roomId, "bigRoomId=",bigRoomId, "ctrlRoomId=",ctrlRoomId,"reason=",reason)
        if reason != TYRoom.ENTER_ROOM_REASON_OK:
            return False

        # 若不存在开关，或者开关为0，代表房间关闭比赛快开
        quickMatchToggle = roomconf.get("quickMatchToggle", 0)
        ftlog.debug("DizhuQuickStartV4_0._canQuickStartDizhuMatch: userId=", userId, "roomId=", roomId, "quickMatchToggle=",quickMatchToggle)
        if quickMatchToggle == 0:
            return False

        # 获取选择比赛快开的条件列表
        coin_toplimit = roomconf.get("quickMatchCoinTopLimit", 0)

        # 获得用户的coin
        chip = userchip.getChip(userId)
        ftlog.debug("DizhuQuickStartV4_0._canQuickStartDizhuMatch: userId=", userId, "roomId=", roomId, "chip=",chip, "coin_toplimit",coin_toplimit)

        # 直接去比赛，不判断金币
        if playMode == dizhuconf.PLAYMODE_STRAIGHT_MATCH:
            return True

        if chip < coin_toplimit:
            return True

        return False

    @classmethod
    def _chooseDizhuMatchRoom(cls, userId, gameId, playMode):
        '''
        地主专属，选择一个比赛场返回
        @return1 roomid{int}: 比赛房间的ID
        @return2 ok{Bool}: 是否成功匹配到房间
        '''
        if gameId!=6:
            return 0, False

        #1.获取所有符合条件的比赛场
        ctrlroomid_list = cls._getDizhuMatchCandidateRoomIds()
        ftlog.debug('DizhuQuickStartV4_0._chooseDizhuMatchRoom: userId=', userId, 'ctrlroomid_list=', ctrlroomid_list)

        #2.选快开比赛房间
        for roomid in ctrlroomid_list:
            ok = cls._canQuickStartDizhuMatch(userId, gameId, roomid, playMode)
            if ok == True:
                ftlog.debug("DizhuQuickStartV4_0._chooseDizhuMatchRoom: before userId=", userId, "roomid=", roomid)

                bigRoomId = gdata.getBigRoomId(roomid)
                if bigRoomId == 0 :
                    break
                ctrRoomIds = gdata.bigRoomidsMap()[bigRoomId]
                ctrlRoomId = ctrRoomIds[userId % len(ctrRoomIds)]

                ftlog.debug("DizhuQuickStartV4_0._chooseDizhuMatchRoom: after userId=", userId, "roomid=", roomid, "bigRoomId=", bigRoomId, 'ctrlRoomId=', ctrlRoomId)
                return ctrlRoomId, True

        ftlog.debug('DizhuQuickStartV4_0._chooseDizhuMatchRoom->exit', 0, False, "userId=", userId)
        return 0, False

    @classmethod
    def notifyQuickGotoDizhuMatch(cls, gameId, userId, roomId):
        ftlog.debug("DizhuQuickStartV4_0.notifyQuickGotoDizhuMatch:notify|", "userId=", userId, "gameId=", gameId, "roomId=", roomId)
        mo = MsgPack()
        mo.setCmd('quick_start')
        mo.setResult('gameId', gameId)
        mo.setResult('userId', userId)
        mo.setResult('roomId', roomId)
        mo.setResult('seatId', 0)
        mo.setResult('isOK', True)
        mo.setResult('isMatch', 1)
        router.sendToUser(mo, userId)

    @classmethod
    def findLoc(cls, locList, roomId, tableId):
        for loc in locList:
            if loc[1] == roomId and loc[2] == tableId:
                return loc
        return None
     
    @classmethod
    def isDiffLoc(cls, userId, gameId, roomId, tableId, clientId, loc):
        pass
    
    @classmethod
    def isMatchRoom(cls, roomId):
        roomConf = gdata.getRoomConfigure(roomId)
        return roomConf.get('typeName') in ('group_match', 'arena_match')
        
    @classmethod
    def checkUserLoc(cls, userId, gameId, roomId, tableId, clientId):
        locList = dizhuonlinedata.getOnlineLocListByGameId(userId, gameId, clientId)
        if ftlog.is_debug():
            ftlog.debug('DizhuQuickStartV4_0.checkUserLoc userId=', userId,
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
        
        # 比赛场只要是同一个bigRoomId就可以
        if cls.isMatchRoom(loc[1]):
            if cls.isSameBigRoom(loc[1], roomId):
                return True, None
            return False, loc
        
        # 金币场roomId必须相同
        if roomId == loc[1]:
            return True, loc
        
        return False, loc
    
    @classmethod
    def isSameBigRoom(cls, roomId1, roomId2):
        return strutil.getBigRoomIdFromInstanceRoomId(roomId1) == strutil.getBigRoomIdFromInstanceRoomId(roomId2)
    
    @classmethod
    def onCmdQuickStart1(cls, msg, userId, gameId, roomId, tableId, playMode, clientId):
        '''
        拦截父类处理的选择房间逻辑，先于父类处理，若选择成功，则不进行父类的选择房间处理逻辑，否则正常走父类的处理逻辑
        '''

        if not pokerconf.isOpenMoreTable(clientId):
            ok, loc = cls.checkUserLoc(userId, gameId, roomId, tableId, clientId)
            if not ok:
                # 弹框
                tipsPlaying = dizhuconf.getPublicConf('tips.playing', '您正在其它房间对局，是否回去？')
                showInfo = TodoTaskShowInfo(tipsPlaying)
                showInfo.setSubCmd(TodoTaskQuickStart(loc[0], loc[1], loc[2], loc[3]))
                TodoTaskHelper.sendTodoTask(gameId, userId, showInfo)
                ftlog.debug('DizhuQuickStartV4_0.onCmdQuickStart Fail userId=', userId,
                           'roomId=', roomId,
                           'tableId=', tableId,
                           'clientId=', clientId,
                           'loc=', loc)
                return
            if loc:
                tableId = loc[2]

        _, version, _ = strutil.parseClientId(clientId)
        ftlog.debug("DizhuQuickStartV4_0.onCmdQuickStart: clientId=", clientId, "userId=", userId, "roomId=", roomId, "tableId=", tableId, "version=", version, "type:", type(version), "playMode=",playMode)

        # 地主会优先去匹配比赛的房间，客户端是3.76及更高版本才支持
        if (playMode == None or playMode == "match" or playMode == "straightMatch") and roomId==0 and gameId==6 and (version >= 3.76 or (version >= 3.73 and not (clientId in _DIZHU_QMATCH_V3_73_IGNORE)) ):
            chose_roomid, ok = cls._chooseDizhuMatchRoom(userId, gameId, playMode)
            ftlog.debug("DizhuQuickStartV4_0._chooseDizhuMatchRoom:chosen|room_id=", chose_roomid, "userId=", userId, "ok=", ok)
            if ok:
                bigroomid = gdata.getBigRoomId(chose_roomid)
                ftlog.debug("DizhuQuickStartV4_0._chooseDizhuMatchRoom: userId=", userId, "roomId=", chose_roomid)
                cls.notifyQuickGotoDizhuMatch(gameId, userId, bigroomid)
                return

        if playMode == "match":
            playMode = dizhuconf.PLAYMODE_123

        super(DizhuQuickStartV4_0, cls).onCmdQuickStart(msg, userId, gameId, roomId, tableId, playMode, clientId)
        return
    
    @classmethod
    def onCmdQuickStart(cls, msg, userId, gameId, roomId, tableId, playMode, clientId):
        '''
        拦截父类处理的选择房间逻辑，先于父类处理，若选择成功，则不进行父类的选择房间处理逻辑，否则正常走父类的处理逻辑
        '''

        if not pokerconf.isOpenMoreTable(clientId) :
            loc = onlinedata.checkUserLoc(userId, clientId, gameId)
            ftlog.debug('DizhuQuickStartV4_0.onCmdQuickStart:old client, checkUserLoc->', loc, caller=cls)
            if isinstance(loc, basestring) :
                lgameId, lroomId, ltableId, lseatId = loc.split('.')
                lgameId, lroomId, ltableId, lseatId = strutil.parseInts(lgameId, lroomId, ltableId, lseatId)
                if lgameId == gameId and lroomId > 0 :
                    roomId = lroomId
                    tableId = ltableId
                    ftlog.debug('DizhuQuickStartV4_0.onCmdQuickStartold client, reset roomId, tableId->', roomId, tableId, caller=cls)

        _, version, _ = strutil.parseClientId(clientId)
        ftlog.debug("DizhuQuickStartV4_0.onCmdQuickStart: clientId=", clientId, "userId=", userId, "roomId=", roomId, "tableId=", tableId, "version=", version, "type:", type(version), "playMode=",playMode)

        # 地主会优先去匹配比赛的房间，客户端是3.76及更高版本才支持
        if (playMode == None or playMode == "match" or playMode == "straightMatch") and roomId==0 and gameId==6 and (version >= 3.76 or (version >= 3.73 and not (clientId in _DIZHU_QMATCH_V3_73_IGNORE)) ):
            chose_roomid, ok = cls._chooseDizhuMatchRoom(userId, gameId, playMode)
            ftlog.debug("DizhuQuickStartV4_0._chooseDizhuMatchRoom:chosen|room_id=", chose_roomid, "userId=", userId, "ok=", ok)
            if ok:
                bigroomid = gdata.getBigRoomId(chose_roomid)
                ftlog.debug("DizhuQuickStartV4_0._chooseDizhuMatchRoom: userId=", userId, "roomId=", chose_roomid)
                cls.notifyQuickGotoDizhuMatch(gameId, userId, bigroomid)
                return

        if playMode == "match":
            playMode = dizhuconf.PLAYMODE_123

        super(DizhuQuickStartV4_0, cls).onCmdQuickStart(msg, userId, gameId, roomId, tableId, playMode, clientId)
        return

    @classmethod
    def _getCandidateRoomIds(cls, gameId, playMode):
        return super(DizhuQuickStartV4_0, cls)._getCandidateRoomIds(gameId, playMode)

    @classmethod
    def _checkOpenTime(cls, roomConfig, nowTime):
        openTimeList = roomConfig.get('openTimeList')
        if not openTimeList:
            return True
        timeRangeList = []
        timeZeroStr = '00:00:00'
        for timeRange in openTimeList:
            try:
                beginTime = datetime.strptime(timeRange.get('begin', timeZeroStr), '%H:%M:%S').time()
                endTime = datetime.strptime(timeRange.get('end', timeZeroStr), '%H:%M:%S').time()
                timeRangeList.append((beginTime, endTime))
            except:
                ftlog.error('DizhuQuickStartV4_0.checkOpenTime',
                            'openTimeList=', openTimeList,
                            'timeRange=', timeRange)
        return cls._checkTimeInRangeList(timeRangeList, nowTime)
    
    @classmethod
    def _checkTimeInRangeList(cls, timeRangeList, nowTime):
        '''
        检测cur_time是否在时间列表范围内
        '''
        for beginTime, endTime in timeRangeList:
            try:
                if beginTime == endTime:
                    return True
                elif beginTime < endTime:
                    if nowTime >= beginTime and nowTime < endTime:
                        return True
                else:
                    if nowTime >= beginTime or nowTime < endTime:
                        return True
            except:
                ftlog.error('DizhuQuickStartV4_0._checkTimeInRangeList',
                            'timeRangeList=', timeRangeList,
                            'nowTime=', nowTime)
        return False

    @classmethod
    def _canQuickEnterRoomBase(cls, userId, gameId, roomId, isOnly):
        try :
            chip = userchip.getChip(userId)
            if ftlog.is_debug():
                ftlog.debug(gdata.roomIdDefineMap()[roomId].configure)
            roomConfig = gdata.roomIdDefineMap()[roomId].configure
            if ftlog.is_debug():
                ftlog.debug('userId =', userId,
                        'minCoin =', roomConfig.get('minCoin'),
                        'maxCoin =', roomConfig.get('maxCoin'),
                        'minCoinQS =', roomConfig.get('minCoinQS'),
                        'maxCoinQS =', roomConfig.get('maxCoinQS'),
                        'chip =', chip,
                        'isOnly =', isOnly)
            if isOnly :
                minCoinQs = roomConfig['minCoin']
                maxCoinQs = roomConfig['maxCoin']
            else:
                minCoinQs = roomConfig['minCoinQS']
                maxCoinQs = roomConfig['maxCoinQS']
            ismatch = roomConfig.get('ismatch')

            if ismatch:
                return TYRoom.ENTER_ROOM_REASON_NOT_QUALIFIED

            if ftlog.is_debug():
                ftlog.debug('roomId =', roomId, 'minCoinQs =', minCoinQs,
                            'maxCoinQs =', maxCoinQs, 'chip =', chip,
                            caller=cls)

            if minCoinQs > 0 and chip < minCoinQs:
                return TYRoom.ENTER_ROOM_REASON_LESS_MIN
            if maxCoinQs > 0 and chip >= maxCoinQs:
                return TYRoom.ENTER_ROOM_REASON_GREATER_MAX

            return TYRoom.ENTER_ROOM_REASON_OK

        except Exception as e:
            ftlog.error(e)
            return TYRoom.ENTER_ROOM_REASON_INNER_ERROR
        
    @classmethod
    def _canQuickEnterRoom(cls, userId, gameId, roomId, isOnly):
        ret = cls._canQuickEnterRoomBase(userId, gameId, roomId, isOnly)
        if ret != TYRoom.ENTER_ROOM_REASON_OK :
            return  ret

        roomConfig = gdata.roomIdDefineMap()[roomId].configure

        # 检测准入情况，配置中若没有准入时间（openTimeList），则默认准许全天进入
        if not cls._checkOpenTime(roomConfig, datetime.now().time()):
            return TYRoom.ENTER_ROOM_REASON_NOT_OPEN

        if roomConfig.get('typeName') in ('dizhuFT', 'dizhu_friend'):
            return TYRoom.ENTER_ROOM_REASON_NOT_OPEN
        
        clientId = sessiondata.getClientId(userId)
        if not dizhuhallinfo.canDisplayRoom(gameId, userId, clientId, roomId, roomConfig):
            if ftlog.is_debug():
                ftlog.debug('DizhuQuickStartV4_0._canQuickEnterMatchRoom NotCanDisplayRoom',
                            'gameId=', gameId,
                            'userId=', userId,
                            'clientId=', clientId,
                            'roomId=', roomId)
            return TYRoom.ENTER_ROOM_REASON_NOT_OPEN
        
        # 大师分和vip准入筛选
        # 两个条件是`或者`的关系
        dashifenLevel = roomConfig.get('dashifenLevel', 0)
        vipLevel = roomConfig.get('vipLevel', 0)
        ftlog.debug('_canQuickEnterRoom->', userId, gameId, roomId, 'dashifenLevel=', dashifenLevel, 'vipLevel=', vipLevel)
        if dashifenLevel <= 0 and vipLevel <= 0 :
            return TYRoom.ENTER_ROOM_REASON_OK

        # 若大师分不满足情况，则再检测VIP，不能直接返回大师分不满足的错误
        if dashifenLevel > 0 :
            dashifen = 0
            from dizhu.game import TGDizhu
            info = TGDizhu.getDaShiFen(userId, None)
            ftlog.debug('_canQuickEnterRoom->', userId, gameId, roomId, 'dashifenInfo=', info)
            if info :
                dashifen = info.get('level', 0)
            if dashifen >= dashifenLevel :
                return TYRoom.ENTER_ROOM_REASON_OK

        if vipLevel > 0 :
            vip = 0
            vipInfo = hallvip.userVipSystem.getUserVip(userId)
            ftlog.debug('_canQuickEnterRoom->', userId, gameId, roomId, 'vipInfo=', vipInfo)
            if vipInfo :
                vip = vipInfo.vipLevel.level
            if vip >= vipLevel :
                return TYRoom.ENTER_ROOM_REASON_OK

        return TYRoom.ENTER_ROOM_REASON_DASHIFEI_LEVEL


    @classmethod
    def _canQuickEnterMatchRoomParent(cls, userId, gameId, roomId, isOnly):

        try :
            chip = userchip.getChip(userId)
            ftlog.debug(gdata.roomIdDefineMap()[roomId].configure)
            roomConfig = gdata.roomIdDefineMap()[roomId].configure
            if isOnly :
                minCoinQs = roomConfig['minCoin']
                maxCoinQs = roomConfig['maxCoin']
            else:
                minCoinQs = roomConfig['minCoinQS']
                maxCoinQs = roomConfig['maxCoinQS']

            ftlog.debug('roomId =', roomId, 'minCoinQs =', minCoinQs,
                        'maxCoinQs =', maxCoinQs, 'chip =', chip,
                        caller=cls)

            if chip < minCoinQs:
                return TYRoom.ENTER_ROOM_REASON_LESS_MIN
            if maxCoinQs > 0 and chip >= maxCoinQs:
                return TYRoom.ENTER_ROOM_REASON_GREATER_MAX

            return TYRoom.ENTER_ROOM_REASON_OK

        except Exception as e:
            ftlog.error(e)
            return TYRoom.ENTER_ROOM_REASON_INNER_ERROR

    @classmethod
    def _canQuickEnterMatchRoom(cls, userId, gameId, roomId, isOnly):
        ret = cls._canQuickEnterMatchRoomParent(userId, gameId, roomId, isOnly)
        if ret != TYRoom.ENTER_ROOM_REASON_OK :
            return  ret

        roomConfig = gdata.roomIdDefineMap()[roomId].configure

        # 检测准入情况，配置中若没有准入时间（openTimeList），则默认准许全天进入
        if not cls._checkOpenTime(roomConfig, datetime.now().time()):
            return TYRoom.ENTER_ROOM_REASON_NOT_OPEN

        clientId = sessiondata.getClientId(userId)
        if not dizhuhallinfo.canDisplayRoom(gameId, userId, clientId, roomId, roomConfig):
            if ftlog.is_debug():
                ftlog.debug('DizhuQuickStartV4_0._canQuickEnterMatchRoom NotCanDisplayRoom',
                            'gameId=', gameId,
                            'userId=', userId,
                            'clientId=', clientId,
                            'roomId=', roomId)
            return TYRoom.ENTER_ROOM_REASON_NOT_OPEN
        
        # 大师分和vip准入筛选
        # 两个条件是`或者`的关系
        dashifenLevel = roomConfig.get('dashifenLevel', 0)
        vipLevel = roomConfig.get('vipLevel', 0)
        ftlog.debug('_canQuickEnterRoom->', userId, gameId, roomId, 'dashifenLevel=', dashifenLevel, 'vipLevel=', vipLevel)
        if dashifenLevel <= 0 and vipLevel <= 0 :
            return TYRoom.ENTER_ROOM_REASON_OK

        # 若大师分不满足情况，则再检测VIP，不能直接返回大师分不满足的错误
        if dashifenLevel > 0 :
            dashifen = 0
            from dizhu.game import TGDizhu
            info = TGDizhu.getDaShiFen(userId, None)
            ftlog.debug('_canQuickEnterRoom->', userId, gameId, roomId, 'dashifenInfo=', info)
            if info :
                dashifen = info.get('level', 0)
            if dashifen >= dashifenLevel :
                return TYRoom.ENTER_ROOM_REASON_OK

        if vipLevel > 0 :
            vip = 0
            vipInfo = hallvip.userVipSystem.getUserVip(userId)
            ftlog.debug('_canQuickEnterRoom->', userId, gameId, roomId, 'vipInfo=', vipInfo)
            if vipInfo :
                vip = vipInfo.vipLevel.level
            if vip >= vipLevel :
                return TYRoom.ENTER_ROOM_REASON_OK

        return TYRoom.ENTER_ROOM_REASON_DASHIFEI_LEVEL
    
    @classmethod
    def _sendTodoTaskToUser(cls, userId, errorCode):
        tip = dizhuconf.getQuickStartErrorMsg(errorCode)
        t = TodoTaskShowInfo(tip, True)
        try:
            ftlog.debug('test ddz pop TodoTaskShowInfo come in userId = ', userId)
            if cls._useSelfPopWnd(userId):
                Alert.sendNormalAlert(DIZHU_GAMEID, userId, '提示', tip, None, '确定')
                return
        except:
            ftlog.error('_sendTodoTaskToUser userId=', userId,
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
            ftlog.error('_sendTodoTaskToUserWithTip userId = ', userId,
                                                    'tip = ', tip)
        msg = TodoTaskHelper.makeTodoTaskMsg(DIZHU_GAMEID, userId, t)
        router.sendToUser(msg, userId)

    @classmethod
    def _sendTodoTaskToUserWithRoomKey(cls, userId, roomId, msg, roomkey):
        if roomId <= 0 :
            roomId = msg.getParam('roomId')
            if not roomId:
                return False

        ftlog.debug("DizhuQuickStartV4_0._sendTodoTaskToUserWithRoomKey: roomId=", roomId, "userId=", userId)
        roomconf = gdata.getRoomConfigure(roomId)
        ftlog.debug("DizhuQuickStartV4_0._sendTodoTaskToUserWithRoomKey: roomId=", roomId, "userId=", userId, "roomconf=", roomconf)

        if not roomconf:
            return False
        tip = roomconf.get(roomkey)
        if not tip:
            return False
        cls._sendTodoTaskToUserWithTip(userId, tip)
        return True

    @classmethod
    def _sendTodoTaskBuyChip(cls, userId, roomId, clientId):
        todotask = hallpopwnd.makeTodoTaskLessbuyChip(DIZHU_GAMEID, userId, clientId, roomId)
        if todotask:
            TodoTaskHelper.sendTodoTask(DIZHU_GAMEID, userId, todotask)
#         from hall.entity import hallstore, hallitem
#         needChip = 0
#         if roomId in gdata.bigRoomidsMap() :
#             # roomId是一个bigRoomId
#             ctlRoomId = gdata.bigRoomidsMap()[roomId][0]
#             needChip = gdata.roomIdDefineMap()[ctlRoomId].configure['minCoin']
#         elif roomId in gdata.roomIdDefineMap() :
#             # roomId是一个ctrlRoomId或者是一个桌子房间ID,
#             needChip = gdata.roomIdDefineMap()[roomId].configure['minCoin']
#         else:
#             needChip = 20000
#         product, _ = hallstore.findProductByContains(DIZHU_GAMEID, userId, clientId,
#                                                      ['lessbuychip'], None,
#                                                      hallitem.ASSET_CHIP_KIND_ID,
#                                                      needChip)
#         if not product:
#             return None
#
#         _, clientVer, _ = strutil.parseClientId(clientId)
#         if clientVer >= 3.7:
#             pass
#         else:
#             TodoTaskHelper.sendTodoTask(DIZHU_GAMEID, userId, TodoTaskPayOrder(product))

    @classmethod
    def _sendChargeLeadTodoTask(cls, userId, roomId, clientId):
        product, _ = hallproductselector.selectLessbuyProduct(DIZHU_GAMEID, userId, clientId, roomId)
        t = TodoTaskPayOrder(product)
        msg = TodoTaskHelper.makeTodoTaskMsg(DIZHU_GAMEID, userId, t)
        router.sendToUser(msg, userId)

    @classmethod
    def _sendTodoTaskJumpHighRoom(cls, userId, playMode, clientId):
        # todo fix the pop wnd to ddz's
        if not playMode in dizhuconf.PLAYMODE_ALLSET :
            playMode = dizhuconf.PLAYMODE_DEFAULT
        chosenRoomId, _ = cls._chooseRoom(userId, DIZHU_GAMEID, playMode)
        if chosenRoomId :
            quick_start_ = TodoTaskQuickStart(DIZHU_GAMEID, chosenRoomId)
            info_str_ = dizhuconf.getQuickStartErrorMsg(TYRoom.ENTER_ROOM_REASON_GREATER_MAX)
            show_info_ = TodoTaskShowInfo(info_str_, True)
            show_info_.setSubCmd(quick_start_)
            try:
                if cls._useSelfPopWnd(userId):
                    todoTaskObj = TodoTaskHelper.encodeTodoTasks(quick_start_)
                    Alert.sendNormalAlert2Button(DIZHU_GAMEID, userId, '提示', info_str_, todoTaskObj[0], '确定', None, '取消')
                    return
            except:
                ftlog.error('_sendTodoTaskJumpHighRoom error userId = ', userId,
                                                    ' clientId = ', clientId,
                                                    'playMode = ', playMode)
            msg = TodoTaskHelper.makeTodoTaskMsg(DIZHU_GAMEID, userId, show_info_)
            router.sendToUser(msg, userId)
        else:
            cls._sendTodoTaskToUser(userId, TYRoom.ENTER_ROOM_REASON_GREATER_ALL)

    @classmethod
    def _sendToDoTaskJumpToStore(cls, userId):
        if not cls._useSelfPopWnd(userId):
            # todo fix the pop wnd to ddz's
            win = hallpopwnd.makeTodotaskJumpToStoreOrHall("您的金币不足，请购买金币或参加免费比赛~")
            msg = TodoTaskHelper.makeTodoTaskMsg(DIZHU_GAMEID, userId, win)
            router.sendToUser(msg, userId)
            return
        
        message = "您的金币不足，请购买金币或参加免费比赛~"
        confirmTodotask = TodoTaskDiZhuEvent('dizhu_goto_store')
        cancelTodotask = TodoTaskDiZhuEvent('dizhu_back_hall')
        ftlog.debug('_sendToDoTaskJumpToStore',
                    'userId=', userId,
                    'confirmTodotask=', confirmTodotask,
                    'cancelTodotask=', cancelTodotask.toDict())
        Alert.sendNormalAlert2Button(DIZHU_GAMEID, userId, '提示', message, 
                                     confirmTodotask.toDict(), '确定', 
                                     cancelTodotask.toDict(), '取消')

    @classmethod
    def _onEnterRoomFailed(cls, msg, checkResult, userId, clientId, roomId=0):
        '''
        进入房间失败,需要判定一下失败原因, 进行不同的业务处理
        '''
        # PC的补丁，需要返回一个失败的quick_start消息
        mo = MsgPack()
        mo.setCmd('quick_start')
        mo.setResult('gameId', DIZHU_GAMEID)
        mo.setResult('userId', userId)
        mo.setResult('roomId', 0)
        mo.setResult('seatId', 0)
        mo.setResult('tableId', 0)
        router.sendToUser(mo, userId)

        if checkResult == TYRoom.ENTER_ROOM_REASON_CONFLICT :
            cls._sendTodoTaskToUser(userId, checkResult)

        elif checkResult == TYRoom.ENTER_ROOM_REASON_INNER_ERROR :
            cls._sendTodoTaskToUser(userId, checkResult)

        elif checkResult == TYRoom.ENTER_ROOM_REASON_ROOM_FULL :
            cls._sendTodoTaskToUser(userId, checkResult)

        elif checkResult == TYRoom.ENTER_ROOM_REASON_LESS_MIN :
            innerTable = msg.getParam("innerTable", 0)
            ftlog.debug('enter_less_min msg=', msg, 'innerTable=', innerTable)
            if innerTable == 1:
                return cls._sendToDoTaskJumpToStore(userId)

            if roomId <= 0 :
                roomId = msg.getParam('roomId')
                if not roomId:
                    roomId = msg.getParam('candidateRoomId')
                if not roomId :
                    return
            cls._sendTodoTaskBuyChip(userId, roomId, clientId)
            #cls._sendChargeLeadTodoTask(userId, roomId, clientId)

        elif checkResult == TYRoom.ENTER_ROOM_REASON_GREATER_MAX :
            playMode = msg.getParam('playMode')
            if not playMode :
                # 找到当前要进入的房间的玩法
                if roomId <= 0 :
                    roomId = msg.getParam('roomId')
                    if not roomId:
                        roomId = msg.getParam('candidateRoomId')
                if roomId > 0 :
                    if roomId in gdata.roomIdDefineMap() :
                        playMode = gdata.roomIdDefineMap()[roomId].configure.get('playMode', None)
                    elif roomId in gdata.bigRoomidsMap() :
                        roomId = gdata.bigRoomidsMap()[roomId][0]
                        playMode = gdata.roomIdDefineMap()[roomId].configure.get('playMode', None)

            cls._sendTodoTaskJumpHighRoom(userId, playMode, clientId)

        elif checkResult == TYRoom.ENTER_ROOM_REASON_GREATER_ALL :
            cls._sendTodoTaskToUser(userId, checkResult)

        elif checkResult == TYRoom.ENTER_ROOM_REASON_TABLE_FULL :
            cls._sendTodoTaskToUser(userId, checkResult)

        elif checkResult == TYRoom.ENTER_ROOM_REASON_WRONG_TIME :
            cls._sendTodoTaskToUser(userId, checkResult)

        elif checkResult == TYRoom.ENTER_ROOM_REASON_NOT_QUALIFIED :
            cls._sendTodoTaskToUser(userId, checkResult)

        elif checkResult == TYRoom.ENTER_ROOM_REASON_ROOM_ID_ERROR :
            cls._sendTodoTaskToUser(userId, checkResult)

        elif checkResult == TYRoom.ENTER_ROOM_REASON_DASHIFEI_LEVEL :
            if cls._sendTodoTaskToUserWithRoomKey(userId, roomId, msg, "vipOrDashifenTip"):
                return
            cls._sendTodoTaskToUser(userId, checkResult)

        elif checkResult == TYRoom.ENTER_ROOM_REASON_NOT_OPEN:
            if cls._sendTodoTaskToUserWithRoomKey(userId, roomId, msg, "openTimeListTip"):
                return
            cls._sendTodoTaskToUser(userId, checkResult)

        elif checkResult == TYRoom.ENTER_ROOM_REASON_VIP_LEVEL :
            if cls._sendTodoTaskToUserWithRoomKey(userId, roomId, msg, "vipOrDashifenTip"):
                return
            cls._sendTodoTaskToUser(userId, checkResult)

        else:  # TYRoom.ENTER_ROOM_REASON_INNER_ERROR :
            cls._sendTodoTaskToUser(userId, TYRoom.ENTER_ROOM_REASON_INNER_ERROR)
