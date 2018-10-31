# -*- coding=utf-8 -*-
'''
Created on 15-12-30

@author: luwei
'''
from datetime import datetime
import json
import random

from dizhu.activities.toolbox import Tool, Redis, UserInfo, Random, UserBag
import freetime.util.log as ftlog
from hall.entity.hallactivity.activity import TYActivityDaoImpl, activitySystem
from poker.entity.biz.activity.activity import TYActivity, TYActivityRegister
from poker.entity.dao import daobase
from poker.entity.events.tyevent import EventConfigure, EventHeartBeat
from poker.entity.events.tyeventbus import globalEventBus
import poker.entity.events.tyeventbus as pkeventbus
from poker.util import strutil


_REDIS_LUA_PUSHLIST_NAME = "ddz_redenvelope_pushlist"
_REDIS_LUA_PUSHLIST_SCRIPT = '''
    local general_jsonstr = tostring(KEYS[1])
    local vip_jsonstr = tostring(KEYS[2])
    local datetime_point = tostring(KEYS[3])

    local is_record = redis.call("HGET", "dizhu:hongbaorecord", datetime_point)
    if is_record then
    	return false
    end

    local key_items_general = "dizhu:hongbao:general:"
    local key_items_vip = "dizhu:hongbao:vip:"
    local key_itemmap_general = "dizhu:hongbaoitemmap:general"
    local key_itemmap_vip = "dizhu:hongbaoitemmap:vip"

    local general_hongbaokeys = redis.call("HKEYS", key_itemmap_general)
    local vip_hongbaokeys = redis.call("HKEYS", key_itemmap_vip)
    for k,v in pairs(general_hongbaokeys) do
    	redis.call("DEL", v)
    end
    for k,v in pairs(vip_hongbaokeys) do
    	redis.call("DEL", v)
    end
    redis.call("DEL", key_itemmap_general)
    redis.call("DEL", key_itemmap_vip)

    local general_listmap = cjson.decode(general_jsonstr)
    for k,list in pairs(general_listmap) do
    	local keypath = key_items_general .. k
    	redis.call("HSET", key_itemmap_general, keypath, #list)
    	for _,v in pairs(list) do redis.call("LPUSH", keypath, v) end
    end

    local vip_listmap = cjson.decode(vip_jsonstr)
    for k,list in pairs(vip_listmap) do
    	local keypath = key_items_vip .. k
    	redis.call("HSET", key_itemmap_vip, keypath, #list)
    	for _,v in pairs(list) do redis.call("LPUSH", keypath, v) end
    end

    redis.call("HSET", "dizhu:hongbaorecord", datetime_point, 1)
    return true
'''

_REDIS_LUA_GETCOUNT_NAME = "ddz_redenvelope_getcount"
_REDIS_LUA_GETCOUNT_SCRIPT = '''
	local what = tostring(KEYS[1]) -- all, vip, general

    local key_itemmap_general = "dizhu:hongbaoitemmap:general"
    local key_itemmap_vip = "dizhu:hongbaoitemmap:vip"
    local count = 0

    if what == "general" or what == "all" then
	    local general_hongbaokeys = redis.call("HKEYS", key_itemmap_general)
	    for k,v in pairs(general_hongbaokeys) do
	    	local num = redis.call("LLEN", v)
	    	count = count + num
	    	if num <= 0 then redis.call("HDEL", key_itemmap_general, v) end
	    end
	end

	if what == "vip" or what == "all" then
	    local vip_hongbaokeys = redis.call("HKEYS", key_itemmap_vip)
	    for k,v in pairs(vip_hongbaokeys) do
	    	local num = redis.call("LLEN", v)
	    	count = count + num
	    	if num <= 0 then redis.call("HDEL", key_itemmap_vip, v) end
	    end
	end

    return count
'''

