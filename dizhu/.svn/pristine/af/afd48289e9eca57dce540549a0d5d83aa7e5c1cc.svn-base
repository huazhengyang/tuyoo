# -*- coding:utf-8 -*-
'''
Created on 2018-06-12

@author: wangyonghui
'''
import json
from dizhu.entity.dizhuconf import DIZHU_GAMEID
from dizhu.entity.segment.dao import segmentdata
from poker.entity.biz.content import TYContentItem
from poker.entity.configure import configure
from poker.util import timestamp as pktimestamp


def buildUserWatchAdDataKey():
    return 'watchAd'


def getUserWatchAdData(userId):
    dataStr = segmentdata.getSegmentAttr(userId, DIZHU_GAMEID, buildUserWatchAdDataKey())
    if dataStr:
        return UserWatchAdData(userId).fromDict(json.loads(dataStr))
    else:
        return UserWatchAdData(userId)


def saveUserWatchAdData(userId, data):
    dataStr = json.dumps(data.toDict())
    segmentdata.setSegmentAttr(userId, DIZHU_GAMEID, buildUserWatchAdDataKey(), dataStr)


class UserWatchAdData(object):
    def __init__(self, userId):
        self.userId = userId
        self.watchCount = 0  # 观看次数，也就是发奖次数
        self.timestamp = pktimestamp.getCurrentTimestamp()  #  时间戳

    def toDict(self):
        return {
            'watchCount': self.watchCount,
            'timestamp': self.timestamp
        }

    def fromDict(self, d):
        timestamp = d.get('timestamp', 0)
        if not pktimestamp.is_same_day(timestamp, pktimestamp.getCurrentTimestamp()):
            return self
        self.timestamp = timestamp
        self.watchCount = d.get('watchCount', 0)
        return self




class WatchAdHelper(object):
    @classmethod
    def getAdConf(cls):
        return configure.getGameJson(DIZHU_GAMEID, 'dizhu_ads', {})

    @classmethod
    def getDailyCountLimit(cls):
        return cls.getAdConf().get('dailyCount', 0)

    @classmethod
    def getUserLeftWatchAdCount(cls, userId):
        data = getUserWatchAdData(userId)
        return max(0, cls.getDailyCountLimit() - data.watchCount)

    @classmethod
    def getCDMinutes(cls):
        return cls.getAdConf().get('cdMinutes', 0)

    @classmethod
    def getAdRewardByWeight(cls, adId, count):
        conf = cls. getAdConf()
        adList = conf.get('adList', [])
        for ad in adList:
            if adId == ad.get('adId', None):
                rewardsByCountList = ad.get('rewardsByCount', [])
                for rewardsByCount in rewardsByCountList:
                    if count == rewardsByCount.get('count', None):
                        from dizhu.entity import dizhu_util
                        return dizhu_util.getItemByWeight(rewardsByCount.get('rewards', [])) if rewardsByCount.get('rewards', []) else None
        return None

    @classmethod
    def sendWatchAdRewards(cls, userId, adId):
        data = getUserWatchAdData(userId)
        if data.watchCount < cls.getDailyCountLimit():
            # 保存用户观看数据
            data.watchCount += 1
            saveUserWatchAdData(userId, data)
            # 发奖
            reward = cls.getAdRewardByWeight(adId, data.watchCount)
            if reward:
                contentItems = TYContentItem.decodeList([reward])
                from dizhu.entity import dizhu_util
                dizhu_util.sendRewardItems(userId, contentItems, None, 'DIZHU_WATCH_AD_REWARD', 0)
                return reward, cls.getDailyCountLimit() - data.watchCount
        return None, 0
