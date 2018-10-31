# -*- coding: utf-8 -*-
"""
Created on 2014年9月17日

@author: zjgzzz@126.com
"""

class MatchException(Exception, ):

    def __init__(self, errorCode, message):
        pass

    @property
    def errorCode(self):
        pass

    @property
    def message(self):
        pass

class ConfigException(MatchException, ):

    def __init__(self, message):
        pass

class MatchExpiredException(MatchException, ):

    def __init__(self, matchId, message=u'\u6bd4\u8d5b\u5df2\u7ecf\u4e0b\u7ebf'):
        pass

class AlreadySigninException(MatchException, ):

    def __init__(self, matchId, message=u'\u5df2\u7ecf\u62a5\u540d\u4e86\u8be5\u6bd4\u8d5b'):
        pass

class SigninNotStartException(MatchException, ):

    def __init__(self, matchId, message=u'\u62a5\u540d\u8fd8\u672a\u5f00\u59cb'):
        pass

class SigninStoppedException(MatchException, ):

    def __init__(self, matchId, message=u'\u62a5\u540d\u5df2\u622a\u6b62'):
        pass

class SigninFullException(MatchException, ):

    def __init__(self, matchId, message=u'\u6bd4\u8d5b\u4eba\u6570\u5df2\u6ee1\uff0c\u8bf7\u7b49\u5f85\u4e0b\u4e00\u573a\u6bd4\u8d5b'):
        pass

class SigninFeeNotEnoughException(MatchException, ):

    def __init__(self, matchInst, fee, message=u'\u62a5\u540d\u8d39\u4e0d\u8db3'):
        pass

class MatchAlreadyStartedException(MatchException, ):

    def __init__(self, matchId, message=u'\u6bd4\u8d5b\u5df2\u7ecf\u5f00\u59cb'):
        pass

class AlreadyInMatchException(MatchException, ):

    def __init__(self, matchId, message=u'\u5df2\u7ecf\u5728\u6bd4\u8d5b\u4e2d'):
        pass

class EnterMatchLocationException(MatchException, ):

    def __init__(self, matchId, message=u'\u9501\u5b9a\u7528\u6237\u5931\u8d25'):
        pass

class ClientVersionException(MatchException, ):
    pass

class MatchSigninConditionException(MatchException, ):
    pass