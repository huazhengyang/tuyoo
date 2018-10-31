# -*- coding: utf-8 -*-
'''
Created on 2015-5-12
@author: zqh
'''

def getResourcePath(fileName):
    '''
    取得当前文件下某一个资源的绝对路径
    '''
    import os
    cpath = os.path.abspath(__file__)
    cpath = os.path.dirname(cpath)
    fpath = cpath + os.path.sep + fileName
    return fpath


def loadResource(fileName):
    '''
    取得当前文件下某一个资源的文件内容
    '''
    fpath = getResourcePath(fileName)
    f = open(fpath)
    c = f.read()
    f.close()
    return c

