# -*- coding:utf-8 -*-
'''
Created on 2017年2月22日

@author: zhaojiangang
'''
import random

from dizhu.activities.toolbox import UserBag
from dizhu.entity import dizhu_util, dizhuconf
from dizhu.entity.dizhuconf import DIZHU_GAMEID
from dizhu.entity.matchhistory import MatchHistoryHandler
from dizhucomm.entity import commconf
from hall.entity import hallconf, hallitem
import poker.util.timestamp as pktimestamp
import freetime.util.log as ftlog
from hall.entity.hallitem import ASSET_CHIP_KIND_ID, ASSET_COUPON_KIND_ID, ASSET_DIAMOND_KIND_ID
from poker.entity.biz.content import TYContentItem
from poker.entity.biz.exceptions import TYBizException, TYBizConfException
from poker.entity.configure import configure, gdata
from poker.entity.dao import sessiondata, daoconst, gamedata, userdata, daobase
from poker.entity.biz import bireport
from poker.util import strutil
from poker.util import webpage


def getMatchSigninFeeWithoutCollect():
    """ 获取不需要消费的比赛报名费 """
    return [hallitem.ASSET_ITEM_CROWN_MONTHCARD_KIND_ID, hallitem.ASSET_ITEM_HONOR_MONTHCARD_KIND_ID]

def buildRewards(rankRewards):
    ret = []
    for r in rankRewards.rewards:
        if r['count'] > 0:
            name = hallconf.translateAssetKindIdToOld(r['itemId'])
            assetKind = hallitem.itemSystem.findAssetKind(r['itemId'])
            ret.append({'name':name or '', 'count':r['count'], 'url': assetKind.pic if assetKind else ''})
    return ret

def buildShareInfo(gameId, clientId):
    return commconf.getGamewinShareinfo(gameId, clientId)

def buildRewardsDesc(rankRewards):
    notNeedDescNames = set(['user:chip', 'user:coupon', 'ddz.exp'])
    allZero = True
    for r in rankRewards.rewards:
        if r['count'] <= 0:
            continue
        if r['itemId'] not in notNeedDescNames:
            return rankRewards.desc
    return rankRewards.desc if allZero else None

def buildFees(fees):
    ret = []
    for fee in fees:
        if fee.count > 0:
            name = hallconf.translateAssetKindIdToOld(fee.assetKindId)
            ret.append({'item':name, 'count':fee.count})
    return ret

def buildFeesList(userId, fees):
    ret = [] # 返回付费列表[{type,desc,selected,img}，{...}]
    # 不用写单位的道具类型集合
    notNeedUnit = set(['user:chip', 'user:exp', 'user:charm', 'ddz:master.score']);
    for fee in fees:
        assetKind = hallitem.itemSystem.findAssetKind(fee.assetKindId)
        if fee.count > 0 and assetKind:
            if fee.assetKindId in notNeedUnit:
                desc = str(fee.count) + assetKind.displayName
            elif fee.assetKindId in getMatchSigninFeeWithoutCollect():
                desc = assetKind.displayName
            else:
                desc = str(fee.count) + assetKind.units + assetKind.displayName
            from dizhu.activities.toolbox import UserBag
            myCount = UserBag.getAssetsCount(userId, fee.assetKindId)
            ret.append({
                'type':fee.assetKindId,
                'desc':desc,
                'img':assetKind.pic,
                'selected':False,
                'fulfilled':1 if myCount >= fee.count else 0
            })
    return ret


def getUserChampionLimitFlag(userId, roomId, recordId, mixId=None):
    '''
    获取用户获取冠军的限制标记
    '''

    matchChampionConf = configure.getGameJson(DIZHU_GAMEID, 'match.champion.limit', {})
    if not matchChampionConf:
        return False
    bigRoomId = gdata.getBigRoomId(roomId)
    limitConf = matchChampionConf.get(str(mixId or bigRoomId), {})
    if limitConf.get('open', 0) == 0:
        return False
    playCountLimit = limitConf.get('playCountLimit', 20)
    playHoursLimit = limitConf.get('playHoursLimit', 48)
    # 获取最近40局的信息
    currentTimeStamp = pktimestamp.getCurrentTimestamp()
    playCount = 0
    histories = MatchHistoryHandler.getMatchHistory(userId, recordId, 40, mixId)
    if ftlog.is_debug():
        ftlog.debug('Matchutil.getUserChampionLimitSign userId=', userId,
                    'roomId=', roomId,
                    'mixId=', mixId,
                    'playCountLimit=', playCountLimit,
                    'playHoursLimit=', playHoursLimit,
                    'histories=', histories)

    for history in histories:
        playCount += 1
        rank = history.get('rank')
        if rank not in [1, 2, 3]:
            continue
        timestamp = history.get('timestamp')
        hourDelta = int((currentTimeStamp - timestamp) / 3600)
        # 与配置相比较，局数以且时间
        if ftlog.is_debug():
            ftlog.debug('Matchutil.getUserChampionLimitSign userId=', userId,
                        'roomId=', roomId,
                        'mixId=', mixId,
                        'playCount=', playCount,
                        'hourDelta=', hourDelta,
                        'playCountLimit=', playCountLimit,
                        'playHoursLimit=', playHoursLimit)
        if playCount <= playCountLimit and hourDelta <= playHoursLimit:
            return True
        return False
    return False


