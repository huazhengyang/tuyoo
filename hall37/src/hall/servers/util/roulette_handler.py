# -*- coding=utf-8
'''
Created on 2016年4月20日

@author: wuyongsheng
@note: roulette——handler
'''
from hall.entity import hallroulette
from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from poker.protocol import router, runcmd
from hall.servers.common.base_checker import BaseMsgPackChecker
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod


class rouletteHelper(object):

    @classmethod
    def encodeRoulette(cls, item):
        ret = {
            'rouletteId': item.rouletteId,
            'picUrl': item.picUrl
        }
        return ret

    @classmethod
    def encodeRouletteList(cls, itemList):
        ret = []
        for d in itemList:
            ret.append(cls.encodeRoulette(d))
        return ret

    @classmethod
    def encodeRouletteTemplate(cls, clientId, gameId, userId, templateName):
        return cls.encodeRouletteList(templateName.items)

    @classmethod
    def makeRouletteQueryResponse(cls, gameId, userId, clientId, action, rouletteTemplate):
        mo = MsgPack()
        mo.setCmd('game')
        mo.setResult('action', action)
        mo.setResult('gameId', gameId)
        mo.setResult('userId', userId)
        mo.setResult('result', rouletteTemplate)
        return mo

    @classmethod
    def getResponseMsg(cls, result, gameId, userId, action):
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


@markCmdActionHandler
class rouletteHandler(BaseMsgPackChecker):

    def __init__(self):
        super(rouletteHandler, self).__init__()

    @markCmdActionMethod(cmd='game', action='roulette_update', clientIdVer=0)
    def doRouletteUpdate(self, userId, gameId, clientId):
        '''
        客户端点击事件
        给客户端判断是否是金盘还是银盘
        依据：抽奖卡的个数
        '''
        result = hallroulette.doUpdate(userId, gameId, clientId)
        mo = rouletteHelper.makeRouletteQueryResponse(gameId, userId, clientId, 'roulette_update', result)
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd='game', action='roulette_gold', clientIdVer=0)
    def doRouletteGold(self, userId, gameId, clientId):
        '''
        客户端点击事件
        金盘抽奖，必须消耗钻石，如果没有钻石，命令客户端去商城
        
        修改：
            给用户添加小兵
        '''
        msg = runcmd.getMsgPack()
        number = msg.getParam('number')
        ftlog.debug('doRouletteGold.userId=', userId,
                   'gameId=', gameId,
                   'clientId=', clientId,
                   'number=', number,
                   'msg=', msg)
        result = hallroulette.doGoldLottery(userId, gameId, clientId, number)
        mo = rouletteHelper.makeRouletteQueryResponse(gameId, userId, clientId, 'roulette_gold', result)
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd='game', action='roulette_silver', clientIdVer=0)
    def doRouletteSilver(self, userId, gameId, clientId):
        '''
        客户端点击事件
        银盘抽奖，必须消耗道具（抽奖卡），如果没有道具，命令客户端导向金盘
        '''
        result = hallroulette.doSilverLottery(userId, gameId, clientId)
        if result:
            mo = rouletteHelper.makeRouletteQueryResponse(gameId, userId, clientId, 'roulette_silver', result)
            router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd='game', action='roulette_beforeReward', clientIdVer=0)
    def doRouletteBeforeReward(self, userId, gameId, clientId):
        '''
        客户端点击事件
        获取整体金盘小兵的历史中奖信息
        '''
        result = hallroulette.doGetBeforeReward(userId, gameId, clientId)
        mo = rouletteHelper.makeRouletteQueryResponse(gameId, userId, clientId, 'roulette_beforeReward', result)
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd='game', action='roulette_soldierInfo', clientIdVer=0)
    def doRouletteGetSoldierInfo(self, userId, gameId, clientId):
        '''
        客户端定时刷新事件（4秒一次）
        发送本期小兵信息
        给这个用户发小兵（TODO 移动到用户金盘抽奖事件中）
        触发发奖核算（TODO 移动到系统定时器检查中）
        修改
            只下发小兵信息，不做其它操作
        '''
        result = hallroulette.doGetSoldierInfo(userId, gameId, clientId)
        if ftlog.is_debug():
            ftlog.debug('doRouletteGetSoldierInfo.userId=', userId,
                   'gameId=', gameId,
                   'clientId=', clientId,
                   'result=', result)
            
        mo = rouletteHelper.makeRouletteQueryResponse(gameId, userId, clientId, 'roulette_soldierInfo', result)
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd='game', action='roulette_goldUpdate', clientIdVer=0)
    def doGetRoulletGoldUpdate(self, userId, gameId, clientId):
        '''
        客户端自动获取（金银转换时1次）
        获取金盘配置信息
        '''
        result = hallroulette.doGetGoldUpdate(userId, gameId, clientId)
        mo = rouletteHelper.makeRouletteQueryResponse(gameId, userId, clientId, 'roulette_goldUpdate', result)
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd='game', action='issue_user', clientIdVer=0)
    def doGetSoldierForUser(self, userId, gameId, clientId):
        '''
        客户端点击事件
        获取用户的历史小兵信息
        '''
        msg = runcmd.getMsgPack()
        issue = msg.getParam('issue')
        if ftlog.is_debug():
            ftlog.debug('doGetSoldierForUser.userId:', userId
                        , ' gameId:', gameId
                        , ' clientId:', clientId
                        , ' issue:', issue)
            
        result, _, _ = hallroulette.doGetSoldierIdForUser(userId, gameId, clientId, issue)
        mo = rouletteHelper.makeRouletteQueryResponse(gameId, userId, clientId, 'issue_user', result)
        router.sendToUser(mo, userId)
    @markCmdActionMethod(cmd='game', action='roulette_led', clientIdVer=0, scope='game')
    def doRouletteRecordLed(self, gameId, userId, clientId):
        mo = MsgPack()
        mo.setCmd('game')
        mo.setResult('action', 'roulette_led')
        mo.setResult('gameId', gameId)
        mo.setResult('userId', userId)
        exLedList = []
        try:
            from poker.entity.dao import daobase
            doRouletteRecordKey = "roulette:recordLed"
            LedList = daobase.executeMixCmd('LRANGE', doRouletteRecordKey, 0, -1)
            if len(LedList) > 0:
                import json
                bigWinColor = "F7C532"
                bigWinDefaultColor = "FFFFFF"
                for exled in LedList:
                    exled = json.loads(exled)
                    content = [
                        [bigWinColor, exled['name']],
                        [bigWinDefaultColor, u'抽中了'],
                        [bigWinColor, exled['itemDesc']],
                        [bigWinDefaultColor, u'!']
                    ]
                    data = {'content': content}
                    exLedList.append(data)
            mo.setResult('rouletteLedList', exLedList)
        except:
            mo.setResult('rouletteLedList', [])
        if ftlog.is_debug():
            ftlog.debug("doRouletteRecordLed:", exLedList)
        router.sendToUser(mo, userId)
