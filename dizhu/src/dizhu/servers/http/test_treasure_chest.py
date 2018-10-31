# -*- coding=utf-8 -*-
'''
Created on 2018年8月14日

@author: wangyonghui
'''
from dizhu.entity.dizhuconf import DIZHU_GAMEID
from dizhu.entity.treasure_chest.treasure_chest import TreasureChestHelper, TREASURE_CHEST_TYPE_AS_WINSTREAK
from freetime.entity.msg import MsgPack
from hall.servers.common.base_http_checker import BaseHttpMsgChecker
from poker.protocol import runhttp
from poker.protocol.decorator import markHttpHandler, markHttpMethod
from poker.util import strutil
from dizhu.servers.util.rpc import event_remote as dizhu_event_remote


@markHttpHandler
class TestDiZhuTreasureChestHttpHandler(BaseHttpMsgChecker):
    def __init__(self):
        pass

    def _check_param_rewardList(self, key, params):
        try:
            jstr = runhttp.getParamStr(key)
            rewardList = strutil.loads(jstr)
            return None, rewardList
        except:
            return 'the jsonstr params is not a list Format !!', None

    def _check_param_rewardId(self, key, params):
        rewardId = runhttp.getParamStr(key)
        return None, rewardId

    def _check_param_rewardType(self, key, params):
        rewardType = runhttp.getParamStr(key)
        return None, rewardType

    def _check_param_helpUserId(self, key, params):
        helpUserId = runhttp.getParamInt(key)
        if isinstance(helpUserId, int):
            return None, helpUserId
        return 'ERROR of helpUserId !' + str(helpUserId), None

    def _check_param_params(self, key, params):
        try:
            jstr = runhttp.getParamStr(key)
            params = strutil.loads(jstr)
            return None, params
        except:
            return 'the jsonstr params is not a list Format !!', None

    @markHttpMethod(httppath='/gtest/dizhu/treasure/chest/list')
    def doGetTreasureChestList(self, userId):
        mo = MsgPack()
        mo.setCmd('dizhu')
        mo.setResult('action', 'treasure_chest_list')
        mo.setResult('gameId', DIZHU_GAMEID)
        mo.setResult('userId', userId)
        mo.setResult('treasureChestList', TreasureChestHelper.getTreasureChestList(userId))
        return mo.pack()

    @markHttpMethod(httppath='/gtest/dizhu/treasure/chest/unlock')
    def doTreasureChestUnlock(self, userId, rewardId):
        mo = MsgPack()
        mo.setCmd('dizhu')
        mo.setResult('action', 'treasure_chest_unlock')
        mo.setResult('gameId', DIZHU_GAMEID)
        mo.setResult('userId', userId)
        mo.setResult('success', TreasureChestHelper.unlockTreasureChest(userId, rewardId))
        return mo.pack()

    @markHttpMethod(httppath='/gtest/dizhu/treasure/chest/open')
    def doTreasureChestOpen(self, userId, rewardId):
        mo = MsgPack()
        mo.setCmd('dizhu')
        mo.setResult('action', 'treasure_chest_open')
        mo.setResult('gameId', DIZHU_GAMEID)
        mo.setResult('userId', userId)
        ret, _ = TreasureChestHelper.openTreasureChest(userId, rewardId)
        mo.setResult('success', ret)
        return mo.pack()

    @markHttpMethod(httppath='/gtest/dizhu/treasure/chest/video')
    def doTreasureChestVideo(self, userId, rewardId):
        mo = MsgPack()
        mo.setCmd('dizhu')
        mo.setResult('action', 'treasure_chest_video')
        mo.setResult('gameId', DIZHU_GAMEID)
        mo.setResult('userId', userId)
        ret, state, leftSeconds = TreasureChestHelper.videoShortenTreasureChest(userId, rewardId)
        mo.setResult('success', ret)
        mo.setResult('state', state)
        mo.setResult('leftSeconds', leftSeconds)
        return mo.pack()

    @markHttpMethod(httppath='/gtest/dizhu/treasure/chest/help')
    def doTreasureChestHelp(self, userId, rewardId, helpUserId):
        mo = MsgPack()
        mo.setCmd('dizhu')
        mo.setResult('action', 'treasure_chest_help')
        mo.setResult('gameId', DIZHU_GAMEID)
        mo.setResult('userId', userId)
        ret, state, leftSeconds = TreasureChestHelper.helpShortenTreasureChest(userId, rewardId, helpUserId)
        mo.setResult('success', ret)
        mo.setResult('state', state)
        mo.setResult('leftSeconds', leftSeconds)
        return mo.pack()

    @markHttpMethod(httppath='/gtest/dizhu/treasure/chest/add')
    def doTreasureChestAdd(self, userId, rewardType, rewardList, params):
        success = False
        if rewardType in [TREASURE_CHEST_TYPE_AS_WINSTREAK]:
            success = True
            dizhu_event_remote.publishTreasureChestEvent(DIZHU_GAMEID,
                                                         userId,
                                                         rewardType,
                                                         rewardList,
                                                         **params)
        mo = MsgPack()
        mo.setCmd('dizhu')
        mo.setResult('action', 'treasure_chest_add')
        mo.setResult('gameId', DIZHU_GAMEID)
        mo.setResult('userId', userId)
        mo.setResult('rewardList', rewardList)
        mo.setResult('success', success)
        return mo.pack()
