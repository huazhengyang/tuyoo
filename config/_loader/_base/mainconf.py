# -*- coding: utf-8 -*-
'''
Created on 2016年7月27日

@author: zqh
'''
from copy import deepcopy
import json
import os
import re

from _loader._base import mainhelper, ignoreclientid


GAMEIDS = []  # 所有配置目录下的gameid列表，按大小排序
ENVS = {}  # 配置系统提供的环境变量
CLIENTIDS = {}  # 全体CLIENTID的配置集合 str-int
CLIENTIDS_INT = {}  # 全体CLIENTID的配置集合 int-str
CLITNEIDS_INT_GAMEID = {}
CLITNEIDS_INT_SYS = {}
PRODUCTIDS = {}  # 全体PRODUCT的ID配置集合 str-int
PRODUCTIDS_INT = {}  # 全体PRODUCT的ID配置集合 int-str

OUT_STATIC = {}
OUT_REDIS = {}


def init(configPath):
    if GAMEIDS:
        return

    def getGameIdFromHallClientId(clientId):
        try:
            gid = re.match('^.*-hall(\\d+).*$', clientId).group(1)
            return int(gid)
        except:
            # ftlog.info('WARRING clientId format error !' + str(clientId))
            return 0

    def getClientSys(clientId):
        clientsys = clientId[0]
        if clientsys == 'W' or clientsys == 'w':
            clientsys = 'winpc'
        elif clientsys == 'I' or clientsys == 'i':
            clientsys = 'ios'
        elif clientsys == 'H' or clientsys == 'h':
            clientsys = 'h5'
        elif clientsys == 'M' or clientsys == 'm':
            clientsys = 'mac'
        else:
            clientsys = 'android'
        return clientsys

    global CLIENTIDS,  PRODUCTIDS
    CLIENTIDS,  PRODUCTIDS = mainhelper.getGdssDatas()
    for k, v in PRODUCTIDS.items():
        PRODUCTIDS_INT[str(v)] = k

    for k, v in CLIENTIDS.items():
        v = str(v)
        if k in ignoreclientid.IGNORE_CLIENTS :
            print 'pass ->', k
            continue
        CLIENTIDS_INT[v] = k
        CLITNEIDS_INT_GAMEID[v] = getGameIdFromHallClientId(k)
        CLITNEIDS_INT_SYS[v] = getClientSys(k)

    print 'CONFIGURE PATH:', configPath
    for gds in os.listdir(configPath):
        if gds[0] == '.':
            continue
        try:
            GAMEIDS.append(int(gds))
        except:
            continue
    GAMEIDS.sort()
    print 'CONFIGURE GAMEIDS:', GAMEIDS

    http_download = os.environ.get('http_download')
    if not http_download:
        http_download = 'http://ddz.dl.tuyoo.com/cdn37'
    http_game = os.environ.get('http_game')
    if not http_game:
        http_game = 'http://open.touch4.me'

    ENVS['${http_download}'] = http_download
    ENVS['${http_game}'] = http_game


class TcVcModule():

    def __init__(self, gameId, baseKey, vcDatas, tcDatas):
        self.gameId = gameId
        self.baseKey = baseKey
        self.vcKey = baseKey + 'vc'
        self.tcKey = baseKey + 'tc'
        self.vcDatas = vcDatas
        self.tcDatas = tcDatas
        self.module = baseKey.split(':')[-2]

    def __str__(self):
        return 'TcVcModule: baseKey=' + str(self.baseKey) + \
            ' vcDatas=' + json.dumps(self.vcDatas) + ' tcDatas=' + json.dumps(self.tcDatas)

    def __repr__(self):
        return str(self)

    def writeOut(self, outPath):
        outGamePath = outPath + '/' + str(self.gameId) + '/' + self.module
        if not os.path.exists(outGamePath):
            os.makedirs(outGamePath)
        mainhelper.writeJsonFile(outGamePath + '/tc.json', self.tcDatas)
        mainhelper.writeJsonFile(outGamePath + '/vc.json', self.vcDatas)


