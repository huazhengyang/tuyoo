# -*- coding=utf-8
'''
Created on 2015年7月21日

@author: zhaojiangang
'''
import unittest

from biz.mock import patch
from dizhu.entity import dizhuflipcard, dizhutask, dizhuasset
from dizhu.entity.dizhutask import DizhuTaskConditionRoomId
from dizhu.game import TGDizhu
from dizhu.gameplays.game_events import UserLevelGrowEvent, UserTablePlayEvent
from dizhu.servers.util.task_handler import MedalTaskHandler
from dizhuentity.dizhuflipcard_test import dizhuflipcard_conf
from entity.halldailycheckin_test import dailycheckin_conf
from entity.hallstore_test import clientIdMap, products_conf, \
    store_template_conf, store_default_conf
from entity.hallvip_test import vip_conf
import freetime.util.log as ftlog
from hall.entity import hallitem, hallvip, halldailycheckin, halltask
from poker.entity.dao import userchip, daoconst
from poker.entity.events.tyevent import EventUserLogin
import poker.util.timestamp as pktimestamp
from test_base import HallTestMockContext


daily_task_conf = {
    "refreshHour":3,
    "refreshContent":{
        "typeId":"FixedContent",
        "items":[
            {"itemId":"user:chip", "count":3000}
        ]
    },
    "starCountList":[
        {"star":1, "count":2},
        {"star":2, "count":2},
        {"star":3, "count":1},
        {"star":4, "count":1},
        {"star":5, "count":1}
    ]        
}

