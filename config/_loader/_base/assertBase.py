# -*- coding: utf-8 -*-
'''
Created on 2016年7月27日

@author: zqh
'''
from datetime import datetime
import json

from _loader._base import mainconf
from _loader._base.mainhelper import ftlog


def assertMustDef(d, k):
    if k not in d:
        raise Exception('must define key of :' + str(k) + ' in ' + json.dumps(d))
    return d[k]


def assertMustStr(d, k):
    assertMustDef(d, k)
    if not isinstance(d[k], (str, unicode)):
        raise Exception('the key ' + str(k) + '\'s value must be string in ' + json.dumps(d))
    return d[k]


def assertMustHttp(d, k):
    assertMustDef(d, k)
    if not isinstance(d[k], (str, unicode)):
        raise Exception('the key ' + str(k) + '\'s value must be string in ' + json.dumps(d))
    if not (d[k].find('http://') == 0 or d[k].find('https://') == 0):
        raise Exception('the key ' + str(k) + '\'s value must be http://xxx format in ' + json.dumps(d))
    return d[k]


def assertMustResource(d, k):
    v = assertMustStr(d, k)
    if v.find('http://') == 0:
        return v
    if v.find('/') == 0:
        return v
    if v.find('${http_') == 0:
        return v
    raise Exception('the key ' + str(k) + '\'s value must be resource format in ' + json.dumps(d))


def assertMustInt(d, k):
    assertMustDef(d, k)
    if not isinstance(d[k], int):
        raise Exception('the key ' + str(k) + '\'s value must be integer in ' + json.dumps(d))
    return d[k]


def assertMustIntLarge(d, k, smallInt):
    assertMustDef(d, k)
    if not isinstance(d[k], int):
        raise Exception('the key ' + str(k) + '\'s value must be integer in ' + json.dumps(d))
    if d[k] <= smallInt:
        raise Exception('the key ' + str(k) + '\'s value must be large than ' + str(smallInt) + ' in ' + json.dumps(d))
    return d[k]


def assetDateTimeStr(d, k, dformat='%Y-%m-%d %H:%M:%S'):
    assertMustStr(d, k)
    try:
        datetime.strptime(d[k], dformat)
    except:
        raise Exception('the key ' + str(k) + '\'s value must be datetime format ' + dformat + ' in ' + json.dumps(d))
    return d[k]


NOT_DATE_TIME = datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def assetDateTimeLarge(d, kBig, kSmall, dformat='%Y-%m-%d %H:%M:%S'):
    assertMustStr(d, kBig)
    assertMustStr(d, kSmall)
    try:
        datetime.strptime(d[kBig], dformat)
    except:
        raise Exception('the key ' + str(kBig) + '\'s value must be datetime format ' + dformat + ' in ' + json.dumps(d))
    try:
        datetime.strptime(d[kSmall], dformat)
    except:
        raise Exception('the key ' + str(kSmall) + '\'s value must be datetime format ' + dformat + ' in ' + json.dumps(d))
    if d[kBig] <= d[kSmall]:
        raise Exception('the key ' + str(kBig) + '\'s value must large than ' + str(kSmall) + ' in ' + json.dumps(d))
#     if d[kBig] < NOT_DATE_TIME:
#         ftlog.info('WARRN !! the big datetime is out of time ' + d[kBig] + ' in ' + json.dumps(d))
    return d[kBig], d[kSmall]


def assertIntUuid(d, k, idSet):
    assertMustInt(d, k)
    if d[k] not in idSet:
        idSet.add(d[k])
    else:
        raise Exception('the int uuid ' + str(k) + '=' + str(d[k]) + ' is already defined in ' + json.dumps(d))
    return d[k]


def assertStrUuid(d, k, idSet):
    assertMustStr(d, k)
    if d[k] not in idSet:
        idSet.add(d[k])
    else:
        raise Exception('the int uuid ' + str(k) + '=' + str(d[k]) + ' is already defined in ' + json.dumps(d))
    return d[k]


