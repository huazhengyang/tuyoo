# -*- coding=utf-8
'''
Created on 2015年8月19日

@author: zhaojiangang
'''

from freetime.entity.msg import MsgPack
from hall.entity import hallled
from hall.servers.common.base_http_checker import BaseHttpMsgChecker
import poker.entity.biz.message.message as pkmessage
from poker.entity.configure import gdata
from poker.protocol import runhttp, router
from poker.protocol.decorator import markHttpHandler, markHttpMethod
from hall.entity.todotask import TodoTaskShowInfo, TodoTaskHelper
import freetime.util.log as ftlog
from poker.util import strutil

@markHttpHandler
class HttpGameHandler(BaseHttpMsgChecker):
    def __init__(self):
        super(HttpGameHandler, self).__init__()

    def _check_param_appId(self, key, params):
        appId = runhttp.getParamInt(key, 0)
        if appId == 0:
            appId = runhttp.getParamInt('gameId', 0)
        if not appId in gdata.gameIds():
            return 'param appId error', None
        return None, appId
    
    def _check_param_message(self, key, params):
        value = runhttp.getParamStr(key, '')
        if not value :
            return 'param message error', None
        return None, value
    
    def _check_param_msg(self, key, params):
        value = runhttp.getParamStr(key, '')
        if not value :
            return 'param msg error', None
        return None, value
    
    def _check_param_authInfo(self, key, params):
        value = runhttp.getParamStr(key, '')
        if not value :
            return 'param authInfo error', None
        return None, value
    
    def _check_param_pageNo(self, key, params):
        value = runhttp.getParamInt(key, 1)
        if value <= 0:
            value = 1
        return None, value
    
    def _check_param_pageSize(self, key, params):
        value = runhttp.getParamInt(key, 20)
        if value <= 0:
            value = 20
        return None, value
    
    def _check_param_mtype(self, key, params):
        value = runhttp.getParamInt(key, 0)
        return None, value
    
    def _check_param_msgtype(self, key, params):
        value = runhttp.getParamInt(key, 0)
        return None, value
    
    def _check_param_toUid(self, key, params):
        value = runhttp.getParamInt(key, 0)
        return None, value
    
    def _check_param_fromUid(self, key, params):
        value = runhttp.getParamInt(key, 0)
        return None, value
    
    def _check_param_ismgr(self, key, params):
        value = runhttp.getParamInt(key, 1)
        return None, value
    
    def _check_param_scope(self, key, params):
        value = runhttp.getParamStr(key, 'hall')
        return None, value
    
    def _check_param_clientIds(self, key, params):
        ret = []
        try:
            jstr = runhttp.getParamStr(key)
            clientIdList = jstr.split('|')
            for clientId in clientIdList:
                ret.append(clientId)
        except:
            ret = []
        return None, ret
    
    @markHttpMethod(httppath='/v1/putmsg')
    def doPutMessage(self, gameId, fromUid, toUid, mtype, msg, ismgr, scope, clientIds):
        button = runhttp.getParamStr('button', None)
        button = strutil.loads(button, ignoreException=True)
        data = None
        mo = MsgPack()
        
        if mtype == 0 and len(msg) > 0 and toUid > 0 and gameId >= 0:
            # 发送私人消息
            # 必须参数 
            # 1）msg - 消息
            # 2）toUid - 接收消息的userId
            # 3）gameId
            data = pkmessage.sendPublic(gameId, toUid, fromUid, msg, button)
            #data = pkmessage.sendPrivate(gameId, toUid, fromUid, msg, button)
        elif mtype == 1 and len(msg) > 0 and gameId >= 0:
            # 发送站内消息到全体用户
            # 必选参数
            # msg - 消息
            # gameId
            data = pkmessage.sendGlobal(gameId, msg, button)
        elif mtype == 2 and gameId > 0 and len(msg) > 0 :
            # 发送LED
            # TODO 当前Game服务为4,5,6号 , 每个服务都发送
            mo.setCmd('send_led')
            mo.setParam('msg', msg)
            mo.setParam('gameId', gameId)
            mo.setParam('ismgr', 1)
            router.sendToAll(mo, gdata.SRV_TYPE_UTIL)
            data = True
        elif mtype == 3 and gameId > 0 and toUid > 0 and len(msg) > 0 :
            # 封装popwnd
            # 必选参数
            # gameId
            # toUid 接收弹窗的userId
            # msg 弹窗消息内容
            task = TodoTaskShowInfo(msg, True)
            mo = TodoTaskHelper.makeTodoTaskMsg(gameId, toUid, task)
            # 将消息发送给此人
            router.sendToUser(mo, toUid)
            data = True
        elif mtype in (4, 5) and gameId > 0 and len(msg) > 0 and len(scope) > 0:
            mo.setCmd('send_led')
            mo.setParam('msg', msg)
            ftlog.info('send_led new msg=', msg)
            mo.setParam('gameId', gameId)
            ftlog.info('send_led new gameId=', gameId)
            mo.setParam('ismgr', ismgr)
            ftlog.info('send_led new ismgr=', ismgr)
            mo.setParam('scope', scope)
            ftlog.info('send_led new scope=', scope)
            mo.setParam('clientIds', clientIds)
            ftlog.info('send_led new clientIds=', clientIds)
            mo.setParam('isStopServer', True if mtype == 5 else False)
            router.sendToAll(mo, gdata.SRV_TYPE_UTIL)
            data = True

        if data == None:
            mo.setError(1, 'params error')
        else:
            mo.setResult('ok', 'true')
        return mo

    @markHttpMethod(httppath='/v1/getmsg')
    def doGetMessage(self, gameId, userId, msgtype, pageNo):
        mo = MsgPack()
        if msgtype == -1 or msgtype == 0 :
            data = pkmessage.getPrivate(gameId, userId, pageNo)
            mo.setResult('private', data)

        if msgtype == -1 or msgtype == 1 :
            data = pkmessage.getGlobal(gameId, userId, pageNo)
            mo.setResult('global', data)

        if msgtype == -1 or msgtype == 2 :
            data = hallled.getLedMsgList(gameId)
            mo.setResult('led', data)
            
        mo.setResult('ok', 'true')
        return mo

    @markHttpMethod(httppath='/v1/getmsgcount')
    def doGetMessageCount(self, gameId, userId):
        mo = MsgPack()
        privateCount = pkmessage.getPrivateUnReadCount(gameId, userId)
        globalCount = pkmessage.getGlobalUnReadCount(gameId, userId)
        mo.setResult('counts', {'global':globalCount, 'private':privateCount, 'led':0})
        mo.setResult('ok', 'true')
        return mo


