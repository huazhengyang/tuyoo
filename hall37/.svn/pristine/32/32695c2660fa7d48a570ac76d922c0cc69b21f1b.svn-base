# -*- coding=utf-8
'''
Created on 2016年6月13日

@author: zhaol
红包模块
红包 : red envelope

红包ID的生成规范
一，种类
1）比赛红包
2）现金桌奖励红包
3）个人推广红包
'''

from sre_compile import isstring
import freetime.util.log as ftlog
from hall.entity import hallconf, hallitem, datachangenotify
from poker.entity.biz.exceptions import TYBizConfException
from poker.entity.events.tyevent import EventConfigure
import poker.entity.events.tyeventbus as pkeventbus
import random, json
from poker.entity.biz.content import TYContentItem
from hall.entity.hallconf import HALL_GAMEID
from poker.entity.biz.item.item import TYAssetUtils
import poker.util.timestamp as pktimestamp
from poker.util import strutil
from poker.entity.dao import daobase
from poker.entity.dao import userdata as pkuserdata


get_content_by_item_script = """
local function cut_content_with_item(key, itemId)
    local contents = redis.call("LRANGE", key, 0, -1)

    if #contents == 0 then
        return nil
    end

    -- 查找符合要求的记录。如果没有，就取第一个
    local item_content_index = 1
    for i=1, #contents do
        local content = cjson.decode(contents[i])
        if content[itemId] then
            item_content_index = i
            break
        end
    end

    local item_content_json = contents[item_content_index]

    -- 由于redis LIST 不能从中间pop，所以把取到的删掉
    if item_content_index == 1 then  -- 优化操作只POP第一个
        redis.call("LPOP", key)

    else
        redis.call("DEL", key)
        for i=1, #contents do
            if i ~= item_content_index then
                redis.call("RPUSH", key, contents[i])
            end
        end
    end
    return item_content_json
end

return cut_content_with_item(KEYS[1], ARGV[1])
"""

get_content_by_item_sha = None


