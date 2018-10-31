# -*- coding: utf-8 -*-
"""
Created on 2015年4月15日

@author: zhaojiangang
"""
from poker.entity.biz.exceptions import TYBizException

class TYRankingException(TYBizException, ):

    def __init__(self, ec, message):
        pass

class TYRankingUnknownException(TYRankingException, ):

    def __init__(self, rankingId):
        pass

class TYRankingConfException(TYRankingException, ):

    def __init__(self, conf, message):
        pass