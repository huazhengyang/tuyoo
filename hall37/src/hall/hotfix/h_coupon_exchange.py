# -*- coding: utf-8 -*-
'''
Created on 2017年09月18日

@author: zqh
请不要删除或随意修改此文件，此py文件作为停服前的关闭房间、检测功能而使用
'''
from hall.entity.hallconf import HALL_GAMEID
from freetime.core.timer import FTTimer
from poker.entity.dao import userchip, userdata
from poker.entity.dao.userchip import ChipNotEnoughOpMode

def fixCoupon():
    userId = 11293
    target = 640
    nowCount = userchip.getCoupon(userId)
    if target < nowCount:
        userchip.incrCoupon(userId, HALL_GAMEID, target - nowCount, ChipNotEnoughOpMode.NOOP,
                    'HALL_INVITEE_TASK_REWARD',
                    0,
                    None)
        userdata.setAttr(userId, 'exchangedCoupon', 0)

FTTimer(1, fixCoupon)