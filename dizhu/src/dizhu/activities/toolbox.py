# -*- coding: utf-8 -*-
'''
Created on  2015-12-30

@author: luwei
'''

from __future__ import division
import time
import random
import freetime.util.log as ftlog
import poker.util.timestamp as pktimestamp
import poker.entity.biz.message.message as pkmessage
from poker.util import strutil
from poker.protocol import router
from datetime import datetime
from poker.entity.biz.content import TYContentItem
from poker.entity.dao import sessiondata, gamedata, userchip, daoconst
from hall.entity.todotask import TodoTaskShowInfo, TodoTaskHelper
from hall.entity import hallitem, datachangenotify
from poker.entity.biz.item.item import TYAssetUtils
from hall.entity import hallvip
from poker.entity.configure import gdata
from poker.entity.dao import daobase
from poker.entity.dao import userdata
from hall.entity import hallled
from hall.entity import hallconf
from dizhu.entity import skillscore
from dizhu.entity.dizhuconf import DIZHU_GAMEID
from collections import deque

class Tool(object):
    
    @classmethod
    def getNormalDateString(cls, datestring):
        '''
        获得将参数日期字符串转换格式,转成20170707.000000这种格式
        @param datestring: 时间格式化字符串，必须是字符串格式为：'2015-01-01 00:00:00'
        '''
        dateformat = '%Y-%m-%d %H:%M:%S'
        dt = datetime.strptime(datestring, dateformat)
        return dt.strftime('%Y%m%d.%H%M%S')
    
    @classmethod
    def checkNow(cls, startdate, enddate):
        '''
        检测当前是否是否在指定时间范围内(全包含关系[startdate, enddate])
        :param startdate 起始时间，必须是字符串格式为：'2015-01-01 00:00:00'
        :param enddate 终止时间，必须是字符串格式为：'2015-01-01 00:00:00'
        :return 若当前在时间范围内则返回True，否则False
        '''
        dateformat = '%Y-%m-%d %H:%M:%S'
        datetime_now = datetime.now()
        datetime_start = datetime.strptime(startdate, dateformat)
        datetime_end = datetime.strptime(enddate, dateformat)

        ok = datetime_start<=datetime_now and datetime_now<=datetime_end
        ftlog.debug('Tool.checkNow: ok=', ok,
                    'datetime_now=', datetime_now,
                    'datetime_start=', datetime_start,
                    'datetime_end=', datetime_end)
        return ok

    @classmethod
    def datetimeFromString(cls, s):
        '''
        将字符串转为datetime对象,默认格式'%Y-%m-%d %H:%M:%S'
        '''
        dateformat = '%Y-%m-%d %H:%M:%S'
        return datetime.strptime(s, dateformat)

    @classmethod
    def datetimeToTimestamp(cls, dt):
        '''
        datetime对象转化为时间戳
        '''
        return time.mktime(dt.timetuple())

    @classmethod
    def datetimeMoveDays(cls, dt, days=1):
        '''
        返回datetime某天之后的同一时间
        :param days 几天之后, 也可以是负数代表几天之前,默认是一天
        '''
        return datetime.fromtimestamp( time.mktime(dt.timetuple()) + 24*60*60*days )

    @classmethod
    def getClientIdWithUserId(cls, userId):
        '''
        通过userId获取clientId
        '''
        clientId = sessiondata.getClientId(userId)
        return clientId

    @classmethod
    def getClientVersionWithUserId(cls, userId):
        '''
        通过userId获取客户端的版本号
        '''
        ver = sessiondata.getClientIdVer(userId)
        return ver

    @classmethod
    def isGameDdz(cls, userId):
        '''
        检测是否为地主大厅
        '''
        user_gameid = strutil.getGameIdFromHallClientId(sessiondata.getClientId(userId))
        ftlog.debug('Tool.isGameDdz: userId=', userId, 'gameId=', 6, 'user_gameid=', user_gameid)
        if user_gameid != 6:
            return False
        return True

    @classmethod
    def sendTodoTaskShowInfo(cls, gameId, userId, info):
        '''
        弹窗提示TodoTask
        '''
        task = TodoTaskShowInfo(info, True)
        mo = TodoTaskHelper.makeTodoTaskMsg(gameId, userId, task)
        router.sendToUser(mo, userId)

    @classmethod
    def sendMailToUser(cls, userId, mail):
        '''
        给用户发送邮箱信息
        '''
        pkmessage.sendPrivate(9999, userId, 0, mail)

    @classmethod
    def dictGet(cls, dictobj, keypath, default=None, separate='.'):
        '''
        从dict中取值，必须是dict嵌套，不支持list
        :param dictobj 必须是dict类型
        :param keypath key路径，默认以'.'分隔，如：'1004.matchconf.xxxx'
        :param default 若Key路径找不到则返回默认值
        :return 返回dict中的对应值
        '''
        if not isinstance(dictobj, dict):
            return default

        keylist = keypath.split(separate)
        sub = dictobj
        for k in keylist:
            if not (k in sub):
                return default
            sub = sub.get(k, default)
        return sub

    @classmethod
    def dictSet(cls, dictobj, keypath, value, separate='.'):
        '''
        向dict中设置值，必须是dict嵌套，不支持list，若路径不存在则创建
        :param dictobj 若为None，则创建dict
        :param keypath key路径，默认以'.'分隔，如：'1004.matchconf.xxxx'
        :param value 要设置的值
        :return 返回处理后的对象
        '''
        if not isinstance(dictobj, dict):
            dictobj = {}

        keylist = keypath.split(separate)
        lastkey = keylist.pop()
        cur = dictobj
        for k in keylist:
            if k not in cur:
                cur[k] = {}
            cur = cur.get(k)
        cur[lastkey] = value
        return dictobj

    @classmethod
    def dictIncr(cls, dictobj, keypath, default=0, separate='.'):
        '''
        自增一个指定位置的值
        :param dictobj 若为None，则创建dict
        :param keypath key路径，默认以'.'分隔，如：'1004.matchconf.xxxx'
        :param default 若不存至值的默认值，结果会在defautl上+1
        :return: 返回增长之后的值
        '''
        num = cls.dictGet(dictobj, keypath, default, separate)
        num = int(num)
        num += 1
        cls.dictSet(dictobj, keypath, num, separate)
        return num

    @classmethod
    def dictDecr(cls, dictobj, keypath, default=0, separate='.'):
        '''
        自减一个指定位置的值
        :param dictobj 若为None，则创建dict
        :param keypath key路径，默认以'.'分隔，如：'1004.matchconf.xxxx'
        :param default 若不存至值的默认值，结果会在defautl上-1
        :return: 返回减少之后的值
        '''
        num = cls.dictGet(dictobj, keypath, default, separate)
        num = int(num)
        num -= 1
        cls.dictSet(dictobj, keypath, num, separate)
        return num

    @classmethod
    def sendLed(cls, text):
        '''
        只在地主大厅和地主插件中播放LED
        '''
        hallled.sendLed(DIZHU_GAMEID, text, 0, scope='hall6')