task_conf = {
    "taskUnits":[
        {
            "taskUnitId":"ddz.task.medal",
            "pools":[
                {
                    "tasks":[
                        {
                            "kindId":10001,
                            "typeId":"ddz.task.medal",
                            "name":"游戏5局",
                            "desc":"游戏5局",
                            "pic":"${http_download}/dizhu/medal/img/play_5.png",
                            "count":5,
                            "star":0,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {"itemId":"user:chip", "count":50}
                                ]
                            },
                            "rewardMail":"勋章奖励：\\${rewardContent}"
                        },
                        {
                            "kindId":10002,
                            "typeId":"ddz.task.medal",
                            "name":"游戏20局",
                            "desc":"游戏20局",
                            "pic":"${http_download}/dizhu/medal/img/play_20.png",
                            "count":20,
                            "star":0,
                            "totalLimit":0,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {"itemId":"user:chip", "count":200}
                                ]
                            },
                            "rewardMail":"勋章奖励：\\${rewardContent}"
                        },
                        {
                            "kindId":10003,
                            "typeId":"ddz.task.medal",
                            "name":"游戏100局",
                            "desc":"游戏100局",
                            "pic":"${http_download}/dizhu/medal/img/play_100.png",
                            "count":100,
                            "star":0,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {"itemId":"user:coupon", "count":50}
                                ]
                            },
                            "rewardMail":"勋章奖励：\\${rewardContent}"
                        },
                        {
                            "kindId":10004,
                            "typeId":"ddz.task.medal",
                            "name":"五胜",
                            "desc":"赢取5局",
                            "pic":"${http_download}/dizhu/medal/img/win_5.png",
                            "count":5,
                            "star":0,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.win",
                                "conditions":[
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {"itemId":"user:chip", "count":100}
                                ]
                            },
                            "rewardMail":"勋章奖励：\\${rewardContent}"
                        },
                        {
                            "kindId":10005,
                            "typeId":"ddz.task.medal",
                            "name":"二十胜",
                            "desc":"赢取20局",
                            "pic":"${http_download}/dizhu/medal/img/win_20.png",
                            "count":20,
                            "star":0,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.win",
                                "conditions":[
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {"itemId":"user:chip", "count":400}
                                ]
                            },
                            "rewardMail":"勋章奖励：\\${rewardContent}"
                        },
                        {
                            "kindId":10006,
                            "typeId":"ddz.task.medal",
                            "name":"百人斩",
                            "desc":"赢取100局",
                            "pic":"${http_download}/dizhu/medal/img/win_100.png",
                            "count":100,
                            "star":0,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.win",
                                "conditions":[
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {"itemId":"user:coupon", "count":100}
                                ]
                            },
                            "rewardMail":"勋章奖励：\\${rewardContent}"
                        },
                        {
                            "kindId":10010,
                            "typeId":"ddz.task.medal",
                            "name":"小红手",
                            "desc":"进行过宝箱抽奖",
                            "pic":"${http_download}/dizhu/medal/img/red_hand.png",
                            "count":1,
                            "star":0,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.tboxLottery",
                                "conditions":[
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {"itemId":"item:2003", "count":1}
                                ]
                            },
                            "rewardMail":"勋章奖励：\\${rewardContent}"
                        },
                        {
                            "kindId":10011,
                            "typeId":"ddz.task.medal",
                            "name":"万元户",
                            "desc":"金币到达10000",
                            "pic":"${http_download}/dizhu/medal/img/yuan_10000.png",
                            "count":10000,
                            "star":0,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.chip",
                                "conditions":[
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {"itemId":"item:2003", "count":3}
                                ]
                            },
                            "rewardMail":"勋章奖励：\\${rewardContent}"
                        },
                        {
                            "kindId":10012,
                            "typeId":"ddz.task.medal",
                            "name":"小康证",
                            "desc":"金币到达100000",
                            "pic":"${http_download}/dizhu/medal/img/xiaokang.png",
                            "count":100000,
                            "star":0,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.chip",
                                "conditions":[
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {"itemId":"item:2003", "count":5}
                                ]
                            },
                            "rewardMail":"勋章奖励：\\${rewardContent}"
                        },
                        {
                            "kindId":10013,
                            "typeId":"ddz.task.medal",
                            "name":"土豪证",
                            "desc":"金币到达1000000",
                            "pic":"${http_download}/dizhu/medal/img/tuhao.png",
                            "count":1000000,
                            "star":0,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.chip",
                                "conditions":[
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {"itemId":"item:2003", "count":5}
                                ]
                            },
                            "rewardMail":"勋章奖励：\\${rewardContent}"
                        },
                        {
                            "kindId":10014,
                            "typeId":"ddz.task.medal",
                            "name":"春天",
                            "desc":"春天或反春取胜",
                            "pic":"${http_download}/dizhu/medal/img/spring.png",
                            "count":1,
                            "star":0,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.win",
                                "conditions":[
                                    {"typeId":"ddz.cond.chuntian"}
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {"itemId":"item:2003", "count":5}
                                ]
                            },
                            "rewardMail":"勋章奖励：\\${rewardContent}"
                        },
                        {
                            "kindId":10015,
                            "typeId":"ddz.task.medal",
                            "name":"炸弹人",
                            "desc":"赢取2炸以上的牌局",
                            "pic":"${http_download}/dizhu/medal/img/boom.png",
                            "count":1,
                            "star":0,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.win",
                                "conditions":[
                                    {"typeId":"ddz.cond.zhadan", "nbomb":2}
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {"itemId":"item:3002", "count":1}
                                ]
                            },
                            "rewardMail":"勋章奖励：\\${rewardContent}"
                        },
                        {
                            "kindId":10018,
                            "typeId":"ddz.task.medal",
                            "name":"3连胜",
                            "desc":"3连胜",
                            "pic":"${http_download}/dizhu/medal/img/continue_win_3.png",
                            "count":3,
                            "star":0,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.winStreak",
                                "conditions":[
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {"itemId":"item:3002", "count":1}
                                ]
                            },
                            "rewardMail":"勋章奖励：\\${rewardContent}"
                        },
                        {
                            "kindId":10019,
                            "typeId":"ddz.task.medal",
                            "name":"5连胜",
                            "desc":"5连胜",
                            "pic":"${http_download}/dizhu/medal/img/continue_win_5.png",
                            "count":5,
                            "star":0,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.winStreak",
                                "conditions":[
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {"itemId":"item:3002", "count":1}
                                ]
                            },
                            "rewardMail":"勋章奖励：\\${rewardContent}"
                        },
                        {
                            "kindId":10020,
                            "typeId":"ddz.task.medal",
                            "name":"10连胜",
                            "desc":"10连胜",
                            "pic":"${http_download}/dizhu/medal/img/continue_win_10.png",
                            "count":10,
                            "star":0,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.winStreak",
                                "conditions":[
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {"itemId":"item:3002", "count":1}
                                ]
                            },
                            "rewardMail":"勋章奖励：\\${rewardContent}"
                        }
                    ]
                }
               ]
        },
        {
            "taskUnitId":"ddz.task.daily",
            "pools":[
                {
                    "tasks":[
                        {
                            "kindId":1,
                            "typeId":"hall.task.simple",
                            "name":"今日赢取5局",
                            "desc":"今日赢取5局",
                            "pic":"",
                            "count":5,
                            "star":1,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.win",
                                "conditions":[
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {"itemId":"user:chip", "count":100}
                                ]
                            },
                            "rewardMail":"任务奖励：\\${rewardContent}"
                        },
                        {
                            "kindId":2,
                            "typeId":"hall.task.simple",
                            "name":"今日游戏10局",
                            "desc":"今日游戏10局",
                            "pic":"",
                            "count":10,
                            "star":1,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {"itemId":"user:chip", "count":100}
                                ]
                            },
                            "rewardMail":"任务奖励：\\${rewardContent}"
                        },
                        {
                            "kindId":3,
                            "typeId":"hall.task.simple",
                            "name":"今日获得1次春天",
                            "desc":"今日获得1次春天",
                            "pic":"",
                            "count":1,
                            "star":1,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.win",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.chuntian"
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {"itemId":"user:chip", "count":100}
                                ]
                            },
                            "rewardMail":"任务奖励：\\${rewardContent}"
                        },
                        {
                            "kindId":4,
                            "typeId":"hall.task.simple",
                            "name":"今日赢2炸以上牌局",
                            "desc":"今日赢2炸以上牌局",
                            "pic":"",
                            "count":1,
                            "star":1,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.win",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.zhadan",
                                        "nbomb":2
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {"itemId":"user:chip", "count":100}
                                ]
                            },
                            "rewardMail":"任务奖励：\\${rewardContent}"
                        },
                        {
                            "kindId":5,
                            "typeId":"hall.task.simple",
                            "name":"今日赢一次3连胜",
                            "desc":"今日赢一次3连胜",
                            "pic":"",
                            "count":3,
                            "star":1,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.winStreak",
                                "conditions":[
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {"itemId":"user:chip", "count":100}
                                ]
                            },
                            "rewardMail":"任务奖励：\\${rewardContent}"
                        },
                        {
                            "kindId":6,
                            "typeId":"hall.task.simple",
                            "name":"今日赢得3000金币",
                            "desc":"今日赢得3000金币",
                            "pic":"",
                            "count":3000,
                            "star":1,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.winChip",
                                "conditions":[
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {"itemId":"user:chip", "count":100}
                                ]
                            },
                            "rewardMail":"任务奖励：\\${rewardContent}"
                        },
                        {
                            "kindId":7,
                            "typeId":"hall.task.simple",
                            "name":"经典场赢取10局",
                            "desc":"经典场赢取10局",
                            "pic":"",
                            "count":10,
                            "star":2,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.win",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.playMode",
                                        "playModes":["123"]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {"itemId":"user:chip", "count":300}
                                ]
                            },
                            "rewardMail":"任务奖励：\\${rewardContent}"
                        },
                        {
                            "kindId":8,
                            "typeId":"hall.task.simple",
                            "name":"欢乐场赢取10局",
                            "desc":"欢乐场赢取10局",
                            "pic":"",
                            "count":10,
                            "star":2,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.win",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.playMode",
                                        "playModes":["happy"]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {"itemId":"user:chip", "count":300}
                                ]
                            },
                            "rewardMail":"任务奖励：\\${rewardContent}"
                        },
                        {
                            "kindId":9,
                            "typeId":"hall.task.simple",
                            "name":"癞子场赢取10局",
                            "desc":"癞子场赢取10局",
                            "pic":"",
                            "count":10,
                            "star":2,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.win",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.playMode",
                                        "playModes":["laizi"]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {"itemId":"user:chip", "count":300}
                                ]
                            },
                            "rewardMail":"任务奖励：\\${rewardContent}"
                        },
                        {
                            "kindId":16,
                            "typeId":"hall.task.simple",
                            "name":"今日升1级",
                            "desc":"今日升1级",
                            "pic":"",
                            "count":1,
                            "star":4,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.levelGrow",
                                "conditions":[
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {"itemId":"item:2003", "count":1}
                                ]
                            },
                            "rewardMail":"任务奖励：\\${rewardContent}"
                        },
                        {
                            "kindId":17,
                            "typeId":"hall.task.simple",
                            "name":"今日开一个月光宝盒",
                            "desc":"今日开一个月光宝盒",
                            "pic":"",
                            "count":1,
                            "star":4,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"hall.item.open",
                                "conditions":[
                                    {
                                        "typeId":"hall.item.open.kindId",
                                        "kindIds":[3002]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {"itemId":"item:2003", "count":1}
                                ]
                            },
                            "rewardMail":"任务奖励：\\${rewardContent}"
                        },
                        {
                            "kindId":18,
                            "typeId":"hall.task.simple",
                            "name":"今日赢一次10连胜",
                            "desc":"今日赢一次10连胜",
                            "pic":"",
                            "count":10,
                            "star":4,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.winStreak",
                                "conditions":[
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {"itemId":"item:2003", "count":1}
                                ]
                            },
                            "rewardMail":"任务奖励：\\${rewardContent}"
                        },
                        {
                            "kindId":21,
                            "typeId":"hall.task.simple",
                            "name":"获得一次10连胜",
                            "desc":"获得一次10连胜",
                            "pic":"",
                            "count":10,
                            "star":5,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.winStreak",
                                "conditions":[
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "desc":"2000金币",
                                "items":[
                                    {"itemId":"user:chip", "count":2000}
                                ]
                            },
                            "rewardMail":"任务奖励：\\${rewardContent}"
                        }
                    ]
                }
               ]
        },
        {
            "taskUnitId":"ddz.task.table",
            "pools":[
                {
                    "tasks":[
                        {
                            "count":3,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"玩3局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20000,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"ddz:master.score",
                                        "count":3
                                    }
                                ],
                                "desc":"3大师分"
                            },
                            "desc":"玩3局"
                        },
                        {
                            "count":10,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"玩10局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":0,
                            "kindId":20001,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":100
                                    }
                                ],
                                "desc":"100金币"
                            },
                            "desc":"玩10局"
                        },
                        {
                            "count":20,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"玩20局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":0,
                            "kindId":20002,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"item:2003",
                                        "count":1
                                    }
                                ],
                                "desc":"记牌器x1"
                            },
                            "desc":"玩20局"
                        },
                        {
                            "count":50,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"玩50局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20003,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":200
                                    }
                                ],
                                "desc":"200金币"
                            },
                            "desc":"玩50局"
                        },
                        {
                            "count":100,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"玩100局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20004,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"ddz:master.score",
                                        "count":10
                                    }
                                ],
                                "desc":"10大师分"
                            },
                            "desc":"玩100局"
                        },
                        {
                            "count":150,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"玩150局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":0,
                            "kindId":20005,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":500
                                    }
                                ],
                                "desc":"500金币"
                            },
                            "desc":"玩150局"
                        },
                        {
                            "count":200,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"玩200局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20006,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"ddz:master.score",
                                        "count":10
                                    }
                                ],
                                "desc":"10大师分"
                            },
                            "desc":"玩200局"
                        },
                        {
                            "count":250,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"玩250局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":0,
                            "kindId":20007,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"item:2003",
                                        "count":3
                                    }
                                ],
                                "desc":"记牌器x3"
                            },
                            "desc":"玩250局"
                        },
                        {
                            "count":300,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"玩300局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20008,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":800
                                    }
                                ],
                                "desc":"800金币"
                            },
                            "desc":"玩300局"
                        },
                        {
                            "count":400,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"玩400局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20009,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"ddz:master.score",
                                        "count":10
                                    }
                                ],
                                "desc":"10大师分"
                            },
                            "desc":"玩400局"
                        },
                        {
                            "count":500,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"玩500局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20010,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":1000
                                    }
                                ],
                                "desc":"1000金币"
                            },
                            "desc":"玩500局"
                        },
                        {
                            "count":666,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"玩666局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20011,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":1000
                                    }
                                ],
                                "desc":"1000金币"
                            },
                            "desc":"玩666局"
                        },
                        {
                            "count":750,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"玩750局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20012,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":1000
                                    }
                                ],
                                "desc":"1000金币"
                            },
                            "desc":"玩750局"
                        },
                        {
                            "count":888,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"玩888局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20013,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":1000
                                    }
                                ],
                                "desc":"1000金币"
                            },
                            "desc":"玩888局"
                        },
                        {
                            "count":1000,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"玩1000局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20014,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":1000
                                    }
                                ],
                                "desc":"1000金币"
                            },
                            "desc":"玩1000局"
                        },
                        {
                            "count":3,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"中级场玩3局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20015,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            603,
                                            605,
                                            607,
                                            651,
                                            652,
                                            653,
                                            671,
                                            672,
                                            673,
                                            691,
                                            692,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"ddz:master.score",
                                        "count":20
                                    }
                                ],
                                "desc":"20大师分"
                            },
                            "desc":"中级场玩3局"
                        },
                        {
                            "count":10,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"中级场玩10局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":0,
                            "kindId":20016,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            603,
                                            605,
                                            607,
                                            651,
                                            652,
                                            653,
                                            671,
                                            672,
                                            673,
                                            691,
                                            692,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":1000
                                    }
                                ],
                                "desc":"1000金币"
                            },
                            "desc":"中级场玩10局"
                        },
                        {
                            "count":20,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"中级场玩20局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":0,
                            "kindId":20017,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            603,
                                            605,
                                            607,
                                            651,
                                            652,
                                            653,
                                            671,
                                            672,
                                            673,
                                            691,
                                            692,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"ddz:master.score",
                                        "count":20
                                    }
                                ],
                                "desc":"20大师分"
                            },
                            "desc":"中级场玩20局"
                        },
                        {
                            "count":50,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"中级场玩50局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20018,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            603,
                                            605,
                                            607,
                                            651,
                                            652,
                                            653,
                                            671,
                                            672,
                                            673,
                                            691,
                                            692,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":1000
                                    }
                                ],
                                "desc":"1000金币"
                            },
                            "desc":"中级场玩50局"
                        },
                        {
                            "count":100,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"中级场玩100局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20019,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            603,
                                            605,
                                            607,
                                            651,
                                            652,
                                            653,
                                            671,
                                            672,
                                            673,
                                            691,
                                            692,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"ddz:master.score",
                                        "count":20
                                    }
                                ],
                                "desc":"20大师分"
                            },
                            "desc":"中级场玩100局"
                        },
                        {
                            "count":150,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"中级场玩150局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":0,
                            "kindId":20020,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            603,
                                            605,
                                            607,
                                            651,
                                            652,
                                            653,
                                            671,
                                            672,
                                            673,
                                            691,
                                            692,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":1000
                                    }
                                ],
                                "desc":"1000金币"
                            },
                            "desc":"中级场玩150局"
                        },
                        {
                            "count":200,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"中级场玩200局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20021,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            603,
                                            605,
                                            607,
                                            651,
                                            652,
                                            653,
                                            671,
                                            672,
                                            673,
                                            691,
                                            692,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"ddz:master.score",
                                        "count":20
                                    }
                                ],
                                "desc":"20大师分"
                            },
                            "desc":"中级场玩200局"
                        },
                        {
                            "count":250,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"中级场玩250局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":0,
                            "kindId":20022,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            603,
                                            605,
                                            607,
                                            651,
                                            652,
                                            653,
                                            671,
                                            672,
                                            673,
                                            691,
                                            692,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"item:2003",
                                        "count":3
                                    }
                                ],
                                "desc":"记牌器x3"
                            },
                            "desc":"中级场玩250局"
                        },
                        {
                            "count":300,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"中级场玩300局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20023,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            603,
                                            605,
                                            607,
                                            651,
                                            652,
                                            653,
                                            671,
                                            672,
                                            673,
                                            691,
                                            692,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":1600
                                    }
                                ],
                                "desc":"1600金币"
                            },
                            "desc":"中级场玩300局"
                        },
                        {
                            "count":400,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"中级场玩400局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20024,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            603,
                                            605,
                                            607,
                                            651,
                                            652,
                                            653,
                                            671,
                                            672,
                                            673,
                                            691,
                                            692,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"ddz:master.score",
                                        "count":20
                                    }
                                ],
                                "desc":"20大师分"
                            },
                            "desc":"中级场玩400局"
                        },
                        {
                            "count":500,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"中级场玩500局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20025,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            603,
                                            605,
                                            607,
                                            651,
                                            652,
                                            653,
                                            671,
                                            672,
                                            673,
                                            691,
                                            692,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":2500
                                    }
                                ],
                                "desc":"2500金币"
                            },
                            "desc":"中级场玩500局"
                        },
                        {
                            "count":666,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"中级场玩666局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20026,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            603,
                                            605,
                                            607,
                                            651,
                                            652,
                                            653,
                                            671,
                                            672,
                                            673,
                                            691,
                                            692,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":2500
                                    }
                                ],
                                "desc":"2500金币"
                            },
                            "desc":"中级场玩666局"
                        },
                        {
                            "count":750,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"中级场玩750局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20027,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            603,
                                            605,
                                            607,
                                            651,
                                            652,
                                            653,
                                            671,
                                            672,
                                            673,
                                            691,
                                            692,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":2500
                                    }
                                ],
                                "desc":"2500金币"
                            },
                            "desc":"中级场玩750局"
                        },
                        {
                            "count":888,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"中级场玩888局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20028,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            603,
                                            605,
                                            607,
                                            651,
                                            652,
                                            653,
                                            671,
                                            672,
                                            673,
                                            691,
                                            692,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":2500
                                    }
                                ],
                                "desc":"2500金币"
                            },
                            "desc":"中级场玩888局"
                        },
                        {
                            "count":1000,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"中级场玩1000局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20029,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            603,
                                            605,
                                            607,
                                            651,
                                            652,
                                            653,
                                            671,
                                            672,
                                            673,
                                            691,
                                            692,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":2500
                                    }
                                ],
                                "desc":"2500金币"
                            },
                            "desc":"中级场玩1000局"
                        },
                        {
                            "count":3,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"高级场玩3局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20030,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            607,
                                            652,
                                            653,
                                            672,
                                            673,
                                            692,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"ddz:master.score",
                                        "count":30
                                    }
                                ],
                                "desc":"30大师分"
                            },
                            "desc":"高级场玩3局"
                        },
                        {
                            "count":10,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"高级场玩10局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":0,
                            "kindId":20031,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            607,
                                            652,
                                            653,
                                            672,
                                            673,
                                            692,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"ddz:master.score",
                                        "count":30
                                    }
                                ],
                                "desc":"30大师分"
                            },
                            "desc":"高级场玩10局"
                        },
                        {
                            "count":20,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"高级场玩20局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":0,
                            "kindId":20032,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            607,
                                            652,
                                            653,
                                            672,
                                            673,
                                            692,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":2500
                                    }
                                ],
                                "desc":"2500金币"
                            },
                            "desc":"高级场玩20局"
                        },
                        {
                            "count":50,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"高级场玩50局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20033,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            607,
                                            652,
                                            653,
                                            672,
                                            673,
                                            692,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"ddz:master.score",
                                        "count":40
                                    }
                                ],
                                "desc":"40大师分"
                            },
                            "desc":"高级场玩50局"
                        },
                        {
                            "count":100,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"高级场玩100局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20034,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            607,
                                            652,
                                            653,
                                            672,
                                            673,
                                            692,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"ddz:master.score",
                                        "count":40
                                    }
                                ],
                                "desc":"40大师分"
                            },
                            "desc":"高级场玩100局"
                        },
                        {
                            "count":150,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"高级场玩150局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":0,
                            "kindId":20035,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            607,
                                            652,
                                            653,
                                            672,
                                            673,
                                            692,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":2500
                                    }
                                ],
                                "desc":"2500金币"
                            },
                            "desc":"高级场玩150局"
                        },
                        {
                            "count":200,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"高级场玩200局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20036,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            607,
                                            652,
                                            653,
                                            672,
                                            673,
                                            692,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"ddz:master.score",
                                        "count":40
                                    }
                                ],
                                "desc":"40大师分"
                            },
                            "desc":"高级场玩200局"
                        },
                        {
                            "count":250,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"高级场玩250局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":0,
                            "kindId":20037,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            607,
                                            652,
                                            653,
                                            672,
                                            673,
                                            692,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"ddz:master.score",
                                        "count":40
                                    }
                                ],
                                "desc":"40大师分"
                            },
                            "desc":"高级场玩250局"
                        },
                        {
                            "count":300,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"高级场玩300局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20038,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            607,
                                            652,
                                            653,
                                            672,
                                            673,
                                            692,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":3200
                                    }
                                ],
                                "desc":"3200金币"
                            },
                            "desc":"高级场玩300局"
                        },
                        {
                            "count":400,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"高级场玩400局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20039,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            607,
                                            652,
                                            653,
                                            672,
                                            673,
                                            692,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":3200
                                    }
                                ],
                                "desc":"3200金币"
                            },
                            "desc":"高级场玩400局"
                        },
                        {
                            "count":500,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"高级场玩500局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20040,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            607,
                                            652,
                                            653,
                                            672,
                                            673,
                                            692,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":5000
                                    }
                                ],
                                "desc":"5000金币"
                            },
                            "desc":"高级场玩500局"
                        },
                        {
                            "count":666,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"高级场玩666局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20041,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            607,
                                            652,
                                            653,
                                            672,
                                            673,
                                            692,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":5000
                                    }
                                ],
                                "desc":"5000金币"
                            },
                            "desc":"高级场玩666局"
                        },
                        {
                            "count":750,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"高级场玩750局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20042,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            607,
                                            652,
                                            653,
                                            672,
                                            673,
                                            692,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":5000
                                    }
                                ],
                                "desc":"5000金币"
                            },
                            "desc":"高级场玩750局"
                        },
                        {
                            "count":888,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"高级场玩888局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20043,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            607,
                                            652,
                                            653,
                                            672,
                                            673,
                                            692,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":5000
                                    }
                                ],
                                "desc":"5000金币"
                            },
                            "desc":"高级场玩888局"
                        },
                        {
                            "count":1000,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"高级场玩1000局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20044,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            607,
                                            652,
                                            653,
                                            672,
                                            673,
                                            692,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":5000
                                    }
                                ],
                                "desc":"5000金币"
                            },
                            "desc":"高级场玩1000局"
                        },
                        {
                            "count":3,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"大师场玩3局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20045,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            653,
                                            673,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"ddz:master.score",
                                        "count":80
                                    }
                                ],
                                "desc":"80大师分"
                            },
                            "desc":"大师场玩3局"
                        },
                        {
                            "count":10,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"大师场玩10局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20046,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            653,
                                            673,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"ddz:master.score",
                                        "count":80
                                    }
                                ],
                                "desc":"80大师分"
                            },
                            "desc":"大师场玩10局"
                        },
                        {
                            "count":20,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"大师场玩20局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20047,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            653,
                                            673,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":5000
                                    }
                                ],
                                "desc":"5000金币"
                            },
                            "desc":"大师场玩20局"
                        },
                        {
                            "count":50,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"大师场玩50局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20048,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            653,
                                            673,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":5000
                                    }
                                ],
                                "desc":"5000金币"
                            },
                            "desc":"大师场玩50局"
                        },
                        {
                            "count":100,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"大师场玩100局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20049,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            653,
                                            673,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"ddz:master.score",
                                        "count":80
                                    }
                                ],
                                "desc":"80大师分"
                            },
                            "desc":"大师场玩100局"
                        },
                        {
                            "count":150,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"大师场玩150局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20050,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            653,
                                            673,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":5000
                                    }
                                ],
                                "desc":"5000金币"
                            },
                            "desc":"大师场玩150局"
                        },
                        {
                            "count":200,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"大师场玩200局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20051,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            653,
                                            673,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"ddz:master.score",
                                        "count":80
                                    }
                                ],
                                "desc":"80大师分"
                            },
                            "desc":"大师场玩200局"
                        },
                        {
                            "count":250,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"大师场玩250局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20052,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            653,
                                            673,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"ddz:master.score",
                                        "count":80
                                    }
                                ],
                                "desc":"80大师分"
                            },
                            "desc":"大师场玩250局"
                        },
                        {
                            "count":300,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"大师场玩300局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20053,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            653,
                                            673,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":10000
                                    }
                                ],
                                "desc":"10000金币"
                            },
                            "desc":"大师场玩300局"
                        },
                        {
                            "count":400,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"大师场玩400局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20054,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            653,
                                            673,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"ddz:master.score",
                                        "count":100
                                    }
                                ],
                                "desc":"100大师分"
                            },
                            "desc":"大师场玩400局"
                        },
                        {
                            "count":500,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"大师场玩500局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20055,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            653,
                                            673,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":10000
                                    }
                                ],
                                "desc":"10000金币"
                            },
                            "desc":"大师场玩500局"
                        },
                        {
                            "count":666,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"大师场玩666局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20056,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            653,
                                            673,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":10000
                                    }
                                ],
                                "desc":"10000金币"
                            },
                            "desc":"大师场玩666局"
                        },
                        {
                            "count":750,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"大师场玩750局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20057,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            653,
                                            673,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":10000
                                    }
                                ],
                                "desc":"10000金币"
                            },
                            "desc":"大师场玩750局"
                        },
                        {
                            "count":888,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"大师场玩888局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20058,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            653,
                                            673,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":10000
                                    }
                                ],
                                "desc":"10000金币"
                            },
                            "desc":"大师场玩888局"
                        },
                        {
                            "count":1000,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"大师场玩1000局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20059,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            653,
                                            673,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":10000
                                    }
                                ],
                                "desc":"10000金币"
                            },
                            "desc":"大师场玩1000局"
                        },
                        {
                            "count":1200,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"大师场玩1200局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20060,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            653,
                                            673,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":15000
                                    }
                                ],
                                "desc":"15000金币"
                            },
                            "desc":"大师场玩1200局"
                        },
                        {
                            "count":1400,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"大师场玩1400局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20061,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            653,
                                            673,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":15000
                                    }
                                ],
                                "desc":"15000金币"
                            },
                            "desc":"大师场玩1400局"
                        },
                        {
                            "count":1600,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"大师场玩1600局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20062,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            653,
                                            673,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":15000
                                    }
                                ],
                                "desc":"15000金币"
                            },
                            "desc":"大师场玩1600局"
                        },
                        {
                            "count":1800,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"大师场玩1800局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20063,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            653,
                                            673,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":15000
                                    }
                                ],
                                "desc":"15000金币"
                            },
                            "desc":"大师场玩1800局"
                        },
                        {
                            "count":2000,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"大师场玩2000局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20064,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            653,
                                            673,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":15000
                                    }
                                ],
                                "desc":"15000金币"
                            },
                            "desc":"大师场玩2000局"
                        },
                        {
                            "count":2200,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"大师场玩2200局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20065,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            653,
                                            673,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":15000
                                    }
                                ],
                                "desc":"15000金币"
                            },
                            "desc":"大师场玩2200局"
                        },
                        {
                            "count":2400,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"大师场玩2400局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20066,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            653,
                                            673,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":15000
                                    }
                                ],
                                "desc":"15000金币"
                            },
                            "desc":"大师场玩2400局"
                        },
                        {
                            "count":2600,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"大师场玩2600局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20067,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            653,
                                            673,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":15000
                                    }
                                ],
                                "desc":"15000金币"
                            },
                            "desc":"大师场玩2600局"
                        },
                        {
                            "count":2800,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"大师场玩2800局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20068,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            653,
                                            673,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":15000
                                    }
                                ],
                                "desc":"15000金币"
                            },
                            "desc":"大师场玩2800局"
                        },
                        {
                            "count":3000,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"大师场玩3000局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20069,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            653,
                                            673,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":15000
                                    }
                                ],
                                "desc":"15000金币"
                            },
                            "desc":"大师场玩3000局"
                        },
                        {
                            "count":3500,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"大师场玩3500局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20070,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            653,
                                            673,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":20000
                                    }
                                ],
                                "desc":"20000金币"
                            },
                            "desc":"大师场玩3500局"
                        },
                        {
                            "count":4000,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"大师场玩4000局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20071,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            653,
                                            673,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":20000
                                    }
                                ],
                                "desc":"20000金币"
                            },
                            "desc":"大师场玩4000局"
                        },
                        {
                            "count":4500,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"大师场玩4500局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20072,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            653,
                                            673,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":20000
                                    }
                                ],
                                "desc":"20000金币"
                            },
                            "desc":"大师场玩4500局"
                        },
                        {
                            "count":5000,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"大师场玩5000局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20073,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            653,
                                            673,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":20000
                                    }
                                ],
                                "desc":"20000金币"
                            },
                            "desc":"大师场玩5000局"
                        },
                        {
                            "count":5500,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"大师场玩5500局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20074,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            653,
                                            673,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":20000
                                    }
                                ],
                                "desc":"20000金币"
                            },
                            "desc":"大师场玩5500局"
                        },
                        {
                            "count":6000,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"大师场玩6000局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20075,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            653,
                                            673,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":20000
                                    }
                                ],
                                "desc":"20000金币"
                            },
                            "desc":"大师场玩6000局"
                        },
                        {
                            "count":6500,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"大师场玩6500局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20076,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            653,
                                            673,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":20000
                                    }
                                ],
                                "desc":"20000金币"
                            },
                            "desc":"大师场玩6500局"
                        },
                        {
                            "count":7000,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"大师场玩7000局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20077,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            653,
                                            673,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":20000
                                    }
                                ],
                                "desc":"20000金币"
                            },
                            "desc":"大师场玩7000局"
                        },
                        {
                            "count":7500,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"大师场玩7500局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20078,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            653,
                                            673,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":20000
                                    }
                                ],
                                "desc":"20000金币"
                            },
                            "desc":"大师场玩7500局"
                        },
                        {
                            "count":8000,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"大师场玩8000局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20079,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            653,
                                            673,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":20000
                                    }
                                ],
                                "desc":"20000金币"
                            },
                            "desc":"大师场玩8000局"
                        },
                        {
                            "count":8500,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"大师场玩8500局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20080,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            653,
                                            673,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":20000
                                    }
                                ],
                                "desc":"20000金币"
                            },
                            "desc":"大师场玩8500局"
                        },
                        {
                            "count":9000,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"大师场玩9000局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20081,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            653,
                                            673,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":20000
                                    }
                                ],
                                "desc":"20000金币"
                            },
                            "desc":"大师场玩9000局"
                        },
                        {
                            "count":9500,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"大师场玩9500局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20082,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            653,
                                            673,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":20000
                                    }
                                ],
                                "desc":"20000金币"
                            },
                            "desc":"大师场玩9500局"
                        },
                        {
                            "count":10000,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"大师场玩10000局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20083,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            653,
                                            673,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":20000
                                    }
                                ],
                                "desc":"20000金币"
                            },
                            "desc":"大师场玩10000局"
                        },
                        {
                            "count":11000,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"大师场玩11000局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20084,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            653,
                                            673,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":30000
                                    }
                                ],
                                "desc":"30000金币"
                            },
                            "desc":"大师场玩11000局"
                        },
                        {
                            "count":12000,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"大师场玩12000局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20085,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            653,
                                            673,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":30000
                                    }
                                ],
                                "desc":"30000金币"
                            },
                            "desc":"大师场玩12000局"
                        },
                        {
                            "count":13000,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"大师场玩13000局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20086,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            653,
                                            673,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":30000
                                    }
                                ],
                                "desc":"30000金币"
                            },
                            "desc":"大师场玩13000局"
                        },
                        {
                            "count":14000,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"大师场玩14000局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20087,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            653,
                                            673,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":30000
                                    }
                                ],
                                "desc":"30000金币"
                            },
                            "desc":"大师场玩14000局"
                        },
                        {
                            "count":15000,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"大师场玩15000局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20088,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            653,
                                            673,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":30000
                                    }
                                ],
                                "desc":"30000金币"
                            },
                            "desc":"大师场玩15000局"
                        },
                        {
                            "count":16000,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"大师场玩16000局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20089,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            653,
                                            673,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":30000
                                    }
                                ],
                                "desc":"30000金币"
                            },
                            "desc":"大师场玩16000局"
                        },
                        {
                            "count":17000,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"大师场玩17000局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20090,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            653,
                                            673,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":30000
                                    }
                                ],
                                "desc":"30000金币"
                            },
                            "desc":"大师场玩17000局"
                        },
                        {
                            "count":18000,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"大师场玩18000局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20091,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            653,
                                            673,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":30000
                                    }
                                ],
                                "desc":"30000金币"
                            },
                            "desc":"大师场玩18000局"
                        },
                        {
                            "count":19000,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"大师场玩19000局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20092,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            653,
                                            673,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":30000
                                    }
                                ],
                                "desc":"30000金币"
                            },
                            "desc":"大师场玩19000局"
                        },
                        {
                            "count":20000,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"大师场玩20000局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20093,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            653,
                                            673,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":30000
                                    }
                                ],
                                "desc":"30000金币"
                            },
                            "desc":"大师场玩20000局"
                        },
                        {
                            "count":21000,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"大师场玩21000局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20094,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            653,
                                            673,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":30000
                                    }
                                ],
                                "desc":"30000金币"
                            },
                            "desc":"大师场玩21000局"
                        },
                        {
                            "count":22000,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"大师场玩22000局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20095,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            653,
                                            673,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":30000
                                    }
                                ],
                                "desc":"30000金币"
                            },
                            "desc":"大师场玩22000局"
                        },
                        {
                            "count":23000,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"大师场玩23000局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20096,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            653,
                                            673,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":30000
                                    }
                                ],
                                "desc":"30000金币"
                            },
                            "desc":"大师场玩23000局"
                        },
                        {
                            "count":24000,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"大师场玩24000局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20097,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            653,
                                            673,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":30000
                                    }
                                ],
                                "desc":"30000金币"
                            },
                            "desc":"大师场玩24000局"
                        },
                        {
                            "count":25000,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"大师场玩25000局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20098,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            653,
                                            673,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":30000
                                    }
                                ],
                                "desc":"30000金币"
                            },
                            "desc":"大师场玩25000局"
                        },
                        {
                            "count":26000,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"大师场玩26000局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20099,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            653,
                                            673,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":30000
                                    }
                                ],
                                "desc":"30000金币"
                            },
                            "desc":"大师场玩26000局"
                        },
                        {
                            "count":27000,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"大师场玩27000局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20100,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            653,
                                            673,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":30000
                                    }
                                ],
                                "desc":"30000金币"
                            },
                            "desc":"大师场玩27000局"
                        },
                        {
                            "count":28000,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"大师场玩28000局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20101,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            653,
                                            673,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":30000
                                    }
                                ],
                                "desc":"30000金币"
                            },
                            "desc":"大师场玩28000局"
                        },
                        {
                            "count":29000,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"大师场玩29000局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20102,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            653,
                                            673,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":30000
                                    }
                                ],
                                "desc":"30000金币"
                            },
                            "desc":"大师场玩29000局"
                        },
                        {
                            "count":30000,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"大师场玩30000局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":20103,
                            "totalLimit":1,
                            "inheritPrevTaskProgress":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.roomId",
                                        "roomIds":[
                                            605,
                                            653,
                                            673,
                                            693
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":30000
                                    }
                                ],
                                "desc":"30000金币"
                            },
                            "desc":"大师场玩30000局"
                        }
                    ],
                    "nextType":"next"
                },
                {
                    "tasks":[
                        {
                            "count":2,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"赢2次春天",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":30000,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.win",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.chuntian"
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":100
                                    }
                                ],
                                "desc":"100金币"
                            },
                            "desc":"赢2次春天"
                        },
                        {
                            "count":2,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"做2次地主",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":0,
                            "kindId":30001,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.dizhu"
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":100
                                    }
                                ],
                                "desc":"100金币"
                            },
                            "desc":"做2次地主"
                        },
                        {
                            "count":5,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"做5次地主",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":0,
                            "kindId":30002,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.dizhu"
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":100
                                    }
                                ],
                                "desc":"100金币"
                            },
                            "desc":"做5次地主"
                        },
                        {
                            "count":5,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"抢5次地主",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":0,
                            "kindId":30003,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.call",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.grabDizhu"
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":100
                                    }
                                ],
                                "desc":"100金币"
                            },
                            "desc":"抢5次地主"
                        },
                        {
                            "count":3,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"玩3局经典玩法",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":0,
                            "kindId":30004,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.playMode",
                                        "playModes":[
                                            "123"
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"item:2003",
                                        "count":1
                                    }
                                ],
                                "desc":"记牌器x1"
                            },
                            "desc":"玩3局经典玩法"
                        },
                        {
                            "count":3,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"玩3局欢乐玩法",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":0,
                            "kindId":30005,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.playMode",
                                        "playModes":[
                                            "happy"
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"item:2003",
                                        "count":1
                                    }
                                ],
                                "desc":"记牌器x1"
                            },
                            "desc":"玩3局欢乐玩法"
                        },
                        {
                            "count":3,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"玩3局癞子玩法",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":0,
                            "kindId":30006,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.playMode",
                                        "playModes":[
                                            "laizi"
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"item:2003",
                                        "count":1
                                    }
                                ],
                                "desc":"记牌器x1"
                            },
                            "desc":"玩3局癞子玩法"
                        },
                        {
                            "count":3,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"玩3局二人玩法",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":0,
                            "kindId":30007,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.playMode",
                                        "playModes":[
                                            "erdou"
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"item:2003",
                                        "count":1
                                    }
                                ],
                                "desc":"记牌器x1"
                            },
                            "desc":"玩3局二人玩法"
                        },
                        {
                            "count":5,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"使用炸弹表情5次",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":0,
                            "kindId":30008,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.emoticonUse",
                                "emotions":["bomb"],
                                "conditions":[]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":100
                                    }
                                ],
                                "desc":"100金币"
                            },
                            "desc":"使用炸弹表情5次"
                        },
                        {
                            "count":5,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"使用钻石表情5次",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":0,
                            "kindId":30009,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.emoticonUse",
                                "emotions":["diamond"],
                                "conditions":[]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":100
                                    }
                                ],
                                "desc":"100金币"
                            },
                            "desc":"使用钻石表情5次"
                        },
                        {
                            "count":5,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"使用鲜花表情5次",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":0,
                            "kindId":30010,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.emoticonUse",
                                "emotions":["flower"],
                                "conditions":[]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":100
                                    }
                                ],
                                "desc":"100金币"
                            },
                            "desc":"使用鲜花表情5次"
                        },
                        {
                            "count":5,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"使用鸡蛋表情5次",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":0,
                            "kindId":30011,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.emoticonUse",
                                "emotions":["egg"],
                                "conditions":[]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":100
                                    }
                                ],
                                "desc":"100金币"
                            },
                            "desc":"使用鸡蛋表情5次"
                        },
                        {
                            "count":3,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"连胜3局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":0,
                            "kindId":30012,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.winStreak",
                                "conditions":[]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"ddz:master.score",
                                        "count":5
                                    }
                                ],
                                "desc":"5大师分"
                            },
                            "desc":"连胜3局"
                        },
                        {
                            "count":5,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"连胜5局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":0,
                            "kindId":30013,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.winStreak",
                                "conditions":[]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"ddz:master.score",
                                        "count":10
                                    }
                                ],
                                "desc":"10大师分"
                            },
                            "desc":"连胜5局"
                        },
                        {
                            "count":10,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"连胜10局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":0,
                            "kindId":30014,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.winStreak",
                                "conditions":[]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"ddz:master.score",
                                        "count":100
                                    }
                                ],
                                "desc":"100大师分"
                            },
                            "desc":"连胜10局"
                        },
                        {
                            "count":3,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"32倍胜利3局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":0,
                            "kindId":30015,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.win",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.windoubles",
                                        "stop":-1,
                                        "start":32
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":1000
                                    }
                                ],
                                "desc":"1000金币"
                            },
                            "desc":"32倍胜利3局"
                        },
                        {
                            "count":2,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"64倍胜利2局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":0,
                            "kindId":30016,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.win",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.windoubles",
                                        "stop":-1,
                                        "start":64
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":1000
                                    }
                                ],
                                "desc":"1000金币"
                            },
                            "desc":"64倍胜利2局"
                        },
                        {
                            "count":1,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"大满贯胜利1局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":0,
                            "kindId":30017,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.win",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.slam"
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":1000
                                    }
                                ],
                                "desc":"1000金币"
                            },
                            "desc":"大满贯胜利1局"
                        },
                        {
                            "count":3,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"3次5炸",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":0,
                            "kindId":30018,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.winlose",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.zhadan",
                                        "nbomb":5
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":1000
                                    }
                                ],
                                "desc":"1000金币"
                            },
                            "desc":"3次5炸"
                        },
                        {
                            "count":4,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"4次3炸",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":0,
                            "kindId":30019,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.winlose",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.zhadan",
                                        "nbomb":3
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":1000
                                    }
                                ],
                                "desc":"1000金币"
                            },
                            "desc":"4次3炸"
                        }
                    ],
                    "nextType":"random"
                },
                {
                    "tasks":[
                        {
                            "count":2,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"火箭结束胜利2局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":40000,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.win",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.outWinCardType",
                                        "cardTypes":[
                                            "huojian"
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":100
                                    }
                                ],
                                "desc":"100金币"
                            },
                            "desc":"火箭结束胜利2局"
                        },
                        {
                            "count":5,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"火箭结束胜利5局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":40001,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.win",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.outWinCardType",
                                        "cardTypes":[
                                            "huojian"
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":100
                                    }
                                ],
                                "desc":"100金币"
                            },
                            "desc":"火箭结束胜利5局"
                        },
                        {
                            "count":2,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"炸弹结束胜利2局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":40002,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.win",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.outWinCardType",
                                        "cardTypes":[
                                            "zhadan"
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":100
                                    }
                                ],
                                "desc":"100金币"
                            },
                            "desc":"炸弹结束胜利2局"
                        },
                        {
                            "count":3,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"炸弹结束胜利3局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":40003,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.win",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.outWinCardType",
                                        "cardTypes":[
                                            "zhadan"
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":100
                                    }
                                ],
                                "desc":"100金币"
                            },
                            "desc":"炸弹结束胜利3局"
                        },
                        {
                            "count":4,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"炸弹结束胜利4局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":40004,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.win",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.outWinCardType",
                                        "cardTypes":[
                                            "zhadan"
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":100
                                    }
                                ],
                                "desc":"100金币"
                            },
                            "desc":"炸弹结束胜利4局"
                        },
                        {
                            "count":2,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"顺子结束胜利2局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":40005,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.win",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.outWinCardType",
                                        "cardTypes":[
                                            "danshun"
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":100
                                    }
                                ],
                                "desc":"100金币"
                            },
                            "desc":"顺子结束胜利2局"
                        },
                        {
                            "count":3,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"顺子结束胜利3局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":40006,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.win",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.outWinCardType",
                                        "cardTypes":[
                                            "danshun"
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":100
                                    }
                                ],
                                "desc":"100金币"
                            },
                            "desc":"顺子结束胜利3局"
                        },
                        {
                            "count":4,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"顺子结束胜利4局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":40007,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.win",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.outWinCardType",
                                        "cardTypes":[
                                            "danshun"
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":100
                                    }
                                ],
                                "desc":"100金币"
                            },
                            "desc":"顺子结束胜利4局"
                        },
                        {
                            "count":2,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"连对结束胜利2局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":40008,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.win",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.outWinCardType",
                                        "cardTypes":[
                                            "shuangshun"
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":100
                                    }
                                ],
                                "desc":"100金币"
                            },
                            "desc":"连对结束胜利2局"
                        },
                        {
                            "count":3,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"连对结束胜利3局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":40009,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.win",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.outWinCardType",
                                        "cardTypes":[
                                            "shuangshun"
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":100
                                    }
                                ],
                                "desc":"100金币"
                            },
                            "desc":"连对结束胜利3局"
                        },
                        {
                            "count":4,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"连对结束胜利4局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":40010,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.win",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.outWinCardType",
                                        "cardTypes":[
                                            "shuangshun"
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":100
                                    }
                                ],
                                "desc":"100金币"
                            },
                            "desc":"连对结束胜利4局"
                        },
                        {
                            "count":2,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"三带结束胜利2局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":40011,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.win",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.outWinCardType",
                                        "cardTypes":[
                                            "sandaidan",
                                            "sandaidui"
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":100
                                    }
                                ],
                                "desc":"100金币"
                            },
                            "desc":"三带结束胜利2局"
                        },
                        {
                            "count":3,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"三带结束胜利3局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":40012,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.win",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.outWinCardType",
                                        "cardTypes":[
                                            "sandaidan",
                                            "sandaidui"
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":100
                                    }
                                ],
                                "desc":"100金币"
                            },
                            "desc":"三带结束胜利3局"
                        },
                        {
                            "count":4,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"三带结束胜利4局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":40013,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.win",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.outWinCardType",
                                        "cardTypes":[
                                            "sandaidan",
                                            "sandaidui"
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":100
                                    }
                                ],
                                "desc":"100金币"
                            },
                            "desc":"三带结束胜利4局"
                        },
                        {
                            "count":2,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"四带结束胜利2局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":40014,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.win",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.outWinCardType",
                                        "cardTypes":[
                                            "sidaidan",
                                            "sidaidui"
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":100
                                    }
                                ],
                                "desc":"100金币"
                            },
                            "desc":"四带结束胜利2局"
                        },
                        {
                            "count":3,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"四带结束胜利3局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":40015,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.win",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.outWinCardType",
                                        "cardTypes":[
                                            "sidaidan",
                                            "sidaidui"
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":100
                                    }
                                ],
                                "desc":"100金币"
                            },
                            "desc":"四带结束胜利3局"
                        },
                        {
                            "count":4,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"四带结束胜利4局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":40016,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.win",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.outWinCardType",
                                        "cardTypes":[
                                            "sidaidan",
                                            "sidaidui"
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":100
                                    }
                                ],
                                "desc":"100金币"
                            },
                            "desc":"四带结束胜利4局"
                        },
                        {
                            "count":2,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"三张结束胜利2局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":40017,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.win",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.outWinCardType",
                                        "cardTypes":[
                                            "sanzhang"
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":100
                                    }
                                ],
                                "desc":"100金币"
                            },
                            "desc":"三张结束胜利2局"
                        },
                        {
                            "count":3,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"三张结束胜利3局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":40018,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.win",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.outWinCardType",
                                        "cardTypes":[
                                            "sanzhang"
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":100
                                    }
                                ],
                                "desc":"100金币"
                            },
                            "desc":"三张结束胜利3局"
                        },
                        {
                            "count":4,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"三张结束胜利4局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":40019,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.win",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.outWinCardType",
                                        "cardTypes":[
                                            "sanzhang"
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":100
                                    }
                                ],
                                "desc":"100金币"
                            },
                            "desc":"三张结束胜利4局"
                        },
                        {
                            "count":2,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"底牌翻出豹子2局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":40020,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.baseCardType",
                                        "cardTypes":[
                                            "baozi"
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":100
                                    }
                                ],
                                "desc":"100金币"
                            },
                            "desc":"底牌翻出豹子2局"
                        },
                        {
                            "count":2,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"底牌翻出顺子2局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":40021,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.baseCardType",
                                        "cardTypes":[
                                            "tonghuashun",
                                            "shunzi"
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":100
                                    }
                                ],
                                "desc":"100金币"
                            },
                            "desc":"底牌翻出顺子2局"
                        },
                        {
                            "count":2,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"底牌翻出同花2局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":40022,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.baseCardType",
                                        "cardTypes":[
                                            "tonghua",
                                            "tonghuashun"
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":100
                                    }
                                ],
                                "desc":"100金币"
                            },
                            "desc":"底牌翻出同花2局"
                        },
                        {
                            "count":2,
                            "typeId":"hall.task.simple",
                            "star":0,
                            "name":"底牌翻出火箭2局",
                            "rewardMail":"完成\\${taskName}，获得\\${rewardContent}",
                            "pic":"",
                            "shareUrl":1,
                            "kindId":40023,
                            "totalLimit":1,
                            "inspector":{
                                "typeId":"ddz.play",
                                "conditions":[
                                    {
                                        "typeId":"ddz.cond.baseCardType",
                                        "cardTypes":[
                                            "huojian"
                                        ]
                                    }
                                ]
                            },
                            "rewardContent":{
                                "typeId":"FixedContent",
                                "items":[
                                    {
                                        "itemId":"user:chip",
                                        "count":100
                                    }
                                ],
                                "desc":"100金币"
                            },
                            "desc":"底牌翻出火箭2局"
                        }
                    ],
                    "nextType":"random"
                }
            ]
        }
    ]
}

