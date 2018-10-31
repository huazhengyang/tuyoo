# -*- coding: utf-8 -*-
'''
Created on 2015年5月20日

@author: zqh
'''


from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from hall.entity import hallmoduletip
from hall.servers.common.base_checker import BaseMsgPackChecker
from poker.protocol import router, runcmd
from poker.protocol.decorator import markCmdActionMethod, markCmdActionHandler

class ModuletipTcpHandlerHelp(object):
    @classmethod
    def buildInfo(cls, action, modules):
        mo = MsgPack()
        mo.setCmd('module_tip')
        mo.setResult('action', action)
        modulesInfo = []
        for module in modules:
            modulesInfo.append({
                                'name': module.name,
                                'type': module.type,
                                'count': module.count,
                                'needReport': module.needReport
                                })
        mo.setResult('modules', modulesInfo)
        return mo
            
@markCmdActionHandler  
class ModuletipTcpHandler(BaseMsgPackChecker):

    def __init__(self):
        pass
    
    def _check_param_action(self, msg, key, params):
        action = msg.getParam(key)
        if action and isinstance(action,  (str, unicode)) :
            return None, action
        return 'ERROR of action !' + str(action), None
    '''
    def _check_param_subGameId(self, msg, key, params):
        subGameId = msg.getParam(key)
        if subGameId and isinstance(subGameId,  (int)) :
            return None, subGameId
        return 'ERROR of subGameId !' + str(subGameId), None
    '''
    def _check_param_modules(self, msg, key, params):
        modules = msg.getParam(key)
        if  isinstance(modules,  (list)) :
            return None, modules
        return 'ERROR of modules !' + str(modules), None
    '''
    def _check_param_counts(self, msg, key, params):
        counts = msg.getParam(key)
        if counts and isinstance(counts,  (list)) :
            return None, counts
        return 'ERROR of counts !' + str(counts), None
    '''
    
    @markCmdActionMethod(cmd='module_tip', action="update", clientIdVer=3.7)
    def doUpdate(self, gameId, userId, modules):
        msg = runcmd.getMsgPack()
        ftlog.debug('ModuletipTcpHandler.doUpdate msg=', msg)
        modulesInfo = hallmoduletip.getInfo(userId, modules, gameId)
        mo = ModuletipTcpHandlerHelp.buildInfo('update', modulesInfo)       
        router.sendToUser(mo, userId)
        
    @markCmdActionMethod(cmd='module_tip', action="update", clientIdVer=0)
    def doUpdateOld(self, gameId, userId, modules):
        msg = runcmd.getMsgPack()
        ftlog.debug('ModuletipTcpHandler.doUpdate msg=', msg)
        modulesInfo = hallmoduletip.getInfo(userId, modules, gameId)
        mo = ModuletipTcpHandlerHelp.buildInfo('update', modulesInfo)       
        router.sendToUser(mo, userId)
        
    @markCmdActionMethod(cmd='module_tip', action="report", clientIdVer=3.7)
    def doReport(self, gameId, userId, modules):
        msg = runcmd.getMsgPack()
        ftlog.debug('ModuletipTcpHandler.report msg=', msg)
        modulesInfo = hallmoduletip.cancelModulesTip(userId, modules, gameId)
        mo = ModuletipTcpHandlerHelp.buildInfo('report', modulesInfo)      
        router.sendToUser(mo, userId)
        
    @markCmdActionMethod(cmd='module_tip', action="report", clientIdVer=0)
    def doReportOld(self, gameId, userId, modules):
        msg = runcmd.getMsgPack()
        ftlog.debug('ModuletipTcpHandler.report msg=', msg)
        modulesInfo = hallmoduletip.cancelModulesTip(userId, modules, gameId)
        mo = ModuletipTcpHandlerHelp.buildInfo('report', modulesInfo)      
        router.sendToUser(mo, userId)
        
 

 
























