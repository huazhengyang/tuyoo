# -*- coding:utf-8 -*-
'''
Created on 2017年7月15日

@author: zhaojiangang
'''
from datetime import datetime
import json
from sre_compile import isstring

import freetime.util.log as ftlog
from hall.entity import datachangenotify, hallitem, hallconf
from hall.entity.hallconf import HALL_GAMEID
from hall.entity.hallusercond import UserConditionRegister
from hall.servers.center.rpc import stock_remote
from poker.entity.biz.confobj import TYConfable, TYConfableRegister
from poker.entity.biz.content import TYContentItem
from poker.entity.biz.exceptions import TYBizConfException, TYBizException
from poker.entity.biz.item.item import TYAssetUtils
import poker.entity.biz.message.message as pkmessage
from poker.entity.configure import configure, gdata
from poker.entity.dao import daobase, daoconst, sessiondata, userdata
from poker.entity.events.tyevent import EventConfigure
import poker.entity.events.tyeventbus as pkeventbus
from poker.util import strutil
import poker.util.timestamp as pktimestamp


RESULT_OK = 0
RESULT_REJECT = 1
RESULT_REJECT_RETURN = 2
RESULT_AUDITSUCC = 3
RESULT_SHIPPINGFAIL = 4
RESULT_SHIPPINGFAIL_RETURN = 5


class NotEnoughStockException(TYBizException):
    def __init__(self, message='抱歉,库存补货中,请改日再来兑换,客服:4008098000!'):
        super(NotEnoughStockException, self).__init__(-1, message)


class NotInExchangeTimeCycleException(TYBizException):
    def __init__(self, message='请在兑换时间段内兑换'):
        super(NotInExchangeTimeCycleException, self).__init__(-1, message)


class UnknownExchangeOrderException(TYBizException):
    def __init__(self, message='未知的订单'):
        super(UnknownExchangeOrderException, self).__init__ (-1, message)


class BadExchangeOrderStateException(TYBizException):
    def __init__(self, message='错误的订单状态'):
        super(BadExchangeOrderStateException, self).__init__(-1, message)


class UnknownExchangeException(TYBizException):
    def __init__(self, message='兑换商品不存在'):
        super(UnknownExchangeException, self).__init__(-1, message)


class ExchangeRequestErrorException(TYBizException):
    def __init__ (self, message='兑换请求出错'):
        super (ExchangeRequestErrorException, self).__init__ (-1, message)


class ExchangeCostNotEnoughException(TYBizException):
    def __init__ (self, message='兑换费用不足'):
        super(ExchangeCostNotEnoughException, self).__init__(-1, message)


class BadExchangeParamsException(TYBizException):
    def __init__(self, message='参数错误'):
        super(BadExchangeParamsException, self).__init__(-1, message)


class TimePeriod(object):
    def __init__(self, startDT=None, stopDT=None):
        self.startDT = startDT
        self.stopDT = stopDT

    def isDTIn(self, nowDT):
        return ((not self.startDT or nowDT >= self.startDT)
                and (not self.stopDT or nowDT < self.stopDT))
        
    def isTimestampIn(self, nowTS):
        return self.isDTIn(datetime.fromtimestamp(nowTS))

    def decodeFromDict(self, d):
        start = d.get('start')
        stop = d.get('stop')
        
        if start:
            self.startDT = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')

        if stop:
            self.stopDT = datetime.strptime(stop, '%Y-%m-%d %H:%M:%S')
        
        return self
    

class TimeCycle(TYConfable):
    TYPE_ID = None
    
    def __init__(self):
        self.timePeriod = None
    
    def calcChecksum(self):
        '''
        计算该周期
        '''
        return None
    
    def calcIssueNum(self, timestamp):
        '''
        计算当前周期期号
        '''
        raise NotImplementedError
    
    def isDTIn(self, nowDT):
        return self.timePeriod.isDTIn(nowDT) if self.timePeriod else True
        
    def isTimestampIn(self, nowTS):
        return self.timePeriod.isTimestampIn(nowTS) if self.timePeriod else True
    
    def decodeFromDict(self, d):
        tp = d.get('timePeriod')
        if tp is not None:
            try:
                self.timePeriod = TimePeriod().decodeFromDict(tp)
            except:
                raise TYBizConfException(d, 'Bad timePeriod %s' % (tp))
        
        self._decodeFromDictImpl(d)
        
        return self
        
    def _decodeFromDictImpl(self, d):
        pass
    

class TimeCycleLife(TimeCycle):
    TYPE_ID = 'timeCycle.life'

    def __init__(self):
        super(TimeCycleLife, self).__init__()

    def calcChecksum(self):
        if self.timePeriod and self.timePeriod.startDT:
            return strutil.md5digest('%s.%s' % (self.TYPE_ID, self.timePeriod.startDT.strftime('%Y%m%d%H%M%S')))
        return strutil.md5digest('%s.%s' % (self.TYPE_ID, None))
    
    def calcIssueNum(self, timestamp):
        if self.timePeriod and self.timePeriod.startDT:
            startDT = self.timePeriod.startDT.replace(second=0, microsecond=0)
            return startDT.strftime('%Y%m%d%H%M%S')
        return datetime.fromtimestamp(0).strftime('%Y%m%d%H%M%S')


class TimeCyclePerDay(TimeCycle):
    TYPE_ID = 'timeCycle.perDay'
    
    def __init__(self):
        super(TimeCyclePerDay, self).__init__()
        
    def calcChecksum(self):
        if self.timePeriod and self.timePeriod.startDT:
            return strutil.md5digest('%s.%s' % (self.TYPE_ID, self.timePeriod.startDT.strftime('%Y%m%d%H%M%S')))
        return strutil.md5digest('%s.%s' % (self.TYPE_ID, None))
    
    def calcIssueNum(self, timestamp):
        dayStart = pktimestamp.getDayStartTimestamp(timestamp)
        return datetime.fromtimestamp(dayStart).strftime('%Y%m%d%H%M%S')


class TimeCycleNday(TimeCycle):
    TYPE_ID = 'timeCycle.nday'
    
    def __init__(self):
        super(TimeCycleNday, self).__init__()
        self.nday = None
        
    def calcChecksum(self):
        if self.timePeriod and self.timePeriod.startDT:
            return strutil.md5digest('%s.%s.%s' % (self.TYPE_ID, self.timePeriod.startDT.strftime('%Y%m%d%H%M%S'), self.nday))
        return strutil.md5digest('%s.%s.%s' % (self.TYPE_ID, None, self.nday))
    
    def calcIssueNum(self, timestamp):
        isseuStartTimestamp = self._calcIssueStartTimestamp(timestamp)
        return datetime.fromtimestamp(isseuStartTimestamp).strftime('%Y%m%d%H%M%S')

    def _decodeFromDictImpl(self, d):
        if not self.timePeriod or not self.timePeriod.startDT:
            raise TYBizConfException(d, 'TimeCycleNday.timePeriod.startDT must be set')
        
        self.nday = d.get('nday')
        if not isinstance(self.nday, int) or self.nday <= 0:
            raise TYBizConfException(d, 'TimeCycleNday.nday must be int > 0')

    def _calcIssueStartTimestamp(self, timestamp):
        if self.timePeriod and self.timePeriod.startDT:
            startTimestamp = pktimestamp.datetime2Timestamp(self.timePeriod.startDT)
        else:
            startTimestamp = pktimestamp.getDayStartTimestamp(timestamp)
        
        seconds = self.nday * 86400
        issueCount = (timestamp - startTimestamp) / seconds
        return startTimestamp + seconds * issueCount


class TimeCycleMinutes(TimeCycle):
    TYPE_ID = 'timeCycle.minutes'
    
    def __init__(self):
        super(TimeCycleMinutes, self).__init__()
        self.minutes = None
    
    def calcChecksum(self):
        if self.timePeriod and self.timePeriod.startDT:
            return strutil.md5digest('%s.%s.%s' % (self.TYPE_ID, self.timePeriod.startDT.strftime('%Y%m%d%H%M%S'), self.minutes))
        return strutil.md5digest('%s.%s' % (self.TYPE_ID, None, self.minutes))
    
    def calcIssueNum(self, timestamp):
        isseuStartTimestamp = self._calcIssueStartTimestamp(timestamp)
        return datetime.fromtimestamp(isseuStartTimestamp).strftime('%Y%m%d%H%M%S')

    def _decodeFromDictImpl(self, d):
        self.minutes = d.get('minutes')
        if not isinstance(self.minutes, int) or self.minutes <= 0:
            raise TYBizConfException(d, 'TimeCycleMinutes.minutes must be int > 0')
    
    def _calcIssueStartTimestamp(self, timestamp):
        if self.timePeriod and self.timePeriod.startDT:
            startDT = self.timePeriod.startDT.replace(second=0, microsecond=0)
            startTimestamp = pktimestamp.datetime2Timestamp(startDT)
        else:
            startTimestamp = pktimestamp.getDayStartTimestamp(timestamp)
        
        seconds = self.minutes * 60
        issueCount = (timestamp - startTimestamp) / seconds
        return startTimestamp + seconds * issueCount


