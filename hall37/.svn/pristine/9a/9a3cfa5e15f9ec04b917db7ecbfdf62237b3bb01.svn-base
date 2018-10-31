# -*- coding=utf-8
'''
Created on 2015年6月30日

@author: zhaojiangang
'''
import unittest

from entity.hallstore_test import clientIdMap, products_conf, \
    store_template_conf, store_default_conf
from entity.hallvip_test import vip_conf
from hall.entity import hallbenefits, hallitem, hallvip
import poker.util.timestamp as pktimestamp
from test_base import HallTestMockContext


benefits_conf = {
    "minChip": 400,
    "sendChip": 2000,
    "maxTimes": 2,
    "privileges": [
        {
            "typeId": "common.vip",
            "desc": "",
            "name": "VIP特权",
            "levels": [
                {
                    "typeId": "vipLevel",
                    "name": "无特权",
                    "level": 0,
                    "desc": "成为VIP1每天多赠送1次"
                },
                {
                    "typeId": "vipLevel",
                    "name": "VIP1特权",
                    "level": 1,
                    "times": "+1",
                    "desc": "成为VIP2每次多送1000"
                },
                {
                    "typeId": "vipLevel",
                    "name": "VIP2特权",
                    "level": 2,
                    "sendChip": "*2",
                    "desc": ""
                }
            ]
        },
        {
            "typeId": "common.member",
            "desc": "",
            "name": "会员特权",
            "sendChip": "+1000"
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
            "kindId": 1018,
            "typeId": "common.simple",
            "displayName": "智运会决赛门票",
            "visibleInBag": 1,
            "desc": "可报名智运会决赛",
            "singleMode": 1,
            "pic": "${http_download}/hall/item/imgs/item_1018.png",
            "units": {
                "typeId": "common.count",
                "displayName": "张"
            },
            "removeFromBagWhenRemainingZero": 1,
            "removeFromBagWhenExpires": 0
        },
        {
            "kindId": 1019,
            "typeId": "common.simple",
            "displayName": "中扑赛复赛门票",
            "visibleInBag": 1,
            "desc": "中扑赛复赛门票",
            "singleMode": 1,
            "pic": "${http_download}/hall/item/imgs/item_1019.png",
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
            "kindId": 2002,
            "typeId": "common.simple",
            "displayName": "喇叭",
            "visibleInBag": 1,
            "desc": "玩牌时可以用来和牌友，语音交流，每次消耗1个",
            "singleMode": 1,
            "pic": "${http_download}/hall/item/imgs/item_2002.png",
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
            "desc": "尊贵的会员，每天登陆可多领3万金币，并拥有会员专属标志，会员互动表情，双倍积分等会员特权",
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
                            },
                            {
                                "itemId": "item:2003",
                                "count": 1
                            }
                        ]
                    }
                }
            ]
        },
        {
            "kindId": 89,
            "typeId": "common.memberCard",
            "displayName": "会员卡",
            "visibleInBag": 1,
            "desc": "尊贵的会员，每天登陆可多领1万金币，并拥有会员专属标志，会员互动表情，双倍积分等会员特权",
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
                        "desc": "10000金币",
                        "items": [
                            {
                                "itemId": "user:chip",
                                "count": 10000
                            },
                            {
                                "itemId": "item:2003",
                                "count": 1
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
                    "displayName": "卸下",
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
                    "displayName": "卸下",
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
                    "displayName": "卸下",
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
                    "displayName": "卸下",
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
                    "displayName": "卸下",
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
                    "displayName": "卸下",
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
                    "displayName": "卸下",
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
                    "displayName": "卸下",
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
                    "displayName": "卸下",
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
                    "displayName": "卸下",
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
                    "displayName": "卸下",
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
                    "displayName": "卸下",
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
                    "displayName": "卸下",
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
                    "displayName": "卸下",
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
                    "displayName": "卸下",
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
                    "displayName": "卸下",
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
                    "displayName": "卸下",
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
                    "displayName": "卸下",
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
                    "displayName": "卸下",
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
                    "displayName": "卸下",
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
                    "displayName": "卸下",
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
                    "displayName": "卸下",
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
                    "displayName": "卸下",
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
                    "displayName": "卸下",
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
                    "displayName": "卸下",
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
                    "displayName": "卸下",
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
                    "displayName": "卸下",
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
                    "displayName": "卸下",
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
                    "displayName": "卸下",
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
                    "displayName": "卸下",
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
                    "displayName": "卸下",
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
                    "displayName": "卸下",
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
                    "displayName": "卸下",
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
                    "displayName": "卸下",
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
                    "displayName": "卸下",
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
                    "displayName": "卸下",
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
                    "displayName": "卸下",
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
                    "displayName": "卸下",
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
                    "displayName": "卸下",
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
                    "displayName": "卸下",
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
            "displayName": "自然力量",
            "visibleInBag": 1,
            "desc": "使用后可佩戴自然力量头像框",
            "singleMode": 0,
            "pic": "${http_download}/hall/item/imgs/item_4135.png",
            "units": {
                "typeId": "common.day",
                "displayName": "天"
            },
            "removeFromBagWhenRemainingZero": 0,
            "removeFromBagWhenExpires": 1,
            "localRes": {
                "resName": "border_nature"
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
                    "displayName": "卸下",
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
            "pic": "${http_download}/hall/item/imgs/item_4136.png",
            "units": {
                "typeId": "common.day",
                "displayName": "天"
            },
            "removeFromBagWhenRemainingZero": 0,
            "removeFromBagWhenExpires": 1,
            "localRes": {
                "resName": "border_classic"
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
                    "displayName": "卸下",
                    "typeId": "common.decroation.unwear"
                }
            ]
        },
        {
            "kindId": 4137,
            "typeId": "common.decroation",
            "displayName": "金属时代",
            "visibleInBag": 1,
            "desc": "使用后可佩戴金属时代头像框",
            "singleMode": 0,
            "pic": "${http_download}/hall/item/imgs/item_4137.png",
            "units": {
                "typeId": "common.day",
                "displayName": "天"
            },
            "removeFromBagWhenRemainingZero": 0,
            "removeFromBagWhenExpires": 1,
            "localRes": {
                "resName": "border_metal"
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
                    "displayName": "卸下",
                    "typeId": "common.decroation.unwear"
                }
            ]
        },
        {
            "kindId": 4138,
            "typeId": "common.simple",
            "displayName": "金砖",
            "visibleInBag": 1,
            "desc": "黄金有价，情无价，送给你最珍贵的人",
            "singleMode": 1,
            "pic": "${http_download}/hall/item/imgs/item_4138.png",
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
                        "count": 1000000
                    }
                },
                {
                    "name": "present",
                    "displayName": "赠送",
                    "typeId": "common.present",
                    "mail": "您赠送\\${presentCount}\\${units}\\${item}，给\\${targetUserId}",
                    "params": {
                        "type": "countAndUserId",
                        "desc": "赠送描述",
                        "confirm": 1
                    }
                }
            ]
        },
        {
            "kindId": 4139,
            "typeId": "common.decroation",
            "displayName": "激萌忍者",
            "visibleInBag": 1,
            "desc": "使用后可佩戴激萌忍者头像",
            "singleMode": 1,
            "pic": "${http_download}/hall/item/imgs/item_4139.png",
            "units": {
                "typeId": "common.day",
                "displayName": "天"
            },
            "removeFromBagWhenRemainingZero": 0,
            "removeFromBagWhenExpires": 1,
            "localRes": {
                "resName": "head_ninja_m"
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
                    "displayName": "卸下",
                    "typeId": "common.decroation.unwear"
                },
                {
                    "name": "present",
                    "displayName": "赠送",
                    "typeId": "common.present",
                    "mail": "您赠送\\${presentCount}\\${units}\\${item}，给\\${targetUserId}",
                    "params": {
                        "type": "countAndUserId",
                        "desc": "赠送描述",
                        "confirm": 1
                    }
                }
            ]
        },
        {
            "kindId": 4140,
            "typeId": "common.decroation",
            "displayName": "俏皮girl",
            "visibleInBag": 1,
            "desc": "使用后可佩戴俏皮girl头像",
            "singleMode": 1,
            "pic": "${http_download}/hall/item/imgs/item_4140.png",
            "units": {
                "typeId": "common.day",
                "displayName": "天"
            },
            "removeFromBagWhenRemainingZero": 0,
            "removeFromBagWhenExpires": 1,
            "localRes": {
                "resName": "head_naughty_f"
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
                    "displayName": "卸下",
                    "typeId": "common.decroation.unwear"
                },
                {
                    "name": "present",
                    "displayName": "赠送",
                    "typeId": "common.present",
                    "mail": "您赠送\\${presentCount}\\${units}\\${item}，给\\${targetUserId}",
                    "params": {
                        "type": "countAndUserId",
                        "desc": "赠送描述",
                        "confirm": 1
                    }
                }
            ]
        },
        {
            "kindId": 4141,
            "typeId": "common.exchange",
            "displayName": "10元电话卡",
            "visibleInBag": 1,
            "desc": "可兑换10元电话费",
            "singleMode": 0,
            "pic": "${http_download}/hall/exch/imgs/phone_10.png",
            "units": {
                "typeId": "common.count",
                "displayName": "张"
            },
            "removeFromBagWhenRemainingZero": 1,
            "removeFromBagWhenExpires": 0,
            "actions": [
                {
                    "name": "exchange",
                    "displayName": "兑换",
                    "typeId": "common.exchange",
                    "params": {
                        "type": "phoneNumber",
                        "desc": "兑换描述",
                        "confirm": 1
                    },
                    "auditParams":{
                        "type":0,
                        "count":10,
                        "desc":"10元电话费"
                    },
                    "message": "您的兑换申请已成功发送，请耐心等待，审核通过后将为您兑换。"
                }
            ]
        },
        {
            "kindId": 4142,
            "typeId": "common.exchange",
            "displayName": "30元电话卡",
            "visibleInBag": 1,
            "desc": "可兑换30元电话费",
            "singleMode": 0,
            "pic": "${http_download}/hall/exch/imgs/phone_30.png",
            "units": {
                "typeId": "common.count",
                "displayName": "张"
            },
            "removeFromBagWhenRemainingZero": 1,
            "removeFromBagWhenExpires": 0,
            "actions": [
                {
                    "name": "exchange",
                    "displayName": "兑换",
                    "typeId": "common.exchange",
                    "params": {
                        "type": "phoneNumber",
                        "desc": "兑换描述",
                        "confirm": 1
                    },
                    "auditParams":{
                        "type":0,
                        "count":30,
                        "desc":"30元电话费"
                    },
                    "message": "您的兑换申请已成功发送，请耐心等待，审核通过后将为您兑换。"
                }
            ]
        },
        {
            "kindId": 4143,
            "typeId": "common.exchange",
            "displayName": "50元电话卡",
            "visibleInBag": 1,
            "desc": "可兑换50元电话费",
            "singleMode": 0,
            "pic": "${http_download}/hall/exch/imgs/phone_50.png",
            "units": {
                "typeId": "common.count",
                "displayName": "张"
            },
            "removeFromBagWhenRemainingZero": 1,
            "removeFromBagWhenExpires": 0,
            "actions": [
                {
                    "name": "exchange",
                    "displayName": "兑换",
                    "typeId": "common.exchange",
                    "params": {
                        "type": "phoneNumber",
                        "desc": "兑换描述",
                        "confirm": 1
                    },
                    "auditParams":{
                        "type":0,
                        "count":50,
                        "desc":"50元电话费"
                    },
                    "message": "您的兑换申请已成功发送，请耐心等待，审核通过后将为您兑换。"
                }
            ]
        },
        {
            "kindId": 4144,
            "typeId": "common.exchange",
            "displayName": "100元电话卡",
            "visibleInBag": 1,
            "desc": "可兑换100元电话费",
            "singleMode": 0,
            "pic": "${http_download}/hall/exch/imgs/phone_100.png",
            "units": {
                "typeId": "common.count",
                "displayName": "张"
            },
            "removeFromBagWhenRemainingZero": 1,
            "removeFromBagWhenExpires": 0,
            "actions": [
                {
                    "name": "exchange",
                    "displayName": "兑换",
                    "typeId": "common.exchange",
                    "params": {
                        "type": "phoneNumber",
                        "desc": "兑换描述",
                        "confirm": 1
                    },
                    "auditParams":{
                        "type":0,
                        "count":100,
                        "desc":"100元电话费"
                    },
                    "message": "您的兑换申请已成功发送，请耐心等待，审核通过后将为您兑换。"
                }
            ]
        }
    ],
    "user.init.items": [
        {
            "itemKindId": 1001,
            "count": 1
        },
        {
            "itemKindId": 1008,
            "count": 5
        },
        {
            "itemKindId": 1007,
            "count": 20
        },
        {
            "itemKindId": 2002,
            "count": 50
        }
    ],
    "user.init.items.new": [
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
        },
        {
            "itemKindId": 2002,
            "count": 50
        }
    ],
    "exchangeGdssUrl": "http://gdss.touch4.me/?act=api.propExchange"
}

class TestBenefits(unittest.TestCase):
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
        self.testContext.configure.setJson('game:9999:benefits', benefits_conf, 0)
        hallitem._initialize()
        hallvip._initialize()
        hallbenefits._initialize()
        
    def tearDown(self):
        self.testContext.stopMock()
        
    def testLoad(self):
        timestamp = pktimestamp.getCurrentTimestamp()
        hallitem.itemSystem.loadUserAssets(self.userId).addAsset(self.gameId, hallitem.ASSET_ITEM_MEMBER_KIND_ID, 1, timestamp, 0, 0)
        userBenefits = hallbenefits.benefitsSystem.loadUserBenefits(self.gameId, self.userId, timestamp)
        print userBenefits.__dict__
        
if __name__ == '__main__':
    unittest.main()
