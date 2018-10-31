# -*- coding=utf-8
'''
Created on 2015年8月24日

@author: zhaojiangang
'''
from datetime import datetime
from sre_compile import isstring

import freetime.util.log as ftlog
from hall.entity import hallconf, hallstore, hallitem, hallbenefits, \
    hallsubmember
from hall.entity.hallusercond import UserConditionRegister, \
    UserConditionRegisterDay, UserConditionisMyGameid,\
    UserConditionNotInClientIDs
from hall.entity.todotask import TodoTaskRegister, TodoTaskFactory, \
    TodoTaskFirstRecharge, TodoTaskMemberTry, TodoTaskRecommendBuy, \
    TodoTaskActivityNew, TodoTaskMonthCheckinNew, TodoTaskNsloginReward, \
    TodoTaskPayOrderFactory, TodoTaskIosUpgradeFactory, TodoTaskMemberBuy, \
    TodoTaskLessBuyOrder, TodoTaskShowInfo, TodoTaskPayOrder, TodoTaskLuckBuy, \
    TodoTaskWinBuy, TodoTaskHelper, TodoTaskReceiveFirstRechargeReward, \
    TodoTaskOrderShow, TodoTaskDiZhuEvent, TodoTaskDiamondToCoin,\
    TodoTaskBuyTableCoin
from poker.entity.biz.confobj import TYConfableRegister, TYConfable
from poker.entity.biz.exceptions import TYBizConfException
from poker.entity.configure import gdata
from poker.entity.dao import userdata as pkuserdata, userchip
from poker.entity.events.tyevent import EventConfigure
import poker.entity.events.tyeventbus as pkeventbus
from poker.util import strutil
import poker.util.timestamp as pktimestamp

_inited = False
# key=templateName, value=map<todotaskTemplateName, todotaskFactory>
_templateMap = {}

class TodoTaskAction(object):
    def __init__(self):
        self.textName = None
        self.textValue = None
        self.isRequired = None
        self.actionName = None
        self.conditionList = None
        # list<(conditionList, todotaskFactory)
        self.todotaskList = None
        
    def decodeFromDict(self, d):
        self.isRequired = d.get('required', 0)
        if self.isRequired not in (0, 1):
            raise TYBizConfException(d, 'TodoTaskAction.isRequired must be int in (0,1)')
        textD = d.get('text')
        if textD is not None:
            if not isinstance(textD, dict):
                raise TYBizConfException(d, 'TodoTaskAction.text must be dict')
            self.textName = textD.get('name')
            if not isstring(self.textName) or not self.textName:
                raise TYBizConfException(d, 'TodoTaskAction.text.name must be string')
            self.textValue = textD.get('value', '')
            if not isstring(self.textValue):
                raise TYBizConfException(d, 'TodoTaskAction.text.value must be string')
        self.conditionList = UserConditionRegister.decodeList(d.get('conditions', []))
        actionD = d.get('action')
        if not isinstance(actionD, dict):
            raise TYBizConfException(d, 'TodoTaskAction.action must be dict')
        self.actionName = actionD.get('name')
        if not isstring(self.actionName):
            raise TYBizConfException(d, 'TodoTaskAction.actionName must be dict')
        self.todotaskList = actionD.get('list', [])
        return self
    
    def initWhenLoaded(self, todotaskTemplateMap):
        todotasks = self.todotaskList
        self.todotaskList = []
        for todotask in todotasks:
            conditions = UserConditionRegister.decodeList(todotask.get('conditions', []))
            subTodotask = decodeTodotaskFactoryByDict(todotask)
            self.todotaskList.append((conditions, subTodotask))
    
    @classmethod
    def decodeList(cls, l):
        ret = []
        for d in l:
            ret.append(TodoTaskAction().decodeFromDict(d))
        return ret
    
class TodoTaskTemplate(TodoTaskFactory):
    def __init__(self):
        self.conditionList = None
        self.actionList = None
        
    def decodeFromDict(self, d):
        self.conditionList = UserConditionRegister.decodeList(d.get('conditions', []))
        self.actionList = TodoTaskAction.decodeList(d.get('actions', []))
        self._decodeFromDictImpl(d)
        return self
    
    def initWhenLoaded(self, actionMap):
        for action in self.actionList:
            action.initWhenLoaded(actionMap)
        self._initWhenLoadedImpl(actionMap)
        
    @classmethod
    def decodeList(cls, l):
        ret = []
        for d in l:
            action = TodoTaskAction().decodeFromDict(d)
            ret.append(action)
        return ret

    def newTodoTask(self, gameId, userId, clientId, **kwargs):
        timestamp = pktimestamp.getCurrentTimestamp()
        if self.conditionList:
            ok, cond = self._checkConditions(gameId, userId, clientId, timestamp, self.conditionList, **kwargs)
            if ftlog.is_debug():
                ftlog.debug('TodoTaskTemplate.newTodoTask gameId=', gameId,
                            'userId=', userId,
                            'clientId=', clientId,
                            'condition=', cond,
                            'checkCondition=', ok)
            if not ok:
                return None
        todotask = self._newTodoTask(gameId, userId, clientId, timestamp, **kwargs)
        if not self._setSubActions(gameId, userId, clientId, timestamp, todotask, **kwargs):
            return None
        return todotask
    
    def _newTodoTask(self, gameId, userId, clientId, timestamp, **kwargs):
        raise NotImplemented()
    
    def _decodeFromDictImpl(self, d):
        pass
    
    def _initWhenLoadedImpl(self, actionMap):
        pass
    
    def _setSubActions(self, gameId, userId, clientId, timestamp, todotask, **kwargs):
        '''
        '''
        for action in self.actionList:
            ok, cond = self._checkConditions(gameId, userId, clientId, timestamp, action.conditionList)
            if not ok and action.isRequired:
                if ftlog.is_debug():
                    ftlog.debug('TodoTaskTemplate._setSubActions gameId=', gameId,
                                'userId=', userId,
                                'clientId=', clientId,
                                'actionName=', action.actionName,
                                'condition=', cond)
                return False
            subTodoTask = None
            for conditions, todotaskFactory in action.todotaskList:
                ok, cond = self._checkConditions(gameId, userId, clientId, timestamp, conditions)
                if ok:
                    subTodoTask = todotaskFactory.newTodoTask(gameId, userId, clientId, **kwargs)
                    break
            if subTodoTask:
                todotask.setParam(action.actionName, subTodoTask)
                if action.textName:
                    todotask.setParam(action.textName, action.textValue)
            elif action.isRequired:
                ftlog.debug('TodoTaskTemplate._setSubActions gameId=', gameId,
                           'userId=', userId,
                           'clientId=', clientId,
                           'actionName=', action.actionName)
                return False
        return True
    
    def _checkConditions(self, gameId, userId, clientId, timestamp, conditions):
        for cond in conditions:
            if not cond.check(gameId, userId, clientId, timestamp):
                return False, cond
        return True, None
    
class TodoTaskIosUpgradeTemplate(TodoTaskTemplate):
    TYPE_ID = 'todotask.template.iosUpgrade'
    def __init__(self):
        super(TodoTaskIosUpgradeTemplate, self).__init__()
        self.iosUpgradeFactory = TodoTaskIosUpgradeFactory()
        
    def _decodeFromDictImpl(self, d):
        self.iosUpgradeFactory.decodeFromDict(d)
    
    def _newTodoTask(self, gameId, userId, clientId, timestamp, **kwargs):
        return self.iosUpgradeFactory.newTodoTask(gameId, userId, clientId)
    
class TodoTaskPayOrderTemplate(TodoTaskTemplate):
    TYPE_ID = 'todotask.template.payOrder'
    def __init__(self):
        super(TodoTaskPayOrderTemplate, self).__init__()
        self.payOrderFactory = TodoTaskPayOrderFactory()
        
    def _decodeFromDictImpl(self, d):
        self.payOrderFactory.payOrder = d.get('payOrder')
        if not isinstance(self.payOrderFactory.payOrder, dict):
            raise TYBizConfException(d, 'TodoTaskPayOrderTemplate.payOrder must be dict')
    
    def _newTodoTask(self, gameId, userId, clientId, timestamp, **kwargs):
        return self.payOrderFactory.newTodoTask(gameId, userId, clientId)
    