class JsonDataModule():

    def __init__(self, gameId, baseKey):
        self.gameId = gameId
        self.baseKey = baseKey
        self.datas = {}

    def __str__(self):
        return 'JsonDataModule: gameId=' + str(self.gameId) + ' baseKey=' + str(self.baseKey) + \
            ' datas=' + json.dumps(self.datas)

    def __repr__(self):
        return str(self)


def getGameDatas(basefile, replaceEvn=1):
    '''
    读取当前游戏下的对应的所有的json的数据信息
    返回 TcVcModule实例
    '''
    gameId, pdir, _pathf, key, _keyf = mainhelper.getPathInfo(basefile)
    print 'READ GAME', pdir
    jdata = JsonDataModule(gameId, key)
    sfs = os.listdir(pdir)
    for f in sfs:
        rkey, datas = mainhelper.readJsonData(pdir, f, 1, replaceEvn)
        if rkey:
            jdata.datas[rkey] = datas
    return jdata


def getTcVcDatasOne(basefile, replaceEvn=1):
    '''
    读取当前游戏下的对应的vc、tc的数据信息
    返回 TcVcModule实例
    '''
    gameId, pdir, _pathf, key, _keyf = mainhelper.getPathInfo(basefile)
    print 'READ GAME', pdir
    tc = mainhelper.readJsonFile(pdir + '/tc.json', replaceEvn)
    vc = mainhelper.readJsonFile(pdir + '/vc.json', replaceEvn)
    cm = TcVcModule(gameId, key, vc, tc)
    return cm


def getTcVcDatasAll(basefile, replaceEvn=1):
    '''
    读取当所有游戏下同名的配置模块下的所有的vc、tc、sc的数据信息
    返回 TcVcModule实例的集合
    '''
    print basefile
    cmlist = []
    _gameId, _pdir, pathf, _key, _keyf = mainhelper.getPathInfo(basefile)
    print 'READ ALL', pathf
    for gid in GAMEIDS:
        fpath = pathf % (gid)
        print 'READ GAME', fpath
        tc = mainhelper.readJsonFile(fpath + '/tc.json', replaceEvn)
        vc = mainhelper.readJsonFile(fpath + '/vc.json', replaceEvn)
        cm = TcVcModule(gid, _keyf % (gid),  vc, tc)
        cmlist.append(cm)
    return cmlist


def getTcDatasAll(basefile, replaceEvn=1):
    '''
    读取当所有游戏下同名的配置模块下的所有的tc的数据信息
    返回 TcVcModule实例的集合
    '''
    cmlist = []
    _gameId, _pdir, pathf, _key, _keyf = mainhelper.getPathInfo(basefile)
    print 'READ ALL', pathf
    for gid in GAMEIDS:
        fpath = pathf % (gid)
        print 'READ GAME', fpath
        tc = mainhelper.readJsonFile(fpath + '/tc.json', replaceEvn)
        cm = TcVcModule(gid, _keyf % (gid),  None, tc, None)
        cmlist.append(cm)
    return cmlist


def meargeCmModules(cmlist):
    '''
    合并cmlist中的所有的TcVcModule的vcDatas和tcDatas到一个新的TcVcModule
    返回：合并后的TcVcModule实例, 其tcKey和vcKey使用cmlist[-1]对象的值
    '''
    vdatas = {}
    tdatas = {}
    for cm in cmlist:
        if cm.tcDatas:
            for k, v in cm.tcDatas.items():
                if not k in tdatas:
                    tdatas[k] = deepcopy(v)
                else:
                    if isinstance(v, dict):
                        tdatas[k].update(deepcopy(v))
                    elif isinstance(v, list):
                        tdatas[k].extend(deepcopy(v))
                    else:
                        tdatas[k] = deepcopy(v)

        if cm.vcDatas:
            vdatas.update(deepcopy(cm.vcDatas))

    cm = TcVcModule(cmlist[-1].gameId, cmlist[-1].baseKey,  vdatas, tdatas)
    return cm


