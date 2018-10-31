# -*- coding: utf-8 -*-
'''
Created on 2016年7月27日

@author: zqh
'''
import json

from _loader._base import assertBase
from _loader._base import mainconf


def assertTodo0001(todo):
    '''
    {
        "actId": "activity_general_btn_qiku_ddz_match_1023",
        "typeId": "hall.goto.activity.byid"
    }
    '''
    assertBase.assertDictMustKeys(todo, ['typeId', 'actId'])
    assertBase.assertMustStr(todo, 'actId')
    # TODO 检查actId指向的活动定义是否存在


def assertTodo0002(todo):
    '''
    {
        "enter_param": {
            "pluginParams": {
                "gameType": 3
            },
            "type": "roomlist"
        },
        "gameId": 6,
        "typeId": "hall.goto.enter.game"
    }
    '''
    assertBase.assertDictMustKeys(todo, ['typeId', 'gameId', 'enter_param'])
    assertBase.assertMustDict(todo, 'enter_param')
    assertBase.assertEnumValue(todo, 'gameId', mainconf.GAMEIDS)
    # TODO 检查enter_param的type应该是一个枚举
    # TODO 检查enter_param的pluginParams


def assertTodo0003(todo):
    '''
    {
        "typeId": "hall.wifikey.promote"
    }
    '''
    assertBase.assertDictMustKeys(todo, ['typeId'])


def assertTodo0004(todo):
    '''
    {
        "typeId": "hall.goto.shop",
        "subStore" : "coin"
    }
    '''
    assertBase.assertDictMustKeys(todo, ['typeId', 'subStore'])
    # TODO subStore的枚举类型暂时不完整
    assertBase.assertEnumValue(todo, 'subStore', ['coin', 'activity'])


def assertTodo0005(todo):
    '''
    {
        "typeId": "hall.download",
        "url": "http://www.tuyoo.com/PrivacyPolicy"
    }
    '''
    assertBase.assertDictMustKeys(todo, ['typeId', 'url'])
    assertBase.assertMustHttp(todo, 'url')


def assertTodo0006(todo):
    '''
    {"payOrder": {
                  "shelves": ["raffle"], 
                  "priceDiamond": {"count": 80, "minCount": 0, "maxCount": -1}, 
                  "buyTypes": ["direct", "consume"]}, 
     "typeId": "todotask.payOrder"}
    '''
    # TODO
    pass

_TODO_CHECKERS_ = {
    'hall.goto.activity.byid': assertTodo0001,
    'hall.goto.enter.game': assertTodo0002,
    'hall.wifikey.promote': assertTodo0003,
    'hall.goto.shop': assertTodo0004,
    'hall.download': assertTodo0005,
    'todotask.payOrder': assertTodo0006,
}


def assertTodoTaskList(todos):
    if todos:
        for todo in todos:
            assertTodoTask(todo)


def assertTodoTask(todo):
    typeId = assertBase.assertMustStr(todo, 'typeId')
    assertfun = _TODO_CHECKERS_.get(typeId, None)
    if not assertfun:
        raise Exception('the todotask typeId ' + str(typeId) + ' is unknow ! in ' + json.dumps(todo))
    assertfun(todo)


def assertTodoTaskRefList(todos):
    if todos:
        for todoId in todos:
            assertTodoTaskRef(todoId)


def assertTodoTaskRef(todoId):
    if not isinstance(todoId, int):
        raise Exception('the todotasks ref id must be integer ! ' + str(todoId) + ' type=' + type(todoId))
