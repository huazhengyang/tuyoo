# -*- coding: utf-8 -*-
"""
Created on 2015年11月12日

@author: zhaoliang
"""

class CheckTime(object, ):

    def checkTimeBitweenStartAndStop(self, time_now, time_start, time_end):
        """
        检查比赛报名时间
        """
        pass
if (__name__ == '__main__'):
    from datetime import datetime
    time_now = datetime.strptime('00:00', '%H:%M').time()
    time_start = datetime.strptime('09:00', '%H:%M').time()
    time_end = datetime.strptime('02:00', '%H:%M').time()
    match = CheckTime()
    print match.checkTimeBitweenStartAndStop(time_now, time_start, time_end)