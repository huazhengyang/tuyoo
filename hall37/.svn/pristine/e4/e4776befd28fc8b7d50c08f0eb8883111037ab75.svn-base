# -*- coding=utf-8 -*-
"""
@file  : message_test
@date  : 2016-07-12
@author: GongXiaobo
"""
import json
import time

import testgdss

_apikey = 'www.tuyoo.com-api-6dfa879490a249be9fbc92e97e4d898d-www.tuyoo.com'


def test_text(url, userid, text):
    # 纯文本
    pdatas = {
        'userId': userid,
        'gameId': 9999,
        'text': text,
    }
    testgdss.sendout(url + '/_gdss/user/message/send', _apikey, pdatas)


def test_assets(url, userid, text, assets, event_param):
    # 发物品
    pdatas = {
        'userId': userid,
        'gameId': 9999,
        'text': text,
        'assets': json.dumps(assets, separators=(',', ':')),
        'intEventParam': event_param,
    }
    testgdss.sendout(url + '/_gdss/user/message/sendasset', _apikey, pdatas)


def test_todotask(url, gameid, clientid, userid, text, duration, todotask, todotask_kwarg):
    # 发跳转
    pdatas = {
        'clientId': clientid,
        'userId': userid,
        'gameId': gameid,
        'text': text,
        'duration': duration,
        'todotask': json.dumps(todotask, separators=(',', ':')),
        'todotask_kwarg': json.dumps(todotask_kwarg, separators=(',', ':')),
    }
    testgdss.sendout(url + '/_gdss/user/message/sendtodotask', _apikey, pdatas)

if __name__ == '__main__':
    myurl = 'http://111.203.187.162:8040'
    myuid = 10003
    test_text(myurl, myuid, 'there is nothing')
    test_todotask(myurl, 6, "IOS_3.33_tuyoo.appStore.0-hall6.tuyoo.huanle", myuid, 'there is todotask', 1,
                  {'templateName': "iosUpgrade"}, {})
    test_assets(myurl, myuid, 'there is attach',
                [{'itemId': 'item:1001', 'count': 1},
                 {'itemId': 'user:chip', 'count': 100},
                 {'itemId': 'user:coupon', 'count': 150}], 0)

    time.sleep(65)
    test_text(myurl, myuid, 'there is nothing again')
