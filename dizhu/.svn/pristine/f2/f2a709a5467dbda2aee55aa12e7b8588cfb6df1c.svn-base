# -*- coding:utf-8 -*-
"""
Created on 2017年12月12日

@author: wangjifa
"""
import random
from datetime import time, datetime
from sre_compile import isstring

from dizhu.activitynew.activity import ActivityNew
from dizhu.entity import dizhu_util
from dizhu.entity.dizhuconf import DIZHU_GAMEID
from dizhucomm.entity.events import UserTableWinloseEvent
from hall.entity import hallitem, hallshare, hallvip
from hall.entity.hallconf import HALL_GAMEID
from hall.entity.todotask import TodoTaskEnterGame, TodoTaskShowRewards, TodoTaskHelper, TodoTaskShowInfo
from poker.entity.biz.activity.activity import TYActivity
from poker.entity.biz.content import TYContentItem
from poker.entity.configure import gdata, pokerconf, configure
from poker.util import timestamp as pktimestamp
from poker.entity.dao import daobase
from poker.entity.biz.exceptions import TYBizConfException
import freetime.util.log as ftlog


class ActivityChristmas(ActivityNew):
    TYPE_ID = 'act_ddz_christmas'
    zeroTime = time()

    def __init__(self):
        super(ActivityChristmas, self).__init__()
        self._open = 0
        self._dayOpenTime = self.zeroTime
        self._dayCloseTime = self.zeroTime
        self._collectItemList = None
        self._tips = None
        self._rewards = None
        self._roomList = None

    def init(self):
        from dizhu.game import TGDizhu
        TGDizhu.getEventBus().subscribe(UserTableWinloseEvent, self._onGameRoundFinish)

    def cleanup(self):
        from dizhu.game import TGDizhu
        TGDizhu.getEventBus().unsubscribe(UserTableWinloseEvent, self._onGameRoundFinish)

    def _decodeFromDictImpl(self, d):
        self._open = d.get('open')
        if not isinstance(self._open, int):
            raise TYBizConfException(d, 'ActivityChristmas.open must be int')

        self._mail = d.get('mail')
        if self._mail and not isstring(self._mail):
            raise TYBizConfException(d, 'ActivityChristmas.mail must be string')

        self._collectItemList = d.get('collectItems')
        if not isinstance(self._collectItemList, dict):
            raise TYBizConfException(d, 'ActivityChristmas.collectItems must be dict')

        self._tips = d.get('tips')
        if self._tips and not isstring(self._tips):
            raise TYBizConfException(d, 'ActivityChristmas.tips must be string')

        self._rewards = d.get('rewards')
        if not isinstance(self._rewards, list):
            raise TYBizConfException(d, 'ActivityChristmas.rewards must be list')

        self._roomList = d.get('roomList')
        if not isinstance(self._roomList, list):
            raise TYBizConfException(d, 'ActivityChristmas.roomList must be list')

        timeStr = d.get('dayOpenTime')
        if timeStr:
            try:
                self._dayOpenTime = datetime.strptime(timeStr, '%H:%M').time()
            except:
                raise TYBizConfException(d, 'ActivityChristmas.dayOpenTime must be time str')

        timeStr = d.get('dayCloseTime')
        if timeStr:
            try:
                self._dayCloseTime = datetime.strptime(timeStr, '%H:%M').time()
            except:
                raise TYBizConfException(d, 'ActivityChristmas.dayCloseTime must be time str')

        if ftlog.is_debug():
            ftlog.debug('ActivityChristmas inited. typeId=', self.TYPE_ID,
                        'rewards=', self._rewards,
                        'open=', self._open,
                        'time=', self._dayOpenTime, self._dayCloseTime,
                        'active=', self.checkActivityActive())

        return self

    @property
    def tips(self):
        return self._tips

    def isOutOfTime(self, timestamp=None):
        timestamp = pktimestamp.getCurrentTimestamp() if not timestamp else timestamp
        t = datetime.fromtimestamp(timestamp).time()
        return (self._dayOpenTime != self.zeroTime and t < self._dayOpenTime) or (
        self._dayCloseTime != self.zeroTime and t >= self._dayCloseTime)

    def checkActivityActive(self):
        timestamp = pktimestamp.getCurrentTimestamp()
        if self.isOutOfTime(timestamp):
            return False
        if self.checkTime(timestamp):
            return False
        return True

    def getUserRewardByVip(self, userId):
        userVip = hallvip.userVipSystem.getUserVip(userId)
        level = userVip.vipLevel.level
        for rewardInfo in self._rewards:
            minVip = rewardInfo.get('minVip', 0)
            maxVip = rewardInfo.get('maxVip', 0)
            if minVip <= level <= maxVip:
                return rewardInfo.get('reward', [])
        return None

    def getUserCollectList(self, userId):
        userAssets = hallitem.itemSystem.loadUserAssets(userId)
        ret = []
        for socks in self._collectItemList:
            itemConf = self._collectItemList[socks]
            itemId = itemConf.get('itemId')
            itemCount = itemConf.get('count')
            balance = userAssets.balance(HALL_GAMEID, itemId, pktimestamp.getCurrentTimestamp())
            todotask = itemConf.get('todotask')
            todotaskDict = None
            if todotask.get('shareId'):
                # 分享的todotask
                clientIdList = [20232, 20293, 20329, 20338, 20340, 20354, 20689, 20729, 21306, 21317, 21360, 21368,
                    21377, 21736, 20195, 20259, 20294, 20331, 20685, 20698, 21330, 21355, 21361, 21419, 20264, 20265,
                    20267, 20268, 20272, 20287, 20288, 20289, 20348, 20349, 20350, 20351, 20488, 20489, 20490, 20699,
                    20701, 20702, 20788, 20790, 20791, 21040, 21328, 21331, 21333, 21334, 21350, 21352, 21353, 21791,
                    21792, 21793, 21794, 22043]
                from poker.entity.dao import sessiondata
                _, intClientId = sessiondata.getClientIdNum(userId)
                if intClientId in clientIdList:
                    # 无法分享的包，弹出提示todotask
                    msg = u"今日登录已获得友谊之袜×1 明天再来吧~"
                    dialog_task = TodoTaskShowInfo(msg, True)
                    # TodoTaskHelper.sendTodoTask(DIZHU_GAMEID, userId, [dialog_task])
                    todotaskDict = dialog_task.toDict() if dialog_task else None
                else:
                    shareId = todotask.get('shareId')
                    share = hallshare.findShare(shareId)
                    todotask = share.buildTodotask(DIZHU_GAMEID, userId, 'diploma_share')
                    todotaskDict = todotask.toDict() if todotask else None
                if not todotaskDict:
                    ftlog.warn('christmas sharePointId not Found. userId=', userId)
                if ftlog.is_debug():
                    ftlog.debug('christmas.shareTodotask. userId=', userId, 'todotaskDict=', todotaskDict)

            elif todotask.get('sessionIndex'):
                # 生成快开的todotask
                jumpTodoTask = TodoTaskEnterGame("enter_game", "")
                enterParam = dict()
                enterParam["type"] = "quickstart"
                enterParam["pluginParams"] = {}
                enterParam["pluginParams"]["gameType"] = 1
                enterParam["pluginParams"]["sessionIndex"] = int(todotask.get('sessionIndex'))    #0-经典 1-欢乐 2-癞子 3-二人
                jumpTodoTask.setParam('gameId', DIZHU_GAMEID)
                jumpTodoTask.setParam('type', "quickstart")
                jumpTodoTask.setParam('enter_param', enterParam)
                if not jumpTodoTask:
                    ftlog.warn('christmas TodoTaskQuickStart not Found. userId=', userId)
                else:
                    todotaskDict = jumpTodoTask.toDict()

            elif todotask.get('matchIndex'):
                # 跳转比赛列表的todotask
                jumpTodoTask = TodoTaskEnterGame("enter_game", "")
                enterParam = dict()
                enterParam["type"] = "roomlist"
                enterParam["pluginParams"] = {}
                enterParam["pluginParams"]["gameType"] = 3
                enterParam["pluginParams"]["matchIndex"] = int(todotask.get('matchIndex'))    #0-比赛第一页 1-比赛第二页 2-比赛第三页
                jumpTodoTask.setParam('gameId', DIZHU_GAMEID)
                jumpTodoTask.setParam('type', "roomlist")
                jumpTodoTask.setParam('enter_param', enterParam)
                if not jumpTodoTask:
                    ftlog.warn('christmas TodoTaskEnterGame not Found. userId=', userId)
                else:
                    todotaskDict = jumpTodoTask.toDict()
            ret.append([itemId, balance, itemCount, todotaskDict])

        if ftlog.is_debug():
            ftlog.debug('christmas.getUserCollectList userId=', userId,
                        'collectList=', ret)
        return ret

    def exchange(self, userId):
        if not self.checkActivityActive():
            if ftlog.is_debug():
                ftlog.debug('christmas.exchange.checkActive.failed. userId=', userId)
            return u"不在活动时间内"

        assetList = None

        collectList = self.getUserCollectList(userId)
        timestamp = pktimestamp.getCurrentTimestamp()
        userAssets = hallitem.itemSystem.loadUserAssets(userId)

        collectCountList = []
        for items in collectList:
            if items[1] and items[2]:
                collectCountList.append(int(items[1] / items[2]))
            else:
                collectCountList.append(0)
        collectCount = min(collectCountList)
        if collectCount:
            for item in collectList:
                itemId = item[0]
                consumeSockCount = item[2] * collectCount
                _, consumeCount, final = userAssets.consumeAsset(DIZHU_GAMEID,
                                                                 itemId,
                                                                 consumeSockCount,
                                                                 timestamp,
                                                                 'DIZHU_ACT_CHRISTMAS_EXCHANGE',
                                                                 0)
                if ftlog.is_debug():
                    ftlog.debug('christmas.exchange.warning userId=', userId,
                                'consumeCount=', consumeCount,
                                'collectCount=', collectCount,
                                'finalCount=', final,
                                'collectList=', collectList)

            collectTimes = daobase.executeUserCmd(userId, 'HINCRBY', 'act:christmas:6:' + str(userId), 'reward', collectCount)

            # 根据VIP等级发奖励
            userRewards = self.getUserRewardByVip(userId)
            if not userRewards:
                ftlog.warn('christmas.exchange.warning.rewardError',
                           'userId=', userId, 'reward=', userRewards)
                return u""

            if ftlog.is_debug():
                ftlog.debug('christmas.exchange',
                            'userId=', userId,
                            'userRewards=', userRewards,
                            'userRewardsId=', id(userRewards))

            contentItems = []
            for rewardItem in userRewards:
                contentItems.append(TYContentItem(rewardItem['itemId'], int(rewardItem['count'] * collectCount)))

            assetList = dizhu_util.sendRewardItems(userId, contentItems, self._mail, 'DIZHU_ACT_CHRISTMAS_REWARD', 0)

            ftlog.info('gainChristmasFinalReward userId=', userId,
                       'collectTimes=', collectTimes,
                       'rewards=', [(atp[0].kindId, atp[1]) for atp in assetList])
        if ftlog.is_debug():
            ftlog.debug('christmas.exchange.info userId=', userId,
                        'collectCount=', collectCount,
                        'collectList=', collectList,
                        'assetList=', [(atp[0].kindId, atp[1]) for atp in assetList] if assetList else None)
        return u""

    def getRewardCountInBag(self, userId, timestamp=None):
        timestamp = timestamp if timestamp else pktimestamp.getCurrentTimestamp()
        userAssets = hallitem.itemSystem.loadUserAssets(userId)
        userRewards = self.getUserRewardByVip(userId)
        if not userRewards:
            return 0
        itemId = userRewards[0].get('itemId')
        return userAssets.balance(HALL_GAMEID, itemId, timestamp)

    @classmethod
    def getCollectTimes(cls, userId):
        return daobase.executeUserCmd(userId, 'HGET', 'act:christmas:6:' + str(userId), 'reward')

    def _onGameRoundFinish(self, event):
        if not self.checkActivityActive():
            return

        bigRoomId = event.mixConfRoomId or gdata.getBigRoomId(event.roomId)
        dropRate = 0
        itemId = ''
        for roomConf in self._roomList:
            if bigRoomId in roomConf.get('roomId', []):
                dropRate = roomConf.get('dropRate', 0)
                itemId = roomConf.get('itemId')
                break

        if random.randint(0, 100) <= (dropRate *100) and itemId:
            contentItems = TYContentItem.decodeList([{'itemId': itemId, 'count': 1}])
            assetList = dizhu_util.sendRewardItems(event.userId, contentItems, self._mail, 'DIZHU_ACT_CHRISTMAS_ITEM', 0)

            # 发奖弹窗
            rewardsList = []
            for assetItemTuple in assetList:
                assetItem = assetItemTuple[0]
                reward = dict()
                reward['name'] = assetItem.displayName
                reward['pic'] = assetItem.pic
                reward['count'] = assetItemTuple[1]
                rewardsList.append(reward)

            reward_task = TodoTaskShowRewards(rewardsList)
            TodoTaskHelper.sendTodoTask(DIZHU_GAMEID, event.userId, reward_task)

            ftlog.info('gainChristmasFinalReward userId=', event.userId,
                       'items=', [(atp[0].kindId, atp[1]) for atp in assetList])

        if ftlog.is_debug():
            ftlog.debug('act.christmas._onGameRoundFinish userId=', event.userId,
                        'bigRoomId=', bigRoomId,
                        'winLose=', event.winlose.isWin,
                        'dropRate=', dropRate,
                        'itemId=', itemId)


