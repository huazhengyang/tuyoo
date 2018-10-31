# -*- coding: utf-8 -*-
'''
Created on 2017年09月18日

@author: zqh
请不要删除或随意修改此文件，此py文件作为停服前的关闭房间、检测功能而使用
'''
from hall.entity.hallconf import HALL_GAMEID
from freetime.core.timer import FTTimer
from poker.entity.dao import userchip
from poker.entity.dao.userchip import ChipNotEnoughOpMode

def fixCoupon():
    hUsers = [
        {'userId': 19274, 'count':926},
        {'userId': 29874, 'count':926},
        {'userId': 24844, 'count':926},
        {'userId': 28158, 'count':926},
        {'userId': 29593, 'count':926},
        {'userId': 24489, 'count':926},
        {'userId': 22459, 'count':926},
        {'userId': 20389, 'count':926},
        {'userId': 24155, 'count':926},
        {'userId': 29755, 'count':926},
        
        {'userId': 10138, 'count':926},
        {'userId': 12715, 'count':926},
        {'userId': 19313, 'count':926},
        {'userId': 22414, 'count':926},
        {'userId': 26982, 'count':926},
        {'userId': 15842, 'count':926},
        {'userId': 21920, 'count':926},
        {'userId': 28971, 'count':926},
        {'userId': 29533, 'count':926},
        {'userId': 29116, 'count':926},
        
        {'userId': 26033, 'count':926},
        {'userId': 24790, 'count':926},
        {'userId': 17400, 'count':926},
        {'userId': 29862, 'count':926},
        {'userId': 10271, 'count':926},
        {'userId': 14800, 'count':926},
        {'userId': 29835, 'count':926},
        {'userId': 25583, 'count':926},
        {'userId': 20964, 'count':926},
        {'userId': 26306, 'count':926},
        
        {'userId': 15786, 'count':926},
        {'userId': 20102, 'count':926},
        {'userId': 24844, 'count':926},
        {'userId': 15031, 'count':926},
        {'userId': 20906, 'count':926},
        {'userId': 24653, 'count':926},
        {'userId': 20420, 'count':926},
        {'userId': 23383, 'count':926},
        {'userId': 28964, 'count':926},
        {'userId': 15369, 'count':926},
        
        {'userId': 10626, 'count':926},
        {'userId': 29590, 'count':926},
        {'userId': 12537, 'count':926},
        {'userId': 21340, 'count':926},
        {'userId': 29740, 'count':926},
        {'userId': 10095, 'count':926},
        {'userId': 16038, 'count':926},
        {'userId': 20445, 'count':926},
        {'userId': 27527, 'count':926},
        {'userId': 29503, 'count':926},
        
        {'userId': 22447, 'count':926},
        {'userId': 29207, 'count':926},
        {'userId': 25352, 'count':926},
        {'userId': 10275, 'count':926},
        {'userId': 23383, 'count':926},
        {'userId': 22522, 'count':926},
        {'userId': 21620, 'count':926},
        {'userId': 28027, 'count':926},
        {'userId': 29149, 'count':926},
        {'userId': 15769, 'count':926},
        
        {'userId': 22286, 'count':926},
        {'userId': 29686, 'count':926},
        {'userId': 10260, 'count':926},
        {'userId': 10783, 'count':926},
        {'userId': 10684, 'count':926},
        {'userId': 29637, 'count':926},
        {'userId': 22319, 'count':926},
        {'userId': 20389, 'count':926},
        {'userId': 25763, 'count':926},
        {'userId': 18587, 'count':926},
        
        {'userId': 29286, 'count':926},
        {'userId': 22980, 'count':926},
        {'userId': 15643, 'count':926},
        {'userId': 25926, 'count':926},
        {'userId': 24011, 'count':926},
        {'userId': 11441, 'count':926},
        {'userId': 11169, 'count':926},
        {'userId': 22709, 'count':926},
        {'userId': 29639, 'count':926}
    ]
    
    for user in hUsers:
        userId = user['userId']
        count = user['count']
        
        userchip.incrCoupon(userId, HALL_GAMEID, count, ChipNotEnoughOpMode.NOOP,
                    'HALL_INVITEE_TASK_REWARD',
                    0,
                    None)

FTTimer(1, fixCoupon)