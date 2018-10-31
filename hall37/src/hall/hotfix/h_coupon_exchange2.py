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
    ls = [
        {
            "userId": 10130,
            "target": 640
        },
        {
            "userId": 10061,
            "target": 740
        },
        {
            "userId": 10003,
            "target": 740
        },
        {
            "userId": 10093,
            "target": 640
        },
        {
            "userId": 10133,
            "target": 640
        },
        {
            "userId": 11434,
            "target": 640
        },
        {
            "userId": 11426,
            "target": 640
        },
        {
            "userId": 11395,
            "target": 640
        },
        {
            "userId": 11146,
            "target": 640
        },
        {
            "userId": 11345,
            "target": 640
        },
        {
            "userId": 10831,
            "target": 640
        },
        {
            "userId": 11252,
            "target": 640
        },
        {
            "userId": 11370,
            "target": 640
        },
        {
            "userId": 11359,
            "target": 640
        },
        {
            "userId": 11316,
            "target": 640
        },
        {
            "userId": 11302,
            "target": 640
        },
        {
            "userId": 10968,
            "target": 980
        },
        {
            "userId": 11292,
            "target": 640
        },
        {
            "userId": 11258,
            "target": 640
        },
        {
            "userId": 10186,
            "target": 640
        },
        {
            "userId": 11251,
            "target": 640
        },
        {
            "userId": 10064,
            "target": 980
        },
        {
            "userId": 10071,
            "target": 1420
        },
        {
            "userId": 10121,
            "target": 640
        },
        {
            "userId": 10271,
            "target": 870
        },
        {
            "userId": 10151,
            "target": 870
        },
        {
            "userId": 10571,
            "target": 740
        },
        {
            "userId": 10330,
            "target": 640
        },
        {
            "userId": 11010,
            "target": 640
        },
        {
            "userId": 10369,
            "target": 870
        },
        {
            "userId": 10552,
            "target": 640
        },
        {
            "userId": 10058,
            "target": 870
        },
        {
            "userId": 10340,
            "target": 640
        },
        {
            "userId": 10305,
            "target": 750
        },
        {
            "userId": 11180,
            "target": 640
        },
        {
            "userId": 10359,
            "target": 640
        },
        {
            "userId": 11170,
            "target": 640
        },
        {
            "userId": 11167,
            "target": 640
        },
        {
            "userId": 12367,
            "target": 530
        },
        {
            "userId": 12156,
            "target": 530
        },
        {
            "userId": 12670,
            "target": 530
        },
        {
            "userId": 12433,
            "target": 530
        },
        {
            "userId": 12583,
            "target": 530
        },
        {
            "userId": 12635,
            "target": 530
        },
        {
            "userId": 12492,
            "target": 530
        },
        {
            "userId": 12463,
            "target": 530
        },
        {
            "userId": 12434,
            "target": 530
        },
        {
            "userId": 12394,
            "target": 530
        },
        {
            "userId": 12197,
            "target": 530
        },
        {
            "userId": 12291,
            "target": 530
        },
        {
            "userId": 12177,
            "target": 530
        },
        {
            "userId": 11974,
            "target": 760
        },
        {
            "userId": 12466,
            "target": 530
        },
        {
            "userId": 12134,
            "target": 530
        },
        {
            "userId": 12306,
            "target": 530
        },
        {
            "userId": 12339,
            "target": 530
        },
        {
            "userId": 12178,
            "target": 530
        },
        {
            "userId": 12152,
            "target": 530
        },
        {
            "userId": 11730,
            "target": 530
        },
        {
            "userId": 12135,
            "target": 530
        },
        {
            "userId": 12135,
            "target": 530
        },
        {
            "userId": 11835,
            "target": 760
        },
        {
            "userId": 11709,
            "target": 760
        },
        {
            "userId": 10110,
            "target": 760
        },
        {
            "userId": 11508,
            "target": 760
        },
        {
            "userId": 10154,
            "target": 530
        },
        {
            "userId": 11932,
            "target": 530
        },
        {
            "userId": 11877,
            "target": 530
        },
        {
            "userId": 11463,
            "target": 530
        },
        {
            "userId": 11787,
            "target": 530
        },
        {
            "userId": 11765,
            "target": 530
        },
        {
            "userId": 11776,
            "target": 530
        },
        {
            "userId": 10500,
            "target": 760
        },
        {
            "userId": 11387,
            "target": 760
        },
        {
            "userId": 10583,
            "target": 530
        },
        {
            "userId": 11668,
            "target": 530
        },
        {
            "userId": 11607,
            "target": 530
        },
        {
            "userId": 11641,
            "target": 530
        },
        {
            "userId": 11666,
            "target": 530
        },
        {
            "userId": 11483,
            "target": 530
        },
        {
            "userId": 11627,
            "target": 530
        },
        {
            "userId": 10286,
            "target": 530
        },
        {
            "userId": 11270,
            "target": 530
        },
        {
            "userId": 10949,
            "target": 530
        },
        {
            "userId": 10398,
            "target": 530
        }
    ]
    
    for lNode in ls:
        userId = lNode['userId']
        target = lNode['target']
        nowCount = userchip.getCoupon(userId)
        if target > nowCount:
            continue
        
        userchip.incrCoupon(userId, HALL_GAMEID, target - nowCount, ChipNotEnoughOpMode.NOOP,
                        'HALL_INVITEE_TASK_REWARD',
                        0,
                        None)
        userdata.setAttr(userId, 'exchangedCoupon', 0)

FTTimer(1, fixCoupon)