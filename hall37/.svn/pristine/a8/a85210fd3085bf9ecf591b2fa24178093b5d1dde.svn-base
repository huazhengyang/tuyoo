# -*- coding=utf-8
'''
Created on 2015年7月1日

@author: zhaojiangang
'''
import json
from sre_compile import isstring

import freetime.util.log as ftlog
from hall.entity import hallitem, hallconf, datachangenotify
from hall.game import TGHall
from poker.entity.biz.confobj import TYConfable
from poker.entity.biz.content import TYContentRegister
from poker.entity.biz.exceptions import TYBizException
from poker.entity.biz.item.item import TYAssetUtils
import poker.entity.dao.daoconst as pkdaoconst
import poker.entity.dao.gamedata as pkgamedata
import poker.entity.dao.userchip as pkuserchip
from poker.entity.events.tyevent import EventConfigure, UserEvent
import poker.entity.events.tyeventbus as pkeventbus
import poker.util.timestamp as pktimestamp


class TYVipException(TYBizException):
    def __init__(self, ec, message):
        super(TYVipException, self).__init__(ec, message)

    def __str__(self):
        return '%s:%s' % (self.errorCode, self.message)
    
    def __unicode__(self):
        return u'%s:%s' % (self.errorCode, self.message)
    
class TYVipLevelGiftAlreadyGotException(TYVipException):
    def __init__(self, level):
        super(TYVipLevelGiftAlreadyGotException, self).__init__(-1, '已经领取过VIP%s礼包' % (level))
        self.level = level

    def __str__(self):
        return '%s:%s %s' % (self.errorCode, self.message, self.level)
    
    def __unicode__(self):
        return u'%s:%s %s' % (self.errorCode, self.message, self.level)
              
class TYVipLevelNoGiftException(TYVipException):
    def __init__(self, level):
        super(TYVipLevelNoGiftException, self).__init__(-1, 'VIP级别%s没有礼包' % (level))
        self.level = level

    def __str__(self):
        return '%s:%s %s' % (self.errorCode, self.message, self.level)
    
    def __unicode__(self):
        return u'%s:%s %s' % (self.errorCode, self.message, self.level)
    
class TYVipLevelNotFoundException(TYVipException):
    def __init__(self, level):
        super(TYVipLevelNotFoundException, self).__init__(-1, '不能识别的VIP级别%s' % (level))
        self.level = level

    def __str__(self):
        return '%s:%s %s' % (self.errorCode, self.message, self.level)
    
    def __unicode__(self):
        return u'%s:%s %s' % (self.errorCode, self.message, self.level)

class TYVipLevelNotGotException(TYVipException):
    def __init__(self, required, actually):
        super(TYVipLevelNotGotException, self).__init__(-1, '还没有达到%s' % (required))
        self.required = required
        self.actually = actually 

    def __str__(self):
        return '%s:%s %s:%s' % (self.errorCode, self.message, self.required, self.actually)
    
    def __unicode__(self):
        return u'%s:%s %s:%s' % (self.errorCode, self.message, self.required, self.actually)
    
class TYVipConfException(TYVipException):
    def __init__(self, conf, message):
        super(TYVipConfException, self).__init__(-1, message)
        self.conf = conf
    
    def __str__(self):
        return '%s:%s conf=%s' % (self.errorCode, self.message, self.conf)
    
    def __unicode__(self):
        return u'%s:%s conf=%s' % (self.errorCode, self.message, self.conf)
    
class TYAssistanceException(TYBizException):
    def __init__(self, ec, message):
        super(TYAssistanceException, self).__init__(ec, message)

    def __str__(self):
        return '%s:%s' % (self.errorCode, self.message)
    
    def __unicode__(self):
        return u'%s:%s' % (self.errorCode, self.message)
    
class TYAssistanceNotHaveException(TYAssistanceException):
    def __init__(self):
        super(TYAssistanceNotHaveException, self).__init__(-1, '对不起，您没有可用的VIP江湖救急余额呦～')
            
