# -*- coding: utf-8 -*-
'''
Created on 2016年7月27日

@author: zqh
'''
import hashlib
import json
import os
import time
import urllib
import urllib2


TIMEFORMAT = '%Y-%m-%d %H:%M:%S.%f'


def md5digest(md5str):
    m = hashlib.md5()
    m.update(md5str)
    md5code = m.hexdigest()
    return md5code.lower()


def toHttpStr(data):
    if isinstance(data, (str, unicode)):
        data = urllib.quote(data)
    elif isinstance(data, dict):
        data = urllib.urlencode(data)
    elif isinstance(data, (list, tuple, int, float, bool)):
        data = urllib.quote(json.dumps(data))
    else:
        data = urllib.quote(str(data))
    return data


def doSyncQueryHttp(posturl, datadict=None):
    Headers = {'Content-type': 'application/x-www-form-urlencoded'}
    postData = None
    if datadict:
        postData = toHttpStr(datadict)
    request = urllib2.Request(url=posturl, data=postData, headers=Headers)
    response = urllib2.urlopen(request)
    if response != None:
        retstr = response.read()
        return retstr
    return None


def syncDataFromGdss(dataType, apiName):
    httpgdss = os.environ.get('http_gdss', 'http://gdss.touch4.me')
    print 'GDSS->', httpgdss,  apiName, dataType
    ct = int(time.time())
    sign = md5digest('gdss.touch4.me-api-' + str(ct) + '-gdss.touch4.me-api')
    posturl = '%s/?act=api.%s&time=%d&sign=%s' % (httpgdss, apiName, ct, sign)
    retstr = doSyncQueryHttp(posturl, {})
    datas = None
    try:
        datas = json.loads(retstr)
    except:
        pass
    if datas and isinstance(datas, dict):
        dictdata = datas.get('retmsg', None)
        if isinstance(dictdata, dataType) and len(dictdata) > 0:
            return dictdata
        else:
            raise Exception('ERROR, _syncDataFromGdss, datas not found, datas=%s' % datas)
    else:
        raise Exception('ERROR, _syncDataFromGdss, gdss return error, datas=%s' % datas)
    raise Exception('ERROR !! GDSS data get False ! Please Try Again !' + str(httpgdss) + ' ' + str(apiName))


def getGdssDatas():
    cids = syncDataFromGdss(dict, 'getClientIdDict')
    prodids = syncDataFromGdss(dict, 'getProductIdDict')
    return cids, prodids


def convertBaseFile(basefile, runfile):
    # ftlog.info('convertBaseFile->', basefile, runfile)
    if basefile:
        return basefile
    if runfile.find('/_loader/game_') >= 0:
        return runfile.replace('/_loader/game_', '/game/')
    if runfile.find('/_loader/poker/') >= 0:
        return runfile.replace('/_loader/poker/', '/poker/')
    if runfile.find('/_loader/') >= 0:
        return runfile.replace('/_loader/', '/game/')
    return runfile


def getPathInfo(basefile):
    '''
    获取当前文件所在配置模块的基本信息
    返回：tuple(
        9999,
        "/<proj>/game/9999/ads5",
        "/<proj>/game/%s/ads5",
        "game:9999:ads5:", 
        "game:%s:ads5:")
    '''
    if basefile.endswith('.py') or basefile.endswith('.pyc'):
        basefile = convertBaseFile(None, basefile)
    pdir = os.path.dirname(os.path.abspath(basefile))
    ppdir = os.path.dirname(pdir)
    pppdir = os.path.dirname(ppdir)
    key = os.path.basename(pppdir) + ':' + os.path.basename(ppdir) + ':' + os.path.basename(pdir) + ':'
    keyf = os.path.basename(pppdir) + ':%s:' + os.path.basename(pdir) + ':'
    pathf = pppdir + '/%s/' + os.path.basename(pdir)
    try:
        gameId = int(os.path.basename(ppdir))
    except:
        gameId = 0
    return gameId, pdir, pathf, key, keyf


def decodeObjUtf8(datas):
    '''
    遍历datas(list,dict), 将遇到的所有的字符串进行encode utf-8处理
    '''
    if isinstance(datas, dict):
        ndatas = {}
        for key, val in datas.items():
            if isinstance(key, unicode):
                key = key.encode('utf-8')
            ndatas[key] = decodeObjUtf8(val)
        return ndatas
    if isinstance(datas, list):
        ndatas = []
        for val in datas:
            ndatas.append(decodeObjUtf8(val))
        return ndatas
    if isinstance(datas, unicode):
        return datas.encode('utf-8')
    return datas


def writeJsonFile(fpath, datas, decodeUtf8=1):
    if decodeUtf8:
        datas = decodeObjUtf8(datas)
        datas = json.dumps(datas, indent=2, sort_keys=True, ensure_ascii=False)
    else:
        datas = json.dumps(datas, indent=2, sort_keys=True)
    fp = open(fpath, 'w+b')
    fp.write(datas)
    fp.close()


def readJsonFile(fpath, replaceEvn=1):
    if not os.path.isfile(fpath):
        print 'The File JSON Not Found', fpath
        return {}
    fp = open(fpath, 'r')
    sdata = fp.read()
    fp.close()
    if replaceEvn:
        from _loader._base.mainconf import ENVS
        for k, v in ENVS.items():
            sdata = sdata.replace(k, v)
    datas = json.loads(sdata)
    return datas


def readJsonData(jpath, jfile, keycount, replaceEvn=1):
    if jpath:
        jfullpath = os.path.normpath(jpath + '/' + jfile)
    else:
        jfullpath = os.path.normpath(jfile)
    if not jfullpath.endswith('.json'):
        # 忽律非json文件
        return None, None
    if jfullpath.find('.svn') > 0:
        # 忽律非svn文件
        return None, None
    if jfullpath.find(os.path.sep + '.') > 0:
        # 忽律隐藏文件
        return None, None
    if os.path.isfile(jfullpath):
        rkey = ':'.join(jfullpath.split(os.path.sep)[-keycount:])
        rkey = rkey[0:-5]
        print 'READ FILE ->', rkey, jfullpath
        data = readJsonFile(jfullpath, replaceEvn)
        return rkey, data
    return None, None


def invoke(mainfun, pyfile):
    from _loader._base import mainconf
    module = os.path.basename(os.path.dirname(pyfile))
    readPath = os.path.abspath(os.path.dirname(pyfile) + './../../../')
    mainconf.init(readPath + '/game')
    outPath = os.path.abspath(readPath + '/../out')
    mainfun(readPath + '/game/9999/' + module + '/tc.json', outPath, module)
