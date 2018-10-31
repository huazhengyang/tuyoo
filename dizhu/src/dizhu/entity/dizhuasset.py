# -*- coding=utf-8
'''
Created on 2015年7月24日

@author: zhaojiangang
'''
from dizhu.entity.skillscore import DizhuAssetKindMasterScore
from poker.entity.biz.item.item import TYAssetKindRegister


ASSET_MASTER_SCORE_KIND_ID = 'ddz:master.score'

def _registerClasses():
    TYAssetKindRegister.registerClass(DizhuAssetKindMasterScore.TYPE_ID, DizhuAssetKindMasterScore)    