def getMatchChampionLimitConf(bigRoomId):
    matchChampionConf = configure.getGameJson(DIZHU_GAMEID, 'match.champion.limit', {})
    if not matchChampionConf:
        return {}
    bigRoomId = gdata.getBigRoomId(bigRoomId)
    return matchChampionConf.get(str(bigRoomId), {})


def report_bi_game_event(eventId, userId, roomId, tableId, roundId, detalChip, state1, state2, cardlist, tag=''):
    try:
        try:
            clientId = sessiondata.getClientId(userId)
        except:
            clientId = 0
        bireport.reportGameEvent(eventId, userId, 6, roomId, tableId, roundId, detalChip, state1, state2, cardlist, clientId, 0, 0)
        ftlog.info('report_bi_game_event tag=', tag, 'eventId=', eventId, 'userId=', userId, 'gameId=6', 'roomId=', roomId, 'tableId=', tableId, 'roundId=', roundId)
    except:
        ftlog.error('report_bi_game_event error tag=', tag, 'eventId=', eventId, 'userId=', userId, 'gameId=6', 'roomId=', roomId, 'tableId=', tableId, 'roundId=', roundId)


def getBiChipType(assetKindId):
    if assetKindId == ASSET_CHIP_KIND_ID:
        return daoconst.CHIP_TYPE_CHIP
    elif assetKindId == ASSET_COUPON_KIND_ID:
        return daoconst.CHIP_TYPE_COUPON
    elif assetKindId.startswith('item'):
        return daoconst.CHIP_TYPE_ITEM
    elif assetKindId == ASSET_DIAMOND_KIND_ID:
        return daoconst.CHIP_TYPE_DIAMOND
    else:
        return 0


class BanHelper(object):
    '''
    托管禁赛策略
    '''
    @classmethod
    def getMatchBanConf(cls):
        return configure.getGameJson(DIZHU_GAMEID, 'match.ban', {})

    @classmethod
    def onGameRoundFinish(cls, event):
        banConf = cls.getMatchBanConf()
        if not banConf.get("open"):
            return

        if ftlog.is_debug():
            ftlog.debug('BanHelper.onGameRoundFinish',
                        'tableId=', event.table.tableId,
                        'seats=', [(s.userId, s.seatId, s.status.isPunish, s.player.isQuit) for s in event.table.seats])
        for seat in event.table.seats:
            if hasattr(seat.player, 'mixId') and seat.player.mixId:
                roomId = int(seat.player.mixId)
            else:
                roomId = event.table.bigRoomId

            if seat.status.isTuoguan and not seat.player.isQuit and roomId in banConf.get('fromRooms', []):
                matchTuoguan = gamedata.getGameAttr(seat.userId, DIZHU_GAMEID, 'matchTuoguanCount')
                matchTuoguan = strutil.loads(matchTuoguan) if matchTuoguan else {}

                # 自然日清零
                currentTimestamp = pktimestamp.getCurrentTimestamp()
                if not pktimestamp.is_same_day(currentTimestamp, matchTuoguan.get('expired', pktimestamp.getCurrentTimestamp())):
                    matchTuoguan['expired'] = pktimestamp.getCurrentTimestamp()
                    matchTuoguan['count'] = 0

                if matchTuoguan.get('count'):
                    matchTuoguan['count'] += 1
                else:
                    matchTuoguan['count'] = 1

                banTime = cls.getTuoguanBanTime(matchTuoguan['count'], banConf)
                if banTime:
                    matchTuoguan['expired'] = banTime * 60 + pktimestamp.getCurrentTimestamp()
                gamedata.setGameAttr(seat.userId, DIZHU_GAMEID, 'matchTuoguanCount', strutil.dumps(matchTuoguan))

    @classmethod
    def getTuoguanBanTime(cls, count, banTimeConf):
        for c in banTimeConf.get('tuoguanBanTime', []):
            if count == c['count']:
                return c['time']

    @classmethod
    def checkBanValid(cls, userId, roomId):
        if roomId not in cls.getMatchBanConf().get('toRooms', []):
            return False, 0
        currentTimestamp = pktimestamp.getCurrentTimestamp()
        matchTuoguan = gamedata.getGameAttr(userId, DIZHU_GAMEID, 'matchTuoguanCount')
        matchTuoguan = strutil.loads(matchTuoguan) if matchTuoguan else {}
        if currentTimestamp >= matchTuoguan.get('expired', 0):
            return False, 0
        return True, matchTuoguan.get('expired') - currentTimestamp


