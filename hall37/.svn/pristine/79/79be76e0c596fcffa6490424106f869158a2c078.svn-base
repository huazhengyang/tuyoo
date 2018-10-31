# -*- coding=utf-8
'''
Created on 2015年8月17日

@author: zhaojiangang
'''
import json

import freetime.util.log as ftlog
from hall.entity import hallconf, datachangenotify, hallitem
from hall.entity.hallconf import HALL_GAMEID
from hall.entity.hallevent import HallWithdrawCashEvent
from hall.entity.hallitem import TYExchangeItem
from hall.game import TGHall
from poker.entity.biz.exceptions import TYBizException
import poker.entity.biz.message.message as pkmessage
from poker.entity.configure import gdata
from poker.entity.dao import paydata, exchangedata, userdata
import poker.util.timestamp as pktimestamp


class TYExchangeRecord(object):
    STATE_NORMAL = 0
    STATE_AUDIT  = 1
    STATE_ACCEPT = 2
    STATE_REJECT = 3
    STATE_REJECT_RETURN = 4
    STATE_SHIPPING_SUCC = 5
    STATE_SHIPPING_FAIL = 6
    STATE_SHIPPING_FAIL_RETURN = 7
    
    def __init__(self, exchangeId):
        self.exchangeId = exchangeId
        self.itemId = None
        self.itemKindId = None
        self.createTime = None
        self.state = TYExchangeRecord.STATE_NORMAL
        self.params = None

    def toDict(self):
        return {
            'st':self.state,
            'itemId':self.itemId,
            'itemKindId':self.itemKindId,
            'ct':self.createTime,
            'params':self.params
        }

    def fromDict(self, d):
        self.state = d['st']
        self.itemId = d['itemId']
        self.itemKindId = d['itemKindId']
        self.createTime = d['ct']
        self.params = d['params']
        return self

def _makeExchangeId():
    return paydata.makeExchangeId()

def _buildExchangeKey(userId):
    return 'eo:9999:%s' % (userId)

def _saveRecordData(userId, exchangeId, recordData):
    return exchangedata.setExchangeData(userId, HALL_GAMEID, exchangeId, recordData)

def _loadRecordData(userId, exchangeId):
    return exchangedata.getExchangeData(userId, HALL_GAMEID, exchangeId)

def _loadRecordDatas(userId):
    return exchangedata.getExchangeDataAll(userId, HALL_GAMEID)

RESULT_OK            = 0
RESULT_REJECT        = 1
RESULT_REJECT_RETURN = 2
RESULT_AUDITSUCC     = 3
RESULT_SHIPPINGFAIL  = 4
RESULT_SHIPPINGFAIL_RETURN = 5

def loadRecord(userId, exchangeId):
    data = _loadRecordData(userId, exchangeId)
    if data:
        d = json.loads(data)
        record = TYExchangeRecord(exchangeId)
        record.fromDict(d)
        return record
    else:
        return None

def getExchangeRecords(userId):
    '''
    获取用户兑换记录
    '''
    ret = []
    datas = _loadRecordDatas(userId)
    if not datas:
        return ret

    for i in xrange(len(datas) / 2):
        try:
            jstr = datas[i*2+1]
            d = json.loads(jstr)
            record = TYExchangeRecord(datas[i*2])
            record.fromDict(d)
            ret.append(record)
        except:
            ftlog.error()
    return ret

def requestExchangeCash(userId, count, wxappId, timestamp):
    # 扣除奖券
    userAssets = hallitem.itemSystem.loadUserAssets(userId)
    _, consumeCount, _ = userAssets.consumeAsset(HALL_GAMEID, hallitem.ASSET_COUPON_KIND_ID, count, timestamp, 'WX_GET_CASH', count)
    if consumeCount < count:
        raise TYExchangeRequestError('个人提现余额不足: consumeCount=%s, count=%s' % (consumeCount, count))
    
    exchangeId = None
    try:
        exchangeId = _makeExchangeId()
        record = TYExchangeRecord(exchangeId)
        record.createTime = timestamp
        amount = count / 100.0
        record.params = {
            'type':7,
            'count':count,
            'amount':amount,
            'wxappId':wxappId
        }
        record.errorCode = 0
        record.state = TYExchangeRecord.STATE_NORMAL
        jstr = json.dumps(record.toDict())
        _saveRecordData(userId, exchangeId, jstr)
    
        displayName = '%.2f现金' % (amount)
        parasDict = {}
        httpAddr = gdata.httpGame()
        parasDict['callbackAudit']    = httpAddr+'/v3/game/exchange/auditCallback'
        parasDict['callbackShipping'] = httpAddr+'/v3/game/exchange/shippingResultCallback'
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
        rStr = json.dumps ( record.toDict () )
        _saveRecordData ( userId, exchangeId, rStr )
    
        ftlog.info('requestExchangeCash',
                   'userId=', userId,
                   'count=', count,
                   'amount=', amount,
                   'wxappId=', wxappId,
                   'exchangeId=', exchangeId,
                   'retcode=', retcode,
                   'retmsg=', retmsg)
        TGHall.getEventBus().publishEvent(HallWithdrawCashEvent(userId, HALL_GAMEID, count))
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

