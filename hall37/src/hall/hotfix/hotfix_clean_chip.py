# -*- coding:utf-8 -*-
'''
Created on 2016年11月3日

@author: zhaojiangang
'''
import freetime.util.log as ftlog
from poker.entity.dao import userdata, userchip, sessiondata
from poker.entity.dao.userchip import ChipNotEnoughOpMode


uids = [
    249577252,
    249577259, 249577491, 249577496, 249577771, 249577792, 249578043, 249578064, 249578331, 249578348, 249578837,
    249578852, 249579543, 249579560, 249579886, 249579971, 249580429, 249580466, 249580718, 249580726, 249580971,
    249580996, 249581858, 249581863, 249582173, 249582196,
    249586706, 249586990, 249587023,
    249582474, 249582506, 249582804, 249582827, 249583084, 249583118, 249583386, 249583458, 249584294, 249584304,
    249584578, 249584610, 249584865, 249584903, 249585140, 249585796, 249586064, 249586076, 249586351, 249586365,
    249586675, 249885019, 249885469, 249888209
]

for uid in uids:
    userdata.checkUserData(uid)
    chip = userchip.getChip(uid)
    clientId = sessiondata.getClientId(uid)
    userchip.incrChip(uid, 9999, -chip, ChipNotEnoughOpMode.CLEAR_ZERO, 'GM_ADJUST', 0, clientId)
    chip2 = userchip.getChip(uid)
    ftlog.info('CLEAN USER CHIP->', uid, 'BEFORE=', chip, 'AFTER=', chip2)
