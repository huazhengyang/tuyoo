# -*- coding: utf-8 -*-
'''
Created on 2015年5月20日

@author: zqh
'''

from collections import namedtuple

from freetime.core.timer import FTTimer
import freetime.entity.config as ftcon
import freetime.entity.service as ftsvr
import freetime.util.log as ftlog
from poker.entity.configure import gdata, configure
from poker.entity.events.tyevent import EventHeartBeat
from poker.entity.events.tyeventbus import globalEventBus
from poker.entity.game.game import TYGame
from poker.protocol.procstatus import updateStatus
from poker.util import strutil
from poker.util.objects import makeReadonly
from freetime.core.tasklet import FTTasklet
from freetime.util import performance
from freetime.core import protocol

_DEBUG = 0
debug = ftlog.info


def getProtoClassByName(protoname):
    '''
    扑克大厅系统的协议层支持设定
    '''
    server_id = ftsvr.getId()
    stype = server_id[0:2]

    if protoname == gdata.PROTOCOL_TYPE_HTTP:
        if stype == gdata.SRV_TYPE_HTTP:
            from poker.protocol.http.protocols import TYHttpChannel
            return TYHttpChannel

        if stype == gdata.SRV_TYPE_SDK_HTTP:
            from poker.protocol.platform.protocols import PLHttpChannel
            return PLHttpChannel

    if protoname == gdata.PROTOCOL_TYPE_CONN:
        if stype == gdata.SRV_TYPE_CONN:
            if ftcon.global_config.get('is_h5', 0):
                from poker.protocol.conn.protocols import COTCPProtoWS
                return COTCPProtoWS
            else:
                from poker.protocol.conn.protocols import COTCPProtoZIP
                return COTCPProtoZIP

    if protoname == gdata.PROTOCOL_TYPE_GAME_S2A:
        if stype == gdata.SRV_TYPE_CONN:
            from poker.protocol.conn.protocols import COS2AProto
            return COS2AProto

        if stype == gdata.SRV_TYPE_HTTP:
            from poker.protocol.http.protocols import HTS2AProto
            return HTS2AProto

        if stype == gdata.SRV_TYPE_SDK_HTTP:
            from poker.protocol.platform.protocols import PLS2AProto
            return PLS2AProto

        if stype == gdata.SRV_TYPE_ROOM:
            from poker.protocol.room.protocols import GRS2AProto
            return GRS2AProto

        if stype == gdata.SRV_TYPE_TABLE:
            from poker.protocol.table.protocols import GTS2AProto
            return GTS2AProto

        if stype == gdata.SRV_TYPE_ROBOT:
            from poker.protocol.robot.protocols import RBS2AProto
            return RBS2AProto

        if stype == gdata.SRV_TYPE_UTIL:
            from poker.protocol.util.protocols import UTS2AProto
            return UTS2AProto

        if stype == gdata.SRV_TYPE_CENTER:
            from poker.protocol.center.protocols import CTS2AProto
            return CTS2AProto

    raise Exception('UnKnow Protocol type ! protoname=' + str(protoname) + ' server_id=' + str(server_id))


