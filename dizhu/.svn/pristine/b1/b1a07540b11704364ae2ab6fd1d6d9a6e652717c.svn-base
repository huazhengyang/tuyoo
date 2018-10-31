# -*- coding=utf-8 -*-

from datetime import datetime
import json
from sre_compile import isstring

from dizhu.entity import dizhuconf
from dizhu.entity.dizhuconf import DIZHU_GAMEID
from dizhu.entity.utils import TimeCycleRegister
from dizhucomm.entity.events import UserTableWinloseEvent
import freetime.util.log as ftlog
from hall.entity import hallitem, datachangenotify, hallstore
from hall.entity.todotask import TodoTaskPayOrder, TodoTaskShowInfo, \
    TodoTaskHelper
from hall.game import TGHall
from poker.entity.biz.activity.activity import TYActivity
from poker.entity.biz.content import TYContentItem
from poker.entity.biz.exceptions import TYBizConfException
import poker.entity.biz.message.message as pkmessage
from poker.entity.biz.store.store import TYOrderDeliveryEvent
from poker.entity.configure import gdata
from poker.entity.dao import gamedata
from poker.entity.events.tyevent import MatchWinloseEvent, EventConfigure
import poker.entity.events.tyeventbus as pkeventbus
from poker.protocol import router
from poker.util import strutil
import poker.util.timestamp as pktimestamp


class FundStatus(object):
    def __init__(self, userId):
        self.userId = userId
        self.updateTime = None
        self.isActivated = 0
        self.gainTaskCount = 0
        
class DdzFundConf(object):
    def __init__(self):
        self.startDT = None
        self.endDT = None
        self.autoActivated = 0
        self.timeCycle = None
        self.productIds = []
        self.hallGameIds = []
        
    def decodeFromDict(self, d):
        try:
            self.startDT = datetime.strptime(d.get('start_date'), '%Y-%m-%d %H:%M:%S')
        except:
            raise TYBizConfException(d, 'DdzFundConf.start_date must be datetime with format: %Y-%m-%d %H:%M:%S')
        try:
            self.endDT = datetime.strptime(d.get('end_date'), '%Y-%m-%d %H:%M:%S')
        except:
            raise TYBizConfException(d, 'DdzFundConf.end_date must be datetime with format: %Y-%m-%d %H:%M:%S')
        if self.endDT <= self.startDT:
            raise TYBizConfException(d, 'DdzFundConf.end_date must > start_date')
        self.autoActivated = d.get('autoactivize', 0)
        if self.autoActivated not in (0, 1):
            raise TYBizConfException(d, 'DdzFundConf.autoActivated must int in (0, 1)')
        
        self.productIds = d.get('productIds', [])
        if not isinstance(self.productIds, list):
            raise TYBizConfException(d, 'DdzFundConf.productIds must be list')
        
        self.timeCycle = TimeCycleRegister.decodeFromDict(d.get('cycle'))
        
        self.hallGameIds = d.get('hallGameIds', [])
        if not isinstance(self.hallGameIds, list):
            raise TYBizConfException(d, 'DdzFundConf.hallGameIds must be list')
        for hallGameId in self.hallGameIds:
            if not isinstance(hallGameId, int):
                raise TYBizConfException(d, 'DdzFundConf.hallGameIds must be int list')
        return self
        