def requestExchange(userId, item, params, timestamp):
    assert(isinstance(item, TYExchangeItem))
    exchangeId = _makeExchangeId()
    record = TYExchangeRecord(exchangeId)
    record.itemId = item.itemId
    record.itemKindId = item.kindId
    record.createTime = timestamp
    record.params = params
    record.errorCode = 0
    record.state = TYExchangeRecord.STATE_NORMAL
    jstr = json.dumps(record.toDict())
    _saveRecordData(userId, exchangeId, jstr)

    parasDict = {}
    httpAddr = gdata.httpGame ()
    parasDict['callbackAudit']    = httpAddr+'/v3/game/exchange/auditCallback'
    parasDict['callbackShipping'] = httpAddr+'/v3/game/exchange/shippingResultCallback'
    parasDict['user_id'] = userId
    parasDict['exchange_id'] = exchangeId
    parasDict['prod_id'] = item.itemId
    parasDict['prod_kind_name'] = item.itemKind.displayName
    parasDict['prod_num'] = 1
    parasDict['exchange_type'] = params.get('type', 0)
    parasDict['exchange_amount'] = params.get('count', 0)
    parasDict['exchange_desc'] = params.get('desc', '')
    parasDict['user_phone'] = params.get('phone')
    parasDict['user_name'] = params.get('uName')
    parasDict['user_addres'] = params.get('uAddres')
    
    platformId = hallconf.getPublicConf('platformId', None)
    if platformId:
        parasDict['platform_id'] = platformId
        
    if parasDict['exchange_type'] == 5:
        parasDict['wxappid'] = params.get('wxappid', '')  # 微信红包需要
    if parasDict['exchange_type'] == 6:
        parasDict['user_province'] = params.get('uProvince')
        parasDict['user_city'] = params.get('uCity')
        parasDict['user_district'] = params.get('uDistrict')
        parasDict['user_town'] = params.get('uTown')
        parasDict['jd_product_id'] = params.get('jdProductId', '')
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
    rStr = json.dumps ( record.toDict () )
    _saveRecordData ( userId, exchangeId, rStr )

    ftlog.info('requestExchange',
               'userId=', userId,
               'exchangeId=', exchangeId,
               'itemId=', item.itemId,
               'itemKindId=', item.kindId,
               'retcode=', retcode,
               'retmsg=', retmsg)
    return record, retmsg

class TYExchangeRequestError(TYBizException):
    def __init__(self, message='兑换请求出错'):
        super(TYExchangeRequestError, self).__init__(-1, message)

class TYUnknownExchangeOrder(TYBizException):
    def __init__(self, message='未知的订单'):
        super(TYUnknownExchangeOrder, self).__init__(-1, message)

class TYBadStateExchangeOrder(TYBizException):
    def __init__(self, message='错误的订单状态'):
        super(TYBadStateExchangeOrder, self).__init__(-1, message)


