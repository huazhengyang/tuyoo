# -*- coding: utf-8 -*-
"""
Created on 2016年12月21日

@author: zhaojiangang
"""
from collections import OrderedDict

class LastUpdatedOrderedDict(OrderedDict, ):

    def __setitem__(self, key, value):
        pass

    def safepop(self, key):
        pass