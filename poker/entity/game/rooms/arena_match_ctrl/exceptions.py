# -*- coding: utf-8 -*-
"""
Created on 2014年9月17日

@author: zjgzzz@126.com
"""
from poker.entity.biz.exceptions import TYBizException

class MatchException(TYBizException, ):

    def __init__(self, matchId, errorCode, message):
        pass

    @property
    def matchId(self):
        pass

class MatchExpiredException(MatchException, ):

    def __init__(self, matchId, message=u'\u6bd4\u8d5b\u5df2\u7ecf\u7ed3\u675f'):
        pass

class MatchSigninException(MatchException, ):

    def __init__(self, matchId, errorCode, message):
        pass

class AlreadySigninException(MatchSigninException, ):

    def __init__(self, matchId, message=u'\u5df2\u7ecf\u62a5\u540d\u4e86\u8be5\u6bd4\u8d5b'):
        pass

class AlreadyInMatchException(MatchSigninException, ):

    def __init__(self, matchId, message=u'\u6bd4\u8d5b\u8fd8\u5728\u8fdb\u884c\u4e2d,\n\u5ba2\u5b98\u53ef\u524d\u5f80\u5176\u4ed6\u6bd4\u8d5b\u73a9\u800d\u5662~'):
        pass

class SigninNotStartException(MatchSigninException, ):

    def __init__(self, matchId, message=u'\u62a5\u540d\u8fd8\u672a\u5f00\u59cb'):
        pass

class SigninStoppedException(MatchSigninException, ):

    def __init__(self, matchId, message=u'\u62a5\u540d\u5df2\u622a\u6b62'):
        pass

class SigninFullException(MatchSigninException, ):

    def __init__(self, matchId, message=u'\u6bd4\u8d5b\u4eba\u6570\u5df2\u6ee1\uff0c\u8bf7\u7b49\u5f85\u4e0b\u4e00\u573a\u6bd4\u8d5b'):
        pass

class SigninFeeNotEnoughException(MatchSigninException, ):

    def __init__(self, matchId, fee, message=u'\u62a5\u540d\u8d39\u4e0d\u8db3'):
        pass

class NotSigninException(MatchSigninException, ):

    def __init__(self, matchId, message=u'\u8fd8\u6ca1\u6709\u62a5\u540d'):
        pass

class EnterMatchLocationException(MatchException, ):

    def __init__(self, matchId, message=u'\u9501\u5b9a\u7528\u6237\u5931\u8d25'):
        pass

class ClientVersionException(MatchException, ):
    pass

class MatchSigninConditionException(MatchException, ):
    pass