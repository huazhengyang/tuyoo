# -*- coding=utf-8
'''
Created on 2015年8月17日

@author: zhaojiangang
'''
import json

import freetime.util.log as ftlog
from hall.entity import hallconf, datachangenotify, hallitem
from hall.entity.hallconf import HALL_GAMEID
from hall.entity.hallexchange import TYExchangeRequestError, _makeExchangeId, TYExchangeRecord, _saveRecordData
from hall.entity import hallexchange
from poker.entity.configure import gdata
from poker.entity.dao import userdata


def requestExchangeCash(userId, count, wxappId, timestamp):
    # 扣除奖券
    userAssets = hallitem.itemSystem.loadUserAssets(userId)
    _, consumeCount, _ = userAssets.consumeAsset(HALL_GAMEID, hallitem.ASSET_COUPON_KIND_ID, count, timestamp, 'WX_GET_CASH', count)
    if consumeCount < count:
        raise TYExchangeRequestError('余额不足')

    exchangeId = None
    try:
        exchangeId = _makeExchangeId()
        record = TYExchangeRecord(exchangeId)
        record.createTime = timestamp
        amount = count / 100.0
        record.params = {
            'type': 7,
            'count': count,
            'amount': amount,
            'wxappId': wxappId
        }
        record.errorCode = 0
        record.state = TYExchangeRecord.STATE_NORMAL
        jstr = json.dumps(record.toDict())
        _saveRecordData(userId, exchangeId, jstr)

        displayName = '%.2f现金' % (amount)
        parasDict = {}
        httpAddr = gdata.httpGame()
        parasDict['callbackAudit'] = httpAddr + '/v3/game/exchange/auditCallback'
        parasDict['callbackShipping'] = httpAddr + '/v3/game/exchange/shippingResultCallback'
        parasDict['user_id'] = userId
        parasDict['exchange_id'] = exchangeId
        parasDict['prod_id'] = 'cash'
        parasDict['prod_kind_name'] = displayName
        parasDict['prod_num'] = 1
        parasDict['exchange_type'] = record.params.get('type', 7)
        parasDict['exchange_amount'] = amount
        parasDict['exchange_desc'] = displayName

        platformId = hallconf.getPublicConf('platformId', None)
        if platformId:
            parasDict['platform_id'] = platformId

        # gdss那边需要
        parasDict['user_phone'] = ''
        parasDict['user_name'] = ''
        parasDict['user_addres'] = ''

        parasDict['wxappid'] = wxappId
        gdssUrl = hallconf.getItemConf().get('exchangeGdssUrl',
                                             'http://gdss.touch4.me/?act=api.propExchange')
        from poker.util import webpage
        try:
            hbody, _ = webpage.webgetGdss(gdssUrl, parasDict)
            resJson = json.loads(hbody)
        except:
            ftlog.exception()
            raise TYExchangeRequestError()
        retcode = resJson.get('retcode', -1)
        retmsg = resJson.get('retmsg', '兑换请求出错')
        if retcode != 1:
            raise TYExchangeRequestError(retmsg)

        record.state = TYExchangeRecord.STATE_AUDIT
        rStr = json.dumps(record.toDict())
        _saveRecordData(userId, exchangeId, rStr)

        ftlog.info('requestExchangeCash',
                   'userId=', userId,
                   'count=', count,
                   'amount=', amount,
                   'wxappId=', wxappId,
                   'exchangeId=', exchangeId,
                   'retcode=', retcode,
                   'retmsg=', retmsg)
        return record, retmsg
    except:
        userAssets.addAsset(HALL_GAMEID, hallitem.ASSET_COUPON_KIND_ID, count, timestamp, 'WX_GET_CASH_BACK', count)
        # 历史提现记录对应减掉这个数额
        userdata.incrAttr(userId, 'exchangedCoupon', -abs(count))
        ftlog.warn('requestExchangeCash BackCoupon',
                   'userId=', userId,
                   'count=', count,
                   'wxappId=', wxappId,
                   'exchangeId=', exchangeId)
        raise
    finally:
        datachangenotify.sendDataChangeNotify(HALL_GAMEID, userId, 'coupon')

hallexchange.requestExchangeCash = requestExchangeCash
