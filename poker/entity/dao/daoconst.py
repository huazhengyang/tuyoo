# -*- coding: utf-8 -*-
"""
Created on 2015-5-12
@author: zqh
"""
from poker.entity.dao import dataschema
from poker.util import city_locator
OFFLINE = 0
ONLINE = 1
ATT_CHIP = 'chip'
ATT_COIN = 'coin'
ATT_DIAMOND = 'diamond'
ATT_COUPON = 'coupon'
ATT_TABLE_CHIP = 'tablechip'
ATT_EXP = 'exp'
ATT_CHARM = 'charm'
ATT_NAME = 'name'
ATT_TRU_NAME = 'truename'
ATT_TABLE_ID = 'tableId'
ATT_SEAT_ID = 'seatId'
ATT_CLIENT_ID = 'clientId'
ATT_APP_ID = 'appId'
HKEY_USERDATA = 'user:'
HKEY_GAMEDATA = 'gamedata:'
HKEY_STATEDATA = 'statedata:'
HKEY_ONLINE_STATE = 'os:'
HKEY_ONLINE_LOC = 'ol:'
HKEY_PLAYERDATA = 'playerdata:'
HKEY_TABLECHIP = 'tablechip:'
HKEY_TABLEDATA = 'tabledata:%d:%d'
FILTER_KEYWORD_FIELDS = {ATT_NAME, ATT_TRU_NAME}
FILTER_MUST_FUNC_FIELDS = {ATT_CHIP, ATT_DIAMOND, ATT_COIN, ATT_COUPON, ATT_CHARM}
OLD_COUPON_ITEMID = '50'
VIP_ITEMID = '88'
CHIP_NOT_ENOUGH_OP_MODE_NONE = 0
CHIP_NOT_ENOUGH_OP_MODE_CLEAR_ZERO = 1
CHIP_TYPE_CHIP = 1
CHIP_TYPE_TABLE_CHIP = 2
CHIP_TYPE_COIN = 3
CHIP_TYPE_DIAMOND = 4
CHIP_TYPE_COUPON = 5
CHIP_TYPE_ITEM = 6
CHIP_TYPE_ALL = (CHIP_TYPE_CHIP, CHIP_TYPE_TABLE_CHIP, CHIP_TYPE_COIN, CHIP_TYPE_DIAMOND, CHIP_TYPE_COUPON, CHIP_TYPE_ITEM)
DATA_CACHE_SIZE = 600
BI_KEY_GCOIN = 'GCOIN:%s'
BI_KEY_USER_ONLINES = 'count:user:onlines'
BI_KEY_ROOM_ONLINES = 'count:room:onlines%d'

@dataschema.redisDataSchema
class GameGeoSchema(dataschema.DataSchema, ):
    REDIS_KEY = 'offline_geo:%d'

@dataschema.redisDataSchema
class GameItemSchema(dataschema.DataSchema, ):
    REDIS_KEY = 'item2:%d:%d'

@dataschema.redisDataSchema
class GameTaskSchema(dataschema.DataSchema, ):
    REDIS_KEY = 'task2:%d:%d'

@dataschema.redisDataSchema
class GameExchangeSchema(dataschema.DataSchema, ):
    REDIS_KEY = 'eo:%d:%d'
ONLINE_KEY_ALLKEYS = 'onlinelist_allkeys'
ONLINE_KEY_USERS = 'onlinelist:users'
ONLINE_KEY_LIST = 'onlinelist:%s:%s'
PAY_KEY_CTY = 'cty:%s:%s'
PAY_KEY_EXCHANGE_ID = 'global.exchangeId'
PAY_KEY_GAME_ORDER_ID = 'global.gameOrderid'

@dataschema.redisDataSchema
class GameOrderSchema(dataschema.DataSchema, ):
    REDIS_KEY = 'gameOrder:%s'
    ORDERID = ('orderId', dataschema.DATA_TYPE_STR, '')
    PLATFORMORDERID = ('platformOrderId', dataschema.DATA_TYPE_STR, '')
    USERID = ('userId', dataschema.DATA_TYPE_INT, 0)
    GAMEID = ('gameId', dataschema.DATA_TYPE_INT, 0)
    REALGAMEID = ('realGameId', dataschema.DATA_TYPE_INT, 0)
    PRODID = ('prodId', dataschema.DATA_TYPE_STR, '')
    COUNT = ('count', dataschema.DATA_TYPE_INT, 0)
    CREATETIME = ('createTime', dataschema.DATA_TYPE_INT, 0)
    UPDATETIME = ('updateTime', dataschema.DATA_TYPE_INT, 0)
    CLIENTID = ('clientId', dataschema.DATA_TYPE_STR, '')
    STATE = ('state', dataschema.DATA_TYPE_INT, 0)
    ERRORCODE = ('errorCode', dataschema.DATA_TYPE_INT, 0)
    CHARGEINFO = ('chargeInfo', dataschema.DATA_TYPE_DICT, {})

