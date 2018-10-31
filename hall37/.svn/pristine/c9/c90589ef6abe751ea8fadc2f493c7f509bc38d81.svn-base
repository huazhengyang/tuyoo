# -*- coding=utf-8
'''
Created on 2015年8月25日

@author: zhaojiangang
'''
from datetime import datetime
from sre_compile import isstring
import time

import freetime.util.log as ftlog
from hall.entity import hallaccount, hallsubmember
from hall.entity.hallconf import HALL_GAMEID
from poker.entity.biz.confobj import TYConfableRegister, TYConfable
from poker.entity.biz.exceptions import TYBizConfException
from poker.entity.configure import pokerconf
from poker.entity.dao import onlinedata, sessiondata, userdata, gamedata, \
    daobase
import poker.entity.dao.userdata as pkuserdata
from poker.util import strutil
import poker.util.timestamp as pktimestamp


class UserCondition(TYConfable):
    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        raise NotImplemented()


class UserConditionFirstRecharged(UserCondition):
    TYPE_ID = 'user.cond.firstRecharged'

    def __init__(self):
        super(UserConditionFirstRecharged, self).__init__()

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        from hall.entity import hallstore
        return hallstore.isFirstRecharged(userId)

    def decodeFromDict(self, d):
        return self


class UserConditionUnFirstRecharged(UserCondition):
    TYPE_ID = 'user.cond.unFirstRecharged'

    def __init__(self):
        super(UserConditionUnFirstRecharged, self).__init__()

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        from hall.entity import hallstore
        return not hallstore.isFirstRecharged(userId)

    def decodeFromDict(self, d):
        return self


class UserConditionGotFirstRechargeReward(UserCondition):
    TYPE_ID = 'user.cond.gotFirstRechargeReward'

    def __init__(self):
        super(UserConditionGotFirstRechargeReward, self).__init__()

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        from hall.entity import hallstore
        return hallstore.isGetFirstRechargeReward(userId)

    def decodeFromDict(self, d):
        return self


class UserConditionUnGotFirstRechargeReward(UserCondition):
    TYPE_ID = 'user.cond.unGotFirstRechargeReward'

    def __init__(self):
        super(UserConditionUnGotFirstRechargeReward, self).__init__()

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        from hall.entity import hallstore
        return not hallstore.isGetFirstRechargeReward(userId)

    def decodeFromDict(self, d):
        return self


class UserConditionisMyGameid(UserCondition):
    '''
    clientId中的gameId是否与条件中的gameId一致
    '''
    TYPE_ID = 'user.cond.isMyGameid'

    def __init__(self, myGameId=6):
        super(UserConditionisMyGameid, self).__init__()
        self.myGameId = myGameId

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        mowGameId = strutil.getGameIdFromHallClientId(clientId)
        ftlog.debug('UserConditionisMyGameid.check userId=', userId,
                    'gameId=', gameId,
                    'clientId=', clientId,
                    'nowGameId=', mowGameId,
                    'myGameId=', self.myGameId)
        if mowGameId == self.myGameId:
            return True
        else:
            return False

    def decodeFromDict(self, d):
        self.myGameId = d.get('myGameId', 0)
        if not isinstance(self.myGameId, int) or self.myGameId < 1:
            raise TYBizConfException(d, 'UserConditionisMyGameid.myGameId must be int >= 1')
        return self

class UserConditionPluginId(UserCondition):
    '''
    clientId中的gameId是否与条件中的gameId一致
    '''
    TYPE_ID = 'user.cond.gameId'

    def __init__(self, myGameId=6):
        super(UserConditionPluginId, self).__init__()
        self.gameId = myGameId

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        '''
        gameId为插件游戏ID
        '''
        ftlog.debug('UserConditionPluginId.check gameId:', gameId
                    , ' self.gameId:', self.gameId)
        return (self.gameId == gameId)

    def decodeFromDict(self, d):
        self.gameId = d.get('gameId', 0)
        if not isinstance(self.gameId, int) or self.gameId < 1:
            raise TYBizConfException(d, 'UserConditionPluginId.myGameId must be int >= 1')
        return self

class UserConditionVipLevel(UserCondition):
    TYPE_ID = 'user.cond.vipLevel'

    def __init__(self, startLevel=-1, stopLevel=-1):
        super(UserConditionVipLevel, self).__init__()
        self.startLevel = startLevel
        self.stopLevel = stopLevel

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        from hall.entity import hallvip
        try:
            userVip = hallvip.userVipSystem.getUserVip(userId)
            level = userVip.vipLevel.level

            startCondition = (self.startLevel == -1 or level >= self.startLevel)
            stopCondition = (self.stopLevel == -1 or level <= self.stopLevel)
            if ftlog.is_debug():
                ftlog.debug('UserConditionVipLevel.check userId:', userId
                            , ' gameId:', gameId
                            , ' startLevel:', self.startLevel
                            , ' stopLevel:', self.stopLevel
                            , ' startCondition:', startCondition
                            , ' stopCondition:', stopCondition
                            )

            return startCondition and stopCondition
        except:
            ftlog.error()
            return False

    def decodeFromDict(self, d):
        self.startLevel = d.get('startLevel', -1)
        if not isinstance(self.startLevel, int) or self.startLevel < -1:
            raise TYBizConfException(d, 'UserConditionVipLevel.startLevel must be int >= -1')
        self.stopLevel = d.get('stopLevel', -1)
        if not isinstance(self.stopLevel, int) or self.stopLevel < -1:
            raise TYBizConfException(d, 'UserConditionVipLevel.stopLevel must be int >= -1')
        if self.stopLevel != -1 and self.stopLevel < self.startLevel:
            raise TYBizConfException(d, 'UserConditionVipLevel.stopLevel must >= startLevel')
        return self


class UserConditionChip(UserCondition):
    TYPE_ID = 'user.cond.chip'

    def __init__(self, startChip=-1, stopChip=-1):
        super(UserConditionChip, self).__init__()
        self.startChip = startChip
        self.stopChip = stopChip

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        from poker.entity.dao import userchip
        try:
            userChip = userchip.getChip(userId)
            if ftlog.is_debug():
                ftlog.debug('userChip:', userChip, ' startChip:', self.startChip, ' stopChip:', self.stopChip)
            return (self.startChip == -1 or userChip >= self.startChip) \
                   and (self.stopChip == -1 or userChip <= self.stopChip)
        except:
            ftlog.error()
            return False

    def decodeFromDict(self, d):
        self.startChip = d.get('startChip', -1)
        if not isinstance(self.startChip, int) or self.startChip < -1:
            raise TYBizConfException(d, 'UserConditionChip.startChip must be int >= -1')

        self.stopChip = d.get('stopChip', -1)
        if not isinstance(self.stopChip, int) or self.stopChip < -1:
            raise TYBizConfException(d, 'UserConditionChip.stopChip must be int >= -1')

        if self.stopChip != -1 and self.stopChip < self.startChip:
            raise TYBizConfException(d, 'UserConditionChip.stopChip must >= startChip')

        return self

#添加钻石条件 2018-3-29 xy
class UserConditionDiamond(UserCondition):
    TYPE_ID = 'user.cond.diamond'

    def __init__(self, startDiamond=-1, stopDiamond=-1):
        super(UserConditionDiamond, self).__init__()
        self.startDiamond = startDiamond
        self.stopDiamond = stopDiamond

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        from poker.entity.dao import userchip
        try:
            userDiamond = userchip.getDiamond(userId)
            if ftlog.is_debug():
                ftlog.debug('userDiamond:', userDiamond, ' startDiamond:', self.startDiamond, ' stopDiamond:', self.stopDiamond)
            return (self.startDiamond == -1 or userDiamond >= self.startDiamond) \
                   and (self.stopDiamond == -1 or userDiamond <= self.stopDiamond)
        except:
            ftlog.error()
            return False

    def decodeFromDict(self, d):
        self.startDiamond = d.get('startDiamond', -1)
        if not isinstance(self.startDiamond, int) or self.startDiamond < -1:
            raise TYBizConfException(d, 'UserConditionDiamond.startDiamond must be int >= -1')

        self.stopDiamond = d.get('stopDiamond', -1)
        if not isinstance(self.stopDiamond, int) or self.stopDiamond < -1:
            raise TYBizConfException(d, 'UserConditionDiamond.stopDiamond must be int >= -1')

        if self.stopDiamond != -1 and self.stopDiamond < self.startDiamond:
            raise TYBizConfException(d, 'UserConditionDiamond.stopDiamond must >= startDiamond')

        return self
    
class UserConditionCoupon(UserCondition):
    TYPE_ID = 'user.cond.coupon'

    def __init__(self, startCoupon=-1, stopCoupon=-1):
        super(UserConditionCoupon, self).__init__()
        self.startCoupon = startCoupon
        self.stopCoupon = stopCoupon

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        from poker.entity.dao import userchip
        try:
            userConpon = userchip.getCoupon(userId)
            if ftlog.is_debug():
                ftlog.debug('userConpon:', userConpon
                            , ' startCoupon:', self.startCoupon
                            , ' stopCoupon:', self.stopCoupon)
            return (self.startCoupon == -1 or userConpon >= self.startCoupon) \
                   and (self.stopCoupon == -1 or userConpon <= self.stopCoupon)
        except:
            ftlog.error()
            return False

    def decodeFromDict(self, d):
        self.startCoupon = d.get('startCoupon', -1)
        if not isinstance(self.startCoupon, int) or self.startCoupon < -1:
            raise TYBizConfException(d, 'UserConditionCoupon.startCoupon must be int >= -1')

        self.stopCoupon = d.get('stopCoupon', -1)
        if not isinstance(self.stopCoupon, int) or self.stopCoupon < -1:
            raise TYBizConfException(d, 'UserConditionCoupon.stopCoupon must be int >= -1')

        if self.stopCoupon != -1 and self.stopCoupon < self.startCoupon:
            raise TYBizConfException(d, 'UserConditionCoupon.stopCoupon must >= startCoupon')

        return self


class UserConditionsignDayMod(UserCondition):
    TYPE_ID = 'user.cond.signDayMod'

    def __init__(self, mod=1, remainder=-1):
        super(UserConditionsignDayMod, self).__init__()
        self.mod = mod
        self.remainder = remainder

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        try:
            nowDate = datetime.fromtimestamp(timestamp).date()
            createDate = datetime.strptime(userdata.getAttr(userId, 'createTime'), '%Y-%m-%d %H:%M:%S.%f').date()
            registerDays = max(0, (nowDate - createDate).days)
            if registerDays % self.mod == self.remainder:
                return True
            else:
                return False
        except:
            ftlog.error()
            return False

    def decodeFromDict(self, d):
        self.mod = int(d.get('mod', 1))
        if not isinstance(self.mod, int) or self.mod < 1:
            raise TYBizConfException(d, 'UserConditionsignDayMod.mod must be int >= 1')
        self.remainder = int(d.get('remainder', -1))
        if not isinstance(self.remainder, int) or self.remainder < -1:
            raise TYBizConfException(d, 'UserConditionsignDayMod.remainder must be int >= -1')
        return self


