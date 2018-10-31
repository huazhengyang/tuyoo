# -*- coding: utf-8 -*-
"""
Created on 2014年2月12日

@author: zjgzzz@126.com
"""
import codecs
from sre_compile import isstring
import freetime.util.log as ftlog
from poker.resource import getResourcePath
from poker.util import fsutils

class KeywordFilter(object, ):
    """
    敏感词过滤器，使用方法
    1. 构造
    1.1 从文件加载(敏感词文件中每行一个词，默认utf8编码，也可以指定其它编码)
        kwf = KeywordFilter.loadFromFile('./keywords.txt', 'utf16')
    1.2 自己构造并添加敏感词
        kfw = KeywordFilter()
        kfw.addKeywords(['hello', 'keyword'])

    2. 替换关键词,
        kfw = KeywordFilter()
        kfw.addKeywords(['hello', 'keyword'])
        content = 'hello-keyword'
        kfw.replace(content) == u'*****-*******'

    3. 检测给定的内容是否存在关键词
        kfw = KeywordFilter()
        kfw.addKeywords(['hello', 'keyword'])
        content = 'hello-keyword'
        kfw.isContains(content) == True
    """

    def __init__(self):
        pass

    def getKeywords(self):
        pass

    def addKeywords(self, keywords):
        pass

    def addKeyword(self, keyword):
        """

        """
        pass

    def isContains(self, content):
        pass

    def replace(self, content, mask=u'*'):
        """
        替换content中的所有敏感词为mask*len(关键词)
        """
        pass

    def count(self):
        """

        """
        pass

    def loadFromFile(self, path, encoding='utf16'):
        """

        """
        pass

    def _match(self, content):
        pass

    def _matchIter(self, content):
        pass

    def __ensureUnicode(self, content):
        pass
_defaultKf = None

def _initialize():
    pass

def replace(content, mask=u'*'):
    """
    替换关键词(敏感词汇)
    """
    pass

def isContains(content):
    """
    检测给定的内容是否存在关键词(敏感词汇)
    """
    pass