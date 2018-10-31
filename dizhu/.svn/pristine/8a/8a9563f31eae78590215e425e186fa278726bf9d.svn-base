# -*- coding=utf-8 -*-
'''
Created on 2015年5月7日

@author: zqh
'''


import freetime.util.log as ftlog
from poker.entity.configure import configure, pokerconf
from poker.util import strutil


DIZHU_GAMEID = 6

PLAYMODE_HAPPY = 'happy'
PLAYMODE_ERDOU = 'erdou'
PLAYMODE_LAIZI = 'wild'
PLAYMODE_123 = '123'
PLAYMODE_ERDAYI = 'erdayi'
PLAYMODE_QUICKLAIZI = 'quick_laizi'
PLAYMODE_EMPTY = 'empty'

PLAYMODE_DEFAULT = "match"
PLAYMODE_STRAIGHT_MATCH = "straightMatch"

PLAYMODE_ALLSET = set([PLAYMODE_HAPPY, PLAYMODE_ERDOU, PLAYMODE_LAIZI, PLAYMODE_123, PLAYMODE_EMPTY, PLAYMODE_QUICKLAIZI])

MATCH_REWARD_REDENVELOPE = 'redEnvelope'
MATCH_REWARD_JIADIAN = 'jiadian'

PROMOTE = 'promote'
WITHDRAW = 'withdraw'
DIAMOND = 'diamond'
RED_ENVELOPE = 'redEnvelope'
WINSTREAK = 'winStreak'
MULTI = 'multi'
HIGHEST = 'highest'


def getPopActivityTemplate(clientId):
    intClientId = pokerconf.clientIdToNumber(clientId)
    # 查看是否关闭了活动弹框
    clientConf = configure.getGameJson(DIZHU_GAMEID, 'pop.activity', {}, intClientId)
    closed = clientConf.get('closed', 0)
    if closed:
        return None
    templateName = clientConf.get('template', 'default')
    templateMap = configure.getGameJson(DIZHU_GAMEID, 'pop.activity', {}, configure.DEFAULT_CLIENT_ID).get('templates')
    if ftlog.is_debug():
        ftlog.debug('dizhuconf.getPopActivityTemplate clientId=', clientId,
                    'templateNames=', templateMap.keys() if templateMap else None)
    if not templateMap:
        return None
    
    return templateMap.get(templateName)
    
def getPublicConf(key, defVal):
    d = configure.getGameJson(DIZHU_GAMEID, 'public', {})
    return d.get(key, defVal)
    
def getDizhuGameItem(mainKey, subKey):
    return configure.getGameJson(DIZHU_GAMEID, mainKey, {})[subKey]


def _adjustDdzSessionInfo(redisfullkey, alldata):
    if not alldata :
        return
    for _, si in alldata['session_items'].items() :
        rooms = si['rooms']
        for x in xrange(len(rooms)) :
            rooms[x] = alldata['room_items'][rooms[x]]
    for _, ss in alldata['templates'].items() :
        for x in xrange(len(ss)) :
            ss[x] = alldata['session_items'][ss[x]]

def getDdzSessionInfo(gameId, clientId):
    intClientId = pokerconf.clientIdToNumber(clientId)
    return configure.getGameTemplateInfo(gameId, 'tvohall.info', intClientId, _adjustDdzSessionInfo)


def getSkillScoreLevelScore():
    return getDizhuGameItem('skill.score', 'score')


def getSkillScoreLevelPic():
    return getDizhuGameItem('skill.score', 'level_pic')

def getSkillScoreBigLevelPic():
    return getDizhuGameItem('skill.score', 'big_level_pic')

def getSkillScoreTitlePic():
    return getDizhuGameItem('skill.score', 'title_pic')

def getTvoAds():
    return getDizhuGameItem('tvoads', 'ads')

def getSkillScoreGameName():
    return getDizhuGameItem('skill.score', 'game_name')


def getSkillScoreDes():
    return getDizhuGameItem('skill.score', 'des')


def getSkillScoreReward():
    return getDizhuGameItem('skill.score', 'reward')


def getSkillSCoreRatioRoom():
    return getDizhuGameItem('skill.score', 'ratio_room')


def getReferrerSwitch():
    return getDizhuGameItem('public', 'referrer_switch')


