# -*- coding=utf-8 -*-
from poker.entity.biz.activity.activity import TYActivity
from hall.entity import hallstore
from hall.entity.todotask import TodoTaskPayOrder
import freetime.util.log as ftlog
from hall.entity.hallactivity.activity_type import TYActivityType
from poker.util import strutil

class TYActivitySale(TYActivity):
    TYPE_ID = TYActivityType.ACTIVITY_SALE  

    def getConfigForClient(self, gameId, userId, clientId):
        """
        预期实现功能。配置中，配置payOrder后台自动生成该商品的todotask
        
        """
        clientConf = strutil.cloneData(self._clientConf)
        payOrder = clientConf["config"]["button"]["payOrder"]
                    
        product, _ = hallstore.findProductByPayOrder(gameId, userId, clientId, payOrder)
        ftlog.debug("TYActivitySale product: ", product)
        payOrder = TodoTaskPayOrder(product)
        ftlog.debug("TYActivitySale params: ", payOrder)
        try:
            clientConf["config"]["button"]["todoTask"] = payOrder.toDict()
        except:
            ftlog.exception("getConfigForClient error, can not set todotask, clientId:", clientId)
            return None
        return clientConf
    
    