def handleAuditResultItem(userId, record, result):
    userBag = hallitem.itemSystem.loadUserAssets(userId).getUserBag()
    item = userBag.findItem(record.itemId)

    timestamp = pktimestamp.getCurrentTimestamp()
    
    if not isinstance(item, TYExchangeItem):
        raise TYBizException (-1, '系统错误')

    if item.state != TYExchangeItem.STATE_AUDIT:
        raise TYBizException (-1, '道具状态错误')

    if result == RESULT_AUDITSUCC:
        item.state = TYExchangeItem.STATE_SHIPPING
        record.state = TYExchangeRecord.STATE_ACCEPT
        userBag.updateItem(HALL_GAMEID, item, timestamp)
    elif result == RESULT_REJECT:
        record.state = TYExchangeRecord.STATE_REJECT
        userBag.removeItem(HALL_GAMEID, item, timestamp, 'EXCHANGE', item.kindId)
    elif result == RESULT_REJECT_RETURN:
        record.state = TYExchangeRecord.STATE_REJECT_RETURN
        item.state = TYExchangeItem.STATE_NORMAL
        userBag.updateItem(HALL_GAMEID, item, timestamp)
    else:
        assert(0)

    itemDisPlayName = item.itemKind.displayName
    exchangeDesc = record.params.get ('desc', '')
    if result == RESULT_REJECT or result == RESULT_REJECT_RETURN:
        mail = '您申请用%s兑换(领取)%s，审核未通过，抱歉。' % (itemDisPlayName, exchangeDesc)
        pkmessage.send(HALL_GAMEID, pkmessage.MESSAGE_TYPE_SYSTEM, userId, mail)
        datachangenotify.sendDataChangeNotify(HALL_GAMEID, userId, 'message')
    
    return record

def handleAuditResultCoupon(userId, record, result):
    timestamp = pktimestamp.getCurrentTimestamp()
    userAssets = hallitem.itemSystem.loadUserAssets(userId)
    
    if result == RESULT_AUDITSUCC:
        record.state = TYExchangeRecord.STATE_ACCEPT
    elif result == RESULT_REJECT:
        record.state = TYExchangeRecord.STATE_REJECT
    elif result == RESULT_REJECT_RETURN:
        record.state = TYExchangeRecord.STATE_REJECT_RETURN
        count = record.params.get('count', 0)
        userAssets.addAsset(HALL_GAMEID, hallitem.ASSET_COUPON_KIND_ID, count, timestamp, 'WX_GET_CASH_BACK', count)
        # 历史提现记录对应减掉这个数额
        userdata.incrAttr(userId, 'exchangedCoupon', -abs(count))
    else:
        assert(0)

    if result in (RESULT_REJECT, RESULT_REJECT_RETURN):
        mail = '您申请提现%.2f元，审核未通过，抱歉。' % (record.params.get('amount', 0))
        pkmessage.send(HALL_GAMEID, pkmessage.MESSAGE_TYPE_SYSTEM, userId, mail)
        datachangenotify.sendDataChangeNotify(HALL_GAMEID, userId, 'message')

    return record

def sendShareForWXRedEnvelope(userId, record, item):
    try:
        action = item.itemKind.findActionByName('exchange')
        from hall.entity.hallitem import TYItemActionExchange
        if isinstance(action, TYItemActionExchange) and action.isWechatRedPack():  # 微信红包
            from poker.util import strutil
            from poker.entity.dao import sessiondata
            clientId = sessiondata.getClientId(userId)
            _, cVer, _ = strutil.parseClientId(clientId)
            if cVer >= 3.90:
                from hall.entity import hallshare
                gameId = strutil.getGameIdFromHallClientId(clientId)
                shareId = hallshare.getShareId('wxRedEnvelope', userId, gameId)
                share = hallshare.findShare(shareId)
                if share:
                    todotask = share.buildTodotask(HALL_GAMEID, userId, 'wxRedEnvelope')
                    if todotask:
                        from hall.entity.todotask import TodoTaskHelper
                        TodoTaskHelper.sendTodoTask(gameId, userId, todotask)
    except:
        ftlog.error('sendShareForWXRedEnvelope',
                    'userId=', userId,
                    'exchangeId=', record.exchangeId,
                    'itemId=', item.itemId,
                    'itemKindId=', item.kindId)