class TodoTaskFirstRechargeTryTemplate(TodoTaskTemplate):
    TYPE_ID = 'todotask.template.firstRechargeTry'
    def __init__(self):
        super(TodoTaskFirstRechargeTryTemplate, self).__init__()
        self.title = None
        self.imgUrl = None
        self.payOrder = None
        self.confirm = None
        self.confirmDesc = None
        self.subActionText = None
        
    def _decodeFromDictImpl(self, d):
        self.title = d.get('title', '')
        if not isstring(self.title):
            raise TYBizConfException(d, 'TodoTaskFirstRechargeTryTemplate.title must be string')
        self.imgUrl = d.get('imgUrl', '')
        if not isstring(self.imgUrl):
            raise TYBizConfException(d, 'TodoTaskFirstRechargeTryTemplate.imgUrl must be string')
        self.confirm = d.get('confirm')
        if self.confirm not in (0, 1):
            raise TYBizConfException(d, 'TodoTaskFirstRechargeTryTemplate.confirm must be int in (0,1)')
        self.confirmDesc = d.get('confirmDesc', '')
        if not isstring(self.confirmDesc):
            raise TYBizConfException(d, 'TodoTaskFirstRechargeTryTemplate.confirmDesc must be string')
        self.subText = d.get('subActionText', '')
        if not isstring(self.subText):
            raise TYBizConfException(d, 'TodoTaskFirstRechargeTryTemplate.subActionText must be string')
        self.payOrder = d.get('payOrder')
        if not isinstance(self.payOrder, dict):
            raise TYBizConfException(d, 'TodoTaskFirstRechargeTryTemplate.payOrder must be dict')
        return self
    
    def _newTodoTask(self, gameId, userId, clientId, timestamp, **kwargs):
        if not hallstore.isFirstRecharged(userId):
            product, _ = hallstore.findProductByPayOrder(gameId, userId, clientId, self.payOrder)
            if product:
                payOrder = TodoTaskHelper.makeTodoTaskPayOrder(userId, clientId, product)
                return TodoTaskFirstRecharge(self.title, self.imgUrl, payOrder, self.confirm, self.confirmDesc, self.subText)
        elif not hallstore.isGetFirstRechargeReward(userId):
            todotask = TodoTaskFirstRecharge(self.title, self.imgUrl)
            todotask.setSubCmd(TodoTaskReceiveFirstRechargeReward())
            return todotask
        return None
    
class TodoTaskMemberBuyTemplate(TodoTaskTemplate):
    TYPE_ID = 'todotask.template.memberBuy'
    def __init__(self):
        super(TodoTaskMemberBuyTemplate, self).__init__()
        self.desc = None
        self.pic = None
        self.pic4 = None  # 匹配hall4.01以上客户端, 老字段保留
        
    def _decodeFromDictImpl(self, d):
        self.desc = d.get('desc', '')
        if not isstring(self.desc):
            raise TYBizConfException(d, 'TodoTaskMemberBuyTemplate.desc must be string')
        self.pic = d.get('pic', '')
        if not isstring(self.pic):
            raise TYBizConfException(d, 'TodoTaskMemberBuyTemplate.pic must be string')
        self.pic4 = d.get('pic4', '')
        if not isstring(self.pic4):
            raise TYBizConfException(d, 'TodoTaskMemberBuyTemplate.pic4 must be string')
    
    def _newTodoTask(self, gameId, userId, clientId, timestamp, **kwargs):
        return TodoTaskMemberBuy(self.desc, self.pic, self.pic4)
    
class TodoTaskMemberBuy2Template(TodoTaskTemplate):
    TYPE_ID = 'todotask.template.memberBuy2'
    def __init__(self):
        super(TodoTaskMemberBuy2Template, self).__init__()
        self.desc = None
        self.descForMember = None
        self.pic = None
        self.pic4 = None  # 匹配hall4.01以上客户端, 老字段保留
        self.tipForMember = None
        self.tipForSubMember = None
        self.subActionText = None
        self.subActionTextForMember = None
        self.payOrder = None
#         "des":"",//顶部描述,[支持富文本][允许不传]
#         "picUrl":"",//图片 url [允许为空]
#         "sub_action_text":"",//确定按钮文案,[允许不传],[默认"获取特权"]
#         "sub_action":{},//确定按钮行为,[允许不传][传空时不显示按钮] 修改了!!!
#         "sub_action_ext":{},//关闭按钮行为,[允许不传]
#         "tip_bottom":"",//底部描述,[支持富文本][允许不传] 新增!!!
#         "tip_bottom_left":""//左下角描述,[支持富文本][允许不传] 新增!!!

    def _decodeFromDictImpl(self, d):
        self.desc = d.get('desc', '')
        if not isstring(self.desc):
            raise TYBizConfException(d, 'TodoTaskMemberBuyTemplate.desc must be string')
        self.descForMember = d.get('descForMember', '')
        if not isstring(self.descForMember):
            raise TYBizConfException(d, 'TodoTaskMemberBuyTemplate.descForMember must be string')
        self.pic = d.get('pic', '')
        if not isstring(self.pic):
            raise TYBizConfException(d, 'TodoTaskMemberBuyTemplate.pic must be string')
        self.pic4 = d.get('pic4', '')
        if not isstring(self.pic4):
            raise TYBizConfException(d, 'TodoTaskMemberBuyTemplate.pic4 must be string')

        self.tipForMember = d.get('tipForMember', '')
        if not isstring(self.tipForMember):
            raise TYBizConfException(d, 'TodoTaskMemberBuyTemplate.tipForMember must be string')
        self.tipForSubMember = d.get('tipForSubMember', '')
        if not isstring(self.tipForSubMember):
            raise TYBizConfException(d, 'TodoTaskMemberBuyTemplate.tipForSubMember must be string')
        
        self.subActionText = d.get('subActionText', '')
        if not isstring(self.subActionText):
            raise TYBizConfException(d, 'TodoTaskMemberBuyTemplate.subActionText must be string')
        self.subActionTextForMember = d.get('subActionTextForMember', '')
        if not isstring(self.subActionTextForMember):
            raise TYBizConfException(d, 'TodoTaskMemberBuyTemplate.subActionTextForMember must be string')
        
        self.payOrder = d.get('payOrder')
        if not isinstance(self.payOrder, dict):
            raise TYBizConfException(d, 'TodoTaskMemberBuyTemplate.payOrder must be dict')
        
        self.closeAction = d.get('closeAction')
        if self.closeAction and not isinstance(self.closeAction, dict):
            raise TYBizConfException(d, 'TodoTaskMemberBuyTemplate.payOrder must be dict')
        
    def _newTodoTask(self, gameId, userId, clientId, timestamp, **kwargs):
        subMemberStatus = kwargs.get('subMemberStatus') or hallsubmember.loadSubMemberStatus(userId)
        if subMemberStatus.isSub:
            todotask = TodoTaskMemberBuy(self.descForMember, self.pic, self.pic4)
            todotask.setParam('tip_bottom', self.tipForSubMember)
            return todotask
        
        memberInfo = kwargs.get('memberInfo') or hallitem.getMemberInfo(userId, timestamp)
        remainDays = memberInfo[0]
        todotask = None
        subActionText = None
        
        product, _ = hallstore.findProductByPayOrder(gameId, userId, clientId, self.payOrder)
        
        if not product:
            return None
        
        isSubMember = False
        if remainDays > 0:
            tipForMember = strutil.replaceParams(self.tipForMember, {'remainDays':str(remainDays)})
            subMemberStatus = hallsubmember.loadSubMemberStatus(userId)
            isSubMember = subMemberStatus.isSub
            todotask = TodoTaskMemberBuy(self.descForMember, self.pic, self.pic4)
            if not isSubMember and remainDays <= 2:
                todotask.setParam('sub_action_text', self.subActionTextForMember)
            else:
                todotask.setParam('tip_bottom_left', tipForMember)
        else:
            price = product.price
            priceUnits = '元'
            if product.buyType == 'consume':
                price = product.priceDiamond
                priceUnits = '钻石'
            params = {'product.price':str(price), 'product.priceUnits':priceUnits}
            if product.content and product.content.desc:
                params['product.content.desc'] = product.content.desc
            desc = strutil.replaceParams(self.desc, params)
            todotask = TodoTaskMemberBuy(desc, self.pic, self.pic4)
            todotask.setSubText(self.subActionText)
            todotask.setParam('sub_action_text', self.subActionText)
        
        if not isSubMember and remainDays <= 2:
            todotask.setSubCmdWithText(TodoTaskPayOrder(product), subActionText)
        
        if remainDays <= 0 and not isSubMember and self.closeAction:
            closeAction = decodeTodotaskFactoryByDict(self.closeAction).newTodoTask(gameId, userId, clientId, **kwargs)
            if closeAction:
                todotask.setParam('sub_action_close', closeAction)
        return todotask
    
