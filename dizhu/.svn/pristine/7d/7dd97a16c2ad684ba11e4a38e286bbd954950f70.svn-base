# coding=utf-8
'''
Created on 2015年7月9日

@author: zhaojiangang
'''
from datetime import datetime
import json
import random
from sre_compile import isstring
import time

from dizhu.entity import dizhuconf, skillscore, dizhu_util
from dizhu.entity.dizhuconf import DIZHU_GAMEID
from dizhu.entity.dizhuversion import SessionDizhuVersion
from dizhu.entity.skillscore import SkillScoreIncrEvent
from dizhu.gamecards.dizhu_rule import CardTypeHuoJian, CardTypeZhaDan, \
    CardTypeDanPai, CardTypeDuiZi, CardTypeSanZhang, CardTypeSanDai1, \
    CardTypeSanDai2, CardTypeDanShun, CardTypeShuangShun, CardTypeFeiJi, \
    CardTypeFeiJiDai1, CardTypeFeiJiDai2, CardTypeSiDai1, CardTypeSiDai2
from dizhucomm.entity.events import UserTablePlayEvent, \
    UserTableWinloseEvent, UserLevelGrowEvent, UserTBoxLotteryEvent, UserTableEvent, \
    UserTableCallEvent, UseTableEmoticonEvent
from dizhu.games.segmentmatch.events import SegmentTableWinloseEvent
from dizhu.gameplays.game_events import MyFTFinishEvent
from dizhu.replay import replay_service
from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from hall.entity import hallitem, datachangenotify
from hall.entity.hallshare import HallShareEvent
from hall.entity.halltask import TYHallTaskModel, TYHallSubTaskSystem, \
    TYTaskSimpleData, TYTaskSimple, TYTaskKindSimple
from poker.entity.biz.content import TYContentRegister
from poker.entity.biz.exceptions import TYBizException
from poker.entity.biz.item.item import TYAssetUtils
from poker.entity.biz.task.exceptions import TYTaskConfException
from poker.entity.biz.task.task import TYTaskCondition, TYTaskInspector, \
    TYTaskConditionRegister, TYTaskInspectorRegister, TYTaskSystem, TYTaskSystemImpl, \
    TYTaskKindRegister, TYTask, TYTaskKind
from poker.entity.configure import configure as pkconfigure, gdata
from poker.entity.dao import gamedata as pkgamedata, sessiondata
import poker.entity.dao.userchip as pkuserchip
from poker.entity.events.tyevent import EventUserLogin, MatchWinloseEvent, \
    UserEvent, EventConfigure
import poker.entity.events.tyeventbus as pkeventbus
from poker.protocol import router
from poker.util import timestamp as pktimestamp
from dizhu.entity.segment import task as SegmentTaskSystem
from dizhu.entity.segment.task import SegmentNewbieTaskKind, SegmentDailyTaskKind


class DizhuTaskConditionChunTian(TYTaskCondition):
    TYPE_ID = 'ddz.cond.chuntian'

    def __init__(self):
        super(DizhuTaskConditionChunTian, self).__init__()

    def check(self, task, event):
        ret = isinstance(event, UserTableWinloseEvent) and event.winlose.isWin and event.winlose.chunTian
        ftlog.debug('DizhuTaskConditionChunTian.check userId=', task.userId,
                    'kindId=', task.kindId,
                    'ret=', ret,
                    'winlose=', event.winlose.__dict__)
        return ret


class DizhuTaskConditionZhaDan(TYTaskCondition):
    TYPE_ID = 'ddz.cond.zhadan'

    def __init__(self):
        super(DizhuTaskConditionZhaDan, self).__init__()
        self.bombCount = 0

    def check(self, task, event):
        return (isinstance(event, UserTableWinloseEvent)
                and event.winlose.isWin
                and event.winlose.nBomb >= self.bombCount)

    def _decodeFromDictImpl(self, d):
        self.bombCount = d.get('nbomb')
        if not isinstance(self.bombCount, int):
            raise TYTaskConfException(d, 'nbomb must be int')


class DizhuTaskConditionWindoubles(TYTaskCondition):
    TYPE_ID = 'ddz.cond.windoubles'

    def __init__(self):
        super(DizhuTaskConditionWindoubles, self).__init__()
        self.start = -1
        self.stop = -1

    def check(self, task, event):
        return (isinstance(event, UserTableWinloseEvent)
                and event.winlose.isWin
                and event.winlose.windoubles >= self.start
                and (self.stop == -1 or event.winlose.windoubles <= self.stop))

    def _decodeFromDictImpl(self, d):
        self.start = d.get('start')
        self.stop = d.get('stop')
        if not isinstance(self.start, int) or self.start < -1:
            raise TYTaskConfException(d, 'DizhuTaskConditionWindoubles.start must be int >= -1')
        if not isinstance(self.stop, int) or self.stop < -1:
            raise TYTaskConfException(d, 'DizhuTaskConditionWindoubles.stop must be int >= -1')
        if self.stop != -1 and self.stop < self.start:
            raise TYTaskConfException(d, 'DizhuTaskConditionWindoubles.stop must be > start')


class DizhuTaskConditionSlam(TYTaskCondition):
    TYPE_ID = 'ddz.cond.slam'

    def __init__(self):
        super(DizhuTaskConditionSlam, self).__init__()

    def check(self, task, event):
        return (isinstance(event, UserTableWinloseEvent)
                and event.winlose.isWin
                and event.winlose.slam)


class DizhuTaskConditionDizhu(TYTaskCondition):
    TYPE_ID = 'ddz.cond.dizhu'

    def __init__(self):
        super(DizhuTaskConditionDizhu, self).__init__()

    def check(self, task, event):
        return (isinstance(event, UserTablePlayEvent)
                and event.dizhuUserId == task.userTaskUnit.userId)


class DizhuTaskConditionMatchId(TYTaskCondition):
    TYPE_ID = 'ddz.cond.matchId'

    def __init__(self):
        super(DizhuTaskConditionMatchId, self).__init__()
        self.matchIdSet = None

    def check(self, task, event):
        return (isinstance(event, MatchWinloseEvent)
                and event.matchId in self.matchIdSet)

    def _decodeFromDictImpl(self, d):
        matchIds = d.get('matchIds')
        if not isinstance(matchIds, list):
            raise TYTaskConfException(d, 'matchIds must be list')
        for matchId in matchIds:
            if not isinstance(matchId, int):
                raise TYTaskConfException(d, 'matchIds.matchId must be int')
        self.matchIdSet = set(matchIds)


class DizhuTaskConditionRoomId(TYTaskCondition):
    TYPE_ID = 'ddz.cond.roomId'

    def __init__(self):
        super(DizhuTaskConditionRoomId, self).__init__()
        self.roomIdSet = None

    def check(self, task, event):
        if isinstance(event, UserTableEvent):
            shortRoomId = int(event.roomId / 10000)
            return event.roomId in self.roomIdSet or shortRoomId in self.roomIdSet
        return False

    def _decodeFromDictImpl(self, d):
        roomIds = d.get('roomIds')
        if not isinstance(roomIds, list):
            raise TYTaskConfException(d, 'roomIds must be list')
        for roomId in roomIds:
            if not isinstance(roomId, int):
                raise TYTaskConfException(d, 'roomIds.roomId must be int')
        self.roomIdSet = set(roomIds)


class DizhuTaskConditionGrabDizhu(TYTaskCondition):
    TYPE_ID = 'ddz.cond.grabDizhu'

    def __init__(self):
        super(DizhuTaskConditionGrabDizhu, self).__init__()

    def check(self, task, event):
        if not isinstance(event, UserTableCallEvent):
            return False
        return event.isGrab


def _baseCardTypeName(baseCardType):
    if baseCardType == 9000000:
        return 'huojian'
    elif baseCardType == 8000052:
        return 'xiaowang'
    elif baseCardType == 8000053:
        return 'dawang'

    value = baseCardType / 1000000
    if value == 7:
        return 'baozi'
    elif value == 6:
        return 'tonghuashun'
    elif value == 5:
        return 'tonghua'
    elif value == 4:
        return 'shunzi'
    elif value == 3:
        return 'duizi'
    elif value == 1:
        return '235'
    else:
        return 'sanpai'


class DizhuTaskConditionBaseCardType(TYTaskCondition):
    TYPE_ID = 'ddz.cond.baseCardType'

    def __init__(self):
        super(DizhuTaskConditionBaseCardType, self).__init__()
        self.cardTypeSet = None

    def check(self, task, event):
        if not isinstance(event, UserTablePlayEvent):
            return False
        cardTypeName = _baseCardTypeName(event.baseCardType)
        return cardTypeName in self.cardTypeSet

    def _decodeFromDictImpl(self, d):
        cardTypes = d.get('cardTypes')
        if not isinstance(cardTypes, list):
            raise TYTaskConfException(d, 'cardTypes must be list')
        for cardType in cardTypes:
            if not isstring(cardType):
                raise TYTaskConfException(d, 'cardTypes.cardType must be string')
        self.cardTypeSet = set(cardTypes)


cardTypeNameMap = {
    CardTypeHuoJian: 'huojian',
    CardTypeZhaDan: 'zhadan',
    CardTypeDanPai: 'danpai',
    CardTypeDuiZi: 'duizi',
    CardTypeSanZhang: 'sanzhang',
    CardTypeSanDai1: 'sandaidan',
    CardTypeSanDai2: 'sandaidui',
    CardTypeDanShun: 'danshun',
    CardTypeShuangShun: 'shuangshun',

    CardTypeFeiJi: 'feiji',
    CardTypeFeiJiDai1: 'feijidaidan',
    CardTypeFeiJiDai2: 'feijidaidui',
    CardTypeSiDai1: 'sidaidan',
    CardTypeSiDai2: 'sidaidui',
}


