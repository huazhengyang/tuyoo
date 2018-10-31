# -*- coding:utf-8 -*-
'''
Created on 2018年9月20日

@author: wangyonghui
'''
from dizhu.entity.dizhuconf import DIZHU_GAMEID
from dizhu.servers.util.rpc import new_table_winlose, new_table_remote
from dizhu.games.normalbase.tableproto import DizhuTableProtoNormalBase
from poker.entity.configure import configure
from poker.entity.dao import gamedata
from poker.protocol import router
import freetime.util.log as ftlog
import dizhu.entity.skillscore as skillscore
from poker.util import strutil


class DizhuTableProtoNormalAI(DizhuTableProtoNormalBase):
    def __init__(self, tableCtrl):
        super(DizhuTableProtoNormalAI, self).__init__(tableCtrl)

    def buildResultDetails(self, result):
        luckyItemArgs = []
        winStreak = []
        skillScoreInfos = []
        cards = []
        addCoupons = []
        seatDetails = []
        seatInfos = []
        for sst in result.seatStatements:
            waittime = self.table.runConf.optimeCall
            if sst.final < self.table.runConf.minCoin:
                waittime = int(waittime / 3)

            datas = {}
            try:
                datas = new_table_winlose.queryDataAfterWinlose(sst.seat.userId,
                                                                self.bigRoomId,
                                                                sst.isWin,
                                                                sst.winStreak,
                                                                result.slam,
                                                                result.isChuntian,
                                                                sst.seat.player.clientId)
            except Exception, e:
                ftlog.warn('DizhuTableProtoNormal.buildResultDetails',
                           'userId=', sst.seat.player.userId,
                           'roomId=', self.roomId,
                           'tableId=', self.tableId,
                           'ex=', str(e))

            # 兼容老版本
            gameClientVer = sst.seat.player.gameClientVer
            if ftlog.is_debug():
                ftlog.debug('DizhuTableProtoNormal.buildResultDetails',
                            'gameClientVer=', gameClientVer,
                            'userId=', sst.seat.player.userId)

            tbbox = datas.get('tbbox', [0, 0])
            details = [
                sst.delta,
                sst.final,
                0,  # addcoupons[i],
                waittime,
                tbbox[0],
                tbbox[1],
                sst.expInfo[0], sst.expInfo[1], sst.expInfo[2], sst.expInfo[3], sst.expInfo[4],
                sst.seat.player.chip
            ]

            # 地主v3.773特效需要知道上一个大师分等级图标
            # 传两个大图
            if not sst.seat.player.isAI:
                skilscoreinfo = sst.skillscoreInfo
                masterlevel = skilscoreinfo['level']
                curlevelpic = skillscore.get_skill_score_big_level_pic(masterlevel)
                lastlevelpic = skillscore.get_skill_score_big_level_pic(masterlevel - 1)
                skilscoreinfo['lastbiglevelpic'] = lastlevelpic
                skilscoreinfo['curbiglevelpic'] = curlevelpic
                winStreak.append(sst.winStreak)
                skillScoreInfos.append(skilscoreinfo)

            seatDetails.append(details)
            cards.append(sst.seat.status.cards)
            addCoupons.append(0)
            seatInfos.append({'punished': 1} if sst.isPunish else {})
            luckyItemArgs.append(datas.get('luckyArgs', {}))

        return {
            'winStreak': winStreak,
            'luckyItemArgs': luckyItemArgs,
            'skillScoreInfos': skillScoreInfos,
            'addcoupons': addCoupons,
            'cards': cards,
            'seatDetails': seatDetails,
            'seatInfos': seatInfos,
            'kickOutCoinTip': '点击继续，将自动将您\n桌面金币补充至%s。\n继续努力吧！' % self.table.room.roomConf['buyinchip']
        }

    def sendWinloseRes(self, result):
        details = self.buildResultDetails(result)
        mp = self.buildWinloseRes(result, details, 1)
        # 免费场开关
        freeFeeSwitch = self.table.room.roomConf.get('freeFeeSwitch', 0)
        mp.setResult('free', freeFeeSwitch)
        from dizhu.game import TGDizhu
        from dizhu.entity.common.events import ActiveEvent
        crossPlayCount = configure.getGameJson(DIZHU_GAMEID, 'wx.cross', {}).get('crossPlayCount', 10)
        crossDelaySeconds = configure.getGameJson(DIZHU_GAMEID, 'wx.cross', {}).get('crossDelaySeconds', 10)
        authPlayCount = configure.getGameJson(DIZHU_GAMEID, 'authorization', {}).get('authPlayCount', 5)
        rewards = configure.getGameJson(DIZHU_GAMEID, 'authorization', {}).get('rewards', {})
        for index, seat in enumerate(self.table.seats):
            isKickOutCoin = 0
            if seat.player and not seat.isGiveup:
                if self.table.room.roomConf.get('isAI') and seat.player.isAI:
                    continue
                ssts = result.seatStatements
                # 是否达到踢出值
                isLowerKickOutCoin = True if ssts[index].final < self.table.room.roomConf.get('kickOutCoin', 0) else False

                # 不踢出
                if isLowerKickOutCoin and seat.player.chip < self.table.room.roomConf['buyinchip']:
                    isKickOutCoin = 1

                # 点击继续的提醒
                mp.rmResult('kickOutCoinTip')
                if isLowerKickOutCoin and seat.player.chip >= self.table.room.roomConf['buyinchip']:
                    mp.setResult('kickOutCoinTip', details.get('kickOutCoinTip'))

                # 是否达到踢出值
                mp.setResult('isKickOutCoin', isKickOutCoin)
                # 破产埋点Id
                kickOutBurialId = self.table.room.roomConf.get('kickOutBurialId')
                mp.setResult('kickOutBurialId', kickOutBurialId)
                # 首败分享埋点
                mp.rmResult('firstLoseBurialId')
                if seat.player.isFirstLose(ssts[index].isWin):
                    firstLoseBurialId = self.table.room.roomConf.get('firstLoseBurialId')
                    mp.setResult('firstLoseBurialId', firstLoseBurialId)

                # 是否展示交叉导流
                dailyPlayCount = new_table_remote.doGetUserDailyPlayCount(seat.userId, DIZHU_GAMEID)
                mp.setResult('dailyPlay', dailyPlayCount)
                mp.rmResult('showCross')
                mp.setResult('showCross', dailyPlayCount > crossPlayCount)
                mp.setResult('crossDelaySeconds', crossDelaySeconds)

                if dailyPlayCount == 3:
                    TGDizhu.getEventBus().publishEvent(ActiveEvent(6, seat.userId, 'playTimes3'))

                mp.rmResult('auth')
                if dailyPlayCount == authPlayCount:
                    mp.setResult('auth', {'auth': 1, 'rewards': rewards})

                # 服务费字段
                mp.setResult('room_fee', ssts[index].fee + ssts[index].fixedFee)

                # 每日首胜
                if seat.player.isFirstWin(ssts[index].isWin):
                    from dizhu.game import TGDizhu
                    from dizhu.entity.common.events import ActiveEvent
                    import poker.util.timestamp as pktimestamp
                    TGDizhu.getEventBus().publishEvent(ActiveEvent(6, seat.userId, 'dailyFirstWin'))
                    today = pktimestamp.formatTimeDayInt()
                    firstWin = {str(today): 1}
                    gamedata.setGameAttrs(seat.userId, DIZHU_GAMEID, ['firstWin'], [strutil.dumps(firstWin)])

                if ftlog.is_debug():
                    ftlog.debug('sendWinloseRes userId=', seat.userId,
                                'dailyPlayCount=', dailyPlayCount,
                                'showCross=', dailyPlayCount > crossPlayCount,
                                'crossDelaySeconds=', crossDelaySeconds,
                                'msg=', mp)
                router.sendToUser(mp, seat.userId)

    # 天梯赛桌重写QuickStart消息
    def buildQuickStartResp(self, seat, isOK, reason):
        mp = self.buildTableMsgRes('quick_start')
        mp.setResult('isOK', isOK)
        mp.setResult('seatId', seat.seatId)
        mp.setResult('reason', reason)
        mp.setResult('tableType', 'classic')
        return mp