class TYRedEnvelope(object):
    '''
    packages - 红包 LIST 单独存储，保持操作的原子性
    receiver - 领奖者 LIST 单独存储上， 保持操作的原子性
    '''
    # 事件ID
    EVENTID = 'HALL_RED_ENVELOPE'
    # 红包状态创建
    STATE_CREATE = '1'
    # 红包状态 被分享
    STATE_SHARED = '2'
    # 红包状态 抢光了
    STATE_FINISH = '3'


    def __init__(self):
        self.id = None
        # 奖品组成/配置一起存储，这些信息红包生成时存储，其他时候都是查询操作
        # 奖品
        self.contents = None
        # 奖品最小个数
        self.minCount = None
        # 奖品最大个数
        self.maxCount = None
        # 红包分包记录
        self.packages_his = None
        # 过期时间
        self.expiredTime = None
        # 数据库前缀
        self.dbPrefix = 'red_envelope:'
        # 红包状态
        self.state = self.STATE_CREATE
        # 领取红包key
        self.RECEIVER = '.receiver'
        # 配置KEY
        self.CONFIG = 'config'
        # 红包KEY
        self.PACKAGES = '.packages'
        # 内容KEY
        self.CONTENTS = 'contents'
        # 领取历史KEY
        self.PACKAGES_HIS = 'packages_his'
        # 红包状态KEY
        self.STATE = 'state'

        
    def getPrefix(self):
        return self.dbPrefix
                
    def buildEnvelope(self, _id):
        '''
        生成红包
        '''
        global _redEnvelopeConfig
        
        self.id = _id
        self.contents = []
        self.packages_his = []
        # 设置过期时间，单位秒 s
        self.expiredTime = _redEnvelopeConfig['config']['expiredTime']

        return self
    
    def addEnvelopeItem(self, item):
        '''
        添加奖品
        '''
        self.contents.append(item)
        
    def setReceiveParams(self, minCount, maxCount):
        '''
        设置抽奖参数
        '''
        self.minCount = minCount
        self.maxCount = maxCount
        
    def buildShareTask(self, userId, gameId, url=None, title=None, desc=None, tips=None, shareIcon=None):
        '''
        获取分享ID
        url - 红包分享页面的URL
        title - 红包分享时的标题
        desc - 红包分享时的描述
        tips - 游戏触发分享时的提醒
        shareIcon - 分享后的图片
        '''
        from hall.entity import hallshare
        
        global _redEnvelopeConfig
        
        shareId = hallshare.getShareId('red_envelope', userId, gameId)
        share = hallshare.findShare(shareId)
        if share:
            if url:
                share.setUrl(url)
            
            if title:
                share.setTitle(title)
                
            if desc:
                share.setDesc(desc)
                
            if tips:
                share.setTips(tips)
        
            if shareIcon:
                share.setShareIcon(shareIcon)
              
            # 设置分享的扩展参数    
            share.setNotifyInfo(userId, self.id, self.EVENTID)
                
            return share.buildTodotask(gameId, userId, 'red_envelope')
        else:
            return None
                
                
    def queryEnvelope(self):
        info = {}
        info['envelopeId'] = self.id
        info['contents'] = self.contents
        info['receiver'] = []
        receivers = daobase.executeMixCmd('LRANGE', self.dbPrefix + self.id + self.RECEIVER, 0, -1)
        if receivers:
            for receiverJson in receivers:
                receiver = json.loads(receiverJson)
                # 补充昵称/头像/金币信息
                userId = receiver['userId']
                chip, name, purl = pkuserdata.getAttrs(userId, ['chip', 'name', 'purl'])
                if chip and name and purl:
                    if ftlog.is_debug():
                        ftlog.debug('TYRedEnvelope.queryEnvelope receiver userId:', userId, ' chip:', chip, ' name:', name, ' purl:', purl)
                    receiver['chip'] = chip
                    receiver['name'] = name
                    receiver['purl'] = purl
                
                info['receiver'].append(receiver)
            
        if ftlog.is_debug():
            ftlog.debug('TYRedEnvelope.queryEnvelope info:', info)
            
        return info
        
    def openRedEnvelope(self, userId, itemId=''):
        '''
        打开红包
        '''
        global _redEnvelopeConfig
        
        # 是否领取过
        receivers = daobase.executeMixCmd('LRANGE', self.dbPrefix + self.id + self.RECEIVER, 0, -1)
        if receivers:
            if ftlog.is_debug():
                ftlog.debug('TYRedEnvelope.openRedEnvelope receivers:', receivers)
                
            for receiverJson in receivers:
                receiver = json.loads(receiverJson)
                if ftlog.is_debug():
                    ftlog.debug('TYRedEnvelope.openRedEnvelope receiver:', receiver)
                if userId == receiver['userId']:
                    return False, _redEnvelopeConfig['tips']['opened']
        
        # 构造添加给获取红包用户的奖励清单        
        contentItemList = []
        prizesJson = self._getPrize(itemId)
        # prizesJson = daobase.executeMixCmd('LPOP', self.dbPrefix + self.id + self.PACKAGES)
        daobase.executeMixCmd('expire', self.dbPrefix + self.id + self.PACKAGES, self.expiredTime)

        if prizesJson:
            prizes = json.loads(prizesJson)
            if ftlog.is_debug():
                ftlog.debug('TYRedEnvelope.openRedEnvelope prizes:', prizes)
            for prize in prizes:
                if ftlog.is_debug():
                    ftlog.debug('TYRedEnvelope.openRedEnvelope prize:', prize)
                    
                result, _itemId = self.getAssetID(prize)
                if result == False:
                    ftlog.debug('TYRedEnvelope.openRedEnvelope prize err1: ', prize, ' left: ', self.contents);
                    continue
                
                result, value = self.getItemValue(prize)
                if result == False:
                    ftlog.debug('TYRedEnvelope.openRedEnvelope prize err2: ', prize, ' left: ', self.contents);
                    continue
                
                if ftlog.is_debug():
                    ftlog.debug('TYRedEnvelope.openRedEnvelope itemId:', _itemId)
                    ftlog.debug('TYRedEnvelope.openRedEnvelope count:', prizes[prize] * value)
                    
                contentItemList.append(TYContentItem.decodeFromDict({'itemId':_itemId, 'count':prizes[prize] * value}))
                
            if ftlog.is_debug():
                ftlog.debug('contentItemList:', contentItemList)
                
            userAssets = hallitem.itemSystem.loadUserAssets(userId)
            # 添加奖励
            results = userAssets.sendContentItemList(HALL_GAMEID, contentItemList, 1, True, pktimestamp.getCurrentTimestamp(), self.EVENTID, 0)
            # notify
            datachangenotify.sendDataChangeNotify(HALL_GAMEID, userId, TYAssetUtils.getChangeDataNames(results))
            # 构造奖励字符串
            prizeString = TYAssetUtils.buildContentsString(results)
            
            if ftlog.is_debug():
                ftlog.debug('TYRedEnvelope.openRedEnvelope prizeString:', prizeString)
            
            # add receiver
            re = {}
            re['userId'] = userId
            re['prize'] = prizes
            re['prizeStr'] = prizeString
            re['time'] = pktimestamp.formatTimeMs()
            
            if ftlog.is_debug():
                ftlog.debug('TYRedEnvelope.openRedEnvelope add receiver re: ', re)
            daobase.executeMixCmd('LPUSH', self.dbPrefix + self.id + self.RECEIVER, json.dumps(re))
            daobase.executeMixCmd('expire', self.dbPrefix + self.id + self.RECEIVER, self.expiredTime)
            
            # make response
            response = {}
            response['envelopeId'] = self.id
            response['prizes'] = prizes
            response['prizeStr'] = prizeString
            
            if ftlog.is_debug():
                ftlog.debug('TYRedEnvelope.openRedEnvelope response: ', response)
                
            return True, response
        else:
            if self.state != self.STATE_FINISH:
                self.state = self.STATE_FINISH
                self.save2DB()
                
            return False, _redEnvelopeConfig['tips']['finished']

    def _getPrize(self, itemId=""):
        key = self.dbPrefix + self.id + self.PACKAGES
        if not itemId:
            prizesJson = daobase.executeMixCmd('LPOP', key)
        else:
            global get_content_by_item_sha
            if not get_content_by_item_sha:
                luaName = 'hall_red_envelope_get_content_by_item'
                get_content_by_item_sha = daobase.loadLuaScripts(luaName, get_content_by_item_script)
            prizesJson = daobase.executeMixCmd("EVALSHA", get_content_by_item_sha, 1, key, itemId)
        return prizesJson

    def devidePackage(self):
        '''
        将整体红包按照配置分成随机的份数
        '''
        global _redEnvelopeConfig
                
        # 划分红包
        prizePool = []
        for item in self.contents:
            for _ in range(1, item['count'] + 1):
                prizePool.append(item['itemId'])
        
        countTotal = len(prizePool)        
        random.shuffle(prizePool)
        
        index = 0
        
        while index < countTotal:
            # 随机获得红包的个数
            count = random.randint(self.minCount, self.maxCount)
            if index + count >= countTotal:
                count = countTotal - index;
            if ftlog.is_debug():
                ftlog.debug('count:', count)
                
            prizes = {}
            for i in range(0, count):
                # 领取红包
                itemId = prizePool[index + i]
                if itemId in prizes:
                    prizes[itemId] += 1
                else:
                    prizes[itemId] = 1
                    
            if ftlog.is_debug():
                ftlog.debug('prizes:', prizes)
                
            # 写数据库
            daobase.executeMixCmd('LPUSH', self.dbPrefix + self.id + self.PACKAGES, json.dumps(prizes))
            # 记录分包信息
            self.packages_his.append(prizes)
            
            index += count
        
        # 设置过期时间
        daobase.executeMixCmd('expire', self.dbPrefix + self.id + self.PACKAGES, self.expiredTime)
    
        # save result to log    
        if ftlog.is_debug():
            checksJson = daobase.executeMixCmd('LRANGE', self.dbPrefix + self.id + self.PACKAGES, 0, -1)
            ftlog.debug('TYRedEnvelope.devidePackage packages: ', checksJson)
        
    def setState(self, state):
        '''
        设置红包状态
        '''
        self.state = state
        self.save2DB()    
        
    def save2DB(self):
        '''
        存储到数据库
        '''
        # 保存基本信息
        config = {}
        config['minCount'] = self.minCount
        config['maxCount'] = self.maxCount
        # 设置配置
        daobase.executeMixCmd('HSET', self.dbPrefix + self.id, self.CONFIG,  json.dumps(config))
        # 设置红包内容
        daobase.executeMixCmd('HSET', self.dbPrefix + self.id, self.CONTENTS, json.dumps(self.contents))
        # 设置红包历史
        daobase.executeMixCmd('HSET', self.dbPrefix + self.id, self.PACKAGES_HIS, json.dumps(self.packages_his))
        # 设置状态
        daobase.executeMixCmd('HSET', self.dbPrefix + self.id, self.STATE, self.state)
        daobase.executeMixCmd('expire', self.dbPrefix + self.id, self.expiredTime)
        
    def loadFromDB(self, envelopeId):
        '''
        从数据库中读取红包
        @return: 
            True 红包存在
            False 红包不存在
        '''
        global _redEnvelopeConfig
        
        self.buildEnvelope(envelopeId)
        
        # config
        configJson = daobase.executeMixCmd('HGET', self.dbPrefix + self.id, self.CONFIG)
        if configJson:
            if ftlog.is_debug():
                ftlog.debug('TYRedEnvelope.loadFromDB configJson:', configJson)
                
            config = json.loads(configJson)
            self.minCount = config.get('minCount', 1)
            self.maxCount = config.get('maxCount', 3)
            
            if ftlog.is_debug():
                ftlog.debug('TYRedEnvelope.loadFromDB minCount: ', self.minCount, ' maxCount: ', self.maxCount)
        else:
            return False, _redEnvelopeConfig['tips']['load_config_err']
        
        # contents
