# -*- coding: utf-8 -*-
"""
Created on 2016年1月16日

@author: zhaojiangang
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

class SigninException(MatchException, ):

    def __init__(self, message):
        pass

class SigninNotStartException(SigninException, ):

    def __init__(self, message='\xe6\x8a\xa5\xe5\x90\x8d\xe8\xbf\x98\xe6\x9c\xaa\xe5\xbc\x80\xe5\xa7\x8b'):
        pass

class SigninStoppedException(SigninException, ):

    def __init__(self, message=u'\u62a5\u540d\u5df2\u622a\u6b62'):
        pass

class SigninFullException(SigninException, ):

    def __init__(self, message=u'\u6bd4\u8d5b\u4eba\u6570\u5df2\u6ee1\uff0c\u8bf7\u7b49\u5f85\u4e0b\u4e00\u573a\u6bd4\u8d5b'):
        pass

class SigninConditionNotEnoughException(SigninException, ):

    def __init__(self, message=u'\u62a5\u540d\u6761\u4ef6\u4e0d\u8db3'):
        pass

class SigninFeeNotEnoughException(SigninException, ):

    def __init__(self, fee, message=u'\u62a5\u540d\u8d39\u4e0d\u8db3'):
        pass

class MatchStoppedException(SigninException, ):

    def __init__(self, message=u'\u6bd4\u8d5b\u5df2\u7ecf\u4e0b\u7ebf'):
        pass

class AlreadySigninException(SigninException, ):

    def __init__(self, message='\xe5\xb7\xb2\xe7\xbb\x8f\xe6\x8a\xa5\xe5\x90\x8d'):
        pass

class AlreadyInMatchException(SigninException, ):

    def __init__(self, message=u'\u6bd4\u8d5b\u8fd8\u5728\u8fdb\u884c\u4e2d,\n\u5ba2\u5b98\u53ef\u524d\u5f80\u5176\u4ed6\u6bd4\u8d5b\u73a9\u800d\u5662~'):
        pass

class BadStateException(MatchException, ):

    def __init__(self, message='\xe9\x94\x99\xe8\xaf\xaf\xe7\x9a\x84\xe7\x8a\xb6\xe6\x80\x81'):
        pass

class NotFoundGroupException(MatchException, ):

    def __init__(self, message='\xe6\xb2\xa1\xe6\x9c\x89\xe6\x89\xbe\xe5\x88\xb0\xe5\x88\x86\xe7\xbb\x84'):
        pass

class PopWndNotException(MatchException, ):

    def __init__(self, message='\xe5\xbc\xb9\xe7\xaa\x97\xe6\x8f\x90\xe7\xa4\xba,\xe4\xb8\x8d\xe6\x8a\x9b\xe5\x87\xba\xe5\xbc\x82\xe5\xb8\xb8'):
        pass
if (__name__ == '__main__'):
    pass