def getGameDataKeys():
    return ['lastlogin', 'nslogin', 'maxwinchip', 'level', 'winrate',
            'marsscore', 'winchips', 'losechips', 'matchscores',
            'slams', 'maxweekdoubles', 'oboxtimes', 'loginsum',
            'referrer', 'headUrl', 'gold']


def getGameDataValues():
    return [0, 0, 0, 0, '{"pt":0,"wt":0,"mt":0}',
            0, 0, 0, 0,
            0, 0, 0, 0,
            0, '', 0]


def getExpDataLevel():
    return configure.getGameJson(DIZHU_GAMEID, 'exp')['level']


def getExpDataTitle():
    return configure.getGameJson(DIZHU_GAMEID, 'exp')['title']


def fillFullUrl(resource):
    if resource.find('.html') >= 0:
        pre = getDizhuGameItem('public', 'http_download_html')
        return pre + resource
    if resource.find('.png') >= 0 or resource.find('.jpg') >= 0:
        pre = getDizhuGameItem('public', 'http_download_pic')
        assert(pre)
        return pre + resource
    pre = getDizhuGameItem('public', 'http_download_default')
    return pre + resource


def getTreasureBoxInfo(roomId):
    infos = configure.getGameJson(DIZHU_GAMEID, 'table.tbbox', {}, configure.DEFAULT_CLIENT_ID)
    rooms = infos.get('rooms', {})
    return rooms.get(str(roomId), None)


def getTreasureBoxDoubleInfo(roomId):
    infos = configure.getGameJson(DIZHU_GAMEID, 'table.tbbox', {}, configure.DEFAULT_CLIENT_ID)
    double = infos.get('double', {})
    return double


def getPublic():
    return configure.getGameJson(DIZHU_GAMEID, 'public')

def getQuickStart():
    return configure.getGameJson(DIZHU_GAMEID, 'quickstart', {})

def _getPublic(key):
    return getPublic().get(key, None)


def getBuyInConf():
    return _getPublic('buyin')


def getTableNetWorkTipStr():
    return _getPublic('optimedis')


def getVipSpecialRight():
    return _getPublic('vip_special_right')


def getChangeNickNameLevel():
    return _getPublic('change_nickname_level')
    

def getQuickStartErrorMsg(errCode):
    infos = _getPublic('quick_start_errinfo')
    errmsg = None
    if infos :
        return infos.get(str(errCode))
    if not errmsg :
        errmsg = 'system exception, please try again ! code=' + str(errCode)
    return errmsg


def getComplainInfo(roomId):
    conf = configure.getGameJson(DIZHU_GAMEID, 'complain', {}, configure.DEFAULT_CLIENT_ID)
    tips = conf.get("tips", {})
    template = conf.get('rooms', {}).get(str(roomId), '')
    if template:
        return conf.get('complains', {}).get(template, {}), tips
    else:
        return {}, tips

def getAllComplainInfo():
    return configure.getGameJson(DIZHU_GAMEID, 'complain', {}, configure.DEFAULT_CLIENT_ID)
    
def getTableSmilesInfo(bigRoomId, vipLevel):
    infos = configure.getGameJson(DIZHU_GAMEID, 'table.smilies', {}, configure.DEFAULT_CLIENT_ID)
    template = infos.get('rooms', {}).get(str(bigRoomId), '')
    ftlog.debug('bigRoomId=', bigRoomId, 'template=', template, 'infos=', infos)
    vips = getattr(infos, '_vips_', None)
    if not vips :
        vips = {}
        setattr(infos, '_vips_', vips)
        viplist = infos.get('vip_special', [])
        templates = infos.get('templates', {})
        for k, v in templates.items() :
            vips[k] = [[0, strutil.cloneData(v)]]
            for x in viplist :
                level = x['level']
                rate = x['rate'] + 1
                v = strutil.cloneData(v)
                for _, sv in v.items() :
                    sv['self_charm'] = int(sv['self_charm'] * rate)
                vips[k].append([level, v])
                ftlog.debug('vips[k][level]->', k, level, v)
            vips[k].sort(key=lambda x:x[0], reverse=True)
    
    ftlog.debug('vips=', vips)
    confs = vips.get(template)
    if not confs :
        return {}
    if vipLevel > 0 :
        for conf in confs :
            if vipLevel >= conf[0] :
                return conf[1]     
    return confs[-1][1]