class UserConditionLoginDays(UserCondition):
    TYPE_ID = 'user.cond.login.days'

    def __init__(self, startDays=1, endDays=-1):
        super(UserConditionLoginDays, self).__init__()
        self.startDays = startDays
        self.endDays = endDays

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        loginDays = gamedata.getGameAttrInt(userId, HALL_GAMEID, 'loginDays')
        startCondition = (self.startDays == -1) or (loginDays >= self.startDays)
        endCondition = (self.endDays == -1) or (loginDays < self.endDays)
        if ftlog.is_debug():
            ftlog.debug('UserConditionLoginDays.check userId:', userId
                        , ' clientId:', clientId
                        , ' loginDays:', loginDays
                        , ' startDays:', self.startDays
                        , ' endDays:', self.endDays
                        , ' startCondition:', startCondition
                        , ' endCondition:', endCondition
                        )
        return startCondition and endCondition

    def decodeFromDict(self, d):
        self.startDays = d.get('startDays', -1)
        if not isinstance(self.startDays, int):
            raise TYBizConfException(d, 'UserConditionLoginDays.startDays must be int')

        self.endDays = d.get('endDays', -1)
        if not isinstance(self.endDays, int):
            raise TYBizConfException(d, 'UserConditionLoginDays.endDays must be int')

        return self


class UserConditionShareCount(UserCondition):
    TYPE_ID = 'user.cond.share.count'

    def __init__(self, start=1, end=-1):
        super(UserConditionShareCount, self).__init__()
        self.start = start
        self.end = end

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        shareCount = gamedata.getGameAttrInt(userId, HALL_GAMEID, 'shareCount')
        startCondition = (self.start == -1) or (shareCount >= self.start)
        endCondition = (self.end == -1) or (shareCount < self.end)
        if ftlog.is_debug():
            ftlog.debug('UserConditionShareCount.check userId=', userId,
                        'clientId:', clientId,
                        'shareCount:', shareCount,
                        'start:', self.start,
                        'end:', self.end,
                        'startCondition:', startCondition,
                        'endCondition:', endCondition)
        return startCondition and endCondition

    def decodeFromDict(self, d):
        self.start = d.get('start', -1)
        if not isinstance(self.start, int):
            raise TYBizConfException(d, 'UserConditionShareCount.start must be int')

        self.end = d.get('end', -1)
        if not isinstance(self.end, int):
            raise TYBizConfException(d, 'UserConditionShareCount.end must be int')

        return self


class UserConditionPlayTime(UserCondition):
    TYPE_ID = 'user.cond.play.time'

    def __init__(self, startTime=1, endTime=-1):
        super(UserConditionPlayTime, self).__init__()
        self.startTime = startTime
        self.endTime = endTime

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        totalTime = gamedata.getGameAttrInt(userId, HALL_GAMEID, 'totaltime')
        startCondition = (self.startTime == -1) or (totalTime >= self.startTime)
        endCondition = (self.endTime == -1) or (totalTime < self.endTime)
        if ftlog.is_debug():
            ftlog.debug('UserConditionPlayTime.check userId:', userId
                        , ' clientId:', clientId
                        , ' totalTime:', totalTime
                        , ' startTime:', self.startTime
                        , ' endTime:', self.endTime
                        , ' startCondition:', startCondition
                        , ' endCondition:', endCondition
                        )
        return startCondition and endCondition

    def decodeFromDict(self, d):
        self.startTime = d.get('startTime', -1)
        if not isinstance(self.startTime, int):
            raise TYBizConfException(d, 'UserConditionPlayTime.startTime must be int')

        self.endTime = d.get('endTime', -1)
        if not isinstance(self.endTime, int):
            raise TYBizConfException(d, 'UserConditionPlayTime.endTime must be int')

        return self


class UserConditionReturnTime(UserCondition):
    '''
    用户再次回归时，与上次登录的时间差
    '''
    TYPE_ID = 'user.cond.return.time'

    def __init__(self, startTime=1, endTime=-1):
        super(UserConditionReturnTime, self).__init__()
        self.startTime = startTime
        self.endTime = endTime

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        lastAuthTime, authTime = userdata.getAttrs(userId, ['lastAuthorTime', 'authorTime'])
        if not lastAuthTime:
            lastAuthTime = pktimestamp.formatTimeMs()

        if ftlog.is_debug():
            ftlog.debug('UserConditionReturnTime.check lastAuthTime:', lastAuthTime)

        if not authTime:
            authTime = pktimestamp.formatTimeMs()
        if ftlog.is_debug():
            ftlog.debug('UserConditionReturnTime.check authTime:', authTime)

        totalTime = pktimestamp.getTimeStrDiff(lastAuthTime, authTime)
        if totalTime < 0:
            totalTime = 0

        startCondition = (self.startTime == -1) or (totalTime >= self.startTime)
        endCondition = (self.endTime == -1) or (totalTime < self.endTime)
        if ftlog.is_debug():
            ftlog.debug('UserConditionReturnTime.check userId:', userId
                        , ' clientId:', clientId
                        , ' totalTime:', totalTime
                        , ' startTime:', self.startTime
                        , ' endTime:', self.endTime
                        , ' startCondition:', startCondition
                        , ' endCondition:', endCondition
                        )
        return startCondition and endCondition

    def decodeFromDict(self, d):
        self.startTime = d.get('startTime', -1)
        if not isinstance(self.startTime, int):
            raise TYBizConfException(d, 'UserConditionReturnTime.startTime must be int')

        self.endTime = d.get('endTime', -1)
        if not isinstance(self.endTime, int):
            raise TYBizConfException(d, 'UserConditionReturnTime.endTime must be int')

        return self

class UserConditionBenefitsTime(UserCondition):
    '''
    用户再次回归时，与上次登录的时间差
    '''
    TYPE_ID = 'user.cond.benefits.time'

    def __init__(self, startTime=1, endTime=-1):
        super(UserConditionBenefitsTime, self).__init__()
        self.startTime = startTime
        self.endTime = endTime

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        '''
        lastAuthorTime > startTime
        and
        authorTime < endTime
        '''
        lastAuthTime = pktimestamp.getCurrentTimestamp();
        authTime = pktimestamp.getCurrentTimestamp();
        lastAuthTimeStr, authTimeStr = userdata.getAttrs(userId, ['lastAuthorTime', 'authorTime'])
        if lastAuthTimeStr:
            lastAuthTime = pktimestamp.timestrToTimestamp(lastAuthTimeStr, '%Y-%m-%d %H:%M:%S.%f')
        if ftlog.is_debug():
            ftlog.debug('UserConditionBenefitsTime.check lastAuthTime:', lastAuthTime)

        if authTimeStr:
            authTime = pktimestamp.timestrToTimestamp(authTimeStr, '%Y-%m-%d %H:%M:%S.%f')
        if ftlog.is_debug():
            ftlog.debug('UserConditionBenefitsTime.check authTime:', authTime)

        loginDays = gamedata.getGameAttrInt(userId, gameId, 'loginDays')
        startCondition = (lastAuthTime < self.startTime) or (loginDays == 1)
        endCondition = (authTime > self.startTime) and (authTime < self.endTime)
        
        if ftlog.is_debug():
            ftlog.debug('UserConditionBenefitsTime.check userId:', userId
                        , ' clientId:', clientId
                        , ' startTime:', self.startTime
                        , ' endTime:', self.endTime
                        , ' lastAuthTime:', lastAuthTime
                        , ' authTime:', authTime
                        , ' startCondition:', startCondition
                        , ' endCondition:', endCondition
                        )
        return startCondition and endCondition

    def decodeFromDict(self, d):
        startTimeStr = d.get('startTime', None)
        if not isstring(startTimeStr):
            raise TYBizConfException(d, 'UserConditionReturnTime.startTime must be string')
        self.startTime = pktimestamp.timestrToTimestamp(startTimeStr, '%Y-%m-%d %H:%M:%S')

        endTimeStr = d.get('endTime', None)
        if not isstring(endTimeStr):
            raise TYBizConfException(d, 'UserConditionReturnTime.endTime must be string')
        self.endTime = pktimestamp.timestrToTimestamp(endTimeStr, '%Y-%m-%d %H:%M:%S')
        
        return self

class UserConditionSex(UserCondition):
    TYPE_ID = 'user.cond.sex'

    def __init__(self, sex=0):
        super(UserConditionSex, self).__init__()
        self.sex = sex

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        return userdata.getAttr(userId, 'sex') == self.sex

    def decodeFromDict(self, d):
        self.sex = d.get('sex', 0)
        if self.sex not in (0, 1):
            raise TYBizConfException(d, 'UserConditionSex.sex must be int in (0,1)')
        return self


class UserConditionRegisterDay(UserCondition):
    TYPE_ID = 'user.cond.registerDays'

    def __init__(self, startDays=-1, stopDays=-1):
        super(UserConditionRegisterDay, self).__init__()
        self.startDays = startDays
        self.stopDays = stopDays

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        try:
            if self.startDays == -1 and self.stopDays == -1:
                return True
            nowDate = datetime.fromtimestamp(timestamp).date()
            createDate = datetime.strptime(userdata.getAttr(userId, 'createTime'), '%Y-%m-%d %H:%M:%S.%f').date()
            registerDays = max(0, (nowDate - createDate).days)
            return (self.startDays == -1 or registerDays >= self.startDays) \
                   and (self.stopDays == -1 or registerDays <= self.stopDays)
        except:
            ftlog.error('UserConditionRegisterDay.check',
                        'gameId=', gameId,
                        'userId=', userId,
                        'clientId=', clientId,
                        'timestamp=', timestamp,
                        'kwargs=', kwargs,
                        'daysRange=', '[%s,%s]' % (self.startDays, self.stopDays))
            return False

    def decodeFromDict(self, d):
        self.startDays = d.get('startDays', -1)
        if not isinstance(self.startDays, int) or self.startDays < -1:
            raise TYBizConfException(d, 'UserConditionRegisterDay.startDays must be int >= -1')
        self.stopDays = d.get('stopDays', -1)
        if not isinstance(self.stopDays, int) or self.stopDays < -1:
            raise TYBizConfException(d, 'UserConditionRegisterDay.stopDays must be int >= -1')
        if self.stopDays != -1 and self.stopDays < self.startDays:
            raise TYBizConfException(d, 'UserConditionRegisterDay.stopDays must >= startDays')
        return self
    
class UserConditionRegisterTime(UserCondition):
    '''
    用户注册的时间段在[startTime, stopTime)内
    '''
    TYPE_ID = 'user.cond.register.time'

    def __init__(self):
        super(UserConditionRegisterTime, self).__init__()

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        createTimeStr = userdata.getAttr(userId, 'createTime')
        if (not createTimeStr) or (not isstring(createTimeStr)):
            return False
        
        createTime = pktimestamp.timestrToTimestamp(createTimeStr, '%Y-%m-%d %H:%M:%S.%f')
        ftlog.debug('UserConditionRegisterTime.check user createTime:', createTime
                    , ' cond startTime:', self.startTime
                    , ' cond stopTime:', self.stopTime
                    , ' result:', (createTime >= self.startTime and createTime < self.stopTime))
        return createTime >= self.startTime and createTime < self.stopTime

    def decodeFromDict(self, d):
        startTimeStr = d.get('startTime', None)
        if (not startTimeStr) or (not isstring(startTimeStr)):
            raise TYBizConfException(d, 'UserConditionRegisterTime.startTime must be valid date string, format %Y-%m-%d %H:%M:%S')
        self.startTime = pktimestamp.timestrToTimestamp(startTimeStr, '%Y-%m-%d %H:%M:%S')
        
        stopTimeStr = d.get('stopTime', None)
        if (not stopTimeStr) or (not isstring(stopTimeStr)):
            raise TYBizConfException(d, 'UserConditionRegisterTime.stopTime must be valid date string, format %Y-%m-%d %H:%M:%S')
        self.stopTime = pktimestamp.timestrToTimestamp(stopTimeStr, '%Y-%m-%d %H:%M:%S')
        return self

