# -*- coding: utf-8 -*-
"""

"""
__author__ = ['"Zhouhao" <zhouhao@tuyoogame.com>']
from freetime.util import log as ftlog

class MultiDict(dict, ):
    """
    扩展的字典
    使用此字典, 可以附加一组特殊的属性值到字典当中, 方便控制特殊属性和当前字典的生命周期一致性
    例如: 再getConf后取得一个字典配置, 但是需要进行一定的数据转换才可使用,
        那么就可以将转换后的结构放在setExtendAttr中, 再次使用的时候, 直接使用上次转换后的数据即可
    """

    def __init__(self, odict=None):
        pass

    def getExtendAttr(self, key):
        pass

    def setExtendAttr(self, key, value):
        pass

class MultiList(list, ):
    """
    扩展的字典
    使用此字典, 可以附加一组特殊的属性值到字典当中, 方便控制特殊属性和当前字典的生命周期一致性
    例如: 再getConf后取得一个字典配置, 但是需要进行一定的数据转换才可使用,
        那么就可以将转换后的结构放在setExtendAttr中, 再次使用的时候, 直接使用上次转换后的数据即可
    """

    def __init__(self, olist=None):
        pass

    def getExtendAttr(self, key):
        pass

    def setExtendAttr(self, key, value):
        pass

class Singleton(type, ):

    def __init__(self, name, bases, dic):
        pass

    def __call__(self, *args, **kwargs):
        pass