class TimeCycleRegister(TYConfableRegister):
    _typeid_clz_map = {
        TimeCycleLife.TYPE_ID:TimeCycleLife,
        TimeCyclePerDay.TYPE_ID:TimeCyclePerDay,
        TimeCycleMinutes.TYPE_ID:TimeCycleMinutes,
        TimeCycleNday.TYPE_ID:TimeCycleNday
    }


class TimeSectionCycle(object):
    '''
    每个周期开始那一天的时间列表
    '''
    def __init__(self):
        self.timePeriod = None
        self.intervalDays = None
        self.times = []
        self.timesStr = None
        self.timePeriodStr = None
    
    def findTimeSection(self, t):
        for tc in self.times:
            if t >= tc[0] and t < tc[1]:
                return tc
        return None
    
    @classmethod
    def adjustTimePeriod(self, tp, limitTP):
        if limitTP:
            if limitTP.startDT:
                if not tp.startDT or limitTP.startDT > tp.startDT:
                    tp.startDT = limitTP.startDT
            
            if limitTP.stopDT:
                if not tp.stopDT or limitTP.stopDT < tp.stopDT:
                    tp.stopDT = limitTP.stopDT
        
        if (tp.startDT
            and tp.stopDT
            and tp.stopDT < tp.startDT):
            tp.stopDT = tp.startDT
        return tp
    
    def _calcCurCycleTimePeriod(self, timestamp):
        if not self.timePeriod.isTimestampIn(timestamp):
            return None
        
        if self.intervalDays == 0:
            return self.timePeriod
        
        # 计算timestamp所在周期起止时间
        issueStartTimestamp = self._calcIssueStartTimestamp(timestamp)
        issueDayStartDT = datetime.fromtimestamp(issueStartTimestamp)
        issueDayStopDT = datetime.fromtimestamp(issueStartTimestamp + 86400)
        
        # 不是周期第一天说明本周起已经没有时间段了
        if pktimestamp.getDayStartTimestamp(issueStartTimestamp) != pktimestamp.getDayStartTimestamp(timestamp):
            return None
        
        # 周期开始的第一天
        if not self.times:
            # 没有时间段配置，则是[issueStartTime, issueStartTime+86400)
            startDT = issueDayStartDT
            stopDT = issueDayStopDT
            return self.adjustTimePeriod(TimePeriod(startDT, stopDT), self.timePeriod)
        
        dt = datetime.fromtimestamp(timestamp)
        
        # 找到时间周期
        for tc in self.times:
            startDT = datetime.combine(dt.date(), tc[0])
            stopDT = datetime.combine(dt.date(), tc[1])
            tp = TimePeriod(startDT, stopDT)
            dayTP = TimePeriod(issueDayStartDT, issueDayStopDT)
            # 还没到时间或者在时间段内
            if (self.timePeriod.isDTIn(dt)
                and (dt < startDT or tp.isDTIn(dt))):
                tp = self.adjustTimePeriod(tp, dayTP)
                tp = self.adjustTimePeriod(tp, self.timePeriod)
                if tp.stopDT != tp.startDT:
                    return tp
        return None
            
    def nextCycleTimePeriod(self, timestamp):
        '''
        timestamp所在周期或者下一个周期的时间段，如果没有下一周期了返回None
        '''
        tp = self._calcCurCycleTimePeriod(timestamp)
        if tp or self.intervalDays == 0:
            return tp
        
        nextCycleTimestamp = timestamp + self.intervalDays * 86400
        issueStartTimestamp = self._calcIssueStartTimestamp(nextCycleTimestamp)
        return self._calcCurCycleTimePeriod(issueStartTimestamp)
    
    def decodeFromDict(self, d):
        self.timePeriod = TimePeriod().decodeFromDict(d)
        for tp in d.get('times', []):
            start = datetime.strptime(tp[0], '%H:%M:%S').time()
            stop = datetime.strptime(tp[1], '%H:%M:%S').time()
            if stop < start:
                raise TYBizConfException(d, 'TimeSectionCycle.times stop must >= start')
            self.times.append((start, stop))
        
        self.intervalDays = d.get('intervalDays', 0)
        if not isinstance(self.intervalDays, int) or self.intervalDays < 0:
            raise TYBizConfException(d, 'TimeSectionCycle.intervalDays must be int >= 0')
        
        if self.times and self.intervalDays == 0:
            raise TYBizConfException(d, 'TimeSectionCycle.intervalDays must be int > 0')
        
        self.times.sort(key=lambda tp: tp[0])
        return self
    
    def _calcIssueStartTimestamp(self, timestamp):
        if self.timePeriod and self.timePeriod.startDT:
            startTimestamp = pktimestamp.datetime2Timestamp(self.timePeriod.startDT)
        else:
            startTimestamp = pktimestamp.getDayStartTimestamp(timestamp)
        
        if self.intervalDays > 0:
            seconds = self.intervalDays * 86400
            issueCount = int((timestamp - startTimestamp) / seconds)
            return startTimestamp + seconds * issueCount
        return startTimestamp
    
    def __str__(self):
        if self.timesStr is None:
            timelst = [(tc[0].strftime('%H:%M:%S'), tc[1].strftime('%H:%M:%S')) for tc in self.times]
            self.timesStr = str(timelst)
        if self.timePeriodStr is None:
            start = self.timePeriod.startDT.strftime('%Y-%m-%d %H:%M:%S') if self.timePeriod.startDT else None
            stop = self.timePeriod.stopDT.strftime('%Y-%m-%d %H:%M:%S') if self.timePeriod.stopDT else None
            self.timePeriodStr = '[%s,%s]' % (start, stop)
        return '%s:%s:%s' % (self.timePeriodStr, self.intervalDays, self.timesStr)


class ExchangeDelivery(TYConfable):
    TYPE_ID = None

    DELIVERYING = 1
    DELIVERIED = 2
    
    def getClientParams(self):
        return {}
    
    def checkParams(self, userId, exchangeObj, count, params):
        pass

    def delivery(self, userId, exchangeObj, count, params):
        pass


class ExchangeDeliveryTY(ExchangeDelivery):
    TYPE_ID = 'ty.delivery:ty'
    
    def __init__(self):
        self.items = None
        self.clientParams = None

    def getClientParams(self):
        return self.clientParams or {}
    
    def delivery(self, order):
        timestamp = pktimestamp.getCurrentTimestamp()
        userAssets = hallitem.itemSystem.loadUserAssets(order.userId)
        userAssets.sendContentItemList(HALL_GAMEID,
                                       self.items,
                                       order.count,
                                       True,
                                       timestamp,
                                       'HALL_EXMALL_DELIVERY',
                                       int(order.exchangeId))
        ftlog.info('ExchangeDeliveryTY.delivery ok',
                   'userId=', order.userId,
                   'exchangeId=', order.exchangeId,
                   'count=', order.count,
                   'params=', order.params)
        
        return ExchangeDelivery.DELIVERIED
    
    def decodeFromDict(self, d):
        self.items = TYContentItem.decodeList(d.get('items'))
        self.clientParams = d.get('clientParams', {})
        if not isinstance(self.clientParams, dict):
            raise TYBizConfException(d, 'ExchangeDeliveryTY.clientParams must dict')
        return self