class UserBag(object):
    @classmethod
    def isHaveAssets(cls, userId, assetsKindId, gameId=6):
        '''
        判断是否拥有指定资产，若kindId是未知的，则会抛出异常
        :param assetsKindId 资产id, 字符串格式：'item:0011'
        :param gameId 统计用途
        :return 若拥有则返回True
        '''
        count = cls.getAssetsCount(userId, assetsKindId, gameId)
        return count > 0

    @classmethod
    def getAssetsCount(cls, userId, assetsKindId, gameId=6):
        '''
        获得指定的用户的资产的数量，若kindId是未知的，则会抛出异常
        :param assetsKindId 资产id, 字符串格式：'item:0011'
        :param gameId 统计用途
        :return 返回指定资产的数量
        '''
        timestamp = pktimestamp.getCurrentTimestamp()
        userAssets = hallitem.itemSystem.loadUserAssets(userId)
        count = userAssets.balance(gameId, assetsKindId, timestamp)
        return count

    @classmethod
    def forceConsumeAssets(cls, userId, assetsKindId, count, eventId, gameId=6, intEventParam=0):
        '''
        删除指定类型的资产指定的数目，若kindId是未知的，则会抛出异常,支持user:chip....
        注意: 如果资源不够的话仍然会消耗,实际消耗数量通过返回值确定
        :param assetsKindId 资产id, 字符串格式：'item:0011'
        :param count 要删除的个数
        :param eventId 事件ID，要在config/poker/map.bieventid.json中注册
        :param gameId 统计用途
        :return (TYAssetKind, consumeCount实际消耗的数量, final剩余的数量)
        '''
        timestamp = pktimestamp.getCurrentTimestamp()
        userAssets = hallitem.itemSystem.loadUserAssets(userId)
        return userAssets.forceConsumeAsset(gameId, assetsKindId, count, timestamp, eventId, intEventParam)

    @classmethod
    def consumeAssetsIfEnough(cls, userId, assetsKindId, count, eventId, gameId=6, intEventParam=0):
        '''
        删除指定类型的资产指定的数目，若kindId是未知的，则会抛出异常,支持user:chip....
        注意:若资源不够则消耗失败
        :param assetsKindId 资产id, 字符串格式：'item:0011'
        :param count 要删除的个数
        :param eventId 事件ID，要在config/poker/map.bieventid.json中注册
        :param gameId 统计用途
        :return 是否消耗成功
        '''
        timestamp = pktimestamp.getCurrentTimestamp()
        userAssets = hallitem.itemSystem.loadUserAssets(userId)
        _, consumeCount, _ = userAssets.consumeAsset(gameId, assetsKindId, count, timestamp, eventId, intEventParam)
        return consumeCount == count


    @classmethod
    def sendAssetsToUser(cls, gameId, userId, assets, eventId, mail=None, intEventParam=0):
        '''
        :param gameId 统计用途,地主就写6
        :param assets 要发送的资产, 格式必须是：{itemId:'item:0011', count:1}
        :param eventId 事件ID，要在config/poker/map.bieventid.json中注册
        :param mail(optional) 给用户邮箱发送信息，默认不发送
        '''
        timestamp = pktimestamp.getCurrentTimestamp()
        contentitem = TYContentItem.decodeFromDict(assets)
        userAssets = hallitem.itemSystem.loadUserAssets(userId)
        assetKind, consumecount, finalcount = userAssets.addAsset(gameId, contentitem.assetKindId, contentitem.count,
                                              timestamp, eventId, intEventParam)
        # 通知用户道具和消息存在改变
        if assetKind.keyForChangeNotify:
            datachangenotify.sendDataChangeNotify(gameId, userId, [assetKind.keyForChangeNotify, 'message'])

        # 发送邮箱信息
        if mail and len(mail) > 0:
            pkmessage.sendPrivate(9999, userId, 0, mail)
            
        return (assetKind, consumecount, finalcount)

    @classmethod
    def sendAssetsListToUser(cls, gameId, userId, assetList, eventId, mail=None, intEventParam=0):
        '''
        :param gameId 统计用途,地主就写6
        :param assetList 要发送的资产, 格式必须是：[{itemId:'item:0011', count:1}, ...]
        :param eventId 事件ID，要在config/poker/map.bieventid.json中注册
        :param mail(optional) 给用户邮箱发送信息，默认不发送
        '''
        timestamp = pktimestamp.getCurrentTimestamp()
        itemList = []
        for i in xrange(0, len(assetList)):
            itemList.insert(i, TYContentItem.decodeFromDict(assetList[i]))
        userAssets = hallitem.itemSystem.loadUserAssets(userId)
        assetList  = userAssets.sendContentItemList(gameId, itemList, 1, True, timestamp, eventId, intEventParam)

        # 通知用户道具和消息存在改变
        if assetList:
            datachangenotify.sendDataChangeNotify(gameId, userId, TYAssetUtils.getChangeDataNames(assetList))

        # 发送邮箱信息
        if mail and len(mail) > 0:
            pkmessage.sendPrivate(9999, userId, 0, mail)


