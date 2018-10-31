# -*- coding=utf-8 -*-

import  json, time, random
from datetime import datetime
import freetime.util.log as ftlog
from poker.entity.biz.activity.activity import TYActivity
from hall.entity.todotask import TodoTaskShowInfo, TodoTaskHelper
from poker.protocol import router
from poker.entity.dao import daobase, sessiondata
from freetime.entity.msg import MsgPack
from hall.entity import datachangenotify
from poker.entity.biz.item.item import TYAssetUtils
from poker.entity.biz.message import message
from sre_compile import isstring
from poker.entity.dao import gamedata as pkgamedata
from hall.entity.hallactivity.activity_type import TYActivityType

class TYActivityExchangeCode(TYActivity):
    TYPE_ID = TYActivityType.ACTIVITY_EXCHANGE_CODE
    
    _script = ''
    _scriptName = ""
    _hasLoadedScript = False
    _wordlist = '0123456789ABCDEFGHIGKLMNOPQRSTUVWXYZ'
    _wordlist2 = '0123456789ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    _rewardMap = {
          'CHIP':{'name':u"金币",'unit':u"个", 'itemId':'user:chip'},
          'COUPON':{'name':u"奖券",'unit':u"个", 'itemId':'user:coupon'},
          'NEWER':{'name':u"新手大礼包",'unit':u"个", 'itemId':'item:1001'},
          'MOONBOX':{'name':u"月光宝盒",'unit':u"个", 'itemId':'item:3002'},
          'MOONKEY':{'name':u"月光之钥",'unit':u"个", 'itemId':'item:3001'},
          'CARDMATCH':{'name':u"参赛券",'unit':u"个", 'itemId':'item:1007'},
          'CARDNOTE':{'name':u"记牌器",'unit':u"个", 'itemId':'item:2003'},
          'VOICE':{'name':u"语音小喇叭",'unit':u"个", 'itemId':'item:2002'}, 
          '1010':{'name':u'三星S6抽奖礼包','unit':u'个','itemId':'item:1010'},
          '1011':{'name':u'51特惠大礼包','unit':u'个','itemId':'item:1011'},
          '1012':{'name':u'51特惠礼包','unit':u'个','itemId':'item:1012'},
          '88':{'name':u'会员','unit':u'天','itemId':'item:88'},
                  }
    
    @classmethod
    def initialize(cls):
        if cls._hasLoadedScript:
            return
        cls._scriptName = "activity_exchange_code_script"
        cls._script = '''
        local userId = tostring(KEYS[1])
        local serial = tostring(KEYS[2])
        local excode = tostring(KEYS[3])
        local unique = tonumber(KEYS[4])
        
        local userkey = "excodeuser:"..serial
        local readykey = "excodeready:"..serial
        local finishkey = "excodefinish:"..serial
        
        if unique >= 0.9 then
            local isdeal = redis.call("SISMEMBER", userkey, userId)
            if isdeal == 1 then
                return 1
            end        
        end
               
        local isfinish = redis.call("SISMEMBER", finishkey, excode)
        if isfinish == 1 then
            return 2
        end
        
        local isexist = redis.call("SISMEMBER", readykey, excode)
        if isexist == 0 then
            return 3
        end
        
        redis.call("SADD", userkey, userId)
        redis.call("SMOVE", readykey, finishkey, excode)
        return 0
        '''
        
        daobase.loadLuaScripts(cls._scriptName, cls._script)
        ftlog.info('ExchangeCode->initialize', cls._scriptName)
  
        #2018-3-19 新兑换码脚本 xy  
        cls._scriptNameNew = "activity_new_exchange_code_script"
        cls._scriptNew = '''
        local userId = tostring(KEYS[1])
        local serial = tostring(KEYS[2])
        local excode = tostring(KEYS[3])
        local unique = tonumber(KEYS[4])
        local deviceId = tostring(KEYS[5])
        local receiveNum = tonumber(KEYS[6])
        
        local userkey = "excodeuser:"..serial
        local devicekey = "excodedevice:"..serial
        local useinfokey = "excode:"..serial
        
        if unique >= 0.9 then
            local isdealuser = redis.call("SISMEMBER", userkey, userId)
            if isdealuser == 1 then
                return 1
            end        
        end
               
        local usenum = redis.call("HGET", useinfokey, excode)
        if usenum then
            if tonumber(usenum) >= receiveNum then
                return 4
            end
        else
            return 3
        end

        local isdealdevice = redis.call("SISMEMBER", devicekey, deviceId)
        if isdealdevice == 1 then
            return 5
        end
        
        redis.call("SADD", userkey, userId)
        redis.call("SADD", devicekey, deviceId)
        redis.call("HSET", useinfokey, excode, tonumber(usenum) + 1)
        return 0        
        '''
        
        daobase.loadLuaScripts(cls._scriptNameNew, cls._scriptNew)
        ftlog.info('NewExchangeCode->initialize', cls._scriptNameNew)
        cls._hasLoadedScript = True
        return True
    
    @classmethod
    def generateNumberCodeList(cls, codeLength, count):
        assert(codeLength >= 1 and codeLength <= 32)
        
        maxValue = 10 ** codeLength
        
        # 最少从10选1
        selectN = maxValue / count
        if selectN >= 10:
            partLen = maxValue / count
            for i in xrange(count):
                codeValue = random.randint(i, i + partLen - 1)
                fmt = '%%0%sd' % (codeLength)
                yield fmt % (codeValue)
                i += partLen
    
    @classmethod
    def generateNormalCodeList(cls, codeLength, count):
        excodeSet = set()
        while count > 0:
            codeValue = ''           
            for _ in xrange(codeLength):
                codeValue += random.choice(cls._wordlist)
            if codeValue not in excodeSet:
                excodeSet.add(codeValue)
                count -= 1
                yield codeValue
    
    @classmethod
    def decodeClientIds(cls, clientIds):
        try:
            clientIds = json.loads(clientIds)
            if not isinstance(clientIds, list):
                return 1, 'client_ids参数必须是数组'
            for clientId in clientIds:
                if not isstring(clientId):
                    return 1, 'client_ids参数必须是字符串数组'
            return 0, clientIds
        except:
            return 1, 'client_ids参数错误'
        
    @classmethod
    def decodeRewards(cls, rewards):
        try:
            rewards = json.loads(rewards)
            if not isinstance(rewards, list) or not rewards:
                return 1, 'rewards参数必须是非空数组'
            for reward in rewards:
                if not isinstance(reward, dict) or not reward:
                    return 1, 'rewards参数必须是非空dict数组'
                for assetKindId, count in reward.iteritems():
                    if not isstring(assetKindId):
                        return 1, 'rewards里的奖励的key必须是字符串'
                    if not isinstance(count, int) or count <= 0:
                        return 1, 'rewards里的奖励的count必须是int并且>0'
            return 0, rewards
        except:
            return 1, 'rewards参数错误'
    
    @classmethod
    def doQueryCode(cls,paramsDict):
        Ecode = paramsDict.get('codeUser', '')
        #截取6位
        excode = Ecode.upper()
        cdkey = excode[0:6]
        return cls.findMessageForCdkey(cdkey)
    @classmethod
    def doQueryTimeCode(cls,paramsDict):
        """
        废弃，目前的生成规则已不再依赖时间，原因不明，人员已离职
        """
        timeTemp = paramsDict.get('strTime', '')
        batchNum = paramsDict.get('batchNum', '')
        batchNum =int(batchNum)
        nowDate = datetime.strptime(timeTemp, "%Y%m%d").date()
        cdkey = cls.generateSeriesForQuery('ct_number', nowDate, batchNum)
        ftlog.debug('doQueryTimeCode cdkey =', cdkey)
        
        return cls.findMessageForCdkey(cdkey)
    @classmethod
    def doExcodeForUser(cls,paramsDict):
        userId = paramsDict.get('userId','')
        return daobase.executeMixCmd('HGET', 'userID:' + str(userId),'common')
    @classmethod
    def findMessageForCdkey(cls,cdkey):
        #兑换码的信息
        exchange_code = {}
        exchange_code["rewards"] = daobase.executeMixCmd('HGET', 'excodeinfo:' + cdkey, 'rewards')#list
        exchange_code["common"] = daobase.executeMixCmd('HGET', 'excodeinfo:' + cdkey, 'common')#Dict
        exchange_code["excodeuser"] = daobase.executeMixCmd('SMEMBERS', 'excodeuser:' + cdkey)#list
        exchange_code["excodeready"] = daobase.executeMixCmd('SMEMBERS', 'excodeready:' + cdkey)#list
        exchange_code["excodefinish"] = daobase.executeMixCmd('SMEMBERS', 'excodefinish:' + cdkey)#list
        return exchange_code
    
    @classmethod
    def doGenerateCode(cls, paramsDict):
        VALIDS_CODE_TYPE = ['ct_normal', 'ct_number', 'ct_new']  #2018-3-19 添加新兑换码  xy
        clientIds = paramsDict.get('client_ids', '[]')
        begin_time = paramsDict.get('begin_time', '')
        end_time = paramsDict.get('end_time', '')
        rewards = paramsDict.get('rewards', '[]')
        count = paramsDict.get('count', 0)
        unique = paramsDict.get('unique', 0)
        #新增参数 游戏ID 两位 20160412
        useGameId = paramsDict.get('useGameId',0)
        #新增参数 推广人ID 就是用户ID
        promoteId = paramsDict.get('promoteId', 0)
        codeType = paramsDict.get('codeType', 'ct_normal')
        receiveNum = paramsDict.get('receiveNum', 0)   #2018-3-19 新兑换码所需可以领取次数的字段  xy
        
        ftlog.info('ExchangeCode->doGenerateCode clientids=', clientIds,
                   'begin_time=', begin_time,
                   'end_time=', end_time,
                   'rewards=', rewards,
                   'count=', count,
                   'unique=', unique,
                   'codeType=', codeType,
                   'useGameId=', useGameId,
                   'promoteId=', promoteId,
                   'receiveNum=', receiveNum)
        
        mo = MsgPack()
        
        ec, clientIds = cls.decodeClientIds(clientIds)
        if ec != 0:
            mo.setError(ec, clientIds)
            return mo
        
        ec, rewards = cls.decodeRewards(rewards)
        if ec != 0:
            mo.setError(ec, rewards)
            return mo

        try:
            receiveNum = int(receiveNum)
            if receiveNum < 0:
                mo.setError(1, 'receiveNum必须是>=0的整数')
                return mo
        except:
            mo.setError(1, 'receiveNum必须是>=0的整数')
            return mo
                
        try:
            count = int(count)
            if count <= 0:
                mo.setError(1, 'count必须是>0的整数')
                return mo
        except:
            mo.setError(1, 'count必须是>0的整数')
            return mo
        
        try:
            unique = int(unique)
            if unique not in (0,1):
                mo.setError(1, 'unique必须是0或1的整数')
                return mo
        except:
            mo.setError(1, 'unique必须是0或1的整数')
            return mo
    
        try:
            unique = int(unique)
            if unique not in (0,1):
                mo.setError(1, 'unique必须是0或1的整数')
                return mo
        except:
            mo.setError(1, 'unique必须是0或1的整数')
            return mo
        
        if codeType not in VALIDS_CODE_TYPE:
            mo.setError(1, 'codeType必须在%s中' % (VALIDS_CODE_TYPE))
            return mo
        
        try:
            datetime.strptime(begin_time, '%Y-%m-%d %H:%M:%S')
        except:
            mo.setError(1, 'begin_time必须是时间字符串')
            return mo
        
        try:
            datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
        except:
            mo.setError(1, 'end_time必须是时间字符串')
            return mo
        
        nowDate = datetime.now().date()
        seqCount,seriesCode, codeList = cls.generateCodes(nowDate, codeType, count, useGameId)
 
        #2018-3-19 新兑换码使用新的存储格式，旧的不变 xy      
        if codeType == 'ct_new':
            useinfoKey = 'excode:%s' % (seriesCode)
            for code in codeList:
                daobase.executeMixCmd('HSET', useinfoKey, code, 0)  #2018-3-19 生成新的兑换码已经使用次数为0 xy
        else:
            readyKey = 'excodeready:%s' % (seriesCode)
            for code in codeList:
                daobase.executeMixCmd('SADD', readyKey, code)
        
        # 通用配置    
        common_ = {
                   'begin_time' : begin_time,
                   'end_time' : end_time,
                   'client_ids' : clientIds,
                   'generate_time' : datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                   'unique' : unique,
                   'seqCount':seqCount,
                   'useGameId':useGameId,
                   'promoteId':promoteId,
                   'receive_num':receiveNum   #2018-3-19 新兑换码所需可以领取次数的字段  xy
                   }
        daobase.executeMixCmd('HSET', 'excodeinfo:' + seriesCode, 'common', json.dumps(common_))
        daobase.executeMixCmd('HSET', 'excodeinfo:' + seriesCode, 'rewards', json.dumps(rewards))
        
        mo.setResult('common', common_)
        mo.setResult('rewards', rewards)
        mo.setResult('excodes', codeList)
        ftlog.info('ExchangeCode->doGenerateCode', 'mo=', mo)
        return mo
        
    @classmethod
    def generateCodes(cls, nowDate, codeType, count, useGameId):
        codeList = []
        seqCount,seriesCode = cls.generateSeries(codeType, nowDate, useGameId)
        if codeType == 'ct_number':
            #20160412德州需求 兑换码更改为12位
            for c in cls.generateNumberCodeList(12, count):
                codeList.append('%s%s' % (seriesCode, c))
        else:
            for c in cls.generateNormalCodeList(10, count):
                codeList.append('%s%s' % (seriesCode, c))
        return seqCount,seriesCode, codeList
    @classmethod
    def generateSeriesForQuery(cls, codeType, nowDate,num):
        if codeType == 'ct_number':
            _snowDateStr = nowDate.strftime('%Y%m%d')
            yearStartDate = nowDate.replace(month=1, day=1)
            days = '%03d' % ((nowDate - yearStartDate).days)
            year = '%02d' % (nowDate.year % 100)
            return '%s%s%s' % (year, days, num)
        else:
            return cls.__generateSeries()
    @classmethod
    def generateSeries(cls, codeType, nowDate, useGameId):
        if codeType == 'ct_number':
            nowDateStr = nowDate.strftime('%Y%m%d')
            dateSeqKey = daobase.executeMixCmd('hincrby', 'excodenum', nowDateStr, 1)
            if dateSeqKey > 10:
                return 1, '每天最多生成10组兑换码'
            dateSeqKey -= 1
            yearStartDate = nowDate.replace(month=1, day=1)
            _days = '%03d' % ((nowDate - yearStartDate).days)
            _year = '%02d' % (nowDate.year % 100)
            nowSeries = daobase.executeMixCmd('hincrby', 'excodeSeries', useGameId , 1)
            if nowSeries >= 10000 :
                raise Exception('游戏' + str(useGameId) + '兑换码生成已满,请联系大厅')
            return dateSeqKey,'%s%04d' % (useGameId, nowSeries)
        else:
            return 10,cls.__generateSeries()
    
    @classmethod
    def doGenerateCodeOld(cls, paramsDict):
        mo = MsgPack()
        clientIds = paramsDict.get('client_ids', '[]')
        begin_time = paramsDict.get('begin_time', '')
        end_time = paramsDict.get('end_time', '')
        rewards = paramsDict.get('rewards', '[]')
        count = int(paramsDict.get('count', 0))
        unique = int(paramsDict.get('unique', 0))
        version = int(paramsDict.get('version', 0))
        activityId = ""
        if version == 2:
            activityId = paramsDict.get('activityId', '')
            if not activityId:
                mo.setError(1, u'缺少activityId')
                return mo                
        ftlog.info('ExchangeCode->doGenerateCode', 'clientids=', clientIds, 'begin_time=', begin_time, \
                   'end_time=', end_time, 'rewards=', rewards, 'count=', count, 'unique=', unique,
                   "version=", version, "activityId=",  activityId)
                
        try:
            clientIds = json.loads(clientIds)
            rewards = json.loads(rewards)
        except:
            mo.setError(1, u'clientIds或者rewards不是json格式,请重配置')
            return mo
        
        if len(clientIds) == 0 or len(rewards) == 0:
            mo.setError(1, u'必须配置生效的clientId和兑换发放奖励,请重配置')
            return mo  
        
        if count == 0:
            mo.setError(1, u'至少生应成一个兑换码')
            return mo
        
        if version == 2:
            seriesCode = activityId
            exCodeLen = 5
            wordlist = cls._wordlist2
        else:
            seriesCode = cls.__generateSeries()
            exCodeLen = 10
            wordlist = cls._wordlist
            
        excodeSet = set([])
        while count > 0:
            code_ = ''           
            for _ in xrange(exCodeLen):
                code_ += random.choice(wordlist)
            if version == 2:
                excode_ = code_
            else:
                excode_ = seriesCode + code_
            if excode_ not in excodeSet:
                excodeSet.add(excode_)
                count -= 1
                
        excodeList = list(excodeSet)        
        for i in xrange(len(excodeList)):
            daobase.executeMixCmd('SADD', 'excodeready:' + seriesCode, excodeList[i])
        
        # 通用配置    
        common_ = {
                   'begin_time' : begin_time,
                   'end_time' : end_time,
                   'client_ids' : clientIds,
                   'generate_time' : datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                   'unique' : unique
                   }
        daobase.executeMixCmd('HSET', 'excodeinfo:' + seriesCode, 'common', json.dumps(common_))
        daobase.executeMixCmd('HSET', 'excodeinfo:' + seriesCode, 'rewards', json.dumps(rewards))
        
        mo.setResult('common', common_)
        mo.setResult('rewards', rewards)
        mo.setResult('excodes', excodeList)
        ftlog.info('ExchangeCode->doGenerateCode', 'mo=', mo)
        return mo
        
    @classmethod
    def __generateSeries(cls):
        wordlist = cls._wordlist
        timenow = int(time.time()) - 100000000
        seriescode = ''
        while True:
            mod = timenow % len(wordlist)
            seriescode += wordlist[mod]
            timenow = int(timenow / len(wordlist))
            if timenow == 0:
                break
        return seriescode      
    
    def __init__(self, dao, clientConfig, serverConfig):
        super(TYActivityExchangeCode, self).__init__(dao, clientConfig, serverConfig)
        self.initialize()
         
    def handleRequest(self, msg):
        userId = msg.getParam('userId')
        gameId = msg.getParam('gameId')   
        clientId = msg.getParam("clientId")     
        activityId = msg.getParam("activityId")
        action = msg.getParam("action")
        if action == "exchange":
            actionParams = msg.getParam('actionParams')
            if not actionParams or "exchangeCode" not in actionParams:
                return {"errorInfo":"exchangeCode not found","errorCode":3}
            else:
                exchangeCode = actionParams["exchangeCode"]
            return self._doExchange(userId, gameId, clientId, activityId, exchangeCode)
        else:
            return {"errorInfo":"unknown action","errorCode":1}
 
    def sendTodoTask(self, gameId, userId, info):
        task = TodoTaskShowInfo(info, True)
        mo = TodoTaskHelper.makeTodoTaskMsg(gameId, userId, task)
        router.sendToUser(mo, userId)
                
    def _doExchange(self, userId, gameId, clientId, activityId, excode):
        if len(excode) != 16 and len(excode) != 5 and len(excode) != 18: 
            self.sendTodoTask(gameId, userId,"兑换码错误！")
            return {"exchangeInfo":"兑换码错误！"}
        if len(excode) == 5:
            rdskey = activityId          
        else:
            excode = excode.upper()
            rdskey = excode[0:6]
        ftlog.debug('this exchange rdskey = ', rdskey,
                    'this exchange clientId = ',clientId)
        #核对公共配置信息，返回（核对结果，错误信息，unique，可领取次数） 2018-3-20 xy
        result_, errdes_, unique_, receive_num_ = self.__commonCheck(rdskey, clientId)
        if result_ != 0:
            self.sendTodoTask(gameId, userId,errdes_)
            return {"exchangeInfo":errdes_}
        #修改兑换流程，新添加两个参数 clientId，receive_num 2018-3-20 xy
        deviceId = sessiondata.getDeviceId(userId)
        result_ , errdes_ = self.__exchange(rdskey, userId, excode, deviceId, receive_num_, unique_)
        if result_ != 0:
            self.sendTodoTask(gameId, userId, errdes_)
            return {"exchangeInfo":errdes_}
        _rewards = self.__getReward(rdskey,userId, gameId, activityId,excode)
        
        if len(excode) == 18 :
            #将用户Id和推广人Id进行绑定
            common_ = daobase.executeMixCmd('HGET', 'excodeinfo:' + rdskey, 'common')
            try:
                common_ = json.loads(common_)
            except:
                return {}
            nowPromoteId = pkgamedata.getGameAttr(userId, gameId, 'promoteId') or 0
            ftlog.debug('__getReward.userId=', userId,
                        'gameId=', gameId,
                        'common_=', common_,
                        'nowPromoteId=', nowPromoteId)
            if int(nowPromoteId) <= 0 and int(userId) != int(common_.get('promoteId', 0)):
                pkgamedata.setGameAttr(userId, gameId, 'promoteId', common_.get('promoteId', 0))
        
        resultInfo = '恭喜您兑换成功,获得：' + _rewards
        self.sendTodoTask(gameId, userId, resultInfo)
        #兑换码使用成功，记录在用户里
        messageUser = daobase.executeMixCmd('HGET', 'userID:' + str(userId),'common')
        if isinstance(messageUser, (str, unicode)) :
            messageUser = json.loads(messageUser)
        else:
            messageUser = {}
        if 'excode' not in messageUser :
            messageUser = {
                           'userId':userId,
                           'excode':[excode],
                           'time':[datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
                           }
        else:
            messageUser['excode'].append(excode)
            messageUser['time'].append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        daobase.executeMixCmd('HSET', 'userID:' + str(userId),'common' ,json.dumps(messageUser))
        return {"exchangeInfo": resultInfo}

# 由于新兑换码，修改公共配置信息的核对过程 2018-3-20 xy
    def __commonCheck(self, rdskey, clientId):
        config_ = daobase.executeMixCmd('HGET', 'excodeinfo:' + rdskey, 'common')
        ftlog.debug('this exchange config_ = ', config_)
        try:
            ftlog.debug('ExchangeCode->__commonCheck load common', config_)
            config_ = json.loads(config_)            
        except:
            return 1, u'无效兑换码', 0, 0
        
        unique = 0
        if 'unique' in config_:
            unique = int(config_['unique'])
            
        # 取出可领取次数 2018-3-20 xy
        receive_num = 0
        if 'receive_num' in config_:
            receive_num = int(config_['receive_num'])
        
        date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if 'begin_time' in config_:
            begin_time = config_['begin_time']
            if begin_time and (date_now < begin_time):
                return 1, u'活动还没开始', unique, receive_num
        if 'end_time' in config_:
            end_time = config_['end_time']
            if end_time and (date_now > end_time):
                return 2, u'活动已经结束', unique, receive_num
        if 'client_ids' in config_:
            client_ids = config_['client_ids']
            if 'ALL' not in client_ids: # client_ids = ['ALL'],说明是全部ID都支持的
                if clientId not in client_ids:
                    return 3, u'不在活动条件内', unique, receive_num
        return 0, '', unique, receive_num

    #修改兑换流程，新添加两个参数 clientId，receive_num,可领取次数大于1次时，走新兑换流程 2018-3-20 xy
    def __exchange(self, rdskey, uid, excode, deviceid, receive_num = 0, unique = 0):
        if receive_num >= 1:
            result = daobase.executeMixLua(self._scriptNameNew, 6,
                                    uid, rdskey, excode, unique, deviceid, receive_num)
        else:
            result = daobase.executeMixLua(self._scriptName, 4,
                                    uid, rdskey, excode, unique)
        
        ftlog.debug('ExchangeCode->__exchange() waitForRedis return', result)
        error_des = ''
        if result == 1:
            error_des = u'每位用户只能兑换一次'
        elif result == 2:
            error_des = u'该兑换码已经使用'
        elif result == 3:
            error_des = u'该兑换码无效'
        elif result == 4:
            error_des = u'该兑换码使用次数已用完'
        elif result == 5:
            error_des = u'每个设备只能兑换一次'
        return result, error_des 
    
    '''
        <option value="NEWER">新手大礼包</option>
                                            <option value="MOONBOX">月光宝盒</option>
                                            <option value="MOONKEY">月光之钥</option>
                                            <option value="CARDMATCH">参赛券</option>
                                            <option value="COUPON">奖券</option>
                                            <option value="CARDNOTE">记牌器</option>
                                            <option value="VOICE">语音小喇叭</option>
  ExchangeCode->doGenerateCode mo= {'result': {'excodes': ['7NDLYLH06W4KN7U1',  ], 
  'rewards': [{u'CHIP': u'1'}, {u'CARDMATCH': u'1'}, {u'CARDNOTE': u'1'}], 
  'common': {'unique': 0, 'client_ids': [u'ALL'], 'end_time': '2015-04-01 21:07:45', 
  'generate_time': '2015-04-01 21:14:59', 'begin_time': '2015-04-01 21:07:43'}}}      
    '''
    def __getReward(self, rdskey, userId, gameId, actId,excode):
        config_ = daobase.executeMixCmd('HGET', 'excodeinfo:' + rdskey, 'rewards')
        
        try:
            config_ = json.loads(config_)
        except:
            return {}
        
        if not isinstance(config_, list):
            return {}
        
        rewards = {}
        items_ = config_
        ftlog.debug('ExchangeCode.__getReward', 'items=', items_)
        from hall.entity.hallitem import itemSystem
        userAssets = itemSystem.loadUserAssets(userId)
        assetTupleList = []
        for itemDict in items_:
            for assetKindId, count in itemDict.iteritems():
                count = int(count)
                if assetKindId in self._rewardMap:
                    assetKindId = self._rewardMap[assetKindId]['itemId']
                assetTuple = userAssets.addAsset(gameId, assetKindId, count,
                                                 int(time.time()),
                                                 'ACTIVITY_EXCHANGE', 0)
                    
                rewards[assetKindId] = count
                assetTupleList.append(assetTuple)
        datachangenotify.sendDataChangeNotify(gameId, userId, TYAssetUtils.getChangeDataNames(assetTupleList))
        ftlog.info('ExchangeCode->__statistics userid=', userId,
                   'excode=', excode,
                   'rewards=', rewards)
        msg = '兑换码兑换礼品成功，已自动加入到您的背包中，请查收。'
        message.send(9999, message.MESSAGE_TYPE_SYSTEM, userId, msg)
        result = TYAssetUtils.buildContentsString(assetTupleList)
        ftlog.debug('the last msg is result', result)
        return result
    '''
    def __getReward(self, rdskey, userId, gameId, actId,excode):
        config_ = daobase.executeMixCmd('HGET', 'excodeinfo:' + rdskey, 'rewards')
        try:
            config_ = json.loads(config_)
        except:
            return {}
        
        if not isinstance(config_, list):
            return {}
        
        rewards = {}
        items_ = config_
        ftlog.debug('ExchangeCode.__getReward', 'items=', items_)
        from hall.entity.hallitem import itemSystem
        userAssets = itemSystem.loadUserAssets(userId)
        changed = []
        result = ""
        for i in xrange(len(items_)):
            for (key, value) in items_[i].items():
                value = int(value)
                if key not in self._rewardMap:
                    assetKind,count,_ = userAssets.addAsset(gameId, key, value,
                                    int(time.time()),
                                    'ACTIVITY_EXCHANGE', 0)
                    
                    changed.append(assetKind)
                    rewards[key] = value
                    result += hallitem.buildContent(assetKind, count)
                else:
                    value = int(value)
                    assetKindId = self._rewardMap[key]['itemId']
                    asset,count,_ = userAssets.addAsset(gameId, assetKindId, value,
                                                int(time.time()),
                                                'ACTIVITY_EXCHANGE', 0)
                    changed.append(asset)                        
                    rewards[key] = value
                    result += hallitem.buildContent(asset, count)
        ret = set()
        ftlog.debug('the last msg is result', result)
        for assetKind in changed:
            if assetKind.keyForChangeNotify:
                ret.add(assetKind.keyForChangeNotify)
        datachangenotify.sendDataChangeNotify(gameId, userId, ret)
        ftlog.info('ExchangeCode->__statistics userid =', userId,
                   'excode = ', excode,
                   'rewards = ', rewards)
        msg = '兑换码兑换礼品成功，已自动加入到您的背包中，请查收。'
        sendPrivate(9999, userId, 0, msg)
        ftlog.debug('the last msg is result', result)
        return result
        '''