class ExchangeDeliveryGDSS(ExchangeDelivery):
    TYPE_ID = 'ty.delivery:gdss'

    def __init__(self):
        self.auditParams = None
        self.clientParams = None

    def getClientParams(self):
        return self.clientParams

    def isWechatRedPack(self):
        return self.auditParams.get('type') == 5

    def isJdActualProduct(self):
        return self.auditParams.get('type') == 6
    
    def checkParams(self, userId, exchangeObj, count, params):
        phone = params.get('phoneNumber')
        if not phone:
            raise BadExchangeParamsException('请填写手机')
        
        if self.isJdActualProduct():
            # 京东实物，必须传地址
            province = params.get('uProvince')
            city = params.get('uCity')
            addr = params.get('uAddres')
            userName = params.get('uName')
            if (not province or not city or not addr or not userName):
                raise BadExchangeParamsException('地址信息错误')
    
    def delivery(self, order):
        parasDict = {}
        httpAddr = gdata.httpGame ()
        parasDict['callbackAudit'] = httpAddr + '/v3/game/hall_exmall/auditCallback'
        parasDict['callbackShipping'] = httpAddr + '/v3/game/hall_exmall/shippingResultCallback'
        parasDict['user_id'] = order.userId
        parasDict['exchange_id'] = order.orderId
        parasDict['prod_id'] = int(order.exchangeId)
        parasDict['prod_kind_name'] = order.exchangeObj.displayName
        parasDict['prod_num'] = order.count
        parasDict['exchange_type'] = self.auditParams.get('type', 0)
        parasDict['exchange_amount'] = self.auditParams.get('count', 0)
        parasDict['exchange_desc'] = self.auditParams.get('desc', '')
        parasDict['user_phone'] = str(order.params.get('phoneNumber')) if not self.isWechatRedPack() else '11111111111'
        parasDict['user_name'] = order.params.get('uName', '')
        parasDict['user_addres'] = order.params.get('uAddres', '')
        if self.isWechatRedPack():
            from hall.entity import hall_wxappid
            clientId = sessiondata.getClientId(order.userId)
            wxappid = hall_wxappid.queryWXAppid(HALL_GAMEID, order.userId, clientId)
            parasDict['wxappid'] = wxappid if wxappid else 0  # 微信红包需要
        elif self.isJdActualProduct():
            parasDict['user_province'] = order.params.get('uProvince', '')
            parasDict['user_city'] = order.params.get('uCity', '')
            parasDict['user_district'] = order.params.get('uDistrict', '')
            parasDict['user_town'] = order.params.get('uTown', '')
            parasDict['jd_product_id'] = self.auditParams.get('jdProductId')

        gdssUrl = getExchangeGdssUrl()
        from poker.util import webpage
        try:
            
            hbody, _ = webpage.webgetGdss(gdssUrl, parasDict)
            resJson = json.loads(hbody)
        except:
            ftlog.error('ExchangeDeliveryGDSS.delivery BadResp',
                        'userId=', order.userId,
                        'orderId=', order.orderId,
                        'exchangeId=', order.exchangeId)
            raise ExchangeRequestErrorException()

        retcode = resJson.get('retcode', -1)
        retmsg = resJson.get('retmsg', '兑换请求出错')
        if retcode != 1:
            ftlog.warn('ExchangeDeliveryGDSS.delivery Failed',
                       'userId=', order.userId,
                       'orderId=', order.orderId,
                       'exchangeId=', order.exchangeId,
                       'gdssRet=', resJson)
            raise ExchangeRequestErrorException(retmsg)

        ftlog.info('ExchangeDeliveryGDSS.delivery OK',
                   'userId=', order.userId,
                   'orderId=', order.orderId,
                   'exchangeId=', order.exchangeId,
                   'cost=', order.cost,
                   'count=', order.count)

        return ExchangeDelivery.DELIVERYING
    
    def decodeFromDict(self, d):
        self.auditParams = d.get('auditParams')
        if not isinstance(self.auditParams, dict):
            raise TYBizConfException(d, 'ExchangeDeliveryGDSS.auditParams must dict')
        
        if self.auditParams.get('type') == 6:
            jdProductId = self.auditParams.get('jdProductId')
            if not jdProductId or not isstring(jdProductId):
                raise TYBizConfException(d, 'ExchangeDeliveryGDSS.auditParams.jdProduct must string')
        
        self.clientParams = d.get('clientParams', {})
        if not isinstance(self.clientParams, dict):
            raise TYBizConfException(d, 'ExchangeDeliveryGDSS.clientParams must dict')
        
        return self


class ExchangeDeliveryRegister(TYConfableRegister):
    _typeid_clz_map = {
        ExchangeDeliveryTY.TYPE_ID:ExchangeDeliveryTY,
        ExchangeDeliveryGDSS.TYPE_ID:ExchangeDeliveryGDSS,
    }


class ExchangeStockConf(object):
    def __init__(self):
        # 时间周期
        self.timeCycle = None
        # 库存数量，-1表示无限制
        self.count = None
        # 库存显示限制，低于这个值客户端要显示库存量，-1代表永不显示
        self.displayStockLimit = None
        
    def decodeFromDict(self, d):
        self.timeCycle = TimeCycleRegister.decodeFromDict(d.get('cycle'))
        self.count = d.get('count')
        
        if not isinstance(self.count, int) or self.count < -1:
            raise TYBizConfException(d, 'ExchangeStockConf.count must be int >= -1')
        
        self.displayStockLimit = d.get('displayStockLimit', -1)
        if not isinstance(self.displayStockLimit, int) or self.displayStockLimit < -1:
            raise TYBizConfException(d, 'ExchangeStockConf.count must be int >= -1')
        
        return self
    
    def adjustStock(self, stockObj, timestamp):
        curIssueNum = self.timeCycle.calcIssueNum(timestamp)
        stockIssueNum = self.timeCycle.calcIssueNum(stockObj.lastUpdateTime)
        
        if not stockObj.checksum:
            stockObj.checksum = self.timeCycle.calcChecksum()
        if not stockObj.issueNum:
            stockObj.issueNum = curIssueNum
        
        if not self.timeCycle or self.timeCycle.isTimestampIn(timestamp):
            if stockObj.lastUpdateTime == 0 or curIssueNum != stockIssueNum:
                stockObj.issueNum = curIssueNum
                stockObj.lastUpdateTime = timestamp
                stockObj.stock = self.count
        return stockObj


class ExchangeCondition(object):
    def __init__(self):
        self.condition = None
        self.failure = None
        self.visibleInStore = None

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        return self.condition.check(gameId, userId, clientId, timestamp, **kwargs)

    def fromDict(self, d):
        self.condition = UserConditionRegister.decodeFromDict(d.get('condition'))
        self.failure = d.get('failure')
        
        if not isstring(self.failure) or not self.failure:
            raise TYBizConfException(d, 'ExchangeCondition.failure must be not empty string')
        
        self.visibleInStore = d.get('visibleInStore', 1)
        return self
        

class ExchangeCountLimitRecord(object):
    def __init__(self, lastExchangeTime=0, count=0):
        self.lastExchangeTime = lastExchangeTime
        self.count = count
    
    def toDict(self):
        return {'let':self.lastExchangeTime, 'ct':self.count}
    
    def fromDict(self, d):
        self.lastExchangeTime = d.get('let', 0)
        self.count = d.get('ct', 0)
        return self


class ExchangeCountLimit(object):
    def __init__(self):
        self.timeCycle = None
        self.count = None
        self.visibleInStore = None
        self.failure = None
        
    def decodeFromDict(self, d):
        self.timeCycle = TimeCycleRegister.decodeFromDict(d.get('cycle'))
        self.count = d.get('count')
        
        if not isinstance(self.count, int) or self.count < 0:
            raise TYBizConfException(d, 'ExchangeStock.count must be int >= 0')
        
        self.visibleInStore = d.get('visibleInStore', 1)
        if self.visibleInStore not in (0, 1):
            raise TYBizConfException(d, 'ExchangeStock.visibleInStore must in (0,1)')
        
        self.failure = d.get('failure')
        if not self.failure or not isstring(self.failure):
            raise TYBizConfException(d, 'ExchangeStock.failure must be not empty string')
        
        return self
    
    def adjustRecord(self, record, timestamp):
        if (record.lastExchangeTime == 0
            or (self.timeCycle.calcIssueNum(record.lastExchangeTime) != self.timeCycle.calcIssueNum(timestamp))):
            record.lastExchangeTime = timestamp
            record.count = 0
        return record
    
    def checkLimit(self, record, count):
        if self.count <= 0:
            return True

        return record.count + count <= self.count


