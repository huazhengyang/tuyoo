# -*- coding=utf-8
'''
Created on 2015年8月4日

@author: zhaojiangang
'''

from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from hall.entity import hallversionmgr, hallconf, hall_third_sdk_switch
from hall.servers.common.base_http_checker import BaseHttpMsgChecker
from poker.entity.configure import gdata, pokerconf, configure
from poker.protocol import runhttp
from poker.protocol.decorator import markHttpHandler, markHttpMethod
from poker.util import strutil
import random
from poker.entity.dao import sessiondata


class HelloTuyou(object):

    @classmethod
    def getNiCaiCode(cls, mo, nicaiCode):
        nicaiCodeEncoded = strutil.tyDesEncode(nicaiCode)
        mo.setResult('nicaiCode', nicaiCodeEncoded)

    @classmethod
    def getThirdSwitches(cls, mo, clientId):
        switches = hall_third_sdk_switch.queryThirdSDKSwitch(clientId)
        if ftlog.is_debug():
            ftlog.debug('HelloTuyou.getThirdSwitches switches:', switches)
        mo.setResult('thirdSwitches', switches)

    @classmethod
    def getUpdataInfo(cls, mo, gameId, clientId, updateVersion, alphaVersion):
        ftlog.debug('doGetUpdataInfo', gameId, clientId, updateVersion, alphaVersion)

        # 获取增量更新信息
        incUpdateInfo = hallversionmgr.getIncUpdateVersion(gameId, clientId, updateVersion)
        incUpdateWeight = 0
        if incUpdateInfo:
            ftlog.debug('incUpdateInfo', incUpdateInfo)
            incUpdateWeight = cls._getUpdateWeight('inc', incUpdateInfo._force)

        # 获取全量更新信息
        fullUpdateWeight = 0
        fullUpdateInfoArr = hallversionmgr.getFullUpdateInfo(gameId, clientId)
        fullUpdateInfo = {}
        if fullUpdateInfoArr != None and isinstance(fullUpdateInfoArr, list):
            # alphaVersion表示要升级的alpha包的版本号
            alphaKey = 'alphaVersion'
            # 先选择合适的alpha更新版本
            for fu in fullUpdateInfoArr:
                ftlog.debug('fullUpdateInfo->', fu)
                if alphaKey in fu:
                    if (fu[alphaKey] != 0) and (fu[alphaKey] != int(alphaVersion)):
                        fullUpdateInfo = fu
                else:
                    fullUpdateInfo = fu

            ftlog.debug('fullUpdateInfo', fullUpdateInfo)
            if 'force' in fullUpdateInfo:
                fullUpdateWeight = cls._getUpdateWeight('apk', fullUpdateInfo['force'])

        # 获取差分更新信息
        diffUpdateInfo = {}
        diffUpdateWeight = 0
        diffUpdateInfoArr = hallversionmgr.getDiffUpdateInfo(gameId, clientId)
        if diffUpdateInfoArr != None and isinstance(diffUpdateInfoArr, list):
            alphaKey = 'alphaVersion'
            # 先选择合适的alpha更新版本
            for du in diffUpdateInfoArr:
                if alphaKey in du:
                    ftlog.debug('alphaVersion', du[alphaKey])
                    if (du[alphaKey] != 0) and (du[alphaKey] > int(alphaVersion)):
                        diffUpdateInfo = du
                else:
                    diffUpdateInfo = du

            ftlog.debug('diffUpdateInfo', diffUpdateInfo)
            if 'force' in diffUpdateInfo:
                diffUpdateWeight = cls._getUpdateWeight('diff', diffUpdateInfo['force'])

        # 根据权重计算当前发送哪个更新
        ftlog.debug('incUpdateWeight:', incUpdateWeight, ' and fullUpdateWeight:', fullUpdateWeight, ' and diffUpdateWeight:', diffUpdateWeight)

        if ((incUpdateWeight > fullUpdateWeight) and (incUpdateWeight > diffUpdateWeight)):
            resUpdate = {}
            resUpdate['updateVersion'] = incUpdateInfo._id
            if incUpdateInfo._force == '1':
                resUpdate['updateType'] = 'force'
            else:
                resUpdate['updateType'] = 'optional'
            resUpdate['updateSize'] = incUpdateInfo._size
            resUpdate['updateUrl'] = incUpdateInfo._path
            resUpdate['updateDes'] = incUpdateInfo._des
            resUpdate['MD5'] = incUpdateInfo._md5
            resUpdate['fileType'] = 'zip'
            resUpdate['autoDownload'] = incUpdateInfo._autoDownloadCondition
            mo.setResult('resUpdate', resUpdate)
        elif((fullUpdateWeight > incUpdateWeight) and (fullUpdateWeight > diffUpdateWeight)):
            apkUpdate = {}
            if fullUpdateInfo['force'] == '1':
                apkUpdate['updateType'] = 'force'
            else:
                apkUpdate['updateType'] = 'optional'
            apkUpdate['updateSize'] = fullUpdateInfo['size']
            apkUpdate['updateUrl'] = fullUpdateInfo['path']
            apkUpdate['updateDes'] = fullUpdateInfo['des']
            apkUpdate['MD5'] = fullUpdateInfo['md5']
            apkUpdate['fileType'] = 'apk'
            apkUpdate['autoDownload'] = fullUpdateInfo['autoDownloadCondition']
            if 'updateAt' in fullUpdateInfo:
                apkUpdate['updateAt'] = fullUpdateInfo['updateAt']
            mo.setResult('apkUpdate', apkUpdate)
        elif((diffUpdateWeight > incUpdateWeight) and (diffUpdateWeight > fullUpdateWeight)):
            diffUpdate = {}
            if diffUpdateInfo['force'] == '1':
                diffUpdate['updateType'] = 'force'
            else:
                diffUpdate['updateType'] = 'optional'
            diffUpdate['updateSize'] = diffUpdateInfo['size']
            diffUpdate['updateUrl'] = diffUpdateInfo['path']
            diffUpdate['updateDes'] = diffUpdateInfo['des']
            diffUpdate['MD5'] = diffUpdateInfo['md5']
            diffUpdate['fileType'] = 'diff'
            diffUpdate['autoDownload'] = diffUpdateInfo['autoDownloadCondition']
            if 'updateAt' in diffUpdateInfo:
                diffUpdate['updateAt'] = diffUpdateInfo['updateAt']
            mo.setResult('diffUpdate', diffUpdate)

        return mo

    @classmethod
    def _getUpdateWeight(cls, updateType, updateStyle):
        '''
        0 - optional
        1 - force
        '''
        weights = {}
        weights['inc'] = {}
        weights['inc']['0'] = 1
        weights['inc']['1'] = 10
        weights['apk'] = {}
        weights['apk']['0'] = 5
        weights['apk']['1'] = 14
        weights['diff'] = {}
        weights['diff']['0'] = 3
        weights['diff']['1'] = 12

        if updateType not in weights:
            return 0

        if updateStyle not in weights[updateType]:
            return 0

        return weights[updateType][updateStyle]


