# -*- coding=utf-8
'''
Created on 2015年8月5日

@author: zhaojiangang
'''
import freetime.util.log as ftlog
from hall.entity import hallstore
from hall.entity.todotask import TodoTaskPayOrder, TodoTaskActivity, \
    TodoTaskVisitHtml, TodoTaskShowInfo, TodoTask
from poker.entity.configure import configure as pkconfigure, pokerconf


def makeBeforeActivityTodoTasks(gameId, userId, clientId):
    try:
        intClientId = pokerconf.clientIdToNumber(clientId)
        enable = pkconfigure.getGameJson(gameId, 'pop.activity', {}, intClientId).get('enable', 0)
        if not enable:
            return None
        msg = pkconfigure.getGameJson(gameId, 'pop.activity', {}, pkconfigure.DEFAULT_CLIENT_ID)
        if msg:
            return TodoTaskShowInfo(msg)
    except:
        ftlog.exception()
    return None

def makeTodoTaskPopActivity(gameId, userId, clientId, conf):
    product = None
    productId = conf.get('productId', None)
    if not productId:
        product = hallstore.findProductFromShelves(gameId, userId, clientId, 'raffle')
    else:
        product = hallstore.storeSystem.findProduct(productId)
    if not product:
        return None
    
    directBuy = conf.get('directBuy', False)
    mpic = conf.get('mpic', None)
    url = conf.get('url', '')
    lpic = conf.get('lpic', '')
    rpic = conf.get('rpic', '')
    
    payOrder = TodoTaskPayOrder(product)
    if directBuy:
        return TodoTaskPayOrder(product)
    
    activity_ = TodoTaskActivity()
    if mpic:
        activity_.setMiddle(mpic, payOrder)
    else:
        activity_.setRight(rpic, payOrder)
        activity_.setLeft(lpic, TodoTaskVisitHtml(url))

    return activity_


# 添加参赛券不够，报名失败弹窗
class TodoTaskQuickSigninTip(TodoTask):
    def __init__(self, title, message):
        super(TodoTaskQuickSigninTip, self).__init__('ddz_pop_quicksignin_tip')
        self.setParam('title', title)
        self.setParam('message', message)

class TodoTaskQuickSignin(TodoTask):
    def __init__(self, roomId, isTip):
        super(TodoTaskQuickSignin, self).__init__('ddz_quicksignin')
        self.setParam('roomId', roomId)
        self.setParam('isTip', isTip)

def makeQuickSigninShow(title, message, roomId, isTip):
    todoTaskQuickSignin = TodoTaskQuickSigninTip(title, message)
    todoTaskQuickSignin.setSubCmd(TodoTaskQuickSignin(roomId, isTip))
    return todoTaskQuickSignin


# 房间幸运宝箱
class TodoTaskLuckyBox(TodoTask):
    def __init__(self, payOrderProduct):
        super(TodoTaskLuckyBox, self).__init__('ddz_pop_lucky_box')
        clientParams = payOrderProduct.clientParams
        if clientParams:
            self.setParam('originalPrice', str(clientParams.get('originalPrice', '')))
            self.setParam('descExtra', clientParams.get('descExtra', ''))
        if payOrderProduct:
            self.setParam('price', payOrderProduct.price)
            self.setParam('desc', payOrderProduct.desc)
            self.setSubCmd(TodoTaskPayOrder(payOrderProduct))

# 连胜礼包
class TodoTaskWinStreakBuffGift(TodoTask):
    def __init__(self, payOrderProduct):
        super(TodoTaskWinStreakBuffGift, self).__init__('ddz_pop_libao_gaoshou')
        clientParams = payOrderProduct.clientParams
        if clientParams:
            self.setParam('originalPrice', str(clientParams.get('originalPrice', '')))
            self.setParam('descExtra', clientParams.get('descExtra', ''))
        if payOrderProduct:
            self.setParam('price', payOrderProduct.price)
            self.setParam('desc', payOrderProduct.desc)
            self.setSubCmd(TodoTaskPayOrder(payOrderProduct))

# 连败礼包
class TodoTaskLoseStreakBuffGift(TodoTask):
    def __init__(self, payOrderProduct):
        super(TodoTaskLoseStreakBuffGift, self).__init__('ddz_pop_libao_zhuanyun')
        clientParams = payOrderProduct.clientParams
        if clientParams:
            self.setParam('originalPrice', str(clientParams.get('originalPrice', '')))
            self.setParam('descExtra', clientParams.get('descExtra', ''))
        if payOrderProduct:
            self.setParam('price', payOrderProduct.price)
            self.setParam('desc', payOrderProduct.desc)
            self.setSubCmd(TodoTaskPayOrder(payOrderProduct))

# 连胜中断礼包
class TodoTaskStopWinStreakBuffGift(TodoTask):
    def __init__(self, payOrderProduct):
        super(TodoTaskStopWinStreakBuffGift, self).__init__('ddz_pop_libao_lianshengzhongduan')
        clientParams = payOrderProduct.clientParams
        if clientParams:
            self.setParam('originalPrice', str(clientParams.get('originalPrice', '')))
            self.setParam('descExtra', clientParams.get('descExtra', ''))
        if payOrderProduct:
            self.setParam('price', payOrderProduct.price)
            self.setParam('desc', payOrderProduct.desc)
            self.setSubCmd(TodoTaskPayOrder(payOrderProduct))