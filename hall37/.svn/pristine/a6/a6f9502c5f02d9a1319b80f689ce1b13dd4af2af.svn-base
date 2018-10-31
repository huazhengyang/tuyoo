# coding: utf-8

"""
代理商城相关实现

HTTP 接口：
http://192.168.10.93:8090/pages/viewpage.action?pageId=6455461
"""


from poker.entity.biz.store.exceptions import TYStoreConfException
from poker.entity.biz.store.store import TYBuyCondition
from poker.entity.biz.store.exceptions import TYStoreException
from poker.entity.biz.exceptions import TYBizConfException, TYBizException
from poker.entity.biz.item.item import TYAssetKind
import poker.entity.biz.message.message as pkmessage
import poker.util.timestamp as pktimestamp
from poker.util import tools
from poker.util import strutil, webpage
import freetime.util.log as ftlog
from freetime.entity.msg import MsgPack
from poker.protocol import router
from poker.entity.dao import gamedata
from poker.entity.configure import configure, pokerconf, gdata
from hall.entity.hallconf import HALL_GAMEID
from hall.entity.todotask import (TodoTaskHelper,
                                  TodoTaskGotoShop,
                                  TodoTaskBindInviter,
                                  )

DEBUG = True


def on_check_inviter_before_goto_shop(userId, clientId):
    """玩家点商城后，判断是否要让用户先绑定代理邀请码再去商城"""
    conf = _get_conf_by_client_id(clientId)
    if not conf:  # 没配，不需要检查
        _goto_shop(userId)
        return

    inviter = gamedata.getGameAttr(HALL_GAMEID, userId, 'inviter_code')
    if not inviter:
        _pop_bind_inviter_window(userId)
    else:
        _goto_shop(userId)


def on_bind_inviter(userId, clientId, inviterCode):
    """处理玩家绑定代理邀请码的请求"""
    ftlog.debug("on_bind_inviter <<|userId, clientId, inviterCode:",
                userId, clientId, inviterCode)

    conf = _get_conf_by_client_id(clientId)
    card_type = conf['itemId']
    url = conf['url']
    ret_code, ret_msg = _http_bind(url, card_type, userId, inviterCode)
    ftlog.debug("on_bind_inviter |userId, clientId, inviterCode:",
                userId, clientId, inviterCode,
                "| ret_code, ret_msg:", ret_code, ret_msg)

    mo = MsgPack()
    mo.setCmd('bind_inviter')

    if ret_code == 1:
        # 绑定代理商邀请码后赠送房卡
        giftTips = ''
        giftItemNum = conf.get('giftItemNumOnBind', 0)
        if giftItemNum > 0:
            from hall.entity import hallitem, datachangenotify
            assetKindId = 'item:%s' % card_type
            userAssets = hallitem.itemSystem.loadUserAssets(userId)
            userAssets.addAsset(HALL_GAMEID, assetKindId, giftItemNum, pktimestamp.getCurrentTimestamp(), 'BIND_AGENT_GIFT', 0)
            datachangenotify.sendDataChangeNotify(HALL_GAMEID, userId, 'item')
            giftTips = '，并赠送给您%s张房卡' % giftItemNum

        tips = '您已成功绑定邀请码为%s的代理%s。' % (inviterCode, giftTips)
        pkmessage.send(HALL_GAMEID, pkmessage.MESSAGE_TYPE_SYSTEM, userId, tips, 0)

        gamedata.setGameAttr(HALL_GAMEID, userId, 'inviter_code', inviterCode)
        mo.setResult('bound', True)
        mo.setResult('tips', tips)
        router.sendToUser(mo, userId)
        _goto_shop(userId)
    else:
        mo.setResult('bound', False)
        mo.setResult('tips', ret_msg)
        router.sendToUser(mo, userId)