#         redEnvelopeItem = {}
#         redEnvelopeItem['itemId'] = _itemId
#         redEnvelopeItem['assetsId'] = assetsId
#         redEnvelopeItem['value'] = value
#         redEnvelopeItem['count'] = count
        contentsJson = daobase.executeMixCmd('HGET', self.dbPrefix + self.id, self.CONTENTS)
        if contentsJson:
            if ftlog.is_debug():
                ftlog.debug('TYRedEnvelope.loadFromDB contentsJson:', contentsJson)
                
            self.contents = json.loads(contentsJson)
            for item in self.contents:
                assetsId = item['assetsId']
                assetKind = hallitem.itemSystem.findAssetKind(assetsId)
                if assetKind:
                    item['name'] = assetKind.displayName
                    item['pic'] = assetKind.pic
                
        else:
            return False, _redEnvelopeConfig['tips']['load_contents_err']
        
        # package_his
        packagesJson = daobase.executeMixCmd('HGET', self.dbPrefix + self.id, self.PACKAGES_HIS)
        if packagesJson:
            if ftlog.is_debug():
                ftlog.debug('TYRedEnvelope.loadFromDB packagesJson:', packagesJson)
                
            self.packages_his = json.loads(packagesJson)
        else:
            return False, _redEnvelopeConfig['tips']['load_packages_err']
        
        # state
        self.state = daobase.executeMixCmd('HGET', self.dbPrefix + self.id, self.STATE)
        if not self.state:
            self.state = self.STATE_CREATE
        
        return True, self
        
    def getAssetID(self, itemId):
        for item in self.contents:
            if item['itemId'] == itemId:
                if ftlog.is_debug():
                    ftlog.debug('TYRedEnvelope.getAssetID itemId:', itemId)
                    ftlog.debug('TYRedEnvelope.getAssetID assetsId:', item['assetsId'])
                return True, item['assetsId']
            
        return False, 'user:none'
    
    def getItemValue(self, itemId):
        for item in self.contents:
            if item['itemId'] == itemId:
                if ftlog.is_debug():
                    ftlog.debug('TYRedEnvelope.getItemValue itemId:', itemId)
                    ftlog.debug('TYRedEnvelope.getItemValue assetsId:', item['assetsId'])
                return True, item['value']
        
        return False, 0