class ActivityDdzFund(object):
    conf = None
    
    @classmethod
    def initialize(cls):
        from dizhu.game import TGDizhu
        TGDizhu.getEventBus().subscribe(MatchWinloseEvent, cls.onMatchWinlose)
        TGDizhu.getEventBus().subscribe(UserTableWinloseEvent, cls.onTableWinlose)
        TGHall.getEventBus().subscribe(TYOrderDeliveryEvent, cls.onOrderDelivery)
        pkeventbus.globalEventBus.subscribe(EventConfigure, cls._onConfChanged)
        cls._reloadConf()
        
    @classmethod
    def _onConfChanged(cls, event):
        if event.isChanged(['game:6:activity:0']):
            ftlog.debug('ActivityDdzFund._onConfChanged')
            cls._reloadConf()
    
    @classmethod
    def _reloadConf(cls):
        conf = dizhuconf.getActivityConf('ddz_fund')
        try:
            cls.conf = DdzFundConf().decodeFromDict(conf)
            ftlog.debug('ActivityDdzFund._reloadConf conf=', conf)
        except:
            ftlog.error('ActivityDdzFund._reloadConf conf=', conf)
        
    @classmethod
    def getFrontKey(cls):
        '''
        生成活动游戏数据的唯一Key值，用于在redis中存储
        '''
        assert(cls.conf)
        return 'act.fund.front.' + cls.conf.startDT.strftime('%Y%m%d.%H%M%S')
    
    @classmethod
    def getBackKey(cls):
        assert(cls.conf)
        return 'act.fund.back.' + cls.conf.startDT.strftime('%Y%m%d.%H%M%S')
    
    @classmethod
    def loadFundStatus(cls, userId, timestamp=None):
        ret = None
        timestamp = timestamp or pktimestamp.getCurrentTimestamp()
        key = cls.getFrontKey()
        d = gamedata.getGameAttrJson(userId, DIZHU_GAMEID, key)
        if ftlog.is_debug():
            ftlog.debug('ActivityDdzFund.loadFundStatus userId=', userId,
                        'key=', key,
                        'statusData=', d)
        if d:
            try:
                ret = FundStatus(userId)
                ret.updateTime = d['updateTime']
                ret.isActivated = d['isActivated']
                ret.gainTaskCount = d['gainTaskCount']
            except:
                ftlog.warn('ActivityDdzFund.loadFundStatus BadData',
                           'key=', key,
                           'data=', d)
                ret = None
        if not ret:
            ret = FundStatus(userId)
        return cls.adjustStatus(ret, timestamp)
    
    @classmethod
    def adjustStatus(cls, status, timestamp):
        if not status.updateTime or not cls.conf.timeCycle.isSameCycle(timestamp, status.updateTime):
            ftlog.info('ActivityDdzFund.adjustStatus DiffCycle userId=', status.userId,
                       'status=', status.__dict__,
                       'timestamp=', timestamp)
            status.updateTime = timestamp
            status.isActivated = 1 if cls.conf.autoActivated else 0
            status.gainTaskCount = 0
            cls.saveFundStatus(status)
            data_wrapper = UserPlayDataDatabase(status.userId)
            data_wrapper.clear()
        else:
            # 如果自动激活，并且没有激活状态则激活
            if cls.conf.autoActivated and not status.isActivated:
                status.isActivated = 1
                cls.saveFundStatus(status)
        return status
    
    @classmethod
    def saveFundStatus(cls, status):
        d = {
             'updateTime':status.updateTime,
             'isActivated':status.isActivated,
             'gainTaskCount':status.gainTaskCount
        }
        key = cls.getFrontKey()
        if ftlog.is_debug():
            ftlog.debug('ActivityDdzFund.saveFundStatus userId=', status.userId,
                        'key=', key,
                        'statusData=', d)
        gamedata.setGameAttr(status.userId, DIZHU_GAMEID, key, strutil.dumps(d))
    
    @classmethod
    def checkActivityDate(cls, nowDT=None):
        '''
        检测活动日期是否在日期范围内
        '''
        if not cls.conf:
            return False
        nowDT = nowDT or datetime.now()
        return nowDT >= cls.conf.startDT and nowDT < cls.conf.endDT
    
    @classmethod
    def onOrderDelivery(cls, event):
        ok = cls.checkActivityDate()
        if not ok:
            if ftlog.is_debug():
                ftlog.debug('ActivityDdzFund.onOrderDelivery OutDate userId=', event.userId,
                            'clientId=', event.orderDeliveryResult.order.clientId,
                            'productId=', event.orderDeliveryResult.order.productId)
            return
        
        if event.orderDeliveryResult.order.productId not in cls.conf.productIds:
            return
        
        hallGameId = strutil.getGameIdFromHallClientId(event.orderDeliveryResult.order.clientId)
        if cls.conf.hallGameIds and hallGameId not in cls.conf.hallGameIds:
            if ftlog.is_debug():
                ftlog.debug('ActivityDdzFund.onOrderDelivery OutHallGameId userId=', event.userId,
                            'clientId=', event.orderDeliveryResult.order.clientId,
                            'productId=', event.orderDeliveryResult.order.productId,
                            'hallGameId=', hallGameId,
                            'hallGameIds=', cls.conf.hallGameIds)
            return
        
        status = cls.loadFundStatus(event.userId, event.timestamp)
        
        if not status.isActivated:
            status.isActivated = 1
            status.updateTime = event.timestamp
            ftlog.info('ActivityDdzFund.onOrderDelivery SetActivated userId=', event.userId,
                       'productId=', event.orderDeliveryResult.order.productId,
                       'status=', status.__dict__)
            cls.saveFundStatus(status)
    
    @classmethod
    def onMatchWinlose(cls, event):
        '''
        监听比赛结局胜负
        '''
        ok = cls.checkActivityDate()
        if not ok:
            if ftlog.is_debug():
                ftlog.debug('ActivityDdzFund.onMatchWinlose OutDate userId=', event.userId,
                            'matchId=', event.matchId)
            return
        
        userId = event.userId
        
        status = cls.loadFundStatus(userId, event.timestamp)
        
        if not status.isActivated:
            ftlog.debug('ActivityDdzFund.onMatchWinlose userId=', userId,
                        'status=', status.__dict__)
            return

        roomId = event.matchId
        try:
            roomId = int(roomId)
        except:
            ftlog.warn('ActivityDdzFund.onMatchWinlose BadMatchId userId=', userId,
                       'status=', status.__dict__)
            return

        bigRoomId = gdata.getBigRoomId(roomId)
        data_wrapper = UserPlayDataDatabase(userId)
        data_wrapper.increase(event.isWin, True, 0, bigRoomId)
        
        ftlog.info('ActivityDdzFund.onMatchWinlose userId=', userId,
                   'matchId=', event.matchId,
                   'isWin=', event.isWin,
                   'isMatch=', True,
                   'roomLevel=', 0,
                   'bigRoomId=', bigRoomId,
                   'roomId=', roomId)

    @classmethod
    def onTableWinlose(cls, event):
        '''
        监听非比赛场的结局胜负
        '''
        ok = cls.checkActivityDate()
        if not ok:
            if ftlog.is_debug():
                ftlog.debug('ActivityDdzFund.onTableWinlose OutDate userId=', event.userId,
                            'roomId=', event.roomId)
            return

        userId = event.userId
        
        status = cls.loadFundStatus(userId, event.timestamp)
        
        if not status.isActivated:
            ftlog.debug('ActivityDdzFund.onTableWinlose userId=', userId,
                        'roomId=', event.roomId,
                        'status=', status.__dict__)
            return

        roomLevel = gdata.roomIdDefineMap()[event.roomId].configure.get('roomLevel', 1)

        data_wrapper = UserPlayDataDatabase(userId)

        bigRoomId = event.mixConfRoomId or gdata.getBigRoomId(event.roomId)
        data_wrapper.increase(event.winlose.isWin, False, roomLevel, bigRoomId)
        
        ftlog.info('ActivityDdzFund.onTableWinlose userId=', userId,
                   'isWin=', event.winlose.isWin,
                   'isMatch=', True,
                   'roomLevel=', 0,
                   'roomId=', event.roomId,
                   'bigRoomId=', bigRoomId)
        
