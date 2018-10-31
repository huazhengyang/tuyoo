# -*- coding: utf-8 -*-
'''
Created on 2015年5月20日

@author: zqh
'''


from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from hall.entity import hallcoupon
from hall.servers.common.base_checker import BaseMsgPackChecker
from poker.entity.biz.exceptions import TYBizException
from poker.protocol import runcmd, router
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod
from poker.util import strutil

class ExchangeHelper(object):
    @classmethod
    def encodeCouponItem(cls, couponItem):
        return {
            'id':couponItem.couponId,
            'quan':couponItem.couponCount,
            'name':'%s%s%s' % (couponItem.itemCount, couponItem.itemUnits, couponItem.itemName),
            'pic':couponItem.pic,
            'tag':couponItem.tag,
            'type':couponItem.itemType
        }
    
    @classmethod
    def encodeCouponItemList(cls, couponItemList):
        ret = []
        for couponItem in couponItemList:
            ret.append(cls.encodeCouponItem(couponItem))
        return ret
    
    @classmethod
    def encodeRecordList(cls, recordList):
        ret = []
        if recordList:
            for record in recordList:
                ret.append({
                    'time':record['rtime'],
                    'use_coupon':record['amount'],
                    'name':str(record['money']) + '元话费',
                    'state':record['state']
                })
        return ret

@markCmdActionHandler
class HallExchangeHandler(BaseMsgPackChecker):
    def __init__(self):
        super(HallExchangeHandler, self).__init__()

    def _check_param_exchangeId(self, msg, key, params):
        exchangeId = msg.getParam(key)
        if exchangeId and isinstance(exchangeId,  (str, unicode)) :
            return None, exchangeId
        return 'ERROR of exchangeId !' + str(exchangeId), None
    
    def _check_param_result(self, msg, key, params):
        result = msg.getParam(key)
        if isinstance(result,  int) :
            return None, result
        return 'ERROR of result !' + str(result), None
        
    @markCmdActionMethod(cmd='exchange', action='update_item', clientIdVer=0, scope='game')
    def doUpdateItem(self, gameId, userId):
        mo = MsgPack()
        mo.setCmd('exchange')
        mo.setResult('action', 'update_item')
        mo.setResult('gameId', gameId)
        mo.setResult('userId', userId)
        mo.setResult('item_list', ExchangeHelper.encodeCouponItemList(self._getCouponService().couponItems))
        router.sendToUser(mo, userId)
        
    @markCmdActionMethod(cmd='exchange', action='update_record', clientIdVer=0, scope='game')
    def doUpdateRecord(self, gameId, userId):
        mo = MsgPack()
        mo.setCmd('exchange')
        mo.setResult('action', 'update_record')
        mo.setResult('gameId', gameId)
        mo.setResult('userId', userId)
        mo.setResult('record_list', ExchangeHelper.encodeRecordList(self._getCouponService().getExchangeRecords(userId)))
        mo.setResult('instruction', strutil.replaceParams(self._getCouponService().instruction, {'userId':str(userId)}))
        router.sendToUser(mo, userId)
        
    @markCmdActionMethod(cmd='exchange', action='audit', clientIdVer=0, scope='game')
    def doExchangeAuditResult(self, userId, exchangeId, result):
        try:
            msg = runcmd.getMsgPack()
            ftlog.debug('doExchangeAuditResult msg=', msg)
            from hall.entity import hallexchange
            hallexchange.handleExchangeAuditResult(userId, exchangeId, result)
        except:
            ftlog.error('HallExchangeHandler.doExchangeAuditResult userId=', userId,
                        'exchangeId=', exchangeId,
                        'result=', result)
        
    @markCmdActionMethod(cmd='exchange', action='exchange', clientIdVer=0, scope='game')
    def doExchange(self, gameId, userId):
        try:
            msg = runcmd.getMsgPack()
            couponId = msg.getParam('id')
            phone = msg.getParam('phone')
            if not phone:
                phone = msg.getParam('phoneNumber')
            if not phone:
                pp = msg.getParam('params', {})
                if isinstance(pp, dict) :
                    phone = pp.get('phoneNumber')
            if not phone:
                if ftlog.is_debug():
                    ftlog.debug('ExchangeHandler.doExchange gameId=', gameId,
                                'userId=', userId,
                                'couponId=', couponId,
                                'phone=', phone)
                raise TYBizException(-1, 'Please input phone number')
            _trueDelta, final = self._getCouponService().exchangeCouponItem(userId, couponId, phone=phone)
            mo = MsgPack()
            mo.setCmd('exchange')
            mo.setResult('action', 'exchange')
            mo.setResult('id', couponId)
            mo.setResult('info', '兑换请求处理成功')
            mo.setResult('quan_left', final)
            router.sendToUser(mo, userId)
        except TYBizException, e:
            mo = MsgPack()
            mo.setCmd('exchange')
            mo.setError(e.errorCode, e.message)
            router.sendToUser(mo, userId)
        
    def _getCouponService(self):
        return hallcoupon.couponService
    
    
