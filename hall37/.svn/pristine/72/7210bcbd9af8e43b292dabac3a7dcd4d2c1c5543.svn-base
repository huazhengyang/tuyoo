# -*- coding:utf-8 -*-
'''
Created on 2016年3月7日

@author: zhaojiangang
'''
from datetime import datetime
from sre_compile import isstring

import freetime.util.log as ftlog
from hall.entity import hallconf
from poker.entity.biz.exceptions import TYBizException, TYBizConfException
from poker.entity.dao import daobase
from poker.entity.events.tyevent import EventConfigure
import poker.entity.events.tyeventbus as pkeventbus
import poker.util.timestamp as pktimestamp


EC_STOCK_PARAM_ERROR = -1
EC_STOCK_LESS_ERROR = -2

EC_STR_MAP = {
    EC_STOCK_PARAM_ERROR:'参数错误',
    EC_STOCK_LESS_ERROR:'库存不足'
}

EC_STR_UNKNOWN = '未知错误'

class StockException(TYBizException):
    def __init__(self, ec, message=None):
        super(StockException, self).__init__(ec, message or EC_STR_MAP.get(ec, EC_STR_UNKNOWN))

class Stock(object):
    def __init__(self, stockId, remCount):
        self._stockId = stockId
        self._remCount = remCount
    
    @property
    def remCount(self):
        return self._remCount

class StockDao(object):
    def loadStock(self, stockId):
        raise NotImplementedError
    
    def inStock(self, stockId, count):
        raise NotImplementedError
    
    def outStock(self, stockId, count):
        raise NotImplementedError
    
class StockDaoRedis(object):
    _REDIS_LUA_STOCK_COMMON = '''
    local function get_rem_count(key, stockId)
        local rem = redis.call('hget', key, stockId)
        if rem then
            return tonumber(rem)
        end
        return -1
    end
    '''
    
    _REDIS_LUA_IN_STOCK_NAME = 'hall_in_stock'
    _REDIS_LUA_IN_STOCK_SCRIPT = _REDIS_LUA_STOCK_COMMON + '''
    local key = KEYS[1]
    local stockId = KEYS[2]
    local count = tonumber(KEYS[3])
    local rem = get_rem_count(key, stockId)
    if count <= 0 then
        return {-1, rem}
    end
    if rem < 0 then
        rem = count
    else
        rem = rem + count
    end
    return {0, redis.call('hset', key, stockId, rem)}
    '''
    
    _REDIS_LUA_OUT_STOCK_NAME = 'hall_out_stock'
    _REDIS_LUA_OUT_STOCK_SCRIPT = _REDIS_LUA_STOCK_COMMON + '''
    local key = KEYS[1]
    local stockId = KEYS[2]
    local count = tonumber(KEYS[3])
    local rem = get_rem_count(key, stockId)
    if count <= 0 then
        return {-1, rem}
    end
    if rem < 0 then
        return {0, rem}
    end
    if rem < count then
        return {-2, rem}
    end
    rem = rem - count
    return {0, redis.call('hset', key, stockId, rem)}
    '''
    
    def __init__(self, namespace):
        self._key = 'stock:%s' % (namespace)
        daobase.loadLuaScripts(self._REDIS_LUA_IN_STOCK_NAME, self._REDIS_LUA_IN_STOCK_SCRIPT)
        daobase.loadLuaScripts(self._REDIS_LUA_OUT_STOCK_NAME, self._REDIS_LUA_OUT_STOCK_SCRIPT)
        
    def loadStock(self, stockId):
        count = daobase.executeMixCmd('hget', self._key, stockId)
        if count is None:
            return -1
        return int(count)
        
    def setStock(self, stockId, count):
        assert(count >= -1)
        return daobase.executeMixCmd('hset', self._key, stockId, count)
        
    def inStock(self, stockId, count):
        assert(count > 0)
        return daobase.executeMixLua(self._REDIS_LUA_IN_STOCK_NAME, 3, self._key, stockId, count)
    
    def outStock(self, stockId, count):
        assert(count > 0)
        return daobase.executeMixLua(self._REDIS_LUA_OUT_STOCK_NAME, 3, self._key, stockId, count)
    
