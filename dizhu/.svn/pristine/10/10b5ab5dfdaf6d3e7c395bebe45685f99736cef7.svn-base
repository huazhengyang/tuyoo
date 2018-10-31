# -*- coding:utf-8 -*-
"""
夺宝模块
"""
import json
import copy
import random
import freetime.util.log as ftlog
from freetime.util.log import catchedmethod
from poker.util import timestamp as pktimestamp
from freetime.entity.msg import MsgPack
from poker.protocol import router
import poker.entity.events.tyeventbus as pkeventbus
from poker.entity.configure import configure, gdata
from poker.entity.events.tyevent import EventConfigure
from poker.entity.dao import daobase
from poker.entity.biz.exceptions import TYBizConfException, TYBizException
from poker.entity.biz.item.item import TYAssetUtils
from poker.entity.biz.content import TYContentRegister
from poker.util import tools
from hall.entity import hallitem, datachangenotify
from dizhu.entity.dizhuconf import DIZHU_GAMEID


_inited = False  # 初始化标志位
DUOBAO_KEY = 'ddz_duobao'     # 当前各个产品的夺宝数据key  hash
DUOBAO_INDEX_KEY = 'ddz_duobao:index'    # 各产品的夺宝序号 hash
DUOBAO_FEE_KEY = 'ddz_duobao:fee:%s:%s'  # 投注费用key  hash
DUOBAO_RECORD_KEY = 'ddz_duobao:record:%d'  # 夺宝记录key hash
DUOBAO_USER_BET_CODE_KEY = 'ddz_duobao:code:user:%s:%s'  # 玩家投注的夺宝码数据key hash
DUOBAO_BET_USER_KEY = 'ddz_duobao:bet:user:%s:%s'  # 夺宝用户key list
DUOBAO_CODE_KEY = 'ddz_duobao:code:%s'   # 夺宝码key hash


def mix_db(*args):
    return daobase.executeMixCmd(*args)


def fee_key(product_id, issue_no):
    return DUOBAO_FEE_KEY % (product_id, issue_no)


def user_code_key(product_id, issue_no):
    return DUOBAO_USER_BET_CODE_KEY % (product_id, issue_no)


def bet_user_key(product_id, issue_no):
    return DUOBAO_BET_USER_KEY % (product_id, issue_no)


def code_key(product_id):
    return DUOBAO_CODE_KEY % product_id


def record_key(product_id):
    return DUOBAO_RECORD_KEY % product_id


def get_cur_product_data():
    """获取当前产品的夺宝数据"""
    res = mix_db("HGETALL", DUOBAO_KEY)
    if not res:
        return {}
    return dict(tools.pairwise(res))


def get_product_data(product_id):
    return mix_db("HGET", DUOBAO_KEY, int(product_id))


def set_duobao_attrs(data_list):
    mix_db("HMSET", DUOBAO_KEY, *data_list)


@catchedmethod
def set_duobao_attr(product_id, attr_key, attr_val):
    product_info_str = get_product_data(product_id)
    product_data = json.loads(product_info_str)
    product_data[attr_key] = attr_val
    product_info_str = json.dumps(product_data)
    mix_db("HSET", DUOBAO_KEY, product_id, product_info_str)


def product_cur_issue_index(product_id):
    return mix_db("HGET", DUOBAO_INDEX_KEY, product_id)


def inc_product_issue_index(product_id):
    return mix_db("HINCRBY", DUOBAO_INDEX_KEY, product_id, 1)


def get_products_from_redis():
    """从redis获取当前的所有product_id及当前期号"""
    return tools.pairwise(mix_db("HGETALL", DUOBAO_INDEX_KEY))


def get_issue_fees(product_id, issue_no):
    """获取issue_no这期的投注费用"""
    return tools.pairwise(mix_db("HGETALL", fee_key(product_id, issue_no)))


def get_issue_fees_by_uid(uid, product_id, issue_no):
    return mix_db("HGET", fee_key(product_id, issue_no), uid)


