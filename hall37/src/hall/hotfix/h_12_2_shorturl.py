# -*- coding:utf-8 -*-
'''
Created on 2017年12月2日

@author: zhaojiangang
'''
from hall.entity import hall_short_url
import freetime.util.log as ftlog
from freetime.core.timer import FTLoopTimer


def hotmain():
    hall_short_url._instance.apiKey = 'bqkVoGCAYx'
    hall_short_url._instance.secretKey = 'EuOLQYtTwyrrkdSKEZWlgqOHRgMPtoZK'

    token, expires = 'bqkVoGCAYx|1514772253|180342e4bf94fbe9ba8d86b682f5fce4', 1514772253
    hall_short_url._instance.saveToken(token, expires)
    
    hall_short_url._instance.token = token
    hall_short_url._instance.expires = 1514772253

    ftlog.info('shorturlhot save token', token, expires)


FTLoopTimer(0, 0, hotmain).start()