class Redis(object):

    @classmethod
    def readJson(cls, userId, key, gameId=6):
        '''
        从Reids的gametable中读取内容，并且将读出的内容作为json处理
        :param key 用于hashmap存储内容的key，必须唯一
        :param gameId 存储在redis中的位置，默认存在game:6下
        :return 返回从JSON解析的对象
        '''
        data = gamedata.getGameAttrJson(userId, gameId, key)
        # ftlog.debug('Redis.readJson: userId=', userId, 'gameId=' , gameId, 'key=', key, ('data(%s)=' % type(data)), data)
        if data == None:
            return {}
        return data

    @classmethod
    def writeJson(cls, userId, key, data, gameId=6):
        '''
        向Reids的gametable中写入内容，并且将传入的内容作为json序列化
        :param key 用于hashmap存储内容的key，必须唯一
        :param gameId 存储在redis中的位置，默认存在game:6下
        :param data 要写入的内容，可以是dict/list/str/unicode
        '''
        jsonstr = data
        if not isinstance(data, basestring):
            jsonstr = strutil.dumps(data)
        # ftlog.debug('Redis.writeJson: userId=', userId, 'gameId=' , gameId, 'key=', key, 'jsonstr(%s)=' % type(jsonstr), jsonstr)
        gamedata.setGameAttr(userId, gameId, key, jsonstr)

    @classmethod
    def readBoolean(cls, userId, key, gameId=6):
        '''
        读取bool类型变量
        :param key 用于hashmap存储内容的key，必须唯一
        :param gameId 存储在redis中的位置，默认存在game:6下
        :return 返回读取的bool值
        '''
        value = gamedata.getGameAttr(userId, gameId, key)
        # ftlog.debug('Redis.readBoolean: userId=', userId, 'gameId=' , gameId, 'key=', key, ('value(%s)=' % type(value)), value)
        return bool(value)

    @classmethod
    def writeBoolean(cls, userId, key, value, gameId=6):
        '''
        写入bool类型变量
        :param key 用于hashmap存储内容的key，必须唯一
        :param gameId 存储在redis中的位置，默认存在game:6下
        :param value bool类型的值
        :return 返回写入的bool值
        '''
        value = bool(value)
        ok = 0
        if value:
            ok = 1
        # ftlog.debug('Redis.writeBoolean: userId=', userId, 'gameId=' , gameId, 'key=', key, 'value(%s)=' % type(value), bool(ok), ok, value)
        gamedata.setGameAttr(userId, gameId, key, ok)
        return bool(ok)

    @classmethod
    def readInteger(cls, userId, key, default=0, gameId=6):
        '''
        读取int类型变量
        :param key 用于hashmap存储内容的key，必须唯一
        :param gameId 存储在redis中的位置，默认存在game:6下
        :return 返回读取的int值
        '''
        value = gamedata.getGameAttrInt(userId, gameId, key)
        # ftlog.debug('Redis.readInteger: userId=', userId, 'gameId=' , gameId, 'key=', key, ('value(%s)=' % type(value)), value)
        if value==None:
            return int(default)
        return int(value)

    @classmethod
    def writeInteger(cls, userId, key, value, gameId=6):
        '''
        写入int类型变量
        :param key 用于hashmap存储内容的key，必须唯一
        :param gameId 存储在redis中的位置，默认存在game:6下
        :param value int类型的值
        :return 返回写入的int值
        '''
        ret = int(value)
        # ftlog.debug('Redis.writeInteger: userId=', userId, 'gameId=' , gameId, 'key=', key, 'ret(%s)=' % type(ret), ret)
        gamedata.setGameAttr(userId, gameId, key, ret)
        return ret

    @classmethod
    def read(cls, userId, key, default='', gameId=6):
        '''
        读取变量
        :param key 用于hashmap存储内容的key，必须唯一
        :param gameId 存储在redis中的位置，默认存在game:6下
        :return 返回读取的值
        '''
        ret = gamedata.getGameAttr(userId, gameId, key) or default
        # ftlog.debug('Redis.read: userId=', userId, 'gameId=' , gameId, 'key=', key, ('ret(%s)=' % type(ret)), ret)
        return ret

    @classmethod
    def write(cls, userId, key, value, gameId=6):
        '''
        写入变量
        :param key 用于hashmap存储内容的key，必须唯一
        :param gameId 存储在redis中的位置，默认存在game:6下
        :param value int类型的值
        :return 返回写入的值
        '''
        # ftlog.debug('Redis.write: userId=', userId, 'gameId=' , gameId, 'key=', key, 'text(%s)=' % type(text), text)
        gamedata.setGameAttr(userId, gameId, key, value)
        return value

    @classmethod
    def writeMixHash(cls, path, key, value):
        '''
        在db1中记录数据
        :param path: 一般是'dizhu:xxxx'
        :param key: hashmap中的key
        :param value: 存储的值
        '''
        return daobase.executeMixCmd('HSET', path, key, value)

    @classmethod
    def readMixHash(cls, path, key, default=None):
        '''
        在db1中读取记录数据
        :param path: 一般是'dizhu:xxxx'
        :param key: hashmap中的key
        :param default: 若所取值为空则返回默认值
        '''
        return daobase.executeMixCmd('HGET', path, key) or default

    @classmethod
    def isFirst(cls, userId, key, gameId=6):
        '''
        只有第一次才能设置成功,若已经成功设置过,则在设置就会失败
        :param key: hashmap中的key
        :param gameId 存储在redis中的位置，默认存在game:6下
        :return: True代表设置成功,False代表已经设置过了
        '''
        return gamedata.setnxGameAttr(userId, gameId, key, 1) == 1