def redis_readjson(userId, gameId, redisKey):
    data = gamedata.getGameAttr(userId, gameId, redisKey)
    ftlog.debug("redis_readjson: userId=", userId, "type:", type(data), "data=", data)
    if data == None:
        return {}
    return json.loads(data)

def redis_writejson(userId, gameId, redisKey, data):
    jstr = json.dumps(data)
    ftlog.debug("redis_writejson: userId=", userId, "type:", type(jstr), "json_str=", jstr)
    gamedata.setGameAttr(userId, gameId, redisKey, jstr)

class UserPlayDataDatabase(object):
    '''
    用来处理记录在redis中的数据
    * COUNT.TABLE.ROOM_ID
    * COUNT.TABLE.ROOM_LEVEL
    * COUNT.MATCH.ROOM_ID
    * COUNT.MATCH.ROOM_LEVEL
    * COUNT_WIN.MATCH.ROOM_ID
    * COUNT_WIN.MATCH.ROOM_LEVEL

    存储结构：
    data = {
        "TOTAL": 0, // 玩的总局数，不论胜负，是否是比赛
        "TOTAL_TABLE": 0, // 非比赛场总局数
        "TOTAL_TABLE_WIN": 0,  // 非比赛场胜利的总局数

        "COUNT": { // 统计的记录的详细情况，分比赛和非比赛场，依据RoomLevel和RoomId分别记录
            "TABLE": {
                "ROOM_LEVEL":{ },
                "ROOM_ID":{}
            },
            "MATCH":{
                "ROOM_LEVEL":{ },
                "ROOM_ID":{}
            }
        },
        "COUNT_WIN":{ // 统计的胜利记录的详细情况，分比赛和非比赛场，依据RoomLevel和RoomId分别记录
            "TABLE": {
                "ROOM_LEVEL":{ },
                "ROOM_ID":{}
            },
            "MATCH":{
                "ROOM_LEVEL":{ },
                "ROOM_ID":{}
            }
        }
    }
    '''

    def __init__(self, userId):
        self._uniqueKey = ActivityDdzFund.getBackKey()
        self._userId = userId
        self._gameId = 6

    def _readFromReids(self):
        userId = self._userId
        gameId = self._gameId
        redisKey = self._uniqueKey
        return redis_readjson(userId, gameId, redisKey)

    def _writeToReids(self, data):
        userId = self._userId
        gameId = self._gameId
        redisKey = self._uniqueKey
        redis_writejson(userId, gameId, redisKey, data)

    def _internalIncrease(self, data_depth2, isMatch, roomLevel, roomId):
        if isMatch:
            depth3 = data_depth2.get("MATCH", {})
        else:
            depth3 = data_depth2.get("TABLE", {})

        depth4_roomid_map = depth3.get("ROOM_ID", {})
        depth4_roomlvl_map = depth3.get("ROOM_LEVEL", {})
        depth3["ROOM_ID"] = depth4_roomid_map
        depth3["ROOM_LEVEL"] = depth4_roomlvl_map

        roomId = str(roomId)
        roomid_count = depth4_roomid_map.get(roomId, 0)
        depth4_roomid_map[roomId] = int(roomid_count) + 1

        roomLevel = str(roomLevel)
        roomlvl_count = depth4_roomlvl_map.get(roomLevel, 0)
        depth4_roomlvl_map[roomLevel] = int(roomlvl_count) + 1

        if isMatch:
            data_depth2['MATCH'] = depth3
        else:
            data_depth2['TABLE'] = depth3


    def increase(self, isWin, isMatch, roomLevel, bigRoomId):
        '''
        增加一次记录，根据参数在不同的选项上增加
        '''
        userId = self._userId
        ftlog.debug("UserPlayDataDatabase.increase: userId=", userId,
                    "isWin=",isWin,
                    "isMatch=",isMatch,
                    "roomLevel=",roomLevel,
                    "bigRoomId=",bigRoomId)
        data = self._readFromReids()
        if not isinstance(data, dict):
            data = {}

        # COUNT 统计
        depth2_count = data.get("COUNT", {})
        data['COUNT'] = depth2_count
        self._internalIncrease(depth2_count, isMatch, roomLevel, bigRoomId)

        # COUNT_WIN 统计
        if isWin:
            depth2_count_win = data.get("COUNT_WIN", {})
            data['COUNT_WIN'] = depth2_count_win
            self._internalIncrease(depth2_count_win, isMatch, roomLevel, bigRoomId)

        # TOTAL 玩的总局数，不论胜负，比赛
        total_count = data.get("TOTAL", 0)
        data["TOTAL"] = int(total_count) + 1

        # TOTAL_TABLE 非比赛场的总局数
        if not isMatch:
            total_table_count = data.get("TOTAL_TABLE", 0)
            data["TOTAL_TABLE"] = int(total_table_count) + 1

        # TOTAL_TABLE_WIN 非比赛场胜利的总局数
        if (not isMatch) and isWin:
            total_table_win_count = data.get("TOTAL_TABLE_WIN", 0)
            data["TOTAL_TABLE_WIN"] = int(total_table_win_count) + 1

        ftlog.debug("UserPlayDataDatabase.increase: userId=", userId, "data=", data)
        ftlog.info("DdzFundActivity:TaskDetail, userId", userId, "TOTAL", data.get("TOTAL", 0), "TOTAL_TABLE", data.get("TOTAL_TABLE", 0), "dataDetail", data)
        self._writeToReids(data)

    def getCount(self, typeId, key=""):
        '''
        * TOTAL
        * TOTAL_TABLE
        * TOTAL_TABLE_WIN
        * COUNT.TABLE.ROOM_ID
        * COUNT.TABLE.ROOM_LEVEL
        * COUNT.MATCH.ROOM_ID
        * COUNT.MATCH.ROOM_LEVEL
        * COUNT_WIN.MATCH.ROOM_ID
        * COUNT_WIN.MATCH.ROOM_LEVEL
        '''
        paramlist = typeId.split('.')
        data = self._readFromReids()
        userId = self._userId
        ftlog.debug("UserPlayDataDatabase.getCount1: userId=", userId, "typeId=", typeId, "key=", key)
        ftlog.debug("UserPlayDataDatabase.getCount2: userId=", userId, "data=", data, "data|type=", type(data))
        if not isinstance(data, dict):
            data = {}

        sub = data
        for x in paramlist:
            sub = sub.get(x, {})

        ftlog.debug("UserPlayDataDatabase.getCount3: userId=", userId, "sub=", sub,  "sub|type=", type(sub))
        if isinstance(sub, dict):
            ftlog.debug("UserPlayDataDatabase.getCount4: userId=", userId, "sub.get(str(key), 0)=", sub.get(str(key), 0))
            return sub.get(str(key), 0)
        if isinstance(sub, int) or isinstance(sub, long):
            return sub
        return 0

    def clear(self):
        self._writeToReids({})

