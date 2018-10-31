# -*- coding:utf-8 -*-
'''
Created on 2017年2月25日

@author: zhaojiangang
'''
from poker.entity.configure import configure
from poker.util import sortedlist


def getLevelInfo(gameId, exp):
    expConf = configure.getGameJson(gameId, 'exp', {})
    levelConf = expConf.get('level')
    titleConf = expConf.get('title') or ['']
    
    if not levelConf:
        return 0, titleConf[0]
    
    level = sortedlist.upperBound(levelConf, exp)
    tindex = abs((max(1, level) - 1) / 3) 
    return level, titleConf[tindex] if tindex < len(titleConf) else titleConf[-1]

def getNextLevelExp(gameId, level):
    levelConf = configure.getGameJson(gameId, 'exp', {}).get('level')
    if not levelConf:
        return 0
    level = abs(int(level))
    return levelConf[level] if level < len(levelConf) else levelConf[-1]


