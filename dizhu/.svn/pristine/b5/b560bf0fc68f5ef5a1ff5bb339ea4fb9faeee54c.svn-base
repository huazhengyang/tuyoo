# -*- coding=utf-8 -*-
'''
Created on 2016-07-18
dizhu.entity.erdayi
@author: luwei
'''
from datetime import datetime
import random
from sre_compile import isstring
import time

from dizhu.entity import dizhuconf
from dizhu.entity.dizhuconf import DIZHU_GAMEID
from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from hall.entity import hallitem
from hall.entity.todotask import TodoTaskPopTip, TodoTaskHelper
from hall.servers.util.rpc import user_remote
import poker.entity.biz.message.message as pkmessage
from poker.entity.dao import daobase
import poker.entity.dao.userdata as pkuserdata
from poker.protocol import router
from poker.util import strutil, webpage
from poker.entity.configure import gdata


class ErrorEnum(object):
    # 第三方错误代码
    ERR_OK                                  = 0     # 正常
    ERR_NO_BIND_IDNUMBER                    = 1     # 此玩家没有绑定身份证号
    ERR_REPEATED_RESULT                     = 2     # 重复的对局结果上报失败
    ERR_ALREADY_BIND_IDNUMBER               = 3     # 绑定身份信息时出错,已经绑定身份证号码
    ERR_IDNUMBER_USED_BY_OTHER              = 4     # 绑定身份信息时出错,身份证号码已被其他用户绑定
    ERR_NO_BIND_BANK_ACCOUNT                = 5     # 没有绑定银行卡
    ERR_WALLET_BALANCE_NOT_ENOUGH           = 6     # 钱包余额不足
    ERR_IDNUMBER_NOT_MATCH                  = 7     # 身份证号不匹配
    ERR_RANK_NUMBER_MUST_GREATER_THAN_ONE   = 8     # 排名必须大于等于1
    ERR_WALLET_NOT_EXIST                    = 9     # 钱包不存在
    ERR_NOT_ACHIEVE_SIGNIN_CONDITION        = 10    # 未达到报名要求
    ERR_WITHDRAW_OVER_LIMIT                 = 11    # 超出取现次数限制
    ERR_BANK_ACCOUNT_AlREADY                = 12    # 绑定银行卡信息时出错,已经绑定银行卡
    ERR_BANK_ACCOUNT_USED_BY_OTHER          = 13    # 定银行卡信息时出错,银行卡已被其他用户绑定
    ERR_WITHDRAW_FAILED                     = 14    # 提现失败
    ERR_BAD_IDNUMBER                        = 15    # 身份证格式错误
     
    ERR_BANK_INFO_NOT_MATCH                 = 16    # 银行信息不匹配
    ERR_MATCH_NOT_EXISTS                    = 17    # 此赛事不存在
    ERR_NOT_BIND_BONUS                      = 18    # 未绑定奖金
    ERR_MATCH_FINISHED                      = 19    # 此赛事已结束
    ERR_MATCH_INVAILED                      = 20    # 此赛事未审核通过
    ERR_PARAMS_FORMAT_ERROR                 = 21    # 参数格式错误 
     
    ERR_API_CLOSED                          = 93    # 接口已关闭
    ERR_REPEATED_REPORT                     = 94    # 重复上报
    ERR_CP_ID                               = 95    # 厂商ID错误
    ERR_TIMESTAMP                           = 96    # 时间戳错误
    ERR_SIGN                                = 97    # 签名错误
    ERR_PARAM_INVAILD                       = 98    # 参数不合法
    ERR_PARAM_NULL                          = 99    # 参数不能为空
    ERR_INNER                               = 100   # 内部错误

    # 自定义错误代码
    ERR_UNKNOWN             = 200 # 未知错误，一般为服务器发生崩溃
    ERR_BAD_USERID          = 201 # 错误的userId参数
    ERR_BAD_SIGN            = 202 # 错误的sign参数
    ERR_BAD_AUTHINFO        = 203 # 错误的autoInfo参数
    
    ERR_BAD_VCODE           = 204 # 错误的验证码
    ERR_EXPIRED_VCODE       = 205 # 验证码已过期

    ERR_BAD_PARAM           = 206 # 错误的参数
    ERR_BAD_MOBILE          = 207 # 错误的手机号码
    ERR_NO_REALINFO         = 208 # 未认证
    
    ERR_WITHDRAW_BALANCE_NOT_ENOUGH  = 209 # 余额太少
    ERR_WITHDRAW_PROCESSING          = 210 # 提现处理中
    
    ERR_SEND_SMS            = 211 # 短信发送失败
    ERR_NO_RET              = 212 # 无返回值

    
