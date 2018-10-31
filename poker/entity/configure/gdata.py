# -*- coding: utf-8 -*-
"""
Created on 2015-5-12
@author: zqh
"""
import stackless
import psutil
import freetime.entity.config as ftcon
import freetime.util.log as ftlog
ENABLIE_DEFENCE_2 = 1
RUN_MODE_ONLINE = 1
RUN_MODE_SIMULATION = 2
RUN_MODE_RICH_TEST = 3
RUN_MODE_TINY_TEST = 4
SRV_TYPE_AGENT = 'AG'
SRV_TYPE_SDK_HTTP = 'PL'
SRV_TYPE_SDK_GATEWAY = 'PG'
SRV_TYPE_CONN = 'CO'
SRV_TYPE_HTTP = 'HT'
SRV_TYPE_ROBOT = 'RB'
SRV_TYPE_UTIL = 'UT'
SRV_TYPE_ROOM = 'GR'
SRV_TYPE_TABLE = 'GT'
SRV_TYPE_CENTER = 'CT'
SRV_TYPE_PKG_NAME = {SRV_TYPE_AGENT: 'agent', SRV_TYPE_SDK_HTTP: 'http', SRV_TYPE_CONN: 'conn', SRV_TYPE_HTTP: 'http', SRV_TYPE_ROBOT: 'robot', SRV_TYPE_UTIL: 'util', SRV_TYPE_ROOM: 'room', SRV_TYPE_TABLE: 'table', SRV_TYPE_CENTER: 'center', SRV_TYPE_SDK_GATEWAY: 'gateway'}
SRV_TYPE_ALL = (SRV_TYPE_AGENT, SRV_TYPE_SDK_HTTP, SRV_TYPE_CONN, SRV_TYPE_HTTP, SRV_TYPE_ROBOT, SRV_TYPE_UTIL, SRV_TYPE_ROOM, SRV_TYPE_TABLE, SRV_TYPE_CENTER, SRV_TYPE_SDK_GATEWAY)
PROTOCOL_TYPE_HTTP = 'ht-http'
PROTOCOL_TYPE_CONN = 'co-tcp'
PROTOCOL_TYPE_GAME_S2A = 's2a'
CONN_CMD_ROUTE_TYPE_RANDOM = 'random'
CONN_CMD_ROUTE_TYPE_UESRID = 'userId'
CONN_CMD_ROUTE_TYPE_ROOMID = 'roomId'
CONN_CMD_ROUTE_TYPE_TABLEID = 'tableId'
_datas = {}
curProcess = psutil.Process()

def _initialize():
    pass

def initializeOk():
    """
    判定当前各个游戏是否初始化完成
    注: 由poker系统initialize()方法进行初始化
    """
    pass

def getTaskSession():
    pass

def isControlProcess():
    pass

def isHttpProcess():
    pass

def gamePackages():
    """
    取得要初始化的游戏的package包列表, 例如: ['hall', 'dizhu', 'texas']
    """
    pass

def games():
    """
    取得当前系统初始化后的TYGame的所有实例
    key为: int(gameId)
    value为: TYGame()
    注: 由poker系统initialize()方法进行初始化
    """
    pass

def gameIds():
    """
    取得当前系统初始化后的TYGame的ID列表
    注: 由poker系统initialize()方法进行初始化
    """
    pass

def getGame(gameId):
    """
    取得当前系统初始化后的TYGame的所有实例
    key为: int(gameId)
    value为: TYGame()
    注: 由poker系统initialize()方法进行初始化
    """
    pass

def rooms():
    """
    取得当前系统初始化后的TYRoom的所有实例
    key为: int(roomId)
    value为: TYRoom()
    注: 由poker系统initialize()方法进行初始化
    """
    pass

def srvIdRoomIdListMap():
    """
    取得ROOM的进程的映射关系, key为str(serverId), value为int(ROOMID)的list
    """
    pass

