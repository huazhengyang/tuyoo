# -*- coding=utf-8
'''
Created on 2016年6月20日

@author: zhaol
'''
import freetime.util.log as ftlog
from hall.entity import hallconf, datachangenotify
from poker.entity.events.tyevent import EventConfigure
import poker.entity.events.tyeventbus as pkeventbus
import poker.util.timestamp as pktimestamp
from poker.entity.biz.item.item import TYAssetUtils
from poker.entity.biz.content import TYContentRegister
from poker.entity.biz.message import message as pkmessage
from hall.entity.todotask import TodoTaskHelper, TodoTaskShowInfo, TodoTaskShowRewards
from poker.entity.dao import gamedata
from hall.entity.hallconf import HALL_GAMEID
    
class HallLoginRewardsItem(object):
    def __init__(self):
        self.items = None
        self.conditions = None
        self.mail = None
        self.todotasks = None
        self.actions = None
        
    def decodeFromDict(self, d):
        from hall.entity.hallusercond import UserConditionRegister
        self.conditions = UserConditionRegister.decodeList(d.get('conditions', []))
        
        rewardContent = d.get('rewardContent')
        if rewardContent:
            self.items = TYContentRegister.decodeFromDict(rewardContent)
        self.mail = d.get('mail', '')
        
        from hall.entity.halluseraction import UserActionRegister
        self.actions = UserActionRegister.decodeList(d.get('actions', []))
        
        from hall.entity.todotask import TodoTaskRegister
        self.todotasks = TodoTaskRegister.decodeList(d.get('todotasks', []))
        
        return self
    
    def sendRewards(self, userId, gameId, clientId):
        bSend = True

        for cond in self.conditions:
            if not cond.check(gameId, userId, clientId, pktimestamp.getCurrentTimestamp()):
                bSend = False
                     
        if not bSend:
            return
        
        # 第一步 发奖励
        if self.items:
            from hall.entity import hallitem
            userAssets = hallitem.itemSystem.loadUserAssets(userId)
            assetList = userAssets.sendContent(gameId
                    , self.items
                    , 1
                    , True
                    , pktimestamp.getCurrentTimestamp()
                    , 'LOGIN_REWARD'
                    , 0)
            
            if assetList:
                if ftlog.is_debug():
                    ftlog.debug('hall_login_reward.sendReward gameId=', gameId,
                       'userId=', userId,
                       'rewards=', [(atup[0].kindId, atup[1]) for atup in assetList])
                # 记录登录奖励获取时间
                gamedata.setGameAttr(userId, HALL_GAMEID, 'login_reward', pktimestamp.getCurrentTimestamp())
                # 通知更新
                changedDataNames = TYAssetUtils.getChangeDataNames(assetList)
                datachangenotify.sendDataChangeNotify(gameId, userId, changedDataNames)
                from poker.util import strutil
                _, cVer, _ = strutil.parseClientId(clientId)
                if cVer < 3.90:
                    TodoTaskHelper.sendTodoTask(gameId, userId, TodoTaskShowInfo(self.mail, True))
                else:
                    rewardsList = []
                    for assetItemTuple in assetList:
                        '''
                        0 - assetItem
                        1 - count
                        2 - final
                        '''
                        assetItem = assetItemTuple[0]
                        reward = {}
                        reward['itemId'] = assetItem.kindId
                        reward['name'] = assetItem.displayName
                        reward['pic'] = assetItem.pic
                        reward['count'] = assetItemTuple[1]
                        rewardsList.append(reward)
                        
                    if ftlog.is_debug():
                        ftlog.debug('hall_login_reward.TodoTaskShowRewards rewardsList: ', rewardsList)
                    
                    TodoTaskHelper.sendTodoTask(gameId, userId, TodoTaskShowRewards(rewardsList))
        
        # 第二步，执行actions
        for action in self.actions:
            action.doAction(gameId, userId, clientId, pktimestamp.getCurrentTimestamp())
            
        # 第三步，发送todotasks
        tasks = TodoTaskHelper.makeTodoTasksByFactory(gameId, userId, clientId, self.todotasks)
        TodoTaskHelper.sendTodoTask(gameId, userId, tasks)
        
        # 第四步，发送消息
        pkmessage.send(gameId, pkmessage.MESSAGE_TYPE_SYSTEM, userId, self.mail)
        
_loginRewards = []
_inited = False

def _reloadConf():
    global _loginRewards
    
    _loginRewards = []
    
    conf = hallconf.getLoginRewardConf()
    rewards = conf.get('rewards', [])
    for reward in rewards:
        rItem = HallLoginRewardsItem().decodeFromDict(reward)
        _loginRewards.append(rItem)
    
    ftlog.debug('hall_login_reward._reloadConf successed config=', _loginRewards)
    
def _onConfChanged(event):
    global _inited
    
    if _inited and event.isModuleChanged('login_reward'):
        ftlog.debug('hall_login_reward._onConfChanged')
        _reloadConf()

def _initialize():
    global _inited

    ftlog.debug('hall_login_reward._initialize begin')
    if not _inited:
        _inited = True
        _reloadConf()
        pkeventbus.globalEventBus.subscribe(EventConfigure, _onConfChanged)
    ftlog.debug('hall_login_reward._initialize end')
    
def sendLoginReward(userId, gameId, clientId):
    global _loginRewards
    if ftlog.is_debug():
        ftlog.debug('hall_login_reward.sendLoginReward userId:', userId
                    , ' gameId:', gameId
                    , ' clientId:', clientId)

    conf = hallconf.getLoginRewardConf()
    supplement = conf.get('supplement', None)
    if supplement!=None:
        from hall.entity import hallitem
        changed = []
        userAssets = hallitem.itemSystem.loadUserAssets(userId)
        items=supplement["items"]
        for item in items:
            maxCount=item["count"]
            itemId=item["itemId"]
            balance=userAssets.balance(gameId
                               , itemId
                               , pktimestamp.getCurrentTimestamp())
            if (maxCount-balance)>0:

                assetKind, _addCount, _final = userAssets.addAsset(gameId, itemId, maxCount-balance, pktimestamp.getCurrentTimestamp(),
                                                                   'LOGIN_REWARD', 0)


                if assetKind.keyForChangeNotify:
                    changed.append(assetKind.keyForChangeNotify)

        datachangenotify.sendDataChangeNotify(gameId, userId, changed)

    for reward in _loginRewards:
        reward.sendRewards(userId, gameId, clientId)
    