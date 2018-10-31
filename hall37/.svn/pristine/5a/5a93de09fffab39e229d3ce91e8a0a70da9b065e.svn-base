# -*- coding=utf-8
'''
Created on 2016年07月29日

@author: zhaojiangang
'''
import freetime.util.log as ftlog
from hall.entity.hall_red_envelope.hall_red_envelope import TYRedEnvelopeID, TYRedEnvelope,\
    TYRedEnvelopeMgr

@classmethod
def openRedEnvelope(cls, envelopeId, userId):
    '''
    打开红包
    @return: 
    1) OK
    2) 领过了
    3) 领光了
    4) 过期了
    '''
    global _redEnvelopeConfig
    
    if TYRedEnvelopeID.isExpired(envelopeId):
        return cls.makeWrongResponse(cls.HALL_RED_ENVELOPE_OPEN, _redEnvelopeConfig['tips']['expired'])
    
    isExist, info = TYRedEnvelope().loadFromDB(envelopeId)
    if isExist:
        envelope = info
        result, response = envelope.openRedEnvelope(userId)
        if result:
            # 如果是推广红包，建立上下线关系
#             inInfo = TYRedEnvelopeID.parseID(envelopeId)
#             if inInfo['reason'] == cls.RED_ENVELOPE_PROMOTE:
#                 # 上线 inInfo['userId']
#                 topUserId = inInfo['userId']
#                 # 下线 userId
#                 if ftlog.is_debug():
#                     ftlog.debug('openRedEnvelope.promoteEnvelope, inviter:', topUserId, ' and invitee:', userId)
#                     
#                 from hall.servers.util.rpc import neituiguang_remote
#                 neituiguang_remote.set_inviter(userId, topUserId)
            
            return cls.makeRightResponse(cls.HALL_RED_ENVELOPE_OPEN, response)
        else:
            return cls.makeWrongResponse(cls.HALL_RED_ENVELOPE_OPEN, response)
    else:
        error = info
        return cls.makeWrongResponse(cls.HALL_RED_ENVELOPE_OPEN, error)

TYRedEnvelopeMgr.openRedEnvelope = openRedEnvelope