def _cardTypeName(cardType):
    return cardTypeNameMap.get(cardType, None)


class DizhuTaskConditionOutWinCardType(TYTaskCondition):
    TYPE_ID = 'ddz.cond.outWinCardType'

    def __init__(self):
        super(DizhuTaskConditionOutWinCardType, self).__init__()
        self.cardTypeSet = None

    def check(self, task, event):
        if not isinstance(event, UserTableWinloseEvent):
            return False
        if event.winlose.winUserId != event.userId:
            return False
        if not event.winlose.winCard:
            ftlog.warn('DizhuTaskConditionOutWinCardType.check userId=', event.userId,
                       'taskId=', task.kindId,
                       'roomId=', event.roomId,
                       'tableId=', event.tableId,
                       'isWin=', event.winlose.isWin,
                       'err=', 'winCardIsNone')
            return False
        winCardTypeName = _cardTypeName(type(event.winlose.winCard.cardType))

        ftlog.debug('DizhuTaskConditionOutWinCardType.check userId=', event.userId,
                    'taskId=', task.kindId,
                    'roomId=', event.roomId,
                    'tableId=', event.tableId,
                    'winloseUserId=', event.winlose.winUserId,
                    'isWin=', event.winlose.isWin,
                    'winCardTypeName=', winCardTypeName,
                    'cardType=', type(event.winlose.winCard.cardType),
                    'self.cardTypeSet=', self.cardTypeSet)

        return winCardTypeName in self.cardTypeSet

    def _decodeFromDictImpl(self, d):
        cardTypes = d.get('cardTypes')
        if not isinstance(cardTypes, list):
            raise TYTaskConfException(d, 'cardTypes must be list')
        for cardType in cardTypes:
            if not isstring(cardType):
                raise TYTaskConfException(d, 'cardTypes.cardType must be string')
        self.cardTypeSet = set(cardTypes)


class DizhuTaskConditionPlayMode(TYTaskCondition):
    TYPE_ID = 'ddz.cond.playMode'

    def __init__(self):
        super(DizhuTaskConditionPlayMode, self).__init__()
        self.playModeSet = None

    def check(self, task, event):
        if not isinstance(event, UserTableEvent):
            return False

        roomConf = gdata.getRoomConfigure(event.roomId)
        playMode = roomConf.get('playMode', dizhuconf.PLAYMODE_DEFAULT)
        if ftlog.is_debug():
            ftlog.debug('DizhuTaskConditionPlayMode.check userId=', event.userId,
                        'roomId=', event.roomId,
                        'playMode=', playMode,
                        'playModeSet=', self.playModeSet)
        return playMode in self.playModeSet

    def _decodeFromDictImpl(self, d):
        playModes = d.get('playModes')
        if not isinstance(playModes, list):
            raise TYTaskConfException(d, 'playModes must be list')
        for playMode in playModes:
            if not isstring(playMode):
                raise TYTaskConfException(d, 'playModes.item must be string')
        self.playModeSet = set(playModes)


class DizhuTaskConditionMatchRank(TYTaskCondition):
    TYPE_ID = 'ddz.cond.matchRank'

    def __init__(self):
        super(DizhuTaskConditionMatchRank, self).__init__()
        self.startRank = None
        self.stopRank = None

    def check(self, task, event):
        if not isinstance(event, MatchWinloseEvent):
            return False

        if self.startRank >= 0 and event.rank < self.startRank:
            return False

        if self.stopRank >= 0 and event.rank > self.stopRank:
            return False

        return True

    def _decodeFromDictImpl(self, d):
        startRank = d.get('startRank', -1)
        if not isinstance(startRank, int) or startRank < -1:
            raise TYTaskConfException(d, 'startRank must be int >= -1')
        stopRank = d.get('stopRank', -1)
        if not isinstance(stopRank, int) or stopRank < -1:
            raise TYTaskConfException(d, 'stopRank must be int >= -1')

        if stopRank != -1 and stopRank < startRank:
            raise TYTaskConfException(d, 'stopRank must >= stopRank %s:%s' % (startRank, stopRank))
        self.startRank = startRank
        self.stopRank = stopRank


class DizhuTaskConditionOnceWinChip(TYTaskCondition):
    TYPE_ID = 'ddz.cond.winChip'

    def __init__(self):
        super(DizhuTaskConditionOnceWinChip, self).__init__()
        self.winChipOnce = 0

    def check(self, task, event):
        if not isinstance(event, UserTableWinloseEvent):
            return False
        return event.winlose.deltaChip >= self.winChipOnce

    def _decodeFromDictImpl(self, d):
        chip = d.get('winChip', 0)
        if not isinstance(chip, int) or chip <= 0:
            raise TYTaskConfException(d, 'winChip must be int > 0')
        self.winChipOnce = chip


class DizhuTaskConditionSegmentUp(TYTaskCondition):
    TYPE_ID = 'ddz.cond.segment.up'

    def __init__(self):
        super(DizhuTaskConditionSegmentUp, self).__init__()
        self.segment = 0

    def check(self, task, event):

        return (isinstance(event, SegmentTableWinloseEvent)
                and dizhu_util.get_user_segment(event.userId) >= self.segment
                )

    def _decodeFromDictImpl(self, d):
        self.segment = d.get('segment')
        if not isinstance(self.segment, int) and self.segment > 0:
            raise TYTaskConfException(d, 'segment must be int > 0')


class DizhuTaskInspectorPlay(TYTaskInspector):
    TYPE_ID = 'ddz.play'
    EVENT_GAMEID_MAP = {UserTablePlayEvent: (6,)}

    def __init__(self):
        super(DizhuTaskInspectorPlay, self).__init__(self.EVENT_GAMEID_MAP)

    def _processEventImpl(self, task, event):
        if isinstance(event, UserTablePlayEvent):
            return task.setProgress(task.progress + 1, event.timestamp)
        return False, 0


class DizhuTaskInspectorCall(TYTaskInspector):
    TYPE_ID = 'ddz.call'
    EVENT_GAMEID_MAP = {UserTableCallEvent: (6,)}

    def __init__(self):
        super(DizhuTaskInspectorCall, self).__init__(self.EVENT_GAMEID_MAP)

    def _processEventImpl(self, task, event):
        if isinstance(event, UserTableCallEvent):
            return task.setProgress(task.progress + 1, event.timestamp)
        return False, 0


class DizhuTaskInspectorWin(TYTaskInspector):
    TYPE_ID = 'ddz.win'
    EVENT_GAMEID_MAP = {UserTableWinloseEvent: (6,)}

    def __init__(self):
        super(DizhuTaskInspectorWin, self).__init__(self.EVENT_GAMEID_MAP)

    def _processEventImpl(self, task, event):
        if (isinstance(event, UserTableWinloseEvent)
            and event.winlose.isWin):
            if ftlog.is_debug():
                ftlog.debug('DizhuTaskInspectorWin._processEventImpl userId=', task.userId,
                            'taskId=', task.kindId,
                            'event=', event.__dict__,
                            'winlose=', event.winlose.__dict__)
            return task.setProgress(task.progress + 1, event.timestamp)
        return False, 0


class DizhuTaskInspectorSegmentWin(TYTaskInspector):
    TYPE_ID = 'ddz.segment.win'
    EVENT_GAMEID_MAP = {SegmentTableWinloseEvent: (6,)}

    def __init__(self):
        super(DizhuTaskInspectorSegmentWin, self).__init__(self.EVENT_GAMEID_MAP)

    def _processEventImpl(self, task, event):
        if (isinstance(event, SegmentTableWinloseEvent)
            and event.winlose.isWin):
            if ftlog.is_debug():
                ftlog.debug('DizhuTaskInspectorSegmentWin._processEventImpl userId=', task.userId,
                            'taskId=', task.kindId,
                            'event=', event.__dict__,
                            'winlose=', event.winlose.__dict__)
            return task.setProgress(task.progress + 1, event.timestamp)
        return False, 0


class DizhuTaskInspectorDizhuWin(TYTaskInspector):
    TYPE_ID = 'ddz.dizhu.win'
    EVENT_GAMEID_MAP = {UserTableWinloseEvent: (6,)}

    def __init__(self):
        super(DizhuTaskInspectorDizhuWin, self).__init__(self.EVENT_GAMEID_MAP)

    def _processEventImpl(self, task, event):
        if (isinstance(event, UserTableWinloseEvent)
            and event.winlose.isWin and event.winlose.isDizhu):
            if ftlog.is_debug():
                ftlog.debug('DizhuTaskInspectorDizhuWin._processEventImpl userId=', task.userId,
                            'taskId=', task.kindId,
                            'event=', event.__dict__,
                            'winlose=', event.winlose.__dict__)
            return task.setProgress(task.progress + 1, event.timestamp)
        return False, 0

class DizhuTaskInspectorNongminWin(TYTaskInspector):
    TYPE_ID = 'ddz.nongmin.win'
    EVENT_GAMEID_MAP = {UserTableWinloseEvent: (6,)}

    def __init__(self):
        super(DizhuTaskInspectorNongminWin, self).__init__(self.EVENT_GAMEID_MAP)

    def _processEventImpl(self, task, event):
        if (isinstance(event, UserTableWinloseEvent)
            and event.winlose.isWin and not event.winlose.isDizhu):
            if ftlog.is_debug():
                ftlog.debug('DizhuTaskInspectorNongminWin._processEventImpl userId=', task.userId,
                            'taskId=', task.kindId,
                            'event=', event.__dict__,
                            'winlose=', event.winlose.__dict__)
            return task.setProgress(task.progress + 1, event.timestamp)
        return False, 0