class StockSystem(object):
    def __init__(self, dao):
        self._dao = dao
    
    def loadStock(self, stockId):
        '''
        根据stockId查找库存
        @return: None or Stock
        '''
        return self._dao.loadStock(stockId)

    def setStock(self, stockId, count):
        '''
        根据stockId设置库存
        '''
        return self._dao.setStock(stockId, count)
    
    def inStock(self, stockId, count):
        '''
        根据sotckId锁定count个库存，如果库存不够则抛出异常
        @return: 库存数量
        '''
        ec, rem = self._dao.inStock(stockId, count)
        if ftlog.is_debug():
            ftlog.debug('StockSystem.inStock stockId=', stockId,
                        'count=', count,
                        'ec=', ec,
                        'rem=', rem)
        if ec != 0:
            raise StockException(ec)
        return rem
    
    def outStock(self, stockId, count):
        '''
        根据sotckId解锁count个库存
        @return: 库存数量
        '''
        ec, rem = self._dao.outStock(stockId, count)
        if ftlog.is_debug():
            ftlog.debug('StockSystem.outStock stockId=', stockId,
                        'count=', count,
                        'ec=', ec,
                        'rem=', rem)
        if ec != 0:
            raise StockException(ec)
        return rem

class TimePeriodLimit(object):
    timeZero = datetime.strptime('00:00', '%H:%M').time()
    
    def __init__(self):
        self.periodId = None
        self.count = None
        self.periods = None
        self.failure = None
        
    def buildDatePeriodId(self, timestamp=None):
        timestamp = timestamp or pktimestamp.getCurrentTimestamp()
        nowDate = datetime.fromtimestamp(timestamp).date()
        return '%s.%s' % (nowDate.strftime('%Y%m%d'), self.periodId)
        
    def isTimeIn(self, timestamp=None):
        timestamp = timestamp or pktimestamp.getCurrentTimestamp()
        nowT = datetime.fromtimestamp(timestamp).time()
        for period in self.periods:
            if ((period[0] is None or nowT >= period[0])
                and (period[1] is None or nowT < period[1])):
                if ftlog.is_debug():
                    ftlog.debug('TimePeriodLimit.check nowT=', nowT,
                                'periodId=', self.periodId,
                                'inPeriod=', True)
                return True
        return False
    
    def decodeFromDict(self, d):
        startTimeStr = d.get('startTime')
        endTimeStr = d.get('endTime')
        self.periods = []
        s = datetime.strptime(d.get('startTime'), '%H:%M').time()
        e = datetime.strptime(d.get('endTime'), '%H:%M').time()
        self.periodId = '%s-%s' % (startTimeStr, endTimeStr)
        s = s if s != self.timeZero else None
        e = e if e != self.timeZero else None
        if s != e:
            if (s is None or e is None) or (s < e):
                self.periods.append((s, e))
            elif s > e:
                self.periods.append((s, None))
                self.periods.append((None, e))
        self.count = d.get('count')
        if not isinstance(self.count, int) or self.count < -1:
            raise TYBizConfException(d, 'TimePeriodLimit.count must be int >= -1')
        
        self.failure = d.get('failure', '')
        if not isstring(self.failure) or not self.failure:
            raise TYBizConfException(d, 'TimePeriodLimit.failure must be not empty string')
        return self
    