class UserConditionNewUser(UserConditionRegisterDay):
    TYPE_ID = 'user.cond.newuser'

    def __init__(self):
        super(UserConditionNewUser, self).__init__(-1, 7)

    def decodeFromDict(self, d):
        return self


class UserConditionIsSubscribeMember(UserCondition):
    TYPE_ID = 'user.cond.isSubscribeMember'

    def __init__(self):
        super(UserConditionIsSubscribeMember, self).__init__()

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        subMemberStatus = hallsubmember.loadSubMemberStatus(userId)
        return subMemberStatus.isSub

    def decodeFromDict(self, d):
        return self


class UserConditionNotSubscribeMember(UserCondition):
    TYPE_ID = 'user.cond.notSubscribeMember'

    def __init__(self):
        super(UserConditionNotSubscribeMember, self).__init__()

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        subMemberStatus = hallsubmember.loadSubMemberStatus(userId)
        return not subMemberStatus.isSub

    def decodeFromDict(self, d):
        return self


class UserConditionMemberRemDays(UserCondition):
    TYPE_ID = 'user.cond.memberRemDays'

    def __init__(self):
        super(UserConditionMemberRemDays, self).__init__()
        self.startRemDays = None
        self.endRemDays = None

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        from hall.entity import hallitem
        userAssets = hallitem.itemSystem.loadUserAssets(userId)
        remDays = userAssets.balance(gameId, hallitem.ASSET_ITEM_MEMBER_NEW_KIND_ID, timestamp)
        if self.startRemDays >= 0 and remDays < self.startRemDays:
            return False
        if self.endRemDays >= 0 and remDays > self.endRemDays:
            return False
        return True

    def decodeFromDict(self, d):
        self.startRemDays = d.get('startRemDays')
        self.endRemDays = d.get('endRemDays')
        if not isinstance(self.startRemDays, int):
            raise TYBizConfException(d, 'UserConditionMemberRemDays.startRemDays must be int')
        if not isinstance(self.endRemDays, int):
            raise TYBizConfException(d, 'UserConditionMemberRemDays.endRemDays must be int')
        if self.endRemDays >= 0 and self.endRemDays < self.startRemDays:
            raise TYBizConfException(d, 'UserConditionMemberRemDays.endRemDays must be >= startRemDays')
        return self


class UserConditionIsMemberNotSub(UserCondition):
    TYPE_ID = 'user.cond.isMemberNotSub'

    def __init__(self):
        super(UserConditionIsMemberNotSub, self).__init__()

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        from hall.entity import hallitem
        subMemberStatus = hallsubmember.loadSubMemberStatus(userId)
        if subMemberStatus.isSub:
            return False
        userAssets = hallitem.itemSystem.loadUserAssets(userId)
        return userAssets.balance(gameId, hallitem.ASSET_ITEM_MEMBER_NEW_KIND_ID, timestamp) > 0

    def decodeFromDict(self, d):
        return self
    
class UserConditionHasAsset(UserCondition):
    TYPE_ID = 'user.cond.has.asset'

    def __init__(self):
        super(UserConditionHasAsset, self).__init__()
        self.itemId = None

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        from hall.entity import hallitem
        userAssets = hallitem.itemSystem.loadUserAssets(userId)
        leftCount = userAssets.balance(gameId, self.itemId, timestamp)
        ftlog.debug('UserConditionHasAsset.check userId:', userId
                    , ' gameId:', gameId
                    , ' clientId:', clientId
                    , ' itemId:', self.itemId
                    , ' leftCount:', leftCount)
        return leftCount > 0

    def decodeFromDict(self, d):
        self.itemId = d.get('itemId', None)
        if not isstring(self.itemId):
            raise TYBizConfException(d, 'UserConditionHasAsset.itemId must be string')
        return self


class UserConditionTimePeriod(UserCondition):
    TYPE_ID = 'user.cond.timePeriod'

    def __init__(self):
        super(UserConditionTimePeriod, self).__init__()
        self.periods = []

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        if not self.periods:
            return True
        nowT = datetime.fromtimestamp(timestamp).time()
        for period in self.periods:
            if (period[0] is None or nowT >= period[0]) and (period[1] is None or nowT < period[1]):
                if ftlog.is_debug():
                    ftlog.debug('UserConditionTimePeriod.check gameId=', gameId,
                                'userId=', userId,
                                'clientId=', clientId,
                                'period=', [period[0], period[1]],
                                'nowT=', nowT,
                                'inPeriod=', True)
                return True
        if ftlog.is_debug():
            ftlog.debug('UserConditionTimePeriod.check gameId=', gameId,
                        'userId=', userId,
                        'clientId=', clientId,
                        'periods=', self.periods,
                        'nowT=', nowT,
                        'inPeriod=', False)
        return False

    def decodeFromDict(self, d):
        periods = d.get('periods')
        if periods:
            timeZero = datetime.strptime('00:00', '%H:%M').time()
            for period in periods:
                s = datetime.strptime(period[0], '%H:%M').time()
                e = datetime.strptime(period[1], '%H:%M').time()
                s = s if s != timeZero else None
                e = e if e != timeZero else None
                if s != e:
                    if (s is None or e is None) or (s < e):
                        self.periods.append((s, e))
                    elif s > e:
                        self.periods.append((s, None))
                        self.periods.append((None, e))
        return self


class UserConditionPayCount(UserCondition):
    TYPE_ID = 'user.cond.payCount'

    def __init__(self, minPayCount=-1, maxPayCount=-1):
        super(UserConditionPayCount, self).__init__()
        self.minPayCount = minPayCount
        self.maxPayCount = maxPayCount

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        payCount = pkuserdata.getAttrInt(userId, 'payCount')
        return ((self.minPayCount < 0 or payCount >= self.minPayCount)
                and (self.maxPayCount < 0 or payCount < self.maxPayCount))

    def decodeFromDict(self, d):
        self.minPayCount = d.get('minPayCount', -1)
        if not isinstance(self.minPayCount, int) or self.minPayCount < -1:
            raise TYBizConfException(d, 'UserConditionPayCount.minPayCount must be int >= -1')
        self.maxPayCount = d.get('maxPayCount', -1)
        if not isinstance(self.maxPayCount, int) or self.maxPayCount < -1:
            raise TYBizConfException(d, 'UserConditionPayCount.maxPayCount must be int >= -1')
        if self.maxPayCount != -1 and self.maxPayCount < self.minPayCount:
            raise TYBizConfException(d, 'UserConditionPayCount.maxPayCount must >= minPayCount')
        return self


class UserConditionNonPay(UserConditionPayCount):
    '''
    用户没有支付
    '''
    TYPE_ID = 'user.cond.nonPay'

    def __init__(self):
        '''
        [0, 1) 也就是0次
        '''
        super(UserConditionNonPay, self).__init__(0, 1)

    def decodeFromDict(self, d):
        return self


class UserConditionPayLeastOnce(UserConditionPayCount):
    TYPE_ID = 'user.cond.payLeastOnce'

    def __init__(self):
        '''
        至少支付一次
        '''
        super(UserConditionPayLeastOnce, self).__init__(1, -1)

    def decodeFromDict(self, d):
        return self


# 是否绑定手机
class UserConditionBindPhone(UserCondition):
    TYPE_ID = 'user.cond.BindPhone'

    def __init__(self):
        super(UserConditionBindPhone, self).__init__()

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        bindmobile = userdata.getAttr(userId, 'bindMobile')
        isBindPhene = True if bindmobile == None or bindmobile == "" else False
        return isBindPhene

    def decodeFromDict(self, d):
        return self


# 今天没有签到
class UserConditionNotCheckInToday(UserCondition):
    TYPE_ID = 'user.cond.NotCheckInToday'

    def __init__(self):
        super(UserConditionNotCheckInToday, self).__init__()

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        from hall.entity import monthcheckin
        status = monthcheckin.loadStatus(userId)
        nowDate = datetime.now().date()
        checked = False
        if nowDate in status.checkinDateList:
            checked = True
        return not checked

    def decodeFromDict(self, d):
        return self


# 今天已经签到  
class UserConditionCheckedInToday(UserCondition):
    TYPE_ID = 'user.cond.CheckedInToday'

    def __init__(self):
        super(UserConditionCheckedInToday, self).__init__()

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        from hall.entity import monthcheckin
        status = monthcheckin.loadStatus(userId)
        nowDate = datetime.now().date()
        checked = False
        if nowDate in status.checkinDateList:
            checked = True
        return checked

    def decodeFromDict(self, d):
        return self


# 有可补签天数
class UserConditionHasSupCheckinDay(UserCondition):
    TYPE_ID = 'user.cond.HasSupCheckinDay'

    def __init__(self):
        super(UserConditionHasSupCheckinDay, self).__init__()

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        from hall.entity import monthcheckin
        status = monthcheckin.loadStatus(userId)
        nowDate = datetime.now()
        hasLack = status.checkinCount + status.supplementCheckinCount < nowDate._day

        return hasLack

    def decodeFromDict(self, d):
        return self


# 是否可领取签到奖励(有签到奖励可以领取,且未领取)
class UserConditionCheckInHasReward(UserCondition):
    TYPE_ID = 'user.cond.CheckInHasReward'

    def __init__(self):
        super(UserConditionCheckInHasReward, self).__init__()

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        from hall.entity import monthcheckin
        status = monthcheckin.loadStatus(userId)
        hasReward = False
        for _days, rewardContent in enumerate(monthcheckin.getConf().get('daysRewards', [])):
            monthRange = monthcheckin.getMonthRange()
            if rewardContent.get('days') < monthRange:
                monthRange = rewardContent.get('days')
            if not status.isReward(monthRange) and status.allCheckinCount >= monthRange:
                hasReward = True
                break
        return hasReward

    def decodeFromDict(self, d):
        return self


# 是否有抽奖卡
class UserConditionHasLuckyCard(UserCondition):
    TYPE_ID = 'user.cond.HasLuckyCard'

    def __init__(self):
        super(UserConditionHasLuckyCard, self).__init__()

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        from hall.entity import hallitem
        userAssets = hallitem.itemSystem.loadUserAssets(userId)
        timestamp = pktimestamp.getCurrentTimestamp()
        cardNum = userAssets.balance(gameId, hallitem.ASSET_ITEM_LOTTERY_CARD_ID, timestamp)
        hasLotteryCard = False if cardNum == 0 else True
        return hasLotteryCard

    def decodeFromDict(self, d):
        return self


# 是否是会员
class UserConditionIsMember(UserConditionMemberRemDays):
    TYPE_ID = 'user.cond.IsMember'

    def __init__(self):
        super(UserConditionIsMember, self).__init__()
        self.startRemDays = 1
        self.endRemDays = -1

    def decodeFromDict(self, d):
        return self