def initialize():
    '''
    扑克大厅系统的初始化入口
    当所有的REDIS和MYSQL链接建立完成后调用此方法
    '''
    try:
        if _DEBUG:
            debug('==== poker.initialize begin ====')
        sconf = ftcon.getServerConf(ftsvr.getId())
        taskc = sconf.get('task-concurrent', 0)
        if taskc > 0:
            FTTasklet.MAX_CONCURRENT = taskc
            if _DEBUG:
                debug('reset FTTasklet.MAX_CONCURRENT=', FTTasklet.MAX_CONCURRENT)

        from poker.entity.dao import daobase
        daobase._REDIS_CMD_PPS_ = 1
        configure._CONFIG_CMD_PPS_ = 1
        protocol._COUNT_PPS = 1
        performance.regPPSCounter(protocol.ppsCountProtocolPack)
        performance.regPPSCounter(configure.ppsCountConfigCmds)
        performance.regPPSCounter(daobase.ppsCountRedisCmd)
        performance.regPPSCounter(performance.threadInfo)

        # 初始化基本全局配置数据
        updateStatus(10)
        gdatas = gdata._initialize()

        from poker.entity.biz import bireport
        bireport.report('bireport', 'open')

        # 初始化DAO
        updateStatus(20)
        daobase._initialize()

        # 初始化旧命令对照表
        updateStatus(30)
        from poker.protocol import oldcmd
        oldcmd._initialize()

        # 装载游戏的PLUGIN
        updateStatus(40)
        tygamelist = _loadTYGames(gdatas)

        # 初始化命令路由
        updateStatus(50)
        from poker.protocol import router
        router._initialize()

        if gdata.serverType() == gdata.SRV_TYPE_UTIL:
            router._initialize_udp()

        # 初始化房间配置
        updateStatus(60)
        _loadRoomDefines(gdatas)

        # 各个游戏PLUGIN的命令入口初始化
        updateStatus(70)
        from poker.protocol import handler
        handler._initializeCommands(gdatas)

        from poker.protocol import rpccore
        rpccore._initializeRpcMehodss(gdatas)

        if gdata.serverType() not in (gdata.SRV_TYPE_AGENT, gdata.SRV_TYPE_CONN):
            # 所有游戏PLUGIN进行初始化
            updateStatus(80)
            for tygame in tygamelist:
                if _DEBUG:
                    debug('call init function : ', tygame.gameId(), 'tygame.initGameBefore()')
                tygame.initGameBefore()

            # 所有游戏PLUGIN进行初始化
            updateStatus(90)
            for tygame in tygamelist:
                if _DEBUG:
                    debug('call init function : ', tygame.gameId(), 'tygame.initGame()')
                tygame.initGame()

            # 房间实例初始化
            updateStatus(100)
            _initializeRooms(gdatas)

            # 桌子示例初始化
            updateStatus(110)
            _initializeTables(gdatas)

            # 所有游戏PLUGIN进行初始化
            updateStatus(120)
            for tygame in tygamelist:
                if _DEBUG:
                    debug('call init function : ', tygame.gameId(), 'tygame.initGameAfter()')
                tygame.initGameAfter()

        # 大厅全局命令入口初始化
        updateStatus(130)
        _initializePoker(gdatas)

        # 设置初始化完成标记
        updateStatus(200)
        gdatas['initialize.ok'] = 1
        if _DEBUG:
            debug('==== poker.initialize done ====')

        # 启动服务系统心跳处理事件
        FTTimer(1, _doServertHeartBeat)

    except:
        updateStatus(500)
        ftlog.error('poker.initialize ERROR')
        ftsvr.terminate()


def _doServertHeartBeat():
    '''
    每秒钟一次的心跳事件广播, 执行之后间隔一秒再次启动, 即: 这个每秒心跳是个大约值,非准确值
    '''
    event = EventHeartBeat()
    event.count = event.count + 1
    globalEventBus.publishEvent(event)
    FTTimer(1, _doServertHeartBeat)


def _auto_change_room_count(roomDict):
    '''
    此方法和webmgr中mode1～mode4的削减标准一致
    '''
    mode = gdata.mode()
    if mode == gdata.RUN_MODE_ONLINE:  # 模式1，完全配置控制
        return roomDict

    if mode == gdata.RUN_MODE_SIMULATION:
        pcount = 2  # 模式2，限制为二个进程
        tcount = 100  # 模式3， 4限制为一个桌子

    if mode in (gdata.RUN_MODE_RICH_TEST, gdata.RUN_MODE_TINY_TEST):
        pcount = 1  # 模式2，限制为二个进程
        tcount = 200  # 模式3， 4限制为一个桌子

    roomDict['controlServerCount'] = min(pcount, int(roomDict['controlServerCount']))
    roomDict['controlTableCount'] = min(pcount, int(roomDict['controlTableCount']))
    roomDict['gameServerCount'] = min(pcount, int(roomDict['gameServerCount']))
    roomDict['gameTableCount'] = min(tcount, int(roomDict['gameTableCount']))
    return roomDict


