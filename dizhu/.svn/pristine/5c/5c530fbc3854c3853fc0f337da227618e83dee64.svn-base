# -*- coding:utf-8 -*-
'''
Created on 2018年7月11日

@author: wangyonghui
'''


from dizhu.entity.led_util import LedUtil
from freetime.core.timer import FTTimer



def deltaUserAsset():
    ledtext = [
        ['FFFFFF', ''],
        ['FFFFFF', 'aaaaa'],
        ['EC3A24', '%.2f元' % (1000 / 100.0)]
    ]
    LedUtil.sendLed(ledtext, 'global', active=1)
FTTimer(0, deltaUserAsset)