class DizhuTaskInspectorMatchWin(TYTaskInspector):
    TYPE_ID = 'ddz.match.win'
    EVENT_GAMEID_MAP = {MatchWinloseEvent: (6,)}

    def __init__(self):
        super(DizhuTaskInspectorMatchWin, self).__init__(self.EVENT_GAMEID_MAP)

    def _processEventImpl(self, task, event):
        if (isinstance(event, MatchWinloseEvent)
            and event.isWin):
            if ftlog.is_debug():
                ftlog.debug('DizhuTaskInspectorMatchWin._processEventImpl userId=', task.userId,
                            'taskId=', task.kindId,
                            'event=', event.__dict__)
            return task.setProgress(task.progress + 1, event.timestamp)
        return False, 0


class DizhuTaskInspectorWinlose(TYTaskInspector):
    TYPE_ID = 'ddz.winlose'
    EVENT_GAMEID_MAP = {UserTableWinloseEvent: (6,)}

    def __init__(self):
        super(DizhuTaskInspectorWinlose, self).__init__(self.EVENT_GAMEID_MAP)

    def _processEventImpl(self, task, event):
        if isinstance(event, UserTableWinloseEvent):
            if ftlog.is_debug():
                ftlog.debug('DizhuTaskInspectorWinlose._processEventImpl userId=', task.userId,
                            'taskId=', task.kindId,
                            'event=', event.__dict__,
                            'winlose=', event.winlose.__dict__)
            return task.setProgress(task.progress + 1, event.timestamp)
        return False, 0


class DizhuTaskInspectorSegmentWinlose(TYTaskInspector):
    TYPE_ID = 'ddz.segment.winlose'
    EVENT_GAMEID_MAP = {SegmentTableWinloseEvent: (6,)}

    def __init__(self):
        super(DizhuTaskInspectorSegmentWinlose, self).__init__(self.EVENT_GAMEID_MAP)

    def _processEventImpl(self, task, event):
        if isinstance(event, SegmentTableWinloseEvent):
            if ftlog.is_debug():
                ftlog.debug('DizhuTaskInspectorSegmentWinlose._processEventImpl userId=', task.userId,
                            'taskId=', task.kindId,
                            'event=', event.__dict__,
                            'winlose=', event.winlose.__dict__)
            return task.setProgress(task.progress + 1, event.timestamp)
        return False, 0



class DizhuTaskInspectorWinStreak(TYTaskInspector):
    TYPE_ID = 'ddz.winStreak'
    EVENT_GAMEID_MAP = {UserTableWinloseEvent: (6,)}

    def __init__(self):
        super(DizhuTaskInspectorWinStreak, self).__init__(self.EVENT_GAMEID_MAP)

    def _processEventImpl(self, task, event):
        if isinstance(event, UserTableWinloseEvent):
            if ftlog.is_debug():
                ftlog.debug('DizhuTaskInspectorWinStreak._processEventImpl userId=', task.userId,
                            'taskId=', task.kindId,
                            'event=', event.__dict__,
                            'winlose=', event.winlose.__dict__)
            if event.winlose.isWin:
                return task.setProgress(task.progress + 1, event.timestamp)
            return task.setProgress(0, event.timestamp)
        return False, 0


class DizhuTaskInspectorSegmentWinStreak(TYTaskInspector):
    TYPE_ID = 'ddz.segment.winStreak'
    EVENT_GAMEID_MAP = {SegmentTableWinloseEvent: (6,)}

    def __init__(self):
        super(DizhuTaskInspectorSegmentWinStreak, self).__init__(self.EVENT_GAMEID_MAP)

    def _processEventImpl(self, task, event):
        if isinstance(event, SegmentTableWinloseEvent):
            if ftlog.is_debug():
                ftlog.debug('DizhuTaskInspectorSegmentWinStreak._processEventImpl userId=', task.userId,
                            'taskId=', task.kindId,
                            'event=', event.__dict__,
                            'winlose=', event.winlose.__dict__)
            if event.winlose.isWin:
                return task.setProgress(task.progress + 1, event.timestamp)
            elif task.progress >= task.total:  # 已经完成,不清零
                return False, 0
            return task.setProgress(0, event.timestamp)
        return False, 0


class DizhuTaskInspectorOnlineWinStreak(TYTaskInspector):
    TYPE_ID = 'ddz.onlineWinStreak'
    EVENT_GAMEID_MAP = {UserTableWinloseEvent: (6,), EventUserLogin: (9999,)}

    def __init__(self):
        super(DizhuTaskInspectorOnlineWinStreak, self).__init__(self.EVENT_GAMEID_MAP)
        self.resetProgressWhenFinish = True

    def processEvent(self, task, event):
        eventType = type(event)
        if eventType not in self._interestEventMap:
            return False, 0
        if self._conditionList:
            for condition in self._conditionList:
                if not condition.check(task, event):
                    return False, 0
        changed, finishCount = self._processEventImpl(task, event)
        if changed:
            task.updateTime = pktimestamp.getCurrentTimestamp()
        return changed, finishCount

    def _processEventImpl(self, task, event):
        # ftlog.debug('DizhuTaskInspectorOnlineWinStreak._processEventImpl:test userId=', task.userId,
        #             '\ntask=', task.__dict__, "\ntask.taskKind", task.taskKind.__dict__,
        #             "\ntask.inspector=", task.taskKind.inspector.__dict__, "\ntaskKindPool", task.taskKind.taskKindPool.__dict__)

        if ftlog.is_debug():
            ftlog.debug('DizhuTaskInspectorOnlineWinStreak._processEventImpl userId=', task.userId, 'taskId=',
                        task.kindId, "task.progress=", task.progress, "event=", event, "event.gameId=", event.gameId)

        if isinstance(event, UserTableWinloseEvent):
            if event.winlose.isWin:
                return task.setProgress(task.progress + 1, event.timestamp)

            nextTaskKind = task.taskKind.taskKindPool.nextTaskKind(None)  # 将任务重置到第一个
            if nextTaskKind:
                newTask = nextTaskKind.newTask(task, event.timestamp)
                task.userTaskUnit.addTask(newTask)
                task.userTaskUnit.removeTask(task)

        if isinstance(event, EventUserLogin) and event.gameId == 9999:  # 重新登录后要重置记录到第一个
            nextTaskKind = task.taskKind.taskKindPool.nextTaskKind(None)
            if nextTaskKind:
                newTask = nextTaskKind.newTask(task, event.timestamp)
                task.userTaskUnit.addTask(newTask)
                task.userTaskUnit.removeTask(task)

        return False, 0


class DizhuTaskInspectorWinChip(TYTaskInspector):
    TYPE_ID = 'ddz.winChip'
    EVENT_GAMEID_MAP = {UserTableWinloseEvent: (6,)}

    def __init__(self):
        super(DizhuTaskInspectorWinChip, self).__init__(self.EVENT_GAMEID_MAP)

    def _processEventImpl(self, task, event):
        if (isinstance(event, UserTableWinloseEvent)
            and event.winlose.isWin):
            if ftlog.is_debug():
                ftlog.debug('DizhuTaskInspectorWinChip._processEventImpl userId=', task.userId,
                            'taskId=', task.kindId,
                            'event=', event.__dict__,
                            'winlose=', event.winlose.__dict__)
            return task.setProgress(task.progress + event.winlose.deltaChip, event.timestamp)
        return False, 0


class DizhuTaskInspectorWinChipOnce(TYTaskInspector):
    TYPE_ID = 'ddz.winChipOnce'
    EVENT_GAMEID_MAP = {UserTableWinloseEvent: (6,)}

    def __init__(self):
        super(DizhuTaskInspectorWinChipOnce, self).__init__(self.EVENT_GAMEID_MAP)

    def _processEventImpl(self, task, event):
        if (isinstance(event, UserTableWinloseEvent)
            and event.winlose.isWin):
            if ftlog.is_debug():
                ftlog.debug('DizhuTaskInspectorWinChipOnce._processEventImpl userId=', task.userId,
                            'taskId=', task.kindId,
                            'event=', event.__dict__,
                            'winlose=', event.winlose.__dict__)
            return task.setProgress(task.progress + 1, event.timestamp)
        return False, 0




class DizhuTaskInspectorLevel(TYTaskInspector):
    TYPE_ID = 'ddz.level'
    EVENT_GAMEID_MAP = {UserLevelGrowEvent: (6,), EventUserLogin: (6, 9999)}

    def __init__(self):
        super(DizhuTaskInspectorLevel, self).__init__(self.EVENT_GAMEID_MAP)

    def _processEventImpl(self, task, event):
        if isinstance(event, EventUserLogin):
            level = pkgamedata.getGameAttrInt(event.userId, event.gameId, 'level')
            return task.setProgress(level, event.timestamp)
        if isinstance(event, UserLevelGrowEvent):
            level = event.newLevel
            return task.setProgress(level, event.timestamp)
        return False, 0


class DizhuTaskInspectorLevelGrow(TYTaskInspector):
    TYPE_ID = 'ddz.levelGrow'
    EVENT_GAMEID_MAP = {UserLevelGrowEvent: (6,)}

    def __init__(self):
        super(DizhuTaskInspectorLevelGrow, self).__init__(self.EVENT_GAMEID_MAP)

    def _processEventImpl(self, task, event):
        if isinstance(event, UserLevelGrowEvent):
            ftlog.debug('DizhuTaskInspectorLevelGrow._processEventImpl taskId=', task.kindId,
                        'newLevel=', event.newLevel,
                        'oldLevel=', event.oldLevel)
            delta = max(0, event.newLevel - event.oldLevel)
            return task.setProgress(task.progress + delta, event.timestamp)
        return False, 0


class DizhuTaskInspectorTBoxLottery(TYTaskInspector):
    TYPE_ID = 'ddz.tboxLottery'
    EVENT_GAMEID_MAP = {UserTBoxLotteryEvent: (6,)}

    def __init__(self):
        super(DizhuTaskInspectorTBoxLottery, self).__init__(self.EVENT_GAMEID_MAP)

    def _processEventImpl(self, task, event):
        if isinstance(event, UserTBoxLotteryEvent):
            return task.setProgress(task.progress + 1, event.timestamp)
        return False, 0