class TYRedEnvelopeID(object):
    '''
    红包ID定义
        总共21位
        version       2位
        ntype         2位
        gameId        3位
        timeStr       6位
        userId        6位
        count         2位
        idExtendInfo  6位 扩展信息
    '''
    def __init__(self):
        self.initialize()
        
    @classmethod
    def initialize(cls):
        return True
    
    @classmethod
    def buildID(cls, version, ntype, gameId, count, userId, idExtendInfo):
        '''
        生成红包ID
        1）校验自推广红包，每人一个
        2）其他类型红包暂时不校验
        '''
        global _redEnvelopeConfig
        
        # 取消推广红包每人一个的限制
#         if ntype == TYRedEnvelopeMgr.RED_ENVELOPE_PROMOTE:
#             # 推广红包
# # pkgamedata.setGameAttr(userId, 9999, _buildModuleTipKey(tipModule, gameId, userId), count)
#             promoteEnvelopeID = pkgamedata.getGameAttr(userId, HALL_GAMEID, 'promote_red_envelope')
#             if promoteEnvelopeID:
#                 return False, _redEnvelopeConfig['tips']['promote_already_have'];
                
        otime = pktimestamp.getCurrentTimestamp()
        return True, '%s%s%s%s%s%s%s' % (version
                               , strutil.tostr62(ntype, 2)
                               , strutil.tostr62(gameId, 3)
                               , strutil.tostr62(otime, 6)
                               , strutil.tostr62(userId, 6)
                               , strutil.tostr62(int(count % 1000), 2)
                               , strutil.tostr62(idExtendInfo, 6)
                               )
    
    @classmethod
    def isExpired(cls, _id):
        '''
        查询红包是否过期
        '''
        global _redEnvelopeConfig
        
        otime = strutil.toint10(_id[7:13])
        
        return otime + _redEnvelopeConfig['config']['expiredTime'] < pktimestamp.getCurrentTimestamp()
        
    @classmethod
    def parseID(cls, _id):
        idExtendInfo = strutil.toint10(_id[21:27])
        count = strutil.toint10(_id[19:21])
        userId = strutil.toint10(_id[13:19])
        otime = strutil.toint10(_id[7:13])
        timeStr = pktimestamp.timestamp2timeStr(otime)
        gameId = strutil.toint10(_id[4:7])
        nType = strutil.toint10(_id[2:4])
        version = _id[0:2]
        
        idStr = 'Version-%s Type-%d GameId-%d Time-%s UserId-%d Count-%d RoomId-%d ExtendInfo-%d' % (version
                                                                                    , nType
                                                                                    , gameId
                                                                                    , timeStr
                                                                                    , userId
                                                                                    , count
                                                                                    , idExtendInfo / 100
                                                                                    , idExtendInfo % 100
                                                                                    )
        if ftlog.is_debug():
            ftlog.debug(idStr)
            
        info = {}
        info['userId'] = userId
        info['gameId'] = gameId
        info['reason'] = nType
        info['version'] = version
        info['time'] = timeStr
        info['count'] = count
        info['roomId'] = idExtendInfo / 100
        info['extendInfo'] = idExtendInfo % 100
        info['timestamp'] = otime

        return info

