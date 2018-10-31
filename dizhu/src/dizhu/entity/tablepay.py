'''
Created on Feb 2, 2015

@author: hanwenfang
'''

from dizhu.entity.dizhuconf import DIZHU_GAMEID
import freetime.util.log as ftlog
from hall.entity import hallproductselector


def getProducts(userId, roomId, clientId):
    result = []
    product, _ = hallproductselector.selectTableBuyProduct(DIZHU_GAMEID, userId, clientId, roomId)
    if product:
        result.append({
                        "id": product.productId,
                        "name": product.displayName,
                        "price": product.price,
                        "desc": product.desc,
                        "price_diamond": product.priceDiamond,
                        "picurl": product.pic,
                        "buy_type": product.buyType
        })
    ftlog.debug('tablepay.getProducts userId=', userId,
                'gameId=', DIZHU_GAMEID,
                'roomId=', roomId,
                'clientId=', clientId,
                'result=', result)
    return result