class DizhuTaskInspectorChip(TYTaskInspector):
    TYPE_ID = 'ddz.chip'
    EVENT_GAMEID_MAP = {EventUserLogin: (6,), UserTableWinloseEvent: (6, 9999)}

    def __init__(self):
        super(DizhuTaskInspectorChip, self).__init__(self.EVENT_GAMEID_MAP)

    def _processEventImpl(self, task, event):
        if isinstance(event, EventUserLogin):
            return task.setProgress(pkuserchip.getChip(event.userId), event.timestamp)
        if isinstance(event, UserTableWinloseEvent):
            return task.setProgress(event.winlose.finalChip, event.timestamp)
        return False, 0


class DizhuTaskInspectorSkillScoreLevel(TYTaskInspector):
    TYPE_ID = 'ddz.skillScore.level'
    EVENT_GAMEID_MAP = {EventUserLogin: (6, 9999), SkillScoreIncrEvent: (6,)}

    def __init__(self):
        super(DizhuTaskInspectorSkillScoreLevel, self).__init__(self.EVENT_GAMEID_MAP)

    def _processEventImpl(self, task, event):
        if isinstance(event, EventUserLogin):
            score = skillscore.get_skill_score(event.userId)
            level = skillscore.get_skill_level(score)
            if ftlog.is_debug():
                ftlog.debug('DizhuTaskInspectorSkillScoreLevel._processEventImpl userId=', event.userId,
                            'skillscore=', score,
                            'level=', level)
            return task.setProgress(level, event.timestamp)
        if isinstance(event, SkillScoreIncrEvent):
            return task.setProgress(event.newLevel, event.timestamp)
        return False, 0


class DizhuTaskInspectorUseEmoticon(TYTaskInspector):
    TYPE_ID = 'ddz.emoticonUse'
    EVENT_GAMEID_MAP = {UseTableEmoticonEvent: (6,)}

    def __init__(self):
        super(DizhuTaskInspectorUseEmoticon, self).__init__(self.EVENT_GAMEID_MAP)
        self.emoticonSet = None

    def _processEventImpl(self, task, event):
        if ftlog.is_debug():
            ftlog.debug('DizhuTaskInspectorUseEmoticon',
                        'task.progress=', task.progress,
                        'timestamp=', event.timestamp,
                        'progressCount=', event.count)
        if isinstance(event, UseTableEmoticonEvent) and event.emoticon in self.emoticonSet:
            progressCount = max(1, event.count)
            return task.setProgress(task.progress + progressCount, event.timestamp)
        return False, 0

    def _decodeFromDictImpl(self, d):
        emoticons = d.get('emotions')
        if not emoticons or not isinstance(emoticons, list):
            raise TYTaskConfException(d, 'inspector.emotions must be list')
        for emoticon in emoticons:
            if not isstring(emoticon):
                raise TYTaskConfException(d, 'inspector.emotions.item must be string')
        self.emoticonSet = set(emoticons)


class DizhuTaskInspectorMyFTFinish(TYTaskInspector):
    '''
    朋友桌完成牌局
    '''
    TYPE_ID = 'ddz.myFTFinish'
    EVENT_GAMEID_MAP = {MyFTFinishEvent: (6,)}

    def __init__(self):
        super(DizhuTaskInspectorMyFTFinish, self).__init__(self.EVENT_GAMEID_MAP)

    def _processEventImpl(self, task, event):
        if isinstance(event, MyFTFinishEvent):
            if ftlog.is_debug():
                ftlog.debug('DizhuTaskInspectorMyFTFinish._processEventImpl userId=', task.userId,
                            'taskId=', task.kindId,
                            'event=', event.__dict__)
            return task.setProgress(task.progress + 1, event.timestamp)
        return False, 0


class DizhuTaskInspectorShareTable(TYTaskInspector):
    '''
    牌局分享
    '''
    TYPE_ID = 'ddz.sharetable'
    EVENT_GAMEID_MAP = {HallShareEvent: (9999,)}

    def __init__(self):
        super(DizhuTaskInspectorShareTable, self).__init__(self.EVENT_GAMEID_MAP)

    def _processEventImpl(self, task, event):
        if isinstance(event, HallShareEvent):
            # 确认是牌局分享的
            if event.shareid not in replay_service.getAllShareIds():
                return False, 0
            if ftlog.is_debug():
                ftlog.debug('DizhuTaskInspectorShareTable._processEventImpl userId=', task.userId,
                            'taskId=', task.kindId,
                            'event=', event.__dict__)
            return task.setProgress(task.progress + 1, event.timestamp)
        return False, 0


class DizhuTaskKindMedal(TYTaskKindSimple):
    TYPE_ID = 'ddz.task.medal'

    def __init__(self):
        super(DizhuTaskKindMedal, self).__init__()
        self.resetProgressWhenFinish = True

    def newTaskData(self):
        return TYTaskSimpleData()

    def newTaskForDecode(self):
        return TYTaskSimple(self)

    def newTask(self, prevTask, timestamp):
        task = TYTaskSimple(self)
        task.finishCount = 0
        task.finishTime = 0
        task.gotReward = 0
        task.updateTime = timestamp
        if prevTask and task.taskKind.inheritPrevTaskProgress:
            task.progress = prevTask.progress
        return task


class DizhuDailyTaskModel(TYHallTaskModel):
    def __init__(self, dailyTaskSystem, refreshTime, userTaskUnit):
        super(DizhuDailyTaskModel, self).__init__(dailyTaskSystem, userTaskUnit)
        self._refreshTime = refreshTime

    @property
    def refreshTime(self):
        return self._refreshTime

    def calcNextRefreshTime(self, timestamp):
        return self.subTaskSystem.calcNextRefreshTime(timestamp)

    def needRefresh(self, timestamp):
        if not self._refreshTime:
            return True
        if len(self.userTaskUnit.taskList) <= 0:
            return True
        todayRefreshTime = self.subTaskSystem.calcTodayRefreshTime(timestamp)
        ftlog.debug('DizhuDailyTaskSystem.needRefresh userId=', self.userId,
                    'timestamp=', datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S'),
                    'todayRefreshTime=', datetime.fromtimestamp(todayRefreshTime).strftime('%Y-%m-%d %H:%M:%S'),
                    'prevRefreshTime=', datetime.fromtimestamp(self._refreshTime).strftime('%Y-%m-%d %H:%M:%S'),
                    'ret=', self._refreshTime < todayRefreshTime and timestamp > todayRefreshTime)
        return self._refreshTime < todayRefreshTime and timestamp > todayRefreshTime

    def refresh(self, timestamp):
        if self.subTaskSystem.refreshContent:
            contentItemList = self.subTaskSystem.refreshContent.getItems()
            if contentItemList:
                userAssets = hallitem.itemSystem.loadUserAssets(self.userId)
                # TODO set eventId and args
                assetList = userAssets.consumeContentItemList(DIZHU_GAMEID, contentItemList, False,
                                                              timestamp, 'DTASK_CHANGE', 0)
                if assetList:
                    datachangenotify.sendDataChangeNotify(DIZHU_GAMEID, self.userId,
                                                          TYAssetUtils.getChangeDataNames(assetList))
        self._refreshImpl(timestamp)

    def _refreshImpl(self, timestamp):
        self._refreshTime = timestamp
        self.subTaskSystem._saveRefreshTime(self.userId, timestamp)
        self._userTaskUnit.removeAllTask()
        taskKinds = self.subTaskSystem._selectTaskKinds()
        if taskKinds:
            for taskKind in taskKinds:
                task = taskKind.newTask(None, timestamp)
                self._userTaskUnit.addTask(task)
        ftlog.debug('DizhuDailyTaskModel._refreshImpl gameId=', DIZHU_GAMEID,
                    'userId=', self.userId,
                    'timestamp=', datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S'),
                    'newTasks=', [taskKind.kindId for taskKind in taskKinds])


class DizhuTaskSimple(TYTask):
    def __init__(self, taskKind):
        assert (isinstance(taskKind, DizhuTaskKindSimple))
        super(DizhuTaskSimple, self).__init__(taskKind)

    def setProgress(self, progress, timestamp):
        if 0 < self.taskKind.totalLimit <= self.finishCount:
            return False, 0

        if progress < self.taskKind.count or self.finishCount > 0:
            if progress == self.progress:
                return False, 0

        self.updateTime = timestamp
        if progress < self.taskKind.count:
            self.progress = progress
            return True, 0

        if self.taskKind.resetProgressWhenFinish:
            self.progress = 0
        else:
            self.progress = self.taskKind.count
            # self.progress = progress
        self.finishCount += 1
        self.finishTime = timestamp
        return True, 1


class DizhuTaskKindSimple(TYTaskKind):
    TYPE_ID = 'ddz.task.simple'

    def __init__(self):
        super(DizhuTaskKindSimple, self).__init__()

    def newTaskData(self):
        return TYTaskSimpleData()

    def newTaskForDecode(self):
        return DizhuTaskSimple(self)

    def newTask(self, prevTask, timestamp):
        task = DizhuTaskSimple(self)
        task.finishCount = 0
        task.finishTime = 0
        task.gotReward = 0
        task.updateTime = timestamp
        if prevTask and task.taskKind.inheritPrevTaskProgress:
            task.progress = prevTask.progress
        return task

    def _decodeFromDictImpl(self, d):
        self.rewardPic = d.get('rewardPic', None)


class DizhuTaskFinishEvent(UserEvent):
    '''
    任务完成Event
    '''

    def __init__(self, gameId, userId, task):
        super(DizhuTaskFinishEvent, self).__init__(userId, gameId)
        self.task = task


