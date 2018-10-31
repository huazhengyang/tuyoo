# -*- coding=utf-8 -*-
'''
Created on 2015年7月7日

@author: zhaojiangang
'''

from dizhu.entity import skillscore, dizhuconf, treasurebox, dizhuaccount, \
    dizhutask
from dizhu.entity.dizhuconf import DIZHU_GAMEID
from dizhu.entity.skillscore import SkillScore
from dizhu.gamecards import cardcenter
from dizhucomm.entity.events import Winlose, UserTableWinloseEvent, \
    UserLevelGrowEvent, UserTablePlayEvent
from dizhu.servers.util.task_handler import TableTaskHelper
import freetime.util.log as ftlog
from hall.entity import hallranking, hallstore, sdkclient
from hall.entity.todotask import TodoTaskHelper
from hall.game import TGHall
from poker.entity.biz import bireport
from poker.entity.configure import gdata
from poker.entity.dao import gamedata, userchip, daoconst, userdata, daobase, \
    sessiondata
from poker.entity.events.tyevent import GameOverEvent
from poker.protocol.rpccore import markRpcCall
from poker.util import strutil, timestamp as pktimestamp, city_locator
from poker.entity.game.tables.table_player import TYPlayer


def doTableGameStartGT(roomId, tableId, roundId, dizhuUserId, baseCardType, roomMutil, basebet, basemulti, userIds):
    # 触发游戏开始的事件, 在此事件监听中处理用户的winrate以及其他任务或属性的调整和设定
    # 更新宝箱的状态
    tbinfos = {}
    datas = {'tbinfos':tbinfos}
    for userId in userIds:
        if TYPlayer.isRobot(userId):
            continue
        
        try:
            tbinfo = _doTableGameStartUT1(userId, roomId, tableId, dizhuUserId, baseCardType, roomMutil, basebet, basemulti)
            tbinfos.update(tbinfo)
        except:
            ftlog.error('table_winlose.doTableGameStartGT userId=', userId,
                        'roomId=', roomId,
                        'tableId=', tableId)
    return datas

@markRpcCall(groupName="", lockName="", syncCall=1)
def _doTableGameStartUT1(userId, roomId, tableId, dizhuUserId, baseCardType, roomMutil, basebet, basemulti):
    # 触发游戏开始的事件, 在此事件监听中处理用户的winrate以及其他任务或属性的调整和设定
    # 更新宝箱的状态
    bigRoomId = gdata.roomIdDefineMap()[roomId].bigRoomId
    tbinfos = treasurebox.updateTreasureBoxStart([userId], bigRoomId)
    # 更新每个人的winrate
    _checkSetMedal(userId, roomMutil, basebet, basemulti, True, 0)
    # 触发每个人的游戏开始事件
    from dizhu.game import TGDizhu
    TGDizhu.getEventBus().publishEvent(UserTablePlayEvent(DIZHU_GAMEID, userId,
                                                     roomId, tableId,
                                                     baseCardType,
                                                     dizhuUserId))
    return tbinfos