_REDIS_LUA_GET_NAME = "ddz_redenvelope_get"
_REDIS_LUA_GET_SCRIPT = '''
	local numrange = function(num, l, r)
		return math.fmod(num, (r - l + 1)) + l -- range[l, r]
	end

	local randomitems = function(rnd, itemmap)
		local count = 0
		for k,v in pairs(itemmap) do
			count = count + v
		end
		local sel = numrange(rnd, 1, count)
		local cursor = 1
		for k,v in pairs(itemmap) do
			local l = cursor
			cursor = cursor + v
			local r = cursor - 1
			if sel >= l and sel <= r then
				return k
			end
		end
	end

    local isvip = KEYS[1]
    local rndnum = KEYS[2]

    local key_itemmap_general = "dizhu:hongbaoitemmap:general"
    local key_itemmap_vip = "dizhu:hongbaoitemmap:vip"

    local items = {}
    local isitemvip = isvip
    if isvip == 'True' then
    	isitemvip = true
    	items = redis.call("HGETALL", key_itemmap_vip)
    end
    if #items <= 0 then
    	isitemvip = false
    	items = redis.call("HGETALL", key_itemmap_general)
    end
    if #items <= 0 then
    	return false
    end

    local itemmap = {}
	for i=1, #items ,2 do
		itemmap[items[i]] = items[i+1]
	end

    local item = randomitems(rndnum, itemmap)
    local itemcount = redis.call("LPOP", item)
    local num = redis.call("LLEN", item)

    if isitemvip then redis.call("HSET", key_itemmap_vip, item, num)
    else redis.call("HSET", key_itemmap_general, item, num)
    end

    if num <= 0 then
    	redis.call("HDEL", key_itemmap_vip, item)
    	redis.call("HDEL", key_itemmap_general, item)
    end

    return {item, itemcount}

'''


daobase.loadLuaScripts(_REDIS_LUA_PUSHLIST_NAME, _REDIS_LUA_PUSHLIST_SCRIPT)
daobase.loadLuaScripts(_REDIS_LUA_GETCOUNT_NAME, _REDIS_LUA_GETCOUNT_SCRIPT)
daobase.loadLuaScripts(_REDIS_LUA_GET_NAME, _REDIS_LUA_GET_SCRIPT)
_redenvelopeWrapper = None

class DdzRedEnvelope(object):
    _timelist = None
    _datetime_start = None
    _datetime_end = None

    @classmethod
    def registerListener(cls, eventbus):
        ftlog.debug("DdzRedEnvelope.registerListener: enter")
        globalEventBus.subscribe(EventHeartBeat, cls.onHeartBeat)

    @classmethod
    def onHeartBeat(cls, event):
        timelist = cls._timelist
        now = datetime.now()
        # ftlog.debug("DdzRedEnvelope.onHeartBeat: timelist=",timelist, "now", now)
        if timelist == None or len(timelist) <= 0:
            return

        cur = None
        while True:
            if len(timelist)<=0 or now < timelist[0]:
                break
            cur = timelist.pop(0)

        if cur:
            r = _redenvelopeWrapper.reset(cur)
            ftlog.debug("DdzRedEnvelope.onHeartBeat: now=", now, "cur=", cur, "r=", r)