def handleShippingResultItem(userId, record, result):
    userBag = hallitem.itemSystem.loadUserAssets(userId).getUserBag()
    item = userBag.findItem(record.itemId)

    if not isinstance(item, TYExchangeItem):
        raise TYBizException(-1, '系统错误')

    if item.state != TYExchangeItem.STATE_SHIPPING:
        raise TYBizException(-1, '道具状态错误')

    timestamp = pktimestamp.getCurrentTimestamp()

    if result == RESULT_OK:
        record.state = TYExchangeRecord.STATE_SHIPPING_SUCC
        userBag.removeItem(HALL_GAMEID, item, timestamp, 'EXCHANGE', item.kindId)
    elif result == RESULT_SHIPPINGFAIL_RETURN:
        record.state = TYExchangeRecord.STATE_SHIPPING_FAIL_RETURN
        item.state = TYExchangeItem.STATE_NORMAL
        userBag.updateItem(HALL_GAMEID, item, timestamp)
    elif result == RESULT_SHIPPINGFAIL:
        record.state = TYExchangeRecord.STATE_SHIPPING_FAIL
        userBag.removeItem(HALL_GAMEID, item, timestamp, 'EXCHANGE', item.kindId)
    else:
        assert(0)
        
    itemDisPlayName = item.itemKind.displayName
    exchangeDesc = record.params.get('desc', '')
    if result == RESULT_OK:
        mail = '您申请用%s兑换(领取)%s，已成功为您办理，请查收。' % (itemDisPlayName, exchangeDesc)
    else:
        mail = '您申请用%s兑换(领取)%s，审核未通过，抱歉。' % (itemDisPlayName, exchangeDesc)

    pkmessage.send(HALL_GAMEID, pkmessage.MESSAGE_TYPE_SYSTEM, userId, mail)
    datachangenotify.sendDataChangeNotify(HALL_GAMEID, userId, 'message')

    if result == RESULT_OK:
        sendShareForWXRedEnvelope(userId, record, item)

def handleShippingResultCoupon(userId, record, result):
    timestamp = pktimestamp.getCurrentTimestamp()
    userAssets = hallitem.itemSystem.loadUserAssets(userId)
    if result == RESULT_OK:
        record.state = TYExchangeRecord.STATE_SHIPPING_SUCC
    elif result == RESULT_SHIPPINGFAIL_RETURN:
        record.state = TYExchangeRecord.STATE_SHIPPING_FAIL_RETURN
        count = record.params.get('count', 0)
        userAssets.addAsset(HALL_GAMEID, hallitem.ASSET_COUPON_KIND_ID, count, timestamp, 'WX_GET_CASH_BACK', count)
        # 历史提现记录对应减掉这个数额
        userdata.incrAttr(userId, 'exchangedCoupon', -abs(count))
    elif result == RESULT_SHIPPINGFAIL:
        record.state = TYExchangeRecord.STATE_SHIPPING_FAIL
    else:
        assert(0)
    
    amount = record.params.get('amount', 0)
    if result != RESULT_OK:
        mail = '您申请提现%.2f元，审核未通过，抱歉。' % (amount)
    else:
        mail = '您已成功提现%.2f元，请查收。' % (amount)
    pkmessage.send(HALL_GAMEID, pkmessage.MESSAGE_TYPE_SYSTEM, userId, mail)
    datachangenotify.sendDataChangeNotify(HALL_GAMEID, userId, 'message')
    
    return record

handlerMap = {
    0:(handleAuditResultItem, handleShippingResultItem),
    1:(handleAuditResultItem, handleShippingResultItem),
    3:(handleAuditResultItem, handleShippingResultItem),
    5:(handleAuditResultItem, handleShippingResultItem),
    6:(handleAuditResultItem, handleShippingResultItem),
    7:(handleAuditResultCoupon, handleShippingResultCoupon)
}

def findAuditResultHandler(record):
    found = handlerMap.get(record.params.get('type'))
    return found[0] if found else None

def findShippingResultHandler(record):
    found = handlerMap.get(record.params.get('type'))
    return found[1] if found else None

def handleExchangeAuditResult2(userId, exchangeId, result):
    '''
    处理审核结果
    '''
    if ftlog.is_debug():
        ftlog.debug('handleExchangeAuditResult2',
                    'userId=', userId,
                    'exchangeId=', exchangeId,
                    'result=', result)
    
    record = loadRecord(userId, exchangeId)
    if not record:
        raise TYUnknownExchangeOrder()
    
    if record.state != TYExchangeRecord.STATE_AUDIT:
        raise TYBadStateExchangeOrder()
    
    if result not in (RESULT_AUDITSUCC, RESULT_REJECT, RESULT_REJECT_RETURN):
        raise TYBizException(-1, '错误的审核结果')
    
    auditResultHandler = findAuditResultHandler(record)
    
    if not auditResultHandler:
        raise TYBizException(-1, '不能识别的兑换类型')
    
    auditResultHandler(userId, record, result)
    
    jstr = json.dumps(record.toDict())
    _saveRecordData(userId, record.exchangeId, jstr)
    
    ftlog.info('hallexchange.handleExchangeAuditResult2',
               'userId=', userId,
               'exchangeId=', record.exchangeId,
               'result=', result,
               'params=', record.params,
               'orderState=', record.state)
    return record