class TYRedEnvelopeMgr(object):
    '''
    红包管理器
        1）生成红包
        2）生成红包内容
        3）查询红包
        4）领取红包
    '''
    # 红包支持的配置类型
    # 道具直接传道具ID
    RED_ENVELOPO_CHIP = 'chip'
    RED_ENVELOPO_COUPON = 'coupon'
    RED_ENVELOPO_DIAMOND = 'diamond'
    RED_ENVELOPO_CHARM = 'charm'
    RED_ENVELOPO_EXP = 'exp'
    
    # 红包类型
    # 比赛奖励红包
    RED_ENVELOPE_MATCH = 1
    # 现金桌奖励红包
    RED_ENVELOPE_TABLE = 2
    # 自推广红包
    RED_ENVELOPE_PROMOTE = 3
    # GDSS生成的红包
    RED_ENVELOPE_GDSS = 4
    # 充值返利
    RED_ENVELOPE_CHARGE = 5
    # 注册红包（注册后第一天）
    RED_ENVELOPE_REGISTER = 6
    # 登录红包（注册之后第二天起）
    RED_ENVELOPE_LOGIN = 7

    #版本号
    RED_ENVELOPE_VERSION = 'R1'
    
    #红包ID存储键值
    RED_ENVELOPE_DBKEY = 'hall_red_envelope_count'
    
    #配置类型与用户数据的对应关系
    _rewardMap = {
        RED_ENVELOPO_CHIP: 'user:chip',
        RED_ENVELOPO_COUPON: 'user:coupon',
        RED_ENVELOPO_DIAMOND: 'user:diamond',
        RED_ENVELOPO_CHARM: 'user:charm',
        RED_ENVELOPO_EXP: 'user:exp',
    }
    
    # CMD 生成红包
    HALL_RED_ENVELOPE_CREATE = 'hall_red_envelope_create'
    # CMD 打开红包
    HALL_RED_ENVELOPE_OPEN = 'hall_red_envelope_open'
    # CMD 查询红包
    HALL_RED_ENVELOPE_QUERY = 'hall_red_envelope_query'
    # CMD 查询红包
    HALL_RED_ENVELOPE_QUERY_ID = 'hall_red_envelope_query_id'
    
    def __init__(self):
        self.initialize()
        
    @classmethod
    def initialize(cls):
        return True
    
    @classmethod
    def makeRightResponse(cls, cmd, result):
        '''
        正确应答
            {"cmd": HALL_RED_ENVELOPE_OPEN, "result": {}}
        '''
        response = {}
        response['cmd'] = cmd
        response['result'] = result
        return response
    
    @classmethod
    def makeWrongResponse(cls, cmd, error):
        '''
        错误应答
            {"cmd": HALL_RED_ENVELOPE_OPEN, "error": {"code": 1, "info": "...."}}
        '''
        response = {}
        response['cmd'] = cmd
        response['error'] = error
        return response
    
    @classmethod
    def getAssetsId(cls, itemId):
        assetsId = itemId
        if itemId in cls._rewardMap:
            assetsId = cls._rewardMap[itemId];
        else:
            assetsId = 'item:' + itemId
        
        if ftlog.is_debug():
            ftlog.debug('itemId:' + itemId + ' convert to assetsID:' + assetsId)
        
        return assetsId
    
    @classmethod
    def getAdjustItemId(cls, _itemId):
        global _redEnvelopeLimitsMap
        
        itemId = _itemId
        if itemId not in _redEnvelopeLimitsMap:
            itemId = 'item'
        return itemId
    
    @classmethod
    def getMinValue(cls, _itemId):
        '''
        获取最小值
        '''
        global _redEnvelopeLimitsMap
        
        itemId = cls.getAdjustItemId(_itemId)
        return _redEnvelopeLimitsMap[itemId].minValue
    
    @classmethod
    def getMaxValue(cls, _itemId):
        '''
        获取最大值
        '''
        global _redEnvelopeLimitsMap
        
        itemId = cls.getAdjustItemId(_itemId)
        return _redEnvelopeLimitsMap[itemId].maxValue
    
    @classmethod
    def getMinCount(cls, _itemId):
        '''
        获取最小数量
        '''
        global _redEnvelopeLimitsMap
        
        itemId = cls.getAdjustItemId(_itemId)
        return _redEnvelopeLimitsMap[itemId].minCount
    
    @classmethod
    def getMaxCount(cls, _itemId):
        '''
        获取最大数量
        '''
        global _redEnvelopeLimitsMap
        
        itemId = cls.getAdjustItemId(_itemId)
        return _redEnvelopeLimitsMap[itemId].maxCount
    
    @classmethod
    def buildItem(cls, _itemId, value, count):
        '''
        生成红包内容
        '''
        global _redEnvelopeLimitsMap
        global _redEnvelopeConfig
        
        if ftlog.is_debug():
            ftlog.debug('itemId:', _itemId, 'value:', value, 'count:', count)
            
        itemId = cls.getAdjustItemId(_itemId)
        
        if itemId not in _redEnvelopeLimitsMap:
            if ftlog.is_debug():
                ftlog.debug('itemId: ', itemId, '_redEnvelopeLimitsMap: ', _redEnvelopeLimitsMap)
            return False, _redEnvelopeConfig['tips']['not_support']
        
        # 强校验数值
        if value < _redEnvelopeLimitsMap[itemId].minValue or value > _redEnvelopeLimitsMap[itemId].maxValue:
            return None, _redEnvelopeConfig['tips']['value_out']
        
        # 强校验数量
        if count < _redEnvelopeLimitsMap[itemId].minCount or count > _redEnvelopeLimitsMap[itemId].maxCount:
            return None, _redEnvelopeConfig['tips']['count_out']
        
        assetsId = cls.getAssetsId(_itemId)
        if ftlog.is_debug():
            ftlog.debug('request TYRedEnvelopeItem itmeId:',  _itemId 
                        , 'assetsId:' , assetsId 
                        , 'value:' , value 
                        , 'count:' , count 
                       )
            
        redEnvelopeItem = {}
        redEnvelopeItem['itemId'] = _itemId
        redEnvelopeItem['assetsId'] = assetsId
        redEnvelopeItem['value'] = value
        redEnvelopeItem['count'] = count
        
        return redEnvelopeItem, _redEnvelopeConfig['tips']['item_ok'] 
    
    @classmethod
    def createItem(cls, itemId, assetsId, value, count):
        item = {}
        
        return item
    
    @classmethod
    def buildCount(cls):
        count = daobase.executeMixCmd('incrby', cls.RED_ENVELOPE_DBKEY, 1)
        if ftlog.is_debug():
            ftlog.debug('count:', count)
        return count
    
    @classmethod
    def buildEnvelope(cls, nType, userId, gameId, contents, config, roomId = 0, extendInfo = 0):
        '''
        contents 红包内容:
            [
                {
                    "itemId": "chip",
                    "value": 2000,
                    "count": 10
                },
                {
                    "itemId": "1012",
                    "value": 1,
                    "count": 10
                }
            ]
            
        config 红包配置，用户可以从红包中领取的内容数量:
            {
                "minCount": 1,
                "maxCount": 2
            }
            
        roomId
            申请红包时的比赛ID/房间ID
            
        extendInfo 红包ID的扩展信息
            一般为房间ID/比赛ID + 2位扩展码
            扩展码可用于区分同一情景下发出的不同面额的红包
        '''
        global _redEnvelopeConfig
        
        # todo，当时推广红包时，推广红包每人一个，如果创建过，会失败
        envelopeId = None
        idExtendInfo = roomId * 100 + extendInfo
        result, info = TYRedEnvelopeID.buildID(cls.RED_ENVELOPE_VERSION, nType, gameId, cls.buildCount(), userId, idExtendInfo)
        if result:
            envelopeId = info
        else:
            error = info
            if ftlog.is_debug():
                ftlog.debug('TYRedEnvelopeMgr.buildEnvelope failed, error: ', error)
            return cls.makeWrongResponse(cls.HALL_RED_ENVELOPE_CREATE, error)
        
        if ftlog.is_debug:
            ftlog.debug('envelopeId:', envelopeId)
            
        envelope = TYRedEnvelope().buildEnvelope(envelopeId)
        for content in contents:
            if ftlog.is_debug():
                ftlog.debug('content:', content);
                
            item, error = cls.buildItem(content['itemId'], content['value'], content['count'])
            if item:
                envelope.addEnvelopeItem(item)
            else:
                ftlog.error(error)
                return cls.makeWrongResponse(cls.HALL_RED_ENVELOPE_CREATE, error)
        
        if config == None:
            config = _redEnvelopeConfig['config']
            
        envelope.setReceiveParams(config['minCount'], config['maxCount'])
        envelope.devidePackage()
        # 保存红包
        envelope.save2DB()
        
        response = {}
        response['envelopeId'] = envelopeId
        
        # 每天生成的红包ID存在一个REDIS键值下面
        dayKey = envelope.getPrefix() + pktimestamp.formatTimeDay()
        if ftlog.is_debug():
            ftlog.debug('buildEnvelope save redEnvelopeID to list: ', dayKey)
            
        daobase.executeMixCmd('LPUSH', dayKey, envelopeId)
        
        # 返回结果
        return cls.makeRightResponse(cls.HALL_RED_ENVELOPE_CREATE, response)    
    
    @classmethod
    def changeRedEnvelopeState(cls, envelopeId, state):
        '''
        修改红包状态
        '''
        isExist, info = TYRedEnvelope().loadFromDB(envelopeId)
        if isExist:
            envelope = info
            envelope.setState(state)
            envelope.save2DB()

    @classmethod
    def queryEnvelope(cls, envelopeId):
        '''
            查询红包
        '''
        global _redEnvelopeConfig
        
        isExist, info = TYRedEnvelope().loadFromDB(envelopeId)
        if isExist:
            envelope = info
            query = envelope.queryEnvelope()
            return cls.makeRightResponse(cls.HALL_RED_ENVELOPE_QUERY, query)
        else:
            error = info
            return cls.makeWrongResponse(cls.HALL_RED_ENVELOPE_QUERY, error)
        
    @classmethod
    def queryEnvelopeID(cls, envelopeId):
        '''
            查询红包ID
        '''
        idInfo = TYRedEnvelopeID.parseID(envelopeId)
        if ftlog.is_debug():
            ftlog.debug('envelopeId info:', idInfo)
            
        return cls.makeRightResponse(cls.HALL_RED_ENVELOPE_QUERY_ID, idInfo)
    
    @classmethod
    def openRedEnvelope(cls, envelopeId, userId, itemId=''):
        '''
        打开红包
        @param itemId: 优先获取指定类型的内容
        @return: 
        1) OK
        2) 领过了
        3) 领光了
        4) 过期了
        '''
        global _redEnvelopeConfig
        
        if TYRedEnvelopeID.isExpired(envelopeId):
            return cls.makeWrongResponse(cls.HALL_RED_ENVELOPE_OPEN, _redEnvelopeConfig['tips']['expired'])
        
        isExist, info = TYRedEnvelope().loadFromDB(envelopeId)
        if isExist:
            envelope = info
            result, response = envelope.openRedEnvelope(userId, itemId)
            if result:
                # 如果是推广红包，建立上下线关系
                inInfo = TYRedEnvelopeID.parseID(envelopeId)
                if inInfo['reason'] == cls.RED_ENVELOPE_PROMOTE:
                    # 上线 inInfo['userId']
                    topUserId = inInfo['userId']
                    # 下线 userId
                    if ftlog.is_debug():
                        ftlog.debug('openRedEnvelope.promoteEnvelope, inviter:', topUserId, ' and invitee:', userId)
                        
                    from hall.servers.util.rpc import neituiguang_remote
                    neituiguang_remote.set_inviter(userId, topUserId)
                
                return cls.makeRightResponse(cls.HALL_RED_ENVELOPE_OPEN, response)
            else:
                return cls.makeWrongResponse(cls.HALL_RED_ENVELOPE_OPEN, response)
        else:
            error = info
            return cls.makeWrongResponse(cls.HALL_RED_ENVELOPE_OPEN, error)
        
    @classmethod
    def buildShareTask(cls, envelopeId, userId, gameId, url=None, title=None, desc=None, tips=None, shareIcon=None):
        isExist, info = TYRedEnvelope().loadFromDB(envelopeId)
        if isExist:
            envelope = info
            return envelope.buildShareTask(userId, gameId, url, title, desc, tips, shareIcon)
        else:
            return None
    