class DizhuDailyTaskSystem(TYHallSubTaskSystem):
    def __init__(self):
        super(DizhuDailyTaskSystem, self).__init__(DIZHU_GAMEID)
        self._refreshContent = None
        self._refreshHour = None
        self._selectPolicy = None

    @property
    def refreshContent(self):
        return self._refreshContent

    @property
    def refreshHour(self):
        return self._refreshHour

    def reloadConf(self, conf):
        refreshContent = conf.get('refreshContent')
        if refreshContent is not None:
            refreshContent = TYContentRegister.decodeFromDict(refreshContent)
        refreshHour = conf.get('refreshHour')
        if (not isinstance(refreshHour, int)
            or refreshHour < 0
            or refreshHour >= 24):
            raise TYTaskConfException(conf, 'refreshHour must [0~24)')
        starCountList = conf.get('starCountList')
        if not starCountList or not isinstance(starCountList, list):
            raise TYTaskConfException(conf, 'starCountList must be not empty list')
        selectPolicy = {}
        for starCount in starCountList:
            selectPolicy[starCount['star']] = (starCount['count'], [])

        self._refreshContent = refreshContent
        self._refreshHour = refreshHour
        self._selectPolicy = selectPolicy
        self._initSelectPolicy()

        ftlog.debug('DizhuDailyTaskSystem.reloadConf successed refreshHour=', refreshHour)

    def calcTodayRefreshTime(self, timestamp):
        nowDT = datetime.fromtimestamp(timestamp)
        refreshDT = nowDT.replace(hour=self.refreshHour, minute=0, second=0, microsecond=0)
        return int(time.mktime(refreshDT.timetuple()))

    def calcNextRefreshTime(self, timestamp):
        todayRefreshTime = self.calcTodayRefreshTime(timestamp)
        if timestamp > todayRefreshTime:
            return todayRefreshTime + 86400
        return todayRefreshTime

    def _loadTaskModel(self, userTaskUnit, timestamp):
        refreshTime = self._loadRefreshTime(userTaskUnit.userId)
        model = DizhuDailyTaskModel(self, refreshTime, userTaskUnit)
        if model.needRefresh(timestamp):
            model._refreshImpl(timestamp)
        return model

    def _loadRefreshTime(self, userId):
        d = pkgamedata.getGameAttrJson(userId, DIZHU_GAMEID, 'medal2.daily.status')
        return d.get('changeTime', 0) if d else 0

    def _saveRefreshTime(self, userId, refreshTime):
        jstr = json.dumps({'changeTime': refreshTime})
        return pkgamedata.setGameAttr(userId, DIZHU_GAMEID, 'medal2.daily.status', jstr)

    def _onTaskUnitLoadedImpl(self, taskUnit):
        if self._selectPolicy:
            self._initSelectPolicy()

    def _onTaskFinished(self, task, timestamp):
        from dizhu.game import TGDizhu
        ebus = TGDizhu.getEventBus()
        ebus.publishEvent(DizhuTaskFinishEvent(self.gameId, task.userId, task))

    def _onGotTaskReward(self, task, assetList, timestamp):
        pass

    def _initSelectPolicy(self):
        if self.taskUnitValid():
            for taskKind in self._taskUnit.taskKindMap.values():
                item = self._selectPolicy.get(taskKind.star)
                if item:
                    item[1].append(taskKind)

    def _randomTask(self, taskKindList, count):
        ret = []
        if len(taskKindList) == count:
            ret.extend(taskKindList)
            return ret
        if len(taskKindList) > 0:
            random.shuffle(taskKindList)
            for i in xrange(min(count, len(taskKindList))):
                ret.append(taskKindList[i])
        return ret

    def _selectTaskKinds(self):
        ret = []
        for star, (count, taskKindList) in self._selectPolicy.iteritems():
            ftlog.debug('TYHallDailyTaskUnit._selectTaskKinds star=', star,
                        'count=', count, 'kindIds=', [taskKind.kindId for taskKind in taskKindList])
            ret.extend(self._randomTask(taskKindList, count))
        ftlog.debug('TYHallDailyTaskUnit._selectTaskKinds kindIds=', [taskKind.kindId for taskKind in ret])
        return ret


class DizhuMedalException(TYBizException):
    def __init__(self, ec, message):
        super(DizhuMedalException, self).__init__(ec, message)


class DizhuMedalAlreadyWeardException(DizhuMedalException):
    def __init__(self, taskId):
        super(DizhuMedalAlreadyWeardException, self).__init__(-1, '勋章已经佩戴')
        self.taskId = taskId


class DizhuMedalNotWeardException(DizhuMedalException):
    def __init__(self, taskId):
        super(DizhuMedalNotWeardException, self).__init__(-1, '勋章没有佩戴')
        self.taskId = taskId


class DizhuMedalNotGetException(DizhuMedalException):
    def __init__(self, taskId):
        super(DizhuMedalNotGetException, self).__init__(-1, '勋章还没有获得')
        self.taskId = taskId


class DizhuMedalTaskModel(TYHallTaskModel):
    def __init__(self, medalTaskSystem, wearedId, userTaskUnit):
        super(DizhuMedalTaskModel, self).__init__(medalTaskSystem, userTaskUnit)
        self._wearedId = wearedId

    @property
    def wearedId(self):
        return self._wearedId

    def wear(self, task):
        assert (task.userTaskUnit == self.userTaskUnit)
        if self._wearedId == task.kindId:
            raise DizhuMedalAlreadyWeardException(task.kindId)
        if not task.isFinished:
            raise DizhuMedalNotGetException(task.kindId)
        self._wearedId = task.kindId
        self.subTaskSystem._saveWearedId(self.userId, task.kindId)

    def unwear(self, task):
        assert (task.userTaskUnit == self.userTaskUnit)
        if self._wearedId != task.kindId:
            raise DizhuMedalNotWeardException(task.kindId)
        self._weardTaskId = 0
        self.subTaskSystem._saveWearedId(self.userId, task.kindId)


class DizhuMedalTaskSystem(TYHallSubTaskSystem):
    def __init__(self):
        super(DizhuMedalTaskSystem, self).__init__(DIZHU_GAMEID)

    def _loadTaskModel(self, userTaskUnit, timestamp):
        for taskKind in self.taskUnit.taskKindMap.values():
            if not userTaskUnit.findTask(taskKind.kindId):
                userTaskUnit.addTask(taskKind.newTask(None, timestamp))
        ftlog.debug('DizhuMedalTaskSystem._loadTaskModel userId=', userTaskUnit.userId,
                    'taskIds=', [task.kindId for task in userTaskUnit.taskList])
        wearedId = self._loadWearedId(userTaskUnit.userId)
        return DizhuMedalTaskModel(self, wearedId, userTaskUnit)

    def _onTaskUnitLoadedImpl(self, taskUnit):
        pass

    def _onTaskFinished(self, task, timestamp):
        # TODO publish event
        pass

    def _onGotTaskReward(self, task, assetList, timestamp):
        # TODO 
        pass

    def _loadWearedId(self, userId):
        d = pkgamedata.getGameAttrJson(userId, DIZHU_GAMEID, 'medal2.medal.status')
        return d.get('wear', 0) if d else 0

    def _saveWearedId(self, userId, wearedId):
        jstr = json.dumps({'wear': wearedId})
        return pkgamedata.setGameAttr(userId, DIZHU_GAMEID, 'medal2.medal.status', jstr)


class DizhuTableTaskModel(TYHallTaskModel):
    def __init__(self, tableTaskSystem, userTaskUnit):
        super(DizhuTableTaskModel, self).__init__(tableTaskSystem, userTaskUnit)


class DizhuTableTaskSystem(TYHallSubTaskSystem):
    def __init__(self):
        super(DizhuTableTaskSystem, self).__init__(DIZHU_GAMEID)

    def _loadTaskModel(self, userTaskUnit, timestamp):
        if ftlog.is_debug():
            ftlog.debug('DizhuTableTaskSystem._loadTaskModel userId=', userTaskUnit.userId,
                        'taskIds=', [task.kindId for task in userTaskUnit.taskList])
        self._initPools(userTaskUnit, timestamp)
        if ftlog.is_debug():
            ftlog.debug('DizhuTableTaskSystem._laodTaskModel',
                        'userTaskUnit=', userTaskUnit,
                        caller=self)
        return DizhuTableTaskModel(self, userTaskUnit)

    def _initPools(self, userTaskUnit, timestamp):
        # 汇总到pool
        poolTaskMap = {pool: [] for pool in userTaskUnit.taskUnit.poolList}
        for task in userTaskUnit.taskList:
            taskList = poolTaskMap.get(task.taskKind.taskKindPool)
            if taskList is None:
                taskList = []
                poolTaskMap[task.taskKind.taskKindPool] = taskList
            taskList.append(task)

        for pool, taskList in poolTaskMap.iteritems():
            # 没有任务的初始化任务
            if not taskList:
                nextTaskKind = pool.nextTaskKind(None)
                if nextTaskKind:
                    task = nextTaskKind.newTask(None, timestamp)
                    userTaskUnit.addTask(task)
                    if ftlog.is_debug():
                        ftlog.debug('DizhuTableTaskSystem._initPools userId=', userTaskUnit.userId,
                                    'addTask=', (task.kindId))
                continue

            # 已经领过奖励的删除
            execTask = None
            gotRewardTask = None

            while (len(taskList) > 0):
                task = taskList[-1]
                del taskList[-1]
                if task.gotReward != 0:
                    if not gotRewardTask:
                        gotRewardTask = task
                    userTaskUnit.removeTask(task)
                    if ftlog.is_debug():
                        ftlog.debug('DizhuTableTaskSystem._initPools userId=', userTaskUnit.userId,
                                    'removeGotRewardTask=', (task.kindId))
                else:
                    if not execTask:
                        # 要保留的任务
                        execTask = task
                    else:
                        # 删除多余的任务，因为每个pool只能有一个任务
                        userTaskUnit.removeTask(task)
                        if ftlog.is_debug():
                            ftlog.debug('DizhuTableTaskSystem._initPools userId=', userTaskUnit.userId,
                                        'removeTask=', (task.kindId))
            if not execTask:
                nextTaskKind = pool.nextTaskKind(gotRewardTask.taskKind)
                if nextTaskKind:
                    newTask = nextTaskKind.newTask(gotRewardTask, timestamp)
                    userTaskUnit.addTask(newTask)
                    if ftlog.is_debug():
                        ftlog.debug('DizhuTableTaskSystem._initPools userId=', userTaskUnit.userId,
                                    'addTask=', (newTask.kindId))

    def _onTaskUnitLoadedImpl(self, taskUnit):
        pass

    def _onTaskFinished(self, task, timestamp):
        # TODO publish event
        # 通知牌桌任务有新完成的
        ftlog.debug("DizhuTableTaskSystem._onTaskFinished | userId=", task.userId, "kindId=", task.kindId, "attrs=",
                    task.__dict__)
        mo = MsgPack()
        mo.setCmd('table_task')
        mo.setResult('gameId', 6)
        mo.setResult('userId', task.userId)
        mo.setResult('taskName', task.taskKind.name)
        mo.setResult('action', 'taskFindished')
        router.sendToUser(mo, task.userId)

    def _onGotTaskReward(self, task, assetList, timestamp):
        nextTaskKind = task.taskKind.taskKindPool.nextTaskKind(task.taskKind)
        if nextTaskKind:
            newTask = nextTaskKind.newTask(task, timestamp)
            task.userTaskUnit.addTask(newTask)
            task.userTaskUnit.removeTask(task)