def assertIdSet(d, k, idSet):
    assertMustInt(d, k)
    if d[k] not in idSet:
        idSet.add(d[k])
    else:
        raise Exception('the id ' + str(k) + '=' + str(d[k]) + ' is already defined in ' + json.dumps(d))
    return d[k]


def assertEnumValue(d, k, enumList):
    assertMustDef(d, k)
    if d[k] not in enumList:
        raise Exception('the enum value ' + str(k) + '=' + str(d[k]) + ' not in emun ' + json.dumps(enumList) + ' in ' + json.dumps(d))
    return d[k]


def assertInEnum(v, enumList):
    if v not in enumList:
        raise Exception('the enum value ' + str(v) + ' not in emun ' + json.dumps(enumList))
    return v


def assertListOrNone(d, k, assertFun=None, argl=[]):
    if k in d:
        if not isinstance(d[k], list):
            raise Exception('the key ' + str(k) + '\'s value must be array list in ' + json.dumps(d))
        else:
            dlist = d[k]
            if assertFun:
                for x in dlist:
                    assertFun(x, *argl)
            return dlist
    return None


def assertMustList(d, k, assertFun=None, argl=[]):
    if k not in d or not isinstance(d[k], list):
        raise Exception('the key ' + str(k) + '\'s value must be array list in ' + json.dumps(d))
    else:
        dlist = d[k]
        if assertFun:
            for x in xrange(len(dlist)):
                assertFun(dlist[x], *argl)
        return dlist


def assertMustDict(d, k, assertFun=None, argl=[]):
    if k not in d or not isinstance(d[k], dict):
        raise Exception('the key ' + str(k) + '\'s value must be dict in ' + json.dumps(d))
    else:
        ddict = d[k]
        if assertFun:
            for k, v in ddict.items():
                assertFun(k, v, *argl)
        return ddict


def assertMustDictOrNone(d, k, assertFun=None, argl=[]):
    if k in d:
        if isinstance(d[k], dict):
            ddict = d[k]
            if assertFun:
                for k, v in ddict.items():
                    assertFun(k, v, *argl)
            return ddict
        else:
            raise Exception('the key ' + str(k) + '\'s value must be dict in ' + json.dumps(d))
    else:
        return None


def assertValueMustDict(k, v, assertFun=None, argl=[]):
    if not isinstance(v, dict):
        raise Exception('the key ' + str(k) + '\'s value must be dict, value=' + str(v))
    if assertFun:
        for k1, v1 in v.items():
            assertFun(k1, v1, *argl)
    return v


def assertDictMustKeys(d, keys):
    s1 = set(d.keys())
    s2 = set(keys)
    ls = s1 - s2
    if ls:
        raise Exception('the key ' + json.dumps(list(ls)) + ' can not define in ' + json.dumps(d))
    rs = s2 - s1
    if rs:
        raise Exception('the key ' + json.dumps(list(rs)) + ' must define in ' + json.dumps(d))


def assertDictMustMaybeKeys(d, mustKeys, maybeKeys):
    s1 = set(d.keys())
    s2 = set(mustKeys)
    s3 = set(maybeKeys)
    ls = s1 - s2 - s3
    if ls:
        raise Exception('the key ' + json.dumps(list(ls)) + ' can not define in ' + json.dumps(d))
    rs = s2 - s1
    if rs:
        raise Exception('the key ' + json.dumps(list(rs)) + ' must define in ' + json.dumps(d))


def assertVcRefence(tcDatas, vcDatas):
    tdict = {}
    tmps = tcDatas.get('templates', {})
    if isinstance(tmps, list):
        for v in tmps:
            tdict[int(v['id'])] = v
    else:
        for k, v in tmps.items():
            tdict[int(k)] = v
    
    cs = mainconf.CLIENTIDS_INT
    for c, t in vcDatas.items():
        if not c in cs:
            # raise Exception('the clientid ' + str(c) + ' is undefined')
            ftlog.info('ERROR the clientid ' + str(c) + ' is undefined')
        if not t in tdict:
            #raise Exception('the template ' + str(t) + ' is undefined')
            ftlog.info('ERROR the template clientid=' + str(c) + ' templateId=' + repr(t) + ' is undefined')
    return tdict
