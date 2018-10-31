# -*- coding: utf-8 -*-
"""
一些游戏无关的小工具
"""
__author__ = ['Wangtao']
from itertools import izip, ifilter, ifilterfalse
import functools
from freetime.core.timer import FTTimer

def mkdict(**kwargs):
    pass

def dict2obj(_dict):
    pass

def obj2dict(obj):
    pass

class MaxInt(int, ):

    def __gt__(self, other):
        pass

def isplit(predicate, iterable):
    """

    """
    pass

def pairwise(iterable):
    """

    """
    pass

def lazy_call(funcs):
    pass

def module_bridge_to_class(names, namespace={}):
    """

    """
    pass

def unique(iterable, hashable_func=None):
    """

    """
    pass

def callLater(delay, func, *args, **keywords):
    """
    用FTTimer实现的callLater
    """
    pass