from poker.entity.dao import daobase

HKEY_OFFICIALDATA_RECORD = 'officialdata:'
HKEY_USERFRIEND = 'userwxfriend:'


def getRank(uid, gameid):
    assert (isinstance(gameid, int) and gameid > 0), 'gameid must be int'
    return daobase.executeUserCmd(uid, 'GET', HKEY_USERFRIEND + str(gameid) + ':' + str(uid))


def getOfficialPushRecord(uid, gameid):
    assert (isinstance(gameid, int) and gameid > 0), 'gameid must be int'
    return daobase.executeUserCmd(uid, 'lrange', HKEY_OFFICIALDATA_RECORD + str(gameid) + ':' + str(uid), 0, -1)


def setRank(uid, gameid, value):
    assert (isinstance(gameid, int) and gameid > 0), 'gameid must be int'
    return daobase.executeUserCmd(uid, 'SET', HKEY_USERFRIEND + str(gameid) + ':' + str(uid), value)


def setOfficialPushRecord(uid, gameid, value):
    assert(isinstance(gameid, int) and gameid > 0), 'gameid must be int'
    return daobase.executeUserCmd(uid, 'rpush', HKEY_OFFICIALDATA_RECORD + str(gameid) + ':' + str(uid), value)


def delOfficialPushRecord(uid, gameid):
    return daobase.executeUserCmd(uid, 'ltrim', HKEY_OFFICIALDATA_RECORD + str(gameid) + ':' + str(uid), 10000, 100000)
