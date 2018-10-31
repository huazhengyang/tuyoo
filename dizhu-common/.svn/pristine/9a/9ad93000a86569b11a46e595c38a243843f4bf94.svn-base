# -*- coding:utf-8 -*-
'''
Created on 2017年2月25日

@author: zhaojiangang
'''
import freetime.util.log as ftlog
from poker.entity.configure import configure
from poker.util import strutil


def getEmojiConf(gameId, bigRoomId, vipLevel):
    conf = configure.getGameJson(gameId, 'table.smilies', {}, configure.DEFAULT_CLIENT_ID)
    templateName = conf.get('rooms', {}).get(str(bigRoomId))
    if ftlog.is_debug():
        ftlog.debug('emoji.getEmojiConf',
                    'gameId=', gameId,
                    'bigRoomId=', bigRoomId,
                    'templateName=', templateName)
    template = conf.get('templates', {}).get(templateName)
    if not template:
        return None
    
    # 获取levelConf
    vipsConf = conf.get('vip_special')
    if not vipsConf:
        return template
    
    vipConf = None
    for item in vipsConf:
        if vipLevel > item['level']:
            vipConf = item
            break
    
    if not vipConf:
        return template
    
    template = strutil.cloneData(template)
    rate = vipConf['rate'] + 1
    for _, value in template.iteritems():
        value['self_charm'] *= rate
    return template


