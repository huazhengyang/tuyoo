# -*- coding=utf-8
'''
Created on 2015年7月30日

@author: zhaojiangang
'''
import unittest

from entity.hallstore_test import clientIdMap, item_conf, products_conf, \
    store_template_conf, store_default_conf
from entity.hallvip_test import vip_conf
from hall.entity import hallitem, hallvip, hallgamelist
from test_base import HallTestMockContext


gamelist_conf = {
    "templates": {
        "hall_game_3_5_no_plugin": [
            {
                "nodes": [
                    "common_dizhu_classics_v3_5", 
                    "common_dizhu_happy_v3_5", 
                    "common_dizhu_match_v3_5", 
                    "common_dizhu_laizi_v3_5", 
                    "common_dizhu_double_v3_5", 
                    "common_dizhu_single_v3_5"
                ], 
                "form": "dizhu3x2"
            }
        ], 
        "hall_game_3_5_03": [
            {
                "nodes": [
                    "common_dizhu_classics_v3_5", 
                    "common_dizhu_happy_v3_5", 
                    "common_dizhu_match_v3_5", 
                    "common_dizhu_laizi_v3_5", 
                    "common_dizhu_single_v3_5", 
                    "common_next_page_v3_5"
                ], 
                "form": "dizhu3x2"
            }, 
            {
                "nodes": [
                    "common_dizhu_double_v3_5", 
                    "plugin_douniu_crazy_v3_502", 
                    "plugin_douniu_100_v3_5", 
                    "plugin_t3card_v3_5", 
                    "plugin_fruit_v3_5", 
                    "plugin_texas_v3_5", 
                    "plugin_dog_v3_5", 
                    "plugin_baohuang_v3_5", 
                    "plugin_t3flush_v3_5"
                ], 
                "form": "dizhu3x3"
            }
        ], 
        "hall_game_3_5_02": [
            {
                "nodes": [
                    "common_dizhu_classics_v3_5", 
                    "common_dizhu_happy_v3_5", 
                    "common_dizhu_match_v3_5", 
                    "common_dizhu_laizi_v3_5", 
                    "common_dizhu_single_v3_5", 
                    "common_next_page_v3_5"
                ], 
                "form": "dizhu3x2"
            }, 
            {
                "nodes": [
                    "common_dizhu_double_v3_5", 
                    "plugin_douniu_crazy_v3_502", 
                    "plugin_douniu_100_v3_5", 
                    "plugin_t3card_v3_5", 
                    "plugin_fruit_v3_5", 
                    "plugin_texas_v3_5", 
                    "plugin_dog_v3_5", 
                    "plugin_t3flush_v3_5"
                ], 
                "form": "dizhu3x3"
            }
        ], 
        "default": [
            {
                "nodes": [
                    "common_dizhu_classics_v3_5", 
                    "common_dizhu_happy_v3_5", 
                    "common_dizhu_match_v3_5", 
                    "common_dizhu_laizi_v3_5", 
                    "common_dizhu_double_v3_5", 
                    "common_dizhu_single_v3_5"
                ], 
                "form": "dizhu3x2"
            }
        ], 
        "hall_game_3_5_t3flush": [
            {
                "nodes": [
                    "common_dizhu_classics_v3_5", 
                    "common_dizhu_happy_v3_5", 
                    "common_dizhu_match_v3_5", 
                    "common_dizhu_laizi_v3_5", 
                    "common_dizhu_single_v3_5", 
                    "common_next_page_v3_5"
                ], 
                "form": "dizhu3x2"
            }, 
            {
                "nodes": [
                    "common_dizhu_double_v3_5", 
                    "plugin_douniu_crazy_v3_5", 
                    "plugin_douniu_100_v3_5", 
                    "plugin_t3card_v3_5", 
                    "plugin_fruit_v3_5", 
                    "plugin_texas_v3_5", 
                    "plugin_majiang_v3_5", 
                    "plugin_dog_v3_5", 
                    "plugin_t3flush_v3_5"
                ], 
                "form": "dizhu3x3"
            }
        ], 
        "hall_game_3_5_not3card": [
            {
                "nodes": [
                    "common_dizhu_classics_v3_5", 
                    "common_dizhu_happy_v3_5", 
                    "common_dizhu_match_v3_5", 
                    "common_dizhu_laizi_v3_5", 
                    "common_dizhu_single_v3_5", 
                    "common_next_page_v3_5"
                ], 
                "form": "dizhu3x2"
            }, 
            {
                "nodes": [
                    "common_dizhu_double_v3_5", 
                    "plugin_douniu_crazy_v3_5", 
                    "plugin_douniu_100_v3_5", 
                    "plugin_fruit_v3_5", 
                    "plugin_texas_v3_5", 
                    "plugin_majiang_v3_5", 
                    "plugin_dog_v3_5"
                ], 
                "form": "dizhu3x3"
            }
        ], 
        "hall_game_3_5": [
            {
                "nodes": [
                    "common_dizhu_classics_v3_5", 
                    "common_dizhu_happy_v3_5", 
                    "common_dizhu_match_v3_5", 
                    "common_dizhu_laizi_v3_5", 
                    "common_dizhu_single_v3_5", 
                    "common_next_page_v3_5"
                ], 
                "form": "dizhu3x2"
            }, 
            {
                "nodes": [
                    "common_dizhu_double_v3_5", 
                    "plugin_douniu_crazy_v3_5", 
                    "plugin_douniu_100_v3_5", 
                    "plugin_t3card_v3_5", 
                    "plugin_fruit_v3_5", 
                    "plugin_texas_v3_5", 
                    "plugin_majiang_v3_5", 
                    "plugin_dog_v3_5", 
                    "plugin_t3flush_v3_5"
                ], 
                "form": "dizhu3x3"
            }
        ], 
        "hall_game_3_6": [
            {
                "nodes": [
                    "plugin_dizhu_classics_v3_6", 
                    "plugin_dizhu_happy_v3_6", 
                    "plugin_dizhu_match_v3_6", 
                    "plugin_dizhu_laizi_v3_6", 
                    "plugin_dizhu_single_v3_6", 
                    "common_next_page_v3_6"
                ], 
                "form": "dizhu3x2"
            }, 
            {
                "nodes": [
                    "plugin_dizhu_double_v3_6", 
                    "plugin_fruit_v3_6", 
                    "plugin_douniu_crazy_v3_601", 
                    "plugin_dog_v3_6", 
                    "plugin_douniu_100_v3_6"
                ], 
                "form": "dizhu3x3"
            }
        ], 
        "hall_game_texas_3_6_phone": [
            {
                "nodes": [
                    "plugin_texas_v3_6_phone_type_2", 
                    "plugin_texas_v3_6_phone_type_3", 
                    "plugin_texas_v3_6_phone_type_4", 
                    "plugin_texas_v3_6_phone_type_1"
                ], 
                "form": "texas1x5"
            }
        ], 
        "hall_game_3_5_03_baohuang_beta": [
            {
                "nodes": [
                    "common_dizhu_classics_v3_5", 
                    "common_dizhu_happy_v3_5", 
                    "common_dizhu_match_v3_5", 
                    "common_dizhu_laizi_v3_5", 
                    "common_dizhu_single_v3_5", 
                    "common_next_page_v3_5"
                ], 
                "form": "dizhu3x2"
            }, 
            {
                "nodes": [
                    "common_dizhu_double_v3_5", 
                    "plugin_fruit_v3_5", 
                    "plugin_texas_v3_5", 
                    "plugin_dog_v3_5", 
                    "plugin_baohuang_v3_5"
                ], 
                "form": "dizhu3x3"
            }
        ], 
        "hall_game_mj_3_5": [
            {
                "nodes": [
                    "common_dizhu_classics_v3_5", 
                    "common_dizhu_double_v3_5", 
                    "common_dizhu_match_v3_5", 
                    "common_dizhu_single_v3_5", 
                    "common_mj_blood_v3_5", 
                    "common_next_page_v3_5"
                ], 
                "form": "dizhu3x2"
            }, 
            {
                "nodes": [
                    "common_dizhu_laizi_v3_5", 
                    "common_mj_xlch_v3_5", 
                    "common_dizhu_happy_v3_5", 
                    "plugin_t3card_v3_5", 
                    "plugin_fruit_v3_5", 
                    "plugin_texas_v3_5", 
                    "plugin_douniu_crazy_v3_5", 
                    "plugin_douniu_100_v3_5", 
                    "plugin_baohuang_v3_5"
                ], 
                "form": "dizhu3x3"
            }
        ], 
        "hall_game_mj_ios_3_5": [
            {
                "nodes": [
                    "common_dizhu_classics_v3_5", 
                    "common_dizhu_double_v3_5", 
                    "common_dizhu_match_v3_5", 
                    "common_dizhu_laizi_v3_5", 
                    "common_dizhu_single_v3_5", 
                    "common_next_page_v3_5"
                ], 
                "form": "dizhu3x2"
            }, 
            {
                "nodes": [
                    "common_dizhu_happy_v3_5", 
                    "common_mj_blood_v3_5", 
                    "common_mj_xlch_v3_5", 
                    "plugin_t3card_v3_5", 
                    "plugin_fruit_v3_5", 
                    "plugin_texas_v3_5", 
                    "plugin_douniu_crazy_v3_5", 
                    "plugin_douniu_100_v3_5", 
                    "plugin_baohuang_v3_5"
                ], 
                "form": "dizhu3x3"
            }
        ], 
        "hall_game_3_5_no_plugin_no_single": [
            {
                "nodes": [
                    "common_dizhu_classics_v3_5", 
                    "common_dizhu_happy_v3_5", 
                    "common_dizhu_match_v3_5", 
                    "common_dizhu_laizi_v3_5", 
                    "common_dizhu_double_v3_5"
                ], 
                "form": "dizhu3x2"
            }
        ], 
        "hall_game_3_5_03_not3card": [
            {
                "nodes": [
                    "common_dizhu_classics_v3_5", 
                    "common_dizhu_happy_v3_5", 
                    "common_dizhu_match_v3_5", 
                    "common_dizhu_laizi_v3_5", 
                    "common_dizhu_single_v3_5", 
                    "common_next_page_v3_5"
                ], 
                "form": "dizhu3x2"
            }, 
            {
                "nodes": [
                    "common_dizhu_double_v3_5", 
                    "plugin_douniu_crazy_v3_502", 
                    "plugin_douniu_100_v3_5", 
                    "plugin_fruit_v3_5", 
                    "plugin_texas_v3_5", 
                    "plugin_dog_v3_5"
                ], 
                "form": "dizhu3x3"
            }
        ], 
        "hall_game_3_5_not3card_nodouniu": [
            {
                "nodes": [
                    "common_dizhu_classics_v3_5", 
                    "common_dizhu_happy_v3_5", 
                    "common_dizhu_match_v3_5", 
                    "common_dizhu_laizi_v3_5", 
                    "common_dizhu_single_v3_5", 
                    "common_next_page_v3_5"
                ], 
                "form": "dizhu3x2"
            }, 
            {
                "nodes": [
                    "common_dizhu_double_v3_5", 
                    "plugin_fruit_v3_5", 
                    "plugin_texas_v3_5", 
                    "plugin_majiang_v3_5", 
                    "plugin_dog_v3_5"
                ], 
                "form": "dizhu3x2"
            }
        ], 
        "hall_game_3_5_ios": [
            {
                "nodes": [
                    "common_dizhu_classics_v3_5", 
                    "common_dizhu_happy_v3_5", 
                    "common_dizhu_match_v3_5", 
                    "common_dizhu_laizi_v3_5", 
                    "common_dizhu_single_v3_5", 
                    "common_next_page_v3_5"
                ], 
                "form": "dizhu3x2"
            }, 
            {
                "nodes": [
                    "common_dizhu_double_v3_5", 
                    "plugin_douniu_crazy_v3_5", 
                    "plugin_douniu_100_v3_5", 
                    "plugin_t3card_v3_5", 
                    "plugin_fruit_v3_5", 
                    "plugin_texas_v3_5", 
                    "plugin_majiang_v3_5", 
                    "plugin_dog_ios_v3_5", 
                    "plugin_t3flush_v3_5"
                ], 
                "form": "dizhu3x3"
            }
        ], 
        "hall_game_3_5_03_huawei": [
            {
                "nodes": [
                    "common_dizhu_classics_v3_5", 
                    "common_dizhu_happy_v3_5", 
                    "common_dizhu_match_v3_5", 
                    "common_dizhu_laizi_v3_5", 
                    "common_dizhu_single_v3_5", 
                    "common_next_page_v3_5"
                ], 
                "form": "dizhu3x2"
            }, 
            {
                "nodes": [
                    "common_dizhu_double_v3_5", 
                    "plugin_fruit_v3_5", 
                    "plugin_texas_v3_5", 
                    "plugin_dog_v3_5"
                ], 
                "form": "dizhu3x3"
            }
        ], 
        "hall_game_3_6_ddz_pc": [
            {
                "nodes": [
                    "plugin_dizhu_classics_v3_6", 
                    "plugin_dizhu_happy_v3_6", 
                    "plugin_dizhu_match_v3_6", 
                    "plugin_dizhu_laizi_v3_6"
                ], 
                "form": "dizhu3x2"
            }
        ], 
        "hall_game_3_5_03_ios": [
            {
                "nodes": [
                    "common_dizhu_classics_v3_5", 
                    "common_dizhu_happy_v3_5", 
                    "common_dizhu_match_v3_5", 
                    "common_dizhu_laizi_v3_5", 
                    "common_dizhu_single_v3_5", 
                    "common_next_page_v3_5"
                ], 
                "form": "dizhu3x2"
            }, 
            {
                "nodes": [
                    "common_dizhu_double_v3_5", 
                    "plugin_douniu_crazy_v3_502", 
                    "plugin_douniu_100_v3_5", 
                    "plugin_t3card_v3_5", 
                    "plugin_fruit_v3_5", 
                    "plugin_texas_v3_5", 
                    "plugin_dog_ios_v3_5", 
                    "plugin_t3flush_v3_5"
                ], 
                "form": "dizhu3x3"
            }
        ], 
        "hall_game_3_5_no_single": [
            {
                "nodes": [
                    "common_dizhu_classics_v3_5", 
                    "common_dizhu_happy_v3_5", 
                    "common_dizhu_match_v3_5", 
                    "common_dizhu_laizi_v3_5", 
                    "common_dizhu_double_v3_5", 
                    "common_next_page_v3_5"
                ], 
                "form": "dizhu3x2"
            }, 
            {
                "nodes": [
                    "plugin_douniu_crazy_v3_5", 
                    "plugin_douniu_100_v3_5", 
                    "plugin_t3card_v3_5", 
                    "plugin_fruit_v3_5", 
                    "plugin_texas_v3_5", 
                    "plugin_majiang_v3_5", 
                    "plugin_dog_v3_5"
                ], 
                "form": "dizhu3x3"
            }
        ], 
        "hall_game_texas_3_6_pc": [
            {
                "nodes": [
                    "plugin_texas_v3_6_pc_type_1", 
                    "plugin_texas_v3_6_pc_type_2", 
                    "plugin_texas_v3_6_pc_type_3"
                ], 
                "form": "dizhu3x2"
            }
        ], 
        "hall_game_3_5_02_ios": [
            {
                "nodes": [
                    "common_dizhu_classics_v3_5", 
                    "common_dizhu_happy_v3_5", 
                    "common_dizhu_match_v3_5", 
                    "common_dizhu_laizi_v3_5", 
                    "common_dizhu_single_v3_5", 
                    "common_next_page_v3_5"
                ], 
                "form": "dizhu3x2"
            }, 
            {
                "nodes": [
                    "common_dizhu_double_v3_5", 
                    "plugin_douniu_crazy_v3_502", 
                    "plugin_douniu_100_v3_5", 
                    "plugin_t3card_v3_5", 
                    "plugin_fruit_v3_5", 
                    "plugin_texas_v3_5", 
                    "plugin_dog_ios_v3_5", 
                    "plugin_t3flush_v3_5"
                ], 
                "form": "dizhu3x3"
            }
        ]
    }, 
    "nodes": {
        "common_dizhu_double_v3_5": {
            "type": "common", 
            "params": {
                "defaultRes": "DoublePerson", 
                "gameType": 6, 
                "gameMark": "ddz"
            }
        }, 
        "plugin_texas_v3_6_pc_type_1": {
            "params": {
                "gameMark": "texas", 
                "gameId": 8, 
                "gameName": "德州扑克", 
                "description": [
                    "1、简单易学，上手快~", 
                    "2、对战刺激，赢得多~"
                ], 
                "ctorName": "dz", 
                "isNew": 1, 
                "currentVer": {
                    "ver": 3.35105, 
                    "url": "http://111.203.187.142:8002/hall6/texas/texas.zip", 
                    "hall_min_required": 3, 
                    "changelogs": [
                        "1、简单易学，上手快~", 
                        "2、对战刺激，赢得多~"
                    ], 
                    "size": "2.61M", 
                    "md5": "18fd76650f50128d58b96e61020b3454"
                }, 
                "gameType": 6, 
                "ctorPath": "games/texas/script/build/dz_release.js", 
                "iconUrl": "", 
                "defaultRes": "TexasRoomList", 
                "isQuickStart": 1
            }, 
            "type": "download"
        }, 
        "plugin_texas_v3_6_phone_type_1": {
            "params": {
                "gameMark": "texas", 
                "gameId": 8, 
                "gameName": "德州扑克", 
                "description": [
                    "1、简单易学，上手快~", 
                    "2、对战刺激，赢得多~"
                ], 
                "ctorName": "dz", 
                "isNew": 1, 
                "currentVer": {
                    "ver": 3.35105, 
                    "url": "http://111.203.187.142:8002/hall6/texas/texas.zip", 
                    "hall_min_required": 3, 
                    "changelogs": [
                        "1、简单易学，上手快~", 
                        "2、对战刺激，赢得多~"
                    ], 
                    "size": "2.61M", 
                    "md5": "18fd76650f50128d58b96e61020b3454"
                }, 
                "gameType": 1, 
                "ctorPath": "games/texas/script/build/dz_release.js", 
                "iconUrl": "", 
                "defaultRes": "Exciting", 
                "isQuickStart": 1
            }, 
            "type": "download"
        }, 
        "plugin_texas_as_default": {
            "params": {
                "iconUrl": "", 
                "gameMark": "texas", 
                "gameId": 8, 
                "description": [
                    "1、简单易学，上手快~", 
                    "2、对战刺激，赢得多~"
                ], 
                "ctorName": "dz", 
                "currentVer": {
                    "ver": 3.35105, 
                    "url": "http://111.203.187.142:8002/hall6/texas/texas.zip", 
                    "hall_min_required": 3, 
                    "changelogs": [
                        "1、简单易学，上手快~", 
                        "2、对战刺激，赢得多~"
                    ], 
                    "md5": "18fd76650f50128d58b96e61020b3454", 
                    "size": "2.61M"
                }, 
                "gameName": "德州扑克", 
                "isNew": 1, 
                "gameType": 1, 
                "ctorPath": "games/texas/script/build/dz_release.js", 
                "defaultRes": "TexasDefault", 
                "isQuickStart": 1
            }, 
            "type": "download"
        }, 
        "plugin_douniu_old100": {
            "params": {
                "iconUrl": "", 
                "gameMark": "douniu", 
                "gameId": 10, 
                "description": [
                    "1、百人共一桌，热闹~", 
                    "2、上庄最刺激，过瘾~"
                ], 
                "ctorName": "dn", 
                "currentVer": {
                    "ver": 3, 
                    "url": "http://ddz.dl.tuyoo.com/hall6/douniu-hundreds/douniu-hundreds_v3.0_1.zip", 
                    "hall_min_required": 3, 
                    "changelogs": [
                        "1、百人共一桌，热闹~", 
                        "2、上庄最刺激，过瘾~"
                    ], 
                    "size": "2.2M", 
                    "md5": ""
                }, 
                "gameName": "百人拼十", 
                "isNew": 1, 
                "gameType": 1, 
                "ctorPath": "games/douniu/douniu_release.js", 
                "defaultRes": "BaiRenDefault"
            }, 
            "type": "download"
        }, 
        "plugin_dizhu_match_v3_6": {
            "type": "download", 
            "params": {
                "gameMark": "ddz", 
                "gameId": 6, 
                "description": [], 
                "isNew": 0, 
                "ctorName": "ddz", 
                "gameName": "比赛场", 
                "currentVer": {
                    "ver": 0, 
                    "url": "http://ddz.dl.tuyoo.com/open/plugin_game/ddz_plugin_3_60_10.zip", 
                    "hall_min_required": 6, 
                    "changelogs": [
                        "1、经典场插件震撼首发~"
                    ], 
                    "md5": "d14d851084eaf8d32871ac9cc6e2ac74", 
                    "size": "4.6M"
                }, 
                "gameType": 3, 
                "ctorPath": "games/ddz/script/build/ddz_release.js", 
                "iconUrl": "", 
                "defaultRes": "Match", 
                "isQuickStart": 1, 
                "isOffline": 0, 
                "autoDownload": 4
            }
        }, 
        "plugin_dizhu_happy": {
            "params": {
                "iconUrl": "", 
                "gameMark": "ddz", 
                "gameId": 6, 
                "description": [], 
                "ctorName": "ddz", 
                "currentVer": {
                    "ver": 0, 
                    "url": "http://ddz.dl.tuyoo.com/open/plugin_game/ddz_plugin_3_60_10.zip", 
                    "hall_min_required": 6, 
                    "changelogs": [
                        "1、经典场插件震撼首发~"
                    ], 
                    "size": "4.6M", 
                    "md5": "d14d851084eaf8d32871ac9cc6e2ac74"
                }, 
                "gameName": "欢乐场", 
                "isNew": 0, 
                "gameType": 2, 
                "ctorPath": "games/ddz/script/build/ddz_release.js", 
                "defaultRes": "Happy", 
                "isQuickStart": 1, 
                "isOffline": 0, 
                "autoDownload": 4
            }, 
            "type": "download"
        }, 
        "plugin_douniu_crazy_v3_502": {
            "params": {
                "gameMark": "douniu", 
                "gameId": 10, 
                "gameName": "疯狂拼十", 
                "description": [
                    "1、看牌再加倍，安逸~", 
                    "2、简单又刺激，精彩~"
                ], 
                "ctorName": "dn", 
                "isNew": 0, 
                "currentVer": {
                    "ver": 3.502, 
                    "url": "http://ddz.dl.tuyoo.com/hall6/douniu/douniu_release_v3.502_1.zip", 
                    "hall_min_required": 2, 
                    "changelogs": [
                        "1、看牌再加倍，安逸~", 
                        "2、简单又刺激，精彩~"
                    ], 
                    "size": "2.1M", 
                    "md5": "b342bffa8f4567924276401806b6e04d"
                }, 
                "gameType": 2, 
                "ctorPath": "games/douniu/douniu_release.js", 
                "iconUrl": "", 
                "defaultRes": "DouNiuDefault"
            }, 
            "type": "download"
        }, 
        "plugin_douniu_crazy_v3_601": {
            "params": {
                "gameMark": "douniu", 
                "gameId": 10, 
                "gameName": "疯狂拼十", 
                "description": [
                    "1、看牌再加倍，安逸~", 
                    "2、简单又刺激，精彩~"
                ], 
                "ctorName": "dn", 
                "isNew": 0, 
                "currentVer": {
                    "ver": 3.6, 
                    "url": "http://ddz.dl.tuyoo.com/hall6/douniu/douniu_release_v3.601.zip", 
                    "hall_min_required": 2, 
                    "changelogs": [
                        "1、看牌再加倍，安逸~", 
                        "2、简单又刺激，精彩~"
                    ], 
                    "size": "2.2M", 
                    "md5": "c67917acb34e1a33b4b4cbfa376d51e5"
                }, 
                "gameType": 2, 
                "ctorPath": "games/douniu/script/build/douniu_release.js", 
                "iconUrl": "", 
                "defaultRes": "DouNiuDefault"
            }, 
            "type": "download"
        }, 
        "plugin_dizhu_happy_v3_6": {
            "type": "download", 
            "params": {
                "gameMark": "ddz", 
                "gameId": 6, 
                "description": [], 
                "isNew": 0, 
                "ctorName": "ddz", 
                "gameName": "欢乐场", 
                "currentVer": {
                    "ver": 0, 
                    "url": "http://ddz.dl.tuyoo.com/open/plugin_game/ddz_plugin_3_60_10.zip", 
                    "hall_min_required": 6, 
                    "changelogs": [
                        "1、经典场插件震撼首发~"
                    ], 
                    "md5": "d14d851084eaf8d32871ac9cc6e2ac74", 
                    "size": "4.6M"
                }, 
                "gameType": 2, 
                "ctorPath": "games/ddz/script/build/ddz_release.js", 
                "iconUrl": "", 
                "defaultRes": "Happy", 
                "isQuickStart": 1, 
                "isOffline": 0, 
                "autoDownload": 4
            }
        }, 
        "plugin_texas_v3_6_phone_type_3": {
            "params": {
                "gameMark": "texas", 
                "gameId": 8, 
                "gameName": "德州扑克", 
                "description": [
                    "1、简单易学，上手快~", 
                    "2、对战刺激，赢得多~"
                ], 
                "ctorName": "dz", 
                "isNew": 1, 
                "currentVer": {
                    "ver": 3.35105, 
                    "url": "http://111.203.187.142:8002/hall6/texas/texas.zip", 
                    "hall_min_required": 3, 
                    "changelogs": [
                        "1、简单易学，上手快~", 
                        "2、对战刺激，赢得多~"
                    ], 
                    "size": "2.61M", 
                    "md5": "18fd76650f50128d58b96e61020b3454"
                }, 
                "gameType": 3, 
                "ctorPath": "games/texas/script/build/dz_release.js", 
                "iconUrl": "", 
                "defaultRes": "TexasVIP", 
                "isQuickStart": 1
            }, 
            "type": "download"
        }, 
        "plugin_fruit_v3_6": {
            "params": {
                "gameMark": "fruit", 
                "gameId": 11, 
                "description": [
                    "1、轻松押注大丰收", 
                    "2、开开心心赢大奖"
                ], 
                "isNew": 1, 
                "ctorName": "fruit", 
                "gameName": "大丰收", 
                "currentVer": {
                    "ver": 3.601, 
                    "url": "http://111.203.187.145:9010/hall6/fruit/fruit_v3.601_1.zip", 
                    "hall_min_required": 6, 
                    "changelogs": [
                        "1、轻松押注大丰收", 
                        "2、开开心心赢大奖"
                    ], 
                    "size": "0.5M", 
                    "md5": "3fa79d7759f05a2cd64795b2e265ddc2"
                }, 
                "gameType": 1, 
                "ctorPath": "games/fruit/script/build/fruit_release.js", 
                "iconUrl": "", 
                "defaultRes": "FruitDefault", 
                "isOffline": 0, 
                "autoDownload": 4
            }, 
            "type": "download"
        }, 
        "common_dizhu_happy_v3_5": {
            "type": "common", 
            "params": {
                "defaultRes": "Happy", 
                "gameType": 2, 
                "gameMark": "ddz"
            }
        }, 
        "common_dizhu_happy": {
            "params": {
                "defaultRes": "Happy", 
                "gameType": 2, 
                "gameMark": "ddz"
            }, 
            "type": "common"
        }, 
        "plugin_douniu_old100_v3_5": {
            "params": {
                "gameMark": "douniu", 
                "gameId": 10, 
                "gameName": "百人拼十", 
                "description": [
                    "1、百人共一桌，热闹~", 
                    "2、上庄最刺激，过瘾~"
                ], 
                "ctorName": "dn", 
                "isNew": 1, 
                "currentVer": {
                    "ver": 3.501, 
                    "url": "http://ddz.dl.tuyoo.com/hall6/douniu/douniu_release_v3.373_2.zip", 
                    "hall_min_required": 3, 
                    "changelogs": [
                        "1、百人共一桌，热闹~", 
                        "2、上庄最刺激，过瘾~"
                    ], 
                    "size": "2.5M", 
                    "md5": "6164b1dcfc8ef89b4e372ab8e719e9a3"
                }, 
                "gameType": 1, 
                "ctorPath": "games/douniu/douniu_release.js", 
                "iconUrl": "", 
                "defaultRes": "BaiRenDefault"
            }, 
            "type": "download"
        }, 
        "plugin_dizhu_double": {
            "params": {
                "iconUrl": "", 
                "gameMark": "ddz", 
                "gameId": 6, 
                "description": [], 
                "ctorName": "ddz", 
                "currentVer": {
                    "ver": 0, 
                    "url": "http://ddz.dl.tuyoo.com/open/plugin_game/ddz_plugin_3_60_10.zip", 
                    "hall_min_required": 6, 
                    "changelogs": [
                        "1、经典场插件震撼首发~"
                    ], 
                    "size": "4.6M", 
                    "md5": "d14d851084eaf8d32871ac9cc6e2ac74"
                }, 
                "gameName": "二人场", 
                "isNew": 0, 
                "gameType": 5, 
                "ctorPath": "games/ddz/script/build/ddz_release.js", 
                "defaultRes": "DoublePerson", 
                "isQuickStart": 1, 
                "isOffline": 0, 
                "autoDownload": 4
            }, 
            "type": "download"
        }, 
        "plugin_texas_v3_6": {
            "params": {
                "gameMark": "texas", 
                "gameId": 8, 
                "gameName": "德州扑克", 
                "description": [
                    "1、简单易学，上手快~", 
                    "2、对战刺激，赢得多~"
                ], 
                "ctorName": "dz", 
                "isNew": 1, 
                "currentVer": {
                    "ver": 3.50101, 
                    "url": "http://111.203.187.142:8002/hall6/texas/texas_v3.501_1.zip", 
                    "hall_min_required": 3, 
                    "changelogs": [
                        "1、简单易学，上手快~", 
                        "2、对战刺激，赢得多~"
                    ], 
                    "md5": "51b3274aa79f05422040853719ff5200", 
                    "size": "2.17M"
                }, 
                "gameType": 1, 
                "ctorPath": "games/texas/script/build/dz_release.js", 
                "iconUrl": "", 
                "defaultRes": "TexasDefault"
            }, 
            "type": "download"
        }, 
        "common_mj_xlch_v3_5": {
            "type": "common", 
            "params": {
                "defaultRes": "XueLiuChengHe", 
                "gameType": 8, 
                "gameMark": "majiang"
            }
        }, 
        "plugin_douniu_100_v3_6": {
            "params": {
                "gameMark": "douniu-hundreds", 
                "gameId": 16, 
                "description": [
                    "1、百人共桌，热闹~", 
                    "2、上庄最刺激，过瘾~"
                ], 
                "isNew": 1, 
                "ctorName": "dnhundreds", 
                "gameName": "百人拼十", 
                "currentVer": {
                    "ver": 3.601, 
                    "url": "http://111.203.187.145:9010/hall6/douniu-hundreds/hundreds.zip", 
                    "hall_min_required": 6, 
                    "changelogs": [
                        "1、百人共四桌，热闹~", 
                        "2、上庄最刺激，过瘾~"
                    ], 
                    "size": "0.5M", 
                    "md5": "3fa79d7759f05a2cd64795b2e265ddc2"
                }, 
                "gameType": 1, 
                "ctorPath": "games/douniu-hundreds/script/build/douniu-hundreds_release.js", 
                "iconUrl": "", 
                "defaultRes": "BaiRenDefault", 
                "autoDownload": 4
            }, 
            "type": "download"
        }, 
        "plugin_dizhu_match": {
            "params": {
                "iconUrl": "", 
                "gameMark": "ddz", 
                "gameId": 6, 
                "description": [], 
                "ctorName": "ddz", 
                "currentVer": {
                    "ver": 0, 
                    "url": "http://ddz.dl.tuyoo.com/open/plugin_game/ddz_plugin_3_60_10.zip", 
                    "hall_min_required": 6, 
                    "changelogs": [
                        "1、经典场插件震撼首发~"
                    ], 
                    "size": "4.6M", 
                    "md5": "d14d851084eaf8d32871ac9cc6e2ac74"
                }, 
                "gameName": "比赛场", 
                "isNew": 0, 
                "gameType": 3, 
                "ctorPath": "games/ddz/script/build/ddz_release.js", 
                "defaultRes": "Match", 
                "isQuickStart": 1, 
                "isOffline": 0, 
                "autoDownload": 4
            }, 
            "type": "download"
        }, 
        "common_dizhu_double": {
            "params": {
                "defaultRes": "DoublePerson", 
                "gameType": 6, 
                "gameMark": "ddz"
            }, 
            "type": "common"
        }, 
        "common_next_page_v3_5": {
            "type": "common", 
            "params": {
                "defaultRes": "Exciting", 
                "gameType": 1, 
                "gameMark": "hall"
            }
        }, 
        "plugin_douniu_100": {
            "params": {
                "iconUrl": "", 
                "gameMark": "douniu-hundreds", 
                "gameId": 16, 
                "description": [
                    "1、百人共桌，热闹~", 
                    "2、上庄最刺激，过瘾~"
                ], 
                "ctorName": "dnhundreds", 
                "currentVer": {
                    "ver": 3, 
                    "url": "http://ddz.dl.tuyoo.com/hall6/douniu-hundreds/douniu-hundreds_v3.0_1.zip", 
                    "hall_min_required": 3, 
                    "changelogs": [
                        "1、百人共四桌，热闹~", 
                        "2、上庄最刺激，过瘾~"
                    ], 
                    "size": "2.2M", 
                    "md5": ""
                }, 
                "gameName": "百人拼十", 
                "isNew": 1, 
                "gameType": 1, 
                "ctorPath": "games/douniu-hundreds/script/build/douniu-hundreds_release.js", 
                "defaultRes": "BaiRenDefault"
            }, 
            "type": "download"
        }, 
        "common_next_page_v3_6": {
            "type": "common", 
            "params": {
                "defaultRes": "Exciting", 
                "gameType": 1, 
                "gameMark": "hall"
            }
        }, 
        "plugin_fruit_v3_5": {
            "params": {
                "gameMark": "fruit", 
                "gameId": 11, 
                "gameName": "大丰收", 
                "description": [
                    "1、轻松押注大丰收", 
                    "2、开开心心赢大奖"
                ], 
                "ctorName": "fruit", 
                "isNew": 1, 
                "currentVer": {
                    "ver": 3.501, 
                    "url": "http://111.203.187.145:9010/hall6/fruit/fruit_v3.501_4.zip", 
                    "hall_min_required": 3, 
                    "changelogs": [
                        "1、轻松押注大丰收", 
                        "2、开开心心赢大奖"
                    ], 
                    "size": "0.6M", 
                    "md5": "3d5550902fbd6918d61bec4bdd547d96"
                }, 
                "gameType": 1, 
                "ctorPath": "games/fruit/script/build/fruit_release.js", 
                "iconUrl": "", 
                "defaultRes": "FruitDefault", 
                "isOffline": 0
            }, 
            "type": "download"
        }, 
        "common_dizhu_single": {
            "params": {
                "defaultRes": "Single", 
                "gameType": 5, 
                "gameMark": "ddz"
            }, 
            "type": "common"
        }, 
        "plugin_dizhu_single_v3_6": {
            "type": "download", 
            "params": {
                "gameMark": "ddz", 
                "gameId": 6, 
                "description": [], 
                "isNew": 0, 
                "ctorName": "ddz", 
                "gameName": "单机场", 
                "currentVer": {
                    "ver": 0, 
                    "url": "http://ddz.dl.tuyoo.com/open/plugin_game/ddz_plugin_3_60_10.zip", 
                    "hall_min_required": 6, 
                    "changelogs": [
                        "1、经典场插件震撼首发~"
                    ], 
                    "md5": "d14d851084eaf8d32871ac9cc6e2ac74", 
                    "size": "4.6M"
                }, 
                "gameType": 6, 
                "ctorPath": "games/ddz/script/build/ddz_release.js", 
                "iconUrl": "", 
                "defaultRes": "Single", 
                "isQuickStart": 1, 
                "isOffline": 1, 
                "autoDownload": 4
            }
        }, 
        "common_dizhu_match_v3_5": {
            "type": "common", 
            "params": {
                "defaultRes": "Match", 
                "gameType": 3, 
                "gameMark": "ddz"
            }
        }, 
        "plugin_majiang": {
            "params": {
                "iconUrl": "", 
                "gameMark": "majiang", 
                "gameId": 7, 
                "description": [
                    "1、牌型丰富想胡就胡", 
                    "2、血战到底连胡不停"
                ], 
                "ctorName": "mj", 
                "currentVer": {
                    "ver": 3.36136, 
                    "url": "http://ddz.dl.tuyoo.com/hall6/majiang/majiang_release_v3.361_36.zip", 
                    "hall_min_required": 3, 
                    "changelogs": [
                        "1、牌型丰富想胡就胡", 
                        "2、血战到底连胡不停"
                    ], 
                    "size": "2.3M", 
                    "md5": ""
                }, 
                "gameName": "麻将", 
                "isNew": 1, 
                "gameType": 1, 
                "ctorPath": "games/majiang/majiang_release.js", 
                "defaultRes": "MaJiangDefault"
            }, 
            "type": "download"
        }, 
        "plugin_texas_v3_6_phone_type_4": {
            "params": {
                "gameMark": "texas", 
                "gameId": 8, 
                "gameName": "德州扑克", 
                "description": [
                    "1、简单易学，上手快~", 
                    "2、对战刺激，赢得多~"
                ], 
                "ctorName": "dz", 
                "isNew": 1, 
                "currentVer": {
                    "ver": 3.35105, 
                    "url": "http://111.203.187.142:8002/hall6/texas/texas.zip", 
                    "hall_min_required": 3, 
                    "changelogs": [
                        "1、简单易学，上手快~", 
                        "2、对战刺激，赢得多~"
                    ], 
                    "size": "2.61M", 
                    "md5": "18fd76650f50128d58b96e61020b3454"
                }, 
                "gameType": 4, 
                "ctorPath": "games/texas/script/build/dz_release.js", 
                "iconUrl": "", 
                "defaultRes": "TexasMatch", 
                "isQuickStart": 1
            }, 
            "type": "download"
        }, 
        "common_dizhu_match": {
            "params": {
                "defaultRes": "Match", 
                "gameType": 3, 
                "gameMark": "ddz"
            }, 
            "type": "common"
        }, 
        "plugin_fruit": {
            "params": {
                "iconUrl": "", 
                "gameMark": "fruit", 
                "gameId": 11, 
                "description": [
                    "1、轻松押注大丰收", 
                    "2、开开心心赢大奖"
                ], 
                "ctorName": "fruit", 
                "currentVer": {
                    "ver": 1, 
                    "url": "http://ddz.dl.tuyoo.com/hall6/fruit/fruit_release_v2.2_2.zip", 
                    "hall_min_required": 3, 
                    "changelogs": [
                        "1、轻松押注大丰收", 
                        "2、开开心心赢大奖"
                    ], 
                    "size": "1.4M", 
                    "md5": ""
                }, 
                "gameName": "大丰收", 
                "isNew": 1, 
                "gameType": 1, 
                "ctorPath": "games/fruit/script/build/fruit_release.js", 
                "defaultRes": "FruitDefault", 
                "isOffline": 0
            }, 
            "type": "download"
        }, 
        "plugin_douniu_100_v3_5": {
            "params": {
                "gameMark": "douniu-hundreds", 
                "gameId": 16, 
                "gameName": "百人拼十", 
                "description": [
                    "1、百人共桌，热闹~", 
                    "2、上庄最刺激，过瘾~"
                ], 
                "ctorName": "dnhundreds", 
                "isNew": 1, 
                "currentVer": {
                    "ver": 3.502, 
                    "url": "http://111.203.187.145:9010/hall6/douniu-hundreds/douniu-hundreds_v3.5_7.zip", 
                    "hall_min_required": 3, 
                    "changelogs": [
                        "1、百人共四桌，热闹~", 
                        "2、上庄最刺激，过瘾~"
                    ], 
                    "size": "1.6M", 
                    "md5": "e7aeef12a935d44eb45009bc4604441e"
                }, 
                "gameType": 1, 
                "ctorPath": "games/douniu-hundreds/script/build/douniu-hundreds_release.js", 
                "iconUrl": "", 
                "defaultRes": "BaiRenDefault"
            }, 
            "type": "download"
        }, 
        "common_dizhu_laizi": {
            "params": {
                "defaultRes": "Rascal", 
                "gameType": 4, 
                "gameMark": "ddz"
            }, 
            "type": "common"
        }, 
        "common_mj_blood_v3_5": {
            "type": "common", 
            "params": {
                "defaultRes": "Blood", 
                "gameType": 7, 
                "gameMark": "majiang"
            }
        }, 
        "package_v3_5": {
            "params": {
                "iconUrl": "", 
                "pages": [
                    {
                        "nodes": [], 
                        "form": "dizhu3x2"
                    }
                ], 
                "defaultRes": "PackageDefault"
            }, 
            "type": "package"
        }, 
        "plugin_dizhu_classics_v3_6": {
            "type": "download", 
            "params": {
                "gameMark": "ddz", 
                "gameId": 6, 
                "description": [], 
                "isNew": 0, 
                "ctorName": "ddz", 
                "gameName": "经典场", 
                "currentVer": {
                    "ver": 0, 
                    "url": "http://ddz.dl.tuyoo.com/open/plugin_game/ddz_plugin_3_60_10.zip", 
                    "hall_min_required": 6, 
                    "changelogs": [
                        "1、经典场插件震撼首发~"
                    ], 
                    "md5": "d14d851084eaf8d32871ac9cc6e2ac74", 
                    "size": "4.6M"
                }, 
                "gameType": 1, 
                "ctorPath": "games/ddz/script/build/ddz_release.js", 
                "iconUrl": "", 
                "defaultRes": "Classic", 
                "isQuickStart": 1, 
                "isOffline": 0, 
                "autoDownload": 4
            }
        }, 
        "plugin_t3flush": {
            "params": {
                "iconUrl": "http://111.203.187.143:20002/t3flush/images/jinsanshun_icon.png", 
                "gameMark": "t3flush", 
                "gameId": 18, 
                "description": [
                    "1、公平防作弊金三顺", 
                    "2、爱拼才赢大锅底"
                ], 
                "ctorName": "ss", 
                "currentVer": {
                    "ver": 3, 
                    "url": "http://ddz.dl.tuyoo.com/hall6/t3flush/t3flush_release_v3.501_1.zip", 
                    "hall_min_required": 2, 
                    "changelogs": [
                        "1、公平防作弊金三顺", 
                        "2、爱拼才赢大锅底"
                    ], 
                    "size": "1.4M", 
                    "md5": ""
                }, 
                "gameName": "金三顺", 
                "isNew": 1, 
                "gameType": 1, 
                "ctorPath": "games/t3flush/script/build/ss_release.js", 
                "defaultRes": "T3FlushDefault"
            }, 
            "type": "download"
        }, 
        "common_dizhu_classics_v3_5": {
            "type": "common", 
            "params": {
                "defaultRes": "Classics", 
                "gameType": 1, 
                "gameMark": "ddz"
            }
        }, 
        "common_dizhu_classics": {
            "params": {
                "defaultRes": "Classics", 
                "gameType": 1, 
                "gameMark": "ddz"
            }, 
            "type": "common"
        }, 
        "common_next_page": {
            "params": {
                "defaultRes": "Exciting", 
                "gameType": 1, 
                "gameMark": "hall"
            }, 
            "type": "common"
        }, 
        "common_dizhu_laizi_v3_5": {
            "type": "common", 
            "params": {
                "defaultRes": "Rascal", 
                "gameType": 4, 
                "gameMark": "ddz"
            }
        }, 
        "plugin_dizhu_single": {
            "params": {
                "iconUrl": "", 
                "gameMark": "ddz", 
                "gameId": 6, 
                "description": [], 
                "ctorName": "ddz", 
                "currentVer": {
                    "ver": 0, 
                    "url": "http://ddz.dl.tuyoo.com/open/plugin_game/ddz_plugin_3_60_10.zip", 
                    "hall_min_required": 6, 
                    "changelogs": [
                        "1、经典场插件震撼首发~"
                    ], 
                    "size": "4.6M", 
                    "md5": "d14d851084eaf8d32871ac9cc6e2ac74"
                }, 
                "gameName": "单机场", 
                "isNew": 0, 
                "gameType": 6, 
                "ctorPath": "games/ddz/script/build/ddz_release.js", 
                "defaultRes": "Single", 
                "isQuickStart": 1, 
                "isOffline": 1, 
                "autoDownload": 4
            }, 
            "type": "download"
        }, 
        "plugin_dog_ios_v3_5": {
            "params": {
                "gameMark": "dog", 
                "gameId": 19, 
                "gameName": "跑狗", 
                "description": [
                    "1、轻松押注跑狗", 
                    "2、开开心心赢大奖"
                ], 
                "ctorName": "dog", 
                "isNew": 1, 
                "currentVer": {
                    "ver": 3.503, 
                    "url": "http://111.203.187.145:9010/hall6/dog/dog_v3.5_5.zip", 
                    "hall_min_required": 3, 
                    "changelogs": [
                        "1、轻松押注跑狗", 
                        "2、开开心心赢大奖"
                    ], 
                    "size": "1.4M", 
                    "md5": "b694d01f71840a822111cd4d14b1f3b7"
                }, 
                "gameType": 1, 
                "ctorPath": "games/dog/script/build/dog_release.js", 
                "iconUrl": "http://ddz.dl.tuyoo.com/hall6/imgs/hall_plugin_dog_icon_1.png", 
                "defaultRes": "DogDefault"
            }, 
            "type": "download"
        }, 
        "plugin_texas_v3_6_pc_type_3": {
            "params": {
                "gameMark": "texas", 
                "gameId": 8, 
                "gameName": "德州扑克", 
                "description": [
                    "1、简单易学，上手快~", 
                    "2、对战刺激，赢得多~"
                ], 
                "ctorName": "dz", 
                "isNew": 1, 
                "currentVer": {
                    "ver": 3.35105, 
                    "url": "http://111.203.187.142:8002/hall6/texas/texas.zip", 
                    "hall_min_required": 3, 
                    "changelogs": [
                        "1、简单易学，上手快~", 
                        "2、对战刺激，赢得多~"
                    ], 
                    "size": "2.61M", 
                    "md5": "18fd76650f50128d58b96e61020b3454"
                }, 
                "gameType": 8, 
                "ctorPath": "games/texas/script/build/dz_release.js", 
                "iconUrl": "", 
                "defaultRes": "TexasMttMatch", 
                "isQuickStart": 1
            }, 
            "type": "download"
        }, 
        "plugin_t3card_v3_5": {
            "params": {
                "gameMark": "t3card", 
                "gameId": 1, 
                "gameName": "三张牌", 
                "description": [
                    "1、公平防作弊三张牌", 
                    "2、闷到底赢得大锅底"
                ], 
                "ctorName": "zjh", 
                "isNew": 1, 
                "currentVer": {
                    "ver": 3.503, 
                    "url": "http://ddz.dl.tuyoo.com/hall6/t3card/t3card_release_v3.502.zip", 
                    "hall_min_required": 2, 
                    "changelogs": [
                        "1、公平防作弊三张牌", 
                        "2、闷到底赢得大锅底"
                    ], 
                    "size": "3M", 
                    "md5": "bfd74eb7d64b0b954b0abd9529b6b073"
                }, 
                "gameType": 1, 
                "ctorPath": "games/t3card/t3card_release.js", 
                "iconUrl": "", 
                "defaultRes": "T3CardDefault"
            }, 
            "type": "download"
        }, 
        "plugin_douniu_crazy_v3_5": {
            "params": {
                "gameMark": "douniu", 
                "gameId": 10, 
                "gameName": "疯狂拼十", 
                "description": [
                    "1、看牌再加倍，安逸~", 
                    "2、简单又刺激，精彩~"
                ], 
                "ctorName": "dn", 
                "isNew": 0, 
                "currentVer": {
                    "ver": 3.501, 
                    "url": "http://ddz.dl.tuyoo.com/hall6/douniu/douniu_release_v3.373_2.zip", 
                    "hall_min_required": 2, 
                    "changelogs": [
                        "1、看牌再加倍，安逸~", 
                        "2、简单又刺激，精彩~"
                    ], 
                    "size": "2.5M", 
                    "md5": "6164b1dcfc8ef89b4e372ab8e719e9a3"
                }, 
                "gameType": 2, 
                "ctorPath": "games/douniu/douniu_release.js", 
                "iconUrl": "", 
                "defaultRes": "DouNiuDefault"
            }, 
            "type": "download"
        }, 
        "common_dizhu_single_v3_5": {
            "type": "common", 
            "params": {
                "defaultRes": "Single", 
                "gameType": 5, 
                "gameMark": "ddz"
            }
        }, 
        "plugin_baohuang": {
            "params": {
                "iconUrl": "http://ddz.dl.tuyoo.com/hall6/imgs/hall_plugin_baohuang_icon.png", 
                "gameMark": "baohuang", 
                "gameId": 17, 
                "description": [
                    "1、明皇暗保步步惊心", 
                    "2、揭竿而起胜者为皇"
                ], 
                "ctorName": "bh", 
                "currentVer": {
                    "ver": 3.502, 
                    "url": "http://ddz.dl.tuyoo.com/hall6/baohuang/baohuang_release_v3.501_2.zip", 
                    "hall_min_required": 3, 
                    "changelogs": [
                        "1、明皇暗保步步惊心", 
                        "2、揭竿而起胜者为皇"
                    ], 
                    "size": "2.3M", 
                    "md5": ""
                }, 
                "gameName": "保皇", 
                "isNew": 1, 
                "gameType": 1, 
                "ctorPath": "games/baohuang/script/baohuang_release.js", 
                "defaultRes": "BaoHuangDefault"
            }, 
            "type": "download"
        }, 
        "common_mj_blood": {
            "params": {
                "defaultRes": "Blood", 
                "gameType": 7, 
                "gameMark": "majiang"
            }, 
            "type": "common"
        }, 
        "plugin_texas_v3_5": {
            "params": {
                "gameMark": "texas", 
                "gameId": 8, 
                "gameName": "德州扑克", 
                "description": [
                    "1、简单易学，上手快~", 
                    "2、对战刺激，赢得多~"
                ], 
                "ctorName": "dz", 
                "isNew": 1, 
                "currentVer": {
                    "ver": 3.50101, 
                    "url": "http://ddz.dl.tuyoo.com/hall6/texas/texas_release_v3.501_2.zip", 
                    "hall_min_required": 3, 
                    "changelogs": [
                        "1、简单易学，上手快~", 
                        "2、对战刺激，赢得多~"
                    ], 
                    "md5": "51b3274aa79f05422040853719ff5200", 
                    "size": "2.17M"
                }, 
                "gameType": 1, 
                "ctorPath": "games/texas/script/build/dz_release.js", 
                "iconUrl": "", 
                "defaultRes": "TexasDefault"
            }, 
            "type": "download"
        }, 
        "plugin_dog_v3_6": {
            "params": {
                "gameMark": "dog", 
                "gameId": 19, 
                "description": [
                    "1、轻松押注跑狗", 
                    "2、开开心心赢大奖"
                ], 
                "isNew": 1, 
                "ctorName": "dog", 
                "gameName": "跑狗", 
                "currentVer": {
                    "ver": 3.601, 
                    "url": "http://111.203.187.145:9010/hall6/dog/dog_v3.601_1.zip", 
                    "hall_min_required": 6, 
                    "changelogs": [
                        "1、轻松押注跑狗", 
                        "2、开开心心赢大奖"
                    ], 
                    "size": "1.3M", 
                    "md5": "d4c34ea5438d83475c670c56e4ce6133"
                }, 
                "gameType": 1, 
                "ctorPath": "games/dog/script/build/dog_release.js", 
                "iconUrl": "http://ddz.dl.tuyoo.com/hall6/imgs/hall_plugin_dog_icon_1.png", 
                "defaultRes": "DogDefault", 
                "autoDownload": 4
            }, 
            "type": "download"
        }, 
        "plugin_dog_v3_5": {
            "params": {
                "gameMark": "dog", 
                "gameId": 19, 
                "gameName": "跑狗", 
                "description": [
                    "1、轻松押注跑狗", 
                    "2、开开心心赢大奖"
                ], 
                "ctorName": "dog", 
                "isNew": 1, 
                "currentVer": {
                    "ver": 3.502, 
                    "url": "http://111.203.187.145:9010/hall6/dog/dog_v3.5_5.zip", 
                    "hall_min_required": 3, 
                    "changelogs": [
                        "1、轻松押注跑狗", 
                        "2、开开心心赢大奖"
                    ], 
                    "size": "1.4M", 
                    "md5": "b694d01f71840a822111cd4d14b1f3b7"
                }, 
                "gameType": 1, 
                "ctorPath": "games/dog/script/build/dog_release.js", 
                "iconUrl": "http://ddz.dl.tuyoo.com/hall6/imgs/hall_plugin_dog_icon_1.png", 
                "defaultRes": "DogDefault"
            }, 
            "type": "download"
        }, 
        "plugin_dizhu_laizi_v3_6": {
            "type": "download", 
            "params": {
                "gameMark": "ddz", 
                "gameId": 6, 
                "description": [], 
                "isNew": 0, 
                "ctorName": "ddz", 
                "gameName": "癞子场", 
                "currentVer": {
                    "ver": 0, 
                    "url": "http://ddz.dl.tuyoo.com/open/plugin_game/ddz_plugin_3_60_10.zip", 
                    "hall_min_required": 6, 
                    "changelogs": [
                        "1、经典场插件震撼首发~"
                    ], 
                    "md5": "d14d851084eaf8d32871ac9cc6e2ac74", 
                    "size": "4.6M"
                }, 
                "gameType": 4, 
                "ctorPath": "games/ddz/script/build/ddz_release.js", 
                "iconUrl": "", 
                "defaultRes": "Rascal", 
                "isQuickStart": 1, 
                "isOffline": 0, 
                "autoDownload": 4
            }
        }, 
        "plugin_texas_v3_6_pc_type_2": {
            "params": {
                "gameMark": "texas", 
                "gameId": 8, 
                "gameName": "德州扑克", 
                "description": [
                    "1、简单易学，上手快~", 
                    "2、对战刺激，赢得多~"
                ], 
                "ctorName": "dz", 
                "isNew": 1, 
                "currentVer": {
                    "ver": 3.35105, 
                    "url": "http://111.203.187.142:8002/hall6/texas/texas.zip", 
                    "hall_min_required": 3, 
                    "changelogs": [
                        "1、简单易学，上手快~", 
                        "2、对战刺激，赢得多~"
                    ], 
                    "size": "2.61M", 
                    "md5": "18fd76650f50128d58b96e61020b3454"
                }, 
                "gameType": 7, 
                "ctorPath": "games/texas/script/build/dz_release.js", 
                "iconUrl": "", 
                "defaultRes": "TexasSngMatch", 
                "isQuickStart": 1
            }, 
            "type": "download"
        }, 
        "plugin_t3flush_v3_5": {
            "params": {
                "gameMark": "t3flush", 
                "gameId": 18, 
                "gameName": "金三顺", 
                "description": [
                    "1、公平防作弊金三顺", 
                    "2、爱拼才赢大锅底"
                ], 
                "ctorName": "ss", 
                "isNew": 1, 
                "currentVer": {
                    "ver": 3.502, 
                    "url": "http://ddz.dl.tuyoo.com/hall6/t3flush/t3flush_release_v3.502_1.zip", 
                    "hall_min_required": 2, 
                    "changelogs": [
                        "1、公平防作弊金三顺", 
                        "2、爱拼才赢大锅底"
                    ], 
                    "size": "3M", 
                    "md5": "9385b0ad0625e8e37d9b612c26b8bc62"
                }, 
                "gameType": 1, 
                "ctorPath": "games/t3flush/script/build/ss_release.js", 
                "iconUrl": "http://111.203.187.143:20002/t3flush/images/jinsanshun_icon.png", 
                "defaultRes": "T3FlushDefault"
            }, 
            "type": "download"
        }, 
        "plugin_dizhu_laizi": {
            "params": {
                "iconUrl": "", 
                "gameMark": "ddz", 
                "gameId": 6, 
                "description": [], 
                "ctorName": "ddz", 
                "currentVer": {
                    "ver": 0, 
                    "url": "http://ddz.dl.tuyoo.com/open/plugin_game/ddz_plugin_3_60_10.zip", 
                    "hall_min_required": 6, 
                    "changelogs": [
                        "1、经典场插件震撼首发~"
                    ], 
                    "size": "4.6M", 
                    "md5": "d14d851084eaf8d32871ac9cc6e2ac74"
                }, 
                "gameName": "癞子场", 
                "isNew": 0, 
                "gameType": 4, 
                "ctorPath": "games/ddz/script/build/ddz_release.js", 
                "defaultRes": "Rascal", 
                "isQuickStart": 1, 
                "isOffline": 0, 
                "autoDownload": 4
            }, 
            "type": "download"
        }, 
        "plugin_baohuang_v3_5": {
            "params": {
                "gameMark": "baohuang", 
                "gameId": 17, 
                "gameName": "保皇", 
                "description": [
                    "1、明皇暗保步步惊心", 
                    "2、揭竿而起胜者为皇"
                ], 
                "ctorName": "bh", 
                "isNew": 1, 
                "currentVer": {
                    "ver": 3.5, 
                    "url": "http://ddz.dl.tuyoo.com/hall6/baohuang/baohuang_release_v3.501_2.zip", 
                    "hall_min_required": 3, 
                    "changelogs": [
                        "1、明皇暗保步步惊心", 
                        "2、揭竿而起胜者为皇"
                    ], 
                    "size": "3M", 
                    "md5": "368c82bad1a107aadb4d5fe5d6793496"
                }, 
                "gameType": 1, 
                "ctorPath": "games/baohuang/script/baohuang_release.js", 
                "iconUrl": "http://ddz.dl.tuyoo.com/hall6/imgs/hall_plugin_baohuang_icon.png", 
                "defaultRes": "BaoHuangDefault"
            }, 
            "type": "download"
        }, 
        "plugin_dog": {
            "params": {
                "iconUrl": "http://ddz.dl.tuyoo.com/hall6/imgs/hall_plugin_dog_icon_1.png", 
                "gameMark": "dog", 
                "gameId": 19, 
                "description": [
                    "1、轻松押注跑狗", 
                    "2、开开心心赢大奖"
                ], 
                "ctorName": "dog", 
                "currentVer": {
                    "ver": 1, 
                    "url": "http://ddz.dl.tuyoo.com/hall6/dog/dog_release_v3.5_1.zip", 
                    "hall_min_required": 3, 
                    "changelogs": [
                        "1、轻松押注跑狗", 
                        "2、开开心心赢大奖"
                    ], 
                    "size": "1.4M", 
                    "md5": ""
                }, 
                "gameName": "跑狗", 
                "isNew": 1, 
                "gameType": 1, 
                "ctorPath": "games/dog/script/build/dog_release.js", 
                "defaultRes": "DogDefault"
            }, 
            "type": "download"
        }, 
        "plugin_dizhu_classics": {
            "params": {
                "iconUrl": "", 
                "gameMark": "ddz", 
                "gameId": 6, 
                "description": [], 
                "ctorName": "ddz", 
                "currentVer": {
                    "ver": 0, 
                    "url": "http://ddz.dl.tuyoo.com/open/plugin_game/ddz_plugin_3_60_10.zip", 
                    "hall_min_required": 6, 
                    "changelogs": [
                        "1、经典场插件震撼首发~"
                    ], 
                    "size": "4.6M", 
                    "md5": "d14d851084eaf8d32871ac9cc6e2ac74"
                }, 
                "gameName": "经典场", 
                "isNew": 0, 
                "gameType": 1, 
                "ctorPath": "games/ddz/script/build/ddz_release.js", 
                "defaultRes": "Classic", 
                "isQuickStart": 1, 
                "isOffline": 0, 
                "autoDownload": 4
            }, 
            "type": "download"
        }, 
        "plugin_texas": {
            "params": {
                "iconUrl": "", 
                "gameMark": "texas", 
                "gameId": 8, 
                "description": [
                    "1、简单易学，上手快~", 
                    "2、对战刺激，赢得多~"
                ], 
                "ctorName": "dz", 
                "currentVer": {
                    "ver": 3.35105, 
                    "url": "http://111.203.187.142:8002/hall6/texas/texas.zip", 
                    "hall_min_required": 3, 
                    "changelogs": [
                        "1、简单易学，上手快~", 
                        "2、对战刺激，赢得多~"
                    ], 
                    "md5": "18fd76650f50128d58b96e61020b3454", 
                    "size": "2.61M"
                }, 
                "gameName": "德州扑克", 
                "isNew": 1, 
                "gameType": 1, 
                "ctorPath": "games/texas/script/build/dz_release.js", 
                "defaultRes": "TexasDefault"
            }, 
            "type": "download"
        }, 
        "plugin_t3card": {
            "params": {
                "iconUrl": "", 
                "gameMark": "t3card", 
                "gameId": 1, 
                "description": [
                    "1、公平防作弊三张牌", 
                    "2、闷到底赢得大锅底"
                ], 
                "ctorName": "zjh", 
                "currentVer": {
                    "ver": 3, 
                    "url": "http://ddz.dl.tuyoo.com/hall6/t3card/t3card_release_v2.2_3.zip", 
                    "hall_min_required": 2, 
                    "changelogs": [
                        "1、公平防作弊三张牌", 
                        "2、闷到底赢得大锅底"
                    ], 
                    "size": "1.4M", 
                    "md5": ""
                }, 
                "gameName": "三张牌", 
                "isNew": 1, 
                "gameType": 1, 
                "ctorPath": "games/t3card/t3card_release.js", 
                "defaultRes": "T3CardDefault"
            }, 
            "type": "download"
        }, 
        "plugin_douniu_crazy": {
            "params": {
                "iconUrl": "", 
                "gameMark": "douniu", 
                "gameId": 10, 
                "description": [
                    "1、看牌再加倍，安逸~", 
                    "2、简单又刺激，精彩~"
                ], 
                "ctorName": "dn", 
                "currentVer": {
                    "ver": 2, 
                    "url": "http://ddz.dl.tuyoo.com/hall6/douniu/douniu_release_v2.3_2.zip", 
                    "hall_min_required": 2, 
                    "changelogs": [
                        "1、看牌再加倍，安逸~", 
                        "2、简单又刺激，精彩~"
                    ], 
                    "size": "2.9M", 
                    "md5": ""
                }, 
                "gameName": "疯狂拼十", 
                "isNew": 0, 
                "gameType": 2, 
                "ctorPath": "games/douniu/douniu_release.js", 
                "defaultRes": "DouNiuDefault"
            }, 
            "type": "download"
        }, 
        "plugin_majiang_v3_5": {
            "params": {
                "gameMark": "majiang", 
                "gameId": 7, 
                "gameName": "麻将", 
                "description": [
                    "1、牌型丰富想胡就胡", 
                    "2、血战到底连胡不停"
                ], 
                "ctorName": "mj", 
                "isNew": 1, 
                "currentVer": {
                    "ver": 3.5, 
                    "url": "http://ddz.dl.tuyoo.com/hall6/majiang/majiang_release_v3.371_12.zip", 
                    "hall_min_required": 3, 
                    "changelogs": [
                        "1、牌型丰富想胡就胡", 
                        "2、血战到底连胡不停"
                    ], 
                    "size": "3M", 
                    "md5": "6628fdeca24b5b67a7a903c021bdbb34"
                }, 
                "gameType": 1, 
                "ctorPath": "games/majiang/majiang_release.js", 
                "iconUrl": "", 
                "defaultRes": "MaJiangDefault"
            }, 
            "type": "download"
        }, 
        "plugin_dizhu_double_v3_6": {
            "type": "download", 
            "params": {
                "gameMark": "ddz", 
                "gameId": 6, 
                "description": [], 
                "isNew": 0, 
                "ctorName": "ddz", 
                "gameName": "二人场", 
                "currentVer": {
                    "ver": 0, 
                    "url": "http://ddz.dl.tuyoo.com/open/plugin_game/ddz_plugin_3_60_10.zip", 
                    "hall_min_required": 6, 
                    "changelogs": [
                        "1、经典场插件震撼首发~"
                    ], 
                    "md5": "d14d851084eaf8d32871ac9cc6e2ac74", 
                    "size": "4.6M"
                }, 
                "gameType": 5, 
                "ctorPath": "games/ddz/script/build/ddz_release.js", 
                "iconUrl": "", 
                "defaultRes": "DoublePerson", 
                "isQuickStart": 1, 
                "isOffline": 0, 
                "autoDownload": 4
            }
        }, 
        "common_mj_xlch": {
            "params": {
                "defaultRes": "XueLiuChengHe", 
                "gameType": 8, 
                "gameMark": "majiang"
            }, 
            "type": "common"
        }, 
        "plugin_texas_v3_6_phone_type_2": {
            "params": {
                "gameMark": "texas", 
                "gameId": 8, 
                "gameName": "德州扑克", 
                "description": [
                    "1、简单易学，上手快~", 
                    "2、对战刺激，赢得多~"
                ], 
                "ctorName": "dz", 
                "isNew": 1, 
                "currentVer": {
                    "ver": 3.35105, 
                    "url": "http://111.203.187.142:8002/hall6/texas/texas.zip", 
                    "hall_min_required": 3, 
                    "changelogs": [
                        "1、简单易学，上手快~", 
                        "2、对战刺激，赢得多~"
                    ], 
                    "size": "2.61M", 
                    "md5": "18fd76650f50128d58b96e61020b3454"
                }, 
                "gameType": 2, 
                "ctorPath": "games/texas/script/build/dz_release.js", 
                "iconUrl": "", 
                "defaultRes": "TexasRoomList", 
                "isQuickStart": 1
            }, 
            "type": "download"
        }
    }
}

class TestGameList(unittest.TestCase):
    userId = 10001
    gameId = 6
    clientId = 'IOS_3.6_momo'
    testContext = HallTestMockContext()
    
    def setUp(self):
        self.testContext.startMock()
        self.testContext.configure.setJson('game:9999:map.clientid', clientIdMap, 0)
        self.testContext.configure.setJson('game:9999:item', item_conf, 0)
        self.testContext.configure.setJson('game:9999:products', products_conf, 0)
        self.testContext.configure.setJson('game:9999:store', store_template_conf, 0)
        self.testContext.configure.setJson('game:9999:store', store_default_conf, clientIdMap[self.clientId])
        self.testContext.configure.setJson('game:9999:vip', vip_conf, 0)
        self.testContext.configure.setJson('game:9999:gamelist', gamelist_conf, 0)
        
        hallitem._initialize()
        hallvip._initialize()
        hallgamelist._initialize()
        
    def tearDown(self):
        self.testContext.stopMock()
        
    def testGetGameList(self):
        gameList = hallgamelist.getGameList(self.clientId)
        print gameList
        
if __name__ == '__main__':
    unittest.main()
    
    