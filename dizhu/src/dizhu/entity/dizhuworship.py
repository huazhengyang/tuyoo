# -*- coding=utf-8 -*-
'''
Created on 2018年1月2日

@author: wangyonghui

拜财神小游戏
'''
import random
import poker.util.timestamp as pktimestamp

import freetime.util.log as ftlog
from dizhu.activities.toolbox import UserBag
from dizhu.entity import dizhu_util
from dizhu.entity.dizhualert import Alert
from dizhu.entity.dizhuconf import DIZHU_GAMEID
from hall.entity import hallstore
from hall.entity.todotask import TodoTaskHelper, TodoTaskOrderShow
from poker.entity.biz.exceptions import TYBizConfException
from poker.entity.configure import configure
from poker.entity.dao import userchip, daobase, userdata, sessiondata
from poker.entity.events.tyevent import EventConfigure
import poker.entity.events.tyeventbus as pkeventbus
from poker.protocol import router
from poker.util import strutil


class Food(object):
    '''
    贡品对象
    '''
    def __init__(self):
        self.id = None
        self.chip = None
        self.rewards = None

    def toDict(self):
        return {
            'chip': self.chip,
            'id': self.id
        }

    def decodeFromDict(self, d):
        self.id = d.get('id')
        if not isinstance(self.id, int) or self.id < 0:
            raise TYBizConfException(d, 'Food.id must be int and >0')
        self.chip = d.get('chip')
        if not isinstance(self.chip, int) or self.chip < 0:
            raise TYBizConfException(d, 'Food.chip must be int and >0')
        self.rewards = d.get('rewards')
        if not isinstance(self.rewards, list):
            raise TYBizConfException(d, 'Food.rewards must be list')
        return self

    def choiceReward(self):
        chip = dizhu_util.getItemByWeight(self.rewards)
        return chip


class WorshipConf(object):
    '''
    拜财神配置
    '''
    def __init__(self):
        self.messageNumber = None
        self.rankLimit = None
        self.foods = None
        self.messages = None
        self.userFoods = None

    def decodeFromDict(self, d):
        self.messageNumber = d.get('messageNumber')
        if not isinstance(self.messageNumber, int) or self.messageNumber < 0:
            raise TYBizConfException(d, 'WorshipConf.messageNumber must be int and >0')

        self.rankLimit = d.get('rankLimit')
        if not isinstance(self.rankLimit, int) or self.rankLimit < 0:
            raise TYBizConfException(d, 'WorshipConf.rankLimit must be int and >0')

        self.messages = d.get('messages')
        if not isinstance(self.messages, list):
            raise TYBizConfException(d, 'WorshipConf.messages must be list')

        self.foods = d.get('foods')
        if not isinstance(self.foods, list):
            raise TYBizConfException(d, 'WorshipConf.foods must be list')
        tempFoods = []
        for foodDict in self.foods:
            tempFoods.append(Food().decodeFromDict(foodDict))
        self.foods = tempFoods

        self.userFoods = d.get('userFoods')
        if not isinstance(self.userFoods, list):
            raise TYBizConfException(d, 'WorshipConf.userFoods must be list')
        return self


# 配置初始化以及配置更新
_worshipConf = None
_inited = False

def buildRecordUniqueKey():
    return 'worship.messages:%s' % DIZHU_GAMEID

def buildWorshipRankKey():
    return 'worship.ranklist:%s' % DIZHU_GAMEID

def buildUserCostKey():
    """用户拜财神花费"""
    return 'worship.usercost:%s' % DIZHU_GAMEID


def insertRankList(userId, chip):
    """ 拜财神花费金币排行榜 """
    try:
        key = buildWorshipRankKey()
        rankLimit = _worshipConf.rankLimit
        daobase.executeRePlayCmd('zadd', key, chip, userId)
        removed = daobase.executeRePlayCmd('zremrangebyrank', str(key), 0,  -rankLimit - 1)
        if ftlog.is_debug():
            ftlog.debug('dizhuworship.insertRankList',
                        'userId=', userId,
                        'key=', key,
                        'userId=', userId,
                        'chip=', chip,
                        'rankLimit=', rankLimit,
                        'removed=', removed)
    except Exception, e:
        ftlog.error('dizhuworship.insertRankList',
                    'userId=', userId,
                    'chip=', chip,
                    'err=', e.message)

