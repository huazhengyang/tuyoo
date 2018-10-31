# -*- coding:utf-8 -*-
'''
Created on 2016年6月3日

@author: zhaojiangang
'''
from datetime import datetime

from dizhu.activities.toolbox import UserBag
from dizhu.entity import dizhuconf
from dizhu.entity.dizhuconf import DIZHU_GAMEID
from dizhu.games import match_signin_discount
from dizhu.servers.util.rpc import match_remote
from dizhu.servers.util.rpc.match_remote import UserMatchInfo
import freetime.util.log as ftlog
from hall.entity import hallconf
from poker.entity.configure import gdata, configure
from poker.entity.dao import userdata
from poker.entity.game.rooms import roominfo
from poker.entity.game.rooms.group_match_ctrl.const import MatchType
from poker.util import strutil
import poker.util.timestamp as pktimestamp
from hall.entity.hallusercond import UserConditionRegister


def loadAllRoomInfo(gameId):
    ret = {}
    roomInfoMap = roominfo.loadAllRoomInfo(gameId)
    for roomId, roomInfo in roomInfoMap.iteritems():
        bigRoomId = gdata.getBigRoomId(roomId)
        if not bigRoomId:
            continue
        bigRoomInfo = ret.get(bigRoomId)
        if bigRoomInfo:
            bigRoomInfo.signinCount += max(0, roomInfo.signinCount)
            bigRoomInfo.playerCount += max(0, roomInfo.playerCount)
        else:
            roomInfo.roomId = bigRoomId
            ret[bigRoomId] = roomInfo
    return ret


def isOutofDateMatch(roomConf, roomInfo, timestamp, margin=60):
    if ftlog.is_debug():
        ftlog.debug('dizhuhallinfo.isOutofDateMatch:roomInfo=', roomInfo.__dict__)
    if roomInfo.startType == MatchType.TIMING:
        return not roomInfo.startTime or timestamp >= (roomInfo.startTime + margin)
    return False


def isInTimePeriod(timestamp, timePeriod):
    startTime = timePeriod.get('start')
    endTime = timePeriod.get('end')
    startTime = pktimestamp.parseTimeSecond(startTime) if startTime else None
    endTime = pktimestamp.parseTimeSecond(endTime) if endTime else None
    nowTime = datetime.fromtimestamp(timestamp)
    return (not startTime or nowTime >= startTime) and (not endTime or nowTime < endTime)


def isNotShowMatch(roomConf, roomInfo, timestamp):
    matchConf = roomConf.get('matchConf')
    if not matchConf:
        return False

    showTime = matchConf.get('showTime', '')
    if not showTime:
        # 没有配置认为永远显示
        return False

    for timePeriod in showTime:
        if isInTimePeriod(timestamp, timePeriod):
            return False
    return True


def getMatchRankConf():
    timestamp = pktimestamp.getCurrentTimestamp()
    matchRankConfList = dizhuconf.getPublic().get('matchRankConfig1', [])
    for matchRankConf in matchRankConfList:
        periods = matchRankConf.get('periods', [])
        if not periods:
            return matchRankConf.get('ranks')
        for timePeriod in periods:
            if isInTimePeriod(timestamp, timePeriod):
                return matchRankConf.get('ranks')
    return None


def getMatchRoomStartTime(roomId, roomInfoMap):
    bigRoomId = gdata.getBigRoomId(roomId)
    roomInfo = roomInfoMap.get(bigRoomId) if bigRoomId else roomInfoMap.get(roomId)
    if roomInfo.startTime:
        return roomInfo.startTime
    else:
        return roomInfo.signinTime if roomInfo.signinTime else 0


def getMatchRoomSortIndex(roomId, roomInfoMap, timeStamp):
    topIndex = startTime = rewardValue = 0
    roomConf = gdata.getRoomConfigure(roomId)
    if roomConf:
        startTime = getMatchRoomStartTime(roomId, roomInfoMap)
        beginSec = startTime - timeStamp
        topIndex = -beginSec if beginSec > 86400 else roomConf.get('topindex', 0)
        rewardValue = roomConf.get('championreward', 0)
    return [topIndex, -startTime, rewardValue]


