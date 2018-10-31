# -*- coding=utf-8 -*-
'''
Created on 2017年8月15日

@author: wangyonghui

钓鱼小游戏
'''
import copy
import json
import random

import freetime.util.log as ftlog
from dizhu.activities.toolbox import UserBag
from dizhu.entity import dizhu_util
from dizhu.entity.dizhualert import Alert
from dizhu.entity.dizhuconf import DIZHU_GAMEID
from hall.entity import hallstore, hallitem
from hall.entity.todotask import TodoTaskHelper, TodoTaskOrderShow
from poker.entity.biz.content import TYContentItem
from poker.entity.biz.exceptions import TYBizConfException
from poker.entity.configure import configure
from poker.entity.dao import userchip, daobase, userdata, sessiondata
from poker.entity.events.tyevent import EventConfigure
import poker.entity.events.tyeventbus as pkeventbus
from poker.protocol import router
from poker.util import strutil


def buildRecordUniqueKey():
    return 'fishing.messages:%s' % DIZHU_GAMEID

def buildUserFishingCountKey(userId):
    return 'fishing.count:%s:%s' % (DIZHU_GAMEID, userId)

def loadUserFishingCount(userId, fishId):
    try:
        key = buildUserFishingCountKey(userId)
        count = daobase.executeRePlayCmd('hget', key, fishId)
        if ftlog.is_debug():
            ftlog.debug('loadUserFishingCount userId=', userId,
                        'fishId=', fishId,
                        'count=', count)
        if count:
            return int(count)
    except:
        ftlog.error('loadUserFishingCount userId=', userId)
    return 0


def saveUserFishingCount(userId, fishId, count):
    key = buildUserFishingCountKey(userId)
    ret = daobase.executeRePlayCmd('hset', key, fishId, count)
    if ftlog.is_debug():
        ftlog.debug('saveUserFishingCount userId=', userId,
                    'fishId=', fishId,
                    'count=', ret)
    return int(ret) if ret else 0



class Fish(object):
    '''
    鱼对象
    '''
    def __init__(self):
        self.id = None
        self.name = None
        self.type = None
        self.rewards = None
        self.pic = None
        self.smallPic = None
        self.needNum = 0

    def toDict(self):
        count1 = self.rewards[0]['item'].count
        count2 = self.rewards[-1]['item'].count
        if count1 >= 10000:
            if count1 % 10000 == 0:
                count1 = '%s万' % (count1 / 10000)
            else:
                count1 = '%s万' % (float(count1) / 10000)

        if count2 >= 10000:
            if count2 % 10000 == 0:
                count2 = '%s万' % (count2 / 10000)
            else:
                count2 = '%s万' % (float(count2) / 10000)

        des = '%s~%s' % (count1, count2)
        pic = _fishingConf.coinPic
        if self.type == 'coupon':
            #des = '%s' % self.rewards[-1]['item'].count
            assetKind = hallitem.itemSystem.findAssetKind('user:coupon')
            des = assetKind.buildContent(self.rewards[-1]['item'].count)
            pic = _fishingConf.couponPic if _fishingConf.couponPic else assetKind.pic

        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'pic': self.pic,
            'smallPic': self.smallPic,
            'needNum': self.needNum,
            'rewards': {
                'count': self.rewards[-1]['item'].count,
                'desc': des,
                'pic': pic
            }
        }

    def decodeFromDict(self, d):
        self.needNum = d.get('needNum', 0)
        if not isinstance(self.needNum, int) or self.needNum < 0:
            raise TYBizConfException(d, 'Fish.needNum must be int and >0')
        self.id = d.get('id')
        if not isinstance(self.id, int) or self.id < 0:
            raise TYBizConfException(d, 'Fish.id must be int and >0')
        self.name = d.get('name')
        if not isinstance(self.name, (str, unicode)):
            raise TYBizConfException(d, 'Fish.name must be str')
        self.type = d.get('type')
        if not isinstance(self.type, (str, unicode)):
            raise TYBizConfException(d, 'Fish.type must be str')

        if not isinstance(d.get('rewards'), list):
            raise TYBizConfException(d, 'Fish.rewards must be list')
        tempRewards = []
        for rewardDict in d.get('rewards'):
            itemDict = rewardDict.get('item', {})
            if itemDict:
                tempRewards.append({
                    'item': TYContentItem.decodeFromDict(itemDict),
                    'weight': rewardDict.get('weight')
                })
        self.rewards = tempRewards
        self.pic = d.get('pic')
        if not isinstance(self.name, (str, unicode)):
            raise TYBizConfException(d, 'Fish.pic must be str')

        self.smallPic = d.get('smallPic', '')
        if not isinstance(self.name, (str, unicode)):
            raise TYBizConfException(d, 'Fish.smallPic must be str')

        return self

    def choiceReward(self):
        '''依据权重选择相应的奖励'''
        return dizhu_util.getItemByWeight(self.rewards)

    def isBigReward(self, item):
        return item == self.rewards[-1]['item']