class TYAssistanceChipTooMuchException(TYAssistanceException):
    def __init__(self, chip, upperChipLimit):
        super(TYAssistanceChipTooMuchException, self).__init__(-1, '金币太多')
        self.chip = chip
        self.upperChipLimit = upperChipLimit
        
class TYUserVipGiftStatusData(object):
    def __init__(self):
        # key=level, value=state
        self.giftStateMap = {}
        
class TYUserVipDao(object):
    def loadVipExp(self, userId):
        '''
        加载用户的VIP经验值
        @param userId: 哪个用户
        @return: VIP经验值
        '''
        raise NotImplemented()
    
    def incrVipExp(self, userId, count):
        '''
        给用户增加count个经验值，count可以为负数
        @param userId: 哪个用户
        @param count: 数量
        @return: 变化后的值
        '''
        raise NotImplemented()
    
    def loadVipGiftStatus(self, userId):
        '''
        加载用户VIP礼包状态
        @param userId: 哪个用户
        @return: TYUserVipGiftStatusData
        '''
        raise NotImplemented()
    
    def saveVipGiftStatus(self, userId, vipGiftStatus):
        '''
        保存用户VIP礼包状态
        @param userId: 哪个用户
        @param vipGiftStatus: 用户VIP礼包状态
        '''
        raise NotImplemented()
    
class TYUserVipDaoImpl(TYUserVipDao):
    def loadVipExp(self, userId):
        '''
        加载用户的VIP经验值
        @param userId: 哪个用户
        @return: VIP经验值
        '''
        return pkgamedata.getGameAttrInt(userId, 9999, 'vip.exp')
    
    def incrVipExp(self, userId, count):
        '''
        给用户增加count个经验值，count可以为负数
        @param userId: 哪个用户
        @param count: 数量
        @return: 变化后的值
        '''
        return pkgamedata.incrGameAttr(userId, 9999, 'vip.exp', count)
    
    def loadVipGiftStatus(self, userId):
        '''
        加载用户VIP礼包状态
        @param userId: 哪个用户
        @return: TYUserVipGiftStatusData
        '''
        status = TYUserVipGiftStatusData()
        d = pkgamedata.getGameAttrJson(userId, 9999, 'vip.gift.states')
        if d:
            for level, state in d.iteritems():
                status.giftStateMap[int(level)] = state
        return status
    
    def saveVipGiftStatus(self, userId, vipGiftStatus):
        '''
        保存用户VIP礼包状态
        @param userId: 哪个用户
        @param vipGiftStatus: 用户VIP礼包状态
        '''
        jstr = json.dumps(vipGiftStatus.giftStateMap)
        pkgamedata.setGameAttr(userId, 9999, 'vip.gift.states', jstr)
  