@dataschema.redisDataSchema
class UserOnlineGameSchema(dataschema.DataSchema, ):
    REDIS_KEY = 'og:%d'

@dataschema.redisDataSchema
class UserLocationSchema(dataschema.DataSchema, ):
    REDIS_KEY = 'ol:%d'
    SEATID = ('seatId', dataschema.DATA_TYPE_INT, 0)

@dataschema.redisDataSchema
class UserWeakSchema(dataschema.DataSchema, ):
    REDIS_KEY = 'weak:%s:%s:%d:%d'

@dataschema.redisDataSchema
class UserPlayTimeSchema(dataschema.DataSchema, ):
    REDIS_KEY = 'pt:%d'

@dataschema.redisDataSchema
class UserSessionSchema(dataschema.DataSchema, ):
    """
    用户主数据,类型:HASH
    """
    REDIS_KEY = 'session:%d'
    """
    在游戏当中使用的数据字段
    """
    ONLINE_STATE = ('os', dataschema.DATA_TYPE_BOOLEAN, OFFLINE)
    LAST_GAME = ('lg', dataschema.DATA_TYPE_INT, 0)
    CLIENTID = ('ci', dataschema.DATA_TYPE_STR, '')
    IPADDRESS = ('ip', dataschema.DATA_TYPE_STR, '')
    APPID = ('appId', dataschema.DATA_TYPE_INT, 0)
    DEVICEID = ('devId', dataschema.DATA_TYPE_STR, '')
    CITYCODE = ('city', dataschema.DATA_TYPE_LIST, city_locator.DEFAULT_LOCATION)
    CONN = ('conn', dataschema.DATA_TYPE_STR, '')
    FIELD_GROUP_SESSION = (CLIENTID, IPADDRESS, APPID, DEVICEID, CITYCODE, CONN)