def _loadRoomDefines(gdatas):
    '''
    需要整理一个全局的 serverid-roomid-roombaseinfo的大集合
    取得server_rooms.json的配置内容, key为服务ID, value为房间配置内容
    '''
    if _DEBUG:
        debug('loadRoomDefines begin')
    # 首先整理进程ID, 展开多房间进程的进程ID
    srvid_rooms_map = {}
    srvidmap = {}
    allserver = gdata.allServersMap()
    for k in allserver:
        srvid_rooms_map[k] = []
        if k.find('-') > 0:
            assert (k.find(gdata.SRV_TYPE_ROOM) == 0 or k.find(gdata.SRV_TYPE_TABLE) == 0)
            tail = '000'
            if k.find(gdata.SRV_TYPE_TABLE) == 0:
                tail = '001'
            ks = k.split('-')
            ps = int(ks[1])
            pe = int(ks[2])
            assert (ps > 0 and ps < 999)
            assert (pe > 0 and pe < 999)
            assert (ps < pe)
            for x in xrange(ps, pe + 1):
                playid = '%03d' % (x)
                sid = ks[0] + playid + ks[3]
                srvidmap[sid + tail] = k
        else:
            if k.find(gdata.SRV_TYPE_ROOM) == 0:
                srvidmap[k + '000'] = k
            if k.find(gdata.SRV_TYPE_TABLE) == 0:
                srvidmap[k] = k

    clsRoomDefine = namedtuple('RoomDefine', ['bigRoomId', 'parentId', 'roomId', 'gameId',
                                              'configId', 'controlId', 'shadowId', 'serverId',
                                              'tableCount', 'shadowRoomIds', 'configure'])
    roomid_define_map = {}
    big_roomids_map = {}
    gameid_big_roomids_map = {}
    # 取得说有挂接的游戏ID, 取得对应GAMEID的房间配置
    gameids = gdata.games().keys()
    if _DEBUG:
        debug('the game ids=', gameids)
    for gid in gameids:
        gameid_big_roomids_map[gid] = []
        roomdict = ftcon.getConfNoCache('GET', 'game:' + str(gid) + ':room:0')
        if roomdict:
            roomdict = strutil.loads(roomdict)
        if not isinstance(roomdict, dict):
            if _DEBUG:
                debug('the game of', gid, 'have no room !')
            continue
        for roomIdStr, configure in roomdict.items():
            bigRoomId = int(roomIdStr)
            gameid, configid = strutil.parseBigRoomId(bigRoomId)

            configure = _auto_change_room_count(configure)
            controlServerCount = int(configure['controlServerCount'])
            controlTableCount = int(configure['controlTableCount'])
            gameServerCount = int(configure['gameServerCount'])
            gameTableCount = int(configure['gameTableCount'])

            assert (gameid == gid)
            assert (configid > 0 and configid < 999), '%s,%s' % (roomIdStr, str(configure))
            assert (controlServerCount > 0 and controlServerCount < 9), '%s,%s' % (roomIdStr, str(configure))
            assert (controlTableCount >= 0 and controlTableCount < 9999), '%s,%s' % (roomIdStr, str(configure))
            assert (gameServerCount >= 0 and gameServerCount < 999), '%s,%s' % (roomIdStr, str(configure))
            assert (gameTableCount > 0 and gameTableCount < 9999), '%s,%s' % (roomIdStr, str(configure))
            assert (not bigRoomId in big_roomids_map)

            extconfig = ftcon.getConfNoCache('GET', 'game:' + str(gid) + ':room:' + str(bigRoomId))
            if extconfig:
                extconfig = strutil.loads(extconfig)
            if isinstance(extconfig, dict):
                configure.update(extconfig)

            gameid_big_roomids_map[gid].append(bigRoomId)
            big_roomids_map[bigRoomId] = []
            for m in xrange(controlServerCount):
                # 自动计算controlId, 重1开始
                controlId = m + 1
                controlRoomId = (bigRoomId * 10 + controlId) * 1000
                shadowRooms = []
                assert (not controlRoomId in big_roomids_map)
                assert (not controlRoomId in roomid_define_map)
                for n in xrange(gameServerCount):
                    # 自动计算shadowId, 重1开始, 此处为桌子运行的房间
                    shadowId = n + 1
                    shadowRoomId = controlRoomId + shadowId
                    assert (not shadowRoomId in roomid_define_map)
                    processId = gdata.SRV_TYPE_TABLE + str(shadowRoomId)
                    serverId = srvidmap[processId]
                    srvid_rooms_map[serverId].append(shadowRoomId)
                    shadowRooms.append(shadowRoomId)
                    roomid_define_map[shadowRoomId] = clsRoomDefine(bigRoomId, controlRoomId, shadowRoomId, gameid,
                                                                    configid, controlId, shadowId, serverId,
                                                                    gameTableCount, tuple([]), configure)
                    if _DEBUG:
                        debug('load room define->bigRoomId=', bigRoomId, 'parentId=', controlRoomId,
                              'roomId=', shadowRoomId, 'gameId=', gameid, 'configId=', configid,
                              'controlId=', controlId, 'shadowId=', shadowId, 'tableCount=', gameTableCount,
                              'serverId=', serverId)

                # 此处为控制房间
                processId = gdata.SRV_TYPE_ROOM + str(controlRoomId)
                serverId = srvidmap[processId]
                srvid_rooms_map[serverId].append(controlRoomId)
                big_roomids_map[bigRoomId].append(controlRoomId)
                roomid_define_map[controlRoomId] = clsRoomDefine(bigRoomId, 0, controlRoomId, gameid,
                                                                 configid, controlId, 0, serverId,
                                                                 controlTableCount, tuple(shadowRooms), configure)
                if _DEBUG:
                    debug('load room define->bigRoomId=', bigRoomId, 'parentId=', 0,
                          'roomId=', controlRoomId, 'gameId=', gameid, 'configId=', configid,
                          'controlId=', controlId, 'shadowId=', 0, 'tableCount=', controlTableCount,
                          'serverId=', serverId, 'shadowRooms=', shadowRooms)
        gameid_big_roomids_map[gid].sort()

    # 整理打印配置的内容
    if _DEBUG:
        debug('find big roomids=', big_roomids_map.keys())
    for k, v in big_roomids_map.items():
        if _DEBUG:
            debug('find big room id ', k, 'has childs :', v)
    for k in srvid_rooms_map.keys():
        if not srvid_rooms_map[k]:
            del srvid_rooms_map[k]
        else:
            if _DEBUG:
                debug('find server', k, 'has roomids :', srvid_rooms_map[k])

    gdatas['srvid_roomid_map'] = makeReadonly(srvid_rooms_map)
    gdatas['roomid_define_map'] = makeReadonly(roomid_define_map)
    gdatas['big_roomids_map'] = makeReadonly(big_roomids_map)
    gdatas['gameid_big_roomids_map'] = makeReadonly(gameid_big_roomids_map)
    if _DEBUG:
        debug('loadRoomDefines end')


