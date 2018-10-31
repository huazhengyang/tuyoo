# -*- coding=utf-8 -*-
'''
Created on 16-2-14

@author: luwei
'''
from poker.entity.biz.activity.activity import TYActivity
import freetime.util.log as ftlog
import random
from poker.util import strutil
from datetime import datetime
from dizhu.activities.toolbox import Tool, Redis, UserInfo, Random, UserBag
from poker.entity.dao import daobase
import json


class PacketRedisInterface(object):
    setpacketdata_key = "ddz.luckypacket.setpacketdata"
    setpacketdata = '''
    local datapath = KEYS[1]
    local packetdata = KEYS[2]
    local cursordata = KEYS[5]

    local d = redis.call('GET', datapath)
    if d then return d
    end
    redis.call('SET', datapath, packetdata)

    local cursordata = cjson.decode(cursordata)
    local vip_cursordata = cursordata['vip'] or {}
    local vip_cursorpath = KEYS[3]
    local nor_cursordata = cursordata['nor'] or {}
    local nor_cursorpath = KEYS[4]
    for k,v in pairs(vip_cursordata) do
        redis.call('HSET', vip_cursorpath, k, v)
    end
    for k,v in pairs(nor_cursordata) do
        redis.call('HSET', nor_cursorpath, k, v)
    end

    return packetdata
    '''

    selectpacket_key = "ddz.luckypacket.selectpacket"
    selectpacket = '''
    local numrange = function(num, l, r)
        return math.fmod(num, (r - l + 1)) + l -- range[l, r]
    end

    local randomitems = function(rnd, itemmap)
        local count = 0
        for k,v in pairs(itemmap) do
            if tonumber(v) > 0 then
                count = count + v
            end
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
    local vip_cursorpath = KEYS[2]
    local nor_cursorpath = KEYS[3]
    local rndnum = KEYS[4]

    local items = {}
    local isitemvip = 0
    if isvip == 'True' then
        isitemvip = 1
        items = redis.call("HGETALL", vip_cursorpath)
    end
    if #items <= 0 then
        isitemvip = 0
        items = redis.call("HGETALL", nor_cursorpath)
    end

    if #items <= 0 then return false
    end

    local itemmap = {}
    for i=1, #items ,2 do
        itemmap[items[i]] = items[i+1]
    end

    local item = randomitems(rndnum, itemmap)

    local cursorpath = nor_cursorpath
    if isitemvip == 1 then
        cursorpath = vip_cursorpath
    end
    local r = redis.call('HINCRBY', cursorpath, item, -1)
    if r <= 0 then
        redis.call('HDEL', cursorpath, item)
    end
    return {item, isitemvip, r}
    '''

    getpacketnumber_key = "ddz.luckypacket.getpacketnumber"
    getpacketnumber = '''
    local path1 = KEYS[1]
    local path2 = KEYS[2]
    local getcount = function(path)
        local items = redis.call("HGETALL", path)
        if items == nil then return 0
        end
        local count = 0
        for i=1, #items ,2 do
            local num = items[i+1] or 0
            if tonumber(num) > 0 then
                count = count + num
            end
        end
        return count
    end

    local count = 0
    count = count + getcount(path1)
    count = count + getcount(path2)
    return count
    '''

    @classmethod
    def loadLuaScripts(cls):
        scripts = {
            cls.setpacketdata_key: cls.setpacketdata,
            cls.selectpacket_key: cls.selectpacket,
            cls.getpacketnumber_key: cls.getpacketnumber
        }
        for x in scripts:
            daobase.loadLuaScripts(x, scripts[x])

    @classmethod
    def getMixKeypath(cls, bankId, issue, suffix):
        '''
        dizhu:luckypacket:6001:20160214155959:data
        dizhu:luckypacket:6001:20160214155959:cursor:vip
        dizhu:luckypacket:6001:20160214155959:cursor:nor
        '''
        return "dizhu:luckypacket:" + str(bankId) + ":" + str(issue) + ":" + suffix

    @classmethod
    def getGamedataKey(cls, bankId, dt):
        '''
        @:param dt datetime对象,一般使用活动的起始时间
        dizhu.luckypacket.6001.20160214155959
        '''
        activity_issue = "%d%02d%02d%02d%02d%02d" % (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
        return "dizhu.luckypacket." + str(bankId) + "." + activity_issue

    @classmethod
    def getPacketsData(cls, bankId, issue):
        '''
        获得红包Json数据,多进程利用Redis进行同步生成的红包数据,用于保持多进程的红包数据一致
        @:param issue 期号,格式20160214155959,每次抢红包都是一期
        @:return 若不存在则返回None
        '''
        path = cls.getMixKeypath(bankId, issue, "data")
        packets = daobase.executeMixCmd("GET", path)
        return packets

    @classmethod
    def setPacketData(cls, bankId, issue, packet_data, count_data):
        '''
        设置红包内容,用于多进程同步
        多个进程可能同时有多个设置,但是保证返回的是同一个
        注意:设置的data未必是返回的数据
        @:return 真实设置成功的红包数据,可能是其他进程设置成功的
        '''
        data_path = cls.getMixKeypath(bankId, issue, "data")
        vip_cursor_path = cls.getMixKeypath(bankId, issue, "cursor:vip")
        nor_cursor_path = cls.getMixKeypath(bankId, issue, "cursor:nor")
        packets_data_str = json.dumps(packet_data)
        cursor_data_str = json.dumps(count_data)

        return daobase.executeMixLua(cls.setpacketdata_key, 5, data_path, packets_data_str, vip_cursor_path, nor_cursor_path, cursor_data_str)

    @classmethod
    def getNormalPacketNumber(cls, bankId, issue):
        '''
        获得普通红包剩余数量
        '''
        nor_cursor_path = cls.getMixKeypath(bankId, issue, "cursor:nor")
        return daobase.executeMixLua(cls.getpacketnumber_key, 1, nor_cursor_path)

    @classmethod
    def getVipPacketNumber(cls, bankId, issue):
        '''
        获得VIP专属红包剩余数量
        '''
        vip_cursor_path = cls.getMixKeypath(bankId, issue, "cursor:vip")
        return daobase.executeMixLua(cls.getpacketnumber_key, 1, vip_cursor_path)

    @classmethod
    def getAllPacketNumber(cls, bankId, issue):
        '''
        获得所有红包剩余数量
        '''
        vip_cursor_path = cls.getMixKeypath(bankId, issue, "cursor:vip")
        nor_cursor_path = cls.getMixKeypath(bankId, issue, "cursor:nor")
        return daobase.executeMixLua(cls.getpacketnumber_key, 2, vip_cursor_path, nor_cursor_path)

    @classmethod
    def selectPacket(cls, bankId, issue, isVIP):
        '''
        按照规则随机领取一个红包,若红包已经领光,则返回None
        规则:VIP用户优先领取VIP专属红包,VIP专属红包领光后才领取普通红包
        '''
        vip_cursor_path = cls.getMixKeypath(bankId, issue, "cursor:vip")
        nor_cursor_path = cls.getMixKeypath(bankId, issue, "cursor:nor")

        return daobase.executeMixLua(cls.selectpacket_key, 4, isVIP, vip_cursor_path, nor_cursor_path, random.randint(1,100000000))
    
    @classmethod
    def getUserActivityData(cls, bankId, userId):
        '''
        获取玩家活动记录数据,存储在db7/db8中的gamedata:6:userId中
        :return: dict
        '''
        conf = ConfigDatabase.getServerConfig(bankId)
        activity_start = conf.get('start')
        key = cls.getGamedataKey(bankId, Tool.datetimeFromString(activity_start))
        return Redis.readJson(userId, key)

    @classmethod
    def setUserActivityData(cls, bankId, userId, data):
        '''
        存储玩家活动记录数据,存储在db7/db8中的gamedata:6:userId中
        '''
        conf = ConfigDatabase.getServerConfig(bankId)
        activity_start = conf.get('start')
        key = cls.getGamedataKey(bankId, Tool.datetimeFromString(activity_start))
        Redis.writeJson(userId, key, data)


class ConfigDatabase(object):
    '''
    用来记录配置数据，用于支持多开造成的，存在多份配置
    '''
    conf = {}
    services_times = {}

    @classmethod
    def addConfig(cls, bankId, clientconf, serverconf):
        '''
        添加配置记录
        '''
        conf = cls.conf
        oldconf = conf.get(bankId)
        conf[bankId] = {"client":clientconf, "server":serverconf}
        if oldconf != conf[bankId]:
            cls.services_times[bankId] = None

    @classmethod
    def getClientConfig(cls, bankId):
        '''
        获得指定bankId的client配置,若没有返回None
        '''
        return cls.conf.get(bankId, {}).get("client")

    @classmethod
    def getServerConfig(cls, bankId):
        '''
        获得指定bankId的server配置,若没有返回None
        '''
        return cls.conf.get(bankId, {}).get("server")

    @classmethod
    def getTimeServices(cls, bankId):
        if cls.services_times.get(bankId):
            return cls.services_times.get(bankId)

        clientconf = cls.getClientConfig(bankId)
        serverconf = cls.getServerConfig(bankId)

        timelist   = Tool.dictGet(clientconf, 'config.activate.timeList')
        conf_start = serverconf.get('start')
        conf_end   = serverconf.get('end')
        datetime_start = datetime.strptime(conf_start, '%Y-%m-%d %H:%M:%S')
        datetime_end   = datetime.strptime(conf_end, '%Y-%m-%d %H:%M:%S')

        services_time = PacketTimeHelper(timelist, datetime_start, datetime_end)
        cls.services_times[bankId] = services_time
        return services_time

    @classmethod
    def getBankId(cls, clientconf):
        '''
        获取bankId,库的id,用于区分红包库存,若不存在bankid则用typeid表示
        '''
        return clientconf["bankid"] or clientconf["typeid"]

class PacketTimeHelper(object):
    '''
    用于记录红包发放时间点，并提供对时间点的便利操作
    '''
    def __init__(self, timelist, datetime_start, datetime_end):
        self._datetime_start = datetime_start
        self._datetime_end = datetime_end

        self._timelist = []
        for s in timelist:
            t = datetime.strptime(s, "%H:%M:%S").time()
            self._timelist.append(t)
        self._timelist.sort()

    def getLastlyReachedDatetime(self):
        '''
        获得已经到达的最后的一个时间点，若未达到今天时间点则返回昨天最后的时间点(前提是昨天时间点在开始时间之后，否则返回False)
        若活动已结束或者未开始,则返回False
        :return datetime/False
        '''
        res = None
        dnow = datetime.now()
        tnow = dnow.time()

        if dnow < self._datetime_start or dnow > self._datetime_end:
            return False

        for t in self._timelist:
            if tnow >= t:
                res = t
        if res:
            return datetime(dnow.year, dnow.month, dnow.day, res.hour, res.minute, res.second)

        last_time = self._timelist[-1]
        datetime_today = datetime(dnow.year, dnow.month, dnow.day, last_time.hour, last_time.minute, last_time.second)
        timestamp_yesterday = Tool.datetimeToTimestamp(datetime_today) - 24*60*60
        datetime_yesterday = datetime.fromtimestamp(timestamp_yesterday)
        datetime_start = self._datetime_start

        if datetime_yesterday>=datetime_start:
            return datetime_yesterday
        return False

    def getFirstUnreachedDatetime(self):
        '''
        获得未到达的最近的一个时间点，若今天没有时间点则返回明天第一个时间点(前提是明天的领取时间点在活动结束之前，否则返回False)
        :return datetime/False
        '''
        res = None
        dnow = datetime.now()
        now = dnow.time()

        if dnow < self._datetime_start or dnow > self._datetime_end:
            return False

        for t in self._timelist:
            if now < t:
                res = t
                break
        if res:
            return datetime(dnow.year, dnow.month, dnow.day, res.hour, res.minute, res.second)

        first_time = self._timelist[0]
        datetime_today = datetime(dnow.year, dnow.month, dnow.day, first_time.hour, first_time.minute, first_time.second)
        timestamp_tomorrow = Tool.datetimeToTimestamp(datetime_today) + 24*60*60
        datetime_tomorrow = datetime.fromtimestamp(timestamp_tomorrow)
        datetime_end = self._datetime_end
        if datetime_tomorrow<=datetime_end:
            return datetime_tomorrow
        return False

    def getCurrentIssueNumber(self):
        '''
        获得当前这一期的期号,若未达到第一期的时间或者没有则返回None
        '''
        getdt = self.getLastlyReachedDatetime()
        if not getdt:
            return
        return "%d%02d%02d%02d%02d%02d" % (getdt.year, getdt.month, getdt.day, getdt.hour, getdt.minute, getdt.second)

    def getIssueNumber(self, dt):
        '''
        获得当前这一期的期号,若未达到第一期的时间或者没有则返回None
        '''
        getdt = dt
        if not dt:
            return
        return "%d%02d%02d%02d%02d%02d" % (getdt.year, getdt.month, getdt.day, getdt.hour, getdt.minute, getdt.second)


class LuckyPacketHelper(object):
    '''
    data = {
        bankId: { issue: packets_data }
    }
    '''
    data = {}

    @classmethod
    def getPacket(cls, bankId, issue, isVIP):
        '''
        领取一个红包,若已经领光了则返回False
        '''
        packets_data = cls.publishIfNeed(bankId, issue)

        # 领取红包
        ret = PacketRedisInterface.selectPacket(bankId, issue, isVIP)
        if not ret:
            return False
        ftlog.debug("LuckyPacketHelper.getPacket: bankId=", bankId, "issue=", issue, "isvip=", isVIP, "ret=", ret)
        itemId = ret[0]
        isVipItem = bool(ret[1])
        cursor = int(ret[2])

        itemlist = packets_data.get('nor')
        if isVipItem:
            itemlist = packets_data.get('vip')

        count = itemlist.get(itemId,[])[cursor]
        return { "isVipItem": isVipItem, "itemId": itemId, "count": count }

    @classmethod
    def publishIfNeed(cls, bankId, issue):
        '''
        自动检测是否已经生成,若没有生成则直接生成
        :return 返回生成的红包数据
        '''
        d = cls.data.get(bankId, {})
        packets_data = d.get(issue)
        if not packets_data:
            packets_data = cls._generatePackets(bankId, issue)
            d[issue] = packets_data
            cls.data[bankId] = d
        return packets_data

    @classmethod
    def _generatePackets(cls, bankId, issue):
        '''
        生成红包,并存储到redis中,多进程利用redis同步生成的红包数据
        '''
        clientconf = ConfigDatabase.getClientConfig(bankId)
        nor_items = Tool.dictGet(clientconf, "config.activate.generalRedEnvelope")
        vip_items = Tool.dictGet(clientconf, "config.activate.vipRedEnvelope")

        # {"user:coupon":[...], "item:1007":[...], ...}
        nor_packets = {}
        nor_packets_num = {} # 每个道具的数量
        for item in nor_items:
            itemtype = item.get("type")
            itemId = item.get("itemId")
            num = item.get("num")
            if itemtype == "random.split":
                total = item.get("total")
                minv = item.get("min")
                nor_packets[itemId] = Random.getNormalDistributionRandomSequence(total,minv,num)
            elif itemtype == "random.fixed":
                count = item.get("count")
                nor_packets[itemId] = [count for _ in xrange(num)]
            nor_packets_num[itemId] = num

        # {"user:coupon":[...], "item:1007":[...], ...}
        vip_packets = {}
        vip_packets_num = {} # 每个道具的数量
        for item in vip_items:
            itemtype = item.get("type")
            itemId = item.get("itemId")
            num = item.get("num")
            if itemtype == "random.split":
                total = item.get("total")
                minv = item.get("min")
                vip_packets[itemId] = Random.getNormalDistributionRandomSequence(total,minv,num)
            elif itemtype == "random.fixed":
                count = item.get("count")
                vip_packets[itemId] = [count for _ in xrange(num)]
            vip_packets_num[itemId] = num

        packets_data = {"nor":nor_packets, "vip":vip_packets}
        count_data = {"nor":nor_packets_num, "vip":vip_packets_num}
        data = PacketRedisInterface.setPacketData(bankId, issue, packets_data, count_data)
        return json.loads(data)

    @classmethod
    def isUserGet(cls, bankId, userId, issue):
        '''
        判断用户是否已经领取
        '''
        d = PacketRedisInterface.getUserActivityData(bankId, userId)
        if d.get(issue):
            return True
        return False

    @classmethod
    def setUserGet(cls, bankId, userId, issue, iteminfo):
        '''
        设置玩家领取的物品,若玩家已经领取则返回False
        :param issue: 期号
        :param iteminfo: 领取的物品信息
        '''
        d = PacketRedisInterface.getUserActivityData(bankId, userId)
        if d.get(issue):
            return False
        d[issue] = iteminfo
        PacketRedisInterface.setUserActivityData(bankId, userId, d)

    @classmethod
    def getUserGetHistory(cls, bankId, userId, issue):
        '''
        获取指定期号的红包领取物品,若没有则返回None
        '''
        d = PacketRedisInterface.getUserActivityData(bankId, userId)
        return d.get(issue)

    @classmethod
    def getUserGetLastlyHistory(cls, bankId, userId):
        '''
        获取用户领取的最近一次的领取内容, 若没有则返回None
        '''
        d = PacketRedisInterface.getUserActivityData(bankId, userId)
        if len(d) <= 0:
            return
        allissue = d.keys()
        allissue.sort()
        lastly = allissue[-1]
        return d.get(lastly)


PacketRedisInterface.loadLuaScripts()

class LuckyPacket(TYActivity):
    '''
    地主基金活动界面处理类
    此类每次请求都会重新构造对象
    '''
    TYPE_ID = 6006
    TYPE_ID_PC = 6007

    def __init__(self, dao, clientConfig, serverConfig):
        ftlog.debug("LuckyPacket.__init__")
        self._dao = dao
        self._serverConf = serverConfig
        self._clientConf = clientConfig

        bankId = ConfigDatabase.getBankId(self._clientConf)
        ConfigDatabase.addConfig(bankId, clientConfig, serverConfig)

        # 检测是否需要生成红包,直接生成红包
        timeservices = ConfigDatabase.getTimeServices(bankId)
        current_issue = timeservices.getCurrentIssueNumber()
        if current_issue:
            d = LuckyPacketHelper.publishIfNeed(bankId, current_issue)
            ftlog.debug("LuckyPacket.__init__: publish", "current_issue=", current_issue, "data=", d)

    def getConfigForClient(self, gameId, userId, clientId):
        clientconf = self._clientConf
        serverconf = self._serverConf
        ftlog.debug("LuckyPacket.getConfigForClient: userId=", userId, "gameId=", gameId,  "clientId", clientId, "serverconf=",serverconf, "clientconf=", clientconf)
        return clientconf

    def handleRequest(self, msg):
        userId = msg.getParam('userId')
        gameId = msg.getParam('gameId')
        clientId = msg.getParam("clientId")
        activityId = msg.getParam("activityId")
        bankId = ConfigDatabase.getBankId(self._clientConf)
        ftlog.debug("LuckyPacket.handleRequest: enter userId=", userId, "msg=", msg)

        action = msg.getParam("action")
        if action == "ddz.redenvelope.update":
            return self.update(userId, gameId, clientId, activityId, bankId)
        elif action == "ddz.redenvelope.get":
            return self.get(userId, gameId, clientId, activityId, bankId)
        else:
            ftlog.debug("LuckyPacket.handleRequest: userId=", userId, "action not match")
            return {"isOK":False}

    def update(self, userId, gameId, clientId, activityId, bankId):
        '''
        未领取 + 有剩余 = 显示可领取
        未领取 + 无剩余 = 显示倒计时
        已领取 + xxx   = 显示倒计时
        {'isOK': True, 'nowTime': 1452161428.0, 'nextTime': 1452218400.0, 'hasGet': False, 'isRemain': True, 'tip': tip}
        '''
        clientconf = self._clientConf

        #检测是否过期
        if not self.checkOperative():
            tip = Tool.dictGet(clientconf, "config.activate.outdateTip")
            return {"isOK":False, "tip": tip} #活动已经过期

        nowstamp = Tool.datetimeToTimestamp(datetime.now())
        rconf = {"isOK":True, "nowTime":nowstamp}
        iteminfo = LuckyPacketHelper.getUserGetLastlyHistory(bankId, userId)
        if iteminfo:
            rconf.update({"itemDesc": iteminfo.get("itemDesc"), "itemCount":iteminfo.get("count")})

        timeservices = ConfigDatabase.getTimeServices(bankId)
        next_timepoint = timeservices.getFirstUnreachedDatetime()
        if next_timepoint:
            rconf["nextTime"] = Tool.datetimeToTimestamp(next_timepoint)

        arrive_timepoint = timeservices.getLastlyReachedDatetime()
        if arrive_timepoint: #已经达到至少一个领取时间点
            current_issue = timeservices.getIssueNumber(arrive_timepoint)
            isget = LuckyPacketHelper.isUserGet(bankId, userId, current_issue)
            isvip = (UserInfo.getVipLevel(userId) > 0)
            if isvip:
                count = PacketRedisInterface.getAllPacketNumber(bankId, current_issue) # 剩余红包数量
            else:
                count = PacketRedisInterface.getNormalPacketNumber(bankId, current_issue) # 非VIP只检测普通红包数量
            rconf.update({"hasGet":isget, "isRemain":(count>0)})

            # 上次领取时间在昨天?
            today = datetime.now().replace(None,None,None,0,0,0,0)
            if arrive_timepoint < today:
                rconf.update({"isFirst":True})

        else: #未达到领取时间
            rconf.update({"hasGet":False, "isRemain":False, "isFirst":True})

        ftlog.debug("LuckyPacket.update: userId=", userId, "bankId=", bankId, "rconf=", rconf, "count=", count)
        return rconf

    def get(self, userId, gameId, clientId, activityId, bankId):
        '''
        {'isOK': True, 'nowTime': 1452161428.0, 'nextTime': 1452218400.0, 'hasGet': False, 'isRemain': True, 'tip': tip}
        '''
        clientconf = self._clientConf

        #检测是否过期
        if not self.checkOperative():
            tip = Tool.dictGet(clientconf, "config.activate.outdateTip")
            return {"isOK":False, "tip": tip} #活动已经过期

        nowstamp = Tool.datetimeToTimestamp(datetime.now())
        rconf = {"isOK":True, "nowTime":nowstamp}

        timeservices = ConfigDatabase.getTimeServices(bankId)
        next_timepoint = timeservices.getFirstUnreachedDatetime()
        if next_timepoint:
            rconf["nextTime"] = Tool.datetimeToTimestamp(next_timepoint)

        arrive_timepoint = timeservices.getLastlyReachedDatetime()
        if not arrive_timepoint: #未达到领取时间
            tip = Tool.dictGet(clientconf, "config.activate.cannotGetTip")
            rconf.update({"isOK":False, "tip": tip})
            return rconf

        current_issue = timeservices.getIssueNumber(arrive_timepoint)
        isget = LuckyPacketHelper.isUserGet(bankId, userId, current_issue)
        if isget: # 已经领取了
            tip = Tool.dictGet(clientconf, "config.activate.alreadyGetTip")
            rconf.update({"isOK":False, "tip": tip})
            return rconf

        isvip = (UserInfo.getVipLevel(userId) > 0)
        iteminfo = LuckyPacketHelper.getPacket(bankId, current_issue, isvip)
        ftlog.debug("TYActivityDdzRedEnvelope.get: userId", userId," iteminfo=",iteminfo, "isvip=", isvip)
        if not iteminfo:
            tip = Tool.dictGet(clientconf, "config.activate.emptyGetTip")
            rconf.update({"isOK":False, "tip": tip})
            return rconf

        itemId = iteminfo.get('itemId')
        itemCount = iteminfo.get('count', 0)
        itemDesc = self.getItemDesc(clientconf, iteminfo)
        iteminfo["itemDesc"] = itemDesc

        # 构造邮箱信息
        assetsdict = {"assets":itemDesc, "count":str(itemCount)}
        mail = Tool.dictGet(clientconf, "config.mail")
        mail = strutil.replaceParams(mail, assetsdict)

        # 发送奖励和邮箱信息
        assets = {'itemId':itemId, 'count':itemCount}
        UserBag.sendAssetsToUser(6, userId, assets, 'DDZ_ACT_REDENVELOPE', mail)

        # 发送LED的(条件满足)
        itemconf = self.getItemConf(clientconf, iteminfo)
        ok = self.sendLedIfNeed(userId, itemconf, itemCount)
        ftlog.debug("TYActivityDdzRedEnvelope.get: sendLed-> userId=", userId, " ok=",ok)

        # 记录领取物品
        assets.update({"itemDesc": itemconf.get('desc')})
        LuckyPacketHelper.setUserGet(bankId, userId, current_issue, iteminfo)

        # 日志记录领取
        ftlog.debug("TYActivityDdzRedEnvelope:Get, ", "userId", userId,
                                                    "gettime", str(datetime.now()),
                                                    "assets", iteminfo.get("itemId"),
                                                    "count", iteminfo.get("count"),
                                                    "desc", iteminfo.get("itemDesc"),
                                                    "detail", iteminfo)

        # 构造协议信息
        itemtip = Tool.dictGet(clientconf, "config.activate.itemGetTip")
        itemtip = strutil.replaceParams(itemtip, assetsdict)
        rconf.update({"isOK":True, "itemDesc": itemDesc, "itemCount": itemCount, "tip":itemtip})
        ftlog.debug("LuckyPacket.get: userId=", userId, " itemconf=",itemconf, "arrive_timepoint=", str(arrive_timepoint), "rconf=", rconf)

        return rconf

    def getItemDesc(self, clientconf, iteminfo):
        conf = self.getItemConf(clientconf, iteminfo)
        if not conf:
            return False
        return conf.get('desc')

    def getItemConf(self, clientconf, iteminfo):
        isvip = iteminfo.get('isVipItem', False)
        conf = Tool.dictGet(clientconf, 'config.activate.generalRedEnvelope')
        if isvip:
            conf = Tool.dictGet(clientconf, 'config.activate.vipRedEnvelope')
        for x in conf:
            if x.get('itemId') == iteminfo.get('itemId'):
                return x
        return False

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

        ftlog.debug("LuckyPacket.sendLedIfNeed: settingkey=", settingkey)
        clientconf = self._clientConf
        settingmap = Tool.dictGet(clientconf, "config.activate.ledSetting")
        if not settingmap:
            return False
        ftlog.debug("LuckyPacket.sendLedIfNeed: settingmap=", settingmap)

        setting = settingmap.get(settingkey)
        if not setting:
            return False
        ftlog.debug("LuckyPacket.sendLedIfNeed: setting=", setting)

        text = setting.get("text")
        if (not text) or len(text) <= 0:
            return False

        ftlog.debug("LuckyPacket.sendLedIfNeed: text=", text, "mincount", setting.get("min", 0))
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
