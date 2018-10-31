# -*- coding:utf-8 -*-
'''
Created on 2016年5月17日

@author: zhaojiangang
'''
from poker.entity.biz.exceptions import TYBizException


class DizhuException(TYBizException):
    def __init__(self, ec, message):
        super(DizhuException, self).__init__(ec, message)

class ChipNotEnoughException(DizhuException):
    def __init__(self, message='金币不足'):
        super(ChipNotEnoughException, self).__init__(-1, message)

class BadPlayerException(DizhuException):
    def __init__(self, message=''):
        super(BadPlayerException, self).__init__(-1, message)

class NotFoundPlayerException(DizhuException):
    def __init__(self, message=''):
        super(NotFoundPlayerException, self).__init__(-1, message)

class NoIdleSeatException(DizhuException):
    def __init__(self, message=''):
        super(NoIdleSeatException, self).__init__(-1, message)

class BadTableException(DizhuException):
    def __init__(self, message=''):
        super(BadTableException, self).__init__(-1, message)
        
class BadSeatException(DizhuException):
    def __init__(self, message=''):
        super(BadSeatException, self).__init__(-1, message)

class SeatNotIdleException(DizhuException):
    def __init__(self, message=''):
        super(SeatNotIdleException, self).__init__(-1, message)

class InSeatException(DizhuException):
    def __init__(self, message=''):
        super(InSeatException, self).__init__(-1, message)

class EmptySeatException(DizhuException):
    def __init__(self, message=''):
        super(EmptySeatException, self).__init__(-1, message)

class BadOpSeatException(DizhuException):
    def __init__(self, message=''):
        super(BadOpSeatException, self).__init__(-1, message)

class BadStateException(DizhuException):
    def __init__(self, message=''):
        super(BadStateException, self).__init__(-1, message)

class BadCardException(DizhuException):
    def __init__(self, message=''):
        super(BadCardException, self).__init__(-1, message)

class BadCardCrcException(DizhuException):
    def __init__(self, message=''):
        super(BadCardCrcException, self).__init__(-1, message)
        
class BadCallException(DizhuException):
    def __init__(self, message=''):
        super(BadCallException, self).__init__(-1, message)

class BadJiabeiException(DizhuException):
    ''' 加倍错误 '''
    def __init__(self, message=''):
        super(BadJiabeiException, self).__init__(-1, message)

class BadHuanpaiException(DizhuException):
    ''' 换牌错误 '''
    def __init__(self, message=''):
        super(BadHuanpaiException, self).__init__(-1, message)

class ClientException(DizhuException):
    ''' 客户端异常 '''
    def __init__(self, message=''):
        super(ClientException, self).__init__(-1, message)
        
class ConfigureException(DizhuException):
    ''' 配置错误 '''
    def __init__(self, message=''):
        super(ConfigureException, self).__init__(-1, message)

class NotSupportedException(DizhuException):
    def __init__(self, message=''):
        super(NotSupportedException, self).__init__(-1, message)


