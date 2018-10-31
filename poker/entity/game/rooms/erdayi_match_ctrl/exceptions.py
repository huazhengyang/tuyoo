# -*- coding: utf-8 -*-
"""
Created on 2016年7月6日

@author: zhaojiangang
"""
from poker.entity.biz.exceptions import TYBizException

class MatchException(TYBizException, ):

    def __init__(self, ec, message):
        pass

class MatchConfException(MatchException, ):

    def __init__(self, message):
        pass

class BadStateException(MatchException, ):

    def __init__(self, message='\xe7\x8a\xb6\xe6\x80\x81\xe9\x94\x99\xe8\xaf\xaf'):
        pass

class MatchStoppedException(MatchException, ):

    def __init__(self, message='\xe6\xaf\x94\xe8\xb5\x9b\xe5\xb7\xb2\xe5\x81\x9c\xe6\xad\xa2'):
        pass

class AleadyInMatchException(MatchException, ):

    def __init__(self, message='\xe6\xaf\x94\xe8\xb5\x9b\xe8\xbf\x98\xe5\x9c\xa8\xe8\xbf\x9b\xe8\xa1\x8c\xe4\xb8\xad,\n\xe5\xae\xa2\xe5\xae\x98\xe5\x8f\xaf\xe5\x89\x8d\xe5\xbe\x80\xe5\x85\xb6\xe4\xbb\x96\xe6\xaf\x94\xe8\xb5\x9b\xe7\x8e\xa9\xe8\x80\x8d\xe5\x99\xa2~'):
        pass

class SigninException(MatchException, ):

    def __init__(self, message='\xe6\x8a\xa5\xe5\x90\x8d\xe5\xa4\xb1\xe8\xb4\xa5'):
        pass

class SigninNotStartException(SigninException, ):

    def __init__(self, message='\xe6\x8a\xa5\xe5\x90\x8d\xe8\xbf\x98\xe6\x9c\xaa\xe5\xbc\x80\xe5\xa7\x8b'):
        pass

class SigninStoppedException(SigninException, ):

    def __init__(self, message='\xe6\x8a\xa5\xe5\x90\x8d\xe5\xb7\xb2\xe6\x88\xaa\xe6\xad\xa2'):
        pass

class SigninFullException(SigninException, ):

    def __init__(self, message='\xe6\x8a\xa5\xe5\x90\x8d\xe4\xba\xba\xe6\x95\xb0\xe5\xb7\xb2\xe6\xbb\xa1'):
        pass

class AlreadySigninException(SigninException, ):

    def __init__(self, message='\xe5\xb7\xb2\xe7\xbb\x8f\xe6\x8a\xa5\xe5\x90\x8d'):
        pass

class SigninConditionNotEnoughException(SigninException, ):

    def __init__(self, message='\xe6\x8a\xa5\xe5\x90\x8d\xe6\x9d\xa1\xe4\xbb\xb6\xe4\xb8\x8d\xe8\xb6\xb3'):
        pass

class SigninFeeNotEnoughException(SigninException, ):

    def __init__(self, fee, message='\xe6\x8a\xa5\xe5\x90\x8d\xe8\xb4\xb9\xe4\xb8\x8d\xe8\xb6\xb3'):
        pass