def set_issue_fees_by_uid(uid, product_id, issue_no, fees_list):
    mix_db("HSET", fee_key(product_id, issue_no), uid, json.dumps(fees_list))


@catchedmethod
def add_issue_fees(product_id, issue_no, uid, add_fees):
    o_fees_str = get_issue_fees_by_uid(uid, product_id, issue_no)
    all_fees = [add_fees]
    if o_fees_str:
        all_fees.extend(json.loads(o_fees_str))

    set_issue_fees_by_uid(uid, product_id, issue_no, all_fees)


def del_keys(key_list):
    """删除已经处理(退费)过的key"""
    if not isinstance(key_list, list):
        return
    mix_db("DEL", *key_list)


def get_user_code_list(product_id, issue_no, uid):
    """
    获取用户夺宝码信息
    @return:
    """
    ret = []
    ret_str = mix_db("HGET", user_code_key(product_id, issue_no), uid)
    if not ret_str:
        return ret
    try:
        ret = json.loads(ret_str)
    except:
        ftlog.error('user_bet data err | uid', uid, ret_str)

    return ret


def add_bet_users(product_id, issue_no, uid_list):
    return mix_db("RPUSH", bet_user_key(product_id, issue_no), *uid_list)


def total_bet_count(product_id, issue_no):
    """获取某个夺宝期的总投注人数"""
    return mix_db("LLEN", bet_user_key(product_id, issue_no))


def get_bet_uid_by_index(product_id, issue_no, index):
    return mix_db("LINDEX", bet_user_key(product_id, issue_no), index)


def is_exist_bet_user_key(product_id, issue_no):
    return mix_db("EXISTS", bet_user_key(product_id, issue_no))


def inc_code_index(product_id, issue_no, delta=1):
    return mix_db("HINCRBY", code_key(product_id), issue_no, delta)


def set_record_attr(product_id, attr, val):
    return mix_db("HSET", record_key(product_id), attr, val)


def is_exists_record_attr(product_id, attr):
    return mix_db("HEXISTS", record_key(product_id), attr)


def gen_code_list(product_id, issue_no, count=1):
    code_index = inc_code_index(product_id, issue_no, count)
    prefix = '1' + '%03s' % gdata.serverNum()[-3:]
    return [prefix + ('%06d' % i) for i in range(code_index-count+1, code_index+1)]


@catchedmethod
def save_user_bet_codes(product_id, issue_no, uid, code_list):
    """存储用户的夺宝码"""
    if not isinstance(code_list, list):
        ftlog.warn('save_user_bet_codes err|',
                   product_id, issue_no, uid, code_list)
        return
    data_str = json.dumps(code_list)
    mix_db("HSET", user_code_key(product_id, issue_no), uid, data_str)


def add_user_item(uid, item_id, count, product_id, issue_no):
    """道具调整接口
    因gameId及服务器环境不一样,eventId就复用之前的夺宝活动
    issue_no 期号,去掉前缀后的整型 通过product_id可以确认是哪一器
    """
    timestamp = pktimestamp.getCurrentTimestamp()
    userAssets = hallitem.itemSystem.loadUserAssets(uid)
    assetKind, consumedCount, final = userAssets.addAsset(DIZHU_GAMEID,
                                                          item_id,
                                                          count,
                                                          timestamp,
                                                          'HALL_DUOBAO_COST',
                                                          int(product_id),
                                                          int(issue_no))

    ftlog.info('duobao.add_user_item',
               'gameId=', DIZHU_GAMEID,
               'userId=', uid,
               'fee=', (item_id, count),
               'consumedCount=', consumedCount,
               'product_id=', product_id,
               'issue_no=', issue_no)

    if assetKind.keyForChangeNotify:
        changes = TYAssetUtils.getChangeDataNames([(assetKind, consumedCount,
                                                    final)])
        datachangenotify.sendDataChangeNotify(DIZHU_GAMEID, uid, changes)


