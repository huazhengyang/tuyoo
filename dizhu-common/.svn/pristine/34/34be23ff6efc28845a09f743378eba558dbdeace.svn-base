'''
Created on Feb 2, 2015

@author: hanwenfang
'''

import freetime.util.log as ftlog
from hall.entity import hallproductselector


def getProducts(gameId, userId, roomId, clientId):
    result = []
    product, _ = hallproductselector.selectTableBuyProduct(gameId, userId, clientId, roomId)
    if product:
        result.append({
            'id': product.productId,
            'name': product.displayName,
            'price': product.price,
            'desc': product.desc,
            'price_diamond': product.priceDiamond,
            'picurl': product.pic,
            'buy_type': product.buyType
        })
    if ftlog.is_debug():
        ftlog.debug('tablepay.getProducts userId=', userId,
                    'gameId=', gameId,
                    'roomId=', roomId,
                    'clientId=', clientId,
                    'result=', result)
    return result