class TodoTaskMonthlyBuyTemplate(TodoTaskTemplate):
    TYPE_ID = 'todotask.template.monthlyBuy'
    def __init__(self):
        super(TodoTaskMonthlyBuyTemplate, self).__init__()
        self.desc = None
        self.descForMember = None
        self.pic = None
        self.pic4 = None  # 匹配hall4.01以上客户端, 老字段保留
        self.tipForMember = None
        self.subActionText = None
        self.subActionTextForMember = None
        self.payOrder = None
#         "des":"",//顶部描述,[支持富文本][允许不传]
#         "picUrl":"",//图片 url [允许为空]
#         "sub_action_text":"",//确定按钮文案,[允许不传],[默认"获取特权"]
#         "sub_action":{},//确定按钮行为,[允许不传][传空时不显示按钮] 修改了!!!
#         "sub_action_ext":{},//关闭按钮行为,[允许不传]
#         "tip_bottom":"",//底部描述,[支持富文本][允许不传] 新增!!!
#         "tip_bottom_left":""//左下角描述,[支持富文本][允许不传] 新增!!!

    def _decodeFromDictImpl(self, d):
        self.desc = d.get('desc', '')
        if not isstring(self.desc):
            raise TYBizConfException(d, 'TodoTaskMemberBuyTemplate.desc must be string')
        self.descForMember = d.get('descForMember', '')
        if not isstring(self.descForMember):
            raise TYBizConfException(d, 'TodoTaskMemberBuyTemplate.descForMember must be string')
        self.pic = d.get('pic', '')
        if not isstring(self.pic):
            raise TYBizConfException(d, 'TodoTaskMemberBuyTemplate.pic must be string')
        self.pic4 = d.get('pic4', '')
        if not isstring(self.pic4):
            raise TYBizConfException(d, 'TodoTaskMemberBuyTemplate.pic4 must be string')
    
        self.tipForMember = d.get('tipForMember', '')
        if not isstring(self.tipForMember):
            raise TYBizConfException(d, 'TodoTaskMemberBuyTemplate.tipForMember must be string')
        self.tipForSubMember = d.get('tipForSubMember', '')
        if not isstring(self.tipForSubMember):
            raise TYBizConfException(d, 'TodoTaskMemberBuyTemplate.tipForSubMember must be string')
        
        self.subActionText = d.get('subActionText', '')
        if not isstring(self.subActionText):
            raise TYBizConfException(d, 'TodoTaskMemberBuyTemplate.subActionText must be string')
        
        self.payOrder = d.get('payOrder')
        if not isinstance(self.payOrder, dict):
            raise TYBizConfException(d, 'TodoTaskMemberBuyTemplate.payOrder must be dict')
        
    def _newTodoTask(self, gameId, userId, clientId, timestamp, **kwargs):
        
        remainDays = kwargs.get('monthlyInfo') or hallitem.getTexasMouthlyCardInfo(userId, timestamp)
        todotask = None
        subActionText = None
        
        product, _ = hallstore.findProductByPayOrder(gameId, userId, clientId, self.payOrder)
        
        if not product:
            return None
        
        if remainDays > 0:
            tipForMember = strutil.replaceParams(self.tipForMember, {'remainDays':str(remainDays)})
            todotask = TodoTaskMemberBuy(self.descForMember, self.pic, self.pic4)
            todotask.setParam('tip_bottom_left', tipForMember)
        else:
            price = product.price
            priceUnits = '元'
            if product.buyType == 'consume':
                price = product.priceDiamond
                priceUnits = '钻石'
            params = {'product.price':str(price), 'product.priceUnits':priceUnits}
            if product.content and product.content.desc:
                params['product.content.desc'] = product.content.desc
            desc = strutil.replaceParams(self.desc, params)
            todotask = TodoTaskMemberBuy(desc, self.pic, self.pic4)
            todotask.setSubText(self.subActionText)
            todotask.setParam('sub_action_text', self.subActionText)

        todotask.setSubCmdWithText(TodoTaskPayOrder(product), subActionText)
            
        return todotask
    
class TodoTaskMemberTryTemplate(TodoTaskTemplate):
    TYPE_ID = 'todotask.template.memberTry'
    def __init__(self):
        super(TodoTaskMemberTryTemplate, self).__init__()
        self.desc = None
        self.pic = None
        self.pic4 = None  # 匹配hall4.01以上客户端, 老字段保留
        
    def _decodeFromDictImpl(self, d):
        self.desc = d.get('desc', '')
        if not isstring(self.desc):
            raise TYBizConfException(d, 'TodoTaskMemberTryTemplate.desc must be string')
        self.pic = d.get('pic', '')
        if not isstring(self.pic):
            raise TYBizConfException(d, 'TodoTaskMemberTryTemplate.pic must be string')
        self.pic4 = d.get('pic4', '')
        if not isstring(self.pic4):
            raise TYBizConfException(d, 'TodoTaskMemberTryTemplate.pic4 must be string')
        
    def _newTodoTask(self, gameId, userId, clientId, timestamp, **kwargs):
        return TodoTaskMemberTry(self.desc, self.pic, self.pic4)
    
class TodoTaskMemberTryMinTemplate(TodoTaskTemplate):
    TYPE_ID = 'todotask.template.memberTryMin'
    def __init__(self):
        super(TodoTaskMemberTryMinTemplate, self).__init__()
        self.desc = None
        self.allowClose = None
        
    def _decodeFromDictImpl(self, d):
        self.desc = d.get('desc', '')
        if not isstring(self.desc):
            raise TYBizConfException(d, 'TodoTaskMemberTryMinTemplate.desc must be string')
        self.allowClose = d.get('allowClose', 0)
        if self.allowClose not in (0, 1):
            raise TYBizConfException(d, 'TodoTaskMemberTryMinTemplate.allowClose must be int in (0,1)')
    
    def _newTodoTask(self, gameId, userId, clientId, timestamp, **kwargs):
        return TodoTaskShowInfo(self.desc, self.allowClose == 1)
    
class TodoTaskActivityTemplate(TodoTaskTemplate):
    TYPE_ID = 'todotask.template.activity'
    def __init__(self):
        super(TodoTaskActivityTemplate, self).__init__()
        self.actId = None
        
    def _decodeFromDictImpl(self, d):
        self.actId = d.get('actId')
        if self.actId is not None and not isstring(self.actId):
            raise TYBizConfException(d, 'TodoTaskActivityNewFactory.actId must be string')
    
    def _newTodoTask(self, gameId, userId, clientId, timestamp, **kwargs):
        return TodoTaskActivityNew(self.actId)
    
class TodoTaskMonthCheckinTemplate(TodoTaskTemplate):
    TYPE_ID = 'todotask.template.monthCheckin'
    def __init__(self):
        super(TodoTaskMonthCheckinTemplate, self).__init__()
        
    def _decodeFromDictImpl(self, d):
        pass
    
    def _newTodoTask(self, gameId, userId, clientId, timestamp, **kwargs):
        return TodoTaskMonthCheckinNew()

