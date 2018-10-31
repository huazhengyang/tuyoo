# -*- coding: utf-8 -*-
"""
Created on 2015年6月30日

@author: zhaojiangang
"""
from poker.entity.biz.exceptions import TYBizException

class TYTaskException(TYBizException, ):

    def __init__(self, errorCode, message):
        pass

    def __str__(self):
        pass

    def __unicode__(self):
        pass

class TYTaskConfException(TYTaskException, ):

    def __init__(self, conf, message):
        pass

    def __str__(self):
        pass

    def __unicode__(self):
        pass

class TYTaskNotFinisheException(TYTaskException, ):

    def __init__(self, taskKindId):
        pass

    def __str__(self):
        pass

    def __unicode__(self):
        pass

class TYTaskAlreayGetRewardException(TYTaskException, ):

    def __init__(self, taskKindId):
        pass

    def __str__(self):
        pass

    def __unicode__(self):
        pass