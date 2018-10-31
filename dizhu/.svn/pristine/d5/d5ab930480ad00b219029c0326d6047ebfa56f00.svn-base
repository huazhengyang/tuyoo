# -*- coding=utf-8 -*-
'''
Created on 2015年7月7日

@author: zhaojiangang
'''
from __future__ import division

import datetime
import json
import math

from dizhu.activities.toolbox import Redis, UserInfo, Tool
from dizhu.entity import skillscore, dizhuconf, treasurebox, dizhuaccount, \
    dizhutask
from dizhu.entity.dizhuconf import DIZHU_GAMEID
from dizhu.entity.dizhuversion import SessionDizhuVersion
from dizhucomm.entity.events import UseTableEmoticonEvent
from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from hall.entity import halluser, hallvip, hallbenefits, hallflipcardluck, \
    datachangenotify, hallpopwnd, hallitem
from hall.entity.hallpopwnd import makeTodoTaskLuckBuy, makeTodoTaskLessbuyChip, \
    makeTodoTaskByTemplate
from hall.entity.hallusercond import UserConditionRegisterDay
from hall.entity.todotask import TodoTaskHelper, TodoTaskGoldRain, \
    TodotaskFlipCardNew
from poker.entity.biz import bireport
from poker.entity.biz.exceptions import TYBizException
from poker.entity.configure import gdata
from poker.entity.dao import gamedata, userchip, daoconst, userdata, sessiondata, \
    userdata as pkuserdata
from poker.entity.events.tyevent import TableStandUpEvent
from poker.protocol import router
from poker.protocol.rpccore import markRpcCall
from poker.util import strutil, timestamp as pktimestamp
from poker.entity.game.tables.table_player import TYPlayer

def _getUserTableTasks(userId, timestamp):
    dizhutask.tableTaskSystem.loadTaskModel(userId, timestamp)

def _getLastTableChip(userId, isSupportBuyin):
    if isSupportBuyin:
        return gamedata.getGameAttrInt(userId, DIZHU_GAMEID, 'last_table_chip') or -1
    else:
        return -1
 
def _resetLastTableChip(userId, isSupportBuyin):
    if isSupportBuyin :
        gamedata.setGameAttr(userId, DIZHU_GAMEID, 'last_table_chip', -1)

def _cleanUpTableChipOnStandUp(userId, roomId, tableId, clientId):
    '''
    TODO 桌子在初始化时, 若发现遗留的金币, 需要进行清理, 此时rpc系统还未建立, 暂时直接调用
    如何处理各个模块的初始化过程还是个问题
    '''
    userchip.moveAllTableChipToChip(userId, DIZHU_GAMEID,
                                    'TABLE_STANDUP_TCHIP_TO_CHIP',
                                    roomId, clientId, tableId)
    userchip.delTableChips(userId, [tableId])

@markRpcCall(groupName="userId", lockName="userId", syncCall=1)
def cleanUpTableChipOnStandUp(userId, roomId, tableId, clientId):
    _cleanUpTableChipOnStandUp(userId, roomId, tableId, clientId)
    datachangenotify.sendDataChangeNotify(DIZHU_GAMEID, userId, 'udata')
    return 1

@markRpcCall(groupName="userId", lockName="userId", syncCall=1)
def setUpTableChipOnSitDown(userId, roomId, tableId, seatId, clientId, isSupportBuyin, continuityBuyin, roomBuyInChip, roomMinCoin):
    ftlog.debug('setUpTableChipOnSitDown ', userId, roomId, tableId, seatId, clientId, isSupportBuyin, continuityBuyin, roomBuyInChip)
    if continuityBuyin == 1:
        # 连续带入判断
        last_table_chip = _getLastTableChip(userId, isSupportBuyin)
        ftlog.debug('setUpTableChipOnSitDown last_table_chip=', last_table_chip)
        if last_table_chip >= roomBuyInChip:
            buyin_chip = _moveChipToTablechipBuyUser(userId, roomId, tableId, seatId, isSupportBuyin, last_table_chip, roomMinCoin, clientId)
        else:
            buyin_chip = _moveChipToTablechipBuyUser(userId, roomId, tableId, seatId, isSupportBuyin, roomBuyInChip, roomMinCoin, clientId)
    else:
        buyin_chip = _moveChipToTablechipBuyUser(userId, roomId, tableId, seatId, isSupportBuyin, roomBuyInChip, roomMinCoin, clientId)
    _resetLastTableChip(userId, isSupportBuyin)
    datachangenotify.sendDataChangeNotify(DIZHU_GAMEID, userId, 'udata')
    return buyin_chip

