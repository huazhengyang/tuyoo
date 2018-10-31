# -*- coding=utf-8 -*-
from hall.entity.todotask import TodoTaskShowInfo, TodoTaskGotoShop

# 测试
def toShop():
    result = {}
    ret = TodoTaskShowInfo('您的钻石不足，请去商城购买', True)
    ret.setSubCmd(TodoTaskGotoShop('diamond'))
    result['todotask'] = ret.toDict()
    return result

from hall.entity import hallroulette
hallroulette.toShop = toShop