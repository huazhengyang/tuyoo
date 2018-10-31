# -*- coding=utf-8
'''
Created on 2015年7月1日

@author: zhaojiangang
'''
from datetime import datetime
import json
from sre_compile import isstring

import freetime.util.log as ftlog
from hall import client_ver_judge
from hall.entity import hallvip, hallconf, hallitem, datachangenotify, hallshare
from hall.entity.hallconf import HALL_GAMEID
from poker.entity.biz.confobj import TYConfable, TYConfableRegister
from poker.entity.biz.exceptions import TYBizException
import poker.entity.dao.daoconst as pkdaoconst
import poker.entity.dao.userchip as pkuserchip
from poker.entity.dao import gamedata, sessiondata
from poker.entity.events.tyevent import EventConfigure, UserEvent
import poker.entity.events.tyeventbus as pkeventbus
import poker.util.timestamp as pktimestamp
from hall.entity.todotask import TodoTaskHelper
from poker.util import strutil


class TYBenefitsException(TYBizException):
    def __init__(self, errorCode, message):
        super(TYBenefitsException, self).__init__(errorCode, message)

    def __str__(self):
        return '%s:%s' % (self.errorCode, self.message)

    def __unicode__(self):
        return u'%s:%s' % (self.errorCode, self.message)


class TYBenefitsConfException(TYBenefitsException):
    def __init__(self, conf, message):
        super(TYBenefitsConfException, self).__init__(-1, message)
        self.conf = conf

    def __str__(self):
        return '%s:%s conf=%s' % (self.errorCode, self.message, self.conf)

    def __unicode__(self):
        return u'%s:%s conf=%s' % (self.errorCode, self.message, self.conf)


class TYBenefitsPrivilege(TYConfable):
    def __init__(self, name=None, desc=None, sortValue=None):
        self.name = name
        self.desc = desc
        self.sortValue = sortValue

    def filterBenefits(self, gameId, userBenefits):
        '''
        过滤userBenefits
        @return: (True/False, extTimes, extChip)
        '''
        raise NotImplemented()

    def sendBenefits(self, gameId, userBenefits):
        '''
        发放救济金特权相关的奖励
        '''
        raise NotImplemented()

    def decodeFromDict(self, d):
        self.name = d.get('name')
        if not isstring(self.name) or not self.name:
            raise TYBenefitsConfException(d, 'Privilege.name must be valid string')
        self.desc = d.get('desc', '')
        if not isstring(self.desc):
            raise TYBenefitsConfException(d, 'Privilege.desc must be string')
        self.sortValue = d.get('sort', 0)
        self._decodeFromDictImpl(d)
        return self

    def _decodeFromDictImpl(self, d):
        pass