def removeUnUsedTemplates(cmlist):
    actuals = {}  # 1：1的模板对应表 clientId <-> templateName
    cmgids = {}  # gameId对应的cm对象  gameId <-> TcVcModule
    defaults = {}  # 缺省的模板对应 gameId <-> { "deftult" : "templateName"}
    errCount = 0
    convertList = 0
    for cm in cmlist:
        if 'templates' not in cm.tcDatas:
            cm.tcDatas['templates'] = {}
        if 'actual' not in cm.vcDatas:
            cm.vcDatas['actual'] = {}

        if isinstance(cm.tcDatas['templates'], list):
            convertList = 1
            ntemps = {}
            for t in cm.tcDatas['templates']:
                ntemps[t['name']] = t
            cm.tcDatas['templates'] = ntemps
        # 补丁，有些模板使用的key和name值不一致
        for k, v in cm.tcDatas['templates'].items() :
            v['name'] = k

        actuals.update(cm.vcDatas['actual'])

        defaults[cm.gameId] = {}
        for k, v in cm.vcDatas.items():
            if k != 'actual':
                defaults[cm.gameId][k] = v
        cm.vcDatas['actual'] = {}
        cm.usedTemplate = set()
        cmgids[cm.gameId] = cm

    # 检查、更新clientId<->模板名称的对应关系
    ciall = set(CLIENTIDS_INT.keys())
    for ci in ciall:
        gid = CLITNEIDS_INT_GAMEID[ci]
        cm = cmgids.get(gid)
        if cm:
            templates = cm.tcDatas['templates']
            tnameActual = actuals.get(ci)
            if tnameActual and tnameActual not in templates:
                print 'MATCH ERROR 1, template name not Found [', tnameActual, '], gameId=', gid, 'clinetId=', ci, CLIENTIDS_INT[ci]
                tnameActual = None
                errCount += 1

            # 使用缺省系统的模板
            tnameDefaultOs = defaults[gid].get('default_' + CLITNEIDS_INT_SYS[ci])
            if tnameDefaultOs and tnameDefaultOs not in templates:
                print 'MATCH ERROR 2, template name not Found [', tnameDefaultOs, '], gameId=', gid, 'clinetId=', ci, CLIENTIDS_INT[ci]
                tnameDefaultOs = None
                errCount += 1

            # 使用缺省系统的模板
            tnameDefault = defaults[gid].get('default')
            if tnameDefault and tnameDefault not in templates:
                print 'MATCH ERROR 3, template name not Found [', tnameDefault, '], gameId=', gid, 'clinetId=', ci, CLIENTIDS_INT[ci]
                tnameDefault = None
                errCount += 1

            if tnameActual:
                if tnameActual != tnameDefaultOs and tnameActual != tnameDefault:
                    cm.vcDatas['actual'][ci] = tnameActual
                    cm.usedTemplate.add(tnameActual)
                    # print 'MATCH ACTUAL, gameId=', gid, 'clinetId=', ci, 'template=', tnameActual
                elif tnameDefaultOs is None and tnameDefault is None:
                    print 'MATCH ERROR 4, gameId=', gid, 'clinetId=', ci, CLIENTIDS_INT[ci]
                    errCount += 1
        else:
            print 'MATCH ERROR 5, template name not Found [ None ], gameId=', gid, 'clinetId=', ci, CLIENTIDS_INT[ci]
            errCount += 1
    # 删除无效的模板
    for cm in cmlist:
        for k in cm.tcDatas['templates'].keys():
            if k not in cm.usedTemplate:
                print 'DELETE UNUSED TEMPLATE:', cm.gameId, k
                del cm.tcDatas['templates'][k]
    # 若原始模板为列表，那么恢复数据格式
    if convertList:
        for cm in cmlist:
            cm.tcDatas['templates'] = cm.tcDatas['templates'].values()
            cm.tcDatas['templates'].sort(key=lambda x: x['name'])
    print 'TOTAL CLINETID COUNT=%s, ERROR COUNT=%s, OK PERCENT %0.2f' % (len(CLIENTIDS_INT), errCount, (100 - 100.0 * errCount / len(CLIENTIDS_INT)))
