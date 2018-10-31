# -*- coding: utf-8 -*-
"""
Created on 2015-5-12
@author: zqh
"""

class ReadonlyDict(object, ):
    """
    类似dict的所有行为, 但是剔除dict的所有"写"方法, 即: 只读的dict
    """

    def __init__(self, objdict):
        pass

    def __setattr__(self, *args, **kwargs):
        pass

    def __contains__(self, key):
        pass

    def __getitem__(self, key):
        pass

    def __iter__(self):
        pass

    def __len__(self):
        pass

    def __repr__(self):
        pass

    def __str__(self):
        pass

    def get(self, key, default=None):
        pass

    def has_key(self, key):
        pass

    def items(self):
        pass

    def iteritems(self):
        pass

    def iterkeys(self):
        pass

    def itervalues(self):
        pass

    def keys(self):
        pass

    def values(self):
        pass

def makeReadonly(obj):
    """
    返回对应obj的只读的数据
    例如: list替换为tuple, dict替换为只读的dict
    """
    pass