class Room(object):

    @classmethod
    def getRoomConfigWitBighRoomId(cls, roomId):
        '''
        获取房间ID的配置
        :param roomId 配置中的ID，如：6015
        '''
        return gdata.getRoomConfigure(roomId)

    @classmethod
    def getDdzBigRoomIdList(cls):
        '''
        获得地主的所有房间ID的列表
        :return 返回的房间ID列表是配置中的ID，如：[6015, 6016]
        '''
        return gdata.gameIdBigRoomidsMap()[6]

    @classmethod
    def getRealRoomIdListWithBigRoomId(cls, roomId):
        '''
        获取某个房间的真实房间ID
        :param roomId是配置中的ID，如：6015
        :return 返回真实ID的元组，如：(60151000, ...)
        '''
        return gdata.bigRoomidsMap()[roomId]

    @classmethod
    def convertToBigRoomId(cls, roomId):
        '''
        可以将房间ID转为配置中的房间ID
        :param roomId 配置中的ID，如：60151000
        :return 例如将60151000=>6015
        '''
        return gdata.getBigRoomId(roomId)

class UserInfo(object):
    @classmethod
    def getDashiFen(cls, userId):
        '''
        获取用户的大师分
        '''
        return skillscore.get_skill_score(userId) or 0

    @classmethod
    def getDashiFenLevel(cls, userId):
        '''
        获取用户的大师分等级
        '''
        from dizhu.game import TGDizhu
        info = TGDizhu.getDaShiFen(userId, None)
        if info:
            return info.get('level', 0)
        return 0

    @classmethod
    def getVipLevel(cls, userId):
        '''
        获取用户的VIP等级
        '''
        info = hallvip.userVipSystem.getUserVip(userId)
        if info :
            return info.vipLevel.level or 0
        return 0

    @classmethod
    def getChip(cls, userId):
        '''
        获取用户的金币数
        '''
        return userchip.getChip(userId)

    @classmethod
    def incrChip(cls, userId, gameId, deltacount, eventId):
        '''
        改变金币数目
        :param deltacount: 金币的变化量，可以为负数
        :param eventId: 事件ID，要在config/poker/map.bieventid.json中注册
        :return: 返回改变之后的金币数
        '''
        clientId = sessiondata.getClientId(userId)
        userchip.incrChip(userId, gameId, deltacount, daoconst.CHIP_NOT_ENOUGH_OP_MODE_CLEAR_ZERO, eventId, 0, clientId)
        datachangenotify.sendDataChangeNotify(gameId, userId, 'chip')
        return userchip.getChip(userId)

    @classmethod
    def getNickname(cls, userId):
        '''
        获得指定UserId玩家的昵称
        '''
        l = userdata.getAttrs(userId, ['name'])
        if l:
            return l[0]
        return ''

    @classmethod
    def getRegisterDays(cls, userId, timestamp):
        '''
        获取注册的天数
        :param userId:
        :param timestamp:当前时间戳
        '''
        nowDate = datetime.fromtimestamp(timestamp).date()
        createDate = datetime.strptime(userdata.getAttr(userId, 'createTime'), '%Y-%m-%d %H:%M:%S.%f').date()
        return max(0, (nowDate-createDate).days)


