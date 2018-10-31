# -*- coding:utf-8 -*-
'''
Created on 2016年6月20日

@author: zhaojiangang
'''
from datetime import datetime
from sre_compile import isstring

from hall.entity import hallitem, datachangenotify
from poker.entity.biz.activity.activity import TYActivity
from poker.entity.biz.exceptions import TYBizException
from poker.entity.dao import daobase, sessiondata
from poker.util import strutil
import poker.util.timestamp as pktimestamp
import freetime.util.log as ftlog
from hall.entity.hallconf import HALL_GAMEID
from hall.entity.hallactivity.activity_type import TYActivityType

class UserQuizStatus(object):
    def __init__(self, userId):
        self._userId = userId
        self._betMap = {}
        self._totalBet = 0
        
    @property
    def userId(self):
        return self._userId
    
    def addBet(self, target, bet):
        assert(isstring(target))
        assert(bet > 0)
        self._betMap[target] = self.getBet(target, 0) + bet
        self._totalBet += bet
        
    def getBet(self, target, defVal=0):
        return self._betMap.get(target, defVal)
    
    @property
    def totalBet(self):
        return self._totalBet
    
    def fromDict(self, d):
        for target, bet in d.get('bets', {}).iteritems():
            if bet > 0:
                self.addBet(target, bet)
        return self
    
    def toDict(self):
        return {
            'bets':self._betMap
        }
        
def loadUserQuizStatus(gameId, userId, actId):
    jstr = daobase.executeUserCmd(userId, 'hget', 'act:%s:%s' % (gameId, userId), actId)
    if jstr:
        d = strutil.loads(jstr)
        return UserQuizStatus(userId).fromDict(d)
    return None

def saveUserQuizStatus(gameId, actId, status):
    d = status.toDict()
    jstr = strutil.dumps(d)
    daobase.executeUserCmd(status.userId, 'hset', 'act:%s:%s' % (gameId, status.userId), actId, jstr)

def addUserIdToActivity(gameId, actId, userId):
    daobase.executeMixCmd('sadd', 'act.users:%s:%s' % (gameId, actId), userId)
    
class ParamException(TYBizException):
    def __init__(self, message):
        super(ParamException, self).__init__(-1, message)
    
class BetForm(object):
    def __init__(self):
        self.userId = None
        self.clientId = None
        self.target = None
        self.bet = None
    
    def fromMsg(self, msg):
        self.gameId = msg.getParam('gameId', 9999)
        self.userId = msg.getParam('userId')
        self.clientId = msg.getParam('clientId')
        self.target = msg.getParam('target')
        self.bet = msg.getParam('bet')
        return self
    
    def checkValid(self):
        if not isinstance(self.gameId, int):
            raise ParamException('Bad gameId %s' % (self.gameId))
        
        if not isinstance(self.userId, int) or self.userId <= 0:
            raise ParamException('Bad userId %s' % (self.userId))
        
        if not self.target in ('l', 'm', 'r'):
            raise ParamException('Bad target %s' % (self.target))
        
        if not self.bet in (0, 1, 2):
            raise ParamException('Bad bet %s' % (self.bet))
        
        return self

