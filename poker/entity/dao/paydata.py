# -*- coding: utf-8 -*-
"""
Created on 2013-3-18

@author: Administrator
"""
from poker.servers.util.direct import dbpay

def getExchangeRecords(gameId, userId):
    """
    取得用户的所有兑换历史记录
    """
    pass

def makeExchangeId():
    """
    生成一个兑换的单号
    """
    pass

def makeGameOrderId(gameId, userId, productId):
    """
    生成一个游戏内的购买单号
    """
    pass

def setGameOrderInfo(userId, orderId, datas):
    """
    设置玩家的游戏内购买信息
    """
    pass

def getGameOrderInfo(orderId):
    """
    取得一个购买单号对应的所有购买信息
    """
    pass