class MatchBanException(TYBizException):
    def __init__(self, remainSeconds, errcode=4, message=''):
        if not message:
            minutes = remainSeconds / 60
            if minutes > 60:
                message = '由于您多次托管，系统将您暂时禁赛。\n%s小时%s分钟后将解除禁赛状态' % (minutes / 60, minutes % 60)
            elif minutes == 0:
                message = '由于您多次托管，系统将您暂时禁赛。\n%s秒后将解除禁赛状态' % remainSeconds
            else:
                message = '由于您多次托管，系统将您暂时禁赛。\n%s分钟后将解除禁赛状态' % minutes
        super(MatchBanException, self).__init__(errcode, message)


class MatchGameRestartException(TYBizException):
    def __init__(self, errcode=4, message=''):
        if not message:
            message = '系统提示：即将进行系统停服维护'
        super(MatchGameRestartException, self).__init__(errcode, message)


class MatchLottery(TYBizException):
    """
    比赛结束后给冠军玩家一次抽奖机会
    """
    def __init__(self, errcode=0, message=''):
        super(MatchLottery, self).__init__(errcode, message)
        self.matchList = None
        self.open = None

    def getMatchLotteryConf(self, roomId, rank):
        lottery_conf = dizhuconf.getMatchLotteryConf()
        self.decodeFromDict(lottery_conf)

        bigRoomId = gdata.getBigRoomId(roomId)
        discount_conf = lottery_conf.get('matchList')
        room_discount_conf = discount_conf.get(str(bigRoomId)) if discount_conf else None
        if room_discount_conf:
            for conf in room_discount_conf:
                beginRank = conf.get('beginRank')
                endRank = conf.get('endRank')
                items = conf.get('items')
                if beginRank <= rank <= endRank:
                    if ftlog.is_debug():
                        ftlog.debug('getMatchLotteryConf. roomId=', roomId, 'rank=', rank, 'items=', items,
                                    'room_discount_conf=', room_discount_conf)
                    return items
        return None

    def chooseReward(self, userId, matchId, rank):
        if ftlog.is_debug():
            ftlog.debug('MatchLottery userId=', userId, 'matchId=', matchId, 'rank=', rank)

        if not self.matchList:
            d = dizhuconf.getMatchLotteryConf()
            self.decodeFromDict(d)

        if not self.checkMatchRank(userId, matchId, rank):
            ftlog.warn('MatchLottery.checkMatchRank failed. userId=', userId,
                        'matchId=', matchId, 'rank=', rank)
            return None, None

        items = self.getMatchLotteryConf(matchId, rank)
        if not items:
            ftlog.warn('MatchLottery.checkMatchRank failed. no items. userId=', userId, 'matchId=', matchId, 'rank=', rank)
            return None, None

        weights = 0
        for item in items:
            weights += item.get('weight', 0)
        r = random.randint(0, weights)
        lotteryReward = []
        weightTotal = 0
        for item in items:
            weightTotal += item.get('weight', 0)
            if r <= weightTotal:
                lotteryReward.append({'itemId': str(item.get('itemId')), 'count': item.get('count')})
                break
        lotteryReward = items[-1] if not lotteryReward else lotteryReward

        if ftlog.is_debug():
            ftlog.debug('MatchLottery weights=', weights, 'r=', r, 'userId=', userId, 'lotteryReward=', lotteryReward)

        if lotteryReward:
            contentItems = TYContentItem.decodeList(lotteryReward)
            assetList = dizhu_util.sendRewardItems(userId, contentItems, '', 'DIZHU_MATCH_LOTTERY', 0)

            ftlog.info('MatchLottery.chooseReward userId=', userId,
                       'matchId=', matchId,
                       'lotteryReward=', lotteryReward,
                       'assetList=', assetList)

        for i in items:
            assetKind = hallitem.itemSystem.findAssetKind(i['itemId'])
            i['img'] = assetKind.pic
            i['des'] = assetKind.desc
            i['name'] = assetKind.displayName

        if ftlog.is_debug():
            ftlog.debug('MatchLottery.chooseReward userId=', userId,
                        'matchId=', matchId, 'rank=', rank,
                        'lotteryReward=', lotteryReward)

        return lotteryReward, items

    @classmethod
    def checkMatchRank(cls, userId, matchId, rank):
        matchId = gdata.getBigRoomId(matchId)
        lottery_conf = dizhuconf.getMatchLotteryConf()
        lottery_switch = lottery_conf.get('open')
        if not lottery_switch:
            return False

        # 钻石数量为0触发
        user_diamond = userdata.getAttrInt(userId, 'diamond')
        if user_diamond != 0:
            return False

        # 身上没有任何报名券 触发
        discount_conf = lottery_conf.get('discountItem', [])
        if not discount_conf:
            return False

        for discountItem in discount_conf:
            itemId = discountItem.get('itemId')
            userHaveAssetsCount = UserBag.getAssetsCount(userId, itemId)
            if userHaveAssetsCount != 0:
                return False

        match_conf = lottery_conf.get('matchList', {}).get(str(matchId), [])
        if not match_conf:
            return False
        for conf in match_conf:
            beginRank = conf['beginRank']
            endRank = conf['endRank']
            if beginRank <= rank <= endRank:
                if ftlog.is_debug():
                    ftlog.debug('checkMatchRank userId=', userId, 'matchId=', matchId, 'return True')
                return True

        # 若是客户端请求则需要验证排名信息
        # histories = MatchHistoryHandler.getMatchHistory(userId, recordId, 1, mixId)
        # for history in histories:
        #     recordRank = history.get('rank')
        #     if rank != recordRank:
        #         return False
        #     timestamp = history.get('timestamp')
        #     currtimestamp = pktimestamp.getCurrentTimestamp()
        #     if (currtimestamp - timestamp) > 300:
        #         return False

        if ftlog.is_debug():
            ftlog.debug('checkMatchRank userId=', userId, 'matchId=', matchId, 'return False')
        return False

    def decodeFromDict(self, d):
        self.open = d.get('open')
        if not isinstance(self.open, int) or self.open not in (0, 1):
            raise TYBizConfException(d, 'MatchLottery.open must in 0, 1')

        self.matchList = d.get('matchList', {})
        if self.matchList and not isinstance(self.matchList, dict):
            raise TYBizConfException(d, 'MatchLottery.matchList must be dict')

        return self.matchList


