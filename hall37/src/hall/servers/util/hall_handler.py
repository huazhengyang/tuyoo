# -*- coding: utf-8 -*-
'''
Created on 2015年5月20日

@author: zqh
'''


from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from hall.entity import hallconf, hallgamelist, hallgamelist2, \
    halllocalnotification
from hall.entity.hallevent import UserBindWeixinEvent
from hall.servers.common.base_checker import BaseMsgPackChecker
from poker.entity.configure import gdata
from poker.entity.dao import daobase
from poker.entity.game import game
from poker.protocol import runcmd, router
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod


class HallHelper(object):
    @classmethod
    def encodeHallPage(cls, gameId, userId, clientId, page):
        result = []
        gIDS = []
        for node in page.nodeList:
            if node.isSuitable(gameId, userId, clientId):
                nodeDict = node.buildToDict(gameId, userId, clientId)
                result.append(nodeDict)
                gIDS.extend(node.getGameIds())
        
        if len(result) > 0:        
            return {"nodes": result}, gIDS
        else:
            return None, None
    
    @classmethod
    def encodeHallPageList(cls, gameId, userId, clientId, pageList):
        result = []
        gIDS = []
        for page in pageList:
            pageDict, IDS = cls.encodeHallPage(gameId, userId, clientId, page)
            if pageDict:
                result.append(pageDict)
                gIDS.extend(IDS)
        return result, gIDS
    
    @classmethod
    def encodeHallInnerGameList(cls, gameId, userId, clientId, innerGames):
        return [game.params for game in innerGames]
    
    @classmethod
    def encodeHallInnerGameList2(cls, gameId, userId, clientId, innerGames):
        result = []
        gIDS = []
        for game in innerGames:
            if game.isSuitable(gameId, userId, clientId):
                gameDict = game.buildToDict(gameId, userId, clientId)
                result.append(gameDict)
                gIDS.extend(game.getGameIds())
        return result, gIDS
    
    @classmethod
    def encodeHallUITemplage(cls, gameId, userId, clientId, template):
        games = []
        pages, _ = cls.encodeHallPageList(gameId, userId, clientId, template.pageList)
        innerGames = cls.encodeHallInnerGameList(gameId, userId, clientId, template.innerGames)
        
        for version in template.versionList:
            gameDict = {
                'gameId':version.game.gameId,
                'gameMark':version.game.gameMark,
                'description':version.game.description,
                'currentVer':version.conf
            }
            games.append(gameDict)
        return games, pages, innerGames
    
    @classmethod
    def encodeHallUITemplage2(cls, gameId, userId, clientId, template):
        games = []
        gameIds = []
        
        pages, pageIds = cls.encodeHallPageList(gameId, userId, clientId, template.pageList)
        if ftlog.is_debug():
            ftlog.debug('encodeHallUITemplage2 build pageIds: ', pageIds)
        gameIds.extend(pageIds)
        
        innerGames, innserIds = cls.encodeHallInnerGameList2(gameId, userId, clientId, template.innerGames)
        if ftlog.is_debug():
            ftlog.debug('encodeHallUITemplage2 build innserIds: ', innserIds)
        gameIds.extend(innserIds)
        
        if ftlog.is_debug():
            ftlog.debug('encodeHallUITemplage2 build gameIds: ', gameIds)
        
        # 去重
        gameIds = list(set(gameIds))
        if ftlog.is_debug():
            ftlog.debug('encodeHallUITemplage2 after heavy gameIds: ', gameIds)
        
        for version in template.versionList:
            if version.game.gameId in gameIds:
                gameDict = {
                    'gameId':version.game.gameId,
                    'gameMark':version.game.gameMark,
                    'description':version.game.description,
                    'currentVer':version.conf
                }
                games.append(gameDict)
        return games, pages, innerGames
        
