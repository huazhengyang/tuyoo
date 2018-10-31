# -*- coding:utf-8 -*-
'''
Created on 2016年12月12日

@author: zhaojiangang
'''
from dizhu.entity import tableskin
from freetime.entity.msg import MsgPack
from hall.servers.common.base_checker import BaseMsgPackChecker
from poker.entity.biz.exceptions import TYBizException
from poker.protocol import router
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod
import freetime.util.log as ftlog

@markCmdActionHandler
class TableSkinTcpHandler(BaseMsgPackChecker):
    def _check_param_skinId(self, msg, key, params):
        skinId = msg.getParam(key)
        try:
            int(skinId)
            return None, skinId
        except:
            return 'ERROR of skinId !' + str(skinId), None
    
    def _check_param_version(self, msg, key, params):
        version = msg.getParam(key)
        if not isinstance(version, int):
            return 'ERROR of version !' + str(version), None
        return None, version
    
    @markCmdActionMethod(cmd='dizhu', action='table_skin_conf', clientIdVer=0, scope='game')
    def doTableSkinConf(self, userId, gameId, clientId, version):
        # 根据clientId过滤返回给用户哪些skin
        return self._doTableSkinConf(userId, gameId, clientId, version)
    
    @markCmdActionMethod(cmd='dizhu', action='table_skin_mine', clientIdVer=0, scope='game')
    def doTableSkinMine(self, userId, gameId, clientId):
        # 根据clientId过滤返回给用户哪些skin
        return self._doTableSkinMine(userId, gameId, clientId)
    
    @markCmdActionMethod(cmd='dizhu', action='table_skin_use', clientIdVer=0, scope='game')
    def doTableSkinUse(self, userId, gameId, clientId, version, skinId):
        # 根据clientId过滤返回给用户哪些skin
        return self._doTableSkinUse(userId, gameId, clientId, version, skinId)
    
    @markCmdActionMethod(cmd='dizhu', action='table_skin_buy', clientIdVer=0, scope='game')
    def doTableSkinBuy(self, userId, gameId, clientId, version, skinId):
        # 根据clientId过滤返回给用户哪些skin
        return self._doTableSkinBuy(userId, gameId, clientId, version, skinId)
    
    @classmethod
    def encodeFeeItem(cls, feeItem):
        return {
            'itemId':feeItem.itemId,
            'count':feeItem.count,
            'img':feeItem.pic,
            'desc':feeItem.desc
        }

    @classmethod
    def encodeSkin(cls, skin):
        ret = {
            'id':skin.skinId,
            'name':skin.name,
            'type':skin.type,
            'display':skin.displayName,
            'update':skin.updateVersion,
            'icon':skin.icon,
            'preview':skin.preview,
            'url':skin.url,
            'md5':skin.md5
        }
        if skin.feeItem:
            ret['fee'] = cls.encodeFeeItem(skin.feeItem)
        return ret
    
    @classmethod
    def encodeSkins(cls, skins):
        ret = []
        for skin in skins:
            ret.append(cls.encodeSkin(skin))
        return ret
    
    @classmethod
    def _doTableSkinConf(cls, userId, gameId, clientId, version):
        skins = tableskin.getClientSkins(userId, clientId, version)
        mo = MsgPack()
        mo.setCmd('dizhu')
        mo.setResult('action', 'table_skin_conf')
        mo.setResult('version', version)
        mo.setResult('skins', cls.encodeSkins(skins))
        router.sendToUser(mo, userId)
        return mo

    @classmethod
    def _doTableSkinMine(cls, userId, gameId, clientId):
        mySkin = tableskin.loadMyVIPSkin(userId, clientId)
        #mySkin = tableskin.loadMySkin(userId)
        mo = MsgPack()
        mo.setCmd('dizhu')
        mo.setResult('action', 'table_skin_mine')
        if mySkin.curSkin:
            mo.setResult('curSkin', mySkin.curSkin)
        if mySkin.mySkins:
            mo.setResult('skins', list(mySkin.mySkins))
        router.sendToUser(mo, userId)
        if ftlog.is_debug():
            ftlog.debug('_doTableSkinMine userId=', userId,
                        'clientId=', clientId,
                        'mo=', mo)
        return mo
    
    @classmethod
    def _doTableSkinUse(cls, userId, gameId, clientId, version, skinId):
        mo = MsgPack()
        mo.setCmd('dizhu')
        mo.setResult('action', 'table_skin_use')
        mo.setResult('skinId', skinId)
        try:
            tableskin.useSkin(userId, clientId, version, skinId)
            mo.setResult('code', 0)
        except TYBizException, e:
            mo.setResult('code', e.errorCode)
            mo.setResult('info', e.message)
        router.sendToUser(mo, userId)
        if ftlog.is_debug():
            ftlog.debug('_doTableSkinUse userId=', userId,
                        'clientId=', clientId,
                        'version=', version,
                        'skinId=', skinId,
                        'mo=', mo)
        return mo

    @classmethod
    def _doTableSkinBuy(cls, userId, gameId, clientId, version, skinId):
        mo = MsgPack()
        mo.setCmd('dizhu')
        mo.setResult('action', 'table_skin_buy')
        mo.setResult('skinId', skinId)
        try:
            tableskin.buySkin(userId, clientId, version, skinId)
            mo.setResult('code', 0)
        except TYBizException, e:
            mo.setResult('code', e.errorCode)
            mo.setResult('info', e.message)

        if ftlog.is_debug():
            ftlog.debug('_doTableSkinBuy userId=', userId,
                        'clientId=', clientId,
                        'version=', version,
                        'skinId=', skinId,
                        'mo=', mo)
        router.sendToUser(mo, userId)
        return mo


