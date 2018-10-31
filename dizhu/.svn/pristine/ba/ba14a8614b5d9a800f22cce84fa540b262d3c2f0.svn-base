# -*- coding=utf-8 -*-
from hall.servers.util.rpc import user_remote
from freetime.util import log as ftlog
from hall.entity import hallitem, hallstore, hallranking
from poker.entity.dao import sessiondata, userdata, gamedata
from hall.entity.todotask import TodoTaskOrderShow, TodoTaskHelper
from poker.protocol import router
from dizhu.entity.dizhuconf import DIZHU_GAMEID
from poker.entity.game.rooms.big_match_ctrl.matchif import MatchIF
from dizhu.gameplays import punish
from freetime.entity.msg import MsgPack
from dizhu.entity import dizhuaccount
from poker.util import timestamp as pktimestamp
 
MATCH_RANK_TEMPLATE_NAME = 'hero_match_success_rank'

class CommonMatchIF(MatchIF):
    
    @staticmethod
    def buildPrizeContent(rDict):
        '''
        构造奖励的描述
        '''
        if not rDict:
            return ''
        
        ftlog.debug('rDict:', rDict)
        contents = ''
        for reward in rDict:
            kindId = reward['itemId']
            rItem = hallitem.itemSystem.findAssetKind(kindId)