# 是否不是会员
class UserConditionNotIsMember(UserConditionMemberRemDays):
    TYPE_ID = 'user.cond.notIsMember'

    def __init__(self):
        super(UserConditionNotIsMember, self).__init__()
        self.startRemDays = 1
        self.endRemDays = -1

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        return not super(UserConditionNotIsMember, self).check(gameId, userId, clientId, timestamp, **kwargs)

    def decodeFromDict(self, d):
        return self


# 是否有会员弹窗配置
class UserConditionHasMemberBuyWindow(UserCondition):
    TYPE_ID = 'user.cond.HasMemberBuyWindow'

    def __init__(self):
        super(UserConditionHasMemberBuyWindow, self).__init__()

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        from hall.entity import hallpopwnd
        todotask = hallpopwnd.makeTodoTaskByTemplate(gameId, userId, clientId, 'memberBuy2')
        return todotask is not None

    def decodeFromDict(self, d):
        return self


# 是否有会员签到没有领取
class UserConditionHasMemberReward(UserCondition):
    TYPE_ID = 'user.cond.HasMemberReward'

    def __init__(self):
        super(UserConditionHasMemberReward, self).__init__()

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        from hall.entity import hallitem
        userBag = hallitem.itemSystem.loadUserAssets(userId).getUserBag()
        memberCardItem = userBag.getItemByKindId(hallitem.ITEM_MEMBER_NEW_KIND_ID)
        return memberCardItem and memberCardItem.canCheckin(timestamp)

    def decodeFromDict(self, d):
        return self


# 是否有新手任务奖励可以领取
class UserConditionHasTaskReward(UserCondition):
    TYPE_ID = 'user.cond.HasTaskReward'

    def __init__(self):
        super(UserConditionHasTaskReward, self).__init__()

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        from hall.entity import neituiguangtask
        taskModel = neituiguangtask.newUserTaskSystem.loadTaskModel(userId, timestamp)
        hasTaskReward = False
        for task in taskModel.userTaskUnit.taskList:
            if task.isFinished and not task.gotReward:
                hasTaskReward = True
                break
        return hasTaskReward

    def decodeFromDict(self, d):
        return self


# 是否全部完成新手任务
class UserConditionTaskAllDone(UserCondition):
    TYPE_ID = 'user.cond.TaskAllDone'

    def __init__(self):
        super(UserConditionTaskAllDone, self).__init__()

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        from hall.entity import neituiguangtask
        taskModel = neituiguangtask.newUserTaskSystem.loadTaskModel(userId, timestamp)
        allFinished = True
        for task in taskModel.userTaskUnit.taskList:
            if not task.isFinished or not task.gotReward:
                allFinished = False
                break
        return allFinished

    def decodeFromDict(self, d):
        return self


# 是否未评价五星评价
class UserConditionNotFiveStar(UserCondition):
    TYPE_ID = 'user.cond.NotFiveStar'

    def __init__(self):
        super(UserConditionNotFiveStar, self).__init__()

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        from hall.entity import fivestarrate
        canTriggle, _channel = fivestarrate.checkCanTriggleFiveStartRate(userId, clientId, timestamp)
        return canTriggle

    def decodeFromDict(self, d):
        return self


# 是否有每日分享配置
class UserConditionHasDailyShareConfig(UserCondition):
    TYPE_ID = 'user.cond.HasDailyShareConfig'

    def __init__(self):
        super(UserConditionHasDailyShareConfig, self).__init__()

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        from hall.entity import hallshare
        shareId = hallshare.getShareId("dailyShare", userId, gameId)
        if shareId is None:
            return False
        share = hallshare.findShare(shareId)
        if not share:
            return False
        return True

    def decodeFromDict(self, d):
        return self


# 是否今天还没有完成每日分享
class UserConditionHasDailyShareReward(UserCondition):
    TYPE_ID = 'user.cond.HasDailyShareReward'

    def __init__(self):
        super(UserConditionHasDailyShareReward, self).__init__()

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        from hall.entity import hallshare
        shareId = hallshare.getShareId('dailyShare', userId, gameId)
        if shareId is None:
            return False
        share = hallshare.findShare(shareId)
        if not share:
            return False
        return hallshare.canReward(userId, share, timestamp)

    def decodeFromDict(self, d):
        return self


# 是否有免费福利小红点
class UserConditionHasFreeMark(UserCondition):
    TYPE_ID = 'user.cond.HasFreeMark'

    def __init__(self):
        super(UserConditionHasFreeMark, self).__init__()

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        from hall.entity import hallfree
        from hall.servers.util.free_handler import FreeHelper
        freeList = hallfree.getFree(gameId, userId, clientId, timestamp)
        encodeFreeList = FreeHelper.encodeFreeList(gameId, userId, clientId, freeList, timestamp)
        markVisible = False
        if freeList:
            for index in range(len(encodeFreeList)):
                markVisible = markVisible or encodeFreeList[index]['markVisible']
        return markVisible

    def decodeFromDict(self, d):
        return self


class UserConditionClientVersion(UserCondition):
    TYPE_ID = 'user.cond.clientVersion'

    def __init__(self):
        super(UserConditionClientVersion, self).__init__()
        self.minVersion = None
        self.maxVersion = None

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        _, clientVer, _ = strutil.parseClientId(clientId)
        return (self.minVersion == -1 or clientVer >= self.minVersion) \
               and (self.maxVersion == -1 or clientVer < self.maxVersion)

    def decodeFromDict(self, d):
        self.minVersion = d.get('minVersion', -1)
        if not isinstance(self.minVersion, (int, float)) or self.minVersion < -1:
            raise TYBizConfException(d, 'UserConditionClientVersion.minVersion must be int >= -1')
        self.maxVersion = d.get('maxVersion', -1)
        if not isinstance(self.maxVersion, (int, float)) or self.maxVersion < -1:
            raise TYBizConfException(d, 'UserConditionClientVersion.maxVersion must be int >= -1')
        if self.maxVersion != -1 and self.maxVersion < self.minVersion:
            raise TYBizConfException(d, 'UserConditionClientVersion.maxVersion must >= minVersion')
        return self


class UserConditionInClientIDs(UserCondition):
    TYPE_ID = 'user.cond.in.clientIds'

    def __init__(self):
        super(UserConditionInClientIDs, self).__init__()
        # clientId编码集合
        self.clientIds = []

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        intClientidNum = pokerconf.clientIdToNumber(clientId)
        if ftlog.is_debug():
            ftlog.debug('UserConditionInClientIDs.check self.clientIds:', self.clientIds
                        , ' intClientidNum:', intClientidNum
                        )

        return intClientidNum in self.clientIds

    def decodeFromDict(self, d):
        self.clientIds = d.get('clientIds', [])
        return self

class UserConditionNotInClientIDs(UserCondition):
    TYPE_ID = 'user.cond.notin.clientIds'

    def __init__(self):
        super(UserConditionNotInClientIDs, self).__init__()
        # clientId编码集合
        self.clientIds = []

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        intClientidNum = pokerconf.clientIdToNumber(clientId)
        if ftlog.is_debug():
            ftlog.debug('UserConditionNotInClientIDs.check self.clientIds:', self.clientIds
                        , ' intClientidNum:', intClientidNum
                        )

        return intClientidNum not in self.clientIds

    def decodeFromDict(self, d):
        self.clientIds = d.get('clientIds', [])
        return self
    
class UserConditionInWhiteList(UserCondition):
    # 用户的userId在白名单内，通过gameId和name游戏可以方便的设置多个白名单
    TYPE_ID = 'user.cond.in.whiteList'

    def __init__(self):
        super(UserConditionInWhiteList, self).__init__()
        # 白名单所在的游戏ID
        self.gameId = 9999
        # 白名单的额名字
        self.name = 'white.list'

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        from poker.entity.configure import configure
        whiteList = configure.getGameJson(self.gameId, self.name, [], configure.DEFAULT_CLIENT_ID)
        ftlog.debug('UserConditionInWhiteList.check gameId:', gameId
                    , ' userId:', userId
                    , ' whiteList:', whiteList
                    , ' result:', (userId in whiteList))
        return userId in whiteList

    def decodeFromDict(self, d):
        self.gameId = d.get('gameId', 9999)
        self.name = d.get('name', 'white.list')
        ftlog.debug('UserConditionInWhiteList.decodeFromDict gameId:', self.gameId
                    , ' name:', self.name)
        return self

class UserConditionOR(UserCondition):
    """多个条件的或关系，有一个正确，结果就正确
    """
    TYPE_ID = 'user.cond.or'

    def __init__(self):
        super(UserConditionOR, self).__init__()
        self.conditions = []

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        if ftlog.is_debug():
            ftlog.debug('UserConditionOR.check >>> gameId=', gameId,
                        'userId=', userId,
                        'clientId=', clientId,
                        'timestamp=', timestamp,
                        'kwargs=', kwargs,
                        'conditions=', self.conditions)

        for condition in self.conditions:
            if condition.check(gameId, userId, clientId, timestamp, **kwargs):
                if ftlog.is_debug():
                    ftlog.debug('UserConditionOR.check <<< gameId=', gameId,
                                'userId=', userId,
                                'clientId=', clientId,
                                'timestamp=', timestamp,
                                'kwargs=', kwargs,
                                'conditions=', self.conditions,
                                'condition=', condition,
                                'ret=', True)
                return True

        if ftlog.is_debug():
            ftlog.debug('UserConditionOR.check <<< gameId=', gameId,
                        'userId=', userId,
                        'clientId=', clientId,
                        'timestamp=', timestamp,
                        'kwargs=', kwargs,
                        'conditions=', self.conditions,
                        'ret=', False)
        return False

    def decodeFromDict(self, d):
        self.conditions = UserConditionRegister.decodeList(d.get('list', []))
        return self


class UserConditionAND(UserCondition):
    """多个条件的与关系，所有条件都满足，结果才满足
    """
    TYPE_ID = 'user.cond.and'

    def __init__(self):
        super(UserConditionAND, self).__init__()
        self.conditions = []

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        if ftlog.is_debug():
            ftlog.debug('UserConditionAND.check >>> gameId=', gameId,
                        'userId=', userId,
                        'clientId=', clientId,
                        'timestamp=', timestamp,
                        'kwargs=', kwargs,
                        'conditions=', self.conditions)
        for condition in self.conditions:
            if not condition.check(gameId, userId, clientId, timestamp, **kwargs):
                if ftlog.is_debug():
                    ftlog.debug('UserConditionAND.check <<< gameId=', gameId,
                                'userId=', userId,
                                'clientId=', clientId,
                                'timestamp=', timestamp,
                                'kwargs=', kwargs,
                                'conditions=', self.conditions,
                                'condition=', condition,
                                'ret=', False)
                return False
        if ftlog.is_debug():
            ftlog.debug('UserConditionAND.check <<< gameId=', gameId,
                        'userId=', userId,
                        'clientId=', clientId,
                        'timestamp=', timestamp,
                        'kwargs=', kwargs,
                        'conditions=', self.conditions,
                        'ret=', True)
        return True

    def decodeFromDict(self, d):
        self.conditions = UserConditionRegister.decodeList(d.get('list', []))
        return self
    

