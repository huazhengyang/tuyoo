# -*- coding: utf-8 -*-
'''
Created on 2017年7月19日
'''

import json
import sys
import os.path
import traceback
from collections import OrderedDict

# rootdir = "/Users/paulyuan/Project/Config/branches/online-release/game/"
rootdir = "/home/tyhall/hall37/source/config_online/game"

Error_Times = 0
Warning_Times = 0


def get_capacity(roomId, serverConf, roomConf):
    ctrlServerCount = serverConf['controlServerCount']
    gameServerCount = serverConf['gameServerCount']
    gameTableCount = serverConf['gameTableCount']

    matchConf = roomConf.get('matchConf')
    tableSeatCount = matchConf.get('table.seat.count', 3)
    if roomConf.get('typeName') in ('arena_match', 'dizhu_arena_match'):
        return  gameServerCount * gameTableCount * tableSeatCount
    return ctrlServerCount * gameServerCount * gameTableCount * tableSeatCount


def get_max_user_size(roomId, serverConf, roomConf):
    if roomConf.get('typeName') in ('arena_match', 'dizhu_arena_match'):
        return roomConf['matchConf']['maxPlayerCount']
    if roomConf['matchConf']['start']['type'] == 2:
        return roomConf['matchConf']['start']['user.maxsize']
    else:
        return roomConf['matchConf']['start']['user.size']


def check_match_room(roomId, serverConf, roomConf):
    capacity = get_capacity(roomId, serverConf, roomConf)
    maxSize = get_max_user_size(roomId, serverConf, roomConf)

    if (capacity * 0.9) < maxSize:
        bad_rooms.append((roomId, maxSize, capacity))
    else:
        pass


def check_room(roomId, serverConf):
    try:
        with open(parent + '/room/%s.json' % (roomId)) as f:
            roomConf = json.load(f)
            if roomConf.get('typeName') in ('group_match', 'arena_match', 'big_match', 'erdayi_match',
                                            'dizhu_group_match', 'dizhu_arena_match', 'dizhu_erdayi_match'):
                check_match_room(roomId, serverConf, roomConf)
    except:
        traceback.print_exc()


def check_empty_templates(parent, filename):
    Path_temp = os.path.join(parent, filename)
    Config_temp_tc = json.loads(open(Path_temp).read())
    if 'templates' in Config_temp_tc:
        template_raw = Config_temp_tc['templates']
        if isinstance(template_raw, dict) :
            for k,v in template_raw.items() :
                if not v:
                    empty_templates.add(k)


def check_wrong_relationship(parent):

    template_name = set()
    Path_temp_tc = os.path.join(parent, 'tc.json')
    Path_temp_vc = os.path.join(parent, 'vc.json')
    Config_temp_tc = json.loads(open(Path_temp_tc).read())
    Config_temp_vc = json.loads(open(Path_temp_vc).read())

    if 'templates' in Config_temp_tc:
        template_all = Config_temp_tc['templates']
        template_name = set()
        if isinstance(template_all, list) :
            for k in template_all:
                template_name.add(k['name'])
        elif isinstance(template_all, dict) :
            for k in template_all :
                template_name.add(k)

    if 'actual' in Config_temp_vc:
        Config_temp_actual = Config_temp_vc['actual']
        vcList = dict([(v,k) for k,v in Config_temp_actual.items()])
        for k,v in vcList.items():
            if str(k) not in template_name and k != 'default':
                wrong_relation_list.add(k)

def check_gamelist2_version(parent):
    Path_temp_tc = os.path.join(parent, 'gamelist2/tc.json')
    Config_temp_tc = json.loads(open(Path_temp_tc).read())
    if 'templates' in Config_temp_tc:
        template_all = Config_temp_tc['templates']
        if isinstance(template_all, list) :
            for k in template_all:
                template_name_temp = k['name']
                pages_temp = k['pages']
                game_version_list = {}
                for r in pages_temp:
                    nodes_temp = r['nodes']
                    for v in nodes_temp:
                        game_id_temp = v['params']['gameId']
                        game_version_temp = v['params']['version']
                        #print game_id_temp, game_version_temp
                        found_version = game_version_list.get(game_id_temp)
                        if found_version and found_version != game_version_temp:
                            Multi_version_list.append((template_name_temp, game_id_temp, game_version_temp))
                        #    print template_name_temp, game_id_temp, game_version_temp
                        else:
                            game_version_list[game_id_temp] = game_version_temp