class BuyCountLimit(object):
    def __init__(self):
        # 限购开始时间
        self.startDT = None
        # 限购结束时间
        self.endDT = None
        # 限购时间段
        self.periodLimitList = []
        # key=limitId, value=TimePeriodLimit
        self.periodLimitMap = {}
        # 不在时间段错误描述
        self.outTimeFailure = ''
        
    def findPeriodLimit(self, timestamp):
        for peroidLimit in self.periodLimitList:
            if peroidLimit.isTimeIn(timestamp):
                return peroidLimit
        return None
    
    def decodeFromDict(self, d):
        startTimeStr = d.get('startTime')
        endTimeStr = d.get('endTime')
        if startTimeStr:
            self.startDT = datetime.strptime(startTimeStr, '%Y-%m-%d %H:%M:%S').timetuple()
        if endTimeStr:
            self.endDT = datetime.strptime(endTimeStr, '%Y-%m-%d %H:%M:%S').timetuple()
            
        if self.endDT and self.startDT and self.endDT < self.startDT:
            raise TYBizConfException(d, 'BuyCountLimit.endTime must >= BuyCountLimit.startTime')
        
        periods = d.get('periods', [])
        if not periods:
            raise TYBizConfException(d, 'BuyCountLimit.periods must not empty list')
        
        for period in periods:
            limit = TimePeriodLimit().decodeFromDict(period)
            if limit.periodId in self.periodLimitMap:
                raise TYBizConfException(d, 'Duplicate BuyCountLimit period %s' % (limit.periodId))
            self.periodLimitList.append(limit)
            self.periodLimitMap[limit.periodId] = limit
            
        self.outTimeFailure = d.get('outTimeFailure', '')
        if not isstring(self.outTimeFailure) or not self.outTimeFailure:
            raise TYBizConfException(d, 'BuyCountLimit.outTimeFailure must be not empty string')
        return self

class PeriodLimitDao(object):
    def lockProductForPeriodLimit(self, periodId, productId, count):
        raise NotImplementedError
    
    def unlockProductForPeriodLimit(self, periodId, productId, count):
        raise NotImplementedError
    
    def deliveryProductForPeriodLimit(self, periodId, productId, count):
        raise NotImplementedError
    
class PeriodLimitDaoRedis(PeriodLimitDao):
    _REDIS_LUA_PERIOD_LIMIT_LOCK_NAME = 'hall_period_limit_lock'
    _REDIS_LUA_PERIOD_LIMIT_LOCK_SCRIPT = '''
    local key = KEYS[1]
    local periodId = KEYS[2]
    local count = tonumber(KEYS[3])
    local limitCount = tonumber(KEYS[4])
    local ts = tonumber(KEYS[5])
    local jstr = redis.call('hget', key, periodId)
    local limit = nil
    if jstr then
        limit = cjson.decode(jstr)
    else
        limit = {}
        limit['lc'] = 0
        limit['dc'] = 0
        limit['ut'] = ts
    end
    if limit['lc'] + limit['dc'] + count > limitCount then
        return {-2, {limit['lc'], limit['dc'], limit['ut']}}
    end
    limit['lc'] = limit['lc'] + count
    limit['ut'] = ts
    
    jstr = cjson.encode(limit)
    redis.call('hset', key, periodId, jstr)
    return {0, {limit['lc'], limit['dc'], limit['ut']}}
    '''
    
    _REDIS_LUA_PERIOD_LIMIT_UNLOCK_NAME = 'hall_period_limit_unlock'
    _REDIS_LUA_PERIOD_LIMIT_UNLOCK_SCRIPT = '''
    local key = KEYS[1]
    local periodId = KEYS[2]
    local count = tonumber(KEYS[3])
    local ts = tonumber(KEYS[4])
    local jstr = redis.call('hget', key, periodId)
    local limit = nil
    if jstr then
        limit = cjson.decode(jstr)
    else
        limit = {}
        limit['lc'] = 0
        limit['dc'] = 0
        limit['ut'] = ts
    end
    if limit['lc'] < count then
        return {-2, {limit['lc'], limit['dc'], limit['ut']}}
    end
    limit['lc'] = limit['lc'] - count
    limit['ut'] = ts
    
    jstr = cjson.encode(limit)
    redis.call('hset', key, periodId, jstr)
    return {0, {limit['lc'], limit['dc'], limit['ut']}}
    '''
    
    _REDIS_LUA_PERIOD_LIMIT_DELIVERY_NAME = 'hall_period_limit_delivery'
    _REDIS_LUA_PERIOD_LIMIT_DELIVERY_SCRIPT = '''
    local key = KEYS[1]
    local periodId = KEYS[2]
    local count = tonumber(KEYS[3])
    local ts = tonumber(KEYS[4])
    local jstr = redis.call('hget', key, periodId)
    local limit = nil
    if jstr then
        limit = cjson.decode(jstr)
    else
        limit = {}
        limit['lc'] = 0
        limit['dc'] = 0
        limit['ut'] = ts
    end
    if limit['lc'] < count then
        return {-2, {limit['lc'], limit['dc'], limit['ut']}}
    end
    limit['lc'] = limit['lc'] - count
    limit['dc'] = limit['dc'] + count
    limit['ut'] = ts
    jstr = cjson.encode(limit)
    redis.call('hset', key, periodId, jstr)
    return {0, {limit['lc'], limit['dc'], limit['ut']}}
    '''
    
    def __init__(self):
        daobase.loadLuaScripts(self._REDIS_LUA_PERIOD_LIMIT_LOCK_NAME, self._REDIS_LUA_PERIOD_LIMIT_LOCK_SCRIPT)
        daobase.loadLuaScripts(self._REDIS_LUA_PERIOD_LIMIT_UNLOCK_NAME, self._REDIS_LUA_PERIOD_LIMIT_UNLOCK_SCRIPT)
        daobase.loadLuaScripts(self._REDIS_LUA_PERIOD_LIMIT_DELIVERY_NAME, self._REDIS_LUA_PERIOD_LIMIT_DELIVERY_SCRIPT)
        
    @classmethod
    def buildKey(cls, productId):
        return 'store:periodLimit:%s' % (productId)
    
    def lockProductForPeriodLimit(self, periodId, productId, count, limitCount, timestamp):
        return daobase.executeMixLua(self._REDIS_LUA_PERIOD_LIMIT_LOCK_NAME, 5, self.buildKey(productId), periodId, count, limitCount, timestamp)
    
    def unlockProductForPeriodLimit(self, periodId, productId, count, timestamp):
        return daobase.executeMixLua(self._REDIS_LUA_PERIOD_LIMIT_UNLOCK_NAME, 4, self.buildKey(productId), periodId, count, timestamp)
    
    def deliveryProductForPeriodLimit(self, periodId, productId, count, timestamp):
        return daobase.executeMixLua(self._REDIS_LUA_PERIOD_LIMIT_DELIVERY_NAME, 4, self.buildKey(productId), periodId, count, timestamp)
    
