'''
Created on 2015年11月10日

@author: zhaojiangang
'''
import freetime.util.log as ftlog
from hall.servers.common.base_http_checker import BaseHttpMsgChecker
from poker.protocol import runhttp


def check_param_buttonId(self, key, params):
    buttonId = runhttp.getParamStr(key, '')
    ftlog.debug('BaseHttpMsgChecker._check_param_buttonId key=', key,
                'params=', params,
                'buttonId=', buttonId)
    return None, buttonId

BaseHttpMsgChecker._check_param_buttonId = check_param_buttonId
ftlog.info('hotfix_http_buttonId ok')