# -*- coding=utf-8 -*-

import freetime.util.log as ftlog
from hall.entity import hallconf
from poker.entity.biz.exceptions import TYBizException
from poker.entity.configure import pokerconf
from freetime.entity.msg import MsgPack


class Version(object):
    def __init__(self, _id, md5, size, path, des, force, autoDownloadCondition):
        self._id = _id
        self._md5 = md5
        self._size = size
        self._path = path
        self._des = des
        self._force = force
        self._autoDownloadCondition = autoDownloadCondition
        
    def generateToSave(self):
        return { 'id': self._id,
                 'md5': self._md5,
                 'size': self._size,
                 'path': self._path,
                 'force': self._force,
                 'des': self._des,
                 'autoDownloadCondition': self._autoDownloadCondition
                }
        
    def generateToManager(self):
        return self.generateToSave()
        
    @classmethod
    def generateFrom(cls, data):
        assert(isinstance(data, dict))
        if 'id' not in data:return None
        if 'md5' not in data: return None
        if 'path' not in data: return None
        if 'size' not in data: return None
        if 'force' not in data: return None
        if 'des' not in data: return None
        
        return cls(data['id'], data['md5'], data['size'], data['path'], data['des'], data['force'],
                   4 if "autoDownloadCondition" not in data else data["autoDownloadCondition"])

    def setMd5(self, md5):
        self._md5 = md5
        
    def setSize(self, size):
        self._size = size
        
    def setPath(self, path):
        self._path = path
        
    def setDes(self, des):
        self._des = des
    
    def setForce(self, force):
        self._force = force       
        
    def setAutoDownloadCondition(self, autoDownloadCondition):
        self._autoDownloadCondition = autoDownloadCondition       


class ClientVersions(object):
    def __init__(self, clientid):
        assert(clientid)
        self.__client = clientid
        self.__versions = []
    
    @property
    def clientId(self):
        return self.__client
    
    def generateToManager(self):
        versions = []
        for ver in self.__versions:
            versions.append(ver.generateToManager())
        return versions
    
    def generateToSave(self):
        versions = []
        for ver in self.__versions:
            versions.append(ver._id)
        return versions        
    
    def addVersion(self, version):
        assert(isinstance(version, Version))
        for oldver in self.__versions:
            if oldver._id == version._id:
                return False
        self.__versions.append(version)
    
    def remVersionById(self, _id):
        for index in xrange(len(self.__versions)):
            if self.__versions[index]._id == _id:
                del self.versions[index]
    
    def remVersionByUpver(self, updateversion):
        assert(updateversion > 0)
        if updateversion <= len(self.__versions):
            del self.__versions[updateversion - 1]
    
    def makeVersionChain(self, updateversion):
        if updateversion >= len(self.__versions):
            return []
        verchain = []
        for index in xrange(updateversion - 1, len(self.__versions)):
            verchain.append([index, self.__versions[index]._force])
        return verchain
    
    def makeNeedUpdateVersion(self, updateversion):
        ftlog.debug('makeNeedUpdateVersion', updateversion, len(self.__versions), self.__versions)
        
        if len(self.__versions) <= 0 or updateversion >= self.__versions[-1]._id:
            return None
        
        force = '0'
        for i in range(len(self.__versions) - 1, -1, -1):
            version = self.__versions[i]
            if version._id <= updateversion:
                break
            if version._force == '1':
                force = '1'
                break
        version = self.__versions[-1]
        return Version(version._id, version._md5, version._size, version._path,
                       version._des, force, version._autoDownloadCondition)       


# 提供服务的代码    
class CliToVersService(object):
        
    def __init__(self, gameId):
        self.__gameId = gameId
    
    def _generateFrom(self, intClientId, data):
        if not data :
            return None
        assert(isinstance(data, list))
        cliv = ClientVersions(intClientId)
        for verdata in data:
            ver = Version.generateFrom(verdata)
            if ver:
                cliv.addVersion(ver)
            else:
                raise TYBizException(-1, 'Bad version data:' + str(data))
        return cliv

    def getNeedUpdateVersion(self, clientId, updatever):
        intClientId = pokerconf.clientIdToNumber(clientId)
        load_data = hallconf.getUpgradeIncConf(self.__gameId, clientId)
        clv = self._generateFrom(intClientId, load_data)
        if clv :
            return clv.makeNeedUpdateVersion(updatever)       
        return None


def getIncUpdateVersion(gid, clientId, updatever):
    ctvs = CliToVersService(gid)
    return ctvs.getNeedUpdateVersion(clientId, updatever)


def getFullUpdateInfo(gameId, clientId):
    configData = hallconf.getUpgradeFullConf(gameId, clientId)
    return configData


def getDiffUpdateInfo(gameId, clientId):
    configData = hallconf.getUpgradeDiffConf(gameId, clientId)
    return configData
                        

def makeStaticMessage():
    staticConf = hallconf.getUpgradeStaticConf()
    mo = MsgPack()
    mo.setCmd('local_static')
    mo.updateResult(staticConf)
    return mo