def _pop_bind_inviter_window(userId):
    """给客户端弹出输入邀请码界面"""
    tips = configure.getGameJson(HALL_GAMEID, "inviter_shop")['bind_tips']
    task = TodoTaskBindInviter(tips)
    TodoTaskHelper.sendTodoTask(HALL_GAMEID, userId, task)


def _goto_shop(userId):
    """让客户端转到商城界面"""
    toStoreTodotask = TodoTaskGotoShop('inviter_shop')
    TodoTaskHelper.sendTodoTask(HALL_GAMEID, userId, toStoreTodotask)


def _get_conf_by_card_type(card_type):
    """通过房卡id获取代理代理商场配置。 card_type: int，房卡id。比如 6113 """
    for conf in configure.getGameJson(HALL_GAMEID, "inviter_shop")['conf']:
        if conf['itemId'] == card_type:
            return conf
    return {}


def _get_conf_by_client_id(clientId):
    """通过client id获取代理代理商场配置"""
    int_client_id = pokerconf.clientIdToNumber(clientId)
    for conf in configure.getGameJson(HALL_GAMEID, "inviter_shop")['conf']:
        if int_client_id in conf['clientIds']:
            return conf
    return {}


def get_url_by_card_type(card_type):
    """通过房卡id获取代理后台的 url"""
    return _get_conf_by_card_type(card_type).get('url')


def get_url_by_client_id(client_id):
    """通过clientid获取代理后台的 url"""
    return _get_conf_by_client_id(client_id).get('url')


def _get_web(params, url=None):
    """http调用代理后台底层接口"""

    card_type = params['cardType']
    if not url:
        url = get_url_by_card_type(card_type)

    response = {}
    has_error = True

    for i in range(3):
        try:
            response, _ = webpage.webget(url, params,
                                         appKey="sales.shediao.com-api-",
                                         appKeyTail="-sales.shediao.com-api",
                                         codeKey='sign', filterParams=['act'],
                                         connector='',connect_timeout=10,
                                         timeout=10)
            if response is None:
                ftlog.error("webget response is None|retry:", i,
                            "|url, params:", url, params)
                continue

            has_error = False
            break
        except Exception as e:
            ftlog.error("webget Exception|url, params:", url, params)

    if has_error:
        return -10, "网络异常导致购买失败，请联系客服"

    if DEBUG:
        ftlog.info("webget |url, params:", url, params, "|response:", response)

    response = strutil.loads(response)

    return response['retcode'], response['retmsg']


def _http_bind(url, card_type, uid, invite_code):
    """http调用代理后台，绑定代理邀请码"""

    return _get_web({
        'act': 'api.playerBind',
        'cardType': card_type,
        'userId': uid,
        'invideCode': invite_code,
    }, url)


def _http_check_enough(card_type, uid):
    """http调用代理后台，检查代理卡够不够"""

    return _get_web({
        'act': 'api.buyCardBalance',
        'cardType': card_type,
        'userId': uid,
    })


def _http_buy(card_type, uid, count, rmb):
    """http调用代理后台，检查代理卡是否够。如果够，扣代理房卡，加房卡给玩家"""

    return _get_web({
        'act': 'api.buyCards',
        'cardType': card_type,
        'userId': uid,
        'cards': count,
        'amount': rmb,
    })


def _get_fangka_count(uid, card_type, userAssets=None):
    """获取玩家的房卡剩余数量"""

    assetKindId = 'item:%s' % card_type
    timestamp = pktimestamp.getCurrentTimestamp()
    if not userAssets:
        from hall.entity import hallitem
        userAssets = hallitem.itemSystem.loadUserAssets(uid)
    return userAssets.balance(9999, assetKindId, timestamp)


