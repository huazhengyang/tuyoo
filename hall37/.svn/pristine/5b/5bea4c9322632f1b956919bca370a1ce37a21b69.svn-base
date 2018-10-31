# -*- coding: utf-8 -*-
 
from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from hall.entity  import hallmenulist
from hall.servers.common.base_checker import BaseMsgPackChecker
from poker.protocol import router, runcmd
from poker.protocol.decorator import markCmdActionMethod, markCmdActionHandler
   
@markCmdActionHandler  
class MenuListTcpHandler(BaseMsgPackChecker):
        
    @markCmdActionMethod(cmd='menu_list', action="", clientIdVer=0)
    def getMenuList(self, gameId, userId, clientId):
        msg = runcmd.getMsgPack()
        ftlog.debug('getMenuList msg=', msg)
        menuList = hallmenulist.getClientMenuList(clientId)
        menu_settings = hallmenulist.getClientCustomMenuSetting(gameId, userId, clientId, menuList)
        
        mo = MsgPack()
        mo.setCmd('menu_list')     
        mo.setResult("gameId", gameId)
        mo.setResult("userId", userId)
        mo.setResult("menus", menuList)  
        mo.setResult("menu_settings", menu_settings)      
        router.sendToUser(mo, userId)

























