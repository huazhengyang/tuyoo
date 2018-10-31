# -*- coding=utf-8
'''
Created on 2016年9月5日
好友/熟人自建桌模板
负责好友桌的建桌/进入流程

本模块不负责配置，由各个游戏管理自建桌需要的配合
只需要配置符合规范即可
@author: zhaol
'''
from hall.entity.hallconf import HALL_GAMEID
from poker.entity.game.game import TYGame
import freetime.util.log as ftlog
from hall.entity.todotask import TodoTaskHelper,\
    TodoTaskPopTip
from poker.entity.dao import daobase
import random
from poker.entity.configure import gdata
import poker.util.timestamp as pktimestamp
from freetime.entity.msg import MsgPack
from poker.protocol import router

FRIEND_TABLE_MAIN_KEY = "friend_table"
FRIEND_TABLE_ROOM_INDEX = "friend_table_index"
FRIEND_TABLE_PLUGIN = "plugin"
FRIEND_TABLE_ROOMID = "roomId"
FRIEND_TABLE_TABLEID = "tableId"
FRIEND_TABLE_RANDOM_KEY = "friend_table_random"
FRIEND_TABLE_RANDOM_COUNT = 1000000

def getStringFTId(roomNumber):
    """获取六位字符串房号"""
    return "%06d" % roomNumber

def createFriendTable(pluginId):
    '''
    创建好友桌
    config - 创建好友桌的参数，非房主依靠config参数加入自建桌
    pluginId - 插件游戏ID
    '''
    # 随机选择自建桌ID
    index = daobase.executeMixCmd('hincrby', FRIEND_TABLE_MAIN_KEY, FRIEND_TABLE_ROOM_INDEX, 1)
    index = index % FRIEND_TABLE_RANDOM_COUNT
    ftlog.debug('hall_friend_table.createFriendTable index: ', index)
    
    ftNumStr = daobase.executeMixCmd('LINDEX', FRIEND_TABLE_RANDOM_KEY, index)
    if ftNumStr:
        ftId = getStringFTId(int(ftNumStr))
        ftlog.debug('hall_friend_table.createFriendTable ftId:', ftId)
    
        check = TYGame(pluginId).checkFriendTable(ftId)
        if check:
            ftlog.info('hall_friend_table.createFriendTable ftId:', ftId, ' already used by plugin:', pluginId)
            return None
        else:
            daobase.executeMixCmd('HSET', FRIEND_TABLE_MAIN_KEY + ftId, FRIEND_TABLE_PLUGIN, pluginId)
            # 设置过期时间
            daobase.executeMixCmd('expire', FRIEND_TABLE_MAIN_KEY + ftId, 604800)
            ftlog.info('hall_friend_table.createFriendTable distribution ftId:', ftId, ' to plugin:', pluginId)
            return ftId
    else:
        ftlog.info('hall_friend_table.createFriendTable get ftId index:', index, ' error, please check redis!!')
        return None

ROOM_NOT_EXIST = {"code": -1, "info": "该房间不存在"}
NOT_SUPPORT_PLUGIN = {"code": -2, "info":"该安装包不支持此房间号所对应的玩法"}
ENTER_FRIEND_OK = {"code": 0, "info": "ok"}

def enterFriendTable(userId, gameId, clientId, ftId):
    """进入自建桌"""
    if ftlog.is_debug():
        ftlog.debug('hall_friend_table.enterFriendTable userId:', userId, ' pluginId:', gameId, ' clientId:', clientId,
                    ' ftId:', ftId)

    pluginId = queryFriendTable(ftId)
    if not pluginId:
        TodoTaskHelper.sendTodoTask(HALL_GAMEID, userId, TodoTaskPopTip(ROOM_NOT_EXIST['info']))
        responseEnterFriendTable(userId, ROOM_NOT_EXIST)
        return

    ftlog.info('hall_friend_table.enterFriendTable userId:', userId, ' lead to pluginId:', pluginId)
    pluginId = int(pluginId)
    TYGame(pluginId).enterFriendTable(userId, gameId, clientId, ftId)
    responseEnterFriendTable(userId, ENTER_FRIEND_OK)
    
def responseEnterFriendTable(userId, exInfo):
    mo = MsgPack()
    mo.setCmd('game')
    mo.setResult('action', 'enter_friend_table')
    mo.setResult('gameId', HALL_GAMEID)
    mo.setResult('userId', userId)
    mo.setResult('code', exInfo['code'])
    mo.setResult('info', exInfo['info'])
    router.sendToUser(mo, userId)
    
def queryFriendTable(ftId):
    """查询自建桌信息"""
    pluginId = daobase.executeMixCmd('HGET', FRIEND_TABLE_MAIN_KEY + ftId, FRIEND_TABLE_PLUGIN)
    return pluginId
    
def releaseFriendTable(pluginId, ftId):
    '''
    回收大厅自建桌房号
    pluginId 插件游戏ID
    ftId 大厅自建桌房号
    '''
    ftlog.info('hall_friend_table.releaseFriendTable pluginId:', pluginId
            , ' ftId:', ftId)
    daobase.executeMixCmd('DEL', FRIEND_TABLE_MAIN_KEY + ftId)