@markHttpHandler
class HttpHelloTuyouHandler(BaseHttpMsgChecker):

    def _check_param_isTempVipUser(self, key, params):
        value = runhttp.getParamInt(key, 0)
        if value not in (0, 1):
            return 'param needRemove error', None
        return None, value

    @markHttpMethod(httppath='/hello')
    def doHelloTuyou(self):
        gameId = runhttp.getParamInt('gameId')
        clientId = runhttp.getParamStr('clientId', '')
        ftlog.debug('Hello->gameId=', gameId, 'clientId=', clientId)

        mo = MsgPack()
        mo.setCmd('hello')

        if gameId not in gdata.gameIds():
            mo.setError(1, 'gameId error !')
            ftlog.error('doHelloTuyou gameId error', runhttp.getDict())
            return mo

        try:
            clientIdInt = pokerconf.clientIdToNumber(clientId)
        except:
            clientIdInt = 0
            ftlog.error()

        if clientIdInt <= 0:
            mo.setError(2, 'clientId error !')
            ftlog.error('doHelloTuyou clientId error', runhttp.getDict())
            return mo

        nicaiCode = runhttp.getParamStr('nicaiCode', '')
        if not nicaiCode:
            mo.setError(3, 'nicai error !')
            ftlog.error('doHelloTuyou nicai error', runhttp.getDict())
            return mo
        # 1. 生存你猜CODE
        HelloTuyou.getNiCaiCode(mo, nicaiCode)

        # 2. 取得更新信息
        updateVersion = runhttp.getParamInt('updateVersion')
        alphaVersion = runhttp.getParamInt('alphaVersion', 0)
        HelloTuyou.getUpdataInfo(mo, gameId, clientId, updateVersion, alphaVersion)

        # 3. 静态配置文件的MD5和URL
        staticConf = hallconf.getUpgradeStaticConf()
        mo.updateResult(staticConf)

        # 4. 返回三方SDK的控制开关
        HelloTuyou.getThirdSwitches(mo, clientId)

        # 设置其他返回值
        mo.setResult('gameId', gameId)
        mo.setResult('clientId', clientId)

        return mo

    @markHttpMethod(httppath='/hellotcp')
    def doTcpPortTuyou(self):
        return _doTcpPortTuyou()