def doTableWinLoseGT(roomId, tableId, roundId, winSeatId, gamebase):
    ftlog.debug('doTableWinLoseGT ->', roomId, tableId, winSeatId, roundId)
    runConfig = gamebase.table.runConfig
    state = gamebase.table.status
    seats = gamebase.table.seats
    players = gamebase.table.players

    bigRoomId = gdata.roomIdDefineMap()[roomId].bigRoomId
    tootle_seat = len(seats)  # 座位的个数
    dizhuSeatId = state.diZhu  # 地主的座位ID
    winuserid = seats[winSeatId - 1].userId  # 出最后一手牌的赢的玩家的ID
    winUserIds = [winuserid]  # 所有赢的玩家的ID集合
    dizhuwin = 0  # 是否是地主赢
    winslam = 0  # 是否大满贯
    # 抢地主倍数
    basewinchip = state.callGrade * runConfig.tableMulti
    # 炸弹倍数
    basewinchip *= pow(2, state.bomb)
    if winSeatId != dizhuSeatId :
        if seats[dizhuSeatId - 1].outCardCount == 1:
            state.chuntian = 2
        dizhuwin = 0
        for ss in xrange(tootle_seat):
            if (ss + 1) != winSeatId and (ss + 1) != dizhuSeatId:
                winUserIds.append(seats[ss].userId)
    else:
        dizhuwin = 1
        chuntian = True
        for idx in xrange(tootle_seat):
            if (idx + 1) != dizhuSeatId: 
                if seats[idx].outCardCount > 0:
                    chuntian = False
                    break
        if chuntian: state.chuntian = 2
        
    ftlog.debug('doTableWinLose dizhuwin=', dizhuwin, 'winuserid=', winuserid, 'winUserIds=', winUserIds)
    
    # 让牌倍数(只有二斗有)
    basewinchip *= state.rangpaiMultiWinLose        
    # 春天倍数
    basewinchip *= state.chuntian
    # 底牌倍数
    basewinchip *= state.baseCardMulti 
    # 明牌倍数
    basewinchip *= state.show
    # 翻倍计算
    windoubles = int(basewinchip / runConfig.tableMulti)
    if windoubles >= runConfig.gslam:
        winslam = 1
    basem = windoubles / state.show
    # 所有玩家的ID列表
    allUserIds = []
    for seat in seats:
        allUserIds.append(seat.userId)

    # 大于5个炸弹局数记录
    if state.bomb >= 5:
        ftlog.info('BombCountRecord: playmode =', runConfig.playMode, 'count = ', state.bomb, 'tableId=', tableId)

    sfeealls = [DIZHU_GAMEID, roomId, tableId, [], []]
    winStreak = [{}] * tootle_seat
    lucky_args = [{}] * tootle_seat
    skill_score_infos = [{}] * tootle_seat
    room_fee = [0] * tootle_seat  # 每个人的房间服务费
    coin_after_sfee = [0] * tootle_seat
    seat_coin = [0] * tootle_seat
    seat_delta = [0] * tootle_seat
    chou_cheng = [0] * tootle_seat
    detalChip = [0] * tootle_seat  # 统计用户总金币变化
    addcoupons = [0] * tootle_seat
    findChips = [0] * tootle_seat
    finalAccChips = [0] * tootle_seat
    robot_card_count = [0] * tootle_seat  # 每个座位
    seat_exps = [0] * tootle_seat
    seatDeltaAll = 0
    cardNoteChip = [0] * tootle_seat  # 每个座位的记牌器金币
    seat_table_tasks = [0] * tootle_seat
    tb_infos = [0] * tootle_seat
    # 服务费抽成调整配置, 扣除玩家的房间服务费
    roomFeeConf = dizhuconf.getRoomFeeConf()
    basic_rate = roomFeeConf.get('basic', 1)
    winner_rate = roomFeeConf.get('winner_chip', 0)
    highMulti = roomFeeConf.get('high_multi', 32)
    feeMulti = roomFeeConf.get('fee_multi', 2.0)
    for x in xrange(tootle_seat):
        xp = players[x]
        userId = allUserIds[x]
        sfeealls[3].append(userId)
        sfee = runConfig.roomFee
        isdizhu = 0
        if windoubles >= highMulti:
            if dizhuwin == 1:
                if x == dizhuSeatId - 1:
                    isdizhu = 1
                    sfee *= feeMulti
                    sfee = int(sfee)
                    sfeealls[3].append(feeMulti)
                else:
                    sfeealls[3].append(1.0)
            else:
                if x != dizhuSeatId - 1:
                    isdizhu = 1
                    sfee *= feeMulti
                    sfee = int(sfee)
                    sfeealls[3].append(feeMulti)
                else:
                    sfeealls[3].append(1.0)
        else:
            sfeealls[3].append(1.0)
        sfeealls[3].append(sfee)
        
        sfee = abs(int(sfee * basic_rate))  # 服务费调整
        room_fee[x] = sfee
        
        cardNoteChip[x] = runConfig.cardNoteChip if xp.inningCardNote > 0 else 0
        trueDelta, ccoin, winStreak_, lucky_args_, skill_score_infos_ = _doTableWinLoseUT1(
                                                userId, bigRoomId, roomId, tableId, sfee, cardNoteChip[x], xp.isSupportBuyin, xp.clientId,
                                                winUserIds, winslam, state.chuntian, isdizhu, windoubles) 
        detalChip[x] = detalChip[x] + trueDelta
        coin_after_sfee[x] = ccoin
        robot_card_count[x] = seats[x].robotCardCount
        winStreak[x] = winStreak_
        lucky_args[x] = lucky_args_
        skill_score_infos[x] = skill_score_infos_

    ftlog.debug('doTableWinLosechip->after room fee->allUserIds=', allUserIds)
    ftlog.debug('doTableWinLosechip->after room fee->room_fee=', room_fee)
    ftlog.debug('doTableWinLosechip->after room fee->cardNoteChip=', cardNoteChip)
    ftlog.debug('doTableWinLosechip->after room fee->detalChip=', detalChip)
    ftlog.debug('doTableWinLosechip->after room fee->coin_after_sfee=', coin_after_sfee)
    ftlog.debug('doTableWinLosechip->after room fee->robot_card_count=', robot_card_count)
    
    if dizhuwin == 1:
        dzswin = 0
        # 先算地主应该赢的钱
        dz_abswin = min(basewinchip * (tootle_seat - 1), coin_after_sfee[winSeatId - 1])
        # 算农民输的钱
        for x in xrange(tootle_seat):
            if x != winSeatId - 1:
                nmlose = min(dz_abswin / (tootle_seat - 1), coin_after_sfee[x])
                dzswin += nmlose
                seat_coin[x] = coin_after_sfee[x] - nmlose
                seat_delta[x] = nmlose * -1
        dzwincoin = int(dzswin)
        seat_coin[winSeatId - 1] = coin_after_sfee[winSeatId - 1] + dzwincoin
        seat_delta[winSeatId - 1] = dzwincoin
        
        if runConfig.sendCoupon and basem >= 64:
            winseat = seats[winSeatId - 1]
            addcoupon = winseat.couponCard[0] * 2 + winseat.couponCard[1] + winseat.couponCard[2] * 2
            if runConfig.roomFee > 220 :
                addcoupon *= (runConfig.roomFee / 220)
            addcoupons[winSeatId - 1] = abs(int(addcoupon))
    else:
        dzslose = 0
        # 地主应该输的钱
        dzlosecoin = min(coin_after_sfee[dizhuSeatId - 1], basewinchip * (tootle_seat - 1))
        for x in xrange(tootle_seat):
            if x != dizhuSeatId - 1:
                if runConfig.sendCoupon and basem >= 64:
                    winseat = seats[x]
                    addcoupon = winseat.couponCard[0] * 2 + winseat.couponCard[1] + winseat.couponCard[2] * 2
                    if runConfig.roomFee > 220 :
                        addcoupon *= (runConfig.roomFee / 220)
                    addcoupons[x] = abs(int(addcoupon))
                nmwin = min(coin_after_sfee[x], dzlosecoin / (tootle_seat - 1))
                dzslose += nmwin
                seat_coin[x] = coin_after_sfee[x] + nmwin
                seat_delta[x] = nmwin
        seat_coin[dizhuSeatId - 1] = coin_after_sfee[dizhuSeatId - 1] - dzslose
        seat_delta[dizhuSeatId - 1] = dzslose * -1
    ftlog.debug('doTableWinLosechip->after cal win->allUserIds=', allUserIds)
    ftlog.debug('doTableWinLosechip->after cal win->seat_delta=', seat_delta)
    ftlog.debug('doTableWinLosechip->after cal win->addcoupons=', addcoupons)
    ftlog.debug('doTableWinLosechip->after cal win->seat_coin=', seat_coin)

    # 计算托管处罚的调整值
    from dizhu.gameplays import punish
    pfIndex = punish.Punish.doWinLosePunish(runConfig.punishCardCount, runConfig.isMatch,
                                            seat_coin, seat_delta, robot_card_count)
    for x in xrange(tootle_seat):
        sp = players[x]
        isdizhu = 0
        if x == dizhuSeatId - 1:
            isdizhu = 1
        seatDeltaAll = seatDeltaAll + seat_delta[x]
        if seat_delta[x] > 0 :
            chou_cheng[x] = -int(seat_delta[x] * winner_rate)
            seat_coin[x] = seat_coin[x] + chou_cheng[x]
        skillLevelUp = skill_score_infos[x].get('isLevelUp', False)
        trueDelta, trueDelta_CC, finalChip, expinfo, tasks, tbplaytimes, tbplaycount = _doTableWinLoseUT2(sp.userId, bigRoomId, roomId, tableId,
                                                                 sp.isSupportBuyin, seat_delta[x],
                                                                 chou_cheng[x], sp.clientId,
                                                                 addcoupons[x],
                                                                 runConfig.isMatch, runConfig.roomMutil, runConfig.basebet, runConfig.basemulti,
                                                                 runConfig.playMode, state.topCardList, roundId, winUserIds, isdizhu, winuserid, windoubles,
                                                                 state.bomb, state.chuntian, winslam, detalChip[x], room_fee[x], skillLevelUp)
        detalChip[x] = detalChip[x] + trueDelta + trueDelta_CC
        sfeealls[4].append(sp.userId)
        sfeealls[4].append(seat_delta[x])
        findChips[x] = finalChip
        seat_exps[x] = expinfo
        seat_table_tasks[x] = tasks
        tb_infos[x] = [tbplaytimes, tbplaycount]

    bireport.tableRoomFee(DIZHU_GAMEID, sfeealls)
    bireport.tableWinLose(DIZHU_GAMEID, roomId, tableId, roundId, allUserIds)

    if seatDeltaAll < 0 :
        ftlog.info('doWinLose out.windiff < 0 !! seatDeltaAll=', seatDeltaAll)
        bireport.gcoin('out.windiff', DIZHU_GAMEID, seatDeltaAll)
    elif seatDeltaAll > 0 :
        ftlog.warn('doWinLose out.windiff > 0 !! seatDeltaAll=', seatDeltaAll)

    ftlog.debug('room_fee->', room_fee)
    ftlog.debug('coin_after_sfee->', coin_after_sfee)
    ftlog.debug('seat_coin->', seat_coin)
    ftlog.debug('seat_delta->', seat_delta)
    ftlog.debug('chou_cheng->', chou_cheng)
    ftlog.debug('detalChip->', detalChip)
    ftlog.debug('addcoupons->', addcoupons)
    ftlog.debug('findChips->', findChips)
    ftlog.debug('finalAccChips->', finalAccChips)
    ftlog.debug('tb_infos->', tb_infos)

    # 独立的陌陌排行榜处理, 此处记录发生变化的userid, 由crontab的脚本发送数据到陌陌服务器
    if dizhuconf.isUseMomoRanking() :
        nowminute = pktimestamp.formatTimeMinuteSort()
        rkey = 'momo:pushrank:' + nowminute
        daobase.executeMixCmd('SADD', rkey, *allUserIds)
        daobase.executeMixCmd('EXPIRE', rkey, 259200)  # 3天后自动过期

    return {'dizhuwin' : dizhuwin,
            'winslam' : winslam,
            'windoubles' : windoubles,
            'winStreak' : winStreak,
            'luckyItemArgs' : lucky_args,
            'skillScoreInfos' : skill_score_infos,
            'seat_delta' : seat_delta,
            'seat_coin' : seat_coin,
            'addcoupons' : addcoupons,
            'seat_exps' : seat_exps,
            'table_task' : seat_table_tasks,
            'final_acc_chips' : finalAccChips,
            'chuntian' : state.chuntian,
            'tb_infos' : tb_infos,
            'pfIndex':pfIndex
            }


