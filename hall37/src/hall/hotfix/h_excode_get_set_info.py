# -*- coding:utf-8 -*-
'''
Created on 2017年11月8日

@author: zhaojiangang
'''
from poker.entity.dao import daobase
from freetime.core.timer import FTLoopTimer
import freetime.util.log as ftlog

excodes = [
    '0P25BNV6TKO80BNA',
    'MO25BNGBNZREUVE8'
]

def getCodeInfo():
    for excode in excodes:
        scode = excode[0:6]
        jstr = daobase.executeMixCmd('HGET', 'excodeinfo:%s' % (scode), 'common')
        ftlog.info('h_excode_get_info code=', excode, 'info=', jstr)


FTLoopTimer(0, 0, getCodeInfo).start()