def _moveChipToTablechipBuyUser(userId, roomId, tableId, seatId, isSupportBuyin, buyinChip, minCoin, clientId):
    ftlog.debug('_moveChipToTablechipBuyUser->userId, roomId, tableId, seatId, isSupportBuyin, buyinChip=',
                userId, roomId, tableId, seatId, isSupportBuyin, buyinChip, clientId)
    if isSupportBuyin :  # 坐下操作, 进行带入金币操作
        isbuyinall = dizhuconf.getIsTableBuyInAll(clientId)
        ftlog.debug('_moveChipToTablechipBuyUser->isbuyinall=', isbuyinall)
        if isbuyinall or buyinChip <= 0 :
            chip, user_chip_final, delta_chip = userchip.moveAllChipToTableChip(userId, DIZHU_GAMEID,
                                                                                'TABLE_SITDOWN_SET_TCHIP',
                                                                                roomId, clientId, tableId) 
        else:
            minchip = min(minCoin, buyinChip)
            maxchip = max(minCoin, buyinChip)
            chip, user_chip_final, delta_chip = userchip.setTableChipToRange(userId, DIZHU_GAMEID,
                                                                             minchip, maxchip,
                                                                             'TABLE_SITDOWN_SET_TCHIP',
                                                                             roomId, clientId, tableId)
        ftlog.debug('_moveChipToTablechipBuyUser->userId, roomId, tableId, chip, user_chip_final, delta_chip=',
                    userId, roomId, tableId, chip, user_chip_final, delta_chip)
    else :
        chip = userchip.getChip(userId)
    return chip

@markRpcCall(groupName="userId", lockName="userId", syncCall=1)
def incUserCharm(userId, charm):
    return userdata.incrCharm(userId, charm)

@markRpcCall(groupName="userId", lockName="userId", syncCall=1)
def doTableSmiliesFrom(roomId, bigRoomId, tableId, userId,
                       smilie, minchip, price, self_charm, clientId):
    eventId = 'EMOTICON_' + smilie.upper() + '_CONSUME'
    trueDelta, final = userchip.incrChipLimit(userId, DIZHU_GAMEID, -price, price + minchip, -1,
                                               daoconst.CHIP_NOT_ENOUGH_OP_MODE_NONE,
                                               eventId, roomId, clientId)
    # 发送通知
    if abs(trueDelta) > 0:
        datachangenotify.sendDataChangeNotify(DIZHU_GAMEID, userId, 'chip')

    if trueDelta != -price:
        return 0, trueDelta, final
    bireport.gcoin('out.chip.emoticon', DIZHU_GAMEID, price)

    # 魅力值
    userdata.incrCharm(userId, self_charm)
    bireport.gcoin('out.smilies.' + smilie + '.' + str(bigRoomId), DIZHU_GAMEID, price)
    
    from dizhu.game import TGDizhu
    TGDizhu.getEventBus().publishEvent(UseTableEmoticonEvent(DIZHU_GAMEID, userId, roomId, tableId, smilie, price))
    return 1, trueDelta, final

