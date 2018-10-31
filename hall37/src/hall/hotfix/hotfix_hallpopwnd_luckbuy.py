# -*- coding=utf-8


import freetime.util.log as ftlog
from hall.entity.todotask import TodoTask, TodoTaskHelper, TodoTaskPayOrder, TodoTaskLuckBuy ,TodoTaskWinBuy

def __linit__(self, desc, tip, payOrderProduct, payOrderText=None, confparams=None):
    super(TodoTaskLuckBuy, self).__init__('pop_lucky_buy')
    self.setParam('desc', desc)
    self.setParam('tip', tip)

    # hall4.01以上客户端使用的新字段
    productParams = TodoTaskHelper.getParamsByProduct(payOrderProduct)
    self.setParam('price', productParams['price'])
    self.setParam('productDesc', productParams['desc'])

    ftlog.hinfo("TodoTaskLuckBuy|v4.56|confparams", confparams)
    if confparams:
        pickey = 'pic_' + productParams['price']
        if pickey in confparams:
            self.setParam('pic', confparams[pickey])
            self.setParam('action', 'pop_lucky_buy')

            ftlog.hinfo("TodoTaskLuckBuy|v4.56|pic",productParams['price'], confparams[pickey])

    if payOrderProduct:
        self.setSubCmdWithText(TodoTaskPayOrder(payOrderProduct), payOrderText)


def __winit__(self, desc, tip, payOrderProduct, payOrderText=None, confparams=None):
    super(TodoTaskWinBuy, self).__init__('pop_winer_buy')
    self.setParam('desc', desc)
    self.setParam('tip', tip)

    # hall4.01以上客户端使用的新字段
    productParams = TodoTaskHelper.getParamsByProduct(payOrderProduct)
    self.setParam('price', productParams['price'])
    self.setParam('productDesc', productParams['desc'])

    ftlog.hinfo("TodoTaskWinBuy|v4.56|confparams", confparams)
    if confparams:
        pickey = 'pic_' + productParams['price']
        if pickey in confparams:
            self.setParam('pic', confparams[pickey])
            self.setParam('action', 'pop_winer_buy')

            ftlog.hinfo("TodoTaskWinBuy|v4.56|pic", productParams['price'], confparams[pickey])

    if payOrderProduct:
        self.setSubCmdWithText(TodoTaskPayOrder(payOrderProduct), payOrderText)

from hall.entity import todotask
todotask.TodoTaskLuckBuy.__init__ = __linit__
todotask.TodoTaskWinBuy.__init__ = __winit__