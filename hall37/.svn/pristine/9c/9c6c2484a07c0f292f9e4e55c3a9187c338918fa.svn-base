# -*- coding:utf-8 -*-
'''
Created on 2017年3月31日

@author: zhaojiangang
'''
from sre_compile import isstring

import freetime.util.log as ftlog
from hall.entity import hallstore
from hall.entity.hallusercond import UserCondition, UserConditionRegister
from poker.entity.biz.exceptions import TYBizConfException


def findProduct(gameId, userId, productId):
    product = hallstore.storeSystem.findProduct(productId)
    return product

hallstore.findProduct = findProduct

class UserConditionCanBuyProduct(UserCondition):
    TYPE_ID = 'user.cond.canBuyProduct'

    def __init__(self):
        super(UserConditionCanBuyProduct, self).__init__()
        self.productIds = None

    def check(self, gameId, userId, clientId, timestamp, **kwargs):
        try:
            for productId in self.productIds:
                product = hallstore.findProduct(gameId, userId, productId)
                if product and hallstore.storeSystem.canBuyProduct(gameId, userId, clientId, product, 1):
                    if ftlog.is_debug():
                        ftlog.debug('UserConditionCanBuyProduct.check',
                                    'gameId=', gameId,
                                    'userId=', userId,
                                    'clientId=', clientId,
                                    'timestamp=', timestamp,
                                    'productIds=', self.productIds,
                                    'ret=', True)
                    return True
            if ftlog.is_debug():
                ftlog.debug('UserConditionCanBuyProduct.check',
                            'gameId=', gameId,
                            'userId=', userId,
                            'clientId=', clientId,
                            'timestamp=', timestamp,
                            'productIds=', self.productIds,
                            'ret=', False)
            return False
        except:
            ftlog.error('UserConditionCanBuyProduct.check',
                        'gameId=', gameId,
                        'userId=', userId,
                        'clientId=', clientId,
                        'timestamp=', timestamp,
                        'productIds=', self.productIds)
            return False

    def decodeFromDict(self, d):
        productIds = d.get('productIds', [])
        if not productIds:
            raise TYBizConfException(d, 'UserConditionCanBuyProduct.productIds must be string list')
        for productId in productIds:
            if not productId or not isstring(productId):
                raise TYBizConfException(d, 'UserConditionCanBuyProduct.productIds must be string list')
        self.productIds = productIds
        return self


UserConditionRegister.registerClass(UserConditionCanBuyProduct.TYPE_ID, UserConditionCanBuyProduct)


