# -*- coding: utf-8 -*-
import _roombase
import datetime

def convertrdef(rid, rdef):
    print rid
    rdef['hasrobot'] = 1
    rdef['robotUserCallUpTime'] = 1
    rdef['robotUserMaxCount'] = -1
    rdef['robotUserOpTime'] = [1,1]
    if int(rid) in (1, 2, 3) :
        rdef['matchConf']['start']['user.minsize'] = 3
        rdef['matchConf']['start']['times']['times_in_day'] = {"first":"00:00", "interval":6, "count":238}
        dt = datetime.datetime.now().strftime('%Y%m%d')
        dayctl = rdef['matchConf']['start']['times']['days']
        if 'list' in dayctl :
            days = dayctl['list']
            if dt not in days :
                days.append(dt)
                days.sort()

_roombase.convert(17, convertrdef)