class TodoTaskLessbuyChipTemplate(TodoTaskTemplate):
    TYPE_ID = 'todotask.template.lessBuyChip'
    def __init__(self):
        super(TodoTaskLessbuyChipTemplate, self).__init__()
        self.desc = None
        self.note = None
        self.iconPic = None
        self.subText = None
        self.subTextWinpcCharge = None
        
    def _decodeFromDictImpl(self, d):
        self.desc = d.get('desc', '')
        if not isstring(self.desc):
            raise TYBizConfException(d, 'TodoTaskLessbuyChipTemplate.desc must be string')
        self.iconPic = d.get('iconPic', '')
        if not isstring(self.iconPic):
            raise TYBizConfException(d, 'TodoTaskLessbuyChipTemplate.iconPic must be string')
        self.note = d.get('note', '')
        if not isstring(self.note):
            raise TYBizConfException(d, 'TodoTaskLessbuyChipTemplate.note must be string')
        self.subText = d.get('subText', '')
        if not isstring(self.subText):
            raise TYBizConfException(d, 'TodoTaskLessbuyChipTemplate.subText must be string')
        self.subTextWinpcCharge = d.get('subTextWinpcCharge', '')
        if not isstring(self.subTextWinpcCharge):
            raise TYBizConfException(d, 'TodoTaskLessbuyChipTemplate.subTextWinpcCharge must be string')
        
    def _newTodoTask(self, gameId, userId, clientId, timestamp, **kwargs):
        from hall.entity import hallproductselector
        roomId = kwargs.get('roomId')
        minCoin = kwargs.get('minCoin', None)
        if ftlog.is_debug():
            ftlog.debug('TodoTaskLessbuyChipTemplate._newTodoTask gameId=', gameId,
                        'userId=', userId,
                        'clientId=', clientId,
                        'timestamp=', timestamp,
                        'roomId=', roomId,
                        'kwargs=', kwargs)
        
        roomMinChip = minCoin or gdata.getRoomMinCoin(roomId)
        if roomMinChip is None:
            ftlog.warn('TodoTaskLessbuyChipTemplate._newTodoTask gameId=', gameId,
                       'userId=', userId,
                       'clientId=', clientId,
                       'timestamp=', timestamp,
                       'roomId=', roomId,
                       'kwargs=', kwargs)
            return None
        product, _ = hallproductselector.selectLessbuyProduct(gameId, userId, clientId, roomId)
        if not product:
            ftlog.warn('TodoTaskLessbuyChipTemplate._newTodoTask gameId=', gameId,
                       'userId=', userId,
                       'clientId=', clientId,
                       'timestamp=', timestamp,
                       'roomId=', roomId,
                       'kwargs=', kwargs,
                       'err=', 'NoProduct')
            return None
        desc = strutil.replaceParams(self.desc, {'room.minCoin':str(roomMinChip), 'product.displayName':product.displayName})
        note = strutil.replaceParams(self.note, {'product.price':str(product.price)})
        ret = TodoTaskLessBuyOrder(desc, self.iconPic, note, None,roomMinChip)
        if product:
            payOrder = TodoTaskHelper.makeTodoTaskPayOrder(userId, clientId, product)
            if not payOrder.isWinpcCharge:
                ret.setSubCmdWithText(payOrder, self.subText)
            else:
                ret.setSubCmdWithText(payOrder, self.subTextWinpcCharge)
        return ret
         
class TodoTaskRecommendBuyTemplate(TodoTaskTemplate):
    TYPE_ID = 'todotask.template.recommendBuy'
    def __init__(self):
        super(TodoTaskRecommendBuyTemplate, self).__init__()
        self.desc = None
        self.pic = None
        self.titlePic = None
        self.payOrder = None
        self.subActionText = None
        
    def _decodeFromDictImpl(self, d):
        self.desc = d.get('desc', '')
        if not isstring(self.desc):
            raise TYBizConfException(d, 'TodoTaskRecommendBuyTemplate.desc must be string')
        self.pic = d.get('pic', '')
        if not isstring(self.pic):
            raise TYBizConfException(d, 'TodoTaskRecommendBuyTemplate.pic must be string')
        self.titlePic = d.get('titlePic', '')
        if not isstring(self.titlePic):
            raise TYBizConfException(d, 'TodoTaskRecommendBuyTemplate.titlePic must be string')
        self.payOrder = d.get('payOrder')
        if not isinstance(self.payOrder, dict):
            raise TYBizConfException(d, 'TodoTaskRecommendBuyTemplate.payOrder must be dict')
        self.subActionText = d.get('subActionText')
        if not isstring(self.subActionText) or not self.subActionText:
            raise TYBizConfException(d, 'TodoTaskRecommendBuyTemplate.subActionText must be string')
        
    def _newTodoTask(self, gameId, userId, clientId, timestamp, **kwargs):
        product, _ = hallstore.findProductByPayOrder(gameId, userId, clientId, self.payOrder)
        if product:
            return TodoTaskRecommendBuy(self.desc, self.pic, self.titlePic, product, self.subActionText)
        return None
    
class TodoTaskFirstRechargeReceiveTemplate(TodoTaskTemplate):
    TYPE_ID = 'todotask.template.firstRechargeReceive'
    def __init__(self):
        super(TodoTaskFirstRechargeReceiveTemplate, self).__init__()
        self.desc = None
        self.pic = None
        self.titlePic = None
        self.subActionText = None
        
    def _decodeFromDictImpl(self, d):
        self.desc = d.get('desc', '')
        if not isstring(self.desc):
            raise TYBizConfException(d, 'TodoTaskFirstRechargeReceiveTemplate.desc must be string')
        self.pic = d.get('pic', '')
        if not isstring(self.pic):
            raise TYBizConfException(d, 'TodoTaskFirstRechargeReceiveTemplate.pic must be string')
        self.titlePic = d.get('titlePic', '')
        if not isstring(self.titlePic):
            raise TYBizConfException(d, 'TodoTaskFirstRechargeReceiveTemplate.titlePic must be string')
        self.subActionText = d.get('subActionText')
        if not isstring(self.subActionText) or not self.subActionText:
            raise TYBizConfException(d, 'TodoTaskFirstRechargeReceiveTemplate.subActionText must be string')
        
    def _newTodoTask(self, gameId, userId, clientId, timestamp, **kwargs):
        ret = TodoTaskRecommendBuy(self.desc, self.pic, self.titlePic, None, self.subActionText)
        ret.setSubCmdWithText(TodoTaskReceiveFirstRechargeReward())
        return ret
    
class TodoTaskRoomBuyTemplate(TodoTaskTemplate):
    def __init__(self):
        super(TodoTaskRoomBuyTemplate, self).__init__()
        self.desc = None
        self.selectProductAction = None
        self.subActionText = None

    def _decodeFromDictImpl(self, d):
        self.desc = d.get('desc', '')
        if not isstring(self.desc):
            raise TYBizConfException(d, 'TodoTaskRoomBuyTemplate.desc must be string')
        self.selectProductAction = d.get('selectProductAction')
        if not isstring(self.selectProductAction) or not self.selectProductAction:
            raise TYBizConfException(d, 'TodoTaskRoomBuyTemplate.selectProductAction must be string')
        self.subActionText = d.get('subActionText')
        if not isstring(self.subActionText) or not self.subActionText:
            raise TYBizConfException(d, 'TodoTaskRoomBuyTemplate.subActionText must be string')
        
    def _newTodoTask(self, gameId, userId, clientId, timestamp, **kwargs):
        from hall.entity import hallproductselector
        roomId = kwargs.get('roomId')
        if ftlog.is_debug():
            ftlog.debug('TodoTaskRoomBuyTemplate._newTodoTask gameId=', gameId,
                        'userId=', userId,
                        'clientId=', clientId,
                        'timestamp=', timestamp,
                        'roomId=', roomId,
                        'selectProductAction=', self.selectProductAction,
                        'kwargs=', kwargs)
        if roomId:
            product, _ = hallproductselector.selectProcutByRoomId(gameId, userId, clientId, roomId, self.selectProductAction)
            if product:
                return self._newTodoTaskByProduct(gameId, userId, clientId, timestamp, product, **kwargs)
        return None
    
    def _newTodoTaskByProduct(self, gameId, userId, clientId, timestamp, product, **kwargs):
        raise NotImplemented()
    