class Random(object):

    @classmethod
    def getNormalDistributionRandomSequence(cls, total, minv, num):
        '''
        计算符合正态分布的随机整数序列（total/num是中间值）
        :param total: 总数量，最终结果会合总数量有稍微的差距
        :param minv: 最小值，序列中允许出现的最小值
        :param num: 份数，产生的序列项数
        :return list: 返回随机序列
        '''
        total = int(total)
        num = int(num)

        if num < 1:
            return []
        
        if num == 1:
            return [total]

        i = 1
        total_money = total

        r = []
        while i < num:
            maxv = total_money - minv*(num - i)
            k = int((num-i)/2)
            if num - i <= 2:
                k = num - i
            maxv = maxv / k
            if maxv <= 0 or minv > maxv:
                break
            monney = random.randint(int(minv), int(maxv))
            r.append(monney)
            total_money = total_money - monney
            if total_money <= 0:
                break
            i += 1

        for i in xrange(0, int(num) - len(r)):
            r.append(minv)

        random.shuffle(r)
        return r


class Activity(object):
    @classmethod
    def getConfigById(cls, activityId):
        conf = hallconf.getActivityConf()
        allactconf = conf.get('activities')
        if not allactconf:
            return
        return allactconf.get(activityId)


class JsonQueue(object):
    '''
	简单的队列，先进先出
	说明：左尾右头
	'''
    def __init__(self, maxsize):
        self.queue = deque(maxlen=maxsize)

    def enqueue(self, obj):
        '''
        从队尾入队,最先入队的最先被淘汰(maxsize限制)
        '''
        self.queue.appendleft(obj)

    def dequeue(self):
        '''
        从队首出队并返回
        '''
        return self.queue.pop()

    def clear(self):
        '''
        清空队列
        '''
        self.queue.clear()

    def tail(self, count):
        '''
        按顺序获取队尾的count个元素，不会删除元素，若队列元素不够count个则只返回队列的全部元素
        顺序是先加入的在数组前，后加入的在数据后
        param: count获取元素个数
        '''
        array = []
        for x in self.queue:
            if count <= 0:
                break
            array.append(x)
            count -= 1
        array.reverse()
        return array

    def head(self, count):
        '''
        按顺序获取队首的count个元素，不会删除元素，若队列元素不够count个则只返回队列的全部元素
        顺序是先加入的在数组前，后加入的在数据后
        param: count获取元素个数
        '''
        array = []
        for i in xrange(0, len(self.queue)):
            if count <= 0:
                break
            count -= 1
            array.append(self.queue[len(self.queue) - 1 - i])
        return array

    def toJson(self):
        '''
        将队列数据序列化为json,序列化的数组左侧是后入队的元素,右侧是先入队的元素
        说明:可以通过fromJson重新构造出相同的队列
        '''
        array = []
        for i in xrange(0,len(self.queue)):
            array.append(self.queue[i])
        return strutil.dumps(array)

    def fromJson(self, j):
        '''
        从json构造出队列,json必须是数组结构,数组右侧最先被入队
        '''
        self.clear()
        array = strutil.loads(j)
        array.reverse()
        for x in array:
            self.enqueue(x)


