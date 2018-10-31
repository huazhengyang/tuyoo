# -*- coding=utf-8
'''
Created on 2015年8月3日

@author: zhaojiangang
'''
import json
import unittest
from entity.hallstore_test import clientIdMap
from hall.entity import hallgamelist2
from hall.servers.util.hall_handler import HallHelper
from test_base import HallTestMockContext

gamelist2_conf = {
    "games": [
        {
            "gameId": 1,
            "gameMark": "t3card",
            "description": [
                "1、玩法最全的三张牌",
                "2、国人最爱玩儿的扑克游戏"
            ],
            "versions": [
                {
                    "url": "${http_download}/hall/plugin/game/t3card_release_v3.701.zip",
                    "md5": "94c1e3436d14f48d558ffae98765c185",
                    "hall_min_required": 6,
                    "changelogs": [
                        "1、扎金花3.7插件震撼首发~"
                    ],
                    "ver": "3.701",
                    "size": "3.2M",
                    "autoDownload": 4
                },
                {
                    "url": "${http_download}/hall/plugin/game/t3card_release_v3.702.zip",
                    "md5": "eeac7e87ca96c40fb70d7ef9d15da83b",
                    "hall_min_required": 6,
                    "changelogs": [
                        "1、扎金花3.7插件震撼首发~"
                    ],
                    "ver": "3.702",
                    "size": "3.2M",
                    "autoDownload": 4
                }
            ]
        },
        {
            "gameId": 3,
            "gameMark": "chess",
            "description": [
                "1、支持联网支持单机的象棋",
                "2、残局多多，快来破局"
            ],
            "versions": [
                {
                    "url": "${http_download}/hall/plugin/game/chinesechess_3.701_release_beta_4.zip",
                    "md5": "e484570b33be0ddbf0e34df30844cea3",
                    "hall_min_required": 6,
                    "changelogs": [
                        "1、象棋3.7插件震撼首发~"
                    ],
                    "ver": "3.701",
                    "size": "2.8M",
                    "autoDownload": 0
                }
            ]
        },
        {
            "gameId": 6,
            "gameMark": "ddz",
            "description": [
                "1、玩法最全的斗地主",
                "2、奖励最多的斗地主"
            ],
            "versions": [
                {
                    "url": "${http_download}/hall/plugin/game/ddz_release_v3.701_1.zip",
                    "md5": "6a600229775e591fe1f98d69cf03b30e",
                    "hall_min_required": 6,
                    "changelogs": [
                        "1、斗地主3.7插件震撼首发~"
                    ],
                    "ver": "3.701",
                    "size": "4.6M",
                    "autoDownload": 0
                }
            ]
        },
        {
            "gameId": 7,
            "gameMark": "majiang",
            "description": [
                "1、玩法最多的麻将游戏",
                "2、奖励最多的麻将游戏"
            ],
            "versions": [
                {
                    "url": "${http_download}/hall/plugin/game/mj_release_v3.701_5.zip",
                    "md5": "6b3757819ec075facaea312b825caaab",
                    "hall_min_required": 6,
                    "changelogs": [
                        "1、麻将3.7插件123~"
                    ],
                    "ver": "3.701",
                    "size": "4.6M",
                    "autoDownload": 0
                }
            ]
        },
        {
            "gameId": 8,
            "gameMark": "texas",
            "description": [
                "1、简单易学，上手快~",
                "2、对战刺激，赢得多~"
            ],
            "versions": [
                {
                    "url": "${http_download}/hall/plugin/game/texas_release_v3.703.zip",
                    "md5": "43cc342645ec86ce982996c6c5dad54e",
                    "hall_min_required": 6,
                    "changelogs": [
                        "1、德州v3.703插件"
                    ],
                    "ver": "3.703",
                    "size": "2.6M",
                    "autoDownload": 0
                }
            ]
        },
        {
            "gameId": 10,
            "gameMark": "douniu",
            "description": [
                "最刺激的斗牛游戏"
            ],
            "versions": [
                {
                    "ver": "3.701",
                    "url": "${http_download}/hall/plugin/game/douniu_release_v3.701_2.zip",
                    "md5": "c315a3a253156c4c05ee43e6daeecc8b",
                    "hall_min_required": 6,
                    "changelogs": [
                        "1、支持MTT大比赛~"
                    ],
                    "size": "5.4M",
                    "autoDownload": 4
                }
            ]
        },
        {
            "gameId": 11,
            "gameMark": "fruit",
            "description": [
                "1、轻松押注大丰收",
                "2、开开心心赢大奖"
            ],
            "versions": [
                {
                    "ver": "3.701",
                    "url": "${http_download}/hall/plugin/game/fruit_release_v3.702.zip",
                    "md5": "2f1cdd1a4891d4afe2b708d020ba32b0",
                    "hall_min_required": 6,
                    "changelogs": [
                        "1、轻松押注大丰收",
                        "2、开开心心赢大奖"
                    ],
                    "size": "1.1M",
                    "autoDownload": 0
                }
            ]
        },
        {
            "gameId": 16,
            "gameMark": "dnhundreds",
            "description": [
                "1、轻松押注百人牛牛",
                "2、开开心心唯吾独尊"
            ],
            "versions": [
                {
                    "ver": "3.701",
                    "url": "${http_download}/hall/plugin/game/dnhundreds_release_v3.704.zip",
                    "md5": "9daf63c9fd6116cd06ba3f89577a4222",
                    "hall_min_required": 6,
                    "changelogs": [
                        "1、轻松押注百人牛牛",
                        "2、开开心心唯吾独尊"
                    ],
                    "size": "1.3M",
                    "autoDownload": 4
                }
            ]
        },
        {
            "gameId": 17,
            "gameMark": "baohuang",
            "description": [
                "1、牌好当皇帝",
                "2、保皇抱大腿"
            ],
            "versions": [
                {
                    "ver": "3.701",
                    "url": "${http_download}/hall/plugin/game/baohuang_release_v3.701_2.zip",
                    "md5": "d6e7e7b6123ae40832da70addb414446",
                    "hall_min_required": 6,
                    "changelogs": [
                        "1、牌好当皇帝",
                        "2、保皇抱大腿"
                    ],
                    "size": "3.9M",
                    "autoDownload": 0
                }
            ]
        },
        {
            "gameId": 18,
            "gameMark": "t3flush",
            "description": [
                "1、轻松押注金三顺",
                "2、开开心心赢大奖"
            ],
            "versions": [
                {
                    "ver": "3.701",
                    "url": "${http_download}/hall/plugin/game/t3flush_release_v3.701.zip",
                    "md5": "9cfb7b6ef8b9ab9318b4375106491372",
                    "hall_min_required": 6,
                    "changelogs": [
                        "1、轻松押注大丰收",
                        "2、开开心心赢大奖"
                    ],
                    "size": "4M",
                    "autoDownload": 0
                },
                {
                    "ver": "3.702",
                    "url": "${http_download}/hall/plugin/game/t3flush_release_v3.702.zip",
                    "md5": "631b2a8495eb228222024b1cf002322e",
                    "hall_min_required": 6,
                    "changelogs": [
                        "1、轻松押注大丰收",
                        "2、开开心心赢大奖"
                    ],
                    "size": "4M",
                    "autoDownload": 0
                }
            ]
        },
        {
            "gameId": 19,
            "gameMark": "dog",
            "description": [
                "1、轻松押注跑狗",
                "2、开开心心赢大奖"
            ],
            "versions": [
                {
                    "ver": "3.701",
                    "url": "${http_download}/hall/plugin/game/dog_release_v3.703.zip",
                    "md5": "cc428be4ad57bbc7c153489955a9c8f6",
                    "hall_min_required": 6,
                    "changelogs": [
                        "1、轻松押注跑狗",
                        "2、开开心心赢大奖"
                    ],
                    "size": "2.7M",
                    "autoDownload": 0
                }
            ]
        },
        {
            "gameId": 21,
            "gameMark": "phz",
            "description": [
                "1、轻松押注跑胡子",
                "2、开开心心赢大奖"
            ],
            "versions": [
                {
                    "ver": "3.701",
                    "url": "${http_download}/hall/plugin/game/phz_debug_3.701_v1.zip",
                    "md5": "d4c34ea5438d83475c670c56e4ce6133",
                    "hall_min_required": 6,
                    "changelogs": [
                        "1、轻松押注跑胡子",
                        "2、开开心心赢大奖"
                    ],
                    "size": "1.3M",
                    "autoDownload": 0
                }
            ]
        },
        {
            "gameId": 22,
            "gameMark": "fanfanle",
            "description": [
                "1、通用牌桌内小游戏之三张牌翻翻乐"
            ],
            "versions": [
                {
                    "ver": "3.701",
                    "url": "${http_download}/hall/plugin/game/ffl_debug_3.701_v1.zip",
                    "md5": "d4c34ea5438d83475c670c56e4ce6133",
                    "hall_min_required": 6,
                    "changelogs": [
                        "1、翻翻乐首发"
                    ],
                    "size": "0.3M",
                    "autoDownload": 0
                }
            ]
        }
    ],
    "templates": [
        {
            "des": "默认模板，用于v3.701",
            "name": "default",
            "innerGames": [
                {
                    "type": "innerGame",
                    "typeId": "hall.gamenode.inner.game",
                    "params": {
                        "des": "公共牌桌内小游戏之三张牌翻翻乐",
                        "gameId": 22,
                        "version": "3.701"
                    }
                }
            ],
            "pages": [
                {
                    "nodes": [
                        {
                            "type": "roomlist",
                            "typeId": "hall.gamenode.normal",
                            "params": {
                                "gameId": 6,
                                "gameName": "经典场",
                                "version": "3.701",
                                "iconUrl": "",
                                "nameUrl": "",
                                "defaultRes": "Classic",
                                "pluginParams": {
                                    "gameType": 1
                                }
                            }
                        },
                        {
                            "type": "roomlist",
                            "typeId": "hall.gamenode.normal",
                            "params": {
                                "gameId": 6,
                                "version": "3.701",
                                "gameName": "欢乐场",
                                "iconUrl": "",
                                "nameUrl": "",
                                "defaultRes": "Happy",
                                "pluginParams": {
                                    "gameType": 2
                                }
                            }
                        },
                        {
                            "type": "roomlist",
                            "typeId": "hall.gamenode.normal",
                            "params": {
                                "gameId": 6,
                                "gameName": "比赛场",
                                "version": "3.701",
                                "iconUrl": "",
                                "nameUrl": "",
                                "defaultRes": "Match",
                                "pluginParams": {
                                    "gameType": 3
                                },
                                "quitAlert": 1,
                                "quitAlertName": "去比赛"
                            }
                        },
                        {
                            "type": "roomlist",
                            "typeId": "hall.gamenode.normal",
                            "params": {
                                "gameId": 6,
                                "gameName": "癞子场",
                                "version": "3.701",
                                "iconUrl": "",
                                "nameUrl": "",
                                "defaultRes": "Rascal",
                                "pluginParams": {
                                    "gameType": 4
                                }
                            }
                        },
                        {
                            "type": "roomlist",
                            "typeId": "hall.gamenode.normal",
                            "params": {
                                "gameId": 6,
                                "gameName": "单机场",
                                "version": "3.701",
                                "iconUrl": "",
                                "nameUrl": "",
                                "defaultRes": "Single",
                                "pluginParams": {
                                    "gameType": 6
                                }
                            }
                        },
                        {
                            "type": "quickstart",
                            "typeId": "hall.gamenode.normal",
                            "params": {
                                "gameId": 6,
                                "gameName": "斗地主快速开始",
                                "version": "3.701",
                                "nameUrl": "",
                                "iconUrl": "",
                                "defaultRes": "QuickStart",
                                "pluginParams": {}
                            }
                        }
                    ]
                },
                {
                    "nodes": [
                        {
                            "type": "roomlist",
                            "typeId": "hall.gamenode.normal",
                            "params": {
                                "gameId": 6,
                                "gameName": "二人场",
                                "version": "3.701",
                                "iconUrl": "",
                                "nameUrl": "",
                                "defaultRes": "DoublePerson",
                                "pluginParams": {
                                    "gameType": 5
                                }
                            }
                        },
                        {
                            "type": "game",
                            "typeId": "hall.gamenode.normal",
                            "params": {
                                "gameId": 8,
                                "gameName": "德州",
                                "version": "3.703",
                                "iconUrl": "",
                                "nameUrl": "",
                                "defaultRes": "TexasDefault",
                                "pluginParams": {
                                }
                            }
                        },
                        {
                            "type": "game",
                            "typeId": "hall.gamenode.normal",
                            "params": {
                                "gameId": 1,
                                "gameName": "三张牌",
                                "version": "3.702",
                                "iconUrl": "",
                                "nameUrl": "",
                                "defaultRes": "T3CardDefault",
                                "pluginParams": {
                                }
                            }
                        },
                        {
                            "type": "game",
                            "typeId": "hall.gamenode.normal",
                            "params": {
                                "gameId": 10,
                                "gameName": "拼十",
                                "version": "3.701",
                                "iconUrl": "",
                                "nameUrl": "",
                                "defaultRes": "DouNiuDefault",
                                "pluginParams": {}
                            }
                        },
                        {
                            "type": "game",
                            "typeId": "hall.gamenode.normal",
                            "params": {
                                "gameId": 16,
                                "gameName": "百人牛牛",
                                "version": "3.701",
                                "iconUrl": "",
                                "nameUrl": "",
                                "defaultRes": "BaiRenDefault",
                                "pluginParams": {
                                }
                            }
                        },
                        {
                            "type": "game",
                            "typeId": "hall.gamenode.normal",
                            "params": {
                                "gameId": 11,
                                "gameName": "大丰收",
                                "version": "3.701",
                                "iconUrl": "",
                                "nameUrl": "",
                                "defaultRes": "FruitDefault",
                                "pluginParams": {
                                    "gameType": 1
                                }
                            }
                        }
                    ]
                },
                {
                    "nodes": [
                        {
                            "type": "game",
                            "typeId": "hall.gamenode.normal",
                            "params": {
                                "gameId": 7,
                                "gameName": "麻将",
                                "version": "3.701",
                                "iconUrl": "",
                                "nameUrl": "",
                                "defaultRes": "MaJiangDefault",
                                "pluginParams": {}
                            }
                        },
                        {
                            "type": "game",
                            "typeId": "hall.gamenode.normal",
                            "params": {
                                "gameId": 19,
                                "gameName": "跑狗",
                                "version": "3.701",
                                "iconUrl": "",
                                "nameUrl": "",
                                "defaultRes": "DogDefault",
                                "pluginParams": {
                                }
                            }
                        },
                        {
                            "type": "game",
                            "typeId": "hall.gamenode.normal",
                            "params": {
                                "gameId": 3,
                                "gameName": "象棋",
                                "version": "3.701",
                                "iconUrl": "",
                                "nameUrl": "",
                                "defaultRes": "ChessDefault",
                                "pluginParams": {
                                }
                            }
                        },
                        {
                            "type": "game",
                            "typeId": "hall.gamenode.normal",
                            "params": {
                                "gameId": 18,
                                "gameName": "金三顺",
                                "version": "3.702",
                                "iconUrl": "",
                                "nameUrl": "",
                                "defaultRes": "T3FlushDefault",
                                "pluginParams": {
                                }
                            }
                        },
                        {
                            "type": "game",
                            "typeId": "hall.gamenode.normal",
                            "params": {
                                "gameId": 17,
                                "gameName": "保皇",
                                "version": "3.701",
                                "iconUrl": "${http_download}/hall/plugin/img/hall_plugin_baohuang_new.png",
                                "nameUrl": "",
                                "defaultRes": "",
                                "pluginParams": {
                                }
                            }
                        },
                        {
                            "type": "game",
                            "typeId": "hall.gamenode.normal",
                            "params": {
                                "gameId": 21,
                                "gameName": "跑胡子",
                                "version": "3.701",
                                "iconUrl": "",
                                "nameUrl": "",
                                "defaultRes": "PaoHuZiDefault",
                                "pluginParams": {
                                }
                            }
                        }
                    ]
                }
            ]
        },
        {
            "des": "地主大厅v3.71模板，与default模板的差别是保皇的icon资源差别",
            "name": "plugin_v3.71",
            "pages": [
                {
                    "nodes": [
                        {
                            "type": "roomlist",
                            "typeId": "hall.gamenode.normal",
                            "params": {
                                "gameId": 6,
                                "gameName": "经典场",
                                "version": "3.701",
                                "iconUrl": "",
                                "nameUrl": "",
                                "defaultRes": "Classic",
                                "pluginParams": {
                                    "gameType": 1
                                }
                            }
                        },
                        {
                            "type": "roomlist",
                            "typeId": "hall.gamenode.normal",
                            "params": {
                                "gameId": 6,
                                "version": "3.701",
                                "gameName": "欢乐场",
                                "iconUrl": "",
                                "nameUrl": "",
                                "defaultRes": "Happy",
                                "pluginParams": {
                                    "gameType": 2
                                }
                            }
                        },
                        {
                            "type": "roomlist",
                            "typeId": "hall.gamenode.normal",
                            "params": {
                                "gameId": 6,
                                "gameName": "比赛场",
                                "version": "3.701",
                                "iconUrl": "",
                                "nameUrl": "",
                                "defaultRes": "Match",
                                "pluginParams": {
                                    "gameType": 3
                                },
                                "quitAlert": 1,
                                "quitAlertName": "去比赛"
                            }
                        },
                        {
                            "type": "roomlist",
                            "typeId": "hall.gamenode.normal",
                            "params": {
                                "gameId": 6,
                                "gameName": "癞子场",
                                "version": "3.701",
                                "iconUrl": "",
                                "nameUrl": "",
                                "defaultRes": "Rascal",
                                "pluginParams": {
                                    "gameType": 4
                                }
                            }
                        },
                        {
                            "type": "roomlist",
                            "typeId": "hall.gamenode.normal",
                            "params": {
                                "gameId": 6,
                                "gameName": "单机场",
                                "version": "3.701",
                                "iconUrl": "",
                                "nameUrl": "",
                                "defaultRes": "Single",
                                "pluginParams": {
                                    "gameType": 6
                                }
                            }
                        },
                        {
                            "type": "quickstart",
                            "typeId": "hall.gamenode.normal",
                            "params": {
                                "gameId": 6,
                                "gameName": "斗地主快速开始",
                                "version": "3.701",
                                "nameUrl": "",
                                "iconUrl": "",
                                "defaultRes": "QuickStart",
                                "pluginParams": {}
                            }
                        }
                    ]
                },
                {
                    "nodes": [
                        {
                            "type": "roomlist",
                            "typeId": "hall.gamenode.normal",
                            "params": {
                                "gameId": 6,
                                "gameName": "二人场",
                                "version": "3.701",
                                "iconUrl": "",
                                "nameUrl": "",
                                "defaultRes": "DoublePerson",
                                "pluginParams": {
                                    "gameType": 5
                                }
                            }
                        },
                        {
                            "type": "game",
                            "typeId": "hall.gamenode.normal",
                            "params": {
                                "gameId": 8,
                                "gameName": "德州",
                                "version": "3.703",
                                "iconUrl": "",
                                "nameUrl": "",
                                "defaultRes": "TexasDefault",
                                "pluginParams": {
                                }
                            }
                        },
                        {
                            "type": "game",
                            "typeId": "hall.gamenode.normal",
                            "params": {
                                "gameId": 1,
                                "gameName": "三张牌",
                                "version": "3.702",
                                "iconUrl": "",
                                "nameUrl": "",
                                "defaultRes": "T3CardDefault",
                                "pluginParams": {
                                }
                            }
                        },
                        {
                            "type": "game",
                            "typeId": "hall.gamenode.normal",
                            "params": {
                                "gameId": 10,
                                "gameName": "拼十",
                                "version": "3.701",
                                "iconUrl": "",
                                "nameUrl": "",
                                "defaultRes": "DouNiuDefault",
                                "pluginParams": {}
                            }
                        },
                        {
                            "type": "game",
                            "typeId": "hall.gamenode.normal",
                            "params": {
                                "gameId": 16,
                                "gameName": "百人牛牛",
                                "version": "3.701",
                                "iconUrl": "",
                                "nameUrl": "",
                                "defaultRes": "BaiRenDefault",
                                "pluginParams": {
                                }
                            }
                        },
                        {
                            "type": "game",
                            "typeId": "hall.gamenode.normal",
                            "params": {
                                "gameId": 11,
                                "gameName": "大丰收",
                                "version": "3.701",
                                "iconUrl": "",
                                "nameUrl": "",
                                "defaultRes": "FruitDefault",
                                "pluginParams": {
                                    "gameType": 1
                                }
                            }
                        }
                    ]
                },
                {
                    "nodes": [
                        {
                            "type": "game",
                            "typeId": "hall.gamenode.normal",
                            "params": {
                                "gameId": 7,
                                "gameName": "麻将",
                                "version": "3.701",
                                "iconUrl": "",
                                "nameUrl": "",
                                "defaultRes": "MaJiangDefault",
                                "pluginParams": {}
                            }
                        },
                        {
                            "type": "game",
                            "typeId": "hall.gamenode.normal",
                            "params": {
                                "gameId": 19,
                                "gameName": "跑狗",
                                "version": "3.701",
                                "iconUrl": "",
                                "nameUrl": "",
                                "defaultRes": "DogDefault",
                                "pluginParams": {
                                }
                            }
                        },
                        {
                            "type": "game",
                            "typeId": "hall.gamenode.normal",
                            "params": {
                                "gameId": 3,
                                "gameName": "象棋",
                                "version": "3.701",
                                "iconUrl": "",
                                "nameUrl": "",
                                "defaultRes": "ChessDefault",
                                "pluginParams": {
                                }
                            }
                        },
                        {
                            "type": "game",
                            "typeId": "hall.gamenode.normal",
                            "params": {
                                "gameId": 18,
                                "gameName": "金三顺",
                                "version": "3.702",
                                "iconUrl": "",
                                "nameUrl": "",
                                "defaultRes": "T3FlushDefault",
                                "pluginParams": {
                                }
                            }
                        },
                        {
                            "type": "game",
                            "typeId": "hall.gamenode.normal",
                            "params": {
                                "gameId": 17,
                                "gameName": "保皇",
                                "version": "3.701",
                                "iconUrl": "",
                                "nameUrl": "",
                                "defaultRes": "BaoHuangDefault",
                                "pluginParams": {
                                }
                            }
                        }
                    ]
                }
            ]
        },
        {
            "des": "斗牛大厅v3.711模板",
            "name": "plugins_douniu_v3.711",
            "pages": [
                {
                    "nodes": [
                        {
                            "type": "roomlist",
                            "typeId": "hall.gamenode.normal",
                            "params": {
                                "gameId": 10,
                                "gameName": "疯狂场",
                                "version": "3.701",
                                "iconUrl": "",
                                "nameUrl": "",
                                "defaultRes": "FengKuang",
                                "pluginParams": {
                                    "gameType": 2
                                }
                            }
                        },
                        {
                            "type": "game",
                            "typeId": "hall.gamenode.normal",
                            "params": {
                                "gameId": 1,
                                "gameName": "三张牌",
                                "version": "3.702",
                                "iconUrl": "",
                                "nameUrl": "",
                                "defaultRes": "T3CardDefault",
                                "pluginParams": {
                                }
                            }
                        },
                        {
                            "type": "roomlist",
                            "typeId": "hall.gamenode.normal",
                            "params": {
                                "gameId": 10,
                                "version": "3.701",
                                "gameName": "快拼场",
                                "iconUrl": "",
                                "nameUrl": "",
                                "defaultRes": "KuaiPin",
                                "pluginParams": {
                                    "gameType": 4
                                }
                            }
                        },
                        {
                            "type": "game",
                            "typeId": "hall.gamenode.normal",
                            "params": {
                                "gameId": 16,
                                "gameName": "百人牛牛",
                                "version": "3.701",
                                "iconUrl": "",
                                "nameUrl": "",
                                "defaultRes": "BaiRenDefault",
                                "pluginParams": {
                                }
                            }
                        },
                        {
                            "type": "roomlist",
                            "typeId": "hall.gamenode.normal",
                            "params": {
                                "gameId": 10,
                                "gameName": "贵宾室",
                                "version": "3.701",
                                "nameUrl": "",
                                "iconUrl": "",
                                "defaultRes": "GuiBinShi",
                                "pluginParams": {
                                    "gameType": 5
                                }
                            }
                        },
                        {
                            "type": "quickstart",
                            "typeId": "hall.gamenode.normal",
                            "params": {
                                "gameId": 10,
                                "gameName": "拼十快速开始",
                                "version": "3.701",
                                "nameUrl": "",
                                "iconUrl": "",
                                "defaultRes": "QuickStart",
                                "pluginParams": {}
                            }
                        }
                    ]
                },
                {
                    "nodes": [
                        {
                            "type": "game",
                            "typeId": "hall.gamenode.normal",
                            "params": {
                                "gameId": 18,
                                "gameName": "金三顺",
                                "version": "3.702",
                                "iconUrl": "",
                                "nameUrl": "",
                                "defaultRes": "T3FlushDefault",
                                "pluginParams": {
                                }
                            }
                        },
                        {
                            "type": "game",
                            "typeId": "hall.gamenode.normal",
                            "params": {
                                "gameId": 11,
                                "gameName": "大丰收",
                                "version": "3.701",
                                "iconUrl": "",
                                "nameUrl": "",
                                "defaultRes": "FruitDefault",
                                "pluginParams": {
                                    "gameType": 1
                                }
                            }
                        },
                        {
                            "type": "game",
                            "typeId": "hall.gamenode.normal",
                            "params": {
                                "gameId": 17,
                                "gameName": "保皇",
                                "version": "3.701",
                                "iconUrl": "",
                                "nameUrl": "",
                                "defaultRes": "BaoHuangDefault",
                                "pluginParams": {
                                }
                            }
                        },
                        {
                            "type": "game",
                            "typeId": "hall.gamenode.normal",
                            "params": {
                                "gameId": 19,
                                "gameName": "跑狗",
                                "version": "3.701",
                                "iconUrl": "",
                                "nameUrl": "",
                                "defaultRes": "DogDefault",
                                "pluginParams": {
                                }
                            }
                        },
                        {
                            "type": "game",
                            "typeId": "hall.gamenode.normal",
                            "params": {
                                "gameId": 3,
                                "gameName": "象棋",
                                "version": "3.701",
                                "iconUrl": "",
                                "nameUrl": "",
                                "defaultRes": "ChessDefault",
                                "pluginParams": {
                                }
                            }
                        }
                    ]
                },
                {
                    "nodes": [
                        {
                            "type": "game",
                            "typeId": "hall.gamenode.normal",
                            "params": {
                                "gameId": 7,
                                "gameName": "麻将",
                                "version": "3.701",
                                "iconUrl": "",
                                "nameUrl": "",
                                "defaultRes": "MaJiangDefault",
                                "pluginParams": {}
                            }
                        }
                    ]
                }
            ]
        },
        {
            "des": "三张牌大厅v3.711模板",
            "name": "t3card_plugin_v3.711",
            "pages": [
                {
                    "nodes": [
                        {
                            "type": "roomlist",
                            "typeId": "hall.gamenode.normal",
                            "params": {
                                "gameId": 1,
                                "gameName": "三张大厅",
                                "version": "3.702",
                                "iconUrl": "",
                                "nameUrl": "",
                                "defaultRes": "T3CardNormal",
                                "pluginParams": {
                                    "gameType": 1
                                }
                            }
                        },
                        {
                            "type": "game",
                            "typeId": "hall.gamenode.normal",
                            "params": {
                                "gameId": 18,
                                "gameName": "金三顺",
                                "version": "3.702",
                                "iconUrl": "",
                                "nameUrl": "",
                                "defaultRes": "T3FlushDefault",
                                "pluginParams": {
                                }
                            }
                        },
                        {
                            "type": "roomlist",
                            "typeId": "hall.gamenode.normal",
                            "params": {
                                "gameId": 1,
                                "version": "3.702",
                                "gameName": "贵宾室",
                                "iconUrl": "",
                                "nameUrl": "",
                                "defaultRes": "T3CardVIP",
                                "pluginParams": {
                                    "gameType": 2
                                }
                            }
                        },
                        {
                            "type": "game",
                            "typeId": "hall.gamenode.normal",
                            "params": {
                                "gameId": 16,
                                "gameName": "百人牛牛",
                                "version": "3.701",
                                "iconUrl": "",
                                "nameUrl": "",
                                "defaultRes": "BaiRenDefault",
                                "pluginParams": {
                                }
                            }
                        },
                        {
                            "type": "roomlist",
                            "typeId": "hall.gamenode.normal",
                            "params": {
                                "gameId": 1,
                                "gameName": "比赛场",
                                "version": "3.702",
                                "iconUrl": "",
                                "nameUrl": "",
                                "defaultRes": "T3CardMatch",
                                "pluginParams": {
                                    "gameType": 3
                                }
                            }
                        },
                        {
                            "type": "quickstart",
                            "typeId": "hall.gamenode.normal",
                            "params": {
                                "gameId": 1,
                                "gameName": "三张快速开始",
                                "version": "3.702",
                                "nameUrl": "",
                                "iconUrl": "",
                                "defaultRes": "T3CardQuickStart",
                                "pluginParams": {}
                            }
                        }
                    ]
                },
                {
                    "nodes": [
                        {
                            "type": "game",
                            "typeId": "hall.gamenode.normal",
                            "params": {
                                "gameId": 7,
                                "gameName": "麻将",
                                "version": "3.701",
                                "iconUrl": "",
                                "nameUrl": "",
                                "defaultRes": "MaJiangDefault",
                                "pluginParams": {}
                            }
                        },
                        {
                            "type": "game",
                            "typeId": "hall.gamenode.normal",
                            "params": {
                                "gameId": 10,
                                "gameName": "拼十",
                                "version": "3.701",
                                "iconUrl": "",
                                "nameUrl": "",
                                "defaultRes": "DouNiuDefault",
                                "pluginParams": {}
                            }
                        },
                        {
                            "type": "game",
                            "typeId": "hall.gamenode.normal",
                            "params": {
                                "gameId": 11,
                                "gameName": "大丰收",
                                "version": "3.701",
                                "iconUrl": "",
                                "nameUrl": "",
                                "defaultRes": "FruitDefault",
                                "pluginParams": {
                                    "gameType": 1
                                }
                            }
                        },
                        {
                            "type": "game",
                            "typeId": "hall.gamenode.normal",
                            "params": {
                                "gameId": 19,
                                "gameName": "跑狗",
                                "version": "3.701",
                                "iconUrl": "",
                                "nameUrl": "",
                                "defaultRes": "DogDefault",
                                "pluginParams": {
                                }
                            }
                        },
                        {
                            "type": "game",
                            "typeId": "hall.gamenode.normal",
                            "params": {
                                "gameId": 3,
                                "gameName": "象棋",
                                "version": "3.701",
                                "iconUrl": "",
                                "nameUrl": "",
                                "defaultRes": "ChessDefault",
                                "pluginParams": {
                                }
                            }
                        }
                    ]
                }
            ]
        },
        {
            "des": "地主大厅v3.711提审包，不开其他任何插件的模板",
            "name": "hall6_without_plugin_v3.71",
            "pages": [
                {
                    "nodes": [
                        {
                            "type": "roomlist",
                            "typeId": "hall.gamenode.normal",
                            "params": {
                                "gameId": 6,
                                "gameName": "经典场",
                                "version": "3.701",
                                "iconUrl": "",
                                "nameUrl": "",
                                "defaultRes": "Classic",
                                "pluginParams": {
                                    "gameType": 1
                                }
                            }
                        },
                        {
                            "type": "roomlist",
                            "typeId": "hall.gamenode.normal",
                            "params": {
                                "gameId": 6,
                                "version": "3.701",
                                "gameName": "欢乐场",
                                "iconUrl": "",
                                "nameUrl": "",
                                "defaultRes": "Happy",
                                "pluginParams": {
                                    "gameType": 2
                                }
                            }
                        },
                        {
                            "type": "roomlist",
                            "typeId": "hall.gamenode.normal",
                            "params": {
                                "gameId": 6,
                                "gameName": "比赛场",
                                "version": "3.701",
                                "iconUrl": "",
                                "nameUrl": "",
                                "defaultRes": "Match",
                                "pluginParams": {
                                    "gameType": 3
                                },
                                "quitAlert": 1,
                                "quitAlertName": "去比赛"
                            }
                        },
                        {
                            "type": "roomlist",
                            "typeId": "hall.gamenode.normal",
                            "params": {
                                "gameId": 6,
                                "gameName": "癞子场",
                                "version": "3.701",
                                "iconUrl": "",
                                "nameUrl": "",
                                "defaultRes": "Rascal",
                                "pluginParams": {
                                    "gameType": 4
                                }
                            }
                        },
                        {
                            "type": "roomlist",
                            "typeId": "hall.gamenode.normal",
                            "params": {
                                "gameId": 6,
                                "gameName": "单机场",
                                "version": "3.701",
                                "iconUrl": "",
                                "nameUrl": "",
                                "defaultRes": "Single",
                                "pluginParams": {
                                    "gameType": 6
                                }
                            }
                        },
                        {
                            "type": "quickstart",
                            "typeId": "hall.gamenode.normal",
                            "params": {
                                "gameId": 6,
                                "gameName": "斗地主快速开始",
                                "version": "3.701",
                                "nameUrl": "",
                                "iconUrl": "",
                                "defaultRes": "QuickStart",
                                "pluginParams": {}
                            }
                        }
                    ]
                },
                {
                    "nodes": [
                        {
                            "type": "roomlist",
                            "typeId": "hall.gamenode.normal",
                            "params": {
                                "gameId": 6,
                                "gameName": "二人场",
                                "version": "3.701",
                                "iconUrl": "",
                                "nameUrl": "",
                                "defaultRes": "DoublePerson",
                                "pluginParams": {
                                    "gameType": 5
                                }
                            }
                        }
                    ]
                }
            ]
        }
    ]
}

class TestGameList(unittest.TestCase):
    userId = 10001
    gameId = 6
    clientId = 'IOS_3.6_momo'
    testContext = HallTestMockContext()
    
    def setUp(self):
        self.testContext.startMock()
        self.testContext.configure.setJson('game:9999:map.clientid', clientIdMap, 0)
        self.testContext.configure.setJson('game:9999:gamelist2', gamelist2_conf, 0)
        
        hallgamelist2._initialize()
        
    def tearDown(self):
        self.testContext.stopMock()
        
    def testGetGameList(self):
#         暂时只能测试default模板
        template = hallgamelist2.getUITemplate(self.gameId, self.userId, self.clientId)
        games, pages = HallHelper.encodeHallUITemplage(self.gameId, self.userId, self.clientId, template)
        print json.dumps({'games':games, 'pages':pages}, ensure_ascii=False, indent=4)
        
if __name__ == '__main__':
    unittest.main()
    