class DataWrapper(object):

    def __init__(self, servconf):
        self._servconf = servconf

    def getRedisKey(self):
        date = self._servconf.get("start", "2016-1-1 0:0:0")
        return "TYActivityDdzRedEnvelope_"+date

    def hasGet(self, userId, datetime):
        '''
        是否已经领取
        :param datetime: 判断这个时间点是否有领取红包
        '''
        rediskey = self.getRedisKey()
        dictobj = Redis.readJson(userId, rediskey)
        key = "get.%s" % str(datetime)
        value = Tool.dictGet(dictobj, key)
        ftlog.debug("DataWrapper.hasGet: userId=", userId, "key=", key, "datetime=",str(datetime), "dictobj=", dictobj, "value=", value)
        if value:
            return True
        return False

    def getLastGetItem(self, userId):
        '''
        获得用户上次领取的道具,若没有则返回false
        :return { "itemId": "user:coupon", "count": 2, "itemDesc": "奖券" }
        '''
        rediskey = self.getRedisKey()
        dictobj = Redis.readJson(userId, rediskey)
        records = dictobj.get("get", {})
        keys = records.keys()
        if len(keys) <= 0:
            return False
        keys.sort()
        lastkey = keys.pop()
        key = "get.%s" % str(lastkey)
        value = Tool.dictGet(dictobj, key)
        ftlog.debug("DataWrapper.getLastGetItem: userId=", userId, "key=", key, "datetime=",str(datetime), "dictobj=", dictobj, "value=", value)
        if value:
            return value
        return False

    def markGet(self, userId, datetime, assets):
        '''
        记录领取红包
        :param datetime: 标记的领取红包的时间点
        '''
        rediskey = self.getRedisKey()
        dictobj = Redis.readJson(userId, rediskey)
        key = "get.%s" % str(datetime)
        Tool.dictSet(dictobj, key, assets)
        Redis.writeJson(userId, rediskey, dictobj)
        ftlog.debug("DataWrapper.makeGet: userId=", userId, "key=", key, "datetime=",str(datetime), "dictobj=", dictobj)

    @classmethod
    def getLastestTimePoint(cls, timelist, startdate):
        '''
        获得已经到达的最近的一个时间点，若未达到今天时间点则返回昨天最后的时间点(前提是昨天时间点在开始时间之后，否则返回False)
        :param timelist 时间列表
        :param startdate 开始时间格式化字符串
        :return datetime
        '''
        l = []
        for s in timelist:
            t = datetime.strptime(s, "%H:%M:%S").time()
            l.append(t)
        l.sort()

        res = None
        dnow = datetime.now()
        now = dnow.time()
        for t in l:
            if now >= t:
                res = t
        if res:
            return datetime(dnow.year, dnow.month, dnow.day, res.hour, res.minute, res.second)

        last_time = l[-1]
        datetime_today = datetime(dnow.year, dnow.month, dnow.day, last_time.hour, last_time.minute, last_time.second)
        timestamp_yesterday = Tool.datetimeToTimestamp(datetime_today) - 24*60*60
        datetime_yesterday = datetime.fromtimestamp(timestamp_yesterday)
        datetime_start = datetime.strptime(startdate, '%Y-%m-%d %H:%M:%S')

        if datetime_yesterday>=datetime_start:
            return datetime_yesterday
        return False

    @classmethod
    def getNextTimePoint(cls, timelist, enddate):
        '''
        获得未到达的最近的一个时间点，若今天没有时间点则返回明天第一个时间点(前提是明天的领取时间点在活动结束之前，否则返回False)
        :param timelist 时间列表
        :param enddate 活动结束时间的格式化字符串
        :return datetime
        '''
        l = []
        for s in timelist:
            t = datetime.strptime(s, "%H:%M:%S").time()
            l.append(t)
        l.sort()

        res = None
        dnow = datetime.now()
        now = dnow.time()
        for t in l:
            if now < t:
                res = t
                break
        if res:
            return datetime(dnow.year, dnow.month, dnow.day, res.hour, res.minute, res.second)

        first_time = l[0]
        datetime_today = datetime(dnow.year, dnow.month, dnow.day, first_time.hour, first_time.minute, first_time.second)
        timestamp_tomorrow = Tool.datetimeToTimestamp(datetime_today) + 24*60*60
        datetime_tomorrow = datetime.fromtimestamp(timestamp_tomorrow)
        datetime_end = datetime.strptime(enddate, '%Y-%m-%d %H:%M:%S')
        if datetime_tomorrow<=datetime_end:
            return datetime_tomorrow
        return False

