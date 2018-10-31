# -*- coding: utf-8 -*-
import datetime

import _roombase
import json
import traceback


def convertrdef(rid, rdef):
    print rid
    if int(rid) == 6003 or int(rid) == 6009 or int(rid) == 6019 or int(rid) == 6029 or int(rid) == 6039:
        rdef['hasrobot'] = 0
        rdef['showCard'] = 0
        rdef['killPigLevel'] = 0
    else:    
        rdef['hasrobot'] = 1
    rdef['robotUserCallUpTime'] = 1
    rdef['robotUserMaxCount'] = -1
    rdef['robotUserOpTime'] = [1,1]
    #if int(rid) == 6211 and 'notStartTimeout' in rdef['tableConf']:
    #    rdef['tableConf']['notStartTimeout'] = 120
    if int(rid) in (6052, 6053, 6047, 6055, 6056, 6057, 6058, 6059, 6051, 6054,
                    6044, 6052, 6998,6997, 6996, 6995, 6993, 6992, 6617,
                    6991, 6060, 6061, 6062, 6064, 6065, 6066, 6069, 6063, 6069, 6070, 6071, 6072,
                    6701, 6073, 6074, 6075, 6703, 6704, 6705, 6706, 6301, 6601, 6602, 6707, 6708, 6709, 6711, 6712,
                    6603, 6605, 6607, 6608, 6609, 6610, 6611, 6612, 6613, 6614, 6719, 6304, 6305):
        if 'start' in rdef['matchConf']:
            rdef['matchConf']['start']['user.minsize'] = 3
            if int(rid) == 6994 :
                rdef['matchConf']['start']['user.maxsize'] = 6
            elif int(rid) == 6998:
                rdef['matchConf']['start']['selectFirstStage'] = 0
            else:
                rdef['matchConf']['start']['user.maxsize'] = 500
            rdef['matchConf']['start']['times']['times_in_day'] = {"first":"00:00", "interval":6, "count":238}
            dt = datetime.datetime.now().strftime('%Y%m%d')
            dayctl = rdef['matchConf']['start']['times']['days']
            if 'list' in dayctl :
                days = dayctl['list']
                if dt not in days :
                    days.append(dt)
                    days.sort()
        if 'stages' in rdef['matchConf']:
            if int(rid) == 6998:
                rdef['matchConf']['stages'][0]['grouping.user.count'] = 150
                rdef['matchConf']['stages'][0]['rise.user.refer'] = 50
                rdef['matchConf']['stages'][0]['rise.user.count'] = 30
            else:
                rdef['matchConf']['stages'][0]['grouping.user.count'] = 90
            for st in rdef['matchConf']['stages']:
                if int(rid) == 6998:
                    st['card.count'] = 5
                else:
                    st['card.count'] = 2

    if int(rid) in (6801,) :
        rdef['matchConf']['start']['times']['times_in_day'] = {"first":"00:00", "interval":2, "count":238}

    mdef = rdef.get('matchConf', None)
    if mdef and 'maxPlayerCount' in mdef :
        mdef['maxPlayerCount'] = 200

    if mdef and 'maxSigninCount' in mdef :
        mdef['maxSigninCount'] = 200


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
        print 'check_match_room roomId=', roomId, 'maxSize=', maxSize, 'capacity=', capacity
        return False, (roomId, maxSize, capacity, serverConf)
    else:
        print 'check_match_room roomId=', roomId, 'maxSize=', maxSize, 'capacity=', capacity
    return True, (roomId, maxSize, capacity, serverConf)


def check_normal_room(roomId, room):
    pass


def check_room(room_conf_root_path, roomId, serverConf):
    match_type_names = ('group_match', 'arena_match', 'big_match', 'erdayi_match',
                                            'dizhu_group_match', 'dizhu_arena_match', 'dizhu_erdayi_match')
    try:
        with open(room_conf_root_path + '%s.json' % (roomId)) as f:
            roomConf = json.load(f)
            if roomConf.get('typeName') in match_type_names:
                ok, info = check_match_room(roomId, serverConf, roomConf)
                if not ok:
                    return info
        return None
    except:
        traceback.print_exc()


def check_room_conf(room_conf_root_path):
    bad_rooms = []
    with open(room_conf_root_path + '0.json', 'r') as f:
        rooms = json.load(f)
        for roomId, serverConf in rooms.iteritems():
            bad_info = check_room(room_conf_root_path, roomId, serverConf)
            if bad_info:
                bad_rooms.append(bad_info)
    if bad_rooms:
        print bad_rooms
        raise Exception('check room conf failed')
    else:
        print 'check room conf ok'


check_room_conf('./game/6/room/')
_roombase.convert(6, convertrdef)