def _doTcpPortTuyou():
    mo = MsgPack()
    mo.setCmd('hellotcp')
    userId = runhttp.getParamInt('userId')
    nicaiCode = runhttp.getParamStr('nicaiCode', '')
    clientId = runhttp.getParamStr('clientId', '')
    if not nicaiCode:
        mo.setError(3, 'nicai error !')
        return mo
    if userId < 1:
        mo.setError(3, 'userId error !')
        return mo

    ftlog.debug('tcpport->userId=', userId, 'nicaiCode=', nicaiCode)
    HelloTuyou.getNiCaiCode(mo, nicaiCode)

    ip, port, wsport = getGaoFangIp2(userId, clientId)
    if not ip:
        ipports = gdata.getUserConnIpPortList()
        address = ipports[userId % len(ipports)]
        ip, port = getGaoFangIp(clientId, address[0], address[1])
        if len(address) > 2 :
            wsport = address[2]
    ftlog.info('doTcpPortTuyou->', userId, ip, port)
    mo.setResult('tcpsrv', {'ip': ip, 'port': port, 'wsport' : wsport})
    return mo


def getGaoFangIp(clientId, ip, port):
    try:
        _, cver, _ = strutil.parseClientId(clientId)
        gaofangConfs = configure.getJson('poker:map.gaofangip', None)
        if gaofangConfs:
            policy = gaofangConfs['policy']
            if policy == 'tuyou':
                ip = gaofangConfs[policy].get(ip, ip)

            elif policy == 'aligaofang':
                original = gaofangConfs['original']
                group = original[ip + ':' + str(port)]
                groupIps = gaofangConfs[policy][group]
                if groupIps:
                    ip = random.choice(groupIps)
            if cver >= 3.78:
                ip = gaofangConfs['namespace'][ip]
    except:
        ftlog.error()
    ftlog.info('getGaoFangIp->', ip, port, clientId)
    return ip, port


def getGaoFangIp2(userId, clientId):
    ip, port, wsport = '', 0, 0
    try:
        gaofangConfs = configure.getJson('poker:map.gaofangip.2', {})
        policy = gaofangConfs.get('policy')
        if policy == 'defence2':
            intClientId = sessiondata.getClientIdNum(userId, clientId)
            clientIds = gaofangConfs['clientIds']
            areaId = clientIds.get(intClientId)
            if not areaId:
                areaId = clientIds.get(str(intClientId))
                if not areaId:
                    areaId = clientIds.get('default')
                    if not areaId:
                        areaId = gaofangConfs['areas'].keys()[0]
                    ftlog.warn('ERROR, getGaoFangIp2 not found area id of ',
                               intClientId, clientId, 'use default !')
                clientIds[intClientId] = areaId
            entrys = gaofangConfs['areas'][areaId]
            ipPorts = entrys[userId % len(entrys)] # 切换不同的端口接入
            ipPort = ipPorts[userId % len(ipPorts)] # 使用相对固定的IP地址接入
            ip, port = ipPort[0], ipPort[1]
            if len(ipPort) > 2 :
                wsport = ipPort[2]
    except:
        ftlog.error()
    ftlog.info('getGaoFangIp2->', ip, port, wsport, userId, clientId)
    return ip, port, wsport
