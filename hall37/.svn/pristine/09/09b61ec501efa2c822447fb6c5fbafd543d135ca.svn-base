# -*- coding: utf-8 -*-
'''
Created on 2017年4月5日

@author: zqh
'''
from copy import deepcopy

import freetime.util.log as ftlog
from hall.entity import hallvip
from hall.entity.hallconf import HALL_GAMEID
from poker.entity.dao import gamedata, sessiondata
from hall.entity.iploc import iploc
from poker.util import strutil
from poker.entity.configure import configure, pokerconf
from hall.servers.util import gamelistipfilter


_DEBUG = 0

def _filtergamelist(version, games, pages, innerGames, userId, clientId):

    filterGameIds = []
    conf = configure.getGameJson(HALL_GAMEID, 'gamelistipfilter', {}, configure.DEFAULT_CLIENT_ID)
    filterGameIds.extend(conf.get('badGameIds', []))
    
    if gamelistipfilter._isOutOfBeijingIp(userId, clientId):
        pass
    else:
        filterGameIds.extend(conf.get('filterGameIds', []))
        
    if not filterGameIds:
        return games, pages, innerGames

    if version <= 0:
        games = deepcopy(games)
        pages = deepcopy(pages)
        innerGames = deepcopy(innerGames)

    for x in xrange(len(innerGames) - 1, -1, -1):
        gameId = innerGames[x].get('params', {}).get('gameId')
        if gameId in filterGameIds:
            if _DEBUG:
                ftlog.debug('filtergamelist rm innerGames', userId, gameId, innerGames[x])
            del innerGames[x]

    adjustPage = 0
    for x in xrange(len(pages) - 1, -1, -1):
        nodes = pages[x].get('nodes', [])
        for y in xrange(len(nodes) - 1, -1, -1):
            gameId = nodes[y].get('params', {}).get('gameId')
            if gameId in filterGameIds:
                if _DEBUG:
                    ftlog.debug('filtergamelist rm pages', userId, gameId, nodes[y])
                del nodes[y]
                adjustPage = 1
            else:
                subnodes = nodes[y].get('nodes', [])
                if subnodes:
                    for z in xrange(len(subnodes) - 1, -1, -1):
                        gameId = subnodes[z].get('params', {}).get('gameId')
                        if gameId in filterGameIds:
                            if _DEBUG:
                                ftlog.debug('filtergamelist rm sub pages', userId, gameId, subnodes[z])
                            del subnodes[z]
                            adjustPage = 1
                    if len(subnodes) <= 0:
                        if _DEBUG:
                            ftlog.debug('filtergamelist rm pages', userId, 'zero list', nodes[y])
                        del nodes[y]
                        adjustPage = 1

    if adjustPage:
        allnodes = []
        for x in xrange(len(pages)):
            nodes = pages[x].get('nodes', [])
            allnodes.extend(nodes)
            pages[x]['nodes'] = []

        x = 0
        while len(allnodes) > 0:
            pages[x]['nodes'] = allnodes[0:6]
            allnodes = allnodes[6:]
            x += 1

        for x in xrange(len(pages) - 1, -1, -1):
            nodes = pages[x].get('nodes', [])
            if not nodes:
                del pages[x]

    for x in xrange(len(games) - 1, -1, -1):
        gameId = games[x].get('gameId')
        if gameId in filterGameIds:
            if _DEBUG:
                ftlog.debug('filtergamelist rm games', userId, gameId, games[x])
            del games[x]

    return games, pages, innerGames

gamelistipfilter._filtergamelist = _filtergamelist