@markRpcCall(groupName="", lockName="", syncCall=1)
def _doTableWinLoseUT1(userId, bigRoomId, roomId, tableId, roomFee, cardNoteChip, isSupportBuyin, clientId, winUserIds, slam, chuntian, isdizhu, windoubles):
    trueDelta, ccoin = _incrRoomFeeChip(roomId, tableId, userId, isSupportBuyin, -roomFee, clientId)
    if cardNoteChip > 0:
        trueDelta2, ccoin = _incrCardNoteChip(roomId, tableId, userId, isSupportBuyin, -cardNoteChip, clientId)
        trueDelta += trueDelta2
    # 连胜处理
    winStreak = _caleWinStreakByUser(userId, winUserIds)
    # 好运礼包
    lucky_args = _caleLuckyItemArgsByUser(userId, bigRoomId, winUserIds, winStreak, slam, chuntian, clientId)
    # 大师分处理
    skill_score_infos = _caleSkillScoreByUser(userId, winUserIds, winStreak, isdizhu, roomId, windoubles)

    return trueDelta, ccoin, winStreak, lucky_args, skill_score_infos


@markRpcCall(groupName="", lockName="", syncCall=1)
def _doTableWinLoseUT2(userId, bigRoomId, roomId, tableId, isSupportBuyin, seat_delta, chou_cheng, clientId, deltaCoupon,
                        isMatch, roomMutil, basebet, basemulti, playMode, topCardList, roundId, winUserIds, isDizhu, winuserid,
                        windoubles, bomb, chuntian, winslam, detalChipAll, room_fee, skillLevelUp):
    # 增减玩家输赢的金币
    trueDelta, trueDelta_cc, finalChip = _incrWinLoseChip(roomId, tableId, userId, isSupportBuyin, seat_delta, chou_cheng, clientId)
    if deltaCoupon > 0 :
        # 发放玩家赢得的兑换券
        _incrWinLoseCoupon(userId, deltaCoupon, roomId, clientId)
    # 更新玩家的宝箱状态
    treasurebox.updateTreasureBoxWin([userId], bigRoomId)
    tbplaytimes, tbplaycount = treasurebox.getTreasureBoxState(userId, bigRoomId)
    # 计算玩家的胜率等基本任务数据
    expinfo = []
    if not isMatch :
        expinfo = _checkSetMedal(userId, roomMutil, basebet, basemulti, False, seat_delta)
    # 广播用户结算事件
    card = cardcenter.getDizhuCard(playMode)
    topValidCard = card.validateCards(topCardList, None)
    detalChipAll = detalChipAll + trueDelta + trueDelta_cc 
    _publishWinLoseEvent(roomId, tableId, userId, roundId, winUserIds, isDizhu, winuserid,
                         seat_delta, detalChipAll, finalChip, windoubles, bomb, chuntian,
                         winslam, clientId, topValidCard, skillLevelUp)
    # 更新排名相关数据
    _calRankInfoData(userId, seat_delta, winslam, windoubles)
    tasks = _queryUserTableTasks(userId, clientId)
    return trueDelta, trueDelta_cc, finalChip, expinfo, tasks, tbplaytimes, tbplaycount


