# -*- coding: utf-8 -*-
'''
Created on 2015年5月20日

@author: zqh
'''



from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from hall.entity import hallvip, hallitem, datachangenotify, hallstore
from hall.entity.hallvip import TYVipGiftState, TYUserVipLevelUpEvent, \
    TYAssistanceChipTooMuchException
from hall.entity.todotask import TodoTaskHelper, \
    TodoTaskVipGotGift, TodoTaskGoldRain, TodoTaskPopTip, TodoTaskVipLevelUp, \
    TodoTaskPayOrder, TodoTaskShowInfo
from hall.game import TGHall
from hall.servers.common.base_checker import BaseMsgPackChecker
from poker.entity.biz.exceptions import TYBizException
from poker.entity.biz.item.item import TYAssetUtils
from poker.entity.dao import sessiondata
from poker.protocol import runcmd, router
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod
from poker.util import strutil


class VipHelper(object):
    @classmethod
    def buildVipInfo(cls, userVip):
        nextVipLevel = userVip.vipLevel.nextVipLevel if userVip.vipLevel.nextVipLevel else userVip.vipLevel
        return {
            'level':userVip.vipLevel.level,
            'name':userVip.vipLevel.name,
            'exp':userVip.vipExp,
            'expCurrent':userVip.vipLevel.vipExp,
            'expNext':nextVipLevel.vipExp,
        }
        
    @classmethod
    def buildExpDesc(cls, userVip):
        expDesc = userVip.vipLevel.expDesc
        if not expDesc:
            return expDesc
        nextVipLevel = userVip.vipLevel.nextVipLevel or userVip.vipLevel
        return strutil.replaceParams(expDesc, {
                                        'deltaExp':str(userVip.deltaExpToNextLevel()),
                                        'deltaRmb':str(max(1, int(userVip.deltaExpToNextLevel() / 10))),
                                        'nextVipLevel':str(nextVipLevel.level),
                                        'nextVipLevelName':str(nextVipLevel.name),
                                        'curVipLevel':str(userVip.vipLevel.level)
                                    })
    
    @classmethod
    def buildUpLevelTodoTasks(cls, gameId, userVip, clientId):
        deltaExp = userVip.deltaExpToNextLevel()
        if deltaExp > 0:
            payOrder = strutil.cloneData(hallvip.vipSystem.getLevelUpPayOrder())
            payOrder['priceDiamond'] = {'count':deltaExp, 'minCount':0, 'maxCount':-1}
            product, _ = hallstore.findProductByPayOrder(gameId, userVip.userId, clientId, payOrder)
            if product:
                return TodoTaskHelper.encodeTodoTasks(TodoTaskPayOrder(product))
        return []
    
    @classmethod
    def buildGiftInfo(cls, userVip, vipGiftState):
        if vipGiftState.vipLevel.giftContent and vipGiftState.state == TYVipGiftState.STATE_UNGOT:
            isAvailable = userVip.vipLevel.level >= vipGiftState.vipLevel.level
            return {'isAvailable':isAvailable}
        return None
    
    @classmethod
    def buildVipLevelStateInfo(cls, userVip, vipGiftState):
        levelStateInfo = {
            'name':vipGiftState.vipLevel.name,
            'level':vipGiftState.vipLevel.level,
            'exp':vipGiftState.vipLevel.vipExp,
            'desc':vipGiftState.vipLevel.desc,
        }
        giftInfo = cls.buildGiftInfo(userVip, vipGiftState)
        if giftInfo:
            levelStateInfo['giftInfo'] = giftInfo
        return levelStateInfo
    
    @classmethod
    def buildGotGiftDesc(self, gotVipGiftResult):
        desc = hallvip.vipSystem.getGotGiftDesc()
        if desc:
            contents = TYAssetUtils.buildContentsString(gotVipGiftResult.giftItemList)
            desc = strutil.replaceParams(desc, {'rewardContent':contents})
        return desc
    
    @classmethod
    def buildGotAssistanceDesc(self, finalCount, sendChip):
        desc = hallvip.vipSystem.getGotAssistanceDesc() or ''
        if desc:
            assetKind = hallitem.itemSystem.findAssetKind(hallitem.ASSET_CHIP_KIND_ID)
            return strutil.replaceParams(desc, {'rewardContent':'%s%s' % (sendChip, assetKind.displayName)})
        return desc
    
    @classmethod
    def makeVipInfoResponse(cls, gameId, userVip, vipGiftStates, clientId=None):
        expDesc = cls.buildExpDesc(userVip)
        clientId = clientId or sessiondata.getClientId(userVip.userId)
        mo = MsgPack()
        mo.setCmd('newvip')
        mo.setResult('action', 'vipInfo')
        mo.setResult('gameId', gameId)
        mo.setResult('userId', userVip.userId)
        mo.setResult('vipLevel', userVip.vipLevel.level)
        mo.setResult('vipExpDesc', expDesc)
        mo.setResult('tasks', cls.buildUpLevelTodoTasks(gameId, userVip, clientId))
        if len(vipGiftStates) > 0 and vipGiftStates[0].vipLevel.level == 0:
            del vipGiftStates[0]
        if userVip.vipLevel.nextVipLevel:
            vipGiftStates.append(TYVipGiftState(userVip.vipLevel.nextVipLevel, TYVipGiftState.STATE_UNGOT))
            if userVip.vipLevel.level == 0 and userVip.vipLevel.nextVipLevel.nextVipLevel:
                vipGiftStates.append(TYVipGiftState(userVip.vipLevel.nextVipLevel.nextVipLevel, TYVipGiftState.STATE_UNGOT))
        vipInfoList = []
        for vipGiftState in vipGiftStates:
            vipInfoList.append(cls.buildVipLevelStateInfo(userVip, vipGiftState))
        mo.setResult('vipInfoList', vipInfoList)
        return mo

