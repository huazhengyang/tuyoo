# -*- coding: utf-8 -*-
'''
Created on 2015年5月20日

@author: zqh
'''


from hall.entity import hallversionmgr
from poker.entity.configure import gdata
from poker.protocol import runhttp
from poker.protocol.decorator import markHttpHandler, markHttpMethod
from poker.servers.conn.rpc import onlines
from poker.servers.rpc import srvmgr
from poker.util import strutil
import freetime.util.log as ftlog


@markHttpHandler
class ManagerHttpHandler(object):

    def _check_param_serverIds(self, key, params):
        allIds = gdata.allServersMap().keys()
        serverIds = runhttp.getParamStr(key, '')
        if serverIds == 'all':
            return None, allIds

        slist = serverIds.split(',')
        if slist and len(slist) > 0:
# TODO HALL51补丁
#             for s in slist:
#                 if not s in allIds:
#                     return 'param serverIds not is allServersMap ' + str(s) + ' allIds=' + str(allIds), None
            return None, slist
        return 'param serverIds error', None

    def _check_param_hotfixpy(self, key, params):
        hotfixpy = runhttp.getParamStr(key, '')
        if hotfixpy:
            return None, hotfixpy
        return 'param hotfixpy error', None

    def _check_param_wait(self, key, params):
        wait = runhttp.getParamInt(key, 1)
        return None, wait

    def _check_param_hotparams(self, key, params):
        hotparams = runhttp.getParamStr(key, '')
        try:
            if len(hotparams) > 0:
                hotparams = strutil.loads(hotparams)
            return None, hotparams
        except:
            pass
        return 'param hotparams error, must be a json dumps string', None

    @markHttpMethod(httppath='/_http_manager_hotfix')
    def doHttpHotFix(self, serverIds, hotfixpy, wait, hotparams):
        ftlog.info('doHttpHotFix->', serverIds, hotfixpy)
        ret = srvmgr.hotFix(hotfixpy, serverIds, wait, hotparams)
        return ret

    @markHttpMethod(httppath='/_http_manager_notify_local_static')
    def doHttpNotifyLocalStatic(self):
        msg = hallversionmgr.makeStaticMessage()
        msg = msg.pack()
        count = onlines.notifyUsers(msg)
        return 'OK' + str(count)