# 新手任务
class DizhuNewbieTaskModel(TYHallTaskModel):
    def __init__(self, taskSystem, usertTaskUnit):
        super(DizhuNewbieTaskModel, self).__init__(taskSystem, usertTaskUnit)


class DizhuNewbieTaskSystem(TYHallSubTaskSystem):
    def __init__(self):
        super(DizhuNewbieTaskSystem, self).__init__(DIZHU_GAMEID)

    @property
    def getTaskKindList(self):
        return self.taskUnit.poolList[0].taskKindList

    @property
    def taskKindCount(self):
        return len(self.taskUnit.poolList[0].taskKindList)

    def getTaskInfo(self, userId, roomPlayTimes=None):
        '''
        新手任务信息，table_info协议调用
        '''
        if not isNewer(userId):
            return None
        kindId, completedList, completed = self.getTaskStatus(userId, self.getUserTaskUnit(userId))
        if completed or len(completedList) >= self.taskKindCount \
                or pktimestamp.getCurrentTimestamp() >= self.getDeadlineTimestamp(userId):
            return None
        curTask = self.getTaskByKindId(userId, kindId)
        if curTask is None:
            return None
        if ftlog.is_debug():
            ftlog.debug('DizhuNewbieTaskSystem.getTaskInfo',
                        'userId=', userId,
                        'kindId=', kindId,
                        'curTask=', curTask,
                        'completelist=', completedList,
                        caller=self)
        allTasks = [t.kindId for t in self.getTaskKindList]
        curIndex = allTasks.index(curTask.kindId)
        finisedTasks = allTasks[:curIndex+1]
        finalRewordConf = dizhuconf.getNewbieTaskConf().get('rewardContent', {})
        finalRewordContent = TYContentRegister.decodeFromDict(finalRewordConf)

        showIcon = finalRewordConf.get('img') if finalRewordConf else None
        ret = []
        for item in finalRewordContent.getItems():
            assetKind = hallitem.itemSystem.findAssetKind(item.assetKindId)
            img = showIcon if showIcon else assetKind.pic
            ret.append({'name': assetKind.displayName, 'img': img, 'count': item.count, 'itemId': item.assetKindId})

        tasksInfo = {
            'details': self._encodeTaskList(userId, list(set(finisedTasks))),
            'final': ret,
            'count': self.taskKindCount,
            'deadline': max(self.getDeadlineTimestamp(userId) - pktimestamp.getCurrentTimestamp(), 0),
            'showTips': 1 if roomPlayTimes in dizhuconf.getNewbieTaskConf().get('showTipsPt', []) else 0,
            'roomPlayTimes': roomPlayTimes if roomPlayTimes else 0,
            'showIcon': dizhuconf.getNewbieTaskConf().get('showIcon', '')
        }
        return tasksInfo

    def _checkKindIdList(self, userId, historylist):
        addFlag = 0
        for kindId in set(historylist):
            task = self.getTaskByKindId(userId, kindId)
            if not task:
                taskKind = self.taskUnit.poolList[0].findTaskKind(kindId)
                if taskKind:
                    addFlag = 1
                    task = taskKind.newTask(None, pktimestamp.getCurrentTimestamp())
                    self.getUserTaskUnit(userId).addTask(task)
                    task.finishCount = task.taskKind.totalLimit
                    task.progress = task.taskKind.count
                    task.finishTime = pktimestamp.getCurrentTimestamp()
                    task.gotReward = 1
                    task.userTaskUnit.updateTask(task)
        return addFlag


    def _encodeTaskList(self, userId, historylist):
        details = []
        for index, kindId in enumerate(historylist[:-1]):
            task = self.getTaskByKindId(userId, kindId)
            if not task:
                taskKind = self.taskUnit.poolList[0].findTaskKind(kindId)
                preTaskKind = None if index == 0 else historylist[:-1][index-1]
                if taskKind:
                    task = taskKind.newTask(preTaskKind, pktimestamp.getCurrentTimestamp())
                    self.getUserTaskUnit(userId).addTask(task)

            if task and task.taskKind:
                details.append({'name': task.taskKind.name,
                                'finish': task.taskKind.count,
                                'total': task.taskKind.count,
                                'desc': task.taskKind.desc,
                                'reward': self._encodeRewardContent(task.taskKind.rewardContent)
                                })
        task = self.getTaskByKindId(userId, historylist[-1])
        if task and task.taskKind:
            details.append({'name': task.taskKind.name,
                            'finish': task.progress,
                            'total': task.taskKind.count,
                            'desc': task.taskKind.desc,
                            'reward': self._encodeRewardContent(task.taskKind.rewardContent)
                            })
        finishCount = len(historylist)
        for taskKind in self.taskUnit.poolList[0].taskKindList[finishCount:]:
            details.append({'name': taskKind.name,
                            'finish': 0,
                            'total': taskKind.count,
                            'desc': taskKind.desc,
                            'reward': self._encodeRewardContent(taskKind.rewardContent)
                            })
        return details

    def getTaskProgress(self, userId):
        '''
        获取玩家新手任务进度，包括当前进行的任务进度、是否完成所有任务
        如果当前任务完成，则发送奖励
        如果所有任务也完成，则发送终极奖励
        '''
        if self.expired(userId):
            return None

        kindId, completedList, completed = self.getTaskStatus(userId)
        curTask = self.getTaskByKindId(userId, kindId)
        if curTask is None:
            # 任务完成或者任务过期会把所有新手任务都删掉，所以这两种情况下都会走到这里，不需要单独处理
            return None

        if completed:
            return None

        if len(completedList) >= self.taskKindCount:
            return None

        currentTimestamp = pktimestamp.getCurrentTimestamp()
        final = 0
        if curTask and curTask.gotReward == 0 and curTask.isFinished:
            # 发送完成当前任务的奖励
            self._sendTaskReward(curTask, currentTimestamp, 'NEWBIE_TASK', curTask.kindId)
            curTask.gotReward = 1
            curTask.userTaskUnit.updateTask(curTask)
            # 尝试激活下一个任务
            final = self._tryToActiveNextTask(userId, curTask, completedList, currentTimestamp)

        if ftlog.is_debug():
            ftlog.debug('getTaskProgress',
                        'userId=', userId,
                        'curTask=', curTask,
                        'completedList=', completedList,
                        'taskKindCount=', self.taskKindCount,
                        'curTaskId=', curTask.kindId,
                        'gotReward=', curTask.gotReward,
                        'progress=', curTask.progress,
                        'final=', final)
        curInfo = {
            'index': min(len(completedList) + 1, self.taskKindCount),
            'kindId': curTask.kindId,
            'total': curTask.taskKind.count,
            'finish': curTask.progress
        }
        return {'cur': curInfo, 'final': final}

    def _tryToActiveNextTask(self, userId, task, completedList, timestamp):
        """
        当前任务完成，激活下一个任务
        """
        nextTaskKind = task.taskKind.taskKindPool.nextTaskKind(task.taskKind)

        if ftlog.is_debug():
            ftlog.debug('DizhuNewbieTaskSystem.activeNextTask | userId=', userId,
                        'curTaskKindId=', task.kindId,
                        'completedList=', completedList,
                        'nextTaskKindId=', nextTaskKind.kindId if nextTaskKind else None)

        if len(completedList) + 1 < self.taskKindCount:
            # 激活下一个任务为当前进行的任务
            self.setTaskStatus(userId, nextTaskKind.kindId, completedList+[task.kindId])
            newTask = nextTaskKind.newTask(task, timestamp)
            task.userTaskUnit.addTask(newTask)
            return 0
        else:
            # 没有下一个任务了，所有任务都完成了, 发送完成所有任务奖励
            self.setTaskStatus(userId, task.kindId, completedList+[task.kindId], completed=1)
            finalReward = dizhuconf.getNewbieTaskConf().get('rewardContent', {})
            rewardMail = dizhuconf.getNewbieTaskConf().get('rewardMail', '')
            dizhu_util.sendReward(userId, finalReward, rewardMail, 'NEWBIE_TASK_FINAL_REWARD', task.kindId)
            return 1

    @classmethod
    def _encodeRewardContent(cls, rewardContent):
        if ftlog.is_debug():
            ftlog.debug('_encodeRewardContent, rewardContent.getItems=', rewardContent.getItems())
        ret = []
        for item in rewardContent.getItems():
            # ftlog.info('item=', item, 'assetKindId=', item.assetKindId)
            assetKind = hallitem.itemSystem.findAssetKind(item.assetKindId)
            ret.append({'name': assetKind.displayName, 'img': assetKind.pic, 'count': item.count, 'itemId': item.assetKindId})
        return ret

    def getTaskByKindId(self, userId, kindId):
        userTaskUnit = self.taskUnit.taskSystem.loadUserTaskUnit(
            userId,
            self.taskUnit,
            pktimestamp.getCurrentTimestamp()
        )
        ftlog.debug('getTaskByKindId',
                    'userId=', userId,
                    'kindId=', kindId,
                    'userTaskUnit=', userTaskUnit)
        return userTaskUnit.findTask(kindId)

    def getUserTaskUnit(self, userId):
        userTaskUnit = self.taskUnit.taskSystem.loadUserTaskUnit(
            userId,
            self.taskUnit,
            pktimestamp.getCurrentTimestamp()
        )
        return userTaskUnit

    @classmethod
    def completedCount(cls, userTaskList):
        count = 0
        for task in userTaskList:
            if task.gotReward != 0:
                count += 1
        return count

    def _loadTaskModel(self, userTaskUnit, timestamp):
        clientVer = SessionDizhuVersion.getVersionNumber(userTaskUnit.userId)
        if clientVer >= 3.822 and isNewer(userTaskUnit.userId):
            self._loadTaskFromPool(userTaskUnit, timestamp)
            curKindId, _, _ = self.getTaskStatus(userTaskUnit.userId, userTaskUnit)
            if curKindId == 0:
                firstKindId = self.taskUnit.poolList[0].taskKindList[0].kindId
                self.setTaskStatus(userTaskUnit.userId, firstKindId, [])
            if ftlog.is_debug():
                ftlog.debug('DizhuNewbieTaskSystem._loadTaskModel userId=', userTaskUnit.userId,
                            'taskIds=', [task.kindId for task in userTaskUnit.taskList],
                            'poolList=', userTaskUnit.taskUnit.poolList,
                            'curKindId=', curKindId,
                            'taskKindCount=', self.taskKindCount,
                            'completeCount=', self.completedCount(userTaskUnit.taskList),
                            'clientVer=', clientVer,
                            caller=self)
        return DizhuNewbieTaskModel(self, userTaskUnit)

    def _loadTaskFromPool(self, userTaskUnit, timestamp):
        poolTaskMap = {pool: [] for pool in userTaskUnit.taskUnit.poolList}
        if ftlog.is_debug():
            ftlog.debug('DizhuNewbieTaskSystem._initPools',
                        'userTaskUnit=', userTaskUnit.taskUnit,
                        'userTaskPoolList=', userTaskUnit.taskUnit.poolList,
                        'userTaskList=', userTaskUnit.taskList,
                        caller=self)
        for task in userTaskUnit.taskList:
            ftlog.debug('taskKindPool=', task.taskKind.taskKindPool)
            taskList = poolTaskMap.get(task.taskKind.taskKindPool)
            if taskList is None:
                taskList = []
                poolTaskMap[task.taskKind.taskKindPool] = taskList
            taskList.append(task)

        for pool, taskList in poolTaskMap.iteritems():
            # 初始化每个pool中未初始化的任务
            if not taskList:
                nextTaskKind = pool.nextTaskKind(None)
                if not nextTaskKind:
                    continue
                task = nextTaskKind.newTask(None, timestamp)
                userTaskUnit.addTask(task)
                ftlog.info('_loadTaskFromPool, add task:', task.kindId)

        if ftlog.is_debug():
            ftlog.debug('after init pools, userId=', userTaskUnit.userId,
                        'userTaskList=', [task.kindId for task in userTaskUnit.taskList])

    @classmethod
    def setTaskStatus(cls, userId, curTaskKindId, completedList, completed=0):
        if ftlog.is_debug():
            ftlog.debug('setTaskStatus',
                        'userId=', userId,
                        'curTaskId=', curTaskKindId,
                        'completedList=', completedList,
                        caller=cls)
        jstr = json.dumps({'curTaskKindId': curTaskKindId, 'completedList': list(set(completedList)), 'completed': completed}) # 去重
        return pkgamedata.setGameAttr(userId, DIZHU_GAMEID, 'newbie.task.status', jstr)

    @classmethod
    def getTaskStatus(cls, userId, userTaskUnit=None):
        taskdata = pkgamedata.getGameAttrJson(userId, DIZHU_GAMEID, 'newbie.task.status')
        if ftlog.is_debug():
            ftlog.debug('getTaskStatus, taskdata=', taskdata, 'userId=', userId, 'userTaskUnit=', userTaskUnit)
        completed = 0
        # 删除添加任务需要进行校验处理， 先获取用户所有任务ID
        curTaskKindId, completedList = 0, []
        if taskdata:
            curTaskKindId, completedList, finished = taskdata.get('curTaskKindId'), taskdata.get('completedList'), taskdata.get('completed')
            if finished:
                return curTaskKindId, completedList, finished
        if taskdata and userTaskUnit:
            allTasks = userTaskUnit.taskUnit.poolList[0].taskKindList
            allTasksIds = [t.kindId for t in allTasks]

            # 删除了一个已完成的任务， 包括当前任务
            removeFlag = 0
            removedTaskKind = []
            for completedTaskKind in completedList:
                if completedTaskKind not in allTasksIds:
                    removeFlag = 1
                    removedTaskKind.append(completedTaskKind)
            for removed in removedTaskKind:
                completedList.remove(removed)

            if curTaskKindId not in allTasksIds:
                removeFlag = 1
                if not completedList:
                    curTaskKindId = allTasks[0].kindId
                elif userTaskUnit.taskUnit.poolList[0].findTaskKind(completedList[-1]).nextTaskKind:
                    curTaskKindId = userTaskUnit.taskUnit.poolList[0].findTaskKind(completedList[-1]).nextTaskKind.kindId
                    # 创建用户taskUint
                    task = userTaskUnit.taskUnit.poolList[0].findTaskKind(completedList[-1]).nextTaskKind.newTask(None, pktimestamp.getCurrentTimestamp())
                    userTaskUnit.addTask(task)
                else:
                    curTaskKindId = userTaskUnit.taskUnit.poolList[0].findTaskKind(completedList[-1]).kindId
            global newbieTaskSystem
            curTaskKindIdIndex = allTasksIds.index(curTaskKindId)
            # 检查是否增加或者删除了一个任务
            if newbieTaskSystem._checkKindIdList(userId, list(set(allTasksIds[:curTaskKindIdIndex]))) or removeFlag:
                # 判断有没有完成
                lastTask = userTaskUnit.findTask(allTasksIds[-1])
                if lastTask and lastTask.gotReward:
                    completed = 1
                jstr = json.dumps({'curTaskKindId': curTaskKindId, 'completedList': list(set(allTasksIds[:curTaskKindIdIndex])), 'completed': completed})  # 去重
                pkgamedata.setGameAttr(userId, DIZHU_GAMEID, 'newbie.task.status', jstr)
                newbieTaskSystem._loadTaskFromPool(userTaskUnit, pktimestamp.getCurrentTimestamp())

        return curTaskKindId, completedList, completed

    @classmethod
    def getDeadlineTimestamp(cls, userId):
        deadline = pkgamedata.getGameAttr(userId, DIZHU_GAMEID, 'newbie.task.deadline')
        return deadline if deadline else pktimestamp.getCurrentTimestamp()

    @classmethod
    def setDeadlineTimestamp(cls, userId, timestamp):
        pkgamedata.setGameAttr(userId, DIZHU_GAMEID, 'newbie.task.deadline', timestamp)

    @classmethod
    def expired(cls, userId):
        return pktimestamp.getCurrentTimestamp() >= cls.getDeadlineTimestamp(userId)

    def _onTaskUnitLoadedImpl(self, taskUnit):
        pass

    def _onTaskFinished(self, task, timestamp):
        # 通知牌桌任务有新完成的
        ftlog.debug("DizhuNewbieTaskSystem._onTaskFinished | userId=", task.userId,
                    "kindId=", task.kindId,
                    "attrs=", task.__dict__)
        """
        mo = MsgPack()
        mo.setCmd('table_task')
        mo.setResult('gameId', DIZHU_GAMEID)
        mo.setResult('userId', task.userId)
        mo.setResult('taskName', task.taskKind.name)
        mo.setResult('action', 'taskFindished')
        router.sendToUser(mo, task.userId)
        """


