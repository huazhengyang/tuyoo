# -*- coding:utf-8 -*-
'''
Created on 2018年5月13日

@author: wangyonghui
'''
from hall.entity.usercoupon import user_coupon_details
from freetime.entity.msg import MsgPack
from hall.servers.common.base_checker import BaseMsgPackChecker
from poker.protocol import router
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod


@markCmdActionHandler
class UserCouponDetailsTcpHandler(BaseMsgPackChecker):
    @classmethod
    def encodeReceived(cls, status):
        ret = []
        if not status:
            return []
        for ritem in status.receivedItems[::-1]:
            itemD = {
                'time': ritem.timestamp,
                'count': ritem.count
            }
            source = user_coupon_details.getSourceName(ritem.source)
            itemD['desc'] = source
            ret.append(itemD)
        return ret

    @classmethod
    def _doGetUserCouponDetails(cls, gameId, userId, clientId):
        mo = MsgPack()
        mo.setCmd('hall')
        mo.setResult('action', 'coupon_details')
        mo.setResult('userId', userId)
        status = user_coupon_details.loadUserStatus(userId, clientId)
        mo.setResult('received', cls.encodeReceived(status))
        return mo

    @markCmdActionMethod(cmd='hall', action='coupon_details', clientIdVer=0)
    def doGetUserCouponDetails(self, gameId, userId, clientId):
        '''
        获取用户奖券列表
        '''
        mo = self._doGetUserCouponDetails(gameId, userId, clientId)
        if mo:
            router.sendToUser(mo, userId)
