# -*- coding: utf-8 -*-

import  datetime
import _roombase
import random

intervalPool = []
def convertrdef(rid, rdef):
    print rid
    rdef['hasrobot'] = 1

    if rdef.get('ismatch', 0):
        rdef['robotUserCallUpTime'] = 1
        rdef['robotUserMaxCount'] = 10
        rdef['robotUserOpTime'] = [1,1]
        rdef['matchConf']['start']['user.minsize'] = 3
        randomMin = random.randint(0,30)
        randomMin1 = random.randint(1,30)
        while randomMin1 in intervalPool:
            randomMin1 = random.randint(1,30)
        intervalPool.append(randomMin1)

        tems = "00"
        if randomMin < 10:
            tems = "0"+str(randomMin)
        else:
            tems = str(randomMin)

        rdef['matchConf']['start']['times']['times_in_day'] = {"first":"00:00", "interval":6, "count":238}
        dt = datetime.datetime.now().strftime('%Y%m%d')
        dayctl = rdef['matchConf']['start']['times']['days']
        if 'list' in dayctl :
            days = dayctl['list']
            if dt not in days :
                days.append(dt)
                days.sort()

_roombase.convert(7, convertrdef)