def handleShippingResult2(userId, exchangeId, result):
    '''
    发货结果处理
    '''
    if ftlog.is_debug():
        ftlog.debug('handleShippingResult2',
                    'userId=', userId,
                    'exchangeId=', exchangeId,
                    'result=', result)

    record = loadRecord(userId, exchangeId)
    if not record:
        raise TYUnknownExchangeOrder()
    
    if record.state != TYExchangeRecord.STATE_ACCEPT:
        raise TYBadStateExchangeOrder()

    if result not in (RESULT_OK, RESULT_SHIPPINGFAIL_RETURN, RESULT_SHIPPINGFAIL):
        raise TYBizException(-1, '错误的发货结果')
    
    shippingResultHandler = findShippingResultHandler(record)
    
    if not shippingResultHandler:
        raise TYBizException(-1, '不能识别的兑换类型')
    
    shippingResultHandler(userId, record, result)
    
    jstr = json.dumps(record.toDict())
    _saveRecordData(userId, exchangeId, jstr)

    ftlog.info('hallexchange.handleShippingResult',
               'userId=', userId,
               'exchangeId=', exchangeId,
               'result=', result,
               'params=', record.params,
               'orderState=', record.state)
    
    return record

def handleExchangeAuditResult1(userId, exchangeId, result):
    '''
    处理审核结果
    '''

    if ftlog.is_debug ( ):
        ftlog.debug ( 'userId=', userId, 'exchangeId=', exchangeId, 'result=', result )

    record = loadRecord ( userId, exchangeId )
    if not record:
        raise TYUnknownExchangeOrder ( )

    if record.state != TYExchangeRecord.STATE_AUDIT:
        raise TYBadStateExchangeOrder ( )

    userBag = hallitem.itemSystem.loadUserAssets ( userId ).getUserBag ( )
    item = userBag.findItem ( record.itemId )

    if not isinstance ( item, TYExchangeItem ):
        raise TYBizException ( -1, '系统错误' )

    if item.state != TYExchangeItem.STATE_AUDIT:
        raise TYBizException ( -1, '道具状态错误' )

    timestamp = pktimestamp.getCurrentTimestamp ( )

    if result == RESULT_AUDITSUCC:
        item.state = TYExchangeItem.STATE_SHIPPING
        record.state = TYExchangeRecord.STATE_ACCEPT
        userBag.updateItem ( HALL_GAMEID, item, timestamp )
    elif result == RESULT_REJECT:
        record.state = TYExchangeRecord.STATE_REJECT
        userBag.removeItem ( HALL_GAMEID, item, timestamp, 'EXCHANGE', item.kindId )
    elif result == RESULT_REJECT_RETURN:
        record.state = TYExchangeRecord.STATE_REJECT_RETURN
        item.state = TYExchangeItem.STATE_NORMAL
        userBag.updateItem ( HALL_GAMEID, item, timestamp )
    else:
        raise TYBizException ( -1, '错误的请求状态' )

    itemDisPlayName = item.itemKind.displayName
    exchangeDesc = record.params.get ( 'desc', '' )
    if result == RESULT_REJECT or result == RESULT_REJECT_RETURN:
        mail = '您申请用%s兑换(领取)%s，审核未通过，抱歉。' % (itemDisPlayName, exchangeDesc)
        pkmessage.send ( HALL_GAMEID, pkmessage.MESSAGE_TYPE_SYSTEM, userId, mail )
        datachangenotify.sendDataChangeNotify ( HALL_GAMEID, userId, 'message' )

    jstr = json.dumps(record.toDict())
    _saveRecordData(userId, exchangeId, jstr)

    ftlog.info('hallexchange.handleExchangeAuditResult1',
               'userId=', userId,
               'exchangeId=', exchangeId,
               'result=', result,
               'itemId=', item.itemId,
               'itemKindId=', item.kindId,
               'orderState=', record.state)
    return record


