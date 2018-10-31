# -*- coding=utf-8 -*-
from poker.entity.configure import gdata
from poker.entity.dao import daobase, userdata, gamedata, userchip, daoconst
from datetime import datetime
import random
import freetime.util.log as ftlog
import json


esnsids = []
sid = gdata.serverNum()
f = open('/home/tyhall/hall37/pcdatas/r.data', 'r')
x = 0
for l in f.readlines() :
    ftlog.info('PCXQ_USER recover ', x, l)
    x += 1
    if l :
        l = json.loads(l.strip())
        rt, userId, snsid, chessExp, totalNum, winNum, loseNum, drawNum, olddata = l
        winNum1, loseNum1, drawNum1 = olddata['winNum'], olddata['loseNum'], olddata['drawNum']
        winNum1 = winNum1 - winNum * rt
        loseNum1 = loseNum1 - loseNum * rt
        drawNum1 = drawNum1 - drawNum * rt
        if winNum1 < 0 or loseNum1 < 0 or drawNum1 < 0 :
            ftlog.info('PCXQ_USER recover2 data ERROR ', rt, userId, snsid, winNum, loseNum, drawNum, olddata)
        else:
            ftlog.info('PCXQ_USER recover2 data', rt, userId, snsid, winNum, loseNum, drawNum, olddata)
            olddata['totalNum'] = winNum1 + loseNum1 + drawNum1
            olddata['winNum'] = winNum1
            olddata['loseNum'] = loseNum1
            olddata['drawNum'] = drawNum1
            gamedata.setGameAttr(userId, 3, 'chessRecord', json.dumps(olddata))
f.close()
ftlog.info('PCXQ_USER ERRSNSIDS=', esnsids)