# 根据配置排序比赛房间
def sortMatchRooms(rooms, roomInfoMap):
    # 获取房间id列表，按照索引排序
    matchRank = getMatchRankConf()
    if not matchRank:
        return rooms
    # 房间默认排序
    matchRankMap = {room.get('id'): index for index, room in enumerate(rooms)}
    # 根据配置更新排序值
    for i, roomId in enumerate(matchRank):
        matchRankMap[roomId] = i
    # 排序
    rooms.sort(cmp=lambda x, y: cmp(matchRankMap[x.get('id')], matchRankMap[y.get('id')]))

    # 根据 置顶值大小 开赛时间最近 冠军奖大小 更新排序
    timeStamp = pktimestamp.getCurrentTimestamp()
    rooms.sort(key=lambda x: getMatchRoomSortIndex(x.get('id'), roomInfoMap, timeStamp), reverse=True)

    return rooms


def getFeesDiscount(userId, rooms):
    # 折扣报名比赛 取玩家背包中的物品确认是否有折扣
    for room in rooms:
        matchCondition = room.get('matchCondition', {})
        discountItems = matchCondition.get('discountItems')
        if discountItems:
            for item in discountItems:
                itemId = item.get('itemId')
                userHaveAssetsCount = UserBag.getAssetsCount(userId, itemId)
                if userHaveAssetsCount > 0:
                    discount = item.get('discount', 1)
                    desc = item.get('desc', "")
                    room['signupFee']['desc'] = desc
                    room['signupFee']['saledesc'] = item.get('oldPrice', "")
                    room['signupFee']['sale'] = int(float(discount) * 10)
                    room['entry'] = desc
                    room['hasOtherDiscount'] = True
                    break
    return rooms


def filterNormalFeesDiscount(userId, rooms):
    # 折扣报名比赛
    for room in rooms:
        if room.get('hasOtherDiscount'):
            continue
        matchCondition = room.get('matchCondition', {})
        normalDiscount = matchCondition.get('normalDiscount', {})
        if normalDiscount:
            room.setdefault('singupFeeDiscount', {})
            room['singupFeeDiscount']['desc'] = normalDiscount.get('showDesc')
            itemId = normalDiscount.get('itemId')
            ret, _, remainDisCount = match_signin_discount.canMatchDiscount(userId, int(room['mixId']) if room.get('mixId') else int(room['id']), itemId)
            if not ret:
                continue
            room['singupFeeDiscount']['desc'] = normalDiscount.get('desc')
            room['singupFeeDiscount']['saledesc'] = normalDiscount.get('oldPrice', '')
            room['singupFeeDiscount']['sale'] = int(float(normalDiscount.get('discount')) * 10)
            room['singupFeeDiscount']['entry'] = normalDiscount.get('desc')
            room['singupFeeDiscount']['itemId'] = normalDiscount.get('itemId')
            room['singupFeeDiscount']['remainDisCount'] = remainDisCount
    return rooms


def buildPlayerCountDisplay(roomInfo):
    '''
    返回指定比赛房间的在线人数描述信息
    '''
    if ftlog.is_debug():
        ftlog.debug('dizhuhallinfo.buildPlayerCountDisplay',
                    'roomId=', roomInfo.roomId,
                    'playerCount=', roomInfo.playerCount)
    peopleNumber_online = dizhuconf.getPublic().get('match_v3_77', {}).get('peopleNumber_online')
    return strutil.replaceParams(peopleNumber_online, {'people_number': roomInfo.playerCount})