class Bait(object):
    '''
    鱼饵对象
    '''
    def __init__(self):
        self.id = None
        self.name = None
        self.pic = None
        self.chip = None
        self.fishList = None
        self.fish = None
        self.superFish = None
        self.couponFishRewards = None
        self.superFishRewards = None

    def toDict(self):
        return {
            'chip': self.chip,
            'name': self.name,
            'id': self.id,
            'pic': self.pic
        }

    def decodeFromDict(self, d):
        self.id = d.get('id')
        if not isinstance(self.id, int) or self.id < 0:
            raise TYBizConfException(d, 'Bait.id must be int and >0')
        self.name = d.get('name')
        if not isinstance(self.name, (str, unicode)):
            raise TYBizConfException(d, 'Bait.name must be str')
        self.pic = d.get('pic')
        if not isinstance(self.pic, (str, unicode)):
            raise TYBizConfException(d, 'Bait.pic must be str')
        self.chip = d.get('chip')
        if not isinstance(self.chip, int) or self.chip < 0:
            raise TYBizConfException(d, 'Bait.chip must be int and >0')
        self.fish = d.get('fish')
        if not isinstance(self.fish, list):
            raise TYBizConfException(d, 'Bait.id must be int')
        self.superFish = d.get('superFish', 0)
        if not isinstance(self.superFish, int):
            raise TYBizConfException(d, 'Bait.superFish must be int')
        self.couponFishRewards = d.get('couponFishRewards')
        if self.couponFishRewards and not isinstance(self.couponFishRewards, list):
            raise TYBizConfException(d, 'Bait.couponFishRewards must be list')
        tempCouponFishRewards = []
        for rewardDict in d.get('couponFishRewards', []):
            itemDict = rewardDict.get('item', {})
            if itemDict:
                tempCouponFishRewards.append({
                    'item': TYContentItem.decodeFromDict(itemDict),
                    'weight': rewardDict.get('weight')
                })
        self.couponFishRewards = tempCouponFishRewards

        self.superFishRewards = d.get('superFishRewards')
        if self.superFishRewards and not isinstance(self.superFishRewards, list):
            raise TYBizConfException(d, 'Bait.superFishRewards must be list')
        tempSuperFishRewards = []
        for rewardDict in d.get('superFishRewards', []):
            itemDict = rewardDict.get('item', {})
            if itemDict:
                tempSuperFishRewards.append({
                    'item': TYContentItem.decodeFromDict(itemDict),
                    'weight': rewardDict.get('weight')
                })
        self.superFishRewards = tempSuperFishRewards

        return self

    def initFishList(self, fishList):
        self.fishList = filter(lambda x: x.id in set([f['item'] for f in self.fish]), fishList)

    def choiceFish(self):
        fishId = dizhu_util.getItemByWeight(self.fish)
        return filter(lambda x: x.id == fishId, _fishingConf.fish)[0]


