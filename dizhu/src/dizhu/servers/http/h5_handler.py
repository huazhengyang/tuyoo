# -*- coding=utf-8 -*-
'''
Created on 2015年5月7日

@author: zqh
'''
import datetime

import freetime.util.log as ftlog
from dizhu.entity.dizhuconf import DIZHU_GAMEID
from hall.servers.common.base_http_checker import BaseHttpMsgChecker
from poker.protocol import runhttp
from poker.protocol.decorator import markHttpHandler, markHttpMethod
from poker.protocol import router
from freetime.entity.msg import MsgPack
from poker.entity.configure import configure

@markHttpHandler
class YouKuHttpHandler(BaseHttpMsgChecker):

    def __init__(self):
        pass
    
    # def _check_param_taskId(self, key, params):
    #     taskId = runhttp.getParamInt(key, 0)
    #     if not isinstance(taskId, int):
    #         return 'param taskId error', None
    #     return None, taskId

    # def _check_param_uid(self, key, params):
    #     val = runhttp.getParamStr(key, '')
    #     return None, val
    #
    # def _check_param_appId(self, key, params):
    #     val = runhttp.getParamStr(key, '')
    #     return None, val
    #
    # def _check_param_clientId(self, key, params):
    #     val = runhttp.getParamStr(key, '')
    #     return None, val

    def _check_param_vip_center_id(self, key, params):
        val = runhttp.getParamStr(key, '')
        return None, val

    def _check_param_grade(self, key, params):
        val = runhttp.getParamStr(key, '')
        return None, val

    def _check_param_excode(self, key, params):
        val = runhttp.getParamStr(key, '')
        return None, val

    def _check_param_mobile(self, key, params):
        val = runhttp.getParamStr(key, '')
        return None, val

    @markHttpMethod(httppath='/v2/game/h5/dizhu/youku/vip_notify')
    def doDizhuVipNotify(self, uid, appId, clientId, vip_center_id, grade):
        ftlog.info('doDizhuVipNotify->', uid, vip_center_id, grade)
        try:
            # vip_center_id = jsondata['vip_center_id']
            # userId = jsondata['uid']
            # gameId = jsondata['appId']
            # grade = jsondata['grade']

            from dizhu.activities.h5youku import YouKu
            YouKu.on_user_vip_charge(uid, vip_center_id, grade)

            mo = MsgPack()
            mo.setCmd('h5_youku_dizhu')
            mo.setResult('action', 'vip_charge')
            mo.setResult('userId', uid)
            mo.setResult('gameId', appId)
            mo.setResult('grade', grade)
            router.sendToUser(mo, uid)
            return 1

        except:
            ftlog.error()
            return 0

    @markHttpMethod(httppath='/v2/game/h5/dizhu/youku/check_excode')
    def check_excode(self, excode):
        from dizhu.activities.h5youku import YouKu
        ec, prize_id = YouKu.check_excode(excode)

        mo = MsgPack()
        mo.setCmd('h5_youku_dizhu')
        mo.setResult('action', 'check_excode')
        mo.setResult('prize_id', prize_id)
        mo.setResult('code', ec)
        return mo

    @markHttpMethod(httppath='/v2/game/h5/dizhu/youku/exchange_prize')
    def exchange_prize_code(self, excode, mobile):
        from dizhu.activities.h5youku import YouKu
        ec, prize_id, info = YouKu.exchange_prize_code(excode, mobile)

        mo = MsgPack()
        mo.setCmd('h5_youku_dizhu')
        mo.setResult('action', 'exchange_prize')
        mo.setResult('prize_id', prize_id)
        mo.setResult('code', ec)
        mo.setResult('info', info)
        return mo

    def makeErrorResponse(self, ec, message):
        return {'error': {'ec': ec, 'message': message}}

    def makeResponse(self, result):
        return {'result': result}


@markHttpHandler
class MatchHttpHandler(BaseHttpMsgChecker):
    def __init__(self):
        pass

    @markHttpMethod(httppath='/v2/game/h5/dizhu/match/share/calendar', jsonp=1)
    def getMatchCalendar(self):
        from poker.entity.configure import configure
        calendarConf = configure.getGameJson(DIZHU_GAMEID, 'match.calendar', {})
        if not calendarConf or calendarConf.get('closed', 0) == 1:
            return {'error': {'ec': -1, 'message': '页面不存在'}}
        from dizhu.servers.util.game_handler import GameTcpHandler
        calendarInfo = GameTcpHandler.buildCalendarInfo(calendarConf)

        shareInfo = []
        for match in calendarInfo['matches']:
            if match.get('shareFlag') == 1:
                shareInfo.append({
                    'name': match.get('name'),
                    'time': match.get('time'),
                    'rewardName': match.get('rewardName'),
                    'shareImgs': match.get('shareImgs', []),
                    'timeList': match.get('timeList', []),
                })

        mo = MsgPack()
        mo.setCmd('match_share')
        mo.setResult('action', 'share')
        mo.setResult('code', 0)
        mo.setResult('currentTime', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        mo.setResult('money', calendarInfo['moneyWeb'])
        mo.setResult('tomorrowReward', calendarInfo['dates'][1])
        mo.setResult('todayReward', calendarInfo['shareImgs'])
        mo.setResult('info', shareInfo)
        return mo

    def makeErrorResponse(self, ec, message):
        return {'error': {'ec': ec, 'message': message}}

    def makeResponse(self, result):
        return {'result': result}


@markHttpHandler
class ShareContentHttpHandler(BaseHttpMsgChecker):
    def __init__(self):
        pass

    @markHttpMethod(httppath='/dizhu/wx/share/content')
    def getShareContent(self):
        share3Conf = configure.getGameJson(6, 'share3', {})
        contents = share3Conf.get('contents', [])
        return {'contents': contents}