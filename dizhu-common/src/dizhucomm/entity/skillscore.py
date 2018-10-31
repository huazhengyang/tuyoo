# -*- coding:utf-8 -*-
'''
Created on 2017年2月14日

@author: zhaojiangang
'''
from sre_compile import isstring

from dizhucomm.entity import commconf
import freetime.util.log as ftlog
from hall.entity import hallranking, hallrename, hallitem, hallconf, \
    datachangenotify
from poker.entity.biz.content import TYContentRegister
from poker.entity.biz.exceptions import TYBizConfException
from poker.entity.biz.item.item import TYAssetUtils
from poker.entity.biz.ranking.rankingsystem import TYRankingInputTypes
from poker.entity.configure import configure
from poker.entity.dao import gamedata
from poker.entity.events.tyevent import UserEvent, EventConfigure
from poker.entity.game.game import TYGame
from poker.util import sortedlist
import poker.util.timestamp as pktimestamp
import poker.entity.events.tyeventbus as pkeventbus


class SkillScoreLevel(object):
    def __init__(self, skillScore, level, scoreRange, pic, bigPic, rewardContent):
        self.skillScore = skillScore
        self.level = level
        self.scoreRange = scoreRange
        self.pic = pic
        self.bigPic = bigPic
        self.rewardContent = rewardContent

class SkillScoreIncrEvent(UserEvent):
    def __init__(self, gameId, userId, oldScore, oldLevel, newScore, newLevel):
        super(SkillScoreIncrEvent, self).__init__(userId, gameId)
        self.oldScore = oldScore
        self.oldLevel = oldLevel
        self.newScore = newScore
        self.newLevel = newLevel

class UserSkillScore(object):
    def __init__(self, userId, score, level):
        self.userId = userId
        self.score = score
        self.level = level
        
class GameSkillScore(object):
    def __init__(self, gameId):
        self.gameId = gameId
        self.gameName = None
        self.desc = None
        self.titlePic = None
        self.levelMap = None
        self.levels = None
        self.levelScores = None
        self._inited = None
        self._configKey = 'game:%s:skill.score:0' % gameId
        
    def init(self):
        self._inited = True
        self._reloadConf()
        pkeventbus.globalEventBus.subscribe(EventConfigure, self._onConfChanged)
    
    def getLevel(self, score):
        i = sortedlist.upperBound(self.levelScores, score)
        i = max(i, 1)
        return self.levelMap[i]

    def getUserSkillScoreValue(self, userId):
        return gamedata.getGameAttrInt(userId, self.gameId, 'skillscore')
        
    def getUserSkillScore(self, userId):
        score = gamedata.getGameAttrInt(userId, self.gameId, 'skillscore')
        level = self.getLevel(score)
        return UserSkillScore(userId, score, level)
    
    def sendLevelReward(self, userId, oldLevel, newLevel):
        if not newLevel.rewardContent:
            return None
        items = newLevel.rewardContent.getItems()
        ftlog.info('GameSkillScore.sendLevelReward',
                   'userId=', userId,
                   'oldLevel=', oldLevel.level,
                   'new_level=', newLevel.level,
                   'items=', [(ci.assetKindId, ci.count) for ci in items])
        ua = hallitem.itemSystem.loadUserAssets(userId)
        aslist = ua.sendContentItemList(self.gameId,
                                        items,
                                        1,
                                        True,
                                        pktimestamp.getCurrentTimestamp(),
                                        'TASK_MASTER_SCORE_UP_LEVEL_REWARD',
                                        newLevel.level)
        items = []
        for x in aslist :
            kindId = hallconf.translateAssetKindIdToOld(x[0].kindId)
            akind = hallitem.itemSystem.findAssetKind(x[0].kindId)
            items.append({
                'id':kindId,
                'count':x[1],
                'name':akind.displayName,
                'pic':akind.pic,
            })
        datachangenotify.sendDataChangeNotify(self.gameId, userId, TYAssetUtils.getChangeDataNames(aslist))
        return items

    def addUserSkillScore(self, userId, toAdd):
        score = gamedata.incrGameAttr(userId, self.gameId, 'skillscore', toAdd)
        # 大师分增量榜
        hallranking.rankingSystem.setUserByInputType(self.gameId,
                                                     TYRankingInputTypes.DASHIFEN_INCR,
                                                     userId,
                                                     toAdd,
                                                     pktimestamp.getCurrentTimestamp())
        oldScore = score - toAdd
        oldLevel = self.getLevel(oldScore)
        newLevel = self.getLevel(score)
        
        ret = buildUserSkillScoreInfo(UserSkillScore(userId, score, newLevel))
        ret['userId'] = userId
        ret['addScore'] = toAdd
        if oldLevel != newLevel:
            changeName = False
            needLevel = commconf.getChangeNickNameLevel(self.gameId)
            if needLevel == newLevel.level:
                setNameCount = hallrename.getRenameSum(self.gameId, userId)
                if setNameCount <= 0:
                    ret['changename'] = 1
                    changeName = True
            rewards = self.sendLevelReward(userId, oldLevel, newLevel)
            if not changeName and rewards:
                ret['rewards'] = rewards
            ret['isLevelUp'] = True
        
        TYGame(self.gameId).getEventBus().publishEvent(SkillScoreIncrEvent(self.gameId, userId, oldScore, oldLevel.level, score, newLevel.level))
        if ftlog.is_debug():
            ftlog.debug('SkillScore.incrSkillScore',
                        'gameId=', self.gameId,
                        'userId=', userId,
                        'addScore=', toAdd,
                        'newScore=', score,
                        'oldLevel=', oldLevel.level,
                        'newLevel=', newLevel.level,
                        'ret=', ret)        
        return ret

    def _onConfChanged(self, event):
        if self._inited and event.isChanged(self._configKey):
            ftlog.info('GameSkillScore._onConfChanged',
                       'gameId=', self.gameId)
            self._reloadConf()
            
    def _reloadConf(self):
        conf = configure.getGameJson(self.gameId, 'skill.score', {}, configure.DEFAULT_CLIENT_ID)
        gameName = conf.get('game_name')
        
        if not isstring(gameName):
            raise TYBizConfException(conf, '%s.skill.score.game_name must be string: %s' % (self.gameId, gameName))
        desc = conf.get('des', '')
        if not isstring(desc):
            raise TYBizConfException(conf, '%s.skill.score.des must be string: %s' % (self.gameId, desc))
        
        titlePic = conf.get('title_pic', '')
        if not isstring(titlePic):
            raise TYBizConfException(conf, '%s.skill.score.title_pic must be string: %s' % (self.gameId, titlePic))
        
        levels = []
        levelMap = {}
        levelScores = conf.get('score', [])
        levelPics = conf.get('level_pic', [])
        levelBigPics = conf.get('big_level_pic', [])
        rewardMap = conf.get('reward', {})
        if not levelScores:
            raise TYBizConfException(conf, '%s.skill.score.scores must be not empty list' % (self.gameId))
        for i, score in enumerate(levelScores):
            level = i + 1
            scoreRange = (score, -1) if level >= len(levelScores) else (score, levelScores[level])
            pic = levelPics[-1] if level >= len(levelPics) else levelPics[i]
            bigPic = levelBigPics[-1] if level >= len(levelBigPics) else levelBigPics[i]
            rewards = rewardMap.get(str(level), {}).get('rewards')
            rewardContent = None
            if rewards:
                rewardContent = TYContentRegister.decodeFromDict(rewards)
            skillScoreLevel = SkillScoreLevel(self, level, scoreRange, pic, bigPic, rewardContent)
            levelMap[level] = skillScoreLevel
            levels.append(skillScoreLevel)
        self.gameName = gameName
        self.desc = desc
        self.titlePic = titlePic
        self.levels = levels
        self.levelMap = levelMap
        self.levelScores = levelScores[:]
        
        ftlog.info('GameSkillScore._reloadConf',
                   'gameId=', self.gameId,
                   'gameName=', self.gameName,
                   'titlePic=', self.titlePic,
                   'levelKeys=', self.levelMap.keys())
        return self