def _initialize():
    """初始化100万个自建桌房号"""
    if gdata.serverType() != gdata.SRV_TYPE_CENTER:
        return
    
    ftlog.debug('hall_friend_table._initialize check friend table randoms in process CT')    
    randomLen = daobase.executeMixCmd('LLEN', FRIEND_TABLE_RANDOM_KEY)
    ftlog.debug('hall_friend_table._initialize randomLen:', randomLen)
        
    if randomLen != FRIEND_TABLE_RANDOM_COUNT:
        ftlog.debug('hall_friend_table._initialize push random begin:', pktimestamp.getCurrentTimestamp())
        
        daobase.executeMixCmd('DEL', FRIEND_TABLE_RANDOM_KEY)
        rList = [x for x in range(0, 1000000)]
        random.shuffle(rList)
        
        # 每次PUSH 100个
        for index in range(0, 10000):
            begin = index * 100
            daobase.executeMixCmd('LPUSH', FRIEND_TABLE_RANDOM_KEY
                , rList[begin], rList[begin + 1], rList[begin + 2], rList[begin + 3], rList[begin + 4]
                , rList[begin + 5], rList[begin + 6], rList[begin + 7], rList[begin + 8], rList[begin + 9]
                
                , rList[begin + 10], rList[begin + 11], rList[begin + 12], rList[begin + 13], rList[begin + 14]
                , rList[begin + 15], rList[begin + 16], rList[begin + 17], rList[begin + 18], rList[begin + 19]
                
                , rList[begin + 20], rList[begin + 21], rList[begin + 22], rList[begin + 23], rList[begin + 24]
                , rList[begin + 25], rList[begin + 26], rList[begin + 27], rList[begin + 28], rList[begin + 29]
                
                , rList[begin + 30], rList[begin + 31], rList[begin + 32], rList[begin + 33], rList[begin + 34]
                , rList[begin + 35], rList[begin + 36], rList[begin + 37], rList[begin + 38], rList[begin + 39]
                
                , rList[begin + 40], rList[begin + 41], rList[begin + 42], rList[begin + 43], rList[begin + 44]
                , rList[begin + 45], rList[begin + 46], rList[begin + 47], rList[begin + 48], rList[begin + 49]
                
                , rList[begin + 50], rList[begin + 51], rList[begin + 52], rList[begin + 53], rList[begin + 54]
                , rList[begin + 55], rList[begin + 56], rList[begin + 57], rList[begin + 58], rList[begin + 59]
                
                , rList[begin + 60], rList[begin + 61], rList[begin + 62], rList[begin + 63], rList[begin + 64]
                , rList[begin + 65], rList[begin + 66], rList[begin + 67], rList[begin + 68], rList[begin + 69]
                
                , rList[begin + 70], rList[begin + 71], rList[begin + 72], rList[begin + 73], rList[begin + 74]
                , rList[begin + 75], rList[begin + 76], rList[begin + 77], rList[begin + 78], rList[begin + 79]
                
                , rList[begin + 80], rList[begin + 81], rList[begin + 82], rList[begin + 83], rList[begin + 84]
                , rList[begin + 85], rList[begin + 86], rList[begin + 87], rList[begin + 88], rList[begin + 89]
                
                , rList[begin + 90], rList[begin + 91], rList[begin + 92], rList[begin + 93], rList[begin + 94]
                , rList[begin + 95], rList[begin + 96], rList[begin + 97], rList[begin + 98], rList[begin + 99]
                )
        
        ftlog.debug('hall_friend_table._initialize push random end:', pktimestamp.getCurrentTimestamp())
        
        
"""
自建桌日志
"""
def getFriendTableInfo(tableNo):
    """获取自建桌的参数"""
    params = {}
    pluginId = daobase.executeMixCmd('HGET', FRIEND_TABLE_MAIN_KEY + tableNo, FRIEND_TABLE_PLUGIN)
    if pluginId:
        params['pluginId'] = pluginId
        
    roomId = daobase.executeMixCmd('HGET', FRIEND_TABLE_MAIN_KEY + tableNo, FRIEND_TABLE_ROOMID)
    if roomId:
        params['roomId'] = roomId
        
    tableId = daobase.executeMixCmd('HGET', FRIEND_TABLE_MAIN_KEY + tableNo, FRIEND_TABLE_TABLEID)
    if tableId:
        params['tableId'] = tableId
    
    ftlog.debug('hall_friend_table.getFriendTableInfo params:', params)
    return params

def gameBegin(tableNo, seats, gameId, roomId, tableId):
    """开局日志"""
    ftlog.info('hall_friend_table.gameBegin tableNo=', tableNo
        , ' seats=', seats
        , ' gameId=', gameId
        , ' roomId=', roomId
        , ' tableId=', tableId
        , ' time=', pktimestamp.getCurrentTimestamp())
    daobase.executeMixCmd('HSET', FRIEND_TABLE_MAIN_KEY + tableNo, FRIEND_TABLE_ROOMID, roomId)
    daobase.executeMixCmd('HSET', FRIEND_TABLE_MAIN_KEY + tableNo, FRIEND_TABLE_TABLEID, tableId)
    
def addOneResult(tableNo, seats, deltaScore, totalScore, curRound, totalRound, gameId, roomId, tableId):
    """每一小局的结果"""
    ftlog.info('hall_friend_table.one_game_result tableNo=', tableNo
        , ' seats=', seats
        , ' deltaScore=', deltaScore
        , ' totalScore=', totalScore
        , ' curRound=', curRound
        , ' totalRound=', totalRound
        , ' gameId=', gameId
        , ' roomId=', roomId
        , ' tableId=', tableId
        , ' time=', pktimestamp.getCurrentTimestamp())
    
def gameEnd(tableNo, seats, totalScore, totalRound, gameId, roomId, tableId):
    """最终结果"""
    ftlog.info('hall_friend_table.gameEnd tableNo=', tableNo
        , ' seats=', seats
        , ' totalScore=', totalScore
        , ' totalRound=', totalRound
        , ' gameId=', gameId
        , ' roomId=', roomId
        , ' tableId=', tableId
        , ' time=', pktimestamp.getCurrentTimestamp())