# -*- coding=utf-8
'''
Created on 2017年4月25日

@author: wangyonghui
'''
import freetime.util.log as ftlog

from dizhu.entity.dizhutodotask import TodoTaskLuckyBox, TodoTaskWinStreakBuffGift, TodoTaskStopWinStreakBuffGift, \
    TodoTaskLoseStreakBuffGift
from hall.entity import hallstore
from hall.entity.hallpopwnd import TodoTaskTemplate, TodoTaskTemplateRegister, findTodotaskTemplate
from poker.entity.biz.exceptions import TYBizConfException
from dizhu.entity.dizhuconf import DIZHU_GAMEID


class DizhuTodoTaskLuckyBoxTemplate(TodoTaskTemplate):
    TYPE_ID = 'todotask.template.dizhuLuckyBox'
    def __init__(self):
        super(DizhuTodoTaskLuckyBoxTemplate, self).__init__()
        self.payOrder = None

    def _decodeFromDictImpl(self, d):
        self.payOrder = d.get('payOrder')
        if not isinstance(self.payOrder, dict):
            raise TYBizConfException(d, 'DizhuTodoTaskLuckyBoxTemplate.payOrder must be dict')

    def _newTodoTask(self, gameId, userId, clientId, timestamp, **kwargs):
        product, _ = hallstore.findProductByPayOrder(gameId, userId, clientId, self.payOrder)
        if product:
            from hall.entity.hallstore import storeSystem
            canBuy = storeSystem.canBuyProduct(DIZHU_GAMEID, userId, clientId, product, 1)
            if not canBuy:
                if ftlog.is_debug():
                    ftlog.debug('DizhuTodoTaskLuckyBoxTemplate._newTodoTask not canBuy')
                return
            return TodoTaskLuckyBox(product)
        return None


class DizhuTodoTaskWinStreakBuffGift(TodoTaskTemplate):
    # 连胜buff礼包
    TYPE_ID = 'todotask.template.dizhuWinStreakBuffGift'
    def __init__(self):
        super(DizhuTodoTaskWinStreakBuffGift, self).__init__()
        self.payOrder = None

    def _decodeFromDictImpl(self, d):
        self.payOrder = d.get('payOrder')
        if not isinstance(self.payOrder, dict):
            raise TYBizConfException(d, 'DizhuTodoTaskWinStreakBuffGift.payOrder must be dict')

    def _newTodoTask(self, gameId, userId, clientId, timestamp, **kwargs):
        product, _ = hallstore.findProductByPayOrder(gameId, userId, clientId, self.payOrder)
        return TodoTaskWinStreakBuffGift(product) if product else None


class DizhuTodoTaskStopWinStreakGift(TodoTaskTemplate):
    # 终止连胜buff礼包
    TYPE_ID = 'todotask.template.dizhuStopWinStreakGift'
    def __init__(self):
        super(DizhuTodoTaskStopWinStreakGift, self).__init__()
        self.payOrder = None

    def _decodeFromDictImpl(self, d):
        self.payOrder = d.get('payOrder')
        if not isinstance(self.payOrder, dict):
            raise TYBizConfException(d, 'DizhuTodoTaskStopWinStreakGift.payOrder must be dict')

    def _newTodoTask(self, gameId, userId, clientId, timestamp, **kwargs):
        product, _ = hallstore.findProductByPayOrder(gameId, userId, clientId, self.payOrder)
        return TodoTaskStopWinStreakBuffGift(product) if product else None


class DizhuTodoTaskLoseStreakBuffGift(TodoTaskTemplate):
    # 连败buff礼包
    TYPE_ID = 'todotask.template.dizhuLoseStreakBuffGift'
    def __init__(self):
        super(DizhuTodoTaskLoseStreakBuffGift, self).__init__()
        self.payOrder = None

    def _decodeFromDictImpl(self, d):
        self.payOrder = d.get('payOrder')
        if not isinstance(self.payOrder, dict):
            raise TYBizConfException(d, 'DizhuTodoTaskLoseStreakBuffGift.payOrder must be dict')

    def _newTodoTask(self, gameId, userId, clientId, timestamp, **kwargs):
        product, _ = hallstore.findProductByPayOrder(gameId, userId, clientId, self.payOrder)
        return TodoTaskLoseStreakBuffGift(product) if product else None