class PeriodLimitSystem(object):
    def __init__(self, stockSystem, periodLimitDao):
        self.stockSystem = stockSystem
        self.periodLimitDao = periodLimitDao
        self._buyCountLimitMap = {}
        self._outStockFailure = ''
        
    def findBuyCountLimit(self, productId):
        return self._buyCountLimitMap.get(productId)
    
    def lockProduct(self, gameId, userId, productId, count, timestamp):
        # 出库count个商品
        try:
            self.stockSystem.outStock(productId, count)
        except:
            ftlog.error('PeriodLimitSystem.lockProduct outStockFail gameId=', gameId,
                        'userId=', userId,
                        'productId=', productId,
                        'count=', count,
                        'err=', 'OutStock')
            raise TYBizException(-1, self._outStockFailure)
        
        # 如果该商品没有限购，则返回
        buyCountLimit = self.findBuyCountLimit(productId)
        if not buyCountLimit:
            ftlog.debug('PeriodLimitSystem.lockProduct ok gameId=', gameId,
                       'userId=', userId,
                       'productId=', productId,
                       'count=', count,
                       'periodId=', None)
            return None
        
        # 查找限购时间段
        periodLimit = buyCountLimit.findPeriodLimit(timestamp)
        if not periodLimit:
            # 归回库存
            ftlog.debug('PeriodLimitSystem.lockProduct fail gameId=', gameId,
                       'userId=', userId,
                       'productId=', productId,
                       'count=', count,
                       'err=', 'NotInPeriod')
            self.stockSystem.inStock(productId, count)
            raise TYBizException(-1, buyCountLimit.outTimeFailure)
        
        # 在这个时间段内锁定count个商品，锁定失败要入库count个商品
        try:
            periodId = periodLimit.buildDatePeriodId()
            ec, limitRecord = self.periodLimitDao.lockProductForPeriodLimit(periodId, productId, count, periodLimit.count, timestamp)
            if ec != 0:
                ftlog.debug('PeriodLimitSystem.lockProduct fail gameId=', gameId,
                           'userId=', userId,
                           'productId=', productId,
                           'count=', count,
                           'ec=', ec,
                           'limitRecord=', limitRecord,
                           'limitCount=', periodLimit.count,
                           'err=', 'LimitPeriod')
                raise TYBizException(-1, periodLimit.failure)
            # 返回限购的periodId
            return periodId
        except:
            self.stockSystem.inStock(productId, count)
            raise

    def unlockProduct(self, gameId, userId, periodId, productId, count, reason, timestamp):
        ec, limitRecord = self.periodLimitDao.unlockProductForPeriodLimit(periodId, productId, count, timestamp)
        if ec != 0:
            # 此处忽略错误
            ftlog.debug('PeriodLimitSystem.unlockProduct fail gameId=', gameId,
                       'userId=', userId,
                       'productId=', productId,
                       'count=', count,
                       'ec=', ec,
                       'limitRecord=', limitRecord,
                       'err=', 'LimitPeriod')
            return
        
        # 入库
        self.stockSystem.inStock(productId, count)
        ftlog.debug('PeriodLimitSystem.unlockProduct ok gameId=', gameId,
                   'userId=', userId,
                   'productId=', productId,
                   'count=', count,
                   'limitRecord=', limitRecord)
        
    def deliveryProduct(self, gameId, userId, periodId, productId, count, timestamp):
        ec, limitRecord = self.periodLimitDao.deliveryProductForPeriodLimit(periodId, productId, count, timestamp)
        if ec != 0:
            # 此处忽略错误
            ftlog.debug('PeriodLimitSystem.deliveryProduct fail gameId=', gameId,
                       'userId=', userId,
                       'productId=', productId,
                       'count=', count,
                       'ec=', ec,
                       'limitRecord=', limitRecord,
                       'err=', 'LimitPeriod')
            return
        
        ftlog.debug('PeriodLimitSystem.deliveryProduct ok gameId=', gameId,
                   'userId=', userId,
                   'productId=', productId,
                   'count=', count,
                   'limitRecord=', limitRecord)
    
    def reloadConf(self, conf):
        buyCountLimitMap = {}
        if not conf:
            return
        
        for productId, limitConf in conf.get('limits', {}).iteritems():
            buyCountLimit = BuyCountLimit().decodeFromDict(limitConf)
            buyCountLimitMap[productId] = buyCountLimit
        
        outStockFailure = conf.get('outStockFailure')
        if not isstring(outStockFailure) or not outStockFailure:
            raise TYBizConfException(conf, 'hallstocklimit.outStockFailure must be not empty string')

        self._outStockFailure = outStockFailure
        self._buyCountLimitMap = buyCountLimitMap
        ftlog.debug('PeriodLimitSystem.reloadConf successed',
                   'productIds=', self._buyCountLimitMap.keys())
        
_inited = False
stockSystem = StockSystem(None)
productBuyLimitSystem = PeriodLimitSystem(None, None)

def _reloadConf():
    if _inited:
        ftlog.debug('hallstocklimit._reloadConf')
        conf = hallconf.getStoreBuyLimitConf()
        productBuyLimitSystem.reloadConf(conf)
    
def _onConfChanged(event):
    if ftlog.is_debug():
        ftlog.debug('hallstocklimit._onConfChanged',
                    'keylist=', event.keylist,
                    'reloadlist=', event.reloadlist)
        
    if _inited and event.isChanged('game:9999:store.buylimit:0'):
        ftlog.debug('hallstocklimit._onConfChanged')
        _reloadConf()
        
def _initialize():
    ftlog.debug('hallstocklimit initialize begin')
    global _inited
    global stockSystem
    global productBuyLimitSystem
    if not _inited:
        _inited = True
        stockSystem = StockSystem(StockDaoRedis('store'))
        productBuyLimitSystem = PeriodLimitSystem(stockSystem, PeriodLimitDaoRedis())
        _reloadConf()
        pkeventbus.globalEventBus.subscribe(EventConfigure, _onConfChanged)
    ftlog.debug('hallstocklimit initialize end')