def _registerClasses():
    ftlog.debug('dizhutask._registerClasses')
    TYTaskConditionRegister.registerClass(DizhuTaskConditionChunTian.TYPE_ID, DizhuTaskConditionChunTian)
    TYTaskConditionRegister.registerClass(DizhuTaskConditionZhaDan.TYPE_ID, DizhuTaskConditionZhaDan)
    TYTaskConditionRegister.registerClass(DizhuTaskConditionWindoubles.TYPE_ID, DizhuTaskConditionWindoubles)
    TYTaskConditionRegister.registerClass(DizhuTaskConditionSlam.TYPE_ID, DizhuTaskConditionSlam)
    TYTaskConditionRegister.registerClass(DizhuTaskConditionDizhu.TYPE_ID, DizhuTaskConditionDizhu)
    TYTaskConditionRegister.registerClass(DizhuTaskConditionMatchId.TYPE_ID, DizhuTaskConditionMatchId)
    TYTaskConditionRegister.registerClass(DizhuTaskConditionRoomId.TYPE_ID, DizhuTaskConditionRoomId)
    TYTaskConditionRegister.registerClass(DizhuTaskConditionGrabDizhu.TYPE_ID, DizhuTaskConditionGrabDizhu)
    TYTaskConditionRegister.registerClass(DizhuTaskConditionBaseCardType.TYPE_ID, DizhuTaskConditionBaseCardType)
    TYTaskConditionRegister.registerClass(DizhuTaskConditionOutWinCardType.TYPE_ID, DizhuTaskConditionOutWinCardType)
    TYTaskConditionRegister.registerClass(DizhuTaskConditionPlayMode.TYPE_ID, DizhuTaskConditionPlayMode)
    TYTaskConditionRegister.registerClass(DizhuTaskConditionMatchRank.TYPE_ID, DizhuTaskConditionMatchRank)
    TYTaskConditionRegister.registerClass(DizhuTaskConditionOnceWinChip.TYPE_ID, DizhuTaskConditionOnceWinChip)
    TYTaskConditionRegister.registerClass(DizhuTaskConditionSegmentUp.TYPE_ID, DizhuTaskConditionSegmentUp)

    TYTaskInspectorRegister.registerClass(DizhuTaskInspectorPlay.TYPE_ID, DizhuTaskInspectorPlay)
    TYTaskInspectorRegister.registerClass(DizhuTaskInspectorCall.TYPE_ID, DizhuTaskInspectorCall)
    TYTaskInspectorRegister.registerClass(DizhuTaskInspectorWin.TYPE_ID, DizhuTaskInspectorWin)
    TYTaskInspectorRegister.registerClass(DizhuTaskInspectorWinlose.TYPE_ID, DizhuTaskInspectorWinlose)
    TYTaskInspectorRegister.registerClass(DizhuTaskInspectorWinStreak.TYPE_ID, DizhuTaskInspectorWinStreak)
    TYTaskInspectorRegister.registerClass(DizhuTaskInspectorOnlineWinStreak.TYPE_ID,
                                          DizhuTaskInspectorOnlineWinStreak)  # Add
    TYTaskInspectorRegister.registerClass(DizhuTaskInspectorDizhuWin.TYPE_ID, DizhuTaskInspectorDizhuWin)
    TYTaskInspectorRegister.registerClass(DizhuTaskInspectorNongminWin.TYPE_ID, DizhuTaskInspectorNongminWin)

    TYTaskInspectorRegister.registerClass(DizhuTaskInspectorMyFTFinish.TYPE_ID, DizhuTaskInspectorMyFTFinish)  # Add
    TYTaskInspectorRegister.registerClass(DizhuTaskInspectorShareTable.TYPE_ID, DizhuTaskInspectorShareTable)  # Add

    TYTaskInspectorRegister.registerClass(DizhuTaskInspectorWinChip.TYPE_ID, DizhuTaskInspectorWinChip)
    TYTaskInspectorRegister.registerClass(DizhuTaskInspectorWinChipOnce.TYPE_ID, DizhuTaskInspectorWinChipOnce)
    TYTaskInspectorRegister.registerClass(DizhuTaskInspectorMatchWin.TYPE_ID, DizhuTaskInspectorMatchWin)
    TYTaskInspectorRegister.registerClass(DizhuTaskInspectorLevel.TYPE_ID, DizhuTaskInspectorLevel)
    TYTaskInspectorRegister.registerClass(DizhuTaskInspectorLevelGrow.TYPE_ID, DizhuTaskInspectorLevelGrow)
    TYTaskInspectorRegister.registerClass(DizhuTaskInspectorTBoxLottery.TYPE_ID, DizhuTaskInspectorTBoxLottery)
    TYTaskInspectorRegister.registerClass(DizhuTaskInspectorChip.TYPE_ID, DizhuTaskInspectorChip)
    TYTaskInspectorRegister.registerClass(DizhuTaskInspectorUseEmoticon.TYPE_ID, DizhuTaskInspectorUseEmoticon)
    TYTaskInspectorRegister.registerClass(DizhuTaskInspectorSkillScoreLevel.TYPE_ID, DizhuTaskInspectorSkillScoreLevel)
    TYTaskInspectorRegister.registerClass(DizhuTaskInspectorSegmentWin.TYPE_ID, DizhuTaskInspectorSegmentWin)
    TYTaskInspectorRegister.registerClass(DizhuTaskInspectorSegmentWinStreak.TYPE_ID, DizhuTaskInspectorSegmentWinStreak)
    TYTaskInspectorRegister.registerClass(DizhuTaskInspectorSegmentWinlose.TYPE_ID, DizhuTaskInspectorSegmentWinlose)

    TYTaskKindRegister.registerClass(DizhuTaskKindMedal.TYPE_ID, DizhuTaskKindMedal)
    TYTaskKindRegister.registerClass(DizhuTaskKindSimple.TYPE_ID, DizhuTaskKindSimple)  # new
    TYTaskKindRegister.registerClass(SegmentNewbieTaskKind.TYPE_ID, SegmentNewbieTaskKind)
    TYTaskKindRegister.registerClass(SegmentDailyTaskKind.TYPE_ID, SegmentDailyTaskKind)