def _registerClasses():
    ftlog.info('dizhupopwnd._registerClasses')
    TodoTaskTemplateRegister.registerClass(DizhuTodoTaskLuckyBoxTemplate.TYPE_ID, DizhuTodoTaskLuckyBoxTemplate)
    TodoTaskTemplateRegister.registerClass(DizhuTodoTaskWinStreakBuffGift.TYPE_ID, DizhuTodoTaskWinStreakBuffGift)
    TodoTaskTemplateRegister.registerClass(DizhuTodoTaskStopWinStreakGift.TYPE_ID, DizhuTodoTaskStopWinStreakGift)
    TodoTaskTemplateRegister.registerClass(DizhuTodoTaskLoseStreakBuffGift.TYPE_ID, DizhuTodoTaskLoseStreakBuffGift)


def generateDizhuLuckyBoxTodoTask(userId, clientId):
    template, templateName = findTodotaskTemplate(DIZHU_GAMEID, userId, clientId, 'dizhuLuckyBox')
    if ftlog.is_debug():
        ftlog.debug('dizhupopwnd.generateDizhuLuckyBoxTodoTask template=', template, 'templateName=', templateName)
    if not template:
        if ftlog.is_debug():
            ftlog.debug('dizhupopwnd.generateDizhuLuckyBoxTodoTask not have todoTaskTemplate')
        return
    task = template.newTodoTask(DIZHU_GAMEID, userId, clientId)
    if not task:
        if ftlog.is_debug():
            ftlog.debug('dizhupopwnd.generateDizhuLuckyBoxTodoTask not have task')
        return
    return task


def generateDizhuWinStreakBuffGift(userId, clientId):
    template, templateName = findTodotaskTemplate(DIZHU_GAMEID, userId, clientId, 'dizhuWinStreakBuffGift')
    if ftlog.is_debug():
        ftlog.debug('dizhupopwnd.generateDizhuWinStreakBuffGift template=', template,
                    'templateName=', templateName)
    if not template:
        return None

    task = template.newTodoTask(DIZHU_GAMEID, userId, clientId)
    if ftlog.is_debug():
        ftlog.debug('dizhupopwnd.generateDizhuWinStreakBuffGift task=', task.toDict() if task else None)

    return task if task else None


def generateDizhuStopWinStreakGift(userId, clientId):
    template, templateName = findTodotaskTemplate(DIZHU_GAMEID, userId, clientId, 'dizhuStopWinStreakGift')
    if ftlog.is_debug():
        ftlog.debug('dizhupopwnd.generateDizhuStopWinStreakGift template=', template,
                    'templateName=', templateName)
    if not template:
        return

    task = template.newTodoTask(DIZHU_GAMEID, userId, clientId)
    if ftlog.is_debug():
        ftlog.debug('dizhupopwnd.generateDizhuStopWinStreakGift task=', task.toDict() if task else None)

    return task if task else None


def generateDizhuLoseStreakBuffGift(userId, clientId):
    template, templateName = findTodotaskTemplate(DIZHU_GAMEID, userId, clientId, 'dizhuLoseStreakBuffGift')
    if ftlog.is_debug():
        ftlog.debug('dizhupopwnd.generateDizhuLoseStreakBuffGift template=', template,
                    'templateName=', templateName)
    if not template:
        return

    task = template.newTodoTask(DIZHU_GAMEID, userId, clientId)
    if ftlog.is_debug():
        ftlog.debug('dizhupopwnd.generateDizhuLoseStreakBuffGift task=', task.toDict() if task else None)

    return task if task else None