def _loadTYGames(gdatas):
    '''
    装载挂接的游戏PLUGIN, 挂接多少PLUGIN由配置: poker:global中的game_packages决定
    '''
    if _DEBUG:
        debug('loadTYGames begin')
    tygames = {}
    gdatas['tygame.instance.dict'] = tygames
    gdatas['tygame.instance.ids'] = set(tygames.keys())
    tygamelist = []
    mpkgs = set()
    for pkg in gdata.gamePackages():
        if _DEBUG:
            debug('load TYGame package :', pkg)
        assert (not pkg in mpkgs)
        mpkgs.add(pkg)

        initfun = None
        exec 'from %s.game import getInstance as initfun' % (pkg)
        assert (callable(initfun))
        tygame = initfun()

        assert (isinstance(tygame, TYGame))
        tygame._packageName = pkg

        gameid = tygame.gameId()
        assert (isinstance(gameid, int))
        assert (gameid > 0 and gameid <= 9999)
        assert (not gameid in tygames)
        tygames[gameid] = tygame
        tygamelist.append(tygame)
        if _DEBUG:
            debug('load TYGame of ', gameid, tygame)

    tygamelist.sort(key=lambda x: x.gameId(), reverse=True)
    gdatas['tygame.instance.ids'] = set(tygames.keys())
    gdatas['tygame.instance.dict'] = makeReadonly(tygames)
    if _DEBUG:
        debug('loadTYGames end')
    return tygamelist


