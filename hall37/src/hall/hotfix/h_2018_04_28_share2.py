# -*- coding: utf-8 -*-
'''
Created on 2017年09月18日

@author: zhaoliang
请不要删除或随意修改此文件，此py文件作为停服前的关闭房间、检测功能而使用
'''
from sre_compile import isstring

def _check_param_pointId(self, msg, key, params):
    value = msg.getParam(key)
    if isinstance(value, int) or isstring(value):
        return None, int(value)
    return 'ERROR of pointId !' + str(value), None
 
from hall.servers.util.share2_handler import Share2TcpHandler
Share2TcpHandler._check_param_pointId = _check_param_pointId