errorinfoTranslate = {
    ErrorEnum.ERR_OK                                  : None,
    ErrorEnum.ERR_NO_BIND_IDNUMBER                    : '此玩家没有绑定身份证号',
    ErrorEnum.ERR_REPEATED_RESULT                     : None,
    ErrorEnum.ERR_ALREADY_BIND_IDNUMBER               : '已绑定身份证号码',
    ErrorEnum.ERR_IDNUMBER_USED_BY_OTHER              : '身份证号码已被其他用户绑定',
    ErrorEnum.ERR_NO_BIND_BANK_ACCOUNT                : '未绑定银行卡',
    ErrorEnum.ERR_WALLET_BALANCE_NOT_ENOUGH           : '钱包余额不足',
    ErrorEnum.ERR_IDNUMBER_NOT_MATCH                  : '身份证号不匹配',
    ErrorEnum.ERR_RANK_NUMBER_MUST_GREATER_THAN_ONE   : None,
    ErrorEnum.ERR_WALLET_NOT_EXIST                    : None,
    ErrorEnum.ERR_NOT_ACHIEVE_SIGNIN_CONDITION        : '未达到报名要求',
    ErrorEnum.ERR_WITHDRAW_OVER_LIMIT                 : '超出取现次数限制',
    ErrorEnum.ERR_BANK_ACCOUNT_AlREADY                : '绑定银行卡信息时出错,已经绑定银行卡',
    ErrorEnum.ERR_BANK_ACCOUNT_USED_BY_OTHER          : '绑定银行卡信息时出错,银行卡已被其他用户绑定',
    ErrorEnum.ERR_WITHDRAW_FAILED                     : '提现失败',
    ErrorEnum.ERR_BAD_IDNUMBER                        : '身份证格式错误',    
    ErrorEnum.ERR_BANK_INFO_NOT_MATCH                 : '银行信息不匹配',
    ErrorEnum.ERR_MATCH_NOT_EXISTS                    : '此赛事不存在',
    ErrorEnum.ERR_NOT_BIND_BONUS                      : '未绑定奖金',
    ErrorEnum.ERR_MATCH_FINISHED                      : '此赛事已结束',
    ErrorEnum.ERR_MATCH_INVAILED                      : '此赛事未审核通过',
    ErrorEnum.ERR_PARAMS_FORMAT_ERROR                 : '参数不合法', 
    
    ErrorEnum.ERR_API_CLOSED                          : None,
    ErrorEnum.ERR_REPEATED_REPORT                     : None,
    ErrorEnum.ERR_CP_ID                               : None,
    ErrorEnum.ERR_TIMESTAMP                           : None,
    ErrorEnum.ERR_SIGN                                : None,
    ErrorEnum.ERR_PARAM_INVAILD                       : "参数不合法",
    ErrorEnum.ERR_PARAM_NULL                          : "参数不合法",
    ErrorEnum.ERR_INNER                               : '服务器忙',
    
    ErrorEnum.ERR_UNKNOWN             : '未知错误',
    ErrorEnum.ERR_BAD_USERID          : None,
    ErrorEnum.ERR_BAD_SIGN            : None,
    ErrorEnum.ERR_BAD_AUTHINFO        : None,
    
    ErrorEnum.ERR_BAD_VCODE           : '验证码无效',
    ErrorEnum.ERR_EXPIRED_VCODE       : '验证码已过期',

    ErrorEnum.ERR_BAD_PARAM           : None,
    ErrorEnum.ERR_BAD_MOBILE          : '手机号码不合法',
    ErrorEnum.ERR_NO_REALINFO         : '未认证',
    
    ErrorEnum.ERR_WITHDRAW_BALANCE_NOT_ENOUGH  : '提现失败，余额大于等于2元时才可提现',
    ErrorEnum.ERR_WITHDRAW_PROCESSING     : '奖金提现审核处理中',
    
    ErrorEnum.ERR_SEND_SMS            : '验证码发送失败',
    ErrorEnum.ERR_NO_RET              : None

}

class SDKInterface(object):
    @classmethod
    def _sign(cls, params):
        sk = sorted(params.keys())
        strs = ['%s=%s' % (k, params[k]) for k in sk]
        md5str = strutil.tyDesEncode('&'.join(strs))
        return strutil.md5digest(md5str)

    @classmethod
    def _requestSdkUrl(cls, url, params, needresponse=False):
        params['code'] = cls._sign(params)
        jsonstr, _ = webpage.webget(url, postdata_=params, needresponse=needresponse)
        if needresponse :
            try:
                data = strutil.loads(jsonstr)
                return data['result']
            except:
                ftlog.error()
                return ErrorEnum.ERR_UNKNOWN
        return None

    @classmethod
    def sendSms(cls, userId, mobile, content):
        params = {
            'userId':userId,
            'mobile':mobile,
            'content':content
        }
        httpsdk = gdata.httpSdkInner()
        url = httpsdk+'/open/v4/user/sendSms2User'
        resp = cls._requestSdkUrl(url, params, True)
        ftlog.debug('SDKInterface.sendSms:',
                    'userId=', userId,
                    'mobile=', mobile,
                    'content=', content,
                    'url=', url,
                    'resp=', resp)
        if resp == ErrorEnum.ERR_UNKNOWN:
            return {'code':ErrorEnum.ERR_UNKNOWN}
        return resp

