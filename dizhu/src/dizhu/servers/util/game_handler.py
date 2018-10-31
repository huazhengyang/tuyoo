# -*- coding: utf-8 -*-
'''
Created on 2015年5月20日

@author: zqh
'''
import collections
import datetime
import json
import numbers
import random
import time

from sre_compile import isstring
from dizhu.activities.toolbox import UserInfo, UserBag
from dizhu.entity import dizhuconf, treasurebox, dizhu_util, dizhutvoads, dizhu_new_roundlist, dizhu_signin
from dizhu.entity.dizhuconf import DIZHU_GAMEID
import dizhu.entity.dizhuhallinfo as dizhuhallinfo
from dizhu.entity.dizhuversion import SessionDizhuVersion
from dizhu.entity.dizhuwarmup import WarmUpSystem
#from dizhu.entity.official_counts import wx_official
from dizhu.entity.wx_follow import WxFollowHelper
from dizhu.game import TGDizhu
from dizhu.games.endgame.endgame import EndgameHelper
from dizhu.gametable.dizhu_quick_start_wx import DizhuQuickStartWx
from dizhu.servers.util.rpc import match_remote, new_table_remote
from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from hall.entity import hallconf, halluser, hall_share3
import hall.entity.hallitem as hallitem
from hall.entity.hallpopwnd import makeTodoTaskLessbuyChip, makeTodoTaskLuckBuy
from hall.entity.hallusercond import UserConditionRegister
from hall.entity.todotask import TodoTaskHelper
from hall.entity.usercoupon import user_coupon_details
from hall.entity.usercoupon.events import UserCouponReceiveEvent
from hall.game import TGHall
from hall.servers.common.base_checker import BaseMsgPackChecker
from hall.servers.util.util_helper import UtilHelper
from hall.entity import halluser_dailydata
from poker.entity.biz import bireport
from poker.entity.biz.bireport import getRoomOnLineUserCount
from poker.entity.biz.content import TYContentItem
from poker.entity.configure import configure, gdata, pokerconf
from poker.entity.dao import gamedata, onlinedata, daobase
from poker.entity.events.tyevent import OnLineGameChangedEvent
from poker.entity.game.rooms.async_upgrade_hero_match_ctrl.match_db import \
    AsyncUpgradeHeroMatchDataBase
from poker.entity.game.rooms.big_match_ctrl.config import StartConfig
from poker.entity.game.rooms.big_match_ctrl.const import MatchType
import poker.entity.game.rooms.roominfo as roominfo
from poker.protocol import runcmd, router
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod
from poker.util import strutil
import poker.util.timestamp as pktimestamp