class ExchangeCost(object):
    def __init__(self):
        self.itemId = None
        self.count = None
        self.original = None
        self.name = None
        
    def decodeFromDict(self, d):
        self.itemId = d.get('itemId')
        if not isstring(self.itemId) or not self.itemId:
            raise TYBizConfException(d, 'ExchangeCost.itemId must be not empty string')
            
        self.count = d.get('count')
        if not isinstance(self.count, int) or self.count <= 0:
            raise TYBizConfException(d, 'ExchangeCost.count must be int > 0')
        
        self.name = d.get('name')
        if (self.name is not None
            and not isstring(self.name)
            and not self.name):
            raise TYBizConfException(d, 'ExchangeCost.name must be not empty string or None')
        
        self.original = d.get('original')
        if (self.original is not None
            and not isinstance(self.original, int)):
            raise TYBizConfException(d, 'ExchangeCost.original must be int')
            
        return self


class Exchange(object):
    def __init__(self):
        # 兑换id
        self.exchangeId = None
        # 显示名称
        self.displayName = None
        # 商品描述
        self.desc = None
        # 商品图片
        self.pic = None
        # vip限制
        self.vipLimit = None
        # 标签
        self.tagMark = None
        # 配送方式
        self.shippingMethod = None
        # 价格
        self.cost = None
        # 发货
        self.delivery = None
        # 显示周期
        self.displayCycle = None
        # 兑换周期
        self.exchangeCycle = None
        # 库存管理
        self.stock = None
        # 用户兑换限制
        self.exchangeCountLimit = None
        # 兑换条件列表，and关系
        self.exchangeConditions = None
        # 玩家兑换完成后给用户发的消息
        self.mail = None
    
    def decodeFromDict(self, d):
        self.exchangeId = d.get('exchangeId')
        if not isstring(self.exchangeId) or not self.exchangeId:
            raise TYBizConfException(d, 'Exchange.exchangeId must be not empty string')
        
        try:
            _intExchangeId = int(self.exchangeId)
        except:
            raise TYBizConfException(d, 'Exchange.exchangeId must be int string')
        
        self.displayName = d.get('displayName')
        if not isstring(self.displayName) or not self.displayName:
            raise TYBizConfException(d, 'Exchange.displayName must be not empty string')
        
        self.desc = d.get('desc', '')
        if not isstring(self.desc):
            raise TYBizConfException(d, 'Exchange.desc must be string')
        
        self.pic = d.get('pic', '')
        if not isstring(self.pic):
            raise TYBizConfException(d, 'Exchange.pic must be string')
        
        self.tagMark = d.get('tagMark', '')
        if not isstring(self.tagMark):
            raise TYBizConfException(d, 'Exchange.tagMark must be string')
        
        self.vipLimit = d.get('vipLimit', 0)
        if not isinstance(self.vipLimit, int) or self.vipLimit < 0:
            raise TYBizConfException(d, 'Exchange.vipLimit must be int >= 0')
        
        self.shippingMethod = d.get('shippingMethod')
        if self.shippingMethod and not isstring(self.shippingMethod):
            raise TYBizConfException(d, 'Exchange.shippingMethod must be string')
        
        self.cost = ExchangeCost().decodeFromDict(d.get('cost'))
        self.delivery = ExchangeDeliveryRegister.decodeFromDict(d.get('delivery'))
        
        displayCycleD = d.get('displayCycle')
        if displayCycleD:
            self.displayCycle = TimeSectionCycle().decodeFromDict(displayCycleD)
            
        exchangeCycleD = d.get('exchangeCycle')
        if exchangeCycleD:
            self.exchangeCycle = TimeSectionCycle().decodeFromDict(exchangeCycleD)
        
        stockD = d.get('stock')
        if stockD:
            self.stock = ExchangeStockConf().decodeFromDict(stockD)

        exchangeCountLimitD = d.get('exchangeCountLimit')
        if exchangeCountLimitD:
            self.exchangeCountLimit = ExchangeCountLimit().decodeFromDict(exchangeCountLimitD)
        
        self.exchangeConditions = []
        for condD in  d.get('exchangeConditions', []):
            cond = ExchangeCondition().fromDict(condD)
            self.exchangeConditions.append(cond)
        
        self.mail = d.get('mail', '')
        if not isstring(self.mail):
            raise TYBizConfException(d, 'Exchange.mail must be string')
        
        return self


class ExchangeStock(object):
    def __init__ (self):
        self.stock = 0
        self.lastUpdateTime = 0
        self.issueNum = None
        self.checksum = None

    def fromDict(self, d):
        self.stock = d.get('stock', 0)
        self.issueNum = d.get('issn')
        self.lastUpdateTime = d.get('lut', 0)
        self.checksum = d.get('cs', 0)
        return self
    
    def toDict(self):
        return {'stock':self.stock, 'lut':self.lastUpdateTime, 'cs':self.checksum, 'issn':self.issueNum}


class ExchangeOrder(object):
    # 订单状态
    STATE_FAIL = -1
    STATE_NORMAL = 0
    STATE_PAID = 1  # 已支付
    STATE_AUDIT = 2 #审核当中
    STATE_AUDITSUCC = 3
    STATE_REJECT = 4 #审核失败
    STATE_REJECT_RETURN = 5 #审核并返回奖券
    STATE_SHIPPING_SUCC = 6 #发货成功
    STATE_SHIPPING_FAIL = 7 #发货失败
    STATE_SHIPPING_FAIL_RETURN = 8 #发货失败并且发货奖券

    def __init__(self, userId, orderId):
        self.userId = userId
        self.orderId = orderId
        self.exchangeId = None
        self.count = None
        self.cost = None
        self.createTime = None
        self.state = self.STATE_NORMAL
        self.params = None
        self.errorCode = 0
        self.clientId = None
        self.exchangeObj = None
        self.deliveryInfo = None

    def toDict (self):
        return {
            'exId':self.exchangeId,
            'cost':self.cost,
            'count':self.count,
            'st':self.state,
            'ct':self.createTime,
            'params':self.params,
            'clientId':self.clientId,
            'ec':self.errorCode,
            'di':self.deliveryInfo
        }

    def fromDict (self, d):
        self.exchangeId = d['exId']
        self.cost = d['cost']
        self.count = d['count']
        self.state = d['st']
        self.createTime = d['ct']
        self.params = d['params']
        self.clientId = d['clientId']
        self.errorCode = d['ec']
        self.deliveryInfo = d.get('di')
        return self


_inited = False
_exchangeMap = {}
_templateMap = {}
_exchangeGdssUrl = ''
_orderTrackUrl = ''

def findExchange(exchangeId):
    return _exchangeMap.get(exchangeId)

def getExchangeGdssUrl():
    return _exchangeGdssUrl

def getOrderTrackUrl():
    return _orderTrackUrl

def getOrderStateTipe():
    return _orderStateTip

def loadExchangeCountLimitRecord(userId, exchangeId):
    jstr = None
    try:
        jstr = daobase.executeUserCmd(userId, 'hget', 'exmall.limit:%s' % (userId), exchangeId)
        if jstr:
            d = strutil.loads(jstr)
            return ExchangeCountLimitRecord().fromDict(d)
    except:
        ftlog.warn('hall_exmall.loadCountLimitRecord',
                   'userId=', userId,
                   'exchangeId=', exchangeId,
                   'jstr=', jstr)
    return ExchangeCountLimitRecord()


def saveExchangeCountLimitRecord(userId, exchangeId, record):
    d = record.toDict()
    jstr = strutil.dumps(d)
    daobase.executeUserCmd(userId, 'hset', 'exmall.limit:%s' % (userId), exchangeId, jstr)


def checkExchangeConditions(userId, exchangeObj, clientId, count, timestamp):
    if not exchangeObj.exchangeConditions:
        return True, None
    
    for cond in exchangeObj.exchangeConditions:
        if not cond.check(HALL_GAMEID, userId, clientId, timestamp):
            return False, cond
    
    return True, None


def checkExchangeCountLimit(userId, exchangeObj, clientId, count, timestamp):
    if not exchangeObj.exchangeCountLimit:
        return True, None
    
    record = loadExchangeCountLimitRecord(userId, exchangeObj.exchangeId)
    exchangeObj.exchangeCountLimit.adjustRecord(record, timestamp)
    
    return exchangeObj.exchangeCountLimit.checkLimit(record, count), record