def _publishWinLoseEvent(roomId, tableId, seatUid, roundId, winUserIds, isDizhu, winuserid, seat_delta,
                         detalChipAll, findChips, windoubles, bomb, chuntian, winslam, clientId, topValidCard, skillLevelUp):
    from dizhu.game import TGDizhu
    ebus = TGDizhu.getEventBus()
    hallebus = TGHall.getEventBus()
    isWin = True if seatUid in winUserIds else False
    winlose = Winlose(winuserid, topValidCard, isWin, isDizhu, seat_delta, findChips,
                      windoubles, bomb, chuntian > 1, winslam)
    ebus.publishEvent(UserTableWinloseEvent(DIZHU_GAMEID, seatUid, roomId, tableId, winlose, skillLevelUp))
    
    isWinNum = 0
    if isWin:
        isWinNum = 1
    roomLevel = gdata.roomIdDefineMap()[roomId].configure.get('roomLevel', 1)
    ftlog.debug('hallebus push gameoverevent userId=', seatUid)
    hallebus.publishEvent(GameOverEvent(seatUid, DIZHU_GAMEID, clientId, roomId, tableId, isWinNum, roomLevel))

    finalUserChip = userchip.getChip(seatUid)
    finalTableChip = userchip.getTableChip(seatUid, DIZHU_GAMEID, tableId)
    bireport.reportGameEvent('TABLE_WIN', seatUid,
                             DIZHU_GAMEID, roomId, tableId, roundId,
                             detalChipAll, 0, 0, [], clientId,
                             finalTableChip, finalUserChip)
    return finalUserChip


