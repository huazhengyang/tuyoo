# -*- coding:utf-8 -*-
'''
Created on 2017年8月16日

@author: wangyonghui
'''
from dizhu.entity.dizhufishing import FishHelper
from freetime.entity.msg import MsgPack
from hall.servers.common.base_checker import BaseMsgPackChecker
from poker.protocol import router
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod


@markCmdActionHandler
class FishingHandler(BaseMsgPackChecker):
    def _check_param_baitId(self, msg, key, params):
        baitId = msg.getParam(key)
        if baitId and isinstance(baitId, int):
            return None, baitId
        return 'ERROR of baitId !' + str(baitId), None

    @markCmdActionMethod(cmd='dizhu', action='fishing_info', clientIdVer=0, scope='game')
    def doGetFishingInfo(self, userId):
        mo = MsgPack()
        mo.setCmd('dizhu')
        mo.setResult('action', 'fishing_info')
        mo.setResult('info', self._doGetFishingInfo(userId))
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd='dizhu', action='fishing_fish', clientIdVer=0, scope='game')
    def doGetFish(self, userId, baitId):
        mo = MsgPack()
        mo.setCmd('dizhu')
        mo.setResult('action', 'fishing_fish')
        mo.setResult('fishReward', self._doGetFish(userId, baitId))
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd='dizhu', action='fishing_history', clientIdVer=0, scope='game')
    def doGetFishingHistory(self, userId):
        mo = MsgPack()
        mo.setCmd('dizhu')
        mo.setResult('action', 'fishing_history')
        mo.setResult('history', self._doGetFishingHistory())
        router.sendToUser(mo, userId)

    def _doGetFishingInfo(self, userId):
        return FishHelper.getFishingInfo(userId)

    def _doGetFish(self, userId, baitId):
        return FishHelper.getFishReward(userId, baitId)

    def _doGetFishingHistory(self):
        return FishHelper.getFishingHistory()
