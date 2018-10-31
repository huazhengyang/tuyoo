# -*- coding: utf-8 -*-
'''
Created on 2018年7月13日

@author: wangyonghui
'''

from dizhu.games.endgame import endgame
from dizhu.games.endgame.endgame import EndgamePlayer, endgame_player_map, EndgameHelper
from dizhu.games.endgame.engine.utils import translate_human_card_to_tycard
from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from hall.servers.common.base_checker import BaseMsgPackChecker
from poker.protocol import router, runcmd
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod


@markCmdActionHandler
class EndgameTcpHandler(BaseMsgPackChecker):
    def _check_param_roundNum(self, msg, key, params):
        roundNum = msg.getParam('roundNum')
        try:
            return None, int(roundNum)
        except:
            return None, 1

    @markCmdActionMethod(cmd='dizhu', action='endgame_start', clientIdVer=0, scope='game')
    def doEndgameStart(self, userId, roundNum, clientId):
        msg = runcmd.getMsgPack()
        isHelp = msg.getParam('isHelp', False)
        self._doEndgameStart(userId, roundNum, clientId, isHelp)

    @classmethod
    def _doEndgameStart(cls, userId, roundNum, clientId, isHelp):
        # 检查更新赛季
        updated = EndgameHelper.updateUserIssueRoundData(userId)

        # 获取用户当前数据
        historyRoundData = None
        udata = EndgameHelper.getUserCurrentRoundData(userId)

        # 获取配置关卡牌
        config = EndgameHelper.getCurrentIssueConfig()
        roundNum = min(roundNum, len(config.roundCards))
        roundCards = config.roundCards.get(str(roundNum), {})
        res = 1
        if not roundCards:
            res = 0

        landlordCards, farmerCards = [], []
        if res:
            historyRoundData = EndgameHelper.getUserRoundDataHistory(userId, roundNum)
            landlordCards, farmerCards = translate_human_card_to_tycard(roundCards.get('landlordCards', []), roundCards.get('farmerCards', []))
            player = EndgamePlayer(userId,
                                   landlordCards,
                                   farmerCards)
            player.historyRoundData = historyRoundData
            player.maxRoundNum = len(config.roundCards)
            player.isHelp = isHelp
            endgame_player_map[userId] = player
            # 闯关次数加 1
            if not historyRoundData:
                udata.playCount += 1
                EndgameHelper.saveUserCurrentRoundData(userId, udata)

        if ftlog.is_debug():
            from dizhu.games.endgame.engine.utils import card_num_to_human_map
            ftlog.debug('EndgameTcpHandler._doEndgameStart userId=', userId,
                        'clientId=', clientId,
                        'roundNum=', roundNum,
                        'updated=', updated,
                        'historyRoundData=', historyRoundData,
                        'udata=', udata.encodeToDict(),
                        'isHelp=', isHelp,
                        'roundCards=', roundCards,
                        'farmerCards=', ''.join([card_num_to_human_map[c] for c in farmerCards]),
                        'landlordCards=', ''.join([card_num_to_human_map[c] for c in landlordCards]))

        mo = MsgPack()
        mo.setCmd('dizhu')
        mo.setResult('action', 'endgame_start')
        mo.setResult('farmerCards', farmerCards)
        mo.setResult('landlordCards', landlordCards)
        mo.setResult('challengeCount', udata.playCount if not historyRoundData else historyRoundData.playCount)
        mo.setResult('totalRoundCount', len(config.roundCards))
        mo.setResult('updated', updated)
        mo.setResult('ok', res)
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd='dizhu', action='endgame_card', clientIdVer=0, scope='game')
    def doEndgameOutCard(self, userId, clientId):
        msg = runcmd.getMsgPack()
        self._doEndgameOutCard(msg, userId, clientId)

    @classmethod
    def _doEndgameOutCard(cls, msg, userId, clientId):
        # 出牌
        cards = msg.getParam('cards', [])
        res = 0
        player = endgame_player_map.get(userId)
        robotCards = []
        state = None
        nextRoundNum = 0
        isHelp = False
        reply = []
        initLandlordCards = []
        initFarmerCards = []
        if player:
            try:
                ret = player.outCards(cards)
                robotCards = ret['removeFarmerCards']
                state = ret['state']
                nextRoundNum = ret['roundNum']
                isHelp = ret['isHelp']
                reply = ret['reply']
                initLandlordCards = ret['initLandlordCards']
                initFarmerCards = ret['initFarmerCards']
                res = 1
            except Exception, e:
                ftlog.warn('EndgameTcpHandler._doEndgameOutCard userId=', userId,
                           'err=', e.message)

        if state != EndgamePlayer.STATE_PLAYING:
            try:
                del endgame.endgame_player_map[userId]
            except:
                pass
        mo = MsgPack()
        mo.setCmd('dizhu')
        mo.setResult('action', 'endgame_card')
        mo.setResult('robotCards', robotCards)
        mo.setResult('state', state)
        mo.setResult('nextRoundNum', nextRoundNum)
        mo.setResult('isHelp', isHelp)
        mo.setResult('reply', reply)
        mo.setResult('initLandlordCards', initLandlordCards)
        mo.setResult('initFarmerCards', initFarmerCards)
        mo.setResult('ok', res)
        router.sendToUser(mo, userId)
