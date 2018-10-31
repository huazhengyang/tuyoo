# -*- coding:utf-8 -*-
'''
Created on 2017年7月24日

@author: wangjifa
'''

import freetime.util.log as ftlog
from dizhu.entity import dizhuredenvelope


_itemConfList = [
    {
        "itemId":1083,
        "playModes":["123"],
        "winTimes":10
    },
    {
        "itemId":1085,
        "playModes":["happy"],
        "winTimes":10
    },
    {
        "itemId":1086,
        "playModes":["wild", "quick_laizi"],
        "winTimes":10
    },
    {
        "itemId":1087,
        "playModes":["123"],
        "winTimes":10
    },
    {
        "itemId":4396,
        "playModes":[],
        "winTimes":30
    },
    {
        "itemId":4397,
        "playModes":[],
        "winTimes":10
    },
    {
        "itemId":4266,
        "playModes":["123"],
        "winTimes":3
    },
    {
        "itemId":1180,
        "playModes":["123"],
        "winTimes":3
    },
    {
        "itemId":1181,
        "playModes":["123"],
        "winTimes":3
    },
    {
        "itemId":1182,
        "playModes":["123"],
        "winTimes":3
    },
    {
        "itemId":1183,
        "playModes":["123"],
        "winTimes":3
    },
    {
        "itemId":2170,
        "playModes":["wild", "quick_laizi"],
        "winTimes":10
    },
    {
        "itemId":2111,
        "playModes":["wild", "quick_laizi"],
        "winTimes":10
    }
]

dizhuredenvelope._itemConfList = _itemConfList

ftlog.info('dizhuredenvelope hotfix ok')