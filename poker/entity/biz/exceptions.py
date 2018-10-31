# -*- coding: utf-8 -*-
"""
Created on 2015年6月1日

@author: zhaojiangang
"""

class TYBizException(Exception, ):

    def __init__(self, errorCode, message):
        pass

    @property
    def errorCode(self):
        pass

    @property
    def message(self):
        pass

    def __str__(self):
        pass

    def __unicode__(self):
        pass

class TYBizBadDataException(Exception, ):

    def __init__(self, message):
        pass

class TYBizConfException(TYBizException, ):

    def __init__(self, conf, message):
        pass

    def __str__(self):
        pass

    def __unicode__(self):
        pass