class FishingConf(object):
    '''
    钓鱼游戏配置
    '''
    def __init__(self):
        self.messageNumber = None
        self.baits = None
        self.fish = None
        self.messages = None
        self.userBaits = None
        self.coinPic = None
        self.couponPic = None
        self.mail = None
        self.tip = None

    def decodeFromDict(self, d):
        self.messageNumber = d.get('messageNumber')
        if not isinstance(self.messageNumber, int) or self.messageNumber < 0:
            raise TYBizConfException(d, 'FishingConf.messageNumber must be int and >0')

        self.messages = d.get('messages')
        if not isinstance(self.messages, list):
            raise TYBizConfException(d, 'FishingConf.messages must be list')

        fish = d.get('fish')
        if not isinstance(fish, list):
            raise TYBizConfException(d, 'FishingConf.fish must be list')
        self.fish = []
        for fishDict in fish:
            self.fish.append(Fish().decodeFromDict(fishDict))

        baits = d.get('baits')
        if not isinstance(baits, list):
            raise TYBizConfException(d, 'FishingConf.baits must be list')

        self.baits = []
        for baitDict in baits:
            bait = Bait().decodeFromDict(baitDict)
            bait.initFishList(self.fish)
            self.baits.append(bait)

        self.userBaits = d.get('userBaits')
        if not isinstance(self.messages, list):
            raise TYBizConfException(d, 'FishingConf.userBaits must be list')

        self.mail = d.get('mail')
        if not isinstance(self.mail, dict):
            raise TYBizConfException(d, 'FishingConf.mail must be dict')

        self.coinPic = d.get('coinPic', '')
        if not isinstance(self.coinPic, (str, unicode)):
            raise TYBizConfException(d, 'FishingConf.coinPic must be str')
        self.couponPic = d.get('couponPic', '')
        if not isinstance(self.couponPic, (str, unicode)):
            raise TYBizConfException(d, 'FishingConf.couponPic must be str')
        self.tip = d.get('tip', '')
        if not isinstance(self.tip, (str, unicode)):
            raise TYBizConfException(d, 'FishingConf.tip must be str')
        return self