class TYBuyConditionFangkaEnough(TYBuyCondition):
    """
    检查邀请人（代理）的房卡库存是否够
    用户购买商品时，由于房卡product使用了这个条件，所以sdk会发起请求：
        /v2/game/consume/transaction
    到 game http，这时这个条件会被调用。

    后来发现用户请求商品列表时也会触发这些检查。所以这里加个判断，只有在http服务才执行
    """

    TYPE_ID = 'fangkaEnough'

    def __init__(self):
        super(self.__class__, self).__init__()
        self.itemId = None

    def check(self, userId, product):
        if gdata.serverType() != "HT":
            return True

        ret_code, ret_msg = _http_check_enough(self.itemId, userId)

        if ftlog.is_debug():
            ftlog.debug('TYBuyConditionFangkaEnough.check userId=', userId,
                        'productId=', product.productId,
                        'itemId=', self.itemId,
                        'ret_code=', ret_code,
                        'ret_msg=', ret_msg)

        if ret_code != 1:
            raise TYStoreException(ret_code, ret_msg)

        return True


    def _decodeFromDictImpl(self, d):
        itemId = d.get('itemId')

        if not isinstance(itemId, int) or itemId <= 0:
            raise TYStoreConfException(d, 'TYBuyConditionFangkaEnough.itemId '
                                          'must be int and > 0. ')

        self.itemId = itemId
        return self


class TYAssetKindDifangFangka(TYAssetKind):
    """
    房卡资产

    搞这个东西，目的是在发货时可以去代理后台检查房卡是不是够。
    如果不这么搞就必须去修改 poker 中的发货代码。
    """

    TYPE_ID = 'difang.fangka'

    def __init__(self):
        super(self.__class__, self).__init__()

    def add(self, gameId, userAssets, kindId, count, timestamp, eventId,
            intEventParam, roomId=0, tableId=0, roundId=0, param01=0, param02=0):

        assert (count >= 0)
        assert(eventId == "BUY_PRODUCT")
        userId = userAssets.userId

        ftlog.info("kindId, count, intEventParam:", kindId, count, intEventParam)

        # intProductId = intEventParam
        # productId = configure.numberToStringId("poker:map.productid", intProductId)
        # product = hallstore.storeSystem.findProduct(productId)
        # priceRmb = float(product.priceDiamond) / 10

        from hall.entity import hallitem, datachangenotify
        from freetime.core.tasklet import FTTasklet
        curr_tasklet = FTTasklet.getCurrentFTTasklet()
        order = curr_tasklet.order
        priceRmb = float(order.product.priceDiamond) / 10

        cardType = int(kindId.split(':')[1])
        final = before = _get_fangka_count(userId, cardType, userAssets)
        ret_code, ret_msg = _http_buy(cardType, userId, count, priceRmb)

        if ret_code == 1:
            itemKind = hallitem.itemSystem.findItemKind(cardType)
            if not itemKind:
                ftlog.error('TYAssetKindDifangFangka.add |itemKind not found',
                            '|userId:', userId, 'kindId:', kindId,
                            'cardType:', cardType, 'count:', count)
                return before

            userBag = userAssets.getUserBag()
            userBag.addItemUnitsByKind(gameId, itemKind, count, timestamp, 0,
                                       eventId, intEventParam,
                                       roomId=roomId, tableId=tableId, roundId=roundId, param01=param01, param02=param02)
            datachangenotify.sendDataChangeNotify(gameId, userId, 'item')
            tools.callLater(5, datachangenotify.sendDataChangeNotify, gameId, userId, 'item')
            tools.callLater(10, datachangenotify.sendDataChangeNotify, gameId, userId, 'item')

            final = _get_fangka_count(userId, cardType, userAssets)

        ftlog.info('TYAssetKindDifangFangka.add gameId=', gameId,
                    'userId=', userId,
                    'kind=', kindId,
                    'count=', count,
                    'timestamp=', timestamp,
                    'eventId=', eventId,
                    'intEventParam=', intEventParam,
                    'ret_code=', ret_code,
                    'ret_msg=', ret_msg,
                   'before=', before,
                   'final=', final
                    )

        if ret_code != 1:
            raise TYBizException(ret_code, ret_msg)

        return final
