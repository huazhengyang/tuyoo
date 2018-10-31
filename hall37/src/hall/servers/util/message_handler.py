# -*- coding: utf-8 -*-
"""
Created on 2015年5月20日
@author: zqh
"""

from freetime.entity.msg import MsgPack
from hall.entity import hallitem, datachangenotify
from hall.servers.common.base_checker import BaseMsgPackChecker
from poker.entity.biz.item.item import TYAssetUtils
from poker.entity.biz.message import message
from poker.protocol import router
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod


@markCmdActionHandler
class MessageTcpHandler(BaseMsgPackChecker):
    def __init__(self):
        pass

    def _check_param_typeid(self, msg, key, params):
        typeid = msg.getParam(key)
        return None, typeid if typeid in message.MESSAGE_TYPES else message.MESSAGE_TYPE_SYSTEM

    def _check_param_msgid(self, msg, key, params):
        msgid = msg.getParam(key)
        if isinstance(msgid, int):
            return None, msgid
        return 'ERROR of msgid:{}'.format(msgid), None

    @markCmdActionMethod(cmd='message', action="list", clientIdVer=3.9)
    def do_message_list(self, userId, gameId, clientId, typeid):
        ret = message.get(userId, typeid)
        mo = MsgPack()
        mo.setCmd('message')
        mo.setResult('action', 'list')
        mo.setResult('gameId', gameId)
        mo.setResult('typeid', typeid)
        mo.setResult('readid', ret['readid'])
        mo.setResult('msgs', ret['list'])
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd='message', action="receive", clientIdVer=3.9)
    def do_message_receive(self, userId, gameId, clientId, typeid, msgid):
        ret = message.attachment_receive(userId, typeid, msgid, hallitem.itemSystem)
        if ret:
            changed = TYAssetUtils.getChangeDataNames(ret[1])
            changed.add('message')
            datachangenotify.sendDataChangeNotify(ret[0], userId, changed)


# =====================
# deprecated
# =====================

    def _check_param_pagenum(self, msg, key, params):
        pagenum = msg.getParam(key)
        if pagenum and isinstance(pagenum, int) and pagenum > 0:
            return None, pagenum
        return None, 1

    @markCmdActionMethod(cmd='message', action="list", clientIdVer=0)
    def doMessagePrivateUpdate1(self, userId, gameId, clientId, pagenum):
        self._doMessagePrivateUpdate(userId, gameId, clientId, pagenum)

    @markCmdActionMethod(cmd='message', action="private_update", clientIdVer=0)
    def doMessagePrivateUpdate2(self, userId, gameId, clientId, pagenum):
        self._doMessagePrivateUpdate(userId, gameId, clientId, pagenum)

    def _doMessagePrivateUpdate(self, userId, gameId, clientId, pagenum):
        total, msgs = self._getMessageForGames(userId)
        mo = MsgPack()
        mo.setCmd('message')
        mo.setResult('action', 'private_update')
        mo.setResult('gameId', gameId)
        mo.setResult('total', total)
        mo.setResult('msgs', msgs)
        mo.setResult('pagecount', message.MAX_SIZE)
        mo.setResult('pagenum', pagenum)
        router.sendToUser(mo, userId)

    def _getMessageForGames(self, userId):
        dict_sys = message.get(userId, message.MESSAGE_TYPE_SYSTEM)
        dict_pri = message.get(userId, message.MESSAGE_TYPE_PRIVATE)
        readid = max(dict_sys['readid'], dict_pri['readid'])
        newmsgs = dict_sys['list']
        newmsgs.extend(dict_pri['list'])
        msglist = []
        total = 0
        for msg in newmsgs:
            msgid = msg['id']
            # 模仿老版本数据结构。。。
            # {'id': maxid, 'from': fromUid, 'time': ct, 'msg': msg}
            msglist.append({'id': msgid, 'from': msg['from'], 'time': msg['time'], 'msg': msg['text']})
            if readid < msgid:
                total += 1
        msglist.sort(key=lambda item: item['time'], reverse=True)
        return total, msglist

    @markCmdActionMethod(cmd='message', action="global_update", clientIdVer=0)
    def doMessageUpdateGlobal(self, userId, gameId, clientId, pagenum):
        gameRet = message.getGlobal(gameId, userId, pagenum)
        if 'total' in gameRet:
            gameTotal = gameRet['total']
        else:
            gameTotal = 0
        mlist = []
        if 'list' in gameRet:
            mlist = gameRet['list']

        mo = MsgPack()
        mo.setCmd('message')
        mo.setResult('action', 'global_update')
        mo.setResult('gameId', gameId)
        mo.setResult('total', gameTotal)
        mo.setResult('msgs', mlist)
        mo.setResult('pagecount', 0)
        mo.setResult('pagenum', pagenum)
        router.sendToUser(mo, userId)