class ActivityChristmasHandler(TYActivity):
    TYPE_ID = 'act_ddz_christmas'
    ACTION_GET_COLLECTED = 'getCollectList'
    ACTION_EXCHANGE = 'exchange'

    def __init__(self, dao, clientConfig, serverConfig):
        super(self.__class__, self).__init__(dao, clientConfig, serverConfig)
        if ftlog.is_debug():
            ftlog.debug('ActivityChristmasHandler.__init__',
                        'clientConfig=', clientConfig,
                        'serverConfig=', serverConfig)

    def getActId(self):
        conf = configure.getGameJson(6, 'activity.new', {})
        for actConf in conf.get('activities', []):
            if actConf.get('typeId', '') == self.TYPE_ID:
                return actConf.get('actId')
        return None

    def handleRequest(self, msg):
        userId = msg.getParam('userId')
        action = msg.getParam("action")
        clientId = msg.getParam('clientId')

        intClientId = pokerconf.clientIdToNumber(clientId)
        actId = self.getActId()

        if ftlog.is_debug():
            ftlog.debug('ActivityChristmasHandler.handleRequest',
                        'userId=', userId,
                        'action=', action,
                        'clientId=', clientId,
                        'intClientId=', intClientId,
                        'actId=', actId,
                        'msg=', msg)
        if not actId:
            ftlog.warn()
            return {'code': -1, 'info': 'please ensure act_ddz_christmas activity in [game/6/activity.new/0.json]'}

        from dizhu.activitynew import activitysystemnew
        actChristmas = activitysystemnew.findActivity(actId)
        if actChristmas:
            errInfo = u""
            if self.ACTION_EXCHANGE == action:
                errInfo = actChristmas.exchange(userId)

            collectList = actChristmas.getUserCollectList(userId)
            socks = []
            for collectItem in collectList:
                # [itemId, balance, itemCount, todotask]
                total = collectItem[1]
                done = collectItem[2]
                todotask = collectItem[3]
                d = {'total': total, 'done': done, 'todotask': todotask}
                socks.append(d)

            collectTimes = actChristmas.getCollectTimes(userId)
            rewardsInBag = actChristmas.getRewardCountInBag(userId)
            retInfo = {
                "errInfo": errInfo,
                "action": action,
                "isExchanged": collectTimes,
                "isInBag" : rewardsInBag,
                "socks" : socks,
                "tip" : actChristmas.tips
            }
            if ftlog.is_debug():
                ftlog.debug('ActivityChristmasHandler.handleRequest userId=', userId,
                            'retInfo=', retInfo)
            return retInfo

        return {'code': -1, 'info': 'dizhu.ActivityChristmasHandler not inited'}