def _incrWinLoseChip(roomId, tableId, userId, isSupportBuyin, seat_delta, chou_cheng, clientId):
    trueDelta = 0
    trueDelta_cc = 0
    finalChip = 0
    if isSupportBuyin : 
        trueDelta, finalChip = userchip.incrTableChip(userId, DIZHU_GAMEID, seat_delta,
                                                      daoconst.CHIP_NOT_ENOUGH_OP_MODE_CLEAR_ZERO,
                                                      'GAME_WINLOSE',
                                                      roomId, clientId, tableId)
        if chou_cheng < 0:
            trueDelta_cc, finalChip = userchip.incrTableChip(userId, DIZHU_GAMEID, chou_cheng,
                                                             daoconst.CHIP_NOT_ENOUGH_OP_MODE_CLEAR_ZERO,
                                                             'WINNER_TAX',
                                                             roomId, clientId, tableId)
        _recordLastTableChip(userId, finalChip, isSupportBuyin)
        finalChip += userchip.getChip(userId)
    else:
        trueDelta, finalChip = userchip.incrChip(userId, DIZHU_GAMEID, seat_delta,
                                                 daoconst.CHIP_NOT_ENOUGH_OP_MODE_CLEAR_ZERO,
                                                 'GAME_WINLOSE',
                                                 roomId, clientId)
        if chou_cheng < 0:
            trueDelta_cc, finalChip = userchip.incrChip(userId, DIZHU_GAMEID, chou_cheng,
                                                        daoconst.CHIP_NOT_ENOUGH_OP_MODE_CLEAR_ZERO,
                                                        'WINNER_TAX',
                                                        roomId, clientId)
    return trueDelta, trueDelta_cc, finalChip


