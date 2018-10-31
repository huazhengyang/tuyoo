# -*- coding=utf-8

import freetime.util.log as ftlog
from hall.entity.hallpopwnd import TodoTaskLuckBuyTemplate, TodoTaskWinBuyTemplate
from sre_compile import isstring
from poker.entity.biz.exceptions import TYBizConfException
from poker.util import strutil
from hall.entity.todotask import TodoTaskLuckBuy, TodoTaskWinBuy



def _ldecodeFromDictImpl(self, d):
    super(TodoTaskLuckBuyTemplate, self)._decodeFromDictImpl(d)
    self.tip = d.get('tip', '')
    self.confparams = d
    ftlog.hinfo("TodoTaskLuckBuyTemplate", d)
    if not isstring(self.tip):
        raise TYBizConfException(d, 'TodoTaskLuckBuyTemplate.tip must be string')

def _lnewTodoTaskByProduct(self, gameId, userId, clientId, timestamp, product, **kwargs):
    tip = strutil.replaceParams(self.tip, {'product.desc': product.desc})
    if hasattr(self,'confparams'):
        return TodoTaskLuckBuy(self.desc, tip, product, self.subActionText, self.confparams)
    else:
        return TodoTaskLuckBuy(self.desc, tip, product, self.subActionText)




def _wdecodeFromDictImpl(self, d):
    super(TodoTaskWinBuyTemplate, self)._decodeFromDictImpl(d)
    self.tip = d.get('tip', '')
    self.confparams = d
    ftlog.hinfo("TodoTaskWinBuyTemplate", d)
    if not isstring(self.tip):
        raise TYBizConfException(d, 'TodoTaskWinBuyTemplate.tip must be string')

def _wnewTodoTaskByProduct(self, gameId, userId, clientId, timestamp, product, **kwargs):
    tip = strutil.replaceParams(self.tip, {'product.desc': product.desc})
    if hasattr(self, 'confparams'):
        return TodoTaskWinBuy(self.desc, tip, product, self.subActionText, self.confparams)
    else:
        return TodoTaskWinBuy(self.desc, tip, product, self.subActionText)

from hall.entity import hallpopwnd
hallpopwnd.TodoTaskLuckBuyTemplate._decodeFromDictImpl = _ldecodeFromDictImpl
hallpopwnd.TodoTaskLuckBuyTemplate._newTodoTaskByProduct = _lnewTodoTaskByProduct

hallpopwnd.TodoTaskWinBuyTemplate._decodeFromDictImpl = _wdecodeFromDictImpl
hallpopwnd.TodoTaskWinBuyTemplate._newTodoTaskByProduct = _wnewTodoTaskByProduct
