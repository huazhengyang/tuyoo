# -*- coding: utf-8 -*-
"""
Created on 2014年11月22日

@author: zjgzzz@126.com
"""
import inspect

def getModuleAttr(pkgpath):
    """
    动态加载对应的pkgpath,并取得pkgpath中的指定的属性的值
    例如: pkgpath为: com.tuyoo.test.A
        那么import的包为com.tuyoo.test, 取的该包中A的值返回, 
        若A不存在这抛出异常
    """
    pass

def getModuleClsIns(clspath):
    """
    动态加载对应的clspath,并取得pkgpath中的指定的cls的实例值
    例如: pkgpath为: com.tuyoo.test.ClsA
        那么import的包为com.tuyoo.test, 取的该包中ClsA, 进行无参数的实例化,返回ClsA() 
    """
    pass

def getObjectFunctions(obj, funhead, funargcount):
    """
    获取obj对象中的方法集合
        方法名称过滤: 必须以funhead开头
        方法参数个数过滤: 方法的参数个数等于funargcount
    """
    pass

class TYClassRegister(object, ):
    """
    类注册表
    """
    _typeid_clz_map = {}

    @classmethod
    def findClass(cls, typeId):
        """
        依据类型, 取得对应的注册的对象
        """
        pass

    @classmethod
    def unRegisterClass(cls, typeId):
        """
        删除一个typeId的注册对象
        """
        pass

    @classmethod
    def registerClass(cls, typeId, clz):
        """
        以typeId为关键字,注册对象clz
        注册的typeId不允许重复
        """
        pass

def findPyFileListUnderModule(moduleName):
    """
    查找所有的直属的py文件,并进行动态装载，只查当前所属,不递归查找py文件
    """
    pass

def findMethodUnderModule(moduleName, methodName, filterFun=None):
    """
    查找给出的模块下的所有直属py文件， 并使用filterFun对直属的py文件进行过滤
    再过滤后的py文件中查找给出的methodName函数定义（只对照函数名，不检查参数）的列表集合
    """
    pass