class TodoTaskLuckBuyTemplate(TodoTaskRoomBuyTemplate):
    TYPE_ID = 'todotask.template.luckBuy'
    def __init__(self):
        super(TodoTaskLuckBuyTemplate, self).__init__()
        self.tip = None
        
    def _decodeFromDictImpl(self, d):
        super(TodoTaskLuckBuyTemplate, self)._decodeFromDictImpl(d)
        self.tip = d.get('tip', '')
        self.confparams = d
        ftlog.debug("TodoTaskLuckBuyTemplate", d)
        if not isstring(self.tip):
            raise TYBizConfException(d, 'TodoTaskLuckBuyTemplate.tip must be string')
        
    def _newTodoTaskByProduct(self, gameId, userId, clientId, timestamp, product, **kwargs):
        tip = strutil.replaceParams(self.tip, {'product.desc':product.desc})
        if hasattr(self, 'confparams'):
            return TodoTaskLuckBuy(self.desc, tip, product, self.subActionText, self.confparams)
        else:
            return TodoTaskLuckBuy(self.desc, tip, product, self.subActionText)
    
class TodoTaskWinBuyTemplate(TodoTaskRoomBuyTemplate):
    TYPE_ID = 'todotask.template.winBuy'
    def __init__(self):
        super(TodoTaskWinBuyTemplate, self).__init__()
        self.tip = None
        
    def _decodeFromDictImpl(self, d):
        super(TodoTaskWinBuyTemplate, self)._decodeFromDictImpl(d)
        self.tip = d.get('tip', '')
        self.confparams = d
        ftlog.debug("TodoTaskWinBuyTemplate", d)
        if not isstring(self.tip):
            raise TYBizConfException(d, 'TodoTaskWinBuyTemplate.tip must be string')
        
    def _newTodoTaskByProduct(self, gameId, userId, clientId, timestamp, product, **kwargs):
        tip = strutil.replaceParams(self.tip, {'product.desc':product.desc})
        if hasattr(self, 'confparams'):
            return TodoTaskWinBuy(self.desc, tip, product, self.subActionText, self.confparams)
        else:
            return TodoTaskWinBuy(self.desc, tip, product, self.subActionText)
    
class TodoTaskTemplateRegister(TYConfableRegister):
    _typeid_clz_map = {
        TodoTaskFirstRechargeTryTemplate.TYPE_ID:TodoTaskFirstRechargeTryTemplate,
        TodoTaskMemberBuyTemplate.TYPE_ID:TodoTaskMemberBuyTemplate,
        TodoTaskMemberBuy2Template.TYPE_ID:TodoTaskMemberBuy2Template,
        TodoTaskMonthlyBuyTemplate.TYPE_ID:TodoTaskMonthlyBuyTemplate,
        TodoTaskMemberTryTemplate.TYPE_ID:TodoTaskMemberTryTemplate,
        TodoTaskRecommendBuyTemplate.TYPE_ID:TodoTaskRecommendBuyTemplate,
        TodoTaskActivityTemplate.TYPE_ID:TodoTaskActivityTemplate,
        TodoTaskMonthCheckinTemplate.TYPE_ID:TodoTaskMonthCheckinTemplate,
        TodoTaskPayOrderTemplate.TYPE_ID:TodoTaskPayOrderTemplate,
        TodoTaskMemberTryMinTemplate.TYPE_ID:TodoTaskMemberTryMinTemplate,
        TodoTaskLessbuyChipTemplate.TYPE_ID:TodoTaskLessbuyChipTemplate,
        TodoTaskLuckBuyTemplate.TYPE_ID:TodoTaskLuckBuyTemplate,
        TodoTaskWinBuyTemplate.TYPE_ID:TodoTaskWinBuyTemplate,
        TodoTaskIosUpgradeTemplate.TYPE_ID:TodoTaskIosUpgradeTemplate,
        # 注意，此窗口是畸形窗口以后尽量不要用
        TodoTaskFirstRechargeReceiveTemplate.TYPE_ID:TodoTaskFirstRechargeReceiveTemplate,
    }

def _reloadConf():
    global _templateMap
    conf = hallconf.getPopWndConf()
    templateMap = {}
    templates = conf.get('templates')
    for templateName, template in templates.iteritems():
        ftlog.debug('hallpopwnd reloadConf templateName:', templateName)
        if templateName in templateMap:
            raise TYBizConfException(template, ' Duplicate simple_invite %s' % (templateName))
        
        actionMap = {}
        templateMap[templateName] = actionMap
        for actionName, action in template.iteritems():
            actionMap[actionName] = TodoTaskTemplateRegister.decodeFromDict(action)
    for templateName, actionMap in templateMap.iteritems():
        for actionName, action in actionMap.iteritems():
            action.initWhenLoaded(actionMap)
            
    _templateMap = templateMap
    ftlog.debug('hallpopwnd._reloadConf successed templateNames=', templateMap.keys())
    
def _onConfChanged(event):
    if _inited and event.isModuleChanged(['popwnd']):
        ftlog.debug('hallpopwnd._onConfChanged')
        _reloadConf()
        
def _initialize():
    ftlog.debug('hallpopwnd._initialize begin')
    global _inited
    if not _inited:
        _inited = True
        _reloadConf()
        pkeventbus.globalEventBus.subscribe(EventConfigure, _onConfChanged)
    ftlog.debug('hallpopwnd._initialize end')
    
def makeAfterNsloginReward(gameId, userId, clientId, remainDays, memberBonus):
    memberBuy = None
    if remainDays <= 0:
        # 还不是会员，推荐成为会员
        memberBuy = makeTodoTaskByTemplate(gameId, userId, clientId, 'memberBuy')

    skipMember = makeTodoTaskByTemplate(gameId, userId, clientId, 'firstRechargeTry')
    if not skipMember:
        skipMember = makeTodoTaskByTemplate(gameId, userId, clientId, 'recommendBuy')
        if not skipMember:
            skipMember = makeTodoTaskByTemplate(gameId, userId, clientId, 'activity')

    return memberBuy, skipMember

def makeTodoTaskNsloginRewardOld(gameId, userId, clientId, remainDays, memberBonus):
    from hall.entity import halldailycheckin
    
    timestamp = pktimestamp.getCurrentTimestamp()
    states = halldailycheckin.dailyCheckin.getStates(gameId, userId, timestamp)
    
    if ftlog.is_debug():
        ftlog.debug('hallpopwnd.makeTodoTaskNsloginReward gameId=', gameId,
                    'userId=', userId,
                    'clientId=', clientId,
                    'states=', states)
        
    if not TodoTaskHelper.canGainReward(states):
        if ftlog.is_debug():
            ftlog.debug('hallpopwnd.makeTodoTaskNsloginReward gameId=', gameId,
                        'userId=', userId,
                        'clientId=', clientId,
                        'states=', states,
                        'err=', 'CannotGainReward')
        return None
    
    todotask = TodoTaskNsloginReward(TodoTaskHelper.translateDailyCheckinStates(states))
    todotask.setMemberInfo(remainDays > 0, remainDays, memberBonus)
    
    memberBuy, skipMember = makeAfterNsloginReward(gameId, userId, clientId, remainDays, memberBonus)
    
    if memberBuy:
        todotask.setSubCmd(memberBuy)
        if skipMember:
            todotask.setParam('sub_action_skip_member', skipMember)
    
    click = memberBuy or skipMember
    if click:
        todotask.setParam('sub_action_click', click)
    return todotask

def getLoginDays(userId):
    createTime = datetime.strptime(pkuserdata.getAttr(userId, 'createTime'), '%Y-%m-%d %H:%M:%S.%f')
    return (datetime.now().date() - createTime.date()).days
    
def getRewardToday(userId):
    from poker.entity.dao import gamedata
    from hall.entity.hallconf import HALL_GAMEID
    import time
    d = gamedata.getGameAttrJson(userId, HALL_GAMEID, 'monthCheckin')
    rewardToday = False
    nowData = time.strftime('%Y%m%d', time.localtime())
    if d and d.get('cl', []):
        # 存在key monthCheckin
        if nowData in d.get('cl', []):
            # 已签到
            rewardToday = False
        else:
            # 未签到
            rewardToday = True
    else:
        # 不存在key
        rewardToday = True
    return rewardToday

