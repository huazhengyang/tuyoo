# -*- coding:utf-8 -*-
'''
Created on 2018年6月6日

@author: zhaojiangang
'''
import time

from freetime.core.reactor import mainloop, exitmainloop
from freetime.core.timer import FTLoopTimer
import freetime.util.log as ftlog
from hall.entity.user_analysis import analysis_api


def getUserFeaturePayCase(userId):
    params = {
        'user_id':userId,
        'time':int(time.time())
    }
    
    ec, datas = analysis_api.requestAnalysis('api.getUserFeatureHall', params)
    
    if ftlog.is_debug():
        ftlog.debug('user_feature_analysis.getUserFeaturePayCase',
                    'userId=', userId,
                    'ec=', ec,
                    'datas=', datas)
    
    return datas.get('pay_case', 0) if ec == 1 else 0


def main():
    userId = 37002005
    print getUserFeaturePayCase(userId)
    exitmainloop()

if __name__ == '__main__':
    FTLoopTimer(0, 0, main).start()
    mainloop()