def add_content_item_list(uid, content):
    timestamp = pktimestamp.getCurrentTimestamp()
    userAssets = hallitem.itemSystem.loadUserAssets(uid)
    assetList = userAssets.sendContent(DIZHU_GAMEID, content, 1, True,
                                       timestamp, 'HALL_DUOBAO_COST', 0)
    ftlog.debug('duobao._send_rewards',
                'userId=', uid,
                'assets=', [(atup[0].kindId, atup[1]) for atup in assetList])
    changed = TYAssetUtils.getChangeDataNames(assetList)
    datachangenotify.sendDataChangeNotify(DIZHU_GAMEID, uid, changed)


def consume_user_item(uid, item_id, count, product_id, issue_no):
    """扣某个道具"""
    timestamp = pktimestamp.getCurrentTimestamp()
    userAssets = hallitem.itemSystem.loadUserAssets(uid)
    _, consume_count, final = userAssets.consumeAsset(DIZHU_GAMEID,
                                                      item_id,
                                                      count,
                                                      timestamp,
                                                      'HALL_DUOBAO_COST',
                                                      int(product_id),
                                                      int(issue_no))
    if consume_count < consume_count:
        return False

    return True


def consume_content_item_list(uid, content):
    """通过FixedCount方式扣费"""
    content_item_list = content.getItems()
    timestamp = pktimestamp.getCurrentTimestamp()
    userAssets = hallitem.itemSystem.loadUserAssets(uid)
    assetList = userAssets.consumeContentItemList(DIZHU_GAMEID,
                                                  content_item_list,
                                                  False,
                                                  timestamp,
                                                  'HALL_DUOBAO_COST', 0)
    if assetList:
        return True
    return False


def multi_items(items_conf, multi):
    items_conf_cp = copy.deepcopy(items_conf)
    for item in items_conf_cp["items"]:
        item["count"] *= multi
    return items_conf_cp


def _build_multi_fixedcontent(items_conf, multi):
    """构建FixedContent"""
    multi_items_conf = multi_items(items_conf, multi)

    return TYContentRegister.decodeFromDict(multi_items_conf)


@catchedmethod
def return_fees_and_del_key(product_id, issue_no, issue_fees):
    """根据redis中的fees进行退费"""
    need_del_keys = []
    for uid, fee_items_str in issue_fees:
        fee_items = json.loads(fee_items_str)
        if not isinstance(fee_items, list):
            ftlog.warn('duobao.return_fees | uid', uid, fee_items_str)
            continue
        for fee_item in fee_items:
            add_user_item(uid, fee_item["itemId"], fee_item["count"],
                          product_id, issue_no)
        need_del_keys.append(fee_key(product_id, issue_no))
        need_del_keys.append(bet_user_key(product_id, issue_no))

        if ftlog.is_debug():
            ftlog.debug('return_fees product_id', product_id,
                        'uid', uid, fee_items_str)

    if need_del_keys:
        del_keys(need_del_keys)


def choose_winner_and_code(product_id, issue_no, total_bet):
    """
    选择中奖者及中奖夺宝码
    @return: uid(中奖用户id), code(中奖码), user_bet_count(中奖用户投入次数)
    """
    for _ in range(5):  # 如果找人失败,最多找五次
        choose_index = random.randint(0, total_bet-1)
        uid = get_bet_uid_by_index(product_id, issue_no, choose_index)
        code_list = get_user_code_list(product_id, issue_no, uid)
        if not code_list:
            ftlog.warn('choose_winner_and_code | not find user code',
                       uid, 'index', choose_index)
            continue
        else:
            return uid, random.sample(code_list, 1)[0], len(code_list)

    return 0, '', 0


def parse_product_json_str(data_str):
    """解析redis中取到的数据"""
    try:
        ret = json.loads(data_str)
    except:
        ret = {}

    return ret


