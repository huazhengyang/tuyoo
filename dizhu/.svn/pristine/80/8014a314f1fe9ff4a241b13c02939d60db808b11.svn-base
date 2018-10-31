# -*- coding=utf-8 -*-
'''
Created on 2015年5月7日

@author: zqh
'''
import math

from dizhu.entity import dizhuconf
from dizhu.entity.dizhuconf import DIZHU_GAMEID
import freetime.util.log as ftlog
from hall.entity import hallvip, hallitem, hallconf, hallrename,\
    datachangenotify
from poker.entity.biz.item.item import TYAssetKind, TYAssetUtils
from poker.entity.configure import gdata
from poker.entity.dao import gamedata
from poker.util import timestamp
from poker.entity.biz.content import TYContentRegister
from hall.entity import hallranking
from poker.entity.biz.ranking.rankingsystem import TYRankingInputTypes
from hall.entity.hallconf import HALL_GAMEID
from poker.entity.events.tyevent import UserEvent

class SkillScore(object):
     
    def __init__(self, uid, roomid, mult, dizhu, win, winstreak):
        self._uid = uid
        self._rid = roomid
        self._mult = mult
        self._iswin = win
        self._dizhu = dizhu
        self._winstreak = winstreak

class SkillScoreIncrEvent(UserEvent):
    def __init__(self, gameId, userId, oldScore, oldLevel, newScore, newLevel):
        super(SkillScoreIncrEvent, self).__init__(userId, gameId)
        self.oldScore = oldScore
        self.oldLevel = oldLevel
        self.newScore = newScore
        self.newLevel = newLevel
        
def incrSkillScore(userId, add_score):
    assert(add_score >= 0)
    tootle = gamedata.incrGameAttr(userId, DIZHU_GAMEID, 'skillscore', add_score)

    # 大师分增量榜
    ftlog.debug('setUserByInputType userId=', userId, 'add_score=', add_score, TYRankingInputTypes.DASHIFEN_INCR)
    hallranking.rankingSystem.setUserByInputType(6, TYRankingInputTypes.DASHIFEN_INCR,
                                     userId, add_score, timestamp.getCurrentTimestamp())
    
    oldScore = tootle - add_score
    level_old = get_skill_level(oldScore)
    level_new = get_skill_level(tootle)
    sinfo = score_info(userId)
    sinfo['userId'] = userId
    sinfo['addScore'] = add_score # add by wuyangwei
    if level_old != level_new:
        # 修改昵称
        change_name = False
        need_level = dizhuconf.getChangeNickNameLevel()
        if need_level == level_new :
            set_name_sum = hallrename.getRenameSum(DIZHU_GAMEID, userId)
            if set_name_sum <= 0:
                sinfo['changename'] = 1 #服务器修改此标记,客户端识别弹出改昵称界面
                change_name = True
        # 升级奖励
        up_info = get_skill_level_reward(userId, level_old, level_new)
        if (not change_name) and up_info:
            sinfo['rewards'] = up_info
        # 是否升级， 以前通过升级奖励配置， 配置去掉后会有问题
        sinfo['isLevelUp'] = True
    
    from dizhu.game import TGDizhu
    TGDizhu.getEventBus().publishEvent(SkillScoreIncrEvent(DIZHU_GAMEID, userId, oldScore, level_old, tootle, level_new))
    ftlog.debug('SkillScore.incrSkillScore gameId=', DIZHU_GAMEID,
                         'userId=', userId,
                         'addScore=', add_score,
                         'newScore=', tootle,
                         'oldLevel=', level_old,
                         'newLevel=', level_new,
                         'skillInfo=', sinfo)        
    return sinfo

    
def inc_skill_score(obj):
    add_score = calc_score(obj)
    remainDays, _ = hallitem.getMemberInfo(obj._uid, timestamp.getCurrentTimestamp())
    if remainDays > 0:
        if ftlog.is_debug():
            ftlog.debug('skillscore.inc_skill_score remainDays=', remainDays,
                        'add_score=', add_score,
                        'toDouble=', add_score*2)
        add_score *= 2
    return incrSkillScore(obj._uid, add_score)

def get_skill_level_reward(userId, old_level, new_level):
    rewards = dizhuconf.getSkillScoreReward().get(str(new_level), {}).get('rewards', None)
    if not rewards:
        return None
    ftlog.debug('get_skill_level_reward->', userId, old_level, new_level, rewards)
    sitems = TYContentRegister.decodeFromDict(rewards).getItems()
    ua = hallitem.itemSystem.loadUserAssets(userId)
    aslist = ua.sendContentItemList(DIZHU_GAMEID, sitems, 1, True,
                                    timestamp.getCurrentTimestamp(),
                                    'TASK_MASTER_SCORE_UP_LEVEL_REWARD', 0)
    items = []
    for x in aslist :
        kindId = hallconf.translateAssetKindIdToOld(x[0].kindId)
        akind = hallitem.itemSystem.findAssetKind(x[0].kindId)
        items.append({'id':kindId,
                    'count':x[1],
                    'name':akind.displayName,
                    'pic':akind.pic,
                    })
    datachangenotify.sendDataChangeNotify(HALL_GAMEID, userId, TYAssetUtils.getChangeDataNames(aslist))
    return items