class RedEnvelopeWrapper(object):
    '''
    对红包一些操作的封装，生成红包，获取红包数量等
    '''
    def __init__(self, general, vip):
        self._general = general or []
        self._vip = vip or []
        self._all = strutil.cloneData(self._general)
        self._all.extend(self._vip)
        self._randomsequence = None

    def getItemConfigWithPath(self, path):
        for item in self._all:
            itemId = item.get("itemId")
            if path.endswith(itemId):
                return item

    def reset(self, datetime_point):
        '''
        重新生成红包，清空上次的领取剩余，重新满池
        :param datetime_point 红包领取时间点
        '''
        r = Redis.readMixHash("dizhu:hongbaorecord", str(datetime_point))
        if r:
            return False

        general_listmap = {} # {"user:coupon":[...], "item:1007":[...], ...}
        for item in self._general:
            itemtype = item.get("type")
            num = item.get("num")
            if itemtype == "random.split":
                total = item.get("total")
                minv = item.get("min")
                general_listmap[item.get("itemId")] = Random.getNormalDistributionRandomSequence(total,minv,num)
            elif itemtype == "random.fixed":
                count = item.get("count")
                general_listmap[item.get("itemId")] = [count for _ in xrange(num)]

        vip_listmap = {} # {"user:coupon":[...], "item:1007":[...], ...}
        for item in self._vip:
            itemtype = item.get("type")
            num = item.get("num")
            if itemtype == "random.split":
                total = item.get("total")
                minv = item.get("min")
                vip_listmap[item.get("itemId")] = Random.getNormalDistributionRandomSequence(total,minv,num)
            elif itemtype == "random.fixed":
                count = item.get("count")
                vip_listmap[item.get("itemId")] = [count for _ in xrange(num)]

        normaljsonstr = json.dumps(general_listmap)
        vipjsonstr = json.dumps(vip_listmap)
        result = daobase.executeMixLua(_REDIS_LUA_PUSHLIST_NAME, 3, normaljsonstr, vipjsonstr, str(datetime_point))
        ftlog.debug("RedEnvelopeWrapper.reset: result=", result)

        return result

    def getCount(self):
        return daobase.executeMixLua(_REDIS_LUA_GETCOUNT_NAME, 1, "all")
    def getGeneralCount(self):
        return daobase.executeMixLua(_REDIS_LUA_GETCOUNT_NAME, 1, "general")