class TYBenefitsPrivilegeMember(TYBenefitsPrivilege):
    TYPE_ID = 'common.member'

    def __init__(self):
        super(TYBenefitsPrivilegeMember, self).__init__()
        self.timesOp = None
        self.sendChipOp = None

    def filterBenefits(self, gameId, userBenefits):
        extTimes = extChip = 0
        if self.timesOp:
            extTimes = self.timesOp.doOp(userBenefits.times)
        if self.sendChipOp:
            extChip = self.sendChipOp.doOp(userBenefits.sendChip)
        remainDays, _ = hallitem.getMemberInfo(userBenefits.userId, pktimestamp.getCurrentTimestamp())
        if remainDays > 0:
            # 是会员
            return True, self, extTimes, extChip
        return False, self, 0, 0

    def sendBenefits(self, gameId, userBenefits):
        from hall.entity import hallsubmember
        assert (isinstance(userBenefits.privilege, TYBenefitsPrivilegeMember))
        status = hallsubmember.loadSubMemberStatus(userBenefits.userId)
        isSubExpires = status.isSubExpires(datetime.now())
        if (userBenefits.times > userBenefits.maxTimes
            and userBenefits.extTimes > 0):
            eventId = 'BENE_SEND_MEMBER_EXT_TIMES' if isSubExpires else 'BENE_SEND_SUB_MEMBER_EXT_TIMES'
            _trueDelta, final = pkuserchip.incrChip(userBenefits.userId, gameId, userBenefits.sendChip,
                                                    pkdaoconst.CHIP_NOT_ENOUGH_OP_MODE_NONE,
                                                    eventId, 0, None)
            ftlog.debug('TYBenefitsPrivilegeMember.sendBenefits gameId=', gameId,
                       'userId=', userBenefits.userId,
                       'sendChip=', userBenefits.sendChip,
                       'times=', userBenefits.times,
                       'maxTimes=', userBenefits.maxTimes,
                       'extTimes=', userBenefits.extTimes,
                       'eventId=', eventId,
                       'final=', final)

        if userBenefits.extSendChip > 0:
            eventId = 'BENE_SEND_MEMBER_EXT' if isSubExpires else 'BENE_SEND_SUB_MEMBER_EXT'
            _trueDelta, final = pkuserchip.incrChip(userBenefits.userId, gameId, userBenefits.extSendChip,
                                                    pkdaoconst.CHIP_NOT_ENOUGH_OP_MODE_NONE,
                                                    eventId, 0, None)
            ftlog.debug('TYBenefitsPrivilegeMember.sendBenefits gameId=', gameId,
                       'userId=', userBenefits.userId,
                       'extSendChip=', userBenefits.extSendChip,
                       'eventId=', eventId,
                       'final=', final)
        return userBenefits

    def _decodeFromDictImpl(self, d):
        opStr = d.get('times')
        if opStr:
            self.timesOp = TYBenefitsOp.decodeOp('times', opStr)
        opStr = d.get('sendChip')
        if opStr:
            self.sendChipOp = TYBenefitsOp.decodeOp('sendChip', opStr)
        return self


class TYBenefitsPrivilegeVIPLevel(TYBenefitsPrivilege):
    def __init__(self):
        super(TYBenefitsPrivilegeVIPLevel, self).__init__()
        self.vipLevel = None
        self.timesOp = None
        self.sendChipOp = None

    @classmethod
    def fromOther(cls, vipLevel, other):
        assert (isinstance(other, TYBenefitsPrivilegeVIPLevel))
        ret = TYBenefitsPrivilegeVIPLevel()
        ret.vipLevel = vipLevel
        ret.desc = other.desc
        ret.name = '' if vipLevel.level == 0 else vipLevel.name
        ret.sortValue = other.sortValue
        ret.timesOp = other.timesOp
        ret.sendChipOp = other.sendChipOp
        return ret

    def filterBenefits(self, gameId, userBenefits):
        extTimes = extChip = 0
        if self.timesOp:
            extTimes = self.timesOp.doOp(userBenefits.maxTimes)
        if self.sendChipOp:
            extChip = self.sendChipOp.doOp(userBenefits.sendChip)
        return True, self, extTimes, extChip

    def sendBenefits(self, gameId, userBenefits):
        assert (isinstance(userBenefits.privilege, TYBenefitsPrivilegeVIPLevel))
        if (userBenefits.times > userBenefits.maxTimes
            and userBenefits.extTimes > 0):
            _trueDelta, final = pkuserchip.incrChip(userBenefits.userId, gameId, userBenefits.sendChip,
                                                    pkdaoconst.CHIP_NOT_ENOUGH_OP_MODE_NONE,
                                                    'BENE_SEND_VIP_EXT_TIMES', self.vipLevel.level,
                                                    None)
            ftlog.debug('TYBenefitsPrivilegeVIPLevel.sendBenefits gameId=', gameId,
                       'userId=', userBenefits.userId,
                       'sendChip=', userBenefits.sendChip,
                       'times=', userBenefits.times,
                       'maxTimes=', userBenefits.maxTimes,
                       'extTimes=', userBenefits.extTimes,
                       'final=', final)

        if userBenefits.extSendChip > 0:
            ftlog.debug('TYBenefitsPrivilegeVIPLevel.sendBenefits gameId=', gameId,
                       'userId=', userBenefits.userId,
                       'extSendChip=', userBenefits.extSendChip)
            _trueDelta, final = pkuserchip.incrChip(userBenefits.userId, gameId, userBenefits.extSendChip,
                                                    pkdaoconst.CHIP_NOT_ENOUGH_OP_MODE_NONE,
                                                    'BENE_SEND_VIP_EXT', self.vipLevel.level,
                                                    None)
        return userBenefits

    def decodeFromDict(self, d):
        level = d.get('level')
        if not isinstance(level, int):
            raise TYBenefitsConfException(d, 'TYBenefitsPrivilegeVIPLevel.level must be int')
        self.vipLevel = hallvip.vipSystem.findVipLevelByLevel(level)
        if not self.vipLevel:
            raise TYBenefitsConfException(d, 'TYBenefitsPrivilegeVIPLevel.level not found %s' % (level))
        self.desc = d.get('desc', '')
        self.name = '' if self.vipLevel.level == 0 else self.vipLevel.name
        if not isstring(self.desc):
            raise TYBenefitsConfException(d, 'TYBenefitsPrivilegeVIPLevel.desc must be string')
        opStr = d.get('times')
        if opStr:
            self.timesOp = TYBenefitsOp.decodeOp('times', opStr)
            ftlog.debug('TYBenefitsPrivilegeVIPLevel.decodeFromDict level=', level, 'timesOp=', opStr)
        opStr = d.get('sendChip')
        if opStr:
            self.sendChipOp = TYBenefitsOp.decodeOp('sendChip', opStr)
            ftlog.debug('TYBenefitsPrivilegeVIPLevel.decodeFromDict level=', level, 'sendChipOp=', opStr)
        return self