class DuoBaoData(object):
    conf = {}
    product_map = {}    # 产品map {product_id: product_obj}
    products_conf = []  # 产品配置

    @classmethod
    def _build_issue_data(cls, issue_no, product, start_time):
        """构建产品当前期数据"""
        product_dict = copy.deepcopy(product.__dict__)
        product_dict['issue_no'] = issue_no
        product_dict['start_time'] = start_time
        filter_fields = ["product_id", "days", "fee_items"]
        for filter_field in filter_fields:
            if filter_field not in product_dict:
                continue
            del product_dict[filter_field]
        return product_dict

    @classmethod
    def _gen_one_product_issue(cls, product_id):
        """
        根据产品当前期的夺宝期号,生成初始数据
        @return:
        """
        product = cls.product_map.get(product_id)
        if not product:
            return '', 0
        issue_no = product_cur_issue_index(product_id)
        if not issue_no:
            issue_no = inc_product_issue_index(product_id)
        if issue_no > product.issue_limit:
            return '', 0

        start_time = pktimestamp.getCurrentTimestamp()
        issue_data = cls._build_issue_data(issue_no, product, start_time)
        return json.dumps(issue_data), issue_no

    @classmethod
    def settlement(cls, product_id, issue_no, total_bet):
        """结算"""
        # 抽奖
        uid, code, user_bet = choose_winner_and_code(product_id,
                                                     issue_no, total_bet)
        if not uid or not code:
            fees = get_issue_fees(product_id, issue_no)
            return_fees_and_del_key(product_id, issue_no, fees)
            # 重新开一个, 初始化
            issue_data_str, issue_no = cls._gen_one_product_issue(product_id)
            if not issue_data_str:  # 出错, 一般不会出现这种情况
                timestamp = pktimestamp.getCurrentTimestamp()
                set_duobao_attr(product_id, 'end_time', timestamp)
                ftlog.warn('_on_timeout _gen_one_product_issue err |',
                           product_id, issue_data_str, issue_no)
                return
            data = [product_id, issue_data_str]
            set_duobao_attrs(data)
        else:
            # 存储中奖信息,删除及更新旧数据
            data_str = json.dumps({
                "uid": uid,
                "code": code,
                "total": total_bet,
                "user_bet": user_bet,
            })
            # 存储中奖信息
            set_record_attr(product_id, issue_no, data_str)
            # 发奖
            reward_items = cls.product_map[product_id].reward_info["items"]
            reward_content = _build_multi_fixedcontent(reward_items, 1)
            add_content_item_list(uid, reward_content)
            # 删除旧数据生成新一期夺宝数据
            cls.gen_one_new_product_issue(product_id, issue_no)

    @classmethod
    def gen_one_new_product_issue(cls, product_id, issue_no):
        pass