def buildSigninCountDisplay(roomInfo):
    '''
    返回指定比赛房间的报名人数描述信息
    '''
    if ftlog.is_debug():
        ftlog.debug('dizhuhallinfo.buildSigninCountDisplay',
                    'roomId=', roomInfo.roomId,
                    'signinCount=', roomInfo.signinCount)
    peopleNumber_signup = dizhuconf.getPublic().get('match_v3_77', {}).get('peopleNumber_signup')
    return strutil.replaceParams(peopleNumber_signup, {'people_number': roomInfo.signinCount})


def isSignin(userId, roomInfo):
    '''
    返回报名状态
    '''
    matchInfo = match_remote.loadUserMatchInfo(DIZHU_GAMEID, userId, roomInfo.roomId)
    if ftlog.is_debug():
        ftlog.debug('dizhuhallinfo.getSigninStatus',
                    'userId=', userId,
                    'roomId=', roomInfo.roomId,
                    'matchInfo=', matchInfo)

    return matchInfo and matchInfo.state == UserMatchInfo.ST_SIGNIN and matchInfo.instId == roomInfo.instId


def checkTime(startTime, stopTime):
    if not startTime or not stopTime:
        return True
    time_now = datetime.now().time()

    time_start = datetime.strptime(startTime, '%H:%M').time()
    time_end = datetime.strptime(stopTime, '%H:%M').time()

    # 今天的启示时间点到明天的终止时间点
    if time_start >= time_end:
        return time_start <= time_now or time_now < time_end
    return time_start <= time_now and time_now < time_end


def fillMatchInfo(gameId, userId, clientId, room, roomInfo, timestamp):
    # TODO 过滤地主版本
    if ftlog.is_debug():
        ftlog.debug('dizhuhallinfo.fillMatchInfo:',
                    'userId=', userId,
                    'room=', room,
                    'roomInfo=', roomInfo.__dict__,
                    'roomInf.fees=', roomInfo.fees)
    room['signupState'] = isSignin(userId, roomInfo)
    if roomInfo.startType == MatchType.TIMING:
        room['matchType'] = 'TIMING'
    else:
        room['matchType'] = 'USER_COUNT'

    # 按规则显示人数信息
    roomconf = gdata.getRoomConfigure(roomInfo.roomId)
    tipinfo = roomconf.get('matchListPeopleNumberTip', '暂未开始报名')
    isArena = roomconf.get('typeName') in ('arena_match', 'dizhu_arena_match')
    peopleNumberBase = max(roomInfo.playerCount, roomInfo.signinCount)
    if ftlog.is_debug():
        ftlog.debug('dizhuhallinfo.fillMatchInfo:',
                    'userId=', userId,
                    'roomId=', roomInfo.roomId,
                    'isArena=', isArena,
                    'peopleNumberBase=', peopleNumberBase)
    if isArena:
        peopleNumber = str(peopleNumberBase * 9)
        startTime = roomconf.get('matchConf', {}).get('startTime')
        stopTime = roomconf.get('matchConf', {}).get('stopTime')
        if ftlog.is_debug():
            ftlog.debug('dizhuhallinfo.fillMatchInfo:ArenaMatch',
                        'userId=', userId,
                        'roomId=', roomInfo.roomId,
                        'startTime=', startTime,
                        'stopTime=', stopTime,
                        'peopleNumber=', peopleNumber)
        if checkTime(startTime, stopTime):
            room['peopleNumber'] = peopleNumber
        else:
            room['peopleNumber'] = tipinfo
    else:
        if roomInfo.startType == MatchType.TIMING:
            peopleNumber = str(roomInfo.playerCount + roomInfo.signinCount)
            curstamp = pktimestamp.getCurrentTimestamp()
            if ftlog.is_debug():
                ftlog.debug('dizhuhallinfo.fillMatchInfo:MatchType.TIMING',
                            'userId=', userId,
                            'roomId=', roomInfo.roomId,
                            'peopleNumber=', peopleNumber,
                            'roomInfo.startTime=', roomInfo.startTime,
                            'roomInfo.signinTime=', roomInfo.signinTime,
                            'curstamp=', curstamp)
            if not roomInfo.startTime or not roomInfo.signinTime:
                room['peopleNumber'] = peopleNumber
            else:
                if curstamp < roomInfo.signinTime:  # 报名未开始
                    room['peopleNumber'] = tipinfo
                else:
                    room['peopleNumber'] = peopleNumber

        elif roomInfo.startType == MatchType.USER_COUNT:
            peopleNumber = str(peopleNumberBase)
            if ftlog.is_debug():
                ftlog.debug('dizhuhallinfo.fillMatchInfo:MatchType.USER_COUNT',
                            'userId=', userId,
                            'roomId=', roomInfo.roomId,
                            'peopleNumber=', peopleNumber,
                            'roomInfo.playerCount=', roomInfo.playerCount,
                            'roomInfo.signinCount=', roomInfo.signinCount)
            room['peopleNumber'] = peopleNumber if roomInfo.playerCount > 0 else '0'
        else:
            room['peopleNumber'] = '0'

    if ftlog.is_debug():
        ftlog.debug('dizhuhallinfo.fillMatchInfo:result',
                    'userId=', userId,
                    'roomId=', roomInfo.roomId,
                    'room.peopleNumber=', room.get('peopleNumber'))

    ## 报名费自动填充
    # signupFee = room.get('signupFee', {})
    # if not signupFee.get('desc'):
    #     signupFee['desc'] = buildFeeDisplay(room, roomInfo)
    # room['signupFee'] = signupFee

    nextTimeDisplay = buildMatchTimeForDisplay(roomInfo, False, timestamp)
    if nextTimeDisplay:
        room['condition'] = nextTimeDisplay

    if roomInfo.startTime:
        room['matchStamp'] = roomInfo.startTime
        room['nowStamp'] = timestamp

        startTimeDT = datetime.fromtimestamp(roomInfo.startTime)
        ## 格式化比赛时间字符串
        matchCondition = room.get('matchCondition', {})
        matchCondition['bottom'] = startTimeDT.strftime('%H:%M')

        ## 根据配置生成,年月日日期字符串
        conditionType = matchCondition.get('type')
        if conditionType == 'datetime':
            datetimeTopDate = dizhuconf.getPublic().get('datetime_topdate')
            try:
                matchCondition['top'] = startTimeDT.strftime(datetimeTopDate)
            except:
                matchCondition['top'] = startTimeDT.strftime('%m月%d日')


