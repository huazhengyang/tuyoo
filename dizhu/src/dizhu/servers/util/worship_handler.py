# -*- coding:utf-8 -*-
'''
Created on 2018年1月2日

@author: wangyonghui
'''
from dizhu.entity.dizhuworship import WorshipHelper
from freetime.entity.msg import MsgPack
from hall.servers.common.base_checker import BaseMsgPackChecker
from poker.protocol import router
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod


@markCmdActionHandler
class WorshipHandler(BaseMsgPackChecker):
    def _check_param_foodId(self, msg, key, params):
        foodId = msg.getParam(key)
        if foodId and isinstance(foodId, int):
            return None, foodId
        return 'ERROR of foodId !' + str(foodId), None

    @markCmdActionMethod(cmd='dizhu', action='worship', clientIdVer=0, scope='game')
    def doGetWorship(self, userId):
        mo = MsgPack()
        foods, userChip = self._doGetWorship(userId)
        mo.setCmd('dizhu')
        mo.setResult('action', 'worship')
        mo.setResult('userId', userId)
        mo.setResult('userChip', userChip)
        mo.setResult('foods', foods)
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd='dizhu', action='worship_pray', clientIdVer=0, scope='game')
    def doGetPray(self, userId, foodId):
        mo = MsgPack()
        reward, userChip = self._doGetPray(userId, foodId)
        if not reward:
            return
        mo.setCmd('dizhu')
        mo.setResult('action', 'worship_pray')
        mo.setResult('userId', userId)
        mo.setResult('userChip', userChip)
        mo.setResult('reward', reward)
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd='dizhu', action='worship_history', clientIdVer=0, scope='game')
    def doGetWorshipHistory(self, userId):
        mo = MsgPack()
        mo.setCmd('dizhu')
        mo.setResult('action', 'worship_history')
        mo.setResult('history', self._doGetWorshipHistory())
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd='dizhu', action='worship_rank', clientIdVer=0, scope='game')
    def doGetWorshipRank(self, userId):
        mo = MsgPack()
        mo.setCmd('dizhu')
        mo.setResult('action', 'worship_rank')
        mo.setResult('userId', userId)
        mo.setResult('rank', self._doGetWorshipRank())
        router.sendToUser(mo, userId)

    def _doGetWorship(self, userId):
        return WorshipHelper.getWorship(userId)

    def _doGetPray(self, userId, foodId):
        return WorshipHelper.getPray(userId, foodId)

    def _doGetWorshipHistory(self):
        return WorshipHelper.getWorshipHistory()

    def _doGetWorshipRank(self):
        return WorshipHelper.getWorshipRank()