@markCmdActionHandler
class GameTcpHandler(BaseMsgPackChecker):
    def __init__(self):
        self.helper = UtilHelper()

    def _check_param_sessionIndex(self, msg, key, params):
        sessionIndex = msg.getParam(key)
        if isinstance(sessionIndex, int) and sessionIndex >= 0:
            return None, sessionIndex
        return None, -1

    def _check_param_mixId(self, msg, key, params):
        mixId = msg.getParam(key)
        if mixId in ['', 'low', 'middle', 'high', 'master', 'xingyao']:
            return None, mixId
        return None, ''

    def _check_param_rankId(self, msg, key, params):
        rankId = msg.getParam(key, '-1')
        return None, rankId

    def _check_param_number(self, msg, key, params):
        number = msg.getParam(key, msg.getParam('number'))
        if isinstance(number, int):
            return None, number
        return 'ERROR of number !', None

    def _check_param_roomId(self, msg, key, params):
        roomId = msg.getParam(key, msg.getParam('roomId'))
        return None, roomId

    def _check_param_version(self, msg, key, params):
        version = msg.getParam(key, msg.getParam('version'))
        if isinstance(version, numbers.Number):
            return None, version
        if isinstance(version, basestring):
            return None, float(version)
        return None, 0

    def _check_param_matchId(self, msg, key, params):
        matchId = msg.getParam(key, msg.getParam('matchId'))
        return None, matchId

    def _check_param_rank(self, msg, key, params):
        rank = msg.getParam(key, msg.getParam('rank'))
        return None, rank

    def _check_param_recordId(self, msg, key, params):
        recordId = msg.getParam(key, msg.getParam('recordId'))
        return None, recordId

    def _check_param_segment(self, msg, key, params):
        try:
            segment = int(msg.getParam(key, 0))
        except:
            segment = 0
        return None, segment

    def _check_param_dayNumber(self, msg, key, params):
        dayNumber = msg.getParam(key, msg.getParam('dayNumber'))
        if isinstance(dayNumber, int):
            return None, dayNumber
        return 'ERROR of dayNumber !', None

    def _check_param_burialId(self, msg, key, params):
        value = msg.getParam(key)
        if isstring(value):
            return None, value
        return 'ERROR of burialId !' + str(value), None

    def _check_param_day(self, msg, key, params):
        day = msg.getParam(key, msg.getParam('day'))
        if isinstance(day, int):
            return None, day
        return 'ERROR of day !', None

    def _check_param_typeId(self, msg, key, params):
        typeId = msg.getParam(key, msg.getParam('typeId'))
        if isinstance(typeId, int):
            return None, typeId
        return 'ERROR of typeId !', None

    def _get_decoration_info(self):
        return dizhuconf.getPublic().get('decoration_info', {})

    def _get_roomlist_decoration_info(self):
        return dizhuconf.getPublic().get('ddzRoomListAdornTag', {})
    
    def _get_switch_config(self, clientId):
        switchInfo = configure.getTcContentByGameId('switch', None, DIZHU_GAMEID, clientId, {})
        return switchInfo

    def _get_wxTuiguang_config(self):
        return dizhuconf.getPublic().get('wxTuiguang', {})

    def _get_popwndSeconds(self):
        return dizhuconf.getPublic().get('popwndSeconds', 3600)

    def _get_gonggao_info(self, userId, clientId):
        if ftlog.is_debug():
            ftlog.debug('GameTcpHandler._get_gonggao_info userId=', userId,
                        'clientId=', clientId)
        intClientId = pokerconf.clientIdToNumber(clientId)
        if intClientId == 24105:  # 小游戏竖版
            return dizhuconf.getPublic().get('gonggao_shuban', [])
        return dizhuconf.getPublic().get('gonggao', [])
    
    @markCmdActionMethod(cmd='game', action="async_upgrade_hero_match", clientIdVer=0, scope='game')
    def doGetAsyncUpgradeHeroMatch(self, userId, gameId, clientId, version):
        '''
        获取异步百万闯关赛的比赛列表
        '''
        ctlRoomIds = [bigRoomId * 10000 + 1000 for bigRoomId in gdata.gameIdBigRoomidsMap()[gameId]]
        ftlog.debug('ddz.GameTcpHandler.doGetAsyncUpgradeHeroMatch',
                    'userId=', userId,
                    'gameId=', gameId,
                    'clientId=', clientId,
                    'ctrRoomIds=', ctlRoomIds)
        
        matches = []
        for ctlRoomId in ctlRoomIds:
            roomDef = gdata.roomIdDefineMap()[ctlRoomId]
            roomConfig = roomDef.configure
            if roomConfig.get('typeName') == 'async_upgrade_hero_match':
                match = {}
                match['roomId'] = gdata.getBigRoomId(ctlRoomId)
                match['playMode'] = roomConfig.get('playMode', '123')
                match['name'] = roomConfig.get('name', '')
                match['type'] = 'async_upgrade_hero_match'
                records = []
                
                asyncCtrRoomIds = gdata.bigRoomidsMap()[gdata.getBigRoomId(ctlRoomId)]
                # 只读取已有的比赛
                for asyncCtrlRoom in asyncCtrRoomIds:
                    loclist = onlinedata.getOnlineLocList(userId)
                    for loc in loclist:
                        roomId, _, _ = loc
                        if asyncCtrlRoom == roomId:
                            continue
                    
                    dataStr = gamedata.getGameAttr(userId, gameId, AsyncUpgradeHeroMatchDataBase.getDBKey(asyncCtrlRoom))
                    if not dataStr:
                        continue
                    
                    data = json.loads(dataStr)
                    enterTime = data.get('enterTime', 0)
                    curTimestamp = pktimestamp.getCurrentTimestamp()
                    if (curTimestamp - enterTime > (86400 * 2)):
                        # 已超过两天
                        gamedata.setGameAttr(userId, gameId, AsyncUpgradeHeroMatchDataBase.getDBKey(asyncCtrlRoom), '')
                        continue
                    
                    data['roomId'] = asyncCtrlRoom
                    records.append(data)
                
                match['records'] = records    
                matches.append(match)
                
        message = MsgPack()
        message.setCmd('game')
        message.setResult('action', 'async_upgrade_hero_match')
        message.setResult('gameId', gameId)
        message.setResult('userId', userId)
        message.setResult('clientId', clientId)
        message.setResult('matches', matches)
        ftlog.debug('msg:', message)
        router.sendToUser(message, userId)
        
        
    '''
    地主获取房间列表信息协议：
        1，过滤已下线比赛房间
        2，在地主3.707，大厅3.76版本中，新增需求：金币场增加比赛场房间、星耀大师场房间:
            1）对之前的版本中滤金币场中的比赛场房间
            2）地主3.703版本中不支持roomLevel大于等于5的值，在星耀大师场中添加一个realRoomLevel字段
                大厅版本<3.76的过滤掉包含realRoomLevel字段的房间
                大厅版本>=3.76的将包含realRoomLevel字段的房间属性中的roomLevel字段的值设定为realRoomLevel，这个值需要在tableinfo协议中处理
    '''

    @markCmdActionMethod(cmd='hall', action="info", clientIdVer=0, scope='game')
    def doHallInfo(self, userId, gameId, clientId):
        # 获取到的不包含已结束比赛的房间信息
        roominfos = self._get_roominfo_by_filter(gameId, clientId)
        # 过滤3.76的金币场加的比赛房间和新增加的金币房间
        self._filter_append_new_room(roominfos)

        msg = MsgPack()

        msg.setCmd('hall_info')
        msg.setResult('gameId', gameId)
        msg.setResult('userId', userId)
        msg.setResult('sessions', roominfos)
        router.sendToUser(msg, userId)

    def filterSegmentRoomUserCount(self, userId, gameId, roomUserCounts, rooms):
        try:
            # 过滤所有roominfos中的比赛，如果再counts中则替换为roominfos中的peopleNumber:
            for room in rooms:
                roomId = room.get('id')
                userCount = roomUserCounts.get(str(roomId)) or 0
                if userCount:
                    userCount = round(int(userCount) * 3 + int(random.randint(80, 100)))
                room['userCount'] = int(userCount)
                room['peopleNumber'] = int(userCount)
        except:
            ftlog.error('filterSegmentRoomUserCount',
                        'gameId=', gameId,
                        'userId=', userId)

    def filterWechatMatchRoomUserCount(self, userId, gameId, roomUserCounts, rooms):
        try:
            # 过滤所有roominfos中的比赛，如果再counts中则替换为roominfos中的peopleNumber:
            for room in rooms:
                roomId = room.get('id')
                peopleNumber = room.get('peopleNumber')
                userCount = roomUserCounts.get(str(roomId))
                if (peopleNumber is not None
                    and userCount is not None):
                    try:
                        userCount = roomUserCounts.get(str(roomId)) or 0
                        if userCount:
                            userCount = round(int(userCount) * 3 + int(random.randint(50, 80)))
                            room['userCount'] = int(userCount)
                            room['peopleNumber'] = int(userCount)
                    except:
                        pass
        except:
            ftlog.error('filterWechatMatchRoomUserCount',
                        'gameId=', gameId,
                        'userId=', userId)

    def filterRoomUserCounts(self, userId, gameId, roomUserCounts, roomInfos):
        try:
            # 过滤所有roominfos中的比赛，如果再counts中则替换为roominfos中的peopleNumber
            for session in roomInfos:
                for room in session.get('rooms', []):
                    roomId = room.get('id')
                    userCount = roomUserCounts.get(str(roomId), 0) * 3 + int(random.randint(1, 50)) if roomUserCounts.get(str(roomId), 0) else 0
                    room['userCount'] = int(userCount)
                    room['peopleNumber'] = int(userCount)
        except:
            ftlog.error('filterRoomUserCounts',
                        'gameId=', gameId,
                        'userId=', userId)

    def filterMixRoomUserCount(self, userId, gameId, roomUserCounts, roomInfos):
        try:
            # 如果房间类型是mix, 根据mixId 获取对应配置的配置比例 mixUserRate 以及 假数据 dummyUserCount 展示在线人数
            for session in roomInfos:
                if not session.get('match'):
                    for room in session.get('rooms', []):
                        roomId = room.get('id')
                        mixId = room.get('mixId')
                        roomConf = gdata.getRoomConfigure(roomId)
                        if room.get('isNotOpenTime'):
                            del room['isNotOpenTime']
                        if mixId:
                            userCount = roomUserCounts.get(str(roomId), 0) * 3
                            mixConf = roomConf.get('mixConf', [])
                            for conf in mixConf:
                                if conf.get('mixId') == mixId:
                                    try:
                                        if userCount:
                                            # 判断此房间当前时间是否开放
                                            if not dizhu_util.checkRoomOpenTime(conf, datetime.datetime.now().time()):
                                                room['isNotOpenTime'] = 1
                                                userCount = 0
                                            else:
                                                userCount = round(userCount * conf.get('mixUserRate', 1) + conf.get('dummyUserCount'))
                                        else:
                                            userCount = 0
                                        room['userCount'] = int(userCount)
                                        room['peopleNumber'] = int(userCount)
                                    except:
                                        pass
                        else:
                            # 判断此房间当前时间是否开放
                            if not dizhu_util.checkRoomOpenTime(roomConf, datetime.datetime.now().time()):
                                room['isNotOpenTime'] = 1
        except:
            ftlog.error('filterMixRoomUserCount',
                        'gameId=', gameId,
                        'userId=', userId)

    def filterMixMatchRoomUserCount(self, userId, gameId, roomUserCounts, roomInfos):
        try:
            # 如果房间类型是mix, 根据mixId 获取对应配置的配置比例 mixUserRate 以及 假数据 dummyUserCount 展示在线人数
            for session in roomInfos:
                for room in session.get('rooms', []):
                    roomId = room.get('id')
                    mixId = room.get('mixId')
                    if mixId:
                        userCount = roomUserCounts.get(str(roomId))
                        roomConf = gdata.getRoomConfigure(roomId)
                        matchConf = roomConf.get('matchConf', {})
                        if matchConf:
                            for conf in matchConf.get('feeRewardList', []):
                                if conf.get('mixId') == mixId:
                                    try:
                                        if userCount:
                                            userCount = round(userCount * conf.get('mixUserRate', 1) * 9 + int(conf.get('dummyUserCount')))
                                            userCount = max(userCount - random.randint(80, 88), 0)
                                        else:
                                            userCount = 0
                                        room['userCount'] = int(userCount)
                                        room['peopleNumber'] = int(userCount)
                                    except:
                                        pass
        except:
            ftlog.error('filterMixMatchRoomUserCount',
                        'gameId=', gameId,
                        'userId=', userId)

    @classmethod
    def _getQuickStartConf(cls, userId):
        # 获取快开配置
        winrate = gamedata.getGameAttrs(userId, DIZHU_GAMEID, ['winrate'], False)[0]
        winrate = strutil.loads(winrate, ignoreException=True, execptionValue={'pt': 0, 'wt': 0})
        playTimes = winrate.get('pt', 0)
        quickStart = configure.getGameJson(DIZHU_GAMEID, 'quickstart', {})
        abPlayCount = quickStart.get('abPlayCount', 0)
        abSwitch = quickStart.get('abSwitch', 0)
        newQuickStart = {
            'hallStartChip': quickStart.get('hallStartChip'),
            'hallStartPlayMode': quickStart.get('hallStartPlayMode'),
            'secondHallPlayMode': quickStart.get('secondHallPlayMode')
        }
        if abSwitch and playTimes < abPlayCount and userId % 2 != 0:
            newQuickStart['hallStartPlayMode'] = 'segment'
        return newQuickStart

    @markCmdActionMethod(cmd='hall', action='info', clientIdVer=3.76, scope='game')
    def doHallInfoV3_76(self, userId, gameId, clientId):
        if ftlog.is_debug():
            ftlog.debug('doHallInfoV3_76 userId=', userId,
                        'gameId=', gameId,
                        'clientId=', clientId)
        onlineInfos = getRoomOnLineUserCount(TGDizhu.gameId())
        roominfos = dizhuhallinfo.getWechatMatchRooms(gameId, userId, clientId)
        self.filterWechatMatchRoomUserCount(userId, gameId, onlineInfos[1], roominfos)
        self.filterMixRoomUserCount(userId, gameId, onlineInfos[1], roominfos)

        segmentRoomInfos = dizhuhallinfo.getSegmentRooms(gameId, userId, clientId)
        self.filterSegmentRoomUserCount(userId, gameId, onlineInfos[1], segmentRoomInfos)

        msg = MsgPack()
        msg.setCmd('hall_info')
        msg.setResult('gameId', gameId)
        msg.setResult('userId', userId)
        # msg.setResult('rooms', roominfos)

        onlineInfos2 = getRoomOnLineUserCount(TGDizhu.gameId())
        roominfos2 = dizhuhallinfo.getSessions(gameId, userId, clientId)
        self.filterRoomUserCounts(userId, gameId, onlineInfos2[1], roominfos2)
        self.filterMixMatchRoomUserCount(userId, gameId, onlineInfos2[1], roominfos2)
        self.filterMixRoomUserCount(userId, gameId, onlineInfos2[1], roominfos2)
        msg.setResult('sessions', roominfos2)
        # msg.setResult('segmentRoomInfo', segmentRoomInfos)

        # 斗地主插件的开关配置
        msg.setResult('switchConf', self._get_switch_config(clientId))

        # 微信推广二维码
        msg.setResult('wxTuiguang', self._get_wxTuiguang_config())

        # 获取公告
        msg.setResult('gonggao', self._get_gonggao_info(userId, clientId))

        # 是否展示banner
        msg.setResult('showBanner', self._showBanner(userId, gameId, clientId))

        # 分流用户快开icon展示
        msg.setResult('quickStart', self._getQuickStartConf(userId))

        # 闯关赛信息
        updated = EndgameHelper.updateUserIssueRoundData(userId)
        udata = EndgameHelper.getUserCurrentRoundData(userId)
        config = EndgameHelper.getCurrentIssueConfig()
        msg.setResult('endgameInfo', {
            'roundNum': min(udata.roundNum, len(config.roundCards) if config else 1),
            'totalRoundCount': len(config.roundCards) if config else 0,
            'challengeCount': udata.playCount,
            'updated': updated
        })
        router.sendToUser(msg, userId)

    # 根据配置判断是否给用户展示banner
    def _showBanner(self, userId, gameId, clientId):
        from hall.entity.hallusercond import UserConditionRegister
        conf = configure.getGameJson(gameId, 'ad.banner', {})
        conD = conf.get('condition')
        if not conD:
            return {'isShow': False, 'freshSeconds': conf.get('freshSeconds', 0)}
        cond = UserConditionRegister.decodeFromDict(conD)
        retCheck = cond.check(DIZHU_GAMEID, userId, clientId, pktimestamp.getCurrentTimestamp())
        if retCheck:
            return {'isShow': True, 'freshSeconds': conf.get('freshSeconds', 0)}
        return {'isShow': False, 'freshSeconds': conf.get('freshSeconds', 0)}

    # 获取经过过滤的房间信息
    def _get_roominfo_by_filter(self, gameId, clientId):
        srcRoomInfos = hallconf.getHallSessionInfo(gameId, clientId)
        roominfos = strutil.cloneData(srcRoomInfos)

        try:
            # 过滤比赛
            if ftlog.is_debug():
                roomses = [roomInfo.get('rooms') for roomInfo in roominfos]
                ftlog.debug('>>> _get_roominfo_by_filter gameId=', gameId,
                            'clientId=', clientId,
                            'roomIds=', [[room.get('id') for room in rooms] for rooms in roomses])
            self._filter_match_info(roominfos)
            if ftlog.is_debug():
                roomses = [roomInfo.get('rooms') for roomInfo in roominfos]
                ftlog.debug('<<< _get_roominfo_by_filter gameId=', gameId,
                            'clientId=', clientId,
                            'roomIds=', [[room.get('id') for room in rooms] for rooms in roomses])
        except:
            ftlog.exception()

        return roominfos

    # 过滤比赛:1,下线过期、未到上架时间的比赛；2，设置下一场比赛开始时间
    def _filter_match_info(self, roominfos):
        for roomInfo in roominfos:
            if 'match' not in roomInfo.keys() or not roomInfo['match']:
                continue

            filterRooms = []
            for room in roomInfo['rooms']:
                if self._is_outofdate_match(room) or self._is_not_show_match(room):
                    ftlog.debug('_filter_match_info roomId=', room.get('id'),
                                '_is_outofdate_match or _is_not_show_match')
                else:
                    # 设置下一场开始时间
                    nextTime = self._get_next_match_time(room, isFromCoinRoom=False)
                    if nextTime:
                        room['condition'] = nextTime
                    filterRooms.append(room)
            roomInfo['rooms'] = filterRooms
            # 排序比赛
            self._sort_match_room_by_config(roomInfo['rooms'])

    # 根据配置排序比赛房间
    def _sort_match_room_by_config(self, rooms):
        matchRank = self._get_curtime_match_rank_config()
        ftlog.debug('matchRank = ', matchRank)
        if not matchRank:
            return
        # 进行排序
        dstPos = 0
        try:
            for ele in matchRank:
                initPos = self._find_init_pos(rooms, ele)
                if initPos < 0:
                    continue
                self._put_room_to_index(rooms, initPos, dstPos)
                dstPos += 1
        except:
            ftlog.exception()

    # 查找一个房间的原始位置
    def _find_init_pos(self, rooms, roomId):
        for index in range(len(rooms)):
            if rooms[index].get('id', '') == roomId:
                return index
        return -1

    # 交换列表的两个位置的值，从srcIndex放到dstIndex
    def _put_room_to_index(self, rooms, srcIndex, dstIndex):
        temp = rooms[dstIndex]
        rooms[dstIndex] = rooms[srcIndex]
        rooms[srcIndex] = temp

    # 获取此时间段的比赛顺序排序
    def _get_curtime_match_rank_config(self):
        try:
            matchRankTimeConfig = dizhuconf.getPublic().get('matchRankTimeConfig', '')
            if not matchRankTimeConfig:
                return None

            matchRankConfig = dizhuconf.getPublic().get('matchRankConfig', '')
            if not matchRankConfig:
                return None

            if len(matchRankTimeConfig) <= 0 or len(matchRankConfig) <= 0:
                return None

            curTimestamp = pktimestamp.getCurrentTimestamp()
            for index in range(len(matchRankTimeConfig)):
                for ele in matchRankTimeConfig[index]:
                    if self._is_curtime_in_scope(curTimestamp, ele):
                        if index < len(matchRankConfig):
                            return matchRankConfig[index]
                        else:
                            return None
        except:
            ftlog.exception()
            ftlog.debug('Got match rank exception')

        return None

    # 检测一个比赛房间是否可以上架显示
    def _is_not_show_match(self, room):
        try:
            roomId = int(room['id'])
            roomConf = gdata.getRoomConfigure(roomId)

            if not roomConf or not roomConf['ismatch']:
                return False

            matchConf = roomConf.get('matchConf', {})
            if not matchConf:
                return False

            showTime = matchConf.get('showTime', '')
            if not showTime:
                # 没有配置认为永远显示
                return False

            curTimestamp = pktimestamp.getCurrentTimestamp()
            for ele in showTime:
                if self._is_curtime_in_scope(curTimestamp, ele):
                    return False

            return True
        except:
            ftlog.exception()
            ftlog.debug('showTime config got exception')
            return False

    def _is_curtime_in_scope(self, curTimestamp, timeScope):
        showTimeStartStamp = pktimestamp.datetime2Timestamp(pktimestamp.parseTimeSecond(timeScope.get('start', '2998-01-01 12:00:00')))  # 填充配置的时间字符串
        showTimeEndStamp = pktimestamp.datetime2Timestamp(pktimestamp.parseTimeSecond(timeScope.get('end', '2999-01-01 12:00:00')))  # 填充配置的时间字符串
        return curTimestamp >= showTimeStartStamp and curTimestamp < showTimeEndStamp

    # 检测一个房间是否是已结束的比赛房间
    def _is_outofdate_match(self, room):
        roomId = int(room['id'])
        # 查询房间信息
        roomConf = gdata.getRoomConfigure(roomId)

        if not roomConf or not roomConf['ismatch']:
            ftlog.debug('roomId, no ismatch= ', roomId)
            return False

        # 判断是否过期
        matchConf = roomConf.get('matchConf', {})
        matchType = matchConf.get('start', {}).get('type', 0)
        if matchType == 1:
            # 人满赛没有下线时间
            return False

        startconf = matchConf.get('start', {})
        if not startconf:
            # Arena赛制没有配置start字段
            return False

        startConf = StartConfig.parse(startconf)
        nextTime = startConf.calcNextStartTime()
        ftlog.debug('roomId, and next seconds = ', roomId, nextTime)
        if nextTime == None:
            # 没有下一场
            ftlog.debug('ddz hall info remove room = ', room)
            return True
        return False

    # 检测修改新增加的星耀大师场、金币场中的比赛场
    def _filter_append_new_room(self, roominfos):
        for info in roominfos:
            if 'match' in info.keys() and info['match']:
                # 比赛场已过滤过了
                continue

            filterRooms = []
            for room in info['rooms']:
                roomAttri = self._get_room_attri(room)
                if roomAttri['isMatch']:
                    ftlog.debug('adjust coin play mode remove refactor match room, roomId = ', room['id'], room['name'])
                    continue
                if roomAttri['isAppendCoinRoom']:
                    ftlog.debug('adjust coin play mode remove refactor append coin room, roomId = ', room['id'])
                    continue
                filterRooms.append(room)
            info['rooms'] = filterRooms

    # 修改金币场的定时赛的房间信息（room_items）项中的[showInfo][extendInfo]为下一场的开赛时间
    def _adjust_ontime_match_info(self, roominfos):
        for info in roominfos:
            if info.has_key('match') and info['match']:
                # 比赛场的信息没有变化
                continue
            rooms = info['rooms']
            curTime = datetime.datetime.now()
            curTime = datetime.time(curTime.hour, curTime.minute)

            for room in rooms:
                roomAttri = self._get_room_attri(room)
                if not roomAttri['isMatch'] or not room.has_key('showInfo'):
                    continue
                # 增加金币场中的比赛场的房间属性
                room['isMatch'] = True
                nextTime = self._get_next_match_time(room,
                                                     isFromCoinRoom=True)
                if not nextTime:
                    continue
                room['showInfo']['extendInfo'] = nextTime
                ftlog.debug('next match time = ', room['showInfo']['extendInfo'])

    # 获取一个比赛下一场开始的时间：今天+hh:mm／明天+hh:mm／日期+hh:mm
    def _get_next_match_time(self, room, isFromCoinRoom):
        roomId = room['id']
        roomConf = gdata.getRoomConfigure(roomId)
        if not roomConf:
            return None
        matchConf = roomConf.get('matchConf', {})
        matchType = matchConf.get('start', {}).get('type', 0)
        if matchType == 1:
            # 人满赛没有下一场开始时间
            return None

        startconf = matchConf.get('start', {})
        if not startconf:
            return None

        startConf = StartConfig.parse(startconf)
        matchTimeList = startConf._cron.getTimeList()
        matchDayList = startConf._cron.getDaysList()

        if len(matchTimeList) <= 0 or len(matchDayList) <= 0:
            return None

        nextMatchTimeFromat = dizhuconf.getPublic().get('nextmatchtime', '')
        if not nextMatchTimeFromat:
            ftlog.debug('get nextMatchTimeFromat None, check config !!')
            return None

        # 将时间按升序排序
        matchTimeList.sort()
        matchDayList.sort()

        ftlog.debug('match time list, roomId ', matchTimeList, roomId)
        ftlog.debug('match day list, roomId', matchDayList, roomId)

        curTime = datetime.datetime.now()
        curTime = datetime.time(curTime.hour, curTime.minute)

        # 获取下一场的比赛时间信息，取最近的一个大于当前时间戳的组合
        dstMatchDay = None
        dstMatchTime = None

        for matchDay in matchDayList:
            for matchTime in matchTimeList:
                combineDateTime = datetime.datetime.combine(matchDay, matchTime)
                matchTimeStamp = pktimestamp.datetime2Timestamp(combineDateTime)
                if matchTimeStamp >= pktimestamp.getCurrentTimestamp():
                    dstMatchDay = matchDay
                    dstMatchTime = matchTime
                    break
            if dstMatchDay and dstMatchTime:
                break

        ftlog.debug('find next matchInfo dstMatchDay = ', dstMatchDay, ' dstMatchTime = ', dstMatchTime)

        if not dstMatchDay or not dstMatchTime:
            return None

        timeFormat = '%H:%M'
        ftlog.debug('_get_next_match_time test roomId = ', roomId, 'isFromCoinRoom = ', isFromCoinRoom)

        if isFromCoinRoom and not nextMatchTimeFromat.get('coinRoomShowDayInfo', 0):
            return dstMatchTime.strftime(timeFormat)

        # 在此获取日期的显示信息了:今天明天，后天还是显示日期
        nextDayInfo = self._get_next_match_dayinfo(dstMatchDay, nextMatchTimeFromat)
        return nextDayInfo + dstMatchTime.strftime(timeFormat)

    # 获取下一场比赛日期信息
    def _get_next_match_dayinfo(self, dstMatchDay, nextMatchTimeFromat):

        dstDay = datetime.date(dstMatchDay.year, dstMatchDay.month, dstMatchDay.day)
        curDay = datetime.date.today()

        if (dstDay - curDay).days <= nextMatchTimeFromat.get('dayInfoCnt', 1):
            return nextMatchTimeFromat.get('dayInfo' + str((dstDay - curDay).days), '')

        other = nextMatchTimeFromat.get('other', '${month}-${day}')
        other = strutil.replaceParams(other, {'month': str(dstDay.month), 'day': str(dstDay.day)})
        return other

    # 检测一个房间的信息，返回一个字典：{'isMatch':False, 'isAppendCoinRoom':True},代表是否是金币场中的比赛场、是否是新增加的金币场房间
    def _get_room_attri(self, room):
        res = {'isMatch': False, 'isAppendCoinRoom': False}
        try:
            roomId = int(room['id'])
            roomConf = gdata.getRoomConfigure(roomId)
            if not roomConf:
                ftlog.debug('''Get room's config is None roomId = ''', roomId)
                return res

            if 'ismatch' in roomConf.keys() and roomConf['ismatch']:
                res['isMatch'] = True
                return res

            if 'realRoomLevel' in roomConf.keys():
                res['isAppendCoinRoom'] = True
                return res
        except:
            ftlog.exception()
        return res

    # @markCmdActionMethod(cmd='game', action="quick_start", clientIdVer=0, scope='game', lockParamName="")
    # def doGameQuickStart(self, userId, gameId, clientId, roomId0, tableId0, playMode, sessionIndex, mixId='', rankId='-1'):
    #     '''
    #     TCP 发送的至UTIL服务的quick_start暂时不能用lock userid的方式,
    #     因为,消息流 CO->UT->GR->GT->UT会死锁
    #     '''
    #     msg = runcmd.getMsgPack()
    #     msg.setParam('mixId', mixId)
    #     # 积分榜0：大积分场；1：小积分场
    #     msg.setParam('rankId', rankId)
    #     ftlog.debug('doGameQuickStart', userId, gameId, clientId, roomId0, tableId0, playMode, sessionIndex, mixId, type(mixId), caller=self)
    #     if not playMode and roomId0 <= 0 and tableId0 <= 0:
    #         try:
    #             # 前端对于sessionIndex是写死的, 不会更具hall_info中的顺序改变而改变
    #             if sessionIndex == 0:
    #                 playMode = dizhuconf.PLAYMODE_123
    #             elif sessionIndex == 1:
    #                 playMode = dizhuconf.PLAYMODE_HAPPY
    #             elif sessionIndex == 3:
    #                 playMode = dizhuconf.PLAYMODE_LAIZI
    #             elif sessionIndex == 4:
    #                 playMode = dizhuconf.PLAYMODE_ERDOU
    #             elif sessionIndex == 5:  # 从比赛分类页来的，快开直接进比赛
    #                 playMode = dizhuconf.PLAYMODE_STRAIGHT_MATCH  # 'straightMatch'
    #             else:
    #                 playMode = dizhuconf.PLAYMODE_DEFAULT
    #             msg.setParam('playMode', playMode)  # 透传playMode, 以便发送高倍房引导弹窗
    #         except:
    #             ftlog.error('doGameQuickStart', msg)
    #         ftlog.debug('doGameQuickStart sessionIndex=', sessionIndex, 'playMode=', playMode)
    #     DizhuQuickStart.onCmdQuickStart(msg, userId, gameId, roomId0, tableId0, playMode, clientId)
    #     if router.isQuery():
    #         mo = runcmd.newOkMsgPack(1)
    #         router.responseQurery(mo, '', str(userId))

    @markCmdActionMethod(cmd='game', action="quick_start", clientIdVer=0, scope='game', lockParamName="")
    def doGameQuickStartWx(self, userId, gameId, clientId, segment, roomId0, tableId0, playMode, mixId=''):
        '''
        TCP 发送的至UTIL服务的quick_start暂时不能用lock userid的方式,
        因为,消息流 CO->UT->GR->GT->UT会死锁
        '''
        msg = runcmd.getMsgPack()
        msg.setParam('mixId', mixId)
        DizhuQuickStartWx.onCmdQuickStart(msg, userId, gameId, roomId0, tableId0, playMode, clientId, segment)
        if router.isQuery():
            mo = runcmd.newOkMsgPack(1)
            router.responseQurery(mo, '', str(userId))

    def _routerToCtlRoomId(self, bigRoomId, userId, tag):
        msg = runcmd.getMsgPack()
        ftlog.debug('msg=', msg, caller=self)

        gameId = strutil.getGameIdFromBigRoomId(bigRoomId)
        minfo = match_remote.loadUserMatchInfo(gameId, userId, bigRoomId)
        ctrRoomId = 0
        if minfo:
            ctrRoomId = minfo.ctrlRoomId
            if ftlog.is_debug():
                ftlog.debug(tag, 'find room location by match info bigRoomId=', bigRoomId,
                            'userId=', userId,
                            'ctrRoomId=', ctrRoomId,
                            'info=', minfo.__dict__)
        ctrls = gdata.bigRoomidsMap()[bigRoomId]
        if ctrRoomId not in ctrls:
            ctrRoomId = ctrls[userId % len(ctrls)]
            if ftlog.is_debug():
                ftlog.debug(tag, 'find room location by match mod bigRoomId=', bigRoomId,
                            'userId=', userId,
                            'ctrRoomId=', ctrRoomId)

        msg.setParam('roomId', ctrRoomId)
        router.sendRoomServer(msg, ctrRoomId)

    @markCmdActionMethod(cmd='room', action="signin", clientIdVer=0, scope="game")
    def doRoomSigIn(self, bigRoomId, userId):
        '''
        多进程分组大比赛，消息需要先分发到UT，在UT中取得该用户所在的比赛进程再进行二次分发
        '''
        return self._routerToCtlRoomId(bigRoomId, userId, 'doRoomSigIn')

    @markCmdActionMethod(cmd='room', action="signout", clientIdVer=0, scope="game")
    def doRoomSigOut(self, bigRoomId, userId):
        '''
        多进程分组大比赛，消息需要先分发到UT，在UT中取得该用户所在的比赛进程再进行二次分发
        '''
        return self._routerToCtlRoomId(bigRoomId, userId, 'doRoomSigOut')

    @markCmdActionMethod(cmd='room', action="update", clientIdVer=0, scope="game")
    def doRoomUpdate(self, bigRoomId, userId):
        '''
        多进程分组大比赛，消息需要先分发到UT，在UT中取得该用户所在的比赛进程再进行二次分发
        '''
        return self._routerToCtlRoomId(bigRoomId, userId, 'doRoomUpdate')

    @markCmdActionMethod(cmd='room', action="giveup", clientIdVer=0, scope="game")
    def doRoomGiveup(self, bigRoomId, userId):
        '''
        多进程分组大比赛，消息需要先分发到UT，在UT中取得该用户所在的比赛进程再进行二次分发
        '''
        return self._routerToCtlRoomId(bigRoomId, userId, 'doRoomGiveup')

    @markCmdActionMethod(cmd='room', action="enter", clientIdVer=0, scope="game")
    def doRoomEnter(self, bigRoomId, userId):
        '''
        多进程分组大比赛，消息需要先分发到UT，在UT中取得该用户所在的比赛进程再进行二次分发
        '''
        return self._routerToCtlRoomId(bigRoomId, userId, 'doRoomEnter')

    @markCmdActionMethod(cmd='room', action="leave", clientIdVer=0, scope="game")
    def doRoomLeave(self, bigRoomId, userId):
        '''
        多进程分组大比赛，消息需要先分发到UT，在UT中取得该用户所在的比赛进程再进行二次分发
        '''
        return self._routerToCtlRoomId(bigRoomId, userId, 'doRoomLeave')

    @markCmdActionMethod(cmd='game', action="enter", clientIdVer=0, scope='game')
    def doGameEnter(self, userId, gameId, clientId, version):
        ftlog.debug('ddz.GameTcpHandler.doGameEnter',
                    'userId=', userId,
                    'gameId=', gameId,
                    'clientId=', clientId,
                    'version=', version)
        ## bind_game
        ## 记录地主插件的版本号
        SessionDizhuVersion.setVersionNumber(userId, version)

        isdayfirst, iscreate = halluser.loginGame(userId, gameId, clientId)
        self.helper.sendUserInfoResponse(userId, gameId, clientId, '', 0, 1)
        self.helper.sendTodoTaskResponse(userId, gameId, clientId, isdayfirst)
        # BI日志统计
        bireport.userGameEnter(gameId, userId, clientId)
        bireport.reportGameEvent('BIND_GAME',
                                 userId, gameId, 0, 0, 0, 0, 0, 0, [], clientId, iscreate)
        evt = OnLineGameChangedEvent(userId, gameId, 1, clientId)
        TGHall.getEventBus().publishEvent(evt)

    ### WarmUp System Handler

    @markCmdActionMethod(cmd='game', action="warmup:luckydraw", clientIdVer=0, scope='game', lockParamName="")
    def doWarmUpLuckyDraw(self, userId, gameId, roomId0):
        response = WarmUpSystem.onUserLuckyDraw(userId, roomId0)
        mo = self.buidWarmUpResponseMsg(response, gameId, userId, 'warmup:luckydraw')
        router.sendToUser(mo, userId)
        ftlog.debug("doWarmUpLuckyDraw", "userId=", userId, "mo=", mo)

    @markCmdActionMethod(cmd='game', action="warmup:getmsg", clientIdVer=0, scope='game', lockParamName="")
    def doWarmUpGetMessages(self, userId, gameId, number):
        ftlog.debug("doWarmUpGetMessages", "userId=", userId, "number=", number)
        response = WarmUpSystem.onGetRecordMessage(userId, number)
        mo = self.buidWarmUpResponseMsg(response, gameId, userId, 'warmup:getmsg')
        router.sendToUser(mo, userId)
        ftlog.debug("doWarmUpGetMessages", "userId=", userId, "mo=", mo)

    @classmethod
    def buidWarmUpResponseMsg(cls, result, gameId, userId, action):
        mo = MsgPack()
        mo.setCmd('game')
        mo.setResult("gameId", gameId)
        mo.setResult("userId", userId)
        mo.setResult("action", action)
        if not result:
            result = {"errorInfo": "unknown action", "errorCode": 1}
        for key in result:
            mo.setResult(key, result[key])
        return mo

    ### Match History Handler

    @classmethod
    def buildMatchHistoryResponseMsg(cls, result, gameId, userId, roomId, action):
        mo = MsgPack()
        mo.setCmd('game')
        mo.setResult("gameId", gameId)
        mo.setResult("userId", userId)
        mo.setResult("action", action)
        mo.setResult("roomId", roomId)
        mo.setResult("histories", result)
        return mo

    @markCmdActionMethod(cmd='hall', action='signs', clientIdVer=0, scope='game')
    def doHallSigns(self, gameId, userId):
        signs = {}
        roomInfos = roominfo.loadAllRoomInfo(gameId)
        for roomId, _ in roomInfos.iteritems():
            issignin = daobase.executeTableCmd(roomId, 0, 'SISMEMBER', 'signs:' + str(roomId), userId)
            if issignin :
                bigRoomId = gdata.getBigRoomId(roomId)
                if bigRoomId:
                    signs[bigRoomId] = 1
                
        msgRes = MsgPack()
        msgRes.setCmd('m_signs')
        msgRes.setResult('gameId', gameId)
        msgRes.setResult('userId', userId)
        msgRes.setResult('signs', signs)
        msgRes.setResult('isAll', 1)
        router.sendToUser(msgRes, userId)

    ### Others

    @classmethod
    def buidResponseMsg(cls, result, gameId, userId, action):
        mo = MsgPack()
        mo.setCmd('game')
        mo.setResult("gameId", gameId)
        mo.setResult("userId", userId)
        mo.setResult("action", action)
        if not result:
            result = {"errorInfo": "unknown action", "errorCode": 1}
        for key in result:
            mo.setResult(key, result[key])
        return mo

    @markCmdActionMethod(cmd='game', action="table.playerinfo", clientIdVer=0, scope='game', lockParamName="")
    def doGameGetChip(self, userId, gameId):
        ftlog.debug("doGameGetChip", "userId=", userId)
        response = {'chip': UserInfo.getChip(userId)}
        mo = self.buidResponseMsg(response, gameId, userId, 'table.playerinfo')
        router.sendToUser(mo, userId)
        ftlog.debug("doGameGetChip", "userId=", userId, "mo=", mo)

    ### tbox 提交任务：获取奖励

    @markCmdActionMethod(cmd='dizhu', action='tbox_getReward', clientIdVer=0, scope='game', lockParamName='')
    def doTboxGetReward(self, userId, gameId):
        ftlog.debug('doTboxGetReward', 'userId=', userId)
        mo = self.buidTboxReward(userId, gameId, 'tbox_getReward')
        ftlog.debug("doTboxGetReward", "userId=", userId, "mo=", mo)
        router.sendToUser(mo, userId)

    def buidTboxReward(self, userId, gameId, action):
        mo = MsgPack()
        mo.setCmd('dizhu')
        mo.setResult("gameId", gameId)
        mo.setResult("userId", userId)
        mo.setResult("action", action)
        datas = treasurebox.doTreasureBox1(userId)
        ftlog.debug('buidTboxReward datas=', datas)
        mo.updateResult(datas)
        return mo

    @markCmdActionMethod(cmd='dizhu', action='get_two_vs_one_rooms', clientIdVer=0, scope='game', lockParamName='')
    def doGetTwoVsOneHallInfo(self, userId, gameId, clientId):
        mo = MsgPack()
        mo.setCmd('dizhu')
        mo.setResult('gameId', gameId)
        mo.setResult('userId', userId)
        mo.setResult('action', 'get_two_vs_one_rooms')
        try:
            # session = dizhuconf.getDdzSessionInfo(gameId, clientId)
            roominfos = dizhuhallinfo.getTvoSessions(gameId, userId, clientId)
            mo.setResult('session', roominfos)
            # 获取斗地主的装饰信息
            mo.setResult('decoration_info', self._get_decoration_info())
        except:
            ftlog.debug("doGetTwoVsOneHallInfo.onHandle",
                        "userId=", userId)
            ftlog.exception()
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd='dizhu', action='get_two_vs_one_ads', clientIdVer=0, scope='game', lockParamName='')
    def doGetTwoVsOneAds(self, userId, gameId, clientId):
        mo = MsgPack()
        mo.setCmd('dizhu')
        mo.setResult('gameId', gameId)
        mo.setResult('userId', userId)
        mo.setResult('action', 'get_two_vs_one_ads')
        try:
            ads = dizhutvoads.getAds(gameId, userId, clientId)
            mo.setResult('ads', ads)
        except:
            ftlog.debug('doGetTwoVsOneAds except userId = ', userId)
            ftlog.exception()
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd='dizhu', action='lucky_packs', clientIdVer=0, scope='game', lockParamName='')
    def doLuckyPacks(self, userId, gameId, clientId, roomId):
        try:
            luckBuyOrLessBuyChip = makeTodoTaskLuckBuy(gameId, userId, clientId, roomId)
            if not luckBuyOrLessBuyChip:
                luckBuyOrLessBuyChip = makeTodoTaskLessbuyChip(gameId, userId, clientId, roomId)

            if not luckBuyOrLessBuyChip:
                return

            todotasks = [luckBuyOrLessBuyChip]
            TodoTaskHelper.sendTodoTask(gameId, userId, todotasks)
        except:
            ftlog.debug('doLuckyPacks except userId = ', userId)
            ftlog.exception()

    @markCmdActionMethod(cmd='dizhu', action='match_calendar', clientIdVer=0, scope='game', lockParamName='')
    def doCalendar(self, userId, gameId, clientId):
        try:
            mo = MsgPack()
            mo.setCmd('dizhu')
            mo.setResult('gameId', gameId)
            mo.setResult('userId', userId)
            mo.setResult('action', 'match_calendar')
            calendarConf = configure.getGameJson(gameId, 'match.calendar', {})
            shareInfo = calendarConf.get('shareInfo', {})

            # 获取二维码
            templateName = configure.getVcTemplate('match.calendar', clientId, gameId)
            shareConf = configure.getGameJson(gameId, 'match.calendar', {}, configure.CLIENT_ID_TEMPLATE)
            templateMap = shareConf.get('templates', {})
            retConf = templateMap.get(templateName, {})
            shareInfo['erweima'] = retConf.get('erweima', '')

            mo.setResult('shareInfo', shareInfo)
            calendarInfo = self.buildCalendarInfo(calendarConf)
            if not calendarInfo:
                return
            mo.setResult('calendarInfo', calendarInfo)
            router.sendToUser(mo, userId)

            # 记录bi日志
            ftlog.info('GameTcpHandler.doCalendar userId=', userId,
                       'gameId=', gameId,
                       'clientId=', clientId)
        except:
            ftlog.debug('doCalendar except userId = ', userId, 'clientId=', clientId)
            ftlog.exception()

    @markCmdActionMethod(cmd='dizhu', action='zhaociji', clientIdVer=0, scope='game', lockParamName='')
    def zhaociji(self, userId, gameId, clientId):
        try:
            mo = MsgPack()
            mo.setCmd('dizhu')
            mo.setResult('gameId', gameId)
            mo.setResult('userId', userId)
            mo.setResult('action', 'zhaociji')
            mo.setResult('gameIds', self.getZhaocijiGames(userId, gameId, clientId))
            router.sendToUser(mo, userId)
        except:
            ftlog.debug('zhaociji except userId = ', userId, 'clientId=', clientId)
            ftlog.exception()

    @classmethod
    def getZhaocijiGames(cls, userId, gameId, clientId):
        from poker.entity.dao import userchip
        userChip = userchip.getChip(userId)
        d = configure.getGameJson(gameId, 'zhaociji', {}, 0)

        showCond = d.get('showCond', {})
        if showCond:
            try:
                from hall.entity.hallusercond import UserConditionRegister
                displayCond = UserConditionRegister.decodeFromDict(showCond)
                ret = displayCond.check(DIZHU_GAMEID, userId, clientId, pktimestamp.getCurrentTimestamp())
                if ret:
                    for game in d.get('games', []):
                        vipLimit = game.get('vipExp', 0)
                        if vipLimit:
                            from hall.entity import hallvip
                            vipExp = hallvip.userVipSystem.getVipInfo(userId).get('exp', 0)
                            if (vipLimit[0] == -1 or vipExp >= vipLimit[0]) and (vipLimit[1] == -1 or vipExp <= vipLimit[1]):
                                return game['gameids']
                        else:
                            chip = game.get('chip', 0)
                            if (chip[0] == -1 or userChip >= chip[0]) and (chip[1] == -1 or userChip <= chip[1]):
                                return game['gameids']
            except Exception, e:
                ftlog.error('getZhaocijiGames',
                            'userId=', userId,
                            'clientId=', clientId,
                            'userChip=', userChip,
                            'zhaocijiConf=', d,
                            'err=', e.message)
        return []

    @classmethod
    def buildCalendarInfo(cls, calendarConf):
        if not calendarConf or calendarConf.get('closed', 0) == 1:
            return
        calendar = calendarConf.get('calendar', [])
        # 获取当前星期，
        weekNum = datetime.datetime.now().weekday() + 1

        currentCalendar = [(index, matchList) for index, matchList in enumerate(calendar) if matchList.get('weekNum') == weekNum]
        if not currentCalendar:
            return
        index, matchList = currentCalendar[0]

        allMatches = collections.deque(calendar)
        allMatches.rotate(index * -1)

        currentTime = datetime.datetime.now()
        # 获取date列表
        dates = []
        for index, m in enumerate(allMatches):
            if index == 0:
                dates.append({
                    'date': '今日大奖',
                    'img': m.get('img'),
                    'shareImgs': m.get('shareImgs')
                })
            elif index == 1:
                dates.append({
                    'date': '明日大奖',
                    'img': m.get('img'),
                    'shareImgs': m.get('shareImgs')
                })
            else:
                nDate = currentTime + datetime.timedelta(days=index)
                dates.append({
                    'date': '%s月%s日' % (nDate.month, nDate.day),
                    'img': m.get('img'),
                    'shareImgs': m.get('shareImgs')
                })

        # 获取当日比赛
        nowMatches = []
        for match in matchList.get('matches', []):
            # 计算进度
            total = match.get('total')
            showTime = match.get('time')
            startEndTime = showTime.split('~')
            startTime = None
            endTime = None
            if len(startEndTime) == 2:
                startTime = datetime.datetime.combine(currentTime.date(), datetime.datetime.strptime(startEndTime[0], '%H:%M').time())
                endTime = datetime.datetime.combine(currentTime.date(), datetime.datetime.strptime(startEndTime[1], '%H:%M').time())
            else:
                startTime = datetime.datetime.combine(currentTime.date(), datetime.datetime.strptime(startEndTime[0], '%H:%M').time())

            if total == 1:
                progress = 1 if currentTime.time() > startTime.time() else 0
            else:
                totalMinutes = (endTime - startTime).seconds / 60
                if currentTime <= startTime:
                    progress = 0
                elif currentTime >= endTime:
                    progress = match.get('total')
                else:
                    progress = min(int(((currentTime - startTime).seconds / 60) * 1.0 / totalMinutes * match.get('total') + 1), match.get('total'))
            nowMatches.append(
                {
                    'id': match.get('id'),
                    'name': match.get('name'),
                    'rewardName': match.get('rewardName'),
                    'time': match.get('time'),
                    'img': match.get('img'),
                    'shareImgs': match.get('shareImgs', []),
                    'shareFlag': match.get('shareFlag', 0),
                    'timeList': match.get('timeList', []),
                    'total': match.get('total'),
                    'progress': progress,
                    'finished': 1 if progress / match.get('total') == 1 else 0
                }
            )

        # 对matches进行排序
        nowMatches.sort(key=lambda x: x.get('finished'))
        return {
            'matches': nowMatches,
            'dates': dates,
            'money': matchList.get('money'),
            'moneyWeb': matchList.get('moneyWeb'),
            'shareImgs': matchList.get('shareImgs')
        }

    @markCmdActionMethod(cmd='dizhu', action="newer_task", clientIdVer=0, scope='game', lockParamName="")
    def doNewerTaskGetTasks(self, userId, clientId):
        '''
        二级大厅返回新手任务信息
        :param userId:
        :param clientId:
        :return: {'newertask': xxx}
        '''
        mo = MsgPack()
        mo.setCmd('dizhu')
        mo.setResult('action', 'newer_task')
        mo.setResult('userId', userId)

        from dizhu.servers.util.rpc import task_remote
        status = task_remote.getNewbieTaskInfo(DIZHU_GAMEID, userId)  # getNewbieTaskInfo
        if status:
            mo.setResult('newertask', status)
        else:
            mo.setResult('error', 'no NewerTask')

        router.sendToUser(mo, userId)

    @classmethod
    def _doMatchLotteryHandler(cls, userId, matchId, rank):
        bigMatchId = gdata.getBigRoomId(matchId)

        from dizhu.games.matchutil import MatchLottery
        match_lottery = MatchLottery()
        item, items = match_lottery.chooseReward(userId, bigMatchId, rank)

        mo = MsgPack()
        mo.setCmd('dizhu')
        mo.setResult('action', 'match_lottery')
        mo.setResult('userId', userId)
        mo.setResult('item', item)
        mo.setResult('items', items)

        if ftlog.is_debug():
            ftlog.debug('_doMatchLotteryHandler userId=', userId, 'bigMatchId=', bigMatchId, 'rank=', rank, 'mo=', mo)
        return mo

    @markCmdActionMethod(cmd='dizhu', action="match_lottery", clientIdVer=0, scope='game', lockParamName="")
    def doMatchLotteryHandler(self, userId, matchId, rank):
        '''
        比赛结束抽奖协议
        :param userId:
        :param matchId:
        :param rank:
        :return:
        '''
        mo = self._doMatchLotteryHandler(userId, matchId, rank)
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd='dizhu', action="get_led_text", clientIdVer=0, scope='game', lockParamName="")
    def doGetLedTextHandler(self, userId):
        mo = MsgPack()
        mo.setCmd('dizhu')
        mo.setResult('action', 'get_led_text')
        mo.setResult('userId', userId)

        from dizhu.entity.led_util import LedUtil
        text = LedUtil.getLedText()
        mo.setResult('led_text', text if text else u"还没有LED记录哦！")

        router.sendToUser(mo, userId)
        if ftlog.is_debug():
            ftlog.debug('doMatchLotteryHandler userId=', userId, 'mo=', mo)
        return mo

    @markCmdActionMethod(cmd='dizhu', action="get_match_rules", clientIdVer=0, scope='game', lockParamName="")
    def doGetMatchRulesHandler(self, userId, roomId):
        '''
        比赛详情界面，获取比赛描述的接口
        :param userId:
        :param roomId:
        :return:
        '''
        mo = MsgPack()
        mo.setCmd('dizhu')
        mo.setResult('action', 'get_match_rules')
        mo.setResult('userId', userId)

        matchConf = configure.getGameJson(DIZHU_GAMEID, 'room', {}, roomId)
        matchRules = matchConf.get('matchConf', {}).get('matchRules', [])
        mo.setResult('matchRules', matchRules)

        router.sendToUser(mo, userId)
        if ftlog.is_debug():
            ftlog.debug('doGetMatchRulesHandler userId=', userId, roomId, 'mo=', mo)
        return mo

    @markCmdActionMethod(cmd='game', action='day_login_reward', clientIdVer=0, scope='game', lockParamName='')
    def doGetDayLoginReward(self, userId, gameId, clientId):
        '''
        每日固定时间签到的接口
        :param userId:
        :param gameId:
        :param clientId:
        :return:
        '''
        mo = self._doGetDayLoginReward(userId, gameId, clientId)
        router.sendToUser(mo, userId)

    def _doGetDayLoginReward(self, userId, gameId, clientId):
        mo = MsgPack()
        mo.setCmd('game')
        mo.setResult('gameId', gameId)
        mo.setResult('action', 'day_login_reward')
        mo.setResult('userId', userId)

        timeNow = datetime.datetime.now().time()
        #获取配置
        loginConfig = dizhuconf.getDayLoginRewardConf()
        rewardLst = loginConfig.get('rewards')
        
        info = halluser_dailydata.getDailyData(userId, DIZHU_GAMEID, "day_login_reward", {})
        if rewardLst:
            for item in rewardLst:
                count = item.get('count')
                sTime, eTime = item.get('startTime'), item.get('endTime')
                startTime = datetime.datetime.strptime(sTime, '%H:%M:%S')
                endTime = datetime.datetime.strptime(eTime, '%H:%M:%S')
                timeRegion = sTime + '-' + eTime
                
                if startTime.time() <= timeNow <= endTime.time():
                    if info:
                        currentCount = info.get(timeRegion, 0)
                        if currentCount and currentCount >= count:
                            # 领取过了 or 领取超限
                            mo.setResult('count', 0)
                            mo.setResult('msg', loginConfig.get('error2'))
                            break
                    
                    info[timeRegion] = count
                    halluser_dailydata.setDailyData(userId, DIZHU_GAMEID, "day_login_reward", info)
                    
                    assets = {'itemId':item.get('itemId'), 'count': count}
                    UserBag.sendAssetsToUser(DIZHU_GAMEID, userId, assets, 'LOGIN_REWARD')
                    mo.setResult('count', count)
                    mo.setResult('msg', item.get('mail'))
                    break
            else:
                # 未在规定时间内领取
                mo.setResult('count', 0)
                mo.setResult('msg', loginConfig.get('error1'))
        else:
            mo.setResult('count', 0)   
        
        if ftlog.is_debug():
            ftlog.debug('doGetDayLoginReward userId=', userId, 'mo=', mo)
        return mo

    @markCmdActionMethod(cmd='dizhu', action='room_online_users', clientIdVer=0, scope='game', lockParamName='')
    def doRoomOnLineUsers(self, userId, gameId):
        if ftlog.is_debug():
            ftlog.debug('doRoomOnLineUsers', 'userId=', userId)
        mo = self._doRoomOnLineUsers(userId, gameId)
        if ftlog.is_debug():
            ftlog.debug("doRoomOnLineUsers", "userId=", userId, "mo=", mo)
        router.sendToUser(mo, userId)

    @classmethod
    def _doRoomOnLineUsers(cls, userId, gameId):
        ret = []
        onlineInfos = getRoomOnLineUserCount(TGDizhu.gameId())[1]
        for roomId, count in onlineInfos.items():
            ret.append({
                'roomId': roomId,
                'count': int(round(int(count) * 3 + int(random.randint(80, 100)))) if count else 0
            })
        mo = MsgPack()
        mo.setCmd('dizhu')
        mo.setResult('action', 'room_online_users')
        mo.setResult('userId', userId)
        mo.setResult('gameId', gameId)
        mo.setResult('online_users', ret)
        return mo

    @markCmdActionMethod(cmd='dizhu', action='login', clientIdVer=3.76, scope='game')
    def doHallLogin(self, userId, gameId, clientId, version):
        ftlog.debug('ddz.GameTcpHandler.doHallLogin',
                    'userId=', userId,
                    'gameId=', gameId,
                    'clientId=', clientId,
                    'version=', version,
                    'gameId=', gameId,
                    'clientId=', clientId)
        ## bind_game
        ## 记录地主插件的版本号
        SessionDizhuVersion.setVersionNumber(userId, version)

        isdayfirst, iscreate = halluser.loginGame(userId, gameId, clientId)
        if isdayfirst:
            from dizhu.entity.common.events import ActiveEvent
            TGDizhu.getEventBus().publishEvent(ActiveEvent(6, userId, 'firstLogin'))
        self.helper.sendUserInfoResponse(userId, gameId, clientId, '', 0, 1)
        self.helper.sendTodoTaskResponse(userId, gameId, clientId, isdayfirst)
        # BI日志统计
        bireport.userGameEnter(gameId, userId, clientId)
        bireport.reportGameEvent('BIND_GAME',
                                 userId, gameId, 0, 0, 0, 0, 0, 0, [], clientId, iscreate)
        evt = OnLineGameChangedEvent(userId, gameId, 1, clientId)
        TGHall.getEventBus().publishEvent(evt)

        onlineInfos = getRoomOnLineUserCount(TGDizhu.gameId())
        roominfos = dizhuhallinfo.getWechatMatchRooms(gameId, userId, clientId)
        self.filterWechatMatchRoomUserCount(userId, gameId, onlineInfos[1], roominfos)
        self.filterMixRoomUserCount(userId, gameId, onlineInfos[1], roominfos)

        segmentRoomInfos = dizhuhallinfo.getSegmentRooms(gameId, userId, clientId)
        self.filterSegmentRoomUserCount(userId, gameId, onlineInfos[1], segmentRoomInfos)

        msg = MsgPack()
        msg.setCmd('dizhu')
        msg.setResult('action', 'login')
        msg.setResult('gameId', gameId)
        msg.setResult('userId', userId)
        try:
            onlineInfos2 = getRoomOnLineUserCount(TGDizhu.gameId())
            roominfos2 = dizhuhallinfo.getSessions(gameId, userId, clientId)
            self.filterRoomUserCounts(userId, gameId, onlineInfos2[1], roominfos2)
            self.filterMixMatchRoomUserCount(userId, gameId, onlineInfos2[1], roominfos2)
            self.filterMixRoomUserCount(userId, gameId, onlineInfos2[1], roominfos2)

            hall_info = {
                'sessions': roominfos2,
                'quickStart': self._getQuickStartConf(userId),
                'switchConf': self._get_switch_config(clientId),
                'wxTuiguang': self._get_wxTuiguang_config(),
                'gonggao': self._get_gonggao_info(userId, clientId),
                'showBanner': self._showBanner(userId, gameId, clientId)
            }
            msg.setResult('hall_info', hall_info)
            from dizhu.entity.segment.dizhu_segment_match import SegmentMatchHelper
            segmentInfo = SegmentMatchHelper.getUserSegmentInfo(userId, issue='')
            msg.setResult('segmentInfo', segmentInfo)
            from dizhu.servers.util.user_share_behavior_handler import UserShareBehaviorHandler
            ret = UserShareBehaviorHandler._doUserShareBehaviorInfo(userId)
            msg.setResult('burial_list', ret.get('burial_list', []))
            msg.setResult('isBehavior', ret.get('isShare', 0))
            msg.setResult('videoOrBanner', ret.get('videoOrBanner', ''))
            msg.setResult('showRecharge', dizhuhallinfo.isUserRechargeCity(userId))
            msg.setResult('wxFollowInfo', WxFollowHelper.wxFollowInfo(userId))
            conf = configure.getGameJson(DIZHU_GAMEID, 'redEnvelope.share', {})
            if conf['switch']:
                msg.setResult('shareStrategy', conf['template'])
            # msg.setResult('isActive', wx_official._isActive(userId))
            msg.setResult('popwndSeconds', self._get_popwndSeconds())
            dailyPlay = gamedata.getGameAttrs(userId, gameId, ['dailyPlay'])
            dailyPlay = strutil.loads(dailyPlay[0], ignoreException=True,
                                      execptionValue={'count': 0, 'timestamp': pktimestamp.getCurrentTimestamp()})
            dailyPlayCount = dailyPlay['count']
            authPlayCount = configure.getGameJson(gameId, 'authorization', {}).get('authPlayCount', 5)
            shouldAuth = 0
            rewards = []
            if authPlayCount <= dailyPlayCount and not gamedata.getGameAttr(userId, gameId, 'auth'):
                shouldAuth = 1
                rewards = configure.getGameJson(gameId, 'authorization', {}).get('rewards', [])
            msg.setResult('auth', {
                'shouldAuth': shouldAuth,
                'rewards': rewards
            })
        except Exception, e:
            msg.setResult('ok', 0)
            msg.setResult('errMsg', '系统错误，请稍后再试')
            router.sendToUser(msg, userId)
            ftlog.error('doHallLogin',
                        'userId=', userId,
                        'err=', e.message,
                        'msg=', msg)
            return
        msg.setResult('ok', 1)
        router.sendToUser(msg, userId)

    @markCmdActionMethod(cmd='dizhu', action='checkin_daily', clientIdVer=0, scope='game')
    def doDailyCheckIn(self, userId, gameId, clientId):
        ftlog.debug('ddz.GameTcpHandler.doDailyCheckIn',
                    'userId=', userId,
                    'gameId=', gameId,
                    'clientId=', clientId)
        msg = MsgPack()
        conf = configure.getGameJson(6, 'daily.checkin', {})
        conditon = conf.get('condition')
        cond = UserConditionRegister.decodeFromDict(conditon)
        timestamp = pktimestamp.getCurrentTimestamp()
        retCheck = cond.check(DIZHU_GAMEID, userId, clientId, timestamp)
        msg.setCmd('dizhu')
        msg.setResult('action', 'checkin_daily')
        if not retCheck:
            msg.setResult('show', 0)
            router.sendToUser(msg, userId)
            return
        signInRewards = conf.get('signInRewards')
        newSignInRewards = []
        for dayRewards in signInRewards:
            day = dayRewards.get('day')
            isGet = 1 if self._checkGetRewards(userId, gameId, day) else 0
            dayRewards.update({'isGet': isGet})
            newSignInRewards.append(dayRewards)
        registerDays = UserInfo.getRegisterDays(userId, timestamp)
        msg.setResult('show', 1)
        msg.setResult('registerDays', registerDays)
        msg.setResult('signInRewards', newSignInRewards)
        router.sendToUser(msg, userId)

    @markCmdActionMethod(cmd='dizhu', action='send_rewards', clientIdVer=0, scope='game')
    def doSendReward(self, userId, gameId, clientId, dayNumber):
        ftlog.debug('ddz.GameTcpHandler.doSendReward',
                    'userId=', userId,
                    'gameId=', gameId,
                    'clientId=', clientId,
                    'dayNumber=', dayNumber)
        conf = configure.getGameJson(6, 'daily.checkin', {})
        signInRewards = conf.get('signInRewards')
        msg = MsgPack()
        msg.setCmd('dizhu')
        msg.setResult('action', 'send_rewards')
        isGet = 1 if self._checkGetRewards(userId, gameId, dayNumber) else 0
        if isGet:
            msg.setResult('isGet', 0)
            router.sendToUser(msg, userId)
            return
        for dayRewards in signInRewards:
            if dayRewards.get('day') == dayNumber:
                rewardsList = dayRewards.get('rewards')
                contentItems = TYContentItem.decodeList(rewardsList)
                assetList = dizhu_util.sendRewardItems(userId, contentItems, '', 'DIZHU_QIANDAO_SEND_REWARD', 0)
                daobase.executeUserCmd(userId, 'HSET', 'checkInReward:' + str(gameId) + ':' + str(userId), dayNumber, 1)
                msg.setResult('isGet', 1)
                router.sendToUser(msg, userId)
                return

    @classmethod
    def _checkGetRewards(cls, userId, gameId, dayNumber):
        return daobase.executeUserCmd(userId, 'HGET', 'checkInReward:' + str(gameId) + ':' + str(userId), dayNumber)

    @markCmdActionMethod(cmd='dizhu', action='segment_share_star', clientIdVer=0, scope='game')
    def segmentShareStar(self, userId, gameId, clientId, burialId):
        ftlog.debug('ddz.GameTcpHandler.segmentShareStar',
                    'userId=', userId,
                    'gameId=', gameId,
                    'clientId=', clientId,
                    'burialId=', burialId)
        leftCount = hall_share3.getShareLeftCountByBurialId(gameId, userId, clientId, burialId)
        msg = MsgPack()
        msg.setCmd('dizhu')
        msg.setResult('action', 'segment_share_star')
        msg.setResult('gameId', gameId)
        msg.setResult('userId', userId)
        msg.setResult('clientId', clientId)
        msg.setResult('leftCount', leftCount)
        router.sendToUser(msg, userId)

    @markCmdActionMethod(cmd='dizhu', action='roundlist', clientIdVer=0, scope='game')
    def roundList(self, userId, gameId):
        mi = runcmd.getMsgPack()
        tableUserId = mi.getParam('tableUserId')
        if ftlog.is_debug():
            ftlog.debug('ddz.GameTcpHandler.roundList',
                        'userId=', userId,
                        'tableUserId=', tableUserId,
                        'mi=', mi,
                        'gameId=', gameId)
        if tableUserId:
            roundInfo = dizhu_new_roundlist.getUserNewRoundInfo(tableUserId)
        else:
            roundInfo = dizhu_new_roundlist.getUserNewRoundInfo(userId)
        msg = MsgPack()
        msg.setCmd('dizhu')
        msg.setResult('action', 'roundlist')
        msg.setResult('gameId', gameId)
        msg.setResult('userId', userId)
        msg.setResult('roundInfo', roundInfo)
        router.sendToUser(msg, userId)

    @markCmdActionMethod(cmd='dizhu', action='unlockRound', clientIdVer=0, scope='game')
    def unlockRound(self, userId, gameId):
        dizhu_new_roundlist.saveUserRoundState(userId)
        msg = MsgPack()
        msg.setCmd('dizhu')
        msg.setResult('action', 'unlockRound')
        msg.setResult('gameId', gameId)
        msg.setResult('userId', userId)
        msg.setResult('unlock', 1)
        router.sendToUser(msg, userId)

    @markCmdActionMethod(cmd='dizhu', action='wx_follow_reward', clientIdVer=0, scope='game')
    def wxFollowReward(self, userId, gameId):
        self._wxFollowReward(userId, gameId)

    def _wxFollowReward(self, userId, gameId):
        rewards = WxFollowHelper.sendUserReward(userId)
        msg = MsgPack()
        msg.setCmd('dizhu')
        msg.setResult('action', 'wx_follow_reward')
        msg.setResult('gameId', gameId)
        msg.setResult('userId', userId)
        msg.setResult('rewards', rewards)
        router.sendToUser(msg, userId)

    @markCmdActionMethod(cmd='dizhu', action='sign_in_list', clientIdVer=0, scope='game')
    def signInList(self, userId, gameId):
        signInList = dizhu_signin._signInList(userId)
        state = signInList.get('state', 0)
        signInDay = signInList.get('signInDay', 0)
        rewardList = signInList.get('rewardList', {})
        msg = MsgPack()
        msg.setCmd('dizhu')
        msg.setResult('action', 'sign_in_list')
        msg.setResult('gameId', gameId)
        msg.setResult('userId', userId)
        msg.setResult('state', state)
        msg.setResult('signInDay', signInDay)
        msg.setResult('rewardList', rewardList)
        router.sendToUser(msg, userId)

    @markCmdActionMethod(cmd='dizhu', action='sign_in_rewards', clientIdVer=0, scope='game')
    def signInRewards(self, userId, gameId, day, typeId):
        state, rewards = dizhu_signin._sendRewards(userId, day, typeId)
        msg = MsgPack()
        msg.setCmd('dizhu')
        msg.setResult('action', 'sign_in_rewards')
        msg.setResult('gameId', gameId)
        msg.setResult('userId', userId)
        msg.setResult('state', state)
        msg.setResult('rewards', rewards)
        router.sendToUser(msg, userId)

    @markCmdActionMethod(cmd='dizhu', action='cross_list', clientIdVer=0, scope='game')
    def crossList(self, userId, gameId, clientId):
        ''' 交叉导流 '''
        self._crossList(userId, gameId, clientId)

    def _crossList(self, userId, gameId, clientId):
        # 获取配置
        crossList = []
        conf = configure.getGameJson(gameId, 'wx.cross', {})
        locked = 1
        if conf:
            crossList = [d for d in conf.get('crossList', []) if d.get('show', 0) == 1]
            cond = UserConditionRegister.decodeFromDict(conf.get('condition', {}))
            if cond.check(gameId, userId, clientId, pktimestamp.getCurrentTimestamp()):
                locked = 0
            if ftlog.is_debug():
                ftlog.debug('GameTcpHandler._crossList userId=', userId,
                            'gameId=', gameId,
                            'clientId=', clientId,
                            'locked=', locked,
                            'crossList=', crossList)
        msg = MsgPack()
        msg.setCmd('dizhu')
        msg.setResult('action', 'cross_list')
        msg.setResult('gameId', gameId)
        msg.setResult('locked', locked)
        msg.setResult('userId', userId)
        msg.setResult('crossList', crossList)
        router.sendToUser(msg, userId)

    @markCmdActionMethod(cmd='dizhu', action='auth_send_rewards', clientIdVer=0, scope='game')
    def authSendRewards(self, userId, gameId):
        self._authSendRewards(userId, gameId)

    def _authSendRewards(self, userId, gameId):
        hasAuth = gamedata.getGameAttr(userId, gameId, 'auth')
        if hasAuth:
            status = 0
        else:
            status = 1
            rewards = configure.getGameJson(gameId, 'authorization', {}).get('rewards', [])
            contentItems = TYContentItem.decodeList(rewards)
            dizhu_util.sendRewardItems(userId, contentItems, None, 'AUTH_REWARDS', 0)
            gamedata.setGameAttr(userId, gameId, 'auth', 1)
            TGHall.getEventBus().publishEvent(UserCouponReceiveEvent(9999, userId, rewards[0]['count'],
                                                                     user_coupon_details.USER_AUTH_SHARE))
        msg = MsgPack()
        msg.setCmd('dizhu')
        msg.setResult('action', 'auth_send_rewards')
        msg.setResult('gameId', gameId)
        msg.setResult('userId', userId)
        msg.setResult('status', status)
        router.sendToUser(msg, userId)