def makeNormalLoginTodotask(gameId, userId, clientId, remainDays, memberBonus, isdayfirst, timestamp):
    loginDays = getLoginDays(userId)
    ret = None
    user_money = pkuserdata.getAttrInt(userId, 'chargeTotal')
    if 0 <= loginDays <= 1:
        ret = makeTodoTaskByTemplate(gameId, userId, clientId, 'activity')
    elif 2 <= loginDays <= 5:
        if user_money > 50 :
            # 弹活动模板
            ret = makeTodoTaskByTemplate(gameId, userId, clientId, 'activity')
        else:
            # 付费弹窗
            if isdayfirst: 
                # 获取玩家会员信息
                ret = makeTodoTaskByTemplate(gameId, userId, clientId, 'memberBuy2')
                # 获取玩家会员信息
                memberInfo = hallitem.getMemberInfo(userId, timestamp)
                remainDays = memberInfo[0]
                # 如果已经是会员,或者没有配会员商品,则改为特惠商品     
                if remainDays > 0 or not ret:
                    ret = makeTodoTaskByTemplate(gameId, userId, clientId, 'recommendBuy')
            else:
                # 弹活动模板
                ret = makeTodoTaskByTemplate(gameId, userId, clientId, 'activity')
    elif loginDays > 5:
        if user_money < 30 or user_money > 500 :
            # 弹活动模板
            ret = makeTodoTaskByTemplate(gameId, userId, clientId, 'activity')
        else :
            if isdayfirst: 
                ret = makeTodoTaskByTemplate(gameId, userId, clientId, 'memberBuy2')
                # 获取玩家会员信息
                memberInfo = hallitem.getMemberInfo(userId, timestamp)
                remainDays = memberInfo[0]
                # 如果已经是会员,或者没有配会员商品,则改为特惠商品     
                if remainDays > 0 or not ret:
                    ret = makeTodoTaskByTemplate(gameId, userId, clientId, 'recommendBuy')
            else:
                # 弹活动模板
                ret = makeTodoTaskByTemplate(gameId, userId, clientId, 'activity')
    
    if ftlog.is_debug():
        ftlog.debug('hallpopwnd.makeNormalLoginTodotask userId=', userId,
                    'gameId=', gameId,
                    'clientId=', clientId,
                    'remainDays=', remainDays,
                    'isdayfirst=', isdayfirst,
                    'loginDays=', loginDays,
                    'user_money=', user_money) 
    return ret

def makeTodoTaskNsloginReward(gameId, userId, clientId, remainDays, memberBonus, isdayfirst):
    timestamp = pktimestamp.getCurrentTimestamp()
    from hall.entity import halldailycheckin
    from poker.entity.dao import gamedata
    _, clientVer, _ = strutil.parseClientId(clientId)
    checkinVer = gamedata.getGameAttrInt(userId, gameId, 'checkinVer')
    ret = []
    todotask = None
    if clientVer < 3.76:
        if checkinVer != 1:
            states = halldailycheckin.dailyCheckin.getStates(gameId, userId, timestamp)
            if not TodoTaskHelper.canGainReward(states):
                if ftlog.is_debug():
                    ftlog.debug('hallpopwnd.makeTodoTaskNsloginReward gameId=', gameId,
                                'userId=', userId,
                                'clientId=', clientId,
                                'states=', states,
                                'err=', 'CannotGainReward')
            else:
                todotask = TodoTaskNsloginReward(TodoTaskHelper.translateDailyCheckinStates(states))
                todotask.setMemberInfo(remainDays > 0, remainDays, memberBonus)    
        nextTodotask = makeTodoTaskByTemplate(gameId, userId, clientId, 'memberBuy2')
        # 获取玩家会员信息
        memberInfo = hallitem.getMemberInfo(userId, timestamp)
        remainDays = memberInfo[0]
        # 如果已经是会员,或者没有配会员商品,则改为特惠商品     
        if remainDays > 0 or not nextTodotask:
            nextTodotask = makeTodoTaskByTemplate(gameId, userId, clientId, 'recommendBuy')
        if todotask and nextTodotask:
            todotask.setParam('sub_action_click', nextTodotask)
        if todotask:
            ret.append(todotask)
        elif nextTodotask:
            ret.append(nextTodotask)
    else :
        # 3.76的处理流程
        startFlow = hallconf.getStartFlowConf()
        ftlog.debug('makeTodoTaskNsloginReward startFlow:', startFlow)
        
        gen = TodoTasksGeneratorRegister.decodeFromDict(startFlow)
        todotasks = gen.makeTodoTasks(gameId, userId, clientId, timestamp, isDayFirstLogin=isdayfirst)
        ftlog.debug('makeTodoTaskNsloginReward todotasks =', todotasks,
                   'userId =', userId,
                   'gameId =', gameId,
                   'clientId =', clientId,
                   'remainDays =', remainDays,
                   'isdayfirst =', isdayfirst,
                   'memberBonus =', memberBonus)
        if todotasks:
            # 优先使用配置好的弹窗
            ret.extend(todotasks)
        else:
            notinClientIds = UserConditionNotInClientIDs()
            notinClientIds.clientIds.append(20365)
            if notinClientIds.check(gameId, userId, clientId, timestamp):
                firstDayCond = UserConditionRegisterDay(0, 0)
                hallGameIdCond = UserConditionisMyGameid(6)
                if (not hallGameIdCond.check(gameId, userId, clientId, timestamp)
                    or not firstDayCond.check(gameId, userId, clientId, timestamp)):
                    # 其次使用推荐购买
                    tempPay = makeTodoTaskByTemplate(gameId, userId, clientId, 'recommendBuy')
                    if tempPay:
                        ret.append(tempPay)
                    else:
                        # 最后弹活动
                        tempObj = makeTodoTaskByTemplate(gameId, userId, clientId, 'activity')
                        if tempObj:
                            ret.append(tempObj)
            
    if ftlog.is_debug():
        ftlog.debug('hallpopwnd.makeTodoTaskNsloginReward gameId=', gameId,
                    'userId=', userId,
                    'clientId=', clientId,
                    'ret=', ret) 
    return ret

def makeTodoTaskByTemplate(gameId, userId, clientId, todotaskTemplateName, **kwargs):
    ret = None
    template, popwndTemplateName = findTodotaskTemplate(gameId, userId, clientId, todotaskTemplateName)
    if template:
        ret = template.newTodoTask(gameId, userId, clientId, **kwargs)
    if ftlog.is_debug():
        ftlog.debug('hallpopwnd.makeTodoTaskByTemplate gameId=', gameId,
                    'userId=', userId,
                    'clientId=', clientId,
                    'todotaskTemplateName=', todotaskTemplateName,
                    'popwndTemplateName=', popwndTemplateName,
                    'template=', template,
                    'kwargs=', kwargs,
                    'ret=', ret)
    return ret

def makeTodoTaskLuckBuy(gameId, userId, clientId, roomId):
    if ftlog.is_debug():
        ftlog.debug('hallpopwnd.makeTodoTaskLuckBuy gameId=', gameId,
                    'userId=', userId,
                    'clientId=', clientId,
                    'roomId=', roomId)
    return makeTodoTaskByTemplate(gameId, userId, clientId, 'luckBuy', roomId=roomId)
        
def makeTodoTaskWinBuy(gameId, userId, clientId, roomId):
    if ftlog.is_debug():
        ftlog.debug('hallpopwnd.makeTodoTaskWinBuy gameId=', gameId,
                    'userId=', userId,
                    'clientId=', clientId,
                    'roomId=', roomId)
    return makeTodoTaskByTemplate(gameId, userId, clientId, 'winBuy', roomId=roomId)