class FishHelper(object):
    '''
    钓鱼游戏核心业务
    '''
    @classmethod
    def getUserBaits(cls, userId):
        userChip = userchip.getChip(userId)
        userBaits = _fishingConf.userBaits
        for userBait in userBaits:
            if (userBait['start'] < 0 or userChip >= userBait['start']) and (userBait['end'] < 0 or userChip <= userBait['end']):
                baitList = filter(lambda x: x.id in userBait['baits'], _fishingConf.baits)
                if ftlog.is_debug():
                    ftlog.debug('FishHelper.getUserBaits',
                                'userId=', userId,
                                'baitList=', [b.id for b in baitList])
                return baitList

    @classmethod
    def getBait(cls, baitId):
        for bait in _fishingConf.baits:
            if bait.id == baitId:
                return bait
        return

    @classmethod
    def getMessageByFishId(cls, fishId):
        messages = _fishingConf.messages
        for message in messages:
            if fishId in message['matchId']:
                return random.choice(message['matchDesc'])

    @classmethod
    def getSuperFishList(cls):
        return filter(lambda x: x.type == 'superChip', _fishingConf.fish)

    @classmethod
    def getCouponFishList(cls):
        return filter(lambda x: x.type == 'coupon', _fishingConf.fish)

    @classmethod
    def getFishingHistory(cls):
        historyList = daobase.executeRePlayCmd('lrange', buildRecordUniqueKey(), 0, - 1) or []
        ret = []
        for history in historyList:
            try:
                ret.append(json.loads(history))
            except:
                pass
        return ret

    @classmethod
    def getFishingInfo(cls, userId):
        # 获取鱼饵
        baits = cls.getUserBaits(userId)

        fishList = set()
        # 获取鱼饵普通鱼信息
        for bait in baits:
            for fish in bait.fishList:
                if fish.id == 0:
                    continue
                fishList.add(fish)

        fishDictList = [fish.toDict() for fish in fishList]

        # 珍珠鱼信息, 获取进度
        couponFish = cls.getCouponFishList()[0]
        couponFishDict = couponFish.toDict()
        couponFishDict['progress'] = loadUserFishingCount(userId, couponFish.id)
        fishDictList.append(couponFishDict)
        baitList = [bait.toDict() for bait in baits]
        return {
            'baits': baitList,
            'fish': fishDictList,
            'finalChip': userchip.getChip(userId),
            'tip': _fishingConf.tip,
            'finalCouponCount': userdata.getAttr(userId, 'coupon')
        }

    @classmethod
    def getFishReward(cls, userId, baitId):
        # 钓到没钓到标志
        rewardCount = 0
        record = ''
        fishPic = ''
        couponFishPic = ''
        exchangeDes = ''
        deltaChip = 0
        deltaCouponCount = 0

        # 检查用户Id， baitId 是否匹配, 获取 bait 消费金币
        userName = str(userdata.getAttrs(userId, ['name'])[0])
        bait = cls.getBait(baitId)
        consumeChip = bait.chip if bait else 0

        if not consumeChip or not cls.consumeExpenses(userId, TYContentItem.decodeFromDict({'itemId': 'user:chip', 'count': consumeChip})):
            ftlog.warn('FishHelper.getFishReward',
                       'userId=', userId,
                       'baitId=', baitId,
                       'userChip=', userchip.getChip(userId),
                       'consumeChip=', consumeChip)
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
                return

            buyType = ''
            orderShow = TodoTaskOrderShow.makeByProduct('金币不足', '', product, buyType)
            orderShow.setParam('sub_action_btn_text', '确定')
            mo = TodoTaskHelper.makeTodoTaskMsg(DIZHU_GAMEID, userId, orderShow)
            router.sendToUser(mo, userId)
            return


        # 随机获得珍珠, 存入数据库
        couponFish = cls.getCouponFishList()[0]
        # 判断鱼饵有没有奖券鱼的配置
        item = dizhu_util.getItemByWeight(bait.couponFishRewards) if bait.couponFishRewards else None
        couponCount = item.count if item else 0
        count = loadUserFishingCount(userId, couponFish.id)
        if couponCount:
            assetKind = hallitem.itemSystem.findAssetKind('user:coupon')
            couponCount = couponCount * 1.0 / assetKind.displayRate
            couponCount = int(couponCount) if couponCount.is_integer() else round(couponCount, 2)
            rewardCount += 1
            count += 1
            couponFishPic = couponFish.pic
            if count >= couponFish.needNum:
                count = 0
                # 发送奖券
                dictionary = {'zhenzhu_count': couponFish.needNum, 'coupon_count': couponCount}
                record = json.dumps(cls.getRealUserMail(cls.getMail(couponFish, True, False), dictionary))
                exchangeDes = json.dumps(cls.getRealUserMail(cls.getMail(couponFish, True, True), dictionary))
                dictionary2 = {'user_name': userName, 'zhenzhu_count': couponFish.needNum, 'coupon_count': couponCount}
                record2 = json.dumps(cls.getRealUserMail(cls.getMail(couponFish, False, True), dictionary2))
                saveUserFishingCount(userId, couponFish.id, count)
                UserBag.sendAssetsToUser(DIZHU_GAMEID, userId, {'itemId': item.assetKindId, 'count': item.count}, 'DDZ_FISHING_SYSTEM')
                deltaCouponCount = item.count
                cls.pushRecord(record2)
                if ftlog.is_debug():
                    ftlog.debug('FishHelper.getFishReward coupon exchangeDes',
                                'userId=', userId,
                                'fishId=', couponFish.id,
                                'exchangeDes=', exchangeDes)
            else:
                # 获得一个奖券鱼
                dictionary = {'zhenzhu_count': couponFish.needNum, 'coupon_count': couponCount}
                record = json.dumps(cls.getRealUserMail(cls.getMail(couponFish, True, False), dictionary))
                dictionary2 = {'user_name': userName, 'zhenzhu_count': couponFish.needNum, 'coupon_count': couponCount}
                record2 = json.dumps(cls.getRealUserMail(cls.getMail(couponFish, False, False), dictionary2))
                saveUserFishingCount(userId, couponFish.id, count)
                cls.pushRecord(record2)
                if ftlog.is_debug():
                    ftlog.debug('FishHelper.getFishReward coupon',
                                'userId=', userId,
                                'fishId=', couponFish.id,
                                'record=', record)

        # 随机获取金币奖励，对应bait下普通鱼
        userBaits = filter(lambda x: x.id == baitId, _fishingConf.baits)
        fish = userBaits[0].choiceFish()
        if fish.id:  # 钓到鱼了
            reward = fish.choiceReward()
            chip = reward.count
            if chip:
                rewardCount += 1
                bigFish = cls.getSuperFishList()[0]
                bigReward = dizhu_util.getItemByWeight(bait.superFishRewards) if bait.superFishRewards else None
                if bigReward and bigReward.count and fish.id == bait.fishList[-1].id:  # roll 大鱼的机会
                    fish = bigFish
                    chip = bigReward.count
                fishPic = fish.pic
                dictionary = {'random_message': cls.getMessageByFishId(fish.id), 'fish_name': fish.name, 'chip_count': chip}
                if rewardCount == 2:
                    record = json.dumps(cls.getRealUserMail(cls.getCombinationMail(), dictionary))
                else:
                    record = json.dumps(cls.getRealUserMail(cls.getMail(fish, True), dictionary))
                dictionary2 = {'user_name': userName, 'fish_name': fish.name, 'chip_count': chip, 'random_message': cls.getMessageByFishId(fish.id)}
                record2 = json.dumps(cls.getRealUserMail(cls.getMail(fish, False), dictionary2))
                UserBag.sendAssetsToUser(DIZHU_GAMEID, userId, {'itemId': 'user:chip', 'count': chip}, 'DDZ_FISHING_SYSTEM')
                cls.pushRecord(record2)
                deltaChip = chip

                if ftlog.is_debug():
                    ftlog.debug('FishHelper.getFishReward',
                                'userId=', userId,
                                'fishId=', fish.id,
                                'record=', record)
        return {
            'rewardCount': rewardCount,
            'desc':  json.loads(record) if rewardCount and record else cls.getailureMail(),
            'couponFishPic': couponFishPic,
            'fishPic': fishPic,
            'exchangeDes': json.loads(exchangeDes) if exchangeDes else '',
            'finalCouponCount': userdata.getAttr(userId, 'coupon'),
            'finalChip': userchip.getChip(userId),
            'couponFishCount': count,
            'deltaChip': deltaChip,
            'deltaCouponCount': deltaCouponCount
        }

    @classmethod
    def consumeExpenses(cls, userId, item):
        '''
        消耗抽奖花费
        '''
        expensesItemId = item.assetKindId
        expensesItemCount = item.count
        ftlog.info('FishHelper.consumeExpenses',
                   'userId=', userId,
                   'itemId=', expensesItemId,
                   'count=', expensesItemCount)
        return UserBag.consumeAssetsIfEnough(userId, expensesItemId, expensesItemCount, 'DDZ_FISHING_SYSTEM')

    @classmethod
    def pushRecord(cls, record):
        '''
        增加一条抽奖记录
        '''
        daobase.executeRePlayCmd('lpush', buildRecordUniqueKey(), record)
        length = daobase.executeRePlayCmd('llen', buildRecordUniqueKey())
        if length > _fishingConf.messageNumber:
            daobase.executeRePlayCmd('ltrim', buildRecordUniqueKey(), 0, _fishingConf.messageNumber - 1)

    @classmethod
    def getMail(cls, fish, isSelf=True, exchange=False):
        '''
        获取发送消息格式
        '''
        if fish.type == 'chip':
            if isSelf:
                return _fishingConf.mail['fish']['me']
            else:
                return _fishingConf.mail['fish']['others']
        elif fish.type == 'superChip':
            if isSelf:
                return _fishingConf.mail['superFish']['me']
            else:
                return _fishingConf.mail['superFish']['others']
        else:
            if isSelf:
                if exchange:
                    return _fishingConf.mail['coupon']['me']
                else:
                    return _fishingConf.mail['couponFish']['me']
            else:
                if exchange:
                    return _fishingConf.mail['coupon']['others']
                else:
                    return _fishingConf.mail['couponFish']['others']

    @classmethod
    def getRealUserMail(cls, mailList, paramsDict):
        '''
        替换配置中的邮箱
        '''
        mailList = copy.deepcopy(mailList)
        for text in mailList:
            text['text'] = strutil.replaceParams(text['text'], paramsDict)
        return mailList

    @classmethod
    def getCombinationMail(cls):
        return _fishingConf.mail['combination']

    @classmethod
    def getailureMail(cls):
        return _fishingConf.mail['failure']

# 配置初始化以及配置更新
_fishingConf = None
_inited = False

def _reloadConf():
    global _fishingConf
    d = configure.getGameJson(DIZHU_GAMEID, 'match.fishing', {}, 0)
    conf = FishingConf().decodeFromDict(d)
    _fishingConf = conf
    ftlog.info('dizhufishing._reloadConf successed')

def _onConfChanged(event):
    if _inited and event.isChanged('game:6:match.fishing:0'):
        ftlog.debug('dizhufishing._onConfChanged')
        _reloadConf()

def _initialize():
    ftlog.debug('dizhufishing._initialize begin')
    global _inited
    if not _inited:
        _inited = True
        _reloadConf()
        pkeventbus.globalEventBus.subscribe(EventConfigure, _onConfChanged)
    ftlog.debug('dizhufishing._initialize end')