@dataschema.redisDataSchema
class UserDataSchema(dataschema.DataSchema, ):
    """
    用户主数据,类型:HASH
    """
    REDIS_KEY = 'user:%d'
    """
    在游戏当中使用的数据字段
    """
    CHIP = ('chip', dataschema.DATA_TYPE_INT_ATOMIC, 0)
    COIN = ('coin', dataschema.DATA_TYPE_INT_ATOMIC, 0)
    DIAMOND = ('diamond', dataschema.DATA_TYPE_INT_ATOMIC, 0)
    COUPON = ('coupon', dataschema.DATA_TYPE_INT_ATOMIC, 0)
    EXP = ('exp', dataschema.DATA_TYPE_INT_ATOMIC, 0)
    CHARM = ('charm', dataschema.DATA_TYPE_INT_ATOMIC, 0)
    EXCHANGED_COUPON = ('exchangedCoupon', dataschema.DATA_TYPE_INT, 0)
    NAME = ('name', dataschema.DATA_TYPE_STR_FILTER, '')
    SEX = ('sex', dataschema.DATA_TYPE_BOOLEAN, 0)
    ADDRESS = ('address', dataschema.DATA_TYPE_STR, '')
    PURL = ('purl', dataschema.DATA_TYPE_STR, '')
    SNSID = ('snsId', dataschema.DATA_TYPE_STR, '')
    VIP360 = ('360.vip', dataschema.DATA_TYPE_STR, '')
    VIP = ('vip', dataschema.DATA_TYPE_INT, 0)
    CREATETIME = ('createTime', dataschema.DATA_TYPE_STR, '')
    CHARGETOTAL = ('chargeTotal', dataschema.DATA_TYPE_FLOAT, 0.0)
    PAYCOUNT = ('payCount', dataschema.DATA_TYPE_INT, 0)
    FIRSTDAILYCHECKIN = ('firstDailyCheckin', dataschema.DATA_TYPE_INT, 0)
    LASTDAILYCHECKIN = ('lastDailyCheckin', dataschema.DATA_TYPE_INT, 0)
    SET_NAME_SUM = ('set_name_sum', dataschema.DATA_TYPE_INT, 0)
    SENDMEGIFT = ('sendMeGift', dataschema.DATA_TYPE_INT, 0)
    ISYOUYIFUVIPUSER = ('isYouyifuVipUser', dataschema.DATA_TYPE_BOOLEAN, 0)
    YOUYIFUVIPMSG = ('youyifuVipMsg', dataschema.DATA_TYPE_STR, '')
    USEDALIPAY = ('used_alipay', dataschema.DATA_TYPE_INT, 0)
    SETNAME = ('setName', dataschema.DATA_TYPE_INT, 0)
    SETPURL = ('setPurl', dataschema.DATA_TYPE_INT, 0)
    SETSEX = ('setSex', dataschema.DATA_TYPE_INT, 0)
    EMAIL = ('email', dataschema.DATA_TYPE_STR, '')
    PDEVID = ('pdevid', dataschema.DATA_TYPE_STR, '')
    MDEVID = ('mdevid', dataschema.DATA_TYPE_STR, '')
    ISBIND = ('isbind', dataschema.DATA_TYPE_INT, 0)
    SOURCE = ('source', dataschema.DATA_TYPE_STR, '')
    SNSINFO = ('snsinfo', dataschema.DATA_TYPE_STR, '')
    DAYANG = ('dayang', dataschema.DATA_TYPE_INT, 0)
    IDCARDNO = ('idcardno', dataschema.DATA_TYPE_STR, '')
    TRUENAME = ('truename', dataschema.DATA_TYPE_STR, '')
    PHONENUMBER = ('phonenumber', dataschema.DATA_TYPE_STR, '')
    DETECT_PHONENUMBER = ('detect_phonenumber', dataschema.DATA_TYPE_STR, '')
    LANG = ('lang', dataschema.DATA_TYPE_STR, '')
    COUNTRY = ('country', dataschema.DATA_TYPE_STR, '')
    SIGNATURE = ('signature', dataschema.DATA_TYPE_STR, '')
    BEAUTY = ('beauty', dataschema.DATA_TYPE_INT, 0)
    PASSWORD = ('password', dataschema.DATA_TYPE_STR, '')
    BINDMOBILE = ('bindMobile', dataschema.DATA_TYPE_STR, '')
    CHIP_EXP = ('chip_exp', dataschema.DATA_TYPE_INT_ATOMIC, 0)
    CHIP_LEVEL = ('chip_level', dataschema.DATA_TYPE_INT, 0)
    """
    SESSION数据字段
    """
    SESSION_APPID = ('sessionAppId', dataschema.DATA_TYPE_INT, 0)
    SESSION_DEVID = ('sessionDevId', dataschema.DATA_TYPE_STR, '')
    SESSION_CLIENTID = ('sessionClientId', dataschema.DATA_TYPE_STR, '')
    SESSION_IP = ('sessionClientIP', dataschema.DATA_TYPE_STR, '')
    SESSION_CITY_CODE = ('city_code', dataschema.DATA_TYPE_LIST, city_locator.DEFAULT_LOCATION)
    FIELD_GROUP_SESSION = (SESSION_CLIENTID, SESSION_IP, SESSION_APPID, SESSION_DEVID, SESSION_CITY_CODE, 'conn_dummy')
    """
    再SDK中使用的数据字段或老旧的数据字段
    """
    CHANGEPWDCOUNT = ('changePwdCount', dataschema.DATA_TYPE_INT, 0)
    STATE = ('state', dataschema.DATA_TYPE_INT, 0)
    USERACCOUNT = ('userAccount', dataschema.DATA_TYPE_STR, '')
    CLIENTID = ('clientId', dataschema.DATA_TYPE_STR, '')
    APPID = ('appId', dataschema.DATA_TYPE_INT, 0)
    MAC = ('mac', dataschema.DATA_TYPE_STR, '')
    IDFA = ('idfa', dataschema.DATA_TYPE_STR, '')
    IMEI = ('imei', dataschema.DATA_TYPE_STR, '')
    ANDROIDID = ('androidId', dataschema.DATA_TYPE_STR, '')
    UUID = ('uuid', dataschema.DATA_TYPE_STR, '')
    USERID = ('userId', dataschema.DATA_TYPE_INT, 0)
    AGREEADDFRIEND = ('agreeAddFriend', dataschema.DATA_TYPE_BOOLEAN, 0)
    STARID = ('starid', dataschema.DATA_TYPE_INT, 0)
    NEITUIGUANG_STATE = ('neituiguang:state', dataschema.DATA_TYPE_INT, 0)
    AUTHORTOKEN = ('authorToken', dataschema.DATA_TYPE_STR, '')