def filterMatchSession(gameId, userId, clientId, roomInfoMap, session, timestamp):
    filterRooms = []
    session = strutil.cloneData(session)
    for room in session.get('rooms', []):
        roomId = room.get('id')
        roomConf = gdata.getRoomConfigure(roomId)

        if not roomConf:
            if ftlog.is_debug():
                ftlog.debug('dizhuhallinfo.filterMatchSession NotRoomConf gameId=', gameId,
                            'userId=', userId,
                            'clientId=', clientId,
                            'session=', session.get('session'),
                            'roomId=', roomId)
            continue

        displayCondDict = room.get('displayCond', {})
        if not canDisplaySessionRoom(gameId, userId, clientId, roomId, displayCondDict):
            if ftlog.is_debug():
                ftlog.debug('dizhuhallinfo.filterMatchSession NotCanDisplaySessionRoom gameId=', gameId,
                            'userId=', userId,
                            'clientId=', clientId,
                            'roomId=', roomId)
            continue

        if not canDisplayRoom(gameId, userId, clientId, roomId, roomConf):
            if ftlog.is_debug():
                ftlog.debug('dizhuhallinfo.filterNormalSession NotCanDisplayRoom gameId=', gameId,
                            'userId=', userId,
                            'clientId=', clientId,
                            'roomId=', roomId)
            continue

        bigRoomId = gdata.getBigRoomId(roomId)
        if not bigRoomId:
            if ftlog.is_debug():
                ftlog.debug('dizhuhallinfo.filterMatchSession NotBigRoomId gameId=', gameId,
                            'userId=', userId,
                            'clientId=', clientId,
                            'session=', session.get('session'),
                            'roomId=', roomId)
            continue

        roomInfo = roomInfoMap.get(bigRoomId)

        if not roomInfo:
            if ftlog.is_debug():
                ftlog.debug('dizhuhallinfo.filterMatchSession NotRoomInfo gameId=', gameId,
                            'userId=', userId,
                            'clientId=', clientId,
                            'session=', session.get('session'),
                            'roomId=', roomId)
            continue

        if isOutofDateMatch(roomConf, roomInfo, timestamp):
            if ftlog.is_debug():
                ftlog.debug('dizhuhallinfo.filterMatchSession OutofTime gameId=', gameId,
                            'userId=', userId,
                            'clientId=', clientId,
                            'startTime=', roomInfo.startTime,
                            'startType=', roomInfo.startType,
                            'roomId=', roomId)
            continue

        if isNotShowMatch(roomConf, roomInfo, timestamp):
            if ftlog.is_debug():
                ftlog.debug('dizhuhallinfo.filterMatchSession NotShow gameId=', gameId,
                            'userId=', userId,
                            'clientId=', clientId,
                            'session=', session.get('session'),
                            'roomId=', roomId,
                            'startTime=', roomInfo.startTime)
            continue

        # 根据用户IP进行不同展示,
        if roomConf.get('typeName') == 'dizhu_arena_match':
            arenaContent = getArenaMatchProvinceContent(userId, int(room['mixId']) if room.get('mixId') else room['id'], clientId)

            if arenaContent:
                room['name'] = arenaContent.get('name')
                room['showInfo']['name'] = arenaContent.get('showName')
                room['showInfo']['namezyy'] = arenaContent.get('showNamezzy')
                room['showInfo']['gameDes'] = arenaContent.get('gameDes')

                # if ftlog.is_debug():
                #     d = {}
                #     roomInfo._toDictImpl(d)
                #     ftlog.debug('filterMatchSession roomId=', roomId, 'room=', room, 'roomInfo=', d)

        fillMatchInfo(gameId, userId, clientId, room, roomInfo, timestamp)
        filterRooms.append(room)

    session_rooms = sortMatchRooms(filterRooms, roomInfoMap)
    session['rooms'] = getFeesDiscount(userId, session_rooms)
    session['rooms'] = filterNormalFeesDiscount(userId, session_rooms)
    return session