def roomIdDefineMap():
    """
    取得ROOM的进程的映射关系, key为int(roomId), value为ROOM的基本定义信息
    ROOM的基本定义信息RoomDefine:
    
    RoomDefine.bigRoomId     int 当前房间的大房间ID, 即为game/<gameId>/room/0.json中的键
    RoomDefine.parentId      int 父级房间ID, 当前为管理房间时, 必定为0 (管理房间, 可以理解为玩家队列控制器)
    RoomDefine.roomId        int 当前房间ID
    RoomDefine.gameId        int 游戏ID
    RoomDefine.configId      int 配置分类ID
    RoomDefine.controlId     int 房间控制ID
    RoomDefine.shadowId      int 影子ID
    RoomDefine.tableCount    int 房间中桌子的数量
    RoomDefine.shadowRoomIds tuple 当房间为管理房间时, 下属的桌子实例房间的ID列表
    RoomDefine.configure     dict 房间的配置内容, 即为game/<gameId>/room/0.json中的值
    """
    pass

def bigRoomidsMap():
    """
    取得ROOM的配置ID的映射关系, key为int(bigRoomId), value为int(roomId)的list
    此处的roomId列表仅包含"管理房间"的ID, 不包含"桌子实例房间shadowRoom"的ID
    """
    pass

def gameIdBigRoomidsMap():
    """
    取得ROOM的配置ID的映射关系, key为int(gameId), value为int(bigRoomId)的list
    """
    pass

def getBigRoomId(roomId):
    pass

def getRoomConfigure(roomId):
    pass

def getRoomMinCoin(roomId):
    pass

def getRoomMaxCoin(roomId):
    pass

def getRoomMutil(roomId):
    pass

def globalConfig():
    """
    取得global.json的配置内容
    """
    pass

def serverTypeMap():
    """
    取得服务类型和服务ID的配置, key为服务类型(SRV_TYPE_XXX), value 为服务ID的list
    """
    pass

def allServersMap():
    """
    取得全部进程的定义,key为进程ID, value为进程信息的dict
    """
    pass

def serverId():
    """
    当前进程的ID, 例如: GA00060001, UT01
    """
    pass

def serverType():
    """
    当前进程的类型, 例如: GA, UT
    """
    pass

def serverNum():
    """
    当前进程的ID去掉类型后的部分, 例如: 00060001, 01
    """
    pass

def serverNumIdx():
    """
    当前进程的ID去掉类型后的部分, 例如: 00060001, 01
    """
    pass

def centerServerLogics():
    """
    取得配置当中, CENTER定义的业务逻辑服务
    """
    pass

def name():
    """
    在poker.json中定义的name的值
    """
    pass

def corporation():
    """
    在poker.json中定义的corporation的值
    """
    pass

def mode():
    """
    运行模式, 在poker.json中定义的mode的值
    参考: RUN_MODE_ONLINE, RUN_MODE_SIMULATION, RUN_MODE_RICH_TEST, RUN_MODE_TINY_TEST
    """
    pass

def pathBin():
    """
    在poker.json中定义的output.path的值加上bin
    即PY文件的编译输出路径
    """
    pass

def pathWebroot():
    """
    在poker.json中定义的output.path的值加上webroot
    即WEBROOT的编译输出路径
    """
    pass

def httpDownload():
    """
    在poker.json中定义的http.download的值
    """
    pass

def httpGame():
    """
    在poker.json中定义的http.game的值
    """
    pass

def httpSdk():
    """
    在poker.json中定义的http.sdk的值
    """
    pass

def httpSdkInner():
    """
    在poker.json中定义的http.sdk.inner的值
    """
    pass

def httpAvatar():
    """
    在poker.json中定义的http.sdk.inner的值
    """
    pass

def httpGdss():
    """
    全局数据同步中心的HTTP地址,例如: clientid的同步地址
    """
    pass

def httpOnlieGateWay():
    """
    全局数据同步中心的HTTP地址,例如: clientid的同步地址
    """
    pass

def biReportGroupInfo():
    """
    取得BI汇报的配置中, 对应汇报类型rec_type的分组个数
    """
    pass

def enableTestHtml():
    """
    判定是否开启测试页面, 通常线上服务是关闭的
    """
    pass

def cloudId():
    """
    判定是否开启测试页面, 通常线上服务是关闭的
    """
    pass

def isH5():
    """
    判定是否运行于H5服务模式, H5模式TCP接入的是WEBSOCKET
    """
    pass

def getUserConnIpPortList():
    """
    取得客户端可接入的TCPIP的IP和端口号列表[(ip, port),(ip, port),(ip, port)...]
    """
    pass

def _dumpGdataInfo():
    pass