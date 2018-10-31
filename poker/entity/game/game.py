# -*- coding: utf-8 -*-
"""
游戏基类
"""
from freetime.core.timer import FTLoopTimer
import freetime.util.log as ftlog
from poker.entity.configure import gdata
from poker.entity.events.tyeventbus import TYEventBus
from poker.entity.robot.robot import TYRobotManager
from poker.util import strutil
__author__ = ['"Zqh"', '"Zhouhao" <zhouhao@tuyoogame.com>']

class _TYGameCallAble(type, ):

    def __init__(self, name, bases, dic):
        pass

    def __call__(self, gameId=0, *args, **kwargs):
        pass

class TYGame(object, ):
    __metaclass__ = _TYGameCallAble
    PLAY_COUNT = 'playGameCount'
    WIN_COUNT = 'winGameCount'

    def __init__(self, *args, **argds):
        pass

    def gameId(self):
        """
        取得当前游戏的GAMEID, int值
        """
        pass

    def newTable(self, room, tableId):
        """
        此方法由系统进行调用
        更具给出的房间的基本定义信息, 创建一个TYTable的实例
        其必须是 poker.entity.game.table.TYTable的子类
        room 桌子所属的房间的TYRoom实例
        tableId 新桌子实例的ID
        """
        pass

    def initGameBefore(self):
        """
        此方法由系统进行调用
        游戏初始化的预处理
        """
        pass

    def initGame(self):
        """
        此方法由系统进行调用
        游戏自己初始化业务逻辑模块, 例如: 初始化配置, 建立事件中心等
        执行的时序为:  首先调用所有游戏的 initGameBefore()
                    再调用所有游戏的 initGame()
                    最后调用所有游戏的 initGameAfter()
        """
        pass

    def initGameAfter(self):
        """
        此方法由系统进行调用
        游戏初始化的后处理
        """
        pass

    def getInitDataKeys(self):
        """
        取得游戏数据初始化的字段列表
        """
        pass

    def getInitDataValues(self):
        """
        取得游戏数据初始化的字段缺省值列表
        """
        pass

    def getGameInfo(self, userId, clientId):
        """
        取得当前用户的游戏账户信息dict
        """
        pass

    def getDaShiFen(self, userId, clientId):
        """
        取得当前用户的游戏账户的大师分信息
        """
        pass

    def getPlayGameCount(self, userId, clientId):
        """
        取得当前用户游戏总局数
        """
        pass

    def getPlayGameInfoByKey(self, userId, clientId, keyName):
        """
        取得当前用户的游戏信息
        key - 要取得的信息键值，枚举详见TYGame类的宏定义
        """
        pass

    def createGameData(self, userId, clientId):
        """
        此方法在UTIL服务中调用
        初始化该游戏的所有的相关游戏数据
        包括: 主游戏数据gamedata, 道具item, 勋章medal等
        返回主数据的键值和值列表
        """
        pass

    def loginGame(self, userId, gameId, clientId, iscreate, isdayfirst):
        """
        此方法在UTIL服务中调用
        用户登录一个游戏, 游戏自己做一些其他的业务或数据处理
        例如: 1. IOS大厅不发启动资金的补丁, 
             2. 麻将的记录首次登录时间
             3. 游戏插件道具合并至大厅道具
        """
        pass

    def getEventBus(self):
        """
        取得当前游戏的事件中心
        """
        pass

    def getRobotManager(self):
        """
        取得游戏的机器人管理器
        一定是 : TYRobotManager 的实例
        """
        pass

    def getTodoTasksAfterLogin(self, userId, gameId, clientId, isdayfirst):
        """
        获取登录后的todotasks列表
        """
        pass

    def isWaitPigTable(self, userId, room, tableId):
        """
        检查是否是杀猪状态的桌子, 缺省为非杀猪状态的桌子
        """
        pass

    def canJoinGame(self, userId, roomId, tableId, seatId):
        """
        检查参数描述的桌子是否可加入游戏
        eg:
            现金桌可加入则返回1
            MTT比赛桌不可加入则返回0
        """
        pass

    def getTuyooRedEnvelopeShareTask(self, userId, clientId, _type):
        """
        获取可用的途游红包分享
        _type: 表示红包类型： all | register | login
        返回值不为None，则有待发送的红包
        返回值为None，则没哟独爱发送的红包

        """
        pass

    def sendTuyooRedEnvelopeCallBack(self, userId, clientId, redEnvelopeId):
        """
        途游红包的发送回调
        红包ID redEnvelopeId
        """
        pass

    def checkFriendTable(self, ftId):
        """
        检测自建桌ID是否继续使用，如果不使用，将回收次ftId
        0 - 有效
        1 - 无效

        返回值：
        False - 无用
        True - 有用
        """
        pass

    def enterFriendTable(self, userId, gameId, clientId, ftId):
        """

        """
        pass
GAME_STATUS_RUN = 0
GAME_STATUS_SHUTDOWN_GO = 80
GAME_STATUS_SHUTDOWN_ERROR = 90
GAME_STATUS_SHUTDOWN_DONE = 100
_gameStatus = GAME_STATUS_RUN

def isShutDown():
    """
    判定当前进程是否处于正常服务状态
    """
    pass

def doShutDown():
    """
    关闭的方法由控制台调用热更新脚本进行执行，并且判定所有房间的运行状态
    一、
    对于UT、CT中进行的业务逻辑，则需要实时判定isShutDown()的值来确保是否要进行业务的继续处理
    非房间内的业务，系统无法确定各个具体业务状态，因此业务本身检测到isShutDown()==True时，
    需要“尽快”结束或屏蔽业务处理，通常这个“尽快”为3秒钟， 
    例如：UT进程停止接收玩家的兑换操作请求、道具打开请求等操作
        CT进程停止排行榜奖励的发放等
    二、
    对于room，将会主动调用用房间的doShutDown()方法，room基类方法中会遍历所有的table，并调用table的doShutDown()
    因此各个游戏需要根据各自的情况对room和table的doShutDown方法进行调整，
    例如：不再开局或立刻解散牌局、归还玩家的带入金币等
    因各个游戏的房间对于进入和快速开始的处理已经有很大的不同，因此无法进行统一的消息截获屏蔽处理
    """
    pass