class UserConditionNOT(UserCondition):
    """单个条件的非关系
    1）条件满足，返回不满足
    2）条件不满足，返回满足
    """
    TYPE_ID = 'user.cond.not'

    def __init__(self):
        super(UserConditionNOT, self).__init__()
        self.condition = {}

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        if ftlog.is_debug():
            ftlog.debug('UserConditionNOT.check >>> gameId=', gameId,
                        'userId=', userId,
                        'clientId=', clientId,
                        'timestamp=', timestamp,
                        'kwargs=', kwargs,
                        'condition=', self.condition,
                        'ret NOT!!!')
            
        if self.condition.check(gameId, userId, clientId, timestamp, **kwargs):
            return False
        else:
            return True

    def decodeFromDict(self, d):
        self.condition = UserConditionRegister.decodeFromDict(d.get('condition', {}))
        return self


class UserConditionDayFirstLogin(UserCondition):
    TYPE_ID = 'user.cond.dayfirstlogin'

    def __init__(self):
        super(UserConditionDayFirstLogin, self).__init__()

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        return kwargs.get('isDayFirstLogin', False)

    def decodeFromDict(self, d):
        return self


class UserConditionNotDayFirstLogin(UserCondition):
    TYPE_ID = 'user.cond.notdayfirstlogin'

    def __init__(self):
        super(UserConditionNotDayFirstLogin, self).__init__()

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        return not kwargs.get('isDayFirstLogin', False)

    def decodeFromDict(self, d):
        return self


class UserConditionChargeTotal(UserCondition):
    TYPE_ID = 'user.cond.chargeTotal'

    def __init__(self):
        super(UserConditionChargeTotal, self).__init__()
        self.minCharge = None
        self.maxCharge = None

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        chargeTotal = pkuserdata.getAttrInt(userId, 'chargeTotal')
        return (self.minCharge == -1 or chargeTotal >= self.minCharge) \
               and (self.maxCharge == -1 or chargeTotal < self.maxCharge)

    def decodeFromDict(self, d):
        self.minCharge = d.get('minCharge', -1)
        if not isinstance(self.minCharge, (int, float)) or self.minCharge < -1:
            raise TYBizConfException(d, 'UserConditionChargeTotal.minCharge must be int >= -1')
        self.maxCharge = d.get('maxCharge', -1)
        if not isinstance(self.maxCharge, (int, float)) or self.maxCharge < -1:
            raise TYBizConfException(d, 'UserConditionChargeTotal.maxCharge must be int >= -1')
        if self.maxCharge != -1 and self.maxCharge < self.minCharge:
            raise TYBizConfException(d, 'UserConditionChargeTotal.maxCharge must >= minCharge')
        return self


class UserConditionTimeInToday(UserCondition):
    TYPE_ID = 'user.cond.time.today'

    def __init__(self):
        super(UserConditionTimeInToday, self).__init__()
        self.begin = None
        self.end = None

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        curTime = pktimestamp.getDayPastSeconds()
        if ftlog.is_debug():
            ftlog.debug('UserConditionTimeInToday.check curTime: ', curTime, ' begin: ', self.begin, ' end: ', self.end)

        return (self.begin == -1 or curTime >= self.begin) and (self.end == -1 or self.end > curTime)

    def decodeFromDict(self, d):
        self.begin = d.get('begin', -1)
        if not isinstance(self.begin, (int, float)) or self.begin < -1:
            raise TYBizConfException(d, 'UserConditionTimeInToday.begin must be int >= -1')

        self.end = d.get('end', -1)
        if not isinstance(self.end, (int, float)) or self.end < -1:
            raise TYBizConfException(d, 'UserConditionTimeInToday.end must be int >= -1')


class UserConditionInWhichGame(UserCondition):
    TYPE_ID = 'user.cond.which.game'

    def __init__(self):
        super(UserConditionInWhichGame, self).__init__()
        self.gameId = None

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        gameIdList = onlinedata.getGameEnterIds(userId)
        if ftlog.is_debug():
            ftlog.debug('UserConditionInWhichGame.check gameIdList: ', gameIdList, ' gameId: ', self.gameId)

        return self.gameId in gameIdList

    def decodeFromDict(self, d):
        self.gameId = d.get('gameId', -1)
        if not isinstance(self.gameId, (int, float)) or self.gameId < -1:
            raise TYBizConfException(d, 'UserConditionInWhichGame.gameId must be int >= -1')


# {
#     "dashifen": {
#         "6": {
#             "curmaxscore": 15,
#             "des": "斗地主房间中每次胜利都可获得大师分，高倍数、高级房间、会员获得的更快！",
#             "premaxscore": 5,
#             "name": "斗地主",
#             "level": 2,
#             "index": 0,
#             "pic": "http://111.203.187.150:8040/dizhu/skillscore/imgs/skillscorenew_002.png",
#             "score": 6,
#             "title": "http://111.203.187.150:8040/dizhu/skillscore/imgs/ddz_skill_score_title.png"
#         }
#     }
# }        
class UserConditionFavoriteGameTopN(UserCondition):
    TYPE_ID = 'user.cond.game.dashifen.topn'

    def __init__(self):
        super(UserConditionFavoriteGameTopN, self).__init__()
        self.gameId = None
        self.topn = None

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        info = hallaccount.getGameInfo(userId, clientId)
        if ftlog.is_debug():
            ftlog.debug('UserConditionFavoriteGameTopN.check gameInfo:', info)

        dashifen = info.get('dashifen', {})
        newDict = {}
        for gameStr in dashifen:
            newDict[gameStr] = dashifen[gameStr].get('level', 0)

        if ftlog.is_debug():
            ftlog.debug('UserConditionFavoriteGameTopN.newDict : ', newDict)

        newList = sorted(newDict.keys(), lambda x, y: cmp(newDict[x], newDict[y]), reverse=True)
        if ftlog.is_debug():
            ftlog.debug('UserConditionFavoriteGameTopN.newList : ', newList, ' topN:', self.topn)

        gameIdStr = str(self.gameId)
        if gameIdStr not in newList:
            return False

        return newList.index(gameIdStr) < self.topn

    def decodeFromDict(self, d):
        self.gameId = d.get('gameId', -1)
        if not isinstance(self.gameId, (int, float)) or self.gameId < -1:
            raise TYBizConfException(d, 'UserConditionFavoriteGameTopN.gameId must be int >= -1')

        self.topn = d.get('topn', -1)
        if not isinstance(self.topn, (int, float)) or self.topn < -1:
            raise TYBizConfException(d, 'UserConditionFavoriteGameTopN.topn must be int >= -1')


class UserConditionGameTimeTopN(UserCondition):
    TYPE_ID = 'user.cond.game.time.topn'

    def __init__(self):
        super(UserConditionGameTimeTopN, self).__init__()
        self.gameId = None
        self.topn = None

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        info = hallaccount.getGameInfo(userId, clientId)
        if ftlog.is_debug():
            ftlog.debug('UserConditionGameTimeTopN.check gameInfo:', info)

        dashifen = info.get('dashifen', {})
        newDict = {}
        for gameStr in dashifen:
            newDict[gameStr] = dashifen[gameStr].get('gameTime', 0)

        if ftlog.is_debug():
            ftlog.debug('UserConditionGameTimeTopN.newDict : ', newDict)

        newList = sorted(newDict.keys(), lambda x, y: cmp(newDict[x], newDict[y]), reverse=True)
        if ftlog.is_debug():
            ftlog.debug('UserConditionGameTimeTopN.newList : ', newList, ' topn:', self.topn)

        gameIdStr = str(self.gameId)
        if gameIdStr not in newList:
            return False

        return newList.index(gameIdStr) < self.topn

    def decodeFromDict(self, d):
        self.gameId = d.get('gameId', -1)
        if not isinstance(self.gameId, (int, float)) or self.gameId < -1:
            raise TYBizConfException(d, 'UserConditionGameTimeTopN.gameId must be int >= -1')

        self.topn = d.get('topn', -1)
        if not isinstance(self.topn, (int, float)) or self.topn < -1:
            raise TYBizConfException(d, 'UserConditionGameTimeTopN.topn must be int >= -1')


class UserConditionGameWinChipsTopN(UserCondition):
    TYPE_ID = 'user.cond.game.winchips.topn'

    def __init__(self):
        super(UserConditionGameWinChipsTopN, self).__init__()
        self.gameId = None
        self.topn = None

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        info = hallaccount.getGameInfo(userId, clientId)
        if ftlog.is_debug():
            ftlog.debug('UserConditionGameWinChipsTopN.check gameInfo:', info)

        dashifen = info.get('dashifen', {})
        newDict = {}
        for gameStr in dashifen:
            newDict[gameStr] = dashifen[gameStr].get('winChips', 0)

        if ftlog.is_debug():
            ftlog.debug('UserConditionGameWinChipsTopN.newDict : ', newDict)

        newList = sorted(newDict.keys(), lambda x, y: cmp(newDict[x], newDict[y]), reverse=True)
        if ftlog.is_debug():
            ftlog.debug('UserConditionGameWinChipsTopN.newList : ', newList, ' topN: ', self.topn)

        gameIdStr = str(self.gameId)
        if gameIdStr not in newList:
            return False

        return newList.index(gameIdStr) < self.topn

    def decodeFromDict(self, d):
        self.gameId = d.get('gameId', -1)
        if not isinstance(self.gameId, (int, float)) or self.gameId < -1:
            raise TYBizConfException(d, 'UserConditionGameWinChipsTopN.gameId must be int >= -1')

        self.topn = d.get('topn', -1)
        if not isinstance(self.topn, (int, float)) or self.topn < -1:
            raise TYBizConfException(d, 'UserConditionGameWinChipsTopN.topn must be int >= -1')


class UserConditionGameMatchScoresTopN(UserCondition):
    TYPE_ID = 'user.cond.game.matchScores.topn'

    def __init__(self):
        super(UserConditionGameMatchScoresTopN, self).__init__()
        self.gameId = None
        self.topn = None

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        info = hallaccount.getGameInfo(userId, clientId)
        if ftlog.is_debug():
            ftlog.debug('UserConditionGameMatchScoresTopN.check gameInfo:', info)

        dashifen = info.get('dashifen', {})
        newDict = {}
        for gameStr in dashifen:
            newDict[gameStr] = dashifen[gameStr].get('matchScores', 0)

        if ftlog.is_debug():
            ftlog.debug('UserConditionGameMatchScoresTopN.newDict : ', newDict)

        newList = sorted(newDict.keys(), lambda x, y: cmp(newDict[x], newDict[y]), reverse=True)
        if ftlog.is_debug():
            ftlog.debug('UserConditionGameMatchScoresTopN.newList : ', newList, ' topN:', self.topn)

        gameIdStr = str(self.gameId)
        if gameIdStr not in newList:
            return False

        return newList.index(gameIdStr) < self.topn

    def decodeFromDict(self, d):
        self.gameId = d.get('gameId', -1)
        if not isinstance(self.gameId, (int, float)) or self.gameId < -1:
            raise TYBizConfException(d, 'UserConditionGameMatchScoresTopN.gameId must be int >= -1')

        self.topn = d.get('topn', -1)
        if not isinstance(self.topn, (int, float)) or self.topn < -1:
            raise TYBizConfException(d, 'UserConditionGameMatchScoresTopN.topn must be int >= -1')