# 获取下一场比赛日期信息
def getNextMatchDateInfo(nowTime, startTime, nextMatchTimeFromat):
    dstDay = startTime.date()
    curDay = nowTime.date()

    if (dstDay - curDay).days <= nextMatchTimeFromat.get('dayInfoCnt', 1):
        return nextMatchTimeFromat.get('dayInfo' + str((dstDay - curDay).days), '')

    other = nextMatchTimeFromat.get('other', '${month}-${day}')
    other = strutil.replaceParams(other, {'month': str(dstDay.month), 'day': str(dstDay.day)})
    return other


def buildMatchTimeForDisplay(roomInfo, isFromCoinRoom, timestamp):
    if roomInfo.startType != MatchType.TIMING or not roomInfo.startTime:
        return None

    nextMatchTimeConf = dizhuconf.getPublic().get('nextmatchtime')
    if not nextMatchTimeConf:
        if ftlog.is_debug():
            ftlog.debug('dizhuhallinfo.buildMatchTimeForDisplay NotNextMatchTimeConf roomId=', roomInfo.roomId,
                        'isFromCoinRoom=', isFromCoinRoom,
                        'startTime=', roomInfo.startTime)

    nowTime = datetime.fromtimestamp(timestamp)
    startTime = datetime.fromtimestamp(roomInfo.startTime)
    timeFormat = '%H:%M'
    if ftlog.is_debug():
        ftlog.debug('dizhuhallinfo.buildMatchTimeForDisplay roomId=', roomInfo.roomId,
                    'isFromCoinRoom=', isFromCoinRoom,
                    'startTime=', startTime)

    if isFromCoinRoom and not nextMatchTimeConf.get('coinRoomShowDayInfo'):
        return startTime.strftime(timeFormat)

    # 在此获取日期的显示信息了:今天明天，后天还是显示日期
    dateInfo = getNextMatchDateInfo(nowTime, startTime, nextMatchTimeConf)
    return dateInfo + startTime.strftime(timeFormat)


