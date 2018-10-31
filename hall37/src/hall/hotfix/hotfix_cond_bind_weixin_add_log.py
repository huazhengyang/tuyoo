# -*- coding:utf-8 -*-
'''
Created on 2017年1月25日

@author: zhaojiangang
'''

import freetime.util.log as ftlog
from hall.entity.hallitem import TYItemActionConditionBindWeixin
from poker.entity.dao import userdata


def _conform(self, gameId, userAssets, item, timestamp, params):
    wxOpenId = userdata.getAttr(userAssets.userId, 'wxOpenId')
    ftlog.info('TYItemActionConditionBindWeixin._conform',
               'gameId=', gameId,
               'userId=', userAssets.userId,
               'itemId=', item.itemId,
               'itemKindId=', item.kindId,
               'wxOpenId=', wxOpenId,
               'ret=', False if not wxOpenId else True)
    return False if not wxOpenId else True

TYItemActionConditionBindWeixin._conform = _conform
