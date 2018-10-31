# -*- coding:utf-8 -*-
'''
Created on 2018年8月11日

@author: wangyonghui
'''
from sre_compile import isstring

import freetime.util.log as ftlog
from dizhu.entity.dizhuconf import DIZHU_GAMEID
from dizhu.entity.treasure_chest.treasure_chest import TreasureChestHelper
from freetime.entity.msg import MsgPack
from hall.servers.common.base_checker import BaseMsgPackChecker
from poker.protocol import router
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod


@markCmdActionHandler
class TreasureChestHandler(BaseMsgPackChecker):
    def __init__(self):
        super(TreasureChestHandler, self).__init__()

    def _check_param_rewardId(self, msg, key, params):
        rewardId = msg.getParam(key)
        if isstring(rewardId):
            return None, rewardId
        return None, {}

    def _check_param_helpUserId(self, msg, key, params):
        helpUserId = msg.getParam(key)
        if isinstance(helpUserId, int):
            return None, helpUserId
        return 'ERROR of helpUserId !' + str(helpUserId), None

    @markCmdActionMethod(cmd='dizhu', action='treasure_chest_list', clientIdVer=0, lockParamName='', scope='game')
    def doGetTreasureChestList(self, userId):
        mo = MsgPack()
        mo.setCmd('dizhu')
        mo.setResult('action', 'treasure_chest_list')
        mo.setResult('gameId', DIZHU_GAMEID)
        mo.setResult('userId', userId)
        treasureChestList = TreasureChestHelper.getTreasureChestList(userId)
        mo.setResult('treasureChestList', treasureChestList)

        videoShortenSeconds, helpShortenSeconds = TreasureChestHelper.getShortSeconds()
        mo.setResult('videoShortenSeconds', videoShortenSeconds)
        mo.setResult('helpShortenSeconds', helpShortenSeconds)

        if ftlog.is_debug():
            ftlog.debug('TreasureChestHandler.doGetTreasureList',
                        'userId= ', userId,
                        'treasureChestList=', treasureChestList)

        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd='dizhu', action='treasure_chest_unlock', clientIdVer=0, lockParamName='', scope='game')
    def doTreasureChestUnlock(self, userId, rewardId):
        self._doTreasureChestUnlock(userId, rewardId)

    @classmethod
    def _doTreasureChestUnlock(cls, userId, rewardId):
        mo = MsgPack()
        mo.setCmd('dizhu')
        mo.setResult('action', 'treasure_chest_unlock')
        mo.setResult('gameId', DIZHU_GAMEID)
        mo.setResult('userId', userId)
        mo.setResult('success', TreasureChestHelper.unlockTreasureChest(userId, rewardId))
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd='dizhu', action='treasure_chest_open', clientIdVer=0, lockParamName='', scope='game')
    def doTreasureChestOpen(self, userId, rewardId):
        self._doTreasureChestOpen(userId, rewardId)

    @classmethod
    def _doTreasureChestOpen(cls, userId, rewardId):
        mo = MsgPack()
        mo.setCmd('dizhu')
        mo.setResult('action', 'treasure_chest_open')
        mo.setResult('gameId', DIZHU_GAMEID)
        mo.setResult('userId', userId)
        ret, rewards = TreasureChestHelper.openTreasureChest(userId, rewardId)
        mo.setResult('success', ret)
        mo.setResult('rewards', rewards)
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd='dizhu', action='treasure_chest_video', clientIdVer=0, lockParamName='', scope='game')
    def doTreasureChestVideo(self, userId, rewardId):
        self._doTreasureChestVideo(userId, rewardId)

    @classmethod
    def _doTreasureChestVideo(cls, userId, rewardId):
        mo = MsgPack()
        mo.setCmd('dizhu')
        mo.setResult('action', 'treasure_chest_video')
        mo.setResult('gameId', DIZHU_GAMEID)
        mo.setResult('userId', userId)
        ret, state, leftSeconds = TreasureChestHelper.videoShortenTreasureChest(userId, rewardId)
        mo.setResult('success', ret)
        mo.setResult('state', state)
        mo.setResult('leftSeconds', leftSeconds)
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd='dizhu', action='treasure_chest_help', clientIdVer=0, lockParamName='', scope='game')
    def doTreasureChestHelp(self, userId, rewardId, helpUserId):
        self._doTreasureChestHelp(userId, rewardId, helpUserId)

    @classmethod
    def _doTreasureChestHelp(cls, userId, rewardId, helpUserId):
        mo = MsgPack()
        mo.setCmd('dizhu')
        mo.setResult('action', 'treasure_chest_help')
        mo.setResult('gameId', DIZHU_GAMEID)
        mo.setResult('userId', userId)
        ret, state, leftSeconds = TreasureChestHelper.helpShortenTreasureChest(userId, rewardId, helpUserId)
        mo.setResult('success', ret)
        mo.setResult('state', state)
        mo.setResult('leftSeconds', leftSeconds)
        mo.setResult('helpMsg', TreasureChestHelper.getHelpMsg(helpUserId))
        router.sendToUser(mo, userId)
