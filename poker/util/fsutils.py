# -*- coding: utf-8 -*-
"""
Created on 2015-5-12
@author: zqh
"""
import json, socket, shutil, re, os, platform, subprocess
from poker.util import strutil
__cur_machine_ip_list = None

def makeDirs(mpath, clear=False):
    """
    创建一个物理路径, 若相关联的上下级路径不存在,也会同时创建
    当clear为False时, 路径已经存在, 则不进行任何操作
    当clear为True时, 若路径已经存在, 那么清空改路径下的所有内容
    """
    pass

def deletePath(mpath):
    """
    强制删除一个物理路径
    """
    pass

def normpath(apath):
    """
    驳接os.path.normpath方法
    """
    pass

def abspath(apath):
    """
    驳接os.path.abspath方法
    """
    pass

def appendPath(parent, *path):
    """
    驳接os.path.join方法
    """
    pass

def getParentDir(apath, level=1):
    """
    取得apath向上跳level级的目录
    """
    pass

def getLastPathName(apath):
    """
    驳接os.path.basename方法, 取得路径的最后一个名称
    """
    pass

def makeAsbpath(mpath, relpath=None):
    """
    获得mpath的绝对路径
    若relpath为None,那么获得当前(PWD)的绝对路径
    否则以relpath为基础,取得绝对路径
    """
    pass

def fileExists(afile):
    """
    驳接os.path.isfile方法
    """
    pass

def dirExists(afile):
    """
    驳接os.path.isdir方法
    """
    pass

def writeFile(fpath, fname, content):
    """
    将内容content写入到 fpath/fname中
    若content为list, tuple, dict, set则进行JSON的序列化后在写入文件
    """
    pass

def readFile(fpath):
    """
    读取fpath指定文件的全部内容, 若文件不存在或出错,返回None
    """
    pass

def readJsonFile(fpath, needdecodeutf8=False):
    """
    读取fpath指定文件的JSON内容, 返回JSON对象
    若needdecodeutf8为真, 则进行UTF8的编码转换处理
    """
    pass

def copyFile(fromFile, toFile):
    """
    拷贝文件fromFile -> toFile
    """
    pass

def deleteFile(fromFile):
    """
    删除一个文件
    """
    pass

def findTreeFiles(fpath, include, exclude):
    """
    查找一个路劲下的所有文件
    include为包含文件的正则表示列表
    exclude为剔除文件的正则表示列表
    先判定是否要剔除,再判定是否要包含
    注意: 判定是否剔除时,是以fpath为基础的文件路径
        例如: fpath下有 <fpath>/a/1.txt <fpath>/2/b.txt
        判定时的文件路径为: "/a/1.txt" "/2/b.txt"
    """
    pass

def copyTree(pathlist, outpath, cuthead=0, logfun=None):
    """
    拷贝文件目录树
    pathlist为一个list列表, 每个列表中为一个拷贝源的定义
        {'path' : '/test/', 'include' : [], 'exclude' : []}
            path为拷贝的源, 
            include为拷贝包含的文件的正则表达式列表
            exclude为拷贝剔除的文件的正则表达式列表
    若cuthead不为0, 那么再拷贝目标时, 将丢弃源文件的cuthead个父级目录
    若logfun为一个函数, 则拷贝时, 调用此函数进行拷贝进度的输出提示
    """
    pass

def checkMachinePort(host, port=22, timeout=3):
    """
    检查一个机器的某个端口是否可以连接
    """
    pass

def getLocalMachineIp():
    """
    取得当前机器的IP地址列表
    """
    pass

def getHostIp(host):
    """
    取得host对应的IP地址
    """
    pass

def isLocalMachine(host):
    """
    判定给出的host是否是当前代码运行的本机
    """
    pass