def makeTodoTaskZhuanyun(gameId, userId, clientId, benefitsSend, userBenefits, roomId):
    """
    生成转运礼包
        benefitsSend - 发给用户的救济金，在转运推荐的取消里展示
        roomId - 根据roomId去发放转运礼包
    """
    from hall.entity import hallproductselector
    if ftlog.is_debug():
        ftlog.debug('hallpopwnd.makeTodoTaskZhuanyun gameId=', gameId,
                    'userId=', userId,
                    'clientId=', clientId,
                    'benefitsSend=', benefitsSend,
                    'userBenefits=', userBenefits.__dict__,
                    'roomId=', roomId)
    clientOs, _clientVer, _ = strutil.parseClientId(clientId)
    clientOs = clientOs.lower()
    
    # 非winpc
    if clientOs != 'winpc':
        return TodoTaskHelper.makeZhuanyunTodoTaskNew(gameId, userId, clientId,
                                                      benefitsSend, userBenefits, roomId)
    
    # winpc
    product, _ = hallproductselector.selectLessbuyProduct(gameId, userId, clientId, roomId)
    if not product:
        return None
    
    user_diamond = pkuserdata.getAttr(userId, 'diamond')
    if user_diamond >= int(product.priceDiamond):
        chip = product.getMinFixedAssetCount(hallitem.ASSET_CHIP_KIND_ID)
        show_str = u'运气不好，来个转运礼包！%s元得%s万金币。' % (product.price, chip)
        buy_type = 'consume'
        btn_txt = u'兑换'
    else:
        show_str = u'运气不好~，买点金币战个痛快吧！'
        buy_type = 'charge'
        btn_txt = u'去充值'
    orderShow = TodoTaskOrderShow.makeByProduct(show_str, '', product, buy_type)
    orderShow.setParam('sub_action_btn_text', btn_txt)
    return orderShow

def makeTodoTaskZhuanyunByLevelName(gameId, userId, clientId, benefitsSend, userBenefits, levelName):
    """
    根据游戏自定的levelName生成转运推荐弹窗
    benefitsSend - 救济金，在转运推荐取消里展示
    levelName - 级别，根据级别选择合适的转运礼包商品
    """
    if ftlog.is_debug():
        ftlog.debug('hallpopwnd.makeTodoTaskZhuanyunByLevelName gameId=', gameId,
                    'userId=', userId,
                    'clientId=', clientId,
                    'benefitsSend=', benefitsSend,
                    'userBenefits=', userBenefits.__dict__,
                    'levelName=', levelName)
    clientOs, _clientVer, _ = strutil.parseClientId(clientId)
    clientOs = clientOs.lower()
    
    # 不支持winpc，只支持手机游戏
    return TodoTaskHelper.makeZhuanyunTodoTaskByLevelName(gameId, userId, clientId,
                                                      benefitsSend, userBenefits, levelName)

def makeTodoTaskLessbuyChip(gameId, userId, clientId, roomId, **kwargs):
    from hall.entity import hallproductselector
    if ftlog.is_debug():
        ftlog.debug('hallpopwnd.makeTodoTaskLessbuyChip gameId=', gameId,
                    'userId=', userId,
                    'clientId=', clientId,
                    'roomId=', roomId)
    clientOs, clientVer, _ = strutil.parseClientId(clientId)
    clientOs = clientOs.lower()
    if clientVer >= 3.7:
        template, popwndTemplateName = findTodotaskTemplate(gameId, userId, clientId, 'lessBuyChip')
        if ftlog.is_debug():
            ftlog.debug('hallpopwnd.makeTodoTaskLessbuyChip gameId=', gameId,
                        'userId=', userId,
                        'clientId=', clientId,
                        'roomId=', roomId,
                        'popwndTemplateName=', popwndTemplateName,
                        'template=', template)
        if template:
            minCoin = kwargs.get('minCoin', None)
            return template.newTodoTask(gameId, userId, clientId, roomId=roomId, minCoin=minCoin)
    else:
        product, _ = hallproductselector.selectLessbuyProduct(gameId, userId, clientId, roomId)
        if product:
            if clientOs == 'winpc':
                # pc特殊处理
                user_diamond = pkuserdata.getAttr(userId, 'diamond')
                if user_diamond >= int(product.priceDiamond):
                    show_str = u'您的金币不够哦~兑换点金币战个痛快吧'
                    buy_type = 'consume'
                    btn_txt = u'兑换'
                else:
                    show_str = u'您的金币不够哦~买点金币战个痛快吧'
                    buy_type = 'charge'
                    btn_txt = u'去充值'
                orderShow = TodoTaskOrderShow.makeByProduct(show_str, '', product, buy_type)
                orderShow.setParam('sub_action_btn_text', btn_txt)
                return orderShow
            else:
                show_str = '         高手过招没钱哪行？\n         充值${product.price}元立即开战！'
                show_str = strutil.replaceParams(show_str, {'product.price':product.price})
                return TodoTaskOrderShow.makeByProduct(show_str, '', product)
    return None

def makeTodoTaskBuyTableChip(gameId, userId, clientId, coin, dis, timeOut, isGameOver, delay, **kwargs):
    '''
    根据所需补充的金币数自动选择合适的商品
    摒弃转运礼包按照房间配置的设计
    
    货架范围：
    lessbuychip
    luckBuy
    
    参数说明：
    coin - 代补充的金币数
    dis - 弹窗说明
    timeOut - 操作超时
    isGameOver - 牌局是否结束
        True 结束
        False 未结束，牌局进行中
    '''
    from hall.entity import hallproductselector
    if ftlog.is_debug():
        ftlog.debug('hallpopwnd.makeTodoTaskBuyTableChip gameId=', gameId,
                    'userId=', userId,
                    'clientId=', clientId,
                    'coin=', coin)
    clientOs, clientVer, _ = strutil.parseClientId(clientId)
    clientOs = clientOs.lower()
    ratio = 1000
    if clientVer >= 5.0:
        ratio = 2000
        
    count = coin / ratio
    if coin % ratio > 0:
        count += 1
        
    product, _ = hallproductselector.selectProductByPayOrder(gameId, userId, clientId, {
                "shelves":["lessbuychip", "luckBuy"],
                "buyTypes":["consume", "direct"],
                "priceDiamond":{"count":count, "minCount":0}
            }
        )
    
    if product:
        content = product.price + '￥=' + product.displayName
        zhekouInfo = ''
        items = product.content.getItems()
        ftlog.debug('items:', items)
        
        chipCount = 0
        for item in items:
            if item.assetKindId == 'user:chip':
                chipCount = item.count
        if chipCount != 0:
            zhekou = chipCount * 100 / (ratio * int(product.priceDiamond)) - 100
            if zhekou > 0:
                zhekouInfo = '加赠' + str(zhekou) + '%'
                
        ftlog.debug('product chipCount:', chipCount
                    , ' priceDiamond:', product.priceDiamond
                    , ' zhekou:', zhekouInfo)
        
        return TodoTaskBuyTableCoin.makeByProduct(dis, content, product, timeOut, isGameOver, delay, zhekouInfo)
    return None

def makeTodoTaskDiamondToCoin(gameId, userId, clientId, coin, dis, timeOut, isGameOver, delay, **kwargs):
    '''
    钻石转金币
    coin 代补充的金币
    dis 弹窗提示
    timeOut 操作超时
    isGameOver 游戏是否结束
        True 结束
        False 未结束，牌局进行中
    '''
    from hall.entity import hallproductselector
    ftlog.debug('hallpopwnd.makeTodoTaskDiamondToCoin gameId=', gameId,
                    'userId=', userId,
                    'clientId=', clientId,
                    'coin=', coin)
    
    product, _ = hallproductselector.selectDiamondToCoinProduct(gameId, userId, clientId)
    if product:
        ftlog.debug('find product ok...')
        
        count = 0
        ratio = product.diamondExchangeRate
        ftlog.debug('ratio:', ratio)
        if ratio <= 0:
            return None
        
        count = coin / ratio
        if coin % ratio > 0:
            count += 1
            
        diamondHave = userchip.getDiamond(userId)
        if diamondHave < count:
            return None
        
        coinTotal = count * ratio
        coinDis = str(coinTotal)
        if (coinTotal > 100000) and (coinTotal % 10000 == 0):
            coinDis = str(coinTotal/10000) + '万'
            
        content = str(count) + '钻石=' + coinDis + '金币'
        promote = '背包钻石剩余：' + str(diamondHave)
        
        return TodoTaskDiamondToCoin.makeByProduct(dis, content, promote, product, count, timeOut, isGameOver, delay)
    
    return None

