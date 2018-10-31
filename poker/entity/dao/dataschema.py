# -*- coding: utf-8 -*-
"""
Created on 2015-5-12
@author: zqh
"""
import json
import freetime.util.log as ftlog
from poker.util import keywords

def DATA_TYPE_INT(field, value, defaultVal, recovers):
    """
    整形数字, 缺省为0
    """
    pass

def DATA_TYPE_INT_ATOMIC(field, value, defaultVal, recovers):
    """
    整形数字, 缺省为0, 必须使用单独方法进行原子操作
    """
    pass

def DATA_TYPE_FLOAT(field, value, defaultVal, recovers):
    """
    浮点数字, 缺省为0.0
    """
    pass

def DATA_TYPE_FLOAT_ATOMIC(field, value, defaultVal, recovers):
    """
    浮点数字, 缺省为0.0, 必须使用单独方法进行原子操作  
    """
    pass

def DATA_TYPE_STR(field, value, defaultVal, recovers):
    """
    字符串, 缺省为空串  
    """
    pass

def DATA_TYPE_STR_FILTER(field, value, defaultVal, recovers):
    """
    字符串, 缺省为空串, 如果有值则进行关键字过滤
    """
    pass

def DATA_TYPE_LIST(field, value, defaultVal, recovers):
    """
    JSON格式的数组, 缺省为[] 
    """
    pass

def DATA_TYPE_DICT(field, value, defaultVal, recovers):
    """
    JSON格式的字典, 缺省的{}
    """
    pass

def DATA_TYPE_BOOLEAN(field, value, defaultVal, recovers):
    """
    真假值, 缺省为假 False  
    """
    pass

def redisDataSchema(cls):
    pass

class DataSchema:
    FIELDS_ALL = ()
    FIELDS_ALL_SET = set()
    WRITES_FIELDS = set()
    READ_ONLY_FIELDS = ()

    @staticmethod
    def checkData(field, value, recovers=None):
        """
        检测对应的字段的数据格式, 此方法由redisDataSchema修饰符自动生成
        """
        pass

    @staticmethod
    def mkey(*argl):
        """
        返回数据中的主键的值, 此方法由redisDataSchema修饰符自动生成
        """
        pass

    @classmethod
    def checkDataList(cls, fields, values, recovers=None):
        pass

    @classmethod
    def checkDataDict(cls, fields, values, recovers=None):
        pass

    @classmethod
    def paramsDict2List(cls, datas, check=1):
        pass

    @classmethod
    def paramsDict2Dict(cls, datas, check=1):
        pass

    @classmethod
    def assertParamDictFields(cls, dataDict):
        pass

    @classmethod
    def assertParamListFields(cls, dataList):
        pass