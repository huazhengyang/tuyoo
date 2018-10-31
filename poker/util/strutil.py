# -*- coding: utf-8 -*-
"""
Created on 2015-5-12
@author: zqh
"""
from hashlib import md5
import uuid
import json
import base64
import urllib
import re
import struct
import os
import freetime.util.log as ftlog
from freetime.util import encry
from freetime.util.cache import lfu_cache
from poker.util.constants import CLIENT_SYS_IOS, CLIENT_SYS_ANDROID, CLIENT_SYS_H5, CLIENT_SYS_WINPC, CLIENT_SYS_MACOS
from poker.util.pokercffi import POKERC
from poker.util.pokercffi import POKERFFI
from poker.util import constants
from sre_compile import isstring
from copy import deepcopy
__buffered_reg = {}
__int62 = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
__int62dictint = {}
__int62dictstr = {}
for x in xrange(len(__int62)):
    __int62dictint[x] = __int62[x]
    __int62dictstr[__int62[x]] = x
__ffi_des_str = POKERFFI.new('unsigned char[]', 65536)
__ffi_code_str = POKERFFI.new('char[]', 65536)

def tycode(seed, datas):
    pass

def desEncrypt(deskey, desstr):
    """
    DES加密算法
    """
    pass

def desDecrypt(deskey, desstr):
    """
    DES解密算法
    """
    pass

def tyDesEncode(desstr):
    """
    途游标准加密算法(固定的deskey)
    """
    pass

def tyDesDecode(desstr):
    """
    途游标准解密算法(固定的deskey)
    """
    pass

def getEnv(ekey, defaultval):
    """
    获取系统环境变量
    """
    pass

def cloneData(data):
    """
    使用JSON的loads和dump克隆一个数据对象
    """
    pass

def uuid():
    """
    取得一个32位长的UUID字符串
    """
    pass

def dumps(obj):
    """
    驳接JSON的dumps方法, 使用紧凑的数据格式(数据项之间无空格)
    """
    pass

def dumpsbase64(obj):
    """
    驳接JSON的dumps方法,并对结果进行BASE64的编码
    """
    pass

def loadsbase64(base64jsonstr, decodeutf8=False):
    """
    驳接JSON的loads方法, 先对json串进行BASE64解密,再解析为JSON格式
    若decodeutf8为真, 那么将所有的字符串转换为ascii格式
    """
    pass

def loads(jsonstr, decodeutf8=False, ignoreException=False, execptionValue=None):
    """
    驳接JSON的loads方法
    若decodeutf8为真, 那么将所有的字符串转换为ascii格式
    若ignoreException为真, 那么忽略JSON格式的异常信息
    若execptionValue为真, 当若ignoreException为真时,发生异常,则使用该缺省值
    """
    pass

def b64decode(base64str):
    """
    驳接BASE64的解密方法, 替换数据中的空格到+号后,再进行解密
    """
    pass

def b64encode(normalstr):
    """
    驳接BASE64的加密方法
    """
    pass

def md5digest(md5str):
    """
    计算一个字符串的MD5值, 返回32位小写的MD5值
    """
    pass

def urlencode(params):
    """
    将params进行URL编码
    """
    pass

@lfu_cache(maxsize=1000, cache_key_args_index=0)
def _getCompiledReg(regExp):
    pass

def regMatch(regExp, checkStr):
    """
    正则表达式匹配处理
    支持特殊的正则"*",意味全量匹配
    此方法会缓存已经编译过的正则, 进行加速处理
    """
    pass

def regMatchList(regExpList, checkStr):
    """
    正则表达式匹配处理, regExpList为一个正则表达式的列表, 若匹配到一个则返回真
    支持特殊的正则"*",意味全量匹配
    此方法会缓存已经编译过的正则, 进行加速处理
    """
    pass

def tostr62(int10, slenfix=0):
    """
    10进制转换为62进制
    """
    pass

def toint10(str62):
    """
    62进制转换为10进制
    """
    pass

def getJsonStr(jsonstr, key, defaultVal=''):
    """
    JSON的快速替代方法
    找到对应的key的字符串值, 
    注意: 必须确信key对应的值为标准的字符串格式,且其中没有转义的双引号存在
    """
    pass

def getJsonInt(jsonstr, key, defaluVal=0):
    """
    JSON的快速替代方法
    找到对应的key的字符串的int值, 
    注意: 必须确信key对应的值为标准的数字格式,且其中没有转义的双引号存在
    """
    pass

def dumpDatas(data):
    """
    使用JSON的方式, 序列化data数据
    """
    pass

def replaceEvnValue(datastr, envdict):
    """
    查找datastr中${XX}格式的字符串, 替换为envdict中的XX对应的值
    对于${标记,支持""转义处理
    若标记为: ${XX++}, 那么取得envdict中的XX值后, 将envdict中的XX值加1
    若标记为: ${XX+n}, 那么取得envdict中的XX+n值
    """
    pass