def handleShippingResult1(userId, exchangeId, result):
    '''
    发货结果处理
    '''
    if ftlog.is_debug():
        ftlog.debug('enter handleShippingResult(), userId:', userId, 'exchangeId:', exchangeId, 'result:', result )

    record = loadRecord(userId, exchangeId)
    if not record:
        raise TYUnknownExchangeOrder()
    if record.state != TYExchangeRecord.STATE_ACCEPT:
        raise TYBadStateExchangeOrder()

    userBag = hallitem.itemSystem.loadUserAssets(userId).getUserBag()
    item = userBag.findItem(record.itemId)

    if not isinstance(item, TYExchangeItem):
        raise TYBizException(-1, '系统错误')

    if item.state != TYExchangeItem.STATE_SHIPPING:
        raise TYBizException(-1, '道具状态错误')

    timestamp = pktimestamp.getCurrentTimestamp()

    if result == RESULT_OK:
        record.state = TYExchangeRecord.STATE_SHIPPING_SUCC
        userBag.removeItem(HALL_GAMEID, item, timestamp, 'EXCHANGE', item.kindId)
    elif result == RESULT_SHIPPINGFAIL_RETURN:
        record.state = TYExchangeRecord.STATE_SHIPPING_FAIL_RETURN
        item.state = TYExchangeItem.STATE_NORMAL
        userBag.updateItem(HALL_GAMEID, item, timestamp)
    elif result == RESULT_SHIPPINGFAIL:
        record.state = TYExchangeRecord.STATE_SHIPPING_FAIL
        userBag.removeItem(HALL_GAMEID, item, timestamp, 'EXCHANGE', item.kindId)
    else:
        raise TYBizException(-1, '错误的请求状态')

    itemDisPlayName = item.itemKind.displayName
    exchangeDesc = record.params.get('desc', '')
    if result == RESULT_OK:
        mail = '您申请用%s兑换(领取)%s，已成功为您办理，请查收。' % (itemDisPlayName, exchangeDesc)
    else:
        mail = '您申请用%s兑换(领取)%s，审核未通过，抱歉。' % (itemDisPlayName, exchangeDesc)

    pkmessage.send(HALL_GAMEID, pkmessage.MESSAGE_TYPE_SYSTEM, userId, mail)
    datachangenotify.sendDataChangeNotify(HALL_GAMEID, userId, 'message')

    if result == RESULT_OK:
        action = item.itemKind.findActionByName('exchange')
        from hall.entity.hallitem import TYItemActionExchange
        if isinstance(action, TYItemActionExchange) and action.isWechatRedPack():  # 微信红包
            from poker.util import strutil
            from poker.entity.dao import sessiondata
            clientId = sessiondata.getClientId(userId)
            _, cVer, _ = strutil.parseClientId(clientId)
            if cVer >= 3.90:
                from hall.entity import hallshare
                gameId = strutil.getGameIdFromHallClientId(clientId)
                shareId = hallshare.getShareId('wxRedEnvelope', userId, gameId)
                share = hallshare.findShare(shareId)
                if share:
                    todotask = share.buildTodotask(HALL_GAMEID, userId, 'wxRedEnvelope')
                    if todotask:
                        from hall.entity.todotask import TodoTaskHelper
                        TodoTaskHelper.sendTodoTask(gameId, userId, todotask)

    jstr = json.dumps(record.toDict())
    _saveRecordData(userId, exchangeId, jstr)

    ftlog.info('hallexchange.handleShippingResult1',
               'userId=', userId,
               'exchangeId=', exchangeId,
               'result=', result,
               'itemId=', item.itemId,
               'itemKindId=', item.kindId,
               'orderState=', record.state)
    
    return record

def handleExchangeAuditResult(userId, exchangeId, result):
    supportWXCash = hallconf.getPublicConf('support_wx_cash', 1)
    if supportWXCash:
        return handleExchangeAuditResult2(userId, exchangeId, result)
    return handleExchangeAuditResult1(userId, exchangeId, result)

def handleShippingResult(userId, exchangeId, result):
    supportWXCash = hallconf.getPublicConf('support_wx_cash', 1)
    if supportWXCash:
        return handleShippingResult2(userId, exchangeId, result)
    return handleExchangeAuditResult1(userId, exchangeId, result)


