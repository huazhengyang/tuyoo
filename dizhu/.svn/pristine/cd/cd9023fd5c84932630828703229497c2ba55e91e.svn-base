# -*- coding: utf-8 -*-
'''
Created on sep 15, 2015

@author: rex
@summary: youku h5

'''
import json, time
from dizhu.entity.dizhutask import DizhuTaskFinishEvent
from poker.entity.dao import sessiondata
import freetime.util.log as ftlog
from poker.entity.configure import pokerconf
from dizhu.game import TGDizhu
from poker.entity.dao import day1st
from poker.entity.dao import daobase
from poker.entity.dao import userdata, userchip
from poker.util import strutil, timestamp
from hall.entity.halldailycheckin import TYDailyCheckinRewardEvent
from hall.entity import datachangenotify
from hall.game import TGHall

import random
from poker.util import smsdown

GAMEID = 6
YOUKU_CLIENTID_NUM = 13492

nick_names = ['滴血玫瑰','火凤凰','玲玲','缘来如此','心雨','寻梦','咖啡伴侣','静听落雪','芥末巧克力','Baby彤彤','D调的华丽','DJ小魔女','GameTime芳芳','画眉鸟','红牡丹','花好月圆','快乐人生','百合花的倾诉','江敏杰','降香','锦州帅哥','舞主角龙','欣妍','一天到晚游泳的鱼','刹那间','狼图腾','岂非乐哉','雷震子','流水','落叶','非凡自我','爱打才会赢','我是高手','展翅高飞','雄鹰翱翔','大王','白煮蛋','百般无奈']