class UserConditionGameLoginSumTopN(UserCondition):
    TYPE_ID = 'user.cond.game.loginsum.topn'

    def __init__(self):
        super(UserConditionGameLoginSumTopN, self).__init__()
        self.gameId = None
        self.topn = None

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        info = hallaccount.getGameInfo(userId, clientId)
        if ftlog.is_debug():
            ftlog.debug('UserConditionGameLoginSumTopN.check gameInfo:', info)

        dashifen = info.get('dashifen', {})
        newDict = {}
        for gameStr in dashifen:
            newDict[gameStr] = dashifen[gameStr].get('loginSum', 0)

        if ftlog.is_debug():
            ftlog.debug('UserConditionGameLoginSumTopN.newDict : ', newDict)

        newList = sorted(newDict.keys(), lambda x, y: cmp(newDict[x], newDict[y]), reverse=True)
        if ftlog.is_debug():
            ftlog.debug('UserConditionGameLoginSumTopN.newList : ', newList, ' topN: ', self.topn)

        gameIdStr = str(self.gameId)
        if gameIdStr not in newList:
            return False

        return newList.index(gameIdStr) < self.topn

    def decodeFromDict(self, d):
        self.gameId = d.get('gameId', -1)
        if not isinstance(self.gameId, (int, float)) or self.gameId < -1:
            raise TYBizConfException(d, 'UserConditionGameLoginSumTopN.gameId must be int >= -1')

        self.topn = d.get('topn', -1)
        if not isinstance(self.topn, (int, float)) or self.topn < -1:
            raise TYBizConfException(d, 'UserConditionGameLoginSumTopN.topn must be int >= -1')


class UserConditionCity(UserCondition):
    TYPE_ID = 'user.cond.city'

    def __init__(self):
        super(UserConditionCity, self).__init__()
        self.city = None

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        c = sessiondata.getCityName(userId)
        if ftlog.is_debug():
            ftlog.debug('UserConditionCity.check userCity: ', c, ' city:', self.city)
        return self.city == c

    def decodeFromDict(self, d):
        self.city = d.get('city', '全国')
        if not isstring(self.city):
            raise TYBizConfException(d, 'UserConditionCity.city must be string')


class UserConditionForbiddenCitys(UserCondition):
    TYPE_ID = 'user.cond.forbidden.citys'

    def __init__(self):
        super(UserConditionForbiddenCitys, self).__init__()
        self.citys = None

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        c = sessiondata.getCityName(userId)
        if ftlog.is_debug():
            ftlog.debug('UserConditionForbiddenCitys.check userCity: ', c, ' citys:', self.citys)
        return c not in self.citys

    def decodeFromDict(self, d):
        self.citys = d.get('citys', [])
        if not isinstance(self.citys, list):
            raise TYBizConfException(d, 'UserConditionForbiddenCitys.citys must be list')


class UserConditionCitys(UserCondition):
    TYPE_ID = 'user.cond.citys'

    def __init__(self):
        super(UserConditionCitys, self).__init__()
        self.citys = None

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        c = sessiondata.getCityName(userId)
        if ftlog.is_debug():
            ftlog.debug('UserConditionCitys.check userCity: ', c, ' citys:', self.citys, ' isin' , c in self.citys)
        return c in self.citys

    def decodeFromDict(self, d):
        self.citys = d.get('citys', [])
        import json
        self.citys = [''.join(json.dumps(city).split('"')) for city in self.citys]
        ftlog.debug("UserConditionCitys.decodeFromDict|citys|",self.citys)
        if not isinstance(self.citys, list):
            raise TYBizConfException(d, 'UserConditionCitys.citys must be list')


class UserConditionHasUnSendTuyooRedenvelope(UserCondition):
    TYPE_ID = 'user.cond.unsend.tuyoo.redenvelope'

    def __init__(self):
        super(UserConditionHasUnSendTuyooRedenvelope, self).__init__()
        self.type = None

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        from hall.entity import hallconf
        from poker.entity.game.game import TYGame

        gameids = hallconf.getDaShiFenFilter(clientId)
        for gid in gameids:
            shareInfo = TYGame(gid).getTuyooRedEnvelopeShareTask(userId, clientId, self.type)
            if ftlog.is_debug():
                ftlog.debug('UserConditionHasUnSendTuyooRedenvelope.check gameId:', gid, ' shareInfo:', shareInfo)

            if shareInfo:
                return True
        return False

    def decodeFromDict(self, d):
        self.type = d.get('type', '')
    
class UserConditionOS(UserCondition):
    TYPE_ID = 'user.cond.os'

    def __init__(self):
        super(UserConditionOS, self).__init__()
        self.os = None

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        clientOS, _, _ = strutil.parseClientId(clientId)
        if ftlog.is_debug():
            ftlog.debug('UserConditionOS.check os:', self.os,
                        ' clientOS:', clientOS)
            
        return clientOS == self.os

    def decodeFromDict(self, d):
        self.os = d.get('os', '')
        if not isstring(self.os):
            raise TYBizConfException(d, 'UserConditionOS.os must be string')

class UserConditionClientOS(UserCondition):
    TYPE_ID = 'user.cond.clientOS'

    def __init__(self):
        super(UserConditionOS, self).__init__()
        self.clientOSList = None

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        clientOS, _, _ = strutil.parseClientId(clientId)
        if ftlog.is_debug():
            ftlog.debug('UserConditionClientOS.check',
                        'gameId=', gameId,
                        'userId=', userId,
                        'clientId=', clientId,
                        'clientOS=', clientOS,
                        'clientOSList=', self.clientOSList)
        
        return clientOS.lower() in self.clientOSList

    def decodeFromDict(self, d):
        clientOSList = d.get('clientOSList', [])
        if not isinstance(clientOSList, list):
            raise TYBizConfException(d, 'UserConditionClientOS.clientOSList must be string')
        self.clientOSList = []
        for clientOS in clientOSList:
            self.clientOSList.append(clientOS.lower())
        

class UserConditionFalse(UserCondition):
    TYPE_ID = 'user.cond.false'

    def __init__(self):
        super(UserConditionFalse, self).__init__()

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        return False
        
    def decodeFromDict(self, d):
        return self


class UserConditionDateTime(UserCondition):
    TYPE_ID = 'user.cond.datetime'

    def __init__(self):
        super(UserConditionDateTime, self).__init__()
        self.start = None
        self.end = None
        self.format = None

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        return self.start <= timestamp < self.end

    def decodeFromDict(self, d):
        self.format = d.get('format')
        self.start = time.mktime(time.strptime(d.get('start'), self.format))
        self.end = time.mktime(time.strptime(d.get('end'), self.format))
        return self

class UserConditionCanBuyProduct(UserCondition):
    TYPE_ID = 'user.cond.canBuyProduct'

    def __init__(self):
        super(UserConditionCanBuyProduct, self).__init__()
        self.productIds = None

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        from hall.entity import hallstore
        try:
            for productId in self.productIds:
                product = hallstore.findProduct(gameId, userId, productId)
                if product and hallstore.storeSystem.canBuyProduct(gameId, userId, clientId, product, 1):
                    if ftlog.is_debug():
                        ftlog.debug('UserConditionCanBuyProduct.check',
                                    'gameId=', gameId,
                                    'userId=', userId,
                                    'clientId=', clientId,
                                    'timestamp=', timestamp,
                                    'productIds=', self.productIds,
                                    'ret=', True)
                    return True
            if ftlog.is_debug():
                ftlog.debug('UserConditionCanBuyProduct.check',
                            'gameId=', gameId,
                            'userId=', userId,
                            'clientId=', clientId,
                            'timestamp=', timestamp,
                            'productIds=', self.productIds,
                            'ret=', False)
            return False
        except:
            ftlog.error('UserConditionCanBuyProduct.check',
                        'gameId=', gameId,
                        'userId=', userId,
                        'clientId=', clientId,
                        'timestamp=', timestamp,
                        'productIds=', self.productIds)
            return False

    def decodeFromDict(self, d):
        productIds = d.get('productIds', [])
        if not productIds:
            raise TYBizConfException(d, 'UserConditionCanBuyProduct.productIds must be string list')
        for productId in productIds:
            if not productId or not isstring(productId):
                raise TYBizConfException(d, 'UserConditionCanBuyProduct.productIds must be string list')
        self.productIds = productIds
        return self

class UserConditionUnGotLoginReward(UserCondition):
    TYPE_ID = 'user.cond.ungot.loginReward'

    def __init__(self):
        super(UserConditionUnGotLoginReward, self).__init__()
        self.start = None
        self.end = None

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        loginReward = gamedata.getGameAttrInt(userId, HALL_GAMEID, 'login_reward')
        ftlog.debug('UserConditionUnGotLoginReward.check start:', self.start
                , ' end:', self.end
                , ' loginReward:', loginReward)
        if self.start <= loginReward <= self.end:
            return False
        return True

    def decodeFromDict(self, d):
        self.start = time.mktime(time.strptime(d.get('start'), '%Y-%m-%d %H:%M:%S'))
        self.end = time.mktime(time.strptime(d.get('end'), '%Y-%m-%d %H:%M:%S'))
        return self

class UserConditionShowTutorial(UserCondition):    
    TYPE_ID = 'user.cond.tutorial'
    
    def __init__(self):
        super(UserConditionShowTutorial, self).__init__()
        self.state = -1
        self.gameId = 0

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        from poker.entity.game.game import TYGame
        
        state = TYGame(self.gameId).getPlayGameInfoByKey(userId, clientId, 'already_show_tutorial')
        ftlog.debug('UserConditionShowTutorial.check state:', state
                    , ' self.state:', self.state)
        return (self.state == state)

    def decodeFromDict(self, d):
        self.state = d.get('state', -1)
        self.gameId = d.get('gameId', 0)
        return self


class UserConditionNotIsMonthCard(UserCondition):
    TYPE_ID = 'user.cond.notIsMonthCard'

    def __init__(self):
        super(UserConditionNotIsMonthCard, self).__init__()

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        from hall.entity import hallitem
        userBag = hallitem.itemSystem.loadUserAssets(userId).getUserBag()
        monthCardItem = userBag.getItemByKindId(hallitem.ITEM_CROWN_MONTHCARD_KIND_ID)
        if not monthCardItem:
            return True
        return False

    def decodeFromDict(self, d):
        return self

class UserConditionIsMonthCard(UserCondition):
    TYPE_ID = 'user.cond.isMonthCard'

    def __init__(self):
        super(UserConditionIsMonthCard, self).__init__()


    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        from hall.entity import hallitem
        userBag = hallitem.itemSystem.loadUserAssets(userId).getUserBag()
        monthCardItem = userBag.getItemByKindId(hallitem.ITEM_CROWN_MONTHCARD_KIND_ID)
        if monthCardItem:
            return True
        return False

    def decodeFromDict(self, d):
        return self

class UserConditionIsHonorMonthCard(UserCondition):
    TYPE_ID = 'user.cond.ishonorMonthCard'

    def __init__(self):
        super(UserConditionIsHonorMonthCard, self).__init__()


    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        from hall.entity import hallitem
        userBag = hallitem.itemSystem.loadUserAssets(userId).getUserBag()
        monthCardItem = userBag.getItemByKindId(hallitem.ITEM_HONOR_MONTHCARD_KIND_ID)
        if monthCardItem:
            return True
        return False

    def decodeFromDict(self, d):
        return self