@markCmdActionHandler
class HallTcpHandler(BaseMsgPackChecker):

    
    def __init__(self):
        pass
    def _get_switch_config(self, clientId):
        from poker.entity.configure import configure
        from hall.entity.hallconf import HALL_GAMEID
        switchInfo = configure.getTcContentByGameId('switch', None, HALL_GAMEID, clientId, {})
        if ftlog.is_debug():
            ftlog.debug('hall._get_switch_config',
                        'clientId=', clientId,
                        'switchInfo=', switchInfo)
        return switchInfo
    

    @markCmdActionMethod(cmd='hall', action="info", clientIdVer=0)
    def doHallInfo(self, userId, gameId, clientId):
        roominfos = hallconf.getHallSessionInfo(gameId, clientId)
        msg = MsgPack()
        msg.setCmd('hall_info')
        msg.setResult('gameId', gameId)
        msg.setResult('userId', userId)
        msg.setResult('sessions', roominfos)
        router.sendToUser(msg, userId)
    @markCmdActionMethod(cmd='hall', action="switchConf", clientIdVer=0)
    def doHallSwitchConf(self, userId, gameId, clientId):
        msg = MsgPack()
        msg.setCmd('hall_switchConf')
        msg.setResult('gameId', gameId)
        msg.setResult('userId', userId)
        msg.setResult('switchConf', self._get_switch_config(clientId))
        router.sendToUser(msg, userId)


    @markCmdActionMethod(cmd='hall', action="htmls_info", clientIdVer=0)
    def doHallHtmlsInfo(self, userId, gameId, clientId):
        roominfos = hallconf.getHallHtmlsInfo(clientId)
        msg = MsgPack()
        msg.setCmd('htmls_info')
        msg.setResult('gameId', gameId)
        msg.setResult('userId', userId)
        msg.setResult('htmls', roominfos)
        router.sendToUser(msg, userId)


    @markCmdActionMethod(cmd='hall', action="signs", clientIdVer=0)
    def doHallSigns(self):
        msg = runcmd.getMsgPack()
        ftlog.debug('msg=', msg)
        gameId = msg.getParam("gameId")
        userId = msg.getParam("userId")
        
        msgRes = MsgPack()
        msgRes.setCmd('m_signs')
        msgRes.setResult('gameId', gameId)
        msgRes.setResult('userId', userId)
        signs = {}
        for roomdef in gdata.roomIdDefineMap().values() :
            if roomdef.shadowId == 0 and roomdef.configure.get('ismatch') :
                roomId = roomdef.roomId
                issignin = daobase.executeTableCmd(roomId, 0, 'SISMEMBER', 'signs:' + str(roomId), userId)
                if issignin :
                    signs[roomdef.bigRoomId] = 1
        
        msgRes.setResult('signs', signs)
        router.sendToUser(msgRes, userId)
    
    
    @markCmdActionMethod(cmd='hall', action="room_list", clientIdVer=0)
    def doHallRoomList(self):
        msg = runcmd.getMsgPack()
        ftlog.error('NotImplementedError, doHallRoomList, msg=', msg)
        return runcmd.newOkMsgPack(code=1)


    @markCmdActionMethod(cmd='hall', action="vip_room_list", clientIdVer=0)
    def doHallVipRoomList(self):
        msg = runcmd.getMsgPack()
        ftlog.error('NotImplementedError, doHallVipRoomList, msg=', msg)
        return runcmd.newOkMsgPack(code=1)


    @markCmdActionMethod(cmd='hall', action="vip_table_list", clientIdVer=0)
    def doHallVipTableList(self):
        msg = runcmd.getMsgPack()
        ftlog.error('NotImplementedError, doHallVipTableList, msg=', msg)
        return runcmd.newOkMsgPack(code=1)


    @markCmdActionMethod(cmd='hall', action="match_room_list", clientIdVer=0)
    def doHallMatchRoomList(self):
        msg = runcmd.getMsgPack()
        ftlog.error('NotImplementedError, doHallMatchRoomList, msg=', msg)
        return runcmd.newOkMsgPack(code=1)


    @markCmdActionMethod(cmd='hall', action="login_reward", clientIdVer=0)
    def doHallLoginReward(self):
        msg = runcmd.getMsgPack()
        ftlog.error('NotImplementedError, doHallLoginReward, msg=', msg)
        return runcmd.newOkMsgPack(code=1)


    @markCmdActionMethod(cmd='hall', action="modules_switch", clientIdVer=0)
    def doHallModulesSwitch(self, userId, gameId, clientId):
        '''
        老版本支撑
        '''
        switches = hallconf.getModulesSwitch(clientId)
        msg = MsgPack()
        msg.setCmd('modules_switch')
        msg.setResult('gameId', gameId)
        msg.setResult('userId', userId)
        msg.setResult('switches', switches)
        router.sendToUser(msg, userId)


    @markCmdActionMethod(cmd='hall', action="more_games", clientIdVer=0)
    def doHallMoreGames(self, userId, gameId, clientId):
        '''
        老版本支撑
        '''
        description = hallconf.getMoreGamesDesc(clientId)
        apks = hallconf.getMoreGamesUpdateApks(clientId)
        moregames = hallconf.getMoreGames(clientId)
        visible = 0
        switches = hallconf.getModulesSwitch(clientId)
        for x in switches :
            if x.get('name') == 'more_games' :
                visible = x.get('open', 0)
                break
        mo = MsgPack()
        mo.setCmd('get_more_games')
        mo.setResult('gameId', gameId)
        mo.setResult('userId', userId)
        mo.setResult('update_url', apks['upurl'])
        mo.setResult('pkg_size', apks['size'])
        mo.setResult('games', moregames)
        mo.setResult('description', description)
        mo.setResult('visible', visible)
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd='hall_game_list', clientIdVer=0)
    def doHallGameList(self, userId, gameId, clientId):
        pages = hallgamelist.getGameList(gameId, userId, clientId)
        from hall.servers.util import gamelistipfilter
        _, pages, _ = gamelistipfilter.filtergamelist(0, [], pages, [], userId, clientId,isNeedPopShutDownGameWnd=True)
        mo = MsgPack()
        mo.setCmd('hall_game_list')
        mo.setResult('gameId', gameId)
        mo.setResult('userId', userId)
        mo.setResult('pages', pages)
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd='hall_game_list', clientIdVer=3.7)
    def doHallGameListV3_7(self, userId, gameId, clientId):
        template = hallgamelist2.getUITemplate(gameId, userId, clientId)
        if template is None:
            ftlog.exception('doHallGameListV3_7 error, please check clientId:', clientId)
        else:
            games, pages, _innerGames = HallHelper.encodeHallUITemplage(gameId, userId, clientId, template)
            from hall.servers.util import gamelistipfilter
            games, pages, _innerGames = gamelistipfilter.filtergamelist(3.7, games, pages, _innerGames, userId, clientId, isNeedPopShutDownGameWnd=True)
            mo = MsgPack()
            mo.setCmd('hall_game_list')
            mo.setResult('gameId', gameId)
            mo.setResult('userId', userId)
            mo.setResult('games', games)
            mo.setResult('pages', pages)
            router.sendToUser(mo, userId)
        

    @markCmdActionMethod(cmd='hall_game_list', clientIdVer=3.76)
    def doHallGameListV3_76(self, userId, gameId, clientId):
        template = hallgamelist2.getUITemplate(gameId, userId, clientId)
        if template is None:
            ftlog.exception('doHallGameListV3_76 error, please check clientId:', clientId)
        else:
            _games, pages, innerGames = HallHelper.encodeHallUITemplage(gameId, userId, clientId, template)
            from hall.servers.util import gamelistipfilter
            _games, pages, innerGames = gamelistipfilter.filtergamelist(3.76, _games, pages, innerGames, userId, clientId, isNeedPopShutDownGameWnd=True)
            mo = MsgPack()
            mo.setCmd('hall_game_list')
            mo.setResult('gameId', gameId)
            mo.setResult('userId', userId)
            mo.setResult('games', _games)
            mo.setResult('pages', pages)
            mo.setResult('innerGames', innerGames)
            router.sendToUser(mo, userId)
            
    @markCmdActionMethod(cmd='hall_game_list', clientIdVer=3.81)
    def doHallGameListV3_81(self, userId, gameId, clientId):
        template = hallgamelist2.getUITemplate(gameId, userId, clientId)
        if template is None:
            ftlog.exception('doHallGameListV3_81 error, please check clientId:', clientId)
        else:
            _games, pages, innerGames = HallHelper.encodeHallUITemplage2(gameId, userId, clientId, template)
            from hall.servers.util import gamelistipfilter
            _games, pages, innerGames = gamelistipfilter.filtergamelist(3.81, _games, pages, innerGames, userId, clientId,isNeedPopShutDownGameWnd=True)
            mo = MsgPack()
            mo.setCmd('hall_game_list')
            mo.setResult('gameId', gameId)
            mo.setResult('userId', userId)
            mo.setResult('games', _games)
            mo.setResult('pages', pages)
            mo.setResult('innerGames', innerGames)
            router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd='hall_local_notification', clientIdVer=0)
    def doHallLocalNotification(self, userId, gameId, clientId):
        lnConfig = halllocalnotification.queryLocalNotification(gameId, userId, clientId)
        mo = MsgPack()
        mo.setCmd('hall_local_notification')
        mo.setResult('gameId', gameId)
        mo.setResult('userId', userId)
        mo.setResult('notifies', lnConfig)
        router.sendToUser(mo, userId)
    @markCmdActionMethod(cmd='hall', action='getMatchNotifyList', clientIdVer=0)
    def doGetMatchNotifyList(self, userId, gameId, clientId):
        '''
        获取赛事通知列表
        '''
        from hall.entity import hallnewnotify

        msg = MsgPack()
        msg.setCmd('hall')
        msg.setResult('action', 'getMatchNotifyList')
        msg.setResult('gameId', gameId)
        msg.setResult('userId', userId)
        msg.setResult('matchNotifyList', hallnewnotify.getMatchNotifyList(userId))
        router.sendToUser(msg, userId)
        
    @markCmdActionMethod(cmd='hall', action='bind_wx_openid', clientIdVer=0)
    def doBindWxOpenId(self, userId, gameId, clientId):
        '''
        绑定微信openid回调
        '''
        from hall.game import TGHall
        TGHall.getEventBus().publishEvent(UserBindWeixinEvent(userId, gameId))
        