def _makeOrderId():
    exchangeId = daobase._executePayDataCmd('INCR', daoconst.PAY_KEY_EXCHANGE_ID)
    ct = datetime.now ()
    exchangeId = 'NEO%s%s' % (ct.strftime ('%Y%m%d%H%M%S'), exchangeId)
    return exchangeId


def makeOrder(userId, exchangeObj, clientId, exchangeParams, count, timestamp):
    orderId = _makeOrderId()
    order = ExchangeOrder(userId, orderId)
    order.cost = None
    order.count = count
    order.exchangeId = exchangeObj.exchangeId
    order.exchangeId = exchangeObj.exchangeId
    order.createTime = timestamp
    order.params = exchangeParams
    order.clientId = clientId
    order.exchangeObj = exchangeObj
    saveOrder(order)
    return order


def saveOrder(order):
    d = order.toDict()
    jstr = strutil.dumps(d)
    daobase.executeUserCmd(order.userId, 'HSET', 'neo:%s:%s' % (HALL_GAMEID, order.userId), order.orderId, jstr)
    if ftlog.is_debug():
        ftlog.debug('hall_exmall.saveOrder',
                    'orderId=', order.orderId,
                    'jstr=', jstr)


def loadOrder(userId, orderId):
    jstr = None
    try:
        jstr = daobase.executeUserCmd(userId, 'HGET', 'neo:%s:%s' % (HALL_GAMEID, userId), orderId)
        if jstr:
            d = strutil.loads(jstr)
            return ExchangeOrder(userId, orderId).fromDict(d)
    except:
        ftlog.warn('hall_exmall.loadOrder BadOrder',
                   'userId=', userId,
                   'orderId=', orderId,
                   'jstr=', jstr)
    return None

def encodeOrder(order):
    return {
        'orderId': order.orderId,
        'exchangeId': order.exchangeId,
        'count': order.count,
        'cost': order.cost,
        'state': order.state,
        'params': order.params,
        'createTime': datetime.fromtimestamp(order.createTime).strftime('%Y-%m-%d %H:%M:%S'),
        'errorCode': order.errorCode,
        'clientId': order.clientId,
        'deliveryInfo': order.deliveryInfo
    }
def loadAllOrder(userId):
    ret = {}
    datas = daobase.executeUserCmd (userId, 'HGETALL', 'neo:%s:%s' % (HALL_GAMEID, userId))
    if datas:
        for i in xrange(len(datas) / 2):
            orderId = datas[i * 2]
            jstr = datas[i * 2 + 1]
            try:
                d = strutil.loads(jstr)
                order = ExchangeOrder(userId, orderId).fromDict(d)
                ret[orderId] = order
            except:
                ftlog.warn('hall_exmall.loadAllOrder BadOrder',
                           'userId=', userId,
                           'orderId=', orderId,
                           'jstr=', jstr)
    return ret


def payForOrder(order, userAssets, itemId, count):
    timestamp = pktimestamp.getCurrentTimestamp()
    order.cost = {'itemId':itemId, 'count':count}
    assetTuple = userAssets.consumeAsset(HALL_GAMEID,
                                         itemId,
                                         count,
                                         timestamp,
                                         'HALL_EXCHANGE_COST',
                                         int(order.exchangeId))

    if assetTuple[1] < count:
        ftlog.warn ('hall_exmall.payForOrder'
                    'gameId=', HALL_GAMEID,
                    'userId=', order.userId,
                    'orderId=', order.orderId,
                    'cost=', (itemId, count),
                    'consumedCount=', assetTuple[1],
                    'err=', 'CostNotEnough')

        raise ExchangeCostNotEnoughException()

    datachangenotify.sendDataChangeNotify(HALL_GAMEID, order.userId, TYAssetUtils.getChangeDataNames([assetTuple]))


def backCost(order, timestamp=None):
    if order.cost:
        changed = []
        timestamp = timestamp if timestamp is not None else pktimestamp.getCurrentTimestamp()
        userAssets = hallitem.itemSystem.loadUserAssets(order.userId)
        assetKind, _addCount, _final = userAssets.addAsset(HALL_GAMEID,
                                                           order.cost['itemId'],
                                                           order.cost['count'],
                                                           timestamp,
                                                           'HALL_EXCHANGE_COST_BACK',
                                                           int(order.exchangeId))
        if assetKind.keyForChangeNotify:
            changed.append(assetKind.keyForChangeNotify)
        datachangenotify.sendDataChangeNotify(HALL_GAMEID, order.userId, changed)


def handleExchangeAuditResult(userId, orderId, result):
    '''
    处理审核结果
    '''
    order = loadOrder(userId, orderId)
    if not order:
        raise UnknownExchangeOrderException()

    if order.state != ExchangeOrder.STATE_AUDIT:
        raise BadExchangeOrderStateException()

    if result not in (RESULT_AUDITSUCC, RESULT_REJECT, RESULT_REJECT_RETURN):
        raise TYBizException(-1, '错误的回调结果')
    
    if result == RESULT_AUDITSUCC:
        order.state = ExchangeOrder.STATE_AUDITSUCC
    elif result == RESULT_REJECT:
        order.state = ExchangeOrder.STATE_REJECT
    elif result == RESULT_REJECT_RETURN:
        order.state = ExchangeOrder.STATE_REJECT_RETURN
        backCost(order)
    
    saveOrder(order)
    
    ftlog.info('hall_exmall.handleExchangeAuditResult',
               'userId=', userId,
               'orderId=', orderId,
               'result=', result,
               'exchangeId=', order.exchangeId,
               'cost=', order.cost,
               'orderState=', order.state)
    
    return order


def handleShippingResult(userId, orderId, result, deliveryInfo=None):
    '''
    发货结果处理
    '''
    order = loadOrder(userId, orderId)
    if not order:
        raise UnknownExchangeOrderException()
    
    if order.state != ExchangeOrder.STATE_AUDITSUCC:
        raise BadExchangeOrderStateException()

    if result not in (RESULT_OK, RESULT_SHIPPINGFAIL, RESULT_SHIPPINGFAIL_RETURN):
        raise TYBizException (-1, '错误的回调结果')
    
    if result == RESULT_OK:
        order.state = ExchangeOrder.STATE_SHIPPING_SUCC
        order.deliveryInfo = deliveryInfo
    elif result == RESULT_SHIPPINGFAIL:
        order.state = ExchangeOrder.STATE_SHIPPING_FAIL
    elif result == RESULT_SHIPPINGFAIL_RETURN:
        order.state = ExchangeOrder.STATE_SHIPPING_FAIL_RETURN
        backCost(order)
    
    saveOrder(order)

    ftlog.info('hall_exmall.handleShippingResult',
               'userId=', userId,
               'orderId=', orderId,
               'result=', result,
               'deliveryInfo=', deliveryInfo,
               'exchangeId=', order.exchangeId,
               'cost=', order.cost,
               'orderState=', order.state)
    
    return order


def _lockStock(exchangeObj, count, timestamp):
    if not exchangeObj.stock:
        return True, timestamp
    
    try:
        ok, balance, stockTimestmap = stock_remote.lockStock(exchangeObj.exchangeId, count)
        if ftlog.is_debug():
            ftlog.debug('hall_exmall.lockStock',
                        'exchangeId=', exchangeObj.exchangeId,
                        'count=', count,
                        'timestamp=', timestamp,
                        'ok=', ok,
                        'balance=', balance,
                        'stockTimestamp=', stockTimestmap)
        if ok:
            return True, stockTimestmap
    except:
        ftlog.error('hall_exmall.lockStock',
                    'exchangeId=', exchangeObj.exchangeId,
                    'count=', count,
                    'timestamp=', timestamp)
    return False, None
    

def _unlockStock(exchangeObj, count, stockTimestamp):
    try:
        stock_remote.backStock(exchangeObj.exchangeId, count, stockTimestamp)
    except:
        ftlog.error('hall_exmall.unlockStock',
                    'exchangeId=', exchangeObj.exchangeId,
                    'count=', count,
                    'stockTimestamp=', stockTimestamp)


def getOrderTrackExchangeRecord(jdOrderId):
    from poker.util import webpage
    orderTrack = []
    orderUrl = getOrderTrackUrl()
    gdssUrl = orderUrl + jdOrderId
    hbody, _ = webpage.webgetGdss(gdssUrl, {})
    resJson = json.loads(hbody)
    _retmsg = resJson.get('retmsg', {})
    retcode = resJson.get('retcode', 0)
    if retcode == "0" or _retmsg == "no data":
        orderTrack = []
    else:
        orderTrack = _retmsg["orderTrack"]

    ftlog.debug('getExchangeRecord', '_retmsg=', _retmsg)

    return orderTrack