class DuobaoUTServerHelper(object):
    """夺宝协议处理类"""
    ERROR_NONE = 0, ''
    ERROR_BET_NUM = 1, '投注数量不正确'
    ERROR_BET_PRODUCT_ID = 2, '夺宝ID不正确'
    ERROR_ISSUE_NO = 3, '该夺宝活动没有此期号'
    ERROR_ONCE_BET_LIMIT = 4, '您的下注数超过了单次最大下注数'
    ERROR_USER_BET_LIMIT = 5, '您的总下注次数超过了此夺宝个人下注数'
    ERROR_FEE_NOT_ENOUGH = 6, '您的费用不足'
    ERROR_BET_LIMIT = 7, '已经达到最大下注数'
    ERROR_UNKNOWN = 10, '未知错误'

    @classmethod
    def handle_bet(cls, uid, product_id, issue_no, num):
        ec, info, code_list, total_bet = cls.bet(uid, product_id, issue_no, num)
        msg = MsgPack()
        msg.setCmd('dizhu')
        msg.setResult('action', 'duobao_bet')
        msg.setResult('gameId', DIZHU_GAMEID)
        msg.setResult('userId', uid)
        msg.setResult('duobaoId', product_id)
        msg.setResult('issue', issue_no)
        msg.setResult('num', num)
        msg.setResult('ec', ec)
        msg.setResult('info', info)
        msg.setResult('luckyCodeList', code_list)
        msg.setResult('totalBetCount', total_bet)
        router.sendToUser(msg, uid)

    @classmethod
    def bet(cls, uid, product_id, issue_no, num):
        """夺宝下注"""
        if not isinstance(num, int) or num <= 0:
            ftlog.warn('DuobaoUTServerHelper.bet', uid,
                       product_id, issue_no, num)
            return cls.ERROR_BET_NUM, [], 0
        if product_id not in DuoBaoUTServerData.products_dict:
            return cls.ERROR_BET_PRODUCT_ID, [], 0
        product_item = DuoBaoUTServerData.products_dict[product_id]
        product_info_str = get_product_data(product_id)
        if not product_info_str:
            ftlog.warn('DuobaoUTServerHelper.bet | product_info_str err',
                       product_info_str)
            return cls.ERROR_BET_PRODUCT_ID, [], 0
        try:
            product_data = json.loads(product_info_str)
        except:
            ftlog.error('DuobaoUTServerHelper.bet | data not json',
                        product_info_str)
            return cls.ERROR_UNKNOWN, [], 0

        if product_data['issue_no'] != issue_no:
            return cls.ERROR_ISSUE_NO, [], 0

        total_bet = total_bet_count(product_id, issue_no)
        user_code_list = get_user_code_list(product_id, issue_no, uid)
        if num + len(user_code_list) >= product_item['userBetLimit']:
            return cls.ERROR_USER_BET_LIMIT, user_code_list, total_bet

        if num > product_item['onceBetLimit']:
            return cls.ERROR_ONCE_BET_LIMIT, user_code_list, total_bet

        if num + total_bet > product_item['totalBetCount']:
            return cls.ERROR_BET_LIMIT, user_code_list, total_bet

        # 扣费
        fee_content = _build_multi_fixedcontent(product_item["fee"], num)
        if not consume_content_item_list(uid, fee_content):
            return cls.ERROR_FEE_NOT_ENOUGH, user_code_list, total_bet

        # 存储费用
        fee_item = multi_items(product_item["fee"], num)
        if "typeId" in fee_item:
            del fee_item["typeId"]
        # 添加费用到投注费用库里
        add_issue_fees(product_id, issue_no, uid, fee_item)

        # 投注
        code_list = gen_code_list(product_id, issue_no, num)
        all_user_code_list = code_list + user_code_list
        save_user_bet_codes(product_id, issue_no, uid, all_user_code_list)

        # 添加用户到总投注列表中
        total_bet = add_bet_users(product_id, issue_no, [uid]*num)

        # 检查是否满足开奖条件
        DuoBaoUTServerData.check_draw(product_id, issue_no)
        return cls.ERROR_NONE, all_user_code_list, total_bet

    @classmethod
    def handle_get_product_list(cls, uid):
        product_list = cls._get_product_list(uid)
        msg = MsgPack()
        msg.setCmd('dizhu')
        msg.setResult('action', 'duobao_product_list')
        msg.setResult('gameId', DIZHU_GAMEID)
        msg.setResult('userId', uid)
        msg.setResult('productList', product_list)
        router.sendToUser(msg, uid)

    @classmethod
    def _get_product_list(cls, uid):
        product_list = []
        product_data = get_cur_product_data()
        if not product_data:
            return product_list
        for product_id, data_str in product_data.items():
            if product_id not in DuoBaoUTServerData.products_dict:
                continue
            product_item = DuoBaoUTServerData.products_dict[product_id]
            product_dict = parse_product_json_str(data_str)
            if "issue_no" in product_dict:
                issue_no = product_dict["issue_no"]
            else:
                issue_no = product_cur_issue_index(product_id)
            reward_conf = product_item["rewardContent"]
            ret = {
                "productId": product_id,
                "cornerTag": product_item["cornerTag"],
                "shopName": reward_conf.get("desc", ""),
                "shopUrl": reward_conf["pic"],
                "grabType": product_item["type"],
                "issueCur": issue_no,
                "issueTotal": product_item["issueLimit"],
                "weight": product_item["sortId"],  # 排序权重
                "grabCountCur": total_bet_count(product_id, issue_no),  # 当前夺宝次数
                "grabCountLimit": product_item["totalBetCount"],
                "myCodes": get_user_code_list(product_id, issue_no, uid),
                "lastWinner": {
                }
            }
            product_list.append(ret)

        return product_list


