# -*- coding:utf-8 -*-
'''
Created on 2016年7月28日

@author: luwei
'''
from dizhu.servers.table.table import TableTcpHandler
import freetime.util.log as ftlog


def _check_param_number(self, msg, key, params):
    number = msg.getParam(key, 1)
    if isinstance(number, int) and number > 0:
        return None, number
    return 'ERROR of number !', 0
    
TableTcpHandler._check_param_number_old = TableTcpHandler._check_param_number
TableTcpHandler._check_param_number = _check_param_number

ftlog.info('hotfix_ddz_smilies_check_number ok')