class TYVipLevel(TYConfable):
    def __init__(self):
        self.conf = None
        # 级别，数字
        self.level = None
        # 级别名称
        self.name = None
        # 当前级别最小VIP经验值
        self.vipExp = None
        # 图片
        self.pic = None
        # 说明
        self.desc = None
        # 达到该级别后给什么奖励
        self.rewardContent = None
        # 该级别的礼包
        self.giftContent = None
        # 经验说明
        self.expDesc = None
        # 上一个级别
        self.prevVipLevel = None
        # 下一个级别的level值
        self.nextVipLevelValue = None
        # 下一个级别对象
        self.nextVipLevel = None

    def initWhenLoaded(self, vipLevelMap):
        if self.nextVipLevelValue is not None:
            nextVipLevel = vipLevelMap.get(self.nextVipLevelValue)
            if not nextVipLevel:
                raise TYVipConfException(self.conf, 'Unknown next vip level %s for %s' % (self.nextVipLevelValue, self.level))
            if nextVipLevel.prevVipLevel:
                raise TYVipConfException(self.conf, 'The next vip level %s already has prev vip level %s' % (nextVipLevel.level))
            nextVipLevel.prevVipLevel = self
            self.nextVipLevel = nextVipLevel
            
    def decodeFromDict(self, d):
        self.conf = d
        self.level = d.get('level')
        if not isinstance(self.level, int):
            raise TYVipConfException(d, 'VipLevel.level must be int')
        self.name = d.get('name')
        if not isstring(self.name) or not self.name:
            raise TYVipConfException(d, 'VipLevel.name must be valid string')
        self.vipExp = d.get('exp')
        if not isinstance(self.vipExp, int):
            raise TYVipConfException(d, 'VipLevel.vipExt must be int')
        self.pic = d.get('pic', '')
        if not isstring(self.pic):
            raise TYVipConfException(d, 'VipLevel.pic must be string')
        self.desc = d.get('desc', [])
        if not isinstance(self.desc, list):
            raise TYVipConfException(d, 'VipLevel.desc must be list')
        if self.desc:
            for subDesc in self.desc:
                if not isstring(subDesc):
                    raise TYVipConfException(d, 'VipLevel.desc.item must be string')
        rewardContent = d.get('rewardContent')
        if rewardContent:
            self.rewardContent = TYContentRegister.decodeFromDict(rewardContent)
        giftContent = d.get('giftContent')
        if giftContent:
            self.giftContent = TYContentRegister.decodeFromDict(giftContent)
        self.expDesc = d.get('expDesc', '')
        if not isstring(self.expDesc):
            raise TYVipConfException(d, 'VipLevel.expDesc must be string')
        self.nextVipLevelValue = d.get('nextLevel')
        if (self.nextVipLevelValue is not None
            and not isinstance(self.nextVipLevelValue, int)):
            raise TYVipConfException(d, 'VipLevel.nextVipLevelValue must be int')
        return self
    
class TYUserVip(object):
    def __init__(self, userId, vipExp, vipLevel):
        assert(vipExp >= vipLevel.vipExp
               and (not vipLevel.nextVipLevel
                    or vipExp < vipLevel.nextVipLevel.vipExp))
        self.userId = userId
        self.vipExp = vipExp
        self.vipLevel = vipLevel
         
    def deltaExpToNextLevel(self):
        if self.vipLevel.nextVipLevel:
            return max(0, self.vipLevel.nextVipLevel.vipExp - self.vipExp)
        return 0
     
class TYVipSystem(object):
    def getAssistanceChip(self):
        '''
        获取江湖救急每次的金币数量
        '''
        raise NotImplemented()
    
    def getAssistanceChipUpperLimit(self):
        '''
        获取江湖救急金币上限
        '''
        raise NotImplemented()
     
    def getLevelUpDesc(self):
        raise NotImplemented()
    
    def getLevelUpPayOrder(self):
        raise NotImplemented()
    
    def getGotGiftDesc(self):
        raise NotImplemented()
    
    def getGotAssistanceDesc(self):
        raise NotImplemented()
    
    def findVipLevelByLevel(self, level):
        '''
        根据级别查找vip
        @param level: 要查找的vip的级别
        @return: 找到的TYVipLevel，没找到返回None
        '''
        raise NotImplemented()
     
    def findVipLevelByVipExp(self, vipExp):
        '''
        根据vip经验值查找对应的vip级别
        @param vipExp: vip经验值
        @return: 找到的对应的TYVip，没找到返回None 
        '''
        raise NotImplemented()
     
    def getAllVipLevel(self):
        '''
        获取所有的vip
        @return: list<TYVipLevel>
        '''
        raise NotImplemented()
 
   
class TYUserVipExpChangedEvent(UserEvent):
    def __init__(self, gameId, userId, userVip, oldVipExp):
        super(TYUserVipExpChangedEvent, self).__init__(userId, gameId)
        self.userVip = userVip
        self.oldVipExp = oldVipExp
        self.userVip = userVip
         