def doExchange(gameId, userId, clientId, exchangeId, count, exchangeParams, timestamp=None):
    '''
    @return: (stockNum)
    '''
    exchangeObj = findExchange(exchangeId)
    if not exchangeObj:
        raise TYBizException(-1, '没有找到要兑换的商品')

    timestamp = timestamp if timestamp is not None else pktimestamp.getCurrentTimestamp()

    if exchangeObj.exchangeCycle:
        tp = exchangeObj.exchangeCycle.nextCycleTimePeriod(timestamp)
        if not tp:
            if ftlog.is_debug():
                ftlog.debug('hall_exmall.doExchange',
                            'userId=', userId,
                            'exchangeId=', exchangeId,
                            'clientId=', clientId,
                            'exchangeParams=', exchangeParams,
                            'count=', count,
                            'timestamp=', timestamp,
                            'exchangeCycle=', str(exchangeObj.exchangeCycle),
                            'err=', 'NotInExchangeTimeCyle')
            raise NotInExchangeTimeCycleException()
    
    # 检查购买条件
    ok, condition = checkExchangeConditions(userId, exchangeObj, clientId, count, timestamp)
    if not ok:
        if ftlog.is_debug():
            ftlog.debug('hall_exmall.doExchange',
                        'userId=', userId,
                        'exchangeId=', exchangeId,
                        'clientId=', clientId,
                        'exchangeParams=', exchangeParams,
                        'count=', count,
                        'timestamp=', timestamp,
                        'condition=', condition,
                        'err=', 'CheckCondition')
        raise TYBizException(-1, condition.failure)

    # 检查兑换参数
    exchangeObj.delivery.checkParams(userId, exchangeObj, count, exchangeParams)

    # 检查个限
    ok, countLimitRecord = checkExchangeCountLimit(userId, exchangeObj, clientId, count, timestamp)
    if not ok:
        if ftlog.is_debug():
            ftlog.debug('hall_exmall.doExchange',
                        'userId=', userId,
                        'exchangeId=', exchangeId,
                        'clientId=', clientId,
                        'exchangeParams=', exchangeParams,
                        'count=', count,
                        'timestamp=', timestamp,
                        'limitRecord=', (countLimitRecord.lastExchangeTime, countLimitRecord.count),
                        'err=', 'OverLoad')
        raise TYBizException(-1, exchangeObj.exchangeCountLimit.failure)

    # 锁定库存
    ok, stockTimestamp = _lockStock(exchangeObj, count, timestamp)
    if not ok:
        if ftlog.is_debug():
            ftlog.debug('hall_exmall.doExchange',
                        'userId=', userId,
                        'exchangeId=', exchangeId,
                        'clientId=', clientId,
                        'exchangePamras=', exchangeParams,
                        'count=', count,
                        'timestamp=', timestamp,
                        'limitRecord=', (countLimitRecord.lastExchangeTime, countLimitRecord.count) if countLimitRecord else None,
                        'err=', 'NoStock')
        raise NotEnoughStockException()
    
    userAssets = hallitem.itemSystem.loadUserAssets(userId)
    
    totalCost = exchangeObj.cost.count * count
    
    if userAssets.balance(HALL_GAMEID, exchangeObj.cost.itemId, timestamp) < totalCost:
        if ftlog.is_debug():
            ftlog.debug('hall_exmall.doExchange',
                        'userId=', userId,
                        'exchangeId=', exchangeId,
                        'clientId=', clientId,
                        'exchangePamras=', exchangeParams,
                        'count=', count,
                        'timestamp=', timestamp,
                        'limitRecord=', (countLimitRecord.lastExchangeTime, countLimitRecord.count) if countLimitRecord else None,
                        'totalCost=', totalCost,
                        'err=', 'NotEnoughCost')
        raise ExchangeCostNotEnoughException()
    
    # 创建订单
    order = makeOrder(userId, exchangeObj, clientId, exchangeParams, count, timestamp)
    
    # 支付
    payForOrder(order, userAssets, exchangeObj.cost.itemId, totalCost)
    
    ftlog.info('hall_exmall.doExchange PaidOrder',
               'userId=', userId,
               'exchangeId=', exchangeId,
               'clientId=', clientId,
               'exchangePamras=', exchangeParams,
               'count=', count,
               'timestamp=', timestamp,
               'limitRecord=', (countLimitRecord.lastExchangeTime, countLimitRecord.count) if countLimitRecord else None,
               'totalCost=', totalCost,
               'orderId=', order.orderId)
    
    # 更新订单为已支付状态
    order.state = order.STATE_PAID
    saveOrder(order)

    #轮播LED仅保留最近10条兑换记录
    name = userdata.getAttr(userId,'name')
    doExchangeRecordKey = "exhall:recordLed"
    datas = {'name': name, 'displayName': exchangeObj.displayName, 'pic': exchangeObj.pic, 'exchangeTime': datetime.now().strftime("%H:%M")}
    ftlog.hinfo('hall_exmall.doExchange recordLED',
                'datas', datas)
    try:
        recordledLen = daobase.executeMixCmd('RPUSH', doExchangeRecordKey, json.dumps(datas))
        if recordledLen > 10:
            # 超过10个就截取后10个
            daobase.executeMixCmd('LTRIM', doExchangeRecordKey, -10, -1)
    except:
        ftlog.warn("redis rpush|ltrim exhall:recordLed error", gameId, userId, clientId, exchangeId, count, exchangeParams, datas)

    try:
        ret = exchangeObj.delivery.delivery(order)
        if ret == ExchangeDelivery.DELIVERIED:
            order.state = ExchangeOrder.STATE_SHIPPING_SUCC
        else:
            order.state = ExchangeOrder.STATE_AUDIT

        if countLimitRecord:
            countLimitRecord.count += count
            countLimitRecord.lastExchangeTime = timestamp
            saveExchangeCountLimitRecord(userId, exchangeId, countLimitRecord)
        
        saveOrder(order)
        ftlog.info('hall_exmall.doExchange OK',
                   'userId=', userId,
                   'exchangeId=', exchangeId,
                   'clientId=', clientId,
                   'exchangePamras=', exchangeParams,
                   'limitRecord=', (countLimitRecord.lastExchangeTime, countLimitRecord.count) if countLimitRecord else None,
                   'timestamp=', timestamp,
                   'orderId=', order.orderId,
                   'orderState=', order.state)
        
        if exchangeObj.mail:
            mail = strutil.replaceParams(exchangeObj.mail, {'displayName':exchangeObj.displayName})
            pkmessage.send(gameId, pkmessage.MESSAGE_TYPE_SYSTEM, userId, mail)
            datachangenotify.sendDataChangeNotify(gameId, userId, 'message')
        return order.orderId
    except:
        ftlog.error('hall_exmall.doExchange Exception',
                    'userId=', userId,
                    'exchangeId=', exchangeId,
                    'clientId=', clientId,
                    'exchangePamras=', exchangeParams,
                    'limitRecord=', (countLimitRecord.lastExchangeTime, countLimitRecord.count) if countLimitRecord else None,
                    'timestamp=', timestamp,
                    'orderId=', order.orderId,
                    'orderState=', order.state)
        _unlockStock(exchangeObj, count, stockTimestamp)
        # 返还费用
        order.state = order.STATE_FAIL
        order.errorCode = -1
        saveOrder(order)
        backCost(order)
        raise


def _getShelvesByNameFromTC(userId, clientId, name, tc, timestamp=None):
    timestamp = timestamp if timestamp is not None else pktimestamp.getCurrentTimestamp()
    for shelvesD in tc.get('shelves', []):
        if shelvesD.get('name') == name:
            return shelvesD
    return None


def getShelvesByName(userId, clientId, name, timestamp=None):
    tcName = configure.getVcTemplate('exmall', clientId)
    if ftlog.is_debug():
        ftlog.debug('hall_exmall.getShelvesByName',
                    'userId=', userId,
                    'clientId=', clientId,
                    'name=', name,
                    'tcName=', tcName)
    if tcName:
        tc = _templateMap.get(tcName)
        if tc:
            return _getShelvesByNameFromTC(userId, clientId, name, tc, timestamp)
    return None