@markRpcCall(groupName="userId", lockName="userId", syncCall=1)
def doTableSmiliesFrom_v3_775(roomId, bigRoomId, tableId, userId,
                       smilie, minchip, price, self_charm, clientId, wcount=1):
    ftlog.debug('doTableSmiliesFrom_v3_775:1',
                'userId=', userId,
                'price=', price,
                'smilie=', smilie,
                'wcount=', wcount)
    eventId = 'EMOTICON_' + smilie.upper() + '_CONSUME'
    trueDelta, final = userchip.incrChipLimit(userId, DIZHU_GAMEID, -price * wcount, -1, -1,
                                               daoconst.CHIP_NOT_ENOUGH_OP_MODE_CLEAR_ZERO,
                                               eventId, roomId, clientId)
    # 真实的发送个数，金币不足也至少发送一次
    rcostchip = abs(trueDelta)
    rcount = 1
    if price > 0:
        rcount = max(1, int(math.ceil(rcostchip/price)));
        
    bireport.gcoin('out.chip.emoticon', DIZHU_GAMEID, rcostchip)
    ftlog.debug('doTableSmiliesFrom_v3_775:2',
                'userId=', userId,
                'rcostchip=', rcostchip,
                'rcount=', rcount,
                'final=', final
                )
    
    # 发送通知
    if rcostchip > 0:
        datachangenotify.sendDataChangeNotify(DIZHU_GAMEID, userId, 'chip')

    # 魅力值
    userdata.incrCharm(userId, self_charm * rcount)
    bireport.gcoin('out.smilies.' + smilie + '.' + str(bigRoomId), DIZHU_GAMEID, rcostchip)

    from dizhu.game import TGDizhu
    for _ in xrange(rcount):
        TGDizhu.getEventBus().publishEvent(UseTableEmoticonEvent(DIZHU_GAMEID, userId, roomId, tableId, smilie, price))
    return rcount, trueDelta, final

@markRpcCall(groupName="userId", lockName="userId", syncCall=1)
def doTableSmiliesTo(userId, other_charm, count=1):
    # 魅力值
    userdata.incrCharm(userId, other_charm * count)
    return count

@markRpcCall(groupName="userId", lockName="userId", syncCall=1)
def doTableTreasureBox(userId, bigRoomId):
    ftlog.debug('doTableTreasureBox userId=', userId)
    datas = treasurebox.doTreasureBox(userId, bigRoomId)
    ftlog.debug('doTableTreasureBox return=', datas)
    return datas

@markRpcCall(groupName="userId", lockName="userId", syncCall=1)
def doGetUserChips(userId, tableId, isSupportBuyin):
    ftlog.debug('doGetUserChips userId=', userId, 'isSupportBuyin=', isSupportBuyin)
    if isSupportBuyin:
        suchip = userchip.getTableChip(userId, DIZHU_GAMEID, tableId)
        accchip = userchip.getChip(userId)
    else:
        suchip = userchip.getChip(userId)
        accchip = suchip
    ftlog.debug('doGetUserChips userId=', suchip, accchip)
    return suchip, accchip