def saveMatchLotteryInfo(userId, fee):
    # 保存用户报名券报名信息
    jstr = daobase.executeRePlayCmd('hget', 'match:discount:6:', userId)
    match_discount = strutil.loads(jstr) if jstr else []
    match_discount.append(fee[0])
    jstr = strutil.dumps(match_discount)
    daobase.executeRePlayCmd('hset', 'match:discount:6', userId, jstr)

    if ftlog.is_debug():
        ftlog.debug('saveMatchLotteryInfo userId=', userId, 'fee=', fee, 'jstr=', jstr)

def delMatchLotteryInfo(userId, matchId):
    jstr = daobase.executeRePlayCmd('hget', 'match:discount:6:', userId)

    match_discount = strutil.loads(jstr) if jstr else []
    for index in range(len(match_discount)):
        if match_discount[index]['matchId'] == matchId:
            del match_discount[index]
            daobase.executeDizhuCmd('hdel', 'match:discount:6', userId)
            daobase.executeDizhuCmd('hset', 'match:discount:6', userId, strutil.dumps(match_discount))
            break
    ftlog.debug('delMatchLotteryInfo userId=', userId, 'jstr=', match_discount)
    return match_discount

def changeSignInFees(userId, matchId, fees):
    matchId = gdata.getBigRoomId(matchId)
    lottery_conf = dizhuconf.getMatchLotteryConf()
    discountItems = lottery_conf.get('discountItem')
    changedItemId = None
    ftlog.debug('changeSignInFees userId=', userId, 'matchId=', matchId, 'fees before=', fees)
    for discount in discountItems:
        discountList = discount.get('discountList', [])
        if matchId in discountList:
            itemId = discount.get('itemId', '')
            discountPoint = discount.get('discount', '')
            if UserBag.getAssetsCount(userId, itemId) > 0:
                for fee in fees:
                    if fee.get('itemId', '') == ASSET_DIAMOND_KIND_ID:
                        fee['count'] = int(discountPoint * fee['count'] /10)
                        saveMatchLotteryInfo(userId, [{'itemId':itemId, 'matchId':matchId}])
                        fees.append({'itemId':itemId, 'count':1})
                        changedItemId = fee.get('itemId', '')
                        break
                break
    ftlog.debug('changeSignInFees userId=', userId, 'fees=', fees)
    return fees, changedItemId

