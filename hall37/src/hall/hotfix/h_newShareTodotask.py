# -*- coding:utf-8 -*-
'''
Created on 2017年11月27日

@author: zhaojiangang
'''
from hall.entity.todotask import TodoTaskNewShareRulePopFactory
from poker.entity.biz.exceptions import TYBizConfException


def decodeFromDict(self, d):
    self.sharePointId = d.get('sharePointId')
    if not isinstance(self.sharePointId, int):
        raise TYBizConfException(d, 'TodoTaskNewShareRulePopFactory.sharePointId must be int')
    self.urlParams = d.get('urlParams', {})
    if not isinstance(self.urlParams, dict):
        raise TYBizConfException(d, 'TodoTaskNewShareRulePopFactory.urlParams must be dict')
    return self

TodoTaskNewShareRulePopFactory.decodeFromDict = decodeFromDict


