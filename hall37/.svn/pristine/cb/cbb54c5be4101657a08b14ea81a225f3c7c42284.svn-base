# -*- coding=utf-8 -*-
"""
@file  : free_test
@date  : 2016-07-27
@author: GongXiaobo
"""
import sys

import testrpc


def build_query_task(userid, clientid):
    return {
        'userId': userid,
        'clientId': clientid
    }


def build_task_reward(userid, clientid):
    return {
        'userId': userid,
        'taskId': sys.argv[2],
        'clientId': clientid
    }


def build_task_progress(userid, clientid):
    return {
        'userId': userid,
        'taskId': sys.argv[2],
        'progress': sys.argv[3],
        'clientId': clientid
    }

CMD2URL = {
    'taskQuery': ('/gtest/free/queryTask', build_query_task),
    'taskReward': ('/gtest/free/getTaskReward', build_task_reward),
    'taskProgress': ('/gtest/free/setTaskProgress', build_task_progress)
}


def test(httpdomain, userid, clientid):
    print sys.argv
    cmd = sys.argv[1]
    if cmd not in CMD2URL:
        raise Exception('command unkown!!!')
    url = CMD2URL[cmd]
    path = httpdomain + url[0]
    datadict = url[1](userid, clientid)
    print testrpc.dohttpquery(path, datadict)

if __name__ == '__main__':
    domain = 'http://111.203.187.162:8040'
    uid = 10002
    cid = 'Android_3.901_360.360,yisdkpay.0-hall6.360.day'  # 'Android_3.37_tuyoo.weakChinaMobile.0-hall7.apphui.sc'
    test(domain, uid, cid)