def _incrWinLoseCoupon(userId, deltaCount, roomId, clientId):
    trueDelta, finalCount = userchip.incrCoupon(userId, DIZHU_GAMEID, deltaCount,
                                                daoconst.CHIP_NOT_ENOUGH_OP_MODE_CLEAR_ZERO,
                                                'COUPON_DIZHU_GAME_WIN',
                                                roomId, clientId)
    bireport.gcoin('in.coupon.gamewin', DIZHU_GAMEID, trueDelta)
    return trueDelta, finalCount


def _recordLastTableChip(userId, tablechip, isSupportBuyin):
    if isSupportBuyin :
        gamedata.setGameAttr(userId, DIZHU_GAMEID, 'last_table_chip', tablechip)


# def _getLastTableChip(userId, isSupportBuyin):
#     if isSupportBuyin:
#         return gamedata.getGameAttrInt(userId, DIZHU_GAMEID, 'last_table_chip') or -1
#     else:
#         return -1
# 
# 
# def _resetLastTableChip(userId, isSupportBuyin):
#     if isSupportBuyin :
#         gamedata.setGameAttr(userId, DIZHU_GAMEID, 'last_table_chip', -1)


def _caleWinStreakByUser(userId, winUserIds):
    winStreak = 0
    if userId in winUserIds:
        winStreak = gamedata.incrGameAttr(userId, DIZHU_GAMEID, 'winstreak', 1)
        gamedata.setGameAttr(userId, DIZHU_GAMEID, 'stopwinstreak', 0)
    else:
        userWinStreak = gamedata.getGameAttr(userId, DIZHU_GAMEID, 'winstreak')
        gamedata.setGameAttr(userId, DIZHU_GAMEID, 'stopwinstreak', userWinStreak)
        gamedata.setGameAttr(userId, DIZHU_GAMEID, 'winstreak', 0)
    return winStreak


def _caleLuckyItemArgsByUser(userId, bigRoomId, winUserIds, winStreak, slam, chuntian, clientId):
    lucky_args = {}
    if userId in winUserIds:
        conf = dizhuconf.getRoomWinLosePayInfo(bigRoomId, clientId)
        if not conf :
            conf = {}
        payOrder = None
        if chuntian > 1 and ('spring' in conf):
            payOrder = conf['spring']
        if winStreak >= 3 and ('winstreak' in conf):
            payOrder = conf['winstreak']
        if slam == 1 and ('slam' in conf):
            payOrder = conf['slam']
        if payOrder :
            product, _ = hallstore.findProductByPayOrder(DIZHU_GAMEID, userId, clientId, payOrder)
            if product :
                lucky_args = TodoTaskHelper.getParamsByProduct(product)
    return lucky_args


def _caleSkillScoreByUser(userId, winUserIds, winStreak, isdizhu_, roomId, windoubles):
    iswin_ = userId in winUserIds
    skill_obj = SkillScore(userId, roomId, windoubles, isdizhu_, iswin_, winStreak)
    skill_score_infos = skillscore.inc_skill_score(skill_obj)
    ftlog.debug('caleSkillScoreByUser->', userId, skill_score_infos)
    return skill_score_infos


def _incrRoomFeeChip(roomId, tableId, userId, isSupportBuyin, deltaCount, clientId):
    ftlog.debug('roomId, tableId, userId, isSupportBuyin, deltaCount, clientId',
                roomId, tableId, userId, isSupportBuyin, deltaCount, clientId)
    if isSupportBuyin :
        trueDelta, ccoin = userchip.incrTableChip(userId, DIZHU_GAMEID, deltaCount,
                                                  daoconst.CHIP_NOT_ENOUGH_OP_MODE_CLEAR_ZERO,
                                                  'ROOM_GAME_FEE',
                                                  roomId, clientId, tableId)
        _recordLastTableChip(userId, ccoin, isSupportBuyin)
    else:
        trueDelta, ccoin = userchip.incrChip(userId, DIZHU_GAMEID, deltaCount,
                                             daoconst.CHIP_NOT_ENOUGH_OP_MODE_CLEAR_ZERO,
                                             'ROOM_GAME_FEE',
                                             roomId, clientId) 
    ftlog.debug('trueDelta, ccoin', trueDelta, ccoin)
    return trueDelta, ccoin