def saveUserCost(userId, cost):
    """保存用户消费金币"""
    try:
        key = buildUserCostKey()
        ret = daobase.executeRePlayCmd('hincrby', key, userId, cost)
        if ftlog.is_debug():
            ftlog.debug('dizhuworship.saveUserCost',
                        'userId=', userId,
                        'cost=', cost,
                        'ret=', ret)
        return int(ret)
    except Exception, e:
        ftlog.error('dizhuworship.saveUserCost',
                    'userId=', userId,
                    'cost=', cost,
                    'err=', e.message)

def clearUserCost():
    """清理用户花费"""
    try:
        key = buildUserCostKey()
        daobase.executeRePlayCmd('del', key)
        if ftlog.is_debug():
            ftlog.debug('dizhuworship.clearUserCost',
                        'key=', key)
    except Exception, e:
        ftlog.error('dizhuworship.clearUserCost',
                    'err=', e.message)

def clearRankList():
    """清理排行榜"""
    try:
        key = buildWorshipRankKey()
        daobase.executeRePlayCmd('del', key)
        if ftlog.is_debug():
            ftlog.debug('dizhuworship.clearRankList',
                        'key=', key)
    except Exception, e:
        ftlog.error('dizhuworship.clearRankList',
                    'err=', e.message)



def _reloadConf():
    global _worshipConf
    d = configure.getGameJson(DIZHU_GAMEID, 'match.worship', {}, 0)
    conf = WorshipConf().decodeFromDict(d)
    _worshipConf = conf
    ftlog.info('dizhuworship._reloadConf successed')

def _onConfChanged(event):
    if _inited and event.isChanged('game:6:match.worship:0'):
        ftlog.info('dizhuworship._onConfChanged')
        _reloadConf()

def _initialize():
    ftlog.info('dizhuworship._initialize begin')
    global _inited

    key = buildUserCostKey()
    first_updated_at = daobase.executeRePlayCmd('hget', key, 'first_updated_at')
    if not first_updated_at:
        first_updated_at = pktimestamp.getCurrentTimestamp()
        daobase.executeRePlayCmd('hset', key, 'first_updated_at', first_updated_at)

    if not _inited:
        _inited = True
        _reloadConf()
        pkeventbus.globalEventBus.subscribe(EventConfigure, _onConfChanged)
    ftlog.info('dizhuworship._initialize end, first_updated_at=', first_updated_at)


