# -*- coding=utf-8 -*-

import  json, time
import freetime.util.log as ftlog
from poker.entity.dao import daobase
from hall.entity import datachangenotify
from poker.entity.biz.item.item import TYAssetUtils
from poker.entity.biz.message.message import sendPrivate
from poker.entity.dao import gamedata as pkgamedata
from hall.entity.hallactivity.activity_exchange_code import TYActivityExchangeCode



def _getReward(self, rdskey, userId, gameId, actId,excode):
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
    sendPrivate(9999, userId, 0, msg)
    result = TYAssetUtils.buildContentsString(assetTupleList)
    ftlog.debug('the last msg is result', result)
    return result

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
    result_, errdes_, unique_ = self._TYActivityExchangeCode__commonCheck(rdskey, clientId)
    if result_ != 0:
        self.sendTodoTask(gameId, userId,errdes_)
        return {"exchangeInfo":errdes_}
    result_ , errdes_ = self._TYActivityExchangeCode__exchange(rdskey, userId, excode, unique_)
    if result_ != 0:
        self.sendTodoTask(gameId, userId, errdes_)
        return {"exchangeInfo":errdes_}
    _rewards = self._TYActivityExchangeCode__getReward(rdskey,userId, gameId, activityId,excode)
        
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
    from datetime import datetime
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

TYActivityExchangeCode._doExchange = _doExchange              
TYActivityExchangeCode._TYActivityExchangeCode__getReward = _getReward