def getTableQuickInfo(clientId):
    intClientId = pokerconf.clientIdToNumber(clientId)
    info = configure.getGameTemplateInfo(DIZHU_GAMEID, 'table.quickpay', intClientId)
    ftlog.debug('quickpay->', intClientId, info)
    if not info :
        systype, _, _ = strutil.parseClientId(clientId)
        defalut = 'default_android'
        if systype == strutil.CLIENT_SYS_IOS :
            defalut = 'default_ios'
        ftlog.debug('quickpay defalut->', defalut)
        templates = configure.getGameTemplates(DIZHU_GAMEID, 'table.quickpay')
        info = templates.get(defalut)
    ftlog.debug('quickpay info->', info)
    return info


def getRoomFeeConf():
    return _getPublic('roomfee_conf')


def getAdNotifyPlayCount():
    return _getPublic('ad_notify_play_count')


def isUseMomoRanking():
    return _getPublic('use_momo_ranking')


def isUseTuyouRanking():
    return _getPublic('use_tuyou_ranking')


def isEnableLogChatMsg():
    return _getPublic('enableLogChatMsg')


def getRoomWinLosePayInfo(bigRoomId, clientId):
    intClientId = pokerconf.clientIdToNumber(clientId)
    info = configure.getGameTemplateInfo(DIZHU_GAMEID, 'room.pay', intClientId)
    if not info :
        systype, _, _ = strutil.parseClientId(clientId)
        defalut = 'default_android'
        if systype == strutil.CLIENT_SYS_IOS :
            defalut = 'default_ios'
        templates = configure.getGameTemplates(DIZHU_GAMEID, 'room.pay')
        info = templates.get(defalut)
    if info :
        return info.get(str(bigRoomId))
    return None


def getIsTableBuyInAll(clientId):
    intClientId = pokerconf.clientIdToNumber(clientId)
    return configure.getGameTemplateInfo(DIZHU_GAMEID, 'table.buyinall', intClientId, None)


def isSupportBuyin(clientId):
    buyinconf = getBuyInConf()
    _, ver, _ = strutil.parseClientId(clientId)
    start_version = buyinconf.get('start_version', 3.502)
    closed = buyinconf.get('closed', [])
    if ver in closed:
        return False
    else:
        if ver >= start_version:
            return True
        else:
            return False

def getClientShareConf(clientId, defaultValue={}):
    intClientId = pokerconf.clientIdToNumber(clientId)
    shares = configure.getGameJson(DIZHU_GAMEID, 'share', {}, intClientId)
    return shares.get('shares', {})

def getShareConf():
    return configure.getGameJson(DIZHU_GAMEID, 'share', {}, configure.DEFAULT_CLIENT_ID)

def getActivityConf(conf_name):
    return configure.getGameJson(DIZHU_GAMEID, 'activity', {}, configure.DEFAULT_CLIENT_ID).get(conf_name, {})

def getTeHuiLiBaoConf():
    return configure.getGameJson(DIZHU_GAMEID, 'activity', {}, configure.DEFAULT_CLIENT_ID).get('tehuilibao', {})

def getLedNotifyConf():
    return configure.getGameJson(DIZHU_GAMEID, 'activity', {}, configure.DEFAULT_CLIENT_ID).get('led_notify', [])

def getFriendTableConf(clientId):
    templateName = configure.getVcTemplate('friendtable', clientId, DIZHU_GAMEID)
    ftconf = configure.getGameJson(DIZHU_GAMEID, 'friendtable', {}, configure.CLIENT_ID_TEMPLATE)
    templateMap = ftconf.get('templates', {})
            
    conf = templateMap.get(templateName)
    if not conf:
        vcconf = configure.getGameJson(DIZHU_GAMEID, 'friendtable:vc', None, None)
        if vcconf:
            templateName = vcconf.get('default', None)
            if templateName:
                conf = templateMap.get(templateName)
    conf = conf or {}
    if ftlog.is_debug():
        ftlog.debug('getFriendTableConf:',
                    'clientId=', clientId,
                    'templateName=', templateName,
                    'conf=', conf,
                    'templateMap=', templateMap)
    return conf

