# -*- coding:utf-8 -*-
'''
Created on 2017年7月15日

@author: zhaojiangang
'''
from sre_compile import isstring

from freetime.entity.msg import MsgPack
from hall.entity import hall_exmall
from hall.servers.common.base_checker import BaseMsgPackChecker
from poker.protocol import router
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod
import freetime.util.log as ftlog
import poker.util.timestamp as pktimestamp
from poker.entity.biz.exceptions import TYBizException


@markCmdActionHandler
class HallExMallHandler(BaseMsgPackChecker):
    def __init__(self):
        super(HallExMallHandler, self).__init__()

    def _check_param_shelvesName(self, msg, key, params):
        value = msg.getParam(key)
        if not isstring(value) or not value:
            return 'ERROR of shelvesName !' + str(value), None
        return None, value
    
    def _check_param_exchangeId(self, msg, key, params):
        value = msg.getParam(key)
        if not isstring(value) or not value:
            return 'ERROR of exchangeId !' + str(value), None
        return None, value
    
    def _check_param_exchangeCount(self, msg, key, params):
        value = msg.getParam(key, 1)
        if value and isinstance(value, int) :
            return None, value
        return 'ERROR of exchangeCount !' + str(value), None
    
    def _check_param_exchangeParams(self, msg, key, params):
        value = msg.getParam(key, {})
        if not isinstance(value, dict):
            return 'ERROR of exchangeParams !' + str(value), None
        return None, value
    
    @classmethod
    def _doGetShelves(cls, gameId, userId, clientId):
        mo = MsgPack()
        mo.setCmd('store_exchange')
        mo.setResult('action', 'get_shelves')
        mo.setResult('gameId', gameId)
        mo.setResult('userId', userId)
        shelvesList = hall_exmall.getShelvesList(userId, clientId)
        mo.setResult('list', [{'name':s.get('name'), 'displayName':s.get('displayName')} for s in shelvesList])
        return mo
    
    @markCmdActionMethod(cmd='store_exchange', action='get_shelves', clientIdVer=0, scope='game')
    def doGetShelves(self, gameId, userId, clientId):
        mo = self._doGetShelves(gameId, userId, clientId)
        router.sendToUser(mo, userId)

    @classmethod
    def encodeExchange(cls, gameId, userId, clientId, exchangeObj, timestamp):
        ret = {}
        ret['exchangeId'] = exchangeObj.exchangeId
        ret['displayName'] = exchangeObj.displayName
        ret['desc'] = exchangeObj.desc
        ret['shippingMethod'] = exchangeObj.shippingMethod or '无'
        ret['curTime'] = timestamp
        if exchangeObj.exchangeCycle:
            tp = exchangeObj.exchangeCycle.nextCycleTimePeriod(timestamp)
            if tp:
                if tp.startDT:
                    ret['exchangeStartTime'] = pktimestamp.datetime2Timestamp(tp.startDT)
                if tp.stopDT:
                    ret['exchangeEndTime'] = pktimestamp.datetime2Timestamp(tp.stopDT)
        
        visibleStock = 0
        stockNum = -1
        if exchangeObj.stock:
            stockNum = hall_exmall.queryStock(exchangeObj.exchangeId)
            if (exchangeObj.stock.displayStockLimit > -1
                and stockNum <= exchangeObj.stock.displayStockLimit):
                visibleStock = 1
        ret['stock'] = {'stockNum':stockNum, 'isVisible':visibleStock}
        
        cost = {'count':exchangeObj.cost.count, 'itemId':exchangeObj.cost.itemId}
        if exchangeObj.cost.name:
            cost['name'] = exchangeObj.cost.name
        if exchangeObj.cost.original:
            cost['original'] = exchangeObj.cost.original
        ret['cost'] = cost
        ret['clientParams'] = exchangeObj.delivery.getClientParams()
        ret['pic'] = exchangeObj.pic
        if exchangeObj.tagMark:
            ret['tagMark'] = exchangeObj.tagMark
        ret['vipLimit'] = exchangeObj.vipLimit
        return ret

    @classmethod
    def encodeExchanges(cls, gameId, userId, clientId, exchangeIds, timestamp):
        ret = []
        for exchangeId in exchangeIds:
            exchangeObj = hall_exmall.findExchange(exchangeId)
            if not exchangeObj:
                ftlog.warn('HallExMallHandler.encodeExchanges NotFoundExchange',
                           'userId=', userId,
                           'clientId=', clientId,
                           'exchangeId=', exchangeId,
                           'timestamp=', timestamp)
                continue
            
            if not hall_exmall.canDisplayExchange(userId, clientId, exchangeObj, timestamp):
                if ftlog.is_debug():
                    ftlog.debug('HallExMallHandler.encodeExchanges CanntDisplay',
                                'userId=', userId,
                                'clientId=', clientId,
                                'exchangeId=', exchangeId,
                                'timestamp=', timestamp)
                continue
            
            try:
                encoded = cls.encodeExchange(gameId, userId, clientId, exchangeObj, timestamp)
                ret.append(encoded)
            except:
                ftlog.error('HallExMallHandler.encodeExchanges Exception',
                            'userId=', userId,
                            'clientId=', clientId,
                            'exchangeId=', exchangeId,
                            'timestamp=', timestamp)
        return ret

    @classmethod
    def _doGetProduct(cls, gameId, userId, clientId, shelvesName, timestamp):
        mo = MsgPack()
        mo.setCmd('store_exchange')
        mo.setResult('action', 'get_product')
        mo.setResult('gameId', gameId)
        mo.setResult('userId', userId)
        mo.setResult('shelvesName', shelvesName)
        shelves = hall_exmall.getShelvesByName(userId, clientId, shelvesName, timestamp)
        exchangeIds = shelves.get('products', []) if shelves else []
        exchanges = cls.encodeExchanges(gameId, userId, clientId, exchangeIds, timestamp)
        mo.setResult('list', exchanges)
        return mo
        
    @markCmdActionMethod(cmd='store_exchange', action='get_product', clientIdVer=0, scope='game')
    def doGetProduct(self, gameId, userId, clientId, shelvesName):
        mo = self._doGetProduct(gameId, userId, clientId, shelvesName, pktimestamp.getCurrentTimestamp())
        router.sendToUser(mo, userId)

    @classmethod
    def _getExchangeRecord(cls,gameId,userId):
        mo = MsgPack()
        mo.setCmd('store_exchange')
        mo.setResult('action', 'exshop_record')
        mo.setResult('gameId', gameId)
        mo.setResult('userId', userId)

        recordList = []
        orderMap = hall_exmall.loadAllOrder(userId)
        for _, order in orderMap.iteritems():
            recordList.append(hall_exmall.encodeOrder(order))

        jdOrderTrack = []
        if ftlog.is_debug():
            ftlog.debug('_getExchangeRecord', 'userId=', userId)
            ftlog.debug('_getExchangeRecord', 'recordList=', recordList)

        if len(recordList) > 0:
            for listOne in xrange(len(recordList)):
                trackOne = {}
                exchangeId = recordList[listOne]['exchangeId']
                deliveryInfo = recordList[listOne]['deliveryInfo']
                state = recordList[listOne]['state']
                exchangeObj = hall_exmall.findExchange(exchangeId)

                if not exchangeObj or deliveryInfo is None or state != 6:

                    if exchangeObj:
                        trackOne['exchangeId'] = exchangeId
                        trackOne['displayName'] = exchangeObj.displayName
                        trackOne['pic'] = exchangeObj.pic
                        trackOne['logistics'] = []
                        orderStateTip = hall_exmall.getOrderStateTipe()
                        tipContent = orderStateTip["default"]
                        if state == 2:
                            tipContent = orderStateTip["state2Tip"]
                        elif state == 3:
                            tipContent = orderStateTip["state3Tip"]
                        elif state == 4:
                            tipContent = orderStateTip["state4Tip"]
                        elif state == 5:
                            tipContent = orderStateTip["state5Tip"]
                        elif state == 7:
                            tipContent = orderStateTip["state7Tip"]
                        elif state == 6:
                            tipContent = orderStateTip["state6Tip"]
                        elif state == 8:
                            tipContent = orderStateTip["state8Tip"]
                        trackOne['logistics'].append({
                            'content': tipContent,
                            'operator': "系统",
                            'msgTime': recordList[listOne]['createTime']
                        })

                        jdOrderTrack.append(trackOne)

                else:
                    try:

                        jdOrderId = deliveryInfo.get('jdOrderId')
                        if jdOrderId:
                            orderTrack = hall_exmall.getOrderTrackExchangeRecord(jdOrderId)
                            if len(orderTrack) > 0:
                                trackOne['logistics'] = orderTrack
                                trackOne['jdOrderId'] = jdOrderId
                                trackOne['exchangeId'] = exchangeId
                                trackOne['displayName'] = exchangeObj.displayName
                                trackOne['pic'] = exchangeObj.pic
                                jdOrderTrack.append(trackOne)

                    except:
                        ftlog.error('_getExchangeRecord.delivery ',
                                'userId=', userId)

        mo.setResult('exshopRList', jdOrderTrack)
        ftlog.hinfo("exmall _getExchangeRecord", gameId, userId, jdOrderTrack)
        return mo
    
    @classmethod
    def _doExchange(cls, gameId, userId, clientId, exchangeId, exchangeCount, exchangeParams, timestamp):
        mo = MsgPack()
        mo.setCmd('store_exchange')
        mo.setResult('action', 'exchange')
        mo.setResult('gameId', gameId)
        mo.setResult('userId', userId)
        mo.setResult('exchangeId', exchangeId)
        try:
            orderId = hall_exmall.doExchange(gameId, userId, clientId, exchangeId, exchangeCount, exchangeParams, timestamp)
            mo.setResult('orderId', orderId)
        except TYBizException, e:
            mo.setResult('code', e.errorCode)
            mo.setResult('info', e.message)
        return mo
    
    @markCmdActionMethod(cmd='store_exchange', action='exchange', clientIdVer=0, scope='game')
    def doExchange(self, gameId, userId, clientId, exchangeId, exchangeCount, exchangeParams):
        mo = self._doExchange(gameId, userId, clientId, exchangeId, exchangeCount, exchangeParams, pktimestamp.getCurrentTimestamp())
        router.sendToUser(mo, userId)


    @markCmdActionMethod(cmd='store_exchange', action='exshop_record', clientIdVer=0, scope='game')
    def doExchangeRecord(self, gameId, userId, clientId):
        mo = self._getExchangeRecord(gameId, userId)
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd='store_exchange', action='exshop_led', clientIdVer=0, scope='game')
    def doExchangeRecordLed(self, gameId, userId, clientId):
        mo = MsgPack()
        mo.setCmd('store_exchange')
        mo.setResult('action', 'exshop_led')
        mo.setResult('gameId', gameId)
        mo.setResult('userId', userId)
        exLedList = []
        try:
            from poker.entity.dao import daobase
            doExchangeRecordKey = "exhall:recordLed"
            LedList = daobase.executeMixCmd('LRANGE', doExchangeRecordKey, 0 , -1)
            if len(LedList) > 0:
                import json
                bigWinColor = "FFFF00"
                bigWinDefaultColor = "F0F8FF"

                for exled in LedList:
                    exled = json.loads(exled)
                    content = [
                        [bigWinDefaultColor, u'玩家'],
                        [bigWinColor, exled['name']],
                        [bigWinDefaultColor, u'成功兑换'],
                        [bigWinColor, exled['displayName']],
                        [bigWinDefaultColor, u'【'],
                        [bigWinColor, u'' + exled['exchangeTime']],
                        [bigWinDefaultColor, u'】']
                    ]
                    data = {'pic': exled['pic'],
                             'content': content}
                    exLedList.append(data)

            mo.setResult('exLedList', exLedList)
        except:
            mo.setResult('exLedList', [])
        ftlog.debug("doExchangeRecordLed:", exLedList)
        router.sendToUser(mo, userId)

    