class TYActivityMatchQuiz(TYActivity):
    TYPE_ID = TYActivityType.ACTIVITY_MATCH_QUIZ
    
    BET_KEYS = ['bet1', 'bet2', 'bet3']
    TIMEFMT = '%m月%d日 %H:%M'
    def __init__(self, dao, clientConfig, serverConfig):
        super(TYActivityMatchQuiz, self).__init__(dao, clientConfig, serverConfig)
        self.activityId = clientConfig['id']
        self.intActivityId = self._serverConf['intActId']
        self.stopBetTime = self.startTime = self.endTime = None
        self.gameId = self._serverConf['gameId']
        startTime = self._serverConf.get('start')
        if startTime is not None:
            self.startTime = datetime.strptime(startTime, '%Y-%m-%d %H:%M:%S')
        stopTime = self._serverConf.get('end')
        if stopTime is not None:
            self.stopTime = datetime.strptime(stopTime, '%Y-%m-%d %H:%M:%S')
        stopBetTime = self._serverConf.get('stopBetTime')
        if stopBetTime is not None:
            self.stopBetTime = datetime.strptime(stopBetTime, '%Y-%m-%d %H:%M:%S')
        
    def _filterScore(self, score):
        l = [
            (100000000, '亿', 2),
            (10000, '万', 2)
        ]
        for divisor, units, ndigits in l:
            if score >= divisor:
                unitsScore = round(score / float(divisor), ndigits)
                fmt = '%d%s' if unitsScore == int(unitsScore) else '%%.%sf%%s' % (ndigits)
                return fmt % (unitsScore, units)
        return str(score)
    
    def loadUserQuizStatus(self, userId):
        status = loadUserQuizStatus(self.gameId, userId, self.activityId)
        if not status:
            status = UserQuizStatus(userId)
        return status
    
    def saveUserQuizStatus(self, status):
        saveUserQuizStatus(self.gameId, self.activityId, status)
    
    def buildChipStr(self, chip):
        return self._filterScore(chip)
    
    def getConfigForClient(self, gameId, userId, clientId):
        status = self.loadUserQuizStatus(userId)
        userAssets = hallitem.itemSystem.loadUserAssets(userId)
        chip = userAssets.balance(gameId, self._serverConf['chipAssetId'], pktimestamp.getCurrentTimestamp()) or 0
        stopBetTime = self.stopBetTime.strftime(self.TIMEFMT) if self.stopBetTime else ''
        config = {
            'stopBetTime':stopBetTime,
            'bgImg':self._serverConf['bgImg'],
            'gameId':self._serverConf['gameId'],
            'chip':self.buildChipStr(chip),
            
            'leftImg':self._serverConf['leftImg'],
            'leftTitle':self._serverConf['leftTitle'],
            'leftBet':strutil.replaceParams(self._serverConf['totalBetDesc'],
                                            {'totalBet':status.getBet('l')}),
            'leftOdds':strutil.replaceParams(self._serverConf['oddsDesc'],
                                             {'odds':self._serverConf['leftOdds']}),
            
            'middleBet':strutil.replaceParams(self._serverConf['totalBetDesc'],
                                            {'totalBet':status.getBet('m')}),
            'middleOdds':strutil.replaceParams(self._serverConf['oddsDesc'],
                                             {'odds':self._serverConf['middleOdds']}),
            'rightImg':self._serverConf['rightImg'],
            'rightTitle':self._serverConf['rightTitle'],
            'rightBet':strutil.replaceParams(self._serverConf['totalBetDesc'],
                                            {'totalBet':status.getBet('r')}),
            'rightOdds':strutil.replaceParams(self._serverConf['oddsDesc'],
                                             {'odds':self._serverConf['rightOdds']}),
            'bet1':self._serverConf['bet1'],
            'bet2':self._serverConf['bet2'],
            'bet3':self._serverConf['bet3']
        }
        self._clientConf['config'] = config
        return self._clientConf
        
    def handleRequest(self, msg):
        action = msg.getParam('action')
        if action == 'bet':
            return self.handleBetMsg(msg)

    def handleBetMsg(self, msg):
        try:
            timestamp = pktimestamp.getCurrentTimestamp()
            nowDT = datetime.fromtimestamp(timestamp)
            # 参数检查
            form = BetForm().fromMsg(msg).checkValid()
            # 检查时间
            if self.startTime and nowDT < self.startTime:
                raise TYBizException(-1, '活动还未开始')
            
            if self.endTime and nowDT >= self.endTime:
                raise TYBizException(-1, '活动已经结束')
            
            if self.stopBetTime and nowDT >= self.stopBetTime:
                raise TYBizException(-1, self._serverConf['stopBetDesc'])
            
            form.clientId = form.clientId or sessiondata.getClientId(form.userId)
            bet = self._serverConf[self.BET_KEYS[form.bet]]
            chip, status = self.bet(form.gameId, form.userId, form.clientId, form.target, bet['amount'], timestamp)
            return self.buildBetResponse(form.gameId, status, chip, form.target)
        except TYBizException, e:
            return {'ec':e.errorCode, 'info':e.message}

    def bet(self, gameId, userId, clientId, target, betAmount, timestamp):
        '''
        @param target:
            下注目标
        @param betId:
            下注额
        '''
        status = self.loadUserQuizStatus(userId)
        
        # 检查totalAmount
        if status.totalBet + betAmount > self._serverConf['totalBetLimit']:
            raise TYBizException(-1, self._serverConf['totalBetLimitDesc'])
        
        userAssets = hallitem.itemSystem.loadUserAssets(userId)
        assetKind, consumeCount, final = userAssets.consumeAsset(gameId,
                                                                  self._serverConf['chipAssetId'],
                                                                  betAmount,
                                                                  timestamp,
                                                                  'ACTIVITY_CONSUME',
                                                                  self.intActivityId)
        if consumeCount != betAmount:
            raise TYBizException(-1, self._serverConf['chipNotEnough'])
        
        ftlog.info('TYActivityMatchQuiz.bet gameId=', gameId,
                   'userId=', userId,
                   'target=', target,
                   'betAmount=', betAmount,
                   'chipAssetId=', self._serverConf['chipAssetId'],
                   'activityId=', self.activityId,
                   'intActivityId=', self.intActivityId,
                   'totalBet=', status.totalBet)
        # 消耗筹码
        status.addBet(target, betAmount)
        self.saveUserQuizStatus(status)
        
        # 加入该活动参与用户集合
        addUserIdToActivity(gameId, self.activityId, userId)
        
        if assetKind and assetKind.keyForChangeNotify:
            datachangenotify.sendDataChangeNotify(HALL_GAMEID, userId, assetKind.keyForChangeNotify)
        return final, status

    def buildBetResponse(self, gameId, status, chip, target):
        ret = {'ec':0}
        ret['chip'] = self.buildChipStr(chip)
        ret['target'] = target
        ret['totalBet'] = strutil.replaceParams(self._serverConf['totalBetDesc'],
                                                {'totalBet':status.getBet(target)})
        return ret

    