_taskSystem = TYTaskSystem()
dailyTaskSystem = DizhuDailyTaskSystem()
medalTaskSystem = DizhuMedalTaskSystem()
tableTaskSystem = DizhuTableTaskSystem()
newbieTaskSystem = DizhuNewbieTaskSystem()

_inited = False


def _reloadConf():
    conf = pkconfigure.getGameJson(6, 'tasks', {})
    _taskSystem.reloadConf(conf)
    conf = pkconfigure.getGameJson(6, 'task.daily', {})
    dailyTaskSystem.reloadConf(conf)
    SegmentTaskSystem.reload_conf()


def _onConfChanged(event):
    SegmentTaskSystem.on_conf_changed(event)
    if _inited and event.isChanged(['game:6:tasks:0', 'game:6:task.daily:0']):
        ftlog.debug('dizhutask._onConfChanged')
        _reloadConf()


def _initialize():
    global _inited
    global dailyTaskSystem
    global medalTaskSystem
    global tableTaskSystem
    global newbieTaskSystem
    global _taskSystem
    if not _inited:
        _inited = True
        from hall.entity.halltask import TYTaskDataDaoImpl
        _taskSystem = TYTaskSystemImpl(DIZHU_GAMEID, TYTaskDataDaoImpl())
        _taskSystem.registerSubTaskSystem('ddz.task.daily', dailyTaskSystem)
        _taskSystem.registerSubTaskSystem('ddz.task.medal', medalTaskSystem)
        _taskSystem.registerSubTaskSystem('ddz.task.table', tableTaskSystem)
        _taskSystem.registerSubTaskSystem('ddz.task.newbie', newbieTaskSystem)
        _reloadConf()
        pkeventbus.globalEventBus.subscribe(EventConfigure, _onConfChanged)


def _transformTableTasks(gameId, userId, clientId, tableTaskModel):
    try:
        tableTaskData = pkgamedata.getGameAttrJson(userId, DIZHU_GAMEID, 'table.tasks')
        if ftlog.is_debug():
            ftlog.debug('dizhutask._transformTableTasks gameId=', gameId,
                        'userId=', userId,
                        'clientId=', clientId,
                        'tableTaskData=', tableTaskData)
        tableTasks = tableTaskData.get('tasks') if tableTaskData else None
        if tableTasks:
            for task in tableTasks:
                taskId = int(task.get('taskId', -1))
                if taskId < 0:
                    continue
                utime = task.get('utime', 0)
                # ctime = task.get('ctime', 0)
                # ftime = task.get('ftime', 0)
                progress = task.get('progress', 0)

                taskKind = tableTaskModel.userTaskUnit.taskUnit.findTaskKind(taskId)
                if not taskKind:
                    ftlog.debug('dizhutask._transformTableTasks gameId=', gameId,
                                'userId=', userId,
                                'clientId=', clientId,
                                'taskKindId=', taskId,
                                'err=', 'UnknownTaskKindId')
                    continue

                newtask = taskKind.newTask(None, utime)
                newtask.setProgress(progress, utime)
                tableTaskModel.userTaskUnit.addTask(newtask)
    except:
        ftlog.error('dizhutask._transformTableTasks gameId=', gameId,
                    'userId=', userId,
                    'clientId=', clientId)


def _onUserLogin(gameId, userId, clientId, isCreate, isdayfirst):
    if not _inited:
        return

    if isCreate:
        pkgamedata.setGameAttr(userId, DIZHU_GAMEID, 'flag.ttask.trans', 1)
        if isNewer(userId):
            currentTimestamp = pktimestamp.getCurrentTimestamp()
            deadline = currentTimestamp + dizhuconf.getNewbieTaskConf().get('deadline', 0) * 86400
            newbieTaskSystem.setDeadlineTimestamp(userId, deadline)
    else:
        timestamp = pktimestamp.getCurrentTimestamp()
        if pkgamedata.setnxGameAttr(userId, DIZHU_GAMEID, 'flag.ttask.trans', 1) == 1:
            userTaskUnit = _taskSystem.loadUserTaskUnit(userId, tableTaskSystem.taskUnit, timestamp)
            tableTaskModel = DizhuTableTaskModel(tableTaskSystem, userTaskUnit)
            _transformTableTasks(gameId, userId, clientId, tableTaskModel)
            ftlog.debug('dizhutask._transformTasks gameId=', gameId,
                        'userId=', userId,
                        'clientId=', clientId,
                        'taskUnit=', tableTaskSystem.taskUnit,
                        'userTaskUnit=', userTaskUnit)

def isNewer(userId):
    clientId = sessiondata.getClientId(userId)
    return dizhuconf.getNewbieTaskConf().get('open', 0) == 1 and clientId not in dizhuconf.getNewbieTaskConf().get('closes', [])