class TYBenefitsPrivilegeVIP(TYBenefitsPrivilege):
    TYPE_ID = 'common.vip'

    def __init__(self):
        super(TYBenefitsPrivilegeVIP, self).__init__()
        self._levelMap = {}
        self._levelList = []

    def filterBenefits(self, gameId, userBenefits):
        userVip = hallvip.userVipSystem.getUserVip(userBenefits.userId)
        privilege = self._findOrCreatePrivilege(userVip)
        if privilege:
            _, p, extTimes, extChip = privilege.filterBenefits(gameId, userBenefits)
            return True, p, extTimes, extChip
        return False, self, 0, 0

    def sendBenefits(self, gameId, userBenefits):
        #         userVip = hallvip.userVipSystem.getUserVip(userBenefits.userId)
        #         privilege = self._findOrCreatePrivilege(userVip)
        #         if privilege:
        #             return privilege.sendBenefits(gameId, userBenefits)
        # 此处不应该调用
        ftlog.error('TYBenefitsPrivilegeVIP.sendBenefits gameId=', gameId,
                    'userId=', userBenefits.userId)
        return userBenefits

    def _findOrCreatePrivilege(self, userVip):
        p = self._levelMap.get(userVip.vipLevel.level)
        if not p:
            p = self._findLessEqual(userVip)
            if p:
                p = TYBenefitsPrivilegeVIPLevel.fromOther(userVip.vipLevel, p)
                self._levelMap[userVip.vipLevel.level] = p
        return p

    def _findLessEqual(self, userVip):
        for p in self._levelList[::-1]:
            if p.vipLevel.level <= userVip.vipLevel.level:
                return p
        return None

    def _resetLevelList(self):
        self._levelList = sorted(self._levelMap.values(),
                                 cmp=lambda x, y: cmp(x.vipLevel.level,
                                                      y.vipLevel.level))

    def _decodeFromDictImpl(self, d):
        levels = d.get('levels', [])
        if not isinstance(levels, list):
            raise TYBenefitsConfException(d, 'TYBenefitsPrivilegeVIP.levels must be list')
        levels.sort(cmp=lambda x, y: cmp(x['level'], y['level']))
        timesOps = []
        sendChipOps = []
        for levelConf in levels:
            levelPrivilege = TYBenefitsPrivilegeVIPLevel()
            levelPrivilege.decodeFromDict(levelConf)
            if levelPrivilege.vipLevel.level in self._levelMap:
                raise TYBenefitsConfException(d, 'TYBenefitsPrivilegeVIP.vip level %s duplicated' % (
                levelPrivilege.vipLevel.level))
            if levelPrivilege.timesOp:
                timesOps.append(levelPrivilege.timesOp)
            if levelPrivilege.sendChipOp:
                sendChipOps.append(levelPrivilege.sendChipOp)
            levelPrivilege.timesOp = TYBenefitsOpComposite(timesOps)
            levelPrivilege.sendChipOp = TYBenefitsOpComposite(sendChipOps)
            self._levelMap[levelPrivilege.vipLevel.level] = levelPrivilege
        self._resetLevelList()