def replaceObjEvnValue(obj, envdict):
    """
    遍历obj(list, dict)中的所有数据, 并使用replaceEvnValue方法,处理遇到的所有的字符串
    """
    pass

def replaceObjRefValue(obj):
    pass

def _replaceObjRefValue(obj, stack):
    pass

def _replaceRefValue(datastr, envdict):
    pass

def unicode2Ascii(idata):
    """
    编码转换: UNICODE至ASCII
    """
    pass

def pack(struct_fmt, *datas):
    """
    驳接struct的pack方法
    """
    pass

def unpack(struct_fmt, datas):
    """
    驳接struct的unpack方法
    """
    pass

def decodeObjUtf8(datas):
    """
    遍历datas(list,dict), 将遇到的所有的字符串进行encode utf-8处理
    """
    pass

def getTableRoomId(tableId):
    """
    解析大房间的roomId, 取得gameId和configId
    """
    pass

@lfu_cache(maxsize=1000, cache_key_args_index=0)
def parseBigRoomId(roomId):
    """
    解析大房间的roomId, 取得gameId和configId
    """
    pass

def getBigRoomIdFromInstanceRoomId(roomId):
    """
    解析大房间的roomId, 取得gameId和configId
    """
    pass

@lfu_cache(maxsize=1000, cache_key_args_index=0)
def parseInstanceRoomId(roomId):
    """
    解析房间实例的roomId(控制房间和桌子房间), 取得gameId, configId, controlId, showdId
    注: 若为控制房间showdId必定为0, 若为桌子房间showdId必定大于0
    """
    pass

@lfu_cache(maxsize=1000, cache_key_args_index=0)
def getGameIdFromInstanceRoomId(roomId):
    """
    解析房间实例的roomId(控制房间和桌子房间), 取得gameId
    注: 若为控制房间showdId必定为0, 若为桌子房间showdId必定大于0
    """
    pass

@lfu_cache(maxsize=1000, cache_key_args_index=0)
def getGameIdFromBigRoomId(bigRoomId):
    """
    解析房间的BigRoomId 取得gameId
    """
    pass

@lfu_cache(maxsize=1000, cache_key_args_index=0)
def parseClientId(clientId):
    pass

def isTheOsClient(clientId, osName):
    pass

def isWinpcClient(clientId):
    pass
_OLDCLIENTID_HALL6 = {'Android_3.28_360.aigame,weakChinaMobile,woStore.0.360.mayor360', 'Android_3.27_360.360.0.360.mayor360', 'Android_3.26_tuyoo.tuyoo.0.tuyoo.tuyoostar', 'Android_3.25_tuyoo.tuyoo.0.tuyoo.tuyoostar', 'Android_3.2_tuyoo.newYinHe.0.wangyi.tuwangyi', 'Android_3.33_newpay', 'Android_3.27_tuyoo.weakChinaMobile.0.tuyoo.mayortuyooyidongmm', 'Android_3.28_tuyoo.woStore.0.tuyoo.mayortuyoowoStore', 'Android_3.27_tuyoo.tuyoo.0.tuyoo.mayortuyoo', 'Android_3.27_tuyoo.woStore.0.starwoStore.starzszhwoStore1', 'Android_3.1_360sns.360sns.1.360.360sns', 'Android_3.11_360sns.360sns,newYinHe.1.360.360sns', 'Android_3.25_360.360.0.360.star360', 'Android_3.26_360.360.0.360.star360', 'Android_3.27_360.360.0.360.star360', 'Android_3.21_360.newYinHe.0.360.tu360', 'Android_3.22_360.newYinHe.0.360.tu360', 'Android_3.23_360.newYinHe.0.360.tu360', 'Android_3.25_360.tuyoo.0.360.tu360', 'Android_3.2_360.newYinHe.0.360.tu360', 'Android_3.21_360.newYinHe.0.360.laizi360', 'Android_3.23_360.newYinHe.0.360.laizi360', 'Android_3.24_360.360.0.360.laizi360', 'Android_3.25_360.360.0.360.laizi360', 'Android_3.2_360.newYinHe.0.360.laizi360', 'Android_3.29_360.360.0.360.mayor360', 'Android_3.28_360.weakChinaMobile.0.360.mayor360yidongmm', 'Android_3.33_kugou.weakChinaMobile.0-6.kugou.kgtongcheng', 'Android_3.7_monitor', 'Android_3.3_monitor'}

@lfu_cache(maxsize=1000, cache_key_args_index=0)
def getGameIdFromHallClientId(clientId):
    pass

@lfu_cache(maxsize=1000, cache_key_args_index=0)
def getChannelFromHallClientId(clientId):
    pass

def getPhoneTypeName(phone_type_code):
    pass

def getPhoneTypeCode(phone_type_name):
    pass

def replaceParams(string, params):
    pass

def parseInts(*args):
    pass

def ensureString(val, defVal=''):
    pass