item_conf = {
    "assets": [
        {
            "kindId": "user:chip",
            "typeId": "common.chip",
            "displayName": "金币",
            "pic": "${http_download}/hall/item/imgs/coin.png",
            "desc": "金币",
            "units": "个",
            "keyForChangeNotify": "chip"
        },
        {
            "kindId": "user:coupon",
            "typeId": "common.coupon",
            "displayName": "奖券",
            "pic": "${http_download}/hall/item/imgs/coupon.png",
            "desc": "奖券",
            "units": "张",
            "keyForChangeNotify": "coupon"
        },
        {
            "kindId": "user:exp",
            "typeId": "common.exp",
            "displayName": "奖券",
            "pic": "${http_download}/hall/item/imgs/coupon.png",
            "desc": "经验值",
            "units": "分",
            "keyForChangeNotify": "exp"
        },
        {
            "kindId": "user:charm",
            "typeId": "common.charm",
            "displayName": "魅力值",
            "pic": "${http_download}/hall/item/imgs/coupon.png",
            "desc": "魅力值",
            "units": "分",
            "keyForChangeNotify": "charm"
        },
        {
            "kindId": "game:assistance",
            "typeId": "common.assistance",
            "displayName": "江湖救急",
            "pic": "",
            "desc": "江湖救急",
            "units": "次",
            "keyForChangeNotify": "gdata"
        },
        {
            "kindId": "ddz:master.score",
            "typeId": "ddz.masterScore",
            "displayName": "大师分",
            "pic": "",
            "desc": "大师分",
            "units": "",
            "keyForChangeNotify": "gdata"
        }
    ],
    "items": [
        {
            "kindId": 1001,
            "typeId": "common.box",
            "displayName": "新手礼包",
            "visibleInBag": 1,
            "desc": "新手上路 微微薄礼，请您笑纳~",
            "singleMode": 1,
            "pic": "${http_download}/hall/item/imgs/item_1001.png",
            "units": {
                "typeId": "common.count",
                "displayName": "个"
            },
            "removeFromBagWhenRemainingZero": 1,
            "removeFromBagWhenExpires": 0,
            "actions": [
                {
                    "name": "sale",
                    "displayName": "出售",
                    "typeId": "common.sale",
                    "mail": "您出售了\\${item}，获得\\${gotContent}",
                    "params": {
                        "type": "countSale",
                        "desc": "出售可获得:",
                        "confirm": 1
                    },
                    "saleContent": {
                        "itemId": "user:chip",
                        "count": 1000
                    }
                },
                {
                    "name": "open",
                    "displayName": "打开",
                    "typeId": "common.box.open",
                    "mail": "您开启了\\${item}，获得\\${gotContent}",
                    "contents": [
                        {
                            "typeId": "FixedContent",
                            "openTimes": {
                                "start": -1,
                                "stop": -1
                            },
                            "items": [
                                {
                                    "itemId": "item:1002",
                                    "count": 1
                                },
                                {
                                    "itemId": "item:1004",
                                    "count": 1
                                },
                                {
                                    "itemId": "item:3002",
                                    "count": 1
                                }
                            ]
                        }
                    ]
                }
            ]
        },
        {
            "kindId": 1002,
            "typeId": "common.box",
            "displayName": "首充礼包",
            "visibleInBag": 1,
            "desc": "只要充过值即可免费打开，内含30000金币和幸运礼帽，感谢您的支持",
            "singleMode": 1,
            "pic": "${http_download}/hall/item/imgs/item_1002.png",
            "units": {
                "typeId": "common.count",
                "displayName": "个"
            },
            "removeFromBagWhenRemainingZero": 1,
            "removeFromBagWhenExpires": 0,
            "actions": [
                {
                    "name": "open",
                    "displayName": "打开",
                    "typeId": "common.box.open",
                    "mail": "您开启了\\${item}，获得\\${gotContent}",
                    "conditions": [
                        {
                            "typeId": "PAY.LEAST_ONCE",
                            "params": {
                                "failure": "您还没充过值，支持一下吧：)"
                            }
                        }
                    ],
                    "contents": [
                        {
                            "openTimes": {
                                "start": -1,
                                "stop": -1
                            },
                            "typeId": "FixedContent",
                            "weight": 1,
                            "items": [
                                {
                                    "itemId": "user:chip",
                                    "count": 30000
                                },
                                {
                                    "itemId": "item:4100",
                                    "count": 1
                                }
                            ]
                        }
                    ]
                }
            ]
        },
        {
            "kindId": 1003,
            "typeId": "common.box",
            "displayName": "支付宝礼包",
            "visibleInBag": 1,
            "desc": "使用支付宝充值后，即可使用，内含50000金币哦~",
            "singleMode": 1,
            "pic": "${http_download}/hall/item/imgs/item_1003.png",
            "units": {
                "typeId": "common.count",
                "displayName": "个"
            },
            "removeFromBagWhenRemainingZero": 1,
            "removeFromBagWhenExpires": 0,
            "actions": [
                {
                    "name": "open",
                    "displayName": "打开",
                    "typeId": "common.box.open",
                    "mail": "您开启了\\${item}，获得\\${gotContent}",
                    "conditions": [
                        {
                            "typeId": "ALIPAY.LEAST_ONCE",
                            "params": {
                                "failure": "用支付宝支付后才能使用哦"
                            }
                        }
                    ],
                    "contents": [
                        {
                            "openTimes": {
                                "start": -1,
                                "stop": -1
                            },
                            "typeId": "FixedContent",
                            "items": [
                                {
                                    "itemId": "user:chip",
                                    "count": 50000
                                }
                            ]
                        }
                    ]
                }
            ]
        },
        {
            "kindId": 1004,
            "typeId": "common.box",
            "displayName": "新手抽奖礼包",
            "visibleInBag": 1,
            "desc": "可以获得奖券或大量金币，来试试手气吧~",
            "singleMode": 1,
            "pic": "${http_download}/hall/item/imgs/item_1004.png",
            "units": {
                "typeId": "common.count",
                "displayName": "个"
            },
            "removeFromBagWhenRemainingZero": 1,
            "removeFromBagWhenExpires": 0,
            "actions": [
                {
                    "name": "open",
                    "displayName": "打开",
                    "typeId": "common.box.open",
                    "nextItemKindId": 1005,
                    "mail": "您开启了\\${item}，获得了\\${gotContent}，再赠送您一次抽奖机会，明天还能中奖哦~",
                    "contents": [
                        {
                            "typeId": "FixedContent",
                            "openTimes": {
                                "start": -1,
                                "stop": -1
                            },
                            "items": [
                                {
                                    "itemId": "user:chip",
                                    "start": 1000,
                                    "stop": 2000
                                }
                            ]
                        }
                    ]
                }
            ]
        },
        {
            "kindId": 1005,
            "typeId": "common.box",
            "displayName": "新手次日抽奖礼包",
            "visibleInBag": 1,
            "desc": "可以获得奖券或大量金币，来试试手气吧~",
            "singleMode": 1,
            "pic": "${http_download}/hall/item/imgs/item_1004.png",
            "units": {
                "typeId": "common.count",
                "displayName": "个"
            },
            "removeFromBagWhenRemainingZero": 1,
            "removeFromBagWhenExpires": 0,
            "actions": [
                {
                    "name": "open",
                    "displayName": "打开",
                    "typeId": "common.box.open",
                    "nextItemKindId": 1006,
                    "mail": "您开启了\\${item}，获得了\\${gotContent}，再赠送您一次抽奖机会，明天还能中奖哦~",
                    "conditions": [
                        {
                            "typeId": "ITEM.GOT.SECOND_DAYS_LATER",
                            "params": {
                                "failure": "明天才可以打开哦"
                            }
                        }
                    ],
                    "contents": [
                        {
                            "openTimes": {
                                "start": -1,
                                "stop": -1
                            },
                            "typeId": "FixedContent",
                            "weight": 1,
                            "items": [
                                {
                                    "itemId": "user:chip",
                                    "start": 100,
                                    "stop": 500
                                }
                            ]
                        }
                    ]
                }
            ]
        },
        {
            "kindId": 1006,
            "typeId": "common.box",
            "displayName": "新手三日抽奖礼包",
            "visibleInBag": 1,
            "desc": "可以获得奖券或大量金币，来试试手气吧~",
            "singleMode": 1,
            "pic": "${http_download}/hall/item/imgs/item_1004.png",
            "units": {
                "typeId": "common.count",
                "displayName": "个"
            },
            "removeFromBagWhenRemainingZero": 1,
            "removeFromBagWhenExpires": 0,
            "actions": [
                {
                    "name": "open",
                    "displayName": "打开",
                    "typeId": "common.box.open",
                    "mail": "您开启了\\${item}，获得了\\${gotContent}",
                    "conditions": [
                        {
                            "typeId": "ITEM.GOT.SECOND_DAYS_LATER",
                            "params": {
                                "failure": "明天才可以打开哦"
                            }
                        }
                    ],
                    "contents": [
                        {
                            "openTimes": {
                                "start": -1,
                                "stop": -1
                            },
                            "typeId": "FixedContent",
                            "weight": 1,
                            "items": [
                                {
                                    "itemId": "user:chip",
                                    "start": 100,
                                    "stop": 500
                                }
                            ]
                        }
                    ]
                }
            ]
        },
        {
            "kindId": 1007,
            "typeId": "common.simple",
            "displayName": "参赛券",
            "visibleInBag": 1,
            "desc": "报名比赛专用",
            "singleMode": 1,
            "pic": "${http_download}/hall/item/imgs/item_1007.png",
            "units": {
                "typeId": "common.count",
                "displayName": "个"
            },
            "removeFromBagWhenRemainingZero": 1,
            "removeFromBagWhenExpires": 0
        },
        {
            "kindId": 1008,
            "typeId": "common.simple",
            "displayName": "英雄帖",
            "visibleInBag": 1,
            "desc": "神秘道具，请您珍藏",
            "singleMode": 1,
            "pic": "${http_download}/hall/item/imgs/item_1008.png",
            "units": {
                "typeId": "common.count",
                "displayName": "个"
            },
            "removeFromBagWhenRemainingZero": 1,
            "removeFromBagWhenExpires": 0
        },
        {
            "kindId": 1009,
            "typeId": "common.simple",
            "displayName": "内涵玩家专属礼包",
            "visibleInBag": 1,
            "desc": "神秘道具，请您珍藏",
            "singleMode": 1,
            "pic": "${http_download}/hall/item/imgs/item_1009.png",
            "units": {
                "typeId": "common.count",
                "displayName": "个"
            },
            "removeFromBagWhenRemainingZero": 1,
            "removeFromBagWhenExpires": 0
        },
        {
            "kindId": 1010,
            "typeId": "common.box",
            "displayName": "三星S6抽奖礼包",
            "visibleInBag": 1,
            "desc": "三星S6，大量金币，月光之钥等道具，来试试手气吧~",
            "singleMode": 1,
            "pic": "${http_download}/hall/item/imgs/item_1010.png",
            "units": {
                "typeId": "common.count",
                "displayName": "个"
            },
            "removeFromBagWhenRemainingZero": 0,
            "removeFromBagWhenExpires": 0,
            "actions": [
                {
                    "name": "open",
                    "displayName": "打开",
                    "typeId": "common.box.open",
                    "nextItemKindId": 1014,
                    "mail": "您开启了\\${item}，获得了\\${gotContent}",
                    "contents": [
                        {
                            "openTimes": {
                                "start": -1,
                                "stop": -1
                            },
                            "typeId": "RandomContent",
                            "randoms": [
                                {
                                    "typeId": "FixedContent",
                                    "weight": 2500,
                                    "items": [
                                        {
                                            "itemId": "user:chip",
                                            "start": 300,
                                            "stop": 2000
                                        }
                                    ]
                                },
                                {
                                    "typeId": "FixedContent",
                                    "weight": 3500,
                                    "items": [
                                        {
                                            "itemId": "user:chip",
                                            "start": 2000,
                                            "stop": 5000
                                        }
                                    ]
                                },
                                {
                                    "typeId": "FixedContent",
                                    "weight": 1000,
                                    "items": [
                                        {
                                            "itemId": "item:2003",
                                            "count": 2
                                        }
                                    ]
                                },
                                {
                                    "typeId": "FixedContent",
                                    "weight": 500,
                                    "items": [
                                        {
                                            "itemId": "item:3002",
                                            "count": 3
                                        }
                                    ]
                                },
                                {
                                    "typeId": "FixedContent",
                                    "weight": 500,
                                    "items": [
                                        {
                                            "itemId": "item:1007",
                                            "count": 5
                                        }
                                    ]
                                },
                                {
                                    "typeId": "FixedContent",
                                    "weight": 1999,
                                    "items": [
                                        {
                                            "itemId": "user:chip",
                                            "start": 5151,
                                            "stop": 5151
                                        }
                                    ]
                                },
                                {
                                    "typeId": "FixedContent",
                                    "weight": 1,
                                    "items": [
                                        {
                                            "itemId": "item:3001",
                                            "count": 1
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        },
        {
            "kindId": 1011,
            "typeId": "common.simple",
            "displayName": "特惠大礼包",
            "visibleInBag": 1,
            "desc": "单次充值100元，可得100万金币",
            "singleMode": 1,
            "pic": "${http_download}/hall/item/imgs/item_1011.png",
            "units": {
                "typeId": "common.count",
                "displayName": "个"
            },
            "removeFromBagWhenRemainingZero": 1,
            "removeFromBagWhenExpires": 0
        },
        {
            "kindId": 1012,
            "typeId": "common.simple",
            "displayName": "特惠礼包",
            "visibleInBag": 1,
            "desc": "单次充值30元，可得30万金币",
            "singleMode": 1,
            "pic": "${http_download}/hall/item/imgs/item_1002.png",
            "units": {
                "typeId": "common.count",
                "displayName": "个"
            },
            "removeFromBagWhenRemainingZero": 1,
            "removeFromBagWhenExpires": 0
        },
        {
            "kindId": 1013,
            "typeId": "common.box",
            "displayName": "新手礼包",
            "visibleInBag": 1,
            "desc": "新手上路 微微薄礼，请您笑纳~",
            "singleMode": 1,
            "pic": "${http_download}/hall/item/imgs/item_1001.png",
            "units": {
                "typeId": "common.count",
                "displayName": "个"
            },
            "removeFromBagWhenRemainingZero": 1,
            "removeFromBagWhenExpires": 0,
            "actions": [
                {
                    "name": "open",
                    "displayName": "打开",
                    "typeId": "common.box.open",
                    "mail": "您开启了\\${item}，获得\\${gotContent}",
                    "contents": [
                        {
                            "typeId": "FixedContent",
                            "openTimes": {
                                "start": -1,
                                "stop": -1
                            },
                            "items": [
                                {
                                    "itemId": "item:1004",
                                    "count": 1
                                },
                                {
                                    "itemId": "item:3002",
                                    "count": 1
                                }
                            ]
                        }
                    ]
                }
            ]
        },
        {
            "kindId": 1014,
            "typeId": "common.box",
            "displayName": "三星S6抽奖礼包",
            "visibleInBag": 1,
            "desc": "三星S6，大量金币，月光之钥等道具，来试试手气吧~",
            "singleMode": 1,
            "pic": "${http_download}/hall/item/imgs/item_1004.png",
            "units": {
                "typeId": "common.count",
                "displayName": "个"
            },
            "removeFromBagWhenRemainingZero": 0,
            "removeFromBagWhenExpires": 0,
            "actions": [
                {
                    "name": "open",
                    "displayName": "打开",
                    "typeId": "common.box.open",
                    "nextItemKindId": 1015,
                    "mail": "您开启了\\${item}，获得了\\${gotContent}",
                    "conditions": [
                        {
                            "typeId": "ITEM.GOT.SECOND_DAYS_LATER",
                            "params": {
                                "failure": "明天才可以打开哦"
                            }
                        }
                    ],
                    "contents": [
                        {
                            "openTimes": {
                                "start": -1,
                                "stop": -1
                            },
                            "typeId": "RandomContent",
                            "randoms": [
                                {
                                    "typeId": "FixedContent",
                                    "weight": 2500,
                                    "items": [
                                        {
                                            "itemId": "user:chip",
                                            "start": 300,
                                            "stop": 2000
                                        }
                                    ]
                                },
                                {
                                    "typeId": "FixedContent",
                                    "weight": 3500,
                                    "items": [
                                        {
                                            "itemId": "user:chip",
                                            "start": 2000,
                                            "stop": 5000
                                        }
                                    ]
                                },
                                {
                                    "typeId": "FixedContent",
                                    "weight": 1000,
                                    "items": [
                                        {
                                            "itemId": "item:2003",
                                            "count": 2
                                        }
                                    ]
                                },
                                {
                                    "typeId": "FixedContent",
                                    "weight": 500,
                                    "items": [
                                        {
                                            "itemId": "item:3002",
                                            "count": 3
                                        }
                                    ]
                                },
                                {
                                    "typeId": "FixedContent",
                                    "weight": 500,
                                    "items": [
                                        {
                                            "itemId": "item:1007",
                                            "count": 5
                                        }
                                    ]
                                },
                                {
                                    "typeId": "FixedContent",
                                    "weight": 1999,
                                    "items": [
                                        {
                                            "itemId": "user:chip",
                                            "start": 5151,
                                            "stop": 5151
                                        }
                                    ]
                                },
                                {
                                    "typeId": "FixedContent",
                                    "weight": 1,
                                    "items": [
                                        {
                                            "itemId": "item:3001",
                                            "count": 1
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        },
        {
            "kindId": 1015,
            "typeId": "common.box",
            "displayName": "三星S6抽奖礼包",
            "visibleInBag": 1,
            "desc": "三星S6，大量金币，月光之钥等道具，来试试手气吧~",
            "singleMode": 1,
            "pic": "${http_download}/hall/item/imgs/item_1004.png",
            "units": {
                "typeId": "common.count",
                "displayName": "个"
            },
            "removeFromBagWhenRemainingZero": 0,
            "removeFromBagWhenExpires": 0,
            "actions": [
                {
                    "name": "open",
                    "displayName": "打开",
                    "typeId": "common.box.open",
                    "mail": "您开启了\\${item}，获得了\\${gotContent}",
                    "conditions": [
                        {
                            "typeId": "ITEM.GOT.SECOND_DAYS_LATER",
                            "params": {
                                "failure": "明天才可以打开哦"
                            }
                        }
                    ],
                    "contents": [
                        {
                            "openTimes": {
                                "start": -1,
                                "stop": -1
                            },
                            "typeId": "RandomContent",
                            "randoms": [
                                {
                                    "typeId": "FixedContent",
                                    "weight": 2500,
                                    "items": [
                                        {
                                            "itemId": "user:chip",
                                            "start": 300,
                                            "stop": 2000
                                        }
                                    ]
                                },
                                {
                                    "typeId": "FixedContent",
                                    "weight": 3500,
                                    "items": [
                                        {
                                            "itemId": "user:chip",
                                            "start": 2000,
                                            "stop": 5000
                                        }
                                    ]
                                },
                                {
                                    "typeId": "FixedContent",
                                    "weight": 1000,
                                    "items": [
                                        {
                                            "itemId": "item:2003",
                                            "count": 2
                                        }
                                    ]
                                },
                                {
                                    "typeId": "FixedContent",
                                    "weight": 500,
                                    "items": [
                                        {
                                            "itemId": "item:3002",
                                            "count": 3
                                        }
                                    ]
                                },
                                {
                                    "typeId": "FixedContent",
                                    "weight": 500,
                                    "items": [
                                        {
                                            "itemId": "item:1007",
                                            "count": 5
                                        }
                                    ]
                                },
                                {
                                    "typeId": "FixedContent",
                                    "weight": 1999,
                                    "items": [
                                        {
                                            "itemId": "user:chip",
                                            "start": 5151,
                                            "stop": 5151
                                        }
                                    ]
                                },
                                {
                                    "typeId": "FixedContent",
                                    "weight": 1,
                                    "items": [
                                        {
                                            "itemId": "item:3001",
                                            "count": 1
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        },
        {
            "kindId": 1016,
            "typeId": "common.box",
            "displayName": "端午礼包",
            "visibleInBag": 1,
            "desc": "由“端午使者”发放的神秘礼包",
            "singleMode": 1,
            "pic": "${http_download}/hall/item/imgs/item_1016.png",
            "units": {
                "typeId": "common.count",
                "displayName": "个"
            },
            "removeFromBagWhenRemainingZero": 1,
            "removeFromBagWhenExpires": 0,
            "actions": [
                {
                    "name": "open",
                    "displayName": "打开",
                    "typeId": "common.box.open",
                    "mail": "您开启了\\${item}，获得了\\${gotContent}",
                    "contents": [
                        {
                            "openTimes": {
                                "start": -1,
                                "stop": -1
                            },
                            "typeId": "FixedContent",
                            "weight": 1,
                            "items": [
                                {
                                    "itemId": "user:chip",
                                    "count": 500000
                                },
                                {
                                    "itemId": "user:coupon",
                                    "count": 100
                                },
                                {
                                    "itemId": "item:4109",
                                    "count": 7
                                },
                                {
                                    "itemId": "item:4110",
                                    "count": 7
                                }
                            ]
                        }
                    ]
                }
            ]
        },
        {
            "kindId": 1017,
            "typeId": "common.simple",
            "displayName": "智运会复赛门票",
            "visibleInBag": 1,
            "desc": "智运会复赛门票",
            "singleMode": 1,
            "pic": "${http_download}/hall/item/imgs/item_1017.png",
            "units": {
                "typeId": "common.count",
                "displayName": "张"
            },
            "removeFromBagWhenRemainingZero": 1,
            "removeFromBagWhenExpires": 0
        },
        {
            "kindId": 2001,
            "typeId": "common.simple",
            "displayName": "改名卡",
            "visibleInBag": 1,
            "desc": "换个名字迎好运吧~",
            "singleMode": 1,
            "pic": "${http_download}/hall/item/imgs/item_2001.png",
            "units": {
                "typeId": "common.count",
                "displayName": "个"
            },
            "removeFromBagWhenRemainingZero": 1,
            "removeFromBagWhenExpires": 0
        },
        {
            "kindId": 2003,
            "typeId": "common.simple",
            "displayName": "记牌器",
            "visibleInBag": 1,
            "desc": "用于斗地主牌桌记牌，好记性不如烂笔头",
            "singleMode": 1,
            "pic": "${http_download}/hall/item/imgs/item_2003.png",
            "units": {
                "typeId": "common.day",
                "displayName": "天"
            },
            "removeFromBagWhenRemainingZero": 0,
            "removeFromBagWhenExpires": 1
        },
        {
            "kindId": 3001,
            "typeId": "common.simple",
            "displayName": "月光之钥",
            "visibleInBag": 1,
            "desc": "可开启月光宝盒，获得多种神秘奖励",
            "singleMode": 1,
            "pic": "${http_download}/hall/item/imgs/item_3001.png",
            "units": {
                "typeId": "common.count",
                "displayName": "把"
            },
            "removeFromBagWhenRemainingZero": 1,
            "removeFromBagWhenExpires": 0
        },
        {
            "kindId": 3002,
            "typeId": "common.box",
            "displayName": "月光宝盒",
            "visibleInBag": 1,
            "desc": "获得大量金币或奖券，必须使用月光之钥开启",
            "singleMode": 1,
            "pic": "${http_download}/hall/item/imgs/item_3002.png",
            "units": {
                "typeId": "common.count",
                "displayName": "个"
            },
            "removeFromBagWhenRemainingZero": 0,
            "removeFromBagWhenExpires": 0,
            "actions": [
                {
                    "name": "open",
                    "displayName": "打开",
                    "typeId": "common.box.open",
                    "mail": "您开启了\\${item}，获得了\\${gotContent}",
                    "bindings": [
                        {
                            "itemId": 3001,
                            "count": 1,
                            "params": {
                                "failure": "需要购买月光之钥",
                                "payOrder": {
                                    "shelves": [
                                        "coin",
                                        "diamond"
                                    ],
                                    "contains": {
                                        "itemId": "item:3001",
                                        "count": 1
                                    }
                                }
                            }
                        }
                    ],
                    "contents": [
                        {
                            "openTimes": {
                                "start": 0,
                                "stop": 3
                            },
                            "typeId": "RandomContent",
                            "randoms": [
                                {
                                    "typeId": "FixedContent",
                                    "weight": 350,
                                    "items": [
                                        {
                                            "itemId": "user:chip",
                                            "start": 26000,
                                            "stop": 28000
                                        }
                                    ]
                                },
                                {
                                    "typeId": "FixedContent",
                                    "weight": 400,
                                    "items": [
                                        {
                                            "itemId": "user:chip",
                                            "start": 30000,
                                            "stop": 34000
                                        }
                                    ]
                                },
                                {
                                    "typeId": "FixedContent",
                                    "weight": 100,
                                    "items": [
                                        {
                                            "itemId": "user:chip",
                                            "start": 40000,
                                            "stop": 40000
                                        }
                                    ]
                                },
                                {
                                    "typeId": "FixedContent",
                                    "weight": 100,
                                    "items": [
                                        {
                                            "itemId": "user:chip",
                                            "start": 60000,
                                            "stop": 60000
                                        }
                                    ]
                                },
                                {
                                    "typeId": "FixedContent",
                                    "weight": 49,
                                    "items": [
                                        {
                                            "itemId": "user:chip",
                                            "start": 100000,
                                            "stop": 100000
                                        }
                                    ]
                                },
                                {
                                    "typeId": "FixedContent",
                                    "weight": 1,
                                    "items": [
                                        {
                                            "itemId": "user:chip",
                                            "start": 20000,
                                            "stop": 20000
                                        },
                                        {
                                            "itemId": "user:coupon",
                                            "count": 500
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "openTimes": {
                                "start": 4,
                                "stop": 10
                            },
                            "typeId": "RandomContent",
                            "randoms": [
                                {
                                    "typeId": "FixedContent",
                                    "weight": 100,
                                    "items": [
                                        {
                                            "itemId": "user:chip",
                                            "start": 10000,
                                            "stop": 10000
                                        }
                                    ]
                                },
                                {
                                    "typeId": "FixedContent",
                                    "weight": 400,
                                    "items": [
                                        {
                                            "itemId": "user:chip",
                                            "start": 21000,
                                            "stop": 25000
                                        }
                                    ]
                                },
                                {
                                    "typeId": "FixedContent",
                                    "weight": 200,
                                    "items": [
                                        {
                                            "itemId": "user:chip",
                                            "start": 22000,
                                            "stop": 28000
                                        }
                                    ]
                                },
                                {
                                    "typeId": "FixedContent",
                                    "weight": 150,
                                    "items": [
                                        {
                                            "itemId": "user:chip",
                                            "start": 30000,
                                            "stop": 34000
                                        }
                                    ]
                                },
                                {
                                    "typeId": "FixedContent",
                                    "weight": 62,
                                    "items": [
                                        {
                                            "itemId": "user:chip",
                                            "start": 40000,
                                            "stop": 40000
                                        }
                                    ]
                                },
                                {
                                    "typeId": "FixedContent",
                                    "weight": 55,
                                    "items": [
                                        {
                                            "itemId": "user:chip",
                                            "start": 60000,
                                            "stop": 60000
                                        },
                                        {
                                            "itemId": "user:coupon",
                                            "count": 980
                                        }
                                    ]
                                },
                                {
                                    "typeId": "FixedContent",
                                    "weight": 32,
                                    "items": [
                                        {
                                            "itemId": "user:chip",
                                            "start": 100000,
                                            "stop": 100000
                                        }
                                    ]
                                },
                                {
                                    "typeId": "FixedContent",
                                    "weight": 1,
                                    "items": [
                                        {
                                            "itemId": "user:chip",
                                            "start": 20000,
                                            "stop": 20000
                                        },
                                        {
                                            "itemId": "user:coupon",
                                            "count": 500
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "openTimes": {
                                "start": 11,
                                "stop": -1
                            },
                            "typeId": "RandomContent",
                            "randoms": [
                                {
                                    "typeId": "FixedContent",
                                    "weight": 77,
                                    "items": [
                                        {
                                            "itemId": "user:chip",
                                            "start": 10000,
                                            "stop": 10000
                                        }
                                    ]
                                },
                                {
                                    "typeId": "FixedContent",
                                    "weight": 150,
                                    "items": [
                                        {
                                            "itemId": "user:chip",
                                            "start": 15000,
                                            "stop": 15000
                                        }
                                    ]
                                },
                                {
                                    "typeId": "FixedContent",
                                    "weight": 400,
                                    "items": [
                                        {
                                            "itemId": "user:chip",
                                            "start": 18000,
                                            "stop": 22000
                                        }
                                    ]
                                },
                                {
                                    "typeId": "FixedContent",
                                    "weight": 200,
                                    "items": [
                                        {
                                            "itemId": "user:chip",
                                            "start": 20000,
                                            "stop": 25000
                                        }
                                    ]
                                },
                                {
                                    "typeId": "FixedContent",
                                    "weight": 100,
                                    "items": [
                                        {
                                            "itemId": "user:chip",
                                            "start": 30000,
                                            "stop": 34000
                                        }
                                    ]
                                },
                                {
                                    "typeId": "FixedContent",
                                    "weight": 350,
                                    "items": [
                                        {
                                            "itemId": "user:chip",
                                            "start": 40000,
                                            "stop": 40000
                                        }
                                    ]
                                },
                                {
                                    "typeId": "FixedContent",
                                    "weight": 350,
                                    "items": [
                                        {
                                            "itemId": "user:chip",
                                            "start": 60000,
                                            "stop": 60000
                                        },
                                        {
                                            "itemId": "user:coupon",
                                            "count": 980
                                        }
                                    ]
                                },
                                {
                                    "typeId": "FixedContent",
                                    "weight": 2,
                                    "items": [
                                        {
                                            "itemId": "user:chip",
                                            "start": 100000,
                                            "stop": 100000
                                        }
                                    ]
                                },
                                {
                                    "typeId": "FixedContent",
                                    "weight": 1,
                                    "items": [
                                        {
                                            "itemId": "user:chip",
                                            "start": 20000,
                                            "stop": 20000
                                        },
                                        {
                                            "itemId": "user:coupon",
                                            "count": 500
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        },
        {
            "kindId": 3003,
            "typeId": "common.simple",
            "displayName": "马年金砖",
            "visibleInBag": 1,
            "desc": "马年行大运，富人必备，馈赠佳品，可出售，价值98万筹码",
            "singleMode": 1,
            "pic": "${http_download}/hall/item/imgs/item_3003.png",
            "units": {
                "typeId": "common.count",
                "displayName": "块"
            },
            "removeFromBagWhenRemainingZero": 1,
            "removeFromBagWhenExpires": 0
        },
        {
            "kindId": 88,
            "typeId": "common.memberCard",
            "displayName": "会员卡",
            "visibleInBag": 1,
            "desc": "尊贵的会员，每天登陆可多领3万金币，并拥有会员专属标志、，会员互动表情、，双倍积分等会员特权",
            "singleMode": 1,
            "pic": "${http_download}/hall/item/imgs/item_88_new.png",
            "units": {
                "typeId": "common.day",
                "displayName": "天"
            },
            "removeFromBagWhenRemainingZero": 0,
            "removeFromBagWhenExpires": 1,
            "actions": [
                {
                    "name": "checkin",
                    "displayName": "打开",
                    "typeId": "common.checkin",
                    "mail": "会员登录奖励\\${gotContent}",
                    "content": {
                        "typeId": "FixedContent",
                        "desc": "30000金币",
                        "items": [
                            {
                                "itemId": "user:chip",
                                "count": 30000
                            }
                        ]
                    }
                }
            ]
        },
        {
            "kindId": 4001,
            "typeId": "common.decroation",
            "displayName": "VIP标识",
            "visibleInBag": 0,
            "desc": "VIP标识",
            "singleMode": 1,
            "pic": "",
            "units": {
                "typeId": "common.day",
                "displayName": "天"
            },
            "removeFromBagWhenRemainingZero": 0,
            "removeFromBagWhenExpires": 1,
            "localRes": {
                "resName": "tip_vip_1"
            },
            "pos": {
                "zOrder": 25
            },
            "masks": 2,
            "actions": [
                {
                    "name": "wear",
                    "displayName": "佩戴",
                    "typeId": "common.decroation.wear"
                },
                {
                    "name": "unwear",
                    "displayName": "取消佩戴",
                    "typeId": "common.decroation.unwear"
                }
            ]
        },
        {
            "kindId": 4002,
            "typeId": "common.decroation",
            "displayName": "VIP2标识",
            "visibleInBag": 0,
            "desc": "VIP2标识",
            "singleMode": 1,
            "pic": "",
            "units": {
                "typeId": "common.day",
                "displayName": "天"
            },
            "removeFromBagWhenRemainingZero": 0,
            "removeFromBagWhenExpires": 1,
            "localRes": {
                "resName": "tip_vip_2"
            },
            "pos": {
                "zOrder": 25
            },
            "masks": 2,
            "actions": [
                {
                    "name": "wear",
                    "displayName": "佩戴",
                    "typeId": "common.decroation.wear"
                },
                {
                    "name": "unwear",
                    "displayName": "取消佩戴",
                    "typeId": "common.decroation.unwear"
                }
            ]
        },
        {
            "kindId": 4003,
            "typeId": "common.decroation",
            "displayName": "VIP3标识",
            "visibleInBag": 0,
            "desc": "VIP3标识",
            "singleMode": 1,
            "pic": "",
            "units": {
                "typeId": "common.day",
                "displayName": "天"
            },
            "removeFromBagWhenRemainingZero": 0,
            "removeFromBagWhenExpires": 1,
            "localRes": {
                "resName": "tip_vip_3"
            },
            "pos": {
                "zOrder": 25
            },
            "masks": 2,
            "actions": [
                {
                    "name": "wear",
                    "displayName": "佩戴",
                    "typeId": "common.decroation.wear"
                },
                {
                    "name": "unwear",
                    "displayName": "取消佩戴",
                    "typeId": "common.decroation.unwear"
                }
            ]
        },
        {
            "kindId": 4004,
            "typeId": "common.decroation",
            "displayName": "VIP4标识",
            "visibleInBag": 0,
            "desc": "VIP4标识",
            "singleMode": 1,
            "pic": "",
            "units": {
                "typeId": "common.day",
                "displayName": "天"
            },
            "removeFromBagWhenRemainingZero": 0,
            "removeFromBagWhenExpires": 1,
            "localRes": {
                "resName": "tip_vip_4"
            },
            "pos": {
                "zOrder": 25
            },
            "masks": 2,
            "actions": [
                {
                    "name": "wear",
                    "displayName": "佩戴",
                    "typeId": "common.decroation.wear"
                },
                {
                    "name": "unwear",
                    "displayName": "取消佩戴",
                    "typeId": "common.decroation.unwear"
                }
            ]
        },
        {
            "kindId": 4005,
            "typeId": "common.decroation",
            "displayName": "VIP5标识",
            "visibleInBag": 0,
            "desc": "VIP5标识",
            "singleMode": 1,
            "pic": "",
            "units": {
                "typeId": "common.day",
                "displayName": "天"
            },
            "removeFromBagWhenRemainingZero": 0,
            "removeFromBagWhenExpires": 1,
            "localRes": {
                "resName": "tip_vip_5"
            },
            "pos": {
                "zOrder": 25
            },
            "masks": 2,
            "actions": [
                {
                    "name": "wear",
                    "displayName": "佩戴",
                    "typeId": "common.decroation.wear"
                },
                {
                    "name": "unwear",
                    "displayName": "取消佩戴",
                    "typeId": "common.decroation.unwear"
                }
            ]
        },
        {
            "kindId": 4006,
            "typeId": "common.decroation",
            "displayName": "VIP红卡标识",
            "visibleInBag": 0,
            "desc": "VIP红卡标识",
            "singleMode": 1,
            "pic": "",
            "units": {
                "typeId": "common.day",
                "displayName": "天"
            },
            "removeFromBagWhenRemainingZero": 0,
            "removeFromBagWhenExpires": 1,
            "remoteRes": {
                "type": "img",
                "imgUrl": "${http_download}/hall/item/imgs/tip_vip_red.png",
                "pos": {
                    "posType": "head_lower_right",
                    "anchorPoint": {
                        "x": 0.95,
                        "y": 0.15
                    }
                }
            },
            "pos": {
                "zOrder": 25
            },
            "masks": 2,
            "actions": [
                {
                    "name": "wear",
                    "displayName": "佩戴",
                    "typeId": "common.decroation.wear"
                },
                {
                    "name": "unwear",
                    "displayName": "取消佩戴",
                    "typeId": "common.decroation.unwear"
                }
            ]
        },
        {
            "kindId": 4007,
            "typeId": "common.decroation",
            "displayName": "VIP金卡标识",
            "visibleInBag": 0,
            "desc": "VIP金卡标识",
            "singleMode": 1,
            "pic": "",
            "units": {
                "typeId": "common.day",
                "displayName": "天"
            },
            "removeFromBagWhenRemainingZero": 0,
            "removeFromBagWhenExpires": 1,
            "remoteRes": {
                "type": "img",
                "imgUrl": "${http_download}/hall/item/imgs/tip_vip_golden.png",
                "pos": {
                    "posType": "head_lower_right",
                    "anchorPoint": {
                        "x": 0.95,
                        "y": 0.15
                    }
                }
            },
            "pos": {
                "zOrder": 25
            },
            "masks": 2,
            "actions": [
                {
                    "name": "wear",
                    "displayName": "佩戴",
                    "typeId": "common.decroation.wear"
                },
                {
                    "name": "unwear",
                    "displayName": "取消佩戴",
                    "typeId": "common.decroation.unwear"
                }
            ]
        },
        {
            "kindId": 4008,
            "typeId": "common.decroation",
            "displayName": "VIP黑卡标识",
            "visibleInBag": 0,
            "desc": "VIP黑卡标识",
            "singleMode": 1,
            "pic": "",
            "units": {
                "typeId": "common.day",
                "displayName": "天"
            },
            "removeFromBagWhenRemainingZero": 0,
            "removeFromBagWhenExpires": 1,
            "remoteRes": {
                "type": "img",
                "imgUrl": "${http_download}/hall/item/imgs/tip_vip_black.png",
                "pos": {
                    "posType": "head_lower_right",
                    "anchorPoint": {
                        "x": 0.95,
                        "y": 0.15
                    }
                }
            },
            "pos": {
                "zOrder": 25
            },
            "masks": 2,
            "actions": [
                {
                    "name": "wear",
                    "displayName": "佩戴",
                    "typeId": "common.decroation.wear"
                },
                {
                    "name": "unwear",
                    "displayName": "取消佩戴",
                    "typeId": "common.decroation.unwear"
                }
            ]
        },
        {
            "kindId": 4100,
            "typeId": "common.decroation",
            "displayName": "幸运礼帽",
            "visibleInBag": 1,
            "desc": "使用后可佩戴，幸运礼帽",
            "singleMode": 1,
            "pic": "${http_download}/hall/item/imgs/item_4100.png",
            "units": {
                "typeId": "common.day",
                "displayName": "天"
            },
            "removeFromBagWhenRemainingZero": 0,
            "removeFromBagWhenExpires": 1,
            "localRes": {
                "resName": "hat_lucky_hat"
            },
            "pos": {
                "zOrder": 40
            },
            "masks": 4,
            "actions": [
                {
                    "name": "wear",
                    "displayName": "佩戴",
                    "typeId": "common.decroation.wear"
                },
                {
                    "name": "unwear",
                    "displayName": "取消佩戴",
                    "typeId": "common.decroation.unwear"
                }
            ]
        },
        {
            "kindId": 4101,
            "typeId": "common.decroation",
            "displayName": "神秘礼帽",
            "visibleInBag": 1,
            "desc": "使用后可佩戴，神秘礼帽",
            "singleMode": 1,
            "pic": "${http_download}/hall/item/imgs/item_4101.png",
            "units": {
                "typeId": "common.day",
                "displayName": "天"
            },
            "removeFromBagWhenRemainingZero": 0,
            "removeFromBagWhenExpires": 1,
            "localRes": {
                "resName": "hat_mystery_hat"
            },
            "pos": {
                "zOrder": 40
            },
            "masks": 4,
            "actions": [
                {
                    "name": "wear",
                    "displayName": "佩戴",
                    "typeId": "common.decroation.wear"
                },
                {
                    "name": "unwear",
                    "displayName": "取消佩戴",
                    "typeId": "common.decroation.unwear"
                }
            ]
        },
        {
            "kindId": 4102,
            "typeId": "common.decroation",
            "displayName": "绅士礼帽",
            "visibleInBag": 1,
            "desc": "使用后可佩戴，绅士礼帽",
            "singleMode": 1,
            "pic": "${http_download}/hall/item/imgs/item_4102.png",
            "units": {
                "typeId": "common.day",
                "displayName": "天"
            },
            "removeFromBagWhenRemainingZero": 0,
            "removeFromBagWhenExpires": 1,
            "localRes": {
                "resName": "hat_gentleman_hat"
            },
            "pos": {
                "zOrder": 40
            },
            "masks": 4,
            "actions": [
                {
                    "name": "wear",
                    "displayName": "佩戴",
                    "typeId": "common.decroation.wear"
                },
                {
                    "name": "unwear",
                    "displayName": "取消佩戴",
                    "typeId": "common.decroation.unwear"
                }
            ]
        },
        {
            "kindId": 4103,
            "typeId": "common.decroation",
            "displayName": "牛仔帽",
            "visibleInBag": 1,
            "desc": "使用后可佩戴，牛仔帽",
            "singleMode": 1,
            "pic": "${http_download}/hall/item/imgs/item_4103.png",
            "units": {
                "typeId": "common.day",
                "displayName": "天"
            },
            "removeFromBagWhenRemainingZero": 0,
            "removeFromBagWhenExpires": 1,
            "localRes": {
                "resName": "hat_cowboy_hat"
            },
            "pos": {
                "zOrder": 40
            },
            "masks": 4,
            "actions": [
                {
                    "name": "wear",
                    "displayName": "佩戴",
                    "typeId": "common.decroation.wear"
                },
                {
                    "name": "unwear",
                    "displayName": "取消佩戴",
                    "typeId": "common.decroation.unwear"
                }
            ]
        },
        {
            "kindId": 4104,
            "typeId": "common.decroation",
            "displayName": "多彩皇冠",
            "visibleInBag": 1,
            "desc": "使用后可佩戴，多彩皇冠",
            "singleMode": 1,
            "pic": "${http_download}/hall/item/imgs/item_4104.png",
            "units": {
                "typeId": "common.day",
                "displayName": "天"
            },
            "removeFromBagWhenRemainingZero": 0,
            "removeFromBagWhenExpires": 1,
            "localRes": {
                "resName": "hat_colorful_crown"
            },
            "pos": {
                "zOrder": 40
            },
            "masks": 4,
            "actions": [
                {
                    "name": "wear",
                    "displayName": "佩戴",
                    "typeId": "common.decroation.wear"
                },
                {
                    "name": "unwear",
                    "displayName": "取消佩戴",
                    "typeId": "common.decroation.unwear"
                }
            ]
        },
        {
            "kindId": 4105,
            "typeId": "common.decroation",
            "displayName": "精灵花冠",
            "visibleInBag": 1,
            "desc": "使用后可佩戴，精灵花冠",
            "singleMode": 1,
            "pic": "${http_download}/hall/item/imgs/item_4105.png",
            "units": {
                "typeId": "common.day",
                "displayName": "天"
            },
            "removeFromBagWhenRemainingZero": 0,
            "removeFromBagWhenExpires": 1,
            "localRes": {
                "resName": "hat_elf_wreath"
            },
            "pos": {
                "zOrder": 40
            },
            "masks": 4,
            "actions": [
                {
                    "name": "wear",
                    "displayName": "佩戴",
                    "typeId": "common.decroation.wear"
                },
                {
                    "name": "unwear",
                    "displayName": "取消佩戴",
                    "typeId": "common.decroation.unwear"
                }
            ]
        },
        {
            "kindId": 4106,
            "typeId": "common.decroation",
            "displayName": "恶魔角饰",
            "visibleInBag": 1,
            "desc": "使用后可佩戴，恶魔角饰",
            "singleMode": 1,
            "pic": "${http_download}/hall/item/imgs/item_4106.png",
            "units": {
                "typeId": "common.day",
                "displayName": "天"
            },
            "removeFromBagWhenRemainingZero": 0,
            "removeFromBagWhenExpires": 1,
            "localRes": {
                "resName": "hat_demon_horn"
            },
            "pos": {
                "zOrder": 40
            },
            "masks": 4,
            "actions": [
                {
                    "name": "wear",
                    "displayName": "佩戴",
                    "typeId": "common.decroation.wear"
                },
                {
                    "name": "unwear",
                    "displayName": "取消佩戴",
                    "typeId": "common.decroation.unwear"
                }
            ]
        },
        {
            "kindId": 4107,
            "typeId": "common.decroation",
            "displayName": "天使头环",
            "visibleInBag": 1,
            "desc": "使用后可佩戴，天使头环",
            "singleMode": 1,
            "pic": "${http_download}/hall/item/imgs/item_4107.png",
            "units": {
                "typeId": "common.day",
                "displayName": "天"
            },
            "removeFromBagWhenRemainingZero": 0,
            "removeFromBagWhenExpires": 1,
            "localRes": {
                "resName": "hat_angel_halo"
            },
            "pos": {
                "zOrder": 40
            },
            "masks": 4,
            "actions": [
                {
                    "name": "wear",
                    "displayName": "佩戴",
                    "typeId": "common.decroation.wear"
                },
                {
                    "name": "unwear",
                    "displayName": "取消佩戴",
                    "typeId": "common.decroation.unwear"
                }
            ]
        },
        {
            "kindId": 4108,
            "typeId": "common.decroation",
            "displayName": "荣耀皇冠",
            "visibleInBag": 1,
            "desc": "使用后可佩戴，荣耀皇冠",
            "singleMode": 1,
            "pic": "${http_download}/hall/item/imgs/item_4108.png",
            "units": {
                "typeId": "common.day",
                "displayName": "天"
            },
            "removeFromBagWhenRemainingZero": 0,
            "removeFromBagWhenExpires": 1,
            "localRes": {
                "resName": "hat_glory_crown"
            },
            "pos": {
                "zOrder": 40
            },
            "masks": 4,
            "actions": [
                {
                    "name": "wear",
                    "displayName": "佩戴",
                    "typeId": "common.decroation.wear"
                },
                {
                    "name": "unwear",
                    "displayName": "取消佩戴",
                    "typeId": "common.decroation.unwear"
                }
            ]
        },
        {
            "kindId": 4109,
            "typeId": "common.decroation",
            "displayName": "青春派(男)",
            "visibleInBag": 1,
            "desc": "使用后可佩戴，青春派动态头像(男)",
            "singleMode": 1,
            "pic": "${http_download}/hall/item/imgs/item_4109.png",
            "units": {
                "typeId": "common.day",
                "displayName": "天"
            },
            "removeFromBagWhenRemainingZero": 0,
            "removeFromBagWhenExpires": 1,
            "localRes": {
                "resName": "head_young_m"
            },
            "pos": {
                "zOrder": 10
            },
            "masks": 8,
            "actions": [
                {
                    "name": "wear",
                    "displayName": "佩戴",
                    "typeId": "common.decroation.wear"
                },
                {
                    "name": "unwear",
                    "displayName": "取消佩戴",
                    "typeId": "common.decroation.unwear"
                }
            ]
        },
        {
            "kindId": 4110,
            "typeId": "common.decroation",
            "displayName": "青春派(女)",
            "visibleInBag": 1,
            "desc": "使用后可佩戴，青春派动态头像(女)",
            "singleMode": 1,
            "pic": "${http_download}/hall/item/imgs/item_4110.png",
            "units": {
                "typeId": "common.day",
                "displayName": "天"
            },
            "removeFromBagWhenRemainingZero": 0,
            "removeFromBagWhenExpires": 1,
            "localRes": {
                "resName": "head_young_f"
            },
            "pos": {
                "zOrder": 10
            },
            "masks": 8,
            "actions": [
                {
                    "name": "wear",
                    "displayName": "佩戴",
                    "typeId": "common.decroation.wear"
                },
                {
                    "name": "unwear",
                    "displayName": "取消佩戴",
                    "typeId": "common.decroation.unwear"
                }
            ]
        },
        {
            "kindId": 4111,
            "typeId": "common.decroation",
            "displayName": "魅力族(男)",
            "visibleInBag": 1,
            "desc": "使用后可佩戴，魅力族动态头像(男)",
            "singleMode": 1,
            "pic": "${http_download}/hall/item/imgs/item_4111.png",
            "units": {
                "typeId": "common.day",
                "displayName": "天"
            },
            "removeFromBagWhenRemainingZero": 0,
            "removeFromBagWhenExpires": 1,
            "localRes": {
                "resName": "head_charm_m"
            },
            "pos": {
                "zOrder": 10
            },
            "masks": 8,
            "actions": [
                {
                    "name": "wear",
                    "displayName": "佩戴",
                    "typeId": "common.decroation.wear"
                },
                {
                    "name": "unwear",
                    "displayName": "取消佩戴",
                    "typeId": "common.decroation.unwear"
                }
            ]
        },
        {
            "kindId": 4112,
            "typeId": "common.decroation",
            "displayName": "魅力族(女)",
            "visibleInBag": 1,
            "desc": "使用后可佩戴，魅力族动态头像(女)",
            "singleMode": 1,
            "pic": "${http_download}/hall/item/imgs/item_4112.png",
            "units": {
                "typeId": "common.day",
                "displayName": "天"
            },
            "removeFromBagWhenRemainingZero": 0,
            "removeFromBagWhenExpires": 1,
            "localRes": {
                "resName": "head_charm_f"
            },
            "pos": {
                "zOrder": 10
            },
            "masks": 8,
            "actions": [
                {
                    "name": "wear",
                    "displayName": "佩戴",
                    "typeId": "common.decroation.wear"
                },
                {
                    "name": "unwear",
                    "displayName": "取消佩戴",
                    "typeId": "common.decroation.unwear"
                }
            ]
        },
        {
            "kindId": 4113,
            "typeId": "common.decroation",
            "displayName": "幸运项链",
            "visibleInBag": 1,
            "desc": "使用后可在牌桌内激发，“幸运项链”特效",
            "singleMode": 1,
            "pic": "${http_download}/hall/item/imgs/item_4113.png",
            "units": {
                "typeId": "common.day",
                "displayName": "天"
            },
            "removeFromBagWhenRemainingZero": 0,
            "removeFromBagWhenExpires": 1,
            "localRes": {
                "resName": "item_lucky_necklace"
            },
            "pos": {
                "zOrder": 30
            },
            "masks": 16,
            "actions": [
                {
                    "name": "wear",
                    "displayName": "佩戴",
                    "typeId": "common.decroation.wear"
                },
                {
                    "name": "unwear",
                    "displayName": "取消佩戴",
                    "typeId": "common.decroation.unwear"
                }
            ]
        },
        {
            "kindId": 4114,
            "typeId": "common.decroation",
            "displayName": "命运酒杯",
            "visibleInBag": 1,
            "desc": "使用后可在牌桌内激发，“命运酒杯”特效",
            "singleMode": 1,
            "pic": "${http_download}/hall/item/imgs/item_4114.png",
            "units": {
                "typeId": "common.day",
                "displayName": "天"
            },
            "removeFromBagWhenRemainingZero": 0,
            "removeFromBagWhenExpires": 1,
            "localRes": {
                "resName": "item_fate_cup"
            },
            "pos": {
                "zOrder": 30
            },
            "masks": 16,
            "actions": [
                {
                    "name": "wear",
                    "displayName": "佩戴",
                    "typeId": "common.decroation.wear"
                },
                {
                    "name": "unwear",
                    "displayName": "取消佩戴",
                    "typeId": "common.decroation.unwear"
                }
            ]
        },
        {
            "kindId": 4115,
            "typeId": "common.decroation",
            "displayName": "绅士手杖",
            "visibleInBag": 1,
            "desc": "使用后可在牌桌内激发，“绅士手杖”特效",
            "singleMode": 1,
            "pic": "${http_download}/hall/item/imgs/item_4115.png",
            "units": {
                "typeId": "common.day",
                "displayName": "天"
            },
            "removeFromBagWhenRemainingZero": 0,
            "removeFromBagWhenExpires": 1,
            "localRes": {
                "resName": "item_gentleman_staff"
            },
            "pos": {
                "zOrder": 30
            },
            "masks": 16,
            "actions": [
                {
                    "name": "wear",
                    "displayName": "佩戴",
                    "typeId": "common.decroation.wear"
                },
                {
                    "name": "unwear",
                    "displayName": "取消佩戴",
                    "typeId": "common.decroation.unwear"
                }
            ]
        },
        {
            "kindId": 4116,
            "typeId": "common.decroation",
            "displayName": "魔法棒",
            "visibleInBag": 1,
            "desc": "使用后可在牌桌内激发，“魔法棒”特效",
            "singleMode": 1,
            "pic": "${http_download}/hall/item/imgs/item_4116.png",
            "units": {
                "typeId": "common.day",
                "displayName": "天"
            },
            "removeFromBagWhenRemainingZero": 0,
            "removeFromBagWhenExpires": 1,
            "localRes": {
                "resName": "item_wand"
            },
            "pos": {
                "zOrder": 30
            },
            "masks": 16,
            "actions": [
                {
                    "name": "wear",
                    "displayName": "佩戴",
                    "typeId": "common.decroation.wear"
                },
                {
                    "name": "unwear",
                    "displayName": "取消佩戴",
                    "typeId": "common.decroation.unwear"
                }
            ]
        },
        {
            "kindId": 4117,
            "typeId": "common.decroation",
            "displayName": "神秘烟斗",
            "visibleInBag": 1,
            "desc": "使用后可在牌桌内激发，“神秘烟斗”特效",
            "singleMode": 1,
            "pic": "${http_download}/hall/item/imgs/item_4117.png",
            "units": {
                "typeId": "common.day",
                "displayName": "天"
            },
            "removeFromBagWhenRemainingZero": 0,
            "removeFromBagWhenExpires": 1,
            "localRes": {
                "resName": "item_mystery_pipe"
            },
            "pos": {
                "zOrder": 30
            },
            "masks": 16,
            "actions": [
                {
                    "name": "wear",
                    "displayName": "佩戴",
                    "typeId": "common.decroation.wear"
                },
                {
                    "name": "unwear",
                    "displayName": "取消佩戴",
                    "typeId": "common.decroation.unwear"
                }
            ]
        },
        {
            "kindId": 4118,
            "typeId": "common.decroation",
            "displayName": "左轮手枪",
            "visibleInBag": 1,
            "desc": "使用后可在牌桌内激发，“左轮手枪”特效",
            "singleMode": 1,
            "pic": "${http_download}/hall/item/imgs/item_4118.png",
            "units": {
                "typeId": "common.day",
                "displayName": "天"
            },
            "removeFromBagWhenRemainingZero": 0,
            "removeFromBagWhenExpires": 1,
            "localRes": {
                "resName": "item_revolver"
            },
            "pos": {
                "zOrder": 30
            },
            "masks": 16,
            "actions": [
                {
                    "name": "wear",
                    "displayName": "佩戴",
                    "typeId": "common.decroation.wear"
                },
                {
                    "name": "unwear",
                    "displayName": "取消佩戴",
                    "typeId": "common.decroation.unwear"
                }
            ]
        },
        {
            "kindId": 4119,
            "typeId": "common.decroation",
            "displayName": "神圣十字",
            "visibleInBag": 1,
            "desc": "使用后可在牌桌内激发，“神圣十字”特效",
            "singleMode": 1,
            "pic": "${http_download}/hall/item/imgs/item_4119.png",
            "units": {
                "typeId": "common.day",
                "displayName": "天"
            },
            "removeFromBagWhenRemainingZero": 0,
            "removeFromBagWhenExpires": 1,
            "localRes": {
                "resName": "item_holy_cross"
            },
            "pos": {
                "zOrder": 30
            },
            "masks": 16,
            "actions": [
                {
                    "name": "wear",
                    "displayName": "佩戴",
                    "typeId": "common.decroation.wear"
                },
                {
                    "name": "unwear",
                    "displayName": "取消佩戴",
                    "typeId": "common.decroation.unwear"
                }
            ]
        },
        {
            "kindId": 4120,
            "typeId": "common.decroation",
            "displayName": "地狱之戟",
            "visibleInBag": 1,
            "desc": "使用后可在牌桌内激发，“地狱之戟”特效",
            "singleMode": 1,
            "pic": "${http_download}/hall/item/imgs/item_4120.png",
            "units": {
                "typeId": "common.day",
                "displayName": "天"
            },
            "removeFromBagWhenRemainingZero": 0,
            "removeFromBagWhenExpires": 1,
            "localRes": {
                "resName": "item_hell_trident"
            },
            "pos": {
                "zOrder": 30
            },
            "masks": 16,
            "actions": [
                {
                    "name": "wear",
                    "displayName": "佩戴",
                    "typeId": "common.decroation.wear"
                },
                {
                    "name": "unwear",
                    "displayName": "取消佩戴",
                    "typeId": "common.decroation.unwear"
                }
            ]
        },
        {
            "kindId": 4121,
            "typeId": "common.decroation",
            "displayName": "天使之翼",
            "visibleInBag": 1,
            "desc": "使用后可在入桌时展示，“天使之翼”",
            "singleMode": 1,
            "pic": "${http_download}/hall/item/imgs/item_4121.png",
            "units": {
                "typeId": "common.day",
                "displayName": "天"
            },
            "removeFromBagWhenRemainingZero": 0,
            "removeFromBagWhenExpires": 1,
            "localRes": {
                "resName": "wing_angel_wing"
            },
            "pos": {
                "zOrder": 50
            },
            "masks": 32,
            "actions": [
                {
                    "name": "wear",
                    "displayName": "佩戴",
                    "typeId": "common.decroation.wear"
                },
                {
                    "name": "unwear",
                    "displayName": "取消佩戴",
                    "typeId": "common.decroation.unwear"
                }
            ]
        },
        {
            "kindId": 4122,
            "typeId": "common.decroation",
            "displayName": "精灵之翼",
            "visibleInBag": 1,
            "desc": "使用后可在入桌时展示，“精灵之翼”",
            "singleMode": 1,
            "pic": "${http_download}/hall/item/imgs/item_4122.png",
            "units": {
                "typeId": "common.day",
                "displayName": "天"
            },
            "removeFromBagWhenRemainingZero": 0,
            "removeFromBagWhenExpires": 1,
            "localRes": {
                "resName": "wing_elf_wing"
            },
            "pos": {
                "zOrder": 50
            },
            "masks": 32,
            "actions": [
                {
                    "name": "wear",
                    "displayName": "佩戴",
                    "typeId": "common.decroation.wear"
                },
                {
                    "name": "unwear",
                    "displayName": "取消佩戴",
                    "typeId": "common.decroation.unwear"
                }
            ]
        },
        {
            "kindId": 4123,
            "typeId": "common.decroation",
            "displayName": "恶魔之翼",
            "visibleInBag": 1,
            "desc": "使用后可在入桌时展示，“恶魔之翼”",
            "singleMode": 1,
            "pic": "${http_download}/hall/item/imgs/item_4123.png",
            "units": {
                "typeId": "common.day",
                "displayName": "天"
            },
            "removeFromBagWhenRemainingZero": 0,
            "removeFromBagWhenExpires": 1,
            "localRes": {
                "resName": "wing_demon_wing"
            },
            "pos": {
                "zOrder": 50
            },
            "masks": 32,
            "actions": [
                {
                    "name": "wear",
                    "displayName": "佩戴",
                    "typeId": "common.decroation.wear"
                },
                {
                    "name": "unwear",
                    "displayName": "取消佩戴",
                    "typeId": "common.decroation.unwear"
                }
            ]
        },
        {
            "kindId": 4124,
            "typeId": "common.decroation",
            "displayName": "牌神之翼",
            "visibleInBag": 1,
            "desc": "使用后可在入桌时展示，“牌神之翼”",
            "singleMode": 1,
            "pic": "${http_download}/hall/item/imgs/item_4124.png",
            "units": {
                "typeId": "common.day",
                "displayName": "天"
            },
            "removeFromBagWhenRemainingZero": 0,
            "removeFromBagWhenExpires": 1,
            "localRes": {
                "resName": "wing_god_red"
            },
            "pos": {
                "zOrder": 50
            },
            "masks": 32,
            "actions": [
                {
                    "name": "wear",
                    "displayName": "佩戴",
                    "typeId": "common.decroation.wear"
                },
                {
                    "name": "unwear",
                    "displayName": "取消佩戴",
                    "typeId": "common.decroation.unwear"
                }
            ]
        },
        {
            "kindId": 4125,
            "typeId": "common.decroation",
            "displayName": "雀神之翼",
            "visibleInBag": 1,
            "desc": "使用后可在入桌时“雀神之翼”",
            "singleMode": 1,
            "pic": "${http_download}/hall/item/imgs/item_4125.png",
            "units": {
                "typeId": "common.day",
                "displayName": "天"
            },
            "removeFromBagWhenRemainingZero": 0,
            "removeFromBagWhenExpires": 1,
            "localRes": {
                "resName": "wing_god_red"
            },
            "pos": {
                "zOrder": 50
            },
            "masks": 32,
            "actions": [
                {
                    "name": "wear",
                    "displayName": "佩戴",
                    "typeId": "common.decroation.wear"
                },
                {
                    "name": "unwear",
                    "displayName": "取消佩戴",
                    "typeId": "common.decroation.unwear"
                }
            ]
        },
        {
            "kindId": 4126,
            "typeId": "common.decroation",
            "displayName": "荣耀之翼",
            "visibleInBag": 1,
            "desc": "使用后可在入桌时展示，“荣耀之翼”",
            "singleMode": 1,
            "pic": "${http_download}/hall/item/imgs/item_4126.png",
            "units": {
                "typeId": "common.day",
                "displayName": "天"
            },
            "removeFromBagWhenRemainingZero": 0,
            "removeFromBagWhenExpires": 1,
            "localRes": {
                "resName": "wing_glory_golden"
            },
            "pos": {
                "zOrder": 50
            },
            "masks": 32,
            "actions": [
                {
                    "name": "wear",
                    "displayName": "佩戴",
                    "typeId": "common.decroation.wear"
                },
                {
                    "name": "unwear",
                    "displayName": "取消佩戴",
                    "typeId": "common.decroation.unwear"
                }
            ]
        },
        {
            "kindId": 4127,
            "typeId": "common.decroation",
            "displayName": "紫禁之翼",
            "visibleInBag": 1,
            "desc": "使用后可在入桌时展示，“紫禁之翼”",
            "singleMode": 1,
            "pic": "${http_download}/hall/item/imgs/item_4127.png",
            "units": {
                "typeId": "common.day",
                "displayName": "天"
            },
            "removeFromBagWhenRemainingZero": 0,
            "removeFromBagWhenExpires": 1,
            "localRes": {
                "resName": "wing_rich_purple"
            },
            "pos": {
                "zOrder": 50
            },
            "masks": 32,
            "actions": [
                {
                    "name": "wear",
                    "displayName": "佩戴",
                    "typeId": "common.decroation.wear"
                },
                {
                    "name": "unwear",
                    "displayName": "取消佩戴",
                    "typeId": "common.decroation.unwear"
                }
            ]
        },
        {
            "kindId": 4128,
            "typeId": "common.decroation",
            "displayName": "会员头像框A",
            "visibleInBag": 1,
            "desc": "会员头像框A",
            "singleMode": 0,
            "pic": "",
            "units": {
                "typeId": "common.day",
                "displayName": "天"
            },
            "removeFromBagWhenRemainingZero": 0,
            "removeFromBagWhenExpires": 1,
            "localRes": {
                "resName": "border_silver"
            },
            "pos": {
                "zOrder": 20
            },
            "masks": 1,
            "actions": [
                {
                    "name": "wear",
                    "displayName": "佩戴",
                    "typeId": "common.decroation.wear"
                },
                {
                    "name": "unwear",
                    "displayName": "取消佩戴",
                    "typeId": "common.decroation.unwear"
                }
            ]
        },
        {
            "kindId": 4129,
            "typeId": "common.decroation",
            "displayName": "会员头像框B",
            "visibleInBag": 0,
            "desc": "会员头像框B",
            "singleMode": 1,
            "pic": "",
            "units": {
                "typeId": "common.day",
                "displayName": "天"
            },
            "removeFromBagWhenRemainingZero": 0,
            "removeFromBagWhenExpires": 1,
            "localRes": {
                "resName": "border_gold"
            },
            "pos": {
                "zOrder": 20
            },
            "masks": 1,
            "actions": [
                {
                    "name": "wear",
                    "displayName": "佩戴",
                    "typeId": "common.decroation.wear"
                },
                {
                    "name": "unwear",
                    "displayName": "取消佩戴",
                    "typeId": "common.decroation.unwear"
                }
            ]
        },
        {
            "kindId": 4130,
            "typeId": "common.decroation",
            "displayName": "赌神戒指",
            "visibleInBag": 1,
            "desc": "使用后可在牌桌内激发，“赌神戒指”特效",
            "singleMode": 1,
            "pic": "${http_download}/hall/item/imgs/item_4130.png",
            "units": {
                "typeId": "common.day",
                "displayName": "天"
            },
            "removeFromBagWhenRemainingZero": 0,
            "removeFromBagWhenExpires": 1,
            "localRes": {
                "resName": "item_god_ring"
            },
            "pos": {
                "zOrder": 30
            },
            "masks": 1,
            "actions": [
                {
                    "name": "wear",
                    "displayName": "佩戴",
                    "typeId": "common.decroation.wear"
                },
                {
                    "name": "unwear",
                    "displayName": "取消佩戴",
                    "typeId": "common.decroation.unwear"
                }
            ]
        },
        {
            "kindId": 4131,
            "typeId": "common.decroation",
            "displayName": "勇气警徽",
            "visibleInBag": 1,
            "desc": "使用后可在牌桌内激发，“勇气警徽”特效",
            "singleMode": 1,
            "pic": "${http_download}/hall/item/imgs/item_4131.png",
            "units": {
                "typeId": "common.day",
                "displayName": "天"
            },
            "removeFromBagWhenRemainingZero": 0,
            "removeFromBagWhenExpires": 1,
            "localRes": {
                "resName": "item_badge"
            },
            "pos": {
                "zOrder": 30
            },
            "masks": 16,
            "actions": [
                {
                    "name": "wear",
                    "displayName": "佩戴",
                    "typeId": "common.decroation.wear"
                },
                {
                    "name": "unwear",
                    "displayName": "取消佩戴",
                    "typeId": "common.decroation.unwear"
                }
            ]
        },
        {
            "kindId": 4132,
            "typeId": "common.box",
            "displayName": "端午节抽奖礼包",
            "visibleInBag": 1,
            "desc": "端午节抽奖礼包，送炫酷道具，大量金币，记牌器，来试试手气吧~",
            "singleMode": 1,
            "pic": "${http_download}/hall/item/imgs/item_1004.png",
            "units": {
                "typeId": "common.count",
                "displayName": "个"
            },
            "removeFromBagWhenRemainingZero": 0,
            "removeFromBagWhenExpires": 0,
            "actions": [
                {
                    "name": "open",
                    "displayName": "打开",
                    "typeId": "common.box.open",
                    "nextItemKindId": 4133,
                    "mail": "您开启了\\${item}，获得了\\${gotContent}",
                    "contents": [
                        {
                            "openTimes": {
                                "start": -1,
                                "stop": -1
                            },
                            "typeId": "RandomContent",
                            "randoms": [
                                {
                                    "typeId": "FixedContent",
                                    "weight": 10,
                                    "items": [
                                        {
                                            "itemId": "user:coupon",
                                            "count": 55
                                        }
                                    ]
                                },
                                {
                                    "typeId": "FixedContent",
                                    "weight": 40,
                                    "items": [
                                        {
                                            "itemId": "item:4118",
                                            "count": 1
                                        }
                                    ]
                                },
                                {
                                    "typeId": "FixedContent",
                                    "weight": 20,
                                    "items": [
                                        {
                                            "itemId": "user:chip",
                                            "count": 550
                                        }
                                    ]
                                },
                                {
                                    "typeId": "FixedContent",
                                    "weight": 30,
                                    "items": [
                                        {
                                            "itemId": "item:2003",
                                            "count": 3
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        },
        {
            "kindId": 4133,
            "typeId": "common.box",
            "displayName": "端午节抽奖礼包",
            "visibleInBag": 1,
            "desc": "端午节抽奖礼包，送炫酷道具，大量金币，记牌器，来试试手气吧~",
            "singleMode": 1,
            "pic": "${http_download}/hall/item/imgs/item_1004.png",
            "units": {
                "typeId": "common.count",
                "displayName": "个"
            },
            "removeFromBagWhenRemainingZero": 0,
            "removeFromBagWhenExpires": 0,
            "actions": [
                {
                    "name": "open",
                    "displayName": "打开",
                    "typeId": "common.box.open",
                    "nextItemKindId": 4134,
                    "mail": "您开启了\\${item}，获得了\\${gotContent}",
                    "conditions": [
                        {
                            "typeId": "ITEM.GOT.SECOND_DAYS_LATER",
                            "params": {
                                "failure": "明天才可以打开哦"
                            }
                        }
                    ],
                    "contents": [
                        {
                            "openTimes": {
                                "start": -1,
                                "stop": -1
                            },
                            "typeId": "RandomContent",
                            "randoms": [
                                {
                                    "typeId": "FixedContent",
                                    "weight": 10,
                                    "items": [
                                        {
                                            "itemId": "user:coupon",
                                            "count": 55
                                        }
                                    ]
                                },
                                {
                                    "typeId": "FixedContent",
                                    "weight": 40,
                                    "items": [
                                        {
                                            "itemId": "item:4118",
                                            "count": 1
                                        }
                                    ]
                                },
                                {
                                    "typeId": "FixedContent",
                                    "weight": 20,
                                    "items": [
                                        {
                                            "itemId": "user:chip",
                                            "count": 550
                                        }
                                    ]
                                },
                                {
                                    "typeId": "FixedContent",
                                    "weight": 30,
                                    "items": [
                                        {
                                            "itemId": "item:2003",
                                            "count": 3
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        },
        {
            "kindId": 4134,
            "typeId": "common.box",
            "displayName": "端午节抽奖礼包",
            "visibleInBag": 1,
            "desc": "端午节抽奖礼包，送炫酷道具，大量金币，记牌器，来试试手气吧~",
            "singleMode": 1,
            "pic": "${http_download}/hall/item/imgs/item_1004.png",
            "units": {
                "typeId": "common.count",
                "displayName": "个"
            },
            "removeFromBagWhenRemainingZero": 0,
            "removeFromBagWhenExpires": 0,
            "actions": [
                {
                    "name": "open",
                    "displayName": "打开",
                    "typeId": "common.box.open",
                    "mail": "您开启了\\${item}，获得了\\${gotContent}",
                    "conditions": [
                        {
                            "typeId": "ITEM.GOT.SECOND_DAYS_LATER",
                            "params": {
                                "failure": "明天才可以打开哦"
                            }
                        }
                    ],
                    "contents": [
                        {
                            "openTimes": {
                                "start": -1,
                                "stop": -1
                            },
                            "typeId": "RandomContent",
                            "randoms": [
                                {
                                    "typeId": "FixedContent",
                                    "weight": 10,
                                    "items": [
                                        {
                                            "itemId": "user:coupon",
                                            "count": 55
                                        }
                                    ]
                                },
                                {
                                    "typeId": "FixedContent",
                                    "weight": 40,
                                    "items": [
                                        {
                                            "itemId": "item:4118",
                                            "count": 1
                                        }
                                    ]
                                },
                                {
                                    "typeId": "FixedContent",
                                    "weight": 20,
                                    "items": [
                                        {
                                            "itemId": "user:chip",
                                            "count": 550
                                        }
                                    ]
                                },
                                {
                                    "typeId": "FixedContent",
                                    "weight": 30,
                                    "items": [
                                        {
                                            "itemId": "item:2003",
                                            "count": 3
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        },
        {
            "kindId": 4135,
            "typeId": "common.decroation",
            "displayName": "夏日清凉头像框",
            "visibleInBag": 1,
            "desc": "使用后可佩戴夏日清凉头像框",
            "singleMode": 0,
            "pic": "",
            "units": {
                "typeId": "common.day",
                "displayName": "天"
            },
            "removeFromBagWhenRemainingZero": 0,
            "removeFromBagWhenExpires": 1,
            "localRes": {
                "resName": "border_silver"
            },
            "pos": {
                "zOrder": 23
            },
            "masks": 64,
            "actions": [
                {
                    "name": "wear",
                    "displayName": "佩戴",
                    "typeId": "common.decroation.wear"
                },
                {
                    "name": "unwear",
                    "displayName": "取消佩戴",
                    "typeId": "common.decroation.unwear"
                }
            ]
        },
        {
            "kindId": 4136,
            "typeId": "common.decroation",
            "displayName": "复古头像框",
            "visibleInBag": 1,
            "desc": "使用后可佩戴复古头像框",
            "singleMode": 0,
            "pic": "",
            "units": {
                "typeId": "common.day",
                "displayName": "天"
            },
            "removeFromBagWhenRemainingZero": 0,
            "removeFromBagWhenExpires": 1,
            "localRes": {
                "resName": "border_silver"
            },
            "pos": {
                "zOrder": 23
            },
            "masks": 64,
            "actions": [
                {
                    "name": "wear",
                    "displayName": "佩戴",
                    "typeId": "common.decroation.wear"
                },
                {
                    "name": "unwear",
                    "displayName": "取消佩戴",
                    "typeId": "common.decroation.unwear"
                }
            ]
        },
        {
            "kindId": 4137,
            "typeId": "common.decroation",
            "displayName": "朋克头像框",
            "visibleInBag": 1,
            "desc": "朋克头像框",
            "singleMode": 0,
            "pic": "",
            "units": {
                "typeId": "common.day",
                "displayName": "天"
            },
            "removeFromBagWhenRemainingZero": 0,
            "removeFromBagWhenExpires": 1,
            "localRes": {
                "resName": "border_silver"
            },
            "pos": {
                "zOrder": 23
            },
            "masks": 64,
            "actions": [
                {
                    "name": "wear",
                    "displayName": "佩戴",
                    "typeId": "common.decroation.wear"
                },
                {
                    "name": "unwear",
                    "displayName": "取消佩戴",
                    "typeId": "common.decroation.unwear"
                }
            ]
        }
    ],
    "user.init.items": [
        {
            "itemKindId": 1013,
            "count": 1
        },
        {
            "itemKindId": 1008,
            "count": 5
        },
        {
            "itemKindId": 1007,
            "count": 20
        }
    ]
}

skill_conf = {
  "score" : [0, 5, 15, 35, 75, 155, 235, 315, 395, 475, 575, 705, 865, 1055,
      1275, 1525, 1825, 2175, 2575, 3025, 3525, 4125, 4825, 5625, 6525, 7525,
      8725, 10125, 11725, 13525, 15525, 18025, 21025, 24525, 28525, 33525,
      39525, 46525, 54525, 63525, 73525, 85525, 99525, 115525, 133525, 153525,
      178525, 208525, 243525, 283525],
  "title_pic" : "${http_download}/dizhu/skillscore/imgs/ddz_skill_score_title.png",
  "des" : "斗地主房间中每次胜利都可获得大师分，高倍数、高级房间、会员获得的更快！",
  "level_pic" : ["${http_download}/dizhu/skillscore/imgs/xiaomai1.png",
      "${http_download}/dizhu/skillscore/imgs/xiaomai2.png",
      "${http_download}/dizhu/skillscore/imgs/xiaomai3.png",
      "${http_download}/dizhu/skillscore/imgs/xiaomai4.png",
      "${http_download}/dizhu/skillscore/imgs/xiaomai5.png",
      "${http_download}/dizhu/skillscore/imgs/buxie6.png",
      "${http_download}/dizhu/skillscore/imgs/buxie7.png",
      "${http_download}/dizhu/skillscore/imgs/buxie8.png",
      "${http_download}/dizhu/skillscore/imgs/buxie9.png",
      "${http_download}/dizhu/skillscore/imgs/buxie10.png",
      "${http_download}/dizhu/skillscore/imgs/chutou11.png",
      "${http_download}/dizhu/skillscore/imgs/chutou12.png",
      "${http_download}/dizhu/skillscore/imgs/chutou13.png",
      "${http_download}/dizhu/skillscore/imgs/chutou14.png",
      "${http_download}/dizhu/skillscore/imgs/chutou15.png",
      "${http_download}/dizhu/skillscore/imgs/tongqian16.png",
      "${http_download}/dizhu/skillscore/imgs/tongqian17.png",
      "${http_download}/dizhu/skillscore/imgs/tongqian18.png",
      "${http_download}/dizhu/skillscore/imgs/tongqian19.png",
      "${http_download}/dizhu/skillscore/imgs/tongqian20.png",
      "${http_download}/dizhu/skillscore/imgs/toujin21.png",
      "${http_download}/dizhu/skillscore/imgs/toujin22.png",
      "${http_download}/dizhu/skillscore/imgs/toujin23.png",
      "${http_download}/dizhu/skillscore/imgs/toujin24.png",
      "${http_download}/dizhu/skillscore/imgs/toujin25.png",
      "${http_download}/dizhu/skillscore/imgs/dizhumao26.png",
      "${http_download}/dizhu/skillscore/imgs/dizhumao27.png",
      "${http_download}/dizhu/skillscore/imgs/dizhumao28.png",
      "${http_download}/dizhu/skillscore/imgs/dizhumao29.png",
      "${http_download}/dizhu/skillscore/imgs/dizhumao30.png",
      "${http_download}/dizhu/skillscore/imgs/yuanbao31.png",
      "${http_download}/dizhu/skillscore/imgs/yuanbao32.png",
      "${http_download}/dizhu/skillscore/imgs/yuanbao33.png",
      "${http_download}/dizhu/skillscore/imgs/yuanbao34.png",
      "${http_download}/dizhu/skillscore/imgs/yuanbao35.png",
      "${http_download}/dizhu/skillscore/imgs/qiche36.png",
      "${http_download}/dizhu/skillscore/imgs/qiche37.png",
      "${http_download}/dizhu/skillscore/imgs/qiche38.png",
      "${http_download}/dizhu/skillscore/imgs/qiche39.png",
      "${http_download}/dizhu/skillscore/imgs/qiche40.png",
      "${http_download}/dizhu/skillscore/imgs/fangwu41.png",
      "${http_download}/dizhu/skillscore/imgs/fangwu42.png",
      "${http_download}/dizhu/skillscore/imgs/fangwu43.png",
      "${http_download}/dizhu/skillscore/imgs/fangwu44.png",
      "${http_download}/dizhu/skillscore/imgs/fangwu45.png",
      "${http_download}/dizhu/skillscore/imgs/huojian46.png",
      "${http_download}/dizhu/skillscore/imgs/huojian47.png",
      "${http_download}/dizhu/skillscore/imgs/huojian48.png",
      "${http_download}/dizhu/skillscore/imgs/huojian49.png",
      "${http_download}/dizhu/skillscore/imgs/huojian50.png"],
  "reward" : {
    "2" : {
      "rewards" : [["CARDNOTE", 1], ["CARDMATCH", 5], ["CHIP", 200]]
    },
    "4" : {
      "rewards" : [["CARDNOTE", 1], ["CARDMATCH", 5], ["CHIP", 500]]
    },
    "5" : {
      "rewards" : [["CARDNOTE", 1], ["CARDMATCH", 5], ["CHIP", 600]]
    },
    "6" : {
      "rewards" : [["CARDNOTE", 1], ["CARDMATCH", 5], ["CHIP", 1000]]
    },
    "7" : {
      "rewards" : [["CARDNOTE", 1], ["CARDMATCH", 5], ["CHIP", 1200]]
    },
    "8" : {
      "rewards" : [["CARDNOTE", 1], ["CARDMATCH", 5], ["CHIP", 1500]]
    },
    "9" : {
      "rewards" : [["CARDNOTE", 1], ["CARDMATCH", 5], ["CHIP", 1600]]
    },
    "10" : {
      "rewards" : [["CARDNOTE", 1], ["CARDMATCH", 5], ["CHIP", 1600]]
    },
    "11" : {
      "rewards" : [["CARDNOTE", 1], ["CARDMATCH", 5], ["CHIP", 2000]]
    },
    "12" : {
      "rewards" : [["CARDNOTE", 1], ["CARDMATCH", 5], ["CHIP", 2000]]
    },
    "13" : {
      "rewards" : [["CARDNOTE", 1], ["CARDMATCH", 5], ["CHIP", 2000]]
    },
    "14" : {
      "rewards" : [["CARDNOTE", 1], ["CARDMATCH", 5], ["CHIP", 2000]]
    },
    "15" : {
      "rewards" : [["CARDNOTE", 1], ["CARDMATCH", 5], ["CHIP", 2000]]
    },
    "16" : {
      "rewards" : [["CARDNOTE", 2], ["CARDMATCH", 5], ["CHIP", 3000]]
    },
    "17" : {
      "rewards" : [["CARDNOTE", 2], ["CARDMATCH", 5], ["CHIP", 3000]]
    },
    "18" : {
      "rewards" : [["CARDNOTE", 2], ["CARDMATCH", 5], ["CHIP", 3000]]
    },
    "19" : {
      "rewards" : [["CARDNOTE", 2], ["CARDMATCH", 5], ["CHIP", 3000]]
    },
    "20" : {
      "rewards" : [["CARDNOTE", 2], ["CARDMATCH", 5], ["CHIP", 3000]]
    },
    "21" : {
      "rewards" : [["CARDNOTE", 2], ["CARDMATCH", 5], ["CHIP", 4000]]
    },
    "22" : {
      "rewards" : [["CARDNOTE", 2], ["CARDMATCH", 5], ["CHIP", 4000]]
    },
    "23" : {
      "rewards" : [["CARDNOTE", 2], ["CARDMATCH", 5], ["CHIP", 4000]]
    },
    "24" : {
      "rewards" : [["CARDNOTE", 2], ["CARDMATCH", 5], ["CHIP", 4000]]
    },
    "25" : {
      "rewards" : [["CARDNOTE", 2], ["CARDMATCH", 5], ["CHIP", 4000]]
    },
    "26" : {
      "rewards" : [["CARDNOTE", 2], ["CARDMATCH", 5], ["CHIP", 5000]]
    },
    "27" : {
      "rewards" : [["CARDNOTE", 2], ["CARDMATCH", 5], ["CHIP", 5000]]
    },
    "28" : {
      "rewards" : [["CARDNOTE", 2], ["CARDMATCH", 5], ["CHIP", 5000]]
    },
    "29" : {
      "rewards" : [["CARDNOTE", 2], ["CARDMATCH", 5], ["CHIP", 5000]]
    },
    "30" : {
      "rewards" : [["CARDNOTE", 2], ["CARDMATCH", 5], ["CHIP", 5000]]
    }
  },
  "ratio_room" : [{
        "roomlist" : [601, 650, 670, 690],
        "ratio" : 1
      }, {
        "roomlist" : [603, 651, 671, 691],
        "ratio" : 2
      }, {
        "roomlist" : [607, 652, 672, 692],
        "ratio" : 4
      }, {
        "roomlist" : [605, 653, 673, 693],
        "ratio" : 6
      }]
}

public_conf = {
  "referrer_switch" : 1,
  "optimedis" : "您的上家网络不好，等他一会儿吧",
  "http_download_html" : "${http_game}/dizhu/",
  "http_download_pic" : "${http_download}/6/",
  "http_download_default" : "${http_game}/6/",
  "buyin" : {
    "start_version" : 3.502,
    "tip" : "客官，此房间最多允许带入{BUYIN_CHIP}金币哦!",
    "tip_auto" : "系统自动为您补充了金币"
  },
  "vip_special_right" : {
    "dashifen" : [{
          "level" : 2,
          "rate" : 0.2,
          "desc" : "大师分获取增加20%"
        }]
  },
  "roomfee_conf" : {
    "basic" : 0.6,
    "winner_chip" : 0.03,
    "high_multi" : 32,
    "fee_multi" : 2.0
  },
  "change_nickname_level" : 3,
  "ad_notify_play_count" : 2,
  "use_momo_ranking" : 0,
  "use_tuyou_ranking" : 1
}


class TestDailyCheckin(unittest.TestCase):
    userId = 10001
    gameId = 6
    clientId = 'IOS_3.6_momo'
    testContext = HallTestMockContext()
    def getCurrentTimestamp(self):
        return self.timestamp
    
    dizhuasset._registerClasses()
    dizhutask._registerClasses()
    halltask._registerClasses()
        
    def setUp(self):
        self.testContext.startMock()
        
        self.timestamp = pktimestamp.getCurrentTimestamp()
        self.pktimestampPatcher = patch('poker.util.timestamp.getCurrentTimestamp', self.getCurrentTimestamp)
        self.pktimestampPatcher.start()
        
        self.testContext.gdataTest.setGame(TGDizhu)
        
        self.testContext.configure.setJson('game:9999:map.clientid', clientIdMap, 0)
        self.testContext.configure.setJson('game:9999:item', item_conf, 0)
        self.testContext.configure.setJson('game:9999:products', products_conf, 0)
        self.testContext.configure.setJson('game:9999:store', store_template_conf, 0)
        self.testContext.configure.setJson('game:9999:store', store_default_conf, clientIdMap[self.clientId])
        self.testContext.configure.setJson('game:9999:vip', vip_conf, 0)
        self.testContext.configure.setJson('game:9999:dailycheckin', dailycheckin_conf, 0)
        
        self.testContext.configure.setJson('game:6:flipcard', dizhuflipcard_conf, 0)
        self.testContext.configure.setJson('game:6:tasks', task_conf, 0)
        self.testContext.configure.setJson('game:6:skill.score', skill_conf, 0)
        self.testContext.configure.setJson('game:6:public', public_conf, 0)
        self.testContext.gameDB.setGameAttr(self.userId, self.gameId, 'nslogin', 0)
        self.testContext.configure.setJson('game:6:task.daily', daily_task_conf, 0)
        
#         
# def getSkillScoreGameName():
#     return getDizhuGameItem('skill.score', 'game_name')
# 
# 
# def getSkillScoreDes():
#     return getDizhuGameItem('skill.score', 'des')
# 
# 
# def getSkillScoreReward():
#     return getDizhuGameItem('skill.score', 'reward')
# 
# 
# def getSkillSCoreRatioRoom():
#     return getDizhuGameItem('skill.score', 'ratio_room')

        self.testContext.configure.setJson('game:6:skill.score:0', {
                                                            'game_name':'dizhu',
                                                            'score':'大师分',
                                                            'des':'des',
                                                            'reward':'reward',
                                                            'ratio_room':'ratio_room',
                                                            'level_pic':'level_pic',
                                                            'title_pic':'title_pic'})
        
        #def setGameAttr(self, userId, gameId, attrname, value):
        hallitem._initialize()
        hallvip._initialize()
        halldailycheckin._initialize()
        dizhuflipcard._initialize()
        dizhutask._initialize()
        
    def tearDown(self):
        self.testContext.stopMock()
        self.pktimestampPatcher.stop()
        
#     def testLoadStatus(self):
#         dailyTaskModel = dizhutask.dailyTaskSystem.loadTaskModel(self.userId, self.timestamp)
#         medalTaskModel = dizhutask.medalTaskSystem.loadTaskModel(self.userId, self.timestamp)
#         tableTaskModel = dizhutask.tableTaskSystem.loadTaskModel(self.userId, self.timestamp)
#         
#         userchip.incrChip(self.userId, self.gameId, 100000, daoconst.CHIP_NOT_ENOUGH_OP_MODE_NONE, 0, 0, 'Android_momo_3.7')
#         dizhutask._taskSystem._handleEvent(EventUserLogin(self.userId, self.gameId, True, False, 'Android_momo_3.7'))
#         dizhutask._taskSystem._handleEvent(UserLevelGrowEvent(self.gameId, self.userId, 0, 1))
#         handler = MedalTaskHandler()
#         handler.doMedalTaskGetReward(self.userId, self.gameId, 10011)
#         
    def testTableTask(self):
        parts = [
            (20000, 20014, UserTablePlayEvent(self.gameId, self.userId, 601, 60101, 9, self.userId)),
            (20015, 20029, UserTablePlayEvent(self.gameId, self.userId, 605, 60501, 9, self.userId)),
            (20030, 20044, UserTablePlayEvent(self.gameId, self.userId, 607, 60701, 9, self.userId)),
            (20045, 20103, UserTablePlayEvent(self.gameId, self.userId, 605, 60501, 9, self.userId)), 
        ]
        for part in parts:
            totalCount = 0
            tableTaskModel = dizhutask.tableTaskSystem.loadTaskModel(self.userId, self.timestamp)
            kindId = part[0]
            while (kindId <= part[1]):
                count = dizhutask.tableTaskSystem.taskUnit.findTaskKind(kindId).count - totalCount
                ftlog.info('********testTableTask kindId=', kindId, 'count=', count)
                for i in xrange(count):
                    taskKind = dizhutask._taskSystem.findTaskKind(kindId)
                    if taskKind.inspector._conditionList:
                        for condition in taskKind.inspector._conditionList:
                            if isinstance(condition, DizhuTaskConditionRoomId):
                                if condition.roomIdSet:
                                    part[2].roomId = list(condition.roomIdSet)[0]
                    if taskKind.kindId == 20015:
                        print taskKind.kindId
                    dizhutask.tableTaskSystem.processEvent(tableTaskModel.userTaskUnit, part[2])
                    task = tableTaskModel.userTaskUnit.findTask(kindId)
                    if task.progress != totalCount+i+1:
                        print task.progress
                    self.assertEqual(task.progress, totalCount+i+1)
                dizhutask.tableTaskSystem.getTaskReward(tableTaskModel.userTaskUnit.findTask(kindId), self.timestamp, '', 0)
                totalCount += count
                kindId += 1

if __name__ == '__main__':
    unittest.main()
    
    