class LotteryPool(object):
    '''
    奖池，按权重分配抽奖概率
    测试: 统计了抽奖一千万次的奖励分布,符合权重预期
    使用:
    lottery = LotteryPool()
    lottery.addingPrize(...)
    lottery.addingPrize(...)
    lottery.addingPrizeList(...)
    ...
    prize = lottery.randomChoose()
    ...
    '''

    def __init__(self):
        self.prizeList = []
        self.weightCounter = 0

    def addingPrizeList(self, prizeList):
        '''
        添加奖品权重配置列表
        :param prizeList:  [{'prize':?, 'weight':10}, {'prize':?, 'weight':0.3}, ...]
        :return: None
        :example:
        lotteryPool.addingPrizeList([
            {'id':1, 'prize':'电脑', 'weight': 10},
            {'id':2, 'prize':'手机', 'weight': 2.5},
            {'id':3, 'prize':'平板', 'weight': 1},
            {'id':4, 'prize':'眼镜', 'weight': 1},
        ])
        '''
        self.prizeList = prizeList
        for item in self.prizeList:
            self.weightCounter += item.get('weight', 0)
        return

    def addingPrize(self, prize, weight):
        '''
        添加抽奖奖品配置单项
        :param prize: 抽奖的奖品,调用抽奖接口时,会返回此项
        :param weight: 奖品对应的权重
        :return: None
        '''
        self.prizeList.append({'prize':prize, 'weight':weight})
        self.weightCounter += weight
        return

    def clear(self):
        '''
        清空搜索奖品配置
        :return: None
        '''
        self.prizeList = []
        self.weightCounter = 0
        return

    def randomChoose(self):
        '''
        选择随机的一个奖品,概率通过对权重的计算获得
        :return: prize, 若返回None则代表奖品列表为空
        '''
        rand = random.random()
        probabilityCounter = 0
        for item in self.prizeList:
            probability = item.get('weight', 0)/self.weightCounter
            probabilityCounter += probability
            if rand < probabilityCounter:
                return item.get('prize')
        return