class FundTaskWrapper(object):
    '''
    对任务统计信息获取的包装
    '''
    def _checkTaskFinished(self, gameId, userId, cond):
        '''
        判断任务是否完成
        '''
        redis = UserPlayDataDatabase(userId)

        typeid = cond.get('typeId', '')
        
        cond_params = cond.get('params', {})
        min_count = cond_params.get('minCount', 0)
        max_count = cond_params.get('maxCount', -1)
        
        # key可以是数组也可以是字符串数组
        key = cond_params.get('key', [])
        keys = [key] if isstring(key) else key
        
        ftlog.debug('FundTaskWrapper._checkTaskFinished:',
                    'userId=', userId,
                    'keys=', keys)
        count = 0
        for key in keys:
            count += redis.getCount(typeid, key)
            
        ftlog.debug("FundTaskWrapper._checkTaskFinished:"
                    "userId=", userId,
                    "min_count=", min_count, 
                    "max_count=", max_count, 
                    "count=", count)
        if count >= min_count:
            if max_count>=0 :
                if count <= max_count:
                    return True
                return False
            return True
        return False

    def increaseGotTaskCount(self, gameId, userId):
        '''
        增加用户已经领取的活动数目
        '''
        timestamp = pktimestamp.getCurrentTimestamp()
        status = ActivityDdzFund.loadFundStatus(userId, timestamp)
        status.gainTaskCount += 1
        status.updateTime = timestamp
        ActivityDdzFund.saveFundStatus(status)
        ftlog.info('FundTaskWrapper.increaseGotTaskCount userId=', userId,
                   'gameId=', gameId)
        return status.gainTaskCount

    def getFinishTaskCount(self, gameId, userId, clientconf):
        '''
        获得用户已经完成的活动数目
        过程：遍历奖励，检查每一个条件，直到第一个不满足条件的位置，此之前就为完成的任务数量
        '''
        subconf = clientconf.get('config', {})
        activate_map = subconf.get('activate', {})
        reward_list = activate_map.get('reward', [])
        index = 0
        for x in reward_list:
            cond = x.get('condition', {})
            ok = self._checkTaskFinished(gameId, userId, cond)
            ftlog.debug("FundTaskWrapper.getFinishTaskCount: userId=", userId, "cond=",cond, "result=",ok)
            if not ok:
                break
            index = index + 1
        return index

    def getRecvTaskCount(self, gameId, userId):
        '''
        获得用户已经领取的活动数目
        '''
        status = ActivityDdzFund.loadFundStatus(userId)
        ftlog.debug('FundTaskWrapper.getRecvTaskCount userId=', userId,
                    'gameId=', gameId,
                    'status=', status.__dict__)
        return status.gainTaskCount

    def getTablePlayCount(self, userId):
        '''
        获得用户非比赛场数目
        '''
        redis = UserPlayDataDatabase(userId)
        count = redis.getCount("TOTAL_TABLE", "")
        return count

    def getRoomTablePlayCount(self, userId, roomId):
        '''
        获得用户非比赛场数目指定房间
        '''
        redis = UserPlayDataDatabase(userId)
        count = redis.getCount("COUNT.TABLE.ROOM_ID", str(roomId))
        return count

    def getPlayCountByKey(self, userId, key):
        redis = UserPlayDataDatabase(userId)
        count = redis.getCount(key)
        return count