class TYRedEnvelopeLimit(object):
    def __init__(self):
        self.itemId = None
        self.minValue = None
        self.maxValue = None
        self.minCount = None
        self.maxCount = None
    
    def decodeFromDict(self, d):
        # itemId
        self.itemId = d.get('itemId')
        if not isstring(self.itemId):
            raise TYBizConfException(d, 'TYRedEnvelopeLimit.itemId must be string')
        
        # minValue
        self.minValue = d.get('minValue', 1)
        if not isinstance(self.minValue, int):
            raise TYBizConfException(d, 'TYRedEnvelopeLimit.minValue must be int')

        # maxValue
        self.maxValue = d.get('maxValue', 1)
        if not isinstance(self.maxValue, int):
            raise TYBizConfException(d, 'TYRedEnvelopeLimit.maxValue must be int')
        
        if self.minValue > self.maxValue:
            raise TYBizConfException(d, 'TYRedEnvelopeLimit minValue > maxValue !!!')
        
        self.minCount = d.get('minCount', 1)
        if not isinstance(self.minCount, int):
            raise TYBizConfException(d, 'TYRedEnvelopeLimit.minCount must be int')
        
        self.maxCount = d.get('maxCount', 1)
        if not isinstance(self.maxCount, int):
            raise TYBizConfException(d, 'TYRedEnvelopeLimit.maxCount must be int')
        
        return self
    
