# -*- coding:utf-8 -*-
'''
Created on 2016年12月21日

@author: zhaojiangang
'''
from collections import OrderedDict


class LastUpdatedOrderedDict(OrderedDict):
    def __setitem__(self, key, value):
        try:
            del self[key]
        except:
            pass
        OrderedDict.__setitem__(self, key, value)