@markRpcCall(groupName="userId", lockName="userId", syncCall=1)
def doInitTableUserData(userId, bigRoomId, tableId, isNextBuyin, buyinchip, isMatch=False):
    clientId = sessiondata.getClientId(userId)
    isSupportBuyin = dizhuconf.isSupportBuyin(clientId)
    exp, suaddress, susex, suname, sucoin, charm = userdata.getAttrs(userId, ['exp', 'address', 'sex', 'name', 'coin', 'charm'])
    sugold, slevel, swinrate, winchips, starid, winstreak = gamedata.getGameAttrs(userId, DIZHU_GAMEID, ['gold', 'level', 'winrate', 'winchips', 'starid', 'winstreak'])
    ftlog.debug('isSupportBuyin=', isSupportBuyin, 'userdata->', suaddress, susex, suname, sucoin, exp, charm)
    ftlog.debug('gamedata->', sugold, slevel, swinrate, winchips, starid)

    swinrate = strutil.loads(swinrate, ignoreException=True, execptionValue={'pt':0, 'wt':0})
    suchip = userchip.getChip(userId)
    buyin_tip = ''
    if not isSupportBuyin or isMatch:
        buyinMark = 0
        buyin_chip = suchip
    else:
        buyinMark = 1
        buyin_chip = userchip.getTableChip(userId, DIZHU_GAMEID, tableId)
        buyinconf = dizhuconf.getBuyInConf()
        if buyin_chip == buyinchip:
            if isNextBuyin :
                buyin_tip = buyinconf.get('tip_auto', '')
            else:
                buyin_tip = buyinconf.get('tip', '').format(BUYIN_CHIP=buyinchip)
        else:
            if suchip <= 0 :
                if isNextBuyin :
                    buyin_tip = buyinconf.get('tip_auto_all_next', '')
                else:
                    buyin_tip = buyinconf.get('tip_auto_all', '')
        suchip = buyin_chip
                
    tbplaytimes, tbplaycount = treasurebox.getTreasureBoxState(userId, bigRoomId)
    try:
        if TYPlayer.isRobot(userId):
            supic, isBeauty = '', False
        else:
            supic, isBeauty = halluser.getUserHeadUrl(userId, clientId)
    except:
        supic, isBeauty = '', False
        
    slevel = _recoverUserAttr(slevel, int, 0)
    datas = {}
    datas['uid'] = userId
    datas['address'] = _recoverUserAttr(suaddress, unicode, '')
    datas['sex'] = _recoverUserAttr(susex, int, 0)
    datas['name'] = _recoverUserAttr(suname, unicode, '')
    datas['coin'] = _recoverUserAttr(sucoin, int, 0)
    datas['headUrl'] = ''
    datas['purl'] = supic
    datas['isBeauty'] = isBeauty
    datas['chip'] = suchip
    datas['buyinMark'] = buyinMark
    datas['buyinChip'] = buyin_chip
    datas['buyinTip'] = buyin_tip
    datas['exp'] = _recoverUserAttr(exp, int, 0)
    datas['gold'] = _recoverUserAttr(sugold, int, 0)
    datas['vipzuan'] = []
    datas['tbc'] = tbplaycount
    datas['tbt'] = tbplaytimes
    datas['level'] = slevel
    datas['wins'] = swinrate.get('wt', 0)
    datas['plays'] = swinrate.get('pt', 0)
    datas['winchips'] = _recoverUserAttr(winchips, int, 0)
    datas['nextexp'] = dizhuaccount.getGameUserNextExp(slevel)
    datas['title'] = dizhuaccount.getGameUserTitle(slevel)
    datas['medals'] = _buildUserMedals()
    datas['skillScoreInfo'] = skillscore.score_info(userId)
    datas['charm'] = 0 if charm == None else _recoverUserAttr(charm, int, 0)
    datas['vipInfo'] = hallvip.userVipSystem.getVipInfo(userId)
    datas['starid'] = 0 if starid == None else _recoverUserAttr(starid, int, 0)
    datas['winstreak'] = 0 if winstreak == None else _recoverUserAttr(winstreak, int, 0)
    datas['gameClientVer'] = SessionDizhuVersion.getVersionNumber(userId)
    # TODO 查询用户增值位
    datas['wearedItems'] = []
    userBag = hallitem.itemSystem.loadUserAssets(userId).getUserBag()
    timestamp = pktimestamp.getCurrentTimestamp()
    memberCardItem = userBag.getItemByKindId(hallitem.ITEM_MEMBER_NEW_KIND_ID)
    datas['memberExpires'] = memberCardItem.expiresTime if memberCardItem else 0
    item = userBag.getItemByKindId(hallitem.ITEM_CARD_NOTE_KIND_ID)
    cardNoteCount = 0
    if item and not item.isDied(timestamp):
        cardNoteCount = max(1, item.balance(timestamp))
    ftlog.debug('DizhuPlayer->userId=', userId, 'isSupportBuyin=', isSupportBuyin,
                'cardNoteCount=', cardNoteCount, 'clientId=', clientId, 'data=', datas)
    return isSupportBuyin, cardNoteCount, clientId, datas


@markRpcCall(groupName="userId", lockName="userId", syncCall=1)
def doUpdateTableUserData(userId, bigRoomId, tableId, isNextBuyin, buyinchip):
    tbplaytimes, tbplaycount = treasurebox.getTreasureBoxState(userId, bigRoomId)
    datas = {}
    datas['tbc'] = tbplaycount
    datas['tbt'] = tbplaytimes
    return datas