def makeTodoTaskBuyDiamondProduct(gameId, userId, clientId, diamondCount, tipStr, **kwargs):
    '''
    充值钻石
    diamondCount 待充值的钻石数量
    tipStr 弹窗提示
    '''
    from hall.entity import hallproductselector
    ftlog.debug('hallpopwnd.makeTodoTaskBuyDiamondProduct gameId=', gameId,
                    'userId=', userId,
                    'clientId=', clientId,
                    'diamondCount=', diamondCount)
    
    product, _ = hallproductselector.selectDiamondProduct(gameId, userId, clientId, diamondCount)
    if product:
        ftlog.debug('find product ok...')
        return TodoTaskOrderShow.makeByProduct(tipStr, '', product)
    
    return None
    
def findTodotaskTemplate(gameId, userId, clientId, todotaskTemplateName):
    templateName = hallconf.getClientPopWndTemplateName(clientId)
    todotaskTemplateMap = _templateMap.get(templateName)
    if todotaskTemplateMap:
        return todotaskTemplateMap.get(todotaskTemplateName), templateName
    return None, templateName

def decodeTodotaskFactoryByDict(d):
    typeId = d.get('typeId')
    if typeId:
        return TodoTaskRegister.decodeFromDict(d)
    else:
        templateName = d.get('templateName')
        if not isstring(templateName):
            raise TYBizConfException(d, 'templateName must be string')
        return TodoTaskFactoryTemplate(templateName)

class TodoTaskFactoryTemplate(TodoTaskFactory):
    def __init__(self, templateName):
        self.templateName = templateName
        
    def newTodoTask(self, gameId, userId, clientId, **kwargs):
        return makeTodoTaskByTemplate(gameId, userId, clientId, self.templateName, **kwargs)

class TodoTasksGenerator(TYConfable):
    def __init__(self):
        self.condition = None
        self.conf = None
        
    def makeTodoTasks(self, gameId, userId, clientId, timestamp, **kwargs):
        if ftlog.is_debug():
            ftlog.debug('TodoTasksGenerator.makeTodoTasks gameId=', gameId,
                        'userId=', userId,
                        'clientId=', clientId,
                        'timestamp=', timestamp,
                        'kwargs=', kwargs,
                        'condition=', self.condition)
        if not self.condition or self.condition.check(gameId, userId, clientId, timestamp, **kwargs):
            return self._makeTodoTasks(gameId, userId, clientId, timestamp, **kwargs)
        return None
    
    def decodeFromDict(self, d):
        condition = d.get('condition')
        if condition:
            self.condition = UserConditionRegister.decodeFromDict(condition)
        self.conf = d
        self._decodeFromDictImpl(d)
        return self

    def _makeTodoTasks(self, gameId, userId, clientId, timestamp, **kwargs):
        return None

    def _decodeFromDictImpl(self, d):
        pass
    
class TodoTasksGeneratorSingle(TodoTasksGenerator):
    TYPE_ID = 'todotasks.gen.single'
    def __init__(self):
        super(TodoTasksGeneratorSingle, self).__init__()
        self.todotaskFactory = None
        
    def _makeTodoTasks(self, gameId, userId, clientId, timestamp, **kwargs):
        todotask = None
        if self.todotaskFactory:
            todotask = self.todotaskFactory.newTodoTask(gameId, userId, clientId, **kwargs)
        return [todotask] if todotask else None
     
    def _decodeFromDictImpl(self, d):
        self.todotaskFactory = decodeTodotaskFactoryByDict(d.get('todotask'))
    
class TodoTasksGeneratorSwitch(TodoTasksGenerator):
    TYPE_ID = 'todotasks.gen.switch'
    def __init__(self):
        super(TodoTasksGeneratorSwitch, self).__init__()
        self.genList = []
        
    def _makeTodoTasks(self, gameId, userId, clientId, timestamp, **kwargs):
        for gen in self.genList:
            todotasks = gen.makeTodoTasks(gameId, userId, clientId, timestamp, **kwargs)
            if todotasks:
                return todotasks
        return None
    
    def _decodeFromDictImpl(self, d):
        self.genList = TodoTasksGeneratorRegister.decodeList(d.get('list', []))

class TodoTasksGeneratorList(TodoTasksGenerator):
    TYPE_ID = 'todotasks.gen.list'
    def __init__(self):
        super(TodoTasksGeneratorList, self).__init__()
        self.genList = []
        
    def _makeTodoTasks(self, gameId, userId, clientId, timestamp, **kwargs):
        ret = []
        for gen in self.genList:
            todotasks = gen.makeTodoTasks(gameId, userId, clientId, timestamp, **kwargs)
            if todotasks:
                ret.extend(todotasks)
        return ret or None
        
    def _decodeFromDictImpl(self, d):
        self.genList = TodoTasksGeneratorRegister.decodeList(d.get('list', []))
            
class TodoTasksGeneratorRegister(TYConfableRegister):
    _typeid_clz_map = {
        TodoTasksGeneratorList.TYPE_ID:TodoTasksGeneratorList,      # todotask列表
        TodoTasksGeneratorSwitch.TYPE_ID:TodoTasksGeneratorSwitch,  # 从列表中选出第一个合适的
        TodoTasksGeneratorSingle.TYPE_ID:TodoTasksGeneratorSingle   # 一个task
    }
    
def processLoseOutRoomV3_7(gameId, userId, clientId, roomId, showMemberTry=False):
    if ftlog.is_debug():
        ftlog.debug('hallpopwnd.processLoseOutRoomV3_7 gameId=', gameId,
                    'userId=', userId,
                    'clientId=', clientId,
                    'roomId=', roomId)
    
    timestamp = pktimestamp.getCurrentTimestamp()
    remainDays, _memberBonus = hallitem.getMemberInfo(userId, timestamp)
    
    benefitsSend, userBenefits = hallbenefits.benefitsSystem.sendBenefits(gameId, userId, timestamp)
    
    memberTry = None
    luckBuyOrLessBuyChip = makeTodoTaskLuckBuy(gameId, userId, clientId, roomId)
    if not luckBuyOrLessBuyChip:
        luckBuyOrLessBuyChip = makeTodoTaskLessbuyChip(gameId, userId, clientId, roomId)
    
    # 冲过值的或者新用户不弹试用会员
    isNewUser = UserConditionRegisterDay(0, 0).check(gameId, userId, clientId, timestamp)
    if ftlog.is_debug():
        ftlog.debug('hallpopwnd.processLoseOutRoomV3_7 gameId=', gameId,
                    'userId=', userId,
                    'clientId=', clientId,
                    'roomId=', roomId,
                    'remainDays=', remainDays,
                    'payCount=', pkuserdata.getAttr(userId, 'payCount'),
                    'isNewUser=', isNewUser)
    if showMemberTry and remainDays <= 0 and pkuserdata.getAttr(userId, 'payCount') <= 0 and not isNewUser:
        memberTry = makeTodoTaskByTemplate(gameId, userId, clientId, 'memberTry')
        if memberTry and luckBuyOrLessBuyChip:
            memberTry.setCloseCmd(luckBuyOrLessBuyChip)
    else:
        ftlog.debug('Not show member popwnd')
    
    if luckBuyOrLessBuyChip:
        cancel = TodoTaskHelper.makeBenefitsTodoTask(gameId, userId, clientId, benefitsSend, userBenefits)
        if cancel:
            luckBuyOrLessBuyChip.setCloseCmd(cancel)
    todotask = memberTry or luckBuyOrLessBuyChip
    if todotask: 
        return TodoTaskHelper.sendTodoTask(gameId, userId, todotask)
    return None
        
def makeTodotaskJumpToStoreOrHall(desc):
    t = TodoTaskShowInfo(desc)
    ok = TodoTaskDiZhuEvent('dizhu_goto_store')
    cancel = TodoTaskDiZhuEvent('dizhu_back_hall')
    t.setSubCmd(ok)
    t.setSubCmdExt(cancel)
    return t