class UserConditionNotIsHonorMonthCard(UserCondition):
    TYPE_ID = 'user.cond.notIshonorMonthCard'

    def __init__(self):
        super(UserConditionNotIsHonorMonthCard, self).__init__()


    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        from hall.entity import hallitem
        userBag = hallitem.itemSystem.loadUserAssets(userId).getUserBag()
        monthCardItem = userBag.getItemByKindId(hallitem.ITEM_HONOR_MONTHCARD_KIND_ID)
        if not monthCardItem:
            return True
        return False

    def decodeFromDict(self, d):
        return self

class UserConditionNotGetHonorMonthCard(UserCondition):
    TYPE_ID = 'user.cond.notGetHonorMonthCard'

    def __init__(self):
        super(UserConditionNotGetHonorMonthCard, self).__init__()


    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        return gamedata.getGameAttr(userId, HALL_GAMEID, "honormonthcardreward") == 0

    def decodeFromDict(self, d):
        return self

class UserConditionVipExp(UserCondition):
    TYPE_ID = 'user.cond.vipExp'

    def __init__(self, startExp=-1, stopExp=-1):
        super(UserConditionVipExp, self).__init__()
        self.startExp = startExp
        self.stopExp = stopExp

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        from hall.entity import hallvip
        try:
            userVip = hallvip.userVipSystem.getUserVip(userId)
            startCondition = (self.startExp == -1 or userVip.vipExp >= self.startExp)
            stopCondition = (self.stopExp == -1 or userVip.vipExp < self.stopExp)
            if ftlog.is_debug():
                ftlog.debug('UserConditionVipExp.check'
                            'userId=', userId,
                            'gameId=', gameId,
                            'userVipExp=', userVip.vipExp,
                            'range=', '[%s, %s)' % (self.startExp, self.stopExp),
                            'startCondition=', startCondition,
                            'stopCondition=', stopCondition)
            return startCondition and stopCondition
        except:
            ftlog.error()
            return False

    def decodeFromDict(self, d):
        self.startExp = d.get('startExp', -1)
        if not isinstance(self.startExp, int) or self.startExp < -1:
            raise TYBizConfException(d, 'UserConditionVipLevel.startExp must be int >= -1')
        self.stopExp = d.get('stopExp', -1)
        if not isinstance(self.stopExp, int) or self.stopExp < -1:
            raise TYBizConfException(d, 'UserConditionVipLevel.stopExp must be int >= -1')
        if self.stopExp != -1 and self.stopExp < self.startExp:
            raise TYBizConfException(d, 'UserConditionVipLevel.stopExp must >= startExp')
        return self

class UserConditionUserBehaviourA(UserCondition):
    TYPE_ID = 'user.cond.userBehaviourA'
    
    def __init__(self):
        super(UserConditionUserBehaviourA, self).__init__()
        self.gameId = None
        self.newUserCond = UserConditionNewUser()

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        if self.newUserCond.check(gameId, userId, clientId, timestamp):
            if ftlog.is_debug():
                ftlog.debug('user.cond.userBehaviourA userId=', userId, 'gameId=', self.gameId, 'newUserCond.check.fail')
            return False

        behaviourInfo = daobase.executeUserCmd(userId, 'hget', 'userBehaviour:6:' + str(userId), 'info')
        if ftlog.is_debug():
            ftlog.debug('user.cond.userBehaviourA userId=', userId, 'gameId=', self.gameId, 'behaviourInfo=', behaviourInfo)
        if not behaviourInfo:
            return False

        try:
            behaviourInfo = strutil.loads(behaviourInfo)
        except Exception, e:
            ftlog.warn('user.cond.userBehaviourA.Exception userId=', userId, 'gameId=', self.gameId, 'err=', e)
            return False

        if behaviourInfo.get('type', 0) == 1:
            return True
        return False

    def decodeFromDict(self, d):
        self.gameId = d.get('gameId', 6)
        if not isinstance(self.gameId, int):
            raise TYBizConfException(d, 'UserConditionUserBehaviourA.gameId must be int')
        return self

class UserConditionHasMyCardNo(UserCondition):
    TYPE_ID = 'user.cond.hasMyCardNo'
    def __init__(self):
        super(UserConditionHasMyCardNo, self).__init__()
    
    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        myCardNo = userdata.getAttr(userId, 'myCardNo')
        return True if myCardNo else False
    
    def decodeFromDict(self, d):
        return self

class UserConditionIsGuest(UserCondition):
    TYPE_ID = 'user.cond.isGuest'
    def __init__(self):
        super(UserConditionIsGuest, self).__init__()
    
    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        isbind = userdata.getAttr(userId, 'isbind')
        return not isbind
    
    def decodeFromDict(self, d):
        return self
    
class UserConditionCheckGameData(UserCondition):
    TYPE_ID = 'user.cond.check.gamedata'
    def __init__(self):
        super(UserConditionCheckGameData, self).__init__()
    
    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        keyAttr = gamedata.getGameAttr(userId, self.gameId, self.key)
        if not keyAttr:
            keyAttr = self.default
        else:
            keyAttr = str(keyAttr)
            
        ftlog.debug('UserConditionCheckGameData.check gameId:', self.gameId
                    , ' key:', self.key
                    , ' value:', keyAttr
                    , ' scope:', self.scope
                    , ' result:', (keyAttr in self.scope))
        return keyAttr in self.scope
    
    def decodeFromDict(self, d):
        self.gameId = d.get('gameId', 0)
        if (not isinstance(self.gameId, int)) or (self.gameId <= 0):
            raise TYBizConfException(d, 'UserConditionCheckGameData.gameId must be int > 0')
        
        self.key = d.get('key', None)
        if (not isstring(self.key)) or (not self.key):
            raise TYBizConfException(d, 'UserConditionCheckGameData.key must be string')
        
        self.default = d.get('default', None)
        if (not isstring(self.default)) or (not self.default):
            raise TYBizConfException(d, 'UserConditionCheckGameData.default must be string')
        
        self.scope = d.get('scope', None)
        if (not self.scope) or (not isinstance(self.scope, list)):
            raise TYBizConfException(d, 'UserConditionCheckGameData.scope must be list')
        
        return self
    
class UserConditionCheckBiggestHallVer(UserCondition):
    '''
    检查用户登录途游棋牌的最高版本号
    [start, stop)
    '''
    TYPE_ID = 'user.cond.check.biggestHallVer'
    def __init__(self):
        super(UserConditionCheckBiggestHallVer, self).__init__()
    
    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        biggestHallVerStr = gamedata.getGameAttr(userId, HALL_GAMEID, 'biggestHallVer')
        if not biggestHallVerStr:
            return False
        
        biggestHallVer = float(biggestHallVerStr)
        ftlog.debug('UserConditionCheckBiggestHallVer.check biggestHallVer:', biggestHallVer
                    , ' start:', self.start
                    , ' stop:', self.stop
                    , ' result:', (biggestHallVer >= self.start and biggestHallVer < self.stop))
        return biggestHallVer >= self.start and biggestHallVer < self.stop
    
    def decodeFromDict(self, d):
        self.start = d.get('start', None)
        if (not isinstance(self.start, float)) or (self.start < 0):
            raise TYBizConfException(d, 'UserConditionCheckBiggestHallVer.start must be float > 0')
        
        self.stop = d.get('stop', None)
        if (not isinstance(self.stop, float)) or (self.stop < 0):
            raise TYBizConfException(d, 'UserConditionCheckBiggestHallVer.stop must be float > 0')
        
        if self.stop <= self.start:
            raise TYBizConfException(d, 'UserConditionCheckBiggestHallVer.start must < stop')
        
        return self

class UserConditionLastChargeType(UserCondition):
    TYPE_ID = 'user.cond.lastChargeType'

    def __init__(self):
        super(UserConditionLastChargeType, self).__init__()
        self.lastChargeTypes = None
    
    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        lastCharageType = userdata.getAttr(userId, 'lastChargeType')
        return lastCharageType in self.lastChargeTypes

    def decodeFromDict(self, d):
        lastChargeTypes = d.get('lastChargeTypes', [])
        if not isinstance(lastChargeTypes, list):
            raise TYBizConfException('UserConditionLastChargeType.lastChargeTypes must be string list')
        self.lastChargeTypes = set(lastChargeTypes)
        return self

class UserConditionLastChargeTypeTuyooios(UserConditionLastChargeType):
    TYPE_ID = 'user.cond.lastChargeType.tuyooios'
    
    def __init__(self):
        super(UserConditionLastChargeTypeTuyooios, self).__init__()
        self.lastChargeTypes = set(['tuyooios'])
    
    def decodeFromDict(self, d):
        return self
    
class UserConditionUserIdTailNumber(UserCondition):
    """判断用户ID尾号是否满足条件
    """
    TYPE_ID = 'user.cond.userIdTailNumber'
    def __init__(self):
        super(UserConditionUserIdTailNumber, self).__init__()
        self.userIdTailNumber = None
    
    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        assert(isinstance(userId, int))
        assert(userId > 0)
        tn = userId % 10
        if ftlog.is_debug():
            ftlog.debug('UserConditionUserIdTailNumber.check userIdTailNumber: ', self.userIdTailNumber, ' userId:', userId)
        return tn in self.userIdTailNumber
    
    def decodeFromDict(self, d):
        self.userIdTailNumber = d.get('userIdTailNumber', [])
        if not isinstance(self.userIdTailNumber, list):
            raise TYBizConfException(d, 'UserConditionUserIdTailNumber.userIdTailNumber must be list')
        return self

class UserConditionInSnsIds(UserCondition):
    '''
    判断用户snsId是否在列表中
    '''
    TYPE_ID = 'user.cond.inSnsIds'
    def __init__(self):
        super(UserConditionInSnsIds, self).__init__()
        self.snsIds = None
    
    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        snsId = userdata.getAttr(userId, 'snsId')
        if ftlog.is_debug():
            ftlog.debug('UserConditionInSnsIds.check',
                        'userId=', userId,
                        'clientId=', clientId,
                        'snsIds=', self.snsIds,
                        'snsId=', snsId)
            
        if not snsId:
            return False
        
        snsCh = snsId.split(':', 1)[0]
        return snsCh in self.snsIds

    def decodeFromDict(self, d):
        self.snsIds = d.get('snsIds', [])
        if not isinstance(self.snsIds, list):
            raise TYBizConfException(d, 'UserConditionInSnsIds.snsIds must be list')
        return self

class UserConditionPrevClientId(UserCondition):
    '''
    判断用户上次登录的clientId在numClientIds里
    '''
    TYPE_ID = 'user.cond.prevClientId'
    def __init__(self):
        super(UserConditionPrevClientId, self).__init__()
        self.numClientIds = None
    
    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        from hall.entity import halluser
        numClientId = pokerconf.clientIdToNumber(clientId)

        if ftlog.is_debug():
            ftlog.debug('UserConditionPrevClientId.check',
                        'userId=', userId,
                        'clientId=', clientId,
                        'numClientId=', numClientId,
                        'numClientIds=', self.numClientIds)
        
        if numClientId in self.numClientIds:
            return False
        
        hisClientIds = halluser.getHistoryClientIds(userId, gameId)
        return len(hisClientIds) > 1 and hisClientIds[-2] in self.numClientIds

    def decodeFromDict(self, d):
        self.numClientIds = d.get('numClientIds', [])
        if not isinstance(self.numClientIds, list):
            raise TYBizConfException(d, 'UserConditionPrevClientId.numClientIds must be list')
        return self