def processLoseOutRoom(gameId, userId, clientId, roomId):
    # 处理江湖救急流程
    if ftlog.is_debug():
        ftlog.debug('table_remote.processLoseOutRoom gameId=', gameId,
                    'userId=', userId,
                    'clientId=', clientId,
                    'roomId=', roomId)
    title = ''
    desc = ''
    tips = ''
    vipBenefits = 0
    try:
        consumeCount, _finalCount, vipBenefits = hallvip.userVipSystem.gainAssistance(gameId, userId)
        if ftlog.is_debug():
            ftlog.debug('table_remote.processLoseOutRoom gameId=', gameId,
                        'userId=', userId,
                        'roomId=', roomId,
                        'consumeCount=', consumeCount,
                        'vipBenefits=', vipBenefits)
        if consumeCount > 0:
            title = hallflipcardluck.getString('vipBenefits.title', 'VIP专属江湖救急')
            desc = hallflipcardluck.getString('vipBenefits.desc', '金币不够啦，送您一次翻奖机会，快来试试手气吧')
            tips = hallflipcardluck.getString('vipBenefits.title', '再送您${vipBenefits}江湖救急')
            tips = strutil.replaceParams(tips, {'vipBenefits':str(vipBenefits)})
    except TYBizException:
        pass
    except:
        ftlog.error('table_remote.processLoseOutRoom gameId=', gameId,
                    'userId=', userId,
                    'roomId=', roomId)
    todotasks = []
    if vipBenefits > 0:
        goldRainDesc = strutil.replaceParams(hallvip.vipSystem.getGotGiftDesc(), {'content':'%s金币' % (vipBenefits)})
        todotasks.append(TodoTaskGoldRain(goldRainDesc))
        datachangenotify.sendDataChangeNotify(gameId, userId, 'chip')
    else:
        desc = hallflipcardluck.getString('benefits.desc', '金币不够啦，送您一次翻奖机会，快来试试手气吧')
        if ftlog.is_debug():
            ftlog.debug('table_remote.processLoseOutRoom gameId=', gameId,
                        'userId=', userId,
                        'roomId=', roomId,
                        'benefits=', desc)
    todotasks.append(TodotaskFlipCardNew(gameId, roomId, title, desc, tips))
    return TodoTaskHelper.sendTodoTask(gameId, userId, todotasks)