class TYActivityFund(TYActivity):
    '''
    地主基金活动界面处理类
    此类每次请求都会重新构造对象
    '''
    TYPE_ID = 20

    def __init__(self, dao, clientConfig, serverConfig):
        ftlog.debug("TYActivityFund.__init__")
        self._dao = dao
        self._serverConf = serverConfig
        self._clientConf = clientConfig
        self._taskWrapper = FundTaskWrapper()

    def checkCanActivateDate(self, clientconf):
        '''
        检测是否在激活日期范围内
        '''
        day_now = datetime.now()

        activateconf = clientconf.get("config", {}).get("activate", {})
        confdate = activateconf.get("activateTime", {})
        ftlog.debug("FundEventHandler.checkActivityDate: confdate=", confdate)

        start_datetime = datetime.strptime(confdate.get('start', '2015-01-01 0:0:0'), '%Y-%m-%d %H:%M:%S')
        end_datetime = datetime.strptime(confdate.get('end', '2015-01-01 0:0:0'), '%Y-%m-%d %H:%M:%S')

        ftlog.debug("FundEventHandler.checkActivityDate: day_now=", day_now, ";start_datetime=", start_datetime, ";end_datetime=", end_datetime)
        ok = day_now>=start_datetime and day_now<=end_datetime
        ftlog.debug("FundEventHandler.checkActivityDate: daynow in range: ok=", ok)
        return ok

    def makeClientConf_old(self, clientconf, gameId, userId, clientId):
        '''
        构造客户端的活动协议配置
        '''
        conf = strutil.cloneData(clientconf)
        activateconf = conf.get("config", {}).get("activate", {})
        subconf = conf.get('config', {})

        task = self._taskWrapper
        roomid_tocount = activateconf.get('countRoomId', -1)
        key_tocount = activateconf.get('countByKey')
        finish_taskcount = task.getFinishTaskCount(gameId, userId, clientconf)
        gain_taskcount = task.getRecvTaskCount(gameId, userId)
        total_tablecount = task.getTablePlayCount(userId)
        roomid_tablecount = task.getRoomTablePlayCount(userId, roomid_tocount)
        is_activited = ActivityDdzFund.loadFundStatus(userId).isActivated
        ftlog.debug("TYActivityFund.makeClientConf: userId=", userId,
                    "roomid_tocount=",roomid_tocount,
                    "total_tablecount=", total_tablecount,
                    "finish_taskcount=", finish_taskcount,
                    "roomid_tablecount=", roomid_tablecount,
                    "gain_taskcount=", gain_taskcount,
                    "is_activited=",is_activited,
                    'key_tocount=', key_tocount)

        # subconf['overCnt'] = finish_taskcount # 已经完成的任务数量
        if key_tocount:
            subconf['overCnt'] = task.getPlayCountByKey(userId, key_tocount)
        elif roomid_tocount > 0:
            subconf['overCnt'] = roomid_tablecount # 已经完成的局数
        else:
            subconf['overCnt'] = total_tablecount # 已经完成的局数
        subconf['getRewardYetCnt'] = gain_taskcount # 已经领取的任务数量
        subconf['isActive'] = is_activited # 是否已经激活基金活动
        subconf['activeYetHint'] = strutil.replaceParams(subconf.get("activeYetHint",""), {
            "finishcount":subconf['overCnt'],
            "finishcount_room": str(roomid_tablecount),
        })

        reward_btn_map = subconf.get('rewardButton', {})
        normal_tip = reward_btn_map.get('normalTip', '')
        activate_map = subconf.get('activate', {})
        reward_list = activate_map.get('reward', [])

        if len(reward_list)>gain_taskcount:
            desc = reward_list[gain_taskcount].get('desc', '')
            reward_btn_map['normalTip'] = strutil.replaceParams(normal_tip, {"assets":desc})

        # TodoTask
        activatebtn_map = subconf.get("activateButton", {})
        todotask = activatebtn_map.get("todoTask", {})
        payOrder = todotask.get("payOrder")
        ftlog.debug("TYActivityFund.makeClientConf: userId=", userId, "payOrder=", payOrder)

        if payOrder:
            product, _ = hallstore.findProductByPayOrder(gameId, userId, clientId, payOrder)
            ftlog.debug("TYActivityFund.makeClientConf: userId=", userId, "product=", product)
            payOrder = TodoTaskPayOrder(product)
            ftlog.debug("TYActivityFund.makeClientConf: userId=", userId, "params=", payOrder)
            activatebtn_map["todoTask"] = payOrder.toDict()

        # 激活日期限制
        ok = self.checkCanActivateDate(conf)
        activateconf['isOutdate'] = not ok
        if ok:
            activateconf['outdateTip'] = None
        ftlog.debug("TYActivityFund.makeClientConf: userId=", userId, "isOutdate", activateconf['isOutdate'])
        ftlog.debug("TYActivityFund.makeClientConf: userId=", userId, "conf=", conf)
        return conf

    def makeClientConf(self, clientconf, gameId, userId, clientId):
        '''
        构造客户端的活动协议配置
        '''
        conf = strutil.cloneData(clientconf)
        activateconf = conf.get("config", {}).get("activate", {})
        subconf = conf.get('config', {})

        task = self._taskWrapper
        
        # New: 要统计的房间列表
        roomid_tocount = activateconf.get('countRoomId', [])
        roomids_tocount = [roomid_tocount] if isstring(roomid_tocount) else roomid_tocount
            
        key_tocount = activateconf.get('countByKey')
        finish_taskcount = task.getFinishTaskCount(gameId, userId, clientconf)
        gain_taskcount = task.getRecvTaskCount(gameId, userId)
        total_tablecount = task.getTablePlayCount(userId)
        
        # New: 统计多个房间的数量
        roomid_tablecount = 0
        for roomid in roomids_tocount:
            roomid_tablecount += task.getRoomTablePlayCount(userId, roomid)
        
        is_activited = ActivityDdzFund.loadFundStatus(userId).isActivated
        ftlog.debug("TYActivityFund.makeClientConf: userId=", userId,
                    "roomids_tocount=",roomids_tocount,
                    "total_tablecount=", total_tablecount,
                    "finish_taskcount=", finish_taskcount,
                    "roomid_tablecount=", roomid_tablecount,
                    "gain_taskcount=", gain_taskcount,
                    "is_activited=",is_activited,
                    'key_tocount=', key_tocount)

        # subconf['overCnt'] = finish_taskcount # 已经完成的任务数量
        if key_tocount:
            subconf['overCnt'] = task.getPlayCountByKey(userId, key_tocount)
        elif len(roomids_tocount) > 0:
            subconf['overCnt'] = roomid_tablecount # 已经完成的局数
        else:
            subconf['overCnt'] = total_tablecount # 已经完成的局数
        subconf['getRewardYetCnt'] = gain_taskcount # 已经领取的任务数量
        subconf['isActive'] = is_activited # 是否已经激活基金活动
        subconf['activeYetHint'] = strutil.replaceParams(subconf.get("activeYetHint",""), {
            "finishcount":subconf['overCnt'],
            "finishcount_room": str(roomid_tablecount),
        })

        reward_btn_map = subconf.get('rewardButton', {})
        normal_tip = reward_btn_map.get('normalTip', '')
        activate_map = subconf.get('activate', {})
        reward_list = activate_map.get('reward', [])

        if len(reward_list)>gain_taskcount:
            desc = reward_list[gain_taskcount].get('desc', '')
            reward_btn_map['normalTip'] = strutil.replaceParams(normal_tip, {"assets":desc})

        # TodoTask
        activatebtn_map = subconf.get("activateButton", {})
        todotask = activatebtn_map.get("todoTask", {})
        payOrder = todotask.get("payOrder")
        ftlog.debug("TYActivityFund.makeClientConf: userId=", userId, "payOrder=", payOrder)

        if payOrder:
            product, _ = hallstore.findProductByPayOrder(gameId, userId, clientId, payOrder)
            ftlog.debug("TYActivityFund.makeClientConf: userId=", userId, "product=", product)
            payOrder = TodoTaskPayOrder(product)
            ftlog.debug("TYActivityFund.makeClientConf: userId=", userId, "params=", payOrder)
            activatebtn_map["todoTask"] = payOrder.toDict()

        # 激活日期限制
        ok = self.checkCanActivateDate(conf)
        activateconf['isOutdate'] = not ok
        if ok:
            activateconf['outdateTip'] = None
        ftlog.debug("TYActivityFund.makeClientConf: userId=", userId, "isOutdate", activateconf['isOutdate'])
        ftlog.debug("TYActivityFund.makeClientConf: userId=", userId, "conf=", conf)
        return conf

    def sendTodoTask(self, gameId, userId, info):
        task = TodoTaskShowInfo(info, True)
        mo = TodoTaskHelper.makeTodoTaskMsg(gameId, userId, task)
        router.sendToUser(mo, userId)

    def getConfigRewardUnreachedTip(self):
        clientconf = self._clientConf
        subconf = clientconf.get('config', {})
        btnconf = subconf.get('rewardButton', {})
        return btnconf.get("grayTip", "")

    def getConfigRewardCompletionTip(self):
        clientconf = self._clientConf
        subconf = clientconf.get('config', {})
        btnconf = subconf.get('rewardButton', {})
        return btnconf.get("completionTip", "")

    def getConfigRewardList(self):
        clientconf = self._clientConf
        subconf = clientconf.get('config', {})
        return subconf.get('activate', {}).get("reward", [])

    def sendRewardToUser(self, gameId, userId, reward, mail):
        ftlog.debug("TYActivityFund.sendRewardToUser: userId=", userId, "reward=", reward, "mail=", mail)

        timestamp = pktimestamp.getCurrentTimestamp()
        contentItem = TYContentItem.decodeFromDict(reward)
        userAssets = hallitem.itemSystem.loadUserAssets(userId)
        assetKind, _, _ = userAssets.addAsset(gameId, contentItem.assetKindId,
                                                      contentItem.count, timestamp,
                                                      'DIZHU_ACT_FUND_SEND', 0)
        # 通知用户道具和消息存在改变
        if assetKind.keyForChangeNotify:
            datachangenotify.sendDataChangeNotify(gameId, userId, [assetKind.keyForChangeNotify, 'message'])

        # 发送邮箱信息
        if mail==None or len(mail) <= 0:
            return
        mail_message = strutil.replaceParams(mail, {"assets":str(reward.get('desc', ''))})
        if mail_message:
            pkmessage.sendPrivate(9999, userId, 0, mail_message)

    def getConfigForClient(self, gameId, userId, clientId):
        '''
        获取客户端要用的活动配置，由TYActivitySystemImpl调用
        '''
        clientconf = self._clientConf
        serverconf = self._serverConf
        ftlog.debug("TYActivityFund.getConfigForClient: userId=", userId, "gameId=", gameId,  "clientId", clientId, "serverconf=",serverconf)
        
        # Warning
        if not self.checkOperative():
            ftlog.debug("TYActivityFund.getConfigForClient: userId=", userId, "checkOperative=False(overdue)")

        return self.makeClientConf(clientconf, gameId, userId, clientId)

    def handleRequest(self, msg):
        ftlog.debug("TYActivityFund.handleRequest: enter")

        userId = msg.getParam('userId')
        gameId = msg.getParam('gameId')
        clientId = msg.getParam("clientId")
        activityId = msg.getParam("activityId")
        action = msg.getParam("action")

        if action == "activityDdzFundGet":
            return self.handleActivityDdzFundGet(userId, gameId, clientId, activityId)
        elif action == "activityDdzFundCheck":
            return self.handleActivityDdzFundCheck(userId, gameId, clientId, activityId)
        else:
            ftlog.debug("TYActivityFund.handleRequest: userId=", userId, "action not match")
            return {"isOk":False, "errorInfo":  "action not match"}

    def handleActivityDdzFundGet(self, userId, gameId, clientId, activityId):
        clientconf = self._clientConf
        task = self._taskWrapper
        reward_list = self.getConfigRewardList()
        reward_num = len(reward_list)

        finish_taskcount = task.getFinishTaskCount(gameId, userId, clientconf)
        gain_taskcount = task.getRecvTaskCount(gameId, userId)
        ftlog.info('TYActivityFund.handleActivityDdzFundGet userId=', userId,
                   'finish_taskcount', finish_taskcount,
                   'getreward_taskcount', gain_taskcount)
        
        # 已经全部领取并完成任务
        tasknum = reward_num
        if gain_taskcount >= tasknum:
            ftlog.debug("TYActivityFund.handleRequest: (gain_taskcount >= tasknum) userId=",userId,"clientId=",clientId,"activityId=",activityId)
            return {"isOk":False, "getRewardYetCnt":gain_taskcount, "tip":self.getConfigRewardCompletionTip()}

        # 完成的任务已经全部领取
        if gain_taskcount + 1 > finish_taskcount:
            ftlog.debug("TYActivityFund.handleRequest: (gain_taskcount + 1 > finish_taskcount) userId=",userId,"clientId=",clientId,"activityId=",activityId)
            return {"isOk":False, "getRewardYetCnt":gain_taskcount, "tip":self.getConfigRewardUnreachedTip()}

        # 领取任务数目增加
        task.increaseGotTaskCount(gameId, userId)
        gain_taskcount = task.getRecvTaskCount(gameId, userId)
        ftlog.debug("TYActivityFund.handleRequest: userId=", userId, "(after get)gain_taskcount=", gain_taskcount)

        # 奖励列表
        if gain_taskcount <= reward_num:
            reward = reward_list[gain_taskcount - 1]
            self.sendRewardToUser(gameId, userId, reward, clientconf.get('config', {}).get('mail', '') )
            tip = clientconf.get("config", {}).get("rewardButton", {}).get("normalTip", "")
            tip = strutil.replaceParams(tip, {"assets":str(reward.get('desc', ''))})
            return {"isOk":True, "getRewardYetCnt":gain_taskcount, "tip":tip}

        ftlog.debug("TYActivityFund.handleRequest: after user get not send reward (err:2) userId=",userId,"clientId=",clientId,"activityId=",activityId)
        return {"isOk":False, "getRewardYetCnt":gain_taskcount}

    def handleActivityDdzFundCheck(self, userId, gameId, clientId, activityId):
        is_activited = ActivityDdzFund.loadFundStatus(userId).isActivated
        return {"isOk":True, "isActive": is_activited}