def canDisplayRoom(gameId, userId, clientId, roomId, roomConf):
    displayCondDict = roomConf.get('displayCond')
    if displayCondDict:
        try:
            displayCond = UserConditionRegister.decodeFromDict(displayCondDict)
            ret = displayCond.check(gameId, userId, clientId, pktimestamp.getCurrentTimestamp())
            if not ret:
                if ftlog.is_debug():
                    ftlog.debug('dizhuhallinfo.canDisplayRoom',
                                'gameId=', gameId,
                                'userId=', userId,
                                'clientId=', clientId,
                                'roomId=', roomId,
                                'displayCond=', displayCondDict,
                                'ret=', ret)
            return ret
        except:
            ftlog.error('dizhuhallinfo.canDisplayRoom',
                        'gameId=', gameId,
                        'userId=', userId,
                        'clientId=', clientId,
                        'roomId=', roomId,
                        'displayCond=', displayCondDict)
            return False
    return True


def canDisplaySessionRoom(gameId, userId, clientId, roomId, displayCondDict):
    if displayCondDict:
        try:
            displayCond = UserConditionRegister.decodeFromDict(displayCondDict)
            ret = displayCond.check(gameId, userId, clientId, pktimestamp.getCurrentTimestamp())
            if not ret:
                if ftlog.is_debug():
                    ftlog.debug('dizhuhallinfo.canDisplaySessionRoom',
                                'gameId=', gameId,
                                'userId=', userId,
                                'clientId=', clientId,
                                'roomId=', roomId,
                                'displayCond=', displayCondDict,
                                'ret=', ret)
            return ret
        except:
            ftlog.error('dizhuhallinfo.canDisplaySessionRoom',
                        'gameId=', gameId,
                        'userId=', userId,
                        'clientId=', clientId,
                        'roomId=', roomId,
                        'displayCond=', displayCondDict)
            return False
    return True