def processLoseOutRoomV3_77(gameId, userId, clientId, roomId, showMemberTry=False):
    if ftlog.is_debug():
        ftlog.debug('table_remote.processLoseOutRoomV3_77 gameId=', gameId,
                    'userId=', userId,
                    'clientId=', clientId,
                    'roomId=', roomId)

    timestamp = pktimestamp.getCurrentTimestamp()
    remainDays, _memberBonus = hallitem.getMemberInfo(userId, timestamp)

    memberTry = None
    luckBuyOrLessBuyChip = makeTodoTaskLuckBuy(gameId, userId, clientId, roomId)
    if not luckBuyOrLessBuyChip:
        luckBuyOrLessBuyChip = makeTodoTaskLessbuyChip(gameId, userId, clientId, roomId)

    # 冲过值的或者新用户不弹试用会员
    isNewUser = UserConditionRegisterDay(0, 0).check(gameId, userId, clientId, timestamp)
    if ftlog.is_debug():
        ftlog.debug('table_remote.processLoseOutRoomV3_77 gameId=', gameId,
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

    datachangenotify.sendDataChangeNotify(gameId, userId, 'chip')
    todotask = memberTry or luckBuyOrLessBuyChip
    if todotask:
        TodoTaskHelper.sendTodoTask(gameId, userId, todotask)

    # 发送救济金气泡提示
    sendUserBenefitsIfNeed(gameId, userId, roomId, timestamp)
    # benefitsSend, userBenefits = hallbenefits.benefitsSystem.sendBenefits(gameId, userId, timestamp)
    # if benefitsSend:
    #     message = [
    #         [{"type":"ttf","font":"ArialMT","text":"送您%s金币救急，"%(userBenefits.sendChip),"color":16777215}],
    #         [{"type":"ttf","font":"ArialMT","text":"继续努力吧！","color":16777215}],
    #         [{"type":"ttf","font":"ArialMT","text":"(今天第","color":16777215},
    #          {"type":"ttf","font":"ArialMT","text":userBenefits.times,"color":65280},
    #          {"type":"ttf","font":"ArialMT","text":"次，共%s次)"%(userBenefits.totalMaxTimes),"color":16777215}]
    #     ]
    #     mo = MsgPack()
    #     mo.setCmd('table_call')
    #     mo.setResult('gameId', gameId)
    #     mo.setResult('userId', userId)
    #     mo.setResult('action', 'benefits')
    #     mo.setResult('message', json.dumps(message))
    #     router.sendToUser(mo, userId)
    return None

def sendUserVipBenefits(userId, roomId, minRoomLevel, sendCount, chip):
    if minRoomLevel < 1 or sendCount <= 0:
        return False

    ## room level limit
    bigroomId = gdata.getBigRoomId(roomId)
    roomconf = gdata.getRoomConfigure(bigroomId)
    if not roomconf:
        return False
    roomlevel = roomconf.get('roomLevel', 1)
    if roomlevel < minRoomLevel:
        ftlog.debug('sendUserVipBenefits: roomlevel',
                    'userId=', userId,
                    'roomlevel=', roomlevel,
                    'minRoomLevel=', minRoomLevel)
        return False

    ## send number limit
    rediskey = 'vip.benefits'
    data = Redis.readJson(userId, rediskey)
    timestamp = data.get('timestamp', 0)
    counter = data.get('counter', 0)

    now = datetime.datetime.now()
    last = datetime.datetime.fromtimestamp(timestamp)
    if last.year != now.year or last.month != now.month or last.day != now.day:
        counter = 0

    if counter >= sendCount:
        ftlog.debug('sendUserVipBenefits: sendCount',
            'userId=', userId,
            'sendCount=', sendCount,
            'counter=', counter)
        return False

    data['counter'] = counter + 1
    data['timestamp'] = Tool.datetimeToTimestamp(now)

    Redis.writeJson(userId, rediskey, data)
    UserInfo.incrChip(userId, 6, chip, 'BENEFITS_VIP_SEND')

    ftlog.debug('sendUserVipBenefits:',
                'userId=', userId,
                'counter=', data['counter'],
                'chip=', chip)
    return True

def sendUserBenefitsIfNeed(gameId, userId, roomId, timestamp):
    benefitsSend, userBenefits = hallbenefits.benefitsSystem.sendBenefits(gameId, userId, timestamp)
    ftlog.debug('sendUserBenefitsIfNeed',
                'userId=', userId,
                'benefitsSend=', benefitsSend)
    if benefitsSend:
        ## vip奖励映射表
        vipmap = dizhuconf.getPublic().get('VipBenefits', {}).get('VipMap', {})
        ## 玩家vip等级
        info = hallvip.userVipSystem.getUserVip(userId)
        uservip = info.vipLevel.level if info else 0

        vipmsg = None
        vipmapitem = vipmap.get(str(uservip))
        ftlog.debug('sendUserBenefitsIfNeed: vipmapitem',
                    'userId=', userId,
                    'vipmapitem=', vipmapitem)
        if vipmapitem:
            chip = vipmapitem.get('chip')
            sendCount = vipmapitem.get('sendCount')
            minRoomLevel = vipmapitem.get('minRoomLevel')
            if chip and chip > 0 and sendCount and minRoomLevel and sendUserVipBenefits(userId, roomId, minRoomLevel, sendCount, chip):
                vipmsg = [
                    [{'type':'ttf', 'font':'ArialMT', 'text':'VIP' + str(uservip), 'color':0x482904},
                     {'type':'ttf', 'font':'ArialMT', 'text':'特权，附', 'color':0x482904},
                     {'type':'ttf', 'font':'ArialMT', 'text':'+' + str(chip), 'color':0xFF0000},
                     {'type':'ttf', 'font':'ArialMT', 'text':'金！', 'color':0x482904}]
                ]

        message = [
            [{'type':'ttf','font':'ArialMT','text':'送您%s金币救急，'%(userBenefits.sendChip),'color':0x482904}],
            [{'type':'ttf','font':'ArialMT','text':'继续努力吧！','color':0x482904}],
            [{'type':'ttf','font':'ArialMT','text':'(今天第','color':0x482904},
             {'type':'ttf','font':'ArialMT','text':userBenefits.times,'color':0x25E10B},
             {'type':'ttf','font':'ArialMT','text':'次，共%s次)'%(userBenefits.totalMaxTimes),'color':0x482904}]
        ]

        ftlog.debug('sendUserBenefitsIfNeed:',
                    'userId=', userId,
                    'uservip=', uservip)

        mo = MsgPack()
        mo.setCmd('table_call')
        mo.setResult('gameId', gameId)
        mo.setResult('userId', userId)
        mo.setResult('action', 'benefits')
        mo.setResult('benefits', 1) # 有救济金了
        mo.setResult('message', json.dumps(message))
        if vipmsg:
            mo.setResult('vipmsg', json.dumps(vipmsg))
        router.sendToUser(mo, userId)
    else:
        ftlog.debug('sendUserBenefitsIfNeed: no benefitsSend',
                    'userId=', userId)
        mo = MsgPack()
        mo.setCmd('table_call')
        mo.setResult('gameId', gameId)
        mo.setResult('userId', userId)
        mo.setResult('action', 'benefits')
        mo.setResult('benefits', 0) # 没有救济金了
        router.sendToUser(mo, userId)
        


@markRpcCall(groupName="userId", lockName="userId", syncCall=1)
def doUserStandUp(userId, roomId, tableId, clientId, reason):
    _, clientVer, _ = strutil.parseClientId(clientId)
    ftlog.debug('table_remote.doUserStandUp userId=', userId,
                'roomId=', roomId,
                'tableId=', tableId,
                'clientId=', clientId,
                'reason=', reason,
                'clientVer=', clientVer)
    if reason not in (TableStandUpEvent.REASON_GAME_OVER,):
        return 0
    
    chipCount = userchip.getChip(userId)
    roomConf = gdata.getRoomConfigure(roomId) or {'minCoin':0, 'maxCoin':-1}
    if chipCount < roomConf['minCoin']:
        reason = TableStandUpEvent.REASON_CHIP_NOT_ENOUGHT
        if clientVer >= 3.77: # 新版救济金弹气泡支持
            processLoseOutRoomV3_77(DIZHU_GAMEID, userId, clientId, roomId, showMemberTry=False)
        elif clientVer >= 3.7:
            hallpopwnd.processLoseOutRoomV3_7(DIZHU_GAMEID, userId, clientId, roomId, showMemberTry=False)
        elif clientVer == 3.502:
            processLoseOutRoom(DIZHU_GAMEID, userId, clientId, roomId)
        elif clientVer >= 3.0:
            timestamp = pktimestamp.getCurrentTimestamp()
            benefitsSend, userBenefits = hallbenefits.benefitsSystem.sendBenefits(DIZHU_GAMEID, userId, timestamp)
            ftlog.debug('benefitsSend, userBenefits =', benefitsSend, userBenefits)
            zhuanyun = hallpopwnd.makeTodoTaskZhuanyun(DIZHU_GAMEID, userId, clientId, benefitsSend, userBenefits, roomId)
            if zhuanyun  :
                TodoTaskHelper.sendTodoTask(DIZHU_GAMEID, userId, zhuanyun)
            else:
                ttask = TodoTaskHelper.makeBenefitsTodoTask(DIZHU_GAMEID, userId, clientId, benefitsSend, userBenefits)
                if ttask :
                    TodoTaskHelper.sendTodoTask(DIZHU_GAMEID, userId, ttask)
            datachangenotify.sendDataChangeNotify(DIZHU_GAMEID, userId, 'chip')
        else:
            benefitsSend, userBenefits = hallbenefits.benefitsSystem.sendBenefits(DIZHU_GAMEID, userId, pktimestamp.getCurrentTimestamp())
            ftlog.debug('benefitsSend, userBenefits =', benefitsSend, userBenefits)
    elif (roomConf['maxCoin'] != -1 and chipCount > roomConf['maxCoin']):
        pass
        # reason = TableStandUpEvent.REASON_CHIP_TOO_MUCH
        # from dizhu.gametable.quick_start import DizhuQuickStartV4_0
        # DizhuQuickStartV4_0._sendTodoTaskJumpHighRoom(userId, roomConf['playMode'], clientId)
    return 1


def _recoverUserAttr(value, recoverType, defaultValue):
    '''
    校验检查用户的基本信息内容, 返回检查变化后的值
    '''
    try:
        ftlog.debug('recover->', value, recoverType, defaultValue)
        value = recoverType(value)
    except:
        ftlog.info('ERROR !! _recoverUserAttr', value, recoverType, defaultValue)
        value = recoverType(defaultValue)
    return value


def _buildUserMedals():
    medals = []
#         wearMedalId = TaskSystem.getInstance().getWearMedalId(userId)
#         userTasks = TaskSystem.getInstance().getUserTasks(userId)
#         for task in userTasks.medalTasks.values():
#             if task.total > 0:
#                 medals.append(_buildUserMedal(task, wearMedalId)) 
    return medals


 
