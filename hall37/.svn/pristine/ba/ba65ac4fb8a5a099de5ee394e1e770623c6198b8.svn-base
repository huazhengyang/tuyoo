# -*- coding=utf-8
'''
Created on 2016年3月1日

@author: wuyongsheng
'''
from hall.entity import hallconf,hallitem
import freetime.util.log as ftlog
from poker.entity.biz.exceptions import TYBizConfException
from sre_compile import isstring
import poker.util.timestamp as pktimestamp

def getConf(userId,gameId,clientId):
    _skinsConf = hallconf.getCustomSkinsConf()
    skinsTemplate =  _skinsConf.get('templates',{})
    if ftlog.is_debug() :
        ftlog.debug('customSkins conf =', skinsTemplate.get('default',{}))
    result = decodeConf(userId,gameId,clientId,skinsTemplate.get('default',{}))
    return result
def decodeConf(userId,gameId,clientId,template):
    skinArr = template.get('skins',[])
    skinsArr = []
    for d in skinArr:
        ftlog.debug('decodeConf skin =', d)
        skinObj = HallSkins()
        skinObj.decodeFromDict(d)
        skinObj.checkIsDownload(userId,gameId)
        ftlog.debug('decodeConf skinObj skin =', skinObj.ObjtoDict())
        skinsArr.append(skinObj.ObjtoDict())
    return {
                "clientVersion":template.get('clientVersion',''),
                "skins":skinsArr
            }
class HallSkins(object):
    def __init__(self):
        self.name = None
        self.icon_url = None
        self.skin_url = None
        self.dirName = None
        self.fileType = None
        self.skin_md5 = None
        self.skins_Desc = None
        self.isDownload = None
        self.skins_name = None
    def decodeFromDict(self, skinObj):
        self.name = skinObj.get('name', '')
        if not isstring(self.name):
            raise TYBizConfException(skinObj, 'HallSkins.name must be string')
        self.icon_url = skinObj.get('icon_url', '')
        self.skin_url = skinObj.get('skin_url', '')
        self.dirName = skinObj.get('dirName', '')
        self.fileType = skinObj.get('fileType', '')
        self.skin_md5 = skinObj.get('skin_md5', '')
        self.skins_Desc = skinObj.get('skins_Desc', '')
        self.isDownload = skinObj.get('isDownload') or False
        self.skins_name = skinObj.get('skins_name', '')
        
    def ObjtoDict(self):
        obj = {}
        obj['name'] = self.name
        obj['icon_url'] = self.icon_url
        obj['skin_url'] = self.skin_url
        obj['dirName'] = self.dirName
        obj['fileType'] = self.fileType
        obj['skin_md5'] = self.skin_md5
        obj['skins_Desc'] = self.skins_Desc
        obj['isDownload'] = self.isDownload
        obj['skins_name'] = self.skins_name
        return obj
    
    def checkIsDownload(self,userId,gameId):
        userAssets = hallitem.itemSystem.loadUserAssets(userId)
        timestamp = pktimestamp.getCurrentTimestamp()
        cardNum = userAssets.balance(gameId,hallitem.ASSET_ITEM_CUSTOM_SKIN_CARD_ID,timestamp)
        if cardNum > 0:
            #存在换肤卡
            self.isDownload = True
        else:
            #不存在换肤卡
            self.isDownload = False
        self.isDownload = True