class DuoBaoUTServerData(DuoBaoData):
    """UT进程夺宝数据相关类
        1 读取redis数据
        2 内存数据主要包括奖励,
    """
    products_dict = {}  # 产品配置字典 {product_id: product_conf}

    @classmethod
    def initialize(cls):
        cls.reload_conf()
        cls._build_data()

    @classmethod
    def refresh_conf(cls):
        cls.reload_conf()
        cls._build_data()

    @classmethod
    def reload_conf(cls):
        cls.conf = _get_conf()

    @classmethod
    def _build_data(cls):
        if "products" not in cls.conf:
            return
        cls.products_conf = cls.conf["products"]
        for product_item in cls.products_conf:
            cls.products_dict[product_item["id"]] = product_item
            product = DuoBaoProduct().decode_dict(product_item)
            cls.product_map[product_item["id"]] = product

    @classmethod
    def check_draw(cls, product_id, issue_no):
        """检查是否达到开奖
            1. 判断条件
            2. 处理数据
            3. 抽奖发奖
        """
        product_item = cls.products_dict[product_id]
        if product_item['type'] not in (DuoBaoProduct.OPEN_TYPE_USER,
                                        DuoBaoProduct.OPEN_TYPE_USER_OR_TIME):
            return
        total_bet = total_bet_count(product_id, issue_no)
        if total_bet < product_item["totalMinBetCount"]:
            return

        cls.settlement(product_id, issue_no, total_bet)

    @classmethod
    def gen_one_new_product_issue(cls, product_id, cur_issue_no):
        """生成新一期夺宝"""
        inc_product_issue_index(product_id)
        issue_data_str, issue_no = cls._gen_one_product_issue(product_id)
        if issue_data_str and issue_no:
            data = [product_id, issue_data_str]
            set_duobao_attrs(data)

        # 删除旧数据
        need_del_keys = [
            fee_key(product_id, cur_issue_no),
            bet_user_key(product_id, cur_issue_no),
            code_key(product_id),
        ]
        del_keys(need_del_keys)


