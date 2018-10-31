# -*- coding:utf-8 -*-
"""
Created on 2017年12月21日

@author: wangjifa
"""
import random

from dizhu.entity import dizhu_util
from dizhu.entity.dizhuconf import DIZHU_GAMEID
from dizhu.game import TGDizhu
from dizhucomm.entity.events import UserTableWinloseEvent
from hall.entity import hallitem, hallshare
from hall.entity.hallconf import HALL_GAMEID
from hall.entity.todotask import TodoTaskEnterGame, TodoTaskShowInfo
from poker.entity.biz.content import TYContentItem
from poker.entity.configure import gdata
from poker.util import timestamp as pktimestamp
import freetime.util.log as ftlog
from dizhu.activitynew.christmas import ActivityChristmas

def _onGameRoundFinish(self, event):
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
        from hall.entity.todotask import TodoTaskShowRewards, TodoTaskHelper
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

        ftlog.info('gainChristmasFinalReward.todotask userId=', event.userId, 'items=',
                   [(atp[0].kindId, atp[1]) for atp in assetList])

    if ftlog.is_debug():
        ftlog.debug('act.christmas._onGameRoundFinish.todotask userId=', event.userId, 'bigRoomId=', bigRoomId, 'winLose=',
                    event.winlose.isWin, 'dropRate=', dropRate, 'itemId=', itemId)


ActivityChristmas._onGameRoundFinish = _onGameRoundFinish

from dizhu.activitynew import activitysystemnew
actChristmas = activitysystemnew.findActivity('act171213')
if not actChristmas:
    ftlog.warn('act.christmas.hotfix.error actChristmas not exist')

#actChristmas.cleanup()

from dizhu.activitynew.christmas import ActivityChristmas
eventBus = TGDizhu.getEventBus()
handlers = eventBus._handlersMap.get(UserTableWinloseEvent)
for h in handlers:
    ftlog.info('UserTableWinloseEvent Listener __module__=', h.__module__)
    if h.__module__ == 'dizhu.activitynew.christmas':
        handlers.remove(h)
        ftlog.info('dizhu.activities.christmas removed. 20171221')
        break

actChristmas.init()




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
            clientIdList = [
                20232, 20293, 20329, 20338, 20340, 20354, 20689, 20729, 21306, 21317, 21360, 21368, 21377,
                21736, 20195, 20259, 20294, 20331, 20685, 20698, 21330, 21355, 21361, 21419, 20264, 20265, 20267, 20268,
                20272, 20287, 20288, 20289, 20348, 20349, 20350, 20351, 20488, 20489, 20490, 20699, 20701, 20702, 20788,
                20790, 20791, 21040, 21328, 21331, 21333, 21334, 21350, 21352, 21353, 21791, 21792, 21793, 21794, 22043
            ]
            from poker.entity.dao import sessiondata
            _, intClientId = sessiondata.getClientIdNum(userId)
            if intClientId in clientIdList:
                # 无法分享的包，弹出提示todotask
                msg = u"今日登录已获得友谊之袜×1 明天再来吧~"
                dialog_task = TodoTaskShowInfo(msg, True)
                #TodoTaskHelper.sendTodoTask(DIZHU_GAMEID, userId, [dialog_task])
                todotaskDict = dialog_task.toDict() if dialog_task else None
            else:
                shareId = todotask.get('shareId')
                share = hallshare.findShare(shareId)
                todotask = share.buildTodotask(DIZHU_GAMEID, userId, 'diploma_share')
                todotaskDict = todotask.toDict() if todotask else None
            if not todotaskDict:
                ftlog.warn('christmas sharePointId not Found. userId=', userId)
            if ftlog.is_debug():
                ftlog.debug('christmas.shareTodotask. userId=', userId,
                            'todotaskDict=', todotaskDict)

        elif todotask.get('sessionIndex'):
            # 生成快开的todotask
            jumpTodoTask = TodoTaskEnterGame("enter_game", "")
            enterParam = dict()
            enterParam["type"] = "quickstart"
            enterParam["pluginParams"] = {}
            enterParam["pluginParams"]["gameType"] = 1
            enterParam["pluginParams"]["sessionIndex"] = int(todotask.get('sessionIndex'))  # 0-经典 1-欢乐 2-癞子 3-二人
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
            enterParam["pluginParams"]["matchIndex"] = int(todotask.get('matchIndex'))  # 0-比赛第一页 1-比赛第二页 2-比赛第三页
            jumpTodoTask.setParam('gameId', DIZHU_GAMEID)
            jumpTodoTask.setParam('type', "roomlist")
            jumpTodoTask.setParam('enter_param', enterParam)
            if not jumpTodoTask:
                ftlog.warn('christmas TodoTaskEnterGame not Found. userId=', userId)
            else:
                todotaskDict = jumpTodoTask.toDict()
        ret.append([itemId, balance, itemCount, todotaskDict])

    if ftlog.is_debug():
        ftlog.debug('christmas.getUserCollectList userId=', userId, 'collectList=', ret)
    return ret

ActivityChristmas.getUserCollectList = getUserCollectList
ftlog.info('dizhu.activities.christmas over. 20171221')