def buildStampStr():
    return str(int(time.time() * 1000))
#     now = datetime.now()
#     return now.strftime('%Y%m%d%H%M%S') + str(int(now.microsecond/1000))

class HttpGetRequest(object):
        
    @classmethod
    def _buildSign(cls, params, secret):
        '''（utf-8编码）
        1.根据参数名排序
        2.参数名和参数值拼装
        3.计算md5值，并转为16进制大写字符串表示
        @param params: 除了sign之外，其他的所有参数
        '''
        param_keys = params.keys()
        param_keys.sort()
        params_joined = ''
        for key in param_keys:
            params_joined += key + str(params[key])
        params_joined += secret
        return strutil.md5digest(params_joined.encode('utf-8')).upper()
    
    @classmethod
    def _get(cls, url, querys):
        ftlog.debug('HttpGetRequest._get:begin',
                    'url=', url,
                    'querys=', querys)
        jsonstr, _ = webpage.webget(url, querys=querys, method_='GET')
        ftlog.debug('HttpGetRequest._get:end',
                    'jsonstr=', jsonstr)
        return jsonstr

    @classmethod
    def request(cls, host, path, params_get={}, secret=None, stampstr=None):
        '''
        自动生成sign参数
        @param host: 
        @param path: /player/identity_number/bind
        @param params_get: get参数
        @param secret: 计算签名使用的secret
        @param stampstr: '20171010010101000'
        '''
        url = host + path
        secret = secret or PlayerControl.getConf('3rdapi.token')
        params = params_get or {}
        params['timestamp'] = stampstr or buildStampStr()
        params['sign'] = cls._buildSign(params, secret)
        ftlog.debug('HttpGetRequest.request:',
                    'requrl=', url,
                    'params=', params)
        return cls._get(url, params)

class HttpPostRequest(object):
    @classmethod
    def _buildSign(cls, path, body, stampstr, secret):
        params_joined = path + body + stampstr + secret
        return strutil.md5digest(params_joined.encode('utf-8')).upper()
    
    @classmethod
    def _post(cls, url, headers, body):
        ftlog.debug('HttpPostRequest._post:begin',
                    'url=', url,
                    'headers=', headers,
                    'body=', body)
        jsonstr, _ = webpage.webget(url, headers_=headers, postdata_=body)
        ftlog.debug('HttpPostRequest._post:end',
                    'jsonstr=', jsonstr)
        return jsonstr

    @classmethod
    def request(cls, host, path, params_post={}, secret=None, stampstr=None):
        '''
        自动在header中添加timestamp和sign参数
        '''
        body = strutil.dumps(params_post)
        secret = secret or PlayerControl.getConf('3rdapi.token')
        stampstr = stampstr or buildStampStr()
        headers = {
            'Accept':['application/json'],
            'timestamp': [stampstr],
            'sign': [cls._buildSign(path, body, stampstr, secret)]
        }
        
        return cls._post(host + path, headers, body)

