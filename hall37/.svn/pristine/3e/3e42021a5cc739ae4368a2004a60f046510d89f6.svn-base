# -*- coding=utf-8
'''
Created on 2017年8月22日

@author: wangzhen

地方麻将金币场发放救济金模块 hallbenefits_fuzhou
注释：刚开始做的是抚州金币场，后缀统一用了 _fuzhou，以后后缀统一用 _dfchip

'''

import freetime.util.log as ftlog
from poker.entity.dao import userchip, gamedata
from poker.entity.events.tyevent import EventConfigure
import poker.entity.events.tyeventbus as pkeventbus
import poker.util.timestamp as pktimestamp
from hall.entity import hallconf, hallshare, todotask, hallstartchip_fuzhou
import hall.entity as hallentity
from hall.entity.todotask import TodoTaskHelper



_inited = False
fuzhou_config = {}
fuzhou_conditions = []




def fuzhou_sendBenefits(userId, gameId, clientId, isSendTodotask = True):
    '''
    抚州金币场发放救济金
    :param userId:
    :param gameId:
    :param clientId:
    :param isSendTodotask: 是否发送救济金的分享弹框
    '''
    try:
        return _sendBenefits(userId, gameId, clientId, isSendTodotask)  
    except:
        ftlog.error()
        return False

def _sendBenefits(userId, gameId, clientId, isSendTodotask):
    '''
    发放救济金
    :param userId:
    :param gameId:
    :param clientId:
    :param isSendTodotask: 是否发送救济金的分享弹框
    '''
    share = _needSendBenefits(userId, gameId, clientId)
    if not share:
        return False
    if getattr(share, 'reward_event_id', '') != 'HALL_BENEFITS_FU_ZHOU':
        ftlog.warn('hallbenefits_fuzhou _sendBenefits bi evnet id error, please check, share =', share, 'shareId =', share.shareId, 'userId =', userId)
    if isSendTodotask:
        ftlog.info("hallbenefits_fuzhou send benefits todotask.", "userId =", userId, "gameId =", gameId, "clientId =", clientId)
        subTask = share.buildTodotask(gameId, userId, fuzhou_config['shareKey'])
        task = todotask.TodoTaskShowInfo(fuzhou_config['shareInfo'], True)
        task.setSubCmdWithText(subTask, "领取")
        task.addSubCmdExtText("取消")
        TodoTaskHelper.sendTodoTask(gameId, userId, task)
    else:
        ftlog.info("hallbenefits_fuzhou send benefits directly.", "userId =", userId, "gameId =", gameId, "clientId =", clientId)
        hallshare.getShareReward(gameId, userId, share, fuzhou_config['shareKey'], pktimestamp.getCurrentTimestamp())
    return True

def getBenefitsTodoTask(userId, gameId, clientId):
    share = _needSendBenefits(userId, gameId, clientId)
    if not share:
        return None
    subTask = share.buildTodotask(gameId, userId, fuzhou_config['shareKey'])
    task = todotask.TodoTaskShowInfo(fuzhou_config['shareInfo'], True)
    task.setSubCmdWithText(subTask, "领取")
    task.addSubCmdExtText("取消")
    return task.toDict()
    

def _needSendBenefits(userId, gameId, clientId):
    '''
    是否需要发放救济金
    :param userId:
    :param gameId:
    :param clientId:
    '''
    global fuzhou_config
    if not _checkConditions(userId, clientId):
        return None
    
    if not hallstartchip_fuzhou.isSentStartChip(userId):
        return None
    
    if userchip.getChip(userId) >= fuzhou_config['minChip']:
        return None
    
    shareId = hallshare.getShareId(fuzhou_config['shareKey'], userId, gameId)
    if not shareId:
        return None
    share = hallshare.findShare(shareId)
    if not share:
        return None
    
    ok, rewardCount = hallshare.checkCanReward(userId, share, pktimestamp.getCurrentTimestamp())
    if not ok or rewardCount > fuzhou_config['maxCount']:
        ftlog.info("hallbenefits_fuzhou daily count:%s is used up!" % fuzhou_config['maxCount'], "userId =", userId, "gameId =", gameId, "clientId =", clientId)
        return None
    return share

def _checkConditions(userId, clientId):
    '''
    检查条件
    :param userId:
    :param clientId:
    '''
    global fuzhou_config, fuzhou_conditions
    if not fuzhou_config:
        return False
    
    if len(fuzhou_conditions) == 0:
            return True
        
    for cond in fuzhou_conditions:
        if not cond.check(hallconf.HALL_GAMEID, userId, clientId, pktimestamp.getCurrentTimestamp()):
            return False

    return True


def _reloadConf():
    global fuzhou_config,fuzhou_conditions
    conf = hallconf.getHallFuZhouBenefits()
    if conf:
        fuzhou_config = conf
        fuzhou_conditions = hallentity.hallusercond.UserConditionRegister.decodeList(conf['conditions'])
    else:
        ftlog.warn("hallbenefits_fuzhou config is None, please check")

def _onConfChanged(event):
    if _inited and event.isChanged('game:9999:fuzhou_benefits:0'):
        ftlog.debug('hallbenefits_fuzhou._onConfChanged')
        _reloadConf()


def _initialize():
    ftlog.debug('hallbenefits_fuzhou initialize begin')
    global _inited
    if not _inited:
        _inited = True
        _reloadConf()
        pkeventbus.globalEventBus.subscribe(EventConfigure, _onConfChanged)
    ftlog.debug('hallbenefits_fuzhou initialize end')