class TYActivityDdzRedEnvelope(TYActivity):
    '''
    地主基金活动界面处理类
    此类每次请求都会重新构造对象
    '''
    TYPE_ID = 6001
    TYPE_ID_PC = 6002

    def __init__(self, dao, clientConfig, serverConfig):
        super(self.__class__, self).__init__(dao, clientConfig, serverConfig)
        self._dao = dao
        self._serverConf = serverConfig
        self._clientConf = clientConfig
        self._dataWrapper = DataWrapper(serverConfig)
        
        ftlog.debug("TYActivityDdzRedEnvelope.__init__", 
                    clientConfig.get('id'), 
                    self.checkOperative(), 
                    serverConfig, 
                    clientConfig)
        
        if not self.checkOperative():
            return

        if not _redenvelopeWrapper:
            ftlog.debug("TYActivityDdzRedEnvelope. global _redenvelopeWrapper")
            global _redenvelopeWrapper
            general = Tool.dictGet(clientConfig, "config.activate.generalRedEnvelope")
            vip = Tool.dictGet(clientConfig, "config.activate.vipRedEnvelope")
            _redenvelopeWrapper = RedEnvelopeWrapper(general, vip)

        if not DdzRedEnvelope._timelist:
            ftlog.debug("TYActivityDdzRedEnvelope. DdzRedEnvelope._timelist")
            timelist = Tool.dictGet(clientConfig, "config.activate.timeList")
            datetime_start = datetime.strptime(serverConfig.get("start"), "%Y-%m-%d %H:%M:%S")
            datetime_end = datetime.strptime(serverConfig.get("end"), "%Y-%m-%d %H:%M:%S")
            DdzRedEnvelope._timelist = self.getTimePointListInRange(timelist, datetime_start, datetime_end)
            DdzRedEnvelope._datetime_start = datetime_start
            DdzRedEnvelope._datetime_end = datetime_end

            DdzRedEnvelope.onHeartBeat(None)

    def getTimePointListInRange(self, timelist, datetime_start, datetime_end):
        '''
        获得在指定时间范围内的时间点(datetime对象)列表
        :param timelist: ["11:20:00", "17:30:00"]
        :param datetime_start: datetime对象,开始时间
        :param datetime_end: datetime对象,结束时间
        :return: [datetime, datetime, ...]
        '''
        cursor = datetime(datetime_start.year, datetime_start.month, datetime_start.day, 0, 0, 0)

        # 生成在活动范围内的领取的时间点列表
        r = []
        while cursor <= datetime_end:
            for x in timelist:
                t = datetime.strptime(x, "%H:%M:%S").time()
                d = datetime(cursor.year, cursor.month, cursor.day, t.hour, t.minute, t.second)
                if d >= datetime_start and d <= datetime_end:
                    r.append(d)
            cursor = datetime.fromtimestamp(Tool.datetimeToTimestamp(cursor) + 24*60*60)
        r.sort()
        return r

    def sendLedIfNeed(self, userId, itemconf, count):
        '''
        如果满足情况则,发送LED
        :param itemconf: 红包奖励配置项{"type":"random.fixed", "itemId": "item:2003", "desc":"记牌器", "num":500, "count":1, "led": "led1"}
        :param count: 拆红包真实领取的物品个数
        :return: Bool, 是否发送
        '''
        settingkey = itemconf.get("led", False)
        if not settingkey:
            return False

        ftlog.debug("TYActivityDdzRedEnvelope.sendLedIfNeed: settingkey=", settingkey)
        clientconf = self._clientConf
        settingmap = Tool.dictGet(clientconf, "config.activate.ledSetting")
        if not settingmap:
            return False
        ftlog.debug("TYActivityDdzRedEnvelope.sendLedIfNeed: settingmap=", settingmap)

        setting = settingmap.get(settingkey)
        if not setting:
            return False
        ftlog.debug("TYActivityDdzRedEnvelope.sendLedIfNeed: setting=", setting)

        text = setting.get("text")
        if (not text) or len(text) <= 0:
            return False

        ftlog.debug("TYActivityDdzRedEnvelope.sendLedIfNeed: text=", text, "mincount", setting.get("min", 0))
        mincount = setting.get("min", 0)
        if count >= mincount:
            leddict = { "assets":str(itemconf.get('desc')),
                        "count":str(count),
                        "userId":str(userId),
                        "nickname": str(UserInfo.getNickname(userId))}
            text = strutil.replaceParams(text, leddict)
            Tool.sendLed(text)
            return True
        return False

    def getConfigForClient(self, gameId, userId, clientId):
        '''
        获取客户端要用的活动配置，由TYActivitySystemImpl调用
        '''
        clientconf = self._clientConf
        serverconf = self._serverConf
        ftlog.debug("TYActivityDdzRedEnvelope.getConfigForClient: userId=", userId, "gameId=", gameId,  "clientId", clientId, "serverconf=",serverconf, "clientconf=", clientconf)

        # activityId = "activity_new_red_envelope"
        # self.update(userId, gameId, clientId, activityId)
        # self.get(userId, gameId, clientId, activityId)
        return clientconf

    def handleRequest(self, msg):
        userId = msg.getParam('userId')
        gameId = msg.getParam('gameId')
        clientId = msg.getParam("clientId")
        activityId = msg.getParam("activityId")

        ftlog.debug("TYActivityDdzRedEnvelope.handleRequest: enter userId=", userId, "msg=", msg)

        action = msg.getParam("action")

        if action == "ddz.redenvelope.update":
            return self.update(userId, gameId, clientId, activityId)
        elif action == "ddz.redenvelope.get":
            return self.get(userId, gameId, clientId, activityId)
        else:
            ftlog.debug("TYActivityDdzRedEnvelope.handleRequest: userId=", userId, "action not match")
            return {"isOK":False}

    def update(self, userId, gameId, clientId, activityId):
        '''
        未领取 + 有剩余 = 显示可领取
        未领取 + 无剩余 = 显示倒计时
        已领取 + xxx   = 显示倒计时
        {'isOK': True, 'nowTime': 1452161428.0, 'nextTime': 1452218400.0, 'hasGet': False, 'isRemain': True, 'tip': tip}
        '''
        clientconf = self._clientConf
        serverconf = self._serverConf
        dataWrapper = self._dataWrapper

        timelist = Tool.dictGet(clientconf, "config.activate.timeList")
        startdate = serverconf.get("start")
        enddate = serverconf.get("end")

        #检测是否过期
        if not self.checkOperative():
            tip = Tool.dictGet(clientconf, "config.activate.outdateTip")
            return {"isOK":False, "tip": tip} #活动已经过期

        nowstamp = Tool.datetimeToTimestamp(datetime.now())
        rconf = {"isOK":True, "nowTime":nowstamp}

        # 上次领取的物品
        itemconf = dataWrapper.getLastGetItem(userId)
        if itemconf:
            rconf.update({"itemDesc": itemconf.get("itemDesc"), "itemCount":itemconf.get("count")})

        arrive_timepoint = dataWrapper.getLastestTimePoint(timelist,startdate)
        next_timepoint = dataWrapper.getNextTimePoint(timelist, enddate)

        if next_timepoint: # 若存在下一个时间点
            rconf["nextTime"] = Tool.datetimeToTimestamp(next_timepoint)

        count = 0
        if arrive_timepoint: #已经达到至少一个领取时间点
            has_get = dataWrapper.hasGet(userId, arrive_timepoint) # 是否已经领取
            isvip = (UserInfo.getVipLevel(userId) > 0)
            if isvip:
                count = _redenvelopeWrapper.getCount() # 剩余红包数量
            else:
                count = _redenvelopeWrapper.getGeneralCount() # 非VIP只检测普通红包数量
            rconf.update({"hasGet":has_get, "isRemain":(count>0)})

            # 上次领取时间在昨天?
            today = datetime.now().replace(None,None,None,0,0,0,0)
            if arrive_timepoint < today:
                rconf.update({"isFirst":True})

        else: #未达到领取时间
            rconf.update({"hasGet":False, "isRemain":False, "isFirst":True})


        ftlog.debug("TYActivityDdzRedEnvelope.update: userId", userId,"rconf=", rconf, "count=", count)
        return rconf

    def get(self, userId, gameId, clientId, activityId):
        '''
        {'isOK': True, 'nowTime': 1452161428.0, 'nextTime': 1452218400.0, 'hasGet': False, 'isRemain': True, 'tip': tip}
        '''
        clientconf = self._clientConf
        serverconf = self._serverConf
        dataWrapper = self._dataWrapper

        timelist = Tool.dictGet(clientconf, "config.activate.timeList")
        startdate = serverconf.get("start")
        enddate = serverconf.get("end")

        #检测是否过期
        if not self.checkOperative():
            tip = Tool.dictGet(clientconf, "config.activate.outdateTip")
            return {"isOK":False, "tip": tip} #活动已经过期

        nowstamp = Tool.datetimeToTimestamp(datetime.now())
        rconf = {"isOK":True, "nowTime":nowstamp}

        arrive_timepoint = dataWrapper.getLastestTimePoint(timelist,startdate)
        next_timepoint = dataWrapper.getNextTimePoint(timelist, enddate)

        if next_timepoint: # 若存在下一个时间点
            rconf["nextTime"] = Tool.datetimeToTimestamp(next_timepoint)

        if not arrive_timepoint: #未达到领取时间
            tip = Tool.dictGet(clientconf, "config.activate.cannotGetTip")
            rconf.update({"isOK":False, "tip": tip})
            return rconf

        has_get = dataWrapper.hasGet(userId, arrive_timepoint) # 是否已经领取
        ftlog.debug("TYActivityDdzRedEnvelope.get: userId", userId," has_get=",has_get)
        if has_get: # 已经领取了
            tip = Tool.dictGet(clientconf, "config.activate.alreadyGetTip")
            rconf.update({"isOK":False, "tip": tip})
            return rconf

        isvip = (UserInfo.getVipLevel(userId) > 0)
        result = daobase.executeMixLua(_REDIS_LUA_GET_NAME, 2, isvip, random.randint(1,10000000))
        ftlog.debug("TYActivityDdzRedEnvelope.get: userId", userId," result=",result, "isvip=", isvip)

        if not result:
            tip = Tool.dictGet(clientconf, "config.activate.emptyGetTip")
            rconf.update({"isOK":False, "tip": tip})
            return rconf

        # 领取红包的结果
        result_count = result[1]

        # 领取红包项的配置
        itemconf = _redenvelopeWrapper.getItemConfigWithPath(result[0])
        result_name = str(itemconf.get('desc'))

        # 构造邮箱信息
        assetsdict = {"assets":result_name, "count":str(result_count)}
        mail = Tool.dictGet(clientconf, "config.mail")
        mail = strutil.replaceParams(mail, assetsdict)

        # 发送奖励和邮箱信息
        assets = {'itemId':itemconf.get("itemId"), 'count':result_count}
        UserBag.sendAssetsToUser(6, userId, assets, 'DDZ_ACT_REDENVELOPE', mail)

        # 发送LED的(条件满足)
        ok = self.sendLedIfNeed(userId, itemconf, result_count)
        ftlog.debug("TYActivityDdzRedEnvelope.get: sendLed-> userId=", userId, " ok=",ok)

        # 记录领取物品
        assets.update({"itemDesc": itemconf.get('desc')})
        dataWrapper.markGet(userId, arrive_timepoint, assets)

        # 日志记录领取
        ftlog.debug("TYActivityDdzRedEnvelope:Get, ", "userId", userId,
                                                    "gettime", str(datetime.now()),
                                                    "assets", assets.get("itemId"),
                                                    "count", assets.get("count"),
                                                    "desc", assets.get("itemDesc"),
                                                    "detail", assets)

        # 构造协议信息
        itemtip = Tool.dictGet(clientconf, "config.activate.itemGetTip")
        itemtip = strutil.replaceParams(itemtip, assetsdict)
        rconf.update({"isOK":True, "itemDesc": result_name, "itemCount": result_count, "tip":itemtip})
        ftlog.debug("TYActivityDdzRedEnvelope.get: userId=", userId, " itemconf=",itemconf, "arrive_timepoint=", str(arrive_timepoint), "rconf=", rconf)

        return rconf