class YouKu(object):
    eventset = [DizhuTaskFinishEvent]

    dailyTaskSystem = None

    is_valid = True

    key_award_list = 'h5:activity:youku.awardlist'

    key_prize_users = 'h5:activity:youku.prize.users'

    key_excodes = 'h5:activity:youku.excodes'

    key_day_vip_num = 'h5:activity:youku.day_vip_num'

    key_vip_charge = 'h5:activity:youku.vip_charge'

    daily_vip_raffle_limit = 200  # 优酷会员奖品每天限制xx个

    RAFFLE_CONFIG = [
          (1, "APP大礼包", 1),  # prize_id = 1
          (2, "牛仔帽7天", 1),
          (3, "优酷7天会员", 1),
          (4, "金币10万", 100000),
          (5, "金币5万", 50000),
          (6, "金币1万", 10000),
          (7, "金币3000", 3000),
          (8, "金币1000", 1000)
    ]

    VIP_COIN_CONFIG = {
        '1': 88888,
        '2': 666666,
        '3': 999999
    }

    @classmethod
    def initialize(cls):
        if not cls.is_valid:
            return
        try:
            cls.registerEvents()
            pass
        except:
            import traceback
            traceback.print_exc()
    
    @classmethod
    def registerEvents(cls):
        eventbus = TGDizhu.getEventBus()
        ftlog.debug('YouKu register events')
        for event in cls.eventset:
            eventbus.subscribe(event, cls.handleEvent)

        hallEventBus = TGHall.getEventBus()
        hallEventBus.subscribe(TYDailyCheckinRewardEvent, cls.handleDailyCheckinEvent)

    @classmethod
    def handleEvent(cls, event):
        if isinstance(event, DizhuTaskFinishEvent):
            cls.handleTaskFinishEvent(event)

    @classmethod
    def handleTaskFinishEvent(cls, event):
        ftlog.debug('handleTaskFinishEvent', event.task.__dict__)
        userId = event.userId
        gameId = event.gameId
        clientId = sessiondata.getClientId(userId)
        clientIdNum = pokerconf.clientIdToNumber(clientId)
        if clientIdNum != YOUKU_CLIENTID_NUM:
            return

        if event.task.taskUnitId != 'ddz.task.daily':
            return

        datas = cls._checkYoukuData(userId, gameId)
        datas_youku = datas.get('h5youku')

        finish_task_count = int(datas_youku.get('finish_task_count', 0))
        finish_task_count += 1
        datas_youku['finish_task_count'] = finish_task_count
        day1st.setDay1stDatas(userId, gameId, datas)

    @classmethod
    def handleDailyCheckinEvent(cls, event):
        ftlog.debug('handleDailyCheckinEvent')
        rewardContent = event.rewardContent
        actionType = event.actionType
        userId = event.userId
        gameId = event.gameId
        clientId = sessiondata.getClientId(userId)
        clientIdNum = pokerconf.clientIdToNumber(clientId)
        snsinfo = userdata.getAttr(userId, 'snsinfo')
        youku_vip = 0
        try:
            infojson = json.loads(snsinfo)
            youku_vip = infojson.get('vip', 0)
        except:
            pass
        # actionType = 2

        if youku_vip and actionType == 2:
            rewardItems = rewardContent.getItems()
            for item in rewardItems:
                item.count = item.count * 2
        ftlog.debug('handleDailyCheckinEvent rewardContent items', rewardContent.getItems())

    @classmethod
    def _checkYoukuData(cls, userId, gameId):
        datas = day1st.getDay1stDatas(userId, gameId)
        datas_youku = datas.get('h5youku')
        if datas_youku is None:
            datas_youku = {}
            datas['h5youku'] = datas_youku
        return datas

    @classmethod
    def getLeftRaffleTimes(cls, userId, gameId):
        times = 1
        datas = day1st.getDay1stDatas(userId, gameId)
        datas_youku = datas.get('h5youku')
        if not datas_youku:
            return times
        finish_task_count = int(datas_youku.get('finish_task_count', 0))
        raffle_times = int(datas_youku.get('raffle_times', 0))
        total_raffle_times = finish_task_count + 1
        return max(total_raffle_times - raffle_times, 0)

    @classmethod
    def raffle(cls, userId, gameId, mo):
        """
        raffle
        """
        ftlog.debug('youku raffle')
        left_times = cls.getLeftRaffleTimes(userId, gameId)
        if left_times <= 0:
            mo.setResult("prize_id", 0)
            mo.setResult("left_times", 0)
            return
        left_times -= 1
        mo.setResult("left_times", left_times)

        datas = cls._checkYoukuData(userId, gameId)
        datas_youku = datas.get('h5youku')
        if 'raffle_times' in datas_youku:
            raffle_times = int(datas_youku['raffle_times'])
        else:
            raffle_times = 0

        raffle_times += 1
        datas_youku['raffle_times'] = raffle_times
        day1st.setDay1stDatas(userId, gameId, datas)

        ex_prize_id = 0
        prize_id = 0
        excode = ''
        can_raffle_special = False  # 暂时关闭可兑换的奖项

        if not can_raffle_special:  # temp
            random_val = random.randint(0, 100)
            if random_val <= 50 and random_val > 45:
                global nick_names
                nick_name = random.choice(nick_names)
                temp_prize_id = random.randint(1, 3)
                data = {}
                data['prize_id'] = temp_prize_id
                data['uid'] = 0
                data['user_name'] = nick_name
                data_str = json.dumps(data)
                list_size = daobase.executeMixCmd('rpush', cls.key_award_list, data_str)
                if list_size > 200:
                    daobase.executeMixCmd('ltrim', cls.key_award_list, 0, 100)

        if can_raffle_special and raffle_times in (2, 4, 5):
            user_prize = daobase.executeMixCmd('hget', cls.key_prize_users, userId)
            if user_prize:
                user_prize_json = json.loads(user_prize)
            else:
                user_prize_json = None
            if raffle_times == 2:
                ex_prize_id = 2
            if raffle_times == 4:
                ex_prize_id = 1
            if raffle_times == 5:
                ex_prize_id = 3

            if not user_prize_json or not str(ex_prize_id) in user_prize_json:
                prize_id = ex_prize_id

                if ex_prize_id == 3:  # youku vip
                    day_vip_num = daobase.executeMixCmd('get', cls.key_day_vip_num)
                    if day_vip_num >= cls.daily_vip_raffle_limit:
                        prize_id = 0
                    else:
                        daobase.executeMixCmd('incr', cls.key_day_vip_num)
                        if day_vip_num <= 1:
                            expire_seconds = timestamp.getCurrentDayLeftSeconds()
                            daobase.executeMixCmd('expire', cls.key_day_vip_num, expire_seconds)

                if prize_id > 0:
                    if not user_prize_json:
                        user_prize_json = {}
                    # save user prize for app exchange
                    data = {}
                    time_val = int(time.time())
                    data['time'] = time_val
                    excode = ExCodeGenerator.generate_excode()
                    data['excode'] = excode
                    data['prize_id'] = prize_id
                    user_prize_json[str(prize_id)] = data

                    daobase.executeMixCmd('hset', cls.key_prize_users, userId, json.dumps(user_prize_json))
                    # daobase.executeMixCmd('zadd', cls.key_prize_users, userId, json.dumps(user_prize_json))

                    # save excode
                    excode_data = {}
                    excode_data['uid'] = userId
                    excode_data['prize_id'] = prize_id
                    excode_data['time'] = time_val
                    daobase.executeMixCmd('hset', cls.key_excodes, excode, json.dumps(excode_data))

                    data = {}
                    data['prize_id'] = prize_id
                    data['uid'] = userId
                    data['user_name'] = userdata.getAttr(userId, 'name')
                    data_str = json.dumps(data)

                    list_size = daobase.executeMixCmd('rpush', cls.key_award_list, data_str)
                    if list_size > 200:
                        daobase.executeMixCmd('ltrim', cls.key_award_list, 0, 100)

        # raffle
        if not prize_id:
            prize_id_start = 4
            # prize_id = random.randint(prize_id_start, len(cls.RAFFLE_CONFIG))
            # rates = [1, 4, 10, 30, 54]
            rates = [1, 5, 16, 22, 99]
            prize_id = 0
            random_num = random.randint(1, 100)
            i = 0
            for rate in rates:
                if random_num <= rate:
                    prize_id = prize_id_start + i
                    break
                i += 1
        mo.setResult("prize_id", prize_id)
        mo.setResult("excode", excode)

        ftlog.debug('youku raffle prize_id', prize_id, 'raffle_times', raffle_times)
        if prize_id == 0:
            return
        mo.setResult("prize_name", cls.RAFFLE_CONFIG[prize_id - 1][1])

        if prize_id > 3:
            chip = cls.RAFFLE_CONFIG[prize_id - 1][2]
            userchip.incrChip(userId, gameId, chip, 0, 'H5_YOUKU_DIZHU_RAFFLE_CHIP', 0, None)
            # datachangenotify.sendDataChangeNotify(gameId, userId, 'chip')
        ftlog.debug('raffle award prize_id', prize_id, 'uid', userId)

    @classmethod
    def get_award_show_list(cls, userId, gameId, mo=None):
        ftlog.debug('youku getAwardList')
        award_list = []
        award_json_list = daobase.executeMixCmd('lrange', cls.key_award_list, 0, 10)
        for award_json in reversed(award_json_list):
            award_item = json.loads(award_json)
            prize_id = award_item['prize_id']
            award_item['prize_name'] = cls.RAFFLE_CONFIG[prize_id - 1][1]
            award_list.append(award_item)
        ftlog.debug('youku getAwardList result', award_list)
        mo.setResult('award_list', award_list)

    @classmethod
    def get_user_ex_prize(cls, userId):
        prizes = []
        user_prize = daobase.executeMixCmd('hget', cls.key_prize_users, userId)
        if not user_prize:
            return prizes

        user_prize_json = json.loads(user_prize)
        prizeids = ['2', '1', '3']
        for prizeid in prizeids:
            if prizeid not in user_prize_json:
                continue
            prizes.append(user_prize_json.get(prizeid))
        return prizes

    @classmethod
    def check_excode(cls, excode):
        excode_str = daobase.executeMixCmd('hget', cls.key_excodes, excode)
        if not excode_str:
            return 1, 0  # not exist

        excode_json = json.loads(excode_str)
        prize_id = excode_json.get('prize_id', 0)
        if excode_json.get('finish', 0):
            return 2, prize_id  # has exchanged
        if excode_json.get('prize_id', 0) != 3:  # 优酷会员有过期时间
            return 0, prize_id
        time_val = excode_json.get('time', 0)
        time_now = timestamp.getCurrentTimestamp()
        expire_days = 3
        if time_now - time_val > expire_days*86400:
            return 3, prize_id  # has expired
        else:
            return 0, prize_id

    @classmethod
    def exchange_prize_code(cls, excode, mobile=0):
        """
        兑换奖品
        """
        ret, prize_id = cls.check_excode(excode)
        info = ''
        if ret != 0:
            if ret == 2:
                info = '已经兑换过了哦'
            else:
                info = '兑换失败'
            return ret, prize_id, info
        excode_str = daobase.executeMixCmd('hget', cls.key_excodes, excode)
        excode_json = json.loads(excode_str)
        excode_json['finish'] = 1
        uid = excode_json['uid']
        prize_id = excode_json.get('prize_id', 0)
        daobase.executeMixCmd('hset', cls.key_excodes, excode, json.dumps(excode_json))

        ftlog.debug('exchange_prize_code', excode)
        if prize_id == 3:
            info = '恭喜获得7天优酷VIP，激活码是7676，请登录优酷官网进行激活'
            smsdown.SmsDownManDao.sendSms(mobile, info)
        return 0, prize_id, '兑换成功'

    @classmethod
    def on_user_vip_charge(cls, userId, vip_center_id, grade):
        """
        用户开通vip
        """
        ftlog.debug('on_user_vip_charge', userId, vip_center_id, grade)
        vip_charge_info = daobase.executeMixCmd('hget', cls.key_vip_charge, userId)

        if not vip_charge_info:
            vip_charge_info = {}
        else:
            vip_charge_info = json.loads(vip_charge_info)

        # data = vip_charge_info.get(str(grade), {})
        grade_data = {'vip_center_id': vip_center_id, 'time': int(time.time()), 'exchanged': 0}
        vip_charge_info[str(grade)] = grade_data
        daobase.executeMixCmd('hset', cls.key_vip_charge, userId, json.dumps(vip_charge_info))
        return

    @classmethod
    def get_user_vip_charge(cls, userId):
        ftlog.debug('get_user_vip_charge', userId)
        vip_charge_info = daobase.executeMixCmd('hget', cls.key_vip_charge, userId)

        if not vip_charge_info:
            vip_charge_info = {}
        else:
            vip_charge_info = json.loads(vip_charge_info)
        return vip_charge_info

    @classmethod
    def get_user_vip_charge_info(cls, userId):
        ftlog.debug('get_user_vip_charge_info', userId)
        vip_charge_info = daobase.executeMixCmd('hget', cls.key_vip_charge, userId)

        if not vip_charge_info:
            vip_charge_info = {}
        else:
            vip_charge_info = json.loads(vip_charge_info)
        data = []
        for i in xrange(3):
            grade = str(i+1)
            item = {'coin': cls.VIP_COIN_CONFIG[grade], 'exchanged': 0, 'charged': 0}
            data.append(item)
            if vip_charge_info.get(grade):
                item['charged'] = 1
                item['exchanged'] = vip_charge_info.get(grade).get('exchanged')
        return data

    @classmethod
    def exchange_user_vip_charge(cls, gameId, userId, grade):
        """
        用户兑换vip充值金币
        """
        ftlog.debug('exchange_user_vip_charge', gameId, userId, grade)
        grade = str(grade)
        vip_charge_info = cls.get_user_vip_charge(userId)
        if not vip_charge_info:
            return 1

        grade_data = vip_charge_info.get(str(grade))
        if not grade_data:
            return 1

        ftlog.debug('exchange_user_vip_charge exchanged', grade_data['exchanged'])
        if grade_data['exchanged']:
            return 2

        grade_data['exchanged'] = 1
        daobase.executeMixCmd('hset', cls.key_vip_charge, userId, json.dumps(vip_charge_info))

        chip = cls.VIP_COIN_CONFIG[grade]
        try:
            userchip.incrChip(userId, gameId, chip, 0, 'H5_YOUKU_DIZHU_VIP_EXCHANGE_CHIP', 0, None)
        except:
            import traceback
            traceback.print_exc()
        datachangenotify.sendDataChangeNotify(gameId, userId, 'chip')
        return 0

# class YoukuH5DailyTaskSystem(dizhutask.DizhuDailyTaskSystem):
#
#     def _onTaskFinished(self, task, timestamp):
#         pass

class ExCodeGenerator(object):

    wordlist = '0123456789ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'

    @classmethod
    def generate_excode(cls):
        char1 = random.choice(cls.wordlist)
        char2 = random.choice(cls.wordlist)
        key = 'h5:excode:cursor'
        cursor = int(daobase.executeMixCmd('incr', key))
        if cursor < 2:
            cursor = 100
            daobase.executeMixCmd('set', key, cursor)
        code = strutil.tostr62(cursor) + str(char1) + str(char2)
        ftlog.debug('generateExcode', code)
        return code