class LotteryPoolFast(object):
    '''
    奖池，按权重分配抽奖概率(权重必须是整数)
    说明: 比LotteryPool抽奖时快一些,但是占用内存多一些
    测试: 统计了抽奖一千万次的奖励分布,符合权重预期
    使用:
    lottery = LotteryPool()
    lottery.addingPrize(...)
    lottery.addingPrize(...)
    lottery.addingPrizeList(...)
    lottery.build()
    ...
    prize = lottery.randomChoose()
    ...
    '''

    def __init__(self):
        self.pool = []
        self.prizeList = []

    def addingPrizeList(self, prizeList):
        '''
        添加奖品权重配置列表(权重必须是整数)
        :param prizeList:  [{'prize':?, 'weight':10}, {'prize':?, 'weight':0.3}, ...]
        :return: None
        :example:
        lotteryPool.addingPrizeList([
            {'id':1, 'prize':'电脑', 'weight': 10},
            {'id':2, 'prize':'手机', 'weight': 2.5},
            {'id':3, 'prize':'平板', 'weight': 1},
            {'id':4, 'prize':'眼镜', 'weight': 1},
        ])
        '''
        self.prizeList = prizeList
        return

    def addingPrize(self, prize, weight):
        '''
        添加抽奖奖品配置单项
        :param prize: 抽奖的奖品,调用抽奖接口时,会返回此项
        :param weight: 奖品对应的权重(权重必须是整数)
        :return: None
        '''
        self.prizeList.append({'prize':prize, 'weight':weight})
        return

    def build(self):
        '''
        每次addingPrize之后都必须重新build
        :return: None
        '''
        self.clear()
        for item in self.prizeList:
            for _ in xrange(0, item.get('weight')):
                self.pool.append(strutil.cloneData(item))
        return

    def clear(self):
        '''
        清空搜索奖品配置
        :return: None
        '''
        self.pool = []
        self.prizeList = []
        return

    def randomChoose(self):
        '''
        选择随机的一个奖品,概率通过对权重的计算获得
        :return: prize, 若返回None则代表奖品列表为空
        '''
        item = self.pool[random.randint(0, len(self.pool) - 1)]
        return item.get('prize')