def calc_score(obj):
    if not isinstance(obj, SkillScore):
        return 0
    if not obj._iswin:
        return 0
    privilege_rat = 1
    room_rat = __get_room_ratio(obj._rid)
    mult_rat = int(math.ceil(obj._mult / float(40)))
    dizhu_rat = 1.5 if obj._dizhu else 1
    winstr_rat = int(math.ceil(obj._winstreak / float(4)))
    userVip = hallvip.userVipSystem.getUserVip(obj._uid)
    score = int(privilege_rat * room_rat * mult_rat * dizhu_rat * winstr_rat)
    return vipDaShiFen(score, userVip.vipLevel.level)


def vipDaShiFen(score, vipLevel):
    result = score
    confs = dizhuconf.getVipSpecialRight().get('dashifen', [])
    for conf in confs:
        confLevel = conf.get('level', -1)
        if vipLevel >= confLevel:
            rate = conf.get('rate', 0)
            if isinstance(rate, (int, float)):
                result = score + score * rate
    return int(result)


def __get_room_ratio(roomId):
    bigRoomId = gdata.roomIdDefineMap()[roomId].bigRoomId
    if not bigRoomId: return 1      
    confs = dizhuconf.getSkillSCoreRatioRoom()
    for conf_ in confs:
        if bigRoomId in conf_['roomlist']:
            return conf_['ratio']
    return 1


def get_skill_level(score):
    level_data = dizhuconf.getSkillScoreLevelScore()
    for i in xrange(len(level_data)):
        if score < level_data[i]:
            return i
    return len(level_data)


def get_skill_score_section(level):
    level_score = dizhuconf.getSkillScoreLevelScore()
    if len(level_score) == 0:
        return [0, 2000000000]
    if len(level_score) == 1:
        return [level_score[0], 2000000000]
     
    if level == 0:
        return [level_score[0], level_score[1]]
    elif level >= len(level_score):
        return [level_score[-1], 2000000000]
    else:
        return [level_score[level - 1], level_score[level]]


def get_skill_score_level_pic(level):
    level_pic = dizhuconf.getSkillScoreLevelPic()
    level = max(1, level)
    if len(level_pic) == 0:
        return ''
    if len(level_pic) >= level:
        return level_pic[level - 1] 
    else:
        return level_pic[-1]

def get_skill_score_big_level_pic(level):
    level_pic = dizhuconf.getSkillScoreBigLevelPic()
    level = max(1, level)
    if len(level_pic) == 0:
        return ''
    if len(level_pic) >= level:
        return level_pic[level - 1] 
    else:
        return level_pic[-1]

def get_skill_score_title_pic():
    title_pic = dizhuconf.getSkillScoreTitlePic()
    return title_pic


def get_skill_score_game_name():
    title_pic = dizhuconf.getSkillScoreGameName()
    return title_pic


def get_skill_score_des():
    des = dizhuconf.getSkillScoreDes()
    return des

def get_skill_score(userId):
    return gamedata.getGameAttrInt(userId, DIZHU_GAMEID, 'skillscore')
    
def score_info(uid):
    score = get_skill_score(uid)
    level = get_skill_level(score)
    score_section = get_skill_score_section(level)
    info = {}
    info['score'] = score
    info['level'] = level
    info['premaxscore'] = score_section[0]
    info['curmaxscore'] = score_section[1]
    info['pic'] = get_skill_score_level_pic(level)
    info['picbig'] = get_skill_score_big_level_pic(level)
    info['title'] = get_skill_score_title_pic()
    info['name'] = get_skill_score_game_name()
    info['des'] = get_skill_score_des()
    # 是否升级， 以前通过升级奖励配置， 配置去掉后会有问题
    info['isLevelUp'] = False
    return info

class DizhuAssetKindMasterScore(TYAssetKind):
    TYPE_ID = 'ddz.masterScore'
    def __init__(self):
        super(DizhuAssetKindMasterScore, self).__init__()
        
    def add(self, gameId, userAssets, kindId, count, timestamp, eventId, intEventParam, roomId=0, tableId=0, roundId=0, param01=0, param02=0):
        '''
        @return: finalCount
        '''
        assert(count >= 0)
        info = incrSkillScore(userAssets.userId, count)
        return info['score']
    
    def consume(self, gameId, userAssets, kindId, count, timestamp, eventId, intEventParam, roomId=0, tableId=0, roundId=0, param01=0, param02=0):
        '''
        @return: consumeCount, finalCount
        '''
        assert(count >= 0)
        info = score_info(userAssets.userId)
        return 0, info['score']
    
    def forceConsume(self, gameId, userAssets, kindId, count, timestamp, eventId, intEventParam):
        '''
        @return: consumeCount, finalCount
        '''
        assert(count >= 0)
        info = score_info(userAssets.userId)
        return 0, info['score']
    
    def balance(self, userAssets, timestamp):
        '''
        @return: balance
        '''
        info = score_info(userAssets.userId)
        return info['score']
    
