# -*- coding:utf-8 -*-
'''
Created on 2018年1月25日

@author: wangyonghui
'''
from dizhu.games.arenamatch.table import DizhuTableCtrlArenaMatch
from freetime.core.lock import locked
import freetime.util.log as ftlog

@locked
def clearMatchTable(self, matchId, ccrc):
    if matchId != self.room.bigmatchId:
        ftlog.error('DizhuTableCtrlGroupMatch.clearMatchTable',
                    'matchId=', matchId,
                    'tableId=', self.tableId,
                    'ccrc=', ccrc,
                    'err=', 'DiffMatchId')
        return

    if not self.matchTableInfo:
        ftlog.error('DizhuTableCtrlGroupMatch.doMatchTableClear',
                    'matchId=', matchId,
                    'tableId=', self.tableId,
                    'ccrc=', ccrc,
                    'err=', 'table match is clear')
        return

    if ccrc != self.matchTableInfo['ccrc']:
        ftlog.error('DizhuTableCtrlGroupMatch.clearMatchTable',
                    'matchId=', matchId,
                    'tableId=', self.tableId,
                    'ccrc=', ccrc,
                    'err=', 'DiffCcrc')
        return

    self.table.forceClear()

DizhuTableCtrlArenaMatch.clearMatchTable = clearMatchTable