class TYUserBenefitsData(object):
    def __init__(self, times, updateTime):
        self.times = times
        self.updateTime = updateTime


class TYUserBenefitsDataDao(object):
    def loadUserBenefitsData(self, userId):
        '''
        加载用户救济金配置
        '''
        raise NotImplemented()

    def saveUserBenefitsData(self, userId, benefitsData):
        '''
        保存用户救济金配置
        '''
        raise NotImplemented()


class TYUserBenefitsDataDaoImpl(TYUserBenefitsDataDao):
    def loadUserBenefitsData(self, userId):
        '''
        加载用户救济金配置
        '''
        try:
            d = gamedata.getGameAttrJson(userId, 9999, 'benefits')
            if d:
                return TYUserBenefitsData(d['times'], d['ut'])
        except:
            ftlog.error()
        return None

    def saveUserBenefitsData(self, userId, benefitsData):
        '''
        保存用户救济金配置
        '''
        jstr = json.dumps({'times': benefitsData.times, 'ut': benefitsData.updateTime})
        gamedata.setGameAttr(userId, 9999, 'benefits', jstr)


class TYUserBenefits(object):
    '''
    用户救济金类
    '''

    def __init__(self, userId, updateTime, times,
                 maxTimes, sendChip, minChip):
        self.userId = userId
        # 最后更新时间
        self.updateTime = updateTime
        # 本次发放周期内的发放次数
        self.times = times
        # 最大发放次数
        self.maxTimes = maxTimes
        # 每次发放金币数
        self.sendChip = sendChip
        # 金币到多少才发送救济金
        self.minChip = minChip
        # 额外要发放的次数
        self.extTimes = 0
        # 额外要发放的金币
        self.extSendChip = 0
        # 额外发放的说明
        self.privilege = None

    def hasLeftTimes(self):
        '''
        是否还有剩余次数
        '''
        return self.times < self.totalMaxTimes

    def leftTimes(self):
        '''
        还剩多少次
        '''
        return max(0, self.totalMaxTimes - self.times)

    @property
    def totalSendChip(self):
        '''
        本次总共发送的金币数
        '''
        return self.sendChip + self.extSendChip

    @property
    def totalMaxTimes(self):
        '''
        一共能发放多少次
        '''
        return self.maxTimes + self.extTimes


class TYUserBenefitsSentEvent(UserEvent):
    '''
    用户发放救济金事件
    '''

    def __init__(self, gameId, userId, userBenefits):
        super(TYUserBenefitsSentEvent, self).__init__(userId, gameId)
        # 用户的救济金对象
        self.userBenefits = userBenefits