class DuoBaoCTServerData(DuoBaoData):
    """CT进程夺宝数据相关类
        1. 初始化夺宝数据到redis
        2. 相关夺宝的定时器
        3. 内存放产品相关属性及判断,例如夺宝期号
    """
    timer_map = {}  # 所有限时夺宝的timer,用于查看状态

    @classmethod
    def initialize(cls):
        """CT进程对数据进行初始化"""
        cls.reload_conf()
        cls._build_data()

    @classmethod
    def refresh_conf(cls):
        cls.reload_conf()
        cls._build_data()

    @classmethod
    def reload_conf(cls):
        cls.conf = _get_conf()

    @classmethod
    def _build_data(cls):
        if "products" not in cls.conf:
            return
        cls.products_conf = cls.conf["products"]
        for product_item in cls.products_conf:
            product = DuoBaoProduct().decode_dict(product_item)
            cls.product_map[product_item["id"]] = product
            # cls.products_dict[product_item["id"]] = product_item

    @classmethod
    def return_back_fees(cls):
        product_issues = get_products_from_redis()
        if not product_issues:
            return
        for product_id, issue_no in product_issues:
            fees = get_issue_fees(product_id, issue_no)
            return_fees_and_del_key(product_id, issue_no, fees)

    @classmethod
    def restart_init_data(cls):
        """
        CT进程重启数据初始化
        根据配置及redis中读取当前夺宝数据进行比较
        1. 存在的退还用户投注的费用
        2. 新增的夺宝产品进行数据初始化
        @return:
        """
        cls.initialize()   # 初始化配置
        cls.return_back_fees()  # 退费及删除key
        cls.init_issue_data()   # 初始化各期数据到redis

    @classmethod
    def init_issue_data(cls):
        """根据配置初始化各产品夺宝数据到redis
            1.各产品夺宝的当前期号到 ddz_duobao:index
            2.各产品夺宝当前期信息到 ddz_duobao
            3.初始化之前删除需要清理的key
        """
        data = []
        need_del_keys = []
        for product_id, product in cls.product_map.items():
            issue_data_str, issue_no = cls._gen_one_product_issue(product_id)
            if not issue_data_str:
                continue
            data.append(product_id)
            data.append(issue_data_str)
            need_del_keys.append(fee_key(product_id, issue_no))
            need_del_keys.append(bet_user_key(product_id, issue_no))
            need_del_keys.append(code_key(product_id))
            need_del_keys.append(user_code_key(product_id, issue_no))

            cls._set_issue_timer(product, issue_no)

        del_keys(need_del_keys)  # 删除老数据
        if data:
            set_duobao_attrs(data)

    @classmethod
    def _set_issue_timer(cls, product, issue_no):
        """为限时夺宝产品设置timer
        @param product DuoBaoProduct 实例对象
        """
        if product.type not in (DuoBaoProduct.OPEN_TYPE_TIME,
                                DuoBaoProduct.OPEN_TYPE_USER_OR_TIME):
            return

        interval = product.time_length * 60
        timer = tools.callLater(interval, cls._on_timeout, product, issue_no)
        cls.timer_map[product.product_id] = timer

    @classmethod
    def _on_timeout(cls, product, issue_no):
        """限时夺宝到开奖时间
            1. 判断是否满足最低人数限制
            2. 抽中奖玩家
            3. 判断是否需要开下一期夺宝
        """
        product_id = product.product_id
        total_bet = total_bet_count(product_id, issue_no)
        if total_bet >= product.total_min_bet_count:
            cls.settlement(product_id, issue_no, total_bet, )
        else:  # 人数不够,数据清理,以当前期号继续
            if (not is_exist_bet_user_key(product_id, issue_no)
                    or is_exists_record_attr(product_id, issue_no)):
                if product_id in cls.timer_map:
                    del cls.timer_map[product_id]
                return

            if product.time_length > 0:  # 防止死循环
                cls._set_issue_timer(product, issue_no)

    @classmethod
    def gen_one_new_product_issue(cls, product_id, cur_issue_no):
        """生成新一期夺宝"""
        inc_product_issue_index(product_id)
        issue_data_str, issue_no = cls._gen_one_product_issue(product_id)
        if issue_data_str and issue_no:
            data = [product_id, issue_data_str]
            set_duobao_attrs(data)
            cls._set_issue_timer(cls.product_map[product_id], issue_no)

        #  删除旧数据
        need_del_keys = [
            fee_key(product_id, cur_issue_no),
            bet_user_key(product_id, cur_issue_no),
            code_key(product_id),
        ]
        del_keys(need_del_keys)