class TYUserVipLevelUpEvent(UserEvent):
    def __init__(self, gameId, userId, oldVipLevel, userVip, contentList, eventId, intEventParam):
        super(TYUserVipLevelUpEvent, self).__init__(userId, gameId)
        self.oldVipLevel = oldVipLevel
        self.userVip = userVip
        self.contentList = contentList
        self.eventId = eventId
        self.intEventParam = intEventParam
 
class TYVipGiftState(object):
    STATE_UNGOT = 0
    STATE_GOT = 1

    def __init__(self, vipLevel, state):
        self.vipLevel = vipLevel
        self.state = state

    @property
    def level(self):
        return self.vipLevel.level
    
class TYUserVipGiftStatus(object):
    def __init__(self):
        # key=level, value=TYVipGiftState
        self.giftStateMap = {}
      
    def getGiftStateByLevel(self, level):
        return self.giftStateMap.get(level)
    
    def setGiftState(self, level, giftState):
        assert(isinstance(giftState, TYVipGiftState))
        self.giftStateMap[level] = giftState
         
class TYUserVipGotGiftResult(object):
    def __init__(self, userVip, vipGiftState, giftItemList):
        # vip
        self.userVip = userVip
        # 
        self.vipGiftState = vipGiftState
        # list<(TYAssetKind, count, final)>
        self.giftItemList = giftItemList
         
class TYUserVipGotGiftEvent(UserEvent):
    def __init__(self, gameId, userId, gotVipGiftResult):
        super(TYUserVipGotGiftEvent, self).__init__(userId, gameId)
        self.gotVipGiftResult = gotVipGiftResult
         
class TYUserVipSystem(object):
    def getUserVip(self, userId):
        '''
        获取用户vip
        @param userId: 要获取的用户ID 
        @return: TYUserVip
        '''
        raise NotImplemented()

    def getVipInfo(self, userId):
        '''
        获取用户vip
        @param userId: 要获取的用户ID 
        @return: TYUserVip的dict格式
        '''
        raise NotImplemented()

    def addUserVipExp(self, gameId, userId, toAddExp, eventId, intEventParam):
        '''
        增加vip经验值
        @param gameId: 在那个gameId中增加的经验值，用于统计 
        @param toAddExp: 要增加的经验值
        @param eventId: 导致经验值增加的事件ID
        @param intEventParam: event参数
        @return: TYUserVip
        '''
        raise NotImplemented()
     
    def gainUserVipGift(self, gameId, userId, level):
        '''
        领取level级别vip的礼品
        @param userId: 要领取礼品的用户ID
        @param level: 要领取的礼品的vip级别
        @return: userVip, list<TYVipGiftState>, TYUserVipGotGiftResult
        '''
        raise NotImplemented()
     
    def getUserVipGiftStates(self, gameId, userId):
        '''
        获取vip各个级别的礼包状态
        @param userId: 要获取状态的用户ID
        @return: TYUserVip, list<TYVipGiftState>
        '''
        raise NotImplemented()

    def getAssistanceCount(self, gameId, userId):
        '''
        获取江湖救急次数
        '''
        raise NotImplemented()
    
    def gainAssistance(self, gameId, userId):
        '''
        领取江湖救急
        @param gameId: gameId
        @param userId: userId 
        @return: consumeCount, finalCount, sendChip
        '''
        raise NotImplemented()
    
