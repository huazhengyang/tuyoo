# -*- coding=utf-8
'''
Created on 2015年10月15日

@author: zhaojiangang
'''
from poker.util import strutil
from hall.entity.todotask import TodoTask, TodoTaskPayOrder, TodoTaskShowInfo
from poker.entity.biz.store.store import TYProduct

class TodoTaskFirstRecharge(TodoTask):
    def __init__(self, title, imgUrl, payOrder=None, confirm=0, confirmDesc=None, subText=None):
        super(TodoTaskFirstRecharge, self).__init__('pop_first_recharge')
        self.setParam('title', title)
        self.setParam('imgUrl', imgUrl)
        if subText:
            self.setParam('subText', subText)
            self.setParam('sub_action_text', subText)
        if payOrder:
            subCmd = payOrder
            if isinstance(payOrder, TYProduct):
                subCmd = TodoTaskPayOrder(payOrder)
            if confirm:
                confirmDesc = confirmDesc or ''
                if confirmDesc:
                    confirmDesc = strutil.replaceParams(confirmDesc, {
                                                            'product.displayName':subCmd.getParam('name', ''),
                                                            'product.price':subCmd.getParam('price', '')
                                                        })
                info = TodoTaskShowInfo(confirmDesc, True)
                info.setSubCmd(subCmd)
                subCmd = info
            self.setSubCmd(subCmd)

from hall.entity import todotask
todotask.TodoTaskFirstRecharge.__init__ = TodoTaskFirstRecharge.__init__