class TYBenefitsOp(object):
    def doOp(self, inValue):
        raise NotImplemented()

    @classmethod
    def decodeOp(cls, name, opStr):
        opType = opStr[0]
        opValue = opStr[1:]
        if opType not in ('+', '*'):
            raise TYBenefitsConfException(opStr, 'privilege.%s must be (+|*)xxx' % (name))
        try:
            opValue = int(opValue)
            if opType == '+':
                return TYBenefitsOpAdd(opValue)
            return TYBenefitsOpMulti(opValue)
        except:
            ftlog.error()
            raise TYBenefitsConfException(opStr,
                                          'privilege.%s must be (+|*)number: %s %s:%s' % (name, opStr, opType, opValue))


class TYBenefitsOpAdd(TYBenefitsOp):
    def __init__(self, addition):
        super(TYBenefitsOpAdd, self).__init__()
        self._addition = addition

    def doOp(self, inValue):
        return self._addition


class TYBenefitsOpMulti(TYBenefitsOp):
    def __init__(self, multiplier):
        super(TYBenefitsOpMulti, self).__init__()
        assert (multiplier > 1)
        self._multiplier = multiplier

    def doOp(self, inValue):
        return (self._multiplier - 1) * inValue


class TYBenefitsOpComposite(TYBenefitsOp):
    def __init__(self, ops):
        super(TYBenefitsOpComposite, self).__init__()
        self._ops = []
        self.addOps(ops)

    def addOp(self, op):
        assert (isinstance(op, TYBenefitsOp))
        self._ops.append(op)

    def addOps(self, ops):
        for op in ops:
            self.addOp(op)

    def doOp(self, inValue):
        outVal = 0
        for op in self._ops:
            outVal += op.doOp(inValue)
        return outVal


class TYBenefitsPrivilegeRegister(TYConfableRegister):
    _typeid_clz_map = {
        TYBenefitsPrivilegeVIP.TYPE_ID: TYBenefitsPrivilegeVIP,
        TYBenefitsPrivilegeMember.TYPE_ID: TYBenefitsPrivilegeMember
    }


class TYBenefitsSystem(object):
    def loadUserBenefits(self, gameId, userId, timestamp=None):
        '''
        加载用户的救济金数据
        @return: TYUserBenefits
        '''
        raise NotImplemented()

    def needSendBenefits(self, gameId, userId, timestamp=None):
        '''
        检查是否需要给用户发救济金
        @return: True/False
        '''
        raise NotImplemented()

    def sendBenefits(self, gameId, userId, timestamp=None):
        '''
        发放救济金
        @return: sentChip(True/False), TYUserBenefits
        '''
        raise NotImplemented()