class TYVipSystemImpl(TYVipSystem):
    def __init__(self):
        self._vipLevelMap = {}
        self._vipLevelList = []
        self._assistanceChip = 0
        self._assistanceChipUpperLimit = 0
        self._levelUpDesc = ''
        self._levelUpErrorGameIds = []
        self._gotGiftDesc = ''
        self._gotAssistanceDesc = ''
        self._levelUpShelves = None
        self.levelUpPayOrder = None
        
    def reloadConf(self, conf):
        vipLevelMap = {}
        assistanceChip = conf.get('assistanceChip')
        if not isinstance(assistanceChip, int) or assistanceChip <= 0:
            raise TYVipConfException(conf, 'assistanceChip must be int > 0')
        assistanceChipUpperLimit = conf.get('assistanceChipUpperLimit')
        if not isinstance(assistanceChipUpperLimit, int) or assistanceChipUpperLimit < 0:
            raise TYVipConfException(conf, 'assistanceChip must be int >= 0')
        levelUpDesc = conf.get('levelUpDesc', '')
        if not isstring(levelUpDesc):
            raise TYVipConfException(conf, 'levelUpDesc must be string')
        levelUpErrorGameIds = conf.get('levelUpErrorGameIds', [])
        if not isinstance(levelUpErrorGameIds, list):
            raise TYVipConfException(conf, 'levelUpErrorGameIds must be list')
        levelUpPayOrder = conf.get('levelUpPayOrder')
        if not isinstance(levelUpPayOrder, dict):
            raise TYVipConfException(conf, 'levelUpPayOrder must be dict')
        gotGiftDesc = conf.get('gotGiftDesc', '')
        if not isstring(gotGiftDesc):
            raise TYVipConfException(conf, 'gotGiftDesc must be string')
        gotAssistanceDesc = conf.get('gotAssistanceDesc', '')
        if not isstring(gotAssistanceDesc):
            raise TYVipConfException(conf, 'gotAssistanceDesc must be string')
        levelsConf = conf.get('levels')
        if not isinstance(levelsConf, list) or not levelsConf:
            raise TYVipConfException(conf, 'vip levels must be list')
        for levelConf in levelsConf:
            vipLevel = TYVipLevel()
            vipLevel.decodeFromDict(levelConf)
            if vipLevel.level in vipLevelMap:
                raise TYVipConfException(conf, 'duplicate vip level' % (vipLevel.level))
            vipLevelMap[vipLevel.level] = vipLevel
        
        for vipLevel in vipLevelMap.values():
            vipLevel.initWhenLoaded(vipLevelMap)

        vipLevelList = sorted(vipLevelMap.values(), cmp=lambda x,y:cmp(x.vipExp, y.vipExp))
        # 判读是否循环配置
        for vipLevel in vipLevelList:
            nextVipLevel = vipLevel.nextVipLevel
            while (nextVipLevel):
                if nextVipLevel == vipLevel:
                    raise TYVipConfException(conf, 'Loop vip level %s' % (vipLevel.level))
                nextVipLevel = nextVipLevel.nextVipLevel
                
        self._vipLevelMap = vipLevelMap
        self._vipLevelList = vipLevelList
        self._assistanceChip = assistanceChip
        self._assistanceChipUpperLimit = assistanceChipUpperLimit
        self._levelUpDesc = levelUpDesc
        self._levelUpErrorGameIds = levelUpErrorGameIds
        self._gotGiftDesc = gotGiftDesc
        self._gotAssistanceDesc = gotAssistanceDesc
        self._levelUpPayOrder = levelUpPayOrder
        ftlog.debug('TYVipSystemImpl.reloadConf successed allLevels=', self._vipLevelMap.keys(), 'list=', [l.level for l in vipLevelList])
         
    def getAssistanceChip(self):
        '''
        获取江湖救急每次的金币数量
        '''
        return self._assistanceChip
    
    def getAssistanceChipUpperLimit(self):
        '''
        获取江湖救急金币上限
        '''
        return self._assistanceChipUpperLimit
    
    def getLevelUpDesc(self):
        return self._levelUpDesc
    
    def getLevelUpErrorGameIds(self):
        return self._levelUpErrorGameIds
    
    def getLevelUpPayOrder(self):
        return self._levelUpPayOrder
    
    def getGotGiftDesc(self):
        return self._gotGiftDesc
    
    def getGotAssistanceDesc(self):
        return self._gotAssistanceDesc
    
    def findVipLevelByLevel(self, level):
        '''
        根据级别查找vip
        @param level: 要查找的vip的级别
        @return: 找到的TYVip，没找到返回None
        '''
        return self._vipLevelMap.get(level)
     
    def findVipLevelByVipExp(self, vipExp):
        '''
        根据vip经验值查找对应的vip级别
        @param vipExp: vip经验值
        @return: 找到的对应的TYVip，没找到返回None 
        '''
        for vip in self._vipLevelList[::-1]:
            if vipExp >= vip.vipExp:
                return vip
        return self._vipLevelList[0]
     
    def getAllVipLevel(self):
        '''
        获取所有的vip
        @return: list<TYVipLevel>
        '''
        return self._vipLevelList
        
