# -*- coding=utf-8
import freetime.util.log as ftlog
from hall.entity import hallconf, hallitem, hallpopwnd
from poker.util import strutil
import poker.util.timestamp as pktimestamp
from hall.entity.hallpopwnd import TodoTasksGeneratorRegister, makeTodoTaskByTemplate
from hall.entity.todotask import TodoTaskHelper, TodoTaskNsloginReward



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
        #获取玩家会员信息
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
        #3.76的处理流程
        
        startFlow = hallconf.getStartFlowConf()
        gen = TodoTasksGeneratorRegister.decodeFromDict(startFlow)
        todotasks = gen.makeTodoTasks(gameId, userId, clientId, timestamp, isDayFirstLogin=isdayfirst)
        ftlog.info('makeTodoTaskNsloginReward todotasks =', todotasks,
                   'userId =', userId,
                   'gameId =', gameId,
                   'clientId =', clientId,
                   'remainDays =', remainDays,
                   'isdayfirst =', isdayfirst,
                   'memberBonus =', memberBonus)
        if todotasks:
            ret.extend(todotasks)
        else:
            tempPay = makeTodoTaskByTemplate(gameId, userId, clientId, 'recommendBuy')
            if tempPay:
                ret.append(tempPay)
            else:
                tempObj = makeTodoTaskByTemplate(gameId, userId, clientId, 'activity')
                if tempObj:
                    ret.append(tempObj)
    if ftlog.is_debug():
        ftlog.debug('hallpopwnd.makeTodoTaskNsloginReward gameId=', gameId,
                    'userId=', userId,
                    'clientId=', clientId,
                    'ret=', ret) 
    return ret

hallpopwnd.makeTodoTaskNsloginReward = makeTodoTaskNsloginReward