_gameSkillScoreMap = {}

def registerGameSkillScore(gameId, gameSkillScore):
    assert(not findGameSkillScore(gameId))
    _gameSkillScoreMap[gameId] = gameSkillScore

def findGameSkillScore(gameId):
    return _gameSkillScoreMap.get(gameId)

def _getGameSkillScore(gameId):
    gameSkillScore = _gameSkillScoreMap.get(gameId)
    if not gameSkillScore:
        ftlog.error('skillscore._getGameSkillScore',
                    'gameId=', gameId)
        assert(gameSkillScore)
    return gameSkillScore

def getLevel(gameId, score):
    return _getGameSkillScore(gameId).getLevel(score)

def getUserSkillScore(gameId, userId):
    return _getGameSkillScore(gameId).getUserSkillScore(userId)

def getUserSkillScoreValue(gameId, userId):
    return _getGameSkillScore(gameId).getUserSkillScoreValue(userId)

def addUserSkillScore(gameId, userId, toAdd):
    return _getGameSkillScore(gameId).addUserSkillScore(userId, toAdd)
    
def buildUserSkillScoreInfo(userSkillScore):
    info = {}
    info['score'] = userSkillScore.score
    info['level'] = userSkillScore.level.level
    info['premaxscore'] = userSkillScore.level.scoreRange[0]
    info['curmaxscore'] = 2000000000 if userSkillScore.level.scoreRange[1] == -1 else userSkillScore.level.scoreRange[1]
    info['pic'] = userSkillScore.level.pic
    info['picbig'] = userSkillScore.level.bigPic
    info['title'] = userSkillScore.level.skillScore.titlePic
    info['name'] = userSkillScore.level.skillScore.gameName
    info['des'] = userSkillScore.level.skillScore.desc
    info['isLevelUp'] = False
    return info