def filterNormalSession(gameId, userId, clientId, roomInfoMap, session, timestamp):
    filterRooms = []
    session = strutil.cloneData(session)
    timestamp = pktimestamp.getCurrentTimestamp()
    for room in session.get('rooms', []):
        roomId = room.get('id')
        roomConf = gdata.getRoomConfigure(roomId)

        if not roomConf:
            if ftlog.is_debug():
                ftlog.debug('dizhuhallinfo.filterNormalSession NotRoomConf gameId=', gameId,
                            'userId=', userId,
                            'clientId=', clientId,
                            'roomId=', roomId)
            continue

        displayCondDict = room.get('displayCond', {})
        if not canDisplaySessionRoom(gameId, userId, clientId, roomId, displayCondDict):
            if ftlog.is_debug():
                ftlog.debug('dizhuhallinfo.filterNormalSession NotCanDisplaySessionRoom gameId=', gameId,
                            'userId=', userId,
                            'clientId=', clientId,
                            'roomId=', roomId)
            continue

        if not canDisplayRoom(gameId, userId, clientId, roomId, roomConf):
            if ftlog.is_debug():
                ftlog.debug('dizhuhallinfo.filterNormalSession NotCanDisplayRoom gameId=', gameId,
                            'userId=', userId,
                            'clientId=', clientId,
                            'roomId=', roomId)
            continue

        if roomConf.get('ismatch'):
            roomInfo = roomInfoMap.get(roomId)
            if not roomInfo:
                if ftlog.is_debug():
                    ftlog.debug('dizhuhallinfo.filterNormalSession NotRoomInfo gameId=', gameId,
                                'userId=', userId,
                                'clientId=', clientId,
                                'roomId=', roomId)
                continue

            if isOutofDateMatch(roomConf, roomInfo, timestamp):
                if ftlog.is_debug():
                    ftlog.debug('dizhuhallinfo.filterNormalSession OutofTime gameId=', gameId,
                                'userId=', userId,
                                'clientId=', clientId,
                                'startTime=', roomInfo.startTime,
                                'startType=', roomInfo.startType,
                                'roomId=', roomId)
                continue

            room['isMatch'] = True
            nextTimeDisplay = buildMatchTimeForDisplay(roomInfo, True, timestamp)
            if nextTimeDisplay:
                showInfo = room.get('showInfo', {})
                showInfo['extendInfo'] = nextTimeDisplay
                room['showInfo'] = showInfo

            #######
            #  根据用户IP进行不同展示,
            if roomConf.get('typeName') == 'dizhu_arena_match':
                arenaContent = getArenaMatchProvinceContent(userId,
                                                            int(room['mixId']) if room.get('mixId') else room['id'],
                                                            clientId)
                if arenaContent:
                    room['name'] = arenaContent.get('name')
                    room['showInfo']['name'] = arenaContent.get('showName')
                    room['showInfo']['namezyy'] = arenaContent.get('showNamezzy')
                    room['showInfo']['gameDes'] = arenaContent.get('gameDes')

        filterRooms.append(room)
        if ftlog.is_debug():
            ftlog.debug('dizhuhallinfo.filterNormalSession ok gameId=', gameId,
                        'userId=', userId,
                        'clientId=', clientId,
                        'roomId=', roomId,
                        'room.showInfo', room['showInfo'])
    session['rooms'] = filterRooms
    return session


def filterSession(gameId, userId, clientId, roomInfoMap, session, timestamp):
    if session.get('match') == 1:
        return filterMatchSession(gameId, userId, clientId, roomInfoMap, session, timestamp)
    return filterNormalSession(gameId, userId, clientId, roomInfoMap, session, timestamp)


def getSessions(gameId, userId, clientId):
    ret = []
    roomInfoMap = loadAllRoomInfo(gameId)
    timestamp = pktimestamp.getCurrentTimestamp()
    sessions = hallconf.getHallSessionInfo(gameId, clientId)
    for session in sessions:
        session = filterSession(gameId, userId, clientId, roomInfoMap, session, timestamp)
        if session:
            ret.append(session)
    return ret


def getWechatMatchRooms(gameId, userId, clientId):
    ret = []
    roomInfoMap = loadAllRoomInfo(gameId)
    timestamp = pktimestamp.getCurrentTimestamp()
    sessions = hallconf.getHallSessionInfo(gameId, clientId)
    for session in sessions:
        if session.get('match') == 1:
            return filterMatchSession(gameId, userId, clientId, roomInfoMap, session, timestamp)['rooms']
    return ret


def getSegmentRooms(gameId, userId, clientId):
    ret = []
    sessions = hallconf.getHallSessionInfo(gameId, clientId)
    for session in sessions:
        if session.get('segment') == 1:
            return session['rooms']
    return ret


def getTvoSessions(gameId, userId, clientId):
    ret = []
    roomInfoMap = loadAllRoomInfo(gameId)
    timestamp = pktimestamp.getCurrentTimestamp()
    sessions = dizhuconf.getDdzSessionInfo(gameId, clientId)
    for session in sessions:
        session = filterSession(gameId, userId, clientId, roomInfoMap, session, timestamp)
        if session:
            ret.append(session)
    return ret


def getMatchSessionRankRewards(gameId, clientId, bigRoomId):
    sessions = hallconf.getHallSessionInfo(gameId, clientId)
    for session in sessions:
        if session.get('match') == 1:
            for room in session.get('rooms', []):
                if room.get('id') == bigRoomId:
                    return room.get('rank.rewards', [])
    return []