class UserConditionRegister(TYConfableRegister):
    _typeid_clz_map = {
        # AND条件
        UserConditionAND.TYPE_ID: UserConditionAND,
        # OR条件
        UserConditionOR.TYPE_ID: UserConditionOR,
        # 非条件
        UserConditionNOT.TYPE_ID: UserConditionNOT,
        # 已首冲
        UserConditionFirstRecharged.TYPE_ID: UserConditionFirstRecharged,
        # clientId中的gameId是否与我的gameId一致
        UserConditionisMyGameid.TYPE_ID: UserConditionisMyGameid,
        # 是否与当前插件游戏的ID一致
        UserConditionPluginId.TYPE_ID: UserConditionPluginId,
        # 未首冲
        UserConditionUnFirstRecharged.TYPE_ID: UserConditionUnFirstRecharged,
        # 已领取首冲奖励
        UserConditionGotFirstRechargeReward.TYPE_ID: UserConditionGotFirstRechargeReward,
        # 没有领取首冲奖励
        UserConditionUnGotFirstRechargeReward.TYPE_ID: UserConditionUnGotFirstRechargeReward,
        # VIP级别
        UserConditionVipLevel.TYPE_ID: UserConditionVipLevel,
        # 奖券携带量
        UserConditionCoupon.TYPE_ID: UserConditionCoupon,
        # 金币携带量
        UserConditionChip.TYPE_ID: UserConditionChip,
        # 钻石携带量
        UserConditionDiamond.TYPE_ID: UserConditionDiamond,
        # 性别
        UserConditionSex.TYPE_ID: UserConditionSex,
        # 注册天数
        UserConditionRegisterDay.TYPE_ID: UserConditionRegisterDay,
        # 新用户
        UserConditionNewUser.TYPE_ID: UserConditionNewUser,
        # 是订阅会员
        UserConditionIsSubscribeMember.TYPE_ID: UserConditionIsSubscribeMember,
        # 是会员但不是订阅会员
        UserConditionIsMemberNotSub.TYPE_ID: UserConditionIsMemberNotSub,
        # 非订阅会员
        UserConditionNotSubscribeMember.TYPE_ID: UserConditionNotSubscribeMember,
        # 会员剩余天数
        UserConditionMemberRemDays.TYPE_ID: UserConditionMemberRemDays,
        # 日期判断
        UserConditionTimePeriod.TYPE_ID: UserConditionTimePeriod,
        # 支付至少一次
        UserConditionPayLeastOnce.TYPE_ID: UserConditionPayLeastOnce,
        # 已绑定手机号
        UserConditionBindPhone.TYPE_ID: UserConditionBindPhone,
        # 本日无签到
        UserConditionNotCheckInToday.TYPE_ID: UserConditionNotCheckInToday,
        # 本日已签到
        UserConditionCheckedInToday.TYPE_ID: UserConditionCheckedInToday,
        # 是否有签到奖励
        UserConditionCheckInHasReward.TYPE_ID: UserConditionCheckInHasReward,
        # 是否有抽奖卡
        UserConditionHasLuckyCard.TYPE_ID: UserConditionHasLuckyCard,
        # 是会员
        UserConditionIsMember.TYPE_ID: UserConditionIsMember,
        # 不是会员
        UserConditionNotIsMember.TYPE_ID: UserConditionNotIsMember,
        # 有会员充值弹窗
        UserConditionHasMemberBuyWindow.TYPE_ID: UserConditionHasMemberBuyWindow,
        # 有会员奖励
        UserConditionHasMemberReward.TYPE_ID: UserConditionHasMemberReward,
        # 有任务奖励
        UserConditionHasTaskReward.TYPE_ID: UserConditionHasTaskReward,
        # 任务完成
        UserConditionTaskAllDone.TYPE_ID: UserConditionTaskAllDone,
        # 没有五星好评
        UserConditionNotFiveStar.TYPE_ID: UserConditionNotFiveStar,
        # 有可补签天数
        UserConditionHasSupCheckinDay.TYPE_ID: UserConditionHasSupCheckinDay,
        # 是否有分享奖励
        UserConditionHasDailyShareReward.TYPE_ID: UserConditionHasDailyShareReward,
        # 是否有免费福利小红点
        UserConditionHasFreeMark.TYPE_ID: UserConditionHasFreeMark,
        # 是否有每日分享配置
        UserConditionHasDailyShareConfig.TYPE_ID: UserConditionHasDailyShareConfig,
        # clientIds的版本号
        UserConditionClientVersion.TYPE_ID: UserConditionClientVersion,
        # 非每日第一次登录
        UserConditionNotDayFirstLogin.TYPE_ID: UserConditionNotDayFirstLogin,
        # 每日第一次登陆
        UserConditionDayFirstLogin.TYPE_ID: UserConditionDayFirstLogin,
        # 充值总额
        UserConditionChargeTotal.TYPE_ID: UserConditionChargeTotal,
        # 登录天数取摸
        UserConditionsignDayMod.TYPE_ID: UserConditionsignDayMod,
        # 用户的支付次数
        UserConditionPayCount.TYPE_ID: UserConditionPayCount,
        # 没有支付
        UserConditionNonPay.TYPE_ID: UserConditionNonPay,
        # 时间段
        UserConditionTimeInToday.TYPE_ID: UserConditionTimeInToday,
        # 用户当前在哪个大厅游戏中
        UserConditionInWhichGame.TYPE_ID: UserConditionInWhichGame,
        # 用户最喜欢的游戏 大师分TOPN
        UserConditionFavoriteGameTopN.TYPE_ID: UserConditionFavoriteGameTopN,
        # 用户地区
        UserConditionCity.TYPE_ID: UserConditionCity,
        # 用户在某地区集合内
        UserConditionCitys.TYPE_ID: UserConditionCitys,
        # 用户在某个禁止地区集合内
        UserConditionForbiddenCitys.TYPE_ID: UserConditionForbiddenCitys,
        # 插件游戏时长TOPN
        UserConditionGameTimeTopN.TYPE_ID: UserConditionGameTimeTopN,
        # 用户赢取金币TOPN
        UserConditionGameWinChipsTopN.TYPE_ID: UserConditionGameWinChipsTopN,
        # loginSum 用户登录插件游戏的次数TOPN
        UserConditionGameLoginSumTopN.TYPE_ID: UserConditionGameLoginSumTopN,
        # 用户在插件游戏的比赛积分TOPN
        UserConditionGameMatchScoresTopN.TYPE_ID: UserConditionGameMatchScoresTopN,
        # 用户的clientId是否在特定的列表内
        UserConditionInClientIDs.TYPE_ID: UserConditionInClientIDs,
        # 用户的clientIds不在禁止列表内
        UserConditionNotInClientIDs.TYPE_ID: UserConditionNotInClientIDs,
        # 用户有未发送的途游红包
        UserConditionHasUnSendTuyooRedenvelope.TYPE_ID: UserConditionHasUnSendTuyooRedenvelope,
        # 用户的登录天数
        UserConditionLoginDays.TYPE_ID: UserConditionLoginDays,
        # 用户的累计游戏时长
        UserConditionPlayTime.TYPE_ID: UserConditionPlayTime,
        # 用户的分享次数
        UserConditionShareCount.TYPE_ID: UserConditionShareCount,
        # 用户本次登录与上次登录的时间差
        UserConditionReturnTime.TYPE_ID: UserConditionReturnTime,
        # 判断用户的操作系统
        UserConditionOS.TYPE_ID: UserConditionOS,
        # 福利时间，某段时间内第一次登录
        UserConditionBenefitsTime.TYPE_ID: UserConditionBenefitsTime,
        # 始终返回False的条件
        UserConditionFalse.TYPE_ID:UserConditionFalse,
        # 指定时间范围
        UserConditionDateTime.TYPE_ID: UserConditionDateTime,
        # 指定的时间段内没有领取登录奖励
        UserConditionUnGotLoginReward.TYPE_ID: UserConditionUnGotLoginReward,
        # 是否有指定的product
        UserConditionCanBuyProduct.TYPE_ID: UserConditionCanBuyProduct,
        # 是否显示新手教学
        UserConditionShowTutorial.TYPE_ID: UserConditionShowTutorial,
        # 用户的用户ID是否在白名单内
        UserConditionInWhiteList.TYPE_ID: UserConditionInWhiteList,
        # 用户背包没有月卡
        UserConditionNotIsMonthCard.TYPE_ID: UserConditionNotIsMonthCard,
        # 用户背包有月卡
        UserConditionIsMonthCard.TYPE_ID: UserConditionIsMonthCard,
        # 客户端操作系统
        UserConditionClientOS.TYPE_ID:UserConditionClientOS,
        # 用户背包有荣誉月卡
        UserConditionIsHonorMonthCard.TYPE_ID: UserConditionIsHonorMonthCard,
        # 用户背包没有荣誉月卡
        UserConditionNotIsHonorMonthCard.TYPE_ID: UserConditionNotIsHonorMonthCard,
        # 用户没有领取过荣誉月卡
        UserConditionNotGetHonorMonthCard.TYPE_ID: UserConditionNotGetHonorMonthCard,
        # 用户vip经验值
        UserConditionVipExp.TYPE_ID: UserConditionVipExp,
        # 用户行为A
        UserConditionUserBehaviourA.TYPE_ID:UserConditionUserBehaviourA,
        # 是否有cardNo字段
        UserConditionHasMyCardNo.TYPE_ID:UserConditionHasMyCardNo,
        # 是否游客
        UserConditionIsGuest.TYPE_ID:UserConditionIsGuest,
        # 用户注册时间的绝对范围
        UserConditionRegisterTime.TYPE_ID: UserConditionRegisterTime,
        # 检查gameData
        UserConditionCheckGameData.TYPE_ID: UserConditionCheckGameData,
        # 用户登录途游棋牌的最高客户端版本号
        UserConditionCheckBiggestHallVer.TYPE_ID : UserConditionCheckBiggestHallVer,
        # 最后支付使用的支付方式
        UserConditionLastChargeType.TYPE_ID: UserConditionLastChargeType,
        # 最后支付使用的支付方式为tuyooios
        UserConditionLastChargeTypeTuyooios.TYPE_ID: UserConditionLastChargeTypeTuyooios,
        # 是否拥有某项资产
        UserConditionHasAsset.TYPE_ID: UserConditionHasAsset,
        # 用户ID尾号是否满足
        UserConditionUserIdTailNumber.TYPE_ID: UserConditionUserIdTailNumber,
        # 判断用户snsId是否在列表中
        UserConditionInSnsIds.TYPE_ID: UserConditionInSnsIds,
        # 判断用户上次登录的clientId
        UserConditionPrevClientId.TYPE_ID: UserConditionPrevClientId,
    }
    