def getShelvesByName1(userId, clientId, name, timestamp=None):
    gameId = strutil.getGameIdFromHallClientId(clientId)
    tc = configure.getTcContentByGameId('exmall', None, gameId, clientId, None)
    if tc:
        return _getShelvesByNameFromTC(userId, clientId, name, tc, timestamp)
    return None


def _getDisplayShelvesByNameFromTC(userId, clientId, name, tc, timestamp=None):
    timestamp = timestamp if timestamp is not None else pktimestamp.getCurrentTimestamp()
    for shelvesD in tc.get('shelves', []):
        if shelvesD.get('name') != name:
            continue
        
        if not shelvesD.get('visible', 1):
            if ftlog.is_debug():
                ftlog.debug('hall_exmall._getDisplayShelvesByNameFromTC NotVisible',
                            'userId=', userId,
                            'clientId=', clientId,
                            'timestmap=', timestamp,
                            'shelvesName=', shelvesD.get('name'))
            return None
        
        # 检查条件
        visibleCond = shelvesD.get('visibleCondition')
        if visibleCond:
            cond = UserConditionRegister.decodeFromDict(visibleCond)
            if not cond.check(HALL_GAMEID, userId, clientId, timestamp):
                if ftlog.is_debug():
                    ftlog.debug('hall_exmall._getDisplayShelvesByNameFromTC NotConformVisibleCondition',
                                'userId=', userId,
                                'clientId=', clientId,
                                'timestmap=', timestamp,
                                'shelvesName=', shelvesD.get('name'),
                                'condition=', visibleCond)
                return None
            
        return shelvesD
        
    return None


def getDisplayShelvesByName(userId, clientId, name, timestamp=None):
    tcName = configure.getVcTemplate('exmall', clientId)
    if ftlog.is_debug():
        ftlog.debug('hall_exmall.getDisplayShelvesByName',
                    'userId=', userId,
                    'clientId=', clientId,
                    'name=', name,
                    'tcName=', tcName)
    if tcName:
        tc = _templateMap.get(tcName)
        if tc:
            return _getDisplayShelvesByNameFromTC(userId, clientId, name, tc, timestamp)
    return None


def getDisplayShelvesByName1(userId, clientId, name, timestamp=None):
    gameId = strutil.getGameIdFromHallClientId(clientId)
    tc = configure.getTcContentByGameId('exmall', None, gameId, clientId, None)
    if tc:
        return _getDisplayShelvesByNameFromTC(userId, clientId, name, tc, timestamp)

    return None


def _getShelvesListFormTC(userId, clientId, tc, timestamp=None):
    ret = []
    timestamp = timestamp if timestamp is not None else pktimestamp.getCurrentTimestamp()
    for shelvesD in tc.get('shelves', []):
        if not shelvesD.get('visible', 1):
            if ftlog.is_debug():
                ftlog.debug('hall_exmall._getShelvesListFormTC NotVisible',
                            'userId=', userId,
                            'clientId=', clientId,
                            'timestmap=', timestamp,
                            'shelvesName=', shelvesD.get('name'))
            continue
        
        # 检查条件
        visibleCond = shelvesD.get('visibleCondition')
        if visibleCond:
            cond = UserConditionRegister.decodeFromDict(visibleCond)
            if not cond.check(HALL_GAMEID, userId, clientId, timestamp):
                if ftlog.is_debug():
                    ftlog.debug('hall_exmall._getShelvesListFormTC NotConformVisibleCondition',
                                'userId=', userId,
                                'clientId=', clientId,
                                'timestmap=', timestamp,
                                'shelvesName=', shelvesD.get('name'),
                                'condition=', visibleCond)
                continue
        
        ret.append(shelvesD)
            
    ret.sort(key=lambda s: s.get('sort', 0))
    
    return ret


def getShelvesList(userId, clientId, timestamp=None):
    tcName = configure.getVcTemplate('exmall', clientId)
    if ftlog.is_debug():
        ftlog.debug('hall_exmall.getShelvesList',
                    'userId=', userId,
                    'clientId=', clientId,
                    'tcName=', tcName)
    if tcName:
        tc = _templateMap.get(tcName)
        if tc:
            return _getShelvesListFormTC(userId, clientId, tc, timestamp)
    return []


def getShelvesList1(userId, clientId, timestamp=None):
    gameId = strutil.getGameIdFromHallClientId(clientId)
    tc = configure.getTcContentByGameId('exmall', None, gameId, clientId, None)
    if tc:
        return _getShelvesListFormTC(userId, clientId, tc, timestamp)
    return []


#################################################################################

def canDisplayExchange(userId, clientId, exchangeObj, timestamp):
    if exchangeObj.displayCycle:
        tp = exchangeObj.displayCycle.nextCycleTimePeriod(timestamp)
        if not tp:
            if ftlog.is_debug():
                ftlog.debug('HallExMallHandler.canDisplayExchange NotInDisplayCycle',
                            'userId=', userId,
                            'clientId=', clientId,
                            'exchangeId=', exchangeObj.exchangeId,
                            'timestamp=', timestamp,
                            'displayCycle=', str(exchangeObj.displayCycle))
            return False
        
        if ftlog.is_debug():
            ftlog.debug('HallExMallHandler.canDisplayExchange InDisplayCycle',
                        'userId=', userId,
                        'clientId=', clientId,
                        'exchangeId=', exchangeObj.exchangeId,
                        'timestamp=', timestamp,
                        'displayCycle=', str(exchangeObj.displayCycle),
                        'tp=', (tp.startDT, tp.stopDT))
    
    ok, cond = checkExchangeConditions(userId, exchangeObj, clientId, 1, timestamp)
    if not ok and not cond.visibleInStore:
        if ftlog.is_debug():
            ftlog.debug('HallExMallHandler.canDisplayExchange CheckCond',
                        'userId=', userId,
                        'clientId=', clientId,
                        'exchangeId=', exchangeObj.exchangeId,
                        'timestamp=', timestamp,
                        'cond=', cond.failure)
        return False
    
    ok, countLimitRecord = checkExchangeCountLimit(userId, exchangeObj, clientId, 1, timestamp)
    
    if not ok and not exchangeObj.exchangeCountLimit.visibleInStore:
        if ftlog.is_debug():
            ftlog.debug('HallExMallHandler.canDisplayExchange CheckCond',
                        'userId=', userId,
                        'clientId=', clientId,
                        'exchangeId=', exchangeObj.exchangeId,
                        'timestamp=', timestamp,
                        'limitRecord=', (countLimitRecord.lastExchangeTime, countLimitRecord.count))
        return False
    
    return True


def loadStockObj(exchangeId):
    jstr = None
    try:
        jstr = daobase.executeMixCmd ('hget', 'exhall:stock', exchangeId)
        if jstr:
            d = strutil.loads(jstr)
            return ExchangeStock().fromDict(d)
    except:
        ftlog.warn('hall_exmall.loadStockObj',
                   'exchangeId=', exchangeId,
                   'jstr=', jstr)
    
    return ExchangeStock()


def saveStockObj(exchangeId, stockObj):
    d = stockObj.toDict()
    jstr = strutil.dumps(d)
    daobase.executeMixCmd ('hset', 'exhall:stock', exchangeId, jstr)
    ftlog.debug('hall_exmall.saveStockObj',
                'exchangeId=', exchangeId,
                'jstr=', jstr)


def removeStockObj(exchangeId):
    ftlog.info('hall_exmall.removeStockObj',
               'exchangeId=', exchangeId)
    daobase.executeMixCmd('hdel', 'exhall:stock', exchangeId)
    

def loadAllStockObj():
    ret = {}
    datas = daobase.executeMixCmd('hgetall', 'exhall:stock')
    if datas:
        for i in xrange(len(datas) / 2):
            exchangeId = str(datas[i * 2])
            jstr = datas[i * 2 + 1]
            try:
                d = strutil.loads(jstr)
                stockObj = ExchangeStock().fromDict(d)
                ret[exchangeId] = stockObj
            except:
                ftlog.warn('hall_exmall.loadStockObj',
                           'exchangeId=', exchangeId,
                           'jstr=', jstr)
    return ret