def _incrCardNoteChip(roomId, tableId, userId, isSupportBuyin, deltaCount, clientId):
    ftlog.debug('table_remote.incrCardNoteChip roomId=', roomId,
                'tableId=', tableId,
                'userId=', userId,
                'isSupportBuyin=', isSupportBuyin,
                'deltaCount=', deltaCount,
                'clientId=', clientId)
    if isSupportBuyin :
        trueDelta, ccoin = userchip.incrTableChip(userId, DIZHU_GAMEID, deltaCount,
                                                  daoconst.CHIP_NOT_ENOUGH_OP_MODE_CLEAR_ZERO,
                                                  'TABLE_OPEN_CARD_NOTE',
                                                  roomId, clientId, tableId)
        _recordLastTableChip(userId, ccoin, isSupportBuyin)
    else:
        trueDelta, ccoin = userchip.incrChip(userId, DIZHU_GAMEID, deltaCount,
                                             daoconst.CHIP_NOT_ENOUGH_OP_MODE_CLEAR_ZERO,
                                             'TABLE_OPEN_CARD_NOTE',
                                             roomId, clientId) 
    ftlog.debug('table_remote.incrCardNoteChip roomId=', roomId,
                'tableId=', tableId,
                'userId=', userId,
                'isSupportBuyin=', isSupportBuyin,
                'deltaCount=', deltaCount,
                'clientId=', clientId,
                'trueDelta=', trueDelta,
                'finalChip=', ccoin)
    return trueDelta, ccoin

def _checkSetMedal(userId, roomMutil, basebet, basemulti, isGameStart, winchip):
    winchip = 0 if isGameStart else winchip

    winrate, oldLevel = gamedata.getGameAttrs(userId, DIZHU_GAMEID, ['winrate', 'level'], False)
    winrate = strutil.loads(winrate, ignoreException=True, execptionValue={})
    if winchip >= 0 or isGameStart :
        _processGamePlayWinTimes(winrate, isGameStart)

    oldLevel = strutil.parseInts(oldLevel)
    detalExp = 0
    if winchip > 0 or isGameStart :
        detalExp = _calUserDetalExp(winchip, roomMutil, basebet, basemulti)
    exp = userdata.incrExp(userId, detalExp)
    explevel = dizhuaccount.getExpLevel(exp)

    gamedata.setGameAttrs(userId, DIZHU_GAMEID, ['winrate', 'level'], [strutil.dumps(winrate), explevel])
    if oldLevel != explevel:
        from dizhu.game import TGDizhu
        TGDizhu.getEventBus().publishEvent(UserLevelGrowEvent(DIZHU_GAMEID, userId, oldLevel, explevel))
    if isGameStart :
        # 广告商通知
        pcount = dizhuconf.getAdNotifyPlayCount()
        if pcount > 0 and winrate.get('pt', 0) == pcount :
            sdkclient.adNotifyCallBack(DIZHU_GAMEID, userId)
    nextExp = dizhuaccount.getGameUserNextExp(explevel)
    title = dizhuaccount.getGameUserTitle(explevel)
    return [explevel, exp, detalExp, nextExp, title]


def _calUserDetalExp(winchip, roomMutil, basebet, basemulti):
    if winchip <= 0 :
        return 30  # 只要开玩，那么加30经验
    winexp = winchip * 1.0 / roomMutil / basebet / basemulti / 10.0
    return abs(int(winexp))


def _processGamePlayWinTimes(wrd, isGameStart):
    if not wrd: return
    if isGameStart :
        if 'pt' not in wrd:
            wrd['pt'] = 0
        wrd['pt'] += 1  # 全局play数加1
    else:
        if 'wt' not in wrd:
            wrd['wt'] = 0
        wrd['wt'] += 1  # 全局play数加1
    return wrd