class GamedataModel(object):
    '''
    Gamedata用户数据模型
    对应redis中的gamedata:gameId:userId的HashMap中的uniquekey的数据
    使用方式:
    子类继承自本类,然后在子类的__init__方法中,定义想要获取的数据字段并且初始化为默认值(若不定义则不会获取,若redis中没有则不会改变默认值)
    例如:
    ```python
    class UserModel(GamedataModel):
    def __init__(self):
        self.pindex = 0
        self.ok = False
    model = UserModel()
    model.loadsFromRedis(userId, uniquekey)
    print model.pindex
    print model.ok
    ```
    '''

    def loadsFromRedis(self, userId, uniquekey, gameId=6):
        '''
        从redis对应位置加载数据,并将数据直接复制给存在的对象属性(属性需在__init__中预先定义)
        :param userId: 用户ID
        :param uniquekey: gamedata:gameId:userId的HashMap的key
        :param gameId: 默认6(决定存储位置)
        :return: self
        '''
        d = Redis.readJson(userId, uniquekey, gameId)
        for key in d:
            if hasattr(self, key):
                setattr(self, key, d[key])
        return self

    def dumpsToRedis(self, userId, uniquekey, gameId=6):
        '''
        将本类的属性全部dumps成json存入redis中
        :param userId: 用户ID
        :param uniquekey: gamedata:gameId:userId的HashMap的key
        :param gameId: 默认6(决定存储位置)
        :return: self
        '''
        Redis.writeJson(userId, uniquekey, self.__dict__, gameId)
        return self

    def dict(self):
        return self.__dict__


class TimeCounter(object):
    '''
    时间(秒)计数器,可用于CD(冷却)计时
    '''
    timestampKey = 'timecounter_timestamp'

    @classmethod
    def resetingCounterToCurrentTimestamp(cls, uniquekey, userId):
        '''
        重置计时器到当前时间戳
        :param uniquekey: redis中gamedata的hashmap中的key
        :param userId: 用户ID
        '''
        data = Redis.readJson(userId, uniquekey)
        data[cls.timestampKey] = Tool.datetimeToTimestamp(datetime.now())
        Redis.writeJson(userId, uniquekey, data)

    @classmethod
    def getCountingSeconds(cls, uniquekey, userId):
        '''
        获得自resetCounterToCurrentTimestamp调用后到当前的时间(秒)
        :param uniquekey: redis中gamedata的hashmap中的key
        :param userId: 用户ID
        :return 若是第一次计时则会返回-1
        '''
        laststamp = Redis.readJson(userId, uniquekey).get(cls.timestampKey)
        if not laststamp:
            cls.resetingCounterToCurrentTimestamp(uniquekey, userId)
            return -1
        return Tool.datetimeToTimestamp(datetime.now()) - laststamp