def _refrushStocks(timestamp=None):
    '''
    刷新库存
    '''
    timestamp = timestamp if timestamp is not None else pktimestamp.getCurrentTimestamp()
    
    stockObjMap = loadAllStockObj()
    
    ftlog.info('hall_exmall._refrushStocks',
               'timestamp=', timestamp,
               'stocks=', stockObjMap.keys())
    
    for exchangeId, stockObj in stockObjMap.iteritems():
        exchangeObj = findExchange(exchangeId)
        if not exchangeObj or not exchangeObj.stock:
            ftlog.info('hall_exmall._refrushStocks removeStockObjNoConf',
                       'timestamp=', timestamp,
                       'stockObj=', (stockObj.stock, stockObj.lastUpdateTime, stockObj.checksum))
            removeStockObj(exchangeId)
            continue
        
        checksum = exchangeObj.stock.timeCycle.calcChecksum()
        if checksum != stockObj.checksum:
            ftlog.info('hall_exmall._refrushStocks removeStockObjDiffChecksum',
                       'timestamp=', timestamp,
                       'stockObj=', (stockObj.stock, stockObj.lastUpdateTime, stockObj.checksum),
                       'confChecksum=', checksum)
            removeStockObj(exchangeId)
            continue


def queryStock(exchangeId):
    exchangeObj = findExchange(exchangeId)
    if not exchangeObj:
        raise UnknownExchangeException()
    
    if not exchangeObj.stock:
        return -1

    try:    
        return stock_remote.getStock(exchangeId)
    except:
        ftlog.error('hall_exmall.queryStock',
                    'exchangeId=', exchangeId)
        raise
    

def getStock(exchangeId, timestamp):
    exchangeObj = findExchange(exchangeId)
    if not exchangeObj:
        raise UnknownExchangeException()
    
    if not exchangeObj.stock:
        if ftlog.is_debug():
            ftlog.debug('hall_exmall.getStock NoStockConf',
                        'exchangeId=', exchangeId,
                        'timestamp=', timestamp)
        return -1
    
    stockObj = loadStockObj(exchangeObj.exchangeId)
    if ftlog.is_debug():
        ftlog.debug('hall_exmall.getStock beforeAdjust',
                    'exchangeId=', exchangeId,
                    'timestamp=', timestamp,
                    'stock=', (stockObj.stock, stockObj.lastUpdateTime, stockObj.checksum))
        
    exchangeObj.stock.adjustStock(stockObj, timestamp)
    
    if ftlog.is_debug():
        ftlog.debug('hall_exmall.getStock afterAdjust',
                    'exchangeId=', exchangeId,
                    'timestamp=', timestamp,
                    'stock=', (stockObj.stock, stockObj.lastUpdateTime, stockObj.checksum))

    return stockObj


def lockStock(exchangeId, count, timestamp):
    exchangeObj = findExchange(exchangeId)
    if not exchangeObj:
        raise UnknownExchangeException()

    if not exchangeObj.stock:
        if ftlog.is_debug():
            ftlog.debug('hall_exmall.lockStock NoStockConf',
                        'exchangeId=', exchangeId,
                        'count=', count,
                        'timestamp=', timestamp)
        return count, -1
    
    stockObj = loadStockObj(exchangeId)
    if ftlog.is_debug():
        ftlog.debug('hall_exmall.lockStock beforeAdjust',
                    'exchangeId=', exchangeId,
                    'count=', count,
                    'timestamp=', timestamp,
                    'stock=', (stockObj.stock, stockObj.lastUpdateTime, stockObj.checksum))
        
    exchangeObj.stock.adjustStock(stockObj, timestamp)

    if ftlog.is_debug():
        ftlog.debug('hall_exmall.lockStock afterAdjust',
                    'exchangeId=', exchangeId,
                    'count=', count,
                    'timestamp=', timestamp,
                    'stock=', (stockObj.stock, stockObj.lastUpdateTime, stockObj.checksum))
        
    if stockObj.stock < count:  # 检查库存
        raise NotEnoughStockException()

    stockObj.stock -= count  # 扣除库存
    stockObj.lastUpdateTime = timestamp
    saveStockObj(exchangeId, stockObj)

    ftlog.info('hall_exmall.lockStock ok',
               'exchangeId=', exchangeId,
               'count=', count,
               'timestamp=', timestamp,
               'stock=', stockObj.stock)
    return count, stockObj.stock


def backStock(exchangeId, count, stockTimestamp, timestamp):
    exchangeObj = findExchange(exchangeId)
    if not exchangeObj:
        raise UnknownExchangeException()

    if not exchangeObj.stock:
        if ftlog.is_debug():
            ftlog.debug('hall_exmall.backStock NoStockConf',
                        'exchangeId=', exchangeId,
                        'count=', count,
                        'stockTimestamp=', stockTimestamp,
                        'timestamp=', timestamp)
        return
    
    # 加载库存信息
    stockObj = loadStockObj(exchangeId)
    if not stockObj:
        if ftlog.is_debug():
            ftlog.debug('hall_exmall.backStock NoStockObj',
                        'exchangeId=', exchangeId,
                        'count=', count,
                        'stockTimestamp=', stockTimestamp,
                        'timestamp=', timestamp)
        return

    exchangeObj.stock.adjustStock(stockObj, timestamp)
    
    if exchangeObj.stock.timeCycle.calcIssueNum(stockTimestamp) != exchangeObj.stock.timeCycle.calcIssueNum(timestamp):
        # 周期已过，不返还
        if ftlog.is_debug():
            ftlog.debug('hall_exmall.backStock DiffCycle',
                        'exchangeId=', exchangeId,
                        'count=', count,
                        'stockTimestamp=', stockTimestamp,
                        'timestamp=', timestamp,
                        'stock=', stockObj.stock)
        return

    # 返还库存
    stockObj.stock += count
    stockObj.lastUpdateTime = stockTimestamp
    saveStockObj(exchangeId, stockObj)

    ftlog.info('hall_exmall.backStock OK',
               'exchangeId=', exchangeId,
               'count=', count,
               'timestamp=', timestamp,
               'stock=', stockObj.stock)
    

def _reloadConf():
    global _exchangeMap
    global _templateMap
    global _exchangeGdssUrl
    global _orderTrackUrl
    global _orderStateTip

    conf = configure.getGameJson(HALL_GAMEID, 'exmall', {}, configure.DEFAULT_CLIENT_ID)
    exchangeMap = {}
    
    for exchangeD in conf.get('exchanges', []):
        exchange = Exchange().decodeFromDict(exchangeD)
        if exchange.exchangeId in exchangeMap:
            raise TYBizConfException(exchangeD, 'Duplicated exchangeId: %s' % (exchange.exchangeId))
        
        exchangeMap[exchange.exchangeId] = exchange
    
    allTemplates = hallconf.getAllTcDatas('exmall')
    
    _templateMap = allTemplates.get('templates', {})
    _exchangeMap = exchangeMap
    _exchangeGdssUrl = conf.get('exchangeGdssUrl','http://gdss.touch4.me/?act=api.propExchange')
    _orderTrackUrl = conf.get('orderTrackUrl','http://gdss.touch4.me/?act=api.getJdOrderTrack&jdOrderId=')
    _orderStateTip = conf.get('exchangeStateTip',{
        'default':"审核当中",
        'state2Tip':"审核发货中",
        'state3Tip':"审核成功",
        'state4Tip':"您的兑换审核失败,奖券不返还,如有问题,请联系客服电话或QQ:4008098000",
        'state5Tip':"可能因为库存不足,兑换失败,奖券已退回,请选择其他商品进行兑换",
        'state6Tip':"兑换成功",
        'state7Tip':"发货失败,请联系客服电话或QQ:4008098000",
        'state8Tip':"发货失败,奖券已退回,请联系客服电话或QQ:4008098000"
    })

    ftlog.info('hall_exmall._reloadConf ok',
               'exchangeIds=', _exchangeMap.keys(),
               'exchangeGdssUrl=', _exchangeGdssUrl,
               'orderTrackUrl=', _orderTrackUrl,
               'orderStateTip', _orderStateTip,
               'templates=', _templateMap.keys())

    serverType = gdata.serverType()
    if serverType == gdata.SRV_TYPE_CENTER:
        _refrushStocks()


def _onConfChanged(event):
    if _inited and event.isChanged(['game:9999:exmall:0', 'game:9999:exmall:tc']):
        _reloadConf()


def _initialize():
    global _inited
    if not _inited:
        _inited = True
        _reloadConf()
        pkeventbus.globalEventBus.subscribe(EventConfigure, _onConfChanged)


