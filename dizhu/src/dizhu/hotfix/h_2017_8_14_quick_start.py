# -*- coding:utf-8 -*-
'''
Created on 2017年8月14日

@author: wangyonghui
'''

from dizhu.entity import dizhuconf
from dizhu.entity.dizhuconf import DIZHU_GAMEID
from freetime.util import log as ftlog
from hall.entity import hallconf
from poker.entity.configure import gdata
from poker.entity.dao import sessiondata
from poker.entity.dao import userchip
from dizhu.gametable.dizhu_quick_start import DizhuQuickStart


_DIZHU_CTRL_ROOM_IDS_LIST = []


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


@classmethod
def _getQuickStartRoomList(cls, userId, playMode, **kwargs):
    # 判断userChip
    quickStartConf = dizhuconf.getQuickStart()
    userChip = userchip.getChip(userId)

    isMatch = 0
    # 比赛快开
    if playMode == dizhuconf.PLAYMODE_STRAIGHT_MATCH:
        matchStartChip = quickStartConf.get('matchStartChip', 0)
        isMatch = 1
        if userChip < matchStartChip:
            startRooms = quickStartConf.get('matchStartRooms', [])
            if startRooms:
                return [bigRoomId * 10000 + 1000 for bigRoomId in startRooms]
    # 大厅快开
    elif playMode == dizhuconf.PLAYMODE_DEFAULT:
        # 新手大厅快开必须进入配置指定的房间
        bigRoomIds = cls._getNewComerBigRoomIds(userId)
        if bigRoomIds:
            try:
                sessionRoomIds = cls.getMatchSessionRoomIds(userId)
                if not sessionRoomIds:  # 提审用
                    return [bigRoomIds[-1] * 10000 + 1000]
            except Exception, e:
                ftlog.error('DizhuQuickStart._getQuickStartRoomList',
                            'userId=', userId,
                            'playMode=', playMode,
                            'kwargs=', kwargs,
                            'bigRoomIds=', bigRoomIds,
                            'err=', e.message)
            return [bigRoomId * 10000 + 1000 for bigRoomId in bigRoomIds]
        hallStartChip = quickStartConf.get('hallStartChip', 0)
        if hallStartChip and userChip >= hallStartChip:
            playMode = dizhuconf.PLAYMODE_123
        else:
            startRooms = quickStartConf.get('hallStartRooms', [])
            if startRooms:
                try:
                    sessionRoomIds = cls.getMatchSessionRoomIds(userId)
                    if not sessionRoomIds:  # 提审用
                        return [startRooms[-1] * 10000 + 1000]
                except Exception, e:
                    ftlog.error('DizhuQuickStart._getQuickStartRoomList',
                                'userId=', userId,
                                'playMode=', playMode,
                                'kwargs=', kwargs,
                                'startRooms=', startRooms,
                                'err=', e.message)
                return [bigRoomId * 10000 + 1000 for bigRoomId in startRooms]

    ctrlroomid_quickstartchip_list = []

    global _DIZHU_CTRL_ROOM_IDS_LIST
    if not _DIZHU_CTRL_ROOM_IDS_LIST:
        # 生成的控制房间的房间id列表，ctrlroomid = bigRoomId * 10000 + 1000
        _DIZHU_CTRL_ROOM_IDS_LIST = [bigRoomId * 10000 + 1000 for bigRoomId in gdata.gameIdBigRoomidsMap().get(DIZHU_GAMEID, [])]

    rankId = kwargs.get('rankId', '-1')
    for ctrlroomid in _DIZHU_CTRL_ROOM_IDS_LIST:
        roomdef = gdata.roomIdDefineMap()[ctrlroomid]
        ismatch = roomdef.configure.get('ismatch', 0)

        if ismatch != isMatch:
            continue

        # 过滤玩法
        playmode = roomdef.configure.get('playMode', '')
        if not ismatch and playmode != playMode:
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
    return ctrlRoomIds

DizhuQuickStart.getMatchSessionRoomIds = getMatchSessionRoomIds
DizhuQuickStart._getQuickStartRoomList = _getQuickStartRoomList