class Erdayi3rdInterface(object):
    '''
    二打一第三方接口集合
    '''
    @classmethod
    def translateResponse(cls, response):
        ftlog.debug('Erdayi3rdInterface.translateResponse:begin',
                    'response=', response)
        try:
            if not response:
                return { 'resp_code': ErrorEnum.ERR_NO_RET }
            response = strutil.loads(response)
            if not response:
                return { 'resp_code': ErrorEnum.ERR_NO_RET }
            respcode = str(response.get('resp_code', ''))
            response['resp_code'] = int(respcode if len(respcode) > 0 else 0)
        except:
            ftlog.error('Erdayi3rdInterface.translateResponse:', 
                        'response=', response)
            response = {
                'resp_code': ErrorEnum.ERR_UNKNOWN, 
                'resp_msg': None
            }
        ftlog.debug('Erdayi3rdInterface.translateResponse:end',
                    'response=', response)
        return response
    
    @classmethod
    def playerIdentityNumberBind(cls, player_id, real_name, player_id_number, player_mobile):
        '''
        身份证绑定接口
        POST:player/identity_number/bind                          
        @param player_id String: 用户ID 
        @param real_name String: 玩家真实名字
        @param player_id_number String: 玩家身份证号
        @param player_mobile String: 玩家手机号
        @return {
            'resp_code': 0,
            'resp_msg':'SUCCESS'
        }
        '''
        host = PlayerControl.getConf('3rdapi.host')
        path = '/player/identity_number/bind'
        params = {
            'cp_id': str(PlayerControl.getConf('3rdapi.cpid')),
            'player_id': str(player_id),
            'real_name': real_name,
            'player_id_number': str(player_id_number),
            'player_mobile': str(player_mobile)
        }
        ftlog.debug('playerIdentityNumberBind',
                    'userId=', player_id,
                    'params=', params,
                    'url=', host + path)
        response = HttpPostRequest.request(host, path, params)
        return cls.translateResponse(response)
    
    @classmethod
    def playerBankAccountBind(cls, player_id, bank_no, bank_name, bank_account):
        '''
        银行卡绑定接口                
        POST:player/bank_acc/bind      
        @param player_id String: 用户ID
        @param bank_no String: 银行编号
        @param bank_name String: 银行名称
        @param bank_account String: 银行账号
        @return {
            'resp_code': 0,
            'resp_msg':'SUCCESS'
        }
        '''
        host = PlayerControl.getConf('3rdapi.host')
        path = '/player/bank_acc/bind'
        params = {
            'cp_id': str(PlayerControl.getConf('3rdapi.cpid')),
            'player_id': str(player_id),
            'bank_no': str(bank_no),
            'bank_name': bank_name,
            'bank_account':str(bank_account)
        }
        ftlog.debug('playerBankAccountBind',
                    'userId=', player_id,
                    'params=', params,
                    'url=', host + path)
        response = HttpPostRequest.request(host, path, params)
        return cls.translateResponse(response)
    
    @classmethod
    def playerBonousWithdraw(cls, player_id, player_id_number):
        '''
        玩家提现接口
        POST:player/bonous/withdraw                               
        @param player_id String: 用户ID
        @param player_id_number String: 玩家身份证号
        @return: {
            'resp_code': 0,
            'resp_msg':'SUCCESS',
            'cp_id':'厂商ID',
            'player_id': '玩家',
            'act_money': '100'
        }
        '''
        host = PlayerControl.getConf('3rdapi.host')
        path = '/player/bonous/withdraw'
        params = {
            'cp_id': str(PlayerControl.getConf('3rdapi.cpid')),
            'player_id': str(player_id),
            'player_id_number': str(player_id_number)
        }
        ftlog.debug('playerBonousWithdraw',
                    'userId=', player_id,
                    'params=', params,
                    'url=', host + path)
        response = HttpPostRequest.request(host, path, params)
        return cls.translateResponse(response)
    
    @classmethod
    def walletBalance(cls, player_id):
        '''
        用户钱包账户余额查询接口
        GET:wallet/balance
        @param player_id String: 用户ID
        @return: {
            'resp_code': 0,
            'resp_msg': '操作成功',
            'cp_id':'0',
            'player_id':'0',
            'money':'10',
            'status':1,
            'result_list':[
                { 'match_id':'12323', 'ranking': '10', 'bonus': '100', 'status': 0, }
            ],
        }
        '''
        host = PlayerControl.getConf('3rdapi.host')
        path = '/wallet/balance'
        params = {
            'cp_id': str(PlayerControl.getConf('3rdapi.cpid')),
            'player_id': str(player_id),
        }
        ftlog.debug('walletBalance',
                    'userId=', player_id,
                    'params=', params,
                    'url=', host + path)
        response = HttpGetRequest.request(host, path, params)
        return cls.translateResponse(response)
        
    @classmethod
    def ratingByIdentityNumber(cls, player_id_number):
        '''
        大师分查询
        GET:rating/by_identity_number                
        @param player_id_number String: 玩家身份证号码
        @return: {
            'resp_code': 0,
            'resp_msg': '操作成功',
            'ranking':'1',
            'player_id':'0',
            'level_name':'大师',
            'g': '10',
            's': '1',
            'r': '100'
        }
        '''
        host = PlayerControl.getConf('3rdapi.host')
        path = '/rating/by_identity_number'
        params = {
            'cp_id': str(PlayerControl.getConf('3rdapi.cpid')),
            'player_id_number': str(player_id_number),
        }
        ftlog.debug('ratingByIdentityNumber',
                    'player_id_number=', player_id_number,
                    'params=', params,
                    'url=', host + path)
        response = HttpGetRequest.request(host, path, params)
        return cls.translateResponse(response)