#
# 配置更新
#

_inited = None

def _onConfChangedReloadActivity(actconf):
    ftlog.debug('_onConfChangedReloadActivity', actconf["typeid"], actconf)
    activityClass = TYActivityRegister.findClass(actconf["typeid"])
    ftlog.debug('_onConfChangedReloadActivity', actconf["typeid"], activityClass)
    if not activityClass:
        return
    serverConf = actconf.pop("server_config")
    clientConf = actconf
    activityClass(activitySystem._dao, clientConf, serverConf)
#     activitySystem._activities[actconf.get('id')] = actobj


def _reloadConf():
    global _redenvelopeWrapper
    _redenvelopeWrapper = None
    DdzRedEnvelope._timelist = None
    
    for k in TYActivityDaoImpl.activitiesConf:
        actconf = TYActivityDaoImpl.activitiesConf[k]
        ftlog.debug('DdzRedEnvelope._reloadConf: typeid', actconf.get('typeid'))
        if actconf.get('typeid') == TYActivityDdzRedEnvelope.TYPE_ID:
            ok = Tool.checkNow(actconf.get('server_config',{}).get('start'), actconf.get('server_config',{}).get('end'))
            if not ok:
                continue
            _onConfChangedReloadActivity(actconf)

def _onConfChanged(event):
    if event.isChanged('game:6:activity:tc'):
        ftlog.debug('DdzRedEnvelope._onConfChanged')
        _reloadConf()

def _initialize():
    ftlog.debug('ddz redenvelope initialize begin')
    global _inited
    if not _inited:
        _inited = True
        _reloadConf()
        pkeventbus.globalEventBus.subscribe(EventConfigure, _onConfChanged)
    ftlog.debug('ddz redenvelope initialize end')


_initialize()