class TYUserVipSystemImpl(TYUserVipSystem):
    def __init__(self, vipSystem, vipDao):
        self._vipSystem = vipSystem
        self._vipDao = vipDao
         
    def getUserVip(self, userId):
        '''
        获取用户vip
        @param userId: 要获取的用户ID 
        @return: TYUserVip
        '''
        vipExp = self._vipDao.loadVipExp(userId)
        vipLevel = self._vipSystem.findVipLevelByVipExp(vipExp)
        return TYUserVip(userId, vipExp, vipLevel)


    def getVipInfo(self, userId):
        userVip = self.getUserVip(userId)
        nextVipLevel = userVip.vipLevel.nextVipLevel if userVip.vipLevel.nextVipLevel else userVip.vipLevel
        return {
            'level':userVip.vipLevel.level,
            'name':userVip.vipLevel.name,
            'exp':userVip.vipExp,
            'expCurrent':userVip.vipLevel.vipExp,
            'expNext':nextVipLevel.vipExp,
        }
    
    def addUserVipExp(self, gameId, userId, toAddExp, eventId, intEventParam):
        '''
        增加vip经验值
        @param gameId: 在那个gameId中增加的经验值，用于统计 
        @param toAddExp: 要增加的经验值
        @param eventId: 导致经验值增加的事件ID
        @param intEventParam: eventId相关参数
        @return: TYUserVip
        '''
        assert(toAddExp >= 0)
        vipExp = self._vipDao.incrVipExp(userId, toAddExp)
        oldVipExp = vipExp - toAddExp
        oldVipLevel = self._vipSystem.findVipLevelByVipExp(oldVipExp)
        newVipLevel = self._vipSystem.findVipLevelByVipExp(vipExp)
        
        ftlog.info('TYUserVipSystemImpl.addUserVipExp gameId=', gameId, 'userId=', userId,
                   'oldExp=', oldVipExp, 'newExp=', vipExp,
                   'oldLevel=', oldVipLevel.level, 'newLevel=', newVipLevel.level)
        
        userVip = TYUserVip(userId, vipExp, newVipLevel)
        if oldVipLevel.level != newVipLevel.level:
            nextVipLevel = oldVipLevel.nextVipLevel
            assetList = []
            while (nextVipLevel and nextVipLevel.level <= newVipLevel.level):
                subContentList = self._sendRewardContent(gameId, userVip, nextVipLevel)
                if subContentList:
                    assetList.extend(subContentList)
                nextVipLevel = nextVipLevel.nextVipLevel
            changeDataNames = TYAssetUtils.getChangeDataNames(assetList)
            changeDataNames.add('vip')
            changeDataNames.add('decoration')
            datachangenotify.sendDataChangeNotify(gameId, userId, changeDataNames)
            TGHall.getEventBus().publishEvent(TYUserVipLevelUpEvent(gameId, userId, oldVipLevel,
                                                                    userVip, assetList,
                                                                    eventId, intEventParam))
        else:
            datachangenotify.sendDataChangeNotify(gameId, userId, 'vip')
            TGHall.getEventBus().publishEvent(TYUserVipExpChangedEvent(gameId, userId, userVip, oldVipExp))
        return userVip

    def gainUserVipGift(self, gameId, userId, level):
        '''
        领取level级别vip的礼品
        @param userId: 要领取礼品的用户ID
        @param level: 要领取的礼品的vip级别
        @return: userVip, list<TYVipGiftState>, TYUserVipGotGiftResult
        '''
        userVip = self.getUserVip(userId)
        if level > userVip.vipLevel.level:
            raise TYVipLevelNotGotException(level, userVip.vipLevel.level)
         
        vipLevel = self._vipSystem.findVipLevelByLevel(level)
        if not vipLevel:
            raise TYVipLevelNotFoundException(level)

        if not vipLevel.giftContent:
            raise TYVipLevelNoGiftException(level)
        
        vipGiftStatus = self._loadUserVipGiftStatus(userId)
        giftState = vipGiftStatus.getGiftStateByLevel(level)
        if giftState and giftState.state == TYVipGiftState.STATE_GOT:
            raise TYVipLevelGiftAlreadyGotException(level)
        
        giftState = TYVipGiftState(vipLevel, TYVipGiftState.STATE_GOT)
        vipGiftStatus.setGiftState(giftState.level, giftState)
        self._saveVipGiftStates(userId, vipGiftStatus)
        
        # 发奖
        assetList = self._sendGiftContent(gameId, userVip, vipLevel)
        datachangenotify.sendDataChangeNotify(gameId, userId, TYAssetUtils.getChangeDataNames(assetList))
        gotGiftResult = TYUserVipGotGiftResult(userVip, giftState, assetList)
        TGHall.getEventBus().publishEvent(TYUserVipGotGiftEvent(gameId, userId, gotGiftResult))
        return userVip, self._fillAndToList(userVip, vipGiftStatus), gotGiftResult
     
    def getUserVipGiftStates(self, gameId, userId):
        '''
        获取vip各个级别的礼包状态
        @param userId: 要获取状态的用户ID
        @return: userVip, list<TYVipGiftState>
        '''
        try:
            vipGiftStatus = self._loadUserVipGiftStatus(userId)
        except:
            vipGiftStatus = TYUserVipGiftStatus()
        userVip = self.getUserVip(userId)
        # 组织获得的所有vip级别的gift状态
        giftStates = self._fillAndToList(userVip, vipGiftStatus)
        return userVip, giftStates
     
    def getAssistanceCount(self, gameId, userId):
        '''
        获取江湖救急次数
        '''
        userAssets = hallitem.itemSystem.loadUserAssets(userId)
        return userAssets.balance(gameId, 'game:assistance', pktimestamp.getCurrentTimestamp())
    
    def gainAssistance(self, gameId, userId):
        '''
        领取江湖救急
        @param gameId: gameId
        @param userId: userId 
        @return: consumeCount, finalCount, sendChip
        '''
        # 检查金币数量是否符合领取江湖救急的条件
        userAllChip = pkuserchip.getUserChipAll(userId)
        assistanceChipUpperLimit = self._vipSystem.getAssistanceChipUpperLimit()
        if userAllChip >= assistanceChipUpperLimit:
            raise TYAssistanceChipTooMuchException(userAllChip, assistanceChipUpperLimit)
        
        timestamp = pktimestamp.getCurrentTimestamp()
        # 发放江湖救急金
        userAssets = hallitem.itemSystem.loadUserAssets(userId)
        _assetKind, consumeCount, final = userAssets.consumeAsset(gameId, 'game:assistance', 1,
                                                                  timestamp, 'VIP_GOT_ASSISTANCE', 0)
        assistanceChip = self._vipSystem.getAssistanceChip()
        if consumeCount >= 1 and assistanceChip > 0:
            pkuserchip.incrChip(userId, gameId, assistanceChip,
                                pkdaoconst.CHIP_NOT_ENOUGH_OP_MODE_NONE,
                                'VIP_GOT_ASSISTANCE', 0, 0)
        ftlog.debug('TYUserVipSystemImpl.gainAssistance gameId=', gameId,
                   'userId=', userId,
                   'consumeCount=', consumeCount,
                   'assistanceChip=', assistanceChip)
        return consumeCount, final, assistanceChip
    
    def _fillAndToList(self, userVip, vipGiftStatus):
        giftStates = []
        vipLevel = userVip.vipLevel
        while (vipLevel):
            giftState = vipGiftStatus.getGiftStateByLevel(vipLevel.level)
            if giftState is None:
                giftState = TYVipGiftState(vipLevel, TYVipGiftState.STATE_UNGOT)
            giftStates.append(giftState)
            vipLevel = vipLevel.prevVipLevel
        giftStates.reverse()
        return giftStates
     
    def _loadUserVipGiftStatus(self, userId):
        vipGiftStatus = TYUserVipGiftStatus()
        vipGiftStatusData = self._vipDao.loadVipGiftStatus(userId)
        if ftlog.is_debug():
            ftlog.debug('TYUserVipSystemImpl._loadUserVipGiftStatus userId=', userId,
                        'giftStateMap=', vipGiftStatusData.giftStateMap)
        for level, state in vipGiftStatusData.giftStateMap.iteritems():
            vipLevel = self._vipSystem.findVipLevelByLevel(level)
            if vipLevel:
                vipGiftStatus.giftStateMap[level] = TYVipGiftState(vipLevel, state)
            else:
                ftlog.error('TYUserVipSystemImpl._loadUserVipGiftStatus userId=', userId,
                                      'level=', level,
                                      'err=', 'UnknownLevel')
        return vipGiftStatus
         
    def _saveVipGiftStates(self, userId, vipGiftStatus):
        vipGiftStatusData = TYUserVipGiftStatusData()
        for giftState in vipGiftStatus.giftStateMap.values():
            vipGiftStatusData.giftStateMap[giftState.level] = giftState.state
        self._vipDao.saveVipGiftStatus(userId, vipGiftStatusData)
        
    def _sendRewardContent(self, gameId, userVip, vipLevel):
        if vipLevel.rewardContent:
            ftlog.debug('TYUserVipSystemImpl._sendRewardContent gameId=', gameId,
                       'userId=', userVip.userId,
                       'level=', vipLevel.level,
                       'rewardContent=', vipLevel.rewardContent.desc)
            timestamp = pktimestamp.getCurrentTimestamp()
            userAssets = hallitem.itemSystem.loadUserAssets(userVip.userId)
            return userAssets.sendContent(gameId, vipLevel.rewardContent, 1, True,
                                          timestamp, 'VIP_REWARD', vipLevel.level)
        return []
                 
    def _sendGiftContent(self, gameId, userVip, vipLevel):
        if vipLevel.giftContent:
            ftlog.debug('TYUserVipSystemImpl._sendGiftContent gameId=', gameId,
                       'userId=', userVip.userId,
                       'level=', vipLevel.level,
                       'giftContent=', vipLevel.giftContent.desc)
            timestamp = pktimestamp.getCurrentTimestamp()
            userAssets = hallitem.itemSystem.loadUserAssets(userVip.userId)
            return userAssets.sendContent(gameId, vipLevel.giftContent, 1, True,
                                          timestamp, 'VIP_GIFT_REWARD', vipLevel.level)
        return []

vipSystem = TYVipSystem()
userVipSystem = TYUserVipSystem()
_inited = False

def _reloadConf():
    conf = hallconf.getVipConf()
    vipSystem.reloadConf(conf)
    
def _onConfChanged(event):
    if _inited and event.isChanged('game:9999:vip:0'):
        ftlog.debug('hallvip._onConfChanged')
        _reloadConf()
        
def _initialize():
    ftlog.debug('VIP initialize begin')
    global vipSystem
    global userVipSystem
    global _inited
    if not _inited:
        _inited = True
        vipSystem = TYVipSystemImpl()
        userVipSystem = TYUserVipSystemImpl(vipSystem, TYUserVipDaoImpl())
        _reloadConf()
        pkeventbus.globalEventBus.subscribe(EventConfigure, _onConfChanged)
    ftlog.debug('VIP initialize end')