class PlayerData(object):
    
    @classmethod
    def save(cls, userId, key, data):
        rpath = 'erdayi:6:' + str(userId)
        daobase.executeUserCmd(userId, 'hset', rpath, key, strutil.dumps(data))
        
    @classmethod
    def load(cls, userId, key):
        rpath = 'erdayi:6:' + str(userId)
        d = daobase.executeUserCmd(userId, 'hget', rpath, key)
        if d:
            return strutil.loads(d)
        return d

    @classmethod
    def setRealInfo(cls, userId, data):
        '''
        牌手认证信息
        '''
        cls.save(userId, 'realInfo', data)
    
    @classmethod
    def getRealInfo(cls, userId):
        '''
        牌手认证信息
        '''
        return cls.load(userId, 'realInfo')

    @classmethod
    def setBankInfo(cls, userId, data):
        '''
        银行卡绑定信息
        '''
        cls.save(userId, 'bankInfo', data)
    
    @classmethod
    def getBankInfo(cls, userId):
        '''
        银行卡绑定信息
        '''
        return cls.load(userId, 'bankInfo')

    @classmethod
    def setVCode(cls, userId, data):
        '''
        验证码信息
        '''
        cls.save(userId, 'vcode', data)
    
    @classmethod
    def getVCode(cls, userId):
        '''
        验证码信息
        '''
        return cls.load(userId, 'vcode')

    @classmethod
    def setWithdraw(cls, userId, data):
        '''
        提现信息
        '''
        cls.save(userId, 'withdraw', data)
    
    @classmethod
    def getWithdraw(cls, userId):
        '''
        提现信息
        '''
        return cls.load(userId, 'withdraw')

