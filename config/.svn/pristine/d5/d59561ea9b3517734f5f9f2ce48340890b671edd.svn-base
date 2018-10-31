# -*- coding: utf-8 -*-
'''
Created on 2016年7月27日

@author: zqh
'''
import os

from _loader._base import mainconf


def upgrade(readPath, outPath, module):
    code = '''
from _loader.game_9999.%s import load
load.main('%s/game/9999/%s/tc.json', '%s', '%s')
''' % (module, readPath,  module, outPath, module)
    exec code

if __name__ == '__main__':
    os.path.dirname(__file__)
    readPath = os.path.abspath(os.path.dirname(__file__) + './../')
    print 'CONFIG READ PATH:', readPath
    mainconf.init(readPath + '/game')
    outPath = os.path.abspath(readPath + '/../out')
    print 'CONFIG OUT  PATH:', outPath

    upgrade(readPath, outPath, 'ads')
    upgrade(readPath, outPath, 'activity')
#     upgrade(readPath, outPath, 'promote')
#     upgrade(readPath, outPath, 'gamelist')
#     upgrade(readPath, outPath, 'products')
#     upgrade(readPath, outPath, 'store')