_redEnvelopeConfig = {}
_redEnvelopeLimitsMap = {}
_inited = False

def _reloadConf():
    global _redEnvelopeConfig
    global _redEnvelopeLimitsMap
    
    conf = hallconf.getRedEnvelope()
    _redEnvelopeConfig = conf
    
    limitMap = {}
    for limitDict in conf.get('limits', []):
        limit = TYRedEnvelopeLimit().decodeFromDict(limitDict)
        if limit.itemId in limitMap:
            raise TYBizConfException(limitDict, 'Duplicate limit for %s' % (limit.itemId))
        limitMap[limit.itemId] = limit
    _redEnvelopeLimitsMap = limitMap
    
    if ftlog.is_debug():
        ftlog.debug('hall_red_envelope._reloadConf successed! limits=', _redEnvelopeLimitsMap
            , ' conf=', _redEnvelopeConfig)
    
def _onConfChanged(event):
    if _inited and event.isModuleChanged('red_envelope'):
        ftlog.debug('hall_red_envelope._onConfChanged')
        _reloadConf()

def _initialize():
    ftlog.debug('hall_red_envelope._initialize begin')
    global vipSystem
    global userVipSystem
    global _inited
    if not _inited:
        _inited = True
        _reloadConf()
        pkeventbus.globalEventBus.subscribe(EventConfigure, _onConfChanged)
    ftlog.debug('hall_red_envelope._initialize end')
    