class PlayerControl(object):
    
    @classmethod
    def getConf(cls, key, default=None):
        return dizhuconf.getPublic().get('erdayi.misc', {}).get(key, default) 
    
    @classmethod
    def sendPopTip(cls, userId, text):
        todotask = TodoTaskPopTip(text)
        mo = TodoTaskHelper.makeTodoTaskMsg(DIZHU_GAMEID, userId, todotask)
        router.sendToUser(mo, userId)

    @classmethod
    def makeResponse(cls, userId, code=0, respmsg=None, notip=False):
        """
        @param notip: 不发送Tip提示
        """
        if code != ErrorEnum.ERR_OK and respmsg:
            ftlog.info('PlayerControl.makeResponse:',
                        'userId=', userId,
                        'code=', code,
                        'respmsg=', respmsg)

        mo = MsgPack()
        mo.setResult("code", code)
                
        # 获取错误码定义的错误提示信息
        errinfo = errorinfoTranslate.get(code)
                    
        # 定制错误信息
        if code == None:
            errinfo = respmsg
        elif code == ErrorEnum.ERR_WITHDRAW_BALANCE_NOT_ENOUGH:
            errinfo = cls.getConf('withdraw_money_toofew_errinfo')
        elif code == ErrorEnum.ERR_WITHDRAW_PROCESSING:
            errinfo = cls.getConf('withdraw_wait_errinfo')
        
        if errinfo:
            mo.setResult('info', errinfo)
            if not notip:
                cls.sendPopTip(userId, errinfo)
        return mo
    
    @classmethod
    def _sendAuthReawrd(cls, userId):
        """发送认证奖励"""
        assets = cls.getConf('auth_reward')
        if ftlog.is_debug():
            ftlog.debug('PlayerControl._sendAuthReawrd',
                        'userId=', userId,
                        'assets=', assets)
        if assets:
            contentItems = [{'itemId':assets.get('itemId'), 'count':assets.get('count')}]
            if user_remote.addAssets(DIZHU_GAMEID, userId, contentItems, 'ERDAYI_AUTH_REWARD', 0):
                ftlog.info('PlayerControl._sendAuthReawrd Succ',
                           'userId=', userId,
                           'assets=', assets)
                rewardDesc = hallitem.buildContent(assets.get('itemId'), assets.get('count'), False)
                mail = strutil.replaceParams(cls.getConf('auth_reward_mail'), {'reward_desc':rewardDesc})
                pkmessage.sendPrivate(9999, userId, 0, mail)
                cls.sendPopTip(userId, mail)
            else:
                ftlog.warn('PlayerControl._sendAuthReawrd Fail',
                           'userId=', userId,
                           'assets=', assets)

    @classmethod
    def getVCode(cls, userId, mobile):
        '''
        获取验证码
        '''
        # 随机一个验证码，注意验证码位数
        vcode = random.randint(1000, 9999) # 四位的验证码
        
        # 格式化短信内容
        vcode_expiryminute = cls.getConf('vcode_expiryminute', 10)
        vcode_content = cls.getConf('vcode_content')
        content = strutil.replaceParams(vcode_content, {'vcode': vcode, 'vcode_expiryminute':vcode_expiryminute})
        
        # 发送短信
        resp = SDKInterface.sendSms(userId, mobile, content)
        resp_code = resp.get('code', ErrorEnum.ERR_OK)
        resp_info = resp.get('info')
        ftlog.debug('PlayerControl.getVCode:',
                    'userId=', userId,
                    'resp_code=', resp_code,
                    'resp_info=', resp_info)
        if resp_code != ErrorEnum.ERR_OK:
            return cls.makeResponse(userId, ErrorEnum.ERR_SEND_SMS)
        
        # 记录验证码信息
        data = {
            'vcode': vcode,
            'stamp': time.time()
        }
        PlayerData.setVCode(userId, data)
        
        # 给玩家返回信息
        response = cls.makeResponse(userId)
        # response.setResult('vcode', vcode)
        return response
    
    @classmethod
    def bindRealInfo(cls, userId, realname, idNo, mobile, vcode):
        '''
        认证接口
        '''
        ftlog.debug('PlayerControl.bindRealInfo:params',
                    'userId=', userId,
                    'realname=', realname,
                    'idNo=', idNo,
                    'mobile=', mobile,
                    'vcode=', vcode)            
        # 1.先取得存储的验证码
        data = PlayerData.getVCode(userId)
        if not data or data.get('vcode',0) == 0:
            return cls.makeResponse(userId, ErrorEnum.ERR_BAD_VCODE)
        
        # 2.验证码是否过期
        vcode_expiryminute = cls.getConf('vcode_expiryminute', 10) # 验证码有效期
        vcode_stamp = data.get('stamp', 0)
        vcode_endstamp = vcode_stamp + vcode_expiryminute*60
        current_stamp = time.time()
        ftlog.debug('PlayerControl.bindRealInfo',
                    'userId=', userId,
                    'vcode_expiryminute=', vcode_expiryminute,
                    'vcode_endstamp=', vcode_endstamp,
                    'current_stamp=', current_stamp)
        if vcode_endstamp < current_stamp:
            return cls.makeResponse(userId, ErrorEnum.ERR_EXPIRED_VCODE)
        if vcode != data.get('vcode'):
            return cls.makeResponse(userId, ErrorEnum.ERR_BAD_VCODE)

        # 销毁验证码，防止重复使用
        PlayerData.setVCode(userId, {
            'vcode': 0,
            'stamp': 0
        })

        # 3.第三方接口认证
        response3rd = Erdayi3rdInterface.playerIdentityNumberBind(userId, realname, idNo, mobile)
        resp_code = response3rd.get('resp_code')
        resp_msg = response3rd.get('resp_msg')
        ftlog.info('PlayerControl.bindRealInfo:Erdayi3rdInterface',
                    'userId=', userId,
                    'resp_code=', resp_code,
                    'resp_msg=', resp_msg,
                    'response3rd=', response3rd)
                
        # 4.绑定成功，则存储牌手认证信息
        if resp_code == ErrorEnum.ERR_OK:
            # 记录玩家认证信息
            player_realinfo = {
                'idNo': idNo,
                'mobile': mobile,
                'realname': realname
            }
            PlayerData.setRealInfo(userId, player_realinfo)
            # 认证奖励发送
            cls._sendAuthReawrd(userId)
            response = cls.makeResponse(userId)
            response.setResult('realInfo', player_realinfo)
            return response
        else:
            return cls.makeResponse(userId, resp_code, resp_msg)
        
    @classmethod
    def bindBankAccount(cls, userId, bankNo, bankName, bankAccount):
        '''
        绑定银行卡
        * 必须先进行玩家认证
        '''
        ftlog.debug('PlayerControl.bindBankAccount:params',
                    'userId=', userId,
                    'bankNo=', bankNo,
                    'bankName=', bankName,
                    'bankAccount=', bankAccount)

        # 1.验证玩家认证信息
        realinfo = PlayerData.getRealInfo(userId)
        if not realinfo:
            return cls.makeResponse(userId, ErrorEnum.ERR_NO_REALINFO)
        
        # 1.第三方接口绑定
        response3rd = Erdayi3rdInterface.playerBankAccountBind(userId, bankNo, bankName, bankAccount)
        resp_code = response3rd.get('resp_code')
        resp_msg = response3rd.get('resp_msg')
        ftlog.info('PlayerControl.bindBankAccount:Erdayi3rdInterface',
                    'userId=', userId,
                    'resp_code=', resp_code,
                    'resp_msg=', resp_msg,
                    'response3rd=', response3rd)

        # 2.绑定成功，则存储银行卡信息
        if resp_code == ErrorEnum.ERR_OK:
            player_bankinfo = {
                'bankNo': bankNo,
                'bankName': bankName,
                'bankAccount': bankAccount
            }
            PlayerData.setBankInfo(userId, player_bankinfo)
            response = cls.makeResponse(userId)
            response.setResult('bank', player_bankinfo)
            cls.sendPopTip(userId, cls.getConf('bind_bank_success_tip'))
            return response
        else:
            return cls.makeResponse(userId, resp_code, resp_msg)
    
    @classmethod
    def withdraw(cls, userId):
        '''
        玩家提现
        * 必须玩家认证->绑定银行卡，之后才能提现
        '''
        ftlog.info('PlayerControl.withdraw:params',
                    'userId=', userId)

        # 1.获取玩家认证信息，获取身份证号码
        realinfo = PlayerData.getRealInfo(userId)
        if not realinfo:
            info = cls.getConf('withdraw_need_realinfo_errinfo')
            cls.sendPopTip(userId, info)
            return cls.makeResponse(userId, ErrorEnum.ERR_NO_REALINFO, info, True)
        idNo = realinfo.get('idNo')
        if not idNo:
            info = cls.getConf('withdraw_need_realinfo_errinfo')
            ftlog.info('PlayerControl.withdraw:Erdayi3rdInterface userId=', userId, 'errInfo=', info,
                       'err= withdraw_need_realinfo_errinfo')
            return cls.makeResponse(userId, ErrorEnum.ERR_NO_BIND_IDNUMBER, info)
        
        # 2.查看玩家是否绑定银行卡
        bankinfo = PlayerData.getBankInfo(userId)
        if not bankinfo:
            info = cls.getConf('withdraw_need_bankinfo_errinfo')
            cls.sendPopTip(userId, info)
            ftlog.info('PlayerControl.withdraw:Erdayi3rdInterface userId=', userId,
                       'errInfo=', info, 'err= withdraw_need_bankinfo_errinfo')
            return cls.makeResponse(userId, ErrorEnum.ERR_NO_REALINFO, info, True)
        
        # 2.先查看玩家余额是否足够
        wallet_resp = cls.getWalletInfo(userId)
        wallet_resp_code = wallet_resp.getResult('code')
        withdraw_money_lowat = cls.getConf('withdraw_money_lowat')
        if wallet_resp_code != ErrorEnum.ERR_OK:
            ftlog.info('PlayerControl.withdraw:Erdayi3rdInterface userId=', userId,
                       'wallet_resp_code=', wallet_resp_code,
                       'withdraw_money_lowat=', withdraw_money_lowat,
                       'err=', 'withdraw_money_lowat')
            return cls.makeResponse(userId, wallet_resp_code, wallet_resp.getResult('info'))

        walletinfo = wallet_resp.getResult('wallet', {})
        if withdraw_money_lowat > float(walletinfo.get('money', 0)):
            ftlog.info('PlayerControl.withdraw:Erdayi3rdInterface userId=', userId,
                       'walletinfo=', walletinfo,
                       'withdraw_money_lowat=', withdraw_money_lowat,
                       'err=', 'withdraw_money_lowat')
            return cls.makeResponse(userId, ErrorEnum.ERR_WITHDRAW_BALANCE_NOT_ENOUGH)

        
        # 3.查看上次领取时间，领取存在24小时的冷却时间
        waittime = cls.getConf('withdraw_wait', 24*60*60)
        withdrawinfo = PlayerData.getWithdraw(userId)
        if withdrawinfo:
            laststamp = withdrawinfo.get('laststamp', 0)
            if time.time() - laststamp < waittime:
                ftlog.info('PlayerControl.withdraw:Erdayi3rdInterface userId=', userId,
                           'withdrawinfo=', withdrawinfo,
                           'laststamp=', laststamp,
                           'waitTime=', waittime,
                           'err=', 'withdraw must cooling 24hours')
                return cls.makeResponse(userId, ErrorEnum.ERR_WITHDRAW_PROCESSING)

        # 3.第三方接口
        response3rd = Erdayi3rdInterface.playerBonousWithdraw(userId, idNo)
        resp_code = response3rd.get('resp_code')
        resp_msg = response3rd.get('resp_msg')
        act_money = response3rd.get('act_money', '0.0')
        ftlog.info('PlayerControl.withdraw:Erdayi3rdInterface',
                    'userId=', userId,
                    'resp_code=', resp_code,
                    'resp_msg=', resp_msg,
                    'act_money=', act_money,
                    'response3rd=', response3rd)

        # 4.提现成功受理
        if resp_code == ErrorEnum.ERR_OK:
            # 记录提现成功受理的时间
            withdrawinfo = {'laststamp':time.time()}
            PlayerData.setWithdraw(userId, withdrawinfo)
            
            # 发送提现成功受理的tip
            tip = cls.getConf('withdraw_accept_tip')
            cls.sendPopTip(userId, tip)
            pkmessage.sendPrivate(9999, userId, 0, tip)
            
            response = cls.makeResponse(userId)
            response.setResult('money', act_money)
            return response
        else:
            tip = cls.getConf('withdraw_failed_tip')
            cls.sendPopTip(userId, tip)
            pkmessage.sendPrivate(9999, userId, 0, tip)
            
            return cls.makeResponse(userId, resp_code, resp_msg, True)
        
    @classmethod
    def translateTrade(cls, typeNumber):
        # 比赛奖金/奖金提现/提现失败/奖金解绑
        transmap = {
            1: '比赛奖金',
            2: '奖金提现',
            3: '提现失败',
            4: '奖金解绑',
        }
        return transmap.get(int(typeNumber), '未知')
   
    @classmethod
    def getWalletInfo(cls, userId):
        '''
        获得钱包信息
        * 不需要玩家认证
        '''
        wallet_resp = Erdayi3rdInterface.walletBalance(userId)
        resp_code = wallet_resp.get('resp_code')
        resp_msg = wallet_resp.get('resp_msg')
        ftlog.debug('PlayerControl.getWalletInfo:',
                    'userId=', userId,
                    'resp_code=', resp_code,
                    'resp_msg=', resp_msg,
                    'wallet_resp=', wallet_resp)
        if resp_code == ErrorEnum.ERR_OK:
            resultList = []
            for item in wallet_resp.get('result_list', []):
                # 时间：XX-XX XX：XX（例如08-01 10:15）
                # 类型：比赛奖金/奖金提现/提现失败/奖金解绑
                # 金额：4位数+2位小数
                ts = item.get('trans_time')
                dt = None
                if ts:
                    dt = datetime.strptime(ts, '%Y-%m-%d %H:%M:%S')
                resultList.append({
                    'transTime': dt.strftime('%m-%d %H:%M') if dt else '',
                    'transType': cls.translateTrade(item.get('trans_type', 0)),
                    'transAnt': '%.2f' % float(item.get('trans_amt', 0)),
                    'remark': item.get('remark', '无')
                })

            walletinfo = {
                'money': wallet_resp.get('money', '0.0'),
                'status': wallet_resp.get('status', 1),
                'resultList':resultList
            }
            response = cls.makeResponse(userId, resp_code, resp_msg)
            response.setResult('wallet', walletinfo) 
            return response
        else:
            return cls.makeResponse(userId, resp_code, resp_msg)  
    
    @classmethod
    def getMasterInfo(cls, userId):
        '''
        获取大师分信息
        * 必须玩家认证之后才能获取
        '''
        realinfo = PlayerData.getRealInfo(userId)
        if realinfo and realinfo.get('idNo'):
            masterResponse = Erdayi3rdInterface.ratingByIdentityNumber(realinfo.get('idNo'))
            resp_code = masterResponse.get('resp_code')
            resp_msg = masterResponse.get('resp_msg')
            ftlog.debug('PlayerControl.getMasterInfo:',
                    'userId=', userId,
                    'resp_code=', resp_code,
                    'resp_msg=', resp_msg,
                    'masterResponse=', masterResponse)
            if resp_code == ErrorEnum.ERR_OK:
                masterinfo = {
                    'ranking': masterResponse.get('ranking', 0),
                    'levelName': masterResponse.get('level_name', '无'),
                    'g': masterResponse.get('g', '0.0'),
                    's': masterResponse.get('s', '0.0'),
                    'r': masterResponse.get('r', '0.0'),
                }
                response = cls.makeResponse(userId)
                response.setResult('rating', masterinfo)
                return response
            else:
                return cls.makeResponse(userId, resp_code, resp_msg)
        else:
            return cls.makeResponse(userId, ErrorEnum.ERR_NO_REALINFO)
      
    @classmethod
    def getInfo(cls, userId):
        '''
        牌手信息
        '''
        ftlog.debug('PlayerControl.getInfo:params',
                    'userId=', userId)
        response = cls.makeResponse(userId)
        
        # 1.获取玩家认证信息，获取身份证号码
        realinfo = PlayerData.getRealInfo(userId)
        
        # 2.获取玩家银行卡信息
        bankinfo = PlayerData.getBankInfo(userId)
            
        # 3.获得玩家大师分信息
        masterinfo = None
        if realinfo and realinfo.get('idNo'):
            master_resp = cls.getMasterInfo(userId)
            master_resp_code = master_resp.getResult('code')
            master_resp_msg = master_resp.getResult('info')
            masterinfo = master_resp.getResult('rating')
            if master_resp_code != ErrorEnum.ERR_OK:
                response = cls.makeResponse(userId, master_resp_code, master_resp_msg, True)
    
        # 4.获得玩家钱包信息，需要玩家认证才能获取
        walletinfo = None
        if realinfo:
            wallet_resp = cls.getWalletInfo(userId)
            wallet_resp_code = wallet_resp.getResult('code')
            wallet_resp_msg = wallet_resp.getResult('info')
            walletinfo = wallet_resp.getResult('wallet')
            if wallet_resp_code != ErrorEnum.ERR_OK:
                response = cls.makeResponse(userId, wallet_resp_code, wallet_resp_msg, True)

        # 组装
        if realinfo:
            response.setResult('realInfo', realinfo)
        if bankinfo:
            response.setResult('bank', bankinfo)
        if masterinfo:
            response.setResult('rating', masterinfo)
        if walletinfo:
            response.setResult('wallet', walletinfo)
        
        # 附加字段
        response.setResult('authRewardDesc', cls.getConf('auth_reward_desc'))
        
        bindMobile = pkuserdata.getAttr(userId, 'bindMobile')
        if isstring(bindMobile) and len(bindMobile) > 0:
            response.setResult('bindedMobile', bindMobile)
        
        return response