class TYBenefitsSystemImpl(TYBenefitsSystem):
    def __init__(self, benefitsDao):
        self._minChip = 0
        self._sendChip = 0
        self._maxTimes = 0
        self._benefitsPrivileges = None
        self._benefitsDao = benefitsDao
        self._notSendGameIds = []

    def reloadConf(self, conf):
        minChip = conf.get('minChip')
        sendChip = conf.get('sendChip')
        maxTimes = conf.get('maxTimes')
        notSendGameIds = conf.get('notSendGameIds', [])
        if not minChip or minChip < 0:
            raise TYBenefitsConfException(conf, 'minChip must be int >= 0')
        if sendChip < 0:
            raise TYBenefitsConfException(conf, 'sendChip must be int >= 0')
        if maxTimes is None or maxTimes < 0:
            raise TYBenefitsConfException(conf, 'maxTimes must be int >= 0')
        if not isinstance(notSendGameIds, list):
            raise TYBenefitsConfException(conf, 'notSendGameIds must be list')

        benefitsPrivileges = TYBenefitsPrivilegeRegister.decodeList(conf.get('privileges', []))
        self._minChip = minChip
        self._sendChip = sendChip
        self._maxTimes = maxTimes
        self._benefitsPrivileges = benefitsPrivileges
        self._notSendGameIds = notSendGameIds
        ftlog.debug('TYBenefitsSystemImpl.reloadConf successed: allConf=', conf)

    def _findPrivileges(self, gameId, userBenefits, benefitsPrivileges):
        ret = []
        for privilege in benefitsPrivileges:
            ok, p, extTimes, extChip = privilege.filterBenefits(gameId, userBenefits)
            if ok:
                ret.append((p, extTimes, extChip))
        ret.sort(cmp=lambda x, y: cmp((userBenefits.maxTimes + x[1]) * (userBenefits.sendChip + x[2]),
                                      (userBenefits.maxTimes + y[1]) * (userBenefits.sendChip + y[2])), reverse=True)
        return ret

    def _findFirstHasChipPrivileges(self, gameId, userBenefits):
        if self._benefitsPrivileges:
            ps = self._findPrivileges(gameId, userBenefits, self._benefitsPrivileges)
            if ps:
                for p, extTimes, extChip in ps:
                    if extTimes != 0 or extChip != 0:
                        return p, extTimes, extChip
                return None, None, None
        return None, None, None

    def loadUserBenefits(self, gameId, userId, timestamp=None):
        '''
        加载用户的救济金数据
        @return: TYUserBenefits
        '''
        if timestamp is None:
            timestamp = pktimestamp.getCurrentTimestamp()

        # 加载用户的救济金配置    
        userBenefits = self._loadUserBenefits(gameId, userId, timestamp)
        if ftlog.is_debug():
            ftlog.debug('TYBenefitsSystemImpl.loadUserBenefits before filter gameId=', gameId,
                        'userId=', userBenefits.userId,
                        'benefits=', userBenefits.__dict__)

        # 矫正救济金数据    
        p, extTimes, extChip = self._findFirstHasChipPrivileges(gameId, userBenefits)
        if p:
            userBenefits.extTimes = extTimes
            userBenefits.extSendChip = extChip
            userBenefits.privilege = p
        if ftlog.is_debug():
            ftlog.debug('TYBenefitsSystemImpl.loadUserBenefits after filter gameId=', gameId,
                        'userId=', userBenefits.userId,
                        'benefits=', userBenefits.__dict__,
                        'privilege=', p,
                        'leftTimes=', userBenefits.leftTimes())
        return userBenefits

    def needSendBenefits(self, gameId, userId, timestamp=None):
        '''
        检查是否需要给用户发救济金
        @return: True/False
        '''
        if self._checkInNotSendGameIds(userId):
            return False
        if timestamp is None:
            timestamp = pktimestamp.getCurrentTimestamp()
        chip = pkuserchip.getUserChipAll(userId)
        userBenefits = self.loadUserBenefits(gameId, userId, timestamp)
        return userBenefits.hasLeftTimes() and chip < userBenefits.minChip

    def _checkInNotSendGameIds(self, userId):
        '''
        检查无需发放救济金的游戏id
        '''
        clientId = sessiondata.getClientId(userId)
        gameId = strutil.getGameIdFromHallClientId(clientId)
        if gameId in self._notSendGameIds:
            return True
        return False

    def sendBenefits(self, gameId, userId, timestamp=None):
        '''
        发放救济金
        @return: isSend(True/False), TYUserBenefits
        '''
        if timestamp is None:
            timestamp = pktimestamp.getCurrentTimestamp()
        if self._checkInNotSendGameIds(userId):
            return False, self.loadUserBenefits(gameId, userId, timestamp)
        chip = pkuserchip.getUserChipAll(userId)
        if chip < self._minChip:
            #添加关于版本控制的部分,当版本高于4.01且不是VIP玩家时不发送救济金
            from poker.util import strutil
            #避免其他游戏修改调用接口,用过session来获取clientID
            from poker.entity.dao import sessiondata
            clientId = sessiondata.getClientId(userId)
            _, clientVer, _ = strutil.parseClientId(clientId)
            userVipLevel = hallvip.userVipSystem.getUserVip(userId).vipLevel.level
            if clientVer >= client_ver_judge.client_ver_451 and userVipLevel == 0:
                return False, self.loadUserBenefits(gameId, userId, timestamp)

            # 用户金币低于指定数目时，发放救济金
            userBenefits = self.loadUserBenefits(gameId, userId, timestamp)
            if not userBenefits.hasLeftTimes():  # 没有剩余次数，弹分享引导
                # oldtime = gamedata.getGameAttr(userId, HALL_GAMEID, 'relief_share_date')
                # if not oldtime or datetime.fromtimestamp(oldtime).date() < datetime.fromtimestamp(timestamp).date():
                #     # 每天最多弹一次
                #     gamedata.setGameAttr(userId, HALL_GAMEID, 'relief_share_date', timestamp)
                #     shareId = hallshare.getShareId('Relieffund', userId, gameId)
                #     share = hallshare.findShare(shareId)
                #     if share:
                #         task = share.buildTodotask(gameId, userId, 'Relieffund')
                #         TodoTaskHelper.sendTodoTask(gameId, userId, task)
                return False, userBenefits

            # 发放救济金
            userBenefits.times += 1
            self._benefitsDao.saveUserBenefitsData(userId, TYUserBenefitsData(userBenefits.times, timestamp))
            self._sendBenefits(gameId, userBenefits)
            # 通知用户金币刷新
            datachangenotify.sendDataChangeNotify(gameId, userId, ['udata'])
            return True, userBenefits
        return False, self.loadUserBenefits(gameId, userId, timestamp)

    def _loadUserBenefits(self, gameId, userId, timestamp):
        try:
            benefitsData = self._benefitsDao.loadUserBenefitsData(userId)
            if benefitsData:
                userBenefits = TYUserBenefits(userId, benefitsData.updateTime, benefitsData.times, self._maxTimes,
                                              self._sendChip, self._minChip)
                self._adjustUserBenefits(gameId, userBenefits, timestamp)
                return userBenefits
        except:
            ftlog.error()
        return TYUserBenefits(userId, timestamp, 0, self._maxTimes, self._sendChip, self._minChip)

    def _adjustUserBenefits(self, gameId, userBenefits, timestamp):
        if (pktimestamp.getDayStartTimestamp(timestamp)
                != pktimestamp.getDayStartTimestamp(userBenefits.updateTime)):
            userBenefits.updateTime = timestamp
            userBenefits.times = 0
            return True
        return False

    def _sendBenefits(self, gameId, userBenefits):
        if userBenefits.times <= userBenefits.maxTimes:
            if userBenefits.sendChip <= 0:
                return
            
            final = pkuserchip.incrChip(userBenefits.userId, gameId, userBenefits.sendChip,
                                        pkdaoconst.CHIP_NOT_ENOUGH_OP_MODE_NONE,
                                        'BENE_SEND', 0, None)
            ftlog.debug('TYBenefitsSystemImpl._sendBenefits gameId=', gameId,
                       'userId=', userBenefits.userId,
                       'sendChip=', userBenefits.sendChip,
                       'final=', final)
        if userBenefits.privilege:
            userBenefits.privilege.sendBenefits(gameId, userBenefits)


benefitsSystem = TYBenefitsSystem()
_inited = False


def _reloadConf():
    conf = hallconf.getBenefitsConf()
    benefitsSystem.reloadConf(conf)


def _onConfChanged(event):
    if _inited and event.isChanged('game:9999:benefits:0'):
        ftlog.debug('hallbenefits._onConfChanged')
        _reloadConf()


def _initialize():
    ftlog.debug('Benefits initialize begin')
    global benefitsSystem
    global _inited
    if not _inited:
        _inited = True
        benefitsSystem = TYBenefitsSystemImpl(TYUserBenefitsDataDaoImpl())
        _reloadConf()
        pkeventbus.globalEventBus.subscribe(EventConfigure, _onConfChanged)
    ftlog.debug('Benefits initialize end')