class DuoBaoProduct(object):
    """夺宝产品类"""

    OPEN_TYPE_USER = 1  # 人满即开
    OPEN_TYPE_TIME = 2  # 限时开
    OPEN_TYPE_USER_OR_TIME = 3  # 人满开或限时开任意一个满足

    def __init__(self):
        self.product_id = None  # 产品id
        self.type = 0           # 开奖类型
        self.total_min_bet_count = None  # 最低开奖下注数
        self.total_bet_count = None      # 总下注数
        self.user_bet_limit = None       # 玩家一期里最多下注数
        self.once_bet_limit = None       # 玩家单次投注限制次数
        self.issue_limit = None     # 产品总期数
        self.fee_items = None       # 投注费用
        self.reward_info = None     # 奖励
        self.time_length = None     # 限时夺宝的夺宝时长,单位:分钟
        self.days = None            # 开放日期

    def decode_dict(self, d):
        self.product_id = d["id"]
        if not isinstance(self.product_id, int):
            raise TYBizConfException(d, 'DuoBaoProduct.product_id must be int')
        self.type = d["type"]
        if self.type not in (self.OPEN_TYPE_USER, self.OPEN_TYPE_TIME,
                             self.OPEN_TYPE_USER_OR_TIME):
            raise TYBizConfException(d, 'DuoBaoProduct.type error')
        self.total_min_bet_count = d.get("totalMinBetCount", 0)
        if (not isinstance(self.total_min_bet_count, int)
                or self.total_min_bet_count < 0):
            raise TYBizConfException(d, 'totalMinBetCount must >= 0')
        self.total_bet_count = d.get("totalBetCount")
        if (not isinstance(self.total_bet_count, int)
                or (self.total_bet_count < 1 and self.total_bet_count != -1)):
            raise TYBizConfException(d, 'totalBetCount must be int > 0 or -1')
        self.issue_limit = d.get("issueLimit", 1)
        if not isinstance(self.issue_limit, int) or self.issue_limit < 1:
            raise TYBizConfException(d, 'issueLimit must be int > 0')
        self.user_bet_limit = d.get("userBetLimit", 1)
        if not isinstance(self.user_bet_limit, int) or self.user_bet_limit < 1:
            raise TYBizConfException(d, 'maxBetCount must be int > 0')
        self.once_bet_limit = d.get("onceBetLimit", 1)
        if not isinstance(self.once_bet_limit, int) or self.once_bet_limit < 1:
            raise TYBizConfException(d, 'onceBetLimit must be int > 0')
        self.fee_items = d["fee"]["items"]
        if not isinstance(self.fee_items, list):
            raise TYBizConfException(d, 'fee["items"] must be list')

        self.reward_info = d["rewardContent"]
        if (not isinstance(self.reward_info, dict)
                or "items" not in self.reward_info):
            raise TYBizConfException(d, 'rewardContent["items"] error')
        self.time_length = d.get("timeLength", 0)
        if not isinstance(self.time_length, int):
            raise TYBizConfException(d, 'timeLength must be int')
        if (self.type in (self.OPEN_TYPE_TIME, self.OPEN_TYPE_USER_OR_TIME)
                and self.time_length <= 0):
            raise TYBizConfException(d, 'timeLength must be > 0')
        self.days = d.get("days", {})
        if not isinstance(self.days, dict):
            raise TYBizConfException(d, 'days must be dict')

        return self


def on_conf_changed(event):
    if _inited and event.isChanged(['game:6:duobao.segment:0']):
        serverType = gdata.serverType()
        ftlog.debug("duobao.on_conf_changed serverType", serverType)
        if serverType == gdata.SRV_TYPE_UTIL:
            DuoBaoUTServerData.refresh_conf()
        elif serverType == gdata.SRV_TYPE_CENTER:
            DuoBaoCTServerData.refresh_conf()


def _get_conf():
    return configure.getGameJson(DIZHU_GAMEID, "duobao.segment", {})


def initialize():
    global _inited
    if not _inited:
        _inited = True
        serverType = gdata.serverType()
        pkeventbus.globalEventBus.subscribe(EventConfigure, on_conf_changed)
        if serverType == gdata.SRV_TYPE_UTIL:
            DuoBaoUTServerData.initialize()
        elif serverType == gdata.SRV_TYPE_CENTER:
            DuoBaoCTServerData.restart_init_data()