class WorshipHelper(object):
    '''
    拜财神戏核心业务
    '''
    @classmethod
    def getUserFoods(cls, userId):
        userChip = userchip.getChip(userId)
        userFoods = _worshipConf.userFoods
        for userFood in userFoods:
            if (userFood['start'] < 0 or userChip >= userFood['start']) and (userFood['end'] < 0 or userChip <= userFood['end']):
                foodList = filter(lambda x: x.id in userFood['foods'], _worshipConf.foods)
                if ftlog.is_debug():
                    ftlog.debug('WorshipHelper.getUserFoods',
                                'userId=', userId,
                                'foodList=', [f.id for f in foodList])
                return foodList

    @classmethod
    def getFood(cls, foodId):
        for food in _worshipConf.foods:
            if food.id == foodId:
                return food
        return

    @classmethod
    def getMessageByFoodId(cls, foodId):
        messages = _worshipConf.messages
        for message in messages:
            if foodId in message['matchId']:
                return random.choice(message['matchDesc'])

    @classmethod
    def getWorshipHistory(cls):
        historyList = daobase.executeRePlayCmd('lrange', buildRecordUniqueKey(), 0, - 1) or []
        ret = []
        for history in historyList:
            try:
                ms = strutil.loads(history)
                nickName, purl = userdata.getAttrs(ms['userId'], ['name', 'purl'])
                ret.append({
                    'userId': ms['userId'],
                    'nickname': str(nickName),
                    'img': purl,
                    'msg': ms['msg'],
                    'chip': ms['chip'],
                    'costChip': ms['costChip']
                })
            except:
                pass
        return ret

    @classmethod
    def getWorship(cls, userId):
        '''
        界面信息
        '''
        userChip = userchip.getChip(userId)
        foodList = cls.getUserFoods(userId)
        return [f.toDict() for f in foodList], userChip

    @classmethod
    def getPray(cls, userId, foodId):
        '''
        获取奖励 
        '''
        food = cls.getFood(foodId)
        if not food:
            return None, None

        if not cls.consumeExpenses(userId, food):
            ftlog.warn('WorshipHelper.getPray',
                       'userId=', userId,
                       'foodId=', foodId,
                       'userChip=', userchip.getChip(userId),
                       'consumeChip=', food.chip)
            payOrder = {
                "contains": {
                    "count": userchip.getChip(userId),
                    "itemId": "user:chip"
                },
                "shelves": [
                    "lessbuychip"
                ]
            }
            clientId = sessiondata.getClientId(userId)
            product, _shelves = hallstore.findProductByPayOrder(DIZHU_GAMEID, userId, clientId, payOrder)
            if not product:
                Alert.sendNormalAlert(DIZHU_GAMEID, userId, '金币不足', '金币不足了， 请去充值吧', None, None)
                return None, None

            buyType = ''
            orderShow = TodoTaskOrderShow.makeByProduct('金币不足', '', product, buyType)
            orderShow.setParam('sub_action_btn_text', '确定')
            mo = TodoTaskHelper.makeTodoTaskMsg(DIZHU_GAMEID, userId, orderShow)
            router.sendToUser(mo, userId)
            return None, None

        # 更新用户花费
        cls.updateUserCost(userId, food.chip)

        # 拜到的奖励
        prayChip = food.choiceReward()
        UserBag.sendAssetsToUser(DIZHU_GAMEID, userId, {'itemId': 'user:chip', 'count': prayChip}, 'DDZ_WORSHIP_SYSTEM')

        # 保存的消息
        msg = cls.getMessageByFoodId(foodId)
        cls.pushRecord(strutil.dumps({
            'userId': userId,
            'msg': msg,
            'chip': prayChip,
            'costChip': food.chip,
        }))
        return {'chip': prayChip, 'msg': msg, 'costChip': food.chip}, userchip.getChip(userId)


    @classmethod
    def consumeExpenses(cls, userId, food):
        '''
        消耗抽奖花费
        '''
        ftlog.info('WorshipHelper.consumeExpenses',
                   'userId=', userId,
                   'food=', food.toDict())
        return UserBag.consumeAssetsIfEnough(userId, 'user:chip', food.chip, 'DDZ_WORSHIP_SYSTEM')

    @classmethod
    def pushRecord(cls, record):
        '''
        增加一条抽奖记录
        '''
        daobase.executeRePlayCmd('lpush', buildRecordUniqueKey(), record)
        length = daobase.executeRePlayCmd('llen', buildRecordUniqueKey())
        if length > _worshipConf.messageNumber:
            daobase.executeRePlayCmd('ltrim', buildRecordUniqueKey(), 0, _worshipConf.messageNumber - 1)


    @classmethod
    def updateUserCost(cls, userId, cost):
        """更新用户花费"""
        # 每天一更新
        currentTimestamp = pktimestamp.getCurrentTimestamp()
        key = buildUserCostKey()
        first_updated_at = daobase.executeRePlayCmd('hget', key, 'first_updated_at') or currentTimestamp
        if pktimestamp.is_same_day(currentTimestamp, first_updated_at):
            userCost = saveUserCost(userId, cost)
            insertRankList(userId, userCost)
        else:
            clearUserCost()
            clearRankList()
            key = buildUserCostKey()
            daobase.executeRePlayCmd('hset', key, 'first_updated_at', currentTimestamp)
            ftlog.info('WorshipHelper.updateUserCost first_updated_at=', first_updated_at)

    @classmethod
    def getWorshipRank(cls):
        """ 获取排行榜 """
        currentTimestamp = pktimestamp.getCurrentTimestamp()
        key = buildUserCostKey()
        first_updated_at = daobase.executeRePlayCmd('hget', key, 'first_updated_at') or currentTimestamp
        if pktimestamp.is_same_day(currentTimestamp, first_updated_at):
            ret = []
            key = buildWorshipRankKey()
            datas = daobase.executeRePlayCmd('zrevrange', key, 0, -1, 'withscores')
            if datas:
                for i in xrange(len(datas) / 2):
                    userId = int(datas[i * 2])
                    chip = int(datas[i * 2 + 1])
                    userName, purl = userdata.getAttrs(userId, ['name', 'purl'])
                    ret.append({'nickname': str(userName),
                                'img': purl,
                                'userId': userId,
                                'chip': chip,
                                'rank': i+1})

            return ret
        else:
            key = buildUserCostKey()
            clearUserCost()
            clearRankList()
            daobase.executeRePlayCmd('hset', key, 'first_updated_at', currentTimestamp)
            ftlog.info('WorshipHelper.getWorshipRank first_updated_at=', first_updated_at)
            return []
