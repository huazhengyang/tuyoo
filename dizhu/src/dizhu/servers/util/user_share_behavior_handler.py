# -*- coding:utf-8 -*-
'''
Created on 2018年6月14日

@author: wangyonghui
'''
from sre_compile import isstring

from dizhu.entity.segment import user_share_behavior
from freetime.entity.msg import MsgPack
from hall.servers.common.base_checker import BaseMsgPackChecker
from poker.protocol import router
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod


@markCmdActionHandler
class UserShareBehaviorHandler(BaseMsgPackChecker):
    def _check_param_burialId(self, msg, key, params):
        burialId = msg.getParam(key)
        if burialId and isstring(burialId):
            return None, burialId
        return 'ERROR of burialId !' + str(burialId), None

    @markCmdActionMethod(cmd='dizhu', action='user_share_behavior_info', clientIdVer=0, scope='game')
    def doUserShareBehaviorInfo(self, userId):
        mo = MsgPack()
        mo.setCmd('dizhu')
        mo.setResult('action', 'user_share_behavior_info')
        mo.setResult('userId', userId)
        ret = self._doUserShareBehaviorInfo(userId)
        mo.setResult('burial_list', ret.get('burial_list', []))
        mo.setResult('isBehavior', ret.get('isShare', 0))
        mo.setResult('videoOrBanner', ret.get('videoOrBanner', ''))
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd='dizhu', action='user_share_behavior_deal', clientIdVer=0, scope='game')
    def doUserShareBehaviorDeal(self, userId, burialId):
        mo = MsgPack()
        mo.setCmd('dizhu')
        mo.setResult('action', 'user_share_behavior_deal')
        mo.setResult('userId', userId)
        mo.setResult('burialId', burialId)
        leftCount, dealResult = self._doUserShareBehaviorDeal(userId, burialId)
        mo.setResult('dealResult', dealResult)
        mo.setResult('leftCount', leftCount)
        router.sendToUser(mo, userId)

    @classmethod
    def _doUserShareBehaviorInfo(cls, userId):
        return user_share_behavior.doGetUserShareBehaviorInfo(userId)

    @classmethod
    def _doUserShareBehaviorDeal(cls, userId, burialId):
        return user_share_behavior.doUserShareBehaviorDealResult(userId, burialId)


    @markCmdActionMethod(cmd='dizhu', action='no_invited_get_diamond', clientIdVer=0, lockParamName='', scope='game')
    def doNoInvitedGetDiamond(self, userId, gameId, clientId):
        getNoDiamond, burialId = self._do_get_no_invited_diamond(userId)
        mo = MsgPack()
        mo.setCmd('dizhu')
        mo.setResult('action', 'no_invited_get_diamond')
        mo.setResult('userId', userId)
        mo.setResult('burialId', burialId)
        mo.setResult('getNoDiamond', getNoDiamond)
        router.sendToUser(mo, userId)

    @classmethod
    def _do_get_no_invited_diamond(cls, userId):
        getNoDiamond, burialId = user_share_behavior.getNoInvitedDiamond(userId)
        return getNoDiamond, burialId