def check_duplicated_exchangeId(parent):
    exchangeId_list = set()
    Path_temp = os.path.join(parent, 'exmall/0.json')
    Config_temp_exhall = json.loads(open(Path_temp).read())
    if 'exchanges' in Config_temp_exhall:
        exchanges_raw = Config_temp_exhall['exchanges']
        for k in exchanges_raw:
            if k['exchangeId'] in exchangeId_list:
                duplicated_exchangeId_list.add(k['exchangeId'])
            else:
                exchangeId_list.add(k['exchangeId'])

product_list_9999_set = set()
def product_list_9999():
    Path_temp = os.path.join(rootdir, '9999/products/0.json')
    product_raw = json.loads(open(Path_temp).read())
    product_list_temp = product_raw['products']
    for k in product_list_temp:
        product_id = k['productId']
        product_list_9999_set.add(product_id)
    return product_list_9999_set
product_list_9999()

def check_product(parent):
    product_list_temp_store = set()
    Path_temp = os.path.join(parent, 'store/tc.json')
    store_config_temp = json.loads(open(Path_temp).read())
    store_config_list_temp = store_config_temp['templates']
    for k in store_config_list_temp:
        templates_name = k['name']
        shelves_temp = k['shelves']
        for k in shelves_temp:
            products_temp = k['products']
            for k in products_temp:
                product_list_temp_store.add(k)

    for k in product_list_temp_store:
        if k not in product_list_9999_set:
            wrong_product_list.add(k)

for parent,dirnames,filenames in os.walk(rootdir):
    if 'room' in dirnames:
        game_id = parent.split('/')[7]
        bad_rooms = []
        if game_id in ('6', ):
            with open(parent + '/room/0.json', 'r') as f:
                rooms = json.load(f)
                for roomId, serverConf in rooms.iteritems():
                    check_room(roomId, serverConf)
                if bad_rooms and game_id in ('6', ):
                    Error_Times += 1
                    print ('Error: Bad rooms', game_id, bad_rooms)

    if 'ads' in dirnames:
        empty_templates = set()
        try:
            check_empty_templates(parent, 'ads/tc.json')
            if empty_templates:
                Error_Times += 1
                print ('Error: Empty templates', game_id, 'ads', empty_templates)
        except:
            pass

    if 'activity' in dirnames:
        empty_templates = set()
        try:
            check_empty_templates(parent, 'activity/tc.json')
            if empty_templates:
                Error_Times += 1
                print ('Error: Empty templates', game_id, 'activity', empty_templates)
        except:
            pass

    if 'gamelist2' in dirnames:
        Multi_version_list = dict()
        try:
            check_gamelist2_version(parent)
            if Multi_version_list:
                Error_Times += 1
                print ('Error: Multi_version', Multi_version_list)
        except:
            pass

    if 'exmall' in dirnames:
        duplicated_exchangeId_list = set()
        try:
            check_duplicated_exchangeId(parent)
            if duplicated_exchangeId_list:
                Error_Times += 1
                print ('Error: Duplicated exchangeID', duplicated_exchangeId_list)
        except:
            pass
    if 'store' in dirnames:
        wrong_product_list = set()
        try:
            check_product(parent)
            if wrong_product_list:
                Error_Times += 1
                print ('Error: Wrong productID', parent, wrong_product_list)
        except:
            pass

    if "vc.json" in filenames:
        try:
            wrong_relation_list = set()
            check_wrong_relationship(parent)
            if wrong_relation_list:
                Warning_Times += 1
                # print ('Warning: Wrong relationship', game_id, parent.split('/')[9], wrong_relation_list)
        except:
            pass

if Error_Times:
    print '==========================='
    print 'Error times:', Error_Times
    print 'Warning times:', Warning_Times
    print '==========================='
    sys.exit(-1)
