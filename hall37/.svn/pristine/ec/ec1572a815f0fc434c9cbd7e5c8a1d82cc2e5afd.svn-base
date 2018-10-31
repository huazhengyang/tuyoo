# -*- coding=utf-8 -*-
"""
@file  : activity_item_exchange
@date  : 2016-12-20
@author: GongXiaobo
"""
import copy

import freetime.util.log as ftlog
from hall.entity import datachangenotify
from hall.entity import hallitem
from hall.entity import hallpopwnd
from hall.entity.hallactivity.activity import ACTIVITY_KEY
from hall.entity.hallactivity.activity_type import TYActivityType
from hall.entity.hallconf import HALL_GAMEID
from poker.entity.biz.activity.activity import TYActivity
from poker.entity.biz.content import TYContentRegister, TYContentItem
from poker.entity.biz.exceptions import TYBizConfException
from poker.entity.biz.item.item import TYAssetUtils
from poker.entity.dao import daobase
from poker.util import timestamp


class TYActItemExchange(TYActivity):
    TYPE_ID = TYActivityType.ACTIVITY_ITEM_EXCHANGE
    FIELD_EXCHANGE_NUM = 'exchange:{}:num'
    FIELD_EXCHANGE_TIME = 'exchange:{}:time'

    def __init__(self, dao, clientConfig, serverConfig):
        super(TYActItemExchange, self).__init__(dao, clientConfig, serverConfig)
        self._initial()

    def reload(self, config):
        super(TYActItemExchange, self).reload(config)
        self._initial()

    def _initial(self):
        _exchanges = {}
        for info in self._clientConf['config']['exchange']:
            info2 = copy.copy(info)
            info2['content'] = TYContentRegister.decodeFromDict(info['content'])
            costs = []
            for costdict in info2['costs']:
                costs.append(TYContentItem.decodeFromDict(costdict))
            if not costs:
                raise TYBizConfException(info, 'costs is empty!!!')
            info2['costs'] = costs
            _exchanges[info2['id']] = info2

            # 原始配置填充图片信息
            content_items = info2['content'].getItems()
            assetKind = hallitem.itemSystem.findAssetKind(content_items[0].assetKindId)
            info['pic'] = assetKind.pic
        # 原始配置,还需要一个消耗物品的图片
        for info in _exchanges.itervalues():
            for cost in info['costs']:
                self.costAssetKindId = cost.assetKindId
                assetKind = hallitem.itemSystem.findAssetKind(cost.assetKindId)
                self._clientConf['config']['costAssetPic'] = assetKind.pic
                break
        self._exchanges = _exchanges

    def getConfigForClient(self, gameId, userId, clientId):
        conf = copy.deepcopy(self._clientConf)
        button = conf["config"]["button"]
        if button["visible"]:
            todoTaskDict = button["todoTask"]
            if todoTaskDict:
                todoTaskObj = hallpopwnd.decodeTodotaskFactoryByDict(todoTaskDict).newTodoTask(gameId, userId, clientId)
                button["todoTask"] = todoTaskObj.toDict()
        else:
            del conf["config"]["button"]
        return conf

    @staticmethod
    def check_reset(resettype, userid, actkey, data_field, time_field):
        oldtime = daobase.executeUserCmd(userid, 'HGET', actkey, time_field)
        curtime = timestamp.getCurrentTimestamp()
        if not oldtime or (resettype == 'day' and not timestamp.is_same_day(oldtime, curtime)):
            daobase.executeUserCmd(userid, 'HMSET', actkey, time_field, curtime, data_field, 0)
            return 0
        return daobase.executeUserCmd(userid, 'HGET', actkey, data_field)

    def get_exchange_buynum(self, userid, actkey, exchange):
        return self.check_reset(exchange['limitReset'], userid, actkey, self.FIELD_EXCHANGE_NUM.format(exchange['id']),
                                self.FIELD_EXCHANGE_TIME.format(exchange['id']))

    def handleRequest(self, msg):
        userid = msg.getParam('userId')
        gameid = msg.getParam('gameId')
        action = msg.getParam("action")
        actkey = ACTIVITY_KEY.format(HALL_GAMEID, userid, self.getid())
        if action == "credit_query":
            return self._query(userid, actkey)
        if action == "credit_exchange":
            exchangeid = msg.getParam('productId')
            return self._exchange(gameid, userid, actkey, exchangeid)
        return {'result': 'fail', 'tip': "unknown action"}

    def _query(self, userid, actkey):
        products = {}
        for iid, info in self._exchanges.iteritems():
            products[iid] = self.get_exchange_buynum(userid, actkey, info)
        return {'products': products,
                'credit': hallitem.itemSystem.loadUserAssets(userid).balance(HALL_GAMEID, self.costAssetKindId,
                                                                             timestamp.getCurrentTimestamp())}

    def _exchange(self, gameid, userid, actkey, exchangeid):
        info = self._exchanges.get(exchangeid)
        if not info:
            return {'result': 'fail', 'tip': "unknown productId"}

        buynum = self.get_exchange_buynum(userid, actkey, info)
        if buynum >= info['limitTimes']:
            return {'result': 'fail', 'tip': '兑换次数已满'}

        curtime = timestamp.getCurrentTimestamp()
        userAssets = hallitem.itemSystem.loadUserAssets(userid)
        try:
            userAssets.consumeContentItemList(gameid, info['costs'], False, curtime,
                                              "ACT_ITEM_EXCHANGE_COST", exchangeid)
        except:
            return {'result': 'fail', 'tip': '您的道具不足，快去获取道具吧'}

        daobase.executeUserCmd(userid, 'HINCRBY', actkey, self.FIELD_EXCHANGE_NUM.format(exchangeid), 1)
        assetList = userAssets.sendContent(gameid, info['content'], 1, True,
                                           timestamp.getCurrentTimestamp(), "ACT_ITEM_EXCHANGE_GAIN", exchangeid)
        response = self._query(userid, actkey)
        ftlog.info('TYActItemExchange._exchange gameId=', gameid,
                   'userId=', userid,
                   'activityId=', self.getid(),
                   'reward=', TYAssetUtils.buildContents(assetList),
                   'buynum=', buynum + 1,
                   'credit=', response['credit'])
        changeNames = TYAssetUtils.getChangeDataNames(assetList)
        datachangenotify.sendDataChangeNotify(gameid, userid, changeNames)
        response['result'] = 'ok'
        response['tip'] = '兑换成功，您获得' + TYAssetUtils.buildContentsString(assetList)
        return response


if __name__ == '__main__':
    pass