def getMatchSessionName(gameId, clientId, bigRoomId):
    sessions = hallconf.getHallSessionInfo(gameId, clientId)
    for session in sessions:
        if session.get('match') == 1:
            for room in session.get('rooms', []):
                if room.get('id') == bigRoomId:
                    return room.get('name', '')
    return ''


def getArenaMatchProvinceContent(userId, bigRoomId, clientId):
    province = userdata.getAttr(userId, 'province')
    if ftlog.is_debug():
        ftlog.debug('dizhuhallinfo.getArenaMatchProvinceContent userId=', userId,
                    'bigRoomId=', bigRoomId,
                    'clientId=', clientId,
                    'province=', province,
                    'provinceType=', type(province))
    if not province:
        return
    try:
        province = province.encode('utf8') if isinstance(province, unicode) else province
    except:
        return

    vcName = getArenaMatchVcTemplateName('arena.match.rewards', province, DIZHU_GAMEID)
    tcTemplate = configure.getTcTemplatesByGameId('arena.match.rewards', None, DIZHU_GAMEID)

    if not tcTemplate:
        return
    tcContent = tcTemplate.get(vcName, {}).get(str(bigRoomId), {})
    return tcContent


def getArenaMatchSessionRankRewards(userId, bigRoomId, clientId):
    tcContent = getArenaMatchProvinceContent(userId, bigRoomId, clientId)
    if tcContent:
        return tcContent.get('rank.rewards', [])
    else:
        return []


def getArenaMatchVcTemplateName(moduleKey, province, gameId):
    if not province:
        return
    xkey = 'game:' + str(gameId) + ':' + moduleKey + ':' + 'vc'
    datas = configure._get(xkey, {})
    if not '_cache' in datas:
        strutil.replaceObjRefValue(datas)
        datas['_cache'] = {}

    _cache = datas['_cache']
    tname = _cache.get(province, None)
    if tname is None:
        actual = datas.get('actual', {})
        tname = actual.get(province, None)
        if tname is None:
            tname = actual.get(province, None)
            if tname is None:
                tname = actual.get(province.decode('utf8'), None)

        # 最后取缺省值
        if tname is None:
            tname = datas.get('default', None)
        if tname is None:
            ftlog.warn('the province can not find template name ' + moduleKey + ' ' + province)
        _cache[province] = tname

    if ftlog.is_debug():
        ftlog.debug('dizhuhallinfo.getArenaMatchVcTemplateName moduleKey=', moduleKey,
                    'tname=', tname,
                    'province=', province,
                    'provinceType=', type(province),
                    'datas=', datas)
    return tname


def isUserRechargeCity(userId):
    conf = configure.getGameJson(DIZHU_GAMEID, 'city.recharge', {})
    if not conf.get('open'):
        return 0
    province = userdata.getAttr(userId, 'province')
    if ftlog.is_debug():
        ftlog.debug('dizhuhallinfo.getUserRechargeCity userId=', userId,
                    'province=', province,
                    'provinceType=', type(province))
    if not province:
        return 1
    try:
        province = province.encode('utf8') if isinstance(province, unicode) else province
    except:
        return 1

    limitCities = conf.get('limitCities', [])
    rechargeTime = conf.get('rechargeTime', {})
    if not limitCities or not rechargeTime:
        return 1

    if province not in limitCities:
        return 1
    else:
        try:
            currentTime = datetime.now().time()
            startTime = datetime.strptime(rechargeTime.get('startTime'), "%H:%M:%S").time()
            stopTime = datetime.strptime(rechargeTime.get('stopTime'), "%H:%M:%S").time()
            if startTime <= currentTime <= stopTime:
                return 1
            return 0
        except Exception, e:
            ftlog.warn('dizhuhallinfo.isUserRechargeCity userId=', userId,
                    'city.recharge conf timeerror=', e.message)
    return 0