#             rInfo = {}
#             rInfo['icon'] = kindId
#             rInfo['name'] = rItem.displayName
#             rInfo['count'] = reward['count']
#             rInfo['iconPath'] = rItem.pic
            
            contents += '%s%s%s' % (reward['count'], rItem.units, rItem.displayName)
        return contents
    
    @staticmethod
    def collectFee(feeDict, userId, matchId, disKey):
        '''
        比赛收费
        '''
        assetKindId, count = user_remote.consumeAssets(
                DIZHU_GAMEID
                , userId
                , feeDict
                , disKey
                , matchId)
        
        ftlog.debug('CommonMatchIF.collectFee matchId=', matchId,
                   'userId=', userId,
                   'fees=', feeDict,
                   'assetKindId=', assetKindId,
                   'count=', count)
        if assetKindId:
            return False
        
        return True
    
    @staticmethod
    def returnFee(feeDict, userId, matchId, disKey):
        '''
        退还比赛费用
        MATCH_RETURN_FEE
        '''
        user_remote.addAssets(DIZHU_GAMEID, userId, feeDict, disKey, matchId)
        ftlog.debug('CommonMatchIF.returnFee matchId=', matchId,
                   'userId=', userId,
                   'fees=', feeDict)
        return True
    
    @staticmethod
    def sendRewards(rewards, userId, matchId, disKey):
        '''
        退还比赛费用
        MATCH_RETURN_FEE
        '''
        user_remote.addAssets(DIZHU_GAMEID, userId, rewards, disKey, matchId)
        ftlog.debug('CommonMatchIF.sendRewards matchId=', matchId,
                   'userId=', userId,
                   'rewards=', rewards)
        rewardsInfo = []
        for reward in rewards:
            kindId = reward['itemId']
            rItem = hallitem.itemSystem.findAssetKind(kindId)
            rInfo = {}
            rInfo['icon'] = kindId
            rInfo['name'] = rItem.displayName
            rInfo['count'] = reward['count']
            rInfo['iconPath'] = rItem.pic
            rewardsInfo.append(rInfo)
         
        ftlog.debug('CommonMatchIF.sendRewards rewardsInfo=', rewardsInfo)
        
        # 更新排行榜
        if disKey == 'MATCH_REWARD':
            hallranking.rankingSystem.setUserByInputType(DIZHU_GAMEID, MATCH_RANK_TEMPLATE_NAME, userId, 1, pktimestamp.getCurrentTimestamp())
        
        # 返回结果
        return rewardsInfo

    @staticmethod
    def sendLed(ledStr):
        '''
        发送LED
        '''
        scope = 'hall' + str(DIZHU_GAMEID)
        ftlog.debug('led scope:', scope)
        user_remote.sendHallLed(DIZHU_GAMEID, ledStr, 0, scope)
    
    @staticmethod
    def payOrder(payOrderParams, userId, failure):
        '''
        比赛报名费不足的充值引导
        '''
        ftlog.debug('userId:', userId
                    , ' payOrderParams:', payOrderParams
                    , ' failure:', failure)
        clientId = sessiondata.getClientId(userId)
        product, _shelves = hallstore.findProductByPayOrder(DIZHU_GAMEID, userId, clientId, payOrderParams)
        ftlog.debug('product:', product
                    , ' shelves:', _shelves)
        
        if not product:
            return False

        orderShow = TodoTaskOrderShow.makeByProduct(failure, '', product, '')
        mo = TodoTaskHelper.makeTodoTaskMsg(DIZHU_GAMEID, userId, orderShow)
        router.sendToUser(mo, userId)
        return True
    
    @classmethod
    def doWinLose(cls, room, table, seatId, isTimeOutKill=False): # TODO:
        # 计算春天
        dizhuseatId = table.status.diZhu
        if seatId != dizhuseatId: 
            if table.seats[dizhuseatId - 1].outCardCount == 1:
                table.status.chuntian = 2
        else:
            s1 = table.seats[(dizhuseatId - 1 + 1) % table.maxSeatN]
            s2 = table.seats[(dizhuseatId - 1 + 2) % table.maxSeatN]
            if s1.outCardCount == 0 and s2.outCardCount == 0:
                table.status.chuntian = 2
                 
        # 翻倍计算 叫地主的倍数
        windoubles = table.status.callGrade
        # 炸弹倍数
        windoubles *= pow(2, table.status.bomb)
        # 春天倍数
        windoubles *= table.status.chuntian
        # 底牌倍数
        windoubles *= table.status.baseCardMulti
        # 明牌倍数
        windoubles *= table.status.show
         
        dizhuwin = 0
        if seatId == dizhuseatId:
            dizhuwin = 1
        if seatId == 0 : # 流局
            dizhuwin = 0
            windoubles = 1
        else:
            windoubles = abs(windoubles)
 
        userids = []
        detalChips = []
        seat_coin = []
        baseBetChip = table._match_table_info['baseChip']
        robot_card_count = [0] * len(table.seats)  # 每个座位
        for x in xrange(len(table.seats)):
            uid = table.seats[x].userId
            userInfo = table._match_table_info['users'][x]
            userids.append(uid)
            if seatId == 0 : # 流局
                detalChip = -baseBetChip
            else:
                if dizhuwin :
                    if x + 1 == dizhuseatId :
                        detalChip = baseBetChip + baseBetChip
                    else:
                        detalChip = -baseBetChip
                else:
                    if x + 1 == dizhuseatId :
                        detalChip = -baseBetChip - baseBetChip
                    else:
                        detalChip = baseBetChip
            detalChip *= windoubles
            detalChips.append(detalChip)
            seat_coin.append(userInfo['score'] + detalChip)
            robot_card_count[x] = table.seats[x].robotCardCount
            ftlog.info('dizhu.game_win userId=', uid, 'roomId=', room.roomId, 'tableId=', table.tableId, 'delta=', detalChip)
        
        ftlog.debug('doWinLose->after room fee->robot_card_count=', robot_card_count)
        punish.Punish.doWinLosePunish(table.runConfig.punishCardCount, table.runConfig.isMatch,
                                      seat_coin, detalChips, robot_card_count)
        for x in xrange(len(table.seats)):
            uid = table.seats[x].userId
            userInfo = table._match_table_info['users'][x]
            userInfo['score'] = seat_coin[x]
        
        # 返回当前Table的game_win
        moWin = MsgPack()
        moWin.setCmd('table_call')
        moWin.setResult('action', 'game_win')
        moWin.setResult('isMatch', 1)
        moWin.setResult('gameId', table.gameId)
        moWin.setResult('roomId', table.roomId)
        moWin.setResult('tableId', table.tableId)
        moWin.setResult('stat', table.status.toInfoDictExt())
        moWin.setResult('dizhuwin', dizhuwin)
        if seatId == 0:
            moWin.setResult('nowin', 1)
        moWin.setResult('slam', 0)
        moWin.setResult('cards', [seat.cards for seat in table.seats])
 
        roundId = table.gameRound.number
        table.clear(userids)
         
        for x in xrange(len(userids)):
            uid = userids[x]
            mrank = 3
            mtableRanking = 3
            moWin.setResult('seat' + str(x + 1), [detalChips[x], seat_coin[x], 0, 0, 0, 0, mrank, mtableRanking])
             
            #增加经验
            exp = userdata.incrExp(uid, 20)
            explevel = dizhuaccount.getExpLevel(exp)
            gamedata.setGameAttr(uid, table.gameId, 'level', explevel)
            ftlog.debug('AsyncUpgradeHeroMatch.doWinLoseTable add 20 exp, tootle', exp, 'level', explevel)
             
        table.gamePlay.sender.sendToAllTableUser(moWin)
         
        # 发送给match manager
        users = []
        for x in xrange(len(userids)):
            user = {}
            user['userId'] = userids[x]
            user['deltaScore'] = int(detalChips[x])
            user['seatId'] = x + 1
            user['score'] = seat_coin[x]
            users.append(user)
         
        mnr_msg = MsgPack()
        mnr_msg.setCmd('room')
        mnr_msg.setParam('action', 'm_winlose')
        mnr_msg.setParam('gameId', table.gameId)
        mnr_msg.setParam('roomId', table.room.ctrlRoomId)
        mnr_msg.setParam('tableId', table.tableId)
        mnr_msg.setParam('users', users)
            
        # 记录游戏winlose
        try:
            for u in users:
                table.room.reportBiGameEvent("TABLE_WIN", u['userId'], table.roomId, table.tableId, roundId, u['deltaScore'], 0, 0, [], 'table_win')
#                 cls.report_bi_game_event(TyContext.BIEventId.TABLE_WIN, u['userId'], table._rid, table._id, table._roundId, u['deltaScore'], 0, 0, [], 'table_win')                
        except:
            if ftlog.is_debug():
                ftlog.exception()
        router.sendRoomServer(mnr_msg, table.room.ctrlRoomId)