def getMatchClassify(clientId):
    '''
    获取新的比赛分类信息
    插件版本需求3.827及以上
    '''
    templateName = configure.getVcTemplate('match.classify', clientId, DIZHU_GAMEID)
    mcconf = configure.getGameJson(DIZHU_GAMEID, 'match.classify', {}, configure.CLIENT_ID_TEMPLATE)
    templateMap = mcconf.get('templates', {})
            
    conf = templateMap.get(templateName)
    if not conf:
        vcconf = configure.getGameJson(DIZHU_GAMEID, 'match.classify:vc', None, None)
        if vcconf:
            templateName = vcconf.get('default', None)
            if templateName:
                conf = templateMap.get(templateName)
    if ftlog.is_debug():
        ftlog.debug('getMatchClassify:',
                    'clientId=', clientId,
                    'templateName=', templateName,
                    'conf=', conf,
                    'templateMap=', templateMap)
    return conf

def getNewbieTaskConf():
    return configure.getGameJson(DIZHU_GAMEID, 'tasks', {}, configure.DEFAULT_CLIENT_ID).get('newbie.task.conf', {})


def getMatchLotteryConf():
    return configure.getGameJson(DIZHU_GAMEID, 'common.conf', {}, 'match_lottery')

def getHonorCardConf():
    return configure.getGameJson(DIZHU_GAMEID, 'common.conf', {}, 'honor_card')

def getUserBehaviourReward():
    return _getPublic('behaviour_reward')

def getCardNoteTips(userId, buyinChip, clientId, cardNoteChip=0, cardNoteDiamod=0):
    _, clientVer, _ = strutil.parseClientId(clientId)
    if ftlog.is_debug():
        ftlog.debug('getCardNoteTips userId=', userId,
                    'buyinChip=', buyinChip,
                    'clientId=', clientId,
                    'clientVer=', clientVer,
                    'cardNoteChip=', cardNoteChip,
                    'cardNoteDiamod=', cardNoteDiamod)

    # 处理牌桌记牌器
    cardNoteOpenConf = getPublic().get('card_note_open')
    if cardNoteOpenConf:
        isBuyMonthCard = False

        if cardNoteDiamod:
            if clientVer >= 4.56:
                isBuyMonthCard = True
                cardNoteTip = cardNoteOpenConf.get('desc.month_card', '购买贵族月卡可免费使用记牌器')
            else:
                cardNoteTip = cardNoteOpenConf.get('diamond', {}).get('desc', '')
            cardNoteTip = strutil.replaceParams(cardNoteTip, {'consumeChip': str(cardNoteDiamod)})

            if ftlog.is_debug():
                ftlog.debug('getCardNoteTips.cardNoteDiamod userId=', userId,
                            'openable=', 1,
                            'desc=', cardNoteTip,
                            'isBuyMonthCard=', isBuyMonthCard)
            return {'openable': 1, 'desc': cardNoteTip, 'isBuyMonthCard': isBuyMonthCard}
        elif isinstance(cardNoteChip, int) and cardNoteChip > 0:
            # 大厅版本4.56以上 修改描述
            openable = 1
            desc = cardNoteOpenConf.get('desc', '')
            if buyinChip < cardNoteChip:
                openable = 0
                desc = cardNoteOpenConf.get('desc.chip_not_enough', '')

            if clientVer >= 4.56:
                desc = cardNoteOpenConf.get('desc.month_card', '购买贵族月卡可免费使用记牌器')

            desc = strutil.replaceParams(desc, {'consumeChip': str(cardNoteChip)})
            if ftlog.is_debug():
                ftlog.debug('getCardNoteTips.cardNoteChip userId=', userId, 'openable=', 1, 'desc=', desc,
                            'isBuyMonthCard=', isBuyMonthCard)

            return {"openable": openable, "desc": desc, "isBuyMonthCard": isBuyMonthCard}
    return None


def segmentConf():
    return configure.getGameJson(DIZHU_GAMEID, 'match.segment', {})

def getDayLoginRewardConf():
    return configure.getGameJson(DIZHU_GAMEID, 'dayloginreward', {})