class MatchListHandlerV3_77(object):
    '''
    V3.77新增需求,修改比赛列表
    '''

    @classmethod
    def onHandle(cls, userId, gameId, clientId, roominfos):

        ## 找到比赛项目
        matchrooms = cls.getMatchSessionRooms(roominfos)
        ftlog.debug("MatchListHandlerV3_77.onHandle",
                    "userId=", userId,
                    "matchrooms=", json.dumps(matchrooms))
        if not matchrooms or len(matchrooms) <= 0:
            return

        ## 加载房间的信息
        # allroominfo = roominfo.loadAllRoomInfo(6)
        dizhuallroominfo = dizhuhallinfo.loadAllRoomInfo(6)
        ftlog.debug("MatchListHandlerV3_77.onHandle: ",
                    "userId=", userId,
                    "dizhuallroominfo=", dizhuallroominfo)

        for room in matchrooms:
            roomId = room.get('id')
            roominfo = dizhuallroominfo.get(roomId)
            ftlog.debug("MatchListHandlerV3_77.onHandle",
                        "userId=", userId,
                        "roomId=", roomId,
                        "isTiming=", cls.isTimingMatch(roomId),
                        "isArena=", cls.isArenaMatch(roomId),
                        'roominfo=', roominfo)
            if not roominfo:
                continue

            ## 人数显示
            if cls.isDisplayMatchingNumber(roomId):  # 显示比赛在线人数
                room['peopleNumber'] = dizhuhallinfo.buildPlayerCountDisplay(roominfo)  # cls.getRoomOnlineNumber(roomId, allroominfo)
            else:  ## 显示报名人数
                room['peopleNumber'] = dizhuhallinfo.buildSigninCountDisplay(roominfo)  # cls.getSignupNumber(roomId, allroominfo)

            ## 报名状态查询
            # room['signupState'] = cls.getSingupStatus(userId, roomId, allroominfo)
            room['signupState'] = dizhuhallinfo.isSignin(userId, roominfo)

            ## 比赛类型
            if cls.isTimingMatch(roomId):
                room['matchType'] = 'TIMING'
            else:
                room['matchType'] = 'USER_COUNT'

            ## 报名费自动填充
            signupFee = room.get('signupFee', {})
            if not signupFee.get('desc'):
                signupFee['desc'] = cls.getMatchDefaultFeesDescription(roomId)
            room['signupFee'] = signupFee

            ## 非定时赛不用处理时间
            if not cls.isTimingMatch(roomId):
                continue

            ## 获得下一场比赛的时间
            match_datetime = cls.getNextMatchTime(roomId, userId, datetime.datetime.now())
            if not match_datetime:
                continue

            ## 比赛时间的时间戳
            room['matchStamp'] = time.mktime(match_datetime.timetuple())
            room['nowStamp'] = time.mktime(datetime.datetime.now().timetuple())

            ## 格式化比赛时间字符串
            matchCondition = room.get('matchCondition', {})
            matchCondition['bottom'] = cls.formatTimeToString(match_datetime.time())

            ## 根据配置生成,年月日日期字符串
            conditionType = matchCondition.get('type')
            if conditionType == 'datetime':
                datetime_topdate = cls.getPublicMatchConfig().get('datetime_topdate')
                matchCondition['top'] = cls.replaceDateToString(match_datetime.date(), datetime_topdate)

    @classmethod
    def getMatchDefaultFeesDescription(cls, roomId):
        roomconf = gdata.getRoomConfigure(roomId)
        if not roomconf:
            ftlog.warn('MatchListHandlerV3_77.isArenaMatch ',
                       'roomId=', roomId,
                       'roomconf=', roomconf)
            return
        feeList = roomconf.get('matchConf', {}).get('fees', [])
        if len(feeList) <= 0:
            return None
        default_fee = feeList[0]
        itemdesc = hallitem.buildContent(default_fee.get('itemId'), default_fee.get('count', 0))
        return itemdesc

    @classmethod
    def isDisplayMatchingNumber(cls, roomId):
        '''
        显示比赛人数的房间(Arena比赛、人满开赛比赛)
        '''
        if cls.isArenaMatch(roomId):
            return True
        return not cls.isTimingMatch(roomId)

    @classmethod
    def isArenaMatch(cls, roomId):
        '''
        是否是Arena比赛
        '''
        roomconf = gdata.getRoomConfigure(roomId)
        if not roomconf:
            ftlog.warn('MatchListHandlerV3_77.isArenaMatch roomId=', roomId,
                       'roomconf=', roomconf)
            return False
        matchTypename = roomconf.get('typeName')
        if matchTypename == 'arena_match':
            return True
        return False

    @classmethod
    def isTimingMatch(cls, roomId):
        '''
        是否是定时赛
        '''
        roomconf = gdata.getRoomConfigure(roomId)
        if not roomconf:
            ftlog.warn('MatchListHandlerV3_77.isTimingMatch roomId=', roomId,
                       'roomconf=', roomconf)
            return False
        matchtype = roomconf.get('matchConf', {}).get('start', {}).get('type')
        if matchtype == MatchType.USER_COUNT:  # 人满开赛
            return False
        elif matchtype == MatchType.TIMING:  # 定时赛
            return True
        return False

    @classmethod
    def getNextMatchTime(cls, roomId, userId, datetime_now):
        '''
        获得指定比赛的下次比赛开赛时间
        :param roomId: 比赛房间Id
        :param userId: 用户ID
        :param datetime_now: 当前时间
        :return: datetime.datetime对象
        '''
        roomconf = gdata.getRoomConfigure(roomId)
        conf = roomconf.get('matchConf', {}).get('start')
        if not conf:
            return None

        startconfobj = StartConfig.parse(conf)
        nextTime = startconfobj.calcNextStartTime()
        ftlog.debug('MatchListHandlerV3_77.getNextMatchTime', "userId=", userId, "roomId=", roomId, "nextTime=", nextTime)
        return datetime.datetime.fromtimestamp(nextTime)

        # match_timelist = startconf._cron.getTimeList()
        # match_daylist = startconf._cron.getDaysList()
        #
        # if len(match_timelist)<=0 or len(match_daylist)<=0:
        #     return None
        #
        # # 将时间按升序排序
        # match_timelist.sort()
        # match_daylist.sort()
        #
        # # ftlog.debug('MatchListHandlerV3_77.getNextMatchTime', "userId=", userId, "roomId=", roomId, "match_timelist=", match_timelist)
        # # ftlog.debug('MatchListHandlerV3_77.getNextMatchTime', "userId=", userId, "roomId=", roomId, "match_daylist=", match_daylist)
        #
        # for d in match_daylist:
        #     for t in match_timelist:
        #         tmp = datetime.datetime(d.year, d.month, d.day, t.hour, t.minute)
        #         if tmp > datetime_now:
        #             return tmp
        # return False

    @classmethod
    def formatTimeToString(cls, time):
        '''
        将时间格式化为字符串
        :param time: datatime.time对象
        '''
        s = ""
        if time.hour <= 9:
            s += "0" + str(time.hour)
        else:
            s += str(time.hour)
        s += ":"
        if time.minute <= 9:
            s += "0" + str(time.minute)
        else:
            s += str(time.minute)
        return s

    @classmethod
    def replaceDateToString(cls, date, s):
        d = {'year': date.year, 'month': date.month, 'day': date.day}
        return strutil.replaceParams(s, d)

    @classmethod
    def getRoomOnlineNumber(cls, roomId, allroominfo):
        '''
        返回指定比赛房间的在线人数描述信息
        '''
        count = 0
        roominfo = cls.getRoomInfo(roomId, allroominfo)
        if roominfo:
            count = roominfo.get('playerCount', 0)
        ftlog.debug('MatchListHandlerV3_77.getRoomOnlineNumber',
                    'roomId=', roomId,
                    'count=', count)
        peopleNumber_online = cls.getPublicMatchConfig().get('peopleNumber_online')
        return strutil.replaceParams(peopleNumber_online, {'people_number': count})

    @classmethod
    def getSignupNumber(cls, roomId, allroominfo):
        '''
        返回指定比赛房间的报名人数描述信息
        '''
        count = 0
        roominfo = cls.getRoomInfo(roomId, allroominfo)
        if roominfo:
            count = roominfo.get('signinCount', 0)
        ftlog.debug('MatchListHandlerV3_77.getSignupNumber',
                    'roomId=', roomId,
                    'count=', count)
        peopleNumber_signup = cls.getPublicMatchConfig().get('peopleNumber_signup')
        return strutil.replaceParams(peopleNumber_signup, {'people_number': count})

    @classmethod
    def getRoomInfo(cls, roomId, allroominfo):
        '''
        获得大房间信息
        :param roomId:要获得的房间号,大房间号
        :param allroominfo:所有房间的房间信息
        :return: {'signinCount': 0, "playerCount": 0}
        '''
        allrooms = {}
        for preRoomId in allroominfo:
            subroom = allroominfo.get(preRoomId)
            bigRoomId = gdata.getBigRoomId(preRoomId)
            room = allrooms.get(bigRoomId, {'signinCount': 0, "playerCount": 0})
            room['signinCount'] += subroom.signinCount or 0
            room['playerCount'] += subroom.playerCount or 0
            allrooms[bigRoomId] = room
        ftlog.debug('MatchListHandlerV3_77.getRoomInfo',
                    'roomId=', roomId,
                    'allrooms=', allrooms)
        return allrooms.get(roomId)

    @classmethod
    def getSingupStatus(cls, userId, roomId, allroominfo):
        '''
        返回报名状态
        '''
        matchinfo = match_remote.loadUserMatchInfo(6, userId, roomId)
        ftlog.debug("MatchListHandlerV3_77.getSingupStatus",
                    "userId=", userId,
                    "roomId=", roomId,
                    "matchinfo=", matchinfo)
        if not matchinfo:
            return False
        subroom = allroominfo.get(roomId)
        ftlog.debug("MatchListHandlerV3_77.getSingupStatus",
                    "userId=", userId,
                    "subroom=", subroom)
        if not subroom:
            return False
        ftlog.debug("MatchListHandlerV3_77.getSingupStatus",
                    "userId=", userId,
                    "matchinfo.state=", matchinfo.state,
                    "matchinfo.instId=", matchinfo.instId,
                    "subroom.instId=", subroom.instId)
        if matchinfo.state == match_remote.UserMatchInfo.ST_SIGNIN and matchinfo.instId == subroom.instId:
            return True
        return False

    @classmethod
    def getMatchSessionRooms(cls, roominfos):
        '''
        获得比赛房间列表
        :param roominfos: 所有房间的信息
        :return:比赛房间列表
        '''
        matchsession = None
        matchsession_index = -1

        for i in range(0, len(roominfos)):
            if roominfos[i].get('match', 0) == 1:
                matchsession = roominfos[i]
                matchsession_index = i

        # 没有找到比赛列表
        if matchsession_index < 0 or matchsession == None:
            return None, -1

        return matchsession.get('rooms', [])

    @classmethod
    def getPublicMatchConfig(cls):
        return dizhuconf.getPublic().get('match_v3_77', {})