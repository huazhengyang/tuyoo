# -*- coding: utf-8 -*-
'''
Created on 2015年8月12日

@author: bo
'''

from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from hall.entity import sdkclient
from hall.servers.common.base_checker import BaseMsgPackChecker
from poker.entity.dao import sessiondata
from poker.protocol import runcmd, router
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod
from poker.entity.dao import onlinedata
from hall.entity.todotask import TodoTaskHelper, TodoTaskPopTip,\
    TodoTaskInviteToGame, TodoTaskShowInfo
from poker.entity.dao import userdata
from poker.util import strutil
from poker.entity.configure import gdata



@markCmdActionHandler
class FriendTcpHandler(BaseMsgPackChecker):

    action_urls = {
        'add_friend': '/open/v3/sns/addFriend',
        'del_friend': '/open/v3/sns/delFriend',
        'get_friend_list': '/open/v3/sns/getFriendsAndRequests',
        'get_friends_rank': '/open/v3/sns/getFriendsRank',
        'praise_friend': '/open/v3/sns/praiseFriend',
        'accept_friend': '/open/v3/sns/confirmFriendRequest',
        'get_contacts_for_invite': '/open/v3/sns/getContactsForInvite',
        'add_contact_friend_invite': '/open/v3/sns/addContactFriendInvite',
        'block_request': '/open/v3/sns/blockFriendRequest',
        'get_recommend_list': '/open/v3/sns/getRecommendList',
        'search_user': '/open/v3/sns/searchUser',
        'get_friend_guide': '/open/v3/sns/getFriendGuide',
        'get_friend_tip_info': '/open/v3/sns/getFriendTipInfo',
        'ready_invite_friend': '/open/v3/sns/readyInviteFriend'
    }

    def __init__(self):
        super(FriendTcpHandler, self).__init__()

    # def _check_param_level(self, msg, key, params):
    #     level = msg.getParam(key, msg.getParam('level'))
    #     if not isinstance(level, int):
    #         return 'ERROR of level !', None
    #     return None, level
            
    def sendErrorResponse(self, userId, cmd, errorCode, errorInfo):
        mo = MsgPack()
        mo.setCmd(cmd)
        mo.setError(errorCode, errorInfo)
        router.sendToUser(mo, userId)
        
    def isInSameTable(self, inviter, invitee):
        inviterList = onlinedata.getOnlineLocList(inviter)
        ftlog.debug('isInSameTable userId->', inviter, ' loc->', inviterList)
        inviteeList = onlinedata.getOnlineLocList(invitee)
        ftlog.debug('isInSameTable userId->', invitee, ' loc->', inviteeList)
        for er in inviterList:
            erRoom, erTable = er[0], er[1]
            for ee in inviteeList:
                eeRoom, eeTable = ee[0], ee[1]
                if (erRoom == eeRoom) and (erTable == eeTable):
                    return True
                
        return False

    def processInvitees(self, enterParam, note, invitees, userId, gameId):
        '''
        邀请好友牌桌游戏
        invitees - 被邀请者
        '''
        if not invitees :
            return
        uds = userdata.getAttrs(userId, ['name'])
        # 检查是否在线
        for invitee in invitees:
            # invitee - 被邀请者
            state = onlinedata.getOnlineState(invitee)
            if state:
                # 在线，则进行下一步操作
                ids = userdata.getAttrs(invitee, ['name'])
                _, clientVer, _, _ = sessiondata.getClientIdInfo(invitee)
                if clientVer < 3.77:
                    # 版本号小于3.77，则提示升级
                    TodoTaskHelper.sendTodoTask(gameId, invitee, TodoTaskPopTip(note + ' 请升级至新版本与好友 ' + uds[0] + ' 一起玩耍！'))
                    TodoTaskHelper.sendTodoTask(gameId, userId, TodoTaskPopTip('您的好友 ' + ids[0] + ' 版本较低，提醒他升级到最新版本一起玩耍吧！'))                
                else:
                    # 判断是否在同一牌桌上
                    if self.isInSameTable(userId, invitee):
                        TodoTaskHelper.sendTodoTask(gameId, userId, TodoTaskPopTip('您的好友 ' + ids[0] + ' 正在跟您一起游戏呢'))
                    else:
                        # 版本号大于3.77，则发送邀请
                        TodoTaskHelper.sendTodoTask(gameId, invitee, TodoTaskInviteToGame(userId, note, enterParam))
            else:
                TodoTaskHelper.sendTodoTask(gameId, userId, TodoTaskPopTip('您的好友当前不在线'))
                ftlog.debug('您的好友当前不在线')
        
    def processInviteAnswser(self, inviter, answer, userId, gameId):
        '''
        对邀请游戏的应答
        userId - 当前用户
        inviter - 邀请者
        向邀请者发送回应
        '''
        uds = userdata.getAttrs(userId, ['name'])
        response = ''
        if answer:
            response = '您的好友 ' + uds[0] + ' 同意了您的游戏邀请'
        else:
            response = '您的好友 ' + uds[0] + ' 拒绝了您的游戏邀请'
            
        TodoTaskHelper.sendTodoTask(gameId, inviter, TodoTaskPopTip(response))

    def _isObserver(self, userId):
        """
        陈龙和才哥需求: 在德州和三张里观战时, 不能加好友。原因是好多恶意玩家用这个做宣传。
        跟辉哥商量过了, 没什么好办法实现~ 只能在这里写死 gameId

        by WangTao
        """

        locList = onlinedata.getOnlineLocList(userId)
        gameIds = {8, 30}

        for onlineLoc in locList:
            roomId, tableId, seatId = onlineLoc
            onlineGameId = strutil.getGameIdFromInstanceRoomId(roomId)

            if onlineGameId not in gameIds:
                continue

            # 判断是否观战状态。 只适用三张和德州
            if roomId and tableId and seatId:
                roomConf = gdata.getRoomConfigure(roomId)
                maxSeatN = roomConf['tableConf']['maxSeatN']
                if seatId == maxSeatN + 1:  # is observe
                    ftlog.info("FriendTcpHandler._isObserver| is observer"
                               "| userId, loc:", userId, onlineLoc)
                    return True

        return False

    @markCmdActionMethod(cmd='friend_call', action='*', clientIdVer=0)
    def doFriendCall(self, gameId, userId):
        ftlog.debug('doFriendCall...')

        cmd = runcmd.getMsgPack()
        # router.sendToUser(mo, userId)
        # clientId = runcmd.getClientId(cmd)
        action = cmd.getParam('action')

        if action == 'invite_to_game':
            # 邀请好友牌桌游戏
            enterParams = cmd.getParam('enterParams')
            note = cmd.getParam('note')
            invitees = cmd.getParam('invitees')
            self.processInvitees(enterParams, note, invitees, userId, gameId)
            return
        elif action == 'answer_to_invite':
            # 对好友邀请的应答
            inviter = cmd.getParam('inviter')
            answer = cmd.getParam('answer')
            self.processInviteAnswser(inviter, answer, userId, gameId)
            return
        elif action in ['get_friends_rank', 'get_friend_tip_info', 'praise_friend']:
            from hall.entity import hallvip
            try:
                vip = hallvip.userVipSystem.getUserVip(userId).vipLevel.level
            except:
                vip = 0
            cmd.setParam('vip', vip)
        elif action == 'add_friend':
            if self._isObserver(userId):
                show_info_task = TodoTaskShowInfo("对不起，旁观时不能加好友哦~")
                TodoTaskHelper.sendTodoTask(gameId, userId, show_info_task)
                return

        # if not clientId:
        #     clientId = sessiondata.getClientId(userId)
        params = cmd._ht['params']
        tcp_params = strutil.cloneData(params)
        del tcp_params['authorCode']

        del params['action']
        del params['gameId']
        params['appId'] = gameId
        # params['from_tcp'] = 1

        import json
        params['tcp_params'] = json.dumps(tcp_params)

        url = self.action_urls[action]
        ftlog.debug('handleFriendCall post', url, params)
        sdkclient._requestSdk(url, params, needresponse=False)