def _calRankInfoData(userId, seatDeltaChip, winslam, windoubles):
    ftlog.debug('calRankInfoData->', userId, seatDeltaChip, winslam, windoubles)
    # 每周,城市赢金榜
    if seatDeltaChip > 0 and dizhuconf.isUseTuyouRanking() :  # 陌陌使用自己的排行榜
        city_code = sessiondata.getCityZip(userId)
        city_index = city_locator.ZIP_CODE_INDEX.get(city_code, 1)
        rankingId = 110006100 + city_index
        hallranking.rankingSystem.setUserScore(str(rankingId), userId, seatDeltaChip)

    # 更新gamedata中的各种max和累积值
    winchips, losechips, maxwinchip, weekchips, winrate, maxweekdoubles, slams, todaychips = gamedata.getGameAttrs(userId, DIZHU_GAMEID,
                                                                       ['winchips', 'losechips', 'maxwinchip',
                                                                        'weekchips', 'winrate', 'maxweekdoubles',
                                                                        'slams', 'todaychips'],
                                                                       False)
    ftlog.debug('calRankInfoData->', winchips, losechips, maxwinchip, weekchips, winrate, maxweekdoubles, slams)
    winchips, losechips, maxwinchip, maxweekdoubles, slams = strutil.parseInts(winchips, losechips, maxwinchip, maxweekdoubles, slams)
    updatekeys = []
    updatevalues = []
    
    # 计算累计的输赢金币
    if seatDeltaChip > 0 :
        winchips = winchips + seatDeltaChip
        updatekeys.append('winchips')
        updatevalues.append(winchips)
    else:
        losechips = losechips + seatDeltaChip
        updatekeys.append('losechips')
        updatevalues.append(losechips)
    
    # 计算增加最大的赢取金币数
    if seatDeltaChip > maxwinchip :
        updatekeys.append('maxwinchip')
        updatevalues.append(seatDeltaChip)
    
    # 计算增加每星期的累计赢取、输掉的金币数
    weekchips = strutil.loads(weekchips, ignoreException=True)
    if weekchips == None or len(weekchips) != 2 or (not 'week' in weekchips) or (not 'chips' in weekchips) :
        weekchips = {'week':-1, 'chips':0}
    weekOfYear = pktimestamp.formatTimeWeekInt()
    if weekOfYear != weekchips['week'] :
        weekchips = {'week':weekOfYear, 'chips':seatDeltaChip}
    else:
        weekchips['chips'] = weekchips['chips'] + seatDeltaChip
    updatekeys.append('weekchips')
    updatevalues.append(strutil.dumps(weekchips))

    # 计算增加每星期的累计赢取的金币数
    if seatDeltaChip > 0 :
        todaychips = strutil.loads(todaychips, ignoreException=True)
        if todaychips == None or len(todaychips) != 3 \
            or (not 'today' in todaychips) or (not 'chips' in todaychips) or (not 'last' in todaychips) :
            todaychips = {'today':-1, 'chips':0, 'last' : 0}
        today = pktimestamp.formatTimeDayInt()
        if today != todaychips['today'] :
            yesterdaychips = 0
            if todaychips['today'] == pktimestamp.formatTimeYesterDayInt() :
                yesterdaychips = todaychips['chips']
            todaychips = {'today':today, 'chips':seatDeltaChip, 'last' : yesterdaychips}
        else:
            todaychips['chips'] = todaychips['chips'] + seatDeltaChip
        updatekeys.append('todaychips')
        updatevalues.append(strutil.dumps(todaychips))

    # 计算marsscore
    winchipsDelta = int(winchips) - int(losechips)
    winrate = strutil.loads(winrate, ignoreException=True, execptionValue={'wt':0})
    wintimes = int(winrate.get('wt', 0))
    marsscore = winchipsDelta * 0.6 + wintimes * 200 * 0.4
    if marsscore > 0:
        updatekeys.append('marsscore')
        updatevalues.append(marsscore)
    
    # 计算slams和maxweekdoubles
    if seatDeltaChip > 0:
        if winslam:
            updatekeys.append('slams')
            updatevalues.append(slams + 1)

        if maxweekdoubles < windoubles:
            updatekeys.append('maxweekdoubles')
            updatevalues.append(windoubles)

    if len(updatekeys) > 0 :
        gamedata.setGameAttrs(userId, DIZHU_GAMEID, updatekeys, updatevalues)
    return 1


def _queryUserTableTasks(userId, clientId):
    taskModel = dizhutask.tableTaskSystem.loadTaskModel(userId, pktimestamp.getCurrentTimestamp())
    return TableTaskHelper.buildTableTasks(taskModel)

