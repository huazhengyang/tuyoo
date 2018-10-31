# -*- coding: utf-8 -*-
"""
Created on 2016年6月7日

@author: luoguanggui
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
if (__name__ == '__main__'):
    pass