def _initializeRooms(gdatas):
    '''
    初始化所有的房间对象
    '''
    if _DEBUG:
        debug('initializeRooms begin')
    from poker.entity.game.rooms import getInstance
    srvid = gdata.serverId()
    roomids = gdata.srvIdRoomIdListMap().get(srvid, None)
    if _DEBUG:
        debug('initializeRooms srvid=', srvid, 'roomids=', roomids)
    if roomids:
        tyrooms = {}
        gdatas['tyrooms.instance.dict'] = tyrooms
        allrooms = gdata.roomIdDefineMap()
        if _DEBUG:
            debug('initializeRooms allroomsid=', allrooms.keys())
        for roomid in roomids:
            roomdefine = allrooms[roomid]
            roomins = getInstance(roomdefine)
            tyrooms[roomid] = roomins
        gdatas['tyrooms.instance.dict'] = makeReadonly(tyrooms)
    if _DEBUG:
        debug('initializeRooms end')


def _initializeTables(gdatas):
    '''
    初始化所有的桌子对象
    '''
    if _DEBUG:
        debug('initializeTables begin')
    srvid = gdata.serverId()
    roomids = gdata.srvIdRoomIdListMap().get(srvid, None)
    if roomids:
        allrooms = gdata.roomIdDefineMap()
        tyrooms = gdata.rooms()
        for roomid in roomids:
            room = tyrooms[roomid]
            roomdefine = allrooms[roomid]
            gameins = gdata.games()[roomdefine.gameId]
            if _DEBUG:
                debug('initializeTables roomid=', roomid, 'tableCount=', roomdefine.tableCount)
            if roomdefine.tableCount > 0:
                baseid = roomid * 10000 + 1
                for x in xrange(roomdefine.tableCount):
                    tableid = baseid + x
                    tableins = gameins.newTable(room, tableid)
                    room.maptable[tableid] = tableins
    if _DEBUG:
        debug('initializeTables end')


def _initializePoker(gdatas):
    '''
    初始化服务的基本(大厅通用)的HTTP和TCP命令入口
    '''
    if _DEBUG:
        debug('initializePoker begin')
    stype = gdata.serverType()

    # 启动全局配置系统的同步
    from poker.entity.configure import synccenter
    synccenter._initialize()
    globalEventBus.subscribe(EventHeartBeat, synccenter.doSyncData)

    from poker.entity.biz import integrate
    integrate._initialize()

    # 如果是CONN进程, 那么启动空闲TCP链接的检查
    if stype == gdata.SRV_TYPE_CONN:
        from poker.protocol.conn.protocols import doCleanUpEmptyTcp
        globalEventBus.subscribe(EventHeartBeat, doCleanUpEmptyTcp)

    # 如果是AGENT进程, 那么启用自身的命令处理器
    if stype == gdata.SRV_TYPE_AGENT:
        from poker.protocol.common.protocols import onAgentSelfCommand
        from freetime.support.tcpagent.protocol import A2SProtocol, A2AProtocol
        A2SProtocol.onCommand = onAgentSelfCommand
        A2AProtocol.onCommand = onAgentSelfCommand

    if gdata.isHttpProcess():
        from poker.protocol import runhttp
        runhttp.addWebRoot(gdata.pathWebroot())

    if stype == gdata.SRV_TYPE_UTIL:
        from poker.entity.dao import datasubscribe
        datasubscribe._initialize()

    if _DEBUG:
        debug('initializePoker end')