@markCmdActionHandler
class VipTcpHandler(BaseMsgPackChecker):
    def __init__(self):
        super(VipTcpHandler, self).__init__()
        TGHall.getEventBus().subscribe(TYUserVipLevelUpEvent, self.onUserVipLevelUp)
        
    def _check_param_level(self, msg, key, params):
        level = msg.getParam(key, msg.getParam('level'))
        if not isinstance(level, int):
            return 'ERROR of level !', None
        return None, level
            
    @classmethod
    def sendErrorResponse(cls, userId, cmd, errorCode, errorInfo):
        mo = MsgPack()
        mo.setCmd(cmd)
        mo.setError(errorCode, errorInfo)
        router.sendToUser(mo, userId)
        return mo
    
    @classmethod
    def _doNewVipInfo(self, gameId, userId):
        userVip, vipGiftStates = hallvip.userVipSystem.getUserVipGiftStates(gameId, userId)
        mo = VipHelper.makeVipInfoResponse(gameId, userVip, vipGiftStates)
        router.sendToUser(mo, userId)
        return mo
    
    @markCmdActionMethod(cmd='newvip', action="vipInfo", clientIdVer=0)
    def doNewVipInfo(self, gameId, userId):
        self._doNewVipInfo(gameId, userId)
        
    @classmethod
    def _doNewVipGift(cls, gameId, userId, level):
        try:
            userVip, _giftStates, gotVipGiftResult = hallvip.userVipSystem.gainUserVipGift(gameId, userId, level)
            ftlog.debug('VipTcpHandler._doNewVipGift userId=', userId,
                       'gameId=', gameId,
                       'giftVipLevel=', gotVipGiftResult.vipGiftState.vipLevel.level)
            giftInfo = VipHelper.buildGiftInfo(userVip, gotVipGiftResult.vipGiftState)
            getGiftTodoTask = TodoTaskVipGotGift(gotVipGiftResult.vipGiftState.vipLevel.level,
                                                 gotVipGiftResult.vipGiftState.vipLevel.vipExp,
                                                 gotVipGiftResult.vipGiftState.vipLevel.name,
                                                 gotVipGiftResult.vipGiftState.vipLevel.desc,
                                                 giftInfo)
            
            todotasks = [getGiftTodoTask]
            needGoldRain = TYAssetUtils.getAssetCount(gotVipGiftResult.giftItemList, hallitem.ASSET_CHIP_KIND_ID) > 0
            if needGoldRain:
                todotasks.append(TodoTaskGoldRain(VipHelper.buildGotGiftDesc(gotVipGiftResult)))
            else:
                todotasks.append(TodoTaskPopTip(VipHelper.buildGotGiftDesc(gotVipGiftResult)))
            
            mo = TodoTaskHelper.sendTodoTask(gameId, userId, todotasks)
            # 通知客户端变化
            if gotVipGiftResult.giftItemList:
                datachangenotify.sendDataChangeNotify(gameId, userId, TYAssetUtils.getChangeDataNames(gotVipGiftResult.giftItemList))
            return mo
        except TYBizException, e:
            return cls.sendErrorResponse(userId, 'newvip', e.errorCode, e.message)
    
    @markCmdActionMethod(cmd='newvip', action="vipGift", clientIdVer=0)
    def doNewVipGift(self, gameId, userId, level):
        self._doNewVipGift(gameId, userId, level)
    
    @markCmdActionMethod(cmd='assistance', action="get", clientIdVer=0)
    def doAssistanceGet(self, gameId, userId):
        try:
            _consumeCount, finalCount, sendChip = hallvip.userVipSystem.gainAssistance(gameId, userId)
            if sendChip > 0:
                datachangenotify.sendDataChangeNotify(gameId, userId, 'udata')
            todotask = TodoTaskGoldRain(VipHelper.buildGotAssistanceDesc(finalCount, sendChip))
            TodoTaskHelper.sendTodoTask(gameId, userId, todotask)
        except TYAssistanceChipTooMuchException, e:
            ftlog.warn('ERROR, doAssistanceGet', gameId, userId, e.chip, e.upperChipLimit, e.errorCode, e.message)
        
    @markCmdActionMethod(cmd='vip', action="info", clientIdVer=0)
    def doVipInfo(self):
        msg = runcmd.getMsgPack()
        ftlog.error('NotImplementedError, doVipInfo, msg=', msg)
        return runcmd.newOkMsgPack(code=1)

    @markCmdActionMethod(cmd='vip', action="gift", clientIdVer=0)
    def doVipGift(self):
        msg = runcmd.getMsgPack()
        ftlog.debug('msg=', msg)
        return runcmd.newOkMsgPack(code=1)
    
    def buildVipLevelUpDesc(self, userId, oldVipLevel, userVip):
        vipLevelUpDesc = hallvip.vipSystem.getLevelUpDesc()
        return strutil.replaceParams(vipLevelUpDesc, {
                                        'oldLevel':str(oldVipLevel.level),
                                        'curLevel':str(userVip.vipLevel.level)
                                    })
    
    def onUserVipLevelUp(self, event):
        if ftlog.is_debug():
            ftlog.debug('VipHandlerImpl.onUserVipLevelUp userId=', event.userId,
                        'gameId=', event.gameId,
                        'oldLevel=', event.oldVipLevel.level,
                        'newLevel=', event.userVip.vipLevel.level)
        todotask = TodoTaskVipLevelUp(VipHelper.buildVipInfo(event.userVip),
                                      self.buildVipLevelUpDesc(event.userId, event.oldVipLevel, event.userVip))
        userGameId = strutil.getGameIdFromHallClientId(sessiondata.getClientId(event.userId))
        if userGameId in hallvip.vipSystem.getLevelUpErrorGameIds():
            msg = "恭喜您升级为VIP %s！" % event.userVip.vipLevel.level
            todotask = TodoTaskShowInfo(msg, True)
        TodoTaskHelper.sendTodoTask(event.gameId, event.userId, todotask)
        
        
