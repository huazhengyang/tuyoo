# -*- coding=utf-8
'''
Created on 2015年8月14日

@author: zhaojiangang
'''
from freetime.entity.msg import MsgPack
from hall.entity import hallbenefits, datachangenotify, hallflipcardluck, \
    hallitem
from hall.entity.hallflipcardluck import FlippedCardAsset, FlippedCardProduct
from hall.entity.todotask import TodoTaskPayOrder, TodoTaskHelper, TodoTaskNoop
from hall.servers.common.base_checker import BaseMsgPackChecker
from poker.protocol import router
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod
from poker.util import strutil
import poker.util.timestamp as pktimestamp


class FlipCardLuckHelper(object):
    @classmethod
    def encodeFlippedCardList(cls, flippedCardList, index):
        cards = []
        for i, flippedCard in enumerate(flippedCardList):
            d = cls.encodeFlippedCard(flippedCard, i != index)
            if d:
                cards.append(d)
        return cards
    
    @classmethod
    def encodeFlippedCard(cls, flippedCard, isPadding):
        d = {}
        if isinstance(flippedCard, FlippedCardAsset):
            d['name'] = flippedCard.assetKind.displayName
            d['pic'] = flippedCard.assetKind.pic
            if not isPadding:
                d['tips'] = cls.filterItemTips(flippedCard)
        elif isinstance(flippedCard, FlippedCardProduct):
            d['name'] = flippedCard.product.displayName
            d['pic'] = flippedCard.product.pic
            if not isPadding:
                d['tips'] = cls.filterProductTips(flippedCard)
        return d
    
    @classmethod
    def filterAssetDesc(cls, flippedCard):
        desc = flippedCard.flipableCard.desc
        assetDesc = flippedCard.assetKind.desc
        if not desc:
            return assetDesc
        return strutil.replaceParams(desc, {'itemDesc':assetDesc, 'count':flippedCard.count})
    
    @classmethod
    def filterAssetTips(cls, flippedCard):
        tips = flippedCard.flipableCard.tips
        return strutil.replaceParams(tips, {'count':flippedCard.count, 'units':flippedCard.item.units})
    
    @classmethod
    def filterProductDesc(self, flippedCard):
        desc = flippedCard.flipableCard.desc
        if not desc:
            return flippedCard.product.content.desc
        return strutil.replaceParams(desc, {
                                'contentDesc':flippedCard.product.content.desc,
                                'price':flippedCard.product.price,
                                'chipCount':flippedCard.product.getMinFixedAssetCount(hallitem.ASSET_CHIP_KIND_ID)
                            })
            
    @classmethod
    def filterProductTips(cls, flippedCard):
        tips = flippedCard.flipableCard.tips
        return tips or '仅10%的概率抽中'
    
    @classmethod
    def getFlippedCardDesc(cls, flippedCard):
        if isinstance(flippedCard, FlippedCardAsset):
            return cls.filterAssetDesc(flippedCard)
        elif isinstance(flippedCard, FlippedCardProduct):
            return cls.filterProductDesc(flippedCard)
        return ''
    
    @classmethod
    def buildFlipCardResponse(cls, gameId, userId, roomId, flipIndex,
                              flippedCardList, benefitsSend, userBenefits):
        assert(flipIndex >= 0 and flipIndex <= len(flippedCardList))
        flippedCard = flippedCardList[flipIndex]
        mo = MsgPack()
        mo.setCmd('flip_card_luck')
        mo.setResult('action', 'flip')
        mo.setResult('index', flipIndex)
        mo.setResult('userId', userId)
        mo.setResult('gameId', gameId)
        
        mo.setResult('cards', cls.encodeFlippedCardList(flippedCardList, flipIndex))
        mo.setResult('desc', cls.getFlippedCardDesc(flippedCard))
        
        if isinstance(flippedCard, FlippedCardProduct):
            payOrder = TodoTaskPayOrder(flippedCard.product)
            mo.setResult('sub_action', payOrder.toDict())
            mo.setResult('sub_text', hallflipcardluck.getString('product.subText', '立即购买'))
            
            if benefitsSend:
                mo.setResult('sub_action_ext', TodoTaskHelper.makeTodoTaskBenefitsInfo(benefitsSend, userBenefits).toDict())
            else:
                mo.setResult('sub_action_ext', TodoTaskNoop().toDict())
            mo.setResult('sub_text_ext', hallflipcardluck.getString('product.subTextExt', '取消'))
        elif isinstance(flippedCard, FlippedCardAsset):
            if benefitsSend:
                mo.setResult('sub_action', TodoTaskHelper.makeTodoTaskBenefitsInfo(benefitsSend, userBenefits).toDict())
            else:
                mo.setResult('sub_action', TodoTaskNoop().toStr())
            mo.setResult('sub_text', hallflipcardluck.getString('item.subText', '确定'))
        return mo
    
@markCmdActionHandler
class FlipCardLuckHandler(BaseMsgPackChecker):
    def __init__(self):
        super(FlipCardLuckHandler, self).__init__()
        
    def _check_param_index(self, msg, key, params):
        index = msg.getParam('index')
        if not isinstance(index, int) or index < 0 or index > 3:
            return 'ERROR of index !' + str(index), None
        return None, index
    
    @markCmdActionMethod(cmd='flip_card_luck', action="flip", clientIdVer=0)
    def doFlip(self, gameId, userId, clientId, index, roomId0):
        # 此处检查是否发放救济金
        timestamp = pktimestamp.getCurrentTimestamp()
        benefitsSend, userBenefits = hallbenefits.benefitsSystem.sendBenefits(gameId, userId, timestamp)
        
        if benefitsSend:
            datachangenotify.sendDataChangeNotify(gameId, userId, ['chip'])
        
        flippedCard, paddingsCardList = hallflipcardluck.flipCard(gameId, userId, clientId, roomId0, 3)
        
        flippedCardList = paddingsCardList
        flippedCardList.insert(index, flippedCard)
        
        mo = FlipCardLuckHelper.buildFlipCardResponse(gameId, userId, roomId0, index,
                                                      flippedCardList, benefitsSend, userBenefits)
        router.sendToUser(mo, userId)
        return mo
    