def returnSignInfFees(userId, roomId, fees):
    #获取用户报名券信息
    roomId = gdata.getBigRoomId(roomId)
    jstr = daobase.executeRePlayCmd('hget', 'match:discount:6', userId)
    match_discounts = strutil.loads(jstr) if jstr else []
    if match_discounts:
        for discount in match_discounts:
            itemId = discount.get('itemId', '')
            matchId = discount.get('matchId', '')
            if matchId == roomId:
                for fee in fees:
                    if fee['itemId'] == ASSET_DIAMOND_KIND_ID:
                        discounted = 10
                        lottery_conf = dizhuconf.getMatchLotteryConf()
                        discountItems = lottery_conf.get('discountItem')
                        for discountItem in discountItems:
                            if itemId == discountItem.get('itemId', ''):
                                discounted = discountItem.get('discount', 10)

                        fee['count'] = fee['count'] * discounted / 10
                        fees.append({'itemId':itemId, 'count':1})
                        delMatchLotteryInfo(userId, roomId)
                break
    ftlog.debug('returnSignInfFees userId=', userId, 'roomId=', roomId, 'fees=', fees, 'match_discounts=', match_discounts)
    return fees


# 小程序口令红包相关
class RedEnvelopeHelper(object):
    ''' 小程序口令红包
        http://192.168.10.93:8090/pages/viewpage.action?pageId=14031256
        sign生成规则：对除了sign的其它参数按参数名作升序排列，再进行key和value的字符串组装；然后对组装成的字符串进行你猜加密，最后进行md5加密;
        http://gdss.touch4.me/?act=api.getCommandRed&userId=99022&gameId=6&money=1&matchId=&roomId=&rank=&sign=4BCC19BE764484ADC7087D8E8BD38F7C
    '''
    REQUEST_URL = "http://gdss.touch4.me/?act=api.getCommandRed"

    @classmethod
    def getRedEnvelopeCode(cls, userId, gameId, exchangeMoney, roomId, instId, rank):
        '''
        获取红包口令
        '''
        try:

            params = {
                "userId": userId,
                "gameId": gameId,
                "money": exchangeMoney,
                "matchId": instId or "",
                "roomId": roomId or "",
                "rank": rank or ""
            }
            sign = cls.signParams(params)
            params['sign'] = sign
            exchangeCode = None
            jsonstr, _ = webpage.webget(cls.REQUEST_URL, querys=params, method_='GET')
            data = None
            if jsonstr:
                data = strutil.loads(jsonstr)
                if data['retcode'] == 1:
                    exchangeCode = data['retmsg']
            ftlog.info('RedEnvelopeHelper.getRedEnvelopeCode:',
                       'userId=', userId,
                       'exchangeMoney=', exchangeMoney,
                       'gameId=', gameId,
                       'roomId=', roomId,
                       'instId=', instId,
                       'rank=', rank,
                       'data=', data,
                       'jsonstr=', jsonstr,
                       'params=', params,
                       'sign=', sign)


            return exchangeCode

        except Exception, e:
            ftlog.error('RedEnvelopeHelper.getRedEnvelopeCode:',
                        'userId=', userId,
                        'exchangeMoney=', exchangeMoney,
                        'gameId=', gameId,
                        'roomId=', roomId,
                        'instId=', instId,
                        'rank=', rank,
                        'err=', e.message)
            return None

    @classmethod
    def signParams(cls, params):
        ''' 参数签名 '''
        sk = sorted(params.keys())
        strs = ['%s=%s' % (k, params[k]) for k in sk]
        md5str = strutil.tyDesEncode('&'.join(strs))
        return strutil.md5digest(md5str)
