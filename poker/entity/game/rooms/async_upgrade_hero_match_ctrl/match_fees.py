# -*- coding: utf-8 -*-
"""
Created on 2017年10月13日

比赛报名费s
报名时，任选一个即可

@author: zhaol

"""
from freetime.util import log as ftlog
from poker.entity.dao import weakdata

class MatchFeeNode(object, ):

    def __init__(self):
        pass

    @property
    def desc(self):
        """
        报名费描述
        """
        pass

    def setDesc(self, desc):
        pass

    @property
    def assetKindId(self):
        pass

    def setAssetKindId(self, kindId):
        pass

    @property
    def count(self):
        pass

    def setCount(self, count):
        pass

    @property
    def failure(self):
        """
        报名失败的提示信息
        """
        pass

    def setFailure(self, failure):
        pass

    @property
    def payOrder(self):
        """
        报名失败的购买引导
        """
        pass

    def setPayOrder(self, payOrder):
        pass

    @property
    def startCollect(self):
        """
        每日第几次报名开始收费
        """
        pass

    def setStartCollect(self, startCollect):
        pass

    def initConfig(self, d):
        pass

    def collectFee(self):
        """
        收取用户报名费
        """
        pass

class AsyncUpgradeHeroMatchFees(object, ):

    def __init__(self):
        pass

    @property
    def fees(self):
        """
        报名费集合
        """
        pass

    def setFees(self, fees):
        pass

    def needFee(self):
        pass

    def getFeeByIndex(self, feeIndex):
        pass

    def initConfig(self, config):
        pass

    def getDesc(self, userId=0, gameId=0):
        """
        获取报名费描述
        """
        pass
if (__name__ == '__main__'):
    config = [{'desc': '1\xe5\xbc\xa0\xe5\x8f\x82\xe8\xb5\x9b\xe5\x88\xb8', 'count': 1, 'itemId': 'item:1007', 'failure': '\xe6\x82\xa8\xe7\x9a\x84\xe8\xb4\xb9\xe7\x94\xa8\xe4\xb8\x8d\xe8\xb6\xb3\xef\xbc\x8c\xe6\x9c\xac\xe6\xaf\x94\xe8\xb5\x9b\xe6\x8a\xa5\xe5\x90\x8d\xe8\xb4\xb9\xe9\x9c\x801\xe5\xbc\xa0\xe5\x8f\x82\xe8\xb5\x9b\xe5\x88\xb8'}]
    fees = AsyncUpgradeHeroMatchFees()
    fees.initConfig(config)