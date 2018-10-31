# -*- coding: utf-8 -*-
"""
Created on 2017年10月13日

比赛报名费

@author: zhaol

"""

class AsyncCommonArenaFee(object, ):

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
    def params(self):
        pass

    def setParams(self, params):
        pass

    def getParam(self, paramName, defVal=None):
        pass

    @property
    def failure(self):
        """
        报名失败的提示信息
        """
        pass

    @property
    def payOrder(self):
        """
        报名失败的购买引导
        """
        pass

    def initConfig(self, d):
        pass

    def collectFee(self):
        """
        收取用户报名费
        """
        pass

    def userCanPay(self, userId, gameId, matchPlugin):
        """
        用户是否可以支付这个费用
        """